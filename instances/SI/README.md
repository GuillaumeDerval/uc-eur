# instances / SI

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `SI_2019_w12.json.gz` | SI | 2019-03-18 | 7 | 17 | 22 | 3 | 2,206 | 64 | 0 | 2,952 | 396,318 | 23,122 | ok |
| `SI_2019_w13.json.gz` | SI | 2019-03-25 | 7 | 17 | 22 | 3 | 2,206 | 62 | 0 | 2,864 | 393,114 | 20,103 | ok |
| `SI_2019_w16.json.gz` | SI | 2019-04-15 | 7 | 17 | 22 | 3 | 2,206 | 64 | 0 | 2,956 | 392,884 | -3,944 | ok |
| `SI_2019_w19.json.gz` | SI | 2019-05-06 | 7 | 17 | 22 | 3 | 2,206 | 64 | 0 | 2,952 | 400,852 | -36,758 | ok |
| `SI_2019_w37.json.gz` | SI | 2019-09-09 | 7 | 17 | 22 | 3 | 2,206 | 64 | 0 | 2,827 | 374,022 | 14,537 | 1.7 MWh shed |

<details><summary>Provenance and exclusions for this directory</summary>

- 14 run-of-river units (805 MW) bounded by installed capacity; no measured inflow series available
- 3 committable thermal units, 2206 MW, carriers ['coal', 'lignite', 'nuclear']
- 6 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- OPSD 2020-10-06 entsoe transparency, peak 1779 MW / mean 1434 MW
- OPSD 2020-10-06 entsoe transparency, peak 1839 MW / mean 1440 MW
- OPSD 2020-10-06 entsoe transparency, peak 1902 MW / mean 1502 MW
- OPSD 2020-10-06 entsoe transparency, peak 1905 MW / mean 1484 MW
- OPSD 2020-10-06 entsoe transparency, peak 1962 MW / mean 1542 MW
- OPSD measured generation as the hourly upper bound for SI/solar, SI/onwind
- SI: 12 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 14 substations inside them in proportion to their connection capacity, 6 regions to their nearest
- carriers not modelled: Steam Turbine (2 units, 490 MW), battery (2 units, 48 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 10 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 6 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 7 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 8 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: waste 9 MW mean
- dropped 23 units below 10 MW (73 MW, 1.8% of fleet capacity)
- excluded 6 reservoir units (257 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net -219 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net -23 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 120 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 138 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 87 MW mean; imports are curtailable, exports are fixed load
- osm-prebuilt 0.7: 17 AC buses, 16 lines, 6 transformers, [220, 380, 400] kV
- skipped 1 PHS units with no reservoir capacity in the data (Avce)

</details>
