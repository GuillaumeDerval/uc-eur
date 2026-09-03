#!/usr/bin/env python3
"""
Generate one UnitCommitment.jl 0.4 instance from PyPSA data sources.

    python generate.py --countries BE --week 1
    python generate.py --countries BE,FR --week 12 --co2-price 80
    python generate.py --countries ES --start 2019-07-15 --hours 336

Writes ``<name>.json`` and ``<name>.summary.json``. See README.md for the data
sources and the modelling assumptions.
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import sys
from pathlib import Path

from pypsa_uc_gen import build, convert, summary, validate

log = logging.getLogger("generate")


def add_common_arguments(p: argparse.ArgumentParser) -> None:
    """Options shared by the single-instance and batch generators."""
    fleet = p.add_argument_group("fleet")
    fleet.add_argument(
        "--min-capacity", type=float, default=10.0,
        help="drop units below this capacity in MW; 10 removes registry noise "
             "(Germany lists ~4600 sub-10 MW units, 4%% of its capacity) without "
             "affecting any other country",
    )
    fleet.add_argument(
        "--initial-conditions", choices=["free", "on", "off"], default="free",
        help="what to assert about the hour before the horizon. 'free' (default) "
             "asserts nothing and lets the solver choose; 'on' starts every unit "
             "at its minimum stable level, 'off' starts everything shut down. "
             "There is no dataset of real initial states, and cold-starting a "
             "whole national fleet forces load shedding that reflects the "
             "assumption rather than the power system",
    )

    imp = p.add_argument_group("imports")
    imp.add_argument(
        "--imports", choices=["historical", "none"], default="historical",
        help="'historical' pins observed cross-border physical flows on every "
             "border leaving the selection; borders inside it stay endogenous",
    )
    imp.add_argument(
        "--import-cost", type=float, default=0.0,
        help="EUR/MWh charged on historical imports",
    )

    econ = p.add_argument_group("economics")
    econ.add_argument("--costs-year", type=int, default=2020,
                      help="PyPSA technology-data vintage")
    econ.add_argument("--co2-price", type=float, default=0.0, help="EUR/tCO2")
    econ.add_argument(
        "--voll", type=float, default=10_000.0,
        help="power balance penalty in EUR/MW: the unlimited load shedding",
    )
    econ.add_argument(
        "--flow-penalty", type=float, default=5_000.0,
        help="transmission flow limit penalty in EUR/MW; keep finite so "
             "congestion is priced rather than infeasible",
    )


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Generate a UnitCommitment.jl 0.4 instance from PyPSA data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    geo = p.add_argument_group("geography and time")
    geo.add_argument("--countries", default="BE",
                     help="comma-separated ISO-2 codes, e.g. BE or BE,FR,NL")
    geo.add_argument("--year", type=int, default=2019, help="calendar year")
    geo.add_argument("--week", type=int, default=None,
                     help="ISO week; the horizon starts Monday 00:00 UTC")
    geo.add_argument("--start", default=None,
                     help="explicit start timestamp, overrides --week")
    geo.add_argument("--hours", type=int, default=168, help="horizon length")

    add_common_arguments(p)

    out = p.add_argument_group("output")
    out.add_argument("-o", "--output", default=None, help="output .json or .json.gz")
    out.add_argument("--outdir", default="instances",
                     help="directory used when --output is not given")
    out.add_argument("--gzip", action="store_true", help="write .json.gz")
    out.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def build_instance(countries, snapshots, args, *, week=None, grid=None):
    """Build, convert, validate and summarise one instance."""
    n, report = build.build_network(
        countries=countries,
        snapshots=snapshots,
        costs_year=args.costs_year,
        co2_price=args.co2_price,
        min_capacity=args.min_capacity,
        imports=args.imports,
        import_cost=args.import_cost,
        initial_conditions=args.initial_conditions,
        grid=grid,
    )
    data = convert.network_to_uc(
        n,
        power_balance_penalty=args.voll,
        flow_limit_penalty=args.flow_penalty,
        initial_conditions=args.initial_conditions,
    )
    validate.validate(data, strict=True)
    notes = validate.feasibility_notes(data)
    for note in notes:
        log.warning("feasibility: %s", note)

    options = {
        "min_capacity_MW": args.min_capacity,
        "imports": args.imports,
        "import_cost_eur_per_MWh": args.import_cost,
        "initial_conditions": args.initial_conditions,
        "costs_year": args.costs_year,
        "co2_price_eur_per_t": args.co2_price,
        "voll_eur_per_MW": args.voll,
        "flow_penalty_eur_per_MW": args.flow_penalty,
    }
    meta = summary.summarise(
        data, n, report, countries=countries,
        year=int(snapshots[0].year), week=week, options=options,
    )
    meta["feasibility"]["warnings"] = notes
    return data, meta, report


def write_instance(data: dict, meta: dict, path: Path) -> Path:
    """Write the instance and its summary side by side."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=1)
    if str(path).endswith(".gz"):
        with gzip.open(path, "wt") as fh:
            fh.write(payload)
        stem = path.name[: -len(".json.gz")]
    else:
        path.write_text(payload)
        stem = path.stem
    meta["files"] = {"instance": path.name, "summary": f"{stem}.summary.json"}
    (path.parent / f"{stem}.summary.json").write_text(json.dumps(meta, indent=1))
    return path


def main(argv=None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    countries = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    if args.week is None and args.start is None:
        args.week = 1
        log.info("neither --week nor --start given, defaulting to ISO week 1")

    snapshots = build.snapshots_for(
        year=args.year, week=args.week, start=args.start, hours=args.hours
    )
    log.info("horizon: %s .. %s (%d hours)",
             snapshots[0], snapshots[-1], len(snapshots))

    data, meta, report = build_instance(countries, snapshots, args, week=args.week)

    if args.output:
        path = Path(args.output)
    else:
        tag = "".join(countries)
        when = f"{args.year}w{args.week:02d}" if args.week else str(args.start)[:10]
        suffix = ".json.gz" if args.gzip else ".json"
        path = Path(args.outdir) / f"uc_{tag}_{when}_{args.hours}h{suffix}"
    write_instance(data, meta, path)

    size = meta["size"]
    print(f"\nwrote {path}  ({path.stat().st_size / 1e6:.2f} MB)")
    print(f"      {meta['files']['summary']}")
    for key in ("buses", "branches", "thermal_units", "profiled_units", "storage_units"):
        print(f"  {key:17s} {size[key]}")
    print(f"  {'peak load':17s} {meta['demand']['peak_MW']:.0f} MW")
    print(f"  {'thermal capacity':17s} {meta['capacity']['thermal_MW']:.0f} MW")
    print("\ndata provenance and exclusions")
    print(report.render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
