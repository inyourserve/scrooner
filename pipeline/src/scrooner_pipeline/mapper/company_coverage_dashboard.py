"""Company-wise coverage dashboard (2026-10-03, by direct request:
"make a dashboard for company wise coverage... financial rows [should
plan] based on company types... put notes... otherwise it will not
[be] transparent for users").

Every coverage view built so far in this project (coverage_snapshot.py,
incidents/dashboard.py) is METRIC-wise: "what % of companies have
revenue." This flips the axis to COMPANY-wise: "for Visa, what does it
have and why is anything missing" -- the exact question the Visa
investigation (2026-10-03, same day) had to answer by hand, company by
company, via ad hoc SQL. This module makes that a standing, reusable
query instead.

Three states per (company, data_point), not two -- a bare has_value
boolean collapses "genuinely doesn't apply to this company" (Visa has
no Cost of Revenue because it's a payment network, not a goods seller)
and "a real, investigable gap" (Visa's missing EPS, confirmed live
against SEC's own data to be a real dimensional-stripping gap) into the
same blank cell, which is exactly what made the Visa report look like a
bug instead of two very different things:

  PRESENT         -- has_value = true, show the real value.
  NOT_APPLICABLE  -- has_value = false, AND EITHER the data point's own
                     applicable_population excludes this company (e.g.
                     dividend_yield's applicable_population is
                     'dividend_payer', and this company has never been
                     classified into that population), OR gap_reason is
                     one of the structural "this company's TYPE doesn't
                     have this line" reasons already verified live by
                     classify_concept_gaps() (pre_revenue_spac,
                     bank_interest_income_not_revenue,
                     pre_revenue_biotech_pharma, passthrough_trust,
                     bdc_reports_investment_income_not_revenue, etc.).
  GAP             -- has_value = false and neither of the above explains
                     it -- a real, un-investigated or investigated-but-
                     unresolved absence. This is the only bucket that
                     should ever read as "something might be wrong."

Every row gets a human-readable note (_friendly_note()) -- never a bare
gap_reason code shown to a user unexplained, per doc 01's traceability
principle generalized to "traceable" meaning "a person can understand
why," not just "a machine can look up a code."""

from collections import defaultdict

import psycopg
import structlog

logger = structlog.get_logger()

# Structural reasons classify_concept_gaps() already verified live
# (pipeline/CLAUDE.md, 2026-09-11/12 entries) as "this company's real
# business type genuinely has no such line" -- NOT_APPLICABLE, not a gap,
# regardless of applicable_population (these predate that column and
# cover concept-level, not just metric-level, absences).
_STRUCTURAL_GAP_REASONS: dict[str, str] = {
    "pre_revenue_spac": "SPAC/blank-check company -- not yet operating, no revenue by construction.",
    "pre_revenue_biotech_pharma": "Pre-revenue biotech/pharma -- genuinely has no revenue yet.",
    "pre_revenue_mining_exploration": "Pre-production exploration miner -- genuinely has no revenue yet.",
    "passthrough_trust": "Royalty/pass-through trust -- not an operating business in the usual sense.",
    "passthrough_commodity_trust": "Commodity/crypto ETF trust (e.g. a gold or bitcoin trust) -- pays sponsor fees, earns no revenue.",
    "bank_interest_income_not_revenue": "Bank/savings institution -- reports net interest income, not a single \"Revenue\" line.",
    "reit_net_interest_income_not_revenue": "Mortgage REIT -- earns net interest income, not a single \"Revenue\" line.",
    "financial_institution_interest_income_not_revenue": "Financial institution -- reports interest/investment income, not a single \"Revenue\" line.",
    "bdc_reports_investment_income_not_revenue": "Business Development Company -- reports total investment income, not a \"Revenue\" line.",
    "foreign_private_issuer_sparse_xbrl": "Foreign private issuer -- SEC's own data for this filer type is sparse by design (20-F/40-F, not a 10-K).",
    "coregistrant_subsidiary_sparse_sec_xbrl": "Wholly-owned subsidiary filer -- its real financials are consolidated into its parent's filing, not its own.",
}


def _friendly_note(gap_reason: str | None, not_applicable: bool) -> str:
    if gap_reason is None:
        return "No reason recorded yet -- a genuine, uninvestigated gap." if not not_applicable else "Not applicable to this company."
    if gap_reason in _STRUCTURAL_GAP_REASONS:
        return _STRUCTURAL_GAP_REASONS[gap_reason]
    if gap_reason.startswith("missing:"):
        dep = gap_reason.split(":", 1)[1]
        return f"Missing a required input: {dep.replace('_', ' ')}."
    if gap_reason.startswith("incomplete:"):
        role = gap_reason.split(":", 1)[1]
        return f"One or more required inputs incomplete for this calculation ({role.replace('_', ' ')})."
    if gap_reason == "no_dividend_history":
        return "This company has no record of paying a dividend."
    if gap_reason == "non_positive_growth_not_meaningful":
        return "Growth rate not meaningful (negative or zero base)."
    if gap_reason == "negative_ratio_undefined_cagr":
        return "CAGR undefined (a negative starting value makes compounding meaningless)."
    if gap_reason.startswith("immaterial_"):
        return "Base value too small/near-zero for this ratio to be meaningful."
    # Fallback: show the raw code, de-slugged, rather than hide it.
    return gap_reason.replace("_", " ").replace(":", ": ")


def summarize_company(conn: psycopg.Connection, company_id: int) -> dict:
    """Full per-company breakdown: every tracked data point, its status,
    value if present, and a human-readable note if not."""
    with conn.cursor() as cur:
        cur.execute(
            "select cik, company_name, display_name, sic_description, status from core.company where id = %s",
            (company_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"no company with id {company_id}")
        cik, company_name, display_name, sic_description, status = row

        cur.execute(
            "select population_name from analytics.company_population where company_id = %s",
            (company_id,),
        )
        populations = {r[0] for r in cur.fetchall()}

        cur.execute(
            """
            select cov.data_point_name, dpr.data_point_type, dpr.applicable_population,
                   cov.has_value, cov.gap_reason
            from analytics.company_data_point_coverage cov
            join analytics.data_point_registry dpr on dpr.data_point_name = cov.data_point_name
            where cov.company_id = %s
            order by dpr.data_point_type, cov.data_point_name
            """,
            (company_id,),
        )
        rows = cur.fetchall()

    items = []
    counts = defaultdict(int)
    for name, dp_type, applicable_population, has_value, gap_reason in rows:
        if has_value:
            status_label = "present"
        elif applicable_population and applicable_population not in populations:
            status_label = "not_applicable"
        elif gap_reason in _STRUCTURAL_GAP_REASONS:
            status_label = "not_applicable"
        else:
            status_label = "gap"
        counts[status_label] += 1
        items.append(
            {
                "data_point_name": name,
                "data_point_type": dp_type,
                "status": status_label,
                "note": None if status_label == "present" else _friendly_note(gap_reason, status_label == "not_applicable"),
            }
        )

    applicable_total = counts["present"] + counts["gap"]
    coverage_pct = (
        round(100 * counts["present"] / applicable_total, 1) if applicable_total else None
    )

    return {
        "company_id": company_id,
        "cik": cik,
        "company_name": display_name or company_name,
        "sic_description": sic_description,
        "status": status,
        "populations": sorted(populations),
        "items": items,
        "counts": dict(counts),
        "coverage_pct": coverage_pct,  # present / (present + genuine gaps), not_applicable excluded from denominator
    }


def summarize_population(conn: psycopg.Connection) -> list[dict]:
    """One row per active company: counts + coverage_pct, for ranking.
    Pure set-based SQL (not a Python loop per company, per this
    project's own documented N+1 discipline) -- computes the same 3-way
    classification as summarize_company(), aggregated."""
    with conn.cursor() as cur:
        cur.execute(
            """
            with classified as (
                select
                    cov.company_id,
                    case
                        when cov.has_value then 'present'
                        when dpr.applicable_population is not null
                             and not exists (
                                 select 1 from analytics.company_population cp
                                 where cp.company_id = cov.company_id
                                   and cp.population_name = dpr.applicable_population
                             )
                        then 'not_applicable'
                        when cov.gap_reason = any(%(structural)s) then 'not_applicable'
                        else 'gap'
                    end as status
                from analytics.company_data_point_coverage cov
                join analytics.data_point_registry dpr on dpr.data_point_name = cov.data_point_name
            )
            select
                c.id, coalesce(c.display_name, c.company_name) as name, c.cik,
                count(*) filter (where cl.status = 'present') as present,
                count(*) filter (where cl.status = 'gap') as gap,
                count(*) filter (where cl.status = 'not_applicable') as not_applicable
            from classified cl
            join core.company c on c.id = cl.company_id
            where c.status = 'active'
            group by c.id, c.display_name, c.company_name, c.cik
            """,
            {"structural": list(_STRUCTURAL_GAP_REASONS.keys())},
        )
        rows = cur.fetchall()

    result = []
    for company_id, name, cik, present, gap, not_applicable in rows:
        applicable_total = present + gap
        coverage_pct = round(100 * present / applicable_total, 1) if applicable_total else None
        result.append(
            {
                "company_id": company_id,
                "company_name": name,
                "cik": cik,
                "present": present,
                "gap": gap,
                "not_applicable": not_applicable,
                "coverage_pct": coverage_pct,
            }
        )
    return result


def render_markdown_company(summary: dict) -> str:
    lines = [
        f"# Coverage: {summary['company_name']} (CIK {summary['cik']})",
        "",
        f"Sector: {summary['sic_description'] or 'unknown'} | Status: {summary['status']} | "
        f"Populations: {', '.join(summary['populations']) or 'none'}",
        "",
        f"**Coverage: {summary['coverage_pct']}%** "
        f"({summary['counts'].get('present', 0)} present / "
        f"{summary['counts'].get('gap', 0)} genuine gaps / "
        f"{summary['counts'].get('not_applicable', 0)} not applicable)",
        "",
        "| Data point | Type | Status | Note |",
        "|---|---|---|---|",
    ]
    for item in summary["items"]:
        icon = {"present": "✅", "not_applicable": "⊘", "gap": "❌"}[item["status"]]
        note = item["note"] or ""
        lines.append(
            f"| {item['data_point_name']} | {item['data_point_type']} | {icon} {item['status']} | {note} |"
        )
    return "\n".join(lines)


def render_markdown_population(rows: list[dict], limit: int = 50, worst_first: bool = True) -> str:
    ranked = sorted(
        (r for r in rows if r["coverage_pct"] is not None),
        key=lambda r: r["coverage_pct"],
        reverse=not worst_first,
    )[:limit]
    lines = [
        f"# Company-wise coverage ({'worst' if worst_first else 'best'} {limit} of {len(rows)} active companies)",
        "",
        "| Company | CIK | Coverage % | Present | Genuine gaps | N/A |",
        "|---|---|---|---|---|---|",
    ]
    for r in ranked:
        lines.append(
            f"| {r['company_name']} | {r['cik']} | {r['coverage_pct']}% | {r['present']} | {r['gap']} | {r['not_applicable']} |"
        )
    return "\n".join(lines)
