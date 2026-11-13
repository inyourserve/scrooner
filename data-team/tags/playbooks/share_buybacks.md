# Playbook: share_buybacks_resolved

Method: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows). Rule today: `cf.buybacks_common_tag@1` = `PaymentsForRepurchaseOfCommonStock` only (VERIFY-BUYBACKS-RUN3 20/20, R2 6/6, founder perimeter ruling). The cash-flow lane's replay (`cf_family_replay.py`) sums printed common buyback lines and excludes tax-withholding lines.

## 1. Mapped: 490 of 632, all `PaymentsForRepurchaseOfCommonStock` on the CF face

## 2. Unmapped buyback-shaped CF lines (whole 632, latest 10-K)

| Rank | Tag | Companies | Labels seen | Read |
|---|---|---|---|---|
| 1 | `PaymentsForRepurchaseOfEquity` | 10 (+6 in filings with no line_map) | "Treasury stock purchased" (89800), "Stock repurchase program" (87347), "Share repurchase" (315293), "Company stock purchases (Note 8)" (66570), "Repurchase of stock - open market" (824142), "Repurchases of common stock" (882184), "Purchases of treasury stock" (898174), "Purchase of treasury stock" (1001316), "Share repurchases" (1681459) | the broader us-gaap element (any equity class). **In 13 of 16 filings it coexists with a `PaymentsForRepurchaseOfCommonStock` line**, so it is often a second buyback line (open-market vs. accelerated, or vs. withholding). Summing both may be right or a double count: per-filing calc check needed |
| 2 | custom buyback tags (one company each) | ~8 | `PaymentsForRepurchaseOfCommonStockIncludingExciseTax` (1280452), `RepurchasesOfCommonStockIncludingExciseTax` (897723), `PaymentsForRepurchaseOfCommonStockIncludingSharesSurrendered` (12659, H&R Block), `PaymentsforRepurchaseofCommonStockintheOpenMarket` (80661, PGR), `PaymentsForPurchasesOfTreasuryStock` (315852), `ShareRepurchasesFinancingActivities` (215466), `PaymentsForRepurchaseOfShares` (1851003), `NetPaymentsForRepurchaseOfCommonStock` (763901, "net": perimeter) | extensions standing for the standard line; the "IncludingExciseTax" pair is a 2023+ pattern (1% IRA excise tax) |
| 3 | `PaymentsRelatedToTaxWithholdingForShareBasedCompensation` | 1 labelled as repurchase (1479094 "Repurchase and retirement of share-based compensation") | | withholding: excluded by the founder's perimeter ruling |

## 3. Structural signature (independent of the tag)
A CF line in the **financing** block (calc child of `NetCashProvidedByUsedInFinancingActivities`, weight −1 as an outflow), label matching `repurchase|buyback|purchase of (treasury|common) (stock|shares)|treasury stock (purchased|acquired)` and NOT matching `debt|notes|senior|preferred|noncontrolling|withholding|tax(es)? paid|units` (partnership units: separate perimeter), `crdr = C` on a `Payments...` tag. Value positive in FSN (the outflow sign is carried by the calc weight).

## 4. Candidates (not approved)
1. `PaymentsForRepurchaseOfEquity` when it is the **only** buyback line in the financing block, with a label that names common/treasury stock: 3 of 16 here (1001316, 1336920 "Repurchases of stock and other" (perimeter: "and other"), 1375365, value 0). When it coexists with the common tag, the Tag Mapper must check the filing's calc: two siblings under financing = sum; a parent-child pair = take the parent.
2. Custom `...IncludingExciseTax` / `...InTheOpenMarket` / `PaymentsForPurchasesOfTreasuryStock` / `ShareRepurchasesFinancingActivities` as the sole buyback line (signature above). Excise-inclusive amounts are about 1% higher than the share cost; a perimeter note, not a different concept (founder ruling needed if the 1% matters).

## 5. Traps
- Repo lines: `ProceedsFromPaymentsForSecuritiesSoldUnderAgreementsToRepurchase`, `IncreaseDecreaseInPayablesUnderRepurchaseAgreements`, "repurchase facilities" at mortgage REITs and banks (NLY, AGNC, MS, GBCI): **financing borrowings**, not buybacks. A label regex on "repurchase" alone catches them.
- Partnership "repurchase of units" (2030781) and NCI repurchases (`PaymentsForRepurchaseOfRedeemableNoncontrollingInterest`) are not common buybacks.
- `TreasuryStockRetiredCostMethodAmount` and noncash treasury lines in the supplemental block (2012383, PG&E 1004980) are not cash buybacks.
- A printed 0 in the latest copy is served as 0 (Dhairya's ruling, NOW.md).
