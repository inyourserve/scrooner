# Playbook: dividends_per_share_resolved

Method: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows). Rules today: `per_share.dps_tag@1` `CommonStockDividendsPerShareDeclared`, `@2` `CommonStockDividendsPerShareCashPaid` (VERIFY-SPLIT-RELEASE-2 10/10).

## 1. Mapped: 64 of 632 (IS face only: Declared 46, CashPaid 21)

## 2. Where DPS actually sits (latest 10-K)

| Tag | Location | Companies | Mapper |
|---|---|---|---|
| `CommonStockDividendsPerShareDeclared` | **EQ statement, parenthetical** ("Cash dividends declared ($x.xx per share)") | **215** | not read |
| | EQ face | 35 | not read |
| | IS face | 46 | mapped |
| | UN / CF parenthetical | 7 | not read / excluded |
| `CommonStockDividendsPerShareCashPaid` | EQ parenthetical | 70 | not read |
| | EQ face | 9 | not read |
| | IS face | 21 | mapped |

So about 250-300 companies print DPS in a place the mapper does not read (overlaps between rows are not removed).

## 3. Identification ladder
1. IS face Declared / CashPaid (as today).
2. EQ statement or its parenthetical, the same two tags, duration = the fiscal year (`qtrs=4`) or quarter, non-dimensional or the common-class member.
3. Notes (`fsn.value` non-statement reports): quarterly dividend tables, often dimensioned by quarter; use only a non-dimensional value of the right duration.

## 4. Traps
- Declared vs paid differ around year-end and for special dividends; the rule order (declared first) is a definition choice already made.
- Per class: multi-class companies declare per class (`StatementClassOfStockAxis`); take the common/class A member that matches the EPS class.
- Preferred DPS (`PreferredStockDividendsPerShareDeclared`) on the same EQ parenthetical: a different tag, never common.
- Split re-basing applies (VERIFY-SPLIT-RELEASE-2).
- The EQ statement prints three years of rows; match the duration and end date of each column.
