# One path from filing to screen: design note (2026-11-16)

**Question from the founder:** we have the filings (FSN store), EDGAR, the resolver and the mapper, so why does coverage lag?

**Short answer:** the resolver usually finds the right line. The number then has to get through five more layers, and each one makes the same decisions again its own way. When two of them disagree, a right answer gets lost. On top of that, every proof rule change throws away every company's proof, including all the cells the change never touched.

## 1. What the numbers say

Latest live export on main (`top100-display-summary-20261115T2031Z.csv` and `top100-open-shown-cells-20261115T2031Z.csv`):

| | cells |
|---|---|
| Shown cells, top 100 | 44,154 |
| Shown with a proven value | 5,670 (12.8%) |
| Open | 38,484 |
| of which **proof missing at the current proof version** (`no_proof_row`) | **35,442 (92%)** |
| of which other work (section 6) | 3,042 |

- At export time, 82 companies had not yet been proved again under the current proof version, so their cells counted as unchecked. The 12 companies that had been proved again show **91.2%** of shown cells as proven values (5,670 of 6,218).
- One day earlier, the local flow log (`.runs/top100_flow/flow_results.tsv`, 2026-11-14, older "proven + reason" measure) had 74 companies at a **median of 99.0%**, 17 at 100%, and 1,449 open cells. The work had not gone away. A version change hid it.
- The proof version went from v1 to **v21 between 11-13 and 11-16** (`proof/prove.py` DETECTOR_VERSION and its pin test). Coverage reads only proof rows of the current version (`top100_coverage.py`, `_load_proofs`), so each change resets all 100 companies until they are proved again.
- The resolver file (`resolver-all110-2026-11-14.csv`, version .41) has 68,903 decisions and only 34 with no answer (`no_role`). Dhairya reports the resolver is right on 99.98% of cells that have an FSN filing. I did not re-measure that figure.

**Diagnosis confirmed:** most of the gap comes from plumbing and proving everything again, not from missing knowledge.

## 2. Today's path: what each layer decides again

| Layer (file) | Decides again |
|---|---|
| Docmap loader (`docmap_loader.py`) | Periods (its own era cut, `nearest_month_ends`), signs, combined lines, R page, hand-fix rows |
| Structural loader (`structural_loader.py`) | Turns resolver rows into tag date ranges. Period, sign, calc quarantine, member parts, false-reason guard, hand-fix predicate |
| Direct serving (`structural_direct.py`) | Picks the filing again (authority), period, sign, printed-zero, member parts, quarantine, false-reason guard, hand-fix predicate |
| Tag-map writer (`company_tag_map.py`, `_plan.py`) | Picks the filing again (latest filed), period match (`fact_options`), sign, combined, holds |
| Proof (`proof/prove.py`, `shown.py`, `identities.py`) | Which claim counts (`claim_for`), filing choice, sign, printed-zero, member parts, filer-calc lift |
| Display (`top100_coverage.py`) | Period lookup, combined-only matching, shown vs hidden, R page |

Every bug from the last two days was one of these concerns going wrong in one layer while another layer was right:

- 52/53-week fiscal year ends broke in four separate places.
- Authority (which filing copy wins) differed between serving and proof for NFLX, PFE and LRCX.
- Hand-fix rows beat the resolver.
- The false-reason guard and the filer-calc quarantine each had to be written twice.
- Printed-zero and member parts each needed three copies of the same code.

## 3. Target design

1. **Serving takes the resolver's decision and value**, keyed by filing and column. The loaders stop deciding again.
2. **Proof checks the same cell using the same shared functions.** It checks the cell's value against the filing, the balance-sheet identity, the calc ties and agreement between filing copies. It never picks a different claim or filing.
3. **Display reads the resolver decision** to choose shown or hidden: not presented means a hidden row, combined means a split, and a year before the first filing is a hidden year.
4. **Each proof verdict records the rules it used.** A rule change re-proves only the cells that used that rule. This fits in the existing `analytics.cell_proof.checks` field, so no migration is needed.

**One new shared module: `common/cell_rules.py`.** It is the only home for:

- period match: `fsn_end_matches`, the era cut and the month-end rounding
- sign: `polarity`
- authority: `face_column_eligible` and `latest_eligible`
- R page lookup
- filer-calc quarantine and lift
- printed-zero and member parts
- the hand-fix and false-reason predicates

The existing `common/` files become the parts it re-exports. Loaders, serving, proof and display may only call it.

**Deleted:** the docmap loader as a value path (docmaps stay as the template and as reading input to the resolver), the structural loader's date-range building, the tag-map writer's selection for resolver-decided cells, `claim_for`'s choice between competing claims, and the display layer's own period and combined matching. Hand-fix rows become resolver input instead of serve-time overrides.

**Stays:** the collector and FSN store, the resolver (Tag Expert tools), `company_tag_map` and `cell_proof` as the records, the identity checks, the certified guard and `scripts/top100_flow.sh`.

## 4. Migration: small steps, each shippable and measured

| # | Step | Size | Measured by |
|---|---|---|---|
| 1 | Rule-scoped proof versions: each verdict stores its rule IDs and versions, and coverage keeps a verdict whose rules did not change | ~1 day | Replay v20 to v21 on 10 companies, full re-prove vs scoped re-prove: the verdicts must match exactly |
| 2 | Create `common/cell_rules.py`. Move one concern per commit (period, sign, authority, page, quarantine, zero/member parts, predicates) and delete the copies | ~2–3 days, 7 commits | Each commit: served values before and after (dry run) must not change, and the pin keeps the same version |
| 3 | Serve resolver-decided cells directly, behind a per-company flag. Pilot on 10 diverse companies, then 100 | ~2 days | Dry-run diff of served values, certified guard, Ritwik's random draws on changed cells |
| 4 | Proof checks the resolver claim only (`claim_for` stops choosing) | ~1 day | Change in verdicts per company. Every new DISAGREE goes back to the Tag Expert as a resolver case |
| 5 | Display takes shown/hidden from the resolver decision | ~1 day | Before/after counts of hidden rows and years, with evidence for each hide |
| 6 | Delete the dead paths once the flag is on everywhere | ~1 day | Tests stay green, served values unchanged |

Total: about 8–10 working days, in steps that each stand alone. Step 1 does not depend on the others.

**During migration the per-company flow keeps its current chain:** docmap-load, structural-load, plan, proof, era guard, plan, proof, coverage, certified guard. Each step changes only what a stage does inside, for flagged companies. Companies without the flag run exactly as today. The certified guard still restores any certified cell that changes.

## 5. Risks and how each is caught

- **Resolver errors reach the screen with fewer checks.** Today the loaders sometimes catch them. Check: the proof keeps its independent tests (filing value, identities, calc ties, copy agreement). Before step 3, the 325 cells in `_resolver-all110-proven-disagreements-2026-11-14.csv` (where a proven served value differs from the resolver) must be resolved.
- **A bug in a shared function breaks serving and proof together**, so proof is less independent. Check: shared code decides *which* cell to look at, while the identities and the filing comparison decide *whether it is right*. Ritwik's random draws against the filing text continue.
- **A rule scope set too narrow skips a cell that should be proved again.** Check: rule IDs are recorded automatically when a rule runs, not declared by hand. A nightly full re-prove of a few random companies is diffed against the scoped verdicts.
- **Step 2 changes values without anyone noticing.** Check: a zero-diff dry run of served values per commit, mutation-checked tests, and the certified guard.

## 6. Expected effect on open cells

| Open work (11-15 export) | Cells | Expected effect |
|---|---|---|
| Proof missing at current version | 35,442 | Proving again clears it today. With step 1, a future rule change re-opens only the cells that rule touches (**estimate**: the 11-14 log suggests ~95%+ of these return as proven) |
| Plumbing-shaped: `derived_inputs_unproven` 533, `era_unmapped` 318, `reason_refused_comparative_presented` 280, `not_in_template_but_in_template` 82, `reason_own_filing_unverified` 60, `proof_unchecked` 46, wrong copy/claim/sum 37, other 12 | 1,368 | Steps 2–5 are expected to clear most of them (**estimate, not measured**) |
| Knowledge-shaped: shown reasons to fill or hide (`gap_fill`) 983, combined splits 360, held 139, no value and no reason 156, other 36 | 1,674 | Needs Tag Expert rules and reads. Step 5 makes the hide decision automatic once the resolver states it |

Not measured: how many of the 3,042 non-backlog cells clear without new knowledge. Step 3's 10-company pilot will measure it.

## 7. Recommendation

Do step 1 now: it is the cheapest step and removes the largest number. Then do step 2 one concern at a time, then pilot steps 3–5 on 10 companies before all 100. There is no big rewrite, and the per-company flow keeps running throughout.

**For approval:** "Approve one path: rule-scoped proof versions first, then one shared rules module (`common/cell_rules.py`), then serve and display straight from the resolver decision, company by company behind a flag, with zero-diff dry runs, the certified guard and Ritwik's draws as the gates."
