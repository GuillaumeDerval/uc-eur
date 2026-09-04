#!/usr/bin/env python3
"""
Write a README.md into every instance directory, tabulating what each instance
contains.

    python describe_instances.py instances instances_BE_52weeks instances_BE_outages

Reads the ``.summary.json`` beside each instance, plus ``results*.json`` from a
solver run when present, and writes one table per subdirectory and an overview
at the top of each set. Safe to re-run; it only writes README.md files.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def key_of(name: str) -> str:
    """Filename without the .gz, so a run made before compression still matches."""
    return Path(name).name.removesuffix(".gz")


def load_results(root: Path) -> dict:
    """Solve outcomes keyed by instance filename, if a run has happened."""
    out = {}
    for f in list(root.glob("results*.json")):
        try:
            for r in json.loads(f.read_text()).get("results", []):
                out[key_of(r["file"])] = r
        except (json.JSONDecodeError, KeyError):
            continue
    return out


def load_summaries(root: Path) -> list[tuple[Path, dict]]:
    return sorted(
        ((p, json.loads(p.read_text())) for p in root.glob("*/*.summary.json")),
        key=lambda t: t[0].name,
    )


def fmt(x, nd=0):
    return "-" if x is None else f"{x:,.{nd}f}"


def days_of(meta: dict) -> str:
    hours = meta["instance"]["time_steps"] * meta["instance"]["time_step_min"] / 60
    d = hours / 24
    return f"{d:g}"


def outcome(res: dict | None) -> str:
    if not res:
        return "-"
    if res.get("status") == "ERROR":
        return "error"
    shed = res.get("load_shed_MWh", 0.0)
    if not res.get("ok"):
        return f"{shed:,.1f} MWh shed"
    return "ok"


def instance_row(meta: dict, res: dict | None, outage: bool, sub: Path) -> str:
    i, s, c, d = meta["instance"], meta["size"], meta["capacity"], meta["demand"]
    imp = meta.get("imports", {})
    name = meta["files"]["instance"]
    stem = name.removesuffix(".gz").removesuffix(".json")
    cells = [f"`{name}`"]
    if outage:
        o = meta.get("outage", {})
        removed = ", ".join(o.get("removed_units", [])) or "_none (baseline)_"
        cells += [removed, fmt(o.get("removed_MW"))]
    else:
        cells += [i["countries"][0], i["start"][:10], days_of(meta)]
    cells += [
        fmt(s["buses"]), fmt(s["branches"]),
        fmt(s["thermal_units"]), fmt(c["thermal_MW"]),
        fmt(s["profiled_units"]), fmt(s["storage_units"]),
        fmt(d["peak_MW"]), fmt(d["energy_MWh"]),
        fmt(imp.get("net_MWh")), outcome(res),
    ]
    png = sub / f"{stem}.png"
    cells.append(f"[plot]({stem}.png)" if png.exists() else "-")
    return "| " + " | ".join(cells) + " |"


HEAD_STD = ("Instance | Country | Start (UTC) | Days | Buses | Branches | "
            "Thermal units | Thermal MW | Profiled | Storage | Peak MW | "
            "Demand MWh | Net imports MWh | Solved | Dispatch")
HEAD_OUT = ("Instance | Units removed | MW removed | Buses | Branches | "
            "Thermal units | Thermal MW | Profiled | Storage | Peak MW | "
            "Demand MWh | Net imports MWh | Solved | Dispatch")


def table(rows: list[str], header: str) -> str:
    cols = header.split(" | ")
    return "\n".join(
        ["| " + " | ".join(cols) + " |",
         "|" + "|".join(["---"] * len(cols)) + "|", *rows]
    )


def write_subdir_readme(sub: Path, items, results, outage: bool, title: str) -> None:
    rows = [instance_row(m, results.get(key_of(m["files"]["instance"])), outage, sub)
            for _, m in items]
    head = HEAD_OUT if outage else HEAD_STD
    notes = sorted({
        note for _, m in items
        for group in m.get("provenance_notes", {}).values() for note in group
    })
    body = [f"# {title}", "",
            f"{len(items)} instances. Columns come from each instance's "
            "`.summary.json`; *Solved* is from the last `solve_all.jl` run, and "
            "*Dispatch* links a plot of demand net of non-committable generation "
            "against the capacity committed at the optimum.", "",
            table(rows, head), ""]
    if notes:
        body += ["<details><summary>Provenance and exclusions for this "
                 "directory</summary>", ""]
        body += [f"- {n}" for n in notes]
        body += ["", "</details>", ""]
    (sub / "README.md").write_text("\n".join(body))


def describe(root: Path) -> None:
    summaries = load_summaries(root)
    if not summaries:
        print(f"{root}: no summaries found, skipped")
        return
    results = load_results(root)
    outage = any("outage" in m for _, m in summaries)

    by_dir = defaultdict(list)
    for p, m in summaries:
        by_dir[p.parent].append((p, m))

    for sub, items in sorted(by_dir.items()):
        write_subdir_readme(sub, items, results, outage, f"{root.name} / {sub.name}")

    # Overview: one line per subdirectory.
    rows = []
    for sub, items in sorted(by_dir.items()):
        metas = [m for _, m in items]
        solved = sum(1 for m in metas
                     if (results.get(key_of(m["files"]["instance"])) or {}).get("ok"))
        rows.append("| " + " | ".join([
            f"[`{sub.name}/`]({sub.name}/README.md)",
            str(len(metas)),
            metas[0]["instance"]["countries"][0],
            fmt(metas[0]["size"]["buses"]),
            fmt(metas[0]["size"]["branches"]),
            fmt(metas[0]["size"]["thermal_units"]),
            fmt(max(m["demand"]["peak_MW"] for m in metas)),
            f"{solved}/{len(metas)}" if results else "-",
        ]) + " |")
    header = ("Directory | Instances | Country | Buses | Branches | "
              "Thermal units | Peak MW | Solved")
    total = len(summaries)
    body = [f"# {root.name}", "",
            f"{total} UnitCommitment.jl 0.4 instances, gzipped. "
            "See the repository README for how they are built and what every "
            "field means.", "",
            table(rows, header), "",
            "Each subdirectory has its own `README.md` with a row per instance, "
            "and every instance has a `.summary.json` beside it.", ""]
    (root / "README.md").write_text("\n".join(body))
    print(f"{root}: wrote README.md and {len(by_dir)} subdirectory tables "
          f"({total} instances)")


def main(argv=None) -> int:
    roots = (argv or sys.argv[1:]) or [
        "instances", "instances_BE_52weeks", "instances_BE_outages"]
    for r in roots:
        p = Path(r)
        if p.is_dir():
            describe(p)
        else:
            print(f"{r}: not a directory, skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
