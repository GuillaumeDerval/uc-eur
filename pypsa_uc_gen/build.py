"""
Assemble a PyPSA network for a given geography and week from the public
datasets in :mod:`pypsa_uc_gen.sources`.

The network is operational only: nothing is extendable, there is no investment,
and every capacity is an existing unit from powerplantmatching placed on the
real transmission grid from PyPSA-Eur's osm-prebuilt dataset.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pypsa

from . import sources

logger = logging.getLogger(__name__)

#: Carriers modelled as dispatchable thermal units with 0-1 commitment.
THERMAL_CARRIERS = [
    "nuclear", "coal", "lignite", "CCGT", "OCGT", "oil", "biomass", "solid biomass",
]

#: OPSD VRE carrier -> the powerplantmatching rows that locate it.
VRE_PPM_MATCH = {
    "solar": ("solar", None),
    "onwind": ("wind", "Onshore"),
    "offwind": ("wind", "Offshore"),
    "wind": ("wind", None),
}

#: Energy-Charts carriers added as profiled units: PyPSA carrier name, and the
#: powerplantmatching carrier used to site them (None = spread evenly).
SUPPLEMENT_CARRIERS = {
    "Hydro water reservoir": ("hydro reservoir", "hydro"),
    "Geothermal": ("geothermal", "geothermal"),
    "Waste": ("waste", "waste"),
    "Fossil oil shale": ("oil shale", None),
    "Fossil peat": ("peat", None),
    "Fossil coal-derived gas": ("coal-derived gas", None),
    "Others": ("other", None),
    "Other renewables": ("other renewable", None),
}

#: Transformers have a rating but no impedance in osm-prebuilt. DC-OPF needs a
#: finite susceptance on every branch, so they get a standard per-unit value.
TRANSFORMER_X_PU = 0.1


class BuildReport(dict):
    """Provenance and exclusion notes accumulated while building the network."""

    def note(self, key: str, msg: str) -> None:
        self.setdefault(key, []).append(msg)

    def render(self) -> str:
        lines = []
        for key, msgs in self.items():
            lines.append(f"{key}:")
            lines.extend(f"  - {m}" for m in msgs)
        return "\n".join(lines)


def snapshots_for(
    year: int,
    week: int | None = None,
    start: str | pd.Timestamp | None = None,
    hours: int = 168,
) -> pd.DatetimeIndex:
    """
    Hourly snapshot index.

    Either ``week`` (ISO week, starting Monday 00:00 UTC) or an explicit
    ``start`` timestamp must be given.
    """
    if start is not None:
        origin = pd.Timestamp(start)
    elif week is not None:
        origin = pd.Timestamp.fromisocalendar(year, week, 1)
    else:
        raise ValueError("provide either week= or start=")
    return pd.date_range(origin, periods=hours, freq="h", name="snapshot")


def unique_ids(frame: pd.DataFrame) -> pd.Series:
    """
    Unique component names for a fleet.

    Sites often host several units under one name -- "Emile Huchet" covers coal,
    CCGT and lignite units -- and PyPSA silently overwrites a component added
    under an existing name. Already-unique names are left alone so instances
    stay readable; colliding ones gain their carrier, then a counter.
    """
    base = frame["name"].astype(str).str.strip()
    ids = base.where(
        ~base.duplicated(keep=False),
        base + " (" + frame["carrier"].astype(str) + ")",
    )
    dup = ids.duplicated(keep=False)
    if dup.any():
        ids = ids.where(~dup, ids + " #" + (ids.groupby(ids).cumcount() + 1).astype(str))
    return ids


def _haversine_km(lat, lon, bus_lat, bus_lon) -> np.ndarray:
    """Great-circle distance in km from every point to every bus."""
    la1, lo1 = np.radians(lat)[:, None], np.radians(lon)[:, None]
    la2, lo2 = np.radians(bus_lat)[None, :], np.radians(bus_lon)[None, :]
    d = (
        np.sin((la2 - la1) / 2) ** 2
        + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(d, 0.0, 1.0)))


def _haversine_nearest(lat, lon, bus_lat, bus_lon) -> np.ndarray:
    """Index of the nearest bus for each point, by great-circle distance."""
    return np.argmin(_haversine_km(lat, lon, bus_lat, bus_lon), axis=1)


def connection_capacity(buses: list[str], n: pypsa.Network) -> pd.Series:
    """
    Total rating of the branches incident on each bus, in MW.

    Splitting a region's demand equally would hand a radial dead-end the same
    load as a meshed hub: in Sweden that put 2175 MW behind one 1877 MW line.
    """
    cap = pd.Series(0.0, index=list(buses))
    for frame in (n.lines, n.transformers):
        if not len(frame):
            continue
        rating = frame.s_nom.astype(float)
        for bus_col in ("bus0", "bus1"):
            grouped = rating.groupby(frame[bus_col]).sum()
            cap = cap.add(grouped.reindex(cap.index).fillna(0.0), fill_value=0.0)
    return cap


def real_substations(buses: list[str], n: pypsa.Network) -> list[str]:
    """
    The buses that are real substations.

    osm-prebuilt splits long lines at tee points, naming those nodes
    ``virtual_*`` (29% of European buses). Attaching demand or a plant to one
    puts it mid-line, where only that line's rating can serve it. PyPSA-Eur
    avoids this with `load: substation_only: true`.
    """
    real = [b for b in buses if not str(b).startswith("virtual")]
    return real or list(buses)


#: Regions further than this from any substation are off the synchronous grid
#: (overseas departements, the Canaries, Corsica) and absent from the national
#: load series. Mainland regions are within 110 km; those are 150-8700 km.
MAX_REGION_TO_GRID_KM = 150.0


def _nearest_buses(frame: pd.DataFrame, buses: list[str], n: pypsa.Network) -> pd.Series:
    # Plants connect at substations too, never at a line's tee point.
    buses = real_substations(buses, n)
    sub = n.buses.loc[buses]
    idx = _haversine_nearest(
        frame.lat.to_numpy(float), frame.lon.to_numpy(float),
        sub.y.to_numpy(float), sub.x.to_numpy(float),
    )
    return pd.Series(sub.index.to_numpy()[idx], index=frame.index)


def add_grid(
    n: pypsa.Network, countries: list[str], report: BuildReport
) -> tuple[dict[str, list[str]], dict[tuple[str, str], pd.Series]]:
    """
    Add the real AC transmission grid from osm-prebuilt, restricted to
    ``countries``.

    HVDC links are dropped: UnitCommitment.jl 0.4 has no controllable branch.
    Only the largest connected AC component is kept, since isolated islands
    cannot exchange power and would silently distort the instance.

    Returns each country's buses, and the share of each country-neighbour
    border entering at each bus (used to site historical imports).
    """
    grid = sources.load_osm_grid()
    buses, lines = grid["buses"], grid["lines"]
    transformers, links = grid["transformers"], grid["links"]

    country_of = buses.set_index("bus_id").country
    buses = buses[buses.country.isin(countries) & ~buses.dc]
    if "under_construction" in buses.columns:
        buses = buses[~buses.under_construction]
    kept = set(buses.bus_id)

    def internal(df, within):
        sel = df.bus0.isin(within) & df.bus1.isin(within)
        if "under_construction" in df.columns:
            sel &= ~df.under_construction
        return df[sel]

    # Border buses, computed before the internal-only filter discards the
    # cross-border branches they are derived from.
    border: dict[tuple[str, str], pd.Series] = {}
    for df, rating in ((lines, "s_nom"), (links, "p_nom")):
        for _, row in df[df.bus0.isin(kept) ^ df.bus1.isin(kept)].iterrows():
            inside, outside = (
                (row.bus0, row.bus1) if row.bus0 in kept else (row.bus1, row.bus0)
            )
            home, away = country_of.get(inside), country_of.get(outside)
            if home is None or away is None or away in countries:
                continue
            w = border.setdefault((home, away), pd.Series(dtype=float))
            w[inside] = w.get(inside, 0.0) + float(row[rating])

    ac_lines = internal(lines, kept)
    ac_transformers = internal(transformers, kept)

    dropped = links[links.bus0.isin(kept) | links.bus1.isin(kept)]
    if len(dropped):
        report.note(
            "topology",
            f"dropped {len(dropped)} HVDC links ({dropped.p_nom.sum():.0f} MW): "
            "UnitCommitment.jl 0.4 has no controllable branch component",
        )

    # Largest connected AC component.
    adj: dict[str, set] = {b: set() for b in kept}
    for df in (ac_lines, ac_transformers):
        for b0, b1 in zip(df.bus0, df.bus1):
            adj[b0].add(b1)
            adj[b1].add(b0)
    seen, best = set(), set()
    for start in adj:
        if start in seen:
            continue
        comp, stack = set(), [start]
        while stack:
            b = stack.pop()
            if b not in comp:
                comp.add(b)
                stack.extend(adj[b] - comp)
        seen |= comp
        if len(comp) > len(best):
            best = comp
    if len(best) < len(kept):
        report.note(
            "topology",
            f"kept the largest connected AC component: {len(best)} of {len(kept)} "
            f"buses ({len(kept) - len(best)} dropped as isolated)",
        )

    buses = buses[buses.bus_id.isin(best)]
    ac_lines = internal(ac_lines, best)
    ac_transformers = internal(ac_transformers, best)

    n.add(
        "Bus", buses.bus_id.values, carrier="AC",
        v_nom=buses.voltage.values, x=buses.x.values, y=buses.y.values,
        country=buses.country.values,
    )
    # osm-prebuilt gives r and x in ohms for the whole branch and s_nom in MVA,
    # which is what PyPSA expects; it derives per-unit values from the bus v_nom.
    n.add(
        "Line", ac_lines.line_id.values,
        bus0=ac_lines.bus0.values, bus1=ac_lines.bus1.values,
        r=ac_lines.r.values, x=ac_lines.x.values, s_nom=ac_lines.s_nom.values,
        length=ac_lines.length.values / 1e3,
    )
    if len(ac_transformers):
        n.add(
            "Transformer", ac_transformers.transformer_id.values,
            bus0=ac_transformers.bus0.values, bus1=ac_transformers.bus1.values,
            s_nom=ac_transformers.s_nom.values, type="", x=TRANSFORMER_X_PU,
        )
        report.note(
            "topology",
            f"{len(ac_transformers)} transformers carry no impedance in "
            f"osm-prebuilt; given x={TRANSFORMER_X_PU} p.u. so DC-OPF has a "
            "finite susceptance on every branch",
        )

    report.note(
        "topology",
        f"osm-prebuilt {sources.OSM_VERSION}: {len(buses)} AC buses, "
        f"{len(ac_lines)} lines, {len(ac_transformers)} transformers, "
        f"{sorted(set(buses.voltage.dropna().astype(int)))} kV",
    )

    border = {k: v[v.index.isin(best)] for k, v in border.items()}
    border = {k: v / v.sum() for k, v in border.items() if v.sum() > 0}
    return (
        {c: buses.bus_id[buses.country == c].tolist() for c in countries},
        border,
    )


def fleet_for(
    countries: list[str], year: int, min_capacity: float = 10.0
) -> pd.DataFrame:
    """
    The fleet an instance would contain, with the same ``uid`` values its
    generators are named by.

    Lets a caller pick units to remove (see ``drop_units``) without having to
    build the network first.
    """
    ppl = sources.load_powerplants(countries, year=year)
    if min_capacity > 0:
        ppl = ppl[ppl.p_nom >= min_capacity]
    return ppl.assign(uid=unique_ids(ppl))


def build_network(
    countries: list[str],
    snapshots: pd.DatetimeIndex,
    *,
    costs_year: int = 2020,
    co2_price: float = 0.0,
    min_capacity: float = 10.0,
    imports: str = "historical",
    drop_units: tuple[str, ...] = (),
    import_cost: float = 0.0,
    initial_conditions: str = "free",
    ppl: pd.DataFrame | None = None,
    grid: tuple | None = None,
) -> tuple[pypsa.Network, BuildReport]:
    """
    Build an operational nodal PyPSA network.

    ``imports`` is ``"historical"`` (observed cross-border flows pinned on every
    border leaving the selection) or ``"none"``.

    ``initial_conditions`` is ``"free"``, ``"on"`` or ``"off"``. It only sets
    the PyPSA ``up_time_before`` / ``down_time_before`` attributes; the
    converter decides whether to assert them at all, and under ``"free"`` it
    omits the initial state entirely.
    """
    report = BuildReport()
    n = pypsa.Network()
    n.set_snapshots(snapshots)
    year = int(snapshots[0].year)

    # ----------------------------------------------------------------- grid
    country_buses, border_buses = (
        grid if grid is not None else add_grid(n, countries, report)
    )
    empty = [c for c in countries if not country_buses.get(c)]
    if empty:
        raise ValueError(f"osm-prebuilt has no connected AC buses for {empty}")

    # --------------------------------------------------------------- demand
    demand = sources.load_demand(countries, snapshots)
    for c in countries:
        buses = country_buses[c]
        shares, how = _load_bus_shares(c, buses, n, year)
        for bus, share in shares.items():
            if share <= 0:
                continue
            n.add(
                "Load", f"load {bus}", bus=bus, carrier="electricity",
                p_set=demand[c].values * share,
            )
        report.note("demand", f"{c}: {how}")
    report.note(
        "demand",
        f"OPSD {sources.OPSD_VERSION} entsoe transparency, peak "
        f"{demand.sum(axis=1).max():.0f} MW / mean {demand.sum(axis=1).mean():.0f} MW",
    )

    # -------------------------------------------------------------- imports
    if imports == "historical":
        flows = sources.load_cross_border_flows(countries, snapshots)
        # Borders between two selected countries are already modelled by their
        # interconnector; imposing history there too would fabricate energy.
        external = [(c, nb) for (c, nb) in flows.columns if nb not in countries]
        net = 0.0
        for country, neighbour in external:
            series = flows[(country, neighbour)]
            imp, exp = series.clip(lower=0.0), (-series).clip(lower=0.0)
            net += series.mean()
            shares = border_buses.get((country, neighbour))
            if shares is None or shares.empty:
                shares = pd.Series(
                    1.0, index=[n.buses.loc[country_buses[country]].v_nom.idxmax()]
                )
            for bus, share in shares.items():
                if imp.max() > 0:
                    n.add(
                        "Generator", f"import {country}<-{neighbour} @ {bus}",
                        bus=bus, carrier="import",
                        p_nom=float(imp.max()) * share,
                        p_max_pu=(imp / imp.max()).values, p_min_pu=0.0,
                        marginal_cost=import_cost, committable=False,
                    )
                if exp.max() > 0:
                    n.add(
                        "Load", f"export {country}->{neighbour} @ {bus}",
                        bus=bus, carrier="export", p_set=(exp * share).values,
                    )
        if external:
            report.note(
                "imports",
                "historical cross-border physical flows from Energy-Charts "
                f"(ENTSO-E) across {len(external)} borders, net {net:.0f} MW mean; "
                "imports are curtailable, exports are fixed load",
            )
            inside = sorted(
                {"-".join(sorted((c, nb))) for c, nb in flows.columns if nb in countries}
            )
            if inside:
                report.note(
                    "imports",
                    f"borders inside the selection stay endogenous: {inside}",
                )
        else:
            report.note("imports", "no external borders for this selection")

    # ---------------------------------------------------------------- fleet
    if ppl is None:
        ppl = sources.load_powerplants(countries, year=year)
    if min_capacity > 0:
        small = ppl[ppl.p_nom < min_capacity]
        ppl = ppl[ppl.p_nom >= min_capacity]
        if len(small):
            report.note(
                "fleet",
                f"dropped {len(small)} units below {min_capacity:g} MW "
                f"({small.p_nom.sum():.0f} MW, "
                f"{100 * small.p_nom.sum() / (small.p_nom.sum() + ppl.p_nom.sum()):.1f}%"
                " of fleet capacity)",
            )
    ppl = ppl.assign(uid=unique_ids(ppl))

    if drop_units:
        # Fail on an unknown name rather than quietly building the intact
        # system under an outage label.
        unknown = set(drop_units) - set(ppl.uid)
        if unknown:
            raise KeyError(
                f"cannot remove unknown unit(s) {sorted(unknown)}; "
                "use build.fleet_for() to list valid uids"
            )
        removed = ppl[ppl.uid.isin(drop_units)]
        ppl = ppl[~ppl.uid.isin(drop_units)]
        report.note(
            "outage",
            f"removed {len(removed)} unit(s), {removed.p_nom.sum():.0f} MW: "
            + ", ".join(
                f"{r.uid} ({r.carrier}, {r.p_nom:.0f} MW)"
                for r in removed.itertuples()
            ),
        )

    ppl = ppl.assign(bus=_assign_buses(ppl, country_buses, n, report))

    costs = sources.load_costs(costs_year, co2_price=co2_price)
    uc = sources.load_unit_commitment_params()

    # ----------------------------------------------- thermal (committable)
    thermal = ppl[ppl.carrier.isin(THERMAL_CARRIERS)]
    missing_uc = sorted(set(thermal.carrier) - set(uc.columns))
    if missing_uc:
        report.note(
            "unit commitment",
            f"no PyPSA-Eur UC parameters for {missing_uc}; these get PyPSA "
            "defaults (no min up/down time, p_min_pu=0, free ramping)",
        )

    for _, row in thermal.iterrows():
        carrier = row.carrier
        p_nom = float(row.p_nom)
        col = uc[carrier] if carrier in uc.columns else None

        def par(attr, default):
            if col is None or attr not in col.index or pd.isna(col[attr]):
                return default
            return float(col[attr])

        eff = row.get("efficiency", np.nan)
        if pd.isna(eff) and carrier in costs.index:
            eff = costs.at[carrier, "efficiency"]
        if pd.isna(eff) or eff <= 0:
            eff = 1.0
        if carrier not in costs.index:
            raise KeyError(f"no cost data for carrier {carrier!r}")
        marginal = costs.at[carrier, "VOM"] + (
            costs.at[carrier, "fuel"] + co2_price * costs.at[carrier, "CO2 intensity"]
        ) / eff

        n.add(
            "Generator", row.uid, bus=row.bus, carrier=carrier,
            p_nom=p_nom, efficiency=float(eff), marginal_cost=float(marginal),
            committable=True,
            p_min_pu=par("p_min_pu", 0.0),
            min_up_time=int(par("min_up_time", 0)),
            min_down_time=int(par("min_down_time", 0)),
            ramp_limit_up=par("ramp_limit_up", np.nan),
            ramp_limit_down=par("ramp_limit_down", np.nan),
            ramp_limit_start_up=par("ramp_limit_start_up", 1.0),
            ramp_limit_shut_down=par("ramp_limit_shut_down", 1.0),
            # per-MW in the PyPSA-Eur table, total in PyPSA
            start_up_cost=par("start_up_cost", 0.0) * p_nom,
            up_time_before=1 if initial_conditions == "on" else 0,
            down_time_before=0 if initial_conditions == "on" else 1,
        )
    report.note(
        "fleet",
        f"{len(thermal)} committable thermal units, {thermal.p_nom.sum():.0f} MW, "
        f"carriers {sorted(thermal.carrier.unique())}",
    )

    handled = set(THERMAL_CARRIERS) | {"ror", "hydro", "PHS"} | set(VRE_PPM_MATCH)
    unhandled = ppl[~ppl.carrier.isin(handled)]
    if len(unhandled):
        by = unhandled.groupby("carrier").p_nom.agg(["count", "sum"])
        report.note(
            "fleet",
            "carriers not modelled: "
            + ", ".join(
                f"{c} ({int(r['count'])} units, {r['sum']:.0f} MW)"
                for c, r in by.iterrows()
            ),
        )

    # ------------------------------------------------------ VRE (profiled)
    vre = sources.load_vre_generation(countries, snapshots)
    for (country, carrier) in vre.columns:
        series = vre[(country, carrier)]
        peak = float(series.max())
        if peak <= 0:
            continue
        vom = float(costs.at[carrier, "VOM"]) if carrier in costs.index else 0.0
        # National total stays equal to the OPSD measurement; it is spread over
        # buses in proportion to the capacity powerplantmatching locates there.
        ppm_carrier, technology = VRE_PPM_MATCH.get(carrier, (carrier, None))
        located = ppl
        if technology is not None and "technology" in ppl.columns:
            located = ppl[ppl.technology == technology]
        for bus, share in _capacity_shares(
            located, country, ppm_carrier, country_buses[country], n
        ).items():
            n.add(
                "Generator", f"{country} {carrier} @ {bus}", bus=bus, carrier=carrier,
                p_nom=peak * share, p_max_pu=(series / peak).values, p_min_pu=0.0,
                marginal_cost=vom, committable=False,
            )
    if len(vre.columns):
        report.note(
            "vre",
            "OPSD measured generation as the hourly upper bound for "
            + ", ".join(f"{c}/{k}" for c, k in vre.columns),
        )
    no_vre = sorted(set(countries) - {c for c, _ in vre.columns})
    if no_vre:
        report.note("vre", f"no OPSD VRE generation series for {no_vre}")

    # ------------------------------- measured generation for other carriers
    # Carriers with no fleet or cost entry still generated; bound them by what
    # Energy-Charts measured, as OPSD wind and solar are bounded.
    if True:
        measured = sources.load_measured_generation(countries, snapshots)
        added = []
        for (country, ec_name) in measured.columns:
            series = measured[(country, ec_name)]
            peak = float(series.max())
            if peak <= 0:
                continue
            carrier, siting = SUPPLEMENT_CARRIERS[ec_name]
            shares = _capacity_shares(ppl, country, siting, country_buses[country], n)
            for bus, share in shares.items():
                n.add(
                    "Generator", f"{country} {carrier} @ {bus}", bus=bus,
                    carrier=carrier, p_nom=peak * share,
                    p_max_pu=(series / peak).values, p_min_pu=0.0,
                    marginal_cost=0.0, committable=False,
                )
            added.append(f"{carrier} {series.mean():.0f} MW mean")
        if added:
            report.note(
                "measured generation",
                "carriers with no fleet or cost data, bounded by Energy-Charts "
                "measured hourly generation: " + ", ".join(sorted(added)),
            )

    # ----------------------------------------------------------- hydro/ror
    ror = ppl[ppl.carrier == "ror"]
    for _, row in ror.iterrows():
        n.add(
            "Generator", row.uid, bus=row.bus, carrier="ror",
            p_nom=float(row.p_nom), p_min_pu=0.0, marginal_cost=0.0,
            committable=False,
        )
    if len(ror):
        report.note(
            "hydro",
            f"{len(ror)} run-of-river units ({ror.p_nom.sum():.0f} MW) bounded by "
            "installed capacity; no measured inflow series available",
        )
    reservoir = ppl[ppl.carrier == "hydro"]
    if len(reservoir):
        report.note(
            "hydro",
            f"excluded {len(reservoir)} reservoir units "
            f"({reservoir.p_nom.sum():.0f} MW): no free hourly inflow dataset, and "
            "UnitCommitment.jl storage has no inflow field",
        )

    # ---------------------------------------------------------- PHS storage
    phs = ppl[ppl.carrier == "PHS"]
    if len(phs):
        eff = float(costs.at["PHS", "efficiency"]) if "PHS" in costs.index else 0.75
        added, skipped = 0, []
        for _, row in phs.iterrows():
            hours = row.get("max_hours", np.nan)
            if pd.isna(hours) or hours <= 0:
                skipped.append(row["name"])
                continue
            n.add(
                "StorageUnit", row.uid, bus=row.bus, carrier="PHS",
                p_nom=float(row.p_nom), max_hours=float(hours),
                # technology-data reports round-trip efficiency; PyPSA wants it
                # split across the charge and discharge legs.
                efficiency_store=float(np.sqrt(eff)),
                efficiency_dispatch=float(np.sqrt(eff)),
                cyclic_state_of_charge=True,
            )
            added += 1
        if added:
            report.note(
                "storage",
                f"{added} PHS units with max_hours from powerplantmatching "
                f"reservoir capacity, round-trip efficiency {eff:.2f}",
            )
        if skipped:
            report.note(
                "storage",
                f"skipped {len(skipped)} PHS units with no reservoir capacity in "
                f"the data ({', '.join(skipped[:4])})",
            )

    return n, report


def _capacity_shares(ppl, country, carrier, buses, n) -> pd.Series:
    """
    Where to put generation of a carrier that has no unit-level entry: on the
    powerplantmatching plants of that carrier, weighted by their capacity, and
    otherwise spread evenly because nothing locates it.
    """
    if carrier is not None:
        sel = (ppl.country == country) & (ppl.carrier == carrier)
        plants = ppl[sel].dropna(subset=["lat", "lon"])
        plants = plants[plants.p_nom > 0]
        if not plants.empty:
            weights = plants.groupby(_nearest_buses(plants, buses, n).values).p_nom.sum()
            return weights / weights.sum()
    real = real_substations(buses, n)
    return pd.Series(1.0 / len(real), index=real)


def _load_bus_shares(country, buses, n, year) -> tuple[pd.Series, str]:
    """
    Split a country's demand across its buses using PyPSA-Eur's key.

PyPSA-Eur weights NUTS3 regions 60% GDP / 40% population, then spreads each
    region over the substation regions overlapping it. Both extremes of that
    second step manufacture congestion: one substation per region concentrates
    demand, an even split strands it on remote buses. Here a region's weight is
    shared among the substations inside it, in proportion to their connection
    capacity; regions holding none go to their nearest.
    """
    try:
        keys = sources.load_nuts3_keys(year)
    except Exception as exc:  # network or Eurostat trouble
        logger.warning("NUTS3 keys unavailable (%s); falling back to uniform", exc)
        return pd.Series(1.0 / len(buses), index=buses), "even split (no NUTS3 data)"

    regions = keys[keys.country == country].dropna(subset=["pop", "gdp"])
    if regions.empty:
        return (
            pd.Series(1.0 / len(buses), index=buses),
            "even split (Eurostat has no NUTS3 population or GDP)",
        )

    # Demand connects at substations, not at the tee points osm-prebuilt
    # inserts when it splits a line.
    buses = real_substations(buses, n)

    # Drop regions off this synchronous grid before normalising, or their
    # weight lands on whichever coastal substation happens to be nearest --
    # France's overseas departements alone are 4% of its population.
    sub = n.buses.loc[buses]
    distance = _haversine_km(
        regions.lat.to_numpy(float), regions.lon.to_numpy(float),
        sub.y.to_numpy(float), sub.x.to_numpy(float),
    ).min(axis=1)
    offgrid = regions.index[distance > MAX_REGION_TO_GRID_KM]
    regions = regions.drop(index=offgrid)
    if regions.empty:
        return (
            pd.Series(1.0 / len(buses), index=buses),
            "even split (every NUTS3 region is off this grid)",
        )

    normed = lambda v: v / v.sum()
    weights = normed(
        sources.GDP_WEIGHT * normed(regions.gdp)
        + sources.POPULATION_WEIGHT * normed(regions["pop"])
    )

    import geopandas as gpd

    sub = n.buses.loc[buses]
    points = gpd.GeoDataFrame(
        index=sub.index,
        geometry=gpd.points_from_xy(sub.x.astype(float), sub.y.astype(float)),
        crs=regions.crs,
    )
    inside = gpd.sjoin(points, regions[["geometry"]], how="left", predicate="within")
    # geopandas names the joined column after the right frame's index when it
    # has one ("NUTS_ID" here) and "index_right" otherwise.
    join_col = next(
        c for c in ("index_right", regions.index.name, "NUTS_ID")
        if c and c in inside.columns
    )
    # A bus on a border can match several regions; keep one.
    inside = inside[~inside.index.duplicated()]
    buses_of_region: dict[str, list[str]] = {}
    for bus, region in inside[join_col].dropna().items():
        buses_of_region.setdefault(region, []).append(bus)

    capacity = connection_capacity(buses, n)
    shares = pd.Series(0.0, index=buses)
    homeless = []
    for region, weight in weights.items():
        hosts = buses_of_region.get(region)
        if hosts:
            # Share the region across its substations in proportion to how much
            # transmission each can actually take, not evenly.
            host_cap = capacity.reindex(hosts).fillna(0.0)
            split = (
                host_cap / host_cap.sum()
                if host_cap.sum() > 0
                else pd.Series(1.0 / len(hosts), index=hosts)
            )
            for bus, frac in split.items():
                shares[bus] += weight * frac
        else:
            homeless.append(region)
    if homeless:
        # No substation inside the region: give it to the closest one.
        at = _nearest_buses(regions.loc[homeless], buses, n)
        for region, bus in at.items():
            shares[bus] += weights[region]

    if shares.sum() <= 0:
        return pd.Series(1.0 / len(buses), index=buses), "even split (no overlap)"
    served = int((shares > 0).sum())
    return (
        shares / shares.sum(),
        f"{len(regions)} NUTS3 regions weighted "
        f"{sources.GDP_WEIGHT:.0%} GDP / {sources.POPULATION_WEIGHT:.0%} population "
        f"(Eurostat {year}) spread over the {served} substations inside them "
        f"in proportion to their connection capacity"
        + (f", {len(homeless)} regions to their nearest" if homeless else "")
        + (
            f"; dropped {len(offgrid)} region(s) over "
            f"{MAX_REGION_TO_GRID_KM:.0f} km from the grid ({', '.join(offgrid)})"
            if len(offgrid) else ""
        ),
    )


def _assign_buses(ppl, country_buses, n, report) -> pd.Series:
    """Nearest substation for every unit, from its coordinates."""
    out = pd.Series(index=ppl.index, dtype=object)
    unlocated = 0
    for country, buses in country_buses.items():
        rows = ppl.index[ppl.country == country]
        if not len(rows):
            continue
        located = ppl.loc[rows].dropna(subset=["lat", "lon"]).index
        if len(located):
            out.loc[located] = _nearest_buses(ppl.loc[located], buses, n)
        rest = rows.difference(located)
        if len(rest):
            unlocated += len(rest)
            out.loc[rest] = n.buses.loc[buses].v_nom.idxmax()
    if unlocated:
        report.note(
            "fleet",
            f"{unlocated} units have no coordinates and were placed at their "
            "country's highest-voltage bus",
        )
    return out
