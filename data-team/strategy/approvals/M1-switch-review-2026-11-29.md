# Approver review: M1 switch (`FSN_NIGHTLY_STAGE=write` + `HYBRID_NEW_PATH=on`), 2026-11-29

Reviewer: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Stage 3 Resolve, M1. Reviewed
`data-team/strategy/certification/structural-write-release-2026-11-29.md` (3635129d6). This is a review only. Flipping
the switch is a production write and needs the founder's own typed words in the session that applies it (root CLAUDE.md).

## Recommendation: not yet; three conditions

1. **The gate isn't met.** PIPELINE.md section 7 gates M1 on "155 top-100 DISAGREE cleared". The release note measures 129 left. Two of them serve a value:
   - ORCL cost_of_revenue FY2024 (15,143,000,000)
   - CRM total_debt FY2018 (2,233,015,000)

   A served value whose proof disagrees breaks the founder's 2026-11-16 rule, switch or no switch. Those two must be fixed or opened first.

   If the lanes want the gate restated as "0 served DISAGREE; the other open DISAGREE cells tracked in the exceptions queue", that's a reasonable gate. But it changes a founder gate, so the founder decides it.
2. **The 26 new values need combined: badges before they serve.** I checked the latest 10-Ks in fsn: the cash-flow lines are combined lines, which may show only with their printed label (Dhairya rule, 2bc5a106).
   - T cf_inventory_change uses IncreaseDecreaseInOtherOperatingAssets. T 0000732717-26-000120 prints it as "Inventories, prepaid and other current assets". The badge must be `combined:Inventories, prepaid and other current assets`.
   - AMZN cf_ar_change uses IncreaseDecreaseInAccountsReceivableAndOtherOperatingAssets. AMZN 0001018724-26-000004 prints it as "Accounts receivable, net and other". The badge must be `combined:Accounts receivable, net and other`.
   - XOM cf_ap_change (IncreaseDecreaseInAccountsPayable) is the plain line.

   Please show the planned badge per cell in the dry run. Served as `as_printed`, these cells fail the badge census.
3. **Proof first.** The 26 cells have no cell_proof row. They serve only after `proof --write`, and the next certification draw for AMZN, XOM and T has to cover them.

## What's fine

- Dropping the 7 T FY2015-21 not_presented reason rows is correct. The filing's column holds a value, so a "not presented" reason would be false. The cells stay OPEN until they are resolved with the combined badge above.
- The NEE cf_ar_change FY2015 relabel keeps the same value (-90,000,000). It's fine.
- 0 served PROVEN values change. The 70 era_unmapped cells are in the serve and guard step, not this switch, so they're out of scope here.
