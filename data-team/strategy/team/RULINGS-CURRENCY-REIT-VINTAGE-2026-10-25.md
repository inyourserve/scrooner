# Rulings (PROPOSED): reporting currency, REIT calculated subtotals, vintage and restatement (2026-10-25)

Role: Standardization Lead. Status of every ruling below: **PROPOSED, reviewed_by = null**. I prepared them, so I cannot approve them. They need an **approver agent that is not me** (an independent Verifier session that did not author the triage or this file). They also need the founder's own words on the two points marked FOUNDER, because those are release-policy or product-scope calls (AC-19 / founder item 12; the currency label in the UI). Nothing here has been applied. No writes, no migration, no commit.

Input: `data-team/strategy/team/TRIAGE-I6-AND-TAX-RATE-2026-10-25.md` (certify dry-run 40094543570; 10 shards failed, so **every count is a lower bound** for the 986-company cohort). I recounted from the same 92 `certify-findings/S###.json` artifacts (scratchpad copy) and ran one read-only query (one connection, `statement_timeout` 30s, 17 sessions in `pg_stat_activity`) to get filing forms and dates for the vintage family.

Evidence labels: FILING-CHECKED = I opened the SEC R-file today (locator given). FILING-CHECKED (prior) = another session opened it; I did not reopen it. DATA-INFERRED = our tables or artifacts only.

---

## Ruling 1. Reporting currency (CP, IMO in CAD; CB, LOGI, TEL dividends in CHF)

### Recommendation
**Show the value in its native currency with the currency label, as filed. Never convert. Never show a non-USD value in a USD slot or with a "$" label.** Ratios whose inputs are all in the filer's own currency are shown. Any metric that mixes a USD market price with non-USD statement values is hidden with the reason `reported_in_CAD` ("Reported in Canadian dollars; price-based ratios are not computed").

| Item | Outcome |
|---|---|
| Statement lines (revenue, net income, assets, debt, cash flow...) | Shown in CAD, labelled "CAD" |
| Per-share values (EPS, DPS, book value per share) | Shown in CAD/share, labelled |
| Ratios with every input in the filer's currency (gross, operating and net margin, ROE, ROA, ROIC, debt/equity, current ratio, payout ratio, growth, CAGR) | Shown. A CAD/CAD ratio has no unit, so it is correct as is |
| Market cap (cover shares x USD price) | Shown in USD. Share counts carry no currency |
| Price-based metrics mixing USD price and CAD values (P/E, P/B, P/S, earnings and FCF yield, dividend yield, EV and every EV multiple, net cash per share vs price) | Hidden, reason `reported_in_CAD` |
| Screener filters on absolute amounts (for example revenue > $10B) | Non-USD reporters excluded and listed as excluded with the reason. Ratio filters include them |
| Sums or averages across companies | Non-USD rows excluded |
| CHF/EUR dividends per share (CB, LOGI, TEL, FTI) | If the filer also files a USD-per-share fact for the same context, that filed USD fact fills the slot (it is the filer's own number, not our conversion). If not, hide with reason `reported_in_CHF` / `reported_in_EUR` |
| Wrong or odd unit codes (VRNS `afn/shares`, SOFI `usn`) | Hidden, reason `unit_not_usd`, until the Verifier opens the filing. We do not read a unit typo as USD |
| PEP total_debt with a CAD-unit fact and a USD sibling | The USD fact is used. A CAD fact never fills a USD slot (this is the Data Engineer's unit gate, triage 2b) |

**Staging condition (FOUNDER, product scope).** Option (b) needs the display layer to render a currency label. If the app cannot show the label at release, the fallback is to **hide** the CAD monetary and per-share cells with reason `reported_in_CAD` and still show the currency-neutral ratios. Showing a CAD number with a "$" sign is not an allowed outcome even for one day.

### Reasoning
1. The CAD values are right as filed. The defect is the label and the ratios that mix currencies (S018 E15: CP P/B 1.645 = USD 76.7B / CAD 46,626M; P/E, P/S, P/B about 28% low, yields about 39% high). Hiding 2,569 correct values (option c) throws away correct data for two top-1000 companies when a label fixes the defect.
2. Converting (option a) brings in a non-SEC data source (an FX series) and an accounting choice the filer never made. ASC 830 translation uses different rates for flows (period average), balances (period end) and equity (historical). Our USD figure would match no filing, which breaks traceability: every number must trace to a filing (CLAUDE.md, data moat). It also changes the meaning of growth (FX moves become "growth"). A convenience translation could be a later, separate, labelled product. It is not a fix.
3. The concept keeps one economic meaning. Currency becomes an attribute of the cell (WO-28 AT-28.1: record the reporting currency per company). That matches ledger rows 36 and 100: a monetary fact may not sit in a USD slot.

### Effect (from the triage and my recount, DATA-INFERRED, lower bounds)
- 2,569 cells move from "shown as if USD" to "shown labelled CAD": CP 1,290, IMO 1,279. Each company has 46 periods, 2015-03-31 to 2026-06-30. Findings: CP 1,656 monetary + 238 per-share; IMO 1,610 + 240.
- 44 CHF dividend-per-share cells (CB 26, LOGI 16, TEL 2) are refilled from the filed USD fact where one exists. Otherwise they are hidden.
- 10 odd-unit cells: VRNS 4 and SOFI 1 hidden until filing-checked; FTI 1 hidden (no USD fact); PEP 4 take the USD fact.
- Price-based metric cells hidden for CP and IMO: **NOT MEASURED** (one query over `analytics.metric_value` for 2 companies; Data Engineer to count in the dry-run).
- Outside the cohort (CNI and other CAD filers): out of the top-1000 scope; the same rule applies when they enter.

### Filing example
- **CP 10-Q 0000016875-26-000026 R2** (FILING-CHECKED today): header "INTERIM CONSOLIDATED STATEMENTS OF INCOME - CAD ($) ... $ in Millions"; Q2 2026 total revenues 4,164; net income 1,024; basic EPS 1.16 (CAD per share).
- CB and LOGI CHF dividend facts: FILING-CHECKED (prior), VERIFY-SPLIT-REBASE-1000-2026-10-24 line 106.

### Tests (for the Data Engineer, to be run by the approver)
- T1.1 No row with a non-`usd` unit sits in a USD canonical slot (`core.unit` join). Expected 0.
- T1.2 CP and IMO: every P/E, P/B, P/S, yield and EV-multiple cell is blank with `reported_in_CAD`. Their margin, ROE and growth cells are unchanged.
- T1.3 Near-miss: a USD filer with one CAD sub-fact (PEP) keeps its USD value and gets no currency label.

---

## Ruling 2. REIT calculated subtotals (gross profit, operating income, operating expenses)

### Recommendation
For REITs (SIC 6798, the 32 cohort companies listed below), **a subtotal is shown only when the filer's own face statement prints it, and the shown value is the printed figure (the filed fact), never our calculation.** Otherwise the cell is hidden with the reason `not_reported_subtotal` ("Not reported as a subtotal by this company").

- **Gross profit:** hidden unless the face prints a gross profit or gross margin line (WY, and some periods of EQIX, ESS and BXP file a `GrossProfit` fact; there the filed fact is shown).
- **Operating expenses:** a plug (revenue - cost - operating income, or gross profit - operating income) is never shown. Shown only when the face prints a total operating expenses or total costs line that meets the concept's definition.
- **Operating income:** revenue minus a filed `OperatingExpenses` total is never shown. Shown only when the face prints an operating income line. RYN, EQIX, EXR, RHP, LAMR, CCI, AMT, GLPI, WY, ESS, BXP, IRM, VICI and CUBE file `OperatingIncomeLoss` (it is an input to their opex plugs, DATA-INFERRED), so their operating income stays and only the plug is hidden.
- **A printed line our resolver missed** (PLD prints "Operating income", ledger row 41, yet has 8 calculated OI cells): it is a resolver or vocabulary defect, routed to the Data Engineer. The cell stays hidden until the filed fact is selected. We do not keep the calculated number in the meantime.
- **Downstream metrics** inherit the input's reason: gross margin, operating margin, interest coverage, operating-income-based ROIC and EBITDA, opex % of revenue. This matches the S3 rulebook (equity REIT: gross margin and Piotroski not applicable).

### OHI (the open definition question): ruling
**Hide OHI operating income with `not_reported_subtotal`. Do not label "total revenues - total expenses" as operating income, and do not add interest back.**
- What the filing shows (FILING-CHECKED today, **OHI 10-Q 0000888491-22-000029 R4**, Q3 2022, $K): Total revenues 239,430 (including mortgage interest income 17,234 and other investment income 14,110). Total expenses 177,670, which **include interest expense 58,238**, provision for credit losses 4,106 and impairment 10,015. Then total other income 40,378, then income before income tax 102,138. There is no operating income line.
- 239,430 - 177,670 = 61,760 is a figure **after financing cost**. Our operating_income for every other company is before interest expense. Showing 61.76M as operating income would put a non-comparable number in a comparable slot. Interest coverage built on it would count interest twice.
- Adding interest back (61,760 + 58,238 = 119,998) is a "calculated" equivalence with no printed line. It also leaves open where impairments and credit-loss provisions belong. That is a new definition, and no approved composition rule covers it.
- Optional later step (FOUNDER, a novel definition call; I do not recommend building it now): a separate concept "Revenue less total expenses (as presented)", never mapped into operating_income and marked not comparable across companies.
- DOC has the same shape. Its "Total costs and expenses" also includes interest expense (147,756K of 1,294,110K for 6M 2025), so its calculated OI cells get the same treatment.

### Reasoning
1. A subtotal the filer does not print has no single definition at a REIT. Property operating expenses, depreciation, impairments, gains on sale and interest sit in different places at each filer (ledger row 41: PLD operating income includes about 943.6M of disposition gains). A calculated subtotal is therefore our own accounting choice, not a reported value.
2. The inputs are often not the face totals. Example: DOC's "gross profit" uses one revenue component, which gives negative gross profit (below).
3. Hiding with a reason meets the standard (correct or visibly unavailable). It drops no printed figure, because printed figures are kept.

### Effect (triage and my recount, DATA-INFERRED, lower bounds)
- 1,025 cells, 1,655 findings, 32 REITs: gross_profit 688 findings, operating_expenses 521, operating_income 446.
- Cells per company: RYN 88, EQIX 80, EXR 78, RHP 76, LAMR 76, CCI 74, DOC 73, WELL 53, WY 48, VICI 41, CUBE 38, BRX 35, VNO 30, AMH 30, WPC 28, REG 24, OHI 22, AMT 20, REXR 20, FR 15, ESS 12, MAA 11, VMRK 10, GLPI 9, CPT 9, NNN 6, KIM 6, PLD 5, BXP 5, FRT 1, DLR 1, IRM 1.
- Expected after the change: certify `reit_calculated_subtotal` = 0. The hidden cells are the 1,025, minus any cell where a face check finds a printed line our resolver missed. That number is **NOT MEASURED**: it needs a per-company, per-statement-era face check by the Sector Analyst, and PLD is the known case.
- Downstream metric cells hidden: NOT MEASURED.

### Filing example
- **DOC (Healthpeak) 10-Q 0001628280-25-036063 R4** (FILING-CHECKED today), 6M 2025 ($K): Rental and related revenues 1,067,828; Resident fees and services 297,782; Interest income and other 31,627; Total revenues 1,397,237. Costs and expenses: Interest expense 147,756; D&A 534,462; Operating 549,324; ...; Total costs and expenses 1,294,110. The face has no gross profit and no operating income line. Stored GP -251.5M = resident fees 297.8M (`RevenueFromContractWithCustomerExcludingAssessedTax`, one of three revenue lines) - "Operating" 549.3M. This matches CERTIFY-ROUND3 (DOC 10 of 10).

### Tests
- T2.1 For SIC 6798 cohort companies, no gross_profit, operating_income or operating_expenses cell has more than one source fact unless a printed subtotal fact is among them. Expected 0.
- T2.2 Near-miss: EXR operating income (filed `OperatingIncomeLoss`) is unchanged. WY gross profit (filed `GrossProfit`) is unchanged.
- T2.3 OHI Q3 2022 operating_income is blank with `not_reported_subtotal`. Its revenue (239,430K) and pretax income (102,138K) are unchanged.

---

## Ruling 3. Vintage when a later filing carries a different value

### Recommendation (rules V1 to V6)
- **V1 Eligible sources.** Only periodic forms may be displayed or used as inputs: 10-K, 10-Q, 10-K/A, 10-Q/A, 10-KT, 10-QT. An 8-K (including recast Exhibit 99 statements), DEF 14A, S-1 or S-4 copy is never displayed. An 8-K recast can count as *evidence* that a restatement exists (V3 G5). Basis: ledger rows 31, 77, 86, 131.
- **V2 Agreeing copies.** If all eligible copies agree within rounding (consistent with the stated decimals, ledger rows 16 and 32), show the most precise copy. There is no vintage question.
- **V3 Display basis = latest restated (AC-19 option a), but only when confirmed.** When eligible copies disagree, the latest eligible copy is shown only if it passes every guard:
  - G1 It is not a label shift: not equal to the same tag's value at another period in the same filing, and that filing's quarters tie to its FY where both exist (ledger rows 33, 114, 128, 138).
  - G2 Its sign agrees with the earlier copies, unless the filing carries an error-correction signal (ledger row 110, CMG).
  - G3 Per-share and rate guards: no quarterly rate on a year context, no annual rate on a quarter, no DPS <= 0 while dividends paid > 0 (ledger rows 66, 71, 139).
  - G4 Its context is not dated after the filing date (ledger row 149).
  - G5 Corroboration, at least one of: (i) a second later eligible copy carries the same value; (ii) the later filing is a 10-K/A or 10-Q/A for the period, or its cover ticks the error-correction box; (iii) the later filing presents discontinued operations or a retrospective recast for that period (a discontinued-operations fact for the same period in the same filing, or an 8-K recast with the same value); (iv) an 8-K Item 4.02 covers the period. Ledger row 107 shows why: CIVB ticked the box, MNSB did not, and COLB was an entity change, not a restatement.
- **V4 Drop error copies, then decide again.** A copy that fails G1 to G4 is a filer error. It is dropped, and V2/V3 are applied to the copies that remain. Example: NTNX FY2023 net income keeps the original -254.56M once the later +1,506.8M copy (sign flip, G2) is dropped. If no copy remains that passes, or the remaining copies still disagree with no G5 evidence, the cell is **HIDDEN with reason `restated_copies_disagree`** ("Filed copies disagree; restated value not confirmed").
- **V5 One basis per calculation.** A calculated cell (gross profit, opex, liabilities identity, Q4 = FY - 9M) takes every input from one eligible filing (NA-4, RF-04). Growth, CAGR and TTM are shown only when the endpoint values and every TTM component share one basis: the same filing, or values the restating filing left unchanged. Otherwise they are hidden with `basis_changed_between_periods`. Example: LLY FY2016 gross profit.
- **V6 Provenance.** As-filed copies stay stored and linked. The `basis = as_filed` key is reserved (FREEZE-REGISTER) and is not displayed in V1. A point-in-time view is a later product (AC-19 option b).

**Restatement default: HIDE when copies disagree is KEPT** (Dhairya's reversible default, PLAN.md). The change is that V3 adds a confirmed path to show the restated value. The previous default left the older copy on display; under this ruling it stays only through V2 (copies agree) or V4 (the later copy was an error).

FOUNDER: the display basis "latest restated" is AC-19 / founder item 12 (release policy). The approver agent can verify the guards. The basis choice needs the founder's words.

### Reasoning
1. **Older copy by default is wrong for series.** When a company recasts for discontinued operations, the old copy is right "as filed" but on a different perimeter from the newer periods next to it. Growth then measures a perimeter change. DOC 2019 quarterly revenue goes from 537,971K (10-Q 0001628280-20-015363) to 321,079K (10-K 0001628280-21-001804) after the senior-housing reclassification. HON and MET show the same pattern (DATA-INFERRED from copies).
2. **Latest copy by default is also wrong.** In this same family the later "authoritative" copy is plainly wrong in several cells (DATA-INFERRED, from the copies' own values): LEA FY2015-2022 DPS later copies -0.50 / -0.60 / -1.40 / -1.50 / -1.54; G FY2020 DPS -0.195; NTNX FY2023 net income +1,506.8M against a filed loss of -254.6M; TECH FY2019 DPS 0.32 vs 0.08. The root CLAUDE.md 2026-10-18 note records that "latest filed wins" published about 4,000 wrong values. Agreement with SEC Frames cannot validate it, because Frames serves the latest copy.
3. Therefore neither copy may win by date alone. Guards remove copies that are filer errors. Corroboration separates a real restatement from a lone outlier (VERIFY-SPLIT-OTHER-CHANGED: "never let a lone outlier win over a majority"). What remains unresolved is hidden with a reason.
4. LEA shows that hiding is sometimes the only correct outcome: the older copy (0.25 on a full-year context) is itself a quarterly rate (ledger row 71). So V4 hides the cell rather than falling back to the original.

### Effect (DATA-INFERRED, lower bounds)
- Triage: 225 findings show an older vintage while a later authoritative copy differs. My recount from the artifacts plus `core.filing` gives **224 findings at 111 companies** (difference of 1, not resolved). Displayed copy form: 10-K 142, 10-Q 75, 10-K/A 5, 8-K 2. Concept: revenue_sanity 196, operating_income 8, DPS 7, net income 4, other 9. Gap size: under 0.1% 50, 0.1-1% 47, 1-10% 73, 10% or more 54. Sign flips 7 (LEA 5, G 1, NTNX 1). 13 have a later copy filed more than 400 days after the displayed one. Some later "authoritative" copies are 8-Ks (MET 3, GPC 1); V1 makes them ineligible.
- Same rules also cover: mixed_vintage 81 cells (27 companies), cross_vintage_arithmetic 4, the 34 earlier-authoritative-copy cells (a derived copy is not eligible, ledger row 29), the 192 non_periodic_form cells (V1), and the split re-base "restated copies disagree" hold of 5,373 cells (3,686 since 2015), which stays hidden unless V3 G5 is met.
- How many of the 224 move to the restated value, stay as they are, or become hidden: **NOT MEASURED**. It needs a dry-run of V1 to V5 (Data Engineer). Expected direction only: recast families (DOC, HON, MET, VOYA, HIG, GM, FNF, HR, HUBB, MAR, OC, PPG, SNPS, STE) move to the restated value where G5 holds. LEA and TECH become hidden. NTNX keeps the original.

### Filing example
- **LLY FY2016**, FILING-CHECKED today ($M). 8-K **0000059478-19-000274 R2** (Elanco recast): FY2016 revenue 18,312.8, cost of sales 4,160.5. Original FY2016 10-K **0000059478-17-000098 R2**: revenue 21,222.1, cost of sales 5,654.9.
  - Our stored gross profit 12,657.9 = recast revenue 18,312.8 - original cost of sales 5,654.9. It matches neither basis: recast GP is 14,152.3, original GP is 15,567.2 (ledger row 70).
  - Under V1 the 8-K is not displayable. Under V5 gross profit takes both inputs from one periodic filing, which gives the original-basis 15,567.2.
  - FY2016 to FY2017 revenue growth is hidden if FY2017 is shown on the post-Elanco basis (19,973.8 in the recast) while FY2016 is on the original basis.

### Tests
- T3.1 No displayed cell has a source fact from a non-periodic form. Expected 0.
- T3.2 Named cases: NTNX FY2023 NI = -254,560,000; LEA FY2015 DPS hidden `restated_copies_disagree`; LLY FY2016 GP equals a one-filing value or is hidden, never 12,657.9.
- T3.3 Near-miss: a rounding-only pair (ledger row 16, TTWO 3,372,772K vs 3,372.8M) shows the precise copy and no hide reason.
- T3.4 The dry-run reports, per class (V2 agree / V3 restated shown / V4 original kept / V4 hidden / V5 hidden), the cell counts with fact ids. The approver checks at least the 54 cells with gaps of 10% or more against the period's own filing and the later filing.

---

## Decision records (decision.json fields, condensed)
| decision_id | kind | status | scope | proposed_by | reviewed_by | next_action |
|---|---|---|---|---|---|---|
| RUL-CUR-1 | release (definition) | proposed | CP, IMO (CAD); CB, LOGI, TEL, FTI DPS; VRNS, SOFI, PEP units; cohort 986, 2015+ | Standardization Lead | null (needs an independent approver agent + founder for the UI label) | Data Engineer: WO-28 currency attribute + unit gate + price-metric hide; dry-run of the cell list |
| RUL-REIT-1 | template/definition | proposed | 32 SIC 6798 cohort companies; GP, OI, opex; OHI ruled hide | Standardization Lead | null (needs an independent approver agent) | Sector Analyst: face check per company and era (printed lines); Data Engineer: rule-registry hide + PLD resolver fix; dry-run |
| RUL-VIN-1 | release (selection) | proposed | all cohort duration and instant cells with 2+ eligible copies that disagree; 224 + 81 + 4 + 34 + 192 named findings, 5,373 split-hold cells | Standardization Lead | null (needs an independent approver agent + founder on AC-19) | Data Engineer: implement V1-V5 as one selection rule (RESTATEMENT_POLICY stays HIDE); dry-run by class; Verifier filing-checks the 10%-or-more cells |

rollback_ref: null (no writes). code_revision: working tree on `main` at 746b80f (uncommitted tree; not read for these rules except `certification/source_integrity.py`).

## Unresolved and untested
- 10 failed certify shards (94 shard-rows) are untested; all counts are lower bounds.
- Price-metric cells hidden by Ruling 1, downstream cells hidden by Ruling 2, and the V3/V4 split for Ruling 3: NOT MEASURED.
- The 1-finding gap between the triage's 225 and my 224 is not resolved.
- I did not reopen CB, LOGI, TEL, VRNS, SOFI or FTI filings, the PLD statement, or any of the 224 vintage cells. LEA, G, NTNX and TECH are DATA-INFERRED from copy values only.
- G5(ii) assumes the cover error-correction flag is tagged in filings since its effective date; when it took effect is [VERIFY] before relying on it for older periods.
