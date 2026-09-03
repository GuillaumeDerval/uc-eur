# instances / SE

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `SE_2019_w05.json.gz` | SE | 2019-01-28 | 7 | 209 | 279 | 64 | 16,153 | 329 | 1 | 28,676 | 4,069,657 | -67,541 | ok |
| `SE_2019_w06.json.gz` | SE | 2019-02-04 | 7 | 209 | 279 | 64 | 16,153 | 329 | 1 | 27,896 | 3,899,050 | -210,499 | ok |
| `SE_2019_w31.json.gz` | SE | 2019-07-29 | 7 | 209 | 279 | 64 | 16,153 | 326 | 1 | 19,036 | 2,611,647 | -348,501 | ok |
| `SE_2019_w44.json.gz` | SE | 2019-10-28 | 7 | 209 | 279 | 64 | 16,153 | 327 | 1 | 24,527 | 3,594,271 | -629,676 | ok |
| `SE_2019_w49.json.gz` | SE | 2019-12-02 | 7 | 209 | 279 | 64 | 16,153 | 329 | 1 | 27,059 | 3,824,728 | -597,131 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 1 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 23 run-of-river units (2223 MW) bounded by installed capacity; no measured inflow series available
- 24 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 64 committable thermal units, 16153 MW, carriers ['CCGT', 'coal', 'nuclear', 'oil', 'solid biomass']
- OPSD 2020-10-06 entsoe transparency, peak 13533 MW / mean 11451 MW
- OPSD 2020-10-06 entsoe transparency, peak 20220 MW / mean 16823 MW
- OPSD 2020-10-06 entsoe transparency, peak 22592 MW / mean 18263 MW
- OPSD 2020-10-06 entsoe transparency, peak 24233 MW / mean 19879 MW
- OPSD 2020-10-06 entsoe transparency, peak 25103 MW / mean 21377 MW
- OPSD measured generation as the hourly upper bound for SE/onwind
- SE: 21 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 159 substations inside them in proportion to their connection capacity, 1 regions to their nearest
- carriers not modelled: battery (26 units, 506 MW), waste (11 units, 452 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 5714 MW mean, other 438 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 8172 MW mean, other 1275 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 8316 MW mean, other 1766 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 8976 MW mean, other 1103 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 9351 MW mean, other 1928 MW mean
- dropped 32 units below 10 MW (141 MW, 0.4% of fleet capacity)
- excluded 129 reservoir units (12259 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -1253 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -2074 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -3554 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -3748 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -402 MW mean; imports are curtailable, exports are fixed load
- kept the largest connected AC component: 209 of 211 buses (2 dropped as isolated)
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 209 AC buses, 255 lines, 24 transformers, [220, 236, 400, 420] kV
- skipped 1 PHS units with no reservoir capacity in the data (Kymmens)

</details>
