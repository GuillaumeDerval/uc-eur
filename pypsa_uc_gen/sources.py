"""
Data acquisition.

Every number that ends up in a generated instance comes from one of the public
datasets below. Nothing is synthesised or hand-tuned; where a modelling
assumption is unavoidable (initial commitment state, value of lost load) it is
an explicit CLI option rather than a made-up "data" value.

  existing power plant fleet .......... powerplantmatching
                                        https://github.com/PyPSA/powerplantmatching
  hourly load + VRE generation ........ Open Power System Data, time series 60min
                                        https://data.open-power-system-data.org/time_series/
                                        (same source and columns PyPSA-Eur uses in
                                        scripts/retrieve_electricity_demand_opsd.py)
  unit commitment parameters .......... PyPSA-Eur data/unit_commitment.csv
  fuel / VOM / efficiency / CO2 ....... PyPSA technology-data outputs/costs_<year>.csv
"""

from __future__ import annotations

import functools
import http.client
import logging
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"

OPSD_VERSION = "2020-10-06"
OPSD_URL = (
    "https://data.open-power-system-data.org/time_series/"
    "{version}/time_series_60min_singleindex.csv"
)
PYPSA_EUR_UC_URL = (
    "https://raw.githubusercontent.com/PyPSA/pypsa-eur/master/data/unit_commitment.csv"
)
TECHNOLOGY_DATA_URL = (
    "https://raw.githubusercontent.com/PyPSA/technology-data/master/"
    "outputs/costs_{year}.csv"
)

#: OPSD load column preference, mirroring PyPSA-Eur's
#: scripts/retrieve_electricity_demand_opsd.py (transparency, filled with
#: power statistics).
_LOAD_PATTERNS = [
    "_load_actual_entsoe_transparency",
    "_load_actual_entsoe_power_statistics",
]

#: OPSD generation columns mapped onto PyPSA carrier names.
VRE_COLUMNS = {
    "solar": "{c}_solar_generation_actual",
    "onwind": "{c}_wind_onshore_generation_actual",
    "offwind": "{c}_wind_offshore_generation_actual",
}
#: Used only when a country reports total wind without an onshore/offshore split.
VRE_WIND_TOTAL = "{c}_wind_generation_actual"


#: Minimum seconds between requests to the same host. Generating a benchmark
#: set issues one API call per country, and Energy-Charts answers 429 to a
#: burst of them.
_MIN_REQUEST_INTERVAL = 1.0
_MAX_RETRIES = 6
_last_request: dict[str, float] = {}


def _fetch(url: str, filename: str, force: bool = False) -> Path:
    """
    Download ``url`` into the cache unless already present.

    Retries on rate limiting and transient server errors with exponential
    backoff, honouring ``Retry-After`` when the server sends it.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest = CACHE_DIR / filename
    if dest.exists() and not force:
        logger.debug("using cached %s", dest)
        return dest

    host = urllib.parse.urlsplit(url).netloc
    tmp = dest.with_suffix(dest.suffix + ".part")
    delay = 2.0
    for attempt in range(1, _MAX_RETRIES + 1):
        since = time.monotonic() - _last_request.get(host, 0.0)
        if since < _MIN_REQUEST_INTERVAL:
            time.sleep(_MIN_REQUEST_INTERVAL - since)
        logger.info("downloading %s -> %s", url, dest)
        try:
            _last_request[host] = time.monotonic()
            with urllib.request.urlopen(url, timeout=300) as response:
                tmp.write_bytes(response.read())
            tmp.replace(dest)
            return dest
        except urllib.error.HTTPError as exc:
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if not retryable or attempt == _MAX_RETRIES:
                raise
            wait = delay
            if exc.headers and exc.headers.get("Retry-After"):
                try:
                    wait = max(wait, float(exc.headers["Retry-After"]))
                except ValueError:
                    pass
            logger.warning(
                "HTTP %s for %s, retry %d/%d in %.0fs",
                exc.code, host, attempt, _MAX_RETRIES, wait,
            )
            time.sleep(wait)
            delay = min(delay * 2, 60.0)
        except (
            urllib.error.URLError,
            # A timeout during response.read() surfaces as TimeoutError, and a
            # dropped keep-alive as http.client.RemoteDisconnected; neither is a
            # URLError, so both slipped past the retry and failed a whole batch.
            TimeoutError,
            socket.timeout,
            ConnectionError,
            http.client.HTTPException,
        ) as exc:
            if attempt == _MAX_RETRIES:
                raise
            logger.warning(
                "network error for %s (%s), retry %d/%d in %.0fs",
                host, type(exc).__name__, attempt, _MAX_RETRIES, delay,
            )
            time.sleep(delay)
            delay = min(delay * 2, 60.0)
    raise RuntimeError(f"could not download {url}")


# --------------------------------------------------------------------------- #
# Unit commitment parameters (PyPSA-Eur)
# --------------------------------------------------------------------------- #


def load_unit_commitment_params(path: str | Path | None = None) -> pd.DataFrame:
    """
    Per-carrier unit commitment parameters.

    Returns a DataFrame indexed by PyPSA generator attribute
    (``min_up_time``, ``min_down_time``, ``p_min_pu``, ``ramp_limit_*``,
    ``start_up_cost``) with one column per carrier.

    ``start_up_cost`` is given per MW of ``p_nom`` and must be multiplied by
    the unit capacity, exactly as PyPSA-Eur does in
    ``add_electricity.attach_conventional_generators``.
    """
    fn = Path(path) if path else _fetch(PYPSA_EUR_UC_URL, "pypsa_eur_unit_commitment.csv")
    return pd.read_csv(fn, index_col=0)


# --------------------------------------------------------------------------- #
# Costs (PyPSA technology-data)
# --------------------------------------------------------------------------- #


def load_costs(year: int = 2020, co2_price: float = 0.0) -> pd.DataFrame:
    """
    Technology cost assumptions with a derived ``marginal_cost`` column.

    ``marginal_cost = VOM + (fuel + co2_price * CO2_intensity) / efficiency``
    in EUR/MWh_el, following PyPSA-Eur's ``add_electricity.load_costs``.

    ``co2_price`` is in EUR/tCO2 and defaults to 0 (no carbon price).
    """
    fn = _fetch(TECHNOLOGY_DATA_URL.format(year=year), f"costs_{year}.csv")
    raw = pd.read_csv(fn)
    costs = raw.pivot(index="technology", columns="parameter", values="value")

    # Gas turbines inherit the gas commodity price and CO2 intensity; nuclear
    # inherits the uranium fuel price. Same substitutions as PyPSA-Eur.
    for tech in ("OCGT", "CCGT"):
        for col in ("fuel", "CO2 intensity"):
            if col in costs.columns and "gas" in costs.index:
                costs.loc[tech, col] = costs.at["gas", col]
    if "uranium" in costs.index and "nuclear" in costs.index:
        costs.loc["nuclear", "fuel"] = costs.at["uranium", "fuel"]

    for col in ("VOM", "fuel", "CO2 intensity"):
        if col not in costs.columns:
            costs[col] = 0.0
        costs[col] = costs[col].fillna(0.0)
    costs["efficiency"] = costs["efficiency"].fillna(1.0)

    costs["marginal_cost"] = costs["VOM"] + (
        costs["fuel"] + co2_price * costs["CO2 intensity"]
    ) / costs["efficiency"]
    return costs


# --------------------------------------------------------------------------- #
# Load and VRE generation (Open Power System Data)
# --------------------------------------------------------------------------- #


@functools.lru_cache(maxsize=2)
def _read_opsd(version: str = OPSD_VERSION) -> pd.DataFrame:
    fn = _fetch(
        OPSD_URL.format(version=version), f"opsd_time_series_60min_{version}.csv"
    )
    df = pd.read_csv(fn, index_col=0, parse_dates=[0], low_memory=False)
    # OPSD timestamps are UTC; drop the tz so snapshots are naive like PyPSA's.
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    return df


def opsd_coverage(countries: list[str], version: str = OPSD_VERSION) -> pd.DataFrame:
    """Report which OPSD columns exist for each country (diagnostic helper)."""
    df = _read_opsd(version)
    rows = []
    for c in countries:
        row = {"country": c}
        row["load"] = next(
            (p for p in _LOAD_PATTERNS if f"{c}{p}" in df.columns), None
        )
        for carrier, tmpl in VRE_COLUMNS.items():
            row[carrier] = tmpl.format(c=c) in df.columns
        row["wind_total"] = VRE_WIND_TOTAL.format(c=c) in df.columns
        rows.append(row)
    return pd.DataFrame(rows).set_index("country")


def load_demand(
    countries: list[str], snapshots: pd.DatetimeIndex, version: str = OPSD_VERSION
) -> pd.DataFrame:
    """
    Hourly electricity demand in MW, indexed by ``snapshots``, one column per
    country. Raises if a country or time range is not covered.
    """
    df = _read_opsd(version)
    out = {}
    for c in countries:
        col = next((f"{c}{p}" for p in _LOAD_PATTERNS if f"{c}{p}" in df.columns), None)
        if col is None:
            raise KeyError(
                f"OPSD {version} has no load series for {c!r}. "
                f"Available: {sorted({x.split('_')[0] for x in df.columns})}"
            )
        s = df[col]
        # Prefer transparency, fill gaps from power statistics where available.
        alt = f"{c}{_LOAD_PATTERNS[1]}"
        if alt in df.columns and alt != col:
            s = s.fillna(df[alt])
        out[c] = s
    demand = pd.DataFrame(out)

    missing = snapshots.difference(demand.index)
    if len(missing):
        raise KeyError(
            f"OPSD {version} does not cover {len(missing)} requested snapshots "
            f"({missing[0]} .. {missing[-1]}). Dataset spans "
            f"{demand.index[0]} .. {demand.index[-1]}."
        )
    demand = demand.loc[snapshots]
    if demand.isna().any().any():
        n_nan = int(demand.isna().sum().sum())
        raise ValueError(
            f"{n_nan} missing load values in the requested window; "
            "pick a different week/year or supply --demand-csv."
        )
    return demand


def load_vre_generation(
    countries: list[str], snapshots: pd.DatetimeIndex, version: str = OPSD_VERSION
) -> pd.DataFrame:
    """
    Observed hourly VRE generation in MW with a ``(country, carrier)`` column
    MultiIndex.

    These are *measured* generation values, used directly as the upper bound of
    the corresponding UnitCommitment.jl ``Profiled`` unit. That avoids having to
    assume an installed capacity or a capacity factor -- the profiled unit can
    produce anything from 0 up to what was actually generated in that hour.

    Carriers with no OPSD coverage for a country are silently omitted.
    """
    df = _read_opsd(version)
    cols: dict[tuple[str, str], pd.Series] = {}
    for c in countries:
        have_split = any(
            VRE_COLUMNS[k].format(c=c) in df.columns for k in ("onwind", "offwind")
        )
        for carrier, tmpl in VRE_COLUMNS.items():
            col = tmpl.format(c=c)
            if col in df.columns:
                cols[(c, carrier)] = df[col]
        if not have_split and VRE_WIND_TOTAL.format(c=c) in df.columns:
            # Only fall back to aggregate wind if the split is unavailable,
            # otherwise onshore + offshore would be double counted.
            cols[(c, "wind")] = df[VRE_WIND_TOTAL.format(c=c)]

    if not cols:
        return pd.DataFrame(
            index=snapshots, columns=pd.MultiIndex.from_tuples([], names=["country", "carrier"])
        )

    vre = pd.DataFrame(cols)
    vre.columns = pd.MultiIndex.from_tuples(vre.columns, names=["country", "carrier"])
    vre = vre.reindex(snapshots)
    # A carrier that is entirely absent over the window carries no information.
    vre = vre.dropna(axis=1, how="all")
    return vre.fillna(0.0).clip(lower=0.0)


# --------------------------------------------------------------------------- #
# Power plant fleet (powerplantmatching)
# --------------------------------------------------------------------------- #

#: PyPSA-Eur's carrier / technology harmonisation
#: (scripts/add_electricity.load_and_aggregate_powerplants).
CARRIER_DICT = {
    "ocgt": "OCGT",
    "ccgt": "CCGT",
    "bioenergy": "biomass",
    "ccgt, thermal": "CCGT",
    "hard coal": "coal",
}
TECH_DICT = {
    "Run-Of-River": "ror",
    "Reservoir": "hydro",
    "Pumped Storage": "PHS",
}


# --------------------------------------------------------------------------- #
# Cross-border physical flows (Energy-Charts)
# --------------------------------------------------------------------------- #

#: Hourly cross-border physical flows per interconnector. No PyPSA dataset has
#: these: OPSD carries no flow columns and PyPSA-Eur computes flows endogenously.
#: Energy-Charts republishes ENTSO-E's and needs no API key.
ENERGY_CHARTS_CBPF = "https://api.energy-charts.info/cbpf"

#: The API reports flows in GW while its power series are in MW.
ENERGY_CHARTS_FLOW_UNIT_MW = 1000.0

#: Country names as the API spells them, mapped to ISO-2.
_EC_COUNTRY_TO_ISO2 = {
    "Austria": "AT", "Belgium": "BE", "Bulgaria": "BG", "Switzerland": "CH",
    "Czech Republic": "CZ", "Czechia": "CZ", "Germany": "DE", "Denmark": "DK",
    "Estonia": "EE", "Spain": "ES", "Finland": "FI", "France": "FR",
    "United Kingdom": "GB", "Great Britain": "GB", "Greece": "GR",
    "Croatia": "HR", "Hungary": "HU", "Ireland": "IE", "Italy": "IT",
    "Lithuania": "LT", "Luxembourg": "LU", "Latvia": "LV",
    "Montenegro": "ME", "North Macedonia": "MK", "Netherlands": "NL",
    "Norway": "NO", "Poland": "PL", "Portugal": "PT", "Romania": "RO",
    "Serbia": "RS", "Sweden": "SE", "Slovenia": "SI", "Slovakia": "SK",
    "Bosnia and Herzegovina": "BA", "Bosnia-Herzegovina": "BA",
    "Albania": "AL", "Kosovo": "XK", "Malta": "MT",
    # Non-European-Union neighbours that still exchange power with the set:
    # the Baltics and Finland with Russia and Belarus, Poland/Slovakia/Hungary/
    # Romania with Ukraine and Moldova, Bulgaria and Greece with Turkey.
    "Russia": "RU", "Belarus": "BY", "Ukraine": "UA", "Moldova": "MD",
    "Turkey": "TR", "Georgia": "GE",
}


def load_cross_border_flows(
    countries: list[str], snapshots: pd.DatetimeIndex
) -> pd.DataFrame:
    """
    Historical hourly cross-border physical flows, in MW, with a
    ``(country, neighbour)`` column MultiIndex.

    Positive values are net *imports* into ``country`` from ``neighbour``.
    The API returns 15-minute data in GW; this resamples to the snapshot
    frequency and converts to MW.

    Note that physical flows include loop flows, so they differ slightly from
    scheduled commercial exchanges.
    """
    import json
    import urllib.parse

    start = (snapshots[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    end = (snapshots[-1] + pd.Timedelta(days=2)).strftime("%Y-%m-%d")

    frames = {}
    for country in countries:
        query = urllib.parse.urlencode(
            {"country": country.lower(), "start": start, "end": end}
        )
        url = f"{ENERGY_CHARTS_CBPF}?{query}"
        cached = _fetch(url, f"cbpf_{country}_{start}_{end}.json")
        payload = json.loads(cached.read_text())
        if not payload.get("countries"):
            logger.warning("no cross-border flow data for %s", country)
            continue
        index = pd.to_datetime(payload["unix_seconds"], unit="s")
        for series in payload["countries"]:
            name = series["name"]
            if name == "sum":
                continue
            iso2 = _EC_COUNTRY_TO_ISO2.get(name)
            if iso2 is None:
                # Skipping a border would silently delete real imports and make
                # the instance look inadequate, so refuse rather than warn.
                raise KeyError(
                    f"Energy-Charts reports a border between {country} and "
                    f"{name!r}, which is not in _EC_COUNTRY_TO_ISO2. Add it: "
                    "dropping the border would silently remove real exchanges."
                )
            s = pd.Series(series["data"], index=index, dtype=float)
            s = s * ENERGY_CHARTS_FLOW_UNIT_MW
            # 15-minute physical flows -> mean over each snapshot interval.
            step = snapshots[1] - snapshots[0] if len(snapshots) > 1 else None
            if step is not None:
                s = s.resample(step).mean()
            frames[(country, iso2)] = s.reindex(snapshots)

    if not frames:
        return pd.DataFrame(
            index=snapshots,
            columns=pd.MultiIndex.from_tuples([], names=["country", "neighbour"]),
        )

    flows = pd.DataFrame(frames)
    flows.columns = pd.MultiIndex.from_tuples(
        flows.columns, names=["country", "neighbour"]
    )
    missing = flows.isna().sum().sum()
    if missing:
        raise ValueError(
            f"{int(missing)} missing cross-border flow values in the requested "
            "window; Energy-Charts may not cover this period"
        )
    return flows


# --------------------------------------------------------------------------- #
# NUTS3 regions, population and GDP (Eurostat)
# --------------------------------------------------------------------------- #

#: PyPSA-Eur's demand key: 60% GDP, 40% population per NUTS3 region
#: (`load: distribution_key`, build_electricity_demand_base.py).
NUTS3_GEOMETRY_URL = (
    "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/"
    "NUTS_RG_10M_2021_4326_LEVL_3.geojson"
)
EUROSTAT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "{dataset}?format=JSON&lang=EN&time={year}{extra}"
)
GDP_WEIGHT = 0.6
POPULATION_WEIGHT = 0.4


def _eurostat_series(dataset: str, year: int, extra: str = "") -> pd.Series:
    """
    One Eurostat table as a Series indexed by NUTS code.

    The JSON-stat payload stores values in a flat dict keyed by the linear
    index over all dimensions; here only ``geo`` varies, so that index is the
    geo index.
    """
    import json

    fn = _fetch(
        EUROSTAT_URL.format(dataset=dataset, year=year, extra=extra),
        f"eurostat_{dataset}_{year}.json",
    )
    payload = json.loads(fn.read_text())
    geo_index = payload["dimension"]["geo"]["category"]["index"]
    sizes = payload["size"]
    n_geo = sizes[payload["id"].index("geo")]
    if n_geo != len(geo_index):
        raise ValueError(f"unexpected Eurostat geo dimension for {dataset}")
    # Any dimension other than geo must be a singleton for the flat index to
    # reduce to the geo index; the URL pins unit and time so it should be.
    if any(sz != 1 for dim, sz in zip(payload["id"], sizes) if dim != "geo"):
        raise ValueError(
            f"Eurostat {dataset} returned more than one slice; pin unit/time"
        )
    values = payload["value"]
    return pd.Series(
        {code: values.get(str(i)) for code, i in geo_index.items()}, dtype=float
    ).dropna()


@functools.lru_cache(maxsize=4)
def load_nuts3_keys(year: int = 2019) -> pd.DataFrame:
    """
    NUTS3 regions with their centroid, population and GDP.

    Returns a GeoDataFrame indexed by NUTS3 code with ``country``, the region
    ``geometry``, its centroid ``lat``/``lon``, ``pop`` (thousands) and ``gdp``
    (million EUR). The geometry is what lets demand be spread over every
    substation inside a region rather than piled onto one.
    """
    import geopandas as gpd

    fn = _fetch(NUTS3_GEOMETRY_URL, "nuts3_regions.geojson")
    regions = gpd.read_file(fn).set_index("NUTS_ID")

    population = _eurostat_series("nama_10r_3popgdp", year)
    gdp = _eurostat_series("nama_10r_3gdp", year, extra="&unit=MIO_EUR")

    # Centroids via an equal-area projection so they are not distorted by
    # latitude, then back to lat/lon.
    centroids = regions.geometry.to_crs(epsg=3035).centroid.to_crs(epsg=4326)
    out = gpd.GeoDataFrame(
        {
            "country": regions["CNTR_CODE"],
            "lat": centroids.y,
            "lon": centroids.x,
            "pop": population.reindex(regions.index),
            "gdp": gdp.reindex(regions.index),
        },
        geometry=regions.geometry,
        crs=regions.crs,
    )
    return out.dropna(subset=["lat", "lon"])


# --------------------------------------------------------------------------- #
# Measured generation by carrier (Energy-Charts)
# --------------------------------------------------------------------------- #

ENERGY_CHARTS_PUBLIC_POWER = "https://api.energy-charts.info/public_power"

#: Every Energy-Charts carrier, classified against what this pipeline already
#: models. Exhaustive on purpose: an unknown name raises, because guessing
#: either double-counts capacity or deletes it.
#:   metadata   = not generation      modelled = already represented
#:   supplement = real generation with no other source here
EC_CARRIER_CLASS = {
    # -- not generation ----------------------------------------------------
    "Load": "metadata",
    "Residual load": "metadata",
    "Renewable share of load": "metadata",
    "Renewable share of generation": "metadata",
    "Cross border electricity trading": "metadata",
    "Hydro pumped storage consumption": "metadata",
    # -- already modelled --------------------------------------------------
    "Nuclear": "modelled",                      # thermal, powerplantmatching
    "Fossil gas": "modelled",                   # CCGT / OCGT
    "Fossil hard coal": "modelled",             # coal
    "Fossil brown coal / lignite": "modelled",  # lignite
    "Fossil oil": "modelled",                   # oil
    "Biomass": "modelled",                      # biomass / solid biomass
    "Solar": "modelled",                        # OPSD profiled
    "Wind onshore": "modelled",                 # OPSD profiled
    "Wind offshore": "modelled",                # OPSD profiled
    "Hydro Run-of-River": "modelled",           # ror, bounded by capacity
    "Hydro pumped storage": "modelled",         # PHS storage unit
    # -- supplement: real generation with no other source here -------------
    # Reservoir hydro needs an hourly inflow series that no free dataset
    # provides; the rest have no technology-data cost entry, so they never
    # reach the thermal fleet. Sweden alone runs 8.3 GW of reservoir hydro.
    "Hydro water reservoir": "supplement",
    "Geothermal": "supplement",
    "Waste": "supplement",
    "Others": "supplement",
    "Other renewables": "supplement",
    "Fossil coal-derived gas": "supplement",    # blast-furnace / coke-oven gas
    "Fossil peat": "supplement",
    # Estonia's oil shale fleet is absent from powerplantmatching entirely --
    # its only Estonian "oil" unit is the 251 MW Kiisa emergency reserve, not
    # the ~1.6 GW Narva stations -- so this supplements rather than duplicates.
    "Fossil oil shale": "supplement",
}


def load_measured_generation(
    countries: list[str], snapshots: pd.DatetimeIndex
) -> pd.DataFrame:
    """
    Measured hourly generation in MW for carriers this pipeline does not model,
    with a ``(country, carrier)`` column MultiIndex.

    Used as the upper bound of a profiled unit, exactly as OPSD measured wind
    and solar are: the unit may produce anything between zero and what the
    carrier actually generated that hour. Nothing is assumed about capacity.
    """
    import json
    import urllib.parse

    start = (snapshots[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    end = (snapshots[-1] + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
    step = snapshots[1] - snapshots[0] if len(snapshots) > 1 else None

    frames = {}
    for country in countries:
        query = urllib.parse.urlencode(
            {"country": country.lower(), "start": start, "end": end}
        )
        cached = _fetch(
            f"{ENERGY_CHARTS_PUBLIC_POWER}?{query}",
            f"public_power_{country}_{start}_{end}.json",
        )
        payload = json.loads(cached.read_text())
        if not payload.get("production_types"):
            logger.warning("no measured generation for %s", country)
            continue
        index = pd.to_datetime(payload["unix_seconds"], unit="s")
        for series in payload["production_types"]:
            name = series["name"]
            if not isinstance(name, str):
                name = name[0]
            kind = EC_CARRIER_CLASS.get(name)
            if kind is None:
                raise KeyError(
                    f"Energy-Charts reports carrier {name!r} for {country}, which "
                    "is not classified in EC_CARRIER_CLASS. Classify it as "
                    "'modelled' (already represented) or 'supplement' (add it): "
                    "ignoring it would silently drop real generation."
                )
            if kind != "supplement":
                continue
            s = pd.Series(series["data"], index=index, dtype=float).clip(lower=0.0)
            if step is not None:
                s = s.resample(step).mean()
            s = s.reindex(snapshots).ffill().fillna(0.0)
            if s.max() <= 0:
                continue
            frames[(country, name)] = s

    if not frames:
        return pd.DataFrame(
            index=snapshots,
            columns=pd.MultiIndex.from_tuples([], names=["country", "carrier"]),
        )
    out = pd.DataFrame(frames)
    out.columns = pd.MultiIndex.from_tuples(out.columns, names=["country", "carrier"])
    return out


# --------------------------------------------------------------------------- #
# Transmission grid (PyPSA-Eur osm-prebuilt)
# --------------------------------------------------------------------------- #

#: The prebuilt OSM transmission grid PyPSA-Eur feeds to its `base_network`
#: rule (its data/versions.csv, dataset "osm").
OSM_VERSION = "0.7"
OSM_URL = "https://data.pypsa.org/workflows/eur/osm/{version}/{component}.csv"
OSM_COMPONENTS = ("buses", "lines", "transformers", "links", "converters")

#: The geometry column is quoted with single quotes ('LINESTRING (x y, x y)'),
#: so the default quotechar leaves its commas unescaped. Reading these files
#: without this silently returns shifted, wrong columns rather than raising.
OSM_QUOTECHAR = "'"


def _osm_bool(series: pd.Series) -> pd.Series:
    """OSM CSVs encode booleans as 't'/'f'."""
    return series.astype(str).str.strip().str.lower().isin(["t", "true", "1"])


@functools.lru_cache(maxsize=2)
def load_osm_grid(
    version: str = OSM_VERSION, force: bool = False
) -> dict[str, pd.DataFrame]:
    """
    The prebuilt OSM European transmission grid, as a dict of DataFrames keyed
    by component name.

    ``buses`` carries ``bus_id, voltage (kV), dc, country, x, y``;
    ``lines`` carries ``bus0, bus1, voltage, circuits, s_nom (MVA), r, x
    (ohm), length (m)``; ``transformers`` carries ``bus0, bus1, s_nom``;
    ``links`` are HVDC.
    """
    out = {}
    for component in OSM_COMPONENTS:
        fn = _fetch(
            OSM_URL.format(version=version, component=component),
            f"osm_{version}_{component}.csv",
            force=force,
        )
        df = pd.read_csv(fn, quotechar=OSM_QUOTECHAR, low_memory=False)
        for col in ("dc", "under_construction", "underground"):
            if col in df.columns:
                df[col] = _osm_bool(df[col])
        out[component] = df

    buses = out["buses"]
    if not buses.bus_id.is_unique:
        raise ValueError("OSM buses.csv has duplicate bus_id values")
    for component in ("lines", "transformers"):
        df = out[component]
        known = set(buses.bus_id)
        missing = (~df.bus0.isin(known)) | (~df.bus1.isin(known))
        if missing.any():
            raise ValueError(
                f"OSM {component}.csv references {int(missing.sum())} unknown "
                "buses; the file was probably parsed with the wrong quotechar"
            )
    return out


#: The matched fleet that powerplantmatching publishes alongside the package.
#: Using it avoids rebuilding the database from its ~15 upstream sources, which
#: downloads several GB and takes tens of minutes. `rebuild=True` runs the full
#: local match instead.
PPM_PREBUILT_URL = (
    "https://raw.githubusercontent.com/PyPSA/powerplantmatching/master/powerplants.csv"
)
PPL_CACHE = "powerplants_harmonised.csv"


def _harmonise(ppl: pd.DataFrame) -> pd.DataFrame:
    """
    Apply PyPSA-Eur's fleet harmonisation: ISO-2 country codes, PyPSA column
    names, and PyPSA carrier names.

    ``convert_country_to_alpha2`` must run before ``to_pypsa_names`` because it
    reads the original ``Country`` column.
    """
    import powerplantmatching  # noqa: F401  (registers the .powerplant accessor)

    if "Country" in ppl.columns:
        ppl = ppl.powerplant.convert_country_to_alpha2()
    if "Fueltype" in ppl.columns:
        ppl = ppl.powerplant.to_pypsa_names()
    ppl = ppl.rename(columns=str.lower).replace(
        {"carrier": CARRIER_DICT, "technology": TECH_DICT}
    )
    # Natural gas and hydro are resolved to their technology (OCGT/CCGT,
    # hydro/PHS/ror), as in PyPSA-Eur. Idempotent.
    ppl["carrier"] = ppl.carrier.where(
        ~ppl.carrier.isin(["hydro", "natural gas"]), ppl.technology
    )
    return ppl


@functools.lru_cache(maxsize=1)
def _harmonised_fleet() -> pd.DataFrame:
    """The full harmonised European fleet, fetched once and memoised."""
    cache = CACHE_DIR / PPL_CACHE
    if cache.exists():
        return pd.read_csv(cache, index_col=0)
    ppl = _harmonise(
        pd.read_csv(_fetch(PPM_PREBUILT_URL, "ppm_powerplants.csv"), index_col=0)
    )
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ppl.to_csv(cache)
    logger.info("cached harmonised fleet to %s", cache)
    return ppl


def load_powerplants(
    countries: list[str], year: int | None = None
) -> pd.DataFrame:
    """
    Existing power plant fleet from the matched dataset powerplantmatching
    publishes, harmonised to PyPSA names and cached after the first fetch.

    One row per unit with ``name``, ``carrier``, ``p_nom`` (MW), ``country``
    (ISO-2), ``efficiency``, ``lat``/``lon``, ``datein``/``dateout``, and
    ``max_hours`` for storage.

    ``year`` drops units commissioned after, or retired before, that year;
    units with no dates are kept. For Belgium in 2019 this correctly removes
    the coal fleet, all of which retired by 2016.
    """
    ppl = _harmonised_fleet()

    unknown = set(countries) - set(ppl.country.unique())
    if unknown:
        raise KeyError(
            f"no powerplant data for {sorted(unknown)}; the fleet covers "
            f"{sorted(ppl.country.dropna().unique())}"
        )

    ppl = ppl[ppl.country.isin(countries)].copy()
    if year is not None:
        keep = (ppl.datein.isna() | (ppl.datein <= year)) & (
            ppl.dateout.isna() | (ppl.dateout >= year)
        )
        ppl = ppl[keep]
    ppl = ppl[ppl.p_nom > 0]
    return ppl.reset_index(drop=True)
