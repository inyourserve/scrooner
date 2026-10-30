# Verify: D&A / capex replay V5 (origin/work/scrooner-25/slot-records 58e8181), 2026-10-26

Verifier 2. **The V5 reports are not committed** (no d_and_a/capex_replay_v5_report.json at 58e8181 or in the slot-records worktree). I reproduced them read-only by running the branch's replay_family.py on the committed v2 records: capex 1,640 publishable and D&A 1,263, as claimed. Seed random.Random(20261112). Each cell checked on the cash-flow R page of its own accession (37 accessions; selection by per-Report FilingSummary parsing, because the kit's find_report_files mis-pairs pages, see VERIFY-KIT-LIVE-TEST). FILING-CHECKED unless marked.

## Result: zero wrong shown values (32 of 32 drawn cells right). One false hold class: KRUS.

## 1. 12 of the restored AVGO/RPAY capex cells
I count 43 restored, not 33: AVGO's Q1 three-month cells also became face columns. All 12 drawn are right, with value, length and column matching. Capex values are positive here while the face prints outflows in parentheses (the convention), e.g. AVGO 9M FY2021 355M (0001730168-21-000123), FY2025 623M, Q1 FY2022 101M; RPAY 6M 2026 2,305K.
- No restored face has a discontinued-operations investing line. The investing total is the single continuing total, so the capex row is continuing operations.
- Perimeter note for the standardization lead: RPAY's narrow capex is PP&E only (FY2025 286K). The face also prints "Capitalized software development costs" 41,497K and intangible purchases 200K, so a reader's capex is about 42M.

## 2. KRUS: false holds
- KRUS's D&A line is NOT custom. It is us-gaap DepreciationDepletionAndAmortization, "Depreciation and amortization" 6,596K (6M FY2025, 0000950170-25-052106).
- The hold comes from the custom krus_BondPremiumAndAccruedInterestAmortization ("Bond premium and accrued interest amortization" 155K). The 2025-2026 record classes it as `other_amort` and makes it a root.
- It is amortization of investment premium (investment_amort), which is excluded from D&A, so it should not be a member at all. The 6 YTD/FY cells marked needs_instance_reader are right values withheld.

## 3. 20 publishable cells from companies not yet drawn
Only PM and SPCX remained undrawn; the draw landed on PM. All 20 are right: capex FY2015 960, FY2017 1,548, FY2018 1,436, FY2022 1,077, FY2025 1,569, plus YTD and Q1 cells; D&A FY2019 964, FY2024 1,787, Q1 2017 197, Q1 2019 240, Q1 2020 241, 6M cells.

Requests: about 75. The replay ran read-only on one connection; the script sets its own 60s timeout. The reproduction worktree was removed afterwards. Untested: SPCX, and the rest of the restored and publishable cells.
