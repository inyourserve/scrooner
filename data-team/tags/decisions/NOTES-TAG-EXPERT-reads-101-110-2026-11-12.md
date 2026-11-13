# For the Tag Expert: the shared docmap.py (558f2f15) on ranks 101-110. Reading stopped at the 2% gate.

From Ritwik cloud, 2026-11-12. Under Dhairya's method, I hand-checked every non-mapped row, every NOTE row and a seeded 10% sample of mapped rows. Each docmap's "Hand checks" section lists them with R pages.

## Gate result

**The mapped-sample disagreement rate is 1/30 = 3.3%, above 2%. Reading has stopped (paused after rank 110) until the tool is fixed.**

The sample disagreement:
- **PLD dividends_paid.** R8 'Dividends/distributions paid on common and preferred stock/units' (PaymentsOfDividends) is keyed as mapped. It mixes common with preferred and OP units, so it must be combined.

## Machine errors found in the checked (non-sample) rows

Each was corrected in the docmap and cites its R page.

| ticker | data point | machine row | filing | class |
|---|---|---|---|---|
| PLD | total_debt | LongTermDebt + LongTermDebt = 70,074,146 | R2 prints 'Debt' 35,037,073 twice (Prologis, Inc. and the co-registrant Prologis, L.P.) | co-registrant double count |
| PLD | capex | not_presented | R8: property improvements (pld:) + TI and leasing commissions + development = 3,670,812 | REIT capex lines (custom and TI tags) not in the family |
| PLD | ppe_net | NOTE R66 221.7 (corporate P&E) | only a component | NOTE hit that is only a component |
| MCK | total_liabilities | NOTE R93 (VIE note) | no total liabilities line | NOTE hit in a VIE note |
| MCK | depreciation_and_amortization | Depreciation 256 only | R9: Depreciation 256 + Amortization 473 (AdjustmentForAmortization) | D&A component misses AdjustmentForAmortization |
| SYK | depreciation_and_amortization | Depreciation 461 only | R8: + Amortization of intangible assets 732 (AdjustmentForAmortization) | same |
| PSX | interest_expense | NOTE R145 InterestExpenseDebt 997 | R3 face prints 'Interest and debt expense' 1,039 (InterestAndDebtExpense) | face library tag missed |
| PSX | accounts_receivable | NOTE R68 9,771 (DCP Midstream VIE schedule) | R5 'Accounts and notes receivable' | VIE note hit; notes receivable is never AR |

## Suggested predict.py and docmap.py fixes

1. **Co-registrant:** when the same tag prints twice on one statement page with equal values, take the parent column only.
2. **D&A components:** include AdjustmentForAmortization.
3. **REIT capex:** include PaymentsForLeasingCostsCommissionsAndTenantImprovements and custom property-improvement lines.
4. **NOTE hits:** reject note pages whose title says Variable Interest Entities, a subsidiary or a merger schedule.
5. **Interest expense:** add InterestAndDebtExpense to the face family.
6. **Dividends:** a label with 'preferred', 'units' or 'noncontrolling' means combined, never mapped.

## Two definition questions, held as review

- **SBUX** 'Product and distribution costs' as cost_of_revenue: the same question as the EXPD call.
- **GLW and PLD:** shares_outstanding and goodwill appear only in note narratives or segment tables. Those pages still need reading.
