# Tag card: CommercialPaper

Written 2026-11-02 by the FSN expert. Family: debt (short-term).

## Meaning
- **What it is:** the carrying value of unsecured short-term promissory notes (commercial paper) at the balance-sheet date. A component of short-term debt.
- **Period type:** instant.
- **Balance:** credit.
- **Usage:** a face line or a debt-note line.

## Who uses it
- On the BS face for **13 EDGAR names** in our top-100 extract, 2009–2026 (213 BS lines; DI): AMGN, ADI, AAPL, FPL/NEE, HD, JPM, MSFT, QCOM, TXN, WMT.
- Labels: "Commercial paper" (141), **"Short-term debt"** (36), "Commercial paper notes" (14), "Short-Term Debt" (12).

## How it behaves
- **It may be the only short-term debt line, under the label "Short-term debt".**
  - MSFT FY2024 10-K 0000950170-24-087843 R4 (FILING-CHECKED): "Short-term debt 6,693" is `CommercialPaper`.
  - MSFT used `ShortTermBorrowings` for the same label to FY2018. The tag switches on an identical label, so a label rule and a tag rule disagree.
- It is a calc child of `LiabilitiesCurrent` on the face.

## Misuse seen
- Production `total_debt` for MSFT FY2024 = 44,937M omits it; the face total is 51,630M (MSFT dossier §7).
- **Rule:** a face `CommercialPaper` line is a debt component. Never add it on top of `ShortTermBorrowings` or `DebtCurrent` when that line is its calc parent (check the calc tree).
