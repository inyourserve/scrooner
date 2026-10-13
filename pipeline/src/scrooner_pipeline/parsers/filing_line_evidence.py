"""Per-company evidence: does a concept's LINE appear on the face of the company's
latest 10-K/10-Q balance sheet or income statement? (2026-10-13)

Why: the concept coverage score divides every concept by all ~4,815 real operating
companies, as if each should report every line. Inventory is absent for 92% of
Financials because a bank has none, not because we failed to extract it, but our own
data cannot say which: defining "applies to you" as "you have a value" is circular
(it would read 100%), and 87% of absent cells in the 22 lowest concepts carried no
recorded reason. The independent evidence is the filing itself.

Method: read the filing's rendered statements (FilingSummary.xml -> R*.htm, the same
source the revenue / cost-of-revenue parsers use) and test row labels per concept.
Stored per (company, concept) with the accession it came from, so every claim is
traceable to a document. coverage_matrix.apply_filing_line_evidence() turns the
evidence into gap reasons; coverage_snapshot.py uses them for denominators.

What it can and cannot say (measured, doc/learnings/2026-10-13-applicability-probe-...):
  * A line absent from the face is EVIDENCE, not proof, that it does not apply: a
    company can disclose it only in the notes. Of companies where we HAVE a value,
    14-34% show no face line. The stored fact is "not shown on the statements".
  * A COMBINED line ("Accounts payable and accrued expenses") means the plain concept
    is not presented on its own; mapping the combined total as the plain concept
    would be the project's known "different concept sharing vocabulary" mistake, so
    it is recorded as combined, not as a missing plain line.
  * line_present is NULL when the statement itself could not be located: no evidence
    either way, never guessed.

Incremental: a company is re-read only when its latest 10-K/10-Q accession differs
from the stored one. Each company is its own transaction; one failure never stops the
batch. Reads nothing from yfinance. SEC requests go through the shared rate limiter
(3 per company: FilingSummary + balance sheet + income statement).
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass

import httpx
import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.parsers.revenue_parser import (
    _CELL,
    _ROW,
    INCOME_STATEMENT_TITLE_PATTERN,
    PARENTHETICAL_SUFFIX_PATTERN,
    _cell_text,
)
from scrooner_pipeline.segments.segment_revenue import _filing_summary_reports

logger = structlog.get_logger()

STAGE = "filing_line_evidence"

BALANCE_SHEET_TITLE = re.compile(
    r"balance\s+sheets?|statements?\s+of\s+(consolidated\s+)?financial\s+(condition|position)"
    r"|statements?\s+of\s+(net\s+)?assets",
    re.IGNORECASE,
)
EARNINGS_TITLE = re.compile(
    r"statements?\s+of\s+(consolidated\s+)?(earnings|profit|comprehensive\s+(income|loss))"
    r"|\bincome\s+statements?\b",
    re.IGNORECASE,
)
# Rendered reports embed a hidden "- Definition ..." popup row under many line items;
# those are documentation, not statement lines (Apple's phantom "goodwill" match).
_DEFINITION_ROW = re.compile(r"^\s*-\s*(definition|details?)\b", re.IGNORECASE)
# A matched label that also names accruals / other items / prepaids is a combined line.
_COMBINED = re.compile(r"\b(accrued|other|prepaid)\b", re.IGNORECASE)


@dataclass(frozen=True)
class LineSpec:
    concept: str
    statement: str  # 'BS' or 'IS'
    pattern: re.Pattern
    # Whether a combined line is a real possibility for this concept.
    check_combined: bool = False


SPECS: tuple[LineSpec, ...] = (
    LineSpec("inventory", "BS", re.compile(r"\binventor(y|ies)\b", re.I)),
    LineSpec(
        "accounts_receivable",
        "BS",
        re.compile(
            r"(account|trade|customer)s?\s*(and\s+[\w\s]+?)?receivable|^\s*receivables?\b",
            re.I,
        ),
        check_combined=True,
    ),
    LineSpec(
        "accounts_payable",
        "BS",
        re.compile(
            r"(account|trade)s?\s*(and\s+[\w\s]+?)?payable|^\s*payables?\b", re.I
        ),
        check_combined=True,
    ),
    LineSpec("goodwill", "BS", re.compile(r"\bgoodwill\b", re.I)),
    LineSpec(
        "cost_of_revenue",
        "IS",
        re.compile(
            r"\bcosts?\s+of\s+(net\s+)?(revenues?|sales|goods|products?|services|operations)\b",
            re.I,
        ),
    ),
    LineSpec(
        "gross_profit", "IS", re.compile(r"\bgross\s+(profit|margin|income)\b", re.I)
    ),
    LineSpec(
        "research_and_development",
        "IS",
        re.compile(
            r"research\s*(and|&)\s*development|product\s+development|technology\s+and\s+development",
            re.I,
        ),
    ),
    LineSpec(
        "interest_income",
        "IS",
        re.compile(
            r"interest\s+(income|and\s+(dividend|other|investment)\s+income)|investment\s+income|interest\s+and\s+other\s+income",
            re.I,
        ),
        check_combined=True,
    ),
    LineSpec(
        "operating_expenses",
        "IS",
        re.compile(
            r"total\s+(operating\s+)?(costs?\s+and\s+)?expenses|total\s+operating\s+costs|operating\s+expenses,?\s+total",
            re.I,
        ),
    ),
)
SPEC_BY_CONCEPT = {s.concept: s for s in SPECS}


def extract_labels(html: str) -> list[str]:
    """First-cell text of every statement row, minus hidden definition popups."""
    labels = []
    for _cls, inner in _ROW.findall(html):
        cells = _CELL.findall(inner)
        if not cells:
            continue
        text = _cell_text(cells[0]).strip()
        if text and not _DEFINITION_ROW.search(text):
            labels.append(text)
    return labels


def classify_labels(spec: LineSpec, labels: list[str]) -> tuple[bool, str | None, bool]:
    """(line_present, matched_label, combined) for one concept over a statement's labels.
    A plain match wins over a combined one; only combined matches -> combined=True."""
    matches = [label for label in labels if spec.pattern.search(label)]
    if not matches:
        return False, None, False
    if spec.check_combined:
        plain = [m for m in matches if not _COMBINED.search(m)]
        if plain:
            return True, plain[0], False
        return True, matches[0], True
    return True, matches[0], False


def _pick_report(
    reports: list[dict], pattern: re.Pattern, extra: re.Pattern | None = None
) -> dict | None:
    for report in reports:
        if PARENTHETICAL_SUFFIX_PATTERN.search(report["title"]):
            continue
        if pattern.search(report["title"]) or (extra and extra.search(report["title"])):
            return report
    return None


def _statement_labels(client: SECClient, url: str) -> list[str] | None:
    """Row labels of one rendered statement; None (statement not located) on a 404."""
    try:
        return extract_labels(client.get(url).text)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return None
        raise


def read_filing(client: SECClient, cik: str, accession: str) -> list[dict] | None:
    """Evidence rows for one filing, or None if it has no FilingSummary reports."""
    try:
        reports = _filing_summary_reports(client, int(cik), accession)
    except httpx.HTTPStatusError as exc:
        # Filings without rendered statements (pre-XBRL, e.g. a dormant company's last
        # 10-K from 2006) have no FilingSummary.xml: "no evidence", not a failure.
        if exc.response.status_code == 404:
            return None
        raise
    if not reports:
        return None
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"
    balance_sheet = _pick_report(reports, BALANCE_SHEET_TITLE)
    income_statement = _pick_report(
        reports, INCOME_STATEMENT_TITLE_PATTERN, EARNINGS_TITLE
    )
    labels: dict[str, list[str] | None] = {"BS": None, "IS": None}
    if balance_sheet:
        labels["BS"] = _statement_labels(client, base + balance_sheet["html_file"])
    if income_statement:
        labels["IS"] = _statement_labels(client, base + income_statement["html_file"])
    rows = []
    for spec in SPECS:
        statement_labels = labels[spec.statement]
        if statement_labels is None:  # statement not located: no evidence either way
            rows.append(no_evidence_row(spec))
            continue
        present, label, combined = classify_labels(spec, statement_labels)
        rows.append(
            {
                "data_point": spec.concept,
                "statement": spec.statement,
                "line_present": present,
                "matched_label": label,
                "combined": combined,
            }
        )
    return rows


def no_evidence_row(spec: LineSpec) -> dict:
    return {
        "data_point": spec.concept,
        "statement": spec.statement,
        "line_present": None,
        "matched_label": None,
        "combined": False,
    }


def find_targets(
    conn: psycopg.Connection, ciks: set[str] | None, force: bool
) -> list[tuple[int, str, str, str]]:
    """(company_id, cik, accession, form) of each active company whose latest
    10-K/10-Q differs from the accession its stored evidence was read from."""
    with conn.cursor() as cur:
        cur.execute("set local statement_timeout = '100s'")
        cur.execute(
            """
            with latest as (
                select distinct on (f.company_id) f.company_id, f.accession_number, f.form
                from core.filing f
                join core.company c on c.id = f.company_id
                where c.status = 'active' and f.form in ('10-K', '10-Q')
                order by f.company_id, f.filing_date desc, f.id desc
            ),
            stored as (
                select company_id, max(accession_number) as accession_number
                from analytics.company_filing_line_evidence
                group by company_id
            )
            select l.company_id, c.cik, l.accession_number, l.form
            from latest l
            join core.company c on c.id = l.company_id
            left join stored s on s.company_id = l.company_id
            where (%(force)s or s.accession_number is distinct from l.accession_number)
              and (%(ciks)s::text[] is null or c.cik = any(%(ciks)s))
            order by c.cik
            """,
            {"force": force, "ciks": sorted(ciks) if ciks else None},
        )
        return cur.fetchall()


def store_evidence(
    conn: psycopg.Connection,
    company_id: int,
    accession: str,
    form: str,
    rows: list[dict],
) -> None:
    """Replace this company's evidence in one transaction (delete-then-insert scoped
    to the company, so a rerun can never leave a stale mixture of two filings)."""
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.company_filing_line_evidence where company_id = %s",
            (company_id,),
        )
        cur.executemany(
            """
            insert into analytics.company_filing_line_evidence
                (company_id, data_point, statement, line_present, matched_label, combined, accession_number, form)
            values (%(company_id)s, %(data_point)s, %(statement)s, %(line_present)s, %(matched_label)s,
                    %(combined)s, %(accession)s, %(form)s)
            """,
            [
                {**r, "company_id": company_id, "accession": accession, "form": form}
                for r in rows
            ],
        )
    conn.commit()


def run(
    conn: psycopg.Connection,
    ciks: set[str] | None = None,
    limit: int | None = None,
    max_seconds: float | None = None,
    force: bool = False,
) -> dict:
    targets = find_targets(conn, ciks, force)
    if limit:
        targets = targets[:limit]
    stats = {
        "targets": len(targets),
        "probed": 0,
        "no_reports": 0,
        "errored": 0,
        "stopped_by_time_limit": 0,
    }
    started = time.monotonic()
    with SECClient() as client:
        for company_id, cik, accession, form in targets:
            if max_seconds is not None and time.monotonic() - started > max_seconds:
                stats["stopped_by_time_limit"] = 1
                break
            try:
                rows = read_filing(client, cik, accession)
                if rows is None:
                    # No rendered reports at all: store "no evidence" for this
                    # accession so it is not re-fetched every run.
                    stats["no_reports"] += 1
                    rows = [no_evidence_row(spec) for spec in SPECS]
                else:
                    stats["probed"] += 1
                store_evidence(conn, company_id, accession, form, rows)
            except (
                Exception
            ) as exc:  # one company's fetch/parse failure must not stop the batch
                stats["errored"] += 1
                log_error(conn, "analytics.mapper_error", cik, STAGE, exc)
                conn = safe_rollback(conn, stage=STAGE, cik=cik)
            if (stats["probed"] + stats["no_reports"] + stats["errored"]) % 100 == 0:
                logger.info("filing_line_evidence.progress", **stats)
    logger.info("filing_line_evidence.done", **stats)
    return stats
