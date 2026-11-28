# Approver review: draw_check@4 (6d5fd3e1d), 2026-11-29

Reviewer: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Stage 5 Certify, M3.

**Regression run** (display-certify 46182416627, judge on main 423749b76): all six certified companies keep their verdict under @4 on their certified coverage shas: BMY, GILD, JNJ, LRCX, MA and MO are PASS. Two cells changed method: MA cash_paid_for_interest FY2025 now matches by `claim`, and no `calc` matches occurred.

## (2) Period type from the registry: accepted
Balance-sheet data points are instants, and that's what the registry says. One side effect: `display_cert.INSTANT_DPS` also drives `search_scope_gap`, so a NOT DISCLOSED hide on any balance-sheet data point now needs the 10-Q in its search scope. That's correct, because 10-Qs present the year-end column. Expect some existing hides to start failing until their evidence names the 10-Qs.

## (1) Calc totals: change before relying on it
`Filing.calc_total` accepts a total when *one* child is in the family and no child is excluded. Cash excludes only `Restricted*`. So a cell that serves "Cash and short-term investments" (children CashAndCashEquivalentsAtCarryingValue + ShortTermInvestments) as cash_and_equivalents would AUTO_MATCH. That is exactly the too-wide total this check exists to catch.

Change requested: require **every** child to be a family member or on a per-data-point allowlist. For cash, the allowlist would include CashAndDueFromBanks, InterestBearingDepositsInBanks and the FederalFundsSold family where the template's bank definition includes them. A total with any other child stays NEEDS_READ. Add a test: cash plus ShortTermInvestments sums to the shown value and is *not* matched.

## (3) Claimed element: not accepted as written
`_claimed_element` matches when the element the cell claims holds the shown value. That checks the claim against itself. It confirms the number was copied, not that the element means the data point. The draw checker's value is that it is independent of the resolver's claim.

- Evidence: MA cash_paid_for_interest FY2025 now auto-matches on `InterestExpenseDebt` (680M). It is right only because a read compared the prior 10-K's `InterestPaidNet` series (reads/MA-ec326ca1b4a3.csv).
- Failure scenario: if the export had mapped cash_paid_for_interest to `InterestExpense` (722M), and the filing had no interest-paid family fact, @4 would AUTO_MATCH a wrong concept with "verified_by machine".

Change requested: a claimed element matches only when it is **presented** on the cited R page (fsn.line) *and* its printed label passes the data point's label pattern (the same kind of gate as LABEL_GATED; for cash_paid_for_interest, something like `interest\s+paid`). QCOM's "Interest paid, net of interest received" passes that gate; MA's InterestExpenseDebt (not presented) stays NEEDS_READ. Add a test: a claimed InterestExpense holding the shown value, with no interest-paid label, is not matched.

**Until (1) and (3) change**, I read by hand every drawn cell that @4 settles by `claim` or `calc`, as if it were NEEDS_READ. This review isn't a revert; the lane owner makes the change.
