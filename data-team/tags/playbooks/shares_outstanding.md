# Playbook: shares_outstanding_resolved

Card: [`../cards/net-income-and-shares.md`](../cards/net-income-and-shares.md). Method: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows).

## 1. The finding: 18 of 632 mapped, and the mapper cannot see the usual locations

Rule today: `per_share.shares_tag@1` = `CommonStockSharesOutstanding` in `stmt BS`. The mapper skips parentheticals and never reads `EQ` or `CP` (README §1). Where `CommonStockSharesOutstanding` sits in the 632 latest 10-Ks:

| Location (FSN `stmt`, report) | Companies | Mapper status |
|---|---|---|
| BS **parenthetical** report | **407** | `excluded` (parenthetical) |
| Equity statement (`EQ`), shares column | 254 | not read |
| BS face (inside the equity caption) | 18 mapped + 7 excluded | mapped |
| `UN` / `CF` parenthetical / `IS` | ~23 | not read |

Other share counts in the same filings:

| Tag | Location | Companies | Meaning |
|---|---|---|---|
| `dei:EntityCommonStockSharesOutstanding` | cover page (`CP`) | 630 | shares outstanding **at the cover date** (weeks after period end), often **per class** (dimensioned or one row per class) |
| `CommonStockSharesIssued` | BS parenthetical 540, EQ 55, BS face 30 | | **issued**, includes treasury shares |
| `TreasuryStockCommonShares` (also `TreasuryStockShares`) | BS parenthetical 296, EQ 116 | | issued − treasury = outstanding |
| `WeightedAverageNumberOfDilutedSharesOutstanding` | IS 490 (unmapped) | | weighted average for the period, a different concept |

## 2. Identification ladder (strongest first), for the builder

1. `CommonStockSharesOutstanding`, instant at the balance-sheet date (`qtrs=0`, `ddate = period`), non-dimensional, from the **BS parenthetical** (407) or the **BS face** (25). This is the period-end count the balance sheet uses.
2. The same tag at the period-end date in the **equity statement** (254): the closing balance of the shares column. Take the row at `ddate = period` only; the EQ statement also prints opening balances.
3. Derived: `CommonStockSharesIssued` − `TreasuryStockCommonShares` (or `TreasuryStockShares`), both at the period date from the same parenthetical. A derivation; label it so.
4. Cover `dei:EntityCommonStockSharesOutstanding`: **a different date** (the cover date). Acceptable only as a separately labelled "as of <date>" value, never as the period-end cell.

## 3. Traps
- **Multi-class companies** (GOOGL, BRK, META-style A/B, Up-C class A/B): the parenthetical carries one value per class, either with a `StatementClassOfStockAxis` member (`dim_id ≠ 0`) or with custom per-class tags. A non-dimensional value may be one class only or absent. Total shares = sum over classes. The economic count (B converted to A at a ratio) is a Standardization Lead question.
- Split re-basing: share counts before a split in older filings must be re-based (`share_basis.TARGETS`, VERIFY-SPLIT-RELEASE).
- Units vs shares: partnerships report units (`LimitedPartnersCapitalAccountUnitsOutstanding`).
- Issued ≠ outstanding whenever treasury stock exists (296 companies print treasury shares).

## 4. Ask for the mapping builder
Read `inpth` lines of the BS report for `CommonStockSharesOutstanding` only (a narrow exception to the parenthetical exclusion), then fall back to the EQ statement's period-end row. On this measurement that moves the reachable set from 18 to roughly 430 (407 + 25, overlap not removed), before the EQ fallback. Not yet measured: how many of the 407 are dimensioned per class.
