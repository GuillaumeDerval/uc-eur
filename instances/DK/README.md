# instances / DK

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `DK_2019_w05.json.gz` | DK | 2019-01-28 | 7 | 33 | 40 | 24 | 6,841 | 28 | 0 | 7,177 | 958,689 | -6,865 | ok | [plot](DK_2019_w05.png) |
| `DK_2019_w07.json.gz` | DK | 2019-02-11 | 7 | 33 | 40 | 24 | 6,841 | 28 | 0 | 6,750 | 894,184 | 7,136 | ok | [plot](DK_2019_w07.png) |
| `DK_2019_w10.json.gz` | DK | 2019-03-04 | 7 | 33 | 40 | 24 | 6,841 | 28 | 0 | 8,647 | 1,022,750 | -128,011 | ok | [plot](DK_2019_w10.png) |
| `DK_2019_w20.json.gz` | DK | 2019-05-13 | 7 | 33 | 40 | 24 | 6,841 | 28 | 0 | 6,073 | 684,695 | 228,433 | ok | [plot](DK_2019_w20.png) |
| `DK_2019_w47.json.gz` | DK | 2019-11-18 | 7 | 33 | 40 | 24 | 6,841 | 29 | 0 | 6,858 | 910,088 | 75,631 | ok | [plot](DK_2019_w47.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 2 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 24 committable thermal units, 6841 MW, carriers ['CCGT', 'coal', 'oil', 'solid biomass']
- DK: 10 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 21 substations inside them in proportion to their connection capacity, 5 regions to their nearest; dropped 1 region(s) over 150 km from the grid (DK014)
- OPSD 2020-10-06 entsoe transparency, peak 4587 MW / mean 3612 MW
- OPSD 2020-10-06 entsoe transparency, peak 5048 MW / mean 4046 MW
- OPSD 2020-10-06 entsoe transparency, peak 5211 MW / mean 4060 MW
- OPSD 2020-10-06 entsoe transparency, peak 5317 MW / mean 4158 MW
- OPSD 2020-10-06 entsoe transparency, peak 5529 MW / mean 4345 MW
- OPSD measured generation as the hourly upper bound for DK/solar, DK/onwind, DK/offwind
- carriers not modelled: Steam Turbine (4 units, 440 MW), battery (1 units, 30 MW), waste (4 units, 153 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 139 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 140 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 160 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 170 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 178 MW mean
- dropped 89 units below 10 MW (297 MW, 2.4% of fleet capacity)
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net -41 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net -762 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 1360 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 42 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 450 MW mean; imports are curtailable, exports are fixed load
- kept the largest connected AC component: 33 of 48 buses (15 dropped as isolated)
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 33 AC buses, 38 lines, 2 transformers, [220, 400] kV

</details>
