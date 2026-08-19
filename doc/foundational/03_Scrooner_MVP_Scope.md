# 03 — Scrooner MVP Scope

The minimum lovable product, explicit exclusions, release gates and
definition of done.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When a core decision changes

---

## MVP outcome

Validate that serious retail investors will repeatedly use—and some will
pay for—a trustworthy plain-English screener for US company
fundamentals. The MVP is not complete when pages exist; it is complete
when the end-to-end query produces correct, explainable results.

## Core user journey

1.  A visitor lands on Scrooner through the homepage, a company page, a
    screen page or educational content.

2.  The user enters a plain-English screening request or starts from a
    curated screen.

3.  Scrooner displays the interpreted filters, metrics, periods and
    operators before or alongside execution.

4.  The user receives a sortable list of matching US-listed companies
    with the fields needed to understand the match.

5.  The user opens a company to inspect metric history, definitions and
    source traceability.

6.  After authentication, the user saves the screen and runs it again
    later.

7.  Limits communicate the paid value without preventing a meaningful
    free evaluation.

## In scope

| **Capability**      | **MVP requirement**                                                                      | **Acceptance signal**                                           |
|---------------------|------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| US company universe | Active US-listed operating companies with stable CIK/ticker identity.                    | Coverage and identity reconciliation pass.                      |
| SEC ingestion       | Raw submissions, company facts, filing metadata/documents and daily indexes.             | Repeatable runs with checksums and no silent loss.              |
| Normalization       | Canonical periods, units, signs and company/fact structures.                             | Golden-company tests pass.                                      |
| Metrics             | Approximately 15–20 well-defined fundamental metrics.                                    | Formula, source and edge-case tests documented.                 |
| Operators           | Approximately 10 useful comparison/logical operators.                                    | Common screens execute consistently.                            |
| Prompt parser       | Converts supported English into a validated query schema.                                | Unsupported intent is rejected or clarified safely.             |
| Results             | Fast, sortable company list with interpreted criteria.                                   | Users can see why a result matched.                             |
| Company pages       | Essential profile, financial history, metrics and provenance.                            | Pages are useful and indexable where appropriate.               |
| Saved screens       | Authenticated create, name, view, rerun and delete. Public/indexed screen pages (`/screens/{slug}/`) are deferred with the rest of the SEO/Content Engine (see below) — not required for MVP. | State persists reliably.                                        |
| Public web          | Homepage, product explanation, pricing placeholder/plan.                                 | Fast, crawlable, canonical pages.                               |
| Admin/operations    | Inspect companies, jobs, mappings, data freshness and failures.                          | Operational issues can be diagnosed without SQL-only workflows. |
| Basic monetization  | Free limits plus one simple annual premium plan.                                         | Entitlements and limits behave correctly.                       |
| Observability       | Job logs, error tracking, freshness checks and basic product analytics.                  | Failures and stale data generate visible signals.               |

## Initial metric families

- Company/market: market capitalization and basic listing identity.

- Growth: annual revenue and multi-year revenue growth/CAGR.

- Profitability: gross/operating/net margins where reliable.

- Returns: ROIC using one canonical published formula.

- Cash flow: operating cash flow, capital expenditure and free cash flow; positive-FCF consistency.

- Capital structure: debt/leverage essentials and share-count dilution.

- Per-share/valuation metrics only where inputs and period alignment are dependable.

The exact metric catalogue is an open decision and must be frozen before
Mapper implementation. “Approximately 15–20” is a hard scope guardrail,
not permission to improvise.

## Explicitly out of scope

| **Excluded from MVP**                         | **Why**                                                                  |
|-----------------------------------------------|--------------------------------------------------------------------------|
| Real-time quotes and trading                  | Cost, operational complexity and no contribution to the core validation. |
| Technical analysis and indicators             | Different user/job; dilutes the fundamental-screening wedge.             |
| News aggregation and sentiment                | Requires separate ingestion, rights and trust workflows.                 |
| Earnings-call summarization                   | Useful later, not necessary to prove screening value.                    |
| Portfolio tracking and brokerage execution    | Large integration and compliance surface.                                |
| Analyst forecasts/consensus                   | Licensed data dependency and inconsistent availability.                  |
| Global exchanges                              | Would multiply mapping, currency and regulatory complexity.              |
| Investment recommendations or target prices   | Scrooner is a research tool, not an adviser.                             |
| Open-ended finance chatbot                    | Hard to constrain, audit and differentiate.                              |
| Custom formula builder and complex dashboards | Premature power-user scope.                                              |
| Native mobile apps                            | Responsive web is sufficient for MVP.                                    |
| B2B/public data API                           | Deferred until stable demand appears.                                    |
| Glossary, guides and public/indexed screen pages | Content, not core screening validation; ships as the SEO/Content Engine phase after MVP (doc 06, Part 12). |

## Delivery sequence

| **Stage**                      | **Deliverable**                                  | **Gate**                                                 |
|--------------------------------|--------------------------------------------------|----------------------------------------------------------|
| 1\. Collector                  | Lossless SEC raw layer and ingest metadata.      | Completeness, idempotency, resume and fair-access tests. |
| 2\. Normalizer                 | Reliable canonical facts and periods.            | Golden-company reconciliations.                          |
| 3\. Mapper/Metrics             | Versioned concepts and formulas.                 | Manual filing comparison and regression suite.           |
| 4\. Company master/market data | Stable identity plus delayed/EOD market inputs.  | Ticker-change and freshness handling.                    |
| 5\. Deterministic screener     | Structured query engine and result set.          | Known screens produce expected companies.                |
| 6\. AI query layer             | English-to-query translation with validation.    | No invented fields; ambiguity handled visibly.           |
| 7\. Web/app experience         | Public pages, app, auth and saved screens.       | End-to-end usability and performance.                    |
| 8\. Limits/billing/beta        | One paid plan, instrumentation and support loop. | Real users complete and repeat the workflow.             |

## Release gates

- Data gate: selected benchmark companies reconcile to source filings within documented tolerances.

- Determinism gate: the same query and dataset version return the same result.

- Explainability gate: interpreted criteria and metric definitions are visible.

- Safety gate: unsupported or ambiguous queries do not silently become different screens.

- Performance gate: common screens feel interactive under expected beta load.

- SEO gate: only useful, canonical public pages are indexable; thin combinations are blocked.

- Commercial gate: limits and entitlement checks work before charging users.

## MVP definition of done

The MVP is done when a controlled beta user can discover Scrooner, run a
supported multi-year fundamental screen in plain English, verify how it
was interpreted, inspect trustworthy results, save it and return
later—while the team can trace every displayed metric to its data
lineage and diagnose failures through admin tooling.
