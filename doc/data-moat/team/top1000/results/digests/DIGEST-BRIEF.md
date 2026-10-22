# Digest brief (read-only synthesis of shard result files; findings only, no fixes)

You are given a block of `results/S###.md` files in /Users/vikash/scrooner/doc/data-moat/team/top1000/results/. Read each fully. Write ONE digest file `results/digests/D<block>.md`. No database, no SEC fetching, no code changes. Use only what the result files say; quote their evidence labels (FILING-CHECKED vs DATA-INFERRED). Do not invent numbers or accessions; copy accession numbers exactly as written in the file.

## Fixed theme list (use these ids; add T13+ for anything that fits none)
- T1 revenue resolves to a partial/sub-line tag (ASC 606 subset, interest-income-only for banks, one segment line) instead of the statement total
- T2 operating income derived (revenue minus OperatingExpenses etc.) or taken from a non-face line / segment note, where the filer presents none or a different figure
- T3 latest 10-Q/10-K has 0 facts in core.fact, or the filing is absent from core.filing (page a quarter or more stale)
- T4 shares_outstanding blank/stale/wrong (multi-class or dimensioned cover counts not summed, issued vs outstanding), market cap on the wrong share basis, and the per-share cascade (book value per share pairing etc.)
- T5 stale series counted as filled (latest period years old but coverage says has_value)
- T6 true zero (no debt, no buyback, no dividend) shown as blank, and total_debt unmapped / wrong / stale
- T7 wrong or missing blank reasons (financial-institution, REIT, pre-revenue-biotech applied to the wrong sector; no reason for non-dividend payers; the 4 universal unexplained cells)
- T8 negative or meaningless ratios shown as numbers (P/E, P/B, ROE, ROIC on negative base)
- T9 fiscal_year / period label wrong (52/53-week years, January year-ends, 16-week Q1, NULL fiscal_period)
- T10 recast / restated / spun-off / predecessor comparatives leave no authoritative fact or mixed bases; missing quarters inside the last 8
- T11 net income basis inconsistent (ProfitLoss / consolidated vs attributable to parent), equity incl. NCI
- T12 capex (and D&A, interest expense, receivables) tags unmapped, stale or split across lines, causing FCF/EBITDA cascades
- T13+ anything else (name it)

## Output format (markdown)
1. `## Block` line: which shard files you read, and any file that was missing/partial.
2. For EACH theme T1..T12 (and T13+ if any): 
   - Companies affected: count and list as `TICKER(S###)`, split FILING-CHECKED vs DATA-INFERRED.
   - Cells: how many are wrong values shown vs blank (coverage) vs measurement problem, as far as the files say (say "not stated" if not).
   - 2-3 FILING-CHECKED exemplars: ticker, what is stored vs filed, accession if the file gives one.
   - Mechanism guess (one line, not a fix), preferably the worker's own wording.
3. `## Per-company verdicts`: one line per company: `TICKER | shard | rank-or-mcap if in file | wrong values | unexplained blanks | CLEAN or NOT CLEAN`. Use the file's own verdict table when it has one; otherwise derive and mark DERIVED.
4. `## History-window items`: any first-period-held versus filing-history, FY2015/2018/2021 spot-check, or missing-quarter findings, per company.
5. `## Population counts quoted`: every population count a worker quoted (e.g. "683 companies carry implausible..."), with the shard it came from and whether it was a query or an estimate.
