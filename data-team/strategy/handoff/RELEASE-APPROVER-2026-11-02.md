# Release approver handoff (Ritwik, session scrooner-3d), 2026-11-02

Role: Verifier 2 and release approver. Never builds. Report to Dhairya (scrooner-df); engineering is scrooner-87. Previous handoff: `RELEASE-APPROVER-2026-11-01.md`. A production write needs the founder's own typed words in the session that applies it. My session's permission classifier denied the 0118/0119 apply (Modify Shared Resources), so the applies below ran in scrooner-87.

## Applied, and checked by me read-only
- **0118 fsn store and 0119 company_value_owner** (scrooner-87, 2026-11-01 13:01 UTC; record feaff03).
  - fsn has 11 tables and 0 rows; fsn.dim has only id 0.
  - `source_value_ids` is bigint[] not null default '{}'.
  - Both canonical_fact guards are enabled; the guard body md5 equals the file's.
  - I landed the branch on main first (c4c2931).
- **0120 company_data_point_template** (scrooner-87, 14:37 UTC): the table exists with 0 rows. It is not seeded: there is no seeder-format file yet (see below).

## Verdicts given
- **0121 company_history_source: the 6 wrong-entity exclude windows are APPROVED.** FILING-CHECKED by an independent Verifier (58 sec.gov requests). In every case the successor's first post-merger 10-K names the accounting acquirer, and its prior-year comparatives equal that acquirer's own 10-K.
  - JCI: 0000833444-16-000216 R10; FY15 net sales 37,179 = 0000053669-15-000034.
  - WCN: 0001144204-17-011069 R10; FY15 revenue 2,117,287 = 0001144204-16-079708.
  - AHR: 0001632970-22-000020 R9; 2020 total assets 3,234,937 = 0001566912-21-000017.
    - Q3 2021 income-statement values come back via AHR's Q3 2022 10-Q reprint (revenue 317,486).
    - Only the 2021-09-30 balance sheet is unfiled; it is a blank with reason.
  - LIN: 0001628280-19-003050 R9; 2017 sales 11,437 = 0000884905-18-000014.
  - VTRS: 0001792044-21-000009 R10; 2019 revenue 11,500.5 = 0001623613-20-000011.
  - PSKY: 0002041610-26-000011 R9; Paramount Global is the predecessor; 2024 total assets 46,172 = 0000813828-25-000005.
    - The predecessor/successor split is at 2025-08-06. FY2025 and Q3 2025 are blank with reason; they are never summed.
  - Exclusion filters whole filings by the filing's own period (`fsn_store/shard.py:156`), so later reprints are kept.
  - **NOT applied as of 2026-11-02 17:10 UTC**: it waits for the founder's words.
- **Sector templates: approved with corrections** (`SECTOR-TEMPLATES-2026-11-01.md` §8).
  - The BDC ruling (founder, relayed) is recorded in doc 02.
  - Before seeding, the approver checks the seeder-format file against §8.
- **BS port fixes 362b391: LAND** (on main as e46bd24). **Debt is NOT G2-eligible** until the six conditions hold:
  1. The equity-block guard is fixed: 7/7 false holds at capitalization-format utilities.
  2. The pinned outputs are published and graded against the answer key in `VERIFY-DEBT-PORT-2026-11-01.md`.
  3. The traps are fixed: META 2018-12-31 = 0, NVDA 2017-01-29 = 2,789, AMZN gross capital-lease payments never used.
  4. No double count when the FinanceLeaseLiability total is itself a face member.
  5. GOOG 2024-12-31 = 13,559 and WMT 2026-01-31 = 51,523.
  6. Rulings accepted by Dhairya: DVN 2017 = latest print 6,864; META 2025-12-31 = the 10-K print only if the 10-Q's printed debt lines are equal, else a blank with reason.
- **capex/D&A port 479f7dd: LAND WITH FOLLOW-UPS.**
  - Store-only values (later vintage where the lane held, derived differently, key not in the lane) are NOT G2-eligible until the store gate fails on them or the Verifier draws them.
  - V11 (KEY) must carry across filings, or KEY is held.
  - The raw-print sign/scale check needs a test.

## Pilot (10 companies: MSFT, HD, AAPL, JPM, TRV, PLD, NEE, XOM, JNJ, WMT)
- Last run I read: 41329681197.
  - Valued 54.8–85.3%; reasonless 155–389 per company.
  - 0 derived cells without SAME_BASIS.
- G2 criteria:
  - 100% of the sector template, valued or reasoned;
  - library completeness 100%;
  - 0 reasonless cells and 0 unevidenced derived cells;
  - before-image saved;
  - Verifier draw: MSFT 40, HD 40, the others 20 each, with at least 10 BS cells per company.
- The 1,000-company load is approved by the founder after G2 passes.

## Open
- **0121 apply:** needs the founder's words.
- **Sector-template seeder file:** the preparer writes it, then I check it.
- **Debt conditions 1–5:** with the BS cloud session.
- **capex follow-ups:** branch work/capex-da-debt/store-gate-followups.
- **Not on main as of 2026-11-02:** `verify/debt-port-2026-11-01` (0b7b2d7; ledger and tag inbox entries).
- **main CI advisory job red: critical Next.js advisory.** next 16.4.0 is pinned; the fix is 16.4.4. Raised to the founder.

## Gotchas
- **Branch CI green does not mean the branch can land on main.** The pre-push hook runs mypy, which CI only runs as advisory.
- **Exit codes are not proof.** A regression gate that only reports can exit 0 over hundreds of differences: check that it fails closed. Pinned-diff gates must refuse "unexplained" classes.
