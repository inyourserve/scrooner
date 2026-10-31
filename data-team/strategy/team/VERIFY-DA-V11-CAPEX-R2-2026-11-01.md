# Verify: D&A v11 and capex release 2 fills (origin/work/cash-flow/da-capex ce06af5, results/cf_da_capex_v11), 2026-11-01

Seed 20261101. File: cf_da_capex_v11/cells.jsonl.gz. Claimed: D&A 33,360 publishable, 1,749 differ; capex release 2 = 2,190 fills of blank production cells. Evidence class: FILING-CHECKED (cash-flow and income-statement R pages of each cell's accession; filing_kit from origin/main). Verifier 2 (scrooner-bc).

## Result
- **V10 fixes confirmed:** GD Q1 2024 = 211M (152 + 59). Both KEY "D&A expense, net" cells are held (6M 2021: 21 < IS intangible amortization 29; FY2021: 32 < 58).
- **D&A: NO.** 16 of 19 readable differences right, 3 wrong (J 6M FY2018 rows not readable by label).
- **Capex release 2 fills: NO.** 10 of 14 readable right, 4 wrong (CHDN lines not readable by label).

## Sample
Required: GD Q1 2024, KEY 6M 2021 and FY2021 holds. `random.Random(20261101)`: 20 of the published D&A cells that differ from production, then 15 of the 2,190 capex fills (published, no perimeter case, production blank).

## Cell table: D&A differences
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| VRSK | Q1 2021 | 48.5 + 45.0 | 93.5M | 48.5M | right |
| J | 6M FY2018 | rows under "Depreciation and amortization:" not matched | 95,187K | 59,139K | not graded |
| MLI | Q1 2015 | CF 8,015 (IS 7,853) | 8,015K | 7,853K | right |
| HSIC | FY2021 | CF 209,528,000 | same | 180M | right |
| HAS | FY2022 | 127.3 + 105.3 | 232.6M | 232.5M | right |
| MSCI | FY2019 | IS: intangibles 49,410 + PP&E 29,999 (CF page unparsed) | 79,409K | 29,999K | right |
| DDS | 6M FY2018 | CF 113,174 | same | 112,224K | right |
| EQT | FY2018 | 1,729,739 + 77,374 | 1,807,113K | 1,569,038K | right |
| EVR | 9M 2017 | CF "Depreciation, Amortization and Accretion" 18,453; IS D&A 18,267 | 18,453K | 18,267K | **wrong: accretion line (the run holds this label class elsewhere)** |
| SYK | 6M 2024 | 210 + 308 | 518M | 709M | right |
| TTC | 9M FY2026 | 70.9 + 27.5 | 98.4M | 101.3M | right |
| VNO | Q1 2019 | D&A 123,135; "Amortization of below-market leases, net" -6,525; IS D&A 116,709 | 116,610K | 123,135K | **wrong: below-market lease (revenue) amortization added** |
| MLI | 6M 2021 | CF 22,975 | same | 22,889K | right |
| KEY | FY2023 | "Depreciation and amortization expense, net" 134 | 134M | 232M | **wrong: the same net line the run holds for KEY 2021** |
| SPG | FY2025 | CF 1,554,346 | same | 1,426,423K | right |
| SGI | 9M 2022 | D&A 93.3 (SBC amortization 39.1 excluded) | 93.3M | 132.5M | right |
| OLLI | FY2020 | CF 22,465 | same | 22.5M | right |
| OLLI | FY2024 | CF 43,958 | same | 44.0M | right |
| OLLI | Q1 FY2023 | CF 8,025 | same | 6,483K | right |
| TPR | 6M FY2019 | 126.3 | same | 127.5M | right |

## Cell table: capex release 2 fills
| Ticker | Period | Face | Slot | Verdict |
|---|---|---|---|---|
| RLI | Q1 2017 | Net property and equipment purchased (3,298) | 3,298K | right |
| RRC | 9M 2020 | Additions to natural gas properties (321,849); Additions to field service assets (2,493) | 321,849K | **wrong: field service assets omitted (324,342)** |
| ASB | Q1 2016 | Premises, equipment and software, net (70,685) | 70,685K | right |
| AXS | 6M 2023 | "Proceeds from the (purchase) sale of other assets, net" +7,584 | 7,584K | **wrong: a net inflow shown as capex** |
| CHDN | Q1 2023 | capital maintenance 11.8 + project 122.9 (rows not matched by label) | 134.7M | not graded |
| APA | FY2021 | oil and gas property (1,101); Altus GPT facilities (3); leasehold (9) | 1,110M | **wrong: GPT facilities omitted (1,113)** |
| AR | FY2016 | proved 134,113; unproved 611,631; D&C 1,327,759; water handling 188,188; gathering 231,044; other 2,694 | 2,307,241K | **wrong: water handling omitted (2,495,429)** |
| SNA | FY2025 | Capital expenditures (76.0) | 76.0M | right |
| APA | Q1 2026 | 542 + 4 | 546M | right |
| ASB | 9M 2021 | (34,337) | 34,337K | right |
| NEE | FY2024 | FPL (7,992) + other (123) | 8,115M | right |
| SO | Q1 2020 | Property additions (1,560), Southern block | 1,560M | right |
| MDLZ | 6M 2026 | (654) | 654M | right |
| EXE | 9M 2017 | D&C (1,597) + acquisitions of properties (226) + other P&E (12) | 1,835M | right |
| NEE | 6M 2021 | FPL segment (2,946) + Gulf Power (323) | 3,269M | right |

## Withheld cells / false holds
KEY 2021 holds are correct. None else in scope.

## Findings for the builder
1. **D&A label classes:** "Depreciation, Amortization and Accretion" (EVR) must take the same combined-with-other hold as "Depreciation, amortization and accretion" (case and word order vary).
2. **D&A lease intangibles:** "Amortization of below-market leases, net" (VNO) is revenue; exclude it like TRNO's lease intangibles.
3. **KEY net line:** once a company's "D&A expense, net" is shown to be below its own intangible amortization, hold that label for the company in every period (KEY FY2023), not only where the IS prints the component.
4. **Capex E&P lines:** every printed "Additions to ..." property/facility/system line in the investing section is capex (field service assets, GPT facilities, water handling and treatment systems). Exclude only acquisitions of businesses, securities and finance receivables.
5. **Capex net lines:** a line labelled "(purchase) sale ... net" with a positive (inflow) value is not capex. Hold it.

## Requests and disk
SEC requests: 99. No DB access.

## Untested scope
20 of ~1,749 D&A differences and 15 of 2,190 fills. Capex release 1 (2,115 cells) was covered by the V10 sample (15/15) and not re-sampled.
