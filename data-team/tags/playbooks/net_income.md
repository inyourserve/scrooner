# Playbook: net_income_resolved (net income attributable to the parent)

Card: [`../cards/net-income-and-shares.md`](../cards/net-income-and-shares.md). Method: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows).

## 1. Mapped (`is.net_income_line@1`): 569 of 632, all `NetIncomeLoss`

## 2. The 63 gap companies

| Class | Companies | Pattern | Example (accession R line, FY value from `fsn.value`) |
|---|---|---|---|
| A. `NetIncomeLossAvailableToCommonStockholdersBasic` (NIACSB) is the parent bottom line, **no preferred-dividend or participating-securities line on the face** | **30** (20 also print `ProfitLoss` + an NCI line; 8 print NIACSB with an NCI line but no `ProfitLoss`; 2 others) | the filer tags its "Net income attributable to X" line with the available-to-common tag | Caterpillar 0000018230-26-000008 R3: l24 `ProfitLoss` "Profit of consolidated and affiliated companies" 8,882M; l25 NCI −2M; **l26 NIACSB "Profit (loss)" 8,884M** = 8,882 − (−2). Eversource 0001628280-26-008461 R5: l17 `ProfitLoss` 1,699.9M; l18 NCI 7.519M; l19 NIACSB "Net Income/(Loss) Attributable to Common Shareholders" 1,692.4M (= 1,699.9 − 7.5). CIKs: 18230 26172 37996 49600 51253 70318 72741 76334 740260 766704 920522 1001250 1001838 1020569 1108426 1109357 1289460 1298675 1324404 1415404 42888 352541 723531 750577 795403 891103 1075531 1823529 717605 831259 |
| B. NIACSB **with** a preferred / participating line on the face | 11 | NIACSB is after preferred dividends: **not** NI to parent | CIKs 92230 720672 783325 885725 895417 912593 914208 1004980 1013871 1063761 1562401 |
| C. `ProfitLoss` is the bottom line, no NIACSB and no `NetIncomeLoss` | 18 | either no NCI exists (then ProfitLoss = NI to parent), or the parent line is custom | ITW 0000049826-26-000008 R3 l10 `ProfitLoss` "Net Income" 3,066M (no NCI line); Terex 0000097216-26-000035 R3 l14 `ProfitLoss` "Net income (loss)" 221M. CIKs incl. 49826 97216 66570 94845 842023 878927 927003 1014473 1065696 (LKQ: custom `NetIncomeAttributableToLKQStockholders`) 1141391 1403161 1489393 (custom) 1571123 1664703 (custom) 1730168 775158 1289419 794367 |
| D. Statement-class trap | 2 | GATX (IS in `CI`), Revvity (IS in `UN`) | README §2 |
| other | 2 | 22444 (no NI-family line on the IS face); 713676 (`ProfitLoss` + preferred + custom `NetIncomeLossAvailableToCommonStockholders`) | |

## 3. Candidates (not approved)
1. **NIACSB as net income to parent** when (a) the filing prints no `NetIncomeLoss` on the IS face, (b) no line tagged `PreferredStockDividendsIncomeStatementImpact`, `DividendsPreferredStock*`, `PreferredStockRedemptionPremium`, `NetIncomeLossAvailableToCommonStockholdersDiluted` adjustment, `...ParticipatingSecurities...` or `UndistributedEarnings...` sits between it and the NCI line, and (c) where `ProfitLoss` and an NCI line are printed, NIACSB = `ProfitLoss` − NCI to the unit (an identity check the builder can run on the stored values; CAT and ES pass it). 30 companies. It is a mis-tag at the filer, so the identity check is the proof per filing, not the tag name.
2. **`ProfitLoss` as net income to parent** only when the filing has no NCI line at all on the face (no `NetIncomeLossAttributableToNoncontrollingInterest`, `...RedeemableNoncontrollingInterest`, `MinorityInterest...`) **and** the BS shows no NCI equity (`MinorityInterest` absent or 0). ITW and Terex look like this (FSN rows); needs a filing check.
3. Custom "Net income attributable to <Company> stockholders" tags (LKQ, 1489393, 1664703): the structural signature is the line after `ProfitLoss` minus the NCI line, with calc parent `ProfitLoss` weight +1 and an NCI sibling weight −1 (or the identity above).

## 4. Traps
- NCI sign: Caterpillar's NCI line is −2M (a loss attributable to NCI) and NI to parent is the larger number. Never assume NI ≤ ProfitLoss.
- Discontinued operations: `NetIncomeLoss` includes them; `IncomeLossFromContinuingOperations` (TFC prints it) does not.
- Partnerships: `NetIncomeLossAllocatedToLimitedPartners` / `...GeneralPartners` (1063761) are allocations of NI, not NI.
- Two-class EPS filers: NIACSB can be after the allocation to participating securities.
