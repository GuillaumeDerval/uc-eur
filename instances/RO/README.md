# instances / RO

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `RO_2019_w19.json.gz` | RO | 2019-05-06 | 7 | 169 | 220 | 17 | 9,186 | 134 | 0 | 8,696 | 1,193,982 | -34,803 | ok | [plot](RO_2019_w19.png) |
| `RO_2019_w29.json.gz` | RO | 2019-07-15 | 7 | 169 | 220 | 17 | 9,186 | 137 | 0 | 7,601 | 1,118,676 | 92,002 | ok | [plot](RO_2019_w29.png) |
| `RO_2019_w36.json.gz` | RO | 2019-09-02 | 7 | 169 | 220 | 17 | 9,186 | 137 | 0 | 7,805 | 1,114,634 | 109,199 | ok | [plot](RO_2019_w36.png) |
| `RO_2019_w38.json.gz` | RO | 2019-09-16 | 7 | 169 | 220 | 17 | 9,186 | 136 | 0 | 7,898 | 1,070,350 | 176,555 | ok | [plot](RO_2019_w38.png) |
| `RO_2019_w39.json.gz` | RO | 2019-09-23 | 7 | 169 | 220 | 17 | 9,186 | 136 | 0 | 7,757 | 1,096,096 | 100,250 | ok | [plot](RO_2019_w39.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 17 committable thermal units, 9186 MW, carriers ['CCGT', 'coal', 'lignite', 'nuclear', 'oil', 'solid biomass']
- 22 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 46 run-of-river units (3959 MW) bounded by installed capacity; no measured inflow series available
- OPSD 2020-10-06 entsoe transparency, peak 7579 MW / mean 6448 MW
- OPSD 2020-10-06 entsoe transparency, peak 7757 MW / mean 6407 MW
- OPSD 2020-10-06 entsoe transparency, peak 7757 MW / mean 6566 MW
- OPSD 2020-10-06 entsoe transparency, peak 7805 MW / mean 6532 MW
- OPSD 2020-10-06 entsoe transparency, peak 7898 MW / mean 6357 MW
- OPSD measured generation as the hourly upper bound for RO/solar, RO/onwind
- RO: 42 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 104 substations inside them in proportion to their connection capacity, 3 regions to their nearest
- carriers not modelled: Steam Turbine (9 units, 2439 MW), battery (7 units, 240 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 437 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 475 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 552 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 659 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 948 MW mean
- dropped 204 units below 10 MW (962 MW, 3.4% of fleet capacity)
- excluded 61 reservoir units (3547 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -207 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 1051 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 548 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 597 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 650 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 169 AC buses, 198 lines, 22 transformers, [220, 400] kV

</details>
