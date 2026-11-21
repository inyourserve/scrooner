# MA display certification, 2026-11-21: FAIL (hide-class fit only)

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/MA-request-2026-11-21.md`. Run: https://github.com/inyourserve/scrooner/actions/runs/44942837244 (read-only, fsn.*).

**Approver note.** The values are clean:
- 32 of 32 random shown cells match the filings.
- total_debt matches in all 11 years.
- The gate is clean.

The FAIL is 22 hidden cells: gross_profit and inventory, hidden as whole rows FY2015-FY2025, are labelled `verified_absent`. Doc 02 rule 1 defines that class only for a year inside the filing window. A row hidden in every year is `structural_not_presented`. Mastercard reports neither line, so the hides themselves look right; the class is an exporter defect, the same one seen on JNJ (CERT-REGISTRY-rulings-2026-11-21.md, addendum 9). Re-export with the corrected class and re-request.

cf_inventory_change went to review only because the tool had no tag family for it; that is now added (`IncreaseDecreaseInInventories`). The summary's `display_certified=yes` for MA is the top100-flow mechanical gate (0 open, 0 pageless, 0 blank parts), not this certificate.

---

# MA display certification (Ritwik (cloud), approver, 2026-11-21): FAIL

Coverage `data-team/strategy/certification/MA-coverage-2026-11-21.csv` (sha256 `13e6d648c1d32d7c3eff5441baea62d05ce7802288bb0727a45f72664221897e`). Cells by display class: HIDDEN_ROW=77, SHOWN_VALUE=429. Seed `MA-13e6d648c1d3`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 32 random shown cells | 32 match, 0 wrong, 0 locator only |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Hidden rows and years | 22 failing, 1 for review, 6 evidenced |

**Bound:** 0 error(s) in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for MA alone (per-company screen; the 0.10% target is pooled across certified companies in registry.csv).

## Findings

- **FAIL** hide_reason gross_profit 2015: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2016: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2017: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2018: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2019: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2020: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2021: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2022: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2023: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2024: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason gross_profit 2025: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2015: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2016: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2017: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2018: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2019: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2020: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2021: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2022: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2023: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2024: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **FAIL** hide_reason inventory 2025: verified_absent applies to a year, not a whole row (that is structural_not_presented)
- **REVIEW** hidden_row cf_inventory_change *: no tag family on file for this data point: approver checks the filings by hand

## Hidden rows evidenced

- comprehensive_income: no presented, undimensioned, annual ['ComprehensiveIncomeNetOfTax'] fact at a display-year end in any periodic filing
- cost_of_revenue: no presented, undimensioned, annual ['CostOfGoodsAndServicesSold', 'CostOfRevenue'] fact at a display-year end in any periodic filing
- gross_profit: no presented, undimensioned, annual ['GrossProfit'] fact at a display-year end in any periodic filing
- interest_income: no presented, undimensioned, annual ['InterestAndOtherIncome', 'InterestIncomeNonoperating', 'InterestIncomeOperating', 'InterestIncomeOther', 'InvestmentIncomeInterest', 'InvestmentIncomeInterestAndDividend'] fact at a display-year end in any periodic filing
- inventory: no presented, undimensioned, annual ['InventoryNet'] fact at a display-year end in any periodic filing
- research_and_development: no presented, undimensioned, annual ['ResearchAndDevelopmentExpense'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
