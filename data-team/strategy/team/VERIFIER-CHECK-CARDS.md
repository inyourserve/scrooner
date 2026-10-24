# Verifier check cards: uniform template (WO-6 step 0, 2026-10-22)

Source: `team/WO-REVIEW-verifier.md` section 5 (template), section 2b (tiers), section 3b (independent evidence), section 4 (second reader), as accepted in doc 49 section 7.5 (C2, C3, C4). One card per family run (a rule family at one rule version over one population draw). A card extends `decision.json` (`data-team/16-DATA-VERIFIER.md`); where Cockpit consumes it, emit the JSON below; otherwise use the same fields as the markdown table. Cards are append-only: a re-run is a new card with `supersedes`.

## 1. Rules every card follows
1. **Independent pass first.** Write the expected interpretation from the filing before reading the proposer's rationale or our stored value.
2. **Frame from the population, not the hit list.** The sampling frame is the population query (rows the rule could apply to), so recall is tested too. Record the query text, the table watermark (`max(updated/checked_at)` or snapshot date) and the random seed.
3. **One cell per company per family**, so n counts independent clusters. Headline cards that need several cells per company quote the bound on companies, not cells.
4. **One finding fails the card.** The owner fixes the root cause; the next card draws a fresh sample (re-checking the old rows is not a pass). A child finding that still fails after replay reopens the root cause.
5. **Never write "the family is correct".** The result line reads: "every row passed checks X, Y, Z on independent evidence, and w of n random rows failed a filing check; at 95% the checks miss fewer than B%".
6. **Name the independent evidence** (section 3). FSDS, Frames or companyfacts agreement is never the sole evidence for a value-changing family or a "Not disclosed" state.
7. **Second reader on 10%** of every card's rows (seeded): Reader 1 (regex on R-file), Reader 2 (lxml on the iXBRL primary document), Reader 3 (edgartools 5.49.0 on instance + linkbases). Any disagreement is decided by reading the primary document page; the losing reader's failure mode becomes a test and every earlier check by that reader with the same signature is re-run.
8. **Evidence labels:** FILING-CHECKED (opened the filing, locator cited), DATA-INFERRED (our tables or a vendor), ASSUMED. Only FILING-CHECKED can verify a value or call a blank structural. If only DATA-INFERRED evidence is reachable, the verdict is `blocked`, not `verified`.
9. **Sign through the row's negation:** compare magnitude first, then sign through the printed row and the element's balance type (ANDE, BBW, CVX treasury stock: the R-file prints the negation of the stored fact).
10. **SEC access:** one fetch process through the shared flock limiter (`common/rate_limiter.py` lock file), declared `SEC_USER_AGENT`, at most 5 requests per second combined; cache by URL.

## 2. Tiers (choose one per card)
| Tier | Applies to | Random n (counts toward the bound) | Not counted in the bound | Pass rule |
|---|---|---|---|---|
| K | Certify rule precision at review severity | 10, sequential | none | 9 or more confirmed of 10 keeps the rule; otherwise demote or fix |
| P | Certify rule at wrong_value (gating) severity | 30 flagged | none | precision measured; any refute gets a rule fix before the rule gates certification |
| H | Hide-with-reason (guards, suppressions, states that only blank or relabel) | 30 from the hidden set | 10 risk-selected (restated, amendment, YTD vs discrete, sector, scale/sign) | 0 wrong reasons AND 0 correct-and-current values hidden by mistake |
| V | Value-changing (writes or replaces a shown value) | 60 changed rows | 15 risk-selected + 15 negative controls (rows the rule did NOT change) | 0 wrong among 90 |
| V+ | Value family over 5,000 changed cells, or headline cells | 100 | same as V | same |
| census | Population of 60 or fewer | all | | all correct |

Clean-sample bounds (one-sided 95%, exact binomial): n=10 25.9%; 30 9.5%; 60 4.9%; 100 2.95%; 300 0.99%; 1,000 0.30%.

Strata for V, V+, group and detector audits: group (corporate, bank, insurer, equity REIT, utility/energy/midstream, other financial) x era (2015-2017, 2018-2020, 2021+) x size (T1, T2 rest, T3) x period kind (FY 10-K, 10-Q quarter, derived Q4, instant). Proportional allocation, minimum 2 per non-empty stratum; strata under 2 rows are checked in full.

## 3. Independent evidence by family (the card names one; the card fails if it is missing)
| Family | Primary evidence | Not acceptable alone |
|---|---|---|
| Revenue total, operating income, gross profit | face row position in the primary iXBRL document + filer calc linkbase parent/children + face sum identity + Ex. 99.1 headline | FSDS value match |
| Total debt / composition | balance-sheet carrying lines + debt note maturity table + calc linkbase; finance-lease perimeter recorded | `LongTermDebt` alone |
| Q4 EPS/DPS guard, Q4 derivation, recast | Ex. 99.1 Q4 column; 10-K Item 302(a) note before 2021-08-09; same-vintage 9M comparative | FY minus 9M on our rows |
| Split basis, per-share | split note text + a later filing's split-adjusted comparatives + cover-share step | the split table |
| DPS rate-on-YTD | 10-Q 3-month vs YTD columns + dividend note declarations | |
| Restatement basis | both vintages opened + the accounting-policy note naming the method | latest-filed precedence |
| Identity / registrant / authority | EDGAR submissions JSON (name, formerNames, tickers, forms) + 8-K Items 2.01/3.01/5.03 + submission header FILER blocks + the instance's default-context `dei:EntityCentralIndexKey` + `dei:LegalEntityAxis` contexts | companyfacts entityName or attribution (wrong for 4 utility groups' Q2 2026 10-Qs, GATE-A file section 3b); accession prefix |
| Vocabulary mappings | face row label + statement role (pre linkbase) + calc parent; coexistence = usage evidence only | coexistence counts |
| TTM consecutiveness / staleness | date math (code) + submissions filing index + FC that the value is absent from the latest filing | our period table |
| Undefined-by-math (negative base, etc.) | pure math; FC the sign of the input (10 cases) | |
| Balance-sheet-date anchor | R2 balance-sheet date header + R1 cover date | |
| Group membership | face statement shape + SIC from submissions; FDIC BankFind for banks | data-value signals |
| not_presented / evidenced_zero / no dividend / no buyback / no R&D / no inventory | presentation linkbase (all roles) + dimension-only rows + notes + full-text search of the primary document for synonyms | label regex on one R-file |
| Headline certification | FSDS `num.txt` + `pre.txt` by code on every cell, then the primary document for the sample | FSDS alone |
| Market cap | cover shares FC per class, and no share-issuing event (merger close, split) after the cover date; price is a vendor value, say so | |

## 4. Card fields
```
card_id, family_id (33/36/46 id), rule_version, code_revision, proposer, verifier, date
claim: one sentence of what the rule asserts about each row
population: query text + watermark + N rows / N companies; frame drawn from population, not hit list
tier: K | P | H | V | V+ | census; seed; strata table (group x era x size x period kind) with n per stratum
n_random / n_risk / n_negative_control
independent_evidence_required: primary source; allowed secondary; forbidden-as-sole (section 3)
procedure: (1) write expected interpretation from the filing BEFORE reading the proposer's rationale;
  (2) open the source; (3) compare magnitude, then sign through the row's negation and balance type;
  (4) check period start/end, instant vs duration, YTD vs discrete, vintage, dimensions (incl. LegalEntityAxis),
      unit/scale, share class, registrant; (5) record the verdict
case rows: company, CIK, accession, form, locator (R-file/row or primary-doc section/table/row), printed label,
  tag, context start/end, dimensions, unit, scale, printed value, stored value, expected value,
  verdict {correct | wrong | correct_hidden_by_mistake | mislocated | definition_question | not_verifiable},
  evidence_label, reader (1/2/3), second_reader_agrees (for the 10% subsample), minutes
result: wrong count, hidden-by-mistake count, 95% upper bound on random n (and on companies), pass/fail
shared_source_disclosure: which evidence shares the filer XBRL or our parser
untested_scope; ledger lines appended; tag-inbox lines appended; next_action; supersedes card_id
```

### 4a. JSON skeleton
```json
{
  "card_id": "VC-<family>-<yyyymmdd>-<n>",
  "family_id": "", "rule_version": "", "code_revision": "", "proposer": "", "verifier": "", "date": "",
  "claim": "",
  "population": {"query": "", "watermark": "", "n_rows": null, "n_companies": null},
  "tier": "K|P|H|V|V+|census", "seed": null,
  "strata": [{"group": "", "era": "", "size": "", "period_kind": "", "n_population": null, "n_drawn": null}],
  "n_random": null, "n_risk": null, "n_negative_control": null,
  "independent_evidence_required": {"primary": "", "allowed_secondary": [], "forbidden_as_sole": []},
  "cases": [{"company_id": null, "cik": "", "accession": "", "form": "", "locator": "", "printed_label": "",
             "tag": "", "context_start": null, "context_end": "", "dimensions": [], "unit": "", "scale": null,
             "printed_value": "", "stored_value": null, "expected_value": null,
             "verdict": "correct|wrong|correct_hidden_by_mistake|mislocated|definition_question|not_verifiable",
             "evidence_label": "FILING-CHECKED|DATA-INFERRED|ASSUMED", "reader": 1, "second_reader_agrees": null, "minutes": null}],
  "result": {"wrong": null, "hidden_by_mistake": null, "upper_bound_95_cells": null, "upper_bound_95_companies": null, "pass": null},
  "shared_source_disclosure": "", "untested_scope": "", "ledger_lines": [], "tag_inbox_lines": [],
  "next_action": "", "supersedes": null
}
```

### 4b. Markdown form (when no machine consumer)
| Field | Value |
|---|---|
| card_id / family / rule version / code revision | |
| proposer / verifier / date | |
| claim | |
| population query, watermark, N rows / companies | |
| tier, seed, strata | |
| n random / risk / negative control | |
| independent evidence (primary; allowed; forbidden as sole) | |
| result (wrong, hidden by mistake, bound on cells and companies, pass/fail) | |
| shared-source disclosure | |
| untested scope | |
| next action / supersedes | |

Case table columns: company | CIK | accession | form | locator | printed label | tag | context start-end | dims | unit/scale | printed | stored | expected | verdict | evidence | reader | 2nd reader agrees | min.

## 5. Readers (tools, kept in the Verifier scratchpad until the Release Manager commits them)
- Reader 1: regex over SEC's rendered R-file (`scratchpad/scripts/rparse.py`; harness copy in `scratchpad/gateA/tools/three_readers.py::reader1`). Known blind spots: cannot see contexts (member and registrant rows look like totals), wrong statement pick, "Uncategorized" MenuCategory, footnote cells, rendered negation, scale in the title.
- Reader 2: lxml over the filer's iXBRL primary document (`three_readers.py::reader2`): `ix:nonFraction` by name and `contextRef`, contexts from `ix:resources` (period and every explicit member), applies `scale`, `sign`, `ixt` zero formats; reads the authored row label from the enclosing `<tr>`.
- Reader 3: edgartools 5.49.0 `XBRL.from_files` on the instance and linkbases, offline (`three_readers.py::reader3`; files fetched by `getfiling.py` through the shared limiter).
- Reader 2 and Reader 3 share the filer's XBRL (the instance is generated from the iXBRL document): they catch our parser's errors and Reader 1's, never a filer tagging error. Say so on every card.
