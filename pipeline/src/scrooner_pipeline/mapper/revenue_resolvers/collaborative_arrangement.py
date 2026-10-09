"""Revenue resolver: biotech/pharma collaboration-arrangement revenue
(root cause 2, 2026-10-02 -- found investigating BioAtla, Inc., whose
real revenue since ~2024 is tagged under `us-gaap:
RevenueFromCollaborativeArrangementExcludingRevenueFromContractWith
Customer`, not in `revenue`'s own concept_mapping at all).

Verified live before shipping: 26 companies / 739 facts population-wide
use this tag; it coexists with an already-mapped, nonzero contract-
revenue tag in 238 real company-periods -- a genuine SECOND revenue
stream for biotech/pharma licensing deals (milestone/collaboration
payments alongside product revenue), not a substitute for it. Kept as
its own canonical concept (`collaborative_arrangement_revenue`, never
added to `revenue`'s own concept_mapping) specifically so it can be
summed rather than risk double-counting via a `first_match` priority
change that would affect every company reporting the primary tag too.

Reuses `concept_fallback.resolve_fallback_for_company()` with
`overlap_tag=None` -- primary (`revenue`) and this tag can never
legitimately double-count the same real-world figure, so every
coexisting period is summed, and a period where `revenue` is missing/
zero is filled from this tag alone (0 + collaborative = the whole,
honest value). Scoped ONLY to companies with >=1
collaborative_arrangement_revenue canonical_fact row -- every other
company's revenue_sanity_resolved row is untouched (not a blanket
delete/reinsert of the whole concept)."""

import psycopg
import structlog

from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.mapper.concept_fallback import (
    _concept_id,
    resolve_fallback_for_company,
)
from scrooner_pipeline.mapper.revenue_resolvers.shared import (
    companies_owned_by_other_revenue_writer,
    revenue_concept_ids,
)

logger = structlog.get_logger()


def run(conn: psycopg.Connection) -> dict:
    revenue_id, resolved_id = revenue_concept_ids(conn)
    collab_id = _concept_id(conn, "collaborative_arrangement_revenue")
    owned = companies_owned_by_other_revenue_writer(conn, revenue_id)

    with conn.cursor() as cur:
        # status = 'active' only (2026-10-02, by direct request) -- a
        # delisted/stale company's revenue_sanity_resolved is never
        # re-served anywhere, so resolving it is pure wasted write/DB
        # size for no reporting benefit. Matches spurious_zero_tag_
        # preference.py's own population scoping discipline (that one
        # via the narrower real_operating_company population; this one
        # via the simpler active-only filter, since this resolver has no
        # dependency on company_data_point_coverage being fresh).
        cur.execute(
            """
            select distinct cf.company_id
            from analytics.canonical_fact cf
            join core.company c on c.id = cf.company_id
            where cf.canonical_concept_id = %s and c.status = 'active'
            """,
            (collab_id,),
        )
        candidate_company_ids = [r[0] for r in cur.fetchall() if r[0] not in owned]

    stats = {
        "considered": len(candidate_company_ids),
        "ok": 0,
        "errored": 0,
        "rows_written": 0,
        "skipped_other_writer": len(owned),
    }
    for company_id in candidate_company_ids:
        try:
            rows = resolve_fallback_for_company(
                conn, company_id, revenue_id, collab_id, resolved_id, overlap_tag=None
            )
            conn.commit()
            stats["ok"] += 1
            stats["rows_written"] += rows
        except Exception:
            logger.warning(
                "revenue_resolvers.collaborative_arrangement_company_failed",
                company_id=company_id,
                exc_info=True,
            )
            stats["errored"] += 1
            conn = safe_rollback(
                conn, stage="collaborative_arrangement_revenue", cik=str(company_id)
            )

    return stats
