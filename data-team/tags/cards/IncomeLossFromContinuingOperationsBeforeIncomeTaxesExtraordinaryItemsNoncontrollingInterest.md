# Tag card: IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (pretax)

Written 2026-11-02 by the FSN expert. Family: pretax income.

## Meaning
- **What it is:** income from continuing operations before income taxes, extraordinary items and NCI. The us-gaap "pretax" total.
- **Period type:** duration.
- **Balance:** credit.
- **Sibling:** `IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments` (IFCOBIT-MI&EMI). It is pretax **before** equity-method income, so the two differ only for a company that prints equity-method income below the pretax line.

## Who uses it
- On the IS face for 100 EDGAR names, 2011–2026 (3,200 lines). The sibling: 84 names, 2009–2026 (2,330 lines) (DI, top-100 extract).
- **Companies switch between the two with no change in what is printed.** MSFT switched at the Q2 FY2022 10-Q 0001564590-22-002324: same label "Income before income taxes", and both are calc children of `NetIncomeLoss`.

## Rule
- Map either as pretax, **per filing**.
- Where a filing prints both on the face, the two are different lines (before vs after equity-method income). Check the calc tree before treating them as synonyms.
