"""Fetch + extract + store employee headcount (4 most recent 10-Ks) and
About text (latest 10-K only) per company. See business_text.py for the
extraction logic and doc/scoping/39_Scrooner_Employee_Headcount_Full_Coverage_Plan.md
for why this scope (annual-only, no LLM tier yet).

4 periods, not 2 (widened 2026-08-31 per direct user request for more
history): still annual-only, not quarterly -- confirmed live that a
10-Q does NOT repeat the Human Capital section (Apple's own 10-Q body
has zero headcount mention across 3 checked quarters), so "4 periods"
means 4 years via 4 10-Ks, not 4 quarters. No genuine quarterly
employee-count data exists in SEC filings at all; this is a real
source-cadence ceiling, not an engineering choice.

Genuinely new fetch: unlike identity.py/contact_details.py, this reads
each 10-K's *primary document body* (the actual filing text), not the
already-stored submissions.json metadata -- confirmed live 2026-08-30
that raw.sec_filing_documents has 10-K rows but every storage_path is
empty (indexed, never fetched)."""

import psycopg
import structlog

from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.company_master.business_text import (
    clean_visible_text,
    extract_about_text,
    extract_employee_headcount,
    extract_website,
)

logger = structlog.get_logger()


def _recent_10ks(client: SECClient, cik: str, limit: int = 2) -> list[dict]:
    padded = cik.zfill(10)
    data = client.get_json(f"https://data.sec.gov/submissions/CIK{padded}.json")
    recent = data["filings"]["recent"]
    results = []
    for i, form in enumerate(recent["form"]):
        if form == "10-K":
            results.append(
                {
                    "accession_number": recent["accessionNumber"][i],
                    "primary_document": recent["primaryDocument"][i],
                    "filing_date": recent["filingDate"][i],
                    "report_date": recent.get(
                        "reportDate", [None] * len(recent["form"])
                    )[i]
                    or None,
                }
            )
            if len(results) >= limit:
                break
    return results


def _document_url(cik: str, accession_number: str, primary_document: str) -> str:
    acc_no_dashes = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_dashes}/{primary_document}"


def process_company(
    client: SECClient, conn: psycopg.Connection, company_id: int, cik: str
) -> dict:
    stats = {
        "headcount_found": 0,
        "headcount_skipped_duplicate": 0,
        "about_found": False,
        "website_found": False,
    }
    filings = _recent_10ks(client, cik, limit=4)
    if not filings:
        return stats

    with conn.cursor() as cur:
        for i, filing in enumerate(filings):
            url = _document_url(
                cik, filing["accession_number"], filing["primary_document"]
            )
            resp = client.get(url)
            plain = clean_visible_text(resp.text)

            headcount = extract_employee_headcount(plain)
            if headcount is not None:
                cur.execute(
                    """
                    insert into core.employee_headcount_disclosure
                        (company_id, filing_date, report_date, headcount, is_approximate,
                         source_form, source_accession, source_snippet)
                    values (%s, %s, %s, %s, %s, '10-K', %s, %s)
                    on conflict (company_id, source_accession) do update
                        set headcount = excluded.headcount,
                            is_approximate = excluded.is_approximate,
                            source_snippet = excluded.source_snippet,
                            extracted_at = now()
                    """,
                    (
                        company_id,
                        filing["filing_date"],
                        filing["report_date"],
                        headcount["headcount"],
                        headcount["is_approximate"],
                        filing["accession_number"],
                        headcount["snippet"],
                    ),
                )
                stats["headcount_found"] += 1

            if i == 0:
                about = extract_about_text(plain)
                if about is not None:
                    cur.execute(
                        """
                        update core.company
                           set about_text = %s, about_text_source_accession = %s
                         where id = %s
                        """,
                        (about, filing["accession_number"], company_id),
                    )
                    stats["about_found"] = True

                website = extract_website(plain)
                if website is not None:
                    cur.execute(
                        "update core.company set website = %s where id = %s",
                        (website, company_id),
                    )
                    stats["website_found"] = True
    conn.commit()
    return stats


def process_companies(conn: psycopg.Connection, ciks: set[str]) -> dict:
    totals = {
        "considered": 0,
        "ok": 0,
        "no_filings": 0,
        "errored": 0,
        "headcount_rows": 0,
        "about_rows": 0,
        "website_rows": 0,
    }
    client = SECClient()
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik from core.company where cik = any(%s)", (list(ciks),)
        )
        rows = cur.fetchall()

    for company_id, cik in rows:
        totals["considered"] += 1
        try:
            stats = process_company(client, conn, company_id, cik)
            if stats["headcount_found"] == 0 and not stats["about_found"]:
                totals["no_filings"] += 1
            totals["ok"] += 1
            totals["headcount_rows"] += stats["headcount_found"]
            totals["about_rows"] += int(stats["about_found"])
            totals["website_rows"] += int(stats["website_found"])
        except Exception:
            logger.warning("employee_headcount.company_failed", cik=cik, exc_info=True)
            totals["errored"] += 1
            # safe_rollback() tolerates a dead connection (a real,
            # recurring Supabase pooler drop) instead of a bare
            # conn.rollback() itself raising and crashing the whole
            # remaining batch -- see common/errors.py.
            conn = safe_rollback(conn, stage="employee_headcount", cik=cik)

    logger.info("employee_headcount.done", **totals)
    return totals
