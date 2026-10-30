# Verify: retirement Family B, plan 4 (work/data-engineer/derivation-gate 20b433e; dryrun_B4), 2026-10-26

Verifier 2. Cohort (top-1000 shards.csv, not excluded): 783 cells (654 replaced, 60 proxy_only_source, 51 proxy_filed_copies_disagree, 18 proxy_nci_inclusive_only), reproduced from B_proxy_form_cells.csv. Income statements fetched for 29 accessions (2 had no statement page my reader matched), plus core.fact reads. FILING-CHECKED where an accession's face is cited, else DATA-INFERRED.

## Result: GATE FAILS on two counts.
1. **Right values blanked:** all 10 MA cells (FY2021-FY2025, net_income and net_income_resolved) are removed as proxy_nci_inclusive_only. MA's "Net Income" line is the attributable figure.
2. **Wrong value shown:** EQH Q4 2021 is replaced with 2,448M, a quarter derived across two filing vintages.

The B2 NCI fix itself works: FCX, THC, CAT, TXRH and PCG now show the attributable figures.

## 1. Named cells
| Cell | Plan | Face | Verdict |
|---|---|---|---|
| FCX FY2021 | 4,306M (0000831259-24-000011) | "Net income attributable to common stockholders" 4,306 (2021 column) | right |
| THC FY2023 | 611M (0000070318-26-000012) | "Net income available to Tenet ... common" 611 (Net income incl. NCI 1,311) | right; FY2024 3,200, FY2025 1,407 right |
| SM FY2024 / FY2023 / FY2022 | 770,293K / 817,880K / 1,111,952K (0000893538-25-000008) | same | right (precise copy) |
| WDAY FY2022 / FY2023 | 29,373K / -366,749K (0001327811-23-000024) | same | right |
| NOW FY2021 | 230,141K | statement page not matched by my reader; DATA-INFERRED | right (B2 finding) |
| CAT FY2023 / FY2024 / FY2025 | 10,335M / 10,792M / 8,884M (0000018230-26-000008) | "Profit (loss)" attributable 10,335 / 10,792 / 8,884 | right |
| TXRH FY2023 / FY2024 / FY2025 | 304,876K / 433,592K / 405,554K | "Net income attributable to Texas Roadhouse" same | right |
| PCG FY2021-FY2025 | -102M, 1,800M, 2,242M, 2,475M, 2,593M | "Income Available for Common Shareholders" same (0001004980-24-000014, -26-000009) | right. PCG Q4 2021 472M = -102 - (-574) on the same concept (DATA-INFERRED) |
| MA FY2024 | removed, proxy_nci_inclusive_only | R4 of 0001141391-25-000011: one bottom line, "Net Income" 12,874 (tagged ProfitLoss), no NCI line on the face. Basic EPS 13.91 x 925M shares = 12,867, so EPS is computed on 12,874 | **WRONG: right value blanked** |
| CLX FY2026 | removed, proxy_only_source (proxy 601M) | R4 of 0000021076-26-000034: Net earnings 601, NCI 14, "Net earnings attributable to Clorox" 587 | removal right, because 601 includes NCI. **Ingestion gap: core.fact has 0 facts from that 10-K**, so the attributable 587M cannot be shown. Q4 FY2026 should be 587 - 424 = 163M (the proxy 177M = 601 - 424 includes NCI) |

MA in detail: core.fact holds ProfitLoss 12,874M and NetIncomeLossAttributableToNoncontrollingInterest 16M from the 10-K; the 16M is not on the income statement face. The rule "block NCI-inclusive tags when a nonzero NCI fact exists" fires on that off-face fact. FY2022 and FY2023 are on the same face (9,930 / 11,195). FY2021 and FY2025 follow the same pattern (DATA-INFERRED). Fix: block only when the same filing's income statement prints an NCI line, or an attributable line, for the column.

## 2. The 18 NCI-blocked cohort removals
- **MA (10 cells): right values blanked** (above).
- 8 Q4 cells (LNG Q4 2021/2022/2023, CAG Q4 FY2023/FY2024, GIS Q4 FY2023/FY2024, Q Q4 2025): removal right. Each stored value is a quarter built from a proxy full-year figure that is NCI-inclusive, labelled NetIncomeLoss in the proxy:
  - LNG proxy FY2021 -1,565 = face "Net income (loss)" incl. NCI; attributable -2,343 (0000003570-24-000040).
  - CAG proxy FY2023 683.2 = face incl. NCI; attributable 683.6 (0001558370-24-009764).
  - GIS proxy FY2023 2,610 vs incl. NCI 2,609.6; attributable 2,593.9 (0001193125-24-168943).
  - Q proxy FY2025 729 = face incl. NCI; attributable 692 (0002058873-26-000010).
- The right attributable quarter is derivable but not produced:
  - LNG: -2,343 - (-1,020) = -1,323; 1,428 - (-2,509) = 3,937; 9,881 - 8,504 = 1,377. These are not produced because LNG's 10-K NetIncomeLoss facts are all non-authoritative in core.fact. LNG Q4 2024 and Q4 2025 do get 977 / 2,296.
  - CAG and Q: the same derivation applies.
  - GIS: the 10-K's own Q4 sits under a different period start (2023-02-28: 614.9M), which suggests a duplicate quarter period.
- Is attributable income absent from the filing face? For these 8, no: it is on the face, and the removal is right only because the stored quarter is wrong.

## 3. 15 random cohort replacements (seed random.Random(20261109))
**Right 13** (face or same-vintage derivation):
- AVAV FY2025 43,619K; HL FY2025 321,712K (DATA-INFERRED, page not matched); COIN FY2025 1,260,327K; PRAX FY2023 -123,277K; MKTX FY2021 257,888K; ALGN FY2021 772,020K; S FY2026 -450,735K; STT FY2021 2,693M (NetIncomeLoss, priority 1); ETSY FY2023 307,568K.
- Derived quarters on one vintage: DUOL Q4 2024 88,574 - 74,667 = 13,907K; DT Q4 FY2026 162,669 - 145,253 = 17,416K; CACC Q4 2023 286.1 - 192.5 = 93.6M; MKTX Q4 2021 52,185K (DATA-INFERRED).

**Wrong 1:** EQH Q4 2021 2,448M is derived from the FY2021 value in the 2023 10-K, which is LDTI-restated: 1,755M (0001333986-24-000009 R4). From that figure the plan subtracts the ORIGINAL nine months, -693M, taken from the 2021 10-Q. The original 10-K (0001333986-22-000006 R4) shows FY2021 "Net income (loss) attributable to Holdings" -439M. The same-vintage Q4 is -439 - (-693) = 254M. The proxy's stored 693,001,755 is also garbage. The pre-existing Q4 derivation must not mix vintages: FY and nine months from the same filing vintage, or no value.

**Imprecise 1:** ST Q4 2023 -202,229K uses FY -3,900K from the 2025 10-K, which prints in rounded hundreds. The original FY -3,909K gives -202,238K. Same rule as B2: use the precise copy for derivation inputs too.

## Required before apply
1. Change the NCI-inclusive block test: block only when an NCI or attributable line is on the same filing's income statement face. Today MA's off-face NCI fact blanks 10 right values.
2. Derived Q4 inputs must come from one vintage (EQH). Prefer the precise copy (ST).
3. Route the CLX FY2026 10-K ingestion gap (0000021076-26-000034, 0 facts).
4. Re-promote the LNG 10-K NetIncomeLoss facts so that the attributable Q4 2021-2023 can be derived. Same for CAG and Q.
