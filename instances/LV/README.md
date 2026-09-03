# instances / LV

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `LV_2019_w06.json.gz` | LV | 2019-02-04 | 7 | 24 | 29 | 4 | 1,110 | 29 | 0 | 1,810 | 200,088 | 22,448 | ok |
| `LV_2019_w10.json.gz` | LV | 2019-03-04 | 7 | 24 | 29 | 4 | 1,110 | 29 | 0 | 1,783 | 197,088 | 10,016 | ok |
| `LV_2019_w29.json.gz` | LV | 2019-07-15 | 7 | 24 | 29 | 4 | 1,110 | 25 | 0 | 1,698 | 200,139 | 41,968 | ok |
| `LV_2019_w35.json.gz` | LV | 2019-08-26 | 7 | 24 | 29 | 4 | 1,110 | 29 | 0 | 1,768 | 196,478 | -17,693 | ok |
| `LV_2019_w52.json.gz` | LV | 2019-12-23 | 7 | 24 | 29 | 4 | 1,110 | 29 | 0 | 1,567 | 177,339 | 9,862 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 3 run-of-river units (1536 MW) bounded by installed capacity; no measured inflow series available
- 4 committable thermal units, 1110 MW, carriers ['CCGT', 'solid biomass']
- LV: 2 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 6 substations inside them in proportion to their connection capacity
- OPSD 2020-10-06 entsoe transparency, peak 1006 MW / mean 783 MW
- OPSD 2020-10-06 entsoe transparency, peak 1008 MW / mean 784 MW
- OPSD 2020-10-06 entsoe transparency, peak 1111 MW / mean 882 MW
- OPSD 2020-10-06 entsoe transparency, peak 1170 MW / mean 921 MW
- OPSD 2020-10-06 entsoe transparency, peak 947 MW / mean 733 MW
- OPSD measured generation as the hourly upper bound for LV/onwind
- carriers not modelled: battery (1 units, 10 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 47 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 52 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 73 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 88 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 91 MW mean
- dropped 2 units below 10 MW (7 MW, 0.2% of fleet capacity)
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net -105 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 134 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 250 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 59 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 3 borders, net 60 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 24 AC buses, 29 lines, 0 transformers, [330] kV

</details>
