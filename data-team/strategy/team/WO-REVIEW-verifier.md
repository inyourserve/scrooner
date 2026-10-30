# WO-REVIEW: Data Verifier review of doc 47 WO-6 and every Verifier-sampled acceptance test (2026-10-22)

Role: Data Verifier (16). Objective: decide whether WO-6 can be done at its stated volume, size it, and propose the sampling, independence, reader and card rules that make "zero wrong rows" mean something. Scope: doc 47 (sections 1-4, every work order), doc 46, R7, S4, data-team/34, data-team/36, data-team/16, 21, 22, plus S2, R8 and code reads of `certification/` and `parsers/filing_line_evidence.py`. Review only. No code, no DB query, no SEC fetch, no commit. Evidence labels: FILING-CHECKED (FC), DATA-INFERRED (DI), ASSUMED (AS), CODE-READ (CR).

**Sign-off: SIGNED WITH CONDITIONS** (conditions C1-C8 in section 7). Without C1 (the "Not disclosed" rule), C2 (sample tiers) and C5 (capacity), it is NOT SIGNED. As written, WO-6 needs about 127 Verifier-days for T1+T2 alone. Gate E is day 90, and Gates A and B load about 17 Verifier-days into the first 10 calendar days.

## 1. Is WO-6 doable at the stated volume?

### 1a. Throughput (what one Verifier session actually does)
- SEC is not the bottleneck. My data-team/36 session fetched 260 SEC objects in one 10-minute window at a 0.35 s spacing (DI: scratchpad `sec/` file mtimes, 2026-10-21 01:00-01:10). One filing check is 3-5 requests: FilingSummary, 1-3 R-files, sometimes the primary document. The SEC limit (10/s) and our own limit (at most 2/s, one fetch process) allow about 1,400 filings an hour. The binding constraint is judgment time plus agent usage limits. Doc 46 section 7 says agents hit the account usage limit twice in one day.
- Measured judgment rates (DI, from my own runs):
  - Clustered scripted lookups: data-team/36 round 2 checked 33 cells in about 40-60 min, roughly 1.5 min per cell, because many cells shared a filing.
  - Root-cause filing reads: R7 covered 16 filings with root cause in about 1 h, roughly 4 min per filing.
  - Statement-level classification: S4 covered 40 filings in one session.
- Planning rates (AS, from the runs above):
  - 3-4 min per filing for a scripted headline lookup.
  - 5-6 min for a family case. That includes writing my own expected interpretation first, as the role spec requires.
  - 8-15 min for an investigative case (precision refute, new root cause, alternative reading).
  - About 6 effective hours per Verifier day after usage limits and DB windows.
  - That gives about 70 filings a day mixed, 100-120 scripted, 30-40 investigative.

### 1b. Total checks the plan implies (T1 top 100 + T2 top 986, as written)
| # | Source in doc 47 / 46 / 34 | Cells | Filing opens | Hours |
|---|---|---|---|---|
| A | WO-6.1 / Gate A: certify precision, 30 flagged cells per rule. About 35 rule ids under I1-I11 (CR, `certification/*.py`). 36 reuse about 100 cells | 1,050 | 450 | 60 |
| B | WO-6.1 identity id 1840, Entergy registrants (0000065984-26-000174), KO lag, WTRG; WO-1.2/1.3 combined-filer scan (Duke, Southern, AEP, other utility co-registrants) | 60 | 40 | 7 |
| C | Rule 1 / WO-6.2: about 30 per released family. About 61 families across Tier 0-3: about 23 Tier 0 (W1-W12, held guards, identity, registrant, E12, T4, T5, R-BASIS, R-SPLIT-BASIS, R-RATE-ON-YTD, R-STATEMENT-ROLE, R-MIXED-VINTAGE), about 8 Tier 1, about 17 Tier 2, about 13 Tier 3. Includes WO-2/3/4/5 "Verifier zero-wrong sample" acceptance tests | 1,830 | 1,500 | 125 |
| D | Rule 2 / WO-4.1: group audit 30 per group under the v2 rules. Sum of min(30, n) over 17 groups is about 255, plus about 35 corporates and captive-finance cases, plus a 30-company asset-manager and broker shape review | 320 | 320 | 27 |
| E | Rule 2 / WO-4.3 / doc 46 Tier 1.4: evidenced-state detectors, 30 per group with zero false positives. About 7 filing-evidenced detectors (not_presented, evidenced_zero, history_horizon, no dividend, no buyback, no R&D, no inventory), about 200 each | 1,400 | 1,400 | 117 |
| F | WO-6.3: "open the filing for every cell where the line is not presented". For the latest period in T2 that is about 11,000 cells (doc 46: A1 4,196, S4 class b about 4,200, about 69% of the 4,520 unevidenced leaves), at about 2 filings per company | 11,000 | 1,800 | 240 |
| G | WO-6.4 / 34 item 4: 11 headline cells x (latest FY + latest Q) = 22 per company. T1 100 companies, T2 10% (about 89), plus every reconciliation disagreement (AS 2-5% of 21,692 cells) | 4,900 | 1,070 | 107 |
| H | 34 history: FY2015/2018/2021 headline values on each certified company (T1 + T2 10%) | 6,237 | 567 | 57 |
| I | WO-2 named samples (MasTec, AAL, HON, PEP), 10 per-share pairing cases, WO-5 fixture checks (13 decisions), fixed regression set (golden-10 plus banks and REITs) | 300 | 166 | 22 |
| | **Total, as written, T1+T2** | **about 27,100** | **about 7,300** | **about 760 h = about 127 Verifier-days** |

T3 (about 4,200 companies) adds roughly the same again for D, E, G and H, plus up to about 8,000 filings if F is read literally. All counts are AS or DI arithmetic on the cited reports. Each one is re-measured when certify and `cell_state` run (Gate A).

**Verdict: not doable as written.**
- 127 Verifier-days does not fit a 90-day program.
- F alone (the literal "every cell") costs more than all of the value checks.
- Gate A (days 0-3) asks for about 500 filing opens, about 9 Verifier-days.
- Gate B (day 10) asks for about 23 Tier 0 families, about 10 more days.

### 1c. What deterministic checks can replace (from data-team/36 precision, S001/S002, 850 findings)
A deterministic check can replace a per-flag Verifier open only when three things hold:
1. Its measured precision is at or above the bound the tier sample would give.
2. Its evidence is independent of the value it judges (section 3).
3. A wrong verdict can only hide a value, never write one.

It never replaces the random audit of cells that pass all detectors. Data-team/36 shows recall is the weak side: NVDA had about 216 wrong cells and I9 flagged 2; Visa had 15 more wrong FY/zero cells than were flagged; JNJ FY2023 R&D was missed. Rule by rule:

| Rule (36 precision) | Replace the Verifier with | Residual Verifier check |
|---|---|---|
| per_share_derived_by_subtraction (282/282 as a class) | Policy plus code: `is_derived` and per-share means the cell is not shown. No value judgment is needed | 0 filings. A 5-row code spot check per run |
| dps_rate_on_ytd (31/31) | The signature: a YTD/FY value equals the same filing's 3-month value, plus a "quarterly" label | 10 per new population run |
| negative_on_nonnegative / DQC_0015 (13/13) | Quarantine by code (hide-only, never flip) | 10, sign-compared through the row negation (ledger ANDE/BBW) |
| share_basis_mismatch (456/486, 0 refuted, 30 mislocated) | Verify each **split event** once (the filed split note), then compute each cell's factor from its source filing date (R-SPLIT-BASIS) | About 1 filing per split event, plus 30 random cells. This replaces per-cell sampling of thousands of cells |
| statement_role_suspect (4/4) | FSDS `pre.txt` stmt/line (SEC's own parse, independent of our mapping) | 10 |
| layer_sign_conflict, I3/I4, per_share_basis_mix (21/21) | Keep as gating | 10 each |
| non_periodic_form (71%), mixed_vintage (86%), quarters_do_not_sum_to_year (50%), share_jump_without_split (67%), identity:gross_profit (0%) | **Not replaceable.** Apply 36's fixes first (recast-8K signature, face-line test, same-vintage FY = 9M + Q4 test, flag both sides of a jump). quarters_do_not_sum_to_year sits at the K2 line: demote to review | 30 each after the fix |
| Code-assertion rules: period-label lengths, duplicate_date_window, wrong_unit_family, stale_* date math, history_starts_after_window, unclassified_by_kind, sector_template | Their claim is a property of our own rows (dates, units, form), so code proves it | 0 filings for the property. Value consequences go into the family samples |

Two limits on this precision table. It comes from 17 megacaps, not a random draw over the 986, so Gate A must re-measure it on the top-986 run. It is also a cell-level estimate, not a population guarantee.

## 2. Sampling design that makes "zero wrong rows" meaningful

### 2a. What a clean sample supports (one-sided 95%, exact binomial; finite-population figures are hypergeometric)
| Clean sample n | Upper bound on the family's wrong-row rate | Note |
|---|---|---|
| 10 | 25.9% | Good only for a K2 decision: 9 or more confirmed of 10 rejects "over half false" (p = 0.011) |
| 30 | 9.5% | 0/30 on a 5,000-row family still allows up to about 475 wrong rows |
| 60 | 4.9% | On N = 1,427 (W10) up to 68 wrong rows are still consistent with 0/60 |
| 100 | 2.95% | |
| 300 | 0.99% | |
| 1,000 | 0.30% | |
| 3,000 | 0.10% | |

So a family sample cannot by itself prove "zero wrong rows" for any family over a few hundred rows. What it measures is the miss rate of the 100%-coverage deterministic checks (section 3) that run on every row. The gate statement must read: "every row passed checks X, Y, Z on independent evidence, and 0 of n random rows failed a filing check, so the checks miss fewer than B% at 95%." It must never read "the family is 100% correct".

### 2b. Tiers (proposed)
| Tier | Applies to | Random n (counts toward the bound) | Plus, not counted in the bound | Pass rule |
|---|---|---|---|---|
| K (K2 screen) | Certify rule precision at review severity | 10, sequential | none | 9 or more confirmed of 10 means keep. Otherwise demote or fix |
| P (precision) | Certify rules at wrong_value severity (gating) | 30 flagged | none | Precision measured. Any refute gets a rule fix before the rule gates certification |
| H (hide-with-reason) | Guards, suppressions, states that only blank or relabel (W1, W2, W6/W7, W8, W9, held guards, staleness, E12, T4, group gates, `cell_state` classes) | 30 drawn from the hidden set: was hiding right? | 10 risk-selected (restated, amendment, YTD vs discrete, sector, scale/sign) | 0 wrong reasons AND 0 correct-and-current values hidden by mistake |
| V (value-changing) | Anything that writes or replaces a shown value (W3, W4, W5, W10, W11, splits, vocabulary, derivation, readers, CIK links, Tier 3 definitions) | 60 changed rows | 15 risk-selected + 15 negative controls (rows in the target population the rule did NOT change, to catch "should have changed") | 0 wrong among 90 |
| V+ | A value family over 5,000 changed cells, or one touching headline cells | 100 | same | same |
| Census | Population of 60 or fewer (e.g. W4 HON class, 24 W5 companies, 12 split duplicates) | all | | all correct |

Rules:
- One finding fails the family. The owner fixes the root cause and the Verifier draws a **fresh** sample. Re-checking the old 30 is not a pass. A child finding that still fails after replay reopens the root cause (16 spec).
- Draw at most one cell per company per family, so n counts independent clusters. Where several cells per company are unavoidable (headline checks), quote the bound on the number of companies, not cells. A split or vintage error hits whole series (NVDA), so cell counts overstate independence.
- Sampling frames come from the **population query**, never from the proposer's hit list alone, so recall is tested too. Record the seed and the query watermark on the card.

### 2c. Stratification (every V/V+ and every group/detector audit)
- **Group:** corporate, bank, insurer, equity REIT, utility/energy/midstream, other financial (broker, asset manager, exchange, lender, crypto, BDC, mortgage REIT).
- **Era:**
  - 2015-2017: pre ASC 606/842, older tag sets.
  - 2018-2020: adoption years vary by filer (ledger: First Merchants, First Seacoast, Apple FY2019).
  - 2021+: Item 302(a) quarterly note gone after 2021-08-09.
- **Size:** T1, T2 rest, later T3.
- **Period kind:** FY 10-K, 10-Q quarter, derived Q4, instant.
- Allocation: proportional to population, with a minimum of 2 per non-empty stratum. Where a stratum has fewer than 2 rows, check all of them. S2 had to deviate (no market-cap field, so spacing was over CIK order), so the size stratum needs a stored market-cap rank that passes the I4 sanity check first (CLAUDE.md: AKTX $1.27T).

### 2d. What we publish as the error rate
- Family samples are risk-weighted and pre-release, so they cannot be the public rate.
- Publish a **separate rotating random audit of displayed certified cells:**
  - 300 cells a month: about 30 random companies x 10 random displayed cells, each FC.
  - Report "w wrong of n checked since <date>; 95% upper bound per 1,000 cells (exact)". Bound the result on the company count as well as the cell count.
  - After 3 months, 900 cells give a bound of about 0.33% if clean (about 3.3% on the 90 companies).
- Next to it publish:
  - wrong values found and fixed per month by any route (detector, Verifier, user report);
  - open defects by class.
- Never publish "0%" or "100% correct". Publish "checked against the filing; m found in n random checks". This matches doc 47 section 1 and the WO-10.3 scorecard.

## 3. The independent-evidence rule (so the gate is not circular)

### 3a. Checks that are NOT independent
| Check | Shares what | Can catch | Cannot catch |
|---|---|---|---|
| Certify I1-I11 over our tables | our data | internal inconsistency | anything consistent and wrong (recall, 36) |
| SEC Frames vs ours | same companyfacts, latest-filed by construction (CLAUDE.md 2026-10-18) | pipeline drops | filer errors, wrong latest filing, sign |
| companyfacts / companyconcept vs `core.fact` | `core.fact` IS companyfacts | load errors only | everything else |
| FSDS `num.txt` vs ours | same filer XBRL; SEC's parser, not ours | our parser, period, scale, dedupe and mapping errors | filer tagging errors, tag meaning (unless paired with `pre.txt`), custom-tag perimeter. FSDS lacks note facts (R7, DLH) |
| My R-file regex reader vs `parsers/filing_line_evidence.py` | both regex over SEC's rendered R-file, both pick the statement by title regex (CR, `_pick_report`) | | the same wrong statement pick (S2: 29 of 256 first picks wrong), MenuCategory "Uncategorized" (MA), footnote-cell shifts (CVX), parentheticals, rendered-sign negation (ANDE, BBW) |
| A sample drawn from the proposer's hit list | the proposer's query | precision | recall |
| A second agent reading the same extract | same evidence | | (16 policy: not independent) |
| `edgartools` vs ours | same XBRL, independent code | parser errors | filer errors |
| yfinance | different pipeline, vendor definitions | disagreement signals | never verifies or classifies (standing rule) |

### 3b. Independent source per family (the check card names one; the gate fails if it is missing)
| Family | Independent evidence (strongest first) | Not acceptable alone |
|---|---|---|
| Revenue total (doc 37), operating income, gross profit | Face row position in the primary iXBRL HTML (filer-authored label) + filer calc linkbase parent and children + face sum identity (rev - COGS = GP; GP - opex = OI) + earnings release Ex. 99.1 headline | FSDS value match |
| Total debt / composition | Balance-sheet carrying lines + debt note maturity table + calc linkbase (ledger CVX); finance-lease perimeter recorded | `LongTermDebt` alone (face value at AMZN/GOOG) |
| Q4 EPS/DPS guard, Q4 derivation, W4 recast | Earnings release Ex. 99.1 Q4 column (non-XBRL, separately prepared); 10-K Item 302(a) quarterly note before 2021-08-09; same-vintage 9M comparative | FY minus 9M arithmetic on our own rows |
| Split basis (R-SPLIT-BASIS), per-share | Split note text (narrative) + a later filing's split-adjusted comparatives + cover-share step | the split table itself |
| DPS rate-on-YTD | 10-Q 3-month column vs YTD column + dividend note declarations | |
| Restatement basis (R-BASIS, R-MIXED-VINTAGE, MSFT, LLY) | Both vintages opened (original and restating filing) + the accounting-policy note naming the method | latest-filed precedence |
| Authority / identity / registrant (W3, E6, E7) | EDGAR submissions JSON (form, CIK, name, former names) + R1 cover per registrant + `dei:LegalEntityAxis` context in the instance | companyfacts entity name |
| Vocabulary mappings (WO-3) | Face row label + statement role (`pre.txt` / presentation linkbase) + calc parent; population coexistence is evidence of usage only (DI) | coexistence counts |
| TTM consecutiveness / staleness (W1, W2, T5) | Date math (code) + submissions JSON filing index (shows the latest periodic filing) + FC that the value is absent from the latest filing (not a companyfacts lag, family B) | our period table |
| Undefined-by-math (W6, W7) | Pure math, no filing needed; FC only the sign of the input (10 cases) | |
| W10 anchor | R2 balance-sheet date header + R1 cover date | |
| Group membership | Face statement shape + SIC from submissions; FDIC BankFind for banks (government source, doc 32b) | data-value signals (S2 BDC failure) |
| not_presented / evidenced_zero / no dividend / no buyback / no R&D / no inventory | Presentation linkbase (all statement roles, not only the face R-file) + dimension-only rows + notes + full-text search of the primary document for the line's synonyms | label regex on one R-file (the production detector's own method) |
| Headline certification | FSDS `num.txt` + `pre.txt` stmt/line by code on every cell, then the Verifier opens the primary document for its sample | FSDS alone |
| Market cap | Cover shares FC (per class: GOOGL, BRK); price is Alpaca, a vendor, never filing-checkable: say so on the card | |

## 4. Parser risk and a second independent reader
- **Risk (CR, DI).** Every filing check I have run (R7, S4, 36, the ledger rows) went through one regex R-file reader (`scratchpad/scripts/rparse.py`). The production `not_presented` evidence (`parsers/filing_line_evidence.py`, migration 0093) uses the same method: title-regex statement pick plus first-cell label regex. A Verifier audit of the evidence detectors with my reader is therefore partly circular. Known failure modes in this reader family:
  - wrong statement pick (S2: 29 of 256);
  - "Uncategorized" MenuCategory (MA);
  - linkbases embedded in the `.xsd` (BLK, NTAP);
  - footnote cells shifting columns (CVX);
  - rendered negation (ANDE, BBW);
  - scale in the title;
  - member-only rows (CAT).
- **Proposal.**
  - Reader 2 is a structured reader of the **filer's own iXBRL primary document**, built on lxml (installed). For each sampled cell it finds the `ix:nonFraction` elements by element name and `contextRef`. It resolves period and dimensions from `ix:resources`, and applies `scale`, `sign` and `format`. It reads the authored row label from the enclosing HTML `<tr>` and the column header. This path does not touch SEC's renderer or any regex label match.
  - Reader 3 is `edgartools` 5.49.0. It is pinned and installed (CR, `pipeline/pyproject.toml` line 50) and unused anywhere in `pipeline/src` (CR). It renders statements from the presentation linkbase, which gives an independent statement-membership answer.
  - On a seeded 10% of every family sample and every detector audit, all three readers record value, sign, scale, period, dimensions, row label and statement.
  - Any disagreement: a human-level read of the primary document page decides, and the losing reader's failure mode becomes a test. Every prior check by that reader with the same signature is re-run.
  - Gate: 0 unresolved disagreements in the subsample. On about 500 double-reads, 0 disagreements bounds reader error near 0.6% (95%).
- Owner: Verifier tooling, kept as scripts and committed by the Release Manager. It writes nothing to the DB and needs no migration. Build effort about 1.5 days (AS).

## 5. Check-card template (one card per family run; JSON where Cockpit consumes it, same fields as a table otherwise; extends decision.json, 16 spec)
```
card_id, family_id (33/36/46 id), rule_version, code_revision, proposer, verifier, date
claim: one sentence of what the rule asserts about each row
population: query text + watermark + N rows / N companies; frame drawn from population, not hit list
tier: K | P | H | V | V+ | census; seed; strata table (group x era x size x period kind) with n per stratum
n_random / n_risk / n_negative_control
independent_evidence_required: primary source; allowed secondary; forbidden-as-sole (section 3b)
procedure: (1) write expected interpretation from the filing BEFORE reading the proposer's rationale;
  (2) open the source; (3) compare magnitude, then sign through the row's negation and balance type;
  (4) check period start/end, instant vs duration, YTD vs discrete, vintage, dimensions, unit/scale, share class;
  (5) record the verdict
case rows: company, CIK, accession, form, locator (R-file/row or primary-doc section/table/row), printed label,
  tag, context start/end, dimensions, unit, scale, printed value, stored value, expected value,
  verdict {correct | wrong | correct_hidden_by_mistake | mislocated | definition_question | not_verifiable},
  evidence_label, reader (1/2/3), second_reader_agrees (for the 10% subsample), minutes
result: wrong count, hidden-by-mistake count, 95% upper bound on random n (and on companies), pass/fail
shared_source_disclosure: which evidence shares the filer XBRL or our parser
untested_scope; ledger lines appended; tag-inbox lines appended; next_action; supersedes card_id
```

## 6. Order and effort (Verifier-days at about 6 effective hours; AS until Gate A re-baselines)
| Step | Days | When |
|---|---|---|
| 0. Card template, Reader 2/3 scripts, shared fetch queue (one SEC process feeding a cache that several Verifier sessions read) | 1.5 | days 0-1 |
| 1. Identity id 1840, Entergy registrants, KO lag, WTRG, combined-filer list (B) | 1 | days 0-2 |
| 2. Certify precision on the top-986 dry-run: K/P tiers, code-assertion rules by code (A', about 130 filings) | 2.5 | days 1-4 (after 0096/0097 are applied and the dry-run is done) |
| 3. Tier 0 families: held guards first (total debt, Q4 EPS/DPS, revenue total), then W1/W2, W6/W7, W10, W3, splits, rate-on-YTD, statement role, basis/vintage | 12 | days 3-12 (2 sessions) |
| 4. Group audit v2, new filings only, reusing S2's 256 FC openings (D') | 1.5 | days 8-15 |
| 5. Detector audit, one shared 255-company sample covering all 7 detectors (E') + visible "Not disclosed" census (F') | 15 | days 12-30 |
| 6. T1 headline certification (FSDS + `pre.txt` first) + history sample 2015/2018/2021 | 8 | days 20-45 |
| 7. Tier 2 value families (V/V+) as they land | 25 | days 15-60 |
| 8. Tier 3 definitions after accountant rulings, fixtures checked | 8 | days 30-75 |
| 9. T2 10% headline per batch + unexplained disagreements + monthly public audit | 10 | days 45-90 |
| **Total T1+T2 (amended)** | **about 84 Verifier-days (about 5,260 filing opens, about 13,000 cells)** | |
| T3 rollout (groups, detectors, 10% headline, history) | about 31 more | after Gate E |

The amended design checks more rows per value family (90 vs 30) and costs 84 days instead of 127. The saving comes from:
- turning F into a detector plus audit plus visible-state census;
- one shared company sample for all detectors;
- per-event split verification;
- code-proving the code-assertion rules;
- FSDS reconciliation before any filing is opened.

Gates A and B need about 17.5 Verifier-days of work by day 10. That is only feasible with **two Verifier sessions** sharing one fetch queue, or with Gate B moved to about day 18.

## 7. Sign-off: SIGNED WITH CONDITIONS
- **C1.** Rewrite WO-6.3 as: a deterministic `not_presented` detector using the presentation linkbase, notes, dimension-only rows and primary-document search (not the label regex alone); audited under tier H per group with Reader 2 on 10%; plus a Verifier census of every cell shown to users as "Not disclosed by this company". Opening every not-presented cell (about 11,000 latest-period, about 40,000 or more in the 2015+ window) is not feasible and adds no rigour over an audited detector.
- **C2.** Adopt tiers K/P/H/V/V+/census (2b). Replace "about 30 filings" in rule 1 with "30 for hide-with-reason, 60 + 15 risk + 15 negative controls for value-changing". Doc 47 WO-3 says "12-case sample each (30 if over 1,000 companies)". That stays the Tag Mapper's evidence, not the Verifier gate.
- **C3.** Every check card names its independent evidence (3b). FSDS/Frames/companyfacts agreement is never the sole evidence for a value-changing family or a "Not disclosed" state.
- **C4.** Second-reader subsample (section 4) before any detector audit counts toward a denominator change.
- **C5.** Capacity: two Verifier sessions through Gate C, or Gate B re-dated to about day 18. A Verifier sample is never shortened to meet a gate date; the gate slips instead.
- **C6.** Gate A precision is per rule, not per invariant (I5 holds rules from 50% to 100% precision, 36). Code-assertion rules are proven by code. The 36 precision is re-measured on the top-986 run before any rule replaces a Verifier check.
- **C7.** Headline certification runs FSDS `num.txt` + `pre.txt` reconciliation (34 P2) by code first. The Verifier opens T1 in full, T2 10%, every code-unexplained disagreement, and any FSDS-agreeing cell that is not on the face statement. [VERIFY] the lag of the quarterly FSDS behind the latest 10-Q before relying on it for the latest quarter.
- **C8.** The public error rate comes only from the separate rotating random audit (2d). It is reported as found/checked with an exact 95% bound per 1,000 cells, also bounded on companies. "Certified" means checks clean plus a sample clean, never "proven correct" (34 honest limit).

If C1, C2 or C5 is refused: NOT SIGNED. The plan would then gate denominators and certification on samples that cannot support the claims made from them, and on a schedule the Verifier cannot meet.

## Commands actually run
Read: data-team/20, 21, 22, 16, 34, 36; strategy/46, 47; team/R7, S4, S2, R8; `grep` of S5 and 33 headings; `parsers/filing_line_evidence.py` lines 140-235; `grep` of `certification/*.py` rule ids and `model.py` INVARIANTS; `pyproject.toml` (edgartools pin); site-packages listing (edgar, lxml present); `git log` on `filing_line_evidence.py` (a18dd40, 267010e, d7b296b); `mind search` (3 queries, no relevant hit); `stat` of my 2026-10-21 scratchpad SEC cache (fetch-rate evidence); `python3 -I` for the binomial and hypergeometric bounds and the volume tally. NOT_RUN: any DB query, any SEC fetch, any filing opened in this review (all FC labels are inherited from the cited reports).

## Untested scope
- Family counts (about 61) and cell volumes are AS/DI arithmetic on doc 46/47 and S1-S5. They are re-measured after the Gate A certify and `cell_state` runs.
- The per-filing minutes are DI from three runs, not a timed study.
- The 36 precision comes from 17 megacaps.
- The number of combined-registrant filers, split events and reconciliation disagreements in T2 is unmeasured.
- Whether S2's 256 openings kept enough per-company evidence for reuse depends on its scratchpad `meta.json` surviving. /tmp can be wiped.
