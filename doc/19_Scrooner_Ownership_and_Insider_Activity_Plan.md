# 19 — Scrooner: Ownership, Insider Activity, and Other EDGAR-Native Data Points

Doc 18 named ownership/insider data as *the* real differentiator toward a $100/year product. This doc scopes it as a full, buildable execution plan — not a rough survey — after a real, live investigation that corrected its own first draft twice before anything got built. See §1 for that correction story in full; it's kept in, not cleaned up, because the user explicitly asked for "how and when we figured this out."

> **Status:** Canonical for Stages 1-4 (2026-08-17) — built and verified against the full golden-10, not a sample. Stage 5 (DEF 14A / deep 8-K text parsing) remains explicitly deferred, gated on its own unsolved problem (unstructured text, P2 per doc 10). Stage 4's design blocker (CUSIP↔CIK crosswalk) was resolved and then built the same day — see §5 and `doc/learnings/form-13f-cusip-crosswalk.md` for the full investigation plus two real bugs found and fixed during verification. **Owner:** Founder / Product · **Review:** When Stage 5 is picked up, or when a core decision changes.
>
> **A note on this doc's own numbers**: §1's table below was itself corrected twice more after being first written — once mid-build (Stage 2, the Form-4 issuer-ambiguity finding) and once at verification (Stage 3, the Schedule 13G-family count itself was a significant undercount). See `doc/learnings/ownership-and-8k-discovery.md` for the full sequence — this doc's own history is a live example of the discipline it documents, not just a description of it.

---

## 1. The correction story — two wrong drafts before the real answer

**First draft (wrong)**: claimed 74 Form 4s, 37 8-Ks, 9 Form 13Fs, 60 Schedule 13G/A already indexed for the golden-10, "zero new discovery work needed." This came from querying `raw.sec_filing_documents` (Module 5, the daily-index-based Filing Metadata Collector) without filtering by CIK at all — the true source included **181 companies**, not the golden-10 specifically.

**Caught by**: re-running the same query with an explicit `cik = any(golden_ciks)` filter, the way every other claim in this project gets checked. Real result: **1** Form 4, **1** 8-K, **1** 13F-HR, **1** Schedule 13G for the *entire* golden-10 — not 74/37/9/60. A materially different, much weaker finding.

**Investigated why**: read `collector/filings.py`'s own module docstring (it says so directly, not discovered by guessing) — Module 5 scans SEC's **daily index**, one calendar date at a time. `raw.sec_filing_documents` only contains whatever the incremental Collector job happened to run for on specific real calendar days during this project's build — not a historical backfill for any company. The 181-company, low-golden-10-count picture was real, just not what "already indexed" should have meant.

**Second, correct finding**: the Collector's *other* fetch (Module 4, `raw.sec_submissions` — each golden company's own submissions.json, fetched comprehensively back in the Collector phase and still sitting in Storage) already contains full historical entries for **every** form type, cross-indexed by EDGAR under the issuer's own CIK. Checked live, company by company:

| Ticker | Form 4 | 8-K | Form 3 | Schedule 13G-family | DEF 14A |
|---|---|---|---|---|---|
| AAPL | 587 | 105 | 11 | 2 | 11 |
| MSFT | 726 | 63 | 11 | 1 | 6 |
| JPM | 134 | 26 | 1 | 47 | 1 |
| GOOGL | 526 | 41 | 6 | 2 | 3 |
| XYZ (Block) | 572 | 63 | 9 | 4 | 6 |
| NKE | 658 | 116 | 24 | 6 | 12 |
| ARCC | 156 | 220 | 16 | 1 | 26 |
| RDDT | 267 | 15 | 15 | 10 | 2 |
| ENB | 160 | 132 | 26 | 9 | 2 |
| TSM | 173 | — | 42 | 8 | — |
| **Total** | **3,959** | **781** | **161** | **90** | **69** |

**Zero new SEC fetches needed for the *list* of these filings** — this part of the original claim was directionally right, just attributed to the wrong Collector module. What *does* still need fetching: each individual filing's actual document body (the list only has accession numbers/dates/form types, not transaction/ownership detail) — confirmed live for a real AAPL Form 4 (§2) and a real AAPL Schedule 13G (§3).

**This table itself was still an undercount, found only once Stage 3 actually ran against the full golden-10.** The Schedule-13G-family column above (90 total) only reflected the base `submissions.json` file's own `filings.recent` window — the same kind of partial view Module 5's mistake (above) already illustrated once. Running Stage 3 for real (base + continuation pages, matching Stage 1/2's own pattern) surfaced **3,637** total Schedule 13D/13G-family filings across the golden-10, not 90 — almost entirely from **JPM alone (2,975)**, which turns out to be a heavy institutional *filer* (JPMorgan Asset Management disclosing >5% stakes in hundreds of other companies), not because JPM itself has that many disclosures made about it. Of those 3,637, only **527** survive the issuer-check as genuine stakes *in* the golden company itself (see §4's final table) — the other ~3,036 are JPM (or another golden company acting as an institutional filer) disclosing a stake in someone else, exactly the ambiguity §1 already predicted, just at a much larger real scale than the original spot-check suggested.

**A second, deeper correction, found while verifying Schedule 13G specifically**: a filing appearing under a golden company's own submissions.json is **not always about that company as subject**. Checked directly: a Schedule 13G found under **JPM's** own CIK turned out to be JPM's asset-management arm disclosing a stake **in Chipotle** — JPM as filer, not subject. A second Schedule 13G, found under **AAPL's** own CIK, correctly showed Vanguard Capital Management disclosing a stake **in Apple** — AAPL as subject, the wanted direction. **Both directions are real and cross-indexed under the same company's submissions list; only checking the filing's own `issuerCik` field distinguishes them — never assume direction from which company's file it was found in.** Form 4 does not have this ambiguity (verified: its `issuerCik` field directly and unambiguously matches the golden company for a real sample) — one company generally can't be an "insider" of another the way it can be an institutional shareholder.

---

## 2. Stage 1 — 8-K into `core.filing` (built)

Cheapest possible win: 8-K shares `core.filing`'s exact existing shape (accession_number, form, filing_date, period_of_report). Widened `FORM_ALLOWLIST` in `normalizer/identity.py` to include `8-K`/`8-K/A`, same table, same parsing code, zero new schema.

## 3. Stage 2 — Form 4 insider transactions (built, full golden-10)

**What it gives**: every open-market buy/sell/tax-withholding/option-exercise disclosed on Form 4 by an officer, director, or 10%+ owner — exact shares, price, date, resulting position. Form 3/5 deliberately out of this pass (Form 4 is doc 10's own named "core insider-activity feed"; Form 3's holding-only XML structure needs its own verification pass, and its document-naming doesn't follow Form 4's predictable pattern — checked live, not assumed).

**Verified against the full golden-10, not a sample**: 55,109 real transactions stored, from 15,684 filings considered (99% parsed — the small remainder is legitimately pre-2003 HTML-era Form 4s, before EDGAR's XML mandate for ownership forms, correctly skipped rather than forced).

**A real correction found only at full-scale run, not the small sample**: an earlier version of this doc claimed Form 4 has no issuer-vs-filer ambiguity ("one company can't be an insider of another"). Wrong — running the full golden-10 surfaced **285 real mismatches** (194 for JPM, 81 for GOOGL, plus smaller counts elsewhere): JPMorgan itself crossing a 10%-ownership threshold in another company and filing as that company's insider; Alphabet's venture arm ("GV 2019 GP, L.L.C.") filing insider disclosures for its own portfolio companies under Alphabet's CIK. The issuer-check (implemented defensively from the start, believed unnecessary) already excluded every one of these correctly — see `doc/learnings/ownership-and-8k-discovery.md` for the full finding.

**New table**: `core.insider_transaction` — one row per transaction, referencing the source filing for lineage, `Decimal` throughout (shares/price are financial values, same discipline as everywhere else in this project).

## 4. Stage 3 — Schedule 13D/13G beneficial ownership (built, full golden-10)

**What it gives**: >5% beneficial-ownership disclosures — activist stakes, major institutional holders. **Requires the issuer-direction check found in §1** — every parsed filing is verified against its own header's `issuerCik` before being stored as "ownership of this company"; a filing where the golden company is the *filer*, not the *subject*, is correctly skipped, not miscounted. A header where `issuer_cik` couldn't be extracted at all is treated as inconclusive and skipped too — never defaulted to "match."

**No structured XML exists for this form type, at any point in its history** — checked live against both a 2024 and a 1995 filing before writing the parser; every Schedule 13D/13G primary document, in every year checked, is plain HTML/text. What *is* structured, and stable back to at least 1995: every filing's full-submission `.txt` carries a machine-readable SGML header (`SUBJECT COMPANY`/`FILED BY` blocks, each with a `CENTRAL INDEX KEY`) — exactly what's needed to resolve the issuer-vs-filer ambiguity, without parsing any free-text body. `percent_of_class`/`shares_owned` live only in that free-text body and are deliberately left `NULL` this pass rather than guessed at — a real, explicit follow-up, not silently skipped.

**Verified against the full golden-10**: 3,637 Schedule 13D/13G-family filings considered, **527** confirmed genuine stakes stored (issuer-matched), 3,036 correctly excluded as the golden company acting as filer not subject, 74 headers unparseable (all pre-2003, logged and skipped, not silently miscounted). AAPL's own 81 stored stakes correctly lead with its actual largest real holders — Berkshire Hathaway, Vanguard Group, BlackRock — spot-checked directly against the stored rows, not assumed.

**New table**: `core.beneficial_ownership` — one row per disclosed stake, `schedule_type` (13D implies activist intent, 13G passive), `percent_of_class`/`shares_owned` (currently `NULL`, see above), filer name.

---

## 5. Stage 4 — Form 13F institutional ownership (built and verified 2026-08-17)

**Built.** Its blocking design question — does a usable CUSIP↔CIK crosswalk exist for free? — needed no external vendor. Schedule 13D/13G cover pages (Stage 3 already fetches these) carry a *mandatory* "CUSIP Number" field for the subject security — confirmed live on a real AAPL filing (`037833100`), cross-checked against a second free source (OpenFIGI). SEC's own Form 13F structured data never carries an issuer CIK, only CUSIP (confirmed against SEC's official spec PDF) — so the crosswalk had to come from somewhere else, and it does, from data this project already fetches for an unrelated reason. Full investigation: `doc/learnings/form-13f-cusip-crosswalk.md`.

**What got built**: (1) `CUSIP` capture added to Stage 3's parser (`beneficial_ownership.py`) — no new fetch, extracted from the same full-submission `.txt` already downloaded, checked against three differently-formatted real filings before trusting one regex. All 10 golden companies got at least one real CUSIP; JPM's history alone surfaced three across a 30-year span (`163722853` → `16161A108` → `46625H100`), a real artifact of the CIK's corporate-merger history (Chemical Banking → Chase Manhattan → JPMorgan Chase), not a parsing bug. (2) A new module, `ownership/institutional.py`, downloads SEC's bulk Form 13F data set (`SUBMISSION`/`COVERPAGE`/`INFOTABLE`, all managers, ~100MB per ~3-month filing window — cached the same way as companyfacts/submissions bulk zips) and matches `INFOTABLE` rows by CUSIP, writing into new `core.institutional_ownership`. (3) `apps/site`'s company page now renders a real "Institutional Ownership" section.

**Real numbers, full golden-10, single most-recent filing window (`01mar2026-31may2026`)**: **58,095** matched institutional holdings out of **3,822,885** total INFOTABLE rows in that window — every golden company represented, from AAPL's 9,866 rows down to ARCC's 1,069. AAPL's top holder correctly resolves to Vanguard Capital Management LLC (953.85M shares, $242.08B) — implied per-share price is identical across every row for a given company, a strong internal-consistency check that no unit got mixed up.

**Deliberately scoped to one snapshot window, not a multi-quarter trend** — matches the free-tier budget discipline every other phase has followed (doc 09's live-measured capacity check); a historical trend is a real future follow-on, not this pass.

**Two real bugs found and fixed during verification**, both against real rendered output, not caught by any type check: a SQL `ORDER BY` that silently bound to a same-named text-cast output column instead of the underlying numeric one (sorted "9995" above "9990000" lexicographically); and a stale field description in SEC's own reference spec PDF ("Market value x$1000") that doesn't reflect a 2023-01-03 SEC rule change to report `VALUE` in actual dollars — caught only by checking the bulk zip's own bundled `FORM13F_readme.htm`, after a first render briefly showed AAPL's top holder as a $242 **trillion** position. Full detail and the generalizable lessons: `doc/learnings/form-13f-cusip-crosswalk.md`.

## 6. Stage 5 — DEF 14A / deep 8-K text parsing (deferred, explicitly)

Narrative- and HTML-table-heavy, not XBRL/structured-XML like Stages 1-4. P2 in doc 10's own priority scheme. Not proposed for this pass.

---

## Definition of Done (Stages 1-3)

**Output**: 8-K filings appear in `core.filing` alongside 10-K/10-Q; real insider transactions render with exact shares/price/date, traceable to the source accession number; real beneficial-ownership stakes render only when the golden company is confirmed as issuer, never when it's the filer.

**Operationally**: reprocessing a company reproduces identical rows (determinism); a Schedule 13G/13D where the golden company is the filer, not the subject, is correctly excluded, not silently miscounted; every stored transaction/stake traces to a real, fetchable SEC accession number.

---

## Repository footprint

```text
pipeline/
├── src/scrooner_pipeline/
│   └── ownership/                    # NEW
│       ├── insider.py                   # Stage 2 -- Form 3/4/5 download + parse
│       └── beneficial_ownership.py      # Stage 3 -- Schedule 13D/13G, incl. issuer-direction check
└── db/migrations/
    └── 0009_ownership_schema.sql     # NEW -- core.insider_transaction, core.beneficial_ownership
```

`normalizer/identity.py`'s `FORM_ALLOWLIST` widened in place for Stage 1 — no new file.

---

## What this doc does *not* decide

- Form 13F's CUSIP-mapping design — flagged, not solved.
- Any DEF 14A or deep 8-K text-parsing work — explicitly deferred, P2.
