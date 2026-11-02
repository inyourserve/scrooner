# Tag card: InterestExpenseNonoperating

Written 2026-11-02 by the FSN expert. See also cards/interest.md (the family card, 2026-10-24), which this extends with face-usage counts and the MSFT note case.

## Meaning
- **What it is:** interest expense classified as nonoperating.
- **Period type:** duration.
- **Balance:** debit.
- **Taxonomy:** exists only from the us-gaap **2024** taxonomy (cards/interest.md).

## Who uses it
- **On the IS face** for 42 EDGAR names in our top-100 extract, 2024–2026 (320 lines; DI). Examples: ABT, AMZN, ADI, AMAT, T, BLK, BKNG, AVGO, CAT, CSCO, KO, CRWD, DHR, ETN, FTNT, GILD, HD, JNJ, KLAC, LIN, LMT, MRVL, MA, MU, NFLX.
- Labels: "Interest expense" (277), **"Interest expense - net" (13)**, "Interest expense excluding Financial Products" (9, CAT), "Interest expense, net of portion capitalized" (9).
- **In notes only** at MSFT: from the Q1 FY2025 10-Q 0000950170-24-118967 it replaces `InterestExpense` in the "Other income (expense), net" note. FY2025 2,385M, FY2026 3,051M; FY2024 under the old tag was 2,935M (DI).

## Misuse seen
- Production `interest_expense` for MSFT stops at 2024-06-30. Every company that moved from `InterestExpense` to this tag goes blank from its switch date. It is the same B6 item as the task board, confirmed at MSFT.
- **The ", net" label (13 lines) means a net amount.** Keep the label check from cards/interest.md.
