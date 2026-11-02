# Pilot gaps: `no_mapped_line_cond` (343) and `no_face_print_for_period` (134), every key classified (2026-11-02)

For Dhairya. Branch `work/gaps/pilot-2026-11-02`. Input: `gaps.csv` and `library.csv` of the latest "FSN store pilot" run, 41329681197 (artifact `fsn-pilot`, code 0624e38b on `work/engineering/fsn-pilot`).

**Method.** Each filing was opened through the FSN store's own company directories for the 10 pilot companies (XOM with its predecessor CIK 0000034088). Those directories were sharded by `fsn_store.shard` from the SEC FSN sets 2014q1–2026m09. `pre` is the filing's rendered statement rows (report = R page, line), and `num` holds its values. Script: `pipeline/scripts/slot_records/pilot_gap_classify.py` (read-only; zero database reads, zero SEC requests). Every key with its evidence (accession, report, line, element, printed label, value, or the face's label list) is in `pipeline/scripts/slot_records/results/pilot_gaps_2026-11-02/gap_keys_classified.jsonl.gz`.

A filing counts as printing a key's column only if two things hold at that date:
- the statement's own total is valued (BS assets / L&E, IS net income, CF operating cash flow);
- at least half of its face lines are valued.

Without this rule, a later 10-K's note value for an old date is wrongly read as a face column.

## 1. Result

| outcome | keys | what to do |
|---|---|---|
| **Printed, our rule misses it** | **81** | 6 rule proposals (section 2); 27 of them are already fixed by the D&A detector |
| **Truly not presented** | **381** | Leaves the template for that company (COND rule) or gets a not-presented reason (section 3), with evidence |
| **Filed after the store's last FSN set** | **15** | Not a gap: Q3 2026 reports (period ≈ 2026-09-30) are filed after the 2026m09 set. Reason `filing_newer_than_fsn_set` (design §8 risk 1) |
| **Filer error** | **0** | None found in these two classes |

## 2. Printed, our rule misses it (81 keys)

| # | company, data point | keys | what the filing prints (example) | proposed rule |
|---|---|---|---|---|
| 1 | JNJ equity | 32 | "Total shareholders' equity" tagged `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest`, with no NCI line and no `StockholdersEquity` line (to 2023-04-02; e.g. 0000200406-23-000056 R2). From 2023-07 JNJ uses `StockholdersEquity` (already mapped) | **Equity detector:** on a face with no NCI line and no parent-equity line, the incl-NCI total IS parent equity → map it to `stockholders_equity_resolved`. This is conditional, so a detector rather than a seed row |
| 1 | TRV equity | 3 | Same pattern in the 2015 Q1–Q3 10-Qs (0001104659-15-071489 R5, 24,033M) | same rule |
| 2 | JPM revenue | 11 | "Total net revenue" tagged `RevenuesNetOfInterestExpense` in every 10-K (e.g. 0001628280-26-008131 R3); only `Revenues` is mapped today, in 5 filings | std_tag `us-gaap:RevenuesNetOfInterestExpense` → `revenue_sanity_resolved` for banks (your 2026-11-01 ruling: bank revenue = "Total net revenue") |
| 3 | XOM revenue FY2015–2016 | 2 | "Sales and other operating revenue" tagged `SalesAndOtherOperatingRevenueIncludingSalesBasedTaxes` (0000034088-19-000010 R2); later years use another tag | **Standardization Lead decision:** before 2017 the line includes sales-based taxes, which XOM then deducts as "Sales-based taxes". Either map it with a precision note, or blank it with reason "revenue includes sales-based taxes" |
| 4 | PLD revenue FY2015 | 1 | "Total revenues" tagged `RealEstateRevenueNet` (0001564590-18-002228 R4) | std_tag `us-gaap:RealEstateRevenueNet` → `revenue_sanity_resolved` when it is the IS total-revenues line |
| 5 | PLD buybacks FY2018–2022 | 5 | "Repurchase and retirement of common stock" tagged `PaymentsForRepurchaseOfEquity` (0001564590-23-001902 R8: 2020 34.8M; 2018, 2019, 2021, 2022 printed 0) | std_tag `us-gaap:PaymentsForRepurchaseOfEquity` → `share_buybacks_resolved` (common-stock label) |
| 6 | D&A at AAPL / JNJ / TRV | 10 / 8 / 9 | "Depreciation and amortization" (`DepreciationDepletionAndAmortization` / `DepreciationAmortizationAndAccretionNet`) on every cash-flow statement | **Already fixed** by the capex/D&A detector (`work/capex-da-debt/fsn-detectors` f17217a9). On all 27 keys' filings it maps exactly this line (checked with its `decide()`). Run 41329681197 predates it |

**Two misfires in the same run that can serve WRONG values (not gaps, found while classifying):**
- **D&A mapped to unrelated lines** by the positional seed `cf.da_operating_member@1`: AAPL `IncreaseDecreaseInNonTradeReceivables` (3 filings), TRV `ChangeInDeferredAcquisitionCosts` (several), JNJ `VenezuelaCurrencyDevaluation` / `InProcessResearchAndDevelopmentCharge` (`library.csv`). The D&A detector replaces these seed mappings; until it is in the pilot, those D&A cells are suspect.
- **PLD buybacks mapped to "Redemption of common limited partnership units"** (`PaymentsForRepurchaseOfCommonStock`, 32 filings). These are operating-partnership unit redemptions, not company buybacks. Proposed demote: drop `PaymentsForRepurchaseOfCommonStock` from `share_buybacks_resolved` when its label names limited-partnership units.

## 3. Truly not presented (381 keys)

In every filing that prints the column, no face line of the data point exists. The evidence for each key is the face's full label list in the jsonl. Q4 keys of a not-presented line are included: a 10-K prints no 3-month column (67 keys).

| company, data point | keys (incl. Q4) | evidence (latest filing) | outcome |
|---|---|---|---|
| WMT gross profit | 59 (12) | IS: Revenues, Cost of sales, Operating, selling, general and administrative expenses, Operating income; **no gross profit line** (0000104169-26-000154 R2) | leaves WMT's template (COND) |
| TRV operating income | 57 (11) + 1 after the set | Insurer IS: revenues, "Total claims and expenses", "Income before income taxes"; **no operating income line** (0000086312-26-000145 R2) | leaves TRV's template (COND) |
| XOM cost of revenue | 57 (11) | "Costs and other deductions": crude oil and product purchases, production and manufacturing, SG&A, D&D, exploration, taxes, "Total costs and other deductions"; **no cost of revenue line** (0000034088-26-000093 R2) | leaves XOM's template (COND) |
| XOM gross profit | 57 (11) | same face, **no gross profit line** | leaves XOM's template (COND) |
| NEE cost of revenue | 56 (11) | Utility IS: fuel, purchased power and interchange; O&M; D&A; taxes; **no cost-of-revenue total** (0000753308-26-000031 R2) | leaves NEE's template (COND) |
| PLD cost of revenue | 56 (11) | REIT IS: Rental, Strategic capital, Development management, G&A, D&A; **no cost-of-revenue total** (0001193125-26-197850 R4) | leaves PLD's template (COND). Sector Analyst: whether "Rental" expenses should define REIT cost of revenue is a template definition, not a gap |
| NEE total liabilities | 22 | Capitalization-format BS: "TOTAL CAPITALIZATION AND LIABILITIES", "Total current liabilities", other-liabilities block; **no total-liabilities line** (e.g. 0000753308-20-000186 R5) | Not-presented reason. Deriving it (L&E − total equity) is a template decision |
| NEE buybacks FY | 11 | The cash-flow statement prints **no share-repurchase line** in these years (e.g. 0000753308-26-000015 R8); the line appears in only 2 filings | Not-presented reason; never 0 by assumption |
| PLD buybacks FY 2015–17, 2023–25 | 6 | Only "Redemption of common limited partnership units", valued only under the Prologis L.P. dimension, so **no common-stock buyback line** (0000950170-25-021272 R8) | Not-presented reason (see the misfire above) |

## 4. Filed after the store's FSN data (15 keys)

MSFT 5, JNJ 6 and TRV 3 instants at 2026-09-30 / 2026-09-27, plus TRV operating income Q 2026-09-30. Their 10-Qs are filed after the 2026m09 set. Reason `filing_newer_than_fsn_set` until the next set or the SEC API path (design §8 risk 1).

## 5. Asks

1. **Engineering:** merge the capex/D&A detector before the next pilot run (27 keys, plus the D&A misfires).
2. **You / the Standardization Lead:**
   - std_tag rules 2, 4 and 5;
   - the equity detector, rule 1 (35 keys);
   - the PLD buyback demote;
   - XOM's pre-2017 revenue definition (rule 3).
3. **Sector Analyst:** whether REIT cost of revenue = rental expenses (PLD, 56 keys).
4. Templates: the COND removals for WMT GP, TRV OI, XOM COR/GP, NEE COR and PLD COR (343 keys) are evidenced above.

## 6. Debt work order of 2026-11-01

Stopped as asked. Nothing was pushed: the local branch `work/debt/eligibility` holds only a merge of `main` and was never pushed. Engineering's agent owns the six items on `work/balance-sheet/equity-guard-fix`.
