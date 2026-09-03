# instances / BE

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `BE_2019_w20.json.gz` | BE | 2019-05-13 | 7 | 71 | 90 | 35 | 10,310 | 99 | 2 | 12,715 | 1,802,768 | 12,802 | ok |
| `BE_2019_w26.json.gz` | BE | 2019-06-24 | 7 | 71 | 90 | 35 | 10,310 | 99 | 2 | 12,878 | 1,808,276 | 49,082 | ok |
| `BE_2019_w32.json.gz` | BE | 2019-08-05 | 7 | 71 | 90 | 35 | 10,310 | 99 | 2 | 13,670 | 1,914,320 | -394,424 | ok |
| `BE_2019_w33.json.gz` | BE | 2019-08-12 | 7 | 71 | 90 | 35 | 10,310 | 99 | 2 | 12,723 | 1,886,721 | -294,182 | ok |
| `BE_2019_w51.json.gz` | BE | 2019-12-16 | 7 | 71 | 90 | 35 | 10,310 | 99 | 2 | 15,011 | 2,047,319 | -49,738 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 12 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 2 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 3 run-of-river units (37 MW) bounded by installed capacity; no measured inflow series available
- 35 committable thermal units, 10310 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- BE: 44 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 51 substations inside them in proportion to their connection capacity, 21 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 10053 MW / mean 8507 MW
- OPSD 2020-10-06 entsoe transparency, peak 10818 MW / mean 8697 MW
- OPSD 2020-10-06 entsoe transparency, peak 11122 MW / mean 9325 MW
- OPSD 2020-10-06 entsoe transparency, peak 11186 MW / mean 9412 MW
- OPSD 2020-10-06 entsoe transparency, peak 12635 MW / mean 10113 MW
- OPSD measured generation as the hourly upper bound for BE/solar, BE/onwind, BE/offwind
- carriers not modelled: Steam Turbine (10 units, 2377 MW), battery (6 units, 177 MW), waste (10 units, 294 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 427 MW mean, waste 189 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 470 MW mean, waste 233 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 510 MW mean, waste 238 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 606 MW mean, waste 243 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 705 MW mean, waste 251 MW mean
- dropped 106 units below 10 MW (397 MW, 2.1% of fleet capacity)
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -1751 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -2348 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -296 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 292 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 76 MW mean; imports are curtailable, exports are fixed load
- kept the largest connected AC component: 71 of 72 buses (1 dropped as isolated)
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 71 AC buses, 78 lines, 12 transformers, [220, 225, 380, 400] kV

</details>
