# instances / FR

5 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run.

| Instance | Country | Start (UTC) | Days | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `FR_2019_w14.json.gz` | FR | 2019-04-01 | 7 | 1,201 | 1,998 | 103 | 79,882 | 532 | 7 | 72,055 | 10,290,614 | -609,856 | ok |
| `FR_2019_w29.json.gz` | FR | 2019-07-15 | 7 | 1,201 | 1,998 | 103 | 79,882 | 526 | 7 | 61,866 | 9,066,715 | -1,294,995 | ok |
| `FR_2019_w31.json.gz` | FR | 2019-07-29 | 7 | 1,201 | 1,998 | 103 | 79,882 | 520 | 7 | 61,675 | 8,774,769 | -1,520,581 | ok |
| `FR_2019_w34.json.gz` | FR | 2019-08-19 | 7 | 1,201 | 1,998 | 103 | 79,882 | 521 | 7 | 57,612 | 8,441,169 | -1,257,541 | ok |
| `FR_2019_w36.json.gz` | FR | 2019-09-02 | 7 | 1,201 | 1,998 | 103 | 79,882 | 530 | 7 | 58,924 | 8,877,400 | -1,289,935 | ok |

<details><summary>Provenance and exclusions for this directory</summary>

- 103 committable thermal units, 79882 MW, carriers ['CCGT', 'coal', 'lignite', 'nuclear', 'oil', 'solid biomass']
- 137 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 64 run-of-river units (7118 MW) bounded by installed capacity; no measured inflow series available
- 7 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- FR: 94 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 1002 substations inside them in proportion to their connection capacity; dropped 7 region(s) over 150 km from the grid (FRY30, FRY40, FRY50, FRM01, FRM02, FRY10, FRY20)
- OPSD 2020-10-06 entsoe transparency, peak 50440 MW / mean 42060 MW
- OPSD 2020-10-06 entsoe transparency, peak 51326 MW / mean 42938 MW
- OPSD 2020-10-06 entsoe transparency, peak 53626 MW / mean 44345 MW
- OPSD 2020-10-06 entsoe transparency, peak 55033 MW / mean 45840 MW
- OPSD 2020-10-06 entsoe transparency, peak 69214 MW / mean 55916 MW
- OPSD measured generation as the hourly upper bound for FR/solar, FR/onwind
- carriers not modelled: Steam Turbine (27 units, 2165 MW), battery (7 units, 261 MW), biogas (1 units, 31 MW), waste (6 units, 208 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 1029 MW mean, waste 184 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 1050 MW mean, waste 194 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 1087 MW mean, waste 198 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 1158 MW mean, waste 193 MW mean
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: hydro reservoir 1735 MW mean, waste 165 MW mean
- dropped 534 units below 10 MW (2176 MW, 1.7% of fleet capacity)
- excluded 88 reservoir units (8598 MW): no free hourly inflow dataset, and UnitCommitment.jl storage has no inflow field
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -3630 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -7485 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -7678 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -7708 MW mean; imports are curtailable, exports are fixed load
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 6 borders, net -9051 MW mean; imports are curtailable, exports are fixed load
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 1201 AC buses, 1861 lines, 137 transformers, [220, 225, 380, 400] kV
- skipped 3 PHS units with no reservoir capacity in the data (Rance Tidal Rance Tidal, Alrance, Chatelard Vallorcine)

</details>
