# Certification method after the founder decision of 2026-11-16 (Ritwik cloud, approver)

Source: doc 02, commit 438677db. A shown cell must hold a real proven value; a reason no longer counts as a covered shown cell. Certification runs on Engineering's coverage export with a `display` column (SHOWN_VALUE / HIDDEN_ROW / HIDDEN_YEAR / OPEN).

## Pass test, per company

1. **No OPEN cells.** Any OPEN cell fails the company.
2. **Shown cells.** A seeded random draw of 32 SHOWN_VALUE cells. Each must equal the filing's printed value at its cited accession, R page, tag and column.
   - Sums are checked part by part against every line in the data point's perimeter: total_debt includes face short-term debt and CP, current and long-term debt, note finance leases and pre-842 capital leases.
   - Split cells (a combined line split from note breakdowns) are checked against the note parts, and the parts must sum to the combined face line.
3. **Census rows.** Every total_debt year that is shown is checked against its full perimeter.
4. **Hidden rows.** For each HIDDEN_ROW data point, I check that the company never reports it in any year. I check the latest 10-K and the first 10-K in the window, face and notes (MetaLinks or note scan). A hide fails if any filing prints a value for that line, including a component that the split rule could use.
5. **Hidden years.** For each HIDDEN_YEAR, I check that the year ends before the company's first periodic filing presents it. A later 10-K comparative column counts as presenting the year, as the GEV draw showed. A registration statement (Form 10 / S-1) counts as presenting the year unless Dhairya rules it out of scope.
6. **Locators.** Every shown cell, and every part of a sum or split, carries an accession and an R page.

**Bound:** 0 errors in the shown draw gives a Clopper-Pearson 95% upper bound of 8.94% per company (n=32). The 0.10% target applies pooled across certified companies.

## Effect on earlier verdicts

- **MSFT certificate (31aa5fc0, 2026-11-14): SUPERSEDED for display.** It was issued under the old value-or-reason test.
  - Its 516 PROVEN cells' evidence stands.
  - Its 36 REASON cells must now be either a shown value or a hide: D&A FY2015-24 and FY2025-26 combined lines are split from the notes; interest income and other income (expense) are hidden if never reported.
  - MSFT is re-certified on the new export: the shown draw, plus checks of its hides.
- **TXN, PM and GEV final draws (FAIL):** the PROVEN, total_debt and locator findings carry over. Their REASON-cell findings become hide or split findings under the new test:
  - GEV: the first 10-K's FY-1 and FY-2 columns mean those years are not hidden years.
  - PM: parent comprehensive income is printed, so the row is shown with values, and FY2022 amortization is split from the note.
  - TXN: amortization of acquired intangibles must be shown with a value, or the row hidden only if never reported.
