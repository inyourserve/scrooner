# Ownership & Insider Activity (doc 19) — how the real design got found, wrong-first

## The claim that was wrong, and why it looked right at first

Scoping doc 19, the first draft claimed "74 Form 4s, 37 8-Ks, 9 Form 13Fs, 60 Schedule 13G/A already indexed for the golden-10, zero new discovery work needed." This came from querying `raw.sec_filing_documents` (Module 5, the daily-index-based Filing Metadata Collector) without an explicit `cik = any(golden_ciks)` filter — the true source of those rows was **181 companies**, not the golden-10 specifically. The number felt plausible because it was a real number, just answering a different question than the one being asked.

**Caught by**: re-running the same query with the CIK filter every other claim in this project gets checked against. Real result: **1** Form 4, **1** 8-K, **1** 13F-HR, **1** Schedule 13G for the entire golden-10 — not 74/37/9/60.

**Investigated why, not just patched the number**: read `collector/filings.py`'s own module docstring. Module 5 scans SEC's daily index, one calendar date at a time — `raw.sec_filing_documents` only has whatever the incremental Collector job happened to run for on specific real calendar days during this project's build, not a historical backfill for any company.

**The real, stronger answer**: `raw.sec_submissions` (Module 4 — each golden company's own submissions.json, fetched comprehensively back in the original Collector build) already has full historical entries for every form type, cross-indexed by EDGAR under the issuer's own CIK. Checked live, company by company — 3,959 Form 4 / 781 8-K / 161 Form 3 / 90 Schedule-13G-family / 69 DEF 14A across the golden-10 (see doc 19 §1's table). Zero new SEC *discovery* fetches needed — this part of the original claim was directionally right, just attributed to the wrong Collector module.

## The second wrong assumption, found while building Stage 3

Doc 19's first design assumed Schedule 13D/13G filings carry a structured XML primary document, the same shape as Form 4 (`edgarSubmission` schema). This was never actually checked against a real filing before being written down — it was inferred from Form 4's shape, not verified.

**Caught by**: fetching a real filing's `index.json` before writing the Stage 3 parser (AAPL's most recent Schedule 13G/A, `0001193125-24-036431`) — every document in that accession folder is `.htm`, none is `.xml`. Checked a second, much older filing (AAPL, 1995, `0000315066-95-002900`) — same result, plain text. **Schedule 13D/13G has never had a structured XML primary document, in any year checked.**

**The real answer**: every EDGAR full-submission `.txt` file (fetchable at a stable, predictable URL for any accession number, old or new) carries a machine-readable SGML header (`<SEC-HEADER>` in modern filings, `<IMS-HEADER>` in pre-1997 ones — same field names either way, confirmed on the 1995 example) with `SUBJECT COMPANY` and `FILED BY` blocks, each carrying a `CENTRAL INDEX KEY`. That header is exactly what's needed to resolve the issuer-vs-filer ambiguity below — reliably, for the full 30-year history, without parsing any free-text filing body. `percent_of_class`/`shares_owned` live only in that free-text body and were deliberately left `NULL` this pass rather than guessed at with a fragile regex across three decades of varying filer formats — same "never guess, leave null" discipline as `core.fact.is_authoritative`.

## The issuer-vs-filer ambiguity — confirmed both directions, live

A filing appearing under a golden company's own `submissions.json` is not always about that company as subject. Confirmed directly, via the header parser, on two real filings:

- **JPM's own CIK, accession `0000019617-24-000658`** → header shows `SUBJECT COMPANY = VICOR CORP (CIK 0000751978)`, `FILED BY = JPMORGAN CHASE & CO`. JPM here is an institutional filer disclosing a stake in an unrelated company, not the subject of the filing.
- **AAPL's own CIK, accession `0001193125-24-036431`** → header shows `SUBJECT COMPANY = Apple Inc. (CIK 0000320193)`, `FILED BY = BERKSHIRE HATHAWAY INC`. Here AAPL genuinely is the subject.

Both directions are real and cross-indexed under the same company's submissions list. `ownership/beneficial_ownership.py` only stores a row when the header's own `issuer_cik` is present **and** matches the golden company — a header where `issuer_cik` couldn't be extracted at all is treated as inconclusive and skipped, never defaulted to "match."

## Third, smaller correction inside Stage 2 itself

`raw.sec_submissions`'s `primaryDocument` field for a Form 4 filing (e.g. `xslF345X06/form4.xml`) is **not** the raw machine-readable document — it's SEC's XSL-viewer path, which returns a 200 with an HTML rendering, not parseable XML. Caught immediately (an `ET.ParseError` on the first real fetch, not a silent bad parse) by checking a failing accession's own `index.json`: the real raw XML sits at the accession folder's top level under just the basename (`form4.xml`), no subfolder. Fixed by stripping the directory prefix from `primaryDocument` before building the fetch URL. A second, unrelated parse-failure class was found and correctly *not* worked around: pre-2003 Form 4 filings (before EDGAR's XML mandate for ownership forms) are plain HTML, not XML at all — these are legitimately skipped, not a bug (verified: AAPL's oldest Form 4, `0001104659-03-004723`, is a real `.htm` document, not corrupted XML).

## Fourth correction: Form 4 has the exact same issuer-vs-filer ambiguity, found only by running the full golden-10, not a small sample

Stage 2's first version claimed Form 4 didn't need an issuer check — "one company can't be an insider of another the way it can be an institutional shareholder" — based on a small real sample (a handful of AAPL filings) where `issuerCik` matched cleanly every time. The check was implemented anyway, defensively, without a strong reason at the time.

That defensive choice caught a real bug the small sample missed. Running the **full** golden-10 (not just AAPL), 285 real issuer mismatches turned up across 5 of the 10 companies:

| Company | Mismatches (of filings considered) |
|---|---|
| JPM | 194 of 2,796 |
| GOOGL | 81 of 1,785 |
| MSFT | 5 of 3,102 |
| ENB | 4 of 164 |
| ARCC | 1 of 200 |

Two distinct real patterns, both confirmed by fetching and reading the actual XML:

- **JPM as institutional insider of someone else**: accession `0000019617-25-000335`'s `issuerCik` is `0001708055` (a different company), with the reporting owner literally named `JPMORGAN CHASE & CO` — JPMorgan itself crossed a 10%-ownership threshold in another public company and had to file Form 4 as that company's insider. A materially different scenario from Schedule 13G's "passive stake" filer, but the same underlying EDGAR behavior: a CIK's submissions.json includes every filing where that CIK appears in *any* role, not just as issuer.
- **A subsidiary filing under the parent's CIK**: GOOGL's 81 mismatches are almost all reporting owner `GV 2019 GP, L.L.C.` (Alphabet's venture-investing arm) disclosing insider positions in GV's own portfolio companies — filed under Alphabet's own CIK, not the portfolio company's.

The check in `insider.py` (present from the start, just believed unnecessary) already excludes every one of these 285 rows correctly — this was not a data-integrity incident, just a wrong docstring. But the same short-circuit bug found in `beneficial_ownership.py` (a missing `issuer_cik` silently passing the check instead of being treated as inconclusive) existed in `insider.py` too and was fixed the same way, defensively, even though no real filing in this run actually exercised it (Form 4's XML schema effectively guarantees `issuerCik` is always present).

**The generalizable lesson updated**: it's not enough to verify a new assumption against *a* real example — verify it against the **full target set**, especially before writing a confident claim into a docstring. A small sample that happens not to exercise an edge case looks identical to a rule that has no edge case. This is the same shape of mistake Company Master 4a already hit once (a ticker-change-date proxy verified against its one design case, wrong for 27 of 38 rows at full-set scale) — now confirmed a second time, in a different module. Worth treating as a standing pattern: a defensive check that "shouldn't be necessary" is cheap insurance precisely because a small sample can't prove it's unnecessary, only fail to disprove it.

## Fifth correction: doc 19's own §1 table was itself an undercount, found only by running Stage 3 for real

The verification pass that produced doc 19 §1's table (90 total Schedule 13G-family filings across the golden-10, JPM's share 47) only checked the base `submissions.json` file's `filings.recent` window — the same partial-view mistake Module 5's original wrong claim illustrated, recurring one level deeper, inside the "correct" answer.

Running Stage 3 for real (base + continuation pages, the same pattern already used for Stage 1/2) surfaced **3,637** Schedule 13D/13G-family filings across the golden-10, not 90 — almost entirely from **JPM alone (2,975 filings)**. Cross-checked directly: JPM is a heavy institutional *filer* — JPMorgan Asset Management routinely discloses >5% stakes in hundreds of unrelated companies, each a separate SC 13G filed under JPM's own CIK. Of JPM's 2,975, only 38 survive the issuer-check as genuine disclosures *about* JPM itself; the other 2,937 are correctly excluded.

Total real, issuer-confirmed stakes across the golden-10: **527** (not 90). AAPL alone: 81, correctly led by its real largest holders (Berkshire Hathaway, Vanguard, BlackRock — spot-checked directly against the stored rows). This doesn't change any conclusion doc 19 already drew (the issuer-check was always going to be needed regardless of the exact count), but it's a second real instance of the same root mistake inside what was already labeled a "correction" — worth noting precisely because it shows a corrected number is not automatically a fully-verified one; the correction itself still needs the same full-run check applied to the original wrong claim.

## The generalizable lesson

Five wrong assumptions across this one doc, each caught the same way, each a variant of the same two root mistakes:

- **Trusting a claim about volume/coverage without running the full check** — Module 5 vs. Module 4 (74/37/9/60 vs. the real 3,959/781/161/90+), and again inside the "correct" answer itself (doc 19 §1's own 90-total Schedule-13G claim, corrected to 3,637 only once Stage 3 actually ran end to end). A number that looks plausible and is real is not the same as a number that answers the right question at the right scope.
- **Extrapolating a new form type's shape from a similar-sounding sibling instead of checking it directly** — Form 4's XML shape wrongly assumed for Schedule 13G; Form 4's issuer field wrongly assumed unambiguous (true for a small sample, false at full-golden-10 scale — 285 real mismatches).

Every one of these would have been caught by the same one-line discipline already established elsewhere in this project (Mapper Day 1's revenue-tag check, Company Master 4a's ticker-proxy check, now proven twice more here): fetch one real example and read it before trusting an assumption about its shape — but also, distinctly, **run the check against the full target set, not just the case that motivated writing it, before writing a confident number down.** A small sample or a partial fetch that happens not to exercise an edge case looks identical to a rule that has none.
