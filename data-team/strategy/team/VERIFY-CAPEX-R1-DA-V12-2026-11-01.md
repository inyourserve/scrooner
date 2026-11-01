# Verify: capex release 1 rebuilt and D&A v12 (origin/work/cash-flow/da-capex 924c056), 2026-11-01

Seed 20261101. Files: results/release_capex_1/capex_release1_cells.jsonl (2,143), capex_release1_changed_vs_ce06af5.jsonl (78 added, 7 changed, 50 removed), results/cf_da_capex_v12/cells.jsonl.gz. Evidence class: FILING-CHECKED (cash-flow and income-statement R pages; Intel's 10-K document for one sign). Verifier 2 (scrooner-bc).

## Result
- **Capex release 1: NO (2 wrong + 1 perimeter leak).**
  - Added/changed: 10 of 10 right (incl. INTC NAND, ZBH, AM).
  - Proceeds-beside-capex stratum: 13 of 15 right. BWA and ON add a positive inflow member.
  - "Net of disposals/proceeds" members: TSLA right as printed; UHS x4 include capitalized IT-application costs (the software perimeter).
- **D&A v12: NO.** 12 of 15 right, 2 wrong (ADC, FR), 1 definition question (LH).
- **Combined holds: 3 of 5 right holds, 2 over-held.** WPC and RSG print D&A on their own income statements.
- **Answer to the brief:** a capex line printed "net of disposals/proceeds" is acceptable as printed when it is the filer's only capex line (UHS, TSLA). Label it net; there is no gross figure on the face to prefer.

## Sample
`random.Random(20261101)`: INTC FY2021, ZBH FY2019 (value_changed) and AM Q1 2019, plus 7 more of 85 added/changed; 15 of 1,626 release cells with skipped_lines; 5 of 40 cells whose member label says "net of disposals/proceeds/sales"; 15 of 1,713 D&A differences; 5 of 5,126 combined holds.

## Cell table: capex added/changed
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| INTC | FY2021 | Additions to PP&E (18,733); Additions to held for sale NAND PP&E: 10-K prints (1,596), R page shows 1,596 unsigned | 20,329M | 18,733M | right (both outflows) |
| ZBH | FY2019 | Additions to instruments (315.9); other PP&E (207.1) | 523.0M | 198.4M | right |
| AM | Q1 2019 | gathering (7,677); water handling (8,328) | 16,005K | 7,677K | right |
| NRG | 9M 2016 | Capital expenditures (898); emission allowances excluded | 898M | 659M | right |
| NRG | 9M 2017 | (760) | 760M | 172M | right |
| ZBH | 9M 2022 | 192.2 + 124.5 | 316.7M | 124.5M | right |
| BWA | 6M 2018 | (268.7) | 268.7M | 269M | right |
| INTC | FY2022 | (24,844) + NAND (206) | 25,050M | 24,844M | right |
| BWA | Q1 2018 | (160.4) | 160.4M | 160M | right |
| ZBH | FY2016 | 345.5 + 184.7 | 530.2M | 184.7M | right |

## Cell table: proceeds-beside-capex stratum
| Ticker | Period | Face | Slot | Verdict |
|---|---|---|---|---|
| JCI | Q1 FY2018 | Capex (230); sale of PP&E 5 skipped | 230M | right |
| BWA | 6M 2026 | Capex (239); "Customer advances related to capital expenditures" +6 | 245M | **wrong: customer advances received are an inflow (239)** |
| R | Q1 2022 | Purchases of property and revenue earning equipment (584,289) | same | right |
| SYY | FY2022 | (632,802) | same | right |
| EPD | Q1 2017 | (446.0); contributions in aid of construction +15.6 not added | 446.0M | right |
| WEX | Q1 2022 | (24,163) | same | right |
| DVN | 6M 2020 | capex (732) + acquisitions of P&E (5) | 737M | right |
| MCD | FY2023 | (2,357.4) | same | right |
| LEVI | 6M 2016 | (47,231) | same | right |
| VRSK | 9M 2016 | (98,570) | same | right |
| APD | FY2015 | (1,614.8) | same | right |
| FRHC | FY2020 | (4,631) | same | right |
| CAG | 9M FY2016 | (279.7); intangibles not added | 279.7M | right |
| ON | FY2023 | Purchase of PP&E (1,575.6); "Deposits utilized (made) for purchases of PP&E" +36.5 | 1,612.1M | **wrong: deposits utilized is a positive (inflow) adjustment (1,575.6, or 1,539.1 net)** |
| NRG | Q1 2018 | (358) | 358M | right |

## Cell table: "net of" members
| Ticker | Period | Face | Slot | Verdict |
|---|---|---|---|---|
| UHS | Q1 2018 | P&E additions, net of disposals (189,041); IT applications (8,570) | 197,611K | perimeter: IT applications = capitalized software |
| UHS | 9M 2018 | (521,349) + IT (25,487) | 546,836K | perimeter (same) |
| TSLA | 9M 2018 | Purchases of P&E excl. capital leases, net of sales (1,775,746) | same | right as printed |
| UHS | 9M 2017 | (418,693) + IT (26,401) | 445,094K | perimeter (same) |
| UHS | 6M 2017 | (262,452) + IT (19,448) | 281,900K | perimeter (same) |

## Cell table: D&A v12 differences
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| MLI | Q1 2016 | CF 9,011 | same | 8,920K | right |
| CPAY | 6M 2015 | 15,096 + 80,186 | 95,282K | 96,909K | right |
| AVT | FY2019 | 97,160 + 83,682 | 180,842K | 180.8M | right |
| GWW | 9M 2025 | CF 190 | same | 247M | right |
| VRSK | Q1 2022 | 49.6 + 44.6 | 94.2M | 49.6M | right |
| RYTM | FY2021 | 1,158 | same | 816K | right |
| MLI | Q1 2020 | 11,119 | same | 11,039K | right |
| LPLA | 6M 2024 | 138,157 + 60,159 | 198,316K | 138,157K | right |
| FR | Q1 2017 | CF depreciation 23,200; "Other amortization incl. SBC" 8,112; IS "Depreciation and Other Amortization" 28,494 | 23,200K | 28,494K | **wrong: amortization dropped; the IS prints D&A** |
| HWC | FY2019 | 30,902 + intangibles 20,844 | 51,746K | 30,902K | right |
| GWW | FY2023 | 214 | same | 277M | right |
| ADC | 9M 2022 | 95,666 + "Amortization from above (below) market lease intangibles, net" 24,863; IS 95,666 | 120,529K | 95,666K | **wrong: lease intangibles (revenue) added** |
| LH | FY2023 | D&A 577.3 + "Depreciation And Amortization Of Leased Assets" 168.0 | 745.3M | 577.3M | definition question: leased assets (operating-lease ROU?) |
| OLLI | FY2020 | 22,465 | same | 22.5M | right |
| STZ | 9M FY2022 | Depreciation 248.6 | same | 252.4M | right |

## Cell table: combined holds
| Ticker | Period | Face | Verdict |
|---|---|---|---|
| ADSK | 9M FY2018 | "Depreciation, amortization and accretion" 81.5 | hold right |
| CPRT | Q1 FY2026 | "Depreciation and amortization, including debt cost" 54,199 | hold right |
| TSLA | 9M 2018 | "Depreciation, amortization and impairment" 1,404,313 | hold right |
| WPC | 6M 2019 | CF combined line 232,100; IS prints "Depreciation and amortization" 226,011 | **over-held: publish IS D&A 226,011** |
| RSG | 6M 2025 | CF "DD&A and accretion" 954; IS prints "Depreciation, depletion and amortization" 897,000 and "Accretion" 57,000 separately | **over-held: publish IS D&A 897M** |

## Findings for the builder
1. **Capex member direction:** a member printed positive whose label describes cash received ("Customer advances related to capital expenditures", "Deposits utilized (made)") is an inflow; do not add it. Caution: R pages can drop parentheses that the document prints (Intel NAND, (1,596) in the 10-K). When the R sign and the label disagree, read the document line before deciding.
2. **Capex software perimeter:** "Costs incurred for purchase and implementation of information technology applications" (UHS) is capitalized software. Route it to the software perimeter case like other software lines.
3. **D&A lease intangibles:** "Amortization from above (below) market lease intangibles, net" (ADC) still passes the v12 rule. Match "above (below) market", "above-market", "below-market" and "market lease" in any order.
4. **D&A from the IS where the CF mixes items:** FR's CF splits depreciation from "other amortization incl. SBC"; the IS prints "Depreciation and Other Amortization" 28,494. WPC and RSG are held although their IS prints D&A. Use the 2a IS tie to publish the IS D&A line when the CF line is combined or partial.
5. **LH:** a definition call on "Depreciation and amortization of leased assets".

## Requests and disk
SEC requests: 122 (incl. one 10-K document). No DB access.

## Untested scope
Removed cells (50) not checked; release 2 fills (2,178) not re-sampled in this pass.
