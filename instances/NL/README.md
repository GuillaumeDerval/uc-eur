# instances / NL

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `NL_2019_w06.json.gz` | NL | 2019-02-04 | 7 | 60 | 108 | 44 | 20,569 | 106 | 0 | 21,281 | 2,921,924 | -177,788 | ok | [plot](NL_2019_w06.png) |
| `NL_2019_w07.json.gz` | NL | 2019-02-11 | 7 | 60 | 108 | 44 | 20,569 | 106 | 0 | 20,679 | 2,765,965 | -135,076 | ok | [plot](NL_2019_w07.png) |
| `NL_2019_w21.json.gz` | NL | 2019-05-20 | 7 | 60 | 108 | 44 | 20,569 | 106 | 0 | 17,029 | 2,349,210 | -115,687 | ok | [plot](NL_2019_w21.png) |
| `NL_2019_w32.json.gz` | NL | 2019-08-05 | 7 | 60 | 108 | 44 | 20,569 | 106 | 0 | 16,498 | 2,280,476 | 86,294 | ok | [plot](NL_2019_w32.png) |
| `NL_2019_w33.json.gz` | NL | 2019-08-12 | 7 | 60 | 108 | 44 | 20,569 | 106 | 0 | 16,676 | 2,294,052 | 160,474 | ok | [plot](NL_2019_w33.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 44 committable thermal units, 20569 MW, carriers ['CCGT', 'coal', 'nuclear', 'solid biomass']
- 8 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- NL: 25 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 24 substations inside them in proportion to their connection capacity, 13 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 14148 MW / mean 12064 MW
- OPSD 2020-10-06 entsoe transparency, peak 14519 MW / mean 11993 MW
- OPSD 2020-10-06 entsoe transparency, peak 14742 MW / mean 12063 MW
- OPSD 2020-10-06 entsoe transparency, peak 17158 MW / mean 13851 MW
- OPSD 2020-10-06 entsoe transparency, peak 17926 MW / mean 14651 MW
- OPSD measured generation as the hourly upper bound for NL/onwind, NL/offwind
- OPSD measured generation as the hourly upper bound for NL/solar, NL/onwind, NL/offwind
- carriers not modelled: Steam Turbine (11 units, 1938 MW), battery (12 units, 243 MW), biogas (3 units, 160 MW), heat storage (1 units, 22 MW), waste (10 units, 696 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 3953 MW mean, waste 227 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 3971 MW mean, waste 229 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 4174 MW mean, waste 236 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 4289 MW mean, waste 246 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 5226 MW mean, waste 199 MW mean
- dropped 143 units below 10 MW (622 MW, 2.0% of fleet capacity)
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -1058 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -689 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -804 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 514 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 955 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 60 AC buses, 100 lines, 8 transformers, [220, 380] kV

</details>
