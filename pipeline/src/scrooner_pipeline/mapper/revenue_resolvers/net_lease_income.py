"""Revenue resolver: equity/net-lease REIT lease income (root cause 3,
2026-10-02 -- found investigating American Strategic Investment Co.,
an equity/net-lease REIT whose real revenue is tagged under
`us-gaap:OperatingLeaseLeaseIncome`, not in `revenue`'s own
concept_mapping).

A SUBSTITUTE fill, not an ADD -- unlike collaborative_arrangement.py,
this project has no evidence lease income and primary revenue are ever
genuinely separate additive streams for this sector, and the whole
point of the gate below is that the primary is already missing/zero,
so there's nothing to add to.

Verified live before shipping: of 75 companies where OperatingLease
LeaseIncome is real/material and the primary concept is missing/zero
for that period, 23 also report a financial-income tag (mortgage
REITs/banks -- same `_REVENUE_FINANCIAL_INCOME_TAGS` discriminator
`mapper/coverage_matrix.py`'s `_FINANCIAL_INCOME_TAGS` already uses for
the `financial_institution_interest_income_not_revenue` gap reason,
mirrored here rather than coupling two modules' internal namespaces for
one short, stable tuple -- correctly excluded) and 49 are NOT REIT-SIC
at all (manufacturers subleasing office space etc., correctly
excluded). The remaining 12 are real, named equity/net-lease REITs
(Industrial Logistics Properties Trust, American Homes 4 Rent,
American Strategic Investment Co., ONE LIBERTY PROPERTIES, Tanger Inc.,
NETSTREIT Corp, Camden Property Trust, Kite Realty Group Trust, etc.)."""

import psycopg
import structlog

from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.mapper.concept_fallback import _concept_id, _load_facts
from scrooner_pipeline.mapper.revenue_resolvers.shared import (
    companies_owned_by_other_revenue_writer,
    revenue_concept_ids,
)

logger = structlog.get_logger()

_REVENUE_FINANCIAL_INCOME_TAGS = (
    "InterestIncomeOperating",
    "InterestAndDividendIncomeOperating",
    "NoninterestIncome",
    "GrossInvestmentIncomeOperating",
    "InterestAndFeeIncomeLoansAndLeases",
)


def run(conn: psycopg.Connection) -> dict:
    revenue_id, resolved_id = revenue_concept_ids(conn)
    net_lease_id = _concept_id(conn, "net_lease_revenue")
    owned = companies_owned_by_other_revenue_writer(conn, revenue_id)

    with conn.cursor() as cur:
        # status = 'active' only (2026-10-02, by direct request) -- same
        # reasoning as collaborative_arrangement.py's own scoping.
        cur.execute(
            """
            select distinct c.id
            from core.company c
            join analytics.canonical_fact cf on cf.company_id = c.id and cf.canonical_concept_id = %(net_lease_id)s
            where c.status = 'active'
              and c.sic_description = 'Real Estate Investment Trusts'
              and not exists (
                  select 1 from core.fact f
                  join core.concept co on co.id = f.concept_id
                  where f.company_id = c.id and co.tag = any(%(fin_tags)s)
              )
            """,
            {
                "net_lease_id": net_lease_id,
                "fin_tags": list(_REVENUE_FINANCIAL_INCOME_TAGS),
            },
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
            net_lease_facts = _load_facts(conn, company_id, net_lease_id)
            existing = {
                period_id: value
                for period_id, (value, _sources) in _load_facts(
                    conn, company_id, resolved_id
                ).items()
            }

            rows = 0
            with conn.cursor() as cur:
                for period_id, (value, source_fact_ids) in net_lease_facts.items():
                    current = existing.get(period_id)
                    if current is not None and current != 0:
                        continue  # primary already has a real value -- never override
                    cur.execute(
                        """
                        insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                        values (%(company_id)s, %(resolved_id)s, %(period_id)s, %(value)s, %(source_fact_ids)s)
                        on conflict (company_id, canonical_concept_id, period_id) do update
                            set value = excluded.value, source_fact_ids = excluded.source_fact_ids
                        """,
                        {
                            "company_id": company_id,
                            "resolved_id": resolved_id,
                            "period_id": period_id,
                            "value": value,
                            "source_fact_ids": source_fact_ids,
                        },
                    )
                    rows += 1
            conn.commit()
            stats["ok"] += 1
            stats["rows_written"] += rows
        except Exception:
            logger.warning(
                "revenue_resolvers.net_lease_income_company_failed",
                company_id=company_id,
                exc_info=True,
            )
            stats["errored"] += 1
            conn = safe_rollback(conn, stage="net_lease_income", cik=str(company_id))

    return stats
