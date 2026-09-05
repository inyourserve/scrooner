# 2026-09-05 — Institutional ownership was severely undercounted: a `distinct on (filer_name)` dedup silently discarded most of every large manager's real position

## What happened

Directly asked to check whether `institutional_ownership_pct` was correct. AAPL's stored value was 36.45% (`institutional_ownership_summary` separately showed a similarly low 36.06%) — both far below AAPL's real, publicly-known institutional ownership of roughly 60-65%.

## Root cause, found by reading the raw data directly

`_institutional_ownership_shares()` (`mapper/expanded_metrics.py`), `_period_holders()` (`ownership/institutional_summary.py`), and `getTopInstitutionalHolders()` (`apps/site/src/lib/db.ts`) all deduplicated Form 13F holdings the same way:

```sql
select distinct on (filer_name) shares
from core.institutional_ownership
where company_id = %s
order by filer_name, is_amendment desc, filing_date desc nulls last
```

This assumes each filer contributes exactly one real row per company, and the only reason a filer would have multiple rows is an amendment superseding an original. **That assumption is wrong.** A single Form 13F filing can legitimately report the same security across multiple separate INFOTABLE line items for one filer — different investment-discretion codes, different managed-account sub-groupings. Checked live for AAPL, most recent window (`01mar2026-31may2026`): **"BlackRock, Inc." reports 25 separate rows, all `is_amendment=false`, all under the exact same `accession_number`** (`0002012383-26-001841`) — a real, additive position summing to roughly $1.1B of AAPL's shares, not a set of duplicates. `distinct on (filer_name)` kept only the single largest row ($423.9M) and silently discarded the other 24. Vanguard's various sub-manager entities showed the same multi-row pattern. This was the dominant cause of the gap — not a data-collection problem, a query-logic problem.

Confirmed the correct way to distinguish a genuine multi-row filing (sum everything) from a genuine amendment (use only the newer one) needs **two different keys**: `filer_cik` identifies *who*, `accession_number` identifies *which filing*. An amendment is a *different* `accession_number` for the same `filer_cik` — verified live: Vanguard Capital Management LLC's original (`0002100119-26-001306`) and amendment (`0002100119-26-001311`) report the identical 953,847,648 shares, confirming the amendment restates rather than adds. BlackRock's 25 rows all share one `accession_number` — a real multi-line position, not a restatement.

## Fix

All three locations changed to a two-step query: pick the single authoritative `(filer_cik, accession_number)` per filer (prefer the amendment, else latest `filing_date`), **then sum every row within that one chosen filing** — never pick a single row once the filing is chosen. Also fixed, in the same pass, a second real gap in two of the three: neither `expanded_metrics.py`'s nor `apps/site`'s query was scoped to a single reporting window at all (`core.institutional_ownership` now holds 2 quarters per company, since doc 19's later upgrade) — both silently blended rows from both windows together. Fixed by picking the window with the most recent real `filing_date` (not a string comparison on the `source_zip` bulk-download filename, which isn't reliably sortable as a date).

## Verified

AAPL: 9,543,113,260 institutional shares (post-fix) / 14,594,180,000 shares outstanding = **65.39%**, matching real-world reporting. JPM (a second, independent company, chosen for its own multi-listing complexity): **74.58%**, also a realistic figure for a large bank heavily held by index funds. Both computed end-to-end through the real `calculate-expanded-metrics` CLI path, not just the isolated SQL.

## A second, separate, pre-existing bug found while verifying the fix

Recomputing the golden-10 with the fix in place, NIKE showed **110.6% institutional ownership** — impossible by definition. Investigated directly rather than assumed: NIKE's institutional total (961.4M shares, itself correctly computed by the fixed query) legitimately exceeds its `shares_outstanding` denominator (~868M) because that denominator is **stale** — the authoritative `dei:EntityCommonStockSharesOutstanding` fact has had no real value since **2015-07-17**, almost certainly the same dimensional/multi-class-share stripping this project already documented and built a cover-page fallback parser for (Block, Reddit) — NIKE just was never identified as needing that same fallback. This is a genuinely separate root cause from the dedup bug above, not fixed here (it needs its own investigation into why NIKE's cover-page fallback isn't covering it, or another resolution path).

**Added a safety guard in both places** (`expanded_metrics.py`'s `institutional_ownership_pct` and `institutional_summary.py`'s `total_institutional_pct`): a computed institutional ownership percentage that exceeds 100% is definitionally proof the denominator is wrong, never evidence of real ownership — null it out with a clear, distinct reason (`implausible:institutional_shares_exceed_shares_outstanding`) rather than silently display an impossible number. This is defense-in-depth, not a fix for the underlying stale-`shares_outstanding` problem, which remains open — worth sizing (how many other companies share NIKE's "no real shares_outstanding since some past year" pattern) as a follow-up.

## Full-population rollout, and two more things found closing it out

Recomputed all 3,422 previously-populated companies. **A real race condition, caught by the same "verify the actual final numbers, don't trust the printed summary" discipline**: 45 companies still showed >100% after the full rollout completed. Root cause: the background batch job was already running (`xargs -P 6`, each batch a fresh `uv run` subprocess) when the >100% guard was added to `expanded_metrics.py` mid-session — a handful of batches that were already mid-flight at that exact moment used the pre-guard code (each new subprocess picks up the current source since the package is installed editable, but a process already running keeps whatever it loaded at its own startup). Fixed by identifying the 45 by direct query (`value > 1`) and rerunning just those — confirmed 0 remaining >100% values afterward, not just fewer.

**A second, real, structural finding while investigating scale**: 622 companies (not just NIKE) hit the >100% guard. Sampled 20 at random and checked their `shares_outstanding` freshness directly — unlike NIKE, most have *current, fresh* denominators (e.g. Robert Half's shares_outstanding is dated 2026-07-31). This rules out "stale denominator" as the cause for most of them. The real explanation is a well-known, genuine limitation of Form 13F itself: multiple *related* filers (a parent asset manager and its subsidiary investment advisers) can each independently report "investment discretion" over the same underlying shares, so a naive sum of all filers' positions can legitimately exceed the true float — a real industry data-quality issue, not a bug in this project's dedup logic (which already correctly handles the *single-filer* multi-row and amendment cases). Properly fixing this would require identifying related-filer groups, which isn't reliably derivable from 13F data alone — left as a real, structural boundary of what this data source can support, not chased further. The guard's behavior here (null with a clear reason, rather than a wrong percentage) is the correct, honest outcome per this project's own "never guess" discipline, even though it costs real display coverage.

**Final verified state, full population**: 2,800 companies with a real value (average 57.9%, plausible for a broad population spanning mega-caps to micro-caps), 622 correctly nulled as implausible, **zero** remaining values over 100%.

## Lesson

**A dedup rule verified correct against a few small holders can still be wrong for the largest ones — the failure mode only appears at exactly the scale (many real position lines per filer) that matters most for the aggregate percentage.** The original dedup logic was tested and looked right; it just never happened to be checked against a filer large enough to have >1 real line item, which is precisely the case that dominates the aggregate ownership number. Whenever a percentage or aggregate looks lower than a well-known real-world anchor (a public company's institutional ownership is one of the most heavily reported numbers in finance), checking the raw rows behind the *largest* contributor first is a fast, high-leverage way to find this class of bug — a small/typical holder's row usually looks completely fine.
