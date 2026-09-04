# instances / HR

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `HR_2019_w07.json.gz` | HR | 2019-02-11 | 7 | 24 | 30 | 7 | 1,728 | 43 | 1 | 3,323 | 432,061 | 86,584 | ok | [plot](HR_2019_w07.png) |
| `HR_2019_w09.json.gz` | HR | 2019-02-25 | 7 | 24 | 30 | 7 | 1,728 | 45 | 1 | 3,030 | 377,334 | 147,414 | ok | [plot](HR_2019_w09.png) |
| `HR_2019_w19.json.gz` | HR | 2019-05-06 | 7 | 24 | 30 | 7 | 1,728 | 45 | 1 | 2,845 | 371,006 | 88,965 | ok | [plot](HR_2019_w19.png) |
| `HR_2019_w40.json.gz` | HR | 2019-09-30 | 7 | 24 | 30 | 7 | 1,728 | 63 | 1 | 2,771 | 375,352 | 115,867 | ok | [plot](HR_2019_w40.png) |
| `HR_2019_w49.json.gz` | HR | 2019-12-02 | 7 | 24 | 30 | 7 | 1,728 | 63 | 1 | 3,299 | 421,289 | 40,647 | ok | [plot](HR_2019_w49.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 1 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 3 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 7 committable thermal units, 1728 MW, carriers ['CCGT', 'coal', 'oil']
- 8 run-of-river units (365 MW) bounded by installed capacity; no measured inflow series available
- HR: 21 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 18 substations inside them in proportion to their connection capacity, 11 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 2363 MW / mean 1869 MW
- OPSD 2020-10-06 entsoe transparency, peak 2417 MW / mean 1940 MW
- OPSD 2020-10-06 entsoe transparency, peak 2693 MW / mean 2055 MW
- OPSD 2020-10-06 entsoe transparency, peak 2717 MW / mean 2185 MW
- OPSD 2020-10-06 entsoe transparency, peak 2729 MW / mean 2166 MW
- carriers not modelled: Steam Turbine (1 units, 35 MW), geothermal (2 units, 36 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 10 MW mean, hydro reservoir 220 MW mean, other renewable 42 MW mean, waste 0 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 10 MW mean, hydro reservoir 531 MW mean, other renewable 45 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 5 MW mean, hydro reservoir 798 MW mean, other renewable 42 MW mean, waste 1 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: geothermal 7 MW mean, hydro reservoir 286 MW mean, other renewable 46 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 600 MW mean, other renewable 47 MW mean
- dropped 17 units below 10 MW (66 MW, 1.4% of fleet capacity)
- excluded 7 reservoir units (1400 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 242 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 515 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 530 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 690 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 877 MW mean; imports are curtailable, exports are fixed load
- kept the largest connected AC component: 24 of 26 buses (2 dropped as isolated)
- no OPSD VRE generation series for ['HR']
- no PyPSA-Eur UC parameters for ['oil']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 24 AC buses, 27 lines, 3 transformers, [220, 400] kV
- skipped 1 PHS units with no reservoir capacity in the data (Vinodol)

</details>
