# Scrooner build learnings

Not a decision doc — this is the running product, design, architecture, and
engineering journal: what was unclear or wrong, how it was actually found, and
what changed as a result. Canonical docs say what is decided; these entries say
how a decision was applied or how the project learned something, so the next
session does not have to rediscover it.

Covers the data pipeline, backend, product UI, public site, and cross-cutting
architecture. Phase/day entries retain their existing filename conventions;
cross-cutting entries use a descriptive name such as
[`public-app-domain-boundary.md`](public-app-domain-boundary.md).

Write an entry when a task produces a material, reusable learning. Use this
structure:

- **Problem or clarification** — what broke, was wrong, or was easy to
  misunderstand, stated plainly.
- **How it was found** — the specific check that surfaced it. If the answer is "I just thought about it," that's worth noting too — most of these were found by verifying against live data/state, not by reasoning from memory.
- **Fix / decision** — what actually changed, and where (file, doc, schema).
- **Why it matters going forward** — the generalizable lesson, not just the one-off fix. This is the part that's actually meant to prevent a repeat.

Read the relevant day's entry (or skim recent ones) before starting related work — that's the whole point of this folder existing.

For work spanning both frontends, start with
[`multi-surface-frontend-completion-is-a-contract.md`](multi-surface-frontend-completion-is-a-contract.md):
it defines completion across shared foundations, native adapters, product
journeys, accessibility structure, production gates, rendered geometry, and
explicitly open boundaries.

For page-speed, API-layer, connection-pooling, and Redis decisions, start with
[`company-page-latency-is-round-trips-not-calculation.md`](company-page-latency-is-round-trips-not-calculation.md).
It records the measured distinction between database execution, connection
cost, frontend waterfalls, CDN caching, and conditional shared caching.
