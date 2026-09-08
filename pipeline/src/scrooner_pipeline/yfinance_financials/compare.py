"""Compares stored yfinance statement lines (fetch.py) against our own
canonical_fact values, period by period -- not just the latest period,
the way sanity/yfinance_check.py's ratio checks do. Writes
analytics.statement_comparison_finding. A finding at major/critical
severity can be handed to sanity/tag_investigator.py's investigate() for
the actual fix -- always sourced from a real core.fact/SEC tag, yfinance
only ever used to detect/match (see that module's docstring for the full
rule, set by explicit user direction 2026-09-08).

Real period-alignment gotcha (see fetch.py's docstring): yfinance's own
quarterly columns are calendar quarter-ends, not a company's actual
fiscal quarter-end, so the join below uses a tolerance window
(fetch.PERIOD_MATCH_TOLERANCE_DAYS), never an exact date match -- and
picks the CLOSEST core.period within that window, not just any period
inside it."""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.yfinance_financials.fetch import PERIOD_MATCH_TOLERANCE_DAYS
from scrooner_pipeline.yfinance_financials.line_item_map import BANK_INCOMPATIBLE_CONCEPTS, BANK_SIC_PREFIXES, CONCEPT_FOR_COMPARISON

logger = structlog.get_logger()

SEVERITY_OK = "ok"
SEVERITY_MINOR = "minor"
SEVERITY_MAJOR = "major"
SEVERITY_MISSING_OURS = "missing_ours"

# Wider than the ratio-based Data Sanity Layer's thresholds -- comparing a
# SPECIFIC quarter (not a TTM-preferred "most recent") against yfinance's
# own calendar-quarter-rounded figure carries more expected noise by
# construction.
MINOR_PCT = 10.0
MAJOR_PCT = 30.0


def _pct_diff(our_value: Decimal, external_value: Decimal) -> Decimal:
    denom = abs(external_value) if external_value != 0 else Decimal(1)
    return (our_value - external_value) / denom * Decimal(100)


def _severity_for(pct_diff: Decimal) -> str:
    abs_pct = abs(pct_diff)
    if abs_pct >= MAJOR_PCT:
        return SEVERITY_MAJOR
    if abs_pct >= MINOR_PCT:
        return SEVERITY_MINOR
    return SEVERITY_OK


def _is_bank(conn: psycopg.Connection, company_id: int) -> bool:
    with conn.cursor() as cur:
        cur.execute("select sic_code from core.company where id = %s", (company_id,))
        row = cur.fetchone()
    return bool(row and row[0] and row[0][:3] in BANK_SIC_PREFIXES)


def _load_mapping(conn: psycopg.Connection) -> dict[tuple[str, str], dict]:
    """Includes concept_id directly (not just concept_name) -- found live
    2026-09-08: an earlier version of compare_company() re-queried
    analytics.canonical_concept for the id once PER FINDING (dozens per
    company), the exact per-row-in-a-loop shape this project's own
    restatements.py lesson warns against. Resolved here, once, for all
    ~29 mapped line items up front."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select m.statement_type, m.line_item, cc.name, cc.id, m.sign_flip, m.notes
            from analytics.yfinance_line_item_mapping m
            join analytics.canonical_concept cc on cc.id = m.canonical_concept_id
            where m.confidence != 'rejected'
            """
        )
        return {
            (statement_type, line_item): {"concept_name": concept_name, "concept_id": concept_id, "sign_flip": sign_flip, "notes": notes}
            for statement_type, line_item, concept_name, concept_id, sign_flip, notes in cur.fetchall()
        }


def _load_our_periods(conn: psycopg.Connection, company_id: int) -> list[tuple[int, object]]:
    """QUARTERLY periods only -- matches yfinance's own `quarterly_*`
    statements' granularity (fetch.py fetches quarterly, not annual).
    Real bug found live 2026-09-08: a company's Q4 and FY periods can
    share the EXACT same end_date (Nike's FY2025: both end 2025-05-31,
    confirmed live -- 2 FY rows and 1 Q4 row, all three same date). An
    earlier version of this query included FY periods too, so
    _closest_period's tie-break (zero distance either way) could pick
    the FY row while comparing against yfinance's QUARTERLY net income --
    a ~15x mismatch that looked like a real Scrooner bug (Nike's Q4 net
    income $211M vs. its FY net income $3,219M) but was actually this
    comparison matching the wrong granularity, not a data error."""
    with conn.cursor() as cur:
        cur.execute(
            "select id, end_date from core.period where company_id = %s and fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4')",
            (company_id,),
        )
        return cur.fetchall()


def _closest_period(periods: list[tuple[int, object]], target_end: object) -> tuple[int, object] | None:
    from datetime import timedelta

    candidates = [(pid, end) for pid, end in periods if abs((end - target_end)) <= timedelta(days=PERIOD_MATCH_TOLERANCE_DAYS)]
    if not candidates:
        return None
    return min(candidates, key=lambda pair: abs(pair[1] - target_end))


def _load_our_values(conn: psycopg.Connection, company_id: int, concept_names: set[str]) -> dict[tuple[str, int], Decimal]:
    """One query for the whole company, every concept this comparison
    could ever need (raw + resolved names) -- see _load_mapping's own
    comment for the N+1 shape this replaces."""
    resolved_names = {CONCEPT_FOR_COMPARISON.get(name, name) for name in concept_names}
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, cf.period_id, cf.value
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            where cf.company_id = %s and cc.name = any(%s)
            """,
            (company_id, sorted(resolved_names)),
        )
        return {(name, period_id): value for name, period_id, value in cur.fetchall()}


def compare_company(conn: psycopg.Connection, company_id: int, mapping: dict[tuple[str, str], dict]) -> dict:
    stats = {"ok": 0, "minor": 0, "major": 0, "missing_ours": 0}
    is_bank = _is_bank(conn, company_id)
    periods = _load_our_periods(conn, company_id)
    concept_names = {m["concept_name"] for m in mapping.values()}
    our_values = _load_our_values(conn, company_id, concept_names)

    with conn.cursor() as cur:
        cur.execute(
            "select statement_type, line_item, period_end, value from analytics.yfinance_statement_line where company_id = %s",
            (company_id,),
        )
        yfinance_rows = cur.fetchall()

    findings = []
    for statement_type, line_item, period_end, external_value in yfinance_rows:
        mapped = mapping.get((statement_type, line_item))
        if mapped is None or external_value is None:
            continue
        concept_name = mapped["concept_name"]
        closest = _closest_period(periods, period_end)
        if closest is None:
            continue
        period_id, _end = closest

        external_decimal = Decimal(str(external_value))
        if mapped["sign_flip"]:
            external_decimal = -external_decimal

        resolved_name = CONCEPT_FOR_COMPARISON.get(concept_name, concept_name)
        our_value = our_values.get((resolved_name, period_id))
        concept_id = mapped["concept_id"]

        note = mapped["notes"] if (is_bank and concept_name in BANK_INCOMPATIBLE_CONCEPTS) else None

        if our_value is None:
            severity = SEVERITY_MISSING_OURS
            pct_diff = None
        else:
            pct_diff = _pct_diff(our_value, external_decimal)
            severity = _severity_for(pct_diff)

        findings.append(
            {
                "company_id": company_id, "concept_id": concept_id, "period_id": period_id, "period_end": period_end,
                "our_value": our_value, "yfinance_value": external_decimal, "yfinance_line_item": line_item,
                "pct_diff": pct_diff, "severity": severity, "note": note,
            }
        )
        stats[severity] += 1

    _write_findings(conn, company_id, findings)
    return stats


_UPSERT_SQL = """
    insert into analytics.statement_comparison_finding
        (company_id, canonical_concept_id, period_id, period_end, our_value, yfinance_value, yfinance_line_item, pct_diff, severity, note, checked_at)
    values (%(company_id)s, %(concept_id)s, %(period_id)s, %(period_end)s, %(our_value)s, %(yfinance_value)s, %(yfinance_line_item)s, %(pct_diff)s, %(severity)s, %(note)s, now())
    on conflict (company_id, canonical_concept_id, period_end) do update
        set period_id = excluded.period_id, our_value = excluded.our_value, yfinance_value = excluded.yfinance_value,
            yfinance_line_item = excluded.yfinance_line_item, pct_diff = excluded.pct_diff,
            severity = excluded.severity, note = excluded.note, checked_at = now()
"""


def _write_findings(conn: psycopg.Connection, company_id: int, findings: list[dict]) -> None:
    with conn.cursor() as cur:
        cur.execute("delete from analytics.statement_comparison_finding where company_id = %s", (company_id,))
        if findings:
            cur.executemany(_UPSERT_SQL, findings)
    conn.commit()


def investigate_major_findings(conn: psycopg.Connection) -> dict:
    """Hands every current 'major' finding WITHOUT an already-understood
    note (i.e. not a known bank-incompatible mismatch) to sanity/
    tag_investigator.py's investigate() -- the same fetcher-tree trace,
    the same rule that a fix is only ever applied from a real core.fact/
    SEC tag, yfinance used only to detect/match. Reuses that pipeline
    instead of duplicating it; see this module's own docstring."""
    from scrooner_pipeline.sanity.tag_investigator import investigate

    stats = {"considered": 0, "auto_fixed": 0, "needs_review": 0, "no_match_found": 0}
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.company_id, cc.name, f.period_id, f.yfinance_value
            from analytics.statement_comparison_finding f
            join analytics.canonical_concept cc on cc.id = f.canonical_concept_id
            where f.severity = 'major' and f.note is null and f.period_id is not null
            """
        )
        rows = cur.fetchall()

    for company_id, concept_name, period_id, yfinance_value in rows:
        stats["considered"] += 1
        outcome = investigate(conn, company_id, concept_name, Decimal(yfinance_value), period_id=period_id)
        stats[outcome["outcome"]] += 1

    logger.info("yfinance_financials.investigate_done", **stats)
    return stats


def compare_statements(conn: psycopg.Connection, company_ids: list[int]) -> dict:
    mapping = _load_mapping(conn)
    totals = {"considered": len(company_ids), "ok": 0, "minor": 0, "major": 0, "missing_ours": 0}
    for company_id in company_ids:
        result = compare_company(conn, company_id, mapping)
        for key, value in result.items():
            totals[key] += value
    logger.info("yfinance_financials.compare_done", **totals)
    return totals
