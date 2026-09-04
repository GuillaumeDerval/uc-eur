# instances / ES

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ES_2019_w03.json.gz` | ES | 2019-01-14 | 7 | 1,066 | 1,358 | 100 | 47,145 | 1,889 | 9 | 40,418 | 5,599,827 | 172,537 | ok | [plot](ES_2019_w03.png) |
| `ES_2019_w12.json.gz` | ES | 2019-03-18 | 7 | 1,066 | 1,358 | 100 | 47,145 | 1,889 | 9 | 36,346 | 4,906,295 | 283,879 | ok | [plot](ES_2019_w12.png) |
| `ES_2019_w17.json.gz` | ES | 2019-04-22 | 7 | 1,066 | 1,358 | 100 | 47,145 | 1,889 | 9 | 33,861 | 4,621,956 | 155,755 | ok | [plot](ES_2019_w17.png) |
| `ES_2019_w40.json.gz` | ES | 2019-09-30 | 7 | 1,066 | 1,358 | 100 | 47,145 | 1,889 | 9 | 35,205 | 4,760,214 | 152,253 | ok | [plot](ES_2019_w40.png) |
| `ES_2019_w43.json.gz` | ES | 2019-10-21 | 7 | 1,066 | 1,358 | 100 | 47,145 | 1,889 | 9 | 34,117 | 4,758,069 | 139,324 | ok | [plot](ES_2019_w43.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 100 committable thermal units, 47145 MW, carriers ['CCGT', 'coal', 'lignite', 'nuclear', 'oil', 'solid biomass']
- 102 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 11 run-of-river units (479 MW) bounded by installed capacity; no measured inflow series available
- 9 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- ES: 49 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 677 substations inside them in proportion to their connection capacity, 3 regions to their nearest; dropped 10 region(s) over 150 km from the grid (ES532, ES533, ES640, ES703, ES704, ES705, ES706, ES707, ES708, ES709)
- OPSD 2020-10-06 entsoe transparency, peak 33256 MW / mean 26466 MW
- OPSD 2020-10-06 entsoe transparency, peak 33381 MW / mean 27367 MW
- OPSD 2020-10-06 entsoe transparency, peak 33641 MW / mean 27174 MW
- OPSD 2020-10-06 entsoe transparency, peak 34644 MW / mean 27940 MW
- OPSD 2020-10-06 entsoe transparency, peak 39044 MW / mean 32382 MW
- OPSD measured generation as the hourly upper bound for ES/solar, ES/onwind
- carriers not modelled: Steam Turbine (3 units, 171 MW), battery (3 units, 74 MW), heat storage (12 units, 1050 MW), waste (5 units, 206 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 1429 MW mean, other 57 MW mean, other renewable 97 MW mean, waste 288 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 1621 MW mean, other 15 MW mean, other renewable 105 MW mean, waste 263 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 2225 MW mean, other 58 MW mean, other renewable 104 MW mean, waste 280 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 2476 MW mean, other 59 MW mean, other renewable 100 MW mean, waste 285 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 942 MW mean, other 60 MW mean, other renewable 87 MW mean, waste 244 MW mean
- dropped 616 units below 10 MW (2698 MW, 2.4% of fleet capacity)
- excluded 95 reservoir units (9816 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 2 borders, net 1027 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 2 borders, net 1690 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 2 borders, net 829 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 2 borders, net 906 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 2 borders, net 927 MW mean; imports are curtailable, exports are fixed load
- kept the largest connected AC component: 1066 of 1075 buses (9 dropped as isolated)
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 1066 AC buses, 1256 lines, 102 transformers, [220, 225, 400] kV
- skipped 12 PHS units with no reservoir capacity in the data (Bolarque, Tanes, Soutelo, Montamara)

</details>
