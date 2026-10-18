# Top-1000 company-by-company campaign (started 2026-10-18)

Founder direction 2026-10-18: work company by company on the 1,000 largest companies by market cap, in 100 shards of 10, to reach 100% data moat and 100% coverage.

## What "100%" means here (from PLAN.md "Launch target", unchanged)
- **Coverage 100%** = every cell is accounted for: either a correct value traceable to a filing, or a blank with a reason shown to the user ("not reported by this company", "not applicable to banks", "history not available before XBRL", ...). We do not fill a cell the company does not report; that would be a guess and break the second goal.
- **Data moat 100%** = no known wrong value is displayed. A wrong value found in any shard is fixed (or hidden with a reason) before launch.

## Baseline, measured 2026-10-18 from `analytics.company_data_point_coverage` (163 data points per company)
| | Cells | Share |
|---|---|---|
| Value present | 131,804 | 80.86% |
| Blank with a gap reason | 17,058 | 10.47% |
| Blank, no reason (unexplained) | 14,138 | 8.67% |
| Total | 163,000 | |

"Value present" is not yet "verified correct". Shard S001 (NVDA..LLY) is 86.8% filled; S100 is 74.0%.

## The list: `shards.csv`
Rank by the latest `market_cap` metric, `real_operating_company` population only. Columns: shard, rank, company_id, cik, ticker, name, sic, mcap_bn, cells, filled, unexplained_blank.

**The ranking is provisional.** Building it surfaced a wrong-value class straight away: AKTX $1,274B (rank 9), TBLA $999B, RPAY $341B are impossible. Their share counts are wrong (AKTX uses `EntityCommonStockSharesOutstanding` = 155.8B ordinary shares, which are ADS-underlying; TBLA 290.5B and RPAY 83.3B diluted weighted-average shares, likely a scale error). Shard S000 audits the ranking, fixes or flags these, and re-ranks; shards are then reissued. Until then, a shard worker that finds a company whose market cap is impossible records it and moves on.

## Shard work order (every worker, every company)
Read first: `data-team/20-SCROONER-INFRA-MAP.md`, `doc/data-moat/team/PLAN.md`, `data-team/16-DATA-VERIFIER.md`, `data-team/22-FILING-LESSONS-LEDGER.md`.
Read-only on the database. No writes, no migrations, no reprocess, no edits to pipeline code. Database access through the Supabase MCP tool only, one query at a time, each with `set statement_timeout` of at most 55s, chunked to the shard's 10 company ids.

For each of the 10 companies:
1. **Blanks.** List every `has_value = false` cell. For each, assign one cause: `mapping_gap` (the filing has the line under a tag we do not map; name the tag and accession), `derivation_gap` (derivable from authoritative inputs we hold), `period_gap`, `not_reported` (the filing does not present it; cite the statement you opened), `not_applicable` (sector; say why), `upstream_conflict`, `unknown`. Never call a blank `not_reported` without opening the filing.
2. **Wrong values.** Check the headline values (revenue, operating income, net income, diluted EPS, total assets, total equity, CFO, capex, shares outstanding, market cap) for the latest fiscal year and latest quarter against the company's own 10-K/10-Q (SEC R-pages or filing HTML). Record each mismatch with accession, stored value, filed value and suspected cause.
3. **Plausibility.** Flag impossible metrics (market cap far from price x shares, margins over 100%, sign flips, ratios on banks that do not apply to banks).

Output: one file per shard, `doc/data-moat/team/top1000/results/S###.md`, with a per-company table and a final "rule families" section that groups findings by cause (for example "tag X unmapped, seen at 3 of 10 companies"). Do not commit; the lead commits.

## Who does what (agreed 2026-10-18)
This campaign FINDS (read-only, `results/S###.md`). Dhairya's manager session FIXES, through rule families, ordered in `fix-register.md` by top-1000 reach. Every finding is labelled FILING-CHECKED (filing opened) or DATA-INFERRED. Already-known families (cite, do not re-derive): GE quarterly revenue = GE Capital only; bank metrics that do not apply (fcf_yield, debt_to_equity, net_cash) and 15 banks with a wrong net_interest_income; CVX/AJG have no operating-income subtotal; period-label errors in later filings (CB, SWK, Ford, MET, TT, SPGI); derived Q4 EPS by subtraction; segment-note operating income mapped as consolidated. Read `data-team/21-US-FILINGS-DOMAIN-KNOWLEDGE.md` section 8 before calling anything `not_reported`.

## How findings become fixes
Shards find; rule families fix. Each finding is grouped into a family across shards, then goes through the existing path in PLAN.md: proposal -> Verifier sample against filings -> full-population coexistence check -> committed migration or code change -> reprocess -> re-measure. That way a fix found at one company also fixes every other company with the same cause, and nothing reaches users on the strength of one example.

## Pace
The database pooler has about 15 connections shared by every service (14 in use when this started). Shards run in waves of a few at a time, not 100 at once. Wave 1 is S000 plus S001-S003, to calibrate the work order before the rest run.

## Status
See `status.md`.

## SEC access (founder decision 2026-10-18)
The founder approved declaring their Gmail as the SEC contact: User-Agent `Scrooner research inyourserve@gmail.com`, sent to sec.gov and data.sec.gov only. Each worker is capped at 2 requests/second so the workers together stay under SEC's ~10/s limit.
