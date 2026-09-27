"""Revenue by business segment (doc 37, built 2026-08-31 per direct user
request: "build this for 10 companies first" -- the golden-10, as a real
first production build, not just doc 37's/build_segment_report_index.py's
research-only index).

Fetch pattern reused from scripts/build_segment_report_index.py (already
verified live 2026-08-28/30 against 100 real companies): find the single
most recent 10-Q or 10-K, read its FilingSummary.xml, find the report
whose title matches a segment/disaggregated-revenue pattern. Per doc 38's
case-1 reasoning, only the single most recent filing is fetched -- these
"Details" reports already contain multiple comparison periods in one
table (confirmed on Apple's own report below: 3-months and 9-months
columns, current and year-ago), so no backfill is needed.

What's genuinely new here (not in the research script): actually parsing
the report's HTML table into (segment, concept, period, value) rows, not
just recording which report to look at.

Real table structure, checked live 2026-08-31 on Apple's own
"Segment Information - Information by Reportable Segment (Details)"
report (R46.htm) before writing this parser, not assumed:
  - Two header <tr> rows: the first groups columns by period TYPE (e.g.
    "3 Months Ended" spanning 2 columns), the second gives each column's
    actual end date.
  - A <tr class="rh"> row marks the start of each segment's block, its
    label cell's onclick handler carrying the real XBRL dimension member
    (e.g. `defref_us-gaap_StatementBusinessSegmentsAxis=aapl_AmericasSegmentMember`,
    display text "Americas | Operating segments" -- the segment name is
    the text before " | Operating segments").
  - Within a segment's block, each line-item row's onclick handler
    carries the real XBRL concept (e.g.
    `defref_us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax`
    for "Net sales") -- concept name, not display label, is what
    _is_revenue_concept matches against, since display labels vary by
    company ("Net sales" vs "Revenues" vs "Total revenue") while the
    revenue concept is drawn from a small, well-known XBRL tag set.
  - Values are parenthesized for a subtraction/expense line (e.g. "Cost
    of sales" as "(21,507)") -- parsed as negative, though revenue rows
    themselves are never parenthesized in any company checked.

Regex-based parsing, not an HTML parser library -- matches this
project's existing style in business_text.py/build_segment_report_index.py
for the same real-but-narrow "just this one anchor-consistent site's
markup" shape, not a general-purpose HTML document."""

import html
import re

import psycopg
import structlog

from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

SEGMENT_TITLE_PATTERN = re.compile(
    r"segment|disaggregat|revenue.*(geographic|by region|by product|by category)",
    re.IGNORECASE,
)
SCAFFOLDING_SUFFIX_PATTERN = re.compile(r"\((Tables|Policies)\)\s*$", re.IGNORECASE)

# The real, small set of XBRL concepts this project has found companies
# use for a segment's top-line revenue figure -- checked live across the
# golden-10 while building this (see the per-company notes in the
# accompanying learnings doc for which company uses which tag).
# Checked live 2026-08-31 against the golden-10's real reports: Apple/
# Alphabet use StatementBusinessSegmentsAxis; Nike uses SubsegmentsAxis
# for its geographic segments AND ProductOrServiceAxis for a separate
# product-category breakdown (footwear/apparel/equipment) in the SAME
# report; Reddit uses ProductOrServiceAxis for revenue-by-source
# (advertising/other). Deliberately NOT matching ConsolidationItemsAxis
# (Apple's own "Corporate non-segment"/generic "Operating segments"
# subtotal rows use this) -- those are reconciliation totals, not named
# segments, and including them would double-count revenue already
# captured under the real segment names.
_SEGMENT_AXIS = re.compile(
    r"StatementBusinessSegmentsAxis|StatementGeographicalAxis|SubsegmentsAxis|ProductOrServiceAxis"
)

REVENUE_CONCEPT_PATTERNS = re.compile(
    r"RevenueFromContractWithCustomerExcludingAssessedTax"
    r"|RevenueFromContractWithCustomerIncludingAssessedTax"
    r"|Revenues\b"
    r"|InterestAndDividendIncomeOperating"
    r"|InterestIncomeExpenseNet",
    re.IGNORECASE,
)

_ROW = re.compile(r"<tr(?:[^>]*class=\"([^\"]*)\")?[^>]*>(.*?)</tr>", re.DOTALL)
_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL)
_CELL_WITH_COLSPAN = re.compile(r"<t[dh]([^>]*)>(.*?)</t[dh]>", re.DOTALL)
_COLSPAN_ATTR = re.compile(r'colspan="(\d+)"')
_ONCLICK_REF = re.compile(r"Show\.showAR\(\s*this,\s*'([^']+)'", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")


def _cell_text(raw_cell: str) -> str:
    plain = _WHITESPACE.sub(" ", _TAG.sub(" ", raw_cell)).strip()
    return html.unescape(plain)


def _parse_value(text: str) -> str | None:
    """Returns a Decimal-safe string, or None for an empty/non-numeric
    cell -- never a float, per this project's Decimal-as-string
    discipline at every boundary."""
    cleaned = text.replace("$", "").replace(",", "").replace("\xa0", "").strip()
    if not cleaned or cleaned in ("—", "-"):
        return None
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    if negative:
        cleaned = cleaned[1:-1]
    if not re.fullmatch(r"-?\d+(\.\d+)?", cleaned):
        return None
    return f"-{cleaned}" if negative and not cleaned.startswith("-") else cleaned


def _latest_10q_or_10k(client: SECClient, cik: str) -> dict | None:
    padded = cik.zfill(10)
    data = client.get_json(f"https://data.sec.gov/submissions/CIK{padded}.json")
    recent = data["filings"]["recent"]
    best = None
    for i, form in enumerate(recent["form"]):
        if form not in ("10-Q", "10-K"):
            continue
        filing_date = recent["filingDate"][i]
        if best is None or filing_date > best["filing_date"]:
            best = {"form": form, "filing_date": filing_date, "accession_number": recent["accessionNumber"][i]}
    return best


def _filing_summary_reports(client: SECClient, cik_int: int, accession_number: str) -> list[dict]:
    accession_nodash = accession_number.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_nodash}/"
    response = client.get(base + "FilingSummary.xml")
    reports = []
    for match in re.finditer(r"<Report[^>]*>.*?</Report>", response.text, re.S):
        block = match.group(0)
        html_name = re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", block)
        short_name = re.search(r"<ShortName>(.*?)</ShortName>", block)
        if html_name and short_name:
            reports.append({"html_file": html_name.group(1), "title": short_name.group(1).strip()})
    return reports


# Real title patterns checked live 2026-08-31 across the golden-10 while
# building this discovery step -- a strict substring match ("by
# reportable segment") missed most real companies outright:
#   Apple:     "...Information by Reportable Segment (Details)"
#   Alphabet:  "Revenues - Revenue by Segment (Details)"
#   Nike:      "REVENUES - Schedule of Disaggregation of Revenue (Details)"
#   Reddit:    "Revenue - Disaggregation of Revenue by Source (Details)"
#   JPMorgan:  "Business Segments & Corporate (Details)" -- no "revenue"
#              in the title at all, real bug found live: a looser
#              fallback filter picked "Loans - By Portfolio Segment
#              (Details)" instead, a real but WRONG report (loan
#              categories, not business-segment revenue) -- excluding
#              known off-topic triggers (loan/goodwill/unearned/
#              narrative/additional information) fixes this.
#   Microsoft: "Segment Revenue, Cost of Revenue, Operating Expenses and
#              Operating Income (Detail)" -- SINGULAR "(Detail)", not
#              "(Details)" -- a literal-substring check for the plural
#              form missed Microsoft entirely; real bug found live.
_DETAILS_SUFFIX = re.compile(r"\(Details?\)\s*$", re.IGNORECASE)
# \bloan\b (singular only) was a real bug: JPMorgan's off-topic report
# is titled "Loans" (plural), which \bloan\b does NOT match -- the
# trailing "s" is itself a word character, so no word boundary exists
# between "loan" and "s". \bloans?\b covers both. "reconciliation" added
# after the same JPM/Reddit-style false-positive pattern recurred: a
# report reconciling segment net income to a consolidated total uses
# different line items (an income bridge) than a clean revenue-by-
# segment table, even though its title also contains "segment"/"revenue".
_OFF_TOPIC_TITLE = re.compile(
    r"\bloans?\b|\bgoodwill\b|\bunearned\b|\bnarrative\b|additional information|reconciliation",
    re.IGNORECASE,
)


def _score_segment_report_title(title: str) -> int:
    score = 0
    if re.search(r"\brevenue\b", title, re.IGNORECASE):
        score += 2
    if re.search(r"\bsegment\b", title, re.IGNORECASE):
        score += 1
    return score


def find_segment_report(client: SECClient, cik: str) -> dict | None:
    """Returns {'filing': {...}, 'report': {...}} for the best candidate
    "Details"/"Detail" (tabular, not narrative) report, or None if no
    10-Q/10-K or no matching report exists. Ranks candidates by
    _score_segment_report_title rather than taking the first match in
    FilingSummary.xml's own (arbitrary) order."""
    filing = _latest_10q_or_10k(client, cik)
    if filing is None:
        return None
    reports = _filing_summary_reports(client, int(cik), filing["accession_number"])
    candidates = [
        r
        for r in reports
        if SEGMENT_TITLE_PATTERN.search(r["title"])
        and not SCAFFOLDING_SUFFIX_PATTERN.search(r["title"])
        and _DETAILS_SUFFIX.search(r["title"])
        and not _OFF_TOPIC_TITLE.search(r["title"])
    ]
    if not candidates:
        return None
    best = max(candidates, key=lambda r: _score_segment_report_title(r["title"]))
    return {"filing": filing, "report": best}


def parse_segment_report(html: str) -> list[dict]:
    """Parses one R*.htm report into a flat list of
    {segment, concept_ref, period_type, period_end, value} dicts, keeping
    only revenue-concept rows (see REVENUE_CONCEPT_PATTERNS) -- this
    module stores revenue by segment, not every line item in the
    reconciliation table."""
    rows = _ROW.findall(html)
    if len(rows) < 2:
        return []

    # Header: row 0 groups by period type (each header cell's own
    # colspan tells us how many date columns it covers), row 1 gives
    # each column's actual end date. _CELL_WITH_COLSPAN captures the
    # opening tag's colspan alongside its text in one pass, in document
    # order -- more robust than re-searching for a cell's text back in
    # the row (which risks a false match if two header cells share a
    # text prefix, e.g. two "3 Months Ended" groups).
    header_cells_with_span = _CELL_WITH_COLSPAN.findall(rows[0][1])
    period_types: list[str] = []
    for attrs, raw_cell in header_cells_with_span[1:]:  # skip the corner label cell
        text = _cell_text(raw_cell)
        if not text:
            continue
        colspan_match = _COLSPAN_ATTR.search(attrs)
        span = int(colspan_match.group(1)) if colspan_match else 1
        period_types.extend([text] * span)

    date_cells = [_cell_text(c) for c in _CELL.findall(rows[1][1])]
    if not date_cells:
        return []
    while len(period_types) < len(date_cells):
        period_types.append(period_types[-1] if period_types else "")

    results: list[dict] = []
    current_segment: str | None = None

    for row_class, row_html in rows[2:]:
        cells = _CELL.findall(row_html)
        if not cells:
            continue
        label_cell_html = cells[0]
        onclick_match = _ONCLICK_REF.search(label_cell_html)
        concept_ref = onclick_match.group(1) if onclick_match else ""
        label_text = _cell_text(label_cell_html)

        if _SEGMENT_AXIS.search(concept_ref):
            current_segment = label_text.split("|")[0].strip()
            continue

        if current_segment is None:
            continue
        if not REVENUE_CONCEPT_PATTERNS.search(concept_ref):
            continue

        value_cells = [_cell_text(c) for c in cells[1:]]
        for i, raw_value in enumerate(value_cells):
            if i >= len(date_cells):
                break
            value = _parse_value(raw_value)
            if value is None:
                continue
            results.append(
                {
                    "segment": current_segment,
                    "concept_ref": concept_ref,
                    "period_type": period_types[i] if i < len(period_types) else "",
                    "period_end": date_cells[i],
                    "value": value,
                }
            )
    return results


def update_segment_revenue(conn: psycopg.Connection, ciks: set[str]) -> dict:
    stats = {"considered": 0, "ok": 0, "no_report": 0, "no_rows_parsed": 0, "errored": 0, "rows_written": 0}
    with conn.cursor() as cur:
        cur.execute("select id, cik from core.company where cik = any(%s)", (list(ciks),))
        company_rows = cur.fetchall()

    with SECClient() as client:
        for company_id, cik in company_rows:
            stats["considered"] += 1
            try:
                found = find_segment_report(client, cik)
                if found is None:
                    stats["no_report"] += 1
                    continue
                report_url = (
                    f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                    f"{found['filing']['accession_number'].replace('-', '')}/{found['report']['html_file']}"
                )
                resp = client.get(report_url)
                parsed_rows = parse_segment_report(resp.text)
                if not parsed_rows:
                    stats["no_rows_parsed"] += 1
                    continue

                with conn.cursor() as cur:
                    cur.execute(
                        "delete from core.segment_revenue where company_id = %s and source_accession = %s",
                        (company_id, found["filing"]["accession_number"]),
                    )
                    cur.executemany(
                        """
                        insert into core.segment_revenue
                            (company_id, segment_name, concept_ref, period_type, period_end,
                             value, source_form, source_accession, source_report)
                        values
                            (%(company_id)s, %(segment)s, %(concept_ref)s, %(period_type)s, %(period_end)s,
                             %(value)s, %(source_form)s, %(source_accession)s, %(source_report)s)
                        """,
                        [
                            {
                                **r,
                                "company_id": company_id,
                                "source_form": found["filing"]["form"],
                                "source_accession": found["filing"]["accession_number"],
                                "source_report": found["report"]["title"],
                            }
                            for r in parsed_rows
                        ],
                    )
                conn.commit()
                stats["ok"] += 1
                stats["rows_written"] += len(parsed_rows)
                logger.info(
                    "segment_revenue.company_done",
                    cik=cik,
                    segments=len({r["segment"] for r in parsed_rows}),
                    rows=len(parsed_rows),
                )
            except Exception:
                logger.warning("segment_revenue.company_failed", cik=cik, exc_info=True)
                stats["errored"] += 1
                # safe_rollback() tolerates a dead connection (a real,
                # recurring Supabase pooler drop) instead of a bare
                # conn.rollback() itself raising and crashing the whole
                # remaining batch -- see common/errors.py.
                conn = safe_rollback(conn, stage="segment_revenue", cik=cik)

    logger.info("segment_revenue.done", **stats)
    return stats
