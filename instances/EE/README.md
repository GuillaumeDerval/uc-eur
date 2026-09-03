# instances / EE

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `EE_2019_w07.json.gz` | EE | 2019-02-11 | 7 | 18 | 22 | 5 | 538 | 84 | 0 | 1,980 | 249,618 | 43,038 | ok |
| `EE_2019_w22.json.gz` | EE | 2019-05-27 | 7 | 18 | 22 | 5 | 538 | 84 | 0 | 1,527 | 208,521 | 64,297 | ok |
| `EE_2019_w31.json.gz` | EE | 2019-07-29 | 7 | 18 | 22 | 5 | 538 | 81 | 0 | 1,687 | 214,340 | 63,079 | ok |
| `EE_2019_w36.json.gz` | EE | 2019-09-02 | 7 | 18 | 22 | 5 | 538 | 84 | 0 | 1,737 | 197,406 | 20,223 | ok |
| `EE_2019_w44.json.gz` | EE | 2019-10-28 | 7 | 18 | 22 | 5 | 538 | 84 | 0 | 1,755 | 219,105 | 76,146 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 1 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 5 committable thermal units, 538 MW, carriers ['CCGT', 'oil', 'solid biomass']
- EE: 5 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 14 substations inside them in proportion to their connection capacity
- OPSD 2020-10-06 entsoe transparency, peak 1017 MW / mean 823 MW
- OPSD 2020-10-06 entsoe transparency, peak 1073 MW / mean 844 MW
- OPSD 2020-10-06 entsoe transparency, peak 1262 MW / mean 1010 MW
- OPSD 2020-10-06 entsoe transparency, peak 1323 MW / mean 1069 MW
- OPSD 2020-10-06 entsoe transparency, peak 994 MW / mean 796 MW
- OPSD measured generation as the hourly upper bound for EE/solar, EE/onwind
- carriers not modelled: battery (1 units, 26 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 47 MW mean, oil shale 539 MW mean, other renewable 7 MW mean, peat 5 MW mean, waste 16 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 53 MW mean, oil shale 483 MW mean, other renewable 7 MW mean, peat 5 MW mean, waste 17 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 54 MW mean, oil shale 239 MW mean, other renewable 6 MW mean, peat 5 MW mean, waste 0 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 59 MW mean, oil shale 332 MW mean, other renewable 5 MW mean, peat 3 MW mean, waste 13 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 70 MW mean, oil shale 224 MW mean, other renewable 7 MW mean, peat 4 MW mean, waste 18 MW mean
- dropped 20 units below 10 MW (83 MW, 7.5% of fleet capacity)
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 120 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 256 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 375 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 383 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 453 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 18 AC buses, 21 lines, 1 transformers, [220, 330] kV

</details>
