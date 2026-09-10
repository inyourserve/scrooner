# 05 — Scrooner Product and Engineering Methodology

How Scrooner will be designed, built, validated, documented and
expanded.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When a core decision changes

---

## Operating principle: KISS BORING

Keep It Simple and Boring. Zerodha and Screener.in are the reference
points: focused utility, restrained interfaces, fast performance, high
trust and very little decorative complexity. Boring is not low quality;
it means predictable, understandable and dependable.

## Core principles

| **Principle**                    | **Working rule**                                                                    |
|----------------------------------|-------------------------------------------------------------------------------------|
| Correctness before breadth       | A small trusted metric set beats a large questionable database.                     |
| Determinism before AI magic      | AI interprets intent; code and versioned data decide results.                       |
| Traceability by default          | Every important number should expose source, period, formula/version and data date. |
| One source of truth              | Each decision, metric definition and interface contract has one canonical home.     |
| Vertical slices                  | Finish usable data-to-interface paths instead of half-building every layer.         |
| Evidence before expansion        | Add features, dependencies and markets only after observed demand.                  |
| Server-first public and private | Use Next.js Server Components by default; add client code only for real interaction. |
| Manual verification is a feature | Inspect filings and edge cases before trusting automation.                          |
| Low operational burden           | Prefer managed, conventional components a solo founder can run.                     |
| Kill scope aggressively          | Anything not needed to validate the core job goes to Later or Never.                |

## Build method

1.  Define the user question and acceptance test before choosing
    implementation details.

2.  Write or update the relevant decision, metric or interface document.

3.  Build the smallest vertical slice with observable inputs and
    outputs — inspect the real source payload/data shape before
    finalizing schema or algorithm design, not just after. Assuming a
    field's shape from its name, a spec, or how a doc described it cost
    real rework five times running on the Normalizer (submissions has no
    per-filing fiscal year field; a fact's own `fy`/`fp` describes the
    filing, not the period; filer-invented units collide case-
    insensitively; ~5% of facts trace to out-of-scope filings; JSON's
    default float parsing loses precision on money) — see
    `doc/learnings/normalizer-day-01` through `-05`. Checking first is
    now the proven-cheaper path, not just the cautious one.

4.  Test happy paths, known SEC edge cases and failure/retry behavior.

5.  Reconcile a golden set of companies manually against filings and
    trusted references.

6.  Release to a small beta group and instrument completion, failure and
    repeat usage.

7.  Fix correctness and clarity problems before adding coverage or
    convenience.

8.  Promote only proven patterns into reusable infrastructure.

## Collector-first execution

The first implementation project is the SEC Collector because every
downstream promise depends on reproducible raw evidence. Its definition
of done is not “we downloaded data”; it is “we can repeat, resume and
audit collection without losing or silently changing source material.”

- Start with company identity/CIK discovery, submissions, company facts, filing metadata/documents and daily indexes.

- Use bulk downloads for bootstrap and incremental sources for freshness.

- Preserve exact bytes, source URL, retrieval time, response metadata and SHA-256.

- Prove idempotency, deduplication, retry, checkpoint, resume and reconciliation.

- Keep transformations out of the Collector, even when a quick fix seems convenient.

## Data quality methodology

| **Control**          | **Application**                                                                         |
|----------------------|-----------------------------------------------------------------------------------------|
| Golden-company set   | Select varied issuers covering standard, complex, amended and edge-case filings.        |
| Layer-specific tests | Collector completeness; Normalizer structure; Mapper semantics; Metric formula outputs. |
| Trust your own zero  | A clean or zero-looking result (0 conflicts, 0 skipped, 0 superseded) gets the same individual scrutiny as a surprising one before it's trusted — it's exactly as capable of hiding a broken join as a messy number is of hiding bad data, and reads as good news, which is what makes it more dangerous, not less. Found live three times over on the Normalizer (Days 4 and 6) before being written down. |
| Lineage tests        | A displayed value must resolve backward to source object and filing.                    |
| Reconciliation       | Compare counts, hashes, filing coverage and changed objects after every run.            |
| Versioning           | Version mappings and formulas; never silently redefine a historical metric.             |
| Freshness checks     | Track expected arrivals and flag stale issuer/market data.                              |
| Confidence states    | Mappings can be approved, provisional or rejected; uncertainty stays visible.           |
| Regression suite     | Every fixed edge case becomes a permanent fixture/test.                                 |

## AI methodology

- AI outputs a structured query, not a stock list or fabricated metric.

- Only allow metrics, operators and time expressions present in the supported schema.

- Show the user the interpreted conditions in plain language.

- Ask for clarification or reject safely when intent cannot be mapped with confidence.

- Log anonymized parse failures and unsupported intents to guide product priorities.

- Evaluate with a fixed prompt set: simple, compound, ambiguous, adversarial and unsupported requests.

- Never let model output change canonical financial data.

## Product and UX methodology

- Answer first: prompt box, interpreted screen and results are the dominant flow.

- Progressive disclosure: show essential results first; definitions and lineage remain one step away.

- Use familiar tables, filters and plain labels; avoid novelty for its own sake.

- Create strong empty, loading, partial-data and error states.

- Treat speed, keyboard usability, mobile readability and accessibility as product quality.

- Keep public pages useful independently; do not generate thin SEO combinations.

## Documentation methodology

| **Document type** | **Rule**                                                                     |
|-------------------|------------------------------------------------------------------------------|
| Master context    | Explains purpose, audience and durable thesis.                               |
| Decision register | Records locked, rejected, deferred, open and superseded decisions.           |
| MVP scope         | Defines in/out, gates and definition of done.                                |
| Architecture      | Defines boundaries and data flow, not task-level implementation.             |
| Metric catalogue  | One definition, formula, inputs, edge cases and examples per metric.         |
| ADRs              | Use for consequential technical changes; link back to the decision register. |
| Runbooks          | Describe repeatable operational responses for failures and recovery.         |

Documentation should be implementation-ready, concise and
non-duplicative. If two documents disagree, the newer explicit decision
in the Decision Register wins; the conflicting document must then be
corrected.

## Prioritization framework

| **Question**                                                           | **If “no”**                     |
|------------------------------------------------------------------------|---------------------------------|
| Does this improve core screening correctness, clarity or repeat usage? | Do not build now.               |
| Is it required for the next validation gate?                           | Move to Later.                  |
| Can we operate it reliably as a solo bootstrapper?                     | Simplify or reject.             |
| Is demand supported by user behavior or repeated requests?             | Keep as a hypothesis.           |
| Can it be tested and traced?                                           | Redesign before implementation. |

## Review cadence and decision discipline

- Daily during active build: failures, blockers and the next smallest shippable slice.

- After every completed build-day/stage (not just weekly): update [`doc/status/SCORECARD.md`](../status/SCORECARD.md) — its single overall score, recomputed with its own documented formula, not re-eyeballed each time. Weekly is the floor, not the actual cadence during active build.

- At each stage gate: explicit go/fix/stop decision before beginning the next layer.

- Monthly after beta: activation, successful screens, repeat use, saved screens, conversion, churn/refunds and support themes.

- Any scope addition must name what is being delayed or removed.

## Definition of “good”

Scrooner is good when investors trust it enough to return, understand it
without training and can verify what it did. The engineering is good
when a solo founder can operate it calmly. The methodology is working
when each release increases evidence—not merely the amount of code.
