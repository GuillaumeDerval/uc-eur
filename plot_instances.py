#!/usr/bin/env python3
"""
Plot the commitment picture for each instance: what the committable fleet is
left to serve, and the capacity actually committed to serve it.

    julia --project=julia julia/dispatch_series.jl instances   # solve first
    python plot_instances.py instances

Reads the ``.dispatch.json`` written by ``julia/dispatch_series.jl`` and writes
``<instance>.png`` beside it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_one(dispatch: Path, out: Path | None = None) -> Path:
    d = json.loads(dispatch.read_text())
    summary_path = dispatch.with_name(
        dispatch.name.replace(".dispatch.json", ".summary.json"))
    meta = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    inst = meta.get("instance", {})

    T = d["time_steps"]
    start = inst.get("start")
    step = inst.get("time_step_min", 60)
    x = (pd.date_range(start, periods=T, freq=f"{step}min") if start
         else np.arange(T))

    residual = np.array(d["residual_demand_MW"])
    committed = np.array(d["committed_capacity_MW"])
    cmin = np.array(d["committed_minimum_MW"])
    shed = np.array(d["load_shed_MW"])

    load = np.array(d["load_MW"])

    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(12, 6.4), sharex=True,
        gridspec_kw={"height_ratios": [3.2, 1], "hspace": 0.12})

    ax.plot(x, load, color="#999", lw=1.0, ls="--", zorder=2,
            label="total demand")
    ax.fill_between(x, cmin, committed, color="#cfe3f7", zorder=1,
                    label="committed band (min stable level to capacity)")
    ax.plot(x, committed, color="#1f6fb4", lw=1.7, zorder=3,
            label="committed capacity")
    ax.plot(x, cmin, color="#1f6fb4", lw=0.9, ls=":", zorder=3)
    ax.plot(x, residual, color="#c2340a", lw=1.8, zorder=4,
            label="demand net of non-committable generation")
    if shed.max() > 1e-6:
        ax.fill_between(x, residual, residual + shed, color="#d62728", alpha=.45,
                        zorder=5, label=f"load shed ({shed.sum():,.0f} MWh)")

    title = dispatch.name.replace(".dispatch.json", "")
    if inst.get("countries"):
        span = f"{inst['start'][:10]} .. {inst['end'][:10]}"
        title = f"{title}   —   {'+'.join(inst['countries'])}, {span}"
    headroom = committed - residual
    # A tiny negative is the solver sitting exactly on the capacity limit.
    low = headroom.min()
    low = 0.0 if abs(low) < 1e-3 else low
    subtitle = (f"peak demand {load.max():,.0f} MW   |   "
                f"peak residual {residual.max():,.0f} MW   |   "
                f"peak committed {committed.max():,.0f} MW   |   "
                f"min headroom {low:,.0f} MW   |   "
                f"units on {min(d['units_on'])}-{max(d['units_on'])}"
                f" of {d['thermal_units']}")
    ax.set_title(f"{title}\n{subtitle}", fontsize=10.5, pad=10)
    ax.set_ylabel("MW")
    ax.grid(alpha=.25)
    ax.set_ylim(0, max(load.max(), committed.max()) * 1.08)

    ax2.step(x, d["units_on"], where="post", color="#444", lw=1.2)
    ax2.set_ylabel("units on")
    ax2.set_ylim(0, max(d["thermal_units"], max(d["units_on"])) * 1.15 + 1)
    ax2.grid(alpha=.25)
    ax2.set_xlabel("time (UTC)" if start else "time step")
    if start:
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%a %d %b"))
        fig.autofmt_xdate(rotation=0, ha="center")

    # One legend for the figure, under both panels.
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.06))

    out = out or dispatch.with_name(dispatch.name.replace(".dispatch.json", ".png"))
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out


def main(argv=None) -> int:
    args = argv or sys.argv[1:]
    if not args:
        args = ["instances", "instances_BE_52weeks", "instances_BE_outages"]
    files: list[Path] = []
    for a in args:
        p = Path(a)
        files += [p] if p.is_file() else sorted(p.rglob("*.dispatch.json"))
    if not files:
        print("no .dispatch.json found; run julia/dispatch_series.jl first")
        return 1
    for i, f in enumerate(files, 1):
        out = plot_one(f)
        print(f"[{i:3d}/{len(files)}] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
