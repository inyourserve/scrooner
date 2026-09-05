# 2026-09-03 — Generalizing the shares-outstanding cover-page parser: from 23% to ~64-80% real success

## Starting point

`company_master/shares_outstanding_fallback.py` (built 2026-08-17 for Block and Reddit specifically) had only ever run for 2 companies. A 30-company pilot at full-population scale (doc 41/42) found only 23% (7/30) real extraction success — the original regex handled exactly the 2 phrasings it was validated against and nothing else.

## Method: read real failures, don't guess at patterns

Fetched and read (via `clean_visible_text`, borrowed from `business_text.py` rather than the module's own naive tag-stripping — this alone fixed several companies whose cover pages were unreadable garbage due to un-stripped inline-XBRL `<ix:header>` blocks) the actual cover-page text of ~30 real companies missing `shares_outstanding`, diverse by SIC code, not cherry-picked. Found at least 9 distinct real phrasings beyond the original 2, each added as its own pattern, each verified against the literal real text that surfaced it via a new unit test (16 tests total, `tests/unit/test_shares_outstanding_fallback.py`):

1. Per-class, "N shares of Class/Series X common stock" (original, broadened to accept "Series" and multi-char suffixes like "Class B-1")
2. Class-prefix, "N Class X ordinary shares" (no "shares of" wording)
3. Two-class "respectively" (original, broadened so either side can be a bare "Common Stock" with no class letter — a real company has only one lettered class)
4. Separate sentences per class ("The number of shares of Class X outstanding ... was N", repeated)
5. Table format with par-value clause ("Class X Common Stock, par value $X per share, N")
6. Table format without par-value clause ("Class X common stock, N shares")
7. A fourth table variant, "Class X Common Stock, $par value, N Shares Outstanding as of DATE"
8. Units of beneficial interest (royalty trusts — "N units of beneficial interest ... outstanding", both orderings)
9. Single-class baseline ("there were N shares outstanding") — the single most common real case, deliberately tried LAST and only when the page never mentions "Class"/"Series" at all

## Real bugs found and fixed while building this, not before shipping

Every one of these was caught by writing a test against real text and watching it fail, not by inspection:

- **A `[^0-9]{0,N}?` gap can't skip a price clause containing digits** ("$.01 per share" has "01" in it) — a lazy non-digit gap stops at the price's own digits instead of the real target number. Fixed twice (two separate table patterns hit this) by explicitly consuming the `$X.XX`-shaped clause rather than trying to skip past it generically.
- **A looser "table" pattern coincidentally cross-matched ordinary per-class prose lists** — "Class A common stock, N shares" (real table shape) also matches inside "...shares OF Class A common stock, N shares of Class B..." (ordinary prose), landing on the *next* class's number. Real tables never have "of" immediately before the class label; prose lists always do — a negative lookbehind `(?<!of\s)` is what actually distinguishes the two, not the surface pattern shape.
- **A real, live false positive on Beasley Broadcast Group**: a filing date's own year ("2026") sat immediately before the next class's label in a flattened table, and the looser class-prefix pattern captured it as a share count (`"2026"` shares). Fixed two ways — a dedicated, higher-priority pattern for that exact table shape, AND a defense-in-depth guard (`_looks_like_a_bare_year`) rejecting any lone single-match result that falls in a plausible calendar-year range, since no real company's total share count is a bare 4-digit number in that range.
- **Priority ORDER matters as much as the patterns themselves** — the table-format patterns had to move ahead of the looser per-class/class-prefix patterns specifically because flattened tables create coincidental adjacencies (a trailing number or date sitting right next to the *next* row's class label) that a looser, earlier-tried pattern can misinterpret before a more specific, correct pattern gets a chance.

## Also checked: does `edgartools` (doc 12) have a structured shortcut around this?

No — read its `EntityFacts.shares_outstanding` implementation directly: it tries exactly two single-tag lookups (`dei:EntityCommonStockSharesOutstanding`, then `us-gaap:CommonStockSharesOutstanding`), the same fundamental limitation this project already has, since both ultimately read the same aggregated Company Facts API that cannot represent per-class dimensional XBRL facts. Confirms cover-page text (or, longer-term, the `R*.htm` rendered-table technique from `segments/segment_revenue.py`, doc 42's Parser 3) is a genuinely necessary independent source, not a gap only this project has.

## Result

Original 30-company pilot: 23% (7/30) → 50% (15/30) after generalization. Fresh, unbiased 25-company random sample: 80% (20/25). Combined: 35/55 considered (63.6%), or 35/50 excluding genuine no-10K cases (70%). Full 504-company population run launched the same day this doc was written — see `doc/planning/41_Scrooner_Coverage_Improvement_Plan.md`/`42_...md` for the completed result and score impact.

## Lesson

**A regex-based extractor validated against 2 real examples is not "done" — it's a first hypothesis.** The generalization process here (read real failures → categorize the real phrasing → write a test against the literal real text → make it pass → verify the fix doesn't break earlier cases → re-pilot on a fresh, unbiased sample before trusting the full population) is the same loop doc 42 formalized for tag-mapping work, now proven for text-parsing work too. The false positives found along the way (the `$.01` digit trap, the table/prose cross-match, the bare-year misread) all shared one property: each individually looked like a working, sensible pattern until tested against real, messy production text — reinforcing that "the regex compiles and matches my one example" is a much weaker bar than "it survives a real, diverse sample with each result spot-checked for plausibility."
