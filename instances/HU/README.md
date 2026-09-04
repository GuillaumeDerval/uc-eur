# instances / HU

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `HU_2019_w01.json.gz` | HU | 2018-12-31 | 7 | 56 | 81 | 25 | 6,161 | 107 | 0 | 7,407 | 1,108,868 | 178,581 | ok | [plot](HU_2019_w01.png) |
| `HU_2019_w32.json.gz` | HU | 2019-08-05 | 7 | 56 | 81 | 24 | 6,101 | 109 | 0 | 6,278 | 937,412 | 215,002 | ok | [plot](HU_2019_w32.png) |
| `HU_2019_w40.json.gz` | HU | 2019-09-30 | 7 | 56 | 81 | 24 | 6,101 | 139 | 0 | 7,029 | 1,055,062 | 136,324 | ok | [plot](HU_2019_w40.png) |
| `HU_2019_w41.json.gz` | HU | 2019-10-07 | 7 | 56 | 81 | 24 | 6,101 | 139 | 0 | 7,241 | 1,033,916 | 150,359 | ok | [plot](HU_2019_w41.png) |
| `HU_2019_w43.json.gz` | HU | 2019-10-21 | 7 | 56 | 81 | 24 | 6,101 | 137 | 0 | 7,070 | 1,033,764 | 128,566 | ok | [plot](HU_2019_w43.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 1 run-of-river units (14 MW) bounded by installed capacity; no measured inflow series available
- 10 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 24 committable thermal units, 6101 MW, carriers ['CCGT', 'lignite', 'nuclear', 'oil', 'solid biomass']
- 25 committable thermal units, 6161 MW, carriers ['CCGT', 'coal', 'lignite', 'nuclear', 'oil', 'solid biomass']
- HU: 20 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2018) spread over the 44 substations inside them in proportion to their connection capacity, 2 regions to their nearest
- HU: 20 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 44 substations inside them in proportion to their connection capacity, 2 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 5552 MW / mean 4781 MW
- OPSD 2020-10-06 entsoe transparency, peak 5781 MW / mean 4706 MW
- OPSD 2020-10-06 entsoe transparency, peak 5784 MW / mean 4835 MW
- OPSD 2020-10-06 entsoe transparency, peak 5933 MW / mean 4926 MW
- OPSD 2020-10-06 entsoe transparency, peak 6213 MW / mean 4961 MW
- OPSD measured generation as the hourly upper bound for HU/onwind
- OPSD measured generation as the hourly upper bound for HU/solar, HU/onwind
- carriers not modelled: Steam Turbine (4 units, 324 MW), battery (3 units, 74 MW), waste (1 units, 24 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 12 MW mean, other 76 MW mean, other renewable 11 MW mean, waste 14 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 14 MW mean, other 70 MW mean, other renewable 11 MW mean, waste 12 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 6 MW mean, other 54 MW mean, other renewable 13 MW mean, waste 19 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 6 MW mean, other 54 MW mean, other renewable 14 MW mean, waste 25 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 8 MW mean, other 57 MW mean, other renewable 14 MW mean, waste 16 MW mean
- dropped 182 units below 10 MW (612 MW, 7.6% of fleet capacity)
- dropped 291 units below 10 MW (964 MW, 11.0% of fleet capacity)
- excluded 1 reservoir units (28 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 1063 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 1280 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 765 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 811 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net 895 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 56 AC buses, 71 lines, 10 transformers, [220, 400, 750] kV

</details>
