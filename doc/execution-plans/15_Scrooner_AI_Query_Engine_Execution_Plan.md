# 15 — Scrooner AI Query Engine: Execution Plan

Screener Engine is done. This is the concrete build plan for Part 6 (AI Query Engine) — translating plain-English screening requests into the Screener's structured `ScreenQuery` schema (doc 14), with validation and visible interpretation. It does not relitigate anything already locked in doc 02/03/04/06 — it operationalizes them into something buildable, the same way docs 08/09/11/13/14 did for the earlier phases.

> **Status:** Canonical for 6a/6b (2026-08-17) — both stages built and verified, including running interpreted queries through the real Screener and reproducing doc 14b's already-verified results exactly. 6c (real LLM interpreter) stays unbuilt, pending a vendor decision that's the user's to make. Evidence: [doc 15b](15b_AI_Query_Engine_Definition_of_Done_Evidence.md). **Owner:** Founder / Product · **Review:** When a real LLM vendor is chosen for 6c, or when a core decision changes.

---

## Where this sits

```
PHASE 4   Company Master (4a + 4b-mock)  ✅ done
              ↓
PHASE 5   Screener Engine                ✅ done
              ↓
PHASE 6   AI Query Engine                ← this doc
              ↓
PHASE 7   Backend / Product API
```

**One-line job description**, from doc 04's data-flow step 8: *"AI query layer translates user language into the supported query schema; validation rejects unknown metrics or ambiguous clauses."* Doc 04's boundary table already gives this component its own row (unlike Company Master/Screener, which needed that gap resolved): **Can do** — interpret language into a supported schema and explain interpretation. **Cannot do** — generate financial facts or bypass deterministic filters.

---

## The one open decision, and how this doc handles it

Translating free text into a structured query needs *something* that parses language — normally an LLM. No LLM vendor/cost decision exists anywhere in doc 02, and unlike the market-price vendor (a fixed subscription-shaped cost), LLM API cost scales directly with usage in a way that's genuinely hard to estimate before this product has real users. Flagged to the user rather than assumed, same discipline as the market-price vendor decision.

**Resolved, by explicit user direction (2026-08-17): build the real validation/safety layer now, against a deterministic rule-based parser, not a real LLM.** Same shape as Company Master 4a/4b's split — the parts that don't need the open decision get built for real; the part that does stays behind a swappable interface. Concretely:

| Sub-phase | Scope | Blocked on |
|---|---|---|
| **6a. Interpreter interface + validation/safety layer** | The `NLInterpreter` contract, unknown-field rejection, ambiguity handling, "explain interpretation" output — all real, all tested | Nothing — buildable immediately |
| **6b. Rule-based interpreter** | A deterministic keyword/pattern parser implementing the interface, covering a defined, bounded query grammar | Nothing — this *is* what "mock LLM" means here, built for real, not a stub |
| **6c. Real LLM interpreter** | A second implementation of the same interface, backed by a real vendor | An LLM vendor/cost decision — not made here |

Swapping in 6c later means writing one new class against an interface 6a already defines and 6b already exercises end-to-end — not a redesign. This mirrors Company Master's `core.market_price` mock-to-real path exactly.

---

## What the AI Query Engine is allowed to do — and not

Doc 04's boundary table already names this row; this operationalizes it:

| Can do | Cannot do |
|---|---|
| Interpret a plain-English request into a `ScreenQuery` (doc 14's schema) | Generate a financial fact, a metric value, or a company list directly — every real answer still comes from the Screener querying `analytics.metric_value` |
| Explain what it understood, in plain language, before/alongside execution (doc 03's core user journey step 3) | Bypass the Screener's own validation — an interpreted query is *handed to* `run_query()` unchanged, never given special access to skip catalog/null-handling checks |
| Reject or flag a request it can't confidently map to the supported schema | Invent a metric, operator, or field the Screener's catalog doesn't have (doc 03's release gate: "No invented fields") |
| Ask for disambiguation rather than guess when a request is genuinely ambiguous | Silently reinterpret an ambiguous or unsupported request as a different, "close enough" screen (doc 03's safety gate) |

Writes: none. The AI Query Engine produces a `ScreenQuery` object; it never touches `core`/`analytics` itself, and it never calls `run_query()` on the user's behalf without the interpreted query being shown first (matching doc 03's "displays the interpreted filters... before or alongside execution").

---

## The real problems this phase has to solve

### 1. The rule-based grammar has to be small and honest about its limits, not pretend to be a real NL parser

A keyword/pattern matcher is not an LLM — it will fail on real phrasing variance. The failure mode that matters is **never claiming to understand something it didn't** (doc 03's safety gate again). Scope: a bounded set of recognizable clause shapes (comparison, `between`, `top_n`/`bottom_n`, sector), joined only by "and" (matching the Screener's own AND-only combination, doc 14). Anything outside that grammar returns an explicit "couldn't understand this part" response, never a best-effort guess.

### 2. Metric aliases need to be curated, not fuzzy-matched — same discipline as Mapper's concept mapping

Checked the real screenable catalog (14 metric_definition rows, `requires_price=false`) before designing this. A small, hand-curated alias table (`"return on equity"` → `roe`, `"debt to equity"`/`"d/e"` → `debt_to_equity`, etc.) — no fuzzy string matching, no LLM-guessed equivalence. Doc 12's own principle (adopted for `edgartools`, but the reasoning generalizes): a wrong auto-accepted mapping would silently corrupt a real result, so acceptance stays an explicit, reviewed list.

### 3. Some natural phrases are genuinely ambiguous against the real catalog — resolved by refusing, not defaulting

Checked directly: `revenue_growth_yoy` and `revenue_growth_3y_cagr` both exist as separate screenable metrics (same for `eps_growth_*`). A bare phrase like *"revenue growth"* doesn't unambiguously mean one or the other. **Decision**: the alias table maps only the *specific* phrasings (`"revenue growth yoy"`, `"3 year revenue growth"`/`"revenue cagr"`) to their exact metric; the bare, ambiguous phrase resolves to neither and the interpreter asks the user to specify — never silently defaults to one. This is the concrete mechanism doc 03's "ambiguity handled visibly" gate calls for, not just a principle restated.

### 4. Percentage values need correct unit conversion — checked against real stored data, not assumed

`analytics.metric_value` stores margins/returns as raw fractions (AAPL's ROE `1.199...`, not `119.9`) — confirmed directly from Screener verification. A user typing *"ROE > 30%"* means `0.30`, not `30`. The rule-based parser must divide any `%`-suffixed number by 100 before handing it to `ScreenQuery` — a small, easy-to-get-wrong detail worth stating as a deliberate, tested design point, not an afterthought.

### 5. Sector phrases map to SIC, with the same coarseness limitation the Screener already documented

Doc 14 already noted SIC is an *industry* code, coarser/different from "sector" as investors usually mean it. The AI layer inherits this limitation rather than pretending to fix it — `"software companies"` maps to a curated SIC-description alias (`7372`), not a semantic sector classifier.

---

## Interpreter interface — the concrete contract

```python
class NLInterpreter(Protocol):
    def interpret(self, text: str) -> InterpretationResult: ...

InterpretationResult:
    query: ScreenQuery | None        # None if nothing could be confidently interpreted
    explanation: str                 # plain-English restatement of what was understood
    unrecognized: list[str]          # clause(s) that couldn't be mapped, verbatim
    ambiguous: list[AmbiguityNote]   # phrase + the specific candidates it could mean
```

`query` is `None` whenever `unrecognized` or `ambiguous` is non-empty for anything that would materially change the result — a partial-but-silently-incomplete `ScreenQuery` is exactly the "invented field" / "silent reinterpretation" failure mode doc 03 rules out. Both the rule-based (6b) and any future LLM-backed (6c) interpreter implement this same interface, so `explain interpretation` and `ambiguity handled visibly` are structural properties of the contract, not something each implementation has to remember to do.

---

## Build sequence

| Stage | Deliverable | Gate before moving on |
|---|---|---|
| 6a. Interface + validation | ✅ **Done and verified 2026-08-17.** `ai_query/interpreter.py` — `NLInterpreter` Protocol, `InterpretationResult` (query only ever populated when nothing is unrecognized/ambiguous). |
| 6b. Rule-based interpreter | ✅ **Done and verified 2026-08-17, after 1 real bug.** `ai_query/aliases.py` + `ai_query/rules.py`. Found and fixed live: "companies with ROE above 30%" — the single most natural real phrasing among all test queries — failed to parse at all, because filler words ("companies with") weren't stripped before metric lookup. Fixed with a small, curated filler-prefix list. See `doc/learnings/ai-query-6a-6b.md`. |
| 6b-verify. End-to-end verification | ✅ **Done and verified 2026-08-17.** `doc/15b` DoD evidence. All 4 positive test queries, run through the real Screener, reproduce doc 14b's already-independently-verified results exactly — the strongest evidence available at this phase. |

3 build steps within 6a/6b — real 6c (the LLM interpreter named in the split table above) is out of this doc's build scope entirely, tracked as future work in "What this phase does not decide," not a step here with a placeholder gate. (Labeled `6b-verify`, not `6c`, specifically to avoid colliding with that name.)

---

## Test queries — concrete, hand-checkable against the Screener's own already-verified results

Reuses doc 14's own test screens as ground truth — if the NL layer parses these correctly, running them through the Screener reproduces results already verified in doc 14b:

| English | Expected `ScreenQuery` | Expected result (from doc 14b) |
|---|---|---|
| "companies with ROE above 30%" | `roe > 0.30` | AAPL, GOOGL, MSFT |
| "software companies" | `sic_code = '7372'` | MSFT, Block |
| "debt to equity between 0 and 1" | `debt_to_equity between (0, 1)` | JPM, NKE, AAPL, MSFT, Block |
| "top 3 by ROIC" | `roic top_n(3)` | AAPL, MSFT, Block |
| "revenue growth above 10%" | *(ambiguous — yoy vs. 3y cagr)* | `query=None`, `ambiguous=[...]`, no silent default |
| "companies with a magic number over 5" | *(unrecognized metric)* | `query=None`, `unrecognized=["magic number"]` |

---

## Definition of Done

**Output:** every supported clause shape (comparison, `between`, `top_n`/`bottom_n`, sector) parses to the exact `ScreenQuery` doc 14 would accept; every result includes a plain-English explanation of what was understood; an unsupported or ambiguous request never produces a partial/guessed query.

**Operationally, it can:** run a parsed query through the real Screener and get the same result doc 14b already verified for that query (end-to-end correctness, not just parser correctness); reject an unknown metric/field before it ever reaches `ScreenQuery` construction; be extended with a real LLM interpreter later without changing anything the Screener sees.

---

## What this phase does *not* decide

- **The real LLM vendor** — flagged to the user, not decided here; 6c stays unbuilt.
- **A general-purpose NL grammar** — the rule-based interpreter covers a bounded, documented set of phrasings, not open-ended language understanding. That's what 6c is for, eventually.
- **OR logic, nested groups** — inherited limitation from the Screener itself (doc 14); the AI layer can't produce what the Screener can't evaluate.
- **The 6 price-dependent metrics** — inherited from the Screener's own catalog scoping; becomes available automatically once Mapper's deferred follow-on computes them.

---

## Repository footprint

```text
pipeline/
├── src/
│   └── scrooner_pipeline/
│       ├── screener/           # done (Phase 5)
│       ├── ai_query/           # this phase
│       │   ├── interpreter.py     # 6a -- NLInterpreter protocol, InterpretationResult
│       │   ├── aliases.py         # 6b -- curated metric/operator/sector alias tables
│       │   └── rules.py           # 6b -- clause grammar, parsing
│       └── jobs/
│           └── ask.py              # NEW -- Typer CLI, takes English text, prints interpretation + (optionally) runs it through the Screener
└── tests/
    └── golden_companies/       # reused unchanged
```

No new migration — this phase writes nothing.

---

## Gotchas to watch for, specifically

- Don't let the rule-based parser's alias table grow via fuzzy matching "since it's close enough" — every alias is a deliberate, reviewed addition, same discipline as Mapper's `concept_mapping`.
- Don't return a `ScreenQuery` with a silently-dropped clause when part of a multi-clause request couldn't be parsed — the whole request should be flagged, not partially executed.
- Don't let `%` handling slip — test it explicitly, both with and without the sign, since a silent 100x error here would be a real, dangerous correctness bug in a financial product.
- Don't build 6c (a real LLM call) "since the interface is ready" — the vendor decision is still the user's to make.
