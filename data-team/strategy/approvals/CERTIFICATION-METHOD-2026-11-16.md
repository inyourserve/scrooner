# Certification method after the founder decision of 2026-11-16 (Ritwik cloud, approver)

Source: doc 02, commit 438677db. A shown cell must hold a real proven value; a reason no longer counts as a covered shown cell. Certification runs on Engineering's coverage export with a `display` column (SHOWN_VALUE / HIDDEN_ROW / HIDDEN_YEAR / OPEN).

## Pass test, per company

1. **No OPEN cells.** Any OPEN cell fails the company.
2. **Shown cells.** A seeded random draw of 32 SHOWN_VALUE cells. Each must equal the filing's printed value at its cited accession, R page, tag and column.
   - Sums are checked part by part against every line in the data point's perimeter: total_debt includes face short-term debt and CP, current and long-term debt, note finance leases and pre-842 capital leases.
   - Split cells (a combined line split from note breakdowns) are checked against the note parts, and the parts must sum to the combined face line.
3. **Census rows.** Every total_debt year that is shown is checked against its full perimeter.
4. **Hidden rows.** For each HIDDEN_ROW data point, I check that the company never reports it in any year. I check the latest 10-K and the first 10-K in the window, face and notes (MetaLinks or note scan). A hide fails if any filing prints a value for that line, including a component that the split rule could use.
5. **Hidden years.** For each HIDDEN_YEAR, I check that the year ends before the company's first periodic filing presents it. A later 10-K comparative column counts as presenting the year, as the GEV draw showed. Only periodic reports present a year: 10-K, 10-Q, 20-F and 40-F, including their comparative columns (Dhairya ruling 2026-11-16). A year that appears only in a registration statement (Form 10, S-1, F-1) is a pre-filing year and is hidden. GEV's FY2022 balance-sheet cells are hidden pre-filing years. **Hides inside the filing window (doc 02, "Display rules under the 2026-11-16 founder decision", main 2bc5a106):** (1) for the VERIFIED_ABSENT_HIDE allowlist only (operating_income, shares_outstanding, share_buybacks, dividends_paid, gross_profit, total_debt, current_assets, current_liabilities), a year may be hidden when no periodic filing that presents the period prints the row's line; (2) a year hidden as reported only combined (`line_presented_combined`) passes the same test on the row's own line. A printed dash counts as printed. The tool reads statement lines (fsn.line), not facts, because a dash has a line but no fact. Every other hidden year must be a pre-filing year.
7. **Hide reasons.** Every hide must carry a doc 02 hide class: never presented (`structural_not_presented`), only combined (`line_presented_combined`), a pre-filing year, or an allowlisted absence. A hide whose reason is anything else (`era_unmapped`, `reason_own_filing_unverified`) is a pipeline gap shown as a hide, and fails. Since main 532fc006 the export writes a `hide_class` column, exactly one of `structural_not_presented`, `line_presented_combined`, `pre_filing`, `verified_absent`. When the column is present it is the class judged, and `reason_code` is kept as the evidence behind it. A class must also fit the cell: `pre_filing` only on a year, and `verified_absent` only on an allowlisted data point. The class is then proved, not trusted: hidden rows against filing facts, and hidden years against pre-filing status or the printed-line test.
8. **Stated values** (doc 02 rule 3: `stated_zero`, `text_stated`) have no XBRL fact to match. A drawn one goes to the approver as NOT_FOUND (REVIEW), and none counts toward a PASS until the founder accepts the proof.
6. **Locators.** Every shown cell, and every part of a sum or split, carries an accession and an R page.

**Bound:** 0 errors in the shown draw gives a Clopper-Pearson 95% upper bound of 8.94% per company (n=32). The 0.10% target applies pooled across certified companies.

## Effect on earlier verdicts

- **MSFT certificate (31aa5fc0, 2026-11-14): SUPERSEDED for display.** It was issued under the old value-or-reason test.
  - Its 516 PROVEN cells' evidence stands.
  - Its 36 REASON cells must now be either a shown value or a hide: D&A FY2015-24 and FY2025-26 combined lines are split from the notes; interest income and other income (expense) are hidden if never reported.
  - MSFT is re-certified on the new export: the shown draw, plus checks of its hides.
- **TXN, PM and GEV final draws (FAIL):** the PROVEN, total_debt and locator findings carry over. Their REASON-cell findings become hide or split findings under the new test:
  - GEV: the first 10-K's FY-1 and FY-2 columns mean those years are not hidden years. Only FY2022 balance-sheet cells are hidden, as pre-filing (registration-only).
  - PM: parent comprehensive income is printed, so the row is shown with values, and FY2022 amortization is split from the note.
  - TXN: amortization of acquired intangibles must be shown with a value, or the row hidden only if never reported.

## How it runs (2026-11-16)

The checks above run as one tool, `pipeline/scripts/certify_display.py` (logic in `pipeline/src/scrooner_pipeline/certification/display_cert.py`, tests in `pipeline/tests/unit/test_display_cert.py`). It downloads nothing from the SEC. Every value is checked against SEC's own Financial Statement and Notes data for the cited filing, already loaded in `fsn.*`, so a company takes minutes, not hours.

- **Run:** dispatch the `Display certification (approver)` workflow (`.github/workflows/display-certify.yml`). It takes request files, or `pending` for every request without a verdict file. It is read-only and writes nothing to the database or the repo. Locally with DATABASE_URL: `python pipeline/scripts/certify_display.py --request <request.md> --live --out-dir <dir>`.
- **Seed:** `<TICKER>-<first 12 hex of the coverage sha256>`. The draw is fixed by the file, so anyone can re-run it and get the same sample.
- **Outputs:** a verdict page and an evidence CSV per company, plus one row in `data-team/strategy/approvals/registry.csv`. The pooled bound is computed over every company whose latest row is PASS.
- **The approver still decides.** Any REVIEW item (a lease location the facts cannot show, a hidden row with no tag family on file, a locator-only difference) is checked by hand, and the approver commits the certificate or final-draw file.
- **Known gap:** fsn.* can miss a fact. For example, MSFT `CapitalLeaseObligationsCurrent` at 2016-06-30 is absent from its FY2017 10-K row set. A NOT_FOUND therefore goes to the approver, not straight to FAIL in the published verdict.
- **Machine-readable certificate (2026-11-21):** each run also writes `<TICKER>-display-cert-<date>.json`, using schema `pipeline/src/scrooner_pipeline/certification/schemas/display_certificate.v1.schema.json` (`display-certificate/1`).
  - It holds every cell of the coverage file, with `evidence`: `drawn`, `census` or `sampled`. It also holds the request's versions and the bound.
  - The workflow pushes its outputs to branch `certify-out/run-<id>`, never main. The approver reviews that branch and commits the certificate to `data-team/strategy/approvals/certificates/<TICKER>-<coverage sha256 first 12>.json`, which the registry loader reads (rulings: CERT-REGISTRY-rulings-2026-11-21.md).
- **Badges (founder decision 2026-11-22, doc 02 "one standard definition per metric, shown with a badge"; supersedes display rule 2):** when an export carries a `badge` column, every shown cell must carry a badge that `metrics/registry/data_points.csv` lists for its data point and sector. A `<placeholder>` step accepts any filled-in text. The rules, checked as a census over every shown cell:
  - A data point that is not applicable to the sector (for example bank or insurer current_assets) has no shown value.
  - A never_derive data point (EPS) is never `derived:`.
  - A `derived:` value takes every part from one filing.
  - Every `combined:` and `derived:` cell is value-checked, drawn or not. A combined cell must equal the printed combined line (same tag, period, duration and dimensions, on the cited R page). A derived cell must match its parts or its identity.
- **Derived identities** (census over every derived cell, drawn or not):
  - total_liabilities = assets - total equity incl. NCI - temporary equity. GILD FY2015: 51,716 - 19,113 - 2 = 32,601, the sum of its printed liability lines.
  - shares_outstanding = shares issued - treasury shares, from the same filing.
  - gross_profit = shown revenue - shown cost of revenue.
