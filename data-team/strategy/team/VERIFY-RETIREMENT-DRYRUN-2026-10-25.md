# Verify: retirement dry-run (work/data-engineer/derivation-gate 7932d7e; dryrun_full_keep CSVs), 2026-10-25

Verifier 2. Seed random.Random(20261103). Cohort = non-excluded rows of `doc/data-moat/team/top1000/shards.csv`. FILING-CHECKED where an accession/R page is cited, else DATA-INFERRED (core.fact rows).

## Result: Family A passes. Family B FAILS the gate: removals blank values that ARE filed in periodic filings, because the proxy fact's own conflict made the periodic copies non-authoritative and because the planner counts periodic copies only under the SAME tag.

## Family A (effective_tax_rate_reported derived by subtraction)
- Every fact to demote is `is_derived = true` (18,855 of 18,855; forms 10-K/10-Q/10-K/A/10-Q/A, 3 8-K, 1 20-F) - filed FY and 10-Q rates are untouched (DATA-INFERRED, full set).
- 20 random removals (one per company): stored derived rates are subtraction artefacts (e.g. AXON Q4 2025 -8.826, BJ -1.497, MPC -1.02, JNJ Q4 2017 0.721). Checked: CNP FY2019 10-K 0001130310-20-000016 R81 prints only 12-month rates; AKAM 0001086222-21-000249 R54 only 6-month (8.5% / 10.3%); MSCI 0001408198-23-000039 R56 only 6-month (16.8% / 13.7%; the 3-month column is empty). No quarter rate is filed for these periods: removal right.
- 7 replacements (MTD Q2 2018, Q3 2020-2025): each replacement is a non-derived 3-month `EffectiveIncomeTaxRateContinuingOperations` fact from that quarter's own 10-Q (e.g. 0.200 for 2022-07-01..09-30, 0001037646-22-000031). The rate is in the 10-Q narrative, not an R page, so this is DATA-INFERRED from the instance-derived facts; stored values (0.008, 0.015, ...) were wrong.

## Family B (proxy-form sources), cohort 783 cells
**Replacements.** 21 "gross" cells + 5 small: all replacement values are the latest 10-K NetIncomeLoss (DATA-INFERRED from core.fact; FY values filing-checked for MPWR below):
- Scale fixes right: CACC x5 (286.1 -> 286,100,000), ANET x2, RBRK x2, SUNB, EQH 2021/2022, MDLN (1,157,000,000,000 -> 1,159,000,000).
- Concept fixes right: TKO 2023 175.7M (ProfitLoss, incl. NCI) -> -35.2M attributable; TKO 2024 6.4M -> 9.4M.
- Vintage switches (not errors in the proxy; both filed): RGA 2021 617M (original FY2021 10-K) -> 1,170M and 2022 623M -> 517M (LDTI-restated, FY2023 10-K); MET 2022 2,354M -> 5,284M (restated); EQH 2023/2024 1,302/1,307 -> 1,283/1,280 (restated); CRWD FY2025 -> -15,241K (FY2026 10-K; original FY2025 10-K -19,271K); MPWR 2024 1,592,058K = FY2025 10-K 0001437749-26-006113 R4 (the original FY2024 10-K 0001437749-25-005903 R4 prints 1,786,700K). "Latest filed" policy applies; the history now mixes restated FY values with original quarters, so growth/TTM must take the same vintage (ledger row 64).
- Precision loss: SM 2023 replacement 818,000,000 (latest 10-K in millions) while the original 10-K holds 817,880,000; ANET 2,087,300,000 vs 2,087,321,000. A rounded copy must not replace a precise one (ledger TTWO row).
**Removals: false removals (value filed in a 10-K; blanking it fails the gate):**
| Cell | Stored (proxy) | Filed value | Why it is "proxy only" |
|---|---|---|---|
| MA FY2024 | 12,874M | Net income 12,874M, 10-K 0001141391-25-000011 R3 (tag ProfitLoss) | planner counts copies of the same tag only; `net_income` maps ProfitLoss at priority 2 |
| TXRH FY2023 | 304.9M | 304,876K attributable, 10-K 0001558370-24-001595 R4 (NetIncomeLossAvailable...) | same; replace, do not blank |
| CAT FY2023 | 10,335M | profit attributable 10,335M, 10-K 0000018230-24-000009 R3 (NetIncomeLossAvailable..., DATA-INFERRED for the tag) | same |
| CHE FY2021 | 268,550 (x1000 low) | 268,550K, 10-K 0001562762-22-000060 R2 (3 periodic copies, all non-authoritative) | the proxy's wrong-scale fact conflicts with the periodic copies, so dedupe de-authorised them |
| JPM FY2021 | 48.3B (rounded) | 48,334M, 10-K 0000019617-22-000272 R3 | same conflict mechanism (ledger row 86) |
| GIS FY2024 | 2,519M (= incl. NCI 2,518.6 rounded) | attributable 2,496.6M, 10-K 0001193125-24-168943 R2 | same; the stored proxy figure is also the wrong perimeter |
| Q4 cells derived from a proxy FY: CMG Q4 2023, LW Q4 FY2024, MKTX Q4 2023, NFLX Q4 2021, TJX Q4 FY2026 | e.g. CMG 282,349K | a 10-K-derived Q4 fact exists and is authoritative (CMG 282,086K; LW 129.6M; MKTX 69,627K; NFLX 607,429K; TJX 1,773M) (DATA-INFERRED) | the cell must re-resolve to the periodic-derived Q4, not go blank |
**Removals right:** HAS 2021 (proxy period 2021-01-01..12-31 is a calendar duplicate; the 10-K period ends 2021-12-26 with 428.7M, 0000046080-22-000023 R5); WULF 2021 (-95,683K = successor 2 months -1,676 + predecessor 9 months -94,007, 0001104659-22-041168 R4: not one filed figure); VNOM 2021 (this CIK has no FY2021 10-K; history sits at the predecessor CIK).

**Required before apply:** (1) after demoting proxy facts, re-run Stage 2e dedupe for the affected periods so the periodic copies regain authority; (2) re-resolve each cell over ALL mapped tags (priority list), and remove only if no periodic fact exists under any of them; (3) Q4 cells re-resolve to the periodic-derived fact; (4) the replacement must prefer the more precise copy over a rounded later one. Until then the 512 removals contain false removals (8 of the 18 removal cells I checked, plus 5 Q4 cells DATA-INFERRED).
