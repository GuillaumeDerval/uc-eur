"""Tests for the benchmark-set generator and the instance summaries."""
import json

import pandas as pd
import pytest

import generate_batch
from pypsa_uc_gen import build, convert, summary, validate


def toy_fleet():
    return pd.DataFrame([
        dict(name="A", carrier="CCGT", p_nom=400.0, country="BE",
             efficiency=0.55, lat=51.0, lon=4.0),
        dict(name="B", carrier="nuclear", p_nom=900.0, country="BE",
             efficiency=0.33, lat=51.3, lon=4.3),
    ])


def test_usable_weeks_stay_inside_opsd_coverage():
    weeks = generate_batch.usable_weeks(2019, 168)
    assert weeks, "2019 should have usable weeks"
    assert all(1 <= w <= 53 for w in weeks)
    # A horizon starting in the last week of 2020 would run past OPSD's end.
    assert 53 not in generate_batch.usable_weeks(2020, 168)


def test_screen_marks_missing_data_ineligible():
    table = generate_batch.screen(["BE", "LU"], 2019)
    assert table.loc["BE", "eligible"]
    # Luxembourg has neither a full load series nor a thermal fleet.
    assert not table.loc["LU", "eligible"]
    assert table.loc["LU", "excluded_because"]


def test_screen_never_raises_on_uncovered_country():
    table = generate_batch.screen(["MT"], 2019)
    assert not table.loc["MT", "eligible"]


def test_weeks_are_distinct_per_country():
    import random
    weeks = generate_batch.usable_weeks(2019, 168)
    rng = random.Random(0)
    chosen = rng.sample(weeks, 5)
    assert len(set(chosen)) == 5


@pytest.fixture(scope="module")
def built():
    snap = build.snapshots_for(2019, week=10, hours=24)
    n, report = build.build_network(
        ["BE"], snap, ppl=toy_fleet(), imports="none", min_capacity=0.0
    )
    data = convert.network_to_uc(n)
    return data, n, report


def test_summary_is_json_serialisable_and_complete(built):
    data, n, report = built
    meta = summary.summarise(
        data, n, report, countries=["BE"], year=2019, week=10,
        options={"costs_year": 2020},
    )
    json.dumps(meta)  # must not raise
    for section in ("instance", "size", "demand", "capacity", "grid",
                    "imports", "options", "feasibility", "sources",
                    "provenance_notes"):
        assert section in meta, section
    assert meta["instance"]["week"] == 10
    assert meta["instance"]["time_steps"] == 24
    assert meta["size"]["thermal_units"] == 2
    assert meta["capacity"]["thermal_MW"] == 1300.0
    assert meta["capacity"]["thermal_by_carrier_MW"] == {"CCGT": 400.0, "nuclear": 900.0}


def test_summary_size_matches_the_instance(built):
    data, n, report = built
    meta = summary.summarise(
        data, n, report, countries=["BE"], year=2019, week=10, options={},
    )
    assert meta["size"]["buses"] == len(data["Buses"])
    assert meta["size"]["branches"] == len(data.get("Transmission lines", {}))
    thermal = sum(1 for u in data["Generators"].values() if u["Type"] == "Thermal")
    assert meta["size"]["thermal_units"] == thermal


def test_summary_records_feasibility_guarantees(built):
    data, n, report = built
    meta = summary.summarise(
        data, n, report, countries=["BE"], year=2019, week=10, options={},
    )
    f = meta["feasibility"]
    assert f["power_balance_penalty_eur_per_MW"] > 0
    assert f["flow_limit_penalty_eur_per_MW"] > 0   # finite -> congestion priced
    assert f["profiled_curtailable"] is True
    assert validate.feasibility_notes(data) == []


def test_every_energy_charts_neighbour_is_mapped():
    """A border whose country name is unmapped would be silently dropped,
    deleting real imports and making the instance look inadequate."""
    import glob
    import json as _json

    from pypsa_uc_gen.sources import _EC_COUNTRY_TO_ISO2

    unmapped = set()
    for path in glob.glob("data/cache/cbpf_*.json"):
        for series in _json.load(open(path)).get("countries", []):
            if series["name"] != "sum" and series["name"] not in _EC_COUNTRY_TO_ISO2:
                unmapped.add(series["name"])
    assert not unmapped, f"unmapped Energy-Charts countries: {sorted(unmapped)}"


def test_virtual_buses_are_not_substations():
    """osm-prebuilt splits long lines at tee points and names them virtual_*.
    Attaching load to one puts demand in the middle of a transmission line."""
    import pypsa

    from pypsa_uc_gen.build import real_substations

    n = pypsa.Network()
    n.add("Bus", ["way/1-380", "virtual_way/2:0-380", "relation/3-220"])
    assert real_substations(list(n.buses.index), n) == ["way/1-380", "relation/3-220"]


def test_real_substations_never_returns_empty():
    """A country made only of tee points must still get its load somewhere."""
    import pypsa

    from pypsa_uc_gen.build import real_substations

    n = pypsa.Network()
    n.add("Bus", ["virtual_a", "virtual_b"])
    assert real_substations(["virtual_a", "virtual_b"], n) == ["virtual_a", "virtual_b"]


def test_connection_capacity_sums_incident_branches():
    import pypsa

    from pypsa_uc_gen.build import connection_capacity

    n = pypsa.Network()
    n.add("Bus", ["a", "b", "c"])
    n.add("Line", "l1", bus0="a", bus1="b", x=0.1, s_nom=500.0)
    n.add("Line", "l2", bus0="b", bus1="c", x=0.1, s_nom=300.0)
    n.add("Transformer", "t1", bus0="a", bus1="c", x=0.1, s_nom=200.0)
    cap = connection_capacity(["a", "b", "c"], n)
    assert cap["a"] == 700.0    # l1 + t1
    assert cap["b"] == 800.0    # l1 + l2
    assert cap["c"] == 500.0    # l2 + t1


def test_offgrid_regions_are_excluded():
    """France's overseas departements and Corsica are not on the synchronous
    grid; their demand is not in the national load series either."""
    from pypsa_uc_gen import build, sources

    keys = sources.load_nuts3_keys(2019)
    grid = sources.load_osm_grid()
    buses = grid["buses"]
    fr_buses = buses[(buses.country == "FR") & ~buses.dc]
    fr = keys[keys.country == "FR"].dropna(subset=["pop", "gdp"])
    d = build._haversine_km(
        fr.lat.to_numpy(float), fr.lon.to_numpy(float),
        fr_buses.y.to_numpy(float), fr_buses.x.to_numpy(float),
    ).min(axis=1)
    offgrid = set(fr.index[d > build.MAX_REGION_TO_GRID_KM])
    # the five overseas departements plus both Corsican regions
    assert {"FRY10", "FRY20", "FRY30", "FRY40", "FRY50"} <= offgrid
    assert {"FRM01", "FRM02"} <= offgrid
    # and no mainland region is caught
    assert not any(r.startswith(("FR1", "FR2", "FR3", "FR4", "FR5", "FR6", "FR7", "FR8"))
                   for r in offgrid)


def test_outage_draws_are_distinct_and_bounded():
    from generate_outages import draw_combinations

    units = [f"u{i}" for i in range(20)]
    combos = draw_combinations(units, 50, 2, seed=0)
    assert len(combos) == 50
    assert len(set(combos)) == 50, "combinations must not repeat"
    assert all(1 <= len(c) <= 2 for c in combos)
    assert all(set(c) <= set(units) for c in combos)
    assert all(list(c) == sorted(c) for c in combos), "order-insensitive"


def test_outage_draws_are_reproducible():
    from generate_outages import draw_combinations

    units = [f"u{i}" for i in range(20)]
    assert draw_combinations(units, 30, 2, 7) == draw_combinations(units, 30, 2, 7)
    assert draw_combinations(units, 30, 2, 7) != draw_combinations(units, 30, 2, 8)


def test_outage_refuses_more_variants_than_exist():
    from generate_outages import draw_combinations

    with pytest.raises(ValueError, match="distinct"):
        draw_combinations(["a", "b"], 99, 2, seed=0)


def test_removing_units_shrinks_the_fleet():
    from pypsa_uc_gen import build

    ppl = pd.DataFrame([
        dict(name="A", carrier="CCGT", p_nom=400.0, country="BE",
             efficiency=0.55, lat=51.0, lon=4.0),
        dict(name="B", carrier="nuclear", p_nom=900.0, country="BE",
             efficiency=0.33, lat=50.5, lon=4.5),
    ])
    snap = build.snapshots_for(2019, week=10, hours=24)
    base, _ = build.build_network(["BE"], snap, ppl=ppl, imports="none",
                                 min_capacity=0.0)
    cut, report = build.build_network(["BE"], snap, ppl=ppl, imports="none",
                                      min_capacity=0.0, drop_units=("A",))
    assert base.generators.committable.sum() == 2
    assert cut.generators.committable.sum() == 1
    assert "A" not in cut.generators.index
    assert any("removed 1 unit" in m for m in report["outage"])


def test_removing_an_unknown_unit_raises():
    """Silently ignoring the name would build the intact system under an
    outage label."""
    from pypsa_uc_gen import build

    ppl = pd.DataFrame([
        dict(name="A", carrier="CCGT", p_nom=400.0, country="BE",
             efficiency=0.55, lat=51.0, lon=4.0),
    ])
    snap = build.snapshots_for(2019, week=10, hours=24)
    with pytest.raises(KeyError, match="unknown unit"):
        build.build_network(["BE"], snap, ppl=ppl, imports="none",
                            min_capacity=0.0, drop_units=("Nonexistent",))
