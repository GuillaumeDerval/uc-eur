# instances / PL

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `PL_2019_w08.json.gz` | PL | 2019-02-18 | 7 | 246 | 382 | 59 | 32,604 | 226 | 6 | 24,946 | 3,569,115 | 186,299 | ok | [plot](PL_2019_w08.png) |
| `PL_2019_w19.json.gz` | PL | 2019-05-06 | 7 | 246 | 382 | 59 | 32,604 | 226 | 6 | 23,251 | 3,282,146 | 183,581 | ok | [plot](PL_2019_w19.png) |
| `PL_2019_w20.json.gz` | PL | 2019-05-13 | 7 | 246 | 382 | 59 | 32,604 | 226 | 6 | 24,230 | 3,313,659 | 201,380 | ok | [plot](PL_2019_w20.png) |
| `PL_2019_w36.json.gz` | PL | 2019-09-02 | 7 | 246 | 382 | 59 | 32,604 | 227 | 6 | 23,189 | 3,193,026 | 275,829 | ok | [plot](PL_2019_w36.png) |
| `PL_2019_w46.json.gz` | PL | 2019-11-11 | 7 | 246 | 382 | 59 | 32,604 | 227 | 6 | 24,719 | 3,355,884 | 239,898 | ok | [plot](PL_2019_w46.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 1 run-of-river units (168 MW) bounded by installed capacity; no measured inflow series available
- 41 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 59 committable thermal units, 32604 MW, carriers ['CCGT', 'coal', 'lignite', 'solid biomass']
- 6 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- OPSD 2020-10-06 entsoe transparency, peak 22154 MW / mean 18381 MW
- OPSD 2020-10-06 entsoe transparency, peak 22278 MW / mean 18766 MW
- OPSD 2020-10-06 entsoe transparency, peak 23215 MW / mean 18928 MW
- OPSD 2020-10-06 entsoe transparency, peak 24289 MW / mean 19466 MW
- OPSD 2020-10-06 entsoe transparency, peak 24561 MW / mean 20451 MW
- OPSD measured generation as the hourly upper bound for PL/onwind
- PL: 73 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 149 substations inside them in proportion to their connection capacity, 16 regions to their nearest
- carriers not modelled: Steam Turbine (3 units, 289 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 33 MW mean, hydro reservoir 10 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 60 MW mean, hydro reservoir 17 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 65 MW mean, hydro reservoir 22 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 65 MW mean, hydro reservoir 23 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 65 MW mean, hydro reservoir 37 MW mean
- dropped 2239 units below 10 MW (4587 MW, 9.5% of fleet capacity)
- excluded 4 reservoir units (125 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 1093 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 1109 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 1199 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 1428 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 1642 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 246 AC buses, 341 lines, 41 transformers, [220, 380, 400] kV

</details>
