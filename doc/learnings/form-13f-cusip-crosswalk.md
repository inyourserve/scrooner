# Form 13F's CUSIP↔CIK crosswalk — the design question doc 19 Stage 4 left open, resolved

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

Doc 19 §5 deferred Stage 4 (Form 13F institutional ownership) behind an explicit unsolved question: "does a usable CUSIP↔CIK crosswalk exist for free?" — because Form 13F's `INFOTABLE` lists holdings by CUSIP, a security identifier this pipeline had never needed before (CIK/ticker only, everywhere else). This was investigated live, not reasoned from memory, prompted by the user asking about screener.in-style shareholding-pattern data before green-lighting more frontend work.

## What was checked live

**SEC's own Form 13F Data Sets spec** (fetched directly — `https://www.sec.gov/files/form_13f.pdf`, the primary source, not a summary): confirmed the gap is real. `SUBMISSION.CIK` is explicitly the *filer* (the institutional manager) only. `INFOTABLE` — the actual holdings table — has `CUSIP` + `NAMEOFISSUER` + `SSHPRNAMT`/`VALUE`, but no issuer CIK field anywhere in any of the seven tables. Nothing in SEC's own 13F data ever tells you the issuer's CIK.

**Where the golden company's own CUSIP already sits, unused**: Schedule 13D/13G cover pages have a *mandatory* "CUSIP Number" field for the subject security — required by the form itself, not optional. Stage 3 (`beneficial_ownership.py`) already fetches and parses these documents for every golden company; it just wasn't capturing this field. Confirmed on a real, already-fetched AAPL Schedule 13G/A (`0001193125-24-036431`):

> `APPLE INC. (Name of Issuer)  COMMON STOCK ...  037833100 (CUSIP Number)`

Per doc 19 §1's own table, every one of the golden-10 has at least one Schedule 13G-family filing on file — so this generalizes across the full golden-10 with **zero new fetches**, just one more field captured while parsing documents Stage 3 already opens.

**Cross-checked against a second, independent free source**: OpenFIGI's unauthenticated mapping API (`POST https://api.openfigi.com/v3/mapping`, no key, 5,000 free lookups/day) correctly resolved `037833100` → `ticker: AAPL, name: APPLE INC` — confirming the value pulled from the filing is right, and giving a fallback path for the rare company with no Schedule 13G/13D on file (implies no holder ever crossed 5%).

**A third candidate source was checked and ruled out**: guessed that SEC's mandatory post-2019 10-K "Description of Securities" exhibit (Item 601(b)(4)) might state CUSIP universally. Checked AAPL's real FY2024 10-K exhibit (`a10-kexhibit4109282024.htm`) directly — no CUSIP present. Don't assume this path works for other companies without checking each one; the 13G/13D cover-page field is the confirmed source, not this.

## The design answer

No external crosswalk vendor or CUSIP-licensing question needed. The chain is entirely inside data this pipeline already touches or that SEC already publishes for free:

1. Capture `CUSIP` while parsing Schedule 13D/13G cover pages (Stage 3, already fetching these documents — small addition, not a new fetch).
2. New Collector scope: SEC's quarterly bulk Form 13F flat files (`SUBMISSION`/`INFOTABLE`, all managers) — this *is* a genuinely new fetch, since 13F is filed *about* holdings, not *by* the issuer, so it can't be found under a golden company's own `submissions.json` the way every other form type in doc 19 could.
3. Filter `INFOTABLE` rows where `CUSIP` matches a golden company's known CUSIP, aggregate `SSHPRNAMT`/`VALUE` across managers → real aggregate institutional-ownership data, the actual US equivalent of screener.in's shareholding-pattern chart (doc 17 §3 already ruled out "Promoter Holding" itself as non-portable, but named institutional ownership as the honest substitute).

Also avoids the CUSIP-copyright dispute entirely (ABA/CGS v. plaintiffs, ongoing antitrust litigation over redistributing CUSIP's *master database*) — this reads a CUSIP the filer was legally required to disclose in one public SEC filing, to match against another public SEC filing. Not the licensed database.

## Generalizable lesson

Before reaching for a third-party vendor or crosswalk service to fill a data gap, check whether the missing field is already a *mandatory disclosure* on a document this project fetches for an unrelated reason — Schedule 13D/13G's CUSIP requirement was sitting unused in a module already built for a different purpose (issuer/holder identification, not security identification). Same shape as doc 19's own repeated finding elsewhere in this phase (`raw.sec_submissions` already had the ownership filing list, no new discovery fetch needed) — the free-tier, "evidence before expansion" discipline (doc 05) keeps paying off by checking what's already been fetched before assuming something new must be built or bought.

## Status

**Built and verified against the full golden-10 (2026-08-17)**, same day as the investigation above. `ownership/institutional.py` downloads SEC's bulk Form 13F data set (cached via the same `get_cached_bulk_zip` mechanism as companyfacts/submissions), matches `INFOTABLE` rows by CUSIP against each golden company's own CUSIP (captured by the Stage 3 change above), and writes into new `core.institutional_ownership`. Real results: **58,095** matched holdings across all 10 golden companies, out of **3,822,885** total INFOTABLE rows in the one filing window fetched (`01mar2026-31may2026`) — every company got real data, from AAPL's 9,866 rows down to ARCC's 1,069. Real top holders check out correctly against public knowledge: AAPL's largest is Vanguard Capital Management LLC (953.85M shares, $242.08B), JPM's is the same entity (165.28M shares, $48.62B) — both plausible, and internally consistent (implied per-share price is identical across every row for a given company, confirming no unit-mixing).

Two real bugs found and fixed during live verification, not before:

1. **A SQL `ORDER BY` silently bound to the wrong column.** `getTopInstitutionalHolders` (`apps/site/src/lib/db.ts`) cast `shares` to text in its outer `SELECT` without an alias, then wrote an unqualified `order by shares desc` — Postgres resolves an unqualified `ORDER BY` name against an output column alias before a same-named `FROM`-clause column, so the sort silently ran as a *text* comparison ("9995" > "9990000" lexicographically) instead of numeric. First render showed AAPL's top "institutional holder" as a 9,995-share position, with the real ~954M-share Vanguard position buried below it. Fixed by qualifying the reference (`order by dedup.shares desc`), which is unambiguous. Lesson: casting a column to text in a `SELECT` list without an explicit alias creates a same-named output column that can silently shadow the numeric one it came from in any later `ORDER BY` — always alias a cast column, or qualify the sort reference, whichever makes the binding unambiguous.

2. **The field-layout spec PDF's own description was stale.** SEC's `VALUE` field is documented in the reference PDF (`form_13f.pdf`, fetched during the design investigation above) as "Market value (x$1000)" — and the earlier design investigation cited that description without knowing it had changed. The bulk zip's own bundled `FORM13F_readme.htm` (shipped inside every download, not fetched separately, easy to skip) states the real current rule: **"Starting on January 3, 2023, market value is reported rounded to the nearest dollar. Previously, market value was reported in thousands."** Multiplying by 1,000 anyway (mirroring the stale PDF) turned AAPL's real ~$242B Vanguard position into a displayed **$242 trillion** figure before this was caught by eyeballing the rendered page, not by any automated check. Fixed by treating `VALUE` as already-dollars (the whole bulk window used here is 2026 data, entirely post-2023-01-03, so this is never ambiguous for this data set) and renaming the column from the wrong `value_usd_thousands` to `value_usd` so the name itself can't mislead a future reader the way the SEC field's own historical name did. Lesson: a dataset's own bundled metadata/readme (shipped with the actual data) is a more current source of truth than a separately-fetched reference spec document, even an official one from the same publisher — check both, and prefer the one that travels with the data itself when they could disagree.

See doc 19 §5 for the final status line and `pipeline/CLAUDE.md` for the durable, project-wide version of both lessons above.
