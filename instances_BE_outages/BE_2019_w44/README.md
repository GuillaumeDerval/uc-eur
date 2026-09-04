# instances_BE_outages / BE_2019_w44

51 instances. Columns come from each instance's `.summary.json`; *Solved* is from the last `solve_all.jl` run, and *Dispatch* links a plot of demand net of non-committable generation against the capacity committed at the optimum.

| Instance | Units removed | MW removed | Buses | Branches | Thermal units | Thermal MW | Profiled | Storage | Peak MW | Demand MWh | Net imports MWh | Solved | Dispatch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `v00_baseline.json.gz` | _none (baseline)_ | 0 | 71 | 90 | 35 | 10,310 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v00_baseline.png) |
| `v01_Awirs_Scheldelaan-Exxonm.json.gz` | Awirs, Scheldelaan Exxonmobil | 220 | 71 | 90 | 33 | 10,090 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v01_Awirs_Scheldelaan-Exxonm.png) |
| `v02_Zedelgem-Tj_Zeebrugge-Tj.json.gz` | Zedelgem Tj, Zeebrugge Tj | 37 | 71 | 90 | 33 | 10,273 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v02_Zedelgem-Tj_Zeebrugge-Tj.png) |
| `v03_Marcinelle-Energie_Zandvliet.json.gz` | Marcinelle Energie Carsid, Zandvliet | 799 | 71 | 90 | 33 | 9,511 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v03_Marcinelle-Energie_Zandvliet.png) |
| `v04_Drogenbos_Zeebrugge-Tj.json.gz` | Drogenbos, Zeebrugge Tj | 479 | 71 | 90 | 33 | 9,832 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v04_Drogenbos_Zeebrugge-Tj.png) |
| `v05_Lillo-Degussa.json.gz` | Lillo Degussa | 85 | 71 | 90 | 34 | 10,225 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v05_Lillo-Degussa.png) |
| `v06_Burgo-Ardennes.json.gz` | Burgo Ardennes | 42 | 71 | 90 | 34 | 10,268 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v06_Burgo-Ardennes.png) |
| `v07_Doel-1_Zwijndrecht-Lanxes.json.gz` | Doel 1, Zwijndrecht Lanxess | 512 | 71 | 90 | 33 | 9,798 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v07_Doel-1_Zwijndrecht-Lanxes.png) |
| `v08_Beringen_Burgo-Ardennes.json.gz` | Beringen, Burgo Ardennes | 464 | 71 | 90 | 33 | 9,846 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v08_Beringen_Burgo-Ardennes.png) |
| `v09_Burgo-Ardennes_Zandvliet.json.gz` | Burgo Ardennes, Zandvliet | 428 | 71 | 90 | 33 | 9,882 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v09_Burgo-Ardennes_Zandvliet.png) |
| `v10_Monsanto-Oud-Lillo_Tihange-1.json.gz` | Monsanto Oud Lillo, Tihange 1 | 1,052 | 71 | 90 | 33 | 9,258 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v10_Monsanto-Oud-Lillo_Tihange-1.png) |
| `v11_Zandvliet.json.gz` | Zandvliet | 386 | 71 | 90 | 34 | 9,924 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v11_Zandvliet.png) |
| `v12_Inesco_Zelzate-Tj.json.gz` | Inesco, Zelzate Tj | 157 | 71 | 90 | 33 | 10,154 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v12_Inesco_Zelzate-Tj.png) |
| `v13_Aalst-Syral.json.gz` | Aalst Syral | 48 | 71 | 90 | 34 | 10,262 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v13_Aalst-Syral.png) |
| `v14_Sappi-Lanaken.json.gz` | Sappi Lanaken | 43 | 71 | 90 | 34 | 10,267 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v14_Sappi-Lanaken.png) |
| `v15_Zedelgem-Tj.json.gz` | Zedelgem Tj | 19 | 71 | 90 | 34 | 10,292 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v15_Zedelgem-Tj.png) |
| `v16_Herdersbrug_Monsanto-Oud-Lillo.json.gz` | Herdersbrug, Monsanto Oud Lillo | 508 | 71 | 90 | 33 | 9,802 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v16_Herdersbrug_Monsanto-Oud-Lillo.png) |
| `v17_Doel-4.json.gz` | Doel 4 | 1,090 | 71 | 90 | 34 | 9,220 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v17_Doel-4.png) |
| `v18_Herdersbrug.json.gz` | Herdersbrug | 465 | 71 | 90 | 34 | 9,845 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v18_Herdersbrug.png) |
| `v19_Zwijndrecht-Lanxes.json.gz` | Zwijndrecht Lanxess | 58 | 71 | 90 | 34 | 10,252 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v19_Zwijndrecht-Lanxes.png) |
| `v20_Biowanze_Monsanto-Oud-Lillo.json.gz` | Biowanze, Monsanto Oud Lillo | 69 | 71 | 90 | 33 | 10,241 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v20_Biowanze_Monsanto-Oud-Lillo.png) |
| `v21_Burgo-Ardennes_Marcinelle-Energie.json.gz` | Burgo Ardennes, Marcinelle Energie Carsid | 455 | 71 | 90 | 33 | 9,855 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v21_Burgo-Ardennes_Marcinelle-Energie.png) |
| `v22_Cierreux-Tj_Noordschote-Tj.json.gz` | Cierreux Tj, Noordschote Tj | 37 | 71 | 90 | 33 | 10,273 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v22_Cierreux-Tj_Noordschote-Tj.png) |
| `v23_Biowanze_Saint-Ghislain.json.gz` | Biowanze, Saint Ghislain | 376 | 71 | 90 | 33 | 9,934 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v23_Biowanze_Saint-Ghislain.png) |
| `v24_Herdersbrug_Lillo-Degussa.json.gz` | Herdersbrug, Lillo Degussa | 550 | 71 | 90 | 33 | 9,760 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v24_Herdersbrug_Lillo-Degussa.png) |
| `v25_Awirs.json.gz` | Awirs | 80 | 71 | 90 | 34 | 10,230 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v25_Awirs.png) |
| `v26_Beringen_Zandvliet.json.gz` | Beringen, Zandvliet | 808 | 71 | 90 | 33 | 9,502 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v26_Beringen_Zandvliet.png) |
| `v27_Deux-Acren-Tj.json.gz` | Deux Acren Tj | 19 | 71 | 90 | 34 | 10,292 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v27_Deux-Acren-Tj.png) |
| `v28_Jemeppe-Sur-Sambre_Zelzate-Tj.json.gz` | Jemeppe Sur Sambre, Zelzate Tj | 125 | 71 | 90 | 33 | 10,186 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v28_Jemeppe-Sur-Sambre_Zelzate-Tj.png) |
| `v29_Drogenbos.json.gz` | Drogenbos | 460 | 71 | 90 | 34 | 9,850 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v29_Drogenbos.png) |
| `v30_Jemeppe-Sur-Sambre_Tihange-2.json.gz` | Jemeppe Sur Sambre, Tihange 2 | 1,161 | 71 | 90 | 33 | 9,149 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v30_Jemeppe-Sur-Sambre_Tihange-2.png) |
| `v31_Biowanze_Ringvaart.json.gz` | Biowanze, Ringvaart | 411 | 71 | 90 | 33 | 9,899 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v31_Biowanze_Ringvaart.png) |
| `v32_Cierreux-Tj_Zedelgem-Tj.json.gz` | Cierreux Tj, Zedelgem Tj | 37 | 71 | 90 | 33 | 10,273 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v32_Cierreux-Tj_Zedelgem-Tj.png) |
| `v33_Doel-4_Herdersbrug.json.gz` | Doel 4, Herdersbrug | 1,555 | 71 | 90 | 33 | 8,755 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | 6,255.2 MWh shed | [plot](v33_Doel-4_Herdersbrug.png) |
| `v34_Jemeppe-Sur-Sambre.json.gz` | Jemeppe Sur Sambre | 106 | 71 | 90 | 34 | 10,204 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v34_Jemeppe-Sur-Sambre.png) |
| `v35_Energie.json.gz` | Energie | 45 | 71 | 90 | 34 | 10,265 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v35_Energie.png) |
| `v36_Doel-2_Noordschote-Tj.json.gz` | Doel 2, Noordschote Tj | 473 | 71 | 90 | 33 | 9,838 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v36_Doel-2_Noordschote-Tj.png) |
| `v37_Beerse_Burgo-Ardennes.json.gz` | Beerse, Burgo Ardennes | 75 | 71 | 90 | 33 | 10,235 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v37_Beerse_Burgo-Ardennes.png) |
| `v38_Aalter-Tj.json.gz` | Aalter Tj | 19 | 71 | 90 | 34 | 10,292 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v38_Aalter-Tj.png) |
| `v39_Rodenhuize.json.gz` | Rodenhuize | 205 | 71 | 90 | 34 | 10,105 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v39_Rodenhuize.png) |
| `v40_Cierreux-Tj.json.gz` | Cierreux Tj | 19 | 71 | 90 | 34 | 10,292 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v40_Cierreux-Tj.png) |
| `v41_Beerse_Drogenbos.json.gz` | Beerse, Drogenbos | 493 | 71 | 90 | 33 | 9,817 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v41_Beerse_Drogenbos.png) |
| `v42_Burgo-Ardennes_Inesco.json.gz` | Burgo Ardennes, Inesco | 180 | 71 | 90 | 33 | 10,130 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v42_Burgo-Ardennes_Inesco.png) |
| `v43_Marcinelle-Energie.json.gz` | Marcinelle Energie Carsid | 413 | 71 | 90 | 34 | 9,897 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v43_Marcinelle-Energie.png) |
| `v44_Doel-3_Tihange-1.json.gz` | Doel 3, Tihange 1 | 2,065 | 71 | 90 | 33 | 8,245 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | 46,423.0 MWh shed | [plot](v44_Doel-3_Tihange-1.png) |
| `v45_Zeebrugge-Tj.json.gz` | Zeebrugge Tj | 19 | 71 | 90 | 34 | 10,292 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v45_Zeebrugge-Tj.png) |
| `v46_Awirs_Burgo-Ardennes.json.gz` | Awirs, Burgo Ardennes | 122 | 71 | 90 | 33 | 10,188 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v46_Awirs_Burgo-Ardennes.png) |
| `v47_Doel-4_Inesco.json.gz` | Doel 4, Inesco | 1,228 | 71 | 90 | 33 | 9,082 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v47_Doel-4_Inesco.png) |
| `v48_Doel-2_Zandvliet.json.gz` | Doel 2, Zandvliet | 840 | 71 | 90 | 33 | 9,470 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v48_Doel-2_Zandvliet.png) |
| `v49_Beerse.json.gz` | Beerse | 33 | 71 | 90 | 34 | 10,277 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v49_Beerse.png) |
| `v50_Doel-2.json.gz` | Doel 2 | 454 | 71 | 90 | 34 | 9,856 | 99 | 2 | 13,174 | 1,837,106 | -73,794 | ok | [plot](v50_Doel-2.png) |

<details><summary>Provenance and exclusions for this directory</summary>

- 12 transformers carry no impedance in osm-prebuilt; given x=0.1 p.u. so DC-OPF has a finite susceptance on every branch
- 2 PHS units with max_hours from powerplantmatching reservoir capacity, round-trip efficiency 0.75
- 3 run-of-river units (37 MW) bounded by installed capacity; no measured inflow series available
- 33 committable thermal units, 10090 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 10130 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 10154 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 10186 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 10188 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 10235 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 10241 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 10273 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 8245 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 8755 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9082 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9149 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9258 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9470 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9502 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9511 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9760 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9798 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9802 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9817 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9832 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9838 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9846 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9855 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9882 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9899 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 33 committable thermal units, 9934 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10105 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10204 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10225 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10230 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10252 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10262 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10265 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10267 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10268 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10277 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 10292 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 9220 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 9845 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 9850 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 9856 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 9897 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 34 committable thermal units, 9924 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- 35 committable thermal units, 10310 MW, carriers ['CCGT', 'nuclear', 'oil', 'solid biomass']
- BE: 44 NUTS3 regions weighted 60% GDP / 40% population (Eurostat 2019) spread over the 51 substations inside them in proportion to their connection capacity, 21 regions to their nearest
- OPSD 2020-10-06 entsoe transparency, peak 11845 MW / mean 9649 MW
- OPSD measured generation as the hourly upper bound for BE/solar, BE/onwind, BE/offwind
- carriers not modelled: Steam Turbine (10 units, 2377 MW), battery (6 units, 177 MW), waste (10 units, 294 MW)
- carriers with no fleet or cost data, bounded by Energy-Charts measured hourly generation: other 733 MW mean, waste 257 MW mean
- dropped 106 units below 10 MW (397 MW, 2.1% of fleet capacity)
- historical cross-border physical flows from Energy-Charts (ENTSO-E) across 4 borders, net -439 MW mean; imports are curtailable, exports are fixed load
- kept the largest connected AC component: 71 of 72 buses (1 dropped as isolated)
- no PyPSA-Eur UC parameters for ['oil', 'solid biomass']; these get PyPSA defaults (no min up/down time, p_min_pu=0, free ramping)
- osm-prebuilt 0.7: 71 AC buses, 78 lines, 12 transformers, [220, 225, 380, 400] kV
- removed 1 unit(s), 106 MW: Jemeppe Sur Sambre (CCGT, 106 MW)
- removed 1 unit(s), 1090 MW: Doel 4 (nuclear, 1090 MW)
- removed 1 unit(s), 19 MW: Aalter Tj (oil, 19 MW)
- removed 1 unit(s), 19 MW: Cierreux Tj (oil, 19 MW)
- removed 1 unit(s), 19 MW: Deux Acren Tj (oil, 19 MW)
- removed 1 unit(s), 19 MW: Zedelgem Tj (oil, 19 MW)
- removed 1 unit(s), 19 MW: Zeebrugge Tj (oil, 19 MW)
- removed 1 unit(s), 205 MW: Rodenhuize (solid biomass, 205 MW)
- removed 1 unit(s), 33 MW: Beerse (oil, 33 MW)
- removed 1 unit(s), 386 MW: Zandvliet (CCGT, 386 MW)
- removed 1 unit(s), 413 MW: Marcinelle Energie Carsid (CCGT, 413 MW)
- removed 1 unit(s), 42 MW: Burgo Ardennes (solid biomass, 42 MW)
- removed 1 unit(s), 43 MW: Sappi Lanaken (CCGT, 43 MW)
- removed 1 unit(s), 45 MW: Energie (solid biomass, 45 MW)
- removed 1 unit(s), 454 MW: Doel 2 (nuclear, 454 MW)
- removed 1 unit(s), 460 MW: Drogenbos (CCGT, 460 MW)
- removed 1 unit(s), 465 MW: Herdersbrug (CCGT, 465 MW)
- removed 1 unit(s), 48 MW: Aalst Syral (CCGT, 48 MW)
- removed 1 unit(s), 58 MW: Zwijndrecht Lanxess (CCGT, 58 MW)
- removed 1 unit(s), 80 MW: Awirs (solid biomass, 80 MW)
- removed 1 unit(s), 85 MW: Lillo Degussa (CCGT, 85 MW)
- removed 2 unit(s), 1052 MW: Tihange 1 (nuclear, 1009 MW), Monsanto Oud Lillo (CCGT, 43 MW)
- removed 2 unit(s), 1161 MW: Tihange 2 (nuclear, 1055 MW), Jemeppe Sur Sambre (CCGT, 106 MW)
- removed 2 unit(s), 122 MW: Awirs (solid biomass, 80 MW), Burgo Ardennes (solid biomass, 42 MW)
- removed 2 unit(s), 1228 MW: Inesco (CCGT, 138 MW), Doel 4 (nuclear, 1090 MW)
- removed 2 unit(s), 125 MW: Jemeppe Sur Sambre (CCGT, 106 MW), Zelzate Tj (oil, 19 MW)
- removed 2 unit(s), 1555 MW: Herdersbrug (CCGT, 465 MW), Doel 4 (nuclear, 1090 MW)
- removed 2 unit(s), 157 MW: Inesco (CCGT, 138 MW), Zelzate Tj (oil, 19 MW)
- removed 2 unit(s), 180 MW: Inesco (CCGT, 138 MW), Burgo Ardennes (solid biomass, 42 MW)
- removed 2 unit(s), 2065 MW: Tihange 1 (nuclear, 1009 MW), Doel 3 (nuclear, 1056 MW)
- removed 2 unit(s), 220 MW: Scheldelaan Exxonmobil (CCGT, 140 MW), Awirs (solid biomass, 80 MW)
- removed 2 unit(s), 37 MW: Noordschote Tj (oil, 19 MW), Cierreux Tj (oil, 19 MW)
- removed 2 unit(s), 37 MW: Zedelgem Tj (oil, 19 MW), Cierreux Tj (oil, 19 MW)
- removed 2 unit(s), 37 MW: Zeebrugge Tj (oil, 19 MW), Zedelgem Tj (oil, 19 MW)
- removed 2 unit(s), 376 MW: Saint Ghislain (CCGT, 350 MW), Biowanze (solid biomass, 26 MW)
- removed 2 unit(s), 411 MW: Ringvaart (CCGT, 385 MW), Biowanze (solid biomass, 26 MW)
- removed 2 unit(s), 428 MW: Zandvliet (CCGT, 386 MW), Burgo Ardennes (solid biomass, 42 MW)
- removed 2 unit(s), 455 MW: Marcinelle Energie Carsid (CCGT, 413 MW), Burgo Ardennes (solid biomass, 42 MW)
- removed 2 unit(s), 464 MW: Beringen (CCGT, 422 MW), Burgo Ardennes (solid biomass, 42 MW)
- removed 2 unit(s), 473 MW: Doel 2 (nuclear, 454 MW), Noordschote Tj (oil, 19 MW)
- removed 2 unit(s), 479 MW: Drogenbos (CCGT, 460 MW), Zeebrugge Tj (oil, 19 MW)
- removed 2 unit(s), 493 MW: Drogenbos (CCGT, 460 MW), Beerse (oil, 33 MW)
- removed 2 unit(s), 508 MW: Herdersbrug (CCGT, 465 MW), Monsanto Oud Lillo (CCGT, 43 MW)
- removed 2 unit(s), 512 MW: Zwijndrecht Lanxess (CCGT, 58 MW), Doel 1 (nuclear, 454 MW)
- removed 2 unit(s), 550 MW: Herdersbrug (CCGT, 465 MW), Lillo Degussa (CCGT, 85 MW)
- removed 2 unit(s), 69 MW: Monsanto Oud Lillo (CCGT, 43 MW), Biowanze (solid biomass, 26 MW)
- removed 2 unit(s), 75 MW: Beerse (oil, 33 MW), Burgo Ardennes (solid biomass, 42 MW)
- removed 2 unit(s), 799 MW: Marcinelle Energie Carsid (CCGT, 413 MW), Zandvliet (CCGT, 386 MW)
- removed 2 unit(s), 808 MW: Beringen (CCGT, 422 MW), Zandvliet (CCGT, 386 MW)
- removed 2 unit(s), 840 MW: Doel 2 (nuclear, 454 MW), Zandvliet (CCGT, 386 MW)

</details>
