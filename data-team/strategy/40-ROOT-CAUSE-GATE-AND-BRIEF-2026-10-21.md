# Root-cause gate and brief for the product head (Dhairya for the founder, 2026-10-21)

## Founder direction (verbatim intent)
Once all 100 shards end with findings, do NOT solve immediately. Ask Ritwik, the product head, to apply strategic thinking and solve in a scalable manner, with strategy, not "x problem, x solution". For the whole set of findings: what is the ROOT CAUSE, what is the CORRECT solution, what is the SCALABLE solution, and how do we build a SYSTEM so that our fix becomes our moat.

## The gate (binding on the chief of staff and every data-team agent)
1. Trigger: every shard in doc/data-moat/team/top1000/status.md is `done` (S000-S102) and its rule-family table is final. Until then the campaign only FINDS.
2. Until the product head's root-cause pass is delivered and the founder accepts it: NO new family-by-family fix is released (committed to main) or applied. Analyses, dry-runs and designs that were already running may finish as EVIDENCE, but their code stays uncommitted, held by the Release Manager. In flight on 2026-10-21 and therefore held: total_debt guards (R1/R5/R4), the Q4 EPS change, the revenue-total rule. CORRECTION (2026-10-21): the certification suite's metric-row classification (not_defined_for_period_kind / insufficient_history / input_gap / no_row_inputs_present) is part of the MEASURING instrument, not a family fix, and is released. Already released and kept: the certification suite (it is the measuring system), bank suppression and staleness guard (they only hide a value with a reason), coverage honesty fix.
3. Allowed meanwhile: measuring (the certification suite on the cohort), verifying (filing checks), documenting evidence, keeping data safe. Not allowed: writing to the production database, new mappings, new derivations.

## What the product head is asked to deliver
A strategy, not a ticket list. For the full finding set (not one family):
1. **Root causes, by layer.** Group ALL findings into the few underlying failure classes of our system (candidates from the evidence, to be confirmed or replaced by Ritwik's own analysis: name-based tag mapping that cannot converge; no population-wide invariants so errors are found by hand; resolution by filing date instead of structure and authority; derivation by arithmetic for non-additive values; authority leaks from non-financial-statement filings; no stable entity identity across re-registration; ingestion gaps between the SEC feed and our filing table; honesty of our own measures; orchestration that cannot finish). For each class: the mechanism, the evidence (counts and FILING-CHECKED cases), why point fixes recur.
2. **The correct solution per root cause**, stated as the principle that makes the error impossible, not the patch that removes the observed instance.
3. **The scalable solution**: what works for 1,000 companies and 5,000, for 2015 to date, with fixed marginal cost per new company/filing/year; what is automated, what needs a human accountant, and where the Verifier's filing check is the gate.
4. **The system**: components, data they need, owners, the loop that keeps it correct as filings arrive (detect, classify, fix, verify, certify), and how learning compounds (tag cards, ledger, calibration, mind).
5. **The moat**: which parts of that system competitors cannot copy cheaply (filing-level provenance for every number, certified correctness state, structural mapping learned from every filing, a public data-quality scorecard) and how they show up to users.
6. **Build order and gates**: smallest vertical slice first, measurable gates, kill criteria, cost in agent-time and money, and the founder decisions needed (e.g. the named accounting reviewer).
Evidence labels required: FILING-CHECKED / DATA-INFERRED / ASSUMED / VENDOR-CLAIM. Recommend, do not decide accounting definitions.

## Evidence pack (all in the repo)
doc/data-moat/team/top1000/status.md (families), results/S###.md (per-shard), fix-register.md; data-team/22 (ledger), 21 (domain rules), 23-24 (primary-source and industry studies), 25-26-27-28-29 (Verifier and Standardization findings), 31 (Tag Mapper results, total_debt buckets, revenue precedence, shares), 33 (fix plan), 34 (certification program), 35-36 (Verifier GE/headline trial and certify dry-run findings), 37 (revenue-total rule, when delivered), tags/ (cards, INDEX, sources), strategy/37-39 (best-screener strategy, Ritwik's tag-uniformity diagnosis and structural-mapping PoC), and the certification suite output (`scrooner-certify --summary-only`) as the measuring instrument.

## What is already pointing the way (not decisions)
Ritwik's 38/39: map by the filing's own structure (presentation, calculation, arithmetic identities) as an independent second path beside name-based mapping, publish only on agreement, route disagreements to the Verifier. The certification suite makes disagreement measurable population-wide. These are inputs, not conclusions.
