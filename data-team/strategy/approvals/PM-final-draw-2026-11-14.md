# PM final draw (Ritwik cloud, approver, 2026-11-14): FAIL

**Checked:** `data-team/strategy/certification/PM-coverage-2026-11-14.csv` at main **eca72c51** (506 cells: 459 PROVEN, 47 REASON), proof v19. Seed: `pm-final-eca72c51`. All checks are against the SEC filings.

| Check | Result |
|---|---|
| 32 random PROVEN cells | 32/32 match. 21 matched by script and 11 by hand (column offsets; DPS FY2016 = 1.04 + 1.04 + 1.02 + 1.02 = 4.12, the four quarterly rows on R8; opex = MA&R + amortization or goodwill impairment, tying GP - OI) |
| 5 random REASON cells | **4/5.** comprehensive_income FY2016 is wrong (item 1). Confirmed: sga FY2024 (R3 prints only 'Marketing, administration and research costs'), share_buybacks FY2025 (R9), sbc FY2016 (R9), shares_outstanding FY2018 (R5 prints only issued and repurchased shares) |
| REASON cells cite a filing presenting their year | 47/47 |
| total_debt, all 11 FY, full perimeter | 11/11. Face short-term borrowings + LongTermDebtAndCapitalLeaseObligations (current and noncurrent). The finance leases sit inside those lines: FY2025 10-K R122 places them in 'current portion of long-term debt' and 'Long-term debt (Note 6)', and R66 lists 'Finance leases 84' in total long-term debt. Nothing is added |
| Locators | **3 cells have no R page:** amortization_of_intangibles FY2022 (REASON) and interest_expense FY2022-23 (PROVEN). Engineering disclosed only the first |

## Failing items

**1. comprehensive_income REASON is false** (11 cells, line_presented_combined, FY2015-25; FY2016 was drawn).
- The reason says only the figure including NCI is printed. The FY2016 10-K (0001413329-17-000014) R5 prints both 'Total comprehensive earnings' 7,043 and **'Comprehensive earnings attributable to PMI' 6,810** (us-gaap ComprehensiveIncomeNetOfTax).
- The parent figure is the data point, so these cells should be PROVEN at the printed parent value per year. Every year must be re-checked.

**2. amortization_of_intangibles FY2022 REASON is false** (1 cell).
- The FY2022 10-K (0001413329-23-000025) R60 prints 'Amortization of intangibles' on two income-statement-line members: Cost of sales **58** + Marketing, administration and research costs **101** = **159**.
- These are printed member rows, so the member-row sum rule applies (as CDNS and INTU cost of revenue). The FY2023 10-K R64 shows the same split for 2023: 58 + 439 = 497, which equals the served 497.
- FY2022 should be PROVEN 159, citing R60. Confirm the column: the R60 header mixes periods.

**3. Locators** (3 cells).
- interest_expense FY2022 (768) and FY2023 (1,526) are PROVEN and cite the FY2024 10-K (0001413329-25-000013) with no R page. That filing's IS (R3) prints only 'Interest expense, net', so the gross figure must come from Note 15. Cite that note's R page and confirm both values there.
- amortization FY2022 becomes PROVEN at R60 under item 2.

## To certify

1. Fix items 1-3 (14 cells).
2. Send the new hash. I then re-check every changed cell and a 5-cell PROVEN top-up.

The other 32 PROVEN, 4 REASON and 11 total_debt checks stand. Evidence: `PM-final-draw-2026-11-14-proven.txt` and `-total-debt.txt` beside this file. In the debt file, the script's 'lease' column adds the note finance leases, but they are already inside the debt lines (R122), so the served values are right.
