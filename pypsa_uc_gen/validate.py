"""
Structural validation of a generated UnitCommitment.jl instance.

Catches converter bugs before the file ever reaches Julia. The rules mirror
``src/instance/read.jl`` of UnitCommitment.jl v0.4.2.
"""

from __future__ import annotations


class ValidationError(Exception):
    pass


def _series(value, T, ctx, errors):
    """A field is valid if it is a scalar or a list of exactly T numbers."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [float(value)] * T
    if isinstance(value, list):
        if len(value) != T:
            errors.append(f"{ctx}: length {len(value)} != time horizon {T}")
            return None
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value):
            errors.append(f"{ctx}: non-numeric entry")
            return None
        return [float(v) for v in value]
    errors.append(f"{ctx}: expected scalar or list, got {type(value).__name__}")
    return None


def validate(data: dict, strict: bool = True) -> list[str]:
    """Return a list of problems; raise on the first one if ``strict``."""
    errors: list[str] = []

    params = data.get("Parameters")
    if not params:
        raise ValidationError("missing 'Parameters'")

    step = int(params.get("Time step (min)", 60))
    if 60 % step:
        errors.append(f"time step {step} does not divide 60")
    if "Time horizon (min)" in params:
        horizon_min = int(params["Time horizon (min)"])
    elif "Time horizon (h)" in params:
        horizon_min = int(params["Time horizon (h)"]) * 60
    else:
        raise ValidationError("missing 'Time horizon (h)' or 'Time horizon (min)'")
    if horizon_min % step:
        errors.append(f"time step {step} does not divide horizon {horizon_min}")
    T = horizon_min // step

    buses = data.get("Buses") or {}
    if not buses:
        errors.append("no buses")
    for name, bus in buses.items():
        _series(bus.get("Load (MW)", 0.0), T, f"bus {name} Load (MW)", errors)

    known_buses = set(buses)

    total_thermal = 0
    for name, unit in (data.get("Generators") or {}).items():
        ctx = f"generator {name}"
        if unit.get("Bus") not in known_buses:
            errors.append(f"{ctx}: unknown bus {unit.get('Bus')!r}")
        utype = str(unit.get("Type", "")).lower()

        if utype == "thermal":
            total_thermal += 1
            mw = unit.get("Production cost curve (MW)")
            cost = unit.get("Production cost curve ($)")
            if not isinstance(mw, list) or not isinstance(cost, list) or not mw:
                errors.append(f"{ctx}: malformed production cost curve")
                continue
            if len(mw) != len(cost):
                errors.append(f"{ctx}: cost curve MW/$ length mismatch")
            if any(b < a for a, b in zip(mw, mw[1:])):
                errors.append(f"{ctx}: cost curve MW points not non-decreasing")
            if any(v < 0 for v in mw):
                errors.append(f"{ctx}: negative power in cost curve")
            pmin, pmax = float(mw[0]), float(mw[-1])

            status = unit.get("Initial status (h)")
            power = unit.get("Initial power (MW)")
            if (status is None) != (power is None):
                errors.append(f"{ctx}: initial status and power must be given together")
            elif status is not None:
                if status == 0:
                    errors.append(f"{ctx}: initial status must be non-zero")
                if status < 0 and power > 1e-3:
                    errors.append(
                        f"{ctx}: initially offline but initial power {power} > 0"
                    )
                if status > 0 and not (pmin - 1e-6 <= power <= pmax + 1e-6):
                    errors.append(
                        f"{ctx}: initial power {power} outside [{pmin}, {pmax}]"
                    )
                # A unit entering the horizon above the level it may shut down
                # from can neither stop nor, if the schedule needs it off,
                # remain on: the whole horizon goes infeasible, and the solver
                # reports it as an unhelpful "0 solutions".
                shutdown = unit.get("Shutdown limit (MW)")
                if (
                    status > 0
                    and shutdown is not None
                    and power > max(float(shutdown), pmin) + 1e-6
                ):
                    errors.append(
                        f"{ctx}: initial power {power} exceeds shutdown limit "
                        f"{shutdown}, so the unit cannot be switched off"
                    )

            delays = unit.get("Startup delays (h)", [1])
            costs = unit.get("Startup costs ($)", [0.0])
            if len(delays) != len(costs):
                errors.append(f"{ctx}: startup delays/costs length mismatch")
            if any(b <= a for a, b in zip(delays, delays[1:])):
                errors.append(f"{ctx}: startup delays must be strictly increasing")

            for field in ("Ramp up limit (MW)", "Ramp down limit (MW)",
                          "Startup limit (MW)", "Shutdown limit (MW)"):
                if field in unit and unit[field] < 0:
                    errors.append(f"{ctx}: negative {field}")
            for field in ("Startup limit (MW)", "Shutdown limit (MW)"):
                if field in unit and unit[field] + 1e-6 < pmin:
                    errors.append(
                        f"{ctx}: {field}={unit[field]} below minimum power {pmin}; "
                        "the unit could never start or stop"
                    )
            for field in ("Minimum uptime (h)", "Minimum downtime (h)"):
                if field in unit and (
                    not isinstance(unit[field], int) or unit[field] < 0
                ):
                    errors.append(f"{ctx}: {field} must be a non-negative integer")

        elif utype == "profiled":
            lo = _series(unit.get("Minimum power (MW)", 0.0), T, f"{ctx} min", errors)
            hi = _series(unit.get("Maximum power (MW)"), T, f"{ctx} max", errors)
            if "Cost ($/MW)" not in unit:
                errors.append(f"{ctx}: profiled units require 'Cost ($/MW)'")
            else:
                _series(unit["Cost ($/MW)"], T, f"{ctx} cost", errors)
            if lo and hi and any(a > b + 1e-6 for a, b in zip(lo, hi)):
                errors.append(f"{ctx}: minimum power exceeds maximum power")
        else:
            errors.append(f"{ctx}: invalid type {unit.get('Type')!r}")

    for name, su in (data.get("Storage units") or {}).items():
        ctx = f"storage {name}"
        if su.get("Bus") not in known_buses:
            errors.append(f"{ctx}: unknown bus {su.get('Bus')!r}")
        for field in ("Maximum level (MWh)", "Maximum charge rate (MW)",
                      "Maximum discharge rate (MW)"):
            if field not in su:
                errors.append(f"{ctx}: missing required {field}")
        for field in ("Charge efficiency", "Discharge efficiency", "Loss factor"):
            v = su.get(field)
            if v is not None and not (0.0 <= v <= 1.0):
                errors.append(f"{ctx}: {field}={v} outside [0, 1]")
        lvl, lo, hi = (
            su.get("Initial level (MWh)"),
            su.get("Minimum level (MWh)", 0.0),
            su.get("Maximum level (MWh)"),
        )
        if lvl is not None and hi is not None and not (lo <= lvl <= hi):
            errors.append(f"{ctx}: initial level {lvl} outside [{lo}, {hi}]")

    for name, line in (data.get("Transmission lines") or {}).items():
        ctx = f"line {name}"
        for field in ("Source bus", "Target bus"):
            if line.get(field) not in known_buses:
                errors.append(f"{ctx}: unknown {field} {line.get(field)!r}")
        b = line.get("Susceptance (S)")
        if b is None or b <= 0:
            errors.append(f"{ctx}: susceptance must be positive, got {b}")
        for field in ("Normal flow limit (MW)", "Emergency flow limit (MW)"):
            if field in line:
                _series(line[field], T, f"{ctx} {field}", errors)

    if total_thermal == 0:
        errors.append("instance contains no thermal units")

    if errors and strict:
        raise ValidationError(
            f"{len(errors)} problem(s):\n  " + "\n  ".join(errors[:20])
        )
    return errors


def feasibility_notes(data: dict) -> list[str]:
    """
    Check the properties that make the instance feasible for any schedule that
    respects the units' own constraints.
    """
    notes = []
    pen = data["Parameters"].get("Power balance penalty ($/MW)", 1000.0)
    if pen is None or pen <= 0:
        notes.append("power balance penalty is not positive: load shedding is not priced")
    for name, line in (data.get("Transmission lines") or {}).items():
        p = line.get("Flow limit penalty ($/MW)", 5000.0)
        if p is None or p < 0:
            notes.append(f"line {name}: hard flow limit can make schedules infeasible")
    for name, unit in (data.get("Generators") or {}).items():
        if str(unit.get("Type", "")).lower() == "profiled":
            lo = unit.get("Minimum power (MW)", 0.0)
            if (isinstance(lo, list) and any(v > 0 for v in lo)) or (
                isinstance(lo, (int, float)) and lo > 0
            ):
                notes.append(f"profiled unit {name} cannot be curtailed to zero")
    for name, r in (data.get("Reserves") or {}).items():
        if r.get("Shortfall penalty ($/MW)", -1) < 0:
            notes.append(f"reserve {name} is a hard constraint and can cause infeasibility")
    return notes
