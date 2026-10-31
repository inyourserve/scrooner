# VERIFY: B9 instance fallback, cohort dry run (2026-11-04)
Branch work/engineering/b9-instance-fallback 2c896c0, data-team/44-b9-instance-fallback/cohort-dryrun-2026-10-31.jsonl.gz. Planned cells regenerated read-only (find_missing + plan_filings, flag OFF, nothing written): 44 fillable filings with period >= 2014, 4,213 statement cells. Seed 20261104: Visa Q3 FY2026 plus 9 random. Each value read from the cited filing's R page, matched by the row's XBRL element. Verifier 2 (scrooner-bc). 22 SEC requests.

## Result: YES, 10 of 10 right
| Cell | Planned | Face |
|---|---|---|
| V Q3 FY2026 OtherNonoperatingIncomeExpense, 3M to 2026-06-30 | 150M | "Investment income (expense) and other" 150 |
| CAT IntangibleAssetsNetExcludingGoodwill 2026-06-30 | 3,550M | "Other intangible assets - net" 3,550 |
| 1047862 ProceedsFromIssuanceInitialPublicOffering 6M 2026 | 884M | "Issuance of common shares - public offering" 884 |
| 1109357 NetCashProvidedByUsedInFinancingActivities 6M 2026 | 2,120M | 2,120 |
| 1967680 PaymentsForRepurchaseOfCommonStock 6M to 2026-07-03 | 434M | (434) |
| CLX WeightedAverageNumberOfSharesOutstandingBasic FY2026 | 121,775,000 | 121,775 (thousands) |
| 910606 ProceedsFromCollectionOfLoansReceivable 6M 2026 | 1,069K | 1,069 |
| CNP NonoperatingIncomeExpense 6M 2026 | -486M | "Total" other income (expense) (486) |
| ABT RepaymentsOfLongTermDebt 6M 2026 | 2,821M | (2,821) |
| SPGI LiabilitiesAndStockholdersEquity 2024-12-31 | 60,221M | 60,221 |

The printed parentheses on payment lines are presentation only. The tag values are positive by definition, so the planned sign is right.

## Notes
- A label-only match is ambiguous on utility statements: CNP prints "Total" three times. Match by element, as here.
- Untested: note cells (`stmt=note`) and the 70 FY2013 filings (before the 2014 floor).
