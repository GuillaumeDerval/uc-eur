# instances / IT

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `IT_2019_w05.json.gz` | IT | 2019-01-28 | 7 | 572 | 842 | 116 | 53,998 | 1,182 | 15 | 48,824 | 6,219,801 | 945,845 | ok | [plot](IT_2019_w05.png) |
| `IT_2019_w13.json.gz` | IT | 2019-03-25 | 7 | 572 | 842 | 116 | 53,998 | 1,181 | 15 | 43,280 | 5,493,061 | 906,869 | ok | [plot](IT_2019_w13.png) |
| `IT_2019_w15.json.gz` | IT | 2019-04-08 | 7 | 572 | 842 | 116 | 53,998 | 1,182 | 15 | 43,485 | 5,532,242 | 724,501 | ok | [plot](IT_2019_w15.png) |
| `IT_2019_w16.json.gz` | IT | 2019-04-15 | 7 | 572 | 842 | 116 | 53,998 | 1,182 | 15 | 41,829 | 5,214,786 | 696,564 | ok | [plot](IT_2019_w16.png) |
| `IT_2019_w37.json.gz` | IT | 2019-09-09 | 7 | 572 | 842 | 116 | 53,998 | 1,180 | 15 | 43,846 | 5,775,206 | 510,796 | ok | [plot](IT_2019_w37.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 116 committable thermal units, 53998 MW, carriers ['CCGT', 'coal', 'oil', 'solid biomass']
- 15 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 156 run-of-river units (8147 MW) bounded by installed capacity; no measured inflow series available
- 63 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- IT: 102 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 391 substations inside them in proportion to their connection capacity, 11 regions to their nearest; dropped 5 region(s) over 150 km from the grid (ITG2D, ITG2E, ITG2H, ITG2G, ITG2F)
- OPSD 2020-10-06 entsoe transparency, peak 41269 MW / mean 30554 MW
- OPSD 2020-10-06 entsoe transparency, peak 42639 MW / mean 32201 MW
- OPSD 2020-10-06 entsoe transparency, peak 42709 MW / mean 33644 MW
- OPSD 2020-10-06 entsoe transparency, peak 42949 MW / mean 32498 MW
- OPSD 2020-10-06 entsoe transparency, peak 48242 MW / mean 36670 MW
- OPSD measured generation as the hourly upper bound for IT/solar, IT/onwind
- carriers not modelled: Steam Turbine (14 units, 4013 MW), battery (26 units, 1215 MW), biogas (1 units, 46 MW), geothermal (23 units, 834 MW), waste (7 units, 376 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 506 MW mean, geothermal 662 MW mean, hydro reservoir 515 MW mean, other 3143 MW mean, waste 47 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 578 MW mean, geothermal 663 MW mean, hydro reservoir 608 MW mean, other 3135 MW mean, waste 36 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 582 MW mean, geothermal 659 MW mean, hydro reservoir 844 MW mean, other 3074 MW mean, waste 45 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 588 MW mean, geothermal 657 MW mean, hydro reservoir 636 MW mean, other 3154 MW mean, waste 36 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 758 MW mean, geothermal 658 MW mean, hydro reservoir 952 MW mean, other 2843 MW mean, waste 45 MW mean
- dropped 181 units below 10 MW (865 MW, 0.9% of fleet capacity)
- excluded 96 reservoir units (5339 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 3040 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 4146 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 4313 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 5398 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 5630 MW mean; imports are curtailable, exports are fixed load
- kept the largest connected AC component: 572 of 590 buses (18 dropped as isolated)
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 572 AC buses, 779 lines, 63 transformers, [220, 225, 380, 400] kV
- skipped 7 PHS units with no reservoir capacity in the data (Gargnano, Capriati, Fadalto, Riva Del Garda)

</details>
