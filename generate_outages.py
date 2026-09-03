#!/usr/bin/env python3
"""
Generate an outage family: many instances for the same country and week that
differ only in which power stations are unavailable.

    python generate_outages.py --country BE --week 44 --count 50

Every instance keeps the same demand, weather, grid and imports, so any
difference in the solution comes from the missing units alone. Each variant
removes 1 or 2 thermal units drawn without replacement from the fleet, with a
seeded RNG so a run is reproducible, and no combination is repeated. Variant 0
is the intact system, included as the baseline to compare against.

The removed units are recorded both in the build report and under
``outage`` in each ``.summary.json``.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from pathlib import Path

from generate import add_common_arguments, build_instance, write_instance
from pypsa_uc_gen import build

log = logging.getLogger("outages")


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Generate instances with power stations removed.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--country", default="BE", help="single ISO-2 code")
    p.add_argument("--year", type=int, default=2019)
    p.add_argument("--week", type=int, required=True, help="ISO week, held fixed")
    p.add_argument("--hours", type=int, default=168)
    p.add_argument("--count", type=int, default=50,
                   help="number of outage variants, excluding the baseline")
    p.add_argument("--max-removed", type=int, default=2,
                   help="each variant removes 1..N units")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--outdir", default="instances_outage")
    p.add_argument("--no-baseline", action="store_true",
                   help="skip the intact-system instance")
    add_common_arguments(p)
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def draw_combinations(units, count, max_removed, seed):
    """Distinct, sorted unit combinations of size 1..max_removed."""
    rng = random.Random(seed)
    possible = len(units) * (1 + (len(units) - 1) // 2 if max_removed >= 2 else 0)
    if count > possible:
        raise ValueError(
            f"asked for {count} variants but only {possible} distinct "
            f"combinations of 1..{max_removed} units exist for {len(units)} units"
        )
    seen, out = set(), []
    while len(out) < count:
        k = rng.randint(1, min(max_removed, len(units)))
        combo = tuple(sorted(rng.sample(units, k)))
        if combo not in seen:
            seen.add(combo)
            out.append(combo)
    return out


def main(argv=None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    country = args.country.strip().upper()

    fleet = build.fleet_for([country], args.year, args.min_capacity)
    thermal = fleet[fleet.carrier.isin(build.THERMAL_CARRIERS)]
    if thermal.empty:
        raise SystemExit(f"{country} has no committable thermal units to remove")
    units = sorted(thermal.uid)
    print(f"{country} week {args.week}: {len(units)} thermal units "
          f"({thermal.p_nom.sum():,.0f} MW) available for outage")

    combos = draw_combinations(units, args.count, args.max_removed, args.seed)
    snapshots = build.snapshots_for(args.year, week=args.week, hours=args.hours)
    outdir = Path(args.outdir) / f"{country}_{args.year}_w{args.week:02d}"

    plan = ([()] if not args.no_baseline else []) + combos
    written, failed = [], []
    capacity = dict(zip(thermal.uid, thermal.p_nom))

    for i, combo in enumerate(plan):
        name = "v00_baseline" if not combo else f"v{i:02d}_" + "_".join(
            u.replace(" ", "-").replace("/", "-")[:18] for u in combo
        )
        path = outdir / f"{name}.json"
        try:
            data, meta, report = build_instance(
                [country], snapshots, args, week=args.week,
            ) if not combo else build_instance_with_outage(
                [country], snapshots, args, combo
            )
            meta["outage"] = {
                "removed_units": list(combo),
                "removed_count": len(combo),
                "removed_MW": round(sum(capacity[u] for u in combo), 1),
                "baseline": not combo,
            }
            write_instance(data, meta, path)
            written.append({
                "name": name, "path": str(path.relative_to(Path(args.outdir))),
                "removed_units": list(combo),
                "removed_MW": meta["outage"]["removed_MW"],
                "thermal_units": meta["size"]["thermal_units"],
                "thermal_MW": meta["capacity"]["thermal_MW"],
                "peak_MW": meta["demand"]["peak_MW"],
            })
            print(f"[{i + 1:3d}/{len(plan)}] {name}: "
                  f"-{meta['outage']['removed_MW']:,.0f} MW, "
                  f"{meta['size']['thermal_units']} thermal units left")
        except Exception as exc:
            print(f"[{i + 1:3d}/{len(plan)}] {name}: FAILED {type(exc).__name__}: {exc}")
            failed.append({"name": name, "removed_units": list(combo), "error": str(exc)})

    index = {
        "family": {
            "country": country, "year": args.year, "week": args.week,
            "hours": args.hours, "seed": args.seed,
            "max_removed": args.max_removed,
            "variants": len(written), "failed": len(failed),
            "note": "identical demand, weather, grid and imports; only the "
                    "available thermal units differ",
        },
        "fleet": [
            {"uid": u, "carrier": c, "p_nom_MW": round(float(m), 1)}
            for u, c, m in zip(thermal.uid, thermal.carrier, thermal.p_nom)
        ],
        "variants": written,
        "failures": failed,
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (Path(args.outdir) / "index.json").write_text(json.dumps(index, indent=1))
    print(f"\n{len(written)} instances -> {outdir}")
    print(f"index: {Path(args.outdir) / 'index.json'}")
    return 1 if failed else 0


def build_instance_with_outage(countries, snapshots, args, combo):
    """build_instance, with the named units removed from the fleet."""
    import generate
    from pypsa_uc_gen import convert, summary, validate

    n, report = build.build_network(
        countries=countries, snapshots=snapshots,
        costs_year=args.costs_year, co2_price=args.co2_price,
        min_capacity=args.min_capacity, imports=args.imports,
        import_cost=args.import_cost,
        initial_conditions=args.initial_conditions,
        drop_units=tuple(combo),
    )
    data = convert.network_to_uc(
        n, power_balance_penalty=args.voll,
        flow_limit_penalty=args.flow_penalty,
        initial_conditions=args.initial_conditions,
    )
    validate.validate(data, strict=True)
    notes = validate.feasibility_notes(data)
    options = {
        "min_capacity_MW": args.min_capacity, "imports": args.imports,
        "import_cost_eur_per_MWh": args.import_cost,
        "initial_conditions": args.initial_conditions,
        "costs_year": args.costs_year, "co2_price_eur_per_t": args.co2_price,
        "voll_eur_per_MW": args.voll, "flow_penalty_eur_per_MW": args.flow_penalty,
    }
    meta = summary.summarise(
        data, n, report, countries=countries,
        year=int(snapshots[0].year), week=args.week, options=options,
    )
    meta["feasibility"]["warnings"] = notes
    return data, meta, report


if __name__ == "__main__":
    sys.exit(main())
