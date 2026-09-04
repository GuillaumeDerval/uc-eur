# instances / GR

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `GR_2019_w06.json.gz` | GR | 2019-02-04 | 7 | 40 | 57 | 22 | 12,621 | 56 | 2 | 8,084 | 1,058,656 | 185,282 | ok | [plot](GR_2019_w06.png) |
| `GR_2019_w26.json.gz` | GR | 2019-06-24 | 7 | 40 | 57 | 22 | 12,621 | 56 | 2 | 8,794 | 1,145,627 | 207,280 | ok | [plot](GR_2019_w26.png) |
| `GR_2019_w46.json.gz` | GR | 2019-11-11 | 7 | 40 | 57 | 22 | 12,621 | 56 | 2 | 6,703 | 875,677 | 214,163 | ok | [plot](GR_2019_w46.png) |
| `GR_2019_w47.json.gz` | GR | 2019-11-18 | 7 | 40 | 57 | 22 | 12,621 | 56 | 2 | 7,196 | 905,723 | 196,879 | ok | [plot](GR_2019_w47.png) |
| `GR_2019_w51.json.gz` | GR | 2019-12-16 | 7 | 40 | 57 | 22 | 12,621 | 56 | 2 | 7,450 | 986,872 | 274,001 | ok | [plot](GR_2019_w51.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 2 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 2 run-of-river units (29 MW) bounded by installed capacity; no measured inflow series available
- 22 committable thermal units, 12621 MW, carriers ['CCGT', 'lignite', 'oil']
- GR: even split (Eurostat has no NUTS3 population or GDP)
- OPSD 2020-10-06 entsoe transparency, peak 6491 MW / mean 5303 MW
- OPSD 2020-10-06 entsoe transparency, peak 6514 MW / mean 5202 MW
- OPSD 2020-10-06 entsoe transparency, peak 7450 MW / mean 5871 MW
- OPSD 2020-10-06 entsoe transparency, peak 7949 MW / mean 6274 MW
- OPSD 2020-10-06 entsoe transparency, peak 8760 MW / mean 6736 MW
- OPSD measured generation as the hourly upper bound for GR/solar, GR/onwind
- carriers not modelled: Steam Turbine (1 units, 582 MW), waste (1 units, 24 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 243 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 255 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 289 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 450 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 500 MW mean
- dropped 368 units below 10 MW (1472 MW, 5.2% of fleet capacity)
- excluded 13 reservoir units (2582 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net 1103 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net 1172 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net 1234 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net 1275 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 5 borders, net 1631 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 40 AC buses, 57 lines, 0 transformers, [400] kV

</details>
