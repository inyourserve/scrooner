# Top-100 cohort read queue, 20 cells, read against the filing (2026-11-29)
Source: data-team/strategy/certification/cohort/top100-cohort-reads-2026-11-29.csv at 8d3930898 (git show; not in shared tree). FILING-CHECKED. 25 sec.gov requests, 1 per >=2.1 s, UA "Scrooner research contact@scrooner.com".
| ticker | data_point | FY | shown | printed (label, scale) | verdict | URL |
|---|---|---|---|---|---|---|
| C | cash_and_equivalents | 2021 | 262,033,000,000 | "Cash, due from banks and deposits with banks at end of period" 262,033 ($M) = 27,515 cash and due from banks + 234,518 deposits with banks | MATCH (checker compared CashAndDueFromBanks only) | https://www.sec.gov/Archives/edgar/data/831001/000083100122000036/R9.htm |
| AMGN | gross_profit | 2019 | 19,006,000,000 | Total revenues 23,362 - Cost of sales 4,356 ($M) = 19,006 | MATCH (derived) | https://www.sec.gov/Archives/edgar/data/318154/000031815422000010/R3.htm |
| AXP | deposits | 2017 | 64,452,000,000 | "Customer deposits" 64,452 ($M) at 2017-12-31, us-gaap:Deposits (instant) | MATCH (claim check looked for qtrs=4) | https://www.sec.gov/Archives/edgar/data/4962/000000496218000032/R5.htm |
| CB | other_income_expense_net | 2018 | 434,000,000 | "Other (income) expense" (434) ($M) in expenses = 434 income | MATCH | https://www.sec.gov/Archives/edgar/data/896159/000089615919000005/R4.htm |
| CRM | dividends_paid | 2021 (FYE 2021-01-31) | 0 | Item 5 Dividend Policy: "We have never paid any cash dividends on our common stock." | MATCH (text) | https://www.sec.gov/Archives/edgar/data/1108524/000110852422000008/crm-20210131.htm |
| DE | cost_of_revenue | 2021 (FYE 2021-10-31) | 29,116,000,000 | "Cost of sales" 29,116 ($M), Net Sales member | MATCH | https://www.sec.gov/Archives/edgar/data/315189/000155837023019812/R2.htm |
| DELL | interest_income | 2025 (FYE 2025-01-31) | 160,000,000 | "Investment income, primarily interest" 160 ($M), InvestmentIncomeInterestAndDividend | MATCH | https://www.sec.gov/Archives/edgar/data/1571996/000157199625000034/R141.htm |
| DIS | dividends_per_share | 2025 (FYE 2025-09-27) | 1 | Note 11 paid table: $0.50 (2025-01-16) + $0.50 (2025-07-23) = $1.00/share | MATCH (derived) | https://www.sec.gov/Archives/edgar/data/1744489/000174448926000066/dis-20261003.htm |
| FTNT | interest_income | 2020 | 17,700,000 | "INTEREST INCOME—NET" 17.7 ($M), InvestmentIncomeNet | MATCH (label is net) | https://www.sec.gov/Archives/edgar/data/1262039/000126203921000008/R4.htm |
| MCD | cost_of_revenue | 2017 | 12,199,600,000 | Food & paper 4,033.5 + Payroll 3,528.5 + Occupancy & other 2,847.6 + Franchised occupancy 1,790.0 ($M) = 12,199.6 | MATCH (derived) | https://www.sec.gov/Archives/edgar/data/63908/000006390820000022/R2.htm |
| MS | dividends_paid | 2021 | 4,171,000,000 | "Cash dividends" (4,171) ($M), PaymentsOfDividends (common+preferred) | MATCH (combined) | https://www.sec.gov/Archives/edgar/data/895421/000089542122000400/R8.htm |
| NEE | cf_ap_change | 2018 | 163,000,000 | NEE block "Current liabilities" 163 ($M) (FPL block separate: (509)) | MATCH (combined) | https://www.sec.gov/Archives/edgar/data/753308/000075330821000014/R7.htm |
| NEE | cf_ap_change | 2024 | 767,000,000 | NEE block "Current liabilities" 767 ($M) (FPL block: (23)) | MATCH (combined) | https://www.sec.gov/Archives/edgar/data/753308/000075330826000015/R8.htm |
| ORCL | cost_of_revenue | 2019 (FYE 2019-05-31) | 7,995,000,000 | Cloud services and license support 3,782 + Hardware 1,360 + Services 2,853 ($M) = 7,995 | MATCH (derived) | https://www.sec.gov/Archives/edgar/data/1341439/000156459021033616/R4.htm |
| QCOM | cash_paid_for_interest | 2018 (FYE 2018-09-30) | 662,000,000 | "Interest paid related to commercial paper and long-term debt, net of cash received from the related interest rate swamps" 662 ($M), 12-month Sep 30 2018 column, qcom_Interestpaidnetofinterestreceived | MATCH | https://www.sec.gov/Archives/edgar/data/804328/000172894918000095/R63.htm |
| QCOM | cash_paid_for_interest | 2020 (FYE 2020-09-27) | 507,000,000 | same label, 507 ($M) | MATCH | https://www.sec.gov/Archives/edgar/data/804328/000172894920000067/R57.htm |
| SNDK | amortization_of_intangibles | 2023 (FYE 2023-06-30) | 133,000,000 | Note: "During 2023, the Company recognized intangible amortization charges of $133 million"; segment recon "Amortization of acquired intangible assets" (133) ($M) | MATCH | https://www.sec.gov/Archives/edgar/data/2023554/000202355425000034/sndk-20250627.htm |
| T | interest_income | 2016 | 118,000,000 | ex13 MD&A Other income (expense) - net: "interest and dividend income of $118" (dollars in millions) | MATCH (text) | https://www.sec.gov/Archives/edgar/data/732717/000073271717000021/ex13.htm |
| VRTX | gross_profit | 2019 | 3,615,063,000 | Revenues 4,162,821 - Cost of sales 547,758 ($K) = 3,615,063 | MATCH (derived) | https://www.sec.gov/Archives/edgar/data/875320/000087532020000007/R2.htm |
| WMT | operating_expenses | 2016 (FYE 2016-01-31) | 97,041,000,000 | "Operating, selling, general and administrative expenses" 97,041 ($M), SellingGeneralAndAdministrativeExpense | MATCH | https://www.sec.gov/Archives/edgar/data/104169/000010416916000079/R2.htm |

MATCH 20 / MISMATCH 0 / CANNOT_LOCATE 0

Definition notes for approver (values match; definitions are rulings, not value errors): C cash includes interest-bearing deposits with banks; FTNT "interest income—net" is a net line; MS and NEE are combined lines; QCOM interest paid is net of swap receipts.

Tag feedback lines NOT appended (repo write denied, brief is read-only); queue for data-team/tags/feedback-inbox.md:
| 2026-11-29 | Data Verifier (cohort reads) | qcom_Interestpaidnetofinterestreceived | QCOM cash interest paid only as this custom tag in Debt details note, net of swap receipts (662 FY2018 / 507 FY2020 $M) | 0001728949-18-000095 R63; 0001728949-20-000067 R57 | FILING-CHECKED | new |
| 2026-11-29 | Data Verifier (cohort reads) | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | Citi CF end total 262,033 = CashAndDueFromBanks 27,515 + deposits with banks 234,518; comparing bank cash to CashAndDueFromBanks alone gives a false mismatch | 0000831001-22-000036 R9 | FILING-CHECKED | new |
| 2026-11-29 | Data Verifier (cohort reads) | us-gaap:InvestmentIncomeNet | FTNT tags face line "INTEREST INCOME—NET" with InvestmentIncomeNet | 0001262039-21-000008 R4 | FILING-CHECKED | new |
| 2026-11-29 | Data Verifier (cohort reads) | us-gaap:InvestmentIncomeInterestAndDividend | DELL label "Investment income, primarily interest" (not "Interest and dividend income") | 0001571996-25-000034 R141 | FILING-CHECKED | new |
| 2026-11-29 | Data Verifier (cohort reads) | us-gaap:Deposits | AXP customer deposits is instant; a claim check with qtrs=4 returns NOT_FOUND falsely | 0000004962-18-000032 R5 | FILING-CHECKED | new |
