# Proposal: read dividends per share from the equity statement (2026-11-10)

For the founder and Ritwik (release approver). Proposal only: no code, data or database change has been made.

## Decision box

| Who | Decision | Answer |
|---|---|---|
| Founder | Approve migration **0122** (allow `EQ` in `fsn.concept_rule.stmt`; claimed in doc 53). Typed approval needed. | yes / no |
| Ritwik | After the dry run and the Verifier draw pass, DPS rejoins the FSN write. | later |

Nothing in this proposal changes a displayed value until both answers are yes.

## The problem in one paragraph

Medtronic (MDT, company 3639) shows dividends per share (DPS) only up to 2018-07-27. Our filing store already holds MDT's declared DPS for every quarter through 2026-07-31 (125 facts). From the FY2019 10-K on, MDT prints DPS only on its statement of shareholders' equity, as the note "Dividends to shareholders" in brackets; in two FY2022 10-Qs it is also on the face of that statement. Our builder reads only the balance sheet, income statement and cash flow statement, so it never sees those prints, and the later years show no value and no reason. (Source: read-only investigation, 2026-11-10.)

## How many companies this touches

One read-only query over the 902 loaded companies (investigation, 2026-11-10):

| Group | Companies |
|---|---|
| Print DPS on some statement line | 534 |
| Print it on the income statement through their latest filing (safe today) | 353 |
| Printed it on the income statement earlier, not recently (the MDT pattern) | 139 |
| Never printed it on the income statement | 42 |
| **At risk of a cut-short or missing DPS history with no reason** | **about 181** |
| Print DPS on the equity statement | 225 |
| Print it on an unclassified statement / comprehensive income | 14 / 3 |

Companies that carry DPS only in a note are not counted; this proposal does not reach them.

DPS is already off the FSN write (release approver rulings C6 and R2). It stays off until this lands and is proven.

## Why it happens (three places in the code)

All three only know `BS`, `IS` and `CF`:

1. The database rule table: `fsn.concept_rule.stmt` has `check (stmt in ('BS','IS','CF'))` (`pipeline/db/migrations/0118_fsn_store.sql`, about line 126).
2. `pipeline/src/scrooner_pipeline/fsn_store/mapping.py` (about line 134) maps only BS/IS/CF lines.
3. `pipeline/src/scrooner_pipeline/fsn_store/select.py`: `ANCHOR_TAGS` (about line 81) has no `EQ` entry, and `face_columns` (about line 714) drops equity-statement columns. `select_concept` builds its period list only from prints, so a period with no mapped print gets neither a value nor a reason.

## Proposed change

1. **Migration 0122** (claimed in doc 53, 2026-11-10): allow `'EQ'` in `fsn.concept_rule.stmt`. One constraint change; no data rewritten.
2. **Two new rules** in `data-team/47-fsn-store/concept_rules/per_share.jsonl`: `per_share.dps_tag@3` (CommonStockDividendsPerShareDeclared) and `@4` (CommonStockDividendsPerShareCashPaid), statement `EQ`, ranked below the income statement rules `@1`/`@2`.
3. **mapping.py** maps per-share concepts on equity-statement lines.
4. **select.py**: `ANCHOR_TAGS["EQ"]` = NetIncomeLoss, ProfitLoss, StockholdersEquity, StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest. The income statement print wins over the equity statement for the same period. If both print in one filing and disagree, the cell gets the existing reason `conflicting_values_in_filing`, not a value.
5. **Periods come from the company's template**, not only from prints, so every period with no print shows a visible reason instead of silently ending.
6. **Q4 DPS** stays the founder-allowed subtraction (full year minus nine months), now also from equity-statement face prints, **only when the full year and all three quarters sit on one share basis**: no split or reverse split between the nine-month and full-year balance dates, checked with the share-basis engine. Otherwise Q4 is a blank with a reason. This is the founder's condition of 2026-11-04, and the reason DPS is held today (C6).
7. **DPS joins the sector templates** as a conditional (`COND`) data point for dividend payers, through the template seed. Today DPS sits outside every template, so the done gate and the rule that every previously valued period must keep a value or a reason never covered it; that is how MDT's DPS went unchecked in the 2026-11-09 write (R2).

## Proof before anything is shown

1. Dry run on the about 181 at-risk companies **and all 225 equity-statement printers**, so conflicts between the income statement and the equity statement are counted: new values, new reasons and any conflict with existing values. No writes.
2. A Verifier draw against the original filings (MDT included).
3. Only then does Ritwik decide whether DPS rejoins the FSN write.

## Risks and how they are limited

- The equity statement also prints other per-share lines (for example preferred dividends per share). The new rules accept only the two common DPS tags, so other lines are not picked up.
- Some equity-statement brackets sit on a report with no parent link. Face columns will be keyed by filing, statement, period and period length, so such a print still lands on the right column.
- Income statement and equity statement can disagree inside one filing; that case shows a reason, never a guessed value.
