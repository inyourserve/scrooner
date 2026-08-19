# 08 — Scrooner Collector Execution Plan

The concrete build plan for Part 1 (Data Collector) from doc 06: architecture, database schema, folder structure, tasks, priorities, tests and a 7-day target.

> **Status:** Canonical (promoted from Draft 2026-08-14 — all 7 days built and independently verified against live data; see [doc 08b](08b_Collector_Definition_of_Done_Evidence.md) for the Definition-of-Done evidence) · **Owner:** Founder / Product · **Review:** When the Collector's implementation changes in a way that would invalidate this plan

---

## What this doc is

Doc 06 defines the Collector's scope, modules and definition of done, then says: *"the team builds the Collector-only execution plan — architecture, database schema, folders, tasks, priorities, tests, and a 7-day target."* This is that plan. It does not relitigate anything already locked — it operationalizes doc 02, 04, 06 and 07 into something buildable this week. If anything here conflicts with those, they win; fix this doc, not your assumptions.

**Not in scope here:** Normalizer, Mapper, anything past raw storage. If you find yourself calculating a ratio or deciding what a fact means, stop — that's the next doc, not this one.

---

## Repository

`pipeline/` inside this repo (`scrooner`) — **not** a separate repo. Doc 02 originally locked "Separate Scrooner Data project," read as a separate git repo; that's since been superseded (2026-08-14) back to a monorepo for solo-founder manageability — one `.claude/` config, one `CLAUDE.md`, no cross-repo doc-pointer maintenance. See doc 02 for the full reasoning and the trigger for splitting it back out (hosting for the Python worker firming up, or a team forming). The boundary discipline below still applies just as strictly — a folder wall is weaker than a repo wall, so it matters *more* here, not less.

`src/` layout (not a flat top-level package) — standard Python packaging practice, adopted 2026-08-14 before any real code existed so it never has to be a disruptive rename later:

```text
pipeline/
├── src/
│   └── scrooner_pipeline/
│       ├── collector/
│       │   ├── universe.py       # Module 1 — Company Universe
│       │   ├── identity.py       # Module 2 — SEC Identity / CIK mapping
│       │   ├── companyfacts.py   # Module 3 — Company Facts Collector
│       │   ├── submissions.py    # Module 4 — Submissions Collector
│       │   ├── filings.py        # Modules 5+6 — Filing Metadata + Filing Documents
│       │   ├── storage.py        # Module 7 — Raw Storage (Supabase Storage client)
│       │   ├── scheduler.py      # Module 8 — Scheduler
│       │   ├── retry.py          # Module 9 — Retry / Failure Handling (Tenacity policies)
│       │   ├── integrity.py      # Module 11 — Data Integrity Checks
│       │   └── logs.py           # Module 10 — Collection Logs (structlog config)
│       ├── common/
│       │   ├── config.py         # Pydantic settings (env vars, User-Agent string, rate limit)
│       │   └── sec_client.py      # httpx client: declared User-Agent, ≤8 req/s, timeouts
│       ├── db/
│       │   └── connection.py       # psycopg connection handling
│       └── jobs/
│           ├── bootstrap.py         # Typer command: one-time bulk load
│           └── incremental.py        # Typer command: daily/scheduled catch-up
├── db/
│   └── migrations/        # raw schema DDL (see below) — plain SQL, not part of the installable package, so it lives outside src/
├── tests/
│   ├── golden_companies/      # fixtures — see Tests section
│   └── ...
└── scripts/                    # one-off ops scripts, never imported by the app
```

Runtime, per doc 04's Collector V1 technical design (unchanged, just restated so this doc is self-contained): Python 3.12, no web framework; httpx for HTTP; Pydantic for validation/config; Tenacity for retries; psycopg for DB access; Typer for the CLI; structlog for logging.

---

## Database schema — resolves the open naming question

Doc 04 locked the **schema names** (`raw`/`core`/`analytics`/`app`) but not table names within them; doc 06 proposed concrete SEC-specific names. This resolves it: **the Collector writes only to `raw`, using doc 06's concrete names, verbatim from SEC — no interpretation, so nothing here crosses into `core`.**

| Table | Purpose | Key fields |
|---|---|---|
| `raw.company_universe` | SEC's own ticker↔CIK↔name list (`company_tickers.json`), stored as published. **Upserted** on `(cik, ticker)` — this one table tracks current known state, not a fetch history. | `cik`, `ticker`, `company_name`, `collected_at` |
| `raw.sec_companyfacts` | **Append-only** — one new row per fetch, never updated or overwritten, even if the payload is byte-identical to the last fetch. This is what makes the archive lossless: history is reconstructable from the row set alone. | `cik`, `fetched_at`, `source_url`, `sha256`, `storage_path`, `http_status` |
| `raw.sec_submissions` | **Append-only**, same rule as above. | `cik`, `fetched_at`, `source_url`, `sha256`, `storage_path`, `http_status` |
| `raw.sec_filing_documents` | **Upserted** on `(cik, accession_number)` — a filing is immutable once filed (amendments get a new accession number), so `download_status` (`indexed`\|`downloaded`\|`failed`) transitions in place via UPDATE, not a new row. `storage_path`/`sha256` are nullable until `downloaded`, since doc 06 says not to fetch every attachment on Day 1. | `cik`, `accession_number`, `form`, `filing_date`, `report_date`, `source_url`, `sha256`, `storage_path`, `download_status`, `collected_at` |
| `raw.collector_runs` | One row per collection run | `id`, `run_type` (`bootstrap`\|`incremental`), `started_at`, `finished_at`, `status`, `stats` (jsonb) |
| `raw.collector_errors` | Dead-letter / failure log | `id`, `run_id`, `cik`, `source`, `error_type`, `message`, `occurred_at`, `resolved` |

Why `company_universe` is `raw`, not `core`: it's SEC's list stored as-is — no dedup, no reconciliation, no judgment call. The moment anything needs deciding (a ticker changed issuer, two CIKs look like the same company, which listing is primary) that's identity *resolution*, which belongs to Company Master (doc 06, Part 4), not the Collector. This keeps the Collector boundary doc 04 requires absolute: it never writes `core`, `analytics`, or `app`. It's upserted rather than append-only — like `sec_filing_documents` above, and unlike `sec_companyfacts`/`sec_submissions` — because it's explicitly a mirror of SEC's current list, not a fetch log. Noted so nobody "fixes" either of those two into append-only later without realizing that was deliberate.

**Verified live against the real endpoint (2026-08-14), not assumed:** `company_tickers.json` returns only `cik_str`/`ticker`/`title` — no `exchange`, no `status`. And CIK↔ticker is **one-to-many**: 1,448 of 7,995 CIKs (18%) have more than one ticker (e.g. Alphabet/CIK 1652044 → `GOOGL`/`GOOG`/`GOOGM`/`GOOGN`). That's why the primary key is `(cik, ticker)`, not `cik` alone — an earlier version of this table had `cik` as the sole key, which would have silently dropped every multi-ticker company. `exchange` isn't fetched here at all: it lives in the Submissions API (doc 07 §4) — fetching it per-company on Day 2 would mean 8,000 individual requests against the "prefer bulk over per-company hammering" rule (doc 07 §3). **Corrected 2026-08-14** (an earlier version of this line was wrong): it does not get its own column populated during Day 3. Day 3's bulk `submissions.zip` pass stores each company's submissions JSON verbatim in `raw.sec_submissions` (§ below) — `exchanges` lives inside that stored payload, same as every other submissions field. Extracting it into a structured column is Company Master's job (doc 06, Part 4), not the Collector's — adding a `raw.company_universe.exchange` column now would mean the Collector deciding how to reconcile it when a company has multiple exchange values over time, which is interpretation. There's no `status` column because no SEC endpoint provides one; deciding what "active" means is interpretation too, same reasoning.

Large payloads (raw JSON/XBRL) go to Supabase Storage; `storage_path` in the tables above points to the object, following SEC's own layout so the path is self-documenting:
```
raw/sec/companyfacts/{cik}/{fetched_at_iso}.json
raw/sec/submissions/{cik}/{fetched_at_iso}.json
raw/sec/filings/{cik}/{accession_number}/{document_type}
```
Postgres holds metadata and the pointer, never the blob itself (doc 04's raw-storage principle).

**Practical note for Day 3:** `companyfacts.zip` is a multi-GB bulk download that unzips to considerably more — stream-unzip and stream-upload per company rather than holding the whole archive in memory.

---

## Tasks, priorities and a 7-day target

Bootstrap before incremental, identity before facts (you can't collect what you can't address), and skip the long tail on Day 1 — doc 06 is explicit: *"Do not necessarily download every possible SEC attachment on Day 1. KISS BORING."*

| Day | Deliverable | Done when |
|---|---|---|
| **1** | Repo scaffold, Python 3.12 env, Supabase project wired up, `raw` schema migration applied, `common/config.py` + `common/sec_client.py` (declared User-Agent, ≤8 req/s limiter) | A throwaway script can hit one SEC endpoint through the shared client and get a 200. |
| **2** | `collector/universe.py` + `identity.py` — fetch SEC's `company_tickers.json`, populate `raw.company_universe` | Row count matches SEC's published list; rerunning doesn't duplicate rows. |
| **3** | `collector/companyfacts.py` + `submissions.py` — bootstrap via bulk `companyfacts.zip` / `submissions.zip`, raw payloads to Storage, metadata + checksums to Postgres | 10 golden companies (below) have raw company-facts and submissions stored with matching SHA-256. |
| **4** | `collector/retry.py` — Tenacity backoff, idempotency keys, checkpoint/resume | Kill the bootstrap job mid-run; rerun; zero duplicate objects, zero lost companies. |
| **5** | `jobs/incremental.py` — SEC daily index / recent-filings endpoints, same rate limit | Running it a day after bootstrap finds only genuinely new filings. |
| **6** | `collector/logs.py` + `integrity.py` — structured run logs, checksum reconciliation report | A report shows expected vs. actual object counts/hashes per run, with zero unexplained deltas. |
| **7** | End-to-end proof against doc 06's Definition of Done | Resume-after-failure, no unnecessary re-download, fair-access respected, failures logged, historical raw data preserved — all demonstrated, not asserted. |

Anything not on this list (Filing Document Collector's full attachment set, the Scheduler beyond a manual trigger, multi-region deploy) waits. That's doc 06's "should NOT" list and doc 05's "kill scope aggressively" working as intended, not something slipping through the cracks.

---

## Tests — golden-company set

Per doc 05's data-quality methodology: pick companies that stress different edge cases, not just the easy case.

**Finalized 2026-08-14** (was illustrative placeholders through Day 2) — the real set, chosen by checking live SEC data rather than guessing, lives at [`pipeline/tests/golden_companies/companies.json`](../../pipeline/tests/golden_companies/companies.json):

| Ticker | CIK | Why it's in the set |
|---|---|---|
| AAPL | 0000320193 | Baseline large-cap 10-K filer. Also non-calendar fiscal year end (late September). |
| MSFT | 0000789019 | Second baseline large-cap 10-K filer. Non-calendar fiscal year end (June 30). |
| JPM | 0000019617 | Baseline, calendar FYE. Verified live to have 69 submissions continuation files beyond the base file — stresses pagination. |
| GOOGL | 0001652044 | One CIK, four simultaneous tickers (GOOGL/GOOG/GOOGM/GOOGN) — the exact multi-ticker case that motivated the Day 2 `(cik, ticker)` primary-key fix. |
| XYZ | 0001512673 | Block, Inc. — ticker changed from SQ in December 2021; ticker is a mutable nickname, CIK isn't. |
| RDDT | 0001713445 | Reddit — recent IPO (March 2024). Verified live to have zero submissions continuation pages, unlike the older large filers above. |
| TSM | 0001046179 | Taiwan Semiconductor — foreign private issuer, 20-F. Verified live to report under `ifrs-full`, not `us-gaap` — stored as-is without assuming a us-gaap shape. |
| ENB | 0000895728 | Enbridge — Canadian MJDS filer, 40-F. Non-10-K/10-Q form-type handling. |
| ARCC | 0001287750 | Ares Capital — has a real 10-K/A amendment on file. |
| NKE | 0000320187 | Nike — second non-calendar FYE example (May 31), independent of the AAPL/MSFT pair. |

Each golden company gets a fixture asserting: raw payload fetched, checksum recorded, `raw.collector_runs`/`raw.collector_errors` rows correct, and a second run is a no-op (idempotency). This set becomes the permanent regression fixture per doc 05 — every edge case found later gets added here, never fixed silently.

---

## Definition of done (restated from doc 06, so this doc is self-contained)

Not "we downloaded Apple." Given a CIK/company universe, for every supported company: raw company-facts payload, raw submissions payload, collection metadata, timestamp, source identifier, and status — with the system able to resume after failure, retry transient failures, avoid unnecessary re-downloads, respect SEC fair-access limits, log failures, run repeatedly, identify new filings, and preserve historical raw data. Only then does the team move to the Normalizer.
