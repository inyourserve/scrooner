# 46 — AI Natural-Language Screen Creation: Planning and Scope

> **Status:** Execution-grade proposed specification; implementation evidence not yet attached  
> **Date:** 2026-09-15  
> **Owner:** Founder / Product  
> **Builds on:** `doc/execution-plans/15_Scrooner_AI_Query_Engine_Execution_Plan.md`, `doc/design/16_Simple_Language_Screener_Redesign.md`, `doc/faster-loading/fast.md`, and the existing `ScreenQuery` contract  
> **Decision required before the LLM phase:** provider, model, regional/data-retention policy, and acceptable per-query cost

## 1. Outcome

A user can describe a stock screen in ordinary language, including imperfect
spelling and common comparative phrases, and receive an exact, validated
`ScreenQuery` without learning internal metric names or mathematical syntax.

Examples the completed layer should understand:

- `profitable software companies with roe higher then 20 percent`
- `market cap at least 2 billion and pe no more than 18`
- `debt equity under one, excluding financial companies`
- `top 25 companies by 5 year revenue growth`
- `fcf yield above 5% or dividend yield greater than 4%`
- `companies with ROIC between 15 and 30 percent`

The system may correct `then` to `than`, resolve `debt equity` to
`debt_to_equity`, and normalize `no more than` to `<=`. It may not silently
decide whether an underspecified phrase such as `growth` means revenue growth,
EPS growth, YoY growth, or CAGR.

The AI layer creates query structure only. It never invents financial values,
selects companies itself, or bypasses the deterministic Screener.

## 2. Product principles

1. **Fast common path.** Deterministic parsing handles known phrases without an
   LLM call. AI is a fallback for language variance, not the first dependency.
2. **Correctness before apparent intelligence.** A rejected query is preferable
   to a confidently wrong financial screen.
3. **Visible correction.** Every material correction is shown as “We understood
   X as Y.” Users can undo or choose another meaning.
4. **One execution authority.** Only a validated `ScreenQuery` can execute.
   Neither browser code nor an LLM response can directly return companies.
5. **Catalog grounding.** Metrics, types, units, operators, periods, sectors and
   sortable fields come from the live metric/query catalog.
6. **No partial execution.** If one material clause is unresolved, the whole
   query remains non-executable.
7. **Deterministic replay.** The normalized query, catalog version, parser
   version and, when used, model/prompt version are recorded for reproducibility.

## 3. Current state and gap

Already implemented:

- typed `ScreenQuery` validation;
- a deterministic parser for comparisons, ranges, rankings, AND/OR and bounded
  categorical exclusions;
- curated metric, operator and sector aliases;
- percentage and magnitude conversion;
- explicit ambiguous/unrecognized results;
- deterministic Screener execution and cached screen runs;
- a results-first browser flow.

Missing:

- spelling and punctuation normalization;
- broader operator language such as `higher than`, `not more than`, and
  `maximum of`;
- safe approximate metric-name resolution;
- parentheses and mixed boolean expressions in natural language;
- multi-clause `between` parsing;
- conversational clarification state;
- a real catalog-grounded LLM fallback;
- confidence/provenance per interpreted clause;
- production evaluation, cost controls and AI-specific observability.

## 4. Scope boundaries

### In scope

- English natural-language screen creation and modification;
- spelling correction for metric and operator phrases;
- normalization of symbols, words, currency, percentages and magnitudes;
- supported metric, sector, ranking, range, sort, limit and boolean intent;
- clarification for ambiguity and conflicting clauses;
- deterministic-first and LLM-fallback routing;
- explainable corrections and structured interpretation;
- validation, caching, telemetry, evaluation and staged rollout;
- modifying an existing screen, for example `make ROE 25% instead` or
  `also exclude financials`, when the current normalized query is supplied.

### Out of scope

- generating investment advice, recommendations, target prices or narratives;
- generating or estimating missing financial data;
- changing metric formulas or accounting definitions;
- executing arbitrary SQL or accepting model-generated field names;
- backtesting or point-in-time screens;
- multilingual input in the first release;
- voice input;
- open-ended company research inside the query interpreter;
- silently choosing a period when multiple period metrics are plausible.

## 5. Interpretation architecture

```text
User text
   ↓
Input normalizer
   ↓
Deterministic lexer/parser ────────────────┐
   ↓ unresolved                            │ confident
Catalog candidate resolver                │
   ↓ unresolved/complex                    │
Grounded LLM fallback                      │
   ↓                                       │
Strict output-schema validation ←─────────┘
   ↓
Semantic + contradiction validator
   ↓
Correction/clarification policy
   ↓ executable only when fully resolved
Canonical ScreenQuery
   ↓
Existing Screener engine
```

### 5.1 Input normalizer

The normalizer is deterministic and side-effect free. It should:

- Unicode-normalize text and convert smart quotes/dashes;
- collapse whitespace without losing parentheses;
- normalize case only for matching, retaining original spans for explanations;
- recognize `%`, `percent`, `percentage`, `$`, `USD`, commas and decimals;
- normalize `k`, `thousand`, `m/mn/million`, `b/bn/billion`, and
  `t/tn/trillion`;
- normalize common punctuation variants such as `debt/equity`, `debt-equity`
  and `debt to equity`;
- detect common comparison typos such as `greater then` and `lesser than`;
- retain a span map from normalized tokens to the user's original wording.

Normalization must not change meaning. It can normalize spelling and syntax,
but semantic resolution belongs to later stages.

### 5.2 Deterministic parser

Expand the current parser rather than replacing it. It remains the preferred
path for queries it can fully resolve.

Required grammar:

- comparisons: `>`, `<`, `>=`, `<=`, `=`, `!=`;
- ranges: `between X and Y`, `from X to Y`;
- rankings: `top/bottom N by metric`;
- boolean groups: AND, OR, NOT, parentheses;
- category inclusion/exclusion;
- explicit sorting: `sorted by`, `highest first`, `lowest first`;
- limits: `show 25`, `first 50`;
- modifications relative to a supplied current query.

Use a token stream or small expression parser rather than continuing to split
raw strings on `and`. `and` inside `between X and Y` must be distinguishable
from boolean AND, and parentheses must establish precedence.

### 5.3 Catalog candidate resolver

Build a versioned in-memory search index from the metric catalog and curated
aliases. Each candidate carries:

- canonical `metric_name`;
- display name and approved aliases;
- value type and unit;
- period/horizon;
- formula version and short definition;
- screenable status;
- domain tags such as valuation, growth, profitability or leverage.

Candidate generation may use normalized token similarity, edit distance and
phonetic similarity. Candidate acceptance follows the correction policy in
section 7; fuzzy similarity alone is never execution authority.

### 5.4 Grounded LLM fallback

Call the LLM only when the deterministic path cannot fully resolve the request
or when the user is modifying an existing structured screen conversationally.

The model receives:

- user text;
- current query when editing;
- only relevant catalog candidates, not the entire database;
- supported operators and schema;
- unit rules and boolean grammar;
- strict instructions to return unresolved spans rather than invent fields.

The model returns structured JSON only. Its output is untrusted input and must
pass the same Pydantic/catalog/semantic validators as every other caller.

The model must never receive database credentials, raw SQL capability, company
result rows, or instructions from page/document content. User text is data,
not a system instruction.

### 5.5 Strict validation

Validation occurs after both deterministic and LLM interpretation:

- metric exists and is currently screenable;
- operator is compatible with the metric type;
- value parses exactly as `Decimal`;
- percentage and magnitude scaling is correct;
- range lower bound is below upper bound;
- `top_n`/`bottom_n` values are within product limits;
- boolean tree is structurally valid;
- sort metric exists;
- no clause or original text span was silently dropped;
- no conflicting constraints exist unless the boolean structure makes them
  intentional;
- requested period/horizon maps to an exact metric;
- generated query serializes to the existing `ScreenQuery` contract.

## 6. Operator and arithmetic normalization

Operator phrases should be centrally versioned and tested longest-first.

| User phrase | Operator | Notes |
|---|---:|---|
| greater than, higher than, above, over, more than | `>` | Strict |
| at least, minimum, no less than, not below | `>=` | Inclusive |
| less than, lower than, below, under, fewer than | `<` | Strict |
| at most, maximum, no more than, not above | `<=` | Inclusive |
| equal to, equals, exactly, is | `=` | `is` allowed only in a valid clause |
| not equal to, is not, excluding exact value | `!=` | Type-compatible only |
| between X and Y, from X to Y | `between` | Inclusive bounds |
| top/best/highest N | `top_n` | “Best” requires a metric; never infer one |
| bottom/lowest/worst N | `bottom_n` | “Worst” requires a metric |

Negated comparisons must be normalized logically, not textually:

- `not less than 10` → `>= 10`;
- `not greater than 10` → `<= 10`;
- `not between 10 and 20` requires a boolean expression (`< 10 OR > 20`),
  not a nonexistent operator;
- `not high debt` is ambiguous because `high` has no numeric boundary.

Percentage handling is metric-aware:

- `ROE > 20%` → `roe > 0.20`;
- `ROE > 20 percent` → `roe > 0.20`;
- `P/E < 20` stays `20`, never `0.20`;
- a percentage metric without `%` follows its documented input convention and
  the UI must show the normalized value before execution;
- basis points are deferred unless a metric/use case explicitly requires them.

## 7. Autocorrection and ambiguity policy

### 7.1 Corrections allowed automatically

Automatic correction is allowed only when all are true:

1. the intended canonical candidate is unique;
2. correction changes spelling/form, not financial meaning;
3. metric type and surrounding operator/value are compatible;
4. no second candidate is inside the configured ambiguity margin;
5. the correction is returned visibly to the client.

Examples:

- `retrun on equity` → `return on equity`;
- `greater then` → `greater than`;
- `debt equit ratio` → `debt_to_equity` when it is the unique candidate;
- `market captalisation` → `market_cap`.

### 7.2 Corrections requiring confirmation

- `revenue growth` → YoY, 3Y, 5Y or 10Y CAGR;
- `earnings growth` → EPS or net-income growth;
- `margin` → gross, operating, pretax, net or FCF margin;
- `return` → ROE, ROA or ROIC;
- `cheap companies` → no universal metric/threshold;
- `good companies`, `safe stocks`, `quality shares` → subjective intent;
- `large companies` → requires a market-cap threshold or approved preset;
- any correction where two catalog candidates are close.

### 7.3 Never autocorrect

- an unknown phrase into the “nearest” metric merely to make the query run;
- a missing numeric threshold;
- an unsupported period into a supported period;
- `and` into `or` or vice versa;
- an impossible/contradictory query into a looser one;
- company names into sectors;
- subjective language into undisclosed proprietary scoring.

## 8. Response contract

Extend `InterpretationResult` additively:

```json
{
  "status": "ready | needs_clarification | unsupported | invalid",
  "query": {},
  "recognized_query": {},
  "explanation": "ROE above 20% and P/E at most 15",
  "clauses": [
    {
      "source_text": "roe higher then 20 percent",
      "metric_name": "roe",
      "operator": ">",
      "normalized_value": "0.20",
      "resolution": "deterministic_alias",
      "confidence": "high"
    }
  ],
  "corrections": [
    {
      "source_text": "higher then",
      "corrected_text": "higher than",
      "kind": "spelling",
      "requires_confirmation": false
    }
  ],
  "ambiguities": [],
  "unrecognized": [],
  "versions": {
    "parser": "...",
    "catalog": "...",
    "model": null,
    "prompt": null
  }
}
```

`query` is non-null only for `ready`. Confidence is an audit/explanation field,
not a bypass around validation.

## 9. API scope

### Interpret and optionally create a run

`POST /v1/screen-runs` can retain the current one-action behavior, but its
interpretation portion should be factored into a reusable service. Add a
dedicated endpoint only if the UI needs clarification without execution:

```text
POST /v1/query-interpretations
{
  "text": "...",
  "current_query": null,
  "catalog_version": "optional-client-version"
}
```

The endpoint returns the response contract above. A ready interpretation may
then be submitted to the existing screen-run endpoint. To preserve the current
fast path, the server may interpret and run in one request when deterministic
resolution is complete.

### Clarification

Clarification responses should use stable candidate IDs, not trust metric names
sent back from arbitrary browser text:

```text
POST /v1/query-interpretations/{id}/clarify
{ "ambiguity_id": "growth-1", "candidate_id": "revenue_growth_3y_cagr" }
```

The server reconstructs and revalidates the complete query. A partial query is
never directly executable.

## 10. User experience

### Ready query

- Navigate immediately to the results page as today.
- Show a compact “Understood as” summary.
- Show non-material corrections without blocking.
- Allow undo/edit and expose exact filters.

### Needs clarification

- Stay on the results route with the query preserved.
- Replace the table skeleton with a focused clarification card.
- Show the original phrase and 2–4 human-readable choices with definitions.
- Choosing a meaning is explicit consent to complete and execute the query.
- Do not show stale results as if they answer the unresolved wording.

### Unsupported or invalid

- Highlight the exact unsupported span inside the query text.
- Keep confidently recognized clauses visible but clearly non-executable.
- Offer examples based on nearby supported catalog terms.
- Never auto-delete unsupported text.

### Correction disclosure

Use compact language:

> Corrected “retrun on equitiy” to “Return on equity (ROE)” and interpreted
> “no more than 20” as `≤ 20`.

Material semantic choices are never buried in a tooltip or closed disclosure.

## 11. Performance and caching

Targets:

| Path | p50 | p95 |
|---|---:|---:|
| Deterministic interpretation | <20 ms | <50 ms |
| Catalog candidate lookup | <10 ms | <25 ms |
| Cached full interpretation | <25 ms | <75 ms |
| LLM fallback | <800 ms | <2,500 ms |
| Valid cached screen to first rows | <150 ms | <400 ms |

Rules:

- do not call an LLM for a deterministic high-confidence match;
- pre-load the catalog index in process and version it;
- cache normalized interpretations by normalized text + current query hash +
  catalog version + parser version + model/prompt version;
- cache only validated structured outputs;
- negative-cache repeated unsupported inputs briefly;
- coalesce identical in-flight requests;
- preserve the existing immediate route transition and results skeleton;
- time out the AI fallback and return a recoverable clarification/error state;
- never fall back from an AI timeout to executing a partial deterministic query.

## 12. Security, privacy and abuse controls

- treat all user text as untrusted data;
- strict structured-output parsing with unknown fields rejected;
- catalog allow-list after model output;
- input and output length limits;
- per-user/IP rate limits and concurrency limits;
- prompt-injection tests (`ignore previous instructions`, SQL fragments, HTML);
- no secrets, SQL schema credentials or private user data in prompts;
- configurable provider retention/zero-data-retention policy;
- redact or hash query text in aggregate telemetry where raw text is not needed;
- do not train an external model on user queries without an explicit policy;
- record model/prompt versions, latency, token use and validation outcome;
- circuit breaker that disables LLM fallback while deterministic parsing remains
  available.

## 13. Evaluation strategy

Create a versioned golden corpus before enabling an LLM in production.

### Corpus categories

- canonical supported queries;
- spelling mistakes and phonetic variants;
- operator synonyms and negations;
- percentages, decimals, currencies and magnitude suffixes;
- AND/OR/NOT and parentheses;
- ranges mixed with other clauses;
- ambiguous metrics and periods;
- contradictory filters;
- unsupported metrics;
- subjective intent;
- adversarial/prompt-injection text;
- edits to an existing query;
- long/noisy mobile-input phrasing;
- real anonymized beta failures after review.

### Required metrics

- exact structured-query match rate;
- executable precision (most important);
- false-execution rate (target: zero in the release corpus);
- correct clarification rate;
- unsupported-span recall;
- correction acceptance/undo rate;
- deterministic-path coverage;
- LLM fallback rate;
- p50/p95 latency;
- cache-hit rate;
- token and monetary cost per successful screen;
- result parity with manually constructed `ScreenQuery` fixtures.

### Release gates

- 100% schema-valid outputs;
- zero invented metric names;
- zero partial execution in ambiguous/unsupported cases;
- 100% correct percent/magnitude conversion in the golden corpus;
- 100% preservation of explicit boolean grouping;
- deterministic repeatability for the rule path;
- manually reviewed LLM failures have a safe non-executing outcome;
- load and timeout behavior meets the budgets in section 11.

## 14. Observability

Emit one structured event per interpretation:

- route: deterministic, candidate-correction, LLM, cache;
- status and reason;
- parser/catalog/model/prompt versions;
- clause count and boolean depth;
- correction and ambiguity counts;
- latency by stage;
- token usage and estimated provider cost;
- downstream validation failures;
- whether the query executed;
- user correction/undo/clarification choice;
- resulting screen-run ID where permitted.

Dashboards should show false-execution incidents separately from ordinary parse
failures. Alerts are required for invented-field validation failures, sharp LLM
fallback-rate increases, latency regression, provider errors and cost spikes.

## 15. Build phases

### Phase A — Contract and corpus

Deliverables:

- additive response schema and clause/correction provenance;
- versioned golden corpus with at least 300 queries;
- production metric-catalog snapshot fixture;
- exact-match evaluator and regression report;
- baseline measurements for the current deterministic parser.

Exit gate: every existing query behavior is represented and passes.

### Phase B — Deterministic language expansion

Deliverables:

- tokenizer/expression parser;
- expanded operator normalization;
- spelling/punctuation normalizer;
- parentheses and mixed boolean support;
- multi-clause ranges;
- contradiction detection;
- tests for every mapping in sections 6 and 7.

Exit gate: high executable precision and no regression in existing screens.

### Phase C — Catalog resolver and safe autocorrection

Deliverables:

- versioned metric candidate index;
- unique-candidate correction thresholds;
- ambiguity-margin policy;
- visible correction payload;
- correction UI and undo behavior;
- offline threshold calibration from the corpus.

Exit gate: all automatic corrections are unique, type-compatible and visible;
semantic ambiguities remain blocked.

### Phase D — LLM adapter behind a feature flag

Deliverables:

- provider-neutral `LLMInterpreter` implementation;
- structured-output prompt and response validator;
- relevant-catalog retrieval;
- timeout, retry, circuit breaker and cost accounting;
- cache versioning;
- shadow evaluation with no user-visible execution.

Exit gate: provider/privacy decision recorded and release gates pass in shadow.

### Phase E — Clarification and conversational editing

Deliverables:

- clarification API/state;
- candidate-choice UI;
- current-query-aware modifications;
- stale-response and concurrent-edit handling;
- accessibility and mobile interaction tests.

Exit gate: ambiguous query → clarified result in two actions, with no partial run.

### Phase F — Controlled rollout

1. internal users, logging only;
2. 5% beta with LLM fallback shadowed;
3. 5% beta with safe fallback active;
4. 25%, 50%, then 100% based on weekly gates;
5. instant kill switch returns traffic to deterministic-only behavior.

## 16. Repository impact

Expected additions/changes:

```text
pipeline/src/scrooner_pipeline/ai_query/
├── normalizer.py
├── tokenizer.py
├── parser.py
├── resolver.py
├── validator.py
├── llm_interpreter.py
├── prompts/
└── evaluation.py

pipeline/tests/
├── unit/test_ai_query_normalizer.py
├── unit/test_ai_query_parser.py
├── unit/test_ai_query_resolver.py
├── unit/test_ai_query_validation.py
└── fixtures/ai_query_golden.jsonl

apps/backend/
├── routers/query_interpretations.py
├── services/query_interpretation.py
└── tests/test_query_interpretations.py

apps/app/
├── components/screener/QueryCorrectionSummary.tsx
├── components/screener/QueryClarification.tsx
└── corresponding component tests
```

No database migration is required for the first implementation if existing
structured logging/usage events cover telemetry. Persisted clarification
sessions should be introduced only if cross-device recovery is a real product
requirement; otherwise use a short-lived signed/cache-backed interpretation ID.

## 17. Decisions required

Before Phase D:

1. LLM provider and primary/fallback model;
2. maximum acceptable cost per interpreted query;
3. regional processing and retention requirements;
4. whether raw user query text may be retained for quality review;
5. free/paid LLM fallback limits;
6. maximum acceptable p95 LLM latency;
7. human review owner for new aliases and ambiguity rules.

Recommended default until those decisions are made: ship Phases A–C first,
retain deterministic-only execution, and keep `LLMInterpreter` disabled behind
a feature flag.

## 18. Definition of done

The AI layer is complete when:

- ordinary language and common misspellings resolve to exact supported metrics;
- comparative words map to the correct inclusive/strict arithmetic operator;
- values and units are normalized without precision loss;
- complex supported boolean/range queries produce exact `ScreenQuery` trees;
- all corrections are visible and reversible;
- genuine semantic ambiguity asks the user instead of guessing;
- no unsupported or partial request can execute;
- every executable output passes catalog and schema validation;
- the deterministic path remains fast and available without the LLM;
- AI outputs reproduce manually constructed Screener results exactly;
- evaluation, latency, cost, caching, privacy, observability and rollback gates
  are demonstrated with evidence rather than asserted.

## 19. Non-negotiable system invariants

These invariants are stronger than implementation preferences. A release that
violates one is incorrect even if aggregate accuracy looks high.

| ID | Invariant | Enforcement point | Required evidence |
|---|---|---|---|
| INV-01 | Only a catalog-valid `ScreenQuery` can reach the Screener | API/service boundary | Property test and API integration test |
| INV-02 | An unresolved or unsupported material span makes `query=null` | Interpreter result constructor | Golden-corpus negative cases |
| INV-03 | The LLM never returns companies, values, SQL or executable code | LLM output schema | Schema rejection and adversarial tests |
| INV-04 | Every source span is resolved, explicitly ignored as non-semantic filler, or returned unresolved | Post-parse coverage validator | Token/span coverage tests |
| INV-05 | Decimal values remain exact across text → query → API serialization | Normalizer and schema boundary | Precision tests with difficult decimals |
| INV-06 | Units are interpreted using the resolved metric type | Semantic validator | Cross-product metric/unit tests |
| INV-07 | Boolean grouping is preserved exactly | Parser/AST compiler | AST snapshot and result-parity tests |
| INV-08 | Automatic correction never changes financial meaning | Correction policy | Reviewed correction corpus; zero semantic auto-corrections |
| INV-09 | Cached output is invalidated by any input that can change interpretation | Cache-key builder | Cache identity tests |
| INV-10 | A model/provider failure cannot disable deterministic parsing | Router/circuit breaker | Fault-injection test |
| INV-11 | Replaying the recorded structured query yields the same screen for the same dataset version | Run persistence | End-to-end replay test |
| INV-12 | Client confidence labels cannot bypass server validation | Backend only | Tampered-client integration test |

The service should expose an invariant violation as a high-severity internal
error, not convert it into a user-facing “no matches” response.

## 20. Resolution confidence and correction calibration

“High confidence” must not be an intuitive label. Candidate resolution uses
measured scores calibrated against the golden corpus.

### Candidate features

- normalized token similarity;
- edit distance relative to phrase length;
- token-order similarity;
- abbreviation/alias exact match;
- phonetic match for common misspellings;
- metric type compatibility with the supplied value/unit;
- period/horizon compatibility;
- surrounding financial-domain terms;
- distance between the best and second-best candidates.

### Decision bands

Initial thresholds below are release hypotheses, not measured facts. Phase C
must tune them on held-out data and record the selected values in an ADR.

| Band | Initial rule | System action |
|---|---|---|
| Exact | Approved alias or canonical name exact after syntax normalization | Accept; syntax correction disclosure only |
| Auto-correct candidate | Top score ≥ 0.94, runner-up ≤ 0.78, type-compatible, spelling-only transform | Accept and visibly disclose |
| Clarify | Top score ≥ 0.75 but auto-correct conditions not met, or multiple semantic candidates | Present candidates; do not execute |
| Unsupported | No candidate ≥ 0.75 | Preserve and highlight source span; do not execute |

Additional guardrails:

- a short phrase of four characters or fewer requires an approved abbreviation
  alias; generic fuzzy matching is disabled;
- transposition/edit thresholds tighten for metrics with materially different
  meanings but similar names;
- candidate scores are logged, but raw scores are not presented as financial
  certainty to users;
- thresholds are versioned and included in the interpretation cache key;
- changes to thresholds require offline replay against current and previous
  golden corpora before rollout.

## 21. Failure taxonomy

Every non-ready outcome has a stable machine-readable code. UI copy may evolve;
code meaning may not change without versioning.

| Code | Meaning | Retryable | User action | Execute? |
|---|---|---:|---|---:|
| `EMPTY_INPUT` | No semantic query text | No | Enter criteria | No |
| `UNKNOWN_METRIC` | No catalog candidate | No | Reword or choose suggested metric | No |
| `AMBIGUOUS_METRIC` | Multiple plausible metrics | No | Choose meaning | No |
| `AMBIGUOUS_PERIOD` | Metric horizon not specified | No | Choose YoY/CAGR/period | No |
| `MISSING_VALUE` | Comparison has no threshold | No | Add value | No |
| `INVALID_VALUE` | Number cannot be parsed exactly | No | Correct value | No |
| `UNIT_MISMATCH` | Unit incompatible with metric | No | Correct unit/metric | No |
| `INVALID_RANGE` | Bounds reversed/equal where invalid | No | Correct bounds | No |
| `AMBIGUOUS_BOOLEAN` | Grouping cannot be proven | No | Add parentheses/rephrase | No |
| `CONTRADICTORY_FILTERS` | Conjunction cannot be satisfied | No | Edit conflicting clauses | No |
| `UNSUPPORTED_OPERATION` | Intent exceeds `ScreenQuery` | No | Use supported alternative | No |
| `CATALOG_VERSION_MISMATCH` | Client/server catalog changed | Yes | Automatic refresh/retry | No |
| `MODEL_TIMEOUT` | LLM exceeded latency budget | Yes | Retry or use exact syntax | No |
| `MODEL_UNAVAILABLE` | Provider/circuit open | Yes | Deterministic path remains available | No |
| `MODEL_OUTPUT_INVALID` | Output failed schema/allow-list | Yes once | Retry once, then stop | No |
| `RATE_LIMITED` | User/IP allowance exceeded | Yes | Wait/upgrade | No |
| `INTERNAL_INVARIANT_VIOLATION` | Safety contract failed | No automatic retry | Support/incident path | No |

API errors include `code`, safe `message`, `source_spans`, `retryable`, and a
correlation ID. Provider payloads and internal prompts are never returned.

## 22. Golden corpus design

The minimum initial corpus is **600 authored queries**, plus generated
property-based cases. The earlier 300-query figure is superseded here because
it did not define coverage and could have produced a misleadingly easy set.

### Authored corpus quotas

| Category | Minimum | Primary assertion |
|---|---:|---|
| Exact aliases and canonical metric names | 60 | Exact query equality |
| Natural operator variants | 60 | Strict/inclusive operator correctness |
| Spelling, punctuation and phonetic errors | 70 | Safe correction/clarification |
| Percent, decimal, currency and magnitude units | 60 | Exact Decimal normalization |
| AND/OR/NOT and parentheses | 70 | Exact AST equality |
| Ranges mixed with other clauses | 35 | Correct range tokenization/grouping |
| Ranking, sorting and limits | 35 | Exact ranking/sort/limit fields |
| Sector/category inclusion and exclusion | 35 | Exact categorical predicates |
| Ambiguous metric or period | 50 | Correct clarification, no execution |
| Contradictory or impossible constraints | 30 | Correct invalid state, no execution |
| Unsupported/subjective requests | 35 | Correct rejection, no guessed proxy |
| Conversational edits to existing queries | 35 | Correct query diff and preservation |
| Adversarial/prompt injection/noise | 25 | No instruction escape or execution |

Total minimum: 600. At least 20% of examples must contain two or more clauses;
at least 10% must contain four or more clauses. No single metric may represent
more than 15% of the corpus.

### Dataset partitions

- 60% development/training of rules and thresholds;
- 20% validation for threshold selection;
- 20% sealed release test set;
- paraphrases of the same logical query remain in the same partition;
- production failures enter a quarantine set first, receive human labels, and
  join the corpus only through review.

### Labels per example

- original text and locale;
- current query, if editing;
- expected status and error code;
- expected exact `ScreenQuery` or expected clarification candidates;
- source-span annotations;
- allowed automatic corrections;
- forbidden interpretations;
- rationale and reviewer;
- data/catalog/parser version;
- difficulty and risk classification.

Two reviewers resolve high-risk ambiguity examples independently. Disagreement
is measured and adjudicated; it is not silently converted into one “truth.”

## 23. Worked end-to-end examples

### Example A — safe spelling and operator correction

Input:

```text
software companies with retrun on equitiy higher then 20 percent
and debt equit below 1
```

Resolution:

```text
software companies                       → sic_code = 7372
retrun on equitiy → return on equity     → roe
higher then → higher than                → >
20 percent                               → Decimal("0.20")
debt equit → debt to equity              → debt_to_equity
below                                     → <
1                                         → Decimal("1")
```

Expected behavior: ready; show three corrections; execute only the canonical
query; return the same companies as the equivalent manually constructed query.

### Example B — semantic ambiguity

Input:

```text
companies with revenue growth above 15%
```

Expected behavior: `AMBIGUOUS_PERIOD`; no run. Choices include YoY, 3Y CAGR,
5Y CAGR and 10Y CAGR with short definitions. Selecting 3Y CAGR reconstructs
the entire query as `revenue_growth_3y_cagr > Decimal("0.15")`, revalidates it,
and then executes.

### Example C — boolean grouping

Input:

```text
(ROIC above 15% or FCF yield above 6%) and not financial companies
```

Expected AST:

```text
AND
├── OR
│   ├── roic > 0.15
│   └── fcf_yield > 0.06
└── NOT
    └── sector = Financials
```

Expected behavior: ready only if parentheses survive normalization and the AST
matches exactly. The LLM may not flatten this into three AND predicates.

### Example D — contradiction

Input:

```text
P/E below 10 and P/E above 20
```

Expected behavior: `CONTRADICTORY_FILTERS`; identify both source spans; no run.
The system must not silently retain only the last condition.

### Example E — conversational edit

Current query:

```text
market_cap >= 2B AND trailing_pe < 20 AND roe > 20%
```

User message:

```text
make PE 15 and also exclude banks
```

Expected behavior: update only `trailing_pe` to `< 15`, preserve market cap and
ROE, add the categorical exclusion, show a structured diff, and execute after
validation. “Make PE 15” preserves the existing `<` operator because the edit
is anchored to an existing clause; without a current clause, it would clarify
whether `15` means `<`, `=`, or another comparison.

## 24. Requirement-to-evidence traceability

| Requirement | Unit/property evidence | Integration evidence | Product telemetry |
|---|---|---|---|
| Metric typo correction | Resolver corpus tests | Interpretation API test | Correction acceptance/undo |
| Operator normalization | Phrase matrix tests | Exact query payload test | Operator clarification rate |
| Exact unit conversion | Decimal property tests | Result parity test | Validation failure by unit |
| Ambiguity blocks execution | Negative corpus tests | Tampered request test | Ambiguous execution count = 0 |
| No dropped spans | Span coverage property | API source-span assertion | Unrecognized-span distribution |
| Boolean preservation | AST snapshots | Screener result parity | Boolean parse failure rate |
| LLM catalog grounding | Output allow-list tests | Adversarial provider stub | Invented-field rejection count |
| Deterministic availability | Router unit test | Provider outage test | Deterministic success during outage |
| Cache correctness | Key property tests | Version invalidation test | Hit rate by interpretation version |
| Clarification UX | Component/a11y tests | Browser flow test | Completion/abandonment rate |
| Cost controls | Budget calculator tests | Rate-limit/provider stub | Cost per successful ready query |
| Rollback | Configuration test | Staging kill-switch drill | Time to disable LLM fallback |

Every release candidate attaches the test run, corpus version, metric snapshot,
latency report, cost projection and rollout decision to an evidence document.

## 25. Capacity and cost model

Do not choose infrastructure from a guessed user count. Measure these variables:

```text
Q = submitted interpretations per second at peak
D = deterministic-path fraction
H = interpretation-cache hit fraction among non-deterministic inputs
L = LLM requests per unresolved interpretation, including retries
T = average input + output tokens per LLM request
C = provider price per token (blended input/output)
S = average LLM service time in seconds
```

Derived planning values:

```text
LLM requests/second = Q × (1 - D) × (1 - H) × L
Expected concurrency = LLM requests/second × S
Monthly token cost = monthly queries × (1 - D) × (1 - H) × L × T × C
```

Capacity tests cover 2× projected peak and a provider slowdown at the p99
timeout. The service must shed LLM load without shedding deterministic traffic.

Initial operational budgets, to be replaced by measured product decisions:

- one LLM attempt normally; at most one retry for transport or invalid JSON;
- bounded catalog candidate context rather than the entire catalog;
- hard input/output token ceilings;
- per-user daily and burst limits;
- global concurrency semaphore;
- cost alerts at 50%, 80% and 100% of daily budget;
- automatic LLM circuit open at the hard budget while deterministic parsing
  remains operational.

## 26. Provider-selection rubric

No provider is selected by this document. A time-boxed bake-off uses the sealed
corpus and the same structured-output contract.

| Dimension | Weight | Evidence |
|---|---:|---|
| Executable precision and safe abstention | 30% | Sealed corpus |
| Structured-output/schema adherence | 15% | Invalid-output rate |
| p50/p95/p99 latency | 15% | Same-region load test |
| Privacy, retention and regional controls | 15% | Contract and configuration proof |
| Cost per successful ready interpretation | 10% | Measured token use and price |
| Reliability, rate limits and support | 10% | Fault/load test and SLA review |
| Portability/tooling quality | 5% | Adapter implementation assessment |

Any provider with a non-zero dangerous-execution result in the sealed corpus is
ineligible regardless of weighted score until the safety layer blocks it.

## 27. Privacy and retention matrix

| Data | Application storage | Provider exposure | Default retention | Access |
|---|---|---|---|---|
| Raw query text | Only if product policy permits | Only on LLM fallback | Short, explicitly decided | Restricted support/quality role |
| Canonical `ScreenQuery` | Persist with screen run | Not required after interpretation | Product run retention | Owning user/service |
| Correction/ambiguity metadata | Aggregate plus sampled reviewed cases | No | Defined analytics window | Product/quality |
| Model prompt/output | Redacted diagnostic sample only | Provider processes it | Minimum supported/zero-retention preferred | Restricted engineering |
| User/account identifiers | Internal correlation ID | Never | Existing account policy | Authorized services |
| Financial result rows | Existing screen-run policy | Never | Existing run policy | Owning user/service |

Before Phase D, record an approved data-processing decision covering provider
training, retention, subprocessors, region, deletion, incident notification and
whether raw prompts can be inspected by provider personnel.

## 28. Ownership, dependencies and effort

Effort estimates are planning ranges in focused engineer-days, not commitments.

| Phase | Directly responsible | Approver | Dependencies | Estimate |
|---|---|---|---|---:|
| A — contract and corpus | Backend/ML engineer + product reviewer | Product owner | Metric catalog | 8–12 |
| B — deterministic expansion | Backend engineer | Technical owner | Phase A fixtures | 10–15 |
| C — resolver/autocorrection | Backend/ML engineer | Product + technical owner | Labeled typo corpus | 8–12 |
| D — LLM adapter/shadow | Backend/ML + platform | Security/product owner | Provider/privacy decisions | 10–16 |
| E — clarification/edit UX | Frontend + backend | Product/design owner | Stable response contract | 10–15 |
| F — rollout/evidence | Platform + product analytics | Product owner | Staging/load/telemetry | 6–10 |

Cross-cutting reviewers:

- finance/domain reviewer approves semantic aliases and ambiguity labels;
- security/privacy reviewer approves provider data handling and threat model;
- accessibility reviewer verifies clarification and correction interactions;
- operations owner owns alerts, circuit breaker and incident response.

Critical path: A → B/C (partly parallel after contract) → provider decision → D
→ E integration → F. The deterministic improvements can ship before D.

## 29. Rollout scorecard and rollback

### Promotion gates

| Gate | Required condition |
|---|---|
| Internal → shadow | All invariants tested; sealed corpus passes; telemetry complete |
| Shadow → 5% active | Zero dangerous executions in shadow; cost/latency within budget |
| 5% → 25% | ≥1 week stable; no Sev-1/2 interpretation incident; clarification UX acceptable |
| 25% → 50% | Held-out precision unchanged; provider capacity proven at 2× expected peak |
| 50% → 100% | Two stable review windows; operations and support sign-off |

Numbers for “acceptable clarification UX” and precision are finalized from the
Phase A baseline and recorded before rollout begins; they cannot be relaxed
mid-rollout without an explicit decision record.

### Rollback triggers

- any ambiguous/unsupported query executes;
- any invented metric reaches the Screener;
- unit conversion produces a materially different threshold;
- p95 LLM latency exceeds budget for two consecutive windows;
- provider error rate or cost crosses the hard threshold;
- privacy or prompt-leak incident;
- validation rejection rate rises sharply after a version change.

Rollback order:

1. disable the affected prompt/model/parser version;
2. route all traffic to the last safe deterministic version;
3. stop new LLM requests with the circuit breaker;
4. preserve correlation IDs and redacted evidence;
5. invalidate affected interpretation caches;
6. identify screen runs created by the affected version;
7. notify users if a material incorrect interpretation reached execution;
8. re-enable only after corpus reproduction and corrective evidence.

## 30. Interpretation incident playbook

### Severity

- **Sev 1:** wrong/unsupported interpretation executed at scale, privacy leak, or
  cross-user data exposure;
- **Sev 2:** isolated materially wrong execution, systematic unit/operator bug,
  or rollback unavailable;
- **Sev 3:** safe rejection/clarification regression, elevated latency/cost, or
  provider degradation with deterministic fallback healthy;
- **Sev 4:** copy, ranking of clarification candidates, or non-safety UX issue.

### First response

1. activate the relevant kill switch;
2. capture correlation ID, versions and canonical query—not secrets;
3. determine whether the issue stopped before execution;
4. identify affected runs/users by version and time window;
5. reproduce with the recorded catalog/parser/model/prompt versions;
6. add the minimized case to quarantine regression tests;
7. correct rules/validation before prompt tuning when deterministic enforcement
   can prevent recurrence;
8. publish an evidence-backed incident review.

The incident review records impact, detection gap, invariant involved, why the
existing tests missed it, affected versions, remediation, corpus addition,
cache invalidation and user communication decision.

## 31. Evidence package required for “world-class” completion

This document is the specification, not proof of implementation. The feature
may be described as production-ready only when the repository contains:

1. an ADR recording provider, retention, thresholds and cost decisions;
2. the versioned 600+ query corpus and labeling guide;
3. an exact-query evaluator with sealed-set report;
4. unit/property/integration/browser/adversarial test reports;
5. deterministic and LLM latency/load measurements;
6. measured cost per successful screen and capacity projection;
7. a prompt/model/parser/catalog version manifest;
8. a security and privacy review;
9. a completed rollback drill;
10. staged-rollout scorecards;
11. incident-response ownership and alert verification;
12. a Definition-of-Done evidence report structured like doc 15b.

Until those artifacts exist, the honest status remains “execution-grade
proposed specification,” not “world-class production implementation.”
