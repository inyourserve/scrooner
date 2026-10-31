# Verify: capex release 1 (rebuilt) and D&A v13 (origin/work/cash-flow/da-capex 74e14f7); revenue sibling holds (slot-records 85a71f9), 2026-11-01

Seed 20261101. Files: release_capex_1/capex_release1_changed_vs_924c056.jsonl (88), cf_da_capex_v13/cells.jsonl.gz, release_is_revenue_1/sibling_holds.jsonl (542). Evidence class: FILING-CHECKED (cash-flow / income-statement R pages; filing_kit at origin/main). Verifier 2 (scrooner-bc).

## Result
- **Capex release 1: YES.**
  - Changed: 10 of 10 right (8 added/changed, 2 removed).
  - Flipped sign: 5 of 5 right (R pages print the payment unsigned; value = the payment).
  - Inflows dropped: ON 1,575.6M and BWA 239M right.
  - NVDA combined line: acceptable.
- **D&A v13: NO.** IS anchors 7 of 10 right, 3 wrong; differences 4 of 4 readable right (MGY column not readable).
- **Revenue sibling holds: 2 of 3 fine; 1 keeps a wrong production value (Snap-on Q2 2018).**
- **Combined capex line, answer to the brief:** a PP&E line that names intangibles ("Purchases related to property and equipment and intangible assets", NVDA 4,434M; AMCR, GWW, STE alike) is acceptable as printed. It is the filer's only capex line and the face gives no split; keep the combined flag.

## Cell table: capex
| Stratum | Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|---|
| changed | ON | FY2023 | PP&E (1,575.6); deposits utilized +36.5 dropped | 1,575.6M | 1,539.1M | right |
| changed | ON | 9M 2024 | (549.1); deposits utilized +12.4 dropped | 549.1M | 536.7M | right |
| changed | AMCR | FY2020 | "PP&E and other intangible assets" (399.5) | 399.5M | 400M | right (combined) |
| changed | GWW | FY2017 | "property, buildings and equipment and intangibles" (237,283) | same | 237M | right (combined) |
| changed | AMCR | Q1 FY2020 | 115.4 unsigned on R page | 115.4M | 115M | right |
| changed | STE | 9M FY2025 | "PP&E and intangibles, net" (299,206) | same | 299.2M | right |
| changed | STE | Q1 FY2025 | (108,083) | same | 108.1M | right |
| changed | ACI | FY2019 | "Payments for property, equipment and intangibles, including lease buyouts" (1,475.1M); face also prints "Total payments for capital investments, excluding lease buyouts" (1,467.4M) | 1,475.1M | 1,467.4M | right as printed; note the filer's own ex-buyout figure |
| removed | BPOP | 6M 2016 | Acquisition of premises and equipment (60,744) | 60,744K = prod | 60,744K | removal right |
| removed | BPOP | 6M 2017 | (29,992) | = prod | same | removal right |
| flipped | LH | FY2017 | Capital expenditures (312.9) | 312.9M | same | right |
| flipped | TXT | 9M 2020 | Capital expenditures 151 (unsigned) | 151M | same | right |
| flipped | VAL | 6M 2020 | Additions to P&E 67,100,000 (unsigned) | 67.1M | same | right |
| flipped | MOS | 9M 2023 | Capital expenditures 1,043.5 (unsigned) | 1,043.5M | same | right |
| flipped | OC | FY2020 | Cash paid for PP&E 307 (unsigned) | 307M | same | right |
| combined | NVDA | 6M FY2027 | "Purchases related to property and equipment and intangible assets" (4,434) | 4,434M | same | right as printed |

## Cell table: D&A
| Stratum | Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|---|
| anchor | TLN | FY2024 | IS "Depreciation, amortization and accretion" 298; nuclear fuel 123 separate | 298M | 298M | **wrong: the anchor line includes accretion (the v12 rule holds any "and accretion" label)** |
| anchor | LNT | 6M 2016 | IS D&A 204.6 | same | same | right |
| anchor | EIX | Q1 2018 | IS D&A 462 (Edison block) | 462M | blank | right |
| anchor | LNG | 6M 2025 | IS "Depreciation, amortization and accretion expense" 641 | 641M | 641M | **wrong: accretion in the anchor line** |
| anchor | DUK | 6M 2015 | IS D&A 1,567 (Duke block); CF combined incl. nuclear fuel 1,784 | 1,567M | 1,784M | right |
| anchor | DDS | 6M 2015 | IS 121,653 | same | 122,697K | right |
| anchor | AHR | 6M 2022 | IS 82,282 | same | 82,293K | right |
| anchor | HR | Q1 2015 | IS 36,595 | same | same | right |
| anchor | PNW | 6M 2017 | IS 253,366 (CF incl. nuclear fuel 291,285) | 253,366K | 291,285K | right |
| anchor | OLLI | 9M FY2016 | CF "D&A of property and equipment" 7,486 + intangibles 284 = 7,770; IS "D&A expenses" 6,188 (excludes D&A in cost of sales) | 6,188K | 7,486K | **wrong: the CF D&A line was not read (cell lines omit it), so a partial IS line was used** |
| diff | AVT | FY2019 | 97,160 + 83,682 | 180,842K | 180.8M | right |
| diff | GWW | 9M 2025 | CF 190 | same | 247M | right |
| diff | PBF | 6M 2024 | CF 310.5 | same | 6.5M | right |
| diff | MGY | Q3 2018 | column not readable (2-month/7-month stub columns) | 67,478K | 65,902K | not graded |
| diff | MLI | Q1 2020 | CF 11,119 | same | 11,039K | right |

## Cell table: revenue sibling holds (production stays)
| CIK | Period | Face | Production | Verdict |
|---|---|---|---|---|
| 914475 | Q1 2016 | Total revenues 15,000 (sibling: license fees and milestones) | 15M | fine (production = printed total) |
| PNW 764622 | Q3 2017 | OPERATING REVENUES 1,183,322 (Pinnacle West block) | 1,183,322K | fine |
| SNA 91440 | Q2 2018 | Net sales 954.6 + Financial services revenue 82.0 = 1,036.6; no total line | 949.2M | **production wrong; the hold keeps it. Apply the calc-sum gate (as for Q1 2016) or hide** |

## Findings for the builder
1. **D&A anchor:** apply the accretion rule to the IS anchor line too (TLN, LNG). An IS line containing "accretion" is not D&A.
2. **D&A OLLI:** the CF line "Depreciation and amortization of property and equipment" was not captured as a member for 9M FY2016 (it is captured in other OLLI periods). Find why that period's row was missed. An IS anchor must not replace a complete CF composition.
3. **Revenue sibling holds:** when production's value matches neither the printed total nor any printed line (SNA Q2 2018 949.2M vs 954.6 / 1,036.6), holding keeps a wrong value. Route these to the calc-sum gate or hide them.
4. **Capex note:** ACI prints both an including-lease-buyouts line and the filer's own capital-investments total excluding buyouts; consider the founder's perimeter call.

## Requests and disk
SEC requests: 83. No DB access.

## Untested scope
CZR/BPOP/NVDA reimbursement-drop cells beyond BPOP's two removals; 1,029 anchor cells and 539 sibling holds not drawn.
