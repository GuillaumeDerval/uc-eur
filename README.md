# pypsa_uc_gen

Generate realistic [UnitCommitment.jl](https://anl-ceeesa.github.io/UnitCommitment.jl/0.4/)
0.4 benchmark instances for European countries from open PyPSA-ecosystem data:
real power plant fleets, the real transmission grid, measured demand, measured
wind and solar, and observed cross-border flows.

```bash
# one instance
python generate.py --countries BE --week 1

# the full benchmark set: 5 weeks x 23 EU countries
python generate_batch.py
julia --project=julia julia/add_initial_conditions.jl instances
julia --project=julia julia/solve_all.jl instances
```

---

## 1. What an instance contains

Each instance is a week (168 hourly steps by default) of operational unit
commitment for one country, in UnitCommitment.jl's 0.4 JSON format.

| Requirement | How it is met |
|---|---|
| **Existing resources only** | Capacities come from `powerplantmatching`. Nothing is extendable; there is no investment decision. |
| **Electricity only, fixed demand** | One `Load (MW)` series per bus, from measured national demand. |
| **0-1 commitment** | Thermal units carry minimum up/down times, startup costs, ramp limits, startup/shutdown limits and minimum stable levels. |
| **DC-OPF** | The real AC transmission grid: substations, lines with their reactances and thermal ratings, and transformers. |
| **Unlimited load shedding** | A finite `Power balance penalty ($/MW)`. See §6. |
| **Customisable horizon** | `--week`/`--start` and `--hours`. |
| **Customisable geography** | `--countries BE`, `--countries BE,FR,NL`, any European selection. |

Every instance is written with a `.summary.json` beside it (§4).

---

## 2. Where every number comes from

Nothing is synthesised. Each dataset is fetched once and cached under
`data/cache/`.

| Data | Source |
|---|---|
| Power plant fleet: capacity, carrier, coordinates, efficiency, commissioning and retirement dates, storage energy capacity | [`powerplantmatching`](https://github.com/PyPSA/powerplantmatching) — the matched dataset it publishes |
| Transmission grid: substations, lines (`r`, `x`, `s_nom`), transformers, HVDC links | [PyPSA-Eur `osm-prebuilt`](https://data.pypsa.org/workflows/eur/osm/) v0.7 — the same file PyPSA-Eur feeds to its `base_network` rule |
| Hourly demand | [Open Power System Data](https://data.open-power-system-data.org/time_series/) `time_series` 2020-10-06, `*_load_actual_entsoe_transparency` — the series and version PyPSA-Eur uses |
| Hourly wind and solar | OPSD `*_solar_generation_actual`, `*_wind_onshore_generation_actual`, `*_wind_offshore_generation_actual` |
| Measured hourly generation for carriers with no fleet or cost data (reservoir hydro, geothermal, waste, oil shale, peat, "Others") | [Energy-Charts](https://api.energy-charts.info) `public_power` |
| NUTS3 region geometry | [Eurostat GISCO](https://gisco-services.ec.europa.eu/distribution/v2/nuts/) NUTS 2021, level 3 |
| NUTS3 population and GDP | Eurostat `nama_10r_3popgdp` and `nama_10r_3gdp` |
| Cross-border physical flows per interconnector | [Energy-Charts](https://api.energy-charts.info) `cbpf` (Fraunhofer ISE, republishing ENTSO-E) — no API key |
| Min up/down time, startup cost, `p_min_pu`, ramp rates | [PyPSA-Eur `data/unit_commitment.csv`](https://github.com/PyPSA/pypsa-eur/blob/master/data/unit_commitment.csv) |
| Fuel prices, VOM, efficiencies, CO2 intensities | [PyPSA technology-data](https://github.com/PyPSA/technology-data) `outputs/costs_<year>.csv` |

Marginal costs are assembled exactly as PyPSA-Eur does:

```
marginal_cost = VOM + (fuel + co2_price * CO2_intensity) / efficiency   [EUR/MWh_el]
```

Startup costs in the PyPSA-Eur table are per MW of `p_nom` and are multiplied
by unit capacity, again as in PyPSA-Eur's `add_electricity.py`.

### How the pieces are put together

1. **Grid.** Load osm-prebuilt, keep AC substations in the selected countries,
   keep branches with both ends inside, and keep only the **largest connected
   component** — isolated islands cannot exchange power and would silently
   distort the instance.
2. **Fleet.** Filter units by commissioning/retirement date against the
   instance year, drop units below `--min-capacity`, and place each unit at its
   **nearest substation** using its coordinates.
3. **Demand.** Take the country's measured hourly load and spread it over the
   substations with a NUTS3 key -- 60% GDP, 40% population (§5).
4. **Wind and solar.** Take the measured national generation series and split
   it across buses in proportion to the VRE capacity `powerplantmatching`
   locates at each. The national total therefore stays equal to what was
   actually generated.
5. **Other carriers.** Reservoir hydro, geothermal, waste, oil shale, peat and
   "Others" never reach the thermal fleet -- they need an inflow series, or
   technology-data has no cost entry -- yet they really generated. Add them as
   profiled units bounded by Energy-Charts measured hourly generation, sited on
   the matching powerplantmatching plants where those exist.
6. **Imports.** Pin observed flows on every border leaving the selection (§3).
7. **Convert** to UnitCommitment.jl 0.4, structurally validate, and summarise.

---

## 3. Imports

A country modelled alone is an island, so a net importer sheds load. Both
options below are supported; they answer different questions.

**Endogenous — let the optimiser decide.** Widen the selection. osm-prebuilt
carries the real cross-border AC lines (BE–FR ≈ 6.9 GW, BE–NL 3.4 GW,
BE–LU 1.0 GW), so they appear automatically and flows are optimised:

```bash
python generate.py --countries BE,FR,NL --imports none
```

**Exogenous — pin the observed flows** (the default). Keeps instances small:

```bash
python generate.py --countries BE --imports historical
```

Imports become **curtailable profiled units** bounded by the observed hourly
flow; net exports become **fixed load**. Borders *inside* the selection stay
endogenous — imposing history on a border that is already modelled would
fabricate energy. There is a test for exactly that.

For Belgium in the first week of 2019 this is the difference between 1.57% and
0.00% load shedding.

> **Is there a PyPSA dataset of historical flows?** No. OPSD's time series has
> no flow columns at all, and PyPSA-Eur ships no historical exchange data — it
> computes flows endogenously. Energy-Charts is therefore the one source here
> from outside the PyPSA ecosystem. Note its `cbpf` endpoint reports **GW**
> while its power endpoints report MW; the loader converts, and the conversion
> was verified by checking that generation + net import − pumping equals load
> to 0.13%.

---

## 4. Generating

### One instance

```bash
python generate.py --countries BE --week 1
python generate.py --countries ES --start 2019-07-15 --hours 336 --co2-price 80
```

### The benchmark set

```bash
python generate_batch.py --dry-run     # show the screen and planned weeks
python generate_batch.py               # 5 instances per eligible country
julia --project=julia julia/add_initial_conditions.jl instances   # step 2, see below
```

`generate_batch.py` screens every EU country against four rules and reports
why anything is excluded:

| Rule | Threshold |
|---|---|
| Load coverage over the year | ≥ 99.5% of hours |
| Committable capacity / peak load | ≥ 0.10 |
| AC substations | ≥ 5 |
| Internal AC lines | ≥ 4 |

For 2019 this admits **23 countries**. Cyprus and Malta are absent from
powerplantmatching and not on the continental grid; Luxembourg has only 95.3%
load coverage and essentially no thermal fleet; Lithuania's thermal capacity is
2% of its peak load. Each country gets `--per-country` distinct weeks drawn
with a seeded RNG, so a run is reproducible.

Output layout:

```
instances/
  index.json                      the whole set, the screen, and the options used
  results.json                    written by solve_all.jl (not in git)
  BE/
    BE_2019_w20.json.gz           the instance
    BE_2019_w20.summary.json      what is inside it
    ...
```

Instances are stored gzipped -- UnitCommitment.jl reads them directly, as its
own benchmark instances ship that way, and every script here discovers
`.json.gz` too. The three sets committed to this repository are:

| Set | Contents |
|---|---|
| `instances/` | 23 EU countries x 5 weeks of 2019 (115) |
| `instances_BE_52weeks/` | Belgium, every week of 2019 (52) |
| `instances_BE_outages/` | Belgium week 44: baseline + 50 variants each missing 1-2 units (51) |

The downloaded source datasets (~220 MB) are **not** in the repository; they
are re-fetched into `data/cache/` on first use.

### A full year for one country

`--all-weeks` uses every usable week instead of sampling:

```bash
python generate_batch.py --countries BE --all-weeks --outdir instances_BE_52weeks
```

For 2019 that is 52 Belgian instances, one per ISO week, differing only in the
week they cover.

### An outage family

`generate_outages.py` holds the country, week, demand, weather, grid and
imports fixed and varies only which power stations are available, so any
difference between two solutions is attributable to the missing units alone:

```bash
python generate_outages.py --country BE --week 44 --count 50
```

* each variant removes **1 or 2 thermal units**, drawn without replacement with
  a seeded RNG; no combination repeats (Belgium's 35 thermal units give 630
  distinct 1-or-2 combinations)
* variant 0 is the **intact system**, the baseline to compare against
  (`--no-baseline` to skip it)
* the removed units, their capacity and the surviving fleet are recorded under
  `outage` in each `.summary.json` and in the family `index.json`
* removing a unit name that does not exist **raises**, because silently
  ignoring it would build the intact system under an outage label

Unlike the main benchmark set, these instances are **not expected to be
uniformly zero-shedding**: taking 1-2 stations out of a fleet that already
leans on capped historical imports can genuinely leave a week unservable, which
is much of the point. `results.json` records which variants shed and how much.

### Describing a set

`describe_instances.py` writes a `README.md` into every instance directory: an
overview table per set and a row per instance underneath, with country, start
date, horizon, buses, branches, committable units and capacity, peak and total
demand, net imports, and the outcome of the last `solve_all.jl` run. It reads
only the `.summary.json` files, so it is safe to re-run at any time:

```bash
python describe_instances.py instances instances_BE_52weeks instances_BE_outages
```

For an outage family the table replaces country and date with the units removed
and the capacity lost, since those are what vary.

### Plotting the commitment

`julia/dispatch_series.jl` solves each instance and dumps the per-step series a
commitment plot needs; `plot_instances.py` renders them:

```bash
julia --project=julia julia/dispatch_series.jl instances
python plot_instances.py instances
```

Each plot shows demand net of every non-committable source (wind, solar,
run-of-river, imports, measured-generation carriers and storage) against the
capacity committed at the optimum, with the minimum stable level those
committed units impose as the lower edge of the band. The residual line must
lie inside the band; that is the commitment constraint made visible.

**How much do the 0-1 decisions actually matter?** Across the 115 instances the
committed set changes a median of 8 times per week and a mean of 26, and only
15% have two changes or fewer:

| Most dynamic | changes/week | Most static | changes/week |
|---|---|---|---|
| IT | 113 | LV | 1.0 |
| FI | 104 | BE | 1.6 |
| DK | 88 | BG | 2.8 |
| SE | 44 | SI | 4.4 |
| DE | 41 | PL | 5.2 |

Belgium is close to the least dynamic country in the set: its residual demand
swings only 1.5x and the minimum stable level of its committed fleet sits
2238 MW below the trough, so no unit is ever forced off and cycling would only
add startup cost. Italy, by contrast, moves its committed capacity by 80% and
visits 24 distinct commitment states in a week. Raising `--co2-price` from its
default of 0 towards the 2019 EU ETS level of about 25 EUR/t makes cycling
sharply more attractive in coal- and lignite-heavy systems, if you want the
commitment decisions to bite harder.

### Measuring congestion

`julia/congestion.jl` solves each instance twice, once as generated and once
with every flow limit multiplied by ten, and reports the objective difference.
That difference is the cost the **network** imposes, as distinct from the
generation fleet, and is what picks the "moderate congestion" week for an
outage family:

```bash
julia --project=julia julia/congestion.jl instances_BE_52weeks
```

### The summary file

Every instance gets a sibling `.summary.json` so a set can be inspected or
filtered without parsing the instances:

```json
{
 "instance": {"countries": ["BE"], "year": 2019, "week": 20,
              "start": "2019-05-13 00:00:00", "time_steps": 168},
 "size": {"buses": 71, "branches": 90, "thermal_units": 35,
          "profiled_units": 46, "storage_units": 2,
          "binary_variables_approx": 17640},
 "demand": {"peak_MW": 13936.0, "mean_MW": 11002.3, "energy_MWh": 1848386.4},
 "capacity": {"thermal_MW": 10310.0,
              "thermal_by_carrier_MW": {"CCGT": 3891.0, "nuclear": 6219.0},
              "storage_MW": 1308.0, "storage_MWh": 5710.0,
              "thermal_to_peak_load_ratio": 0.74},
 "grid": {"voltages_kV": [220, 225, 380, 400], "transformers": 12},
 "imports": {"enabled": true, "borders": ["BE<-FR", "BE<-GB", "BE<-LU", "BE<-NL"],
             "import_energy_MWh": 368941.0, "net_MWh": 214000.0},
 "feasibility": {"power_balance_penalty_eur_per_MW": 10000.0,
                 "profiled_curtailable": true, "warnings": []},
 "sources": {"...": "dataset names and versions"},
 "provenance_notes": {"...": "every exclusion and assumption for this instance"}
}
```

`demand` is total bus load, which includes export obligations when
`--imports historical` is on; `imports.export_energy_MWh` reports that part
separately.

### Options

| Option | Default | Meaning |
|---|---|---|
| `--countries` | `BE` | comma-separated ISO-2 codes |
| `--week` / `--start`, `--hours` | ISO week 1, 168 | horizon |
| `--min-capacity` | `10` MW | drops registry noise; see §5 |
| `--imports` | `historical` | or `none` |
| `--import-cost` | `0` | EUR/MWh on historical imports |
| `--initial-conditions` | `free` | `free` asserts nothing (see §6); or `on` / `off` |
| `--costs-year` | `2020` | technology-data vintage |
| `--co2-price` | `0` | EUR/tCO2 |
| `--voll` | `10000` | power balance penalty, EUR/MW |
| `--flow-penalty` | `5000` | transmission violation penalty, EUR/MW |

---

## 5. What is left out, where demand goes, and the assumptions

The build report printed after every run — and `provenance_notes` in each
summary — lists exactly what happened for that instance.

**Genuinely dropped:**

* **HVDC links** — UnitCommitment.jl 0.4 has no controllable-branch component.
  The converter *raises* rather than silently dropping them, because a silently
  dropped link disconnects the grid and changes the answer.
* **Battery and heat storage** — outside an electricity-only thermal UC.
* **Units below `--min-capacity`** — Germany's registry lists ~4600 sub-10 MW
  units, 4% of its capacity, that would make the MILP 15× larger. At 10 MW this
  is a no-op for every other country.

**Not in the thermal fleet, but not lost either.** These carriers have no
powerplantmatching entry, or no technology-data cost entry, so they cannot be
committable units — yet they really generated. Each becomes a **profiled unit
bounded by Energy-Charts measured hourly generation**, the same treatment OPSD
wind and solar get, sited on the matching plants where powerplantmatching has
them:

* **Reservoir hydro** — needs an hourly inflow series, none ships free with
  PyPSA, and UnitCommitment.jl's storage model has no inflow field. Sweden runs
  8–9 GW of it; omitting it made Swedish instances shed 9% of demand.
* **Oil shale** — Estonia's entire baseload, absent from powerplantmatching
  (its only Estonian "oil" unit is the 251 MW Kiisa emergency reserve, not the
  ~1.6 GW Narva stations). Omitting it made Estonian instances shed 10%.
* **Geothermal, waste, peat, coal-derived gas, "Others"** — no technology-data
  cost entry. Italy alone runs 3.8 GW of "Others".
* **Gas steam turbines** stay dropped: powerplantmatching resolves natural gas
  to its technology and technology-data has no `Steam Turbine` entry, exactly
  as PyPSA-Eur drops them. For Belgium this is 2.4 GW, and the report says so.

An unclassified Energy-Charts carrier **raises** rather than being ignored:
`EC_CARRIER_CLASS` must label every one as already modelled or supplementary,
because guessing either double-counts capacity or deletes it.

**Included from the fleet:** run-of-river (bounded by installed capacity) and
pumped hydro (reservoir hours from powerplantmatching's energy capacity — Coo
is 1164 MW / 5000 MWh = 4.3 h — and round-trip efficiency from
technology-data).

**The two assumptions.** These are not data. Each is a flag or is stated in
every report:

1. **Transformer reactance.** osm-prebuilt gives transformer ratings but no
   impedance, so each gets `x = 0.1` p.u. DC-OPF needs a finite susceptance on
   every branch.
2. **Value of lost load** (`--voll`).

### Where demand is placed, and how it differs from PyPSA-Eur

This is the part of the pipeline that took the most work to get right, because
getting it wrong does not look like an error -- it looks like a power system
that cannot serve its own load.

| Step | PyPSA-Eur | Here |
|---|---|---|
| NUTS3 weight | `normed(0.6 * normed(gdp) + 0.4 * normed(pop))` | same |
| Load only at substations | `load: substation_only: true` | same |
| Spatial step | area overlap between each NUTS3 region and each substation's Voronoi cell | region's weight split among the substations **inside** it, in proportion to their **connection capacity** |
| Network resolution | clustered to **50 nodes** for all of Europe | full nodal: 1201 buses for France, 780 for Germany |

The last two rows are deliberate deviations, and they are linked. PyPSA-Eur
clusters to ~2 nodes per country before dispatch, so a single radial 420 kV
substation never carries a region's demand on its own. These instances keep the
full nodal grid, where that artifact is real: splitting a region evenly among
its substations handed one Swedish 420 kV bus 2175 MW -- 8% of national peak --
behind a **single 1877 MW line**, which no schedule can serve. Weighting the
split by each substation's incident transmission capacity puts demand where the
network can actually carry it.

Two further corrections, both necessary at full resolution:

* **Tee points carry no load.** osm-prebuilt splits long lines at junctions and
  border crossings, naming the nodes `virtual_*`; they are 29% of European
  buses (39% in Poland). They are genuine electrical nodes but not substations,
  and putting demand on one places it in the middle of a line, where it can
  only be served through that line's rating. This is what
  `substation_only: true` prevents.
* **Off-grid regions are dropped.** NUTS3 includes France's five overseas
  departements and Corsica, Spain's Canaries, Balearics and Melilla, and
  Portugal's Azores and Madeira -- none on the synchronous AC grid, and none in
  the national load series. With no substation inside them their weight would
  land on whichever coastal bus is nearest; France's overseas departements
  alone are 4% of its population. Any region more than 150 km from a modelled
  substation is dropped. The cut is unambiguous: mainland regions sit within
  110 km of a substation, off-grid territories 150 km to 8700 km away.

Each of these was found by tracing shedding back to the individual bus causing
it, and each is recorded in the per-instance report.

## 6. Initial commitment state

There is no observational dataset of what was running the hour before an
arbitrary week, so the Python generator **asserts nothing**: it omits
`Initial status (h)` and `Initial power (MW)` entirely
(`--initial-conditions free`, the default).

This matters. Asserting a state shows up directly in the answer: cold-starting
a whole national fleet at hour 0 forced 3139 MWh of load shedding in Belgium's
week 32 — 0.16% of demand — that vanished entirely once the state was relaxed.
The shedding measured the assumption, not the power system.

`julia/add_initial_conditions.jl` then fills the state in, in place, using
UnitCommitment.jl's own `generate_initial_conditions!`, which solves a
single-period MIP against the first hour's demand to derive a **feasible,
self-consistent** starting point from the instance itself:

```bash
julia --project=julia julia/add_initial_conditions.jl instances
```

Shipped instances therefore carry a real initial state and are **self-contained
for any solver**, not only UnitCommitment.jl — the file is complete, and nothing
about it was invented by hand. The step is idempotent, records itself under
`initial_conditions` in each summary, and rewrites only those two fields.

`--initial-conditions on` / `off` remain available if you want a state asserted
at generation time instead.

## 7. Why every instance is feasible

UnitCommitment.jl's `Power balance penalty ($/MW)` prices **both** unserved
load and surplus generation, so it is unlimited load shedding in both
directions — a unit held on by its minimum up time cannot make the instance
infeasible by over-producing. Together with

* profiled units having `Minimum power (MW) = 0`, so wind, solar and imports
  are always curtailable, and
* a **finite** `Flow limit penalty ($/MW)`, so congestion is priced rather than
  hard,

any commitment schedule that respects the units' own operational constraints is
feasible at system level. The only remaining infeasibility is a contradiction
inside one unit — an initial status incompatible with its minimum downtime, say
— which is exactly the intended notion.

`pypsa_uc_gen.validate.feasibility_notes()` checks these properties; the
generators warn, and each summary records the result under `feasibility`.

---

## 8. Solving and checking

```bash
julia --project=julia julia/solve_all.jl instances            # whole set
julia --project=julia julia/solve_all.jl instances 0.05 900 1 # gap, limit, threads
julia --project=julia julia/solve.jl instances/BE/BE_2019_w20.json  # one instance
```

`solve_all.jl` solves every instance with HiGHS at a deliberately loose MIP gap
— the check is that a schedule with **no load shedding** exists, not that it is
cost-optimal — and writes `instances/results.json` with status, solve time,
objective, load shed and the power balance residual for each.

### Verified results

The full benchmark set, solved with Gurobi at a 0.1% gap on a 10-core laptop:

| | |
|---|---|
| Instances | 115 (23 countries x 5 weeks of 2019) |
| **Reach a schedule with no load shedding** | **114 / 115** |
| Solve time | median 5.4 s, mean 57 s, max 1201 s (109 min total) |
| Worst power-balance residual, any instance, any hour | 2.0e-05 MW |
| Largest | France, 1201 buses, 1998 branches, 103 thermal units, ~97-149 s |

The one exception is discrete unit sizing, not a data defect. `SI_2019_w37`
sheds **1.741 MWh** — 0.0005% of demand, in a single hour. At that hour both
running units are already at full output and the renewables and imports are at
their measured ceiling:

| | |
|---|---|
| Load | 2667.70 MW |
| Te Tol | on, 124.0 / 124.0 MW |
| Krsko 1 | on, 727.0 / 727.0 MW |
| Wind + solar + imports | 1814.96 / 1814.96 MW |
| **Short by** | **1.74 MW** |

The only unused unit, Sostanj, has a minimum stable level of 677.5 MW — some
390x the shortfall — and an eight-hour minimum up time. The cheapest way to use
it is 66 395 EUR to start plus eight hours at 19 084 EUR/h, or **219 066 EUR**,
which also burns 5420 MWh of lignite while curtailing an equal amount of free
wind, solar and imports. Not serving 1.741 MWh costs **17 410 EUR**. The
optimiser takes the option that is 13x cheaper, and the result persists at a
0.001% gap, so it is not solver tolerance.

> **A caveat in UnitCommitment.jl 0.4.2.** `UnitCommitment.validate` returns
> `false` for any solution that sheds load. `src/validation/validate.jl` wraps a
> single-scenario solution as `Dict("s1" => solution)` at line 32, then guards
> the curtailment term with `"Load curtail (MW)" in keys(solution)` at line 569
> — which tests the *wrapped* dict, whose only key is `"s1"`. The term is always
> zero, so the balance looks violated by exactly the amount shed. Both Julia
> scripts here therefore recompute the power balance with curtailment included
> and report that instead.

---

## 9. Layout

```
generate.py                CLI for a single instance
generate_batch.py          eligibility screen + the per-country benchmark set
generate_outages.py        an outage family: one week, varying available units
describe_instances.py      README.md tables for every instance directory
plot_instances.py          commitment plots from the dispatch series
julia/dispatch_series.jl   solve and dump the per-step dispatch series
pypsa_uc_gen/sources.py    fetches and caches the seven datasets
pypsa_uc_gen/build.py      datasets -> pypsa.Network, with a provenance report
pypsa_uc_gen/convert.py    pypsa.Network -> UnitCommitment.jl 0.4
pypsa_uc_gen/validate.py   structural and feasibility checks
pypsa_uc_gen/summary.py    the .summary.json written beside each instance
julia/add_initial_conditions.jl  derive and bake in the initial state
julia/solve.jl             solve one instance
julia/solve_all.jl         solve a directory, check zero load shedding
julia/congestion.jl        cost attributable to the network, per instance
tests/                     pytest; the converter tests need no network
data/cache/                downloaded datasets (OPSD is ~250 MB)
```

Use it as a library when you want the intermediate PyPSA network:

```python
from pypsa_uc_gen import build, convert, validate

snapshots = build.snapshots_for(2019, week=20, hours=168)
n, report = build.build_network(["BE"], snapshots, imports="historical")
data = convert.network_to_uc(n, power_balance_penalty=10_000)
validate.validate(data)
print(report.render())
```

## 10. Setup

```bash
pip install -e .
julia --project=julia -e 'using Pkg; Pkg.instantiate()'
python -m pytest tests/ -q
```

## Notes

* `--week` is **ISO** week numbering, so week 1 of 2019 starts Monday
  2018-12-31. Use `--start` for calendar dates.
* OPSD 2020-10-06 spans roughly 2015 to 2020-09. A window outside it raises a
  clear error rather than silently filling.
* Energy-Charts rate-limits bursts; the fetcher spaces requests and retries
  with backoff, and everything is cached, so a repeated run is offline.
