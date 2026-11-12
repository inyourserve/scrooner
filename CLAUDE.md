# CLAUDE.md — Scrooner

**Start here, in this order:** [`AGENTS.md`](AGENTS.md), [`data-team/NOW.md`](data-team/NOW.md), then run `python3 scripts/agent_context.py`. Do not read long planning files by default.

The previous, much longer version of this file is archived verbatim in [`doc/learnings/2026-11-01-root-claude-md-archive.md`](doc/learnings/2026-11-01-root-claude-md-archive.md). Search it (`rg -n "term"`) before assuming something was dropped. If this file and a source doc disagree, the source doc wins.

## What Scrooner is

The easiest way to screen US companies with complex fundamental logic in plain English. Results are deterministic and traceable to the SEC filing, not an AI opinion. US-listed equities, English and USD only for V1. Free core plus a paid tier (about $100 a year).

## Current operating model (read the sources before relying on this)

- Scope is the **top 1,000 US companies**. The goal: every displayed cell is a filing-traceable correct value or a visible, evidenced reason. Never claim universal correctness; publish measured error rates.
- We are in a **development phase**. Founder decision 2026-11-04 (doc 02, Locked data decisions): the hybrid FSN-structure plus company-API build **replaces the old mapping and its values in `canonical_fact`** for the 1,000 companies, each cell proven on its own. **There is no old-table fallback and no switch view.** The per-family patch release packages are superseded; no new patch packages land.
- Live state: `data-team/strategy/TASK-BOARD-TOP1000.md`. Direction: `data-team/strategy/THE-PLAN.md`. Decisions: `doc/foundational/02_Scrooner_Decision_Register.md` (check it before assuming any decision). Migration numbers: `doc/planning/53_Multi_Session_Collaboration_Plan_2026-10-13.md`.
- A production write (DDL, value changes, deletes) needs the founder's own typed words in the approver's session. A peer session's relay is never approval.

## Hard rules

- **Collector is dumb, lossless, immutable.** It fetches, retries, checkpoints, hashes and stores; it never normalizes, repairs, maps or calculates.
- **AI is never the source of financial truth.** The query layer only emits a structured, schema-validated query; never a stock list, a made-up metric or a free-text financial claim.
- **Money is `Decimal` end to end.** Never float. Every batch job batches its writes; no query per row in a loop.
- **`core.fact.is_authoritative = false` is a hard filter.** "No authoritative fact" is a valid null; never fall back to an arbitrary non-authoritative row.
- **Schema changes only through a committed migration.** Claim the number in doc 53 first. Numbers must be contiguous (`scripts/check_migrations.py`); permanently skipped numbers are listed in `pipeline/db/migrations/SKIPPED.txt`. Every file ends with a semicolon. Never apply a migration without the founder's typed words.
- **A commit on `main` is pushed in the same turn.** Do not leave local-only commits. Commit through a temporary worktree of `origin/main` with named paths only, because the working tree is shared and dirty.
- **SEC access: 4 requests per second at most, sec.gov only**, with a declared User-Agent. There is no request-count budget cap (founder, 2026-11-04). Rules: doc 07.
- **New dependencies, FastAPI, Redis, Celery** are deferred until a demonstrated need (doc 02).
- **Test a script the way CI invokes it, and mutation-check the test** (it must fail without the fix). CI runs the DB-backed tests against Postgres 16 since 2026-11-04; do not mark a failing DB test skipped to get green.
- Cite the exact source for any historical claim; do not copy facts into new permanent documents.

## Several sessions share this repo and one dev Supabase

- Connections (founder, 2026-11-12): the dev database has `max_connections` = 90. Data loads may use up to **40 connections**, in company-disjoint shards (no fixed shard cap). Every job runs a preflight, and each shard re-checks during the run, pausing while `pg_stat_activity` exceeds 60. Doc 02 has the full rule (decisions of 2026-11-01 and 2026-11-12). Run `ListAgents` before a full-population run so two such jobs don't collide.
- The nightly refresh is no longer a fixed no-go window. Before each step, a job checks whether `pipeline-refresh` is running. A full-population job pauses while it runs. A job scoped to a set of companies may run alongside it. A trivial query hanging is a signal to stop and check, not to retry.
- Every long job sets its own `statement_timeout` and wall-clock cap; the pooler default (2 min) kills full-population scans and rolls back whole scripts.
- A schema change applied to the live database without a committed migration silently diverges from `main`.
- This Mac's disk can fill and hang a process silently (`df -h /private/tmp`); `/tmp` can be wiped by a restart. Re-derive state from a live query, not an old file.
- Killing another session's process or cancelling its CI run needs that session's confirmation.

## Architecture and layout (one screen)

SEC EDGAR → Collector (raw, lossless) → Normalizer (canonical facts) → Mapper/Metrics (canonical concepts, versioned formulas) → Company Master → Screener ← AI query layer → Next.js. Schemas: `raw`, `core`, `analytics`, `app`. One monorepo: `pipeline/` (Python 3.12, Polars, Postgres; its own [`pipeline/CLAUDE.md`](pipeline/CLAUDE.md)), `apps/app` (Next.js, public `scrooner.com` and authenticated `/app`), `apps/backend` (FastAPI, internal product use only), `packages/design-system`. Supabase Pro for Postgres, Auth and Storage.

## Where things live

- Doc map: [`doc/README.md`](doc/README.md). Data-correctness entry point: [`doc/data-moat/README.md`](doc/data-moat/README.md). Day-by-day engineering journal: `doc/learnings/`.
- Accounting or XBRL meaning: `data-team/tags/cards/`, then `data-team/22-FILING-LESSONS-LEDGER.md`. Release and commit rules: `data-team/08-RELEASE-MANAGER.md`.
- Shared team memory: `mind/mind.py search` before reading docs; capture durable findings with `mind.py add` (never in this file).
