# instances / AT

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `AT_2019_w03.json.gz` | AT | 2019-01-14 | 7 | 113 | 132 | 22 | 5,424 | 293 | 13 | 13,874 | 1,879,281 | 44,070 | ok |
| `AT_2019_w17.json.gz` | AT | 2019-04-22 | 7 | 113 | 132 | 22 | 5,424 | 297 | 13 | 10,684 | 1,443,321 | -154,884 | ok |
| `AT_2019_w25.json.gz` | AT | 2019-06-17 | 7 | 113 | 132 | 22 | 5,424 | 297 | 13 | 11,444 | 1,450,477 | -111,597 | ok |
| `AT_2019_w27.json.gz` | AT | 2019-07-01 | 7 | 113 | 132 | 22 | 5,424 | 295 | 13 | 11,671 | 1,498,465 | -10,912 | ok |
| `AT_2019_w49.json.gz` | AT | 2019-12-02 | 7 | 113 | 132 | 22 | 5,424 | 299 | 13 | 12,779 | 1,728,118 | 262,159 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 13 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 18 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 22 committable thermal units, 5424 MW, carriers ['CCGT', 'coal', 'oil', 'solid biomass']
- 45 run-of-river units (2326 MW) bounded by installed capacity; no measured inflow series available
- AT: 35 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 87 substations inside them in proportion to their connection capacity, 4 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 10200 MW / mean 8356 MW
- OPSD 2020-10-06 entsoe transparency, peak 10613 MW / mean 8378 MW
- OPSD 2020-10-06 entsoe transparency, peak 8152 MW / mean 6436 MW
- OPSD 2020-10-06 entsoe transparency, peak 8533 MW / mean 6505 MW
- OPSD 2020-10-06 entsoe transparency, peak 8807 MW / mean 6823 MW
- OPSD measured generation as the hourly upper bound for AT/solar, AT/onwind
- carriers not modelled: Steam Turbine (2 units, 548 MW), battery (3 units, 37 MW), waste (4 units, 73 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 0 MW mean, hydro reservoir 1005 MW mean, other 22 MW mean, waste 100 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 0 MW mean, hydro reservoir 382 MW mean, other 22 MW mean, waste 100 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 0 MW mean, hydro reservoir 466 MW mean, other 22 MW mean, waste 100 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 0 MW mean, hydro reservoir 543 MW mean, other 22 MW mean, waste 100 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 0 MW mean, hydro reservoir 926 MW mean, other 22 MW mean, waste 100 MW mean
- dropped 92 units below 10 MW (322 MW, 1.3% of fleet capacity)
- excluded 66 reservoir units (6180 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -65 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -664 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -922 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 1560 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 262 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 113 AC buses, 114 lines, 18 transformers, [220, 380, 400] kV
- skipped 6 PHS units with no reservoir capacity in the data (Feldsee, Koralpe, Innerfragant Oschenik, Hintermuhr)

</details>
