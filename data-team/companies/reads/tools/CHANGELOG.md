# docmap.py changelog

Shared document-first read tool (`data-team/companies/reads/tools/docmap.py`), owned by the cloud reader session. Fixtures: `test_docmap.py` (offline; one synthetic 10-K, one assertion per fix). Run: `uv run --project pipeline python -m pytest -q data-team/companies/reads/tools/test_docmap.py`.

## 2026-11-12: fixes from NOTES-TAG-EXPERT-reads-101-110-2026-11-12.md (main e545bafb) + SG&A
Every fixture fails on the previous tool and passes on this one (7/7 each way).
1. **Co-registrant facts never count twice:** a tag repeated on one statement page (co-registrant block) counts once, parent/consolidated only (PLD debt 70,074 → 35,037). `dedupe_coreg`, test_1.
2. **NOTE values only from undimensioned consolidated facts:** a note hit needs a companyfacts (undimensioned) value for the same accession and period, and note pages titled VIE / subsidiary / merger / acquisition / segment / investee / equity method / joint venture / unconsolidated / discontinued / guarantor / parent-only are rejected (MCK, PSX, BWXT, SEIC). `NOTE_REJECT`, test_2.
3. **D&A includes `AdjustmentForAmortization`** when the face prints it (MCK, SYK). `DA_PARTS`, test_3.
4. **Interest face line variants:** `InterestAndDebtExpense`, labels "Interest and debt expense" / "Interest and other financing costs" (PSX). test_4.
5. **REIT capex:** with no PP&E-purchase line, a component sum of development, property/capital improvements and TI/leasing-commission lines; acquisitions excluded (PLD). `REIT_CAPEX`, test_5.
6. **Dividends on common AND preferred / units / NCI → combined;** preferred- or NCI-only lines stay excluded (PLD). test_6.
7. **SG&A is never G&A alone** when a selling or marketing line is printed: component sum of G&A + every selling/marketing line (LYFT 1,877,231,000 ties companyfacts). test_7.

Earlier 2026-11-12 rulings already in the tool: FY2015-to-latest eras (FY2015 10-K opened), whole-filing (MetaLinks) resolution of face misses with `check: machine-full-filing`, opex never includes cost of revenue, interest gross-only (net line combined), D&A with accretion combined, shares at the BS date (cover count never used), buyback withholding / NCI-preferred dividends / interest-notes-financing receivables excluded, bank and insurer OUT data points (SIC).

## 2026-11-12 (later): three fixes found in the ranks 901-1000 mismatch rows
8. NOTE values use the data point's scale: EPS unscaled, share counts by the page's shares scale (ESNT EPS 6970 → 6.97; CTVA weighted shares 680,000 → 680,000,000).
9. Component sums compare each part's companyfacts value with the sign printed on the face (a gain shown negative inside expenses, AAON).
10. REIT capex never includes accrued / non-cash supplemental lines (`CapitalExpendituresIncurredButNotYetPaid`, HR); fixture row added to test_5.

## 2026-11-12 (later): debt leases and capex turnarounds (founder 2026-11-04 item 5; Dhairya 2026-11-12)
11. **total_debt includes finance lease liabilities** (current + noncurrent), never operating leases. Not added again when a debt line already carries leases (by tag or label, e.g. LongTermDebtAndCapitalLeaseObligations); the lease-note total (`FinanceLeaseLiability`, or current + noncurrent, same accession and BS date) is used only when no face line carries finance leases. test_1 (now 1,550 = 1,500 debt once + 50 finance leases) and test_8.
12. **capex includes turnaround expenditures** only when printed in investing activities (between the CFO and CFI totals). test_9.
