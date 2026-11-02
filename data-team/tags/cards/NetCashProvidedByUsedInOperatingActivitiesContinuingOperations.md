# Tag card: NetCashProvidedByUsedInOperatingActivitiesContinuingOperations

Written 2026-11-02 by the FSN expert. Family: cash-flow totals.

## Meaning
- **What it is:** net cash from operating activities of **continuing** operations.
- **Period type:** duration.
- **Balance:** debit.
- **Relation to the total:** the calc child of `NetCashProvidedByUsedInOperatingActivities` when discontinued operations are presented separately.

## Who uses it
- On the CF face for 60 EDGAR names in our top-100 extract, 2009–2026 (997 lines). The total tag: 130 names, 5,218 lines (DI).
- **Many companies use it as their only CFO line, with no discontinued operations.** MSFT Q2 FY2014 0001193125-14-018634 … Q1 FY2018 0001564590-17-020171, label "Net cash from operations".
- The `…FinancingActivitiesContinuingOperations` / `…InvestingActivitiesContinuingOperations` siblings follow the same era.

## Rule
- Map it as CFO **only when the filing prints no `NetCashProvidedByUsedInOperatingActivities` line**.
- If both are printed, the difference is discontinued-operations cash flow, and CFO is the total (or the continuing figure, per the concept definition). Never sum them.
