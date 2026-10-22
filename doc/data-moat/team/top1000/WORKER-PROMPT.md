# Shard worker brief (read fully, then do one shard)

You check ONE shard of 10 companies from `shards.csv` in this folder and write `results/S###.md`. You FIND problems; engineering and the data team FIX them later through rule families. Read-only everywhere except your own results file and your scratch folder.

## Hard rules
- No database writes, migrations, reprocess, pipeline code edits, commits, or edits to `status.md` / `shards.csv` / `PLAYBOOK.md` / `fix-register.md` (the lead merges). Your only repo write is `results/S###.md`.
- Database: Supabase MCP `execute_sql` only (load it with ToolSearch `select:mcp__claude_ai_Supabase__execute_sql`), project_id `yaqvssrpkieutdklmdjr`, one query at a time, start each with `set statement_timeout='50s';`. Scope every query to your 10 company_ids and to recent dates. Joins over `core.fact` without a company filter time out. The pooler is shared by many sessions; no loops of hundreds of queries.
- SEC: User-Agent `Scrooner research inyourserve@gmail.com`, at most 2 requests per second (the tools sleep 0.6 s), only sec.gov / data.sec.gov. One fetch process at a time. Never print secrets.
- Keep scratch files in your own folder: `/private/tmp/claude-501/scratch-S###/` (create it). Never share a folder with another worker.
- Label every finding **FILING-CHECKED** (you opened the filing page and read the figure) or **DATA-INFERRED** (our tables only). Never call a blank `not_reported` without opening the statement.

## Read first (skim, 10 minutes max)
`README.md` and `PLAYBOOK.md` in this folder (problem types and fix rules), `results/S023.md` and `results/S009.md` (the format and depth expected), `status.md` (families already known), `fix-register.md`.

## Tools (in `tools/`, run from that directory, plain `python3`, not `-I`)
- `python3 headline.py <cache_dir> <cik_no_leading_zeros> <accession_with_dashes>` prints the key income statement, balance sheet, cash flow and cover lines of a filing from its R-pages. Use `<cache_dir>` = your scratch folder.
- `tools/sec_rpages.py` has `get(url)` (cached curl, rate limited) and `rows(html)` to print any R-page: `import sys; sys.argv=['x',CACHE]; import sec_rpages as f; f.rows(f.get(base+'R4.htm'))`. R-page numbers vary per filing; if a page is empty try neighbours. Python urllib fails on certificates here; the tool uses curl. `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` (curl it to a file) lets you check SEC's own `fy`/`fp` labels and whether a recent accession is present.
- zsh gotcha: loop variables need `${=var}` to word-split; no `timeout` command; do not `sleep` in Bash.

## Schema cheat sheet (verified 2026-10-21)
- `analytics.company_data_point_coverage(company_id, data_point_name, has_value, gap_reason, checked_at)`: 163 cells per company; `gap_reason` null on a blank means unexplained. `has_value` counts only if the LATEST period has a value.
- `analytics.canonical_concept(id, name)`; `analytics.canonical_fact(company_id, canonical_concept_id, period_id, value, source_fact_ids)`. Concept names: revenue, operating_income, operating_income_resolved, net_income, diluted_eps, total_assets, stockholders_equity, cfo, capex, shares_outstanding, ...
- `core.period(id, fiscal_year, fiscal_period, start_date, end_date)`; `core.filing(id, company_id, accession_number, form, filing_date, period_of_report)`; `core.fact(company_id, concept_id, period_id, filing_id, value, is_authoritative)`; `core.concept(id, taxonomy, tag)`.
- `analytics.metric_definition(id, metric_name)`; `analytics.metric_value(company_id, metric_definition_id, period_label, period_end, value, is_null_reason)` (metric_name `market_cap`, `trailing_pe`, ...).
- `analytics.company_concept_lineage(company_id, canonical_concept_id, has_value, latest_period_end, latest_value, source_tags, mapped_tags_filed, candidate_tags_filed, gap_reason)`; "nothing relevant filed" there only means none of OUR tags were filed.
- A filing with 0 rows in `core.fact` is the "0 facts" family (PLAYBOOK B1).

## Work order (every company)
1. **Blanks.** `select data_point_name, gap_reason from company_data_point_coverage where not has_value and company_id in (...)`. Give every blank one cause: mapping_gap (name the tag and accession), derivation_gap, period_gap, not_reported (statement opened, cite it), not_applicable (sector, say why), upstream_conflict, unknown. Group by pattern rather than listing 40 near-identical cells, but name every cell somewhere.
2. **Wrong values.** For the latest 10-Q and the latest 10-K, compare stored revenue, operating income, net income, diluted EPS, total assets, equity, CFO, capex, shares outstanding, market cap with the filing. Use `headline.py`. Also compare the latest stored period with the company's newest filing (stale or missing quarter, 0-facts filing, wrong fiscal_year labels versus SEC companyfacts `fy`). Look at how `operating_income_resolved` and `revenue` were derived in `company_concept_lineage` (`source_tags`): a derivation such as revenue minus `OperatingExpenses` can include income tax or exclude derivative revenue.
3. **Plausibility.** Impossible market caps, negative P/E shown as a number, margins over 100%, ratios that do not apply (banks, insurers, REITs, utilities), wrong blank reasons (for example a "financial institution" reason on a non-financial company).
4. Check each blank reason for truthfulness: a company that pays no dividend should not show an unexplained dividend blank; a utility is not a financial institution.

## Output: `results/S###.md`
Follow `results/S023.md`: title; worker/date/sources; evidence level and what was NOT done; headline check summary; a "Wrong values and plausibility" table (company, cell, stored, filed, cause, level); blanks by cause per company; "Rule families" section grouping findings by cause with population counts where a cheap query gives one (tag the family name from PLAYBOOK/status.md or NEW); "What I did not check". Be honest about partial coverage. If sec.gov is blocked, say so and mark everything DATA-INFERRED.

## Final reply (to the lead, under 200 words)
Shard id, number of FILING-CHECKED wrong values, the top 3 NEW rule families (one line each), anything that blocked you. Do not paste the results file.

## Additions (2026-10-21, from Dhairya; apply to shards started after this note)
- **Per-company verdict table** near the top of your results file: one row per company with `wrong values shown (count)`, `unexplained blanks (count)`, and a verdict `CLEAN` (no wrong value, no unexplained blank) or `NOT CLEAN`. This feeds the list of closest-to-certifiable large companies.
- **Mechanism line** for every finding: one line guessing the mechanism (not a fix), for example "revenue resolved by tag-name priority, not by statement structure".
- **History window (cheap version):** per company, the earliest annual period we hold (`min(end_date)` of FY revenue in `canonical_fact`) versus the earliest 10-K the company has in `core.filing`, and one spot check that FY2018 or FY2021 revenue matches the filing's income statement comparatives (use any later 10-K that shows that year). Missing quarters inside the last 8 quarters: list them with cause. Skip if it would take more than 5 queries.
- Findings only. No fixes proposed.
- **Optional shared memory (from Dhairya, beta, never a blocker):** before researching a rule family you may run `python3 mind/mind.py search "<topic>"` from the repo root, then `get <id>`, and afterwards `feedback <id> helped|wrong`. Entries are hints with evidence labels; do not rely on one without checking its source, and do not wait on it.
