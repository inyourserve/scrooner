# WO review: Standardization Lead (WO-5, and the WO-13 accountant agenda) (2026-10-22)

Role: Standardization Lead (data-team/11). Objective: review my work order before execution: is WO-5 doable, what decisions the named accountant must make (one card each), my definition-level position on the held guards, how definitions are versioned so a later change does not force a redo, effort, sign-off.
Status of everything here: **PROPOSED**. I do not approve accounting definitions; a named human does (WO-13). No code, no database queries, no commits, no SEC fetches in this run. Evidence is relayed from the cited files and labelled as they labelled it; the only new evidence is CODE-READ (what the repository does today, which is not financial evidence).
Inputs read: data-team/20, 21, 22, 11, 03, 27, 31 (section B), 33 (D-N), 37; strategy/40-ROOT-CAUSE-GATE, 41-TEMPLATE, 41-EVIDENCE-TOTAL-DEBT, 42-EVIDENCE-PER-SHARE, 46, 47, 48 (grep); team/R3, S3; tags/cards/debt.md, net-income-and-shares.md (grep), feedback-inbox.md; `doc/data-moat/wave1-canonical-definitions.md` (grep); code: held diff of `mapper/concept_fallback.py`, `sanity/tag_investigator.py`, `normalizer/derived.py` (stat); `mapper/definitions.py` (lines 225-255); migrations 0004 (lines 50-130), 0095; `git log` on concept_fallback.py, derived.py, concepts.py; `git show a595b72`; `mind search` (4 topics).

## 0. Four findings that change the plan (read first)

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| 0.1 | **The "revenue-total disagreement guard" is not built.** Docs 46 (W12) and 47 (WO-9) call it "held, already built". The commit that delivered doc 37 says "No code exists for the rule. Docs only, no tests." The working tree holds code only for the total-debt guards and the per-share non-derivation. | `git show a595b72` message; `git status` (no revenue-guard file); grep of `pipeline/src` for the guard's reason text: no hit (CODE-READ) | Gate B's "release held guards" cannot include revenue on day 10 unless the Data Engineer builds it first. Spec in card NA-8. Docs 46/47 should be corrected. |
| 0.2 | **The held total-debt guard produces reasonless blanks.** `evaluate_total_debt` returns a reason, but `resolve_total_debt_components` deletes the company's rows and inserts only valued rows; a blocked date writes nothing, so the reason lives only in a log counter. | held diff, `concept_fallback.py` writer loop (`continue` when value is None; delete-then-insert at the chunk) (CODE-READ) | Exactly the S4 failure (a missing reason means the engine never wrote a row). Condition on release: the reason must reach the cell (cell_state or `is_null_reason` pass-through). |
| 0.3 | **Formula versioning is nominal today.** `metric_definition` has `formula_version`, but `definitions.py` always inserts version 1 and upserts `on conflict do update` the description, then deletes and re-inserts the inputs. `canonical_concept` and `concept_mapping` carry no version; `canonical_fact` is delete-then-insert. | `mapper/definitions.py` 237-255; migration 0004 lines 55-68, 92-101 (CODE-READ) | A definition change today silently overwrites history: the "one-time" test fails as built. Section 4 fixes this before any backfill. |
| 0.4 | **CFO already mixes bases period by period.** `cfo` maps the continuing-operations total at priority 2 under first_match (and 0095 does the same for investing and financing), so one company's series can switch between total and continuing-ops CFO when one period lacks the plain tag. FCF then subtracts total-basis capex. | migration 0095 header; cfo priority-2 note there (CODE-READ) | Feeds card AC-20. Not a new wrong value I verified; a basis-mixing path to check in the Verifier sample. |

## 1. WO-5: doable by me with the evidence available?

| WO-5 item | Doable now? | What I can deliver without new inputs | Missing inputs (who) |
|---|---|---|---|
| 1. Answer S3 section 7 (13 items) and R3 C1-C15, plus EBITDA without an OI line, D&A and capex composition, DPS policy, NI to parent, bank revenue, REIT capex, insurer revenue | **Proposals yes; answers no.** I can only recommend. Answers need the named accountant (WO-13). | The 38 decision cards in section 2, each with options, consequences, my recommendation and what it blocks. Fixture packs exist for C1, C4, D&A, capex, debt, interest, revenue, NI (R3 section 2; 27; 37; 42). | (a) Named accountant (founder). (b) FILING-CHECKED fixtures still missing for insurer revenue, REIT capex, dividend yield and payout basis, TTM P/E, quick ratio/CCC/goodwill %, comprehensive income, restatement basis, cash perimeter, continuing-ops CFO (me + Verifier, about 5 days, section 5). (c) Cohort cell counts per option: most cards have FSDS one-quarter counts or top-1000 row counts, not template-cell counts; R3 section 9's impact query plan is NOT_RUN (Data Engineer or Triage, one connection). (d) Independent Verifier review of R3 and S3: not done (both say "Verifier next"). |
| 2. Conditional rulebook (S3): condition, evidence, state, coverage, propagation, wording for every conditional metric; remove 29 `*_resolved` twins and internal rows from the denominator | **Yes for the rulebook content** (S3 drafted all 163 data points). **No for wiring**: the states need somewhere to live. | Finalize S3 into a machine-readable table (rule ID, data point, condition, evidence locator type, state, wording, propagation rule P1-P10, coverage class) for the Data Engineer's `cell_state` job. Denominator removal is a founder card (F-1). | (a) `cell_state` storage design (WO-1.5, R6): where state, rule ID and evidence reference live. (b) Evidence detectors audited 30 per group (WO-4.3) before any NP/Z state may shrink a denominator. (c) Founder approval of the state model and of F-1. (d) Tag Mapper coexistence for `PaymentsOfOrdinaryDividends` and MLP distribution tags before Z-dividend evidence can be trusted. |
| 3. Versioned definitions for the composition layer, once K1 passes | **Design yes (section 4); seeding no.** | Registry design, slot lists (R3 section 5), version classes and the replay rule. | (a) K1 result: the structure pilot (FSN `cal`, FSDS `pre`, WO-1.10). (b) A migration number claimed in doc 53 at build time. (c) Accountant answers for the slot include/exclude flags. |
| Acceptance: FILING-CHECKED fixture set per definition, accountant approval before any REPLACED cell | Achievable per card; the gate is the accountant. | Fixtures listed per card. | Named accountant. |

Conclusion: nothing in WO-5 is blocked on my side; every answer is blocked on one human, and the rulebook's wiring is blocked on WO-1.5. I can do all proposal and fixture work now.

## 2. Decision cards

Counts: **38 cards. 21 need the accountant (AC-1 to AC-21). 14 can be decided without an accountant because they only hide a value, are arithmetic, or select a source by the filing's own arithmetic within an unchanged meaning (NA-1 to NA-14). 3 are founder product decisions, not accounting (F-1 to F-3).** NA cards still need a Verifier zero-wrong sample and the founder's release policy; they need no accounting ruling.
Format per card: question; options with consequence for users and cells (scope of each count stated, evidence label from the source); recommendation; blocked until answered. "Top 1000" = 1,014 ids in shards.csv; "cohort" = the top 986; "FSDS" = SEC data sets 2025q4, one quarter, non-financial filings unless stated (DATA-INFERRED). Cell counts are what the evidence files report; where none exists I say NOT MEASURED.

### 2A. Decidable without an accountant (hide-only, arithmetic, or filing-proven source selection)

**NA-1. Per-share values are never derived by subtraction (EPS and DPS, Q2/Q3/Q4)**
- Question: Q4 = FY - 9M and Q2/Q3 = YTD differences are applied today to EPS and DPS. Stop for both, including dividends declared per share?
- Options: (a) stop EPS only: DPS keeps -1.18 (V), -1.54 (LEA), -4.9 (KLAC) style values; 210 negative derived DPS rows shown in the top 1000. (b) stop EPS and DPS (held code): Q4 EPS/DPS cells blank with "not filed separately (per-share values are not derived)"; derived per-share rows in the top 1000: basic EPS 7,476, diluted 7,107, DPS 6,844; displayed canonical cells from derived facts: diluted EPS 5,263 Q4 / 38 Q2-Q3, basic 5,354 / 31, DPS 3,914 / 379 (42-EVIDENCE 2a, 2d; DATA-INFERRED). (c) derive DPS only within a split-free year when no quarterly-rate-on-annual-context pattern: still fails on CAT's lumpy declarations (Q2 3M = 6M = 2.92, inbox 2026-10-22) and needs a detector we do not have.
- Why no accountant: per-share non-additivity is arithmetic (EPS uses each period's weighted shares; MSFT 4.80 vs filed 4.81, AAPL 1.84 vs 1.85, KLAC -22.61 vs 1.04, all FILING-CHECKED). Option (b) only hides.
- Recommendation: (b). It matches the founder's standing "never derive" instruction (42 section 8.1).
- Blocks: release of the held `derived.py` change; AC-13 and AC-14 (they define what replaces TTM EPS and TTM DPS).

**NA-2. Scope of "non-additive": pure ratios, other per-share values, other share counts**
- Question: the held guard also stops deriving `pure`-unit facts (effective tax rate, volatility, segment counts) and other per-share facts (option exercise prices, grant-date fair values, antidilutive counts). Keep that scope? What about non-weighted share counts (antidilutive, incremental dilutive) and the window-weighted weighted-average quarters?
- Options: (a) scope as held: top 1000 stops 16,540 derived `pure` rows and 21,673 other per-share rows (42-EVIDENCE 2a). (b) narrower (EPS/DPS tags only): those rows stay; none of them is additive, so every one is arithmetic nonsense (a Q4 tax rate of FY rate minus three quarterly rates). (c) also block derivation of non-weighted share counts.
- Recommendation: (a) plus (c). Keep the founder-adopted window-weight method for weighted-average quarters (wave1 line 38, commit 7825b47) but label it "approximation" where shown. Before release, confirm no displayed metric reads a derived quarterly `pure` value (42 section 8.2 asks the same; CODE-READ check, Data Engineer).
- Blocks: final form of the held change.

**NA-3. A filed FY per-share value that is really a quarterly rate, and the FY-equals-Q4 demotion**
- Question: V and LEA tag the quarterly DPS (0.59, 0.77) on the FY context; KLAC's FY EPS is post-split while its quarters are pre-split. Guard the FY value? Keep the existing demotion of a "Q4" equal to its FY value for per-share facts?
- Options: (a) guard: an FY per-share value must be >= each filed quarter of the same year (DPS) and on the same split basis as its quarters, else hidden with a reason; (b) no guard: the FY DPS of V and LEA stays understated and feeds dividend yield (AC-13).
- Recommendation: (a), and keep the demotion (it only blanks; 42 section 8.5 notes it can misfire near zero, which only hides). Hide-only.
- Blocks: AC-13 option "latest filed FY DPS / price".

**NA-4. Additive derivation only on same-sign, same-basis inputs**
- Question: block Q4 = FY - 9M for additive flows when the FY and quarterly signs disagree on the same tag (DIS interest expense FY -1,812M vs quarters +487/+471/+438M gives -3,208M) or when the FY comes from a recast filing and the 9M from the original (HON capex 58M = recast 986M - original 928M, W4).
- Options: (a) block and blank with a reason; (b) keep deriving: DIS and HON-type values stay wrong.
- Recommendation: (a). Arithmetic precondition, hide-only. The choice of WHICH basis to show is AC-19.
- Blocks: W4 release; Period Engineer WO-2.4.

**NA-5. Undefined-by-math states (W6/W7, S3 M1-G and M1-R)**
- Question: growth over a non-positive base and ratios over a non-positive denominator are published as numbers (RDDT NI growth -209.5% on a loss-to-profit turn, FILING-CHECKED; Ford 5y NI CAGR +44.9% across two losses; 117 negative P/E, 36 negative PEG, 24 negative payout, 145 ROE values incl. loss over negative equity, cohort, DATA-INFERRED). Show "Not meaningful: <reason>"?
- Options: (a) NM state with the input named (S3 2.2); (b) keep the numbers: ~245 YoY values plus CAGRs and ~180+ ratios stay misleading; (c) replace with another measure (absolute change, "turned profitable"): a new display, not a correction.
- Recommendation: (a) now. (c) is optional later product wording (founder), not needed for correctness. Out of this card and kept for the accountant: interest coverage with an operating loss (AC-15) and the ROIC tax term (AC-16), because some practice shows those as values.
- Blocks: W6/W7 release.

**NA-6. Held total-debt guards: R1(b) containment, R5 zero, R5 floor, R4 preference** (decision in section 3)

**NA-7. Prefer the balance-sheet carrying lines N + C over a differing `LongTermDebt` (R1a, "N+C reorder")**
- Question: where `LongTermDebt` (L), `LongTermDebtNoncurrent` (N) and `LongTermDebtCurrent` (C) are all filed and L differs from N + C, which wins?
- Options: (a) N + C (the face carrying lines): changes 1,122 of 7,102 company-instants at 158 of 428 companies, 100 at their latest period (file 31 B, DATA-INFERRED); fixes AMZN/GOOG face-value vs carrying (ledger 2026-10-21, FILING-CHECKED) and PFE 2020-type cases (L 4,000M vs N + C 39,135M, where L is a component). (b) keep L: those stay. (c) interim: where they differ beyond rounding and the stored path used L, hide total debt with "debt composition undecidable" until (a) passes its Verifier sample.
- Why no accountant: L, N and C are all lease-exclusive borrowings tags (FASB calc, ledger row 53); the meaning of total debt does not change, only which filed lines represent it, and the choice is proven by the face statement. If the founder reads K5 strictly ("never close a definition without the accountant"), this moves to AC-2's first question; it is a one-word answer there.
- Recommendation: (a), released as a MINOR version (section 4) after a dry-run and a 30-case Verifier sample that includes MCD (L smaller), CTAS, NXPI, CL, TMUS 2021; (c) only if the sample fails.
- Blocks: about 100 latest-period total-debt values and their dependents (D/E, net debt, EV).

**NA-8. Revenue-total disagreement guard (to be built; see 0.1)**
- Question: hide revenue and revenue-derived cells where `Revenues` (or `RegulatedAndUnregulatedOperatingRevenue`, `RevenuesNetOfInterestExpense`) and RCFC are both filed undimensioned for the same context and differ beyond rounding, until the structural rule (NA-9) picks the face total?
- Options: (a) guard in BOTH directions, whichever tag is displayed (doc 37: RCFC-first wrong 14 of 19, Revenues-first wrong 5 of 19; EMR and NTAP display a `Revenues` fact that is not on any statement); reach up to 4,479 company-periods (772 annual) at 201 top-1000 companies (file 31 B). (b) the narrower 33-G form (only when the displayed tag is RCFC): leaves EMR 1,660M (face 13,804M) and NTAP 6,237M (face 6,925M) shown, both FILING-CHECKED wrong. (c) no guard: 7 of 22 sampled displayed periods wrong stay shown.
- Cost stated honestly: in doc 37's sample 15 of 22 displayed periods were right, so this guard hides many correct values. That is allowed ("unavailable with a reason") but it must be short-lived and its hidden-correct count measured.
- Recommendation: (a), banks excluded (their own template), paired with NA-9 so most hides convert to values quickly.
- Blocks: Gate B revenue item; WO-6 family 3.

**NA-9. Revenue: select the face total by structure for the clean subset**
- Question: publish the filer's printed total revenue (position + calc parent + identity, doc 37 section 4) when the selected tag is standard us-gaap, the identity is exact within rounding, the company is in a non-bank template, and the total contains only revenue-family lines?
- Options: (a) yes, as a MINOR version (same meaning, "total revenue", better source selection), Verifier 30 of 30 per doc 37 section 8; (b) wait for the accountant on AC-9 first.
- Recommendation: (a). Everything outside the clean subset (gains or other income inside the total, contra-revenue gross vs net, excise, custom-tag totals, cross-vintage) stays hidden by NA-8 until AC-9. Same K5 caveat as NA-7.
- Blocks: conversion of NA-8 hides into values; Walmart 179,496 vs 177,769 and ITC 454 vs 515 (R3 fixtures).

**NA-10. Consistency guards for capex/FCF and D&A**
- Question: FCF, FCF margin and FCF yield read raw `capex` while the statement row shows `capex_resolved` (adds software); D&A takes the larger of two tags. Hide where they diverge until AC-5 and AC-6?
- Options: (a) hide FCF-family cells where `capex_resolved` differs from `capex` for the same period, and stop the max-of-two D&A from feeding EBITDA ratios where both tags are filed and differ beyond rounding; (b) leave: the displayed capex row and the FCF using it can have different perimeters for the same company-period (R3 0.2, CODE-READ).
- Recommendation: (a). Hide-only. Which perimeter is right is AC-5/AC-6.
- Blocks: nothing upstream; reduces wrong-value exposure now.

**NA-11. Net income sourced from `ProfitLoss` while non-zero NCI exists**
- Question: hide net income and dependents where the resolved source is `ProfitLoss` and a non-zero `NetIncomeLossAttributableToNoncontrollingInterest` exists for the same context (33 I B1)?
- Options: (a) hide: FCX Q1-2026 1,387M shown vs 881M attributable (FILING-CHECKED in 33 I) leaves the screen; population 1,189 rows (PLAN.md per 33 I, DATA-INFERRED); (b) leave.
- Recommendation: (a). Deterministic, hide-only. The subtraction fix is AC-8.

**NA-12. Gross margin only from `GrossProfit` or a single total cost line (33 N)**
- Question: hide gross margin unless the company files undimensioned `GrossProfit` or one total cost-of-revenue line for the same context?
- Options: (a) hide with "gross profit not presented by this company": removes UNH 88.6%, CVX 43.6%, ELV 89.1%, WM, RCL, RSG (FILING-CHECKED in 33 N); about 15 of 190 shard companies (ESTIMATE); (b) leave.
- Recommendation: (a). Hide-only. Member sums (CAT, AMH, BRK) are a later composition rule.

**NA-13. Unknown is never zero; evidenced zero needs tag-agnostic filing evidence**
- Question: (i) remove TSY's unconditional $0 default for missing dividends (PFE stored -0.25% vs 5.7% dividend yield, FILING-CHECKED; 26 cohort payers file unmapped dividend tags; 225 companies have a TSY value with blank dividends_paid, DATA-INFERRED); (ii) adopt S3 2.1 evidence for Z (activity did not occur) for dividends, buybacks, capex, SBC, interest expense; (iii) accept "row omitted in the 10-K + later 10-Q comparative 0" as zero activity (CMI, FILING-CHECKED).
- Options: (a) all three; (b) keep the $0 default: wrong yields stay.
- Recommendation: (a). Arithmetic and evidence rules; borrowings Z with no line and no note stays AC-4.
- Blocks: W8; the Z state in cell_state.

**NA-14. Dividend initiated or suspended (S3 item 9)**
- Question: prior DPS > 0 and current Z: show -100%? Prior Z and current > 0: show a percentage?
- Options: (a) suspended = -100% with "Dividend suspended" (the arithmetic is exact given Z evidence); initiated = NM "Dividend initiated in FY<t>" (division by zero); (b) both NM.
- Recommendation: (a). S3 listed this as accountant; on review it is arithmetic plus wording (founder for wording). Requires NA-13 Z evidence.

### 2B. Founder product decisions (not accounting)

**F-1. Coverage denominator: remove the 29 `*_resolved` twins and internal rows (total_debt_split, base employee_count)**
- Options: (a) remove: one template cell per economic line (163 data points count 29 concepts twice); (b) keep: coverage double-counts.
- Recommendation: (a), with both scoreboards kept (fixed 160,718-cell denominator and template denominator) so the change is visible. Blocks: WO-5.2, Gate C.

**F-2. May a pre-2015 base year start a 10-year growth rate? (S3 2.3, doc 38)**
- Options: (a) yes when the base fact is post-2009 XBRL and certified (doc 38 is about "current" display); (b) no: every 10y CAGR ending before FY2025 shows "Base year before 2015 not used".
- Recommendation: (a). Blocks: 10y CAGR cells (342 revenue 10y history blanks in the cohort, S3 F5).

**F-3. Growth period basis and history wording**
- Options: (a) growth templates show FY and TTM rows only; quarter rows stay series data (a 10y Q2-vs-Q2 CAGR compounds one quarter's seasonality); streak wording ">= N years (all available history)"; (b) keep quarter-row growth.
- Recommendation: (a). S3 tagged the period basis [ACCT]; it is a presentation choice, so I moved it here. Blocks: SH state wording.

### 2C. Need the named accountant

**AC-1. Finance leases in debt, with the coupled interest, D&A and FCF choices (R3 C1, C2; 27 D3)**
- Question: is screen "total debt" borrowings only (`total_debt_std`) or borrowings plus finance leases (`_incl_fl`)? Coupled: finance-lease interest in interest expense, finance-lease ROU amortization in D&A, lease principal in FCF. And may a separately filed finance-lease amount be subtracted from a combined lease-inclusive debt tag (C2)?
- Options and consequence: (a) exclude finance leases everywhere: needs C2 subtraction for combined-tag filers (CVX) or they go `partial`; (b) include everywhere: add `FinanceLeaseLiability*` where not already inside a combined tag (double-count risk); (c) today: in when combined-tagged, out when separate (inconsistent). Walmart 2025-10-31: 46,369M vs 53,127M (+14.6%); interest 563 vs 684 (FILING-CHECKED). FSDS: lease-combined debt tag on the face 516 filings, separate finance-lease line 443, both 18. Cohort cells NOT MEASURED. Operating leases are out under every option (wave1 1.3-1.4; CATO/ATEX).
- Recommendation: R3's default: `_incl_fl` for EV, net debt, debt/EBITDA and interest coverage, with ROU amortization and lease interest included; `total_debt_std` shown as "borrowings"; C2 subtraction only where the filer's note or calc shows combined = debt + that lease amount. Interim until answered: store and show the composition path ("includes finance leases") (27 option C).
- Blocks: `total_debt_std`/`_incl_fl`, EV and every EV multiple, D/E, net debt/EBITDA, interest coverage, FCF-after-lease; the debt and interest composers.

**AC-2. Debt composition beyond N + C: short-term block (R2) and instrument sums (R3/F2)**
- Question: (i) add `DebtCurrent` once, minus the current part already inside L; refuse when two distinct short-term tags remain (BAC, nested vs additive undecidable)? (ii) may a total be built by summing instrument tags when no role tag exists (CDNL pair, FRD, EG three-tag, NET/CME/CDNS/DLR)?
- Options: (a) adopt R2 and R3 as written in file 31 B (refusal where undecidable); (b) single-instrument F1 only (sole tag including current and noncurrent, non-financial SIC); (c) none.
- Consequence: R2 double count 51 instants, DebtCurrent omission 83, outside-list short-term tag 463; R3 would address 3,301 blank instants with instrument tags only (1,459 single tag, 1,308 non-financial) (file 31 B, DATA-INFERRED); cohort total-debt capture defects 1,086 cells (doc 46). CDNL shows gross `NotesPayable` 121,178,878 vs net pair (FILING-CHECKED): precedence face pair > schedule total.
- Recommendation: (a), each sum requiring a filed total or face check to tie within rounding; refuse otherwise.
- Blocks: Tier 2 total-debt fills (CDE custom noncurrent line, AMP segment lines are company-scoped on top).

**AC-3. Special liabilities: FHLB advances for non-banks, mandatorily redeemable preferred (C15), vehicle/captive-finance debt**
- Options: (a) FHLB advances are debt for insurers (EG) but never for banks and thrifts (funding, bank template); MRP out; HTZ vehicle debt in (it is borrowing; its interest is AC-15); (b) all out; (c) case by case.
- Consequence: EG D/E blank today; EWBC stored total debt 35.6M vs 3,035.6M (bank; moot under the bank template). Counts NOT MEASURED.
- Recommendation: (a). Blocks: EG and similar insurer D/E; HTZ-type leverage.

**AC-4. Zero borrowings (27 D3 E2/E3; S3 item 8)**
- Question: when may total debt show 0?
- Options: (a) E1 (a total tag = 0, or zeros on every family tag) and E2 (filing text "no borrowings outstanding" plus no face borrowing line, CATO) show 0; E3 (no line, no note, ATEX) stays blank "No borrowings reported"; (b) E3 also 0 if a strict face test passes (every face liability line identified, none a catch-all, no debt note); (c) only E1.
- Consequence: `zero_debt` 184 blank and `missing:total_debt` cells (S3, cohort); E2/E3 population NOT MEASURED.
- Recommendation: (a), with (b) as a later rule only after a Verifier audit of the face test.
- Blocks: Z state for borrowings; zero_debt, D/E = 0, ROIC invested capital for debt-free filers.

**AC-5. Capex composition (R3 C4 capex half, C5, C6, C8; ArcBest; Air Lease)**
- Question: what is capex? (i) capitalized software in (C4); (ii) intangible purchases separate (C5); (iii) `PaymentsToAcquireProductiveAssets` labelled "Capital expenditures" with no separate intangible line accepted as PP&E + software (C6); (iv) "PP&E net of financings" accepted with a flag; (v) rental-fleet purchases (C8); (vi) every investing-section capex row summed (Air Lease flight equipment 2,348,253K plus deposits on a custom tag next to a 237,683K PP&E tag).
- Options: (a) R3 defaults: software IN, intangibles SEP, C6 accept flagged, net-of-financings flagged, rental fleet in a separate template, all face capex rows summed; (b) PP&E tag only (today's raw capex): understates Aptiv (489 on productive assets, blank), ArcBest (9,958K software), Air Lease; (c) PP&E + software + intangibles.
- Consequence: FSDS capex shapes: PP&E only 2,514; PP&E + intangibles 321; PP&E + software 146; two or three PP&E lines 137; custom only 53; about 152 FY2025 10-K filers with other capex lines >= 10% of the PP&E line (ledger, DATA-INFERRED). Cohort capex defects 1,567 cells (doc 46).
- Recommendation: (a). Coupled with AC-6 (software amortization IN D&A if software IN capex).
- Blocks: FCF, FCF margin, FCF yield, FCF per share, capex % revenue, FCF growth, fcf_gt_net_income; NA-10 hides convert to values.

**AC-6. D&A for EBITDA (R3 C3, C4 amortization half, C7, C11, C12; S3 item 12)**
- Question: which slots are in EBITDA's D&A? Depletion (C3); capitalized-software amortization (C4); is a "D&A" label on a `Depreciation` tag evidence that amortization is inside (C7, ArcBest); content, regulatory and contract-cost amortization (C11); ARO accretion (C12); debt-cost amortization (proposed OUT); intangible amortization Z when there are no finite-lived intangibles (S3 item 12).
- Options: (a) R3 5.1 defaults (depletion IN, software IN, label accepted when only intangibles are separate, C11/C12/debt-cost OUT, Z only with a no-intangibles note); (b) today's larger-of-two-tags (fitted to yfinance, perimeter by size).
- Consequence: FSDS D&A face shapes: one combined line 2,286; Depreciation only 427; depreciation + separate intangible amortization 286; debt-cost amortization lines in 1,439 filings; ROU amortization in 823. Cohort: 710 cells where D&A is filed only as two component lines (MSFT, GOOG, ABT, AMD); EBITDA 427 / EBITDA margin 452 blank. Fixtures AMD 2,253, Aptiv 741 (debt cost 7 excluded), Jabil 674, Gilead partial (FILING-CHECKED).
- Recommendation: (a).
- Blocks: EBITDA family (EBITDA, margin, EV/EBITDA, debt/EBITDA, net debt/EBITDA).

**AC-7. Operating income and EBITDA when the statement has no operating-income line (314 cells; 27 D1, D2)**
- Question: for single-step statements (CVX, AJG, HTZ, GE) and statements without an OI subtotal (NKE, JNJ, IBM cited in doc 46), what do operating income and EBITDA show?
- Options: (a) operating income blank "not reported as a subtotal by this company" (face evidence required); EBITDA blank; (b) a separately named "EBIT (pretax + interest expense)" concept and metric, never written into operating income, excluded for financials and `InterestExpenseOperating` filers; (c) OI = revenue - cost of revenue - SG&A only when SG&A is the only operating line, with an exactness gate on a control group (D2); (d) the existing arithmetic fallback (85.5-90.3% within 2% of filed OI on its own control group, measured 2026-09-13): **a wrong-value class today**, needs suppression of inexact shapes whatever is chosen here.
- Consequence: 314 EBITDA cells (doc 46); FSDS no OI line 398 filings, CostsAndExpenses without OI 89; `CostsAndExpenses` has four meanings (ledger HP/XOM: 651 / 29 / 42 / 115 / 64 of 958).
- Recommendation: (a) now, (c) after its control-group exactness gate, (b) only if the product wants a named EBIT metric. Separately and without the accountant: guard OperatingIncomeLoss facts that equal pretax (AFG, ELS; 30 FY2025 filers, ledger) and flag OI that includes disposal gains (PLD) per R3 5.5.
- Blocks: operating margin, interest coverage, ROIC numerator, EBITDA for these issuer-periods.

**AC-8. Net income attribution (R3 5.7; C14; 33 I)**
- Question: (i) adopt three distinct concepts (consolidated incl. NCI, attributable to parent, available to common) with parent feeding net margin, ROE and P/E checks and common feeding EPS checks? (ii) when only `ProfitLoss` is filed and no NCI line exists, is NCI zero (C14)?
- Options: (a) three concepts; parent = consolidated - NCI when NCI is reported; no NCI line = `partial` (not zero); (b) (a) but treat a missing NCI line as zero; (c) today's single chain NetIncomeLoss -> ProfitLoss -> available-to-common (three attributions under one name).
- Consequence: FSDS: NetIncomeLoss only 2,679; NetIncomeLoss + ProfitLoss + NCI 744; ProfitLoss with no NetIncomeLoss 259; available-to-common lines 523. FCX Q1-2026 1,387M vs 881M; T equity incl. 15,990M NCI (33 I, FILING-CHECKED there).
- Recommendation: (a). The split itself is attribution, not perimeter; the accountant is needed for (ii) and to confirm the metric wiring.
- Blocks: NA-11 hides convert to values; net margin, ROE, P/E basis (AC-14).

**AC-9. Revenue definition beyond the clean subset (doc 37 section 6; R3 C9, C10)**
- Question: when the filer's printed total includes non-revenue items or is presented gross/net, what is Scrooner revenue?
- Sub-questions with my default: (i) insurer "total revenues" incl. realized capital gains (HIG): template-specific, see AC-11; (ii) "total revenues and other income" (XOM 332,238M incl. other income; COP 61,548M on a custom tag; CVX equity-affiliate income): subtract equity-method and non-operating income only where shown on the face, else flag; (iii) contra-revenue (MA 29,845 gross - 10,961 rebates = 18,884 net): net as presented; (iv) pre-606 bad-debt provision netting (THC): net as presented, basis-labelled; (v) premium taxes inside total (CNC): as presented; (vi) excise taxes (C9): net where presented as a deduction; (vii) custom-tag totals: company-scoped mapping with accession and calc path; (viii) Q4 when 10-K and Q3 10-Q select different tags: blank `q4_basis_change`.
- Consequence: these are the hides NA-8 cannot convert; share of the 4,479 periods NOT MEASURED (doc 37 sample: 4 of 19 decidable companies sit in these cases).
- Recommendation: defaults above; "revenue = the filer's total revenue as presented, net of contra-revenue, excluding non-operating income shown inside the total".
- Blocks: revenue, P/S, EV/S, margins and growth for those companies.

**AC-10. Bank revenue**
- Question: bank revenue = net interest income + noninterest income? (Citigroup `Revenues` is already net of interest expense, 65,354M = 44,127M + 21,227M; BAC 138,566M stored vs 113,097M; 5 of 5 printing banks agree, data-team/32.)
- Options: (a) NII + noninterest income, computed, labelled; (b) not shown for banks (NT); (c) the filer's `Revenues` (unsafe: gross at some banks, net at others).
- Consequence: 44 banks in the cohort (S2); NII and interest income blank for 40 of 44 banks though on the face (USB R4); part of the 961 "sector definition pending" cells (doc 46).
- Recommendation: (a). Blocks: bank template revenue, P/S, revenue growth; the 961-cell T1 class.

**AC-11. Insurer revenue composition**
- Question: insurer revenue = premiums earned + net investment income + fees + other, with or without realized gains (HIG)? How are managed care (CNC premium taxes) and insurance brokers treated?
- Options: (a) "total revenues as presented excluding realized and unrealized investment gains" for P&C/life, with a separate gains line; managed care and brokers use the corporate template (S2); (b) total revenues as presented (gains included; volatile); (c) premiums only.
- Consequence: 40 insurers, 7 managed care, 7 insurance brokers in the cohort (S2); counts of affected cells NOT MEASURED. PGR tags investment income with a bank tag (ledger).
- Recommendation: (a). Needs fixtures (HIG, PGR, a life insurer, CNC) before the sitting. Blocks: insurer template revenue cells.

**AC-12. REIT capex**
- Question: for equity REITs, is capex development + recurring improvements, with acquisitions separate? Is FFO ever computed (no: R3 section 8)?
- Options: (a) capex = development + capital improvements; acquisitions SEP; FCF family NT (S3 section 6); (b) capex NT for REITs; (c) all real-estate payments.
- Consequence: 54 equity REITs and 2 mortgage REITs in the cohort (S2); cells NOT MEASURED.
- Recommendation: (b) for the screen (consistent with S3's REIT removals) plus (a) as a statement-only line. Needs fixtures. Blocks: REIT template finalization.

**AC-13. Dividends: per-share basis, dividend yield, payout ratio, MLP distributions (S3 items 2, 10)**
- Question: with no derived Q4 DPS (NA-1), what are dividend yield and payout? Declared or paid? Are MLP/LLC distributions to unit holders "dividends to common"? Does `PaymentsOfOrdinaryDividends` (which can include preferred) count?
- Options for dividend yield: (a) latest filed FY DPS declared / current price, guarded by NA-3, labelled "FY<year> dividends declared per share"; (b) TTM common dividends paid (cash flow, additive) / market cap; (c) TTM DPS sum (blocked by NA-1); (d) latest quarterly rate x 4 (not reliably in XBRL).
- Consequence: dividend_yield rows using a derived DPS: 420 (top 1000), 938 (all); dps_growth 3,739 / 3,399; payout 7,289 (42-EVIDENCE 2e); dividend_yield `missing:dividends_per_share_ttm` 453 and dividends_paid blank 280 in the cohort (S3); 26 cohort payers on unmapped tags; MLPs CQP, EPD, ET, MPLX, PAA.
- Recommendation: dividend yield (a), with (b) as a cross-check that holds the cell when they disagree beyond a stated band; payout = FY DPS / FY diluted EPS on the same FY (NM when EPS <= 0); MLP distributions count for MLPs labelled "distributions"; `PaymentsOfOrdinaryDividends` maps to common dividends only after the Tag Mapper's coexistence check shows preferred is not inside (else per-company).
- Blocks: dividend yield, payout, dividends % FCF, TSY dividend term, dps growth, dividend streak.

**AC-14. TTM EPS, trailing P/E and PEG basis (42 section 6; S3 item 2)**
- Question: with no derived Q4 EPS, TTM EPS is unavailable almost everywhere. What are P/E and PEG?
- Options for P/E: (a) market cap / TTM net income attributable to common (NI to parent minus preferred dividends where filed), basis labelled; (b) market cap / TTM NI to parent (today's fallback, `price_metrics.py` 367-383); (c) price / latest filed FY diluted EPS (up to 12 months stale); (d) price / sum of four quarters only when all four are filed (rare, no Q4 10-Q).
- Consequence: trailing_pe rows using a derived EPS: 874 (top 1000), 3,334 (all); displayed diluted EPS from derived facts 5,263 Q4 cells (top 1000); negative P/E 117 (NA-5); PEG non-positive 328, and PEG reads "latest eps_growth_yoy", which can be a quarter row (S3).
- Recommendation: P/E (a), falling back to (b) only where the filing shows no preferred and no participating securities; TTM EPS not displayed as a number, show "FY<year> diluted EPS (filed)" plus the filed quarters; PEG = P/E (TTM basis) / FY-over-FY EPS growth, NM when either is NM or growth <= 0.
- Blocks: release of NA-1 without a basis change being shown unlabelled; trailing P/E, PEG, earnings yield.

**AC-15. Interest expense composition and interest coverage (R3 5.4; C8 interest; 27 D4; S3 item 3)**
- Question: (i) gross interest expense = debt interest + fees (+ finance-lease interest per AC-1), capitalized interest OUT, net tags never; (ii) operating interest for rental and captive finance (HTZ: 608 of 1,077 is vehicle interest tagged `InterestExpenseOperating`); (iii) net-only filers (VVX, UNIT) blank, with a company-scoped exception only with per-period composition evidence; (iv) coverage with an operating loss: NM or a negative value; (v) zero interest: "No interest expense".
- Options for (iv): (a) NM "operating loss"; (b) show the negative ratio.
- Consequence: cohort interest-expense capture defects 798 cells (doc 46); interest_coverage blank 788 (588 `incomplete:denominator`) (S3); FSDS: gross only 1,349, gross + income 867, net only 763.
- Recommendation: (i) as stated; (ii) operating interest in a separate template, excluded from the commercial coverage ratio; (iii) as 27 D4; (iv) (a); (v) as stated.
- Blocks: interest coverage, interest expense statement row for those shapes.

**AC-16. ROIC and ROE details (S3 item 4)**
- Question: ROIC tax term when pretax income <= 0 (statutory rate or NM); ROE and ROIC on average or ending capital.
- Options: (a) NOPAT = operating income x (1 - statutory 21%) when pretax <= 0, labelled; average capital where both ends are certified, ending otherwise, labelled; (b) NM when pretax <= 0; (c) ending capital always.
- Consequence: ROIC blank 422 in the cohort, mostly input gaps (S3); ROE negative 145.
- Recommendation: (b) for the tax term (no assumed rate on a loss), average capital where available. Blocks: ROIC, ROE wording.

**AC-17. A line that is not presented: zero or not applicable in a ratio? (S3 items 5, 6, 7)**
- Question: quick ratio with no inventory line (inventory = 0 so quick = current, or NP); cash conversion cycle without inventory (a separately named "DSO - DPO" variant, or NP); goodwill % assets with no goodwill line (0% or NP).
- Options: (a) inventory absent on a classified balance sheet = 0 for quick ratio; CCC NP (no variant under that name); goodwill % = 0% "No goodwill" when the face shows no goodwill and no goodwill note; (b) all NP; (c) all zero.
- Consequence (cohort, S3): quick_ratio 169 blank; CCC 598 blank with 359 companies inventory NP; goodwill_pct_assets 190 blank, goodwill NP 94.
- Recommendation: (a). Every zero here needs the NP evidence (FILING-CHECKED or an audited detector). Blocks: those three metrics.

**AC-18. Comprehensive income with no OCI statement (S3 item 11)**
- Options: (a) comprehensive income = net income when the filing states no OCI items; (b) NP.
- Consequence: 28 cohort blanks. Recommendation: (a) only with the filing statement; else NP. Blocks: 28 cells.

**AC-19. Restatement basis for series, growth and TTM (S3 item 13; R3 4.4; doc 37 mechanism 4)**
- Question: which basis does the product show, and may a series splice across a basis change?
- Options: (a) latest-filed (restated) basis for every period shown, and growth/TTM only from endpoints of the same filing vintage (MSFT FY2016 growth 0.6845 cross-basis vs 0.3777 same-basis); as-originally-reported kept as provenance; (b) as-originally-reported for every period (point-in-time view); (c) mixed (today).
- Consequence: MSFT FY2016-17, AJG FY2017 (6,249.0 restated vs 6,159.6 original), LLY recast gross profit, HON W4 (FILING-CHECKED in 22/36); population NOT MEASURED; part of S3 F5's 786 history blanks.
- Recommendation: (a) for display; (b) is a later backtest product. Cross-basis pairs are OPEN (NA-4 hides them now).
- Blocks: growth and TTM certification; AC-9 (viii).

**AC-20. Continuing-operations basis for CFO and FCF (R3 C13; 0.4)**
- Options: (a) FCF uses continuing CFO and continuing capex when the filer reports discontinued cash flows separately, total otherwise, never mixed within a series; (b) total always; (c) today: first_match picks the continuing total only when the plain total is absent for that period (series can switch basis).
- Consequence: AMD 9M CFO 5,109 includes 920 discontinued (FILING-CHECKED, R3); MGNC/LRDC put the total tag on a continuing subtotal (ledger); population NOT MEASURED.
- Recommendation: (a). Blocks: FCF certification for companies with discontinued operations.

**AC-21. Cash perimeter**
- Question: may `Cash` (excludes cash equivalents by definition) fill cash_and_equivalents (CDNL)? Restricted cash in or out? Insurer cash inside "total investments and cash" (EG)?
- Options: (a) `Cash` fills only when the filing states no cash equivalents; restricted cash OUT of cash and equivalents (balance sheet) but IN for the cash-flow reconciliation (ASU 2016-18); insurer cash via the insurer template; (b) `Cash` as a component: never fills.
- Consequence: CDNL ROIC cash input, PGR plain `Cash` for C&CE (ledger); counts NOT MEASURED (27 Q-C not run).
- Recommendation: (a). Blocks: net cash and EV for those filers.

Suggested accountant sitting order (by blocked reach): AC-1, AC-5, AC-6, AC-13, AC-14, AC-8, AC-10, AC-2, AC-9, AC-7, AC-15, AC-19, then the rest. AC-11, AC-12, AC-17-AC-21 need my extra fixtures first (section 5).

## 3. Held guards: my definition-level decision per guard

| Guard | Decision | Conditions before release |
|---|---|---|
| **R1(b) containment** (bare `LongTermDebt` dropped when it is smaller than N, C or half of the lease-combined noncurrent tag; MAR 23M -> 16,915M; 317 instants at 72 companies, 41-EVIDENCE) | **Approve.** A total cannot be smaller than its own parts on the same basis; the fallback path is an existing approved path. No accountant. | (1) Every guard-changed VALUE (not only blanks) is in the Verifier sample. (2) Include MAR, TSCO, CSGP, WTRG, DPZ, ALGM fixtures. |
| **R5 zero** (a 0 total beside a nonzero debt tag is recomputed without zero-valued role tags, else blank; 68 instants at 37 companies) | **Approve.** Arithmetic impossibility. | Blank reason persisted to the cell (finding 0.2). |
| **R5 floor, 2% tolerance** (total below a single filed instrument tag by more than 2% is not published; 664 + 16 instants at 122 companies) | **Approve as hide-only at 2%. Reject widening to 5%. Reject a blanket exemption of the company's own total path.** A wider tolerance or an exemption would publish values the guard cannot verify; that is an error rate in disguise. The 61 own-total rows (WMT, HIG, WY, SCHW, BIIB...) are counted as "possibly correct values hidden" and shown with the reason. | (1) Follow-up rule version (MINOR): exempt a row only when the difference equals a filed unamortized discount or issuance-cost tag for the same instant within rounding (face vs carrying explained by the filing's own numbers); never by percentage. (2) Banks (UMBF 44, EWBC 38 instants) are served by the bank template (total debt is in the bank suppression list), so the floor's bank blanks are moot at serve time; confirm in the dry-run. (3) Verifier reports the hidden-correct count. |
| **R4 preference filter** (a total_debt preference naming a single component is not applied; all 41 rows; WFC 25,168M -> 207,307M) | **Approve.** A component cannot be a total. | Preference rows stay in the database (as coded). |
| **Fallback overcount risk inside the guard set** (CVX 2016-12-31 43,330M -> 55,033M because DebtCurrent exceeds ST + LTD current; DPZ 2024 14.7M -> 3,825.8M while DebtAndCapitalLeaseObligations is 4,975M; PFE 2020, MMM, COR, PPG, DD: 12 instants unverified) | **Hold these subclasses.** A guard may only blank or fall to a path whose value is not contradicted by another filed debt tag. | Before release: the ~19 named instants are filing-checked or blanked; add a test that the fallback value never sits below a filed lease-inclusive total (DPZ) or above the filed parts' sum (CVX). |
| **No derived Q4 EPS/DPS** (held `derived.py`) | **Approve** as NA-1 + NA-2. | (1) Ship with or after the `price_metrics.py` anchor fix (lines 289-298 anchor all six TTM concepts on the latest diluted EPS quarter; without Q4 EPS, TTM revenue/CFO/capex go one quarter stale for ~3 months a year). (2) New `period_gap` cause "per-share, not filed separately" (migration) so blanks are not labelled `pipeline_bug`. (3) Existing derived rows retired by a reviewed dry-run (demote, never delete), not by the nightly stage. (4) P/E basis change shown labelled until AC-14; dividend yield hidden where it used a derived DPS until AC-13. (5) NA-3 FY per-share guard released with it (V, LEA). |
| **Revenue-total disagreement guard** | **Approve definition (NA-8, both directions, banks excluded). It does not exist yet; build it.** | (1) Data Engineer builds it from NA-8 (dry-run on the 201 companies first). (2) Verifier counts hidden-correct values (expected high, see NA-8). (3) NA-9 follows as soon as its 30-case sample passes. (4) Correct docs 46 W12 and 47 WO-9. |
| **Revenue structural rule** | **Approve the clean subset as a MINOR source-selection version (NA-9); hold the rest for AC-9.** | Doc 37 section 8 sample 30 of 30, independently derived; withdrawal on any selected value that is not the printed total, any identity passing by a sign flip, any selected fact outside the statement role. |

## 4. Definition versioning: passing the one-time test

The test: a later definition change must not force re-opening filings, re-mapping tags or redoing backfilled history. Today it fails (finding 0.3). Proposal for the Data Engineer (extends 0004 and R3 4.2; no new parallel tracker):

1. **Separate four layers; only the last depends on the definition.**
   - L1 source facts: `core.fact` (immutable, lossless) plus structure evidence per accession (presentation rows, calc arcs, contexts; WO-1.10).
   - L2 perimeter evidence: per company-period-slot, what the filing contains (`company_perimeter_slot`: inside_anchor / reported_separately / not_present / combined_inseparable / unknown, with fact ids and locators). This is a fact about the filing, independent of any definition.
   - L3 definition: concept id, version, slot include/exclude flags, conditions, rule IDs, approval (who, when), effective-from, supersedes.
   - L4 outputs: standardized values, states and metric values keyed by (definition id, version).
2. **Capture slots at the finest grain on the first pass, including slots the current definition excludes.** Finance-lease liability, interest and ROU amortization separately; software, intangibles and each PP&E line separately; depletion, debt-cost amortization, ARO accretion; NCI and preferred dividends; DPS declared and paid, per class; continuing vs discontinued cash flows; excise and contra-revenue lines; filing vintage of every input. Then flipping AC-1 (or any include/exclude flag) is arithmetic over stored L2 rows: recompute L4, no filing re-read. The only redo trigger left is a slot nobody captured; that is why the slot lists in R3 section 5 must be complete before any history backfill.
3. **Version classes.** PATCH = guard, state or evidence-detector change (changes states, not values; no accountant). MINOR = source selection within an unchanged meaning (NA-7, NA-9; values change; Verifier sample). MAJOR = perimeter or meaning change (any AC answer that differs from the running version; accountant approval; published diff per company; screens and statements switch together, coupled concepts move as one version, e.g. AC-1 moves debt, interest, D&A and FCF in one release).
4. **Never overwrite.** A new version writes new L4 rows; old rows are retired with `superseded_by`, not deleted; `metric_definition` gets a real version increment (stop the hard-coded `1` and the `on conflict do update`), and `metric_value`/standardized facts cite the definition version that produced them. The displayed value is "the active version"; a past screen can be reproduced (the Compustat re-standardization lesson, R3 section 1).
5. **Replay is a pure function.** Same L1 + L2 + definition version gives byte-identical L4 (determinism test). A version change runs the replay for affected companies only and emits a diff (company, period, old, new, reason) for the Verifier sample before the active pointer moves.
6. **Cache keys** = source hash + definition version + rule version (data-team/11 work limits); a new version reuses evidence, never stale verdicts.
7. **Interim, before the registry exists:** do not backfill history under any definition that an open AC card can change, unless the backfill stores the slot components separately (point 2). Guards (PATCH) are safe to run now because they change states only.

## 5. Effort and order (agent-days, ASSUMED; the calendar is set by the accountant and the Verifier, not by this work)

| Order | Work | Days | Depends on |
|---|---|---|---|
| 1 | NA-1, NA-6, NA-8 release packs: rule IDs, fixtures, test cases, reason text; revenue-guard build spec for the Data Engineer; reason-persistence condition | 2 | none (now) |
| 2 | NA-2 to NA-5, NA-7, NA-9 to NA-14 rule specs with fixtures (most fixtures exist) | 3 | none |
| 3 | Accountant packet: one page per AC card (this file) plus new FILING-CHECKED fixtures for AC-11, 12, 13, 14, 17, 18, 19, 20, 21 (about 3-5 filings each, SEC fair-access limits) | 5 | none; parallel with 1-2 |
| 4 | Machine-readable conditional rulebook (S3 -> rule table for `cell_state`), propagation tests | 3 | WO-1.5 storage design |
| 5 | Versioning spec for the Data Engineer (section 4 to table and test level) | 1 | none |
| 6 | Encode each approved AC answer as a versioned definition with fixtures and Verifier handoff | about 0.5 per card, ~10 | accountant answers |
| 7 | Composition-layer definitions seeded (WO-5.3) | 3 | K1 pass (WO-1.10), AC-1/5/6 answered |
| | **Total** | **about 27 agent-days**; about 14 before the accountant sits | |

## 6. Sign-off

**SIGNED WITH CONDITIONS.** WO-5 is doable and correctly scoped. Conditions:
1. A named accountant before any AC card changes a displayed value; until then those cells stay hidden with a reason (no interim guesses).
2. Held total-debt guards release only with blank reasons persisted to the cell (finding 0.2), the fallback-overcount subclasses checked or blanked, and the floor kept at 2% hide-only.
3. The revenue disagreement guard is built (it does not exist; finding 0.1) and docs 46/47 corrected before Gate B counts it.
4. The per-share non-derivation ships with the `price_metrics` anchor fix, the new `period_gap` cause and a reviewed retirement dry-run.
5. Real definition versioning (section 4) before any history backfill under a definition an open AC card can change.
6. NA-7 and NA-9 are treated as MINOR (no accountant) only if the founder's release policy accepts filing-proven source selection as non-definitional; otherwise they join AC-2 and AC-9.

## 7. Commands actually run, evidence, untested scope
- Commands: `wc -l` and `ls` on data-team; Read of the files listed at the top; `git status --short`, `git log --oneline` on `mapper/concept_fallback.py`, `normalizer/derived.py`, `mapper/concepts.py`, `mapper/revenue_resolvers`; `git diff --stat` and `git diff` on `concept_fallback.py` and `tag_investigator.py`; `git show a595b72 --stat`; `grep` over data-team, doc/data-moat, `pipeline/src`, `pipeline/db/migrations`; `sed -n` on `concept_fallback.py` 700-730, `definitions.py` 225-255, migration 0004 50-130, migration 0095 head; `python3 mind/mind.py search` x4.
- NOT_RUN: no database query, no SEC fetch, no filing opened in this run; every FILING-CHECKED label above is relayed from the cited file. No cohort cell counts per option (R3 section 9 impact plan). No Verifier review of R3/S3.
- Untested: whether any displayed metric reads a derived quarterly `pure` value (NA-2 condition); the fallback-overcount instants; the revenue guard's real reach on today's data; the CFO basis-switch frequency (0.4).
