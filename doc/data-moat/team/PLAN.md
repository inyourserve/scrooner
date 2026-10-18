# Data moat and coverage plan (mentor + Data Chief), 2026-10-18

Status: adopted by the mentor under the founder's delegation ("decide yourself, discuss with the team, go ahead"). Detail, day-by-day schedule and release-policy worksheet: `chief-plan-detail-2026-10-18.md`. Evidence trail: `log.md`. Everything stays reversible; nothing here changes the database by itself.

## Approach (changed after the Chief's challenge)
Work by **rule family**, chosen by **weighted reach to what users see**, verified by **sample**, checked by **code over the whole population**. Not company-by-company (only for the golden verification set and long-tail exceptions), not "map all tags" (12,013 unmapped; 3,534 used by five or fewer companies).

## What the Chief corrected in my first proposal (accepted)
1. **Correctness before coverage.** Known wrong-value classes go first: stored value differs from an authoritative copy (39 of 52,464 sampled rows), mislabeled period columns and full-year values under quarter labels, stale negative weighted-average share rows.
2. **"A cycle must move a number" was too crude.** New concepts grow the denominator. Use a fixed denominator for gains and a guard number that must not worsen; a held mapping that prevents a wrong value counts as a success.
3. **Denominator work must not look like a gain.** Report three states: value / proven-absent-from-face / unknown, with both denominators shown. `line_not_presented_in_filing` is evidence, not proof (14-34% of values we hold show no face line).
4. **Selection by rule family, weighted by company band** (top 100 / 1,000), not raw tag counts. A 12-case sample with 0 failures bounds the failure rate at only about 25%, so every family also gets a full-population code check.
5. **The apply step needs an approver.** See release tiers below.

## New finding that reorders the work (mine, measured 2026-10-18)
`analytics.metric_definition_input` has 88 inputs over 33 canonical concepts. The other 45 concepts, and all 10 face lines we just proposed, feed **no metric**. So the 10 proposals add data points but cannot raise the 74.61% metric coverage. To raise what users see, work first on the gaps inside the 33 consumed concepts and the metrics' own gap reasons (top reasons in the 2026-10-13 matrix: incomplete numerator 23,790; line not presented 13,903; incomplete add 10,645; incomplete subtract 9,332; incomplete denominator 8,121; missing ebitda_ttm 7,817; missing share_buybacks_ttm 5,652). The 10 face lines move to a second wave, or wait until a metric needs them.

## Order
1. **Wrong values out** (days 3-15): "authoritative same-tag copy wins" with precision tie-break and label-error detectors; weighted-average reprocess; verify by re-running the 150-company seed sample (target: 39 -> 0 except documented different-basis rows) and a fresh Verifier sample with 0 critical.
2. **Honest baseline and ledger** (days 1-5, parallel): fresh snapshot (the 2026-10-13 one is stale; diagnose why it stopped), three-state ledger, metric-to-concept inventory per metric.
3. **Metric-driven gaps in the 33 consumed concepts**: start with the biggest reasons above (EBITDA inputs, buyback inputs, incomplete numerator/add/subtract); each is a rule family with baseline -> propose -> define -> verify sample -> full-population check -> committed migration + reprocess -> re-measure.
4. **Quarter derivation** after step 1's upstream fix: additive allowlist only (cash-flow items, tax, pretax); EPS and shares by their own methods.
5. **Second-wave concepts** (the 10 face lines, then top tags by weighted reach) once a metric or page needs them.
6. **Sector templates**, banks first (1,339 companies with revenue but no gross profit).
7. **Financial Statement Data Sets** only after a size pilot (DB is 46 GB).

## Release tiers (mentor decision, because no accounting reviewer is named)
- **Auto-eligible after checks:** a single clean standard tag, exact match to the definition, full-population coexistence check shows no conflicting use, Verifier sample (12 cases, 30 if it feeds a locked metric or reaches 1,000+ companies) has 0 failures, applied by committed migration, with rollback and re-measure.
- **Proposal-only until a named human accounting reviewer approves:** anything that changes an accounting perimeter (APIC vs APIC-common, taxes Paid vs Net, preferred value, combined lines, fallbacks across tags), template/sector formulas, the existing `diluted_eps` / `net_income` priority-3 fallbacks (grandfather or revisit), and acceptance of the window-weight method for weighted-average shares.
- AI review never counts as accounting approval; labels say so.

## Decisions taken now (the Chief listed them as founder-only; made under delegation, reversible)
1. Headline KPI becomes the three-state ledger (value / proven-absent / unknown), not coverage %. Coverage % stays as a secondary number.
2. Foreign-private-issuer-only filers are outside the V1 operating denominator (already doc 02); the 83 companies with no 10-K stay in as UNKNOWN until diagnosed.
3. Derivation uses authoritative inputs only; conflicts resolve upstream first.
4. Restated periods store the latest-filed figure (decisions.md, 2026-10-18).
5. Financial Statement Data Sets: size pilot on one quarter first, no wider load without a measured size report.
6. Budget caps: batches of at most 10 rule families and 50 cases; model and Verifier time are capped per batch by those limits; cost telemetry is not available, so costs are reported as unknown, not guessed.
7. Coverage targets are NOT set until the fresh baseline exists.

## Still needs a person (cannot be decided by the team)
Name the accounting reviewer; adopt the written release policy (or keep batches proposal-only); set the acceptable wrong-value ceiling and freshness SLA; confirm that a transactional diff or company-subset replay can stand in for staging; confirm the sector scope the product promises at launch.

## Rules of engagement
`ListAgents` and a connection check before any heavy job; one connection per role task; `statement_timeout` set explicitly; schema changes only via committed migration (next number claimed in doc 53); read `git log` on a module before flagging it; commit named paths and push the same turn.
