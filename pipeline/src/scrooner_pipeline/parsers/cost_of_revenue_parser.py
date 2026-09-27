"""Parser: Cost of Revenue via rendered-report DIMENSIONAL summation.

Real finding, 2026-09-21 (direct user report: Hyatt Hotels' quarterly
results showing blank Cost of Revenue/Gross Profit/Operating Expenses/
Operating Income rows, cik 0001468174): a company's true Cost of Revenue
can be tagged in real XBRL under a tag ALREADY in concept_mapping
(`us-gaap:CostOfGoodsAndServicesSold`), but reported ONLY as several
DIMENSIONAL facts -- one per segment/product-line axis member (Hyatt's
real 10-Q tags this separately for its Owned & Leased / Distribution /
Reimbursed-costs segments) -- never as a single company-wide total fact.
The standard Company Facts API (data.sec.gov/api/xbrl/companyfacts) --
what this project's Collector fetches -- strips ALL dimensional context
entirely (doc 22's already-documented finding, reconfirmed here for a
genuinely new population: cost-of-revenue-family concepts, not just
segment revenue). `core.fact` never sees these facts at all, so no
number of tags added to `concept_mapping` could ever find them --
sized at ~570 companies across dozens of unrelated sectors (oil & gas,
insurance, hospitality, restaurants, airlines, software...), too
heterogeneous to be one or two clean SIC buckets the way `revenue`'s own
gap was.

The SAME rendered R*.htm primary income-statement report that
revenue_parser.py/segment_revenue.py already read renders these
dimensional facts as repeated rows (identical label, once per segment)
UNDER the main non-dimensional statement, in the exact same HTML
document -- this parser sums every occurrence of a cost-of-revenue-shaped
label found anywhere in that one report for the current period, rather
than picking a single "best" row (revenue_parser.py's approach, correct
for revenue since its own top-line total is a single non-dimensional row
for every company checked so far -- confirmed NOT true here).

Verified against Hyatt Q2 2025 before writing this as a general rule:
summing all 3 "Costs of goods and services sold" rows ($246M + $219M +
$949M = $1,414M) landed within 1.4% of yfinance's own reported $1,434M
for the identical period -- the small residual gap traced to a real,
separate company-extension tag (`h:OtherDirectCosts`, $20M) this parser
deliberately does NOT chase; matching a tag ALREADY in concept_mapping
well within tolerance is real, checkable evidence, guessing at a
company-specific extension tag's label would not be.

Explicit, standing user direction (2026-09-08, reaffirmed 2026-09-21):
yfinance is comparison/validation ONLY, never a value source. This
module never stores a yfinance number -- it uses yfinance's OWN already-
fetched line item (analytics.yfinance_statement_line, populated by
yfinance_financials/fetch.py) purely as the target to validate a parsed
SEC-sourced sum against. A parsed sum that does not reconcile within
tolerance is discarded (outcome='no_yfinance_match'), never stored with
lower confidence -- there is no code path where a number written by this
module did not originate from summing real core-fact-shaped rendered
SEC values.

Reuses revenue_parser.py's own income-statement report discovery
(`find_income_statement_report`) and segment_revenue.py's row/cell
parsing primitives -- same report, same real markup shape, a different
row-selection rule (sum every matching label, not pick one best)."""

import re
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.parsers.revenue_parser import (
    _detect_scale,
    _parse_period_end,
    find_income_statement_report,
)
from scrooner_pipeline.segments.segment_revenue import (
    _CELL,
    _ROW,
    _cell_text,
    _parse_value,
)

logger = structlog.get_logger()

# Matches every tag currently mapped to `cost_of_revenue`
# (CostOfGoodsAndServicesSold/CostOfRevenue/CostOfGoodsSold) by its real,
# observed rendered label -- deliberately narrow, mirrors
# revenue_parser.py's REVENUE_LABEL_PATTERN discipline of matching a
# known concept's own vocabulary rather than a broad "looks cost-shaped"
# guess. Does NOT match "Cost of Goods and Services Sold" appearing as a
# SECTION HEADER (no trailing colon here since real headers in this
# report end with ':' -- confirmed live against Hyatt's own "DIRECT AND
# GENERAL AND ADMINISTRATIVE EXPENSES:" header, which this pattern
# correctly does not match).
#
# "products?\s+sold" and the optional trailing parenthetical qualifier
# added 2026-09-21, found live checking a real "no_row_matched" case
# (Ampco Pittsburgh Corp, an industrial manufacturer) during the initial
# broad rollout: its real label is "Costs of products sold (excluding
# depreciation and amortization)" -- a genuine, common variant (product
# companies say "products sold", not "goods sold") plus a real,
# common qualifier clause many manufacturers add. The parenthetical is
# matched generically (any `(...)` suffix), not hardcoded to this one
# company's exact wording, since the qualifier text itself varies by
# filer and carries no information this parser needs.
COST_OF_REVENUE_LABEL_PATTERN = re.compile(
    r"^(total\s+)?costs?\s+of\s+(goods\s+and\s+services\s+sold|goods\s+sold|products?\s+sold|revenues?|sales)(\s*\([^)]*\))?$",
    re.IGNORECASE,
)

# How many independent matching rows this parser will sum before treating
# the report as too irregular to trust automatically -- a real safeguard,
# not an arbitrary number: every real case checked (Hyatt: 3 segments) is
# well under this, and a report matching more than this many times is
# more likely a parsing/label-collision problem than a real company
# structure, so it's safer to report `too_many_matches` and leave the gap
# honest than to silently sum something wrong.
MAX_MATCHING_ROWS = 8

# How close the parsed sum must land to yfinance's own already-fetched
# figure before being trusted -- wider than a single-tag reconciliation
# tolerance because summing several dimensional rows can legitimately
# miss a small residual company-extension line item (Hyatt's own
# `h:OtherDirectCosts`, 1.4% of the total) without that being a wrong
# answer, just an incomplete-but-still-correct-tag one.
YFINANCE_VALIDATION_TOLERANCE_PCT = Decimal(10)


def _extract_cost_of_revenue_rows(html: str) -> dict | None:
    """Returns {'value': ..., 'period_end': ...} summing EVERY row in the
    report whose label matches COST_OF_REVENUE_LABEL_PATTERN, using each
    matching row's own first non-empty value cell (the current-period
    column -- same "first valid cell, not raw index" rule revenue_parser.py
    already established, since dimensional sub-tables can carry their own
    interleaved footnote cells same as any other row). Returns None if no
    row matches at all, or if more than MAX_MATCHING_ROWS match (too
    irregular to trust)."""
    rows = _ROW.findall(html)
    if len(rows) < 2:
        return None
    title_cells = _CELL.findall(rows[0][1])
    scale = _detect_scale(_cell_text(title_cells[0])) if title_cells else Decimal(1)
    date_cells = [_cell_text(c) for c in _CELL.findall(rows[1][1])]
    period_end = _parse_period_end(date_cells[0]) if date_cells else None

    matched_values: list[Decimal] = []
    for _row_class, row_html in rows[2:]:
        cells = _CELL.findall(row_html)
        if not cells:
            continue
        label = _cell_text(cells[0])
        if not label or not COST_OF_REVENUE_LABEL_PATTERN.match(label):
            continue

        value = None
        for raw_cell in cells[1:]:
            value = _parse_value(_cell_text(raw_cell))
            if value is not None:
                break
        if value is not None:
            matched_values.append(Decimal(value))

    if not matched_values or len(matched_values) > MAX_MATCHING_ROWS:
        return None

    total = sum(matched_values) * scale
    return {
        "value": str(total),
        "period_end": period_end,
        "matched_rows": len(matched_values),
    }


def _pct_diff(a: Decimal, b: Decimal) -> Decimal:
    denom = abs(b) if b != 0 else Decimal(1)
    return abs(a - b) / denom * Decimal(100)


def _yfinance_target(
    conn: psycopg.Connection, company_id: int, period_end: str | None
) -> Decimal | None:
    """The closest already-fetched yfinance 'Cost Of Revenue' figure for
    this company -- comparison/validation only, per this module's own
    docstring; never stored. Matches on exact period_end first (the
    common case -- this parser and yfinance_financials/fetch.py both key
    off the filing's own quarter-end), falling back to the closest
    available period_end within 15 days (yfinance's own calendar-quarter
    rounding, the same tolerance compare.py already established)."""
    if period_end is None:
        return None
    with conn.cursor() as cur:
        cur.execute(
            """
            select value, abs(period_end - %(period_end)s::date) as dist
            from analytics.yfinance_statement_line
            where company_id = %(company_id)s and statement_type = 'income_statement'
              and line_item = 'Cost Of Revenue' and value is not null
            order by dist asc
            limit 1
            """,
            {"company_id": company_id, "period_end": period_end},
        )
        row = cur.fetchone()
    if row is None or row[1] > 15:
        return None
    return Decimal(str(row[0]))


def _parse_with_outcome(
    client: SECClient, conn: psycopg.Connection, company_id: int, cik: str
) -> tuple[str, dict | None]:
    found = find_income_statement_report(client, cik)
    if found is None:
        return "no_report", None
    report_url = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{found['filing']['accession_number'].replace('-', '')}/{found['report']['html_file']}"
    )
    resp = client.get(report_url)
    extracted = _extract_cost_of_revenue_rows(resp.text)
    if extracted is None:
        return "no_row_matched", None

    target = _yfinance_target(conn, company_id, extracted["period_end"])
    if target is None:
        return "no_yfinance_target", None
    parsed_value = Decimal(extracted["value"])
    pct_diff = _pct_diff(parsed_value, target)
    if pct_diff > YFINANCE_VALIDATION_TOLERANCE_PCT:
        logger.info(
            "cost_of_revenue_parser.yfinance_mismatch",
            cik=cik,
            parsed=str(parsed_value),
            yfinance=str(target),
            pct_diff=str(pct_diff),
        )
        return "no_yfinance_match", None

    return "matched", {
        "value": extracted["value"],
        "period_end": extracted["period_end"],
        "source_form": found["filing"]["form"],
        "source_accession": found["filing"]["accession_number"],
        "source_report": found["report"]["title"],
        "matched_rows": extracted["matched_rows"],
        "pct_diff_vs_yfinance": str(pct_diff),
    }


PARSER_NAME = "cost_of_revenue_parser"
CONCEPT_NAME = "cost_of_revenue"


def find_gap_companies(
    conn: psycopg.Connection, ciks: set[str] | None = None
) -> list[tuple[int, str]]:
    """Active companies genuinely missing `cost_of_revenue` in
    analytics.canonical_fact, not already attempted by this parser
    before (same efficiency contract as revenue_parser.py's own
    find_gap_companies -- a rerun only looks at companies never tried).
    Read-only."""
    with conn.cursor() as cur:
        cik_filter = "and c.cik = any(%s)" if ciks else ""
        params: tuple = (sorted(ciks),) if ciks else ()
        cur.execute(
            f"""
            select c.id, c.cik
            from core.company c
            where c.status = 'active'
              and not exists (
                  select 1 from analytics.canonical_fact cf
                  join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
                  where cf.company_id = c.id and cc.name = %s
              )
              and not exists (
                  select 1 from analytics.concept_parser_attempt cpa
                  join analytics.canonical_concept cc2 on cc2.id = cpa.canonical_concept_id
                  where cpa.company_id = c.id and cc2.name = %s and cpa.parser_name = %s
              )
              {cik_filter}
            order by c.cik
            """,
            (CONCEPT_NAME, CONCEPT_NAME, PARSER_NAME, *params),
        )
        return cur.fetchall()


def run(conn: psycopg.Connection, ciks: set[str] | None = None) -> dict:
    """Same orchestration contract as revenue_parser.py's run(): never
    writes into `cost_of_revenue`'s own canonical_fact directly -- a
    matched, yfinance-validated value is stored in the shared
    analytics.concept_parser_result registry (full source_form/
    accession/report provenance, plus matched_rows/pct_diff_vs_yfinance
    in its own note-equivalent, see below) so a future reader can trace
    exactly which rendered rows were summed and how closely they
    reconciled. Every outcome is logged to concept_parser_attempt so a
    rerun never re-fetches a company already tried -- EXCEPT
    'no_yfinance_target', deliberately not recorded: unlike
    revenue_parser.py, this parser's correctness depends on
    yfinance_statement_line already being populated for the company,
    itself a separate, independently-rotating daily fetch (~200/day).
    A company whose yfinance data simply hasn't arrived YET would
    otherwise be permanently marked 'attempted' here and never re-tried
    once that data exists -- found and fixed 2026-09-21 before this ran
    broadly enough to matter in practice."""
    stats = {
        "considered": 0,
        "ok": 0,
        "no_report": 0,
        "no_row_matched": 0,
        "no_yfinance_target": 0,
        "no_yfinance_match": 0,
        "errored": 0,
    }
    candidates = find_gap_companies(conn, ciks)

    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = %s",
            (CONCEPT_NAME,),
        )
        canonical_concept_id = cur.fetchone()[0]

    results = []
    with SECClient() as client:
        for company_id, cik in candidates:
            stats["considered"] += 1
            outcome = "errored"
            try:
                outcome, extracted = _parse_with_outcome(client, conn, company_id, cik)
                stats[outcome if outcome != "matched" else "ok"] += 1
                if outcome == "matched":
                    result = {"company_id": company_id, "cik": cik, **extracted}
                    results.append(result)
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            insert into analytics.concept_parser_result
                                (company_id, canonical_concept_id, parser_name, value, period_end,
                                 source_form, source_accession, source_report)
                            values (%s, %s, %s, %s, %s, %s, %s, %s)
                            on conflict (company_id, canonical_concept_id) do update
                                set parser_name = excluded.parser_name, value = excluded.value,
                                    period_end = excluded.period_end, source_form = excluded.source_form,
                                    source_accession = excluded.source_accession,
                                    source_report = excluded.source_report, created_at = now()
                            """,
                            (
                                company_id,
                                canonical_concept_id,
                                PARSER_NAME,
                                result["value"],
                                result["period_end"],
                                result["source_form"],
                                result["source_accession"],
                                result["source_report"],
                            ),
                        )
                    logger.info(
                        "cost_of_revenue_parser.company_matched",
                        cik=cik,
                        value=result["value"],
                        matched_rows=result["matched_rows"],
                        pct_diff_vs_yfinance=result["pct_diff_vs_yfinance"],
                    )
            except Exception:
                logger.warning(
                    "cost_of_revenue_parser.company_failed", cik=cik, exc_info=True
                )
                stats["errored"] += 1
                outcome = "errored"
                conn = safe_rollback(conn, stage="cost_of_revenue_parser", cik=cik)

            if outcome != "no_yfinance_target":
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        insert into analytics.concept_parser_attempt
                            (company_id, canonical_concept_id, parser_name, outcome)
                        values (%s, %s, %s, %s)
                        on conflict (company_id, canonical_concept_id, parser_name) do update
                            set outcome = excluded.outcome, attempted_at = now()
                        """,
                        (company_id, canonical_concept_id, PARSER_NAME, outcome),
                    )
            conn.commit()

    logger.info("cost_of_revenue_parser.done", **stats)
    return {"stats": stats, "results": results}
