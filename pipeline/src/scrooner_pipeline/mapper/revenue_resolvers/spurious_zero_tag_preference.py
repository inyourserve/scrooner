"""Revenue resolver: resolve()'s authoritative-$0 bug (root cause 1,
first found 2026-09-07 on Flowserve Corp, confirmed a second and third
time 2026-10-02 on Commerce Bancshares and `income_before_tax`). A
company's priority-1 revenue tag is a real, authoritative-but-spurious
$0 -- Stage 2e's dedupe logic correctly rejecting a trivial cross-filing
rounding disagreement on the tag that SHOULD have won, with no
tolerance-aware fallback to the next-best already-mapped tag.

Fixed via `sanity/tag_investigator.py`'s existing per-company tag-
preference mechanism -- this module is a thin wrapper giving it a
`run()` entry point consistent with every other resolver in this
package, not a reimplementation. Bulk, non-reactive discovery (`run_
internal_tag_preference_sweep`) finds every company in the real-
operating-company population whose zero-revenue periods are majority-
fixable by one of its OWN already-mapped alternate tags (internal
corroboration -- same-company same-tag history agreeing with itself,
NOT a yfinance anchor, since `investigate()`'s 20%-tolerance gate is
the wrong bar for this bug class: a bank's best honest alternate tag
can be ~78% off from yfinance's full revenue figure yet still be
categorically correct). Verified live 2026-10-02: 878 companies
scanned, 31 qualified (Commerce Bancshares 68/68 periods fixed via
InterestAndDividendIncomeOperating, Flowserve 5/5 via SalesRevenueNet,
plus 29 others), `revenue_sanity_resolved` re-merged to 341,376 rows
with zero regressions."""

import psycopg

from scrooner_pipeline.sanity.tag_investigator import (
    resolve_company_tag_preferences,
    run_internal_tag_preference_sweep,
)


def run(conn: psycopg.Connection) -> dict:
    sweep_stats = run_internal_tag_preference_sweep(
        conn, concept_name="revenue", resolved_concept_name="revenue_sanity_resolved"
    )
    merged_rows = resolve_company_tag_preferences(
        conn, "revenue", "revenue_sanity_resolved"
    )
    return {
        "considered": sweep_stats.get("considered", 0),
        "ok": sweep_stats.get("applied", 0),
        "errored": sweep_stats.get("errored", 0),
        "no_candidate": sweep_stats.get("no_candidate", 0),
        "rows_written": merged_rows,
    }
