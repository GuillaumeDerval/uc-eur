# instances / BG

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `BG_2019_w14.json.gz` | BG | 2019-04-01 | 7 | 153 | 240 | 17 | 9,554 | 90 | 1 | 6,165 | 881,804 | -124,709 | ok | [plot](BG_2019_w14.png) |
| `BG_2019_w23.json.gz` | BG | 2019-06-03 | 7 | 153 | 240 | 17 | 9,554 | 90 | 1 | 4,853 | 719,226 | -24,960 | ok | [plot](BG_2019_w23.png) |
| `BG_2019_w31.json.gz` | BG | 2019-07-29 | 7 | 153 | 240 | 17 | 9,554 | 90 | 1 | 6,081 | 848,222 | -152,937 | ok | [plot](BG_2019_w31.png) |
| `BG_2019_w33.json.gz` | BG | 2019-08-12 | 7 | 153 | 240 | 17 | 9,554 | 90 | 1 | 5,620 | 804,701 | -132,707 | ok | [plot](BG_2019_w33.png) |
| `BG_2019_w38.json.gz` | BG | 2019-09-16 | 7 | 153 | 240 | 17 | 9,554 | 92 | 1 | 5,397 | 748,126 | -105,569 | ok | [plot](BG_2019_w38.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 1 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 13 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 17 committable thermal units, 9554 MW, carriers ['CCGT', 'coal', 'lignite', 'nuclear']
- 4 run-of-river units (241 MW) bounded by installed capacity; no measured inflow series available
- BG: 28 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 49 substations inside them in proportion to their connection capacity, 10 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 4234 MW / mean 3685 MW
- OPSD 2020-10-06 entsoe transparency, peak 4577 MW / mean 3764 MW
- OPSD 2020-10-06 entsoe transparency, peak 4682 MW / mean 3882 MW
- OPSD 2020-10-06 entsoe transparency, peak 4748 MW / mean 3993 MW
- OPSD 2020-10-06 entsoe transparency, peak 5150 MW / mean 4177 MW
- OPSD measured generation as the hourly upper bound for BG/solar, BG/onwind
- carriers not modelled: Steam Turbine (3 units, 501 MW), battery (4 units, 220 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 119 MW mean, waste 4 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 219 MW mean, waste 3 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 286 MW mean, waste 4 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 357 MW mean, waste 2 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 82 MW mean, waste 4 MW mean
- dropped 160 units below 10 MW (770 MW, 4.9% of fleet capacity)
- excluded 21 reservoir units (1773 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net -149 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net -628 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net -742 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net -790 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net -910 MW mean; imports are curtailable, exports are fixed load
- osm-prebuilt 0.7: 153 AC buses, 227 lines, 13 transformers, [220, 400] kV

</details>
