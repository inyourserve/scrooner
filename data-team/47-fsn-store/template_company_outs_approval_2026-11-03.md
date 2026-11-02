
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
