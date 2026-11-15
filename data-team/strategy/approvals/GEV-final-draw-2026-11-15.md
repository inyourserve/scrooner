# GEV final draw (Ritwik cloud, approver, 2026-11-15): FAIL

**Checked:** `data-team/strategy/certification/GEV-coverage-2026-11-16.csv` at main **faa6e974**. The request named `...-11-15.csv`; the file in the commit is `...-11-16.csv`. 184 cells, FY2022-2025: 142 PROVEN, 42 REASON. Proof v19. Seed: `gev-final-faa6e974`. All checks are against the SEC filings.

| Check | Result |
|---|---|
| 32 random PROVEN cells | 32/32 match the filing |
| total_debt FY2023-25, full perimeter | 3/3. The BS (FY2024 10-K R4, FY2025 10-K R4) prints no borrowing line, so total debt is finance leases only: 311 / 266 / 278 (lease notes R77 and R74) |
| 5 random REASON cells | **3/5.** ppe_net and current_assets FY2022 pass (no 10-K presents a Dec 31, 2022 balance sheet). interest_expense FY2025 passes ('Interest and other financial charges – net' is combined). **dividends_per_share FY2023 and operating_expenses FY2022 fail** (item 1) |

## Failing items

**1. `no_public_filing_for_period` is applied to periods the first 10-K does present.**
- The FY2024 10-K (0001996810-25-000011) prints the income statement for 2024, 2023 and **2022** (R3) and the balance sheet at Dec 31, 2024 and **2023** (R4). Each reason's text says "no 10-K covers this year … that 10-K's FY-2 column does not print the line". For these cells that is false:
  - **operating_expenses FY2022** (drawn) = SG&A 5,360 + R&D 979 = **6,339** = GP 3,458 − OI (−2,881) (R3, FY2022 column). It should be PROVEN.
  - **accounts_receivable FY2023** = current receivables – net 7,409 (non-related) + 80 (related party) = **7,489** (R4, Dec 31, 2023 column; same method as the PROVEN FY2024 cell 8,174 + 4 = 8,178). It should be PROVEN.
  - **dividends_per_share FY2023** (drawn): the year is covered by that 10-K, so the reason is false. Whatever GEV declared for 2023 (likely none, as part of GE) needs evidence from that filing (equity statement or EPS note), not "no filing".
  - **interest_expense, interest_income FY2023 and FY2022:** R3 prints 'Interest and other financial charges – net' for both years, so the reason is `line_presented_combined`, as for FY2024-25.
  - **other_income_expense_net FY2022:** R3 prints 'Other income (expense) – net' 370 for FY2022. Classify it as FY2024 is classified.
  - Every other FY2022 IS or CF cell and every FY2023 cell under this code: re-derive from the FY2024 10-K's FY-1 or FY-2 column (CF R6 also prints three years).
- `no_public_filing_for_period` is true only for **FY2022 balance-sheet** cells (no 10-K presents Dec 31, 2022).
- **Name the code honestly.** GE Vernova's Form 10 registration (2024) was public and carried 2022 figures. If Form 10 periods are out of scope, call the code `no_10k_presents_period`. Using Form 10 values is a call for Dhairya.

**2. accounts_payable FY2024 and FY2023 reason (minor).**
- The BS line is 'Accounts payable and equipment project payables' (AccountsPayableAndOtherAccruedLiabilitiesCurrent), a bundled line. The honest reason is `line_presented_combined`, not "not presented".
- FY2025 AP is PROVEN 5,721 from the trade-payables note. If that note (FY2025 10-K Note 12) prints a Dec 31, 2024 comparative, then FY2024 must be PROVEN from it too.

## To certify

1. Re-derive every `no_public_filing_for_period` cell for FY2023 and every IS or CF cell for FY2022 from the FY2024 10-K columns.
2. Fix the AP reason or value.
3. Send the new hash. I then re-check every changed cell and a 5-cell REASON top-up.

The 32 PROVEN checks and 3 total_debt checks stand. Evidence: `GEV-final-draw-2026-11-15-proven.txt` beside this file.
