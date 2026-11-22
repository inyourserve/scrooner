# Card family: share buybacks, dividends paid, dividends per share, CFO basis (written 2026-11-09 by the Tag Expert)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Tags: `us-gaap:PaymentsForRepurchaseOfCommonStock`, `PaymentsForRepurchaseOfEquity`, `PaymentsRelatedToTaxWithholdingForShareBasedCompensation`, `PaymentsForRepurchaseOfRedeemablePreferredStock`, `StockRepurchasedDuringPeriodValue`; `PaymentsOfDividends`, `PaymentsOfDividendsCommonStock`, `PaymentsOfOrdinaryDividends`, `PaymentsOfCapitalDistribution`, `PaymentsOfDividendsMinorityInterest`; `CommonStockDividendsPerShareDeclared`, `CommonStockDividendsPerShareCashPaid`; `NetCashProvidedByUsedInOperatingActivities(ContinuingOperations)`.
Playbooks with FSN-store counts: [`../playbooks/share_buybacks.md`](../playbooks/share_buybacks.md), [`../playbooks/dividends_paid.md`](../playbooks/dividends_paid.md), [`../playbooks/dividends_per_share.md`](../playbooks/dividends_per_share.md). This first version is assembled from relays (FILING-CHECKED by the named role, not re-opened by me: sec.gov refuses this cloud session) plus my FSN measurements (DATA-INFERRED). Official-definition section: to be added from the FASB schema next run.

## 1. Buybacks
- FSN write rule: `PaymentsForRepurchaseOfCommonStock` only (490 of 632 latest 10-Ks). Perimeter (founder ruling, VERIFY-BUYBACKS-R2): common open-market and accelerated repurchases; withholding excluded.
- **Exclusions, FILING-CHECKED (cash-flow lane, Verifier):** lines tagged or labelled tax withholding on share settlement (`PaymentsRelatedToTaxWithholdingForShareBasedCompensation`; INSW "Cash paid to tax authority…"), and preferred redemptions (`PaymentsForRepurchaseOfRedeemablePreferredStock`, KHC "Redemption of Series A Preferred"). These lines give the cell a reason (`only_excluded_lines_presented`), never a value. An unnamed share-purchase line is `unclassified_share_line` (held). Classifier: `pilot.classify_filing` / `cf_family_replay.buyback_class`.
- **A printed 0 is a value**: Brixmor's FY2017/FY2018 10-Ks print a separate "Repurchase(s) of common shares" line valued 0; it is the common buyback line, served as 0 (Dhairya's ruling 2026-11-08; the cash-flow lane withdrew its earlier "combined/held" reading).
- **An absent row in a year without repurchases means zero activity**, shown by a later 0 comparative: CMI's FY2023-25 10-K has no repurchase row and later 10-Qs carry the period as 0 (0000026172-26-000009 R6; Period Engineer).
- **Non-standard durations**: AZO 10-Q files cumulative program-to-date repurchases (1998-01-01..2015-05-09, 14,872M) on the same tag beside the 9M value (0001193125-15-225958; Data Verifier, DATA-INFERRED). Filter by duration.
- `StockRepurchasedDuringPeriodValue` is an equity-statement tag. AMD's Q2 10-Q equity statements carry the YTD amount on the 3-month context (241 Q2 2023, 221 Q2 2026; 0000002488-23-000139 R7). Never a buyback fallback without a duration check (Data Verifier).
- FSN-store leads (DATA-INFERRED): `PaymentsForRepurchaseOfEquity` on 16 latest 10-K CF faces, coexisting with the common tag in 13 of them; custom sole-line tags (excise-inclusive, open-market). See the playbook.

## 2. Dividends paid
- FSN write rule: `PaymentsOfDividends`, `PaymentsOfDividendsCommonStock`, `PaymentsOfOrdinaryDividends` (455 of 632).
- `PaymentsOfOrdinaryDividends` is the main cash-dividend tag at PFE ("Cash dividends paid" 4,896M, 6M 2026, 0000078003-26-000095 R8), JNJ (since 2007) and CL (since 2009). The old mapper missed it; the FSN rule includes it (Standardization Lead).
- **The generic `PaymentsOfDividends` is not evidence of a COMMON dividend**: BPOP Q1 2015 files 620K (preferred) before its first common dividend; WYNN Q1 2021 files 295K while the common dividend was suspended; TDG FY2016 files 3M (dividend equivalents) beside CashPaid 0 (Period Engineer, DATA-INFERRED). For the FSN write: a small `PaymentsOfDividends` value with no common DPS in the same period is a preferred or equivalents payment; hold it or give a reason.
- dividend_class (cash-flow lane): "dividends and dividend equivalents" = common (founder ruling 2026-11-01, AAPL); "dividends and distributions" = combined (held); "not paid"/"unpaid" = excluded_noncash; preferred and NCI lines excluded.
- FSN-store lead: `PaymentsOfCapitalDistribution` is a mixed perimeter (common REIT distributions, but also Up-C member and parent payments). See the playbook.

## 3. Dividends per share (declared vs paid)
- **The quarterly rate tagged on annual or YTD contexts**: Visa (FY2015-FY2026, 0001403161-25-000089 R8: FY context 0.59 = one quarter; the Verifier relay reads 0.52 labelled "quarterly"), NVDA FY2016 (0001045810-16-000205 R58), LEA (0000842162-26-000011, FY 0.77), WTRG (0.3255 Declared on FY2024 while CashPaid is 1.2652) (Data Verifier, Period Engineer). Derived Q4 then goes negative; FY DPS shows one quarter.
- **Guard (Standardization Lead correction of ledger row 71)**: "FY ≥ each filed quarter" does not catch Visa when the rate is unchanged all year. The test that works for any rate history: the FY value must equal the sum of the filed quarters (or CashPaid FY / PaymentsOfDividendsCommonStock ÷ shares within tolerance).
- **LEA's negative DPS values are OURS, not filed** (Data Chief, SEC companyconcept, correcting a 2026-10-25 relay): -0.50/-0.60 = FY-context 0.25 minus 9M 0.75. LEA has no negative filed DPS fact.
- Lumpy declarations: CAT declares two dividends in some quarters (Q2 2025 3M = 6M = 2.92; Q3 0.00; Q4 3.02; FY 5.94). AMGN tags the quarter as the latest declaration but its FY2025 10-K files Q4 2025 = 2.38 against its own December 2.52 (FY 9.66). DCI FY2015 files Q4 declared 0.34 (later 0.175). LMT Q2 2016 declared 3.30 = two declarations. So **"per-share equal on 3M and YTD = a rate" misfires on declared DPS**.
- Other filer misuse: OGE tags the annual 1.505 on Q1 2020; OHI files -0.66 in its FY2019 10-K; BWA files 0 for FY2019 with 140M paid; COP 10-Qs re-file Q3 2021 Declared as the FY figure on a 9M context (CashPaid is consistent). Cross-check Declared against CashPaid and `PaymentsOfDividendsCommonStock` in the same filing.
- **One basis per company** (AC-24 default): Declared and CashPaid are different bases (declared quarter vs paid quarter: LMT, AMT, CVI, CWEN, AES); 240 of 681 cohort companies had mixed series. Use the tag with more filed quarters since 2015; on a tie, Declared.
- FSN-store finding: Declared sits on the EQ statement or its parenthetical at about 250 companies, which the mapper never reads (playbook).

## 4. CFO basis
- **`...ContinuingOperations` vs the total**: the old first_match could switch a series between bases period by period (AMD 9M 2025 CFO 5,109 including 920 discontinued) (Standardization Lead). **FSN-store finding (DATA-INFERRED): 16 latest 10-Ks print both with different values, and both are mapped, so select blanks CFO as `conflicting_values_in_filing`** (e.g. 2488 0000002488-26-000018 R8 l18 6,493M vs l20 7,709M; 773840 6,075M vs 6,408M). **FILING-CHECKED 2026-11-09**: AMD 0000002488-26-000018 R8 prints "Cash Provided by (Used in) Operating Activity, Continuing Operation" 6,493 + "…Discontinued Operation" 1,216 = "…Including Discontinued Operation, Total" 7,709 (FY2025). Rule implied by the cases: the continuing tag counts only when no total is printed. Sent to the mapping builder and the cash-flow lane 2026-11-09.
- **FX twin (cash-flow lane, FILING-CHECKED)**: CSCO prints the exchange-rate effect as two lines under the net-change total (both `EffectOfExchangeRateOnCash…` family, calc children of the net change). FX = the signed sum of every FX-family calc child (CSCO FY2025 10-K R8: 14,193 + 1,733 − 15,815 = 111; 111 − 43 = 68). RTX's single-line shape is unchanged.
- **An 8-K can carry another entity's statements**: WTRG's 8-K 0001193125-26-124163 tags American Water's full statements under WTRG's CIK (merger Ex. 99.1), and the old pipeline took WTRG's FY CFO, capex and NI from it (Period Engineer). The FSN write reads 10-K/10-Q forms only (`FACE_QTRS`): safe.

## 5. Mapping verdicts
- `PaymentsForRepurchaseOfCommonStock`: safe common buyback line on the CF face (Verifier 20/20 + 6/6), with the duration filter (AZO) and the exclusions above.
- `PaymentsOfDividendsCommonStock`, `PaymentsOfOrdinaryDividends`: safe common cash dividends (PFE FILING-CHECKED). `PaymentsOfDividends`: common only when no separate preferred line exists and a common DPS exists in the period.
- `CommonStockDividendsPerShareDeclared` / `CashPaid`: safe only per company basis, with the FY = sum-of-quarters guard; never derive across bases.
- `PaymentsForRepurchaseOfEquity`, `PaymentsOfCapitalDistribution`: never as single tags; per-filing label and calc check (playbooks).

## 6. Folded in from the FSN-expert per-tag cards (2026-11-10)
- **`NetCashProvidedByUsedInOperatingActivitiesContinuingOperations` is the ONLY CFO line at many filers with no discontinued operations**: 60 top-100 names, 997 face lines (the total tag: 130 names, 5,218 lines); MSFT Q2 FY2014 0001193125-14-018634 … Q1 FY2018, label "Net cash from operations". The investing/financing `…ContinuingOperations` siblings follow the same era. Rule (agrees with §4): CFO from it only when no total line is printed; never sum the two.
- **FX on the cash flow has four sibling tags**: `EffectOfExchangeRateOnCashAndCashEquivalents` (pre-ASU 2016-18), `…RestrictedCashAndRestrictedCashEquivalents` (post), `…IncludingDisposalGroupAndDiscontinuedOperations` (19 top-100 names incl. ABT, AMZN, GE, GS, MSFT from the FY2022 10-K 0001564590-22-026876, AMZN 2024, PLD, QCOM, TSLA, TMO, DIS), and the near-twin `…DisposalGroupIncludingDiscontinuedOperations` (CSCO, RTX). The label rarely says "disposal group". `fsn_store/checks.py` CF_FX listed only the two older ones, so MSFT FY2020-26 CFO, dividends and buybacks failed the cash identity (22 cells each, pilot run 41490670432). PR #4 adds the IncludingDisposalGroup tag; the CSCO case needs the twin, as the cash-flow lane found (FX = the signed sum of every FX-family calc child of the net change; FSN-expert P-1).
- MSFT `msft:GainLossOnInvestmentsAndDerivativeInstruments` is stored as a gain (−2,136M) and printed negated "Net recognized losses (gains)" 2,136M (10-Q 0001193125-26-027207 R6).

## 7. Engineering relay 2026-11-11 (fsn.pre query, DATA-INFERRED; MDT FILING-CHECKED)
- Of 534 companies that print DPS on a statement line: 139 STOPPED printing it on the IS, 42 never did; 225 print it on EQ, 14 on UN, 3 on CI. MDT moved it to the EQ parenthetical from the FY2019 10-K (checked 2026-11-10). So DPS needs EQ (face and parenthetical) read, era by era.
- Toll Brothers: a PRINTED 0 for gross interest (FY2015-2019, interest fully capitalised) is a real value per Engineering. **Open conflict**: `select`'s note fill holds a note value ≤ 0 with a reason (Verifier draw 2026-11-03: TOL "Directly expensed interest" 0). Proposed resolution: a 0 PRINTED on the face (or in the interest note under a label that reads as interest expense, with a capitalisation disclosure) is a value; a 0 on a sole `InterestExpenseDebt` note fact without such a label stays held. Needs the Verifier's filing check of TOL before the rule changes (interest.md §7).

## 8. Cash-flow lane relay 2026-11-11 (FC = FILING-CHECKED by the Verifier, DI = DATA-INFERRED; CF-PERSHARE-PORT-2026-11-01, CF-GAPS-2026-11-02 on work/cashflow/fsn-gaps-rebased ce7f19ab)
- **DPS one series (FC)**: CFG FY2017 10-K 0000759944-18-000016: Declared 0.18 on a 12-month context = the Q4 declared amount; CashPaid FY 0.64 beside it; mixing tags for Q4 = FY − 9M gave −0.28. Rules: both DPS inputs from ONE tag series; a negative Q4 is never shown; a FY DPS below its own 9M is impossible: hold it (the Declared-first order would serve 0.18 as FY).
- Instant shares are never derived; copies disagreeing by > 0.005 are hidden.
- **CF identity (DI)**: FX lines = `EffectOfExchangeRateOn…{,IncludingDisposalGroupAndDiscontinuedOperations,ContinuingOperations}` and `EffectOfExchangeRateOnCash`; `NetCashProvidedByUsedInDiscontinuedOperations` must enter the identity; inputs = the primary registrant's coreg = '' and iprx = 0 copy (GE `SubsidiariesGecc` sits in coreg); a calc parent can have several calc groups in one filing: the check passes if ANY group ties; a group listing both ProfitLoss and NetIncomeLoss ties with either.
- **Buybacks (FC)**: EMR FY2024 435M excludes the AspenTech (subsidiary) repurchase line; ROST FY2019 several repurchase lines → held; LDOS FY2020 combined → held; GPN FY2022 2,921,307K. Brixmor FY2017/2018 printed 0 = the common line (FY2015/16 print only the equity-award line → excluded).
- Waters 10-Q 0001193125-26-344691 R6: "Purchases of treasury shares" and no dividend line = a reasoned absent dividend line (FC). SO FY2024 CFO 9,788M; GM Q1 2016 CFO −164M (FC). A printed-zero YTD pair (6M = 0, 9M = 0) gives a 0 quarter with no basis witness (Somnigroup Q2/Q3 2020; Dhairya ruling).
## 9. FSN-expert relay part 2 (cash flow; DATA-INFERRED)
- `InterestPaid` (gross) vs `InterestPaidNet` (net of capitalised): JNJ 10-K 0000200406-16-000071 R8 prints both (617 vs 515M), cal InterestPaid ← InterestPaidNet; 35 filings print both: prefer the net tag, never sum (confirmed by DQC_0065, interest.md §10). `IncomeTaxesPaid` (27 → 14 cos) vs `IncomeTaxesPaidNet` (35 → 45): overlapping labels; the ASU 2023-09 disaggregation era starts 2025. Both are supplemental, never expense. **Superseded 2026-11-12: the gross/net reading is filer-specific (XOM 0000034088-26-000045 R109: InterestPaidNet = operating portion 218M vs InterestPaid 1,752M total); read the label, never "prefer the net tag".**
- Acquisitions: `PaymentsToAcquireBusinessesNetOfCashAcquired` (96 names); `PaymentsToAcquireBusinessesAndInterestInAffiliates` (18; PEP, UTX) includes investments; `…Gross` at 5. Asset sales: `ProceedsFromSaleOfPropertyPlantAndEquipment` (43) vs `ProceedsFromSaleOfProductiveAssets` (18; may include businesses; MCD prints both).
- Debt flows: `ProceedsFromIssuanceOfDebt` can be the calc PARENT of `…SeniorLongTermDebt`/`…LongTermDebt`/`…CommercialPaper`: never sum a parent with its children. "Repayments of short-term debt, net" is the label on `ProceedsFromRepaymentsOfCommercialPaper` 21 times.
- `IncomeLossFromEquityMethodInvestments` is an IS line at 39 names and a CF adjustment at some; the CF twin `…NetOfDividendsOrDistributions` (T, KO) nets dividends received.

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.

## 10. Ritwik (cloud) card notes 15, 19, 23, 26, 30 (DATA-INFERRED)
- Combined (blank with reason): AXP "Repurchase of … common shares and other" with preferred redemptions (0000004962-22-000008 l28, 30); BLK 2025+ Subco exchangeable-unit lines (0001193125-26-071966 l35, 37; mapped only from the equity note's common-only amount); SPG/TRGP "dividends to common and preferred"; KMI "shares and warrants"; SPG LP-unit + treasury; BX "net settlement of vested … and repurchase".
- Filer tag errors (map by label and position, flag): CME 2025-26 Class A repurchase tagged `PaymentsForProceedsFromDerivativeInstrumentFinancingActivities`; KMI, AON buybacks tagged `ProceedsFromRepurchaseOfEquity` (sign check).
- MLPs: EPS = per common unit (EPD, ET, KKR to 2018); distributions to common unitholders = the dividend line (ET open).

## 11. Annual DPS from printed quarters (Dhairya ruling 2026-11-12)
- When a 10-K prints only quarterly DPS, annual DPS = the sum of the FOUR quarterly facts printed in that same filing (declared, or paid if only paid is printed), served with the note "sum of printed quarterly dividends". Conditions: all four quarters in the one filing; one basis; each fact on its own 3-month or dated-payment context (a quarterly rate on a 12-month context, as at CFG, V, NVDA, is not a quarterly fact); no special dividend unless printed as such. Otherwise not_presented. Cases: C 2.32 (0.56 + 0.56 + 0.60 + 0.60), COF, CRM 1.664 (4 × 0.416), DIS (dated payments in the fiscal year). DPS is additive; EPS is never derived.

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 23 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `NetIncomeLoss`
- **Meaning:** Net Income (Loss) Attributable to Parent (us-gaap, duration, credit). The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income; role net_income:primary#1
- **Rules:** X77; C29; resolver functions resolve
- **Evidence:** 105 companies, 1212 served, 28185 proven, 106 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InvestmentCompanyNetAssetsFromOperationsIncreaseDecrease@2023; RestatementOfPriorYearIncomeNetOfTax@2020

### `NetCashProvidedByUsedInOperatingActivities`
- **Meaning:** Cash Provided by (Used in) Operating Activity, Including Discontinued Operation (us-gaap, duration). Amount of cash inflow (outflow) from operating activity, including, but not limited to, discontinued operation. Operating activity includes, but is not limited to, transaction, adjustment, and change in value not defined as investing or fin...
- **Data point definition:** cfo: Net cash provided by (used in) operating activities as printed.
- **Data point:** cfo; polarity cfo:signed; role cfo:primary#1
- **Rules:** X84
- **Evidence:** 110 companies, 1154 served, 40731 proven, 115 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `PaymentsForRepurchaseOfCommonStock`
- **Meaning:** Payments for Repurchase of Common Stock (us-gaap, duration, credit). The cash outflow to reacquire common stock during the period.
- **Data point definition:** share_buybacks: Cash repurchases of the company's own common stock;  excludes tax-withholding shares, excise tax, employee-plan purchases, subsidiary buybacks and swaps (founder 2026-11-04).
- **Data point:** share_buybacks; polarity share_buybacks:positive; role share_buybacks:primary#1
- **Rules:** K10; K11; K12; K13; K14; K15; K16; resolver functions resolve_cf; family resolve_all.NARROW[share_buybacks]
- **Evidence:** 106 companies, 1118 served, 29887 proven, 108 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 1 open hit(s) at 1 companies, e.g. AXP share_buybacks 2018-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (1)

### `InterestPaidNet`
- **Meaning:** Interest Paid, Excluding Capitalized Interest, Operating Activity (us-gaap, duration, credit). Amount of cash paid for interest, excluding capitalized interest, classified as operating activity. Includes, but is not limited to, payment to settle zero-coupon bond for accreted interest of debt discount and debt instrument with insignif...
- **Data point definition:** cash_paid_for_interest: Cash paid for interest, net of amounts capitalized (InterestPaidNet).
- **Data point:** cash_paid_for_interest; polarity cash_paid_for_interest:positive; role cash_paid_for_interest:primary#1
- **Rules:** K35
- **Evidence:** 98 companies, 883 served, 1627 proven, 69 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `IncomeTaxesPaidNet`
- **Meaning:** Income Tax Paid, after Refund Received (us-gaap, duration, credit). Amount, after refund, of cash paid to foreign, federal, state, and local jurisdictions as income tax.
- **Data point definition:** cash_paid_for_income_taxes: Cash paid for income taxes, net of refunds, as printed.
- **Data point:** cash_paid_for_income_taxes; polarity cash_paid_for_income_taxes:signed; role cash_paid_for_income_taxes:primary#1
- **Rules:** K32; K34; K33
- **Evidence:** 105 companies, 866 served, 1547 proven, 70 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000040545-17-000010: GE FY2016 10-K R7.htm statement of cash flows: Cash recovered (paid) during the year for income taxes (7,469): 7,469 paid;  IncomeTaxesPaidNet is positive for ta; filer XBRL error 0000040545-16-000145: GE FY2016 10-K R7.htm (0000040545-17-000010) prints the FY2015 column: Cash recovered (paid) during the year for income taxes (2,486): 2,486 paid;  the FY2015 10 (+2 more)
- **Pattern hits:** none

### `CommonStockDividendsPerShareDeclared`
- **Meaning:** Common Stock, Dividends, Per Share, Declared (us-gaap, duration). Aggregate dividends declared during the period for each share of common stock outstanding.
- **Data point definition:** dividends_per_share: Dividends declared per common share for the fiscal year.
- **Data point:** dividends_per_share; polarity dividends_per_share:positive; role dividends_per_share:primary#1
- **Rules:** none
- **Evidence:** 81 companies, 767 served, 2489 proven, 96 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0001137789-24-000068: STX FY2024 10-K stx-20240628.htm consolidated statements of shareholders' equity: Dividends to shareholders ($ 2.80 per ordinary share);  the XBRL facts are 10^6; filer XBRL error 0001137789-24-000068: STX FY2024 10-K stx-20240628.htm R9 consolidated statements of shareholders' equity, FY2022 column: Dividends to shareholders ($ 2.77 per ordinary share);  the X (+1 more)
- **Pattern hits:** none
- **Deprecation:** replaces DividendDeclaredMember@2025

### `PaymentsOfDividendsCommonStock`
- **Meaning:** Payments of Ordinary Dividends, Common Stock (us-gaap, duration, credit). Amount of cash outflow in the form of ordinary dividends to common shareholders of the parent entity.
- **Data point definition:** dividends_paid: Cash dividends paid to common shareholders.
- **Data point:** dividends_paid; polarity dividends_paid:positive; role dividends_paid:primary#1
- **Rules:** K23; K17; K18; K19; K20; K21; K22; resolver functions apply_note_split; family resolve_all.NARROW[dividends_paid]
- **Evidence:** 49 companies, 519 served, 18541 proven, 49 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `PaymentsOfDividends`
- **Meaning:** Payments of Dividends (us-gaap, duration, credit). Cash outflow in the form of capital distributions and dividends to common shareholders, preferred shareholders and noncontrolling interests.
- **Data point definition:** dividends_paid: Cash dividends paid to common shareholders.
- **Data point:** dividends_paid; polarity dividends_paid:positive; role dividends_paid:primary#2
- **Rules:** K17; K18; K19; K20; K21; K22; K23
- **Evidence:** 50 companies, 455 served, 11139 proven, 51 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces DividendPaymentRestrictionsScheduleAmountsPaid@2013

### `IncomeTaxesPaid`
- **Meaning:** Income Tax Paid, before Refund Received (us-gaap, duration, credit). Amount, before refund, of cash paid to foreign, federal, state, and local jurisdictions as income tax.
- **Data point definition:** cash_paid_for_income_taxes: Cash paid for income taxes, net of refunds, as printed.
- **Data point:** cash_paid_for_income_taxes; polarity cash_paid_for_income_taxes:signed; role cash_paid_for_income_taxes:primary#2
- **Rules:** K32; K33; K34
- **Evidence:** 47 companies, 429 served, 497 proven, 46 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestPaid`
- **Meaning:** Interest Paid, Including Capitalized Interest, Operating and Investing Activities (us-gaap, duration, credit). Amount of cash paid for interest, including, but not limited to, capitalized interest and payment to settle zero-coupon bond attributable to accreted interest of debt discount and debt instrument with insignificant coupon interest rate in r...
- **Data point definition:** cash_paid_for_interest: Cash paid for interest, net of amounts capitalized (InterestPaidNet).
- **Data point:** cash_paid_for_interest; polarity cash_paid_for_interest:positive; role cash_paid_for_interest:primary#2
- **Rules:** K35
- **Evidence:** 61 companies, 336 served, 313 proven, 46 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CommonStockDividendsPerShareCashPaid`
- **Meaning:** Common Stock, Dividends, Per Share, Cash Paid (us-gaap, duration). Aggregate dividends paid during the period for each share of common stock outstanding.
- **Data point definition:** dividends_per_share: Dividends declared per common share for the fiscal year.
- **Data point:** dividends_per_share; polarity dividends_per_share:positive; role dividends_per_share:primary#2
- **Rules:** none
- **Evidence:** 28 companies, 238 served, 787 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations`
- **Meaning:** Cash Provided by (Used in) Operating Activity, Continuing Operation (us-gaap, duration). Amount of cash inflow (outflow) from operating activity attributable to continuing operation. Operating activity includes, but is not limited to, transaction, adjustment, and change in value not defined as investing or financing activity.
- **Data point definition:** cfo: Net cash provided by (used in) operating activities as printed.
- **Data point:** cfo; polarity cfo:signed; role cfo:primary#2
- **Rules:** none
- **Evidence:** 40 companies, 156 served, 2874 proven, 2 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `LongTermDebt`
- **Meaning:** Long-Term Debt (us-gaap, instant, credit). Amount, after deduction of unamortized premium (discount) and debt issuance cost, of long-term debt. Excludes lease obligation.
- **Data point definition:** total_debt: Total debt: short- and long-term borrowings incl. current portion, commercial paper, finance and capital leases (face or notes), financing obligations and failed sale-leasebacks;  excludes operating leases and accrued interest. (+1 more)
- **Data point:** total_debt; total_liabilities
- **Rules:** D11; resolver functions run
- **Evidence:** 15 companies, 119 served, 68 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseLongTermDebt@2021; NonRecourseDebt@2022; PostconfirmationLongTermDebt@2021; PreconfirmationLongTermDebt@2021

### `InterestExpenseDebt`
- **Meaning:** Interest Expense, Debt (us-gaap, duration, debit). Amount of the cost of borrowed funds accounted for as interest expense for debt.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** interest_expense; other_income_expense_net; polarity interest_expense:positive; role interest_expense:primary#3
- **Rules:** I20; I21; I22; I23; I24; family resolve_all.NARROW[interest_expense]
- **Evidence:** 10 companies, 113 served, 1434 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces DebtInstrumentConvertibleInterestExpense@2013

### `IncomeLossFromEquityMethodInvestments`
- **Meaning:** Income (Loss) from Equity Method Investments (us-gaap, duration, credit). Amount of income (loss) for proportionate share of equity method investee's income (loss).
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** operating_expenses; other_income_expense_net
- **Rules:** none
- **Evidence:** 13 companies, 82 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** filer XBRL error 0001562762-20-000064: T FY2019 10-K t-20191231.htm consolidated statements of income: Equity in net income (loss) of affiliates 6 (2018: (48));  the XBRL fact is -6 and the printed to
- **Pattern hits:** none
- **Deprecation:** replaces IncomeLossFromEquityMethodInvestmentsMember@2013; MinorityInterestAndEarningsLossesEquityInvestmentsMember@2013

### `PaymentsOfOrdinaryDividends`
- **Meaning:** Payments of Ordinary Dividends (us-gaap, duration, credit). Cash outflow in the form of ordinary dividends to common shareholders, preferred shareholders and noncontrolling interests, generally out of earnings.
- **Data point definition:** dividends_paid: Cash dividends paid to common shareholders.
- **Data point:** dividends_paid; polarity dividends_paid:positive; role dividends_paid:primary#3
- **Rules:** K17; K18; K19; K20; K21; K22; K23
- **Evidence:** 7 companies, 55 served, 268 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 20 open hit(s) at 2 companies, e.g. BAC dividends_paid 2015-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (20)
- **Deprecation:** replaces DividendPaidMember@2025

### `CommercialPaper`
- **Meaning:** Commercial Paper (us-gaap, instant, credit). Carrying value as of the balance sheet date of short-term borrowings using unsecured obligations issued by banks, corporations and other borrowers to investors. The maturities of these money market securities generally do not exceed 270 day...
- **Data point definition:** total_debt: Total debt: short- and long-term borrowings incl. current portion, commercial paper, finance and capital leases (face or notes), financing obligations and failed sale-leasebacks;  excludes operating leases and accrued interest.
- **Data point:** total_debt
- **Rules:** none
- **Evidence:** 8 companies, 49 served, 2 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `ProfitLoss`
- **Meaning:** Net Income (Loss), Including Portion Attributable to Noncontrolling Interest (us-gaap, duration, credit). The consolidated profit or loss for the period, net of income taxes, including the portion attributable to the noncontrolling interest.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income
- **Rules:** X77; F03; F04; resolver functions run
- **Evidence:** 3 companies, 23 served, 1314 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToEarningsNet@2013; CashFlowHedgeGainReclassifiedToEarnings@2013; CashFlowHedgeLossReclassifiedToEarnings@2013; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012 (+8 more)

### `PaymentsForRepurchaseOfEquity`
- **Meaning:** Payments for Repurchase of Equity (us-gaap, duration, credit). The cash outflow to reacquire common and preferred stock.
- **Data point definition:** share_buybacks: Cash repurchases of the company's own common stock;  excludes tax-withholding shares, excise tax, employee-plan purchases, subsidiary buybacks and swaps (founder 2026-11-04).
- **Data point:** share_buybacks; polarity share_buybacks:positive; role share_buybacks:primary#2
- **Rules:** K10; K11; K12; K13; K14; K15; K16
- **Evidence:** 4 companies, 12 served, 6 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `StockRepurchasedDuringPeriodValue`
- **Meaning:** Stock Repurchased During Period, Value (us-gaap, duration, debit). Equity impact of the value of stock that has been repurchased during the period and has not been retired and is not held in treasury. Some state laws may mandate the circumstances under which an entity may acquire its own stock and prescrib...
- **Data point:** none (the resolver never serves it)
- **Rules:** none
- **Evidence:** 0 companies, 0 served, 47 proven, 0 certified cells; last verified 2026-11-13
- **Known problems:** none recorded
- **Pattern hits:** none

### `Dividends`
- **Meaning:** Dividends (us-gaap, duration, debit). Amount of paid and unpaid cash, stock, and paid-in-kind (PIK) dividends declared, for example, but not limited to, common and preferred stock.
- **Data point:** none (the resolver never serves it)
- **Rules:** X93; I35; K21; resolver functions PURE_II
- **Evidence:** 0 companies, 0 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none

### `PaymentsOfCapitalDistribution`
- **Meaning:** Payments of Capital Distribution (us-gaap, duration, credit). Cash outflow to owners or shareholders, excluding ordinary dividends. Includes special dividends.
- **Data point definition:** dividends_paid: Cash dividends paid to common shareholders.
- **Data point:** dividends_paid; polarity dividends_paid:positive
- **Rules:** K17; K18; K19; K20; K21; K22; K23
- **Evidence:** 0 companies, 0 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none

### `ProceedsFromRepurchaseOfEquity`
- **Meaning:** Proceeds from (Repurchase of) Equity (us-gaap, duration, debit). The net cash inflow or outflow resulting from the entity's share transaction.
- **Data point definition:** share_buybacks: Cash repurchases of the company's own common stock;  excludes tax-withholding shares, excise tax, employee-plan purchases, subsidiary buybacks and swaps (founder 2026-11-04).
- **Data point:** share_buybacks
- **Rules:** none
- **Evidence:** 1 companies, 0 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
