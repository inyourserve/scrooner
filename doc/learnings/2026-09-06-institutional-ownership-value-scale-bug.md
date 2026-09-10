# Form 13F "value in thousands" convention still present in real 2026 filings — found via a frontend display bug, not a pipeline check

**Date:** 2026-09-06
**Where:** `pipeline/src/scrooner_pipeline/ownership/institutional.py`, `core.institutional_ownership`
**Trigger:** reviewing the live, real-data-backed AAPL company page for frontend polish, a single institutional holder's numbers looked wrong on sight — "PRICE T ROWE ASSOCIATES INC /MD/" showed 179.34M shares but only $45.51M of value, where every other large holder showed a plausible $30-250B.

## What was found

`ownership/institutional.py`'s own module docstring asserted, with citation, that Form 13F's `VALUE` field is unambiguously actual dollars for any bulk window postdating SEC's 2023-01-03 rule change (confirmed against the bulk zip's own bundled `FORM13F_readme.htm`, not just the separately-hosted spec PDF that still says "(x$1000)" — see the earlier `form-13f-cusip-crosswalk.md` finding this pass reopens). That's true of what SEC's *systems* accept. It is not true of what every *filer* actually submits.

Pulled T. Rowe Price's real, live 13F filing (accession `0000080255-26-000381`, `infotable.xml`) directly from EDGAR to rule out a Scrooner parsing bug before assuming a data-quality issue:

```xml
<infoTable>
  <nameOfIssuer>APPLE INC</nameOfIssuer>
  <cusip>037833100</cusip>
  <value>45514867</value>
  <shrsOrPrnAmt><sshPrnamt>179340662</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt>
  ...
```

`45514867` is exactly what's stored in `core.institutional_ownership.value_usd` — the pipeline read the filer's own number correctly. T. Rowe Price's own 13F-generation software still reports `VALUE` in thousands (pre-2023 convention), three years after the rule requiring actual dollars. SEC's own filing-acceptance system apparently does not reject or normalize this.

## How big

Checked with a peer-relative query rather than assuming T. Rowe Price is the only offender: for every `(company_id, source_zip)` group with ≥5 filers, compute the median implied price-per-share (`value_usd / shares`) across all filers holding that security in that window, then find rows whose own implied price is between 1/2000 and 1/500 of that median — a tight band that only matches a clean, deliberate ~1000x error, not ordinary noise.

- **223,979 of 4,631,711** rows with valid shares/value (~4.8%) fall in that band.
- **423 distinct filers**, **3,678 distinct companies** affected.
- Other affected filers include real, well-known managers, not obscure ones: Bessemer Group, Teachers Retirement System of the State of Kentucky, KBC Group NV, State of Alaska Department of Revenue, Thrivent Financial for Lutherans, BNP Paribas Asset Management, Public Employees Retirement Association of Colorado, New York State Teachers Retirement System, Acadian Asset Management, Van Eck Associates, and more.
- A separate, much smaller (3,756 rows) population shows the *opposite* anomaly (implied price 100x+ **above** peer median) — checked and NOT the same bug: every one of these has a trivial share count (1-11 shares), consistent with individual filer typos/rounding artifacts on stub positions, not a systematic scale convention. No reliable correction exists without guessing, so these were deliberately left untouched.

## What was fixed

- Migration `0043_institutional_ownership_value_scale_flag.sql`: adds `core.institutional_ownership.value_scale_corrected boolean not null default false` — same "flag, don't hide" discipline as `match_method`/`is_amendment` on the same table.
- `ownership/institutional.py`'s new `correct_value_scale_anomalies()`: one set-based SQL `UPDATE` (not a per-row loop) multiplying `value_usd` by 1000 for rows matching the peer-relative band, guarded by `not value_scale_corrected` so a rerun can't double-correct. Verified idempotent live: two passes were needed to reach a fixed point (a handful of companies had *more than one* bad filer, which skewed that company's own first-pass median enough to mask one of the two until the first pass's correction shifted the median back toward reality); a third run corrected zero rows.
- Wired into `update_institutional_ownership()` to run automatically after every fetch, not just once by hand — `_process_window()` deletes-then-reinserts every matched company's rows on every run, so `value_scale_corrected` does **not** survive a rerun on its own; skipping this step would silently re-break every previously-fixed row the next time the daily/quarterly fetch runs.
- New standalone CLI command, `scrooner-ownership correct-institutional-value-scale`, to apply the fix to already-stored data immediately without re-downloading and re-matching the ~400MB bulk zips.
- Ran live 2026-09-06: 223,979 rows corrected in one pass, converged to 0 after a second pass, confirmed AAPL's T. Rowe Price rows now show the same ~$253.79/$271.86 implied price-per-share as every other holder in the same window.

## What this does NOT affect

`core.institutional_ownership_summary.total_institutional_pct` is computed purely from `shares / shares_outstanding` (checked directly in `institutional_summary.py` before assuming otherwise) — it never touches `value_usd`. The Overview strip's institutional-ownership percentage was correct the whole time; only the $ Value column (both the raw per-holder table every company page reads directly, and the golden-10's cached Top 10 holders JSON) was wrong. Recomputed `compute-institutional-ownership-summary` for the golden-10 anyway, since their JSON snapshot embeds the pre-correction dollar values.

## Generalizable lesson

**A documented, evidence-based claim about "what a data format now guarantees" (here: SEC's bundled readme confirming the 2023 rule) is a claim about the *platform's* contract, not a guarantee every individual submitter actually complies with it.** The original 2026-08-17 finding (`form-13f-cusip-crosswalk.md`) was itself a correction of exactly this kind of mistake — trusting a stale spec PDF over the bulk zip's own bundled readme — and was right as far as it went. This finding is one level further: even the *authoritative* source's own stated rule can be violated by a filer's own submission with no rejection or flag from SEC's system. Any field whose correctness depends on every independent third-party submitter following a rule (not just on the platform enforcing a schema) is worth a peer-relative sanity check, not just a citation to the rule.

Also worth generalizing: this bug sat undetected through the entire Ownership build (doc 19), full-population scale-out (2026-08-29 to 2026-08-31), and every subsequent coverage pass — because none of those checked *individual displayed values* against real-world plausibility, only row counts, coverage percentages, and reconciliation totals. It was caught by a human glancing at one rendered number on a real page and thinking "that looks wrong" — a reminder that aggregate correctness checks (the dominant verification method throughout this project) don't substitute for occasionally just looking at what a real page shows a real user.
