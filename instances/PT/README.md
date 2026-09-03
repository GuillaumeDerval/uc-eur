# instances / PT

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `PT_2019_w14.json.gz` | PT | 2019-04-01 | 7 | 153 | 242 | 25 | 7,067 | 188 | 9 | 9,454 | 1,069,586 | -49,267 | ok |
| `PT_2019_w22.json.gz` | PT | 2019-05-27 | 7 | 153 | 242 | 25 | 7,067 | 188 | 9 | 7,862 | 981,544 | 101,906 | ok |
| `PT_2019_w35.json.gz` | PT | 2019-08-26 | 7 | 153 | 242 | 25 | 7,067 | 188 | 9 | 8,461 | 949,983 | 85,614 | ok |
| `PT_2019_w36.json.gz` | PT | 2019-09-02 | 7 | 153 | 242 | 25 | 7,067 | 188 | 9 | 8,357 | 981,004 | 202,283 | ok |
| `PT_2019_w52.json.gz` | PT | 2019-12-23 | 7 | 153 | 242 | 25 | 7,067 | 188 | 9 | 9,000 | 1,111,166 | -223,243 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 12 run-of-river units (2365 MW) bounded by installed capacity; no measured inflow series available
- 15 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 25 committable thermal units, 7067 MW, carriers ['CCGT', 'coal', 'oil', 'solid biomass']
- 9 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- OPSD 2020-10-06 entsoe transparency, peak 6471 MW / mean 5369 MW
- OPSD 2020-10-06 entsoe transparency, peak 6966 MW / mean 5681 MW
- OPSD 2020-10-06 entsoe transparency, peak 6971 MW / mean 5262 MW
- OPSD 2020-10-06 entsoe transparency, peak 7096 MW / mean 5754 MW
- OPSD 2020-10-06 entsoe transparency, peak 7270 MW / mean 5711 MW
- OPSD measured generation as the hourly upper bound for PT/solar, PT/onwind
- PT: 9 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 44 substations inside them in proportion to their connection capacity, 1 regions to their nearest; dropped 2 region(s) over 150 km from the grid (PT200, PT300)
- carriers not modelled: Steam Turbine (1 units, 24 MW), battery (2 units, 38 MW), geothermal (2 units, 24 MW), waste (2 units, 76 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 245 MW mean, other 29 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 300 MW mean, other 56 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 91 MW mean, other 34 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 94 MW mean, other 34 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 995 MW mean, other 24 MW mean
- dropped 193 units below 10 MW (798 MW, 3.7% of fleet capacity)
- excluded 16 reservoir units (1461 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net -1329 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net -293 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net 1204 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net 510 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 1 borders, net 607 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 153 AC buses, 227 lines, 15 transformers, [220, 400] kV
- skipped 1 PHS units with no reservoir capacity in the data (Foz Tua)

</details>
