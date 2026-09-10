# Full project inspection — gaps, staleness, and what's not achieved

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

**Method:** an initial pass read the project's own living-status docs (`doc/status/PROGRESS.md`, `DATA_COVERAGE.md`, `SCORECARD.md`), the decision register (`doc/foundational/02`), the consolidated remaining-work plan (`doc/planning/20`), and the full `doc/learnings/` index (48 entries), cross-checked against real, live database state as of tonight's (2026-08-23→24) full-population expansion. That pass was then deepened by 13 parallel agents, each independently investigating one part of doc 06's 14-part breakdown (Billing excluded, per explicit direction), reading real code and checking real live state rather than restating documentation. **Section 0 below corrects two things the first pass got wrong** — found only because the deeper agents checked rather than trusted the same assumption. Everywhere else, findings are additive.

---

## 0. Corrections to this report's own first pass

Get this out front, because it matters for trusting the rest of the report: an inspection that doesn't correct its own mistakes when it finds them isn't credible.

1. **"No recurring-job scheduler exists" — wrong.** `.github/workflows/pipeline-refresh.yml` exists (added 2026-08-20), with a real daily cron. It has actually been running daily. **But its last three consecutive scheduled runs (08-21, 08-22, 08-23) have all failed** — and the failures are benign: ingestion succeeds every time, but `scrooner-operations --fail-on-alert` correctly flags known open alerts (stale freshness, dead letters) and exits 1. With no external alert destination wired up, a "working as intended but flagging something real" run is visually indistinguishable in GitHub Actions from an actually-broken one — alert fatigue built into the design from day one, not a hypothetical risk. See §12.
2. **The full-population learnings doc's claim that "every write is genuinely disjoint per company" is incomplete.** `core.concept` and `core.unit` are shared, globally-written lookup tables — `facts.py` reads and writes them from every one of the 6 concurrent workers. It's safe in practice (unique constraint + `ON CONFLICT DO NOTHING` handles the race correctly — confirmed no corruption), but the claim as written overstated the isolation. See §2.

---

## 1. Documentation staleness (unchanged from the first pass, still the top-level framing issue)

| Doc | Last updated | What it's missing |
|---|---|---|
| `doc/status/SCORECARD.md` | **2026-08-17** | Everything since — the entire Frontend Product buildout, docs 21-29, sector-bucket mapping, doc 24's backlog, and all of tonight's full-population work. Its "Overall score: 94/100" is computed against a golden-10/golden-8 denominator that no longer describes the system's actual scope. Needs a full recompute once tonight's run finishes and can be verified the same rigorous way every prior recompute was. |
| `doc/status/PROGRESS.md` | ~2026-08-21/22 | Doesn't reflect tonight's expansion, the dropped `update-security-types` stage, the reopened-then-reconfirmed market-price vendor conversation, or any of tonight's infra findings. |
| `doc/status/DATA_COVERAGE.md` | 2026-08-21 | All coverage percentages are golden-10/174-scoped; whether they hold at 5,258-company scale is unknown (see §2, §4 for evidence this may not hold uniformly). |
| `doc/foundational/02_Scrooner_Decision_Register.md` | Predates tonight | Market-price vendor shown "RESOLVED — Alpaca" with no record that EODHD was seriously evaluated tonight before reconfirming Alpaca. Also: several real, live changes to the Screener's operative scope (see §5) were never reflected here either. |

---

## 2. Part 1 — Data Collector

**Boundary discipline (dumb/lossless/immutable): confirmed intact** — no formula/repair/concept-mapping logic found anywhere in `collector/`.

**New finding: zero automated regression coverage for the Collector's own retry/resume logic.** Every one of doc 08b's "PASS" results was live/manual verification; nothing in `pytest` exercises `collector/retry.py`'s checkpoint/resume mechanics. This is concrete, not theoretical: tonight's real btree-index-size bug (`params_key` too long for its own index, fixed in migration 0021) was caught only by hitting it at full scale — no test would have caught a regression of that fix before the next large run.

**New finding: the params_key index fix is real and confirmed holding at full scale, but undocumented in the cross-referenced learnings.** Live check: `raw.collector_runs` 76 succeeded / 19 failed, 0 stale `running` rows; `raw.sec_companyfacts`/`sec_submissions` both close to the 5,258 target. But this fix isn't mentioned in `full-population-scale-out-and-supabase-capacity.md` alongside the other tonight-discovered bugs, nor in `pipeline/CLAUDE.md`'s own learnings log — a cross-referencing gap, not a functional one.

**Confirmed, not new:** 14 of 48 `submissions` job failures correlate exactly with the disk-space exhaustion window already documented — no new failure mode.

---

## 3. Part 2 — Normalizer

**Boundary discipline: confirmed clean** — no formula/concept-mapping logic anywhere in `normalizer/*.py`.

**Real scale numbers, checked live:** `core.fact` ≈ **27.2M rows / 8.46 GB** (up from 2.68M pre-expansion), `core.filing` ≈ 1.2M, `core.period` ≈ 889K. **A plain unfiltered `count(*)` over `core.fact` timed out at 15 seconds** under current concurrent load — the table is now big enough that even a read-only full scan is a real contention risk. Nothing in the Normalizer itself does this, but it's a hazard for any future dashboard/report query without a company filter.

**Correction to this report's own claim** — see §0.2 above: `core.concept`/`core.unit` are shared write targets, not fully disjoint. Real growth: `core.concept` 1,976→10,737 rows, `core.unit` 28→1,041 across 526x more companies — sublinear, not alarming, but per-company cost isn't perfectly flat.

**New finding: a silent golden-10 fallback footgun.** Every Normalizer CLI command (`jobs/normalize.py`) silently defaults to the 10-company golden set if `--ciks` is omitted — no error, no warning. Tonight's orchestrator always passed explicit CIKs, so this wasn't triggered, but any future manual/ad hoc invocation without `--ciks` would look like a clean success while covering 0.2% of the universe.

**Already-flagged, still genuinely open:** the 6.57% dedupe conflict rate (SCORECARD.md's "single biggest open product question") — whether that *rate* rises, falls, or holds for the many newer/smaller/shorter-history companies now in the population is unmeasured either way, not just unresolved.

**Confirmed sound:** the batched-load-then-batched-write discipline holds at full scale in every one of the 7 stages — no O(n²) pattern, no unbounded cross-company join found anywhere.

---

## 4. Part 3 — Mapper & Metrics Engine

**The single most important finding across all 13 audits, on the concept-mapping-coverage question (§2 of the first pass named this "not formally re-checked before backfilling"):** it's worse than "not checked" — **there is no automated checkpoint anywhere in the pipeline that would catch a concept-mapping shortfall at full scale, and the one CLI tool that could check it (`scrooner-map coverage`) silently defaults back to the golden-10 if `--ciks` is omitted.** `jobs/pilot.py` (tonight's orchestration file) contains zero references to `unmapped-tag`/`coverage`/`concept` at all. A direct attempt to check this live tonight **hit a query timeout**, itself evidence of how much load the live run is under — this question remains completely unanswered and nothing will answer it automatically; it requires someone to deliberately run `unmapped-tags --ciks <full population>` after tonight's run finishes.

**Positive finding: the `is_authoritative=false` hard filter is enforced at exactly one place** (`resolve.py`, the sole write path from `core.fact` to `analytics.canonical_fact`) and every other Mapper stage reads only already-filtered `analytics.*` tables — clean design by construction, though a single point of failure if a future stage ever adds a direct `core.fact` read with no structural guard against it.

**Positive finding: the Day 6 delete-scoping bug (the project's most consequential historical bug) does not recur.** Every one of the 7 newer Mapper modules added since correctly scopes its delete by `company_id` + `metric_definition_id`(s) + the right `period_label` — the fix generalized correctly, and each is atomic per company, safe even under concurrent retry.

---

## 5. Part 4 — Company Master / Market Data (incl. Ownership, doc 19)

**Headline, confirmed live with hard numbers: ownership/insider/institutional data is 100% golden-10-scoped, 0% of the full 5,258-company population.** `core.insider_transaction` (55,109 rows), `core.beneficial_ownership` (527), `core.institutional_ownership` (58,095) — every single row belongs to the same 10 companies. Insider-transaction and beneficial-ownership commands already accept `--ciks` (no code change needed to scale, but nobody has sized the SEC-fetch volume/runtime a full-population run would need). Institutional-ownership (13F) has no `--ciks` parameter by design (matches by CUSIP against whatever's in beneficial_ownership) — a positive architectural fact: expanding Stage 3 would make Stage 4 pick up automatically.

**New, more concerning finding: price-dependent metrics have regressed even for the golden-10 since doc 25's claimed "42/60" state.** Live check: only **1 of 60 golden-10 price-dependent metric values is currently non-null** (GOOGL's market_cap); everything else is timestamped 3 days before tonight's expansion and never refreshed. The "103 distinct companies" figure some expanded metrics show is almost entirely null placeholder rows from an earlier pilot batch, not real coverage.

**New code gap (not just a scoping choice): `update-market-price` (the real Alpaca command) hardcodes the golden-10 CIK list with no `--ciks` option at all**, unlike every sibling Company Master command — this genuinely needs a code change, not just a bigger invocation, before real price ingestion could reach the wider population.

**Confirmed, not new:** `update-security-types` dropped for the full population — live count shows `core.listing.security_type` populated for only 1,210 of 6,963 total listing rows.

---

## 6. Part 5 — Screener Engine

**Significant new finding: the metric catalog has silently grown ~2.6x past doc 02's locked guardrail.** The Screener auto-derives its screenable set from `analytics.metric_definition where requires_price=false` — doc 14 scoped this to "12 EDGAR-only metrics," doc 02 locks ~18 total; live query today shows **47 metrics** come back screenable, including everything the Mapper expansion work added (Piotroski score, quality flags, reconciliation gaps, etc.), with zero re-validation against the "not permission to expand ad hoc" rule and no doc 02 update. This happened automatically, with no code change, the moment each new metric was seeded.

**Confirmed, concrete: the Screener has never been run against anything wider than the golden-10.** Every test (unit or DoD-evidence) is either golden-10-scoped or pure synthetic in-memory values. Correctness at the real 5,258-company scale is genuinely unverified, not just unperformant.

**New finding with live numbers: the `active`-only default status filter, previously untestable (all golden-10 were active), is now live against 244 real non-active companies** (222 delisted, 15 stale, 7 unknown) that have never been exercised — including a query path the code's own comment already flagged as "a simplification worth revisiting" (returns *every* inactive company as excluded, not just relevant ones).

**Confirmed sound:** value-resolution logic is a single batched window-function query, not a per-company loop — holds at scale same as at 10 companies. No bug found here.

---

## 7. Part 6 — AI Query Engine

**Sharper, precisely quantified version of the previously-flagged gap:** the real metric count in code today is **58** (not the 45 `DATA_COVERAGE.md` still cites — that figure predates several later commits). Alias coverage in `ai_query/aliases.py` is exactly **14 metrics (24%)**, unchanged since 2026-08-17. **44 metrics have zero natural-language alias — and critically, 38 of those 44 are fully screenable** (not price-gated), yet completely unreachable in plain English. This is worse than the earlier "14/45" framing suggested.

**New finding: the "tech companies"/sector natural-language phrasing was never actually tested through the real parser.** The commit that added it verified `sector='Technology'` returns correct results as a direct Screener query — that's real, but it's not the same as calling `ai_query.rules.interpret("tech companies")`. No test anywhere exercises the actual NL→query path for sector phrases; the "verified live" language in that commit overstated what was checked.

**One clean area, worth crediting:** all 9 of doc 02's locked operators are properly reachable via natural language — no gap found here, contrary to expectation.

---

## 8. Part 7 — Backend / Product API

**New: an undocumented endpoint exists.** `GET /v1/metrics` (`routers/screen.py`) isn't in doc 16/16b's original spec — low-risk (read-only metric catalog for UI), but drift from the documented surface that should be added to doc 16.

**New, real production-readiness gaps:** **zero CORS configuration** anywhere (moot today since nothing calls it cross-origin yet, but this must be added — not just tightened — before any browser frontend calls it); **zero rate limiting or request-size limiting** at all — combined with `/v1/screen`/`/v1/ask` being deliberately unauthenticated by design, and each request opening a brand-new unpooled DB connection, this is a real, currently-unmitigated connection-exhaustion/DoS surface the moment either endpoint is internet-facing; **`/v1/screen` has no default result cap** — its initial company scan and exclusion lists are fully unbounded, and nobody has checked response size/query time at the new 5,258-company scale (a genuine, unquantified regression risk from tonight's expansion, specific to this component).

**Confirmed still true:** `app.user_entitlement` is genuinely shape-only, zero real limit enforcement; secrets handling is correct (gitignored, no hardcoded credentials found anywhere).

**Positive, worth crediting:** a real automated pytest suite (969 lines, 6 files) already covers Decimal precision, validation rejection, and per-user ownership isolation in both directions — materially more than doc 16b's original manual-only evidence describes.

---

## 9. Part 8 — Frontend Product

**New, more precise than "no auth UI exists": auth scaffolding is dead code, not just absent.** Real, tested utility functions exist (`apps/app/lib/auth/config.ts`, `redirect.ts`) but have **zero call sites outside their own tests**. `apps/app`'s root page is an unconditional redirect to `/screener` with no gate at all — anyone can hit it right now, there is no `/login` route anywhere.

**New: no `robots.txt`/`sitemap.xml` anywhere, and this now has real teeth** — 5,258 real `/stock/{ticker}/` pages exist today with no sitemap driving their discovery and no site-level indexing policy, distinct from Part 12's deliberate content-page deferral (this is plumbing for already-built pages).

**New: a genuinely unscaled landmine, but dead code.** `getExampleScreenResults` scans every company's `roic` values with no bound — but has zero live callers (superseded by a different function), so the fix is deletion, not optimization.

**New: the stock page itself scales correctly** (single parameterized query via a `selected_company` CTE, real 15-min/24h caching) — **but the homepage has no caching at all**, inconsistent with that pattern, doing a live DB round-trip on every hit (low risk today given its small query, but worth normalizing).

**Confirmed, not new:** "Day Change %" is genuinely zero-built anywhere in the codebase — no schema field, no scaffolding. Test coverage is lopsided: `apps/app` has real, substantive tests; `apps/site` has none touching the actual rendering path (`stock/[ticker].astro`, `MetricGrid.astro`) — the whole company page relies on manual screenshot review, not automated tests.

---

## 10. Part 9 — User System

**Correction to "not started": this is more precisely "attempted, correctly self-blocked, left as safety scaffolding."** A real, dated attempt happened on 2026-08-22 (`doc/learnings/auth-and-saved-screens-require-user-scoped-supabase-credentials.md`) — env-contract checks, a fail-closed config guard, an open-redirect sanitizer, all genuinely tested. It stopped because the repo has a server-side Supabase key but no browser-safe *publishable* key needed for real `@supabase/ssr` wiring, and correctly refused to fake it. No `@supabase/*` package exists in either frontend's `package.json` — confirmed, not assumed.

**Positive, corrects a possible misreading: the `app` schema tables DO correctly reference `auth.users` via real foreign keys** — the schema-design work is sound. The actual blocker is entirely upstream: **no signup flow exists anywhere**, so no real visitor could ever get an `auth.users` row in the first place. The two Supabase Auth users used in Backend API testing were created directly via admin API/test fixtures, never through a real user-facing flow.

**Recommendation for the status docs:** change Part 9's row from "Not started" to something like "Not started (frontend); one safe-stop attempt 2026-08-22 left non-functional scaffolding; blocked on obtaining a browser-safe Supabase publishable key."

---

## 11. Part 11 — Internal Admin

**Confirmed: genuinely 0% built as a real admin UI** — no Django anywhere in the repo (the originally-planned tool), no dependency, no admin app.

**Worth crediting explicitly: real, well-built CLI substitutes exist that materially cover the operational need even without a UI.** A guarded dead-letter *resolution* command (`scrooner-reconcile resolve --confirm`, requires an explicit confirm flag and a ≥20-character evidence note, row-level locking, refuses unknown/already-resolved IDs) is a genuine write path, not a stub. Combined with a read-only status/pilot-preflight command and a real operations runbook, this is more rigorous informal admin capability than a flat "0% built" implies — worth crediting the capability while still correctly scoring the named deliverable (a Django UI) as not started.

---

## 12. Part 13 — Analytics & Monitoring

**Directly answers the first pass's open question ("would anything have caught tonight's incidents automatically?"): no, confirmed with hard evidence, worse than assumed.** The monitoring tool's alert checks (`operations.py`) contain **zero disk-space/capacity dimension** — the only disk-space reference anywhere in the codebase is a post-hoc code comment written after the incident. One of tonight's three real incidents (the btree index-size crash) happened *before* the run-tracking row was even created — invisible even to a human manually running the status check; it only ever existed as a terminal exception someone happened to be watching live.

**New, live finding: unresolved dead letters have grown, not shrunk** — 67 total (52 collector + 15 normalizer, mapper 0), up from PROGRESS.md's documented 38 — and nothing paged anyone about that growth, because no alert-delivery destination exists (still listed "open" in doc 13, target date today, still not built).

**Confirmed:** request-ID/telemetry middleware is real, correctly wired, but goes to stdout only — lost on process restart, no configured durable destination anywhere.

---

## 13. Part 14 — Infrastructure/DevOps

**See §0.1 above for the major correction: a real scheduler exists and has been silently failing for 3 consecutive days**, benignly (ingestion succeeds; only the alert-check exit code fails) but indistinguishably from a real break given no alert destination exists. **This is now the single most urgent, concrete infra fix in this entire report** — not "build a scheduler," but "fix the alert-fatigue design flaw in the one that already exists."

**New: CI hasn't touched the last 14 local commits.** Nothing has been pushed to `origin/main` since 2026-08-20 — every real fix from tonight (connection-pool understanding, new indexes, sector mapping, the resumability-index fix, the bulk-zip cache fix, the name-history dedup fix) has **zero CI verification** behind it, despite doc 12's "all automated gates pass" framing describing an earlier state.

**New: the dependency/security audit has never actually executed.** A CI job configuration bug (an early step fails without `if: always()` on later ones) means `pip-audit` and both `npm audit` steps have been silently skipped in every run to date — the question "any concerning outdated dependencies" is genuinely unanswerable right now, not "no" — the tool that would answer it has never run.

**New: deployment story is uneven, not absent.** `apps/site` has a real Vercel link; **`apps/app` (the authenticated Next.js app) and `apps/backend` (FastAPI) have zero deployment configuration anywhere** — no Dockerfile, no Procfile, no fly.toml/render.yaml, and no CI workflow deploys anything at all (build/test only).

**Confirmed real, not just claimed:** the backup/restore round-trip genuinely runs in CI against a fresh Postgres container — this is solid, verified infrastructure, not aspiration.

---

## 14. Data coverage — genuinely blocked vs. just not built

- **Confirmed accurate, not re-litigated:** vendor-blocked items (analyst data, short interest, 52-week range, beta, forward estimates, credit ratings) and structurally-blocked items (segment/geography revenue, a real dimensional-XBRL API limitation) both stand as-is.
- **Worth prioritizing louder than `DATA_COVERAGE.md` currently does:** "Day Change %" is the one item needing a genuinely new (but small, cheap) fetch — a second Alpaca price point — and the vendor ambiguity that used to surround it is resolved (Alpaca reconfirmed tonight).
- **Genuinely new gap, not currently its own row anywhere:** business-description ("About") text has no data source anywhere in the project — named in `SCORECARD.md`'s "Worst" list but not tracked as its own `DATA_COVERAGE.md` row.

---

## 15. What's genuinely done well (not just gaps)

- **Verify-then-proceed discipline is real and consistent** — every "Definition of Done" doc cites actual row counts, reruns, and independent cross-checks. No instance found anywhere of a status claim with no citable evidence behind it, aside from *currency* (staleness), never fabrication.
- **Database design is sound** — correct FK/no-FK choices throughout (confirmed again by the Normalizer/Mapper agents independently), all financial values as `numeric`, deliberate schema isolation from Supabase's public REST surface.
- **The `doc/learnings/` discipline (48 real entries)** — including the project correcting its *own* earlier wrong numeric claims — is a genuinely rare level of honesty in a fast-moving build.
- **Several architectural decisions held up correctly under 13 independent deep audits**: the `is_authoritative` filter's single enforcement point, the Day 6 delete-scoping fix generalizing cleanly to 7 later modules, the stock page's scale-invariant query design, all 9 locked Screener operators reachable in natural language, and the Collector's boundary discipline — none of these needed defending, they simply held.

---

## 16. Recommended priority order

1. **Fix the alert-fatigue flaw in the existing scheduler** (§13) — this is the most urgent, concrete, and cheapest fix in the whole report: either wire a real alert destination (even a simple webhook) so a "benign alert" run doesn't look identical to a broken one, or separate "ingestion failed" from "ingestion succeeded but flagged something" as distinct CI outcomes.
2. **Push the last 14 local commits and get CI running against real state again** (§13) — nothing from tonight has been verified by CI at all.
3. **Verify the concept-mapping coverage gate against the full 5,258-company population** (§4) — the single highest-value data-correctness question left completely open, with no automated way to ever answer it unless someone deliberately runs the existing tool with the right `--ciks`.
4. **Fix the CI dependency-audit job** so `pip-audit`/`npm audit` actually run (§13) — currently answering "unknown," not "clean."
5. **Refresh `SCORECARD.md`, `PROGRESS.md`, `DATA_COVERAGE.md`** against post-expansion reality (§1) — can't sequence well against stale ground truth.
6. **Decide what to do about the Screener's 47-vs-18 metric catalog drift** (§6) — either amend doc 02's locked list deliberately, or add a real guardrail preventing every new Mapper metric from silently becoming screenable.
7. **Add basic production-readiness hygiene to the Backend API** (§8) — CORS, a rate limit, a result cap on `/v1/screen` — before it's ever exposed to real browser traffic.
8. Then resume the standing critical path: rest of Frontend Product, the remaining open decisions (usage limits, pricing, legal), and closing the ownership/price-metric gap for the full population once the above is stable.

---

## 17. 2026-08-28 frontend latency and cache-architecture finding

A focused localhost timing pass changed the performance diagnosis from a broad
"pages are slow" concern into a specific serving-path issue.

| Path | Cold | Warm |
|---|---:|---:|
| Astro AAPL company page | 4.53s | 0.67–0.94s |
| Astro homepage | — | 0.59–0.62s |
| Next screener HTML | 4.77s | 0.11–0.17s |
| Next saved-screens HTML | 1.72s | 0.027–0.030s |
| Next `/api/metrics` | 3.06s | 2.56–2.69s |
| FastAPI `/health` | — | ~2ms |

The saved-screen measurement lacked the real local auth environment, so it
excludes the production auth waterfall and is not an authenticated end-to-end
result.

A fresh Postgres connection took 1.70–1.85s and a subsequent `select 1` took
0.53–0.58s locally. `pg_stat_statements` showed the consolidated company query
averaging about 138ms across 47 calls (another variant averaged about 68ms
across 14 calls). Most observed localhost delay is therefore connection and
network overhead, not financial calculation.

Astro is not the main company-page payload bottleneck: company-search
JavaScript is about 5.4KB raw/2.2KB gzip, company CSS about 37.1KB raw/8KB gzip,
and the page ships no framework hydration. The Next screener and saved-screen
journeys are heavier at roughly 211KB and 202KB gzip initial JavaScript.

Request tracing found that FastAPI creates a new `psycopg.connect()` connection
per operation; `/screen` and `/ask` can open another for usage logging; the
stable metric catalog repeatedly reaches an uncached database path; saved
screens traverse hydration, session lookup, Next API, claims middleware,
backend user validation, connection setup, and query; and global middleware
performs claims work for routes that do not all require authentication.

**Decision:** introduce a versioned backend read API and cache hierarchy, but
do not mistake an API hop or Redis alone for a speed fix. The order is
CDN-cached public HTML → cached company read API → optional shared Redis →
pooled Postgres/Supabase. Implement bounded connection pooling and stable
metadata caching first, then measure the colocated origin. Add Redis cache-aside
only where repeated reads must be shared across instances. Never cache auth
decisions, and keep private saved-screen data user-scoped.

This finding adds the performance sprint in
`doc/planning/24_Scrooner_Final_Build_Backlog.md` and refines the reusable rule
in `doc/learnings/company-page-latency-is-round-trips-not-calculation.md`.
