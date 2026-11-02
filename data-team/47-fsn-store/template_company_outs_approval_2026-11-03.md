# Approval of template_company_outs.csv (Ritwik, release approver), 2026-11-03

Input: `template_company_outs.csv` on work/engineering/fsn-pilot d9e7767. It has 280 company × data point template-OUT rows from the tag-mapper. The tag-mapper's evidence is a scan of face statement (pre) rows only.

Condition (Dhairya, 2026-11-03): OUT is right only if neither the face nor any note prints the concept. FSN carries note facts.

Check run: one read on `core.fact` + `core.period` + `core.concept`.
- The facts are SEC companyfacts: non-dimensional, face and notes.
- Periods are annual (350–380 days) with an end date on or after 2015-01-01.
- Interest-expense tags: us-gaap InterestExpense, InterestExpenseNonoperating, InterestExpenseDebt, InterestAndDebtExpense, InterestExpenseOperating.
- Operating-income tag: us-gaap OperatingIncomeLoss.
- Evidence level: DATA-INFERRED. A fact's presence shows the filer printed the concept somewhere; it does not tell face from note, and no R page was opened.

Per-row verdicts are in `template_company_outs_approval_2026-11-03.csv`:

| Verdict | Count | Meaning |
|---|---|---|
| APPROVE_OUT | 182 (OI 97, IE 85) | No fact since 2015. OUT for every period. |
| REJECT_NOTE_SOURCED_VALUE | 73 (IE 58, OI 15) | Printed through 2024 or later (e.g. MSFT, GOOG, MRK, INTC, PFE interest expense; HON, PH, DE operating income). Not an OUT: serve as a note-sourced value with its own Verifier stratum. |
| APPROVE_OUT_FROM | 25 (IE 12, OI 13) | Printed up to `out_effective_after`, then stopped (e.g. AAPL IE through FY2023; PPG, SLB, SHW OI through 2023). IN up to and including that date; OUT for later periods (the template is effective-dated). |

Before the seeder uses this file:
1. Engineering confirms with FSN `num` rows that the REJECT and APPROVE_OUT_FROM rows really come from a note or face of the company's own 10-K, not a dimensional segment slice. Report the FSN accession for each row.
2. The Verifier draws 10 REJECT rows and 5 APPROVE_OUT_FROM rows, filing-checked, before the note-sourced values count for G2.

## Correction, 2026-11-03 (after engineering's FSN confirmation, d0689d1)
- **My error:** my check counted `InterestExpenseDebt` as gross. The interest card says it is the debt-only component.
- **13 interest rows → `PENDING_SOLE_DEBT_INTEREST_RULE`:** ACI, CI, AVAV, CRWV, KTOS, WMG, CARR, BR, FLUT, YUM, TPR, HPQ (gross only FY2015) and VRNS (Debt only, FY2018–2021).
  - Ruling: `InterestExpenseDebt` counts as gross interest expense for a filing only when all three hold:
    - it is the only interest-expense line that filing prints;
    - its label reads as interest expense, not "interest on borrowings" beside other interest;
    - no other gross IE tag is in that filing (the PGR and CVX pattern on the card).
  - The Verifier checks the label for these 13. If a row fails, it becomes APPROVE_OUT with reason `only_component_printed`.
- **TOL interest:** OUT after 2019-10-31, not 2022. Gross InterestExpense ends in FY2019; the zero it prints then is real (interest capitalised).
- **40-F/20-F years (SHOP, CP interest; CNH operating income):** the verdict stands for the 10-K years. Cells in a 40-F/20-F year follow that period's filing-form reason, not this row.
- **Unchanged:** the 81 gross note-only rows engineering confirmed, and all 15 OperatingIncomeLoss REJECTs, stand as note-sourced values (own Verifier stratum; production write OFF until the draw passes).
