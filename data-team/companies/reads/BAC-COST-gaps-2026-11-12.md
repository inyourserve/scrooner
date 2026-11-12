# BAC / COST gaps, read 2026-11-12 (FILING-CHECKED, sec.gov at <=0.5 req/s)
Filings: BAC 10-K FY2025 acc 0000070858-26-000157 (period 2025-12-31); COST 10-K FY2026 acc 0000909832-26-000093 (period 2026-08-30; FY-1 = FY2025 ending 2025-08-31).
Companyfacts: data.sec.gov/api/xbrl/companyfacts CIK0000070858 / CIK0000909832.

1. BAC amortization of intangibles: PRINTED (note only, not on the face).
 - R108.htm "Goodwill and Intangible Assets - Narrative (Details)", label "Amortization of intangibles", tag us-gaap:AmortizationOfIntangibleAssets. 2025 78, 2024 78, 2023 78 ($M). Text (Note 7 / Note 1): "Amortization of intangibles expense was $78 million for 2025, 2024 and 2023."
 - companyfacts AmortizationOfIntangibleAssets (undimensioned): FY0 2025-01-01..2025-12-31 = 78,000,000 acc 0000070858-26-000157; FY-1 2024-01-01..2024-12-31 = 78,000,000 (accs 0000070858-25-000139 and -26-000157).
 - Not on income statement R3 (R3 = Consolidated Statement of Income); the cash-flow D&A line (DepreciationDepletionAndAmortization 2,314M / 2,189M) is a different, larger item.

2. BAC dividends per share (common):
 - PAID, printed: R133.htm "Shareholders' Equity - Common Stock Narrative (Details)", label "Cash dividends paid (in dollars per share)", tag us-gaap:CommonStockDividendsPerShareCashPaid (member CommonStockMember): 2025 $1.08, 2024 $1.00, 2023 $0.92. Text: "cash dividends paid per share of common stock were $1.08, $1.00 and $0.92 for 2025, 2024 and 2023". companyfacts CommonStockDividendsPerShareCashPaid: FY0 1.08 (2025-01-01..2025-12-31, acc -26-000157), FY-1 1.00 (2024, accs -25-000139 and -26-000157).
 - DECLARED: only quarterly, no annual declared figure printed. R132.htm "Declared Quarterly Cash Dividends on Common Stock (Details)", tag us-gaap:CommonStockDividendsPerShareDeclared: Q1'25 0.26, Q2'25 0.26, Q3'25 0.28, Q4'25 0.28 (sum 1.08, arithmetic only); subsequent event 0.28 declared Feb 2026. companyfacts has the quarterly durations (2025 quarters acc -26-000157; 2024 quarters 0.24,0.24,0.26,0.26 acc 0000070858-25-000139). No annual declared value in companyfacts.
 - Statement of equity R7 prints dividend dollars (DividendsCommonStockCash), not per share.

3. COST dividends per share (common): declared, printed.
 - R55.htm "Stockholders' Equity - Additional Information (Details)", label "Common Stock, Dividends, Per Share, Declared", tag us-gaap:CommonStockDividendsPerShareDeclared: FY2026 $5.54, FY2025 $4.92 (and 4-month column ended 2026-08-30 $1.47 = current quarterly rate). Text, Note 6 Equity: "Cash dividends declared in 2026 totaled $2,458 or $5.54 per share, as compared to $2,183 or $4.92 per share in 2025." Also MD&A Liquidity.
 - companyfacts CommonStockDividendsPerShareDeclared: FY0 5.54 (2025-09-01..2026-08-30, acc 0000909832-26-000093); FY-1 4.92 (2024-09-02..2025-08-31, accs 0000909832-25-000101 and -26-000093). Also fragments 1.30 (2025-05-12..2025-08-31) and 1.47 (2026-05-11..2026-08-30).
 - Special dividend: $15/share (total $6,655M) is in FY2024 only (R55 Special Dividend member, FY2024 column; Note 6 "Dividends in 2024 included a special dividend of $15 per share"). FY2024 companyfacts 19.36 (2023-09-04..2024-09-01) includes it (4.36 regular + 15). No special dividend in FY0 or FY-1. FY0/FY-1 5.54 and 4.92 are regular only.
 - Costco R3 (income statement) and R7 (equity statement) print dividends in dollars, not per share.

Pages searched: BAC main 10-K text, R3, R7, R8, R108, R132, R133; COST main 10-K text, R3, R7, R55. Nothing missing.
