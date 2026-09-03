# instances / IE

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `IE_2019_w16.json.gz` | IE | 2019-04-15 | 7 | 56 | 71 | 15 | 5,342 | 122 | 1 | 4,757 | 576,358 | -5,072 | ok |
| `IE_2019_w21.json.gz` | IE | 2019-05-20 | 7 | 56 | 71 | 15 | 5,342 | 122 | 1 | 3,863 | 538,525 | 27,932 | ok |
| `IE_2019_w22.json.gz` | IE | 2019-05-27 | 7 | 56 | 71 | 15 | 5,342 | 75 | 1 | 4,297 | 566,299 | -41,546 | ok |
| `IE_2019_w46.json.gz` | IE | 2019-11-11 | 7 | 56 | 71 | 15 | 5,342 | 122 | 1 | 5,040 | 657,934 | -24,668 | ok |
| `IE_2019_w47.json.gz` | IE | 2019-11-18 | 7 | 56 | 71 | 15 | 5,342 | 122 | 1 | 5,063 | 647,904 | -14,380 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 1 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 15 committable thermal units, 5342 MW, carriers ['CCGT', 'coal', 'lignite', 'oil', 'solid biomass']
- 4 run-of-river units (215 MW) bounded by installed capacity; no measured inflow series available
- 5 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- IE: 8 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 46 substations inside them in proportion to their connection capacity, 1 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 3826 MW / mean 3093 MW
- OPSD 2020-10-06 entsoe transparency, peak 3863 MW / mean 3141 MW
- OPSD 2020-10-06 entsoe transparency, peak 4370 MW / mean 3327 MW
- OPSD 2020-10-06 entsoe transparency, peak 4797 MW / mean 3662 MW
- OPSD 2020-10-06 entsoe transparency, peak 4908 MW / mean 3699 MW
- OPSD measured generation as the hourly upper bound for IE/onwind
- carriers not modelled: Steam Turbine (4 units, 1310 MW), battery (17 units, 817 MW), waste (2 units, 85 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 0 MW mean, peat 320 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 1 MW mean, peat 280 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 1 MW mean, peat 284 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 3 MW mean, peat 190 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: peat 217 MW mean
- dropped 15 units below 10 MW (79 MW, 0.6% of fleet capacity)
- excluded 1 reservoir units (45 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net -147 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net -247 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net -30 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net -86 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net 166 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 56 AC buses, 66 lines, 5 transformers, [220, 275, 400] kV

</details>
