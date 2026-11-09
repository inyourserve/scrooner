# FSN nightly incremental: design (2026-11-09)

Status: built on branch `work/fsn-nightly-incremental`, flag off. Asked for by Dhairya (manager session) at the founder's request. Numbers are MEASURED unless marked.

**Problem.** The hybrid build writes `analytics.canonical_fact` only through `pipeline-fsn-write.yml`, which reads SEC FSN sets. Those sets publish weeks after the filing. The nightly refresh has no FSN step, so every new 10-K/10-Q goes through the old mapper alone. Once migration 0119 makes a company "owned", its new quarters would stay empty.

## Source and parse

- **Source: the filing's own XBRL on EDGAR, sec.gov only.** Per accession the fetcher (`fsn_store/edgar_fetch.py`) reads:
  - `index.json` and the index header (acceptance time, form, period, filer CIKs);
  - `FilingSummary.xml` and `MetaLinks.json`;
  - the instance (`*_htm.xml`), the filer's schema and its linkbases;
  - the R pages of the cover and the statements.
- **Cost.** About 15 requests and 5–22 MB per filing, at most 4 requests per second, with the declared User-Agent and retry on 429/5xx. It uses the same cross-process lock file as `common.sec_client`. TSLA and BAC took 4.6 s and 4.2 s to fetch and 0.1–0.5 s to convert.
- **Converter.** `fsn_store/xbrl_fsn.py` builds the same seven tables the shard writes: sub, num, pre, cal, ren, tag, dim. Its module docstring lists every rule and where it was calibrated: ddate rounding, qtrs/durp/datp, iprx order, uom, dimh and segments (typed axes, LegalEntity → coreg), the version string, non-ASCII stripping and quoting, statement typing, and the pre rows mirroring the R page. Values are the instance's own, as `Decimal`, rounded to 4 decimals as the FSN readme says. Nothing is repaired.

## Equivalence with FSN

`pipeline/scripts/fsn_xbrl_equivalence.py` compares, on the shard view, 20 top-100 filings of the SEC set 2026m10 (17 10-Qs and 3 10-Ks: GOOG, MSFT, AMZN, META, TSLA, MU, JNJ, INTC, COST, KO, BAC, GE, WFC, IBM, PEP, NEE+FPL, T, BA, ACN, CB). Criteria are in `fsn_store/xbrl_equivalence.py`. Result (`pipeline/scripts/results/fsn_xbrl_equivalence/summary.md`): **20 of 20 pass.**

- **num:** 22,774 rows. 0 missing, 0 extra, 0 value or dcml differences on the keys (tag, version, ddate, qtrs, uom, dimh, iprx, coreg).
- **pre:** 155 statement and cover reports. 150 match row for row, and every fact-carrying line matches in all 155. 35 structural rows differ (abstracts, axes or members on KO, PEP, T), which carry no values.
- **cal:** 3,747 arcs. The groups and their (parent, child, weight) are identical.
- **sub:** cik, form, period, fy, fp, fye, filed, accepted and aciks are identical.
- **Statement typing:** across all 1,014 10-K/10-Q filings in 2026m10, 99.1% of 7,401 statement reports get the same type, and 977 filings are right on every report (`stmt_classifier_2026m10.txt`).
- **Not reproduced, and not used downstream:**
  - SEC's cal group and arc numbering, which follows no order the linkbase has. It only enters `filing_check.check_id`, per filing.
  - Which of two identical duplicate facts carries a footnote (12 rows).
  - The taxonomy's own `tlabel` for a standard tag. `fsn.tag` rows are insert-if-absent, so the existing ones stay.
- **CI** pins two of the 20 filings byte for byte (`pipeline/tests/fixtures/fsn_xbrl/`, META and NEE, 0.5 MB), plus a synthetic filing for the rules those two do not exercise. Each rule was mutation-checked: reverting it fails a test.

## Amendments, restatements, floor

- **Amendments.** 10-K/A, 10-Q/A and the transition forms are included.
- **Vintage.** The vintage order is `accepted`, rounded to the minute exactly as FSN rounds it. The store keeps every vintage, and selection is unchanged: latest accepted, SAME_BASIS, never derive across a break. A restatement in a new 10-K is a new vintage, so the existing break and witness rules apply as they do to FSN data.
- **Cover-only amendments** (Part III 10-K/A) load with cover rows only. They print no statement line, so they can never win a cell.
- **Floor.** Candidates need `period_of_report >= 2014-01-01`. `pilot` already drops comparatives before the floor.

## Order, budget, isolation, later FSN set

- **Order.** The step runs in `pipeline-refresh.yml` after `scrooner-incremental` (so `core.filing` is fresh) and before `reprocess_recent_filers.sh` (the old mapper). Once a pair is written, the 0113 `slot_protected_cell` guard and the 0119 owner guard stop the old mapper from overwriting it.
- **Steps** (`pipeline/scripts/fsn_nightly_incremental.sh`):
  1. `scrooner-fsn nightly`: one indexed read with `statement_timeout` 15 s, then fetch and convert. Fetching is capped at 25 minutes, and the rest is deferred.
  2. `load --increment`: one connection, one transaction per company.
  3. `pilot`: map, checks and select.
  4. `pilot-prod`, which writes the before-image, then `done-gate`.
  5. `scrooner-cells load --protect` for the passed pairs of done companies.
  6. A pg_stat_activity headroom check (60 of 90) runs before any write.
- **Time.** At about 5 s per filing, 25 minutes covers about 300 filings. A peak earnings day for the top 1,000 is ASSUMED at 150–250. The step timeout is 45 minutes.
- **Before switching load or write on,** raise the job's 180-minute timeout, because `reprocess_recent_filers.sh` already overran on 2026-11-08 (NOW.md).
- **Isolation.**
  - One filing failing is reported, never raised.
  - `load.run` and `pilot` isolate each company.
  - The script always exits 0, and the step is `continue-on-error`.
  - A filing that did not make it is still absent from `fsn.filing`, so the next night's 7-day lookback retries it.
- **When the FSN set arrives.**
  - EDGAR-built filings carry `fsn_set = 'edgar:<date>'` and a per-accession `src_sha256`.
  - The full company reload now deletes only FSN-set filings plus the accessions its directory carries. So the set's copy replaces the EDGAR copy by accession, and EDGAR copies the sets do not hold yet are kept.
  - An increment never overwrites an accession an FSN set already holds, and reruns are no-ops.
  - No migration was needed (0118 already has `fsn_set` and `src_sha256`).

## Flag and what is left

- **Flag.** `FSN_NIGHTLY_STAGE`, a repository variable or dispatch input, takes `off` (the default), `build` (local files only), `load` (writes fsn.* only) or `write` (canonical_fact with protection). `load` and `write` are production writes and need the founder's typed words before the variable is set.
- **Open.** Gating is per company through today's `done-gate`. The per-(company, data point) gate (Ritwik's ruling, `review/ruling-done-gate-c4-2026-11-09`) should replace it when it lands.
- **Open.** `pilot` against production timed out per company in run 42561798991 (NOW.md), and the same fix applies here.
- **Open.** Standard-tag labels come from `MetaLinks.json`. A filing without it (the pre-2018 renderer) still converts, but a standard line's `plabel` is empty unless the filer relabelled it. Only new filings come through this path, so the case is not expected.
