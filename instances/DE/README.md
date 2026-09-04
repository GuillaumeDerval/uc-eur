# instances / DE

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `DE_2019_w01.json.gz` | DE | 2018-12-31 | 7 | 780 | 1,172 | 346 | 93,635 | 2,850 | 26 | 80,869 | 10,830,970 | -1,562,073 | ok | [plot](DE_2019_w01.png) |
| `DE_2019_w04.json.gz` | DE | 2019-01-21 | 7 | 780 | 1,172 | 341 | 89,561 | 2,863 | 26 | 85,138 | 12,107,553 | -1,194,821 | ok | [plot](DE_2019_w04.png) |
| `DE_2019_w17.json.gz` | DE | 2019-04-22 | 7 | 780 | 1,172 | 341 | 89,561 | 2,865 | 26 | 78,878 | 9,710,986 | -274,626 | ok | [plot](DE_2019_w17.png) |
| `DE_2019_w36.json.gz` | DE | 2019-09-02 | 7 | 780 | 1,172 | 341 | 89,561 | 2,350 | 26 | 75,047 | 9,588,125 | 21,034 | ok | [plot](DE_2019_w36.png) |
| `DE_2019_w52.json.gz` | DE | 2019-12-23 | 7 | 780 | 1,172 | 341 | 89,561 | 2,352 | 26 | 67,727 | 8,816,969 | -270,669 | ok | [plot](DE_2019_w52.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 153 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 26 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 341 committable thermal units, 89561 MW, carriers ['CCGT', 'OCGT', 'coal', 'lignite', 'nuclear', 'oil', 'solid biomass']
- 346 committable thermal units, 93635 MW, carriers ['CCGT', 'OCGT', 'coal', 'lignite', 'nuclear', 'oil', 'solid biomass']
- 85 run-of-river units (2700 MW) bounded by installed capacity; no measured inflow series available
- DE: 394 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2018) spread over the 511 substations inside them in proportion to their connection capacity, 173 regions to their nearest
- DE: 394 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 511 substations inside them in proportion to their connection capacity, 173 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 58740 MW / mean 46505 MW
- OPSD 2020-10-06 entsoe transparency, peak 66817 MW / mean 52443 MW
- OPSD 2020-10-06 entsoe transparency, peak 69037 MW / mean 52337 MW
- OPSD 2020-10-06 entsoe transparency, peak 69801 MW / mean 53806 MW
- OPSD 2020-10-06 entsoe transparency, peak 75981 MW / mean 63587 MW
- OPSD measured generation as the hourly upper bound for DE/solar, DE/onwind, DE/offwind
- carriers not modelled: Combustion Engine (39 units, 823 MW), Steam Turbine (88 units, 10398 MW), battery (19 units, 335 MW), biogas (1 units, 10 MW), hydrogen storage (1 units, 14 MW), other (41 units, 1754 MW), waste (102 units, 2905 MW)
- carriers not modelled: Combustion Engine (39 units, 823 MW), Steam Turbine (88 units, 10398 MW), battery (23 units, 397 MW), biogas (1 units, 10 MW), hydrogen storage (1 units, 14 MW), other (41 units, 1754 MW), waste (101 units, 2863 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 359 MW mean, geothermal 17 MW mean, hydro reservoir 202 MW mean, other 352 MW mean, waste 1077 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 428 MW mean, geothermal 18 MW mean, hydro reservoir 313 MW mean, other 476 MW mean, waste 1079 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 450 MW mean, geothermal 17 MW mean, hydro reservoir 89 MW mean, other 479 MW mean, waste 1226 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 18 MW mean, hydro reservoir 243 MW mean, other 295 MW mean, waste 1087 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 23 MW mean, hydro reservoir 97 MW mean, other 459 MW mean, waste 1424 MW mean
- dropped 93099 units below 10 MW (89023 MW, 41.4% of fleet capacity)
- dropped 99639 units below 10 MW (93824 MW, 43.5% of fleet capacity)
- excluded 8 reservoir units (320 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 9 borders, net -1611 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 9 borders, net -1635 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 9 borders, net -7112 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 9 borders, net -9298 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 9 borders, net 125 MW mean; imports are curtailable, exports are fixed load
- kept the largest connected AC component: 780 of 781 buses (1 dropped as isolated)
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 780 AC buses, 1019 lines, 153 transformers, [220, 380, 400] kV
- skipped 1 PHS units with no reservoir capacity in the data (Tanzmuhle)

</details>
