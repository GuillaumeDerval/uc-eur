"""
A compact, machine-readable description of what a generated instance contains.

Written next to every instance as ``<name>.summary.json`` so a batch of
instances can be inspected, filtered or tabulated without parsing the instances
themselves.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import sources


def _series_stats(values) -> dict:
    arr = np.asarray(values, dtype=float)
    return {
        "peak_MW": round(float(arr.max()), 1),
        "mean_MW": round(float(arr.mean()), 1),
        "min_MW": round(float(arr.min()), 1),
        "energy_MWh": round(float(arr.sum()), 1),
    }


def summarise(
    data: dict,
    n,
    report,
    *,
    countries: list[str],
    year: int,
    week: int | None,
    options: dict,
) -> dict:
    """Build the summary dictionary for one instance."""
    params = data["Parameters"]
    step_h = params["Time step (min)"] / 60.0
    horizon = params["Time horizon (min)"] / 60.0

    generators = data["Generators"]
    thermal = {k: v for k, v in generators.items() if v["Type"] == "Thermal"}
    profiled = {k: v for k, v in generators.items() if v["Type"] == "Profiled"}

    # Fleet capacity by carrier, taken from the network so carriers survive.
    gens = n.generators
    thermal_by_carrier = (
        gens[gens.committable].groupby("carrier").p_nom.agg(["count", "sum"])
    )
    profiled_by_carrier = (
        gens[~gens.committable].groupby("carrier").p_nom.agg(["count", "sum"])
    )

    load = np.zeros(int(horizon / step_h))
    for bus in data["Buses"].values():
        v = bus["Load (MW)"]
        load = load + (np.full(len(load), v) if np.isscalar(v) else np.asarray(v))

    thermal_capacity = float(gens[gens.committable].p_nom.sum())

    summary = {
        "instance": {
            "countries": countries,
            "year": year,
            "week": week,
            "start": str(n.snapshots[0]),
            "end": str(n.snapshots[-1]),
            "time_steps": len(n.snapshots),
            "time_step_min": int(params["Time step (min)"]),
            "format_version": params["Version"],
        },
        "size": {
            "buses": len(data["Buses"]),
            "branches": len(data.get("Transmission lines", {})),
            "thermal_units": len(thermal),
            "profiled_units": len(profiled),
            "storage_units": len(data.get("Storage units", {})),
            "binary_variables_approx": len(thermal) * len(n.snapshots) * 3,
        },
        "demand": _series_stats(load),
        "capacity": {
            "thermal_MW": round(thermal_capacity, 1),
            "thermal_by_carrier_MW": {
                c: round(float(r["sum"]), 1) for c, r in thermal_by_carrier.iterrows()
            },
            "thermal_units_by_carrier": {
                c: int(r["count"]) for c, r in thermal_by_carrier.iterrows()
            },
            "profiled_by_carrier_MW": {
                c: round(float(r["sum"]), 1) for c, r in profiled_by_carrier.iterrows()
            },
            "storage_MW": round(float(n.storage_units.p_nom.sum()), 1)
            if len(n.storage_units)
            else 0.0,
            "storage_MWh": round(
                float((n.storage_units.p_nom * n.storage_units.max_hours).sum()), 1
            )
            if len(n.storage_units)
            else 0.0,
            "thermal_to_peak_load_ratio": round(
                thermal_capacity / float(load.max()), 3
            )
            if load.max() > 0
            else None,
        },
        "grid": {
            "voltages_kV": sorted(
                {int(v) for v in n.buses.v_nom.dropna().unique() if v > 0}
            ),
            "total_line_capacity_MW": round(float(n.lines.s_nom.sum()), 1),
            "transformers": int(len(n.transformers)),
        },
        "imports": _import_summary(n, data),
        "options": options,
        "feasibility": {
            "power_balance_penalty_eur_per_MW": params["Power balance penalty ($/MW)"],
            "flow_limit_penalty_eur_per_MW": next(
                (
                    line["Flow limit penalty ($/MW)"]
                    for line in data.get("Transmission lines", {}).values()
                ),
                None,
            ),
            "profiled_curtailable": all(
                u.get("Minimum power (MW)", 0.0) == 0.0 for u in profiled.values()
            ),
        },
        "sources": {
            "fleet": "powerplantmatching (published matched dataset)",
            "demand": f"Open Power System Data time_series {sources.OPSD_VERSION}",
            "vre": f"Open Power System Data time_series {sources.OPSD_VERSION}",
            "grid": f"PyPSA-Eur osm-prebuilt {sources.OSM_VERSION}",
            "cross_border_flows": "Energy-Charts (ENTSO-E physical flows)",
            "unit_commitment_params": "PyPSA-Eur data/unit_commitment.csv",
            "costs": f"PyPSA technology-data costs_{options.get('costs_year')}.csv",
        },
        "provenance_notes": {k: list(v) for k, v in report.items()},
    }
    return summary


def _import_summary(n, data: dict) -> dict:
    gens = n.generators
    imp = gens[gens.carrier == "import"]
    exports = n.loads[n.loads.carrier == "export"] if "carrier" in n.loads else []
    borders = sorted(
        {name.split(" @ ")[0].replace("import ", "") for name in imp.index}
    )
    import_energy = 0.0
    if len(imp):
        pu = n.generators_t.p_max_pu.reindex(columns=imp.index).fillna(1.0)
        import_energy = float((pu * imp.p_nom).sum().sum())
    export_energy = 0.0
    if len(exports):
        export_energy = float(n.loads_t.p_set[exports.index].sum().sum())
    return {
        "enabled": bool(len(imp) or len(exports)),
        "borders": borders,
        "max_import_MW": round(float(imp.p_nom.sum()), 1) if len(imp) else 0.0,
        "import_energy_MWh": round(import_energy, 1),
        "export_energy_MWh": round(export_energy, 1),
        "net_MWh": round(import_energy - export_energy, 1),
    }
