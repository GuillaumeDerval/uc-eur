# instances / CZ

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `CZ_2019_w17.json.gz` | CZ | 2019-04-22 | 7 | 67 | 108 | 46 | 16,460 | 192 | 1 | 11,183 | 1,477,383 | -135,055 | ok | [plot](CZ_2019_w17.png) |
| `CZ_2019_w35.json.gz` | CZ | 2019-08-26 | 7 | 67 | 108 | 46 | 16,460 | 187 | 1 | 11,062 | 1,572,005 | -282,397 | ok | [plot](CZ_2019_w35.png) |
| `CZ_2019_w39.json.gz` | CZ | 2019-09-23 | 7 | 67 | 108 | 46 | 16,460 | 187 | 1 | 12,541 | 1,742,869 | -323,071 | ok | [plot](CZ_2019_w39.png) |
| `CZ_2019_w46.json.gz` | CZ | 2019-11-11 | 7 | 67 | 108 | 46 | 16,460 | 190 | 1 | 12,458 | 1,725,647 | -270,492 | ok | [plot](CZ_2019_w46.png) |
| `CZ_2019_w52.json.gz` | CZ | 2019-12-23 | 7 | 67 | 108 | 46 | 16,460 | 192 | 1 | 9,904 | 1,319,878 | -209,440 | ok | [plot](CZ_2019_w52.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 1 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 14 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 2 run-of-river units (40 MW) bounded by installed capacity; no measured inflow series available
- 46 committable thermal units, 16460 MW, carriers ['CCGT', 'coal', 'lignite', 'nuclear', 'solid biomass']
- CZ: 14 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 49 substations inside them in proportion to their connection capacity
- OPSD 2020-10-06 entsoe transparency, peak 7632 MW / mean 6323 MW
- OPSD 2020-10-06 entsoe transparency, peak 8615 MW / mean 7029 MW
- OPSD 2020-10-06 entsoe transparency, peak 8659 MW / mean 7240 MW
- OPSD 2020-10-06 entsoe transparency, peak 8813 MW / mean 7146 MW
- OPSD 2020-10-06 entsoe transparency, peak 9773 MW / mean 8129 MW
- OPSD measured generation as the hourly upper bound for CZ/solar, CZ/onwind
- carriers not modelled: Steam Turbine (5 units, 351 MW), waste (1 units, 23 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 112 MW mean, hydro reservoir 82 MW mean, other 106 MW mean, other renewable 263 MW mean, waste 23 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 204 MW mean, hydro reservoir 47 MW mean, other 109 MW mean, other renewable 275 MW mean, waste 23 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 209 MW mean, hydro reservoir 85 MW mean, other 109 MW mean, other renewable 277 MW mean, waste 21 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 221 MW mean, hydro reservoir 58 MW mean, other 123 MW mean, other renewable 269 MW mean, waste 21 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: coal-derived gas 228 MW mean, hydro reservoir 92 MW mean, other 107 MW mean, other renewable 271 MW mean, waste 23 MW mean
- dropped 462 units below 10 MW (1812 MW, 8.4% of fleet capacity)
- excluded 3 reservoir units (612 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -1247 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -1610 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -1681 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -1923 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -804 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 67 AC buses, 94 lines, 14 transformers, [220, 380, 400] kV
- skipped 2 PHS units with no reservoir capacity in the data (Stechovice, Dlouhe Strane)

</details>
