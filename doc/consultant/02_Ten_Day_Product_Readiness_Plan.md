# Scrooner — 10-Day Product Readiness Plan

> **Status:** Consultant recommendation  
> **Date:** 2026-08-18  
> **Duration:** Ten focused working days; each day is an outcome gate, not a promise about elapsed calendar time.  
> **Authority:** Advisory only. Canonical product decisions remain in `doc/foundational/02_Scrooner_Decision_Register.md`; implementation status remains in `doc/status/PROGRESS.md` and `doc/status/DATA_COVERAGE.md`.

## Objective

Convert Scrooner from a well-verified, golden-company data prototype into a test-protected, measurable product slice that can be demonstrated to real users.

At the end of Day 10, Scrooner should have:

- Repeatable automated tests around its highest-risk financial logic
- CI that prevents known correctness regressions
- A formally defined eligible-security universe
- Evidence from a materially wider pilot dataset
- Coverage and failure reporting by company and metric
- A usable Screener interface over the existing API
- A usable plain-English Query interface with interpretation shown before execution
- Source lineage and missing-data explanations visible to users
- Basic product and pipeline observability
- A private-beta readiness decision based on explicit evidence

## What this plan deliberately does not do

The ten days should not be consumed by expanding the metric catalog, parsing every SEC form, building billing, adding a production LLM, or polishing a broad marketing site.

New data work is allowed only when it fixes a material correctness or coverage problem discovered by the wider-universe pilot.

## Non-negotiable working rules

1. Every previously discovered bug class becomes an automated regression test.
2. Every day ends with executable evidence, not only code or prose.
3. No failed or missing value is silently guessed.
4. Filing date, financial period, source filing, and calculation version remain traceable.
5. Existing user changes and unrelated worktree changes are preserved.
6. Live SEC checks are separated from fast deterministic tests.
7. `PROGRESS.md`, `DATA_COVERAGE.md`, and this plan are updated only with demonstrated results.
8. Scope is reduced before quality gates are weakened.

## Recommended team rhythm

- Start of day: select the day's named outcome and confirm prerequisites.
- Midday: run the narrowest useful test or pilot early; do not wait until implementation appears finished.
- End of day: capture commands, results, counts, failures, and unresolved risks.
- A day passes only when its Definition of Done is satisfied.

---

## Day 1 — Establish the automated test foundation

> **Status:** Complete — see [`03_Day_01_Test_Foundation_Evidence.md`](03_Day_01_Test_Foundation_Evidence.md).

### Outcome

The repository has a real, runnable test structure and a documented testing strategy. `pytest` must collect meaningful tests instead of reporting zero tests.

### Tasks

- Create test layers:
  - Fast unit tests with no network or production database
  - Database integration tests against an isolated test schema/database
  - Frozen-fixture pipeline tests
  - Optional live SEC/vendor verification tests, excluded from default runs
- Add factories or fixtures for companies, filings, periods, facts, canonical facts, metrics, and prices.
- Store a minimal set of sanitized/frozen SEC payloads for representative cases.
- Add deterministic Decimal, date, UUID, and JSON fixtures.
- Define test markers such as `unit`, `integration`, and `live`.
- Add one passing test through each major boundary:
  - Normalizer
  - Mapper
  - Screener
  - AI Query parser
  - Backend API
- Document exact local commands.

### Definition of Done

- Both pipeline and backend test commands collect and run tests.
- The default test run needs no external network access.
- Test data cannot write to production tables.
- At least five meaningful smoke tests pass.
- A deliberate assertion failure makes the command and CI candidate fail non-zero.

### Evidence to record

- Test collection count
- Passing/failing count
- Runtime
- Test database isolation mechanism
- Fixture sources and accession numbers where applicable

---

## Day 2 — Lock down financial-period and normalization correctness

> **Status:** Complete — see [`04_Day_02_Normalizer_Regression_Evidence.md`](04_Day_02_Normalizer_Regression_Evidence.md).

### Outcome

The highest-risk Normalizer behavior is protected against regression.

### Tasks

- Test instant versus duration period classification.
- Test fiscal-year and fiscal-quarter identity.
- Test non-calendar fiscal years.
- Test unit normalization and unit collisions.
- Test duplicate resolution and unresolved-conflict handling.
- Test amendment/restatement precedence while preserving original facts.
- Test derived Q4 calculations.
- Test cumulative YTD cash-flow decomposition into discrete interim quarters.
- Include fixtures representing at least:
  - Calendar-year filer
  - Non-calendar-year filer
  - Amended filing
  - Directly reported Q4
  - Derived Q4
  - Incomplete derivation that must remain null

### Required regression cases

- Do not derive Q4 when a directly reported value exists.
- Do not subtract incomparable contexts or units.
- Do not treat incomplete YTD chains as complete quarters.
- Do not overwrite or delete facts belonging to another company.

### Definition of Done

- Normalizer tests cover every listed behavior.
- Expected null/skip reasons are asserted explicitly.
- Rerunning normalization produces the same logical result.
- A single-company rerun leaves another company's fixture output unchanged.

---

## Day 3 — Lock down canonical mapping and metric formulas

> **Status:** Complete for the current-screen calculation scope — see [`05_Day_03_Mapper_Metrics_Regression_Evidence.md`](05_Day_03_Mapper_Metrics_Regression_Evidence.md). Historical as-known screening and generalized non-XBRL lineage are documented architecture follow-ups.

### Outcome

Metric calculations and lineage are executable specifications rather than documentation-only claims.

### Tasks

- Add tests for canonical tag priority and fallback behavior.
- Test standard tags versus company extensions.
- Test point-in-time selection without look-ahead.
- Test TTM construction and the fiscal-year boundary equivalence check.
- Add formula tests for all locked V1 metrics.
- Add formula tests for currently exposed expanded metrics.
- Test invalid denominators, negative values, and zero denominators.
- Assert Decimal precision and serialization expectations.
- Assert every metric's source fact lineage.
- Assert definition/version identity on calculated values.

### Required regression cases

- Delete/reinsert operations must be scoped by company, definition, period, and calculation family as appropriate.
- One calculation stage must not destroy another stage's output.
- Industry-structural nulls must not become zero.
- Price-dependent metrics must use the correct security and price timestamp.
- Multi-class share fallbacks must apply the correct unit scale.

### Definition of Done

- Every user-visible metric has at least one positive and one edge-case test.
- The known shared-table delete-scoping bug has a permanent test.
- No metric row has dangling or non-authoritative lineage in the fixture run.
- Formula documentation and implementation names agree.

---

## Day 4 — Lock down Screener, AI Query, API, and authorization behavior

> **Status:** Complete — see [`06_Day_04_Query_API_Auth_Regression_Evidence.md`](06_Day_04_Query_API_Auth_Regression_Evidence.md).

### Outcome

The complete query path is protected from parser, filtering, serialization, and authorization regressions.

### Tasks

- Test all nine locked Screener operators.
- Test null exclusion, sorting, ranking, ties, limit behavior, and deterministic ordering.
- Test `sort_by` fields that are not predicates.
- Test malformed and contradictory queries.
- Test natural filler words, aliases, percentages, ranges, ranking phrases, and categorical filters.
- Confirm ambiguous or unknown language produces no executable query.
- Test `/v1/screen` and `/v1/ask` response contracts.
- Test Decimal JSON serialization.
- Test missing, invalid, and valid authentication.
- Test saved-screen ownership in both directions using two users.
- Test UUID/string normalization.

### Definition of Done

- Every previously documented Screener, parser, API, and authorization bug has a regression test.
- The same request produces byte-equivalent logical output across repeated executions.
- Non-owners cannot read, rename, or delete another user's saved screen.
- Unknown natural language can never execute a partial guessed query.

---

## Day 5 — Add CI and repository quality gates

> **Status:** Complete as repository implementation and local verification; first hosted run pending push — see [`07_Day_05_CI_Quality_Gates_Evidence.md`](07_Day_05_CI_Quality_Gates_Evidence.md).

### Outcome

Every change is automatically checked before it can be considered merge-ready.

### Tasks

- Add CI for supported Python and Node versions.
- Run pipeline and backend tests in CI.
- Build the Astro site in CI.
- Add formatting and lint checks.
- Add Python static/type checks appropriate to the current codebase.
- Validate database migration ordering and syntax.
- Add documentation-link validation.
- Add secret detection.
- Add dependency vulnerability scanning or audit commands.
- Cache dependencies without caching secrets or test output.
- Document required versus advisory checks.

### Definition of Done

- A clean branch passes all required checks.
- A broken test, malformed migration, broken internal link, or leaked test secret fails the appropriate check.
- CI does not require production credentials for the default suite.
- Live verification is a separately triggered or scheduled workflow.
- Required checks and local equivalents are documented.

---

## Day 6 — Define the production company and security universe

> **Status:** Implementation and isolated validation complete; production migration and live full-universe snapshot pending authorized deployment — see [`08_Day_06_Production_Universe_Evidence.md`](08_Day_06_Production_Universe_Evidence.md).

### Outcome

Scrooner has explicit, reproducible eligibility rules instead of an implicit list of tickers.

### Tasks

- Define separate company, filer, listing, and security identities.
- Specify inclusion/exclusion rules for:
  - Common stocks
  - Multiple share classes
  - ADRs and foreign private issuers
  - REITs and BDCs
  - Banks and insurers
  - SPACs and shells
  - ETFs and registered funds
  - Preferred shares, warrants, units, and debt
  - Delisted, acquired, and deregistered issuers
- Define primary-listing selection.
- Define ticker-change and ticker-reuse behavior.
- Define point-in-time eligibility so historical screens avoid survivorship bias.
- Produce reason codes for inclusion, exclusion, and uncertainty.
- Create an initial universe snapshot from official SEC sources plus the existing security classification mechanism.

### Definition of Done

- Every candidate security receives an eligibility status and reason.
- One CIK with multiple securities is represented without collapsing them incorrectly.
- Universe generation is deterministic and rerunnable.
- Uncertain cases are measurable and inspectable.
- The open ADR/20-F/40-F product decision is surfaced, not silently decided by code.

### Evidence to record

- Candidate companies, securities, and listings
- Included/excluded/uncertain counts
- Counts by security type, exchange, and filer type
- Multi-listing and multi-class counts
- Representative manually checked edge cases

---

## Day 7 — Run a 100-company stratified pilot

> **Status:** NO-GO at executable preflight; the unsafe full run was not launched — see [`09_Day_07_100_Company_Pilot_Readiness.md`](09_Day_07_100_Company_Pilot_Readiness.md).

### Outcome

The pipeline is tested beyond the golden set with a deliberately diverse sample.

### Sample design

Select approximately 100 eligible companies across:

- All major SIC/sector groupings available in the data
- Large, mid, small, and micro capitalization bands where price data permits
- Calendar and non-calendar fiscal years
- Banks, insurers, REITs, BDCs, and general industrial companies
- Multiple share classes
- Recent IPOs and mature filers
- Domestic issuers and separately reported foreign/ADR candidates
- Known amendments and restatements

### Tasks

- Run Collector through Mapper/Metrics for the full sample.
- Capture runtime and storage growth per stage.
- Generate coverage by company, concept, metric, form, and fiscal period.
- Aggregate null and skip reasons.
- Collect unmapped tags and extension frequency.
- Classify every failure as code defect, mapping gap, unavailable filing data, universe error, or expected structural null.
- Manually reconcile at least ten companies selected across strata, not only famous technology companies.

### Definition of Done

- At least 95% of eligible pilot companies finish without an unhandled failure.
- Every failure has a recorded category and reproducible input.
- Coverage is reported by metric and company type.
- Ten stratified manual reconciliations are documented.
- Any discovered correctness defect receives a failing test before its fix.

### Stop condition

Do not scale further if a systemic period, identity, lineage, or formula defect is found. Repair and rerun the 100-company pilot first.

---

## Day 8 — Build the Screener UI vertical slice

> **Status:** Complete — see [`10_Day_08_Screener_UI_Evidence.md`](10_Day_08_Screener_UI_Evidence.md).

### Outcome

A user can construct and run a structured fundamental screen without using an API client.

### Tasks

- Scaffold or complete the interactive application at the canonical app location.
- Build a filter builder using the API's validated metric definitions and operators.
- Support adding/removing predicates, categorical filters, sort, direction, and limit.
- Render results with company, ticker, selected values, period dates, and null/coverage state.
- Add loading, empty, validation-error, API-error, and partial-coverage states.
- Provide metric definitions and formatting by metric type.
- Link each company to its company page.
- Ensure keyboard navigation, labels, focus states, and readable contrast.
- Add frontend tests for query construction and important UI states.

### Definition of Done

- A non-developer can reproduce the four verified reference screens through the UI.
- UI requests match the backend schema exactly.
- Results preserve deterministic ordering and Decimal precision.
- Invalid queries are blocked before execution and explained.
- Empty results are distinguishable from failed requests and incomplete data.
- The production build passes.

---

## Day 9 — Build the explainable plain-English Query UI

> **Status:** Complete — see [`11_Day_09_Explainable_Query_UI_Evidence.md`](11_Day_09_Explainable_Query_UI_Evidence.md). The expanded-metric test/fixture drift was reconciled; the repository-wide pipeline gate passes with 129 tests passed and 1 intentionally deselected.

### Outcome

A user can enter a supported English screen, inspect its interpretation, and deliberately execute it.

### Tasks

- Add the natural-language query input.
- Display recognized predicates, metrics, operators, ranges, sorting, and limits.
- Show ambiguous and unrecognized phrases separately.
- Require an explicit execution action after interpretation.
- Allow the user to edit the interpreted structured query.
- Explain that AI/parser interpretation is not the source of financial truth.
- Add example queries that the existing interpreter genuinely supports.
- Display pass reasons and source/period context in results.
- Add tests for supported, ambiguous, unsupported, and partially recognizable inputs.

### Definition of Done

- The four verified positive queries work through the browser.
- The known ambiguous and unknown examples do not execute.
- No partial interpretation can be submitted accidentally.
- The exact structured query sent to the Screener is visible to the user.
- Results link to definitions and source-aware company details.

---

## Day 10 — Add observability and conduct the private-beta readiness review

> **Status:** Readiness assessment complete — **No-Go for private beta**. See [`12_Day_10_Observability_and_Private_Beta_Readiness.md`](12_Day_10_Observability_and_Private_Beta_Readiness.md). Observability and backup/restore controls were added, while live freshness, dead-letter, 100-company pilot, capacity, deployment, and external-user gates remain open.

### Outcome

The team can decide, using evidence, whether Scrooner is ready for a controlled private beta and what must happen next.

### Tasks

- Add structured identifiers across requests and pipeline runs.
- Record pipeline success/failure, stage duration, row counts, freshness, retry counts, and dead-letter counts.
- Record API request count, latency, error rate, and endpoint without logging sensitive query/user content unnecessarily.
- Define freshness targets for filings, prices, and derived metrics.
- Define alerts for stale data, failed runs, abnormal row-count changes, and reconciliation failures.
- Exercise backup and restore in a non-production environment.
- Run the full automated suite and frontend production build.
- Rerun the 100-company pilot or a deterministic subset to confirm no regression.
- Conduct five task-based usability sessions if users are available; otherwise run five internally scripted sessions and mark external validation as still missing.
- Produce a go/conditional-go/no-go decision.

### Definition of Done

- A failed pipeline run is visible without querying raw database tables manually.
- Data freshness is measurable by source and stage.
- Backup restoration has been demonstrated, not merely configured.
- All required automated checks pass.
- Known risks have owners and target dates.
- Private-beta readiness is decided against the exit gates below.

---

## Ten-day exit gates

### Data correctness

- All user-visible metrics have automated formula and edge-case coverage.
- All previously discovered material bug classes have regression tests.
- No known non-authoritative or dangling lineage reaches user-visible output.
- Point-in-time selection prevents use of facts before their filing date.

### Universe and coverage

- Eligibility rules are documented and executable.
- A stratified 100-company pilot has completed.
- At least 95% of eligible pilot companies complete without unhandled errors.
- Coverage and null reasons are quantified by company and metric.

### Product

- Structured screens run successfully through a browser.
- Supported English queries can be interpreted, reviewed, edited, and executed.
- Ambiguous/unsupported text fails safely.
- Results show period dates, definitions, and coverage/source context.

### Engineering

- Tests run locally and in CI.
- CI includes backend, pipeline, frontend build, migration, link, and secret checks.
- Default tests require no production credentials or external network.
- Deployment and rollback steps are documented.

### Operations

- Pipeline freshness, failures, duration, and row-count anomalies are observable.
- API failures and latency are measurable.
- Backup restoration has been exercised.
- Production secrets are not committed to the repository.

### User validation

- At least five representative users complete the core screening task, or the lack of external testing is explicitly recorded as the final beta blocker.
- Confusion points and requested metrics are captured without automatically expanding scope.

## Decision rules after Day 10

### Go to controlled private beta

Choose **Go** only if all correctness, product, engineering, and operations gates pass, and no known defect can silently produce an incorrect company match.

### Conditional go

Choose **Conditional Go** when remaining problems are visible and non-corrupting—for example incomplete company coverage, limited supported English grammar, or manual operations with reliable alerts.

### No-go

Choose **No-Go** if any of the following remains:

- A query can silently return an incorrect result.
- Historical screens can use future information.
- User data isolation is not automatically tested.
- Pipeline failures or stale data are invisible.
- Production and test data are not safely separated.
- The wider-universe pilot exposes unresolved systemic identity, period, or mapping defects.

## Recommended backlog after the ten days

If the exit gates pass, the next order should be:

1. Expand the pilot from 100 to 500 and then 2,000 securities.
2. Add authentication and saved-screen UI.
3. Run structured user research and measure repeat screening behavior.
4. Add sector-specific definitions where the pilot proves they are necessary.
5. Add selected dimensional XBRL, beginning with segment and geographic revenue.
6. Add filing-event intelligence and capital-allocation signals.
7. Decide usage limits and pricing before billing implementation.
8. Add a production LLM only when it improves query coverage without weakening validation.

Do not make N-PORT, proxy extraction, hundreds of metrics, or general AI research the next priority unless user evidence changes the product strategy.
