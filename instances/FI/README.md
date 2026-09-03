# instances / FI

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `FI_2019_w21.json.gz` | FI | 2019-05-20 | 7 | 105 | 146 | 81 | 12,199 | 284 | 0 | 9,869 | 1,447,615 | 362,427 | ok |
| `FI_2019_w23.json.gz` | FI | 2019-06-03 | 7 | 105 | 146 | 81 | 12,199 | 283 | 0 | 9,567 | 1,428,602 | 322,203 | ok |
| `FI_2019_w28.json.gz` | FI | 2019-07-08 | 7 | 105 | 146 | 81 | 12,199 | 284 | 0 | 9,775 | 1,479,135 | 302,881 | ok |
| `FI_2019_w40.json.gz` | FI | 2019-09-30 | 7 | 105 | 146 | 81 | 12,199 | 285 | 0 | 11,322 | 1,652,815 | 365,646 | ok |
| `FI_2019_w41.json.gz` | FI | 2019-10-07 | 7 | 105 | 146 | 81 | 12,199 | 285 | 0 | 11,423 | 1,650,581 | 428,334 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 32 run-of-river units (1195 MW) bounded by installed capacity; no measured inflow series available
- 5 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 81 committable thermal units, 12199 MW, carriers ['CCGT', 'coal', 'lignite', 'nuclear', 'oil', 'solid biomass']
- FI: 10 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 54 substations inside them in proportion to their connection capacity, 1 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 10583 MW / mean 9172 MW
- OPSD 2020-10-06 entsoe transparency, peak 10593 MW / mean 9531 MW
- OPSD 2020-10-06 entsoe transparency, peak 8823 MW / mean 7944 MW
- OPSD 2020-10-06 entsoe transparency, peak 9021 MW / mean 8025 MW
- OPSD 2020-10-06 entsoe transparency, peak 9066 MW / mean 8017 MW
- OPSD measured generation as the hourly upper bound for FI/onwind
- carriers not modelled: Steam Turbine (2 units, 156 MW), battery (7 units, 190 MW), heat storage (13 units, 608 MW), other (2 units, 80 MW), waste (2 units, 88 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 130 MW mean, other renewable 25 MW mean, peat 597 MW mean, waste 31 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 42 MW mean, other renewable 25 MW mean, peat 101 MW mean, waste 19 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 46 MW mean, other renewable 7 MW mean, peat 273 MW mean, waste 16 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 60 MW mean, other renewable 11 MW mean, peat 293 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 67 MW mean, other renewable 26 MW mean, peat 554 MW mean, waste 25 MW mean
- dropped 82 units below 10 MW (316 MW, 1.7% of fleet capacity)
- excluded 15 reservoir units (1568 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 1803 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 1918 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 2157 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 2176 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 2550 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 105 AC buses, 141 lines, 5 transformers, [220, 400] kV

</details>
