"""
Convert a PyPSA network into a UnitCommitment.jl 0.4 instance.

Field names, defaults and validation rules follow
``src/instance/read.jl`` of UnitCommitment.jl v0.4.2 and
https://anl-ceeesa.github.io/UnitCommitment.jl/0.4/guides/format/

Feasibility
-----------
The instance is feasible-by-construction for any commitment schedule that
respects the units' own operational constraints, because

* ``Power balance penalty ($/MW)`` is finite, so both unserved load and
  surplus generation are absorbed at a price rather than being infeasible;
* profiled (VRE) units have ``Minimum power (MW) = 0`` and are curtailable;
* ``Flow limit penalty ($/MW)`` is finite, so congestion is priced, not hard.

The only remaining infeasibility source is a contradiction inside a unit's own
constraints (e.g. an initial status incompatible with its minimum downtime),
which is exactly the intended notion of infeasibility.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pypsa

logger = logging.getLogger(__name__)

FORMAT_VERSION = "0.4"


def _ts(values, T: int, decimals: int = 4):
    """
    Emit a UnitCommitment.jl time series: a scalar when constant, otherwise a
    list of exactly ``T`` floats.
    """
    arr = np.asarray(values, dtype=float)
    if arr.ndim == 0:
        return round(float(arr), decimals)
    arr = arr.reshape(-1)
    if len(arr) != T:
        raise ValueError(f"expected {T} values, got {len(arr)}")
    arr = np.round(arr, decimals)
    if np.all(arr == arr[0]):
        return float(arr[0])
    return [float(x) for x in arr]


def _pu(n: pypsa.Network, component: str, name: str, attr: str, T: int):
    """Static or time-varying per-unit attribute of one component."""
    dynamic = getattr(n, f"{component.lower()}s_t", None)
    if dynamic is not None and attr in dynamic and name in dynamic[attr].columns:
        return dynamic[attr][name].values
    return float(getattr(n, f"{component.lower()}s").at[name, attr])


def network_to_uc(
    n: pypsa.Network,
    *,
    power_balance_penalty: float = 10_000.0,
    flow_limit_penalty: float = 5_000.0,
    emergency_flow_factor: float = 1.0,
    initial_conditions: str = "free",
    scenario_name: str = "s1",
    scenario_weight: float = 1.0,
    include_storage: bool = True,
    cost_decimals: int = 4,
) -> dict:
    """
    Build the UnitCommitment.jl instance dictionary.

    Parameters
    ----------
    power_balance_penalty
        Value of lost load in $/MW, applied to both shortage and surplus.
        This is what gives the instance unlimited load shedding.
    initial_conditions
        ``"free"`` (default) omits the initial status and power entirely, so
        nothing is asserted about the hour before the horizon. ``"on"`` and
        ``"off"`` assert a state taken from the network's ``up_time_before`` /
        ``down_time_before``.
    """
    if n.snapshots.empty:
        raise ValueError("network has no snapshots")
    T = len(n.snapshots)

    weights = n.snapshot_weightings["objective"]
    if not np.allclose(weights, weights.iloc[0]):
        raise ValueError(
            "UnitCommitment.jl assumes a uniform time step; snapshot weightings "
            "are not constant"
        )

    deltas = np.unique(np.diff(n.snapshots.values))
    if len(deltas) != 1:
        raise ValueError("snapshots are not evenly spaced")
    step_min = int(pd.Timedelta(deltas[0]).total_seconds() // 60)
    if 60 % step_min != 0:
        raise ValueError(f"time step {step_min} min does not divide 60")

    params = {
        "Version": FORMAT_VERSION,
        "Time horizon (min)": int(T * step_min),
        "Time step (min)": step_min,
        "Power balance penalty ($/MW)": float(power_balance_penalty),
        "Scenario name": scenario_name,
        "Scenario weight": float(scenario_weight),
    }

    data: dict = {"Parameters": params, "Buses": {}, "Generators": {}}

    # ------------------------------------------------------------- buses
    for bus in n.buses.index:
        loads = n.loads.index[n.loads.bus == bus]
        if len(loads):
            p = np.zeros(T)
            for load in loads:
                if load in n.loads_t.p_set.columns:
                    p += n.loads_t.p_set[load].values
                else:
                    p += float(n.loads.at[load, "p_set"])
        else:
            p = np.zeros(T)
        data["Buses"][str(bus)] = {"Load (MW)": _ts(p, T)}

    # -------------------------------------------------------- generators
    for name in n.generators.index:
        g = n.generators.loc[name]
        p_nom = float(g.p_nom)
        if p_nom <= 0:
            continue
        bus = str(g.bus)
        p_max_pu = _pu(n, "Generator", name, "p_max_pu", T)
        p_min_pu = _pu(n, "Generator", name, "p_min_pu", T)

        if bool(g.get("committable", False)):
            data["Generators"][str(name)] = _thermal_unit(
                n,
                name,
                g,
                bus,
                p_nom,
                p_max_pu,
                p_min_pu,
                T,
                initial_conditions,
                cost_decimals,
            )
        else:
            data["Generators"][str(name)] = {
                "Bus": bus,
                "Type": "Profiled",
                "Cost ($/MW)": _ts(float(g.marginal_cost), T, cost_decimals),
                "Minimum power (MW)": _ts(p_nom * np.asarray(p_min_pu), T),
                "Maximum power (MW)": _ts(p_nom * np.asarray(p_max_pu), T),
            }

    # ----------------------------------------------------------- storage
    if include_storage and len(n.storage_units):
        data["Storage units"] = {}
        for name in n.storage_units.index:
            s = n.storage_units.loc[name]
            p_nom = float(s.p_nom)
            e_nom = p_nom * float(s.max_hours)
            data["Storage units"][str(name)] = {
                "Bus": str(s.bus),
                "Minimum level (MWh)": 0.0,
                "Maximum level (MWh)": round(e_nom, 4),
                "Charge cost ($/MW)": 0.0,
                "Discharge cost ($/MW)": round(float(s.marginal_cost), cost_decimals),
                "Charge efficiency": round(float(s.efficiency_store), 6),
                "Discharge efficiency": round(float(s.efficiency_dispatch), 6),
                "Loss factor": round(float(s.standing_loss), 6),
                "Minimum charge rate (MW)": 0.0,
                "Maximum charge rate (MW)": round(p_nom, 4),
                "Minimum discharge rate (MW)": 0.0,
                "Maximum discharge rate (MW)": round(p_nom, 4),
                "Initial level (MWh)": round(
                    float(s.state_of_charge_initial), 4
                ),
                "Allow simultaneous charging and discharging": False,
            }

    # ------------------------------------------------- transmission lines
    if len(n.lines) or len(n.transformers):
        if hasattr(n, "calculate_dependent_values"):
            n.calculate_dependent_values()
        lines: dict = {}

        # Transformers are series reactances in the linearised power flow, so
        # they become ordinary branches. Dropping them would split a real grid
        # into disconnected voltage-level islands.
        for component, frame, rating in (
            ("Line", n.lines, "s_nom"),
            ("Transformer", n.transformers, "s_nom"),
        ):
            for name in frame.index:
                br = frame.loc[name]
                x = float(br.get("x_pu_eff", np.nan))
                if not np.isfinite(x) or x <= 0:
                    x = float(br.x)
                if not np.isfinite(x) or x <= 0:
                    raise ValueError(
                        f"{component} {name} has non-positive reactance {x!r}; "
                        "UnitCommitment.jl needs a finite positive susceptance"
                    )
                s_nom = float(br[rating]) * float(br.get("s_max_pu", 1.0))
                key = str(name)
                if key in lines:  # a line and a transformer can share a name
                    key = f"{component}:{name}"
                lines[key] = {
                    "Source bus": str(br.bus0),
                    "Target bus": str(br.bus1),
                    # Only relative susceptances matter: they cancel in the
                    # injection shift factors UnitCommitment.jl derives.
                    "Susceptance (S)": round(1.0 / x, 6),
                    "Normal flow limit (MW)": round(s_nom, 4),
                    "Emergency flow limit (MW)": round(
                        s_nom * emergency_flow_factor, 4
                    ),
                    "Flow limit penalty ($/MW)": float(flow_limit_penalty),
                }
        data["Transmission lines"] = lines

    # UnitCommitment.jl 0.4 has no controllable-branch component, so HVDC links
    # cannot be represented. Silently dropping them would disconnect parts of a
    # PyPSA-Eur network and quietly change the answer.
    if len(n.links):
        raise ValueError(
            f"network has {len(n.links)} Link components (HVDC or other "
            "controllable branches) which UnitCommitment.jl 0.4 cannot express. "
            "Merge the linked buses, drop the links deliberately, or use a "
            "copperplate topology."
        )

    return data


def _thermal_unit(
    n, name, g, bus, p_nom, p_max_pu, p_min_pu, T,
    initial_conditions, cost_decimals,
):
    pmax = float(np.max(np.asarray(p_max_pu))) * p_nom
    pmin = float(np.max(np.asarray(p_min_pu))) * p_nom
    pmin = min(pmin, pmax)

    mc = float(g.marginal_cost)
    mq = float(g.get("marginal_cost_quadratic", 0.0) or 0.0)

    if pmax - pmin < 1e-6:
        # Degenerate unit: a single cost-curve point pins output at pmin.
        curve_mw = [pmin]
    elif mq > 0:
        curve_mw = [pmin, 0.5 * (pmin + pmax), pmax]
    else:
        curve_mw = [pmin, pmax]
    curve_cost = [mc * x + mq * x * x for x in curve_mw]

    unit = {
        "Bus": bus,
        "Type": "Thermal",
        "Production cost curve (MW)": [round(x, 4) for x in curve_mw],
        "Production cost curve ($)": [round(x, cost_decimals) for x in curve_cost],
        "Minimum uptime (h)": int(g.get("min_up_time", 1) or 0),
        "Minimum downtime (h)": int(g.get("min_down_time", 1) or 0),
        "Startup costs ($)": [round(float(g.get("start_up_cost", 0.0)), cost_decimals)],
        "Startup delays (h)": [1],
    }

    # Ramping. PyPSA stores per-unit-of-p_nom rates; NaN means unconstrained.
    for pypsa_attr, uc_field in (
        ("ramp_limit_up", "Ramp up limit (MW)"),
        ("ramp_limit_down", "Ramp down limit (MW)"),
    ):
        rate = g.get(pypsa_attr, np.nan)
        if pd.notna(rate):
            unit[uc_field] = round(float(rate) * p_nom, 4)

    # Startup/shutdown limits must be at least pmin, otherwise the unit could
    # never legally start or stop.
    for pypsa_attr, uc_field in (
        ("ramp_limit_start_up", "Startup limit (MW)"),
        ("ramp_limit_shut_down", "Shutdown limit (MW)"),
    ):
        rate = g.get(pypsa_attr, np.nan)
        if pd.notna(rate):
            unit[uc_field] = round(max(float(rate) * p_nom, pmin), 4)

    # Initial conditions.
    #
    # There is no dataset of what was running the hour before a chosen week, so
    # the default is to assert nothing: UnitCommitment.jl treats "Initial status
    # (h)" and "Initial power (MW)" as optional and, when both are omitted,
    # leaves the unit's history free. Minimum up and down times still bind on
    # every transition inside the horizon.
    #
    # Asserting a state instead is an assumption that shows up in the answer:
    # cold-starting a whole national fleet at hour 0 forces load shedding that
    # reflects the assumption rather than the power system.
    if initial_conditions == "free":
        return unit

    # When a state is asserted, UnitCommitment.jl requires both fields together,
    # a non-zero status, and zero power whenever the status is negative.
    up_before = float(g.get("up_time_before", 0) or 0)
    down_before = float(g.get("down_time_before", 0) or 0)
    if up_before > 0:
        status = int(round(up_before))
        power = pmin
    else:
        status = -int(round(down_before)) if down_before > 0 else -1
        power = 0.0
    # Widen the status past the unit's own minimum up/down time so the asserted
    # state does not silently bind in the first hours.
    if status > 0:
        status = max(status, unit["Minimum uptime (h)"])
    elif unit["Minimum downtime (h)"]:
        status = min(status, -unit["Minimum downtime (h)"])
    unit["Initial status (h)"] = int(status)
    unit["Initial power (MW)"] = round(float(power), 4)
    return unit
