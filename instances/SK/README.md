# instances / SK

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `SK_2019_w06.json.gz` | SK | 2019-02-04 | 7 | 47 | 65 | 14 | 4,335 | 105 | 0 | 6,363 | 852,386 | 59,513 | ok | [plot](SK_2019_w06.png) |
| `SK_2019_w21.json.gz` | SK | 2019-05-20 | 7 | 47 | 65 | 14 | 4,335 | 101 | 0 | 5,971 | 765,929 | -14,848 | ok | [plot](SK_2019_w21.png) |
| `SK_2019_w25.json.gz` | SK | 2019-06-17 | 7 | 47 | 65 | 14 | 4,335 | 104 | 0 | 5,385 | 690,159 | 35,552 | ok | [plot](SK_2019_w25.png) |
| `SK_2019_w39.json.gz` | SK | 2019-09-23 | 7 | 47 | 65 | 14 | 4,335 | 132 | 0 | 5,708 | 792,228 | 125,468 | ok | [plot](SK_2019_w39.png) |
| `SK_2019_w52.json.gz` | SK | 2019-12-23 | 7 | 47 | 65 | 14 | 4,335 | 137 | 0 | 5,025 | 634,704 | -57,767 | ok | [plot](SK_2019_w52.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 14 committable thermal units, 4335 MW, carriers ['CCGT', 'coal', 'lignite', 'nuclear']
- 18 run-of-river units (1306 MW) bounded by installed capacity; no measured inflow series available
- 5 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- OPSD 2020-10-06 entsoe transparency, peak 3571 MW / mean 2977 MW
- OPSD 2020-10-06 entsoe transparency, peak 3759 MW / mean 3197 MW
- OPSD 2020-10-06 entsoe transparency, peak 3794 MW / mean 3164 MW
- OPSD 2020-10-06 entsoe transparency, peak 4227 MW / mean 3686 MW
- OPSD 2020-10-06 entsoe transparency, peak 4297 MW / mean 3179 MW
- OPSD measured generation as the hourly upper bound for SK/solar
- OPSD measured generation as the hourly upper bound for SK/solar, SK/onwind
- SK: 8 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 32 substations inside them in proportion to their connection capacity
- carriers not modelled: Steam Turbine (3 units, 250 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 23 MW mean, other 98 MW mean, other renewable 60 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 33 MW mean, other 223 MW mean, other renewable 65 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 38 MW mean, other 127 MW mean, other renewable 61 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 58 MW mean, other 154 MW mean, other renewable 64 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 79 MW mean, other 113 MW mean, other renewable 63 MW mean
- dropped 135 units below 10 MW (500 MW, 6.4% of fleet capacity)
- excluded 3 reservoir units (125 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -344 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -88 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 212 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 354 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net 747 MW mean; imports are curtailable, exports are fixed load
- osm-prebuilt 0.7: 47 AC buses, 60 lines, 5 transformers, [220, 400] kV
- skipped 4 PHS units with no reservoir capacity in the data (Cierny Vah, Liptovska Mara, Ruzin, Dobsina)

</details>
