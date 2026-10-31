# Approval ruling: interest_expense.era_tag_fill@1 (2024+ taxonomy tags for gross interest expense)

Approver: Ritwik (Head of Data Product, scrooner-31), named by Dhairya. Preparer: scrooner-26 (per-share lane). Approver and preparer are different agents (all-agent policy). Date: 2026-10-31.
Proposal under review: `data-team/strategy/team/results/interest-expense-era/MAPPING-PROPOSAL.md` on `work/per-share/interest-expense-era` 7508968. Verifier verdict read: `VERIFY-INTEREST-EXPENSE-ERA-2026-11-02.md` (scrooner-bc, 12 of 12 fills right, FILING-CHECKED). Tag card read: `data-team/tags/cards/interest.md`.

## Ruling: APPROVED WITH CHANGES

This is a taxonomy-succession mapping of the same canonical concept (gross interest expense), not a new accounting definition, so no founder definition call is needed: `InterestExpenseNonoperating` (non-banks) and `InterestExpenseOperating` (banks, SIC 6021/6022/6029/6035/6036) exist only from the us-gaap 2024 schema and carry the line that `InterestExpense` carried before. Evidence accepted: bank IEO = IE in 98.6% of 2,254 shared periods (card, FILING-CHECKED on the CIVB exception); IEN = IE in 2,499 of 2,715 shared periods; every difference is held by guard 1. The approved mapping `InterestExpense` p1 / `InterestExpenseDebt` p2 stays untouched and wins where present.

## Conditions before any production write
1. **Sample the new release path.** The 328 cells released by guard 1's face clause after the 2026-11-02 draw were never sampled. A Verifier draw of at least 12 of those 328 (bank / non-bank x quarter / FY), verdict YES in a VERIFY file. "Same rule as already verified" does not substitute for a sample of a path that released new cells.
2. **Protect the written cells.** The module's own caveat says the nightly rebuild can remove the written rows. Migration 0113 (`analytics.slot_protected_cell` + guard trigger on `analytics.canonical_fact`) is applied to production (2026-10-31 06:33 UTC). Either register every written cell in `slot_protected_cell` in the same transaction (session `scrooner.slot_writer = 'on'`, rule_id, run_id, package digest) and make `restore(run_id)` clear them, or show that the nightly resolver honours the rule. One of the two.
3. **Reasons for every hold.** Each of the 1,362 held cells gets a reason row with its hold code (net label, no overlap, non-bank IEO, not on face, label unread, perimeter, sign), not only a CSV.
4. **Frozen package.** Digest and cell list fixed at the commit the Verifier draws from; a changed digest needs a fresh stale-check and a note of what changed.

## Not asked, not approved
`InterestExpenseOperating` for non-banks (operating component; held), any net-perimeter line, `InterestAndDebtExpense`.

## Production write
Needs the founder's words typed in the approver's session; approval here applies nothing.
