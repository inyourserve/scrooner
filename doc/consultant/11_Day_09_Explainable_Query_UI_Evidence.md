# Day 9 — Explainable Plain-English Query UI Evidence

> **Status:** COMPLETE FOR DAY 9 SCOPE  
> **Date:** 2026-08-19  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 9  
> **Repository gate:** GREEN — the expanded-metric regression drift was reconciled and the full pipeline suite passes.

## Executive outcome

Scrooner now lets a user describe a supported screen in plain English, inspect exactly what the bounded parser understood, resolve known ambiguity, transfer the interpretation into the structured editor, edit it, and deliberately execute it.

Interpretation and execution remain separate operations. The browser always calls `/v1/ask` with `run: false`; a successful interpretation is still not a screen run. Only after the user moves the criteria into the structured editor and presses **Run screen** does the browser call `/v1/screen`.

This preserves the core proposition: language makes discovery easier, while validated structured criteria and the deterministic Screener remain the source of query truth. Financial values continue to come from the existing metric pipeline, not the parser.

## What was built

### Plain-English workspace

- Multi-line screening input with `Ctrl/⌘ + Enter` interpretation support.
- Five selectable examples that the current deterministic parser genuinely supports.
- Honest “Bounded parser” positioning rather than a claim of general conversational AI.
- Distinct idle, interpreting, ready, ambiguous, unsupported, partially recognized, and API-error states.
- Original user text preserved through interpretation and error states.
- Exact interpreted JSON available through progressive disclosure.
- Recognized metrics, operators, values/ranges/rank counts, period policy, sorting, direction, limit, and universe scope displayed before handoff.

### Safe interpretation contract

The interpreter result now has two intentionally different fields:

- `query`: populated only when every clause is recognized and no ambiguity remains; this is the sole executable confidence gate.
- `recognized_query`: may contain clauses recognized inside a partially unsupported request, solely so the UI can explain progress. It never makes a partial request executable.

For example, `roe above 20% and magic number below 5` returns:

- `query = null`;
- a non-executable `recognized_query` containing `roe > 0.20`;
- `unrecognized = ["magic number below 5"]`;
- no result and no Screener execution.

Known ambiguous phrases such as bare “revenue growth” present explicit YoY and three-year-CAGR choices. Choosing one rewrites the phrase to a supported canonical alias and sends it through interpretation again; it does not bypass the parser or construct a query in the browser.

### Editable structured handoff

A confident interpretation can be copied into the Day 8 editor with **Review and edit criteria**. The transfer preserves:

- metrics and operators;
- exact percentage conversion without floating-point arithmetic;
- ranges and ranking counts;
- categorical predicates;
- sorting, direction, limit, and inactive-company scope.

The user receives a visible provenance banner showing the original English request. No screen runs until the separate structured **Run screen** action.

### Explainable results

Matched companies now include a **Why matched** disclosure that shows:

- each active financial or classification criterion;
- the actual matched value;
- the metric period and period end;
- the formula version used; and
- a link to the company page for filings and source context.

Metric headers link to an on-page definition section with the human definition, current formula, and catalog version. The result cell still reports its actual formula version so a future definition change is not silently conflated with historical output.

## Four verified browser interpretation contracts

The backend browser contract is tested for all four already-verified positive queries:

| English request | Confident interpretation |
|---|---|
| `companies with ROE above 30%` | `roe > 0.3` |
| `software companies` | `sic_code = 7372` |
| `debt to equity between 0 and 1` | `debt_to_equity between [0, 1]` |
| `top 3 by ROIC` | `roic top_n 3` |

Each returns `recognized_query == query`, with empty ambiguity and unrecognized lists. The UI exposes all four as supported examples or equivalent reference flows.

## Verification evidence

### Frontend

Run from `apps/app`:

```bash
npm test
npm run lint
npm run build
```

Results on 2026-08-19:

- Vitest: **2 files, 13 tests passed**.
- ESLint: **passed with zero findings**.
- Next.js production build: **passed**, including TypeScript and static generation.
- Built routes include `/screener`, `/api/ask`, `/api/metrics`, and `/api/screen`.

The new UI tests prove:

- supported language does not execute during interpretation;
- the request body explicitly carries `run: false`;
- confident criteria transfer into editable display units;
- execution happens only after the separate Run action;
- ambiguous input has no review/run handoff before resolution;
- an ambiguity choice is re-interpreted rather than trusted locally;
- partial recognition is displayed but remains non-executable;
- fully unsupported language is preserved for editing;
- match reasons include actual value, period, formula version, definitions, and company-source navigation.

### Backend API

Run from `apps/backend`:

```bash
.venv/bin/pytest tests -q
```

Result: **19 tests passed** in 0.59 seconds. This includes all four positive browser contracts, ambiguous-text non-execution, partial-recognition non-execution, Decimal preservation, metric catalog behavior, authentication, health, and saved-screen isolation. One existing FastAPI test-client deprecation warning remains non-blocking.

### Parser-focused pipeline tests

Run from the repository root:

```bash
pipeline/.venv/bin/pytest \
  pipeline/tests/unit/test_ai_query_smoke.py \
  pipeline/tests/unit/test_ai_query_complete.py -q
```

Result: **10 tests passed** in 0.13 seconds. The partial-recognition regression test asserts that `recognized_query` is visible while `query` remains null and `is_confident` remains false.

## Repository-wide regression status

The full pipeline command was also run:

```bash
cd pipeline
.venv/bin/pytest tests -q
```

Result after reconciliation: **129 passed, 1 deselected** in 0.60 seconds, with zero failures.

The repair updated the expanded-metric contract rather than weakening it:

- the composite-metric fixture now includes `cash_conversion_cycle` and its three day-metric dependencies;
- the positive case proves `45 + 60 - 30 = 75` days;
- the missing-dependency case proves an explicit `missing:debtor_days` null reason;
- the generic formula suite now proves exact Decimal results for debtor, inventory, and payables days; and
- catalog coverage asserts the complete named set of 17 expanded definitions instead of relying on a stale count.

## Definition of Done

| Gate | Result |
|---|---|
| Four verified positive queries work through browser contract | PASS — parameterized API test and UI examples |
| Interpretation shown before execution | PASS — separate `/api/ask` and `/api/screen` actions |
| Known ambiguous and unknown examples cannot execute | PASS — API and UI tests |
| Partial interpretation cannot be submitted accidentally | PASS — `query = null`; no editor handoff button |
| Interpreted criteria can be edited | PASS — exact structured-editor transfer |
| Exact interpreted and executed queries are visible | PASS — separate JSON disclosures |
| Results link to definitions and source-aware company details | PASS — metric anchors, match context, company links |
| Frontend lint/tests/production build pass | PASS |
| Repository-wide pipeline suite passes | PASS — 129 passed, 1 deselected, zero failures |

## Consultant assessment

The Day 9 product outcome is complete and correctly bounded. The most important decision is the two-stage interaction: Scrooner never converts “the parser understood something” into “execute immediately.” This is safer, easier to audit, and consistent with a research product whose differentiator is inspectable truth rather than conversational novelty.

The expanded-metric blocker is cleared. Day 10 can proceed to observability, backup/restore evidence, scripted usability sessions, and the private-beta go/conditional-go/no-go decision; those remaining Day 10 outcomes are not implied complete by this regression repair.
