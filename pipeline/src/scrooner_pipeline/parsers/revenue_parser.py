"""Parser 3 (doc 42): revenue via rendered-report LABEL matching, for the
genuine residual `revenue` gap -- companies whose income statement really
does report a top-line revenue figure, just under a company-specific
custom XBRL extension tag no `concept_mapping` tag list could enumerate
in advance (the confirmed real example: MSP Recovery, tagged
`mspr_TotalClaimsRecovery`).

This is NOT a general "read any income statement" parser -- built and
verified live 2026-09-05 against 6 real, deliberately diverse companies
(MSP Recovery, a real bank, a real mortgage REIT via segment_revenue's
own report-title probe, BOXABL, AmBase Corp, Australian Oilseeds/IFRS)
before writing a single line of matching logic, because the naive ideas
tried first were each unsafe on at least one of them:

- A "first monetary row" positional fallback would have UNDER-counted
  MSP Recovery's own real revenue (its first monetary line is "Claims
  recovery income", a component; "Total Revenues" two rows later --
  "Claims recovery income" + "Other" -- is the real figure) and would
  have WRONGLY populated `revenue` for a real bank (Arrow Financial's
  first monetary row is "Interest and Fees on Loans", a component of
  "Total Interest and Dividend Income" -- a bank's own gross interest
  figure, not a revenue-equivalent per doc 42 Part 1's own reasoning)
  and for a SPAC shell (BOXABL's first monetary row is a G&A expense;
  its only other monetary line before net income is "Investment income
  on trust account", SPAC trust interest, not operating revenue).
- The fix: match ONLY a curated, strict revenue-family label pattern
  (REVENUE_LABEL_PATTERN below), scanned top-to-bottom but capped at
  the first EXPENSE_SECTION_PATTERN row encountered (never look past
  where the statement itself signals "the revenue section is over").
  A bank's "Total Interest and Dividend Income" and a SPAC's
  "Investment income on trust account" don't match this pattern at
  all -- no extra bank/SPAC exclusion logic was needed once the label
  pattern was kept this strict. Confirmed live: this correctly returns
  None for the bank, BOXABL, and AmBase (no revenue row exists there),
  and correctly finds MSP Recovery's "Total Revenues" (preferring it
  over the "Claims recovery income" component row above it).

Sized honestly before building (doc 42): of 693 companies missing
`revenue`, ~503 are legitimate structural absence (SPACs, pre-revenue
pharma/biotech, mining exploration, commodity brokers) and 44 were a
real sector cluster (BDCs, fixed separately as `bdc_total_investment_
income`, never routed through this parser). The remaining ~130-140
companies (see `scripts/find_concept_gap_clusters.py`'s own output) are
themselves mostly ANOTHER round of structural populations this parser
correctly returns None for (banks, mortgage REITs, asset-backed trusts,
oil royalty trusts, foreign IFRS filers miscategorized as active, more
SPACs/pre-revenue startups with a non-obvious SIC code) -- the genuinely
parser-fixable population is smaller still, on the order of single
digits to low tens of real companies. This module is deliberately
conservative (never guesses, returns None rather than a low-confidence
value) rather than sized to hit a target number.

Reuses segment_revenue.py's own proven FilingSummary.xml discovery and
row/cell HTML parsing helpers -- the same real markup shape, a
different report (the primary income statement, not a segment detail)
and a different row-selection rule (label match, not XBRL concept_ref
match, since by definition the target tag is unknown in advance)."""

import re
from datetime import datetime

import psycopg
import structlog

from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.segments.segment_revenue import (
    _CELL,
    _ROW,
    _cell_text,
    _latest_10q_or_10k,
    _parse_value,
    _filing_summary_reports,
)

logger = structlog.get_logger()

# Primary income-statement report titles -- deliberately narrower than
# segment_revenue.py's own SEGMENT_TITLE_PATTERN, which targets the
# segment-BREAKDOWN detail report, not the primary statement. Checked
# live across 6 real companies before finalizing (see module docstring).
INCOME_STATEMENT_TITLE_PATTERN = re.compile(
    r"(condensed\s+)?(consolidated\s+)?statements?\s+of\s+(operations|income)\b",
    re.IGNORECASE,
)
# A report titled "... (Parenthetical)" is a companion disclosure table
# (share/per-share detail for the same statement), not the statement
# itself -- excluded the same way segment_revenue.py excludes
# scaffolding "(Tables)"/"(Policies)" reports.
PARENTHETICAL_SUFFIX_PATTERN = re.compile(r"\(parenthetical\)\s*$", re.IGNORECASE)

# A revenue-family TOTAL label -- deliberately strict. Matches "Total
# Revenues", "Total Revenue", "Total Net Sales", "Net sales", "Revenues"
# (bare, when it's the statement's own top-line label), "Total Claims
# Recovery"/"Claims recovery income" (MSP Recovery's real, confirmed
# custom-tag case). Does NOT match "Total Interest and Dividend Income"
# (a bank's own gross interest figure -- checked live, doesn't overlap
# this pattern), "Investment income on trust account" (SPAC trust
# interest), or "Total investment income" (BDCs -- deliberately handled
# by the SEPARATE bdc_total_investment_income concept, doc 42 Part 4,
# never this parser, so this pattern intentionally excludes the word
# "investment" to avoid re-capturing that population here).
REVENUE_LABEL_PATTERN = re.compile(
    r"^(total\s+)?(net\s+)?(revenues?|sales|claims?\s+recover(y|ies)(\s+income)?)$",
    re.IGNORECASE,
)
# A row containing "total" AND the revenue keyword is preferred over a
# bare component row with the same keyword (MSP Recovery: "Total
# Revenues" over "Claims recovery income" -- both match
# REVENUE_LABEL_PATTERN, "total" wins the tie).
_HAS_TOTAL = re.compile(r"^total\b", re.IGNORECASE)

# Once a row's label matches this, the revenue section of the statement
# is over -- never match a REVENUE_LABEL_PATTERN row found AFTER this
# point (a coincidental later "sales" mention deep in an expense/tax
# footnote-style row is not the top-line figure).
EXPENSE_SECTION_PATTERN = re.compile(
    r"^(operating\s+expenses?|costs?\s+and\s+expenses?|cost\s+of\s+(revenues?|sales|goods\s+sold)|expenses?):?$",
    re.IGNORECASE,
)

# The absolute backstop: EVERY primary income statement ends at a net
# income/loss line, regardless of company type (bank, lender, REIT,
# ordinary operating company) -- so nothing found after this row can
# possibly be the statement's own top-line revenue figure. This is
# NOT the same signal as EXPENSE_SECTION_PATTERN and must be checked
# separately: a first attempted fix here tried adding "Interest
# Expense" to EXPENSE_SECTION_PATTERN directly (reasoning: a bank's
# real income statement has no "Operating expenses:" header at all,
# so the scanner never stopped) -- but that BROKE loanDepot, a real
# lender whose real "Total net revenues" line legitimately comes
# AFTER its own Interest income/Interest expense section (interest
# income/expense there are components being netted INTO a broader
# revenue build-up, not the whole statement). Verified live 2026-09-05
# against the two real companies that surfaced the original bug
# (Peoples Financial Corp, BV Financial): both have a "Net income" row
# well before the later, unrelated ASC-606 revenue-disaggregation
# footnote table (row 37/35 vs. row 43/40) that caused the original
# false positive -- so this boundary correctly excludes that table
# without excluding loanDepot's legitimate later revenue line.
NET_INCOME_PATTERN = re.compile(
    r"^net\s+(income|loss|earnings)(\s*\(loss\)|\s*\(income\))?(\s+before\s+(income\s+)?tax(es)?)?:?$",
    re.IGNORECASE,
)


def find_income_statement_report(client: SECClient, cik: str) -> dict | None:
    """Same shape as segment_revenue.py's find_segment_report, targeting
    the primary income statement report instead of a segment-detail one."""
    filing = _latest_10q_or_10k(client, cik)
    if filing is None:
        return None
    reports = _filing_summary_reports(client, int(cik), filing["accession_number"])
    candidates = [
        r
        for r in reports
        if INCOME_STATEMENT_TITLE_PATTERN.search(r["title"])
        and not PARENTHETICAL_SUFFIX_PATTERN.search(r["title"])
    ]
    if not candidates:
        return None
    # FilingSummary.xml lists reports in filing order -- the primary
    # statement report is always the first one whose title matches
    # (checked live: R4.htm/R2.htm across every company sampled), a
    # later match would be a derivative/footnote table reusing the
    # same title words.
    return {"filing": filing, "report": candidates[0]}


def _parse_period_end(text: str) -> str | None:
    """SEC's rendered date-header cells use 'Sep. 30, 2024'-style text
    (abbreviated month, trailing period, comma) -- not an ISO date.
    Found live 2026-09-05: storing this raw text directly into
    core.period_end (a `date` column) crashed with InvalidDatetimeFormat
    on the very first real run. Returns an ISO date string, or None if
    the text doesn't match this specific known format (never guesses)."""
    if not text:
        return None
    cleaned = text.replace(".", "").strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _extract_revenue_row(html: str) -> str | None:
    """Returns {'value': ..., 'period_end': ...} for the MOST RECENT
    period column (the first data column after the label), or None if
    no safe match exists. Never guesses -- a statement with no row
    matching REVENUE_LABEL_PATTERN before the expense section returns
    None, exactly like a bank, a SPAC shell, or any company with
    genuinely no revenue line."""
    rows = _ROW.findall(html)
    if len(rows) < 2:
        return None
    # Row 1 is the date-header row (row 0 groups by period TYPE, e.g.
    # "3 Months Ended" spanning N columns) -- same layout
    # segment_revenue.py's own parse_segment_report already established
    # and verified live across the golden-10 and every company sampled
    # for this module.
    date_cells = [_cell_text(c) for c in _CELL.findall(rows[1][1])]

    best_value: str | None = None
    best_period_end: str | None = None
    best_had_total = False

    for _row_class, row_html in rows[2:]:
        cells = _CELL.findall(row_html)
        if not cells:
            continue
        label = _cell_text(cells[0])
        if not label:
            continue

        if EXPENSE_SECTION_PATTERN.match(label) or NET_INCOME_PATTERN.match(label):
            break

        if not REVENUE_LABEL_PATTERN.match(label):
            continue

        # First non-empty value cell is the most recent period's figure
        # -- checked live across every company sampled for this module:
        # the FIRST data column in a 3-month/6-month comparison table is
        # always the current period, oldest-to-newest is never reversed.
        #
        # Deliberately NOT using the raw cell's own index to look up
        # date_cells[i] -- found live 2026-09-05 (MSP Recovery): data
        # rows carry extra interleaved footnote-reference cells
        # (sometimes a real marker like '[1]', sometimes just an empty
        # placeholder slot) that the plain date-header row does NOT
        # have, so raw cell position and date-column position drift out
        # of sync (a value found at raw cell index 2 does NOT mean
        # date_cells[2] -- it can genuinely mean date_cells[0]).
        # Instead: the first valid value found in the row is always
        # paired with date_cells[0] (this table's own most-recent
        # period) -- correct whenever the current period is actually
        # populated (true for a real top-line revenue figure in every
        # case checked), a known, accepted imprecision in the rare case
        # a row's current-period cell is itself genuinely blank.
        value = None
        for raw_cell in cells[1:]:
            value = _parse_value(_cell_text(raw_cell))
            if value is not None:
                break
        if value is None:
            continue
        period_end = _parse_period_end(date_cells[0]) if date_cells else None

        has_total = bool(_HAS_TOTAL.match(label))
        if best_value is None or (has_total and not best_had_total):
            best_value = value
            best_period_end = period_end
            best_had_total = has_total

    if best_value is None:
        return None
    return {"value": best_value, "period_end": best_period_end}


def _parse_revenue_with_outcome(client: SECClient, cik: str) -> tuple[str, dict | None]:
    """Returns (outcome, result) where outcome is 'no_report',
    'no_row_matched', or 'matched' -- the single fetch/parse path shared
    by parse_revenue() (simple callers, tests) and run() (which also
    needs the distinction for its per-outcome stats and the
    concept_parser_attempt log)."""
    found = find_income_statement_report(client, cik)
    if found is None:
        return "no_report", None
    report_url = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{found['filing']['accession_number'].replace('-', '')}/{found['report']['html_file']}"
    )
    resp = client.get(report_url)
    extracted = _extract_revenue_row(resp.text)
    if extracted is None:
        return "no_row_matched", None
    return "matched", {
        **extracted,
        "source_form": found["filing"]["form"],
        "source_accession": found["filing"]["accession_number"],
        "source_report": found["report"]["title"],
    }


def parse_revenue(client: SECClient, cik: str) -> dict | None:
    """Returns {'value': str, 'period_end': ..., 'source_form':...,
    'source_accession': ..., 'source_report': ...} or None (either no
    income-statement report exists for this filer, or none of its rows
    safely match REVENUE_LABEL_PATTERN). Read-only, no writes -- same
    contract as segment_revenue.py's own parse_segment_report."""
    _outcome, result = _parse_revenue_with_outcome(client, cik)
    return result


PARSER_NAME = "revenue_parser"
CONCEPT_NAME = "revenue"


def find_gap_companies(conn: psycopg.Connection, ciks: set[str] | None = None) -> list[tuple[int, str]]:
    """The real candidate population -- active companies genuinely
    missing `revenue` in analytics.canonical_fact AND not already
    attempted by this parser before (the efficiency this registry
    exists for: a rerun only ever looks at companies this parser has
    never tried, never re-fetches a filing it already read). Returns
    (company_id, cik) pairs. Read-only."""
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
    """Orchestration entry point, called by parsers/main_parser.py.
    Never writes into `revenue`'s own canonical_fact rows directly --
    a real, custom-tag revenue figure found this way is stored in the
    separate analytics.concept_parser_result registry (with full
    source_form/source_accession/source_report provenance, same
    discipline as segment_revenue.py) so a future reader can always
    trace it back to the exact rendered report, not just a bare number.
    Every outcome (matched or not) is also logged to
    analytics.concept_parser_attempt so a rerun never re-fetches a
    company this parser already tried."""
    stats = {"considered": 0, "ok": 0, "no_report": 0, "no_row_matched": 0, "errored": 0}
    candidates = find_gap_companies(conn, ciks)

    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (CONCEPT_NAME,))
        canonical_concept_id = cur.fetchone()[0]

    results = []
    with SECClient() as client:
        for company_id, cik in candidates:
            stats["considered"] += 1
            outcome = "errored"
            try:
                outcome, extracted = _parse_revenue_with_outcome(client, cik)
                stats[{"no_report": "no_report", "no_row_matched": "no_row_matched", "matched": "ok"}[outcome]] += 1
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
                    logger.info("revenue_parser.company_matched", cik=cik, **extracted)
            except Exception:
                logger.warning("revenue_parser.company_failed", cik=cik, exc_info=True)
                stats["errored"] += 1
                outcome = "errored"
                # A failed statement (e.g. the InvalidDatetimeFormat bug
                # found live 2026-09-05) leaves the connection in
                # "current transaction is aborted" state -- every later
                # cursor.execute on this same connection would fail too
                # without this rollback, cascading one bad row into the
                # whole rest of the batch. Same lesson as common/
                # errors.py's log_error() (mapper/CLAUDE.md).
                conn.rollback()

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

    logger.info("revenue_parser.done", **stats)
    return {"stats": stats, "results": results}
