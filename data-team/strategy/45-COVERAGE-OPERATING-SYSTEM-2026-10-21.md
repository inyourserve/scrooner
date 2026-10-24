# 45. The coverage operating system: the whole system, layer by layer (Ritwik, 2026-10-21)

This replaces "fix gaps one at a time" with one system in which a blank cannot exist unclassified. It joins doc 41 (templates), doc 42 (plan), doc 43 (strategy) and the measured baseline (doc 44). Sizing below is MEASURED on the live database for the top 986 companies (doc 44, 2026-10-21) unless marked; the layer designs are PROPOSALS. Five specialist reports (S1-S5) are running to harden specific layers; their results will be folded in as v2.

## 1. What the measured data says about the design (read first)
37,392 blank cells in 160,718 (fill 76.7%). Classified by their recorded reason:
| Class | Blanks | Share | What it really is | System layer that closes it |
|---|---|---|---|---|
| U0 no reason recorded | 13,349 | 35.7% | unclassified; 3,725 are sector-only / non-XBRL rows counted against everyone | L4 template + L5 state machine (classification is mandatory) |
| C1+C2 input missing (cascade) | 10,906 | 29.2% | a derived metric is blank because an input is blank | L3 dependency graph: fix leaves; propagate legitimate absence |
| D1 TTM/derivation input missing | 4,086 | 10.9% | four-quarter windows and YTD cash-flow items | L2 period derivation |
| H1 history window short | 2,839 | 7.6% | 10y CAGR for a young filer, missing prior period | L5 horizon state + ingestion |
| A1 line not on filer statements | 2,492 | 6.7% | evidence says the line is not presented | L5 state: not presented (evidenced) |
| M1 math undefined | 1,381 | 3.7% | negative growth, zero base | L5 state: undefined (evidenced by values) |
| T1 sector definition pending | 961 | 2.6% | bank/REIT/BDC definitions waiting | L4 template + accountant |
| X1 on filing, not extracted | 654 | 1.7% | real extraction defect | L2 resolution |
| E1 evidenced zero | 323 | 0.9% | non-payer etc. | L5 state: evidenced zero |
| other | ~400 | 1.1% | pre-revenue, implausible, immaterial base | L5 / L2 |
Three conclusions that shape everything below:
1. **Most blanks are not "missing data".** About 14% (A1, M1, E1, T1) are cells whose honest state is already evidenced; a further share of the 13,349 reasonless and 10,906 cascade blanks will resolve to the same states once classified. The system needs states, not more mapping.
2. **40% are cascades.** One missing leaf input blanks many metrics. The efficient lever is the dependency graph: fix and classify leaves, not metrics.
3. **Real extraction/mapping defects (X1 plus fixable leaves) are a minority** of the problem. Tag non-uniformity is real but is one lever of five.
Also measured: the 701 corporates hold 22,295 blanks, only 2,700 in rows blank for 90% or more of them; financial groups are 60-85% structural (bank 1,897 of 2,404 blanks sit in rows blank for 90%+ of banks). So templates matter most for financials, conditional states and leaf fixes matter most for corporates. Draft group sizes (unaudited): corporate 701, REIT 54, utility 50, other financial 49, bank 40, energy 34, BDC/unclassified 29, insurer 28.

## 2. Architecture: nine layers
- **L0 Sources.** SEC companyfacts, filing R-files, FSDS/FSN bulk sets (Range-read). Lossless; the Collector never transforms.
- **L1 Facts.** `core.fact` normalization with authority rules (10-K/10-Q family only, `is_authoritative` hard filter).
- **L2 Concept resolution.** Three cooperating paths per concept, with lineage stored:
  A. name path (vocabulary, today's mapper);
  B. structure path (statement position, label, calculation tree, identities) as candidate generator and wrong-value detector;
  C. composition (versioned definitions with included/excluded components, per-company perimeter; reported and standardized value).
  Agreement publishes; disagreement becomes a finding; structure-only becomes a candidate that needs coexistence check plus a Verifier sample.
  Period derivation (Q4, TTM, per-share pairing) lives here under the additive allowlist, calendar-aware windows, and "use the filed Q4 where the 10-K note carries it" for years before mid-2021.
- **L3 Metric graph.** Every metric is a node with named inputs (extracted from the definition modules). Each node computes from certified inputs or returns a state, never a silent null. Legitimate absence propagates by rule (no R&D line => R&D intensity is "not applicable", not a gap).
- **L4 Templates.** `company_group` (evidence-based shape signature, effective-dated per fiscal year, audited) + `metric_template` (group, cell, rule: REQUIRED / REPLACED / CONDITIONAL / not in template, definition version). Draft groups: corporate (utility and energy as variants), bank, insurer, equity REIT, mortgage REIT, BDC/fund, pre-revenue overlay, other financial (asset manager, broker, lender after shape review), non-screener.
- **L5 Cell state machine.** Each (company, period, cell) is in exactly one state, stored with its evidence reference:
  1. `value` (certified, filing locator) 2. `derived` (inputs listed) 3. `evidenced_zero` (no activity in the filing) 4. `undefined_by_math` (negative base, zero base; values prove it) 5. `history_horizon` (fewer years exist since listing or first XBRL filing) 6. `not_presented` (line not on the filer's statements, Verifier-confirmed where it shrinks the denominator) 7. `not_in_template` (group does not use the cell) 8. `defect(class, owner)`.
  Only states 1-3 and, with evidence, 4-6 count as covered. State 8 is the defect register. This replaces the free-text `gap_reason` column with an enumerated, evidenced state.
- **L6 Quality gates.** Invariants I1-I11 (certify), independent reconciliation to the SEC data sets, Verifier filing checks, instrument precision (false positive and miss rates measured, demote below threshold), and the release path: classify, dry-run, Verifier sample with zero wrong rows, Release Manager commit, separate first live run.
- **L7 Certification and serving.** Company state (uncertified, checks clean, reconciled, verified, certified); the page renders template cells only; badge, "why this number", restatement note, public scorecard; the screener honors group and state, default certified-only.
- **L8 Operating loop.** Nightly incremental: new filing => normalize => resolve => graph => template cells => states => incremental certify. Weekly scoreboard and Data Chief ranking. Yearly taxonomy diff. Quarterly group re-audit. Learning loop: every fix becomes a permanent artifact (tag card, template cell, rule, invariant, ledger line) so cost per company falls.

## 3. How blanks flow through the system (so nothing is left unclassified)
Every blank cell enters a fixed triage: (1) Is the cell in the company's template? No => `not_in_template`. (2) Is a condition false with evidence (non-payer, negative base, history horizon, input legitimately absent)? => the matching state. (3) Is the input in the filing? Yes and not captured => extraction/vocabulary defect (L2). (4) Is it derivable from filed pieces? => derived. (5) Else after a Verifier check => `not_presented` / "Not disclosed by this company". Anything left is a defect with an owner. The classification itself is code, run for every cell nightly, so the 13,349 reasonless cells cannot reappear.

## 4. Data model (proposal; extend existing tables, reuse 0093 and `certification_*`)
- `company_group(company_id, group, effective_from, effective_to, evidence_accession, audited_at)`.
- `metric_template(group, data_point, rule, definition_version, condition_ref)`.
- `metric_input_edge(metric, input, role)` (the dependency graph; seed from `metric_dependency_graph.csv` produced by S1).
- `cell_state(company_id, period, data_point, state, evidence_ref, defect_class, defect_owner, computed_at)`.
- Evidence layer: extend `company_filing_line_evidence`; structure tables only after the pilot passes (K-criteria in doc 42).
Size: modest. Cells 986 x 163 per period; the whole top-1000 current-period grid is 160,718 rows; with history on 33 concepts and 18 metrics from 2015 the state table is millions of rows, well inside the 14 GB headroom (database is 46 of 60 GB; ASSUMED row sizes).

## 5. Rollout (matches doc 42 gates, re-ordered by the measured classes)
1. **Classify first, then fix.** Compute `cell_state` for the cohort from existing data without changing any value: it replaces U0 with real classes and gives the true defect count. This is the single highest-value step and needs no accountant.
2. **Templates for the four first groups** (corporate, bank, insurer, REIT) + gating of the three sector-only rows + employee_count source decision.
3. **Conditional rulebook** (S3) for dividend, R&D, inventory, PEG, CAGR horizon metrics.
4. **Leaf fixes in rank order** from S1 (cascade attribution), then the held guards and release path.
5. **Structure path and composition** for vocabulary and perimeter defects; accountant-gated definitions.
6. **Certification, trust surfaces, population scale-out**, then nightly incremental and the yearly diff.

## 6. How we will measure the system itself (not just the data)
- Unclassified cells: 13,349 now => 0 (hard gate before any "covered" report).
- Defect register size and age by class; share closed by rule versus by hand (rule-closed share must rise).
- Cost per certified company in Verifier minutes and engineer-hours, cohort over cohort (must fall).
- False-positive and miss rate of each invariant (published internally weekly).
- Wrong-value rate per 1,000 cells in independent sampling (target 0 for released families).
- State mix per group, so denominator work is visible and cannot masquerade as progress.

## 7. Open design questions being answered by running reports
- S1: which leaf inputs explain the 10,906 + 4,086 cascade blanks, and what share is legitimate absence propagating.
- S2: audit of the draft group assignment against opened filings (misassignment rate per group, corrected rules).
- S3: conditional-metric rulebook: conditions, evidence, wording, coverage treatment, propagation rules.
- S4: what the 13,349 reasonless blanks really are, filing-checked sample.
- S5: how much of D1 and H1 is fixable derivation versus legitimate history horizon.
Open for the founder: name the accounting reviewer; approve the state model (incl. the single visible "Not disclosed" state); decide where employee count comes from (not an XBRL fact).
