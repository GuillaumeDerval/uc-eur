"""Converter unit tests -- no network access required."""
import numpy as np
import pandas as pd
import pypsa
import pytest

from pypsa_uc_gen import convert, validate


def toy_network(T=6):
    n = pypsa.Network()
    n.set_snapshots(pd.date_range("2019-01-01", periods=T, freq="h"))
    n.add("Bus", ["b1", "b2"], carrier="AC")
    n.add("Line", "l1", bus0="b1", bus1="b2", x=0.1, r=0.0, s_nom=500.0)
    n.add("Load", "d1", bus="b1", p_set=np.linspace(300, 700, T))
    n.add("Load", "d2", bus="b2", p_set=200.0)
    n.add("Generator", "coal1", bus="b1", carrier="coal", p_nom=600.0,
          committable=True, p_min_pu=0.38, marginal_cost=26.0,
          min_up_time=8, min_down_time=8, start_up_cost=29400.0,
          ramp_limit_up=0.9, ramp_limit_down=0.9,
          ramp_limit_start_up=0.4, ramp_limit_shut_down=0.4,
          up_time_before=0, down_time_before=1)
    n.add("Generator", "ocgt1", bus="b2", carrier="OCGT", p_nom=200.0,
          committable=True, p_min_pu=0.2, marginal_cost=35.0,
          min_up_time=0, min_down_time=0, start_up_cost=4800.0,
          up_time_before=3, down_time_before=0)
    n.add("Generator", "wind", bus="b2", carrier="onwind", p_nom=300.0,
          p_max_pu=np.linspace(0.1, 0.9, T), marginal_cost=0.0)
    return n


def test_structure_and_validation():
    data = convert.network_to_uc(toy_network(), power_balance_penalty=9999.0)
    validate.validate(data, strict=True)
    assert data["Parameters"]["Version"] == "0.4"
    assert data["Parameters"]["Time horizon (min)"] == 360
    assert data["Parameters"]["Time step (min)"] == 60
    assert data["Parameters"]["Power balance penalty ($/MW)"] == 9999.0
    assert set(data["Buses"]) == {"b1", "b2"}
    assert data["Generators"]["wind"]["Type"] == "Profiled"
    assert data["Generators"]["coal1"]["Type"] == "Thermal"


def test_initial_state_is_omitted_by_default():
    """No dataset says what was running before the horizon, so the converter
    asserts nothing; UnitCommitment.jl treats both fields as optional and
    julia/add_initial_conditions.jl derives a feasible state afterwards."""
    data = convert.network_to_uc(toy_network())
    for unit in data["Generators"].values():
        if unit["Type"] == "Thermal":
            assert "Initial status (h)" not in unit
            assert "Initial power (MW)" not in unit
    validate.validate(data, strict=True)


def test_asserted_initial_state_is_self_consistent():
    data = convert.network_to_uc(toy_network(), initial_conditions="off")
    for unit in data["Generators"].values():
        if unit["Type"] != "Thermal":
            continue
        status, power = unit["Initial status (h)"], unit["Initial power (MW)"]
        assert status != 0                      # zero is invalid in the format
        if status < 0:
            assert power == 0.0                 # offline units produce nothing
    validate.validate(data, strict=True)


def test_thermal_fields():
    u = convert.network_to_uc(toy_network(), initial_conditions="off")["Generators"]["coal1"]
    assert u["Production cost curve (MW)"] == [228.0, 600.0]      # p_min_pu * p_nom
    assert u["Production cost curve ($)"] == [5928.0, 15600.0]    # 26 EUR/MWh
    assert u["Ramp up limit (MW)"] == 540.0                       # 0.9 * 600
    assert u["Startup limit (MW)"] == 240.0                       # 0.4 * 600 >= pmin
    assert u["Minimum uptime (h)"] == 8
    # starts offline -> negative status at least as long as the min downtime
    assert u["Initial status (h)"] <= -8
    assert u["Initial power (MW)"] == 0.0


def test_initially_online_unit_gets_pmin():
    u = convert.network_to_uc(
        toy_network(), initial_conditions="on"
    )["Generators"]["ocgt1"]
    assert u["Initial status (h)"] > 0
    assert u["Initial power (MW)"] == 40.0                        # 0.2 * 200


def test_timeseries_collapse_and_expand():
    data = convert.network_to_uc(toy_network(T=6))
    # constant load collapses to a scalar, varying load stays a list of length T
    assert data["Buses"]["b2"]["Load (MW)"] == 200.0
    assert isinstance(data["Buses"]["b1"]["Load (MW)"], list)
    assert len(data["Buses"]["b1"]["Load (MW)"]) == 6
    assert len(data["Generators"]["wind"]["Maximum power (MW)"]) == 6


def test_line_susceptance_is_inverse_reactance():
    line = convert.network_to_uc(toy_network())["Transmission lines"]["l1"]
    assert line["Source bus"] == "b1" and line["Target bus"] == "b2"
    assert line["Susceptance (S)"] > 0
    assert line["Normal flow limit (MW)"] == 500.0
    assert line["Flow limit penalty ($/MW)"] == 5000.0            # finite -> soft


def test_feasibility_notes_clean_by_default():
    assert convert.network_to_uc(toy_network()) is not None
    assert validate.feasibility_notes(convert.network_to_uc(toy_network())) == []


def test_hard_flow_limit_is_flagged():
    data = convert.network_to_uc(toy_network(), flow_limit_penalty=-1.0)
    assert any("infeasible" in m for m in validate.feasibility_notes(data))


def test_validator_catches_bad_initial_power():
    data = convert.network_to_uc(toy_network(), initial_conditions="off")
    data["Generators"]["coal1"]["Initial power (MW)"] = 100.0   # offline but producing
    with pytest.raises(validate.ValidationError):
        validate.validate(data, strict=True)


def test_validator_catches_wrong_series_length():
    data = convert.network_to_uc(toy_network())
    data["Buses"]["b1"]["Load (MW)"] = [1.0, 2.0]
    with pytest.raises(validate.ValidationError):
        validate.validate(data, strict=True)


def test_non_uniform_snapshots_rejected():
    n = toy_network()
    n.set_snapshots(pd.DatetimeIndex(["2019-01-01 00:00", "2019-01-01 01:00",
                                      "2019-01-01 03:00"]))
    with pytest.raises(ValueError):
        convert.network_to_uc(n)


def test_sub_hourly_step():
    n = pypsa.Network()
    n.set_snapshots(pd.date_range("2019-01-01", periods=8, freq="15min"))
    n.add("Bus", "b1", carrier="AC")
    n.add("Load", "d", bus="b1", p_set=100.0)
    n.add("Generator", "g", bus="b1", carrier="OCGT", p_nom=200.0,
          committable=True, p_min_pu=0.2, marginal_cost=35.0)
    data = convert.network_to_uc(n)
    assert data["Parameters"]["Time step (min)"] == 15
    assert data["Parameters"]["Time horizon (min)"] == 120
    validate.validate(data, strict=True)


def test_unique_ids_disambiguates_multi_unit_sites():
    """Sites like 'Emile Huchet' host coal, CCGT and lignite units under one
    name; PyPSA would silently overwrite all but the last."""
    from pypsa_uc_gen.build import unique_ids

    ppl = pd.DataFrame({
        "name": ["Emile Huchet", "Emile Huchet", "Emile Huchet", "Doel 1"],
        "carrier": ["coal", "CCGT", "lignite", "nuclear"],
    })
    ids = unique_ids(ppl)
    assert ids.is_unique
    assert list(ids) == [
        "Emile Huchet (coal)", "Emile Huchet (CCGT)",
        "Emile Huchet (lignite)", "Doel 1",
    ]


def test_unique_ids_handles_same_name_and_carrier():
    from pypsa_uc_gen.build import unique_ids

    ppl = pd.DataFrame({"name": ["X", "X", "X"], "carrier": ["CCGT"] * 3})
    ids = unique_ids(ppl)
    assert ids.is_unique
    assert list(ids) == ["X (CCGT) #1", "X (CCGT) #2", "X (CCGT) #3"]


def test_every_fleet_unit_reaches_the_instance():
    """No unit may be lost between the fleet and the generated instance."""
    from pypsa_uc_gen import build

    ppl = pd.DataFrame([
        dict(name="Site A", carrier="coal", p_nom=100.0, country="BE",
             efficiency=0.4, lat=51.0, lon=4.0),
        dict(name="Site A", carrier="CCGT", p_nom=200.0, country="BE",
             efficiency=0.55, lat=51.0, lon=4.0),
        dict(name="Site A", carrier="lignite", p_nom=300.0, country="BE",
             efficiency=0.35, lat=51.0, lon=4.0),
        dict(name="Site B", carrier="nuclear", p_nom=900.0, country="BE",
             efficiency=0.33, lat=50.5, lon=4.5),
    ])
    snap = build.snapshots_for(2019, start="2019-01-01", hours=24)
    n, _ = build.build_network(["BE"], snap, ppl=ppl, imports="none",
                               min_capacity=0.0)
    thermal = n.generators[n.generators.committable]
    assert len(thermal) == 4
    assert thermal.p_nom.sum() == 1500.0


def test_transformers_become_branches():
    """Transformers are series reactances in DC power flow; dropping them
    would split a real grid into disconnected voltage-level islands."""
    n = toy_network()
    n.add("Bus", "b3", carrier="AC")
    n.add("Transformer", "t1", bus0="b2", bus1="b3", x=0.05, s_nom=400.0)
    n.add("Generator", "g3", bus="b3", carrier="OCGT", p_nom=100.0,
          committable=True, p_min_pu=0.2, marginal_cost=40.0)
    data = convert.network_to_uc(n)
    validate.validate(data, strict=True)
    lines = data["Transmission lines"]
    assert set(lines) == {"l1", "t1"}
    assert lines["t1"]["Source bus"] == "b2"
    assert lines["t1"]["Target bus"] == "b3"
    assert lines["t1"]["Susceptance (S)"] > 0
    assert lines["t1"]["Normal flow limit (MW)"] == 400.0


def test_links_are_rejected_not_silently_dropped():
    n = toy_network()
    n.add("Bus", "b3", carrier="AC")
    n.add("Link", "dc1", bus0="b1", bus1="b3", p_nom=500.0)
    with pytest.raises(ValueError, match="Link components"):
        convert.network_to_uc(n)


def test_every_bus_is_reachable_in_the_emitted_grid():
    """A generated network must not contain islands the converter created."""
    n = toy_network()
    n.add("Bus", "b3", carrier="AC")
    n.add("Transformer", "t1", bus0="b2", bus1="b3", x=0.05, s_nom=400.0)
    n.add("Generator", "g3", bus="b3", carrier="OCGT", p_nom=100.0,
          committable=True, p_min_pu=0.2, marginal_cost=40.0)
    data = convert.network_to_uc(n)

    adj = {b: set() for b in data["Buses"]}
    for line in data["Transmission lines"].values():
        adj[line["Source bus"]].add(line["Target bus"])
        adj[line["Target bus"]].add(line["Source bus"])
    seen, stack = set(), [next(iter(adj))]
    while stack:
        b = stack.pop()
        if b not in seen:
            seen.add(b)
            stack.extend(adj[b] - seen)
    assert seen == set(data["Buses"]), f"islands: {set(data['Buses']) - seen}"


def test_osm_bool_parsing():
    from pypsa_uc_gen.sources import _osm_bool
    s = pd.Series(["t", "f", "T", "F", "true", "false"])
    assert list(_osm_bool(s)) == [True, False, True, False, True, False]


def test_osm_csvs_need_single_quotechar():
    """OSM geometry is quoted with ' not ". Parsing with the default quotechar
    silently returns shifted columns instead of raising, so the loader must
    pin quotechar and verify bus references resolve."""
    import inspect
    from pypsa_uc_gen import sources
    assert sources.OSM_QUOTECHAR == "'"
    src = inspect.getsource(sources.load_osm_grid)
    assert "quotechar=OSM_QUOTECHAR" in src
    assert "unknown" in src  # cross-reference check on bus ids


def _fake_flows(monkeypatch, snapshots, spec):
    """Patch the Energy-Charts loader with a fixed flow table."""
    from pypsa_uc_gen import sources
    cols = pd.MultiIndex.from_tuples(list(spec), names=["country", "neighbour"])
    df = pd.DataFrame(
        {k: np.full(len(snapshots), v) for k, v in spec.items()},
        index=snapshots,
    )
    df.columns = cols
    monkeypatch.setattr(sources, "load_cross_border_flows", lambda c, s: df)
    return df


def _fleet():
    return pd.DataFrame([
        dict(name="G1", carrier="CCGT", p_nom=500.0, country="BE",
             efficiency=0.55, lat=51.0, lon=4.0),
        dict(name="G2", carrier="CCGT", p_nom=500.0, country="FR",
             efficiency=0.55, lat=48.9, lon=2.4),
    ])


def test_internal_borders_are_not_imposed_as_imports(monkeypatch):
    """Selecting BE and FR together means the BE-FR border is modelled, not
    pinned to history; double counting it would fabricate energy."""
    from pypsa_uc_gen import build

    snap = build.snapshots_for(2019, start="2019-01-01", hours=6)
    _fake_flows(monkeypatch, snap, {("BE", "FR"): 800.0, ("BE", "NL"): 300.0})
    n, report = build.build_network(
        ["BE", "FR"], snap, ppl=_fleet(), imports="historical", min_capacity=0.0
    )
    names = set(n.generators.index)
    assert any(g.startswith("import BE<-NL") for g in names), \
        "external border must be imposed"
    assert not any("BE<-FR" in g for g in names), "internal border must stay endogenous"


def test_external_border_becomes_a_curtailable_import(monkeypatch):
    from pypsa_uc_gen import build

    snap = build.snapshots_for(2019, start="2019-01-01", hours=6)
    _fake_flows(monkeypatch, snap, {("BE", "NL"): 300.0})
    n, _ = build.build_network(["BE"], snap, ppl=_fleet(), imports="historical",
                               min_capacity=0.0)
    imports = n.generators[n.generators.carrier == "import"]
    assert len(imports) >= 1
    assert round(imports.p_nom.sum(), 6) == 300.0   # split across border buses
    assert (imports.p_min_pu == 0.0).all()          # curtailable -> always feasible
    assert not imports.committable.any()
    assert not any(l.startswith("export BE->NL") for l in n.loads.index)


def test_net_export_becomes_load_not_negative_generation(monkeypatch):
    from pypsa_uc_gen import build

    snap = build.snapshots_for(2019, start="2019-01-01", hours=6)
    _fake_flows(monkeypatch, snap, {("BE", "NL"): -450.0})
    n, _ = build.build_network(["BE"], snap, ppl=_fleet(), imports="historical",
                               min_capacity=0.0)
    assert not any(g.startswith("import BE<-NL") for g in n.generators.index)
    exports = [l for l in n.loads.index if l.startswith("export BE->NL")]
    assert exports
    assert round(float(n.loads_t.p_set[exports].iloc[0].sum()), 6) == 450.0


def test_imports_off_by_default(monkeypatch):
    from pypsa_uc_gen import build

    snap = build.snapshots_for(2019, start="2019-01-01", hours=6)
    _fake_flows(monkeypatch, snap, {("BE", "NL"): 300.0})
    n, _ = build.build_network(["BE"], snap, ppl=_fleet(), imports="none",
                               min_capacity=0.0)
    assert not any("import" in g for g in n.generators.index)


def test_validator_catches_initial_power_above_shutdown_limit():
    """UnitCommitment.jl's generate_initial_conditions! solves a single-period
    MIP that ignores ramp and shutdown limits, so it can leave a unit above the
    level it may stop from. The horizon is then infeasible and the solver only
    says "0 solutions"."""
    data = convert.network_to_uc(toy_network(), initial_conditions="on")
    unit = next(u for u in data["Generators"].values() if u["Type"] == "Thermal")
    unit["Shutdown limit (MW)"] = unit["Production cost curve (MW)"][0]
    unit["Initial status (h)"] = 24
    unit["Initial power (MW)"] = unit["Production cost curve (MW)"][-1]
    errors = validate.validate(data, strict=False)
    assert any("cannot be switched off" in e for e in errors), errors


def test_initial_power_at_the_shutdown_limit_is_accepted():
    data = convert.network_to_uc(toy_network(), initial_conditions="on")
    for unit in data["Generators"].values():
        if unit["Type"] != "Thermal":
            continue
        pmin = unit["Production cost curve (MW)"][0]
        unit["Shutdown limit (MW)"] = pmin
        unit["Initial status (h)"] = 24
        unit["Initial power (MW)"] = pmin
    assert validate.validate(data, strict=False) == []
