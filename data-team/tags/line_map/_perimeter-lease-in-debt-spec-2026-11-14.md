# Spec for proof/perimeter.py: a debt line that already holds the finance leases (IBM)

Tag Expert, 2026-11-14. Requested by Dhairya for Engineering. The four IBM total_debt cells marked DISAGREE `perimeter_incomplete` are right. The perimeter rule is what's wrong.

## Verdict on the four cells

All values are in millions. "LTD&CLO" stands for the filer's own `LongTermDebtAndCapitalLeaseObligations*` facts in the same filing and column. FL is the note `FinanceLeaseLiability`.

| FY | Shown (ST + LT) | Face short-term debt | LTD&CLO Current | Face long-term debt (tag) | LTD&CLO noncurrent | FL | Lease location |
|---|---|---|---|---|---|---|---|
| 2021 | 51,704 | 6,787 | 6,764 (+22 short-term loans) | 44,917 (`LongTermDebtAndCapitalLeaseObligations`) | 44,917 | 99 | ExtensibleList `in` |
| 2022 | 50,949 | 4,760 | 4,751 (+8 short-term loans) | 46,189 (`LongTermDebtNoncurrent`) | 46,189 | 239 | ExtensibleList `in` |
| 2024 | 54,973 | 5,089 | 5,059 | 49,884 (`LongTermDebtNoncurrent`) | 49,884 | 1,000 | none in instance |
| 2025 | 61,260 | 6,424 | 6,424 | 54,836 (`LongTermDebtNoncurrent`) | 54,836 | 1,153 | none in instance |

The FY2025 10-K debt note (R125.htm, "Borrowings - Long-Term Debt, Components") prints the arithmetic directly. FILING-CHECKED.

- Long-term debt, gross 62,286 = "Long-term debt excluding finance lease obligations" 61,134 + "Finance lease obligations" 1,153.
- Total 61,259, less current maturities 6,424, gives "Total long-term debt (excluding current portion)" 54,836. That is the face Long-term debt.
- The current maturities 6,424 are the face Short-term debt 6,424 (R124.htm).
- FY2024 column: gross 56,112 = 55,111 + ~1,000.

So IBM's face "Short-term debt" and "Long-term debt" already contain the finance leases in every year. Adding FL again would double count. The resolver (.22) serves ST + LT and adds no lease. It also no longer adds the FY2024 1,000 by absence.

## Why the current guard misses them

`missing_parts` skips the lease family only in three cases:

1. the claim carries a `LongTermDebtAndCapitalLeaseObligations*` tag;
2. the filer's location list names a claim tag;
3. a lease tag is a calc child of a claim part.

From FY2022 IBM tags the face line `LongTermDebtNoncurrent`, and its labels ("Long-term debt", "Short-term debt") name no lease. The lease-including element appears only in the note, with the same value. FY2024 and FY2025 also have no location list. In FY2021 the face tag is lease-named, so the claim evidently names `LongTermDebtNoncurrent` (the same 44,917) instead of the face tag.

## Rule to add to `missing_parts` (lease family loop, before `out.append(... "finance_lease")`)

The lease family counts as carried by the claim (skip it, record `resolved_by`) when **either** condition holds.

**L1, the name says so.** A claim-named balance-sheet line meets one of these:

- its tag starts with `LongTermDebtAndCapitalLeaseObligations`, `LongTermDebtAndFinanceLease`, `DebtAndCapitalLeaseObligations`, `DebtCurrentAndFinanceLease` or `LongTermDebtCurrentAndFinanceLease`;
- its face label matches `(?i)\b(finance|capital) lease|lease obligations|including (finance|capital) leases`.

This is the existing `in_debt_family` guard, widened to the other lease-including families and to the label.

**L2, the value says so.** Both parts must hold, at the column, within presentation rounding (1.5 units of the coarser figure, as `_parts_carry_total` does):

- **noncurrent:** a claim-named line's value equals one of these lease-including facts in the same filing:
  - `LongTermDebtAndCapitalLeaseObligations`
  - `LongTermDebtAndFinanceLeaseLiabilityNoncurrent` (or any `LongTermDebtAndFinanceLease*Noncurrent`)
  - `DebtAndCapitalLeaseObligations`
- **current**, required only when the filing reports a lease-including current fact (`LongTermDebtAndCapitalLeaseObligationsCurrent` / `DebtCurrentAndFinanceLease*` / `LongTermDebtCurrentAndFinanceLease*`): the claim-named current-debt lines (`SHORT_FACE_TAGS` the claim names) sum to at least that value minus rounding. They contain it; IBM's short-term debt adds short-term loans to the current maturities.

Record it in `checks.perimeter` as `{"status": "ok", "resolved_by": "lease_in_debt_by_name"}` or `"lease_in_debt_by_value"`, with the matched fact and value. Then the pass stays evidence-carrying and never silent.

## What it must not do

- Satisfy the perimeter because a debt total merely exceeds the lease figure. Equality with a lease-including element is the evidence, not size.
- Apply to pre-ASC 842 capital leases with no location member. Rule 3 stays as it is: absence is not evidence (CVX 2014-17 keeps its current capital lease flagged READER CHECK in the resolver).
- Change operating leases. They are never debt.

## Test cases (all from the filings above)

1. **IBM FY2022.** Claim `ShortTermBorrowings` 4,760 + `LongTermDebtNoncurrent` 46,189. Note `LongTermDebtAndCapitalLeaseObligations` 46,189, `...Current` 4,751, `FinanceLeaseLiability` 239. Expected: no missing part, resolved_by `lease_in_debt_by_value`.
2. **Same filing, claim long-term debt changed to 46,000.** Expected: `finance_lease` 239 missing. The mutant must fail.
3. **Same filing, claim short-term debt changed to 4,700 (< 4,751 - rounding).** Expected: `finance_lease` missing. The current condition fails.
4. **IBM FY2021, claim naming `LongTermDebtAndCapitalLeaseObligations` 44,917.** Expected: no missing part via L1 (existing behaviour).
5. **A label-only case: face line `LongTermDebtNoncurrent` labelled "Long-term debt, including finance lease obligations".** Expected: L1 by label.

Evidence: the resolver's IBM debt facts come from the standard extract (debt_vals) and the committed instance evidence. The note wording is from the FY2025 R124 and R125 pages on sec.gov, read at 1 request a second.
