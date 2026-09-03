#!/usr/bin/env python3
"""
Generate a benchmark set: N instances per eligible EU country, each on a
different randomly chosen week of the year.

    python generate_batch.py                     # 5 per country, 2019, seed 0
    python generate_batch.py --per-country 3 --seed 7
    python generate_batch.py --countries BE,FR    # restrict the selection

Each instance is written as ``instances/<CC>/<CC>_<year>_w<NN>.json`` with a
``.summary.json`` beside it, plus a top-level ``instances/index.json``
describing the whole set and the eligibility screen that produced it.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import traceback
from pathlib import Path

import pandas as pd

from generate import add_common_arguments, build_instance, write_instance
from pypsa_uc_gen import build, sources

log = logging.getLogger("batch")

#: EU member states. Cyprus and Malta are absent from powerplantmatching and
#: are not connected to the continental grid, so they cannot be screened.
EU_COUNTRIES = [
    "AT", "BE", "BG", "HR", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU",
    "IE", "IT", "LV", "LT", "LU", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
]

#: A country enters the benchmark only if every input needed to build a
#: self-consistent instance is present for the whole year.
MIN_LOAD_COVERAGE = 0.995   # fraction of hours with a load reading
MIN_THERMAL_RATIO = 0.10    # committable capacity / peak load
MIN_BUSES = 5
MIN_LINES = 4


def screen(countries: list[str], year: int) -> pd.DataFrame:
    """Assess each country against the eligibility rules; never raises."""
    opsd = sources._read_opsd()
    grid = sources.load_osm_grid()
    buses, lines = grid["buses"], grid["lines"]
    hours = pd.date_range(f"{year}-01-01", f"{year}-12-31 23:00", freq="h")

    available = set(sources._harmonised_fleet().country.dropna().unique())
    rows = []
    for c in countries:
        row: dict = {"country": c}

        col = next(
            (f"{c}{p}" for p in sources._LOAD_PATTERNS if f"{c}{p}" in opsd.columns),
            None,
        )
        if col is None:
            row.update(load_coverage=0.0, peak_MW=float("nan"))
        else:
            s = opsd[col].reindex(hours)
            alt = f"{c}{sources._LOAD_PATTERNS[1]}"
            if alt in opsd.columns:
                s = s.fillna(opsd[alt].reindex(hours))
            row.update(load_coverage=float(s.notna().mean()), peak_MW=float(s.max()))

        bb = buses[(buses.country == c) & ~buses.dc]
        ids = set(bb.bus_id)
        row["buses"] = len(bb)
        row["lines"] = int((lines.bus0.isin(ids) & lines.bus1.isin(ids)).sum())

        if c in available:
            fleet = sources.load_powerplants([c], year=year)
            thermal = fleet[fleet.carrier.isin(build.THERMAL_CARRIERS)]
            row["thermal_units"] = len(thermal)
            row["thermal_MW"] = float(thermal.p_nom.sum())
        else:
            row["thermal_units"], row["thermal_MW"] = 0, 0.0

        peak = row["peak_MW"]
        row["thermal_ratio"] = (
            row["thermal_MW"] / peak if peak and peak == peak and peak > 0 else 0.0
        )
        reasons = []
        if row["load_coverage"] < MIN_LOAD_COVERAGE:
            reasons.append(f"load coverage {row['load_coverage']:.1%}")
        if row["thermal_ratio"] < MIN_THERMAL_RATIO:
            reasons.append(f"thermal/peak {row['thermal_ratio']:.2f}")
        if row["buses"] < MIN_BUSES:
            reasons.append(f"{row['buses']} buses")
        if row["lines"] < MIN_LINES:
            reasons.append(f"{row['lines']} lines")
        row["eligible"] = not reasons
        row["excluded_because"] = "; ".join(reasons)
        rows.append(row)

    return pd.DataFrame(rows).set_index("country")


def usable_weeks(year: int, hours: int) -> list[int]:
    """ISO weeks whose whole horizon lies inside the OPSD coverage."""
    opsd_index = sources._read_opsd().index
    lo, hi = opsd_index.min(), opsd_index.max()
    weeks = []
    for w in range(1, 54):
        try:
            snaps = build.snapshots_for(year, week=w, hours=hours)
        except ValueError:
            continue
        if snaps[0] >= lo and snaps[-1] <= hi:
            weeks.append(w)
    return weeks


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Generate a per-country benchmark set of UC instances.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--countries", default=None,
                   help="comma-separated ISO-2 codes; default is all EU states")
    p.add_argument("--per-country", type=int, default=5,
                   help="instances per country, each on a different week")
    p.add_argument("--year", type=int, default=2019)
    p.add_argument("--hours", type=int, default=168, help="horizon length")
    p.add_argument("--all-weeks", action="store_true",
                   help="use every usable week of the year instead of sampling "
                        "--per-country of them")
    p.add_argument("--seed", type=int, default=0,
                   help="seed for week selection, so a run is reproducible")
    p.add_argument("--outdir", default="instances")
    p.add_argument("--gzip", action="store_true")
    p.add_argument("--dry-run", action="store_true",
                   help="print the eligibility screen and planned weeks, build nothing")
    p.add_argument("--reindex", action="store_true",
                   help="rebuild index.json from the summaries already on disk, "
                        "without regenerating anything")
    add_common_arguments(p)
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def reindex(outdir: Path) -> int:
    """Rebuild index.json from the summaries present on disk."""
    written = []
    for summary_path in sorted(outdir.glob("*/*.summary.json")):
        meta = json.loads(summary_path.read_text())
        inst = meta["instance"]
        size = meta["size"]
        written.append({
            "country": inst["countries"][0], "week": inst["week"],
            "path": str(summary_path.with_name(meta["files"]["instance"])
                        .relative_to(outdir)),
            "summary": str(summary_path.relative_to(outdir)),
            "buses": size["buses"], "branches": size["branches"],
            "thermal_units": size["thermal_units"],
            "peak_MW": meta["demand"]["peak_MW"],
        })
    index_path = outdir / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    index.setdefault("generated", {}).update(
        {"instances": len(written), "failed": 0}
    )
    index["instances"] = written
    index["failures"] = []
    index_path.write_text(json.dumps(index, indent=1))
    print(f"reindexed {len(written)} instances -> {index_path}")
    return 0


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.reindex:
        return reindex(Path(args.outdir))
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    countries = (
        [c.strip().upper() for c in args.countries.split(",") if c.strip()]
        if args.countries else EU_COUNTRIES
    )

    print(f"screening {len(countries)} countries for {args.year} ...")
    table = screen(countries, args.year)
    shown = table[["load_coverage", "peak_MW", "buses", "lines",
                   "thermal_units", "thermal_MW", "thermal_ratio", "eligible"]]
    print(shown.to_string(float_format=lambda v: f"{v:,.2f}"))
    excluded = table[~table.eligible]
    if len(excluded):
        print("\nexcluded:")
        for c, r in excluded.iterrows():
            print(f"  {c}: {r.excluded_because}")

    eligible = table.index[table.eligible].tolist()
    weeks = usable_weeks(args.year, args.hours)
    per = len(weeks) if args.all_weeks else args.per_country
    print(f"\n{len(eligible)} eligible countries x {per} instances "
          f"from {len(weeks)} usable weeks -> {len(eligible) * per} instances")

    rng = random.Random(args.seed)
    if args.all_weeks:
        plan = {c: list(weeks) for c in eligible}
    else:
        plan = {c: sorted(rng.sample(weeks, args.per_country)) for c in eligible}
    for c in eligible:
        print(f"  {c}: weeks {plan[c]}")
    if args.dry_run:
        return 0

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    written, failed = [], []
    total = len(eligible) * args.per_country
    done = 0

    for country in eligible:
        for week in plan[country]:
            done += 1
            stem = f"{country}_{args.year}_w{week:02d}"
            suffix = ".json.gz" if args.gzip else ".json"
            path = outdir / country / (stem + suffix)
            try:
                snapshots = build.snapshots_for(args.year, week=week, hours=args.hours)
                data, meta, _ = build_instance(
                    [country], snapshots, args, week=week
                )
                write_instance(data, meta, path)
                size, cap = meta["size"], meta["capacity"]
                print(
                    f"[{done:3d}/{total}] {stem}: {size['buses']} buses, "
                    f"{size['branches']} branches, {size['thermal_units']} thermal, "
                    f"peak {meta['demand']['peak_MW']:,.0f} MW, "
                    f"thermal/peak {cap['thermal_to_peak_load_ratio']}"
                )
                written.append({
                    "country": country, "week": week,
                    "path": str(path.relative_to(outdir)),
                    "summary": str(
                        (path.parent / f"{stem}.summary.json").relative_to(outdir)
                    ),
                    "buses": size["buses"], "branches": size["branches"],
                    "thermal_units": size["thermal_units"],
                    "peak_MW": meta["demand"]["peak_MW"],
                })
            except Exception as exc:  # keep going; report at the end
                log.debug("%s", traceback.format_exc())
                print(f"[{done:3d}/{total}] {stem}: FAILED {type(exc).__name__}: {exc}")
                failed.append({"country": country, "week": week, "error": str(exc)})

    index = {
        "generated": {
            "year": args.year, "hours": args.hours,
            "per_country": args.per_country, "seed": args.seed,
            "instances": len(written), "failed": len(failed),
        },
        "options": {
            "min_capacity_MW": args.min_capacity,
            "imports": args.imports,
            "initial_conditions": args.initial_conditions,
            "costs_year": args.costs_year,
            "co2_price_eur_per_t": args.co2_price,
            "voll_eur_per_MW": args.voll,
            "flow_penalty_eur_per_MW": args.flow_penalty,
        },
        "eligibility_rules": {
            "min_load_coverage": MIN_LOAD_COVERAGE,
            "min_thermal_to_peak_ratio": MIN_THERMAL_RATIO,
            "min_buses": MIN_BUSES,
            "min_lines": MIN_LINES,
        },
        "screen": json.loads(table.to_json(orient="index")),
        "instances": written,
        "failures": failed,
    }
    (outdir / "index.json").write_text(json.dumps(index, indent=1))

    print(f"\n{len(written)} instances written to {outdir}/")
    print(f"index: {outdir / 'index.json'}")
    if failed:
        print(f"{len(failed)} failed:")
        for f in failed:
            print(f"  {f['country']} w{f['week']:02d}: {f['error']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
