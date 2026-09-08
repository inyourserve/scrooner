"""Self-consistency comparison: SEC's own bulk Frames data vs. what we
actually stored in `core.fact` for the identical (company, tag, period).
Both sides are supposed to be reading the SAME filing -- a mismatch here
is direct evidence of a bug in OUR OWN Collector/Normalizer pipeline
(a value captured wrong, mis-scaled, or resolved to the wrong period),
not a "different source, different opinion" question the way every other
check built this session is.

Bulk-loads company CIKs and our own facts ONCE per (taxonomy, tag)
combination -- never a query per Frames row (a single Frames response can
carry 1,000-5,500+ rows; a per-row query would be exactly the N+1 shape
already documented as a recurring mistake in this project)."""

import structlog
import psycopg
from decimal import Decimal

from scrooner_pipeline.frames.fetch import FramesRow

logger = structlog.get_logger()

SEVERITY_OK = "ok"
SEVERITY_MISMATCH = "mismatch"
SEVERITY_MISSING_OURS = "missing_ours"

# Both sides read the identical XBRL fact -- this should be an EXACT
# match, not a "real drift expected" tolerance the way a yfinance
# comparison needs. A tiny allowance only for floating-point-adjacent
# rounding noise somewhere in the pipeline, not a real-world-drift budget.
EXACT_MATCH_TOLERANCE_PCT = Decimal("0.01")


def _company_id_by_cik(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where status = 'active'")
        return dict(cur.fetchall())


def _concept_id_for_tag(conn: psycopg.Connection, taxonomy: str, tag: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute("select id from core.concept where taxonomy = %s and tag = %s", (taxonomy, tag))
        row = cur.fetchone()
        return row[0] if row else None


def _load_our_facts_for_tag(
    conn: psycopg.Connection, concept_id: int, company_ids: list[int],
) -> dict[tuple[int, str, str | None], tuple[Decimal, bool, bool]]:
    """(company_id, end_date_str, start_date_str) -> (value, is_authoritative,
    has_real_fiscal_period) -- one bulk query.

    Real bug found live 2026-09-08, first production run: keying by
    end_date ALONE (not also start_date) conflated two genuinely
    different periods that happen to share an end_date -- e.g. Madison
    Square Garden Sports' real Q3 2026 (start 2026-01-01, end 2026-03-31,
    fiscal_period='Q3') vs. its own 9-month YTD cumulative span (start
    2025-07-01, end 2026-03-31, fiscal_period=NULL -- the exact
    "non-standard YTD duration, deliberately left unclassified" case
    `statements/classify.py`'s own `get_statement()` already filters out
    for the identical reason). Both are real, legitimately authoritative
    facts -- NOT a Normalizer conflict at all -- but comparing against a
    SEC Frames row (which reports the true discrete quarter) via
    end-date-only matching non-deterministically picked whichever one a
    Python dict happened to see last, misreporting ~280 real companies'
    net_income as "duplicate-authoritative" when the actual issue was
    this comparison's own key. Fixed by keying on (end_date, start_date)
    together, and preferring a real fiscal_period-classified period over
    an unclassified one when a genuine ambiguity remains."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.company_id, p.end_date::text, p.start_date::text, f.value, f.is_authoritative,
                   (p.fiscal_period is not null) as has_real_fiscal_period
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.concept_id = %s and f.company_id = any(%s)
            """,
            (concept_id, company_ids),
        )
        result: dict[tuple[int, str, str | None], tuple[Decimal, bool, bool]] = {}
        for company_id, end_date, start_date, value, is_authoritative, has_real_fiscal_period in cur.fetchall():
            key = (company_id, end_date, start_date)
            existing = result.get(key)
            # Prefer authoritative over non-authoritative; among equally-
            # authoritative candidates, prefer a real classified fiscal
            # period over an unclassified YTD-span artifact.
            if existing is None:
                result[key] = (value, is_authoritative, has_real_fiscal_period)
            else:
                _ev, e_auth, e_real = existing
                if (is_authoritative, has_real_fiscal_period) > (e_auth, e_real):
                    result[key] = (value, is_authoritative, has_real_fiscal_period)
        return result


def _pct_diff(a: Decimal, b: Decimal) -> Decimal:
    denom = abs(b) if b != 0 else Decimal(1)
    return abs(a - b) / denom * Decimal(100)


def compare_frame(
    conn: psycopg.Connection, canonical_concept_id: int, taxonomy: str, tag: str, rows: list[FramesRow],
) -> dict:
    stats = {"considered": len(rows), "matched_company": 0, SEVERITY_OK: 0, SEVERITY_MISMATCH: 0, SEVERITY_MISSING_OURS: 0}
    concept_id = _concept_id_for_tag(conn, taxonomy, tag)
    if concept_id is None:
        logger.warning("frames.concept_not_in_core", taxonomy=taxonomy, tag=tag)
        return stats

    cik_to_company_id = _company_id_by_cik(conn)
    matched_company_ids = []
    row_by_company: dict[int, FramesRow] = {}
    for row in rows:
        cik_str = str(row.cik).zfill(10)
        company_id = cik_to_company_id.get(cik_str)
        if company_id is not None:
            matched_company_ids.append(company_id)
            row_by_company[company_id] = row
    stats["matched_company"] = len(matched_company_ids)
    if not matched_company_ids:
        return stats

    our_facts = _load_our_facts_for_tag(conn, concept_id, matched_company_ids)

    findings = []
    for company_id in matched_company_ids:
        frame_row = row_by_company[company_id]
        frames_value = Decimal(str(frame_row.value))
        # Instant Frames rows carry no `start` at all; our own core.period
        # convention for an instant period is start_date == end_date --
        # defaulting to end_date here (not None) matches that convention
        # exactly, so instant concepts key correctly without needing an
        # explicit is_instant flag threaded through this function.
        frame_start = frame_row.period_start or frame_row.period_end
        our_fact = our_facts.get((company_id, frame_row.period_end, frame_start))

        if our_fact is None:
            severity = SEVERITY_MISSING_OURS
            our_value = None
            pct_diff = None
        else:
            our_value, _is_auth, _has_real_fp = our_fact
            pct_diff = _pct_diff(our_value, frames_value)
            severity = SEVERITY_OK if pct_diff <= EXACT_MATCH_TOLERANCE_PCT else SEVERITY_MISMATCH

        stats[severity] += 1
        findings.append(
            {
                "company_id": company_id, "concept_id": canonical_concept_id, "taxonomy": taxonomy, "tag": tag,
                "period_start": frame_row.period_start, "period_end": frame_row.period_end,
                "frames_value": frames_value, "our_value": our_value, "pct_diff": pct_diff,
                "severity": severity, "accession": frame_row.accession,
            }
        )

    _write_findings(conn, matched_company_ids, taxonomy, tag, findings)
    logger.info("frames.compare_done", taxonomy=taxonomy, tag=tag, **stats)
    return stats


_INSERT_SQL = """
    insert into analytics.frames_consistency_check
        (company_id, canonical_concept_id, taxonomy, tag, period_start, period_end,
         frames_value, our_value, pct_diff, severity, accession, checked_at)
    values (%(company_id)s, %(concept_id)s, %(taxonomy)s, %(tag)s, %(period_start)s, %(period_end)s,
            %(frames_value)s, %(our_value)s, %(pct_diff)s, %(severity)s, %(accession)s, now())
    on conflict (company_id, taxonomy, tag, period_end) do update
        set canonical_concept_id = excluded.canonical_concept_id, period_start = excluded.period_start,
            frames_value = excluded.frames_value, our_value = excluded.our_value, pct_diff = excluded.pct_diff,
            severity = excluded.severity, accession = excluded.accession, checked_at = now()
"""


def _write_findings(conn: psycopg.Connection, company_ids: list[int], taxonomy: str, tag: str, findings: list[dict]) -> None:
    with conn.cursor() as cur:
        # Delete-then-reinsert, scoped to exactly the companies/tag this
        # call actually evaluated -- same discipline as every other batch
        # writer in this codebase (a company no longer appearing in a
        # fresh Frames pull for this tag/period shouldn't keep a stale row).
        cur.execute(
            "delete from analytics.frames_consistency_check where taxonomy = %s and tag = %s and company_id = any(%s)",
            (taxonomy, tag, company_ids),
        )
        cur.executemany(_INSERT_SQL, findings)
    conn.commit()
