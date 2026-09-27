"""Stage 3 -- Schedule 13D/13G beneficial ownership (doc 19). Reads the
golden company's own already-stored raw.sec_submissions payload for
form in ('SC 13D','SC 13D/A','SC 13G','SC 13G/A') -- same zero-new-discovery
mechanism as Stage 2 -- then downloads each filing's full-submission text
file and parses its SEC-HEADER block, NOT the free-text document body.

This is a real, verified design change from Stage 2's approach, not a
shortcut: checked live before writing this that unlike Form 4, Schedule
13D/13G has NEVER had a structured XML primary document -- every filing
from 1994 through the most recent (2024) checked is plain HTML/text.
There is, however, a machine-readable SGML header (<SEC-HEADER>, or
<IMS-HEADER> in pre-1997 filings -- same field names either way, confirmed
live back to a real 1995 filing) prepended to every full-submission .txt,
carrying SUBJECT COMPANY and FILED BY blocks with CENTRAL INDEX KEY for
each. That header is exactly what's needed to resolve the issuer-vs-filer
ambiguity a prior pass found (doc 19 Sec 1) -- reliably, for the entire
30-year history, without parsing any free-text filing body.

percent_of_class / shares_owned are NOT extracted this pass -- those live
only in the free-text body (Item 4/5 of the form), whose layout genuinely
varies across decades of filers and would need its own dedicated,
verified text-extraction pass. Left NULL rather than guessed, same
discipline as core.fact.is_authoritative/Screener's excluded_missing_data
-- a real, explicit follow-up, not silently skipped.

CUSIP IS extracted this pass (doc 19 Stage 4 prep, see
doc/learnings/form-13f-cusip-crosswalk.md) -- every Schedule 13D/13G cover
page carries a mandatory CUSIP field for the subject security, embedded in
this same full-submission .txt already fetched above (no new request).
Checked live against three real, differently-formatted AAPL filings before
writing the extraction regex, not assumed from one example: "037833100
(CUSIP Number)" (number before label, 2024 filing), "037833100
-------- (CUSIP Number)" (number before label with a dashed filler line,
2016 filing), and "CUSIP Number: 037833100" (number after label, a
different 2016 filer's template). All three are handled by searching a
window around the literal word "CUSIP" for a standalone 9-character
alphanumeric token, rather than anchoring to one exact label phrase.
"""

import json
import re
from datetime import date, datetime, timedelta

import psycopg
import structlog

from scrooner_pipeline.collector.storage import (
    SupabaseStorageClient,
    strip_bucket_prefix,
)
from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

FORMS = {"SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A"}

MIN_FILING_DATE = (date.today() - timedelta(days=365 * 3)).isoformat()  # explicit
# History-depth decision (2026-08-30), prompted directly: this module had NO
# recency bound at all, unlike insider.py's own 12-month MIN_FILING_DATE --
# checked live before picking a number: for every (company, filer)
# relationship in core.beneficial_ownership, 73% (38,861 of 53,067) have
# their MOST RECENT filing more than 3 years old -- almost certainly
# genuinely closed positions (the filer sold below 5%, nothing left to
# report), not stale-but-still-current ones. A 1-year bound (Form 4's own
# rule) was considered and rejected: unlike Form 4 (every transaction gets
# a filing) or Form 13F (mandatory every quarter regardless of change),
# Schedule 13G does NOT require an annual refile if nothing changed -- a
# genuinely stable, still-active >5% holder can legitimately go more than a
# year without a new filing. Only 1 of 53,067 relationships had a most-
# recent filing within the last year, which would make a 1-year bound
# actively wrong here, not just conservative. 3 years balances both real
# purposes this data serves: the CUSIP crosswalk only ever needs ONE valid
# CUSIP (stable for a company's life, any filing in the window works), and
# the >5%-holder disclosure itself wants "who currently holds this," which
# a 3-year window captures far more completely than 1 year would while
# still excluding the clear historical majority. Computed dynamically (not
# a hardcoded string), same reasoning as insider.py's own bound.

_SUBJECT_BLOCK_RE = re.compile(r"SUBJECT COMPANY:(.*?)FILED BY:", re.DOTALL)
_FILED_BY_BLOCK_RE = re.compile(
    r"FILED BY:(.*?)(?:FILED BY:|<DOCUMENT>|</(?:SEC|IMS)-HEADER>)", re.DOTALL
)
_NAME_RE = re.compile(r"COMPANY CONFORMED NAME:\s*(.+)")
_CIK_RE = re.compile(r"CENTRAL INDEX KEY:\s*(\d+)")
_FILED_DATE_RE = re.compile(r"FILED AS OF DATE:\s*(\d{8})")

_TAG_RE = re.compile(r"<[^>]+>")
_CUSIP_LABEL_RE = re.compile(r"CUSIP", re.IGNORECASE)
_CUSIP_TOKEN_RE = re.compile(r"\b[0-9A-Z]{9}\b")
# A real, recurring alternate format, found live 2026-09-15 investigating
# why real companies (ADT Inc./Apollo, Global Business Travel Group,
# among others) had a matched 13G filing but no extractable CUSIP: some
# filer templates typeset the CUSIP's own 6+2+1 character grouping with
# whitespace between the groups instead of writing it contiguously
# ("CUSIP No. 00090Q 10 3", "CUSIP No. 37890B 10 0") -- checked against
# two unrelated companies before trusting this as a real, common pattern
# rather than a one-off.
_CUSIP_SPACED_RE = re.compile(r"\b([0-9A-Z]{6})\s+([0-9A-Z]{2})\s+([0-9A-Z])\b")


def _extract_cusip(full_text: str) -> str | None:
    """Finds the cover-page CUSIP by searching a window around the first
    literal "CUSIP" mention for a standalone 9-character alphanumeric
    token, rather than anchoring to one exact label phrase -- real filings
    put the number before OR after the label, with varying separators
    (see module docstring for the three real formats this was checked
    against). Requires at least one digit in the candidate token so a
    stray 9-letter English word near "CUSIP" can't false-positive. Falls
    back to the spaced 6+2+1 grouping (_CUSIP_SPACED_RE) when no
    contiguous 9-character token is found in the same window."""
    clean = _TAG_RE.sub(" ", full_text)
    clean = re.sub(r"\s+", " ", clean)
    label_match = _CUSIP_LABEL_RE.search(clean)
    if label_match is None:
        return None
    window = clean[max(0, label_match.start() - 80) : label_match.end() + 80]
    for token in _CUSIP_TOKEN_RE.findall(window):
        if any(ch.isdigit() for ch in token):
            return token
    spaced_match = _CUSIP_SPACED_RE.search(window)
    if spaced_match:
        candidate = "".join(spaced_match.groups())
        if any(ch.isdigit() for ch in candidate):
            return candidate
    return None


def _parse_date_yyyymmdd(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y%m%d").date()


def _extract_company(block: str) -> tuple[str | None, str | None]:
    name_match = _NAME_RE.search(block)
    cik_match = _CIK_RE.search(block)
    name = name_match.group(1).strip() if name_match else None
    cik = cik_match.group(1) if cik_match else None
    return name, cik


def _parse_header(text: str) -> dict | None:
    subject_match = _SUBJECT_BLOCK_RE.search(text)
    filed_by_match = _FILED_BY_BLOCK_RE.search(text)
    if subject_match is None or filed_by_match is None:
        return None
    issuer_name, issuer_cik = _extract_company(subject_match.group(1))
    filer_name, filer_cik = _extract_company(filed_by_match.group(1))
    filed_date_match = _FILED_DATE_RE.search(text)
    return {
        "issuer_name": issuer_name,
        "issuer_cik": issuer_cik,
        "filer_name": filer_name,
        "filer_cik": filer_cik,
        "filed_date": _parse_date_yyyymmdd(
            filed_date_match.group(1) if filed_date_match else None
        ),
    }


def _load_schedule_filings(
    storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str
) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select storage_path
            from raw.sec_submissions
            where cik = %s
              and fetched_at = (select max(fetched_at) from raw.sec_submissions where cik = %s)
            order by storage_path
            """,
            (cik, cik),
        )
        storage_paths = [row[0] for row in cur.fetchall()]

    filings: list[dict] = []
    for storage_path in storage_paths:
        payload = json.loads(storage.download(strip_bucket_prefix(storage_path)))
        block = payload["filings"]["recent"] if "filings" in payload else payload
        for i, form in enumerate(block.get("form", [])):
            if form in FORMS and block["filingDate"][i] >= MIN_FILING_DATE:
                filings.append(
                    {
                        "form": form,
                        "accession_number": block["accessionNumber"][i],
                        "filing_date": block["filingDate"][i],
                    }
                )
    return filings


def update_beneficial_ownership_for_company(
    conn: psycopg.Connection, sec: SECClient, company_id: int, cik: str
) -> dict:
    with SupabaseStorageClient() as storage:
        filings = _load_schedule_filings(storage, conn, cik)

    rows: list[dict] = []
    stats = {
        "filings_considered": len(filings),
        "filings_parsed": 0,
        "issuer_mismatch": 0,
        "header_unparseable": 0,
    }
    for f in filings:
        acc_no_dash = f["accession_number"].replace("-", "")
        cik_int = str(int(cik))
        url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_dash}/{f['accession_number']}.txt"
        try:
            resp = sec.get(url)
        except Exception:
            logger.warning(
                "beneficial_ownership.fetch_failed",
                cik=cik,
                accession_number=f["accession_number"],
            )
            continue
        header = _parse_header(resp.text)
        if header is None:
            stats["header_unparseable"] += 1
            logger.warning(
                "beneficial_ownership.header_unparseable",
                cik=cik,
                accession_number=f["accession_number"],
            )
            continue
        # Require a confirmed issuer_cik match -- a header we couldn't
        # extract issuer_cik from is inconclusive, not a match, so it's
        # skipped the same as a genuine mismatch rather than accepted by
        # default (a missing field must never silently pass the check
        # this stage exists specifically to enforce).
        if not header["issuer_cik"] or header["issuer_cik"].lstrip("0") != cik.lstrip(
            "0"
        ):
            stats["issuer_mismatch"] += 1
            continue
        schedule_type = "13D" if f["form"].startswith("SC 13D") else "13G"
        stats["filings_parsed"] += 1
        cusip = _extract_cusip(resp.text)
        if cusip is None:
            stats["cusip_unparseable"] = stats.get("cusip_unparseable", 0) + 1
        rows.append(
            {
                "company_id": company_id,
                "accession_number": f["accession_number"],
                "schedule_type": schedule_type,
                "is_amendment": f["form"].endswith("/A"),
                "filer_name": header["filer_name"] or "unknown",
                "filer_cik": header["filer_cik"],
                "percent_of_class": None,
                "shares_owned": None,
                "cusip": cusip,
                "filing_date": header["filed_date"] or f["filing_date"],
            }
        )

    with conn.cursor() as cur:
        cur.execute(
            "delete from core.beneficial_ownership where company_id = %s", (company_id,)
        )
        if rows:
            # ON CONFLICT DO NOTHING (added 2026-08-28, same fix as
            # insider.py's identical issue): accession_number carries a
            # global `unique` constraint, but the per-company delete above
            # only protects against a duplicate within THIS company's own
            # rows -- a genuine cross-run duplicate would otherwise crash
            # the whole chunk with an uncaught UniqueViolation.
            cur.executemany(
                """
                insert into core.beneficial_ownership
                    (company_id, accession_number, schedule_type, is_amendment, filer_name,
                     filer_cik, percent_of_class, shares_owned, cusip, filing_date)
                values
                    (%(company_id)s, %(accession_number)s, %(schedule_type)s, %(is_amendment)s, %(filer_name)s,
                     %(filer_cik)s, %(percent_of_class)s, %(shares_owned)s, %(cusip)s, %(filing_date)s)
                on conflict (accession_number) do nothing
                """,
                rows,
            )
        conn.commit()
    logger.info("beneficial_ownership.company_done", cik=cik, **stats)
    return stats


PER_COMPANY_TIMEOUT_SECONDS = 1800  # same rationale and same value as
# insider.py's identical constant -- a company with a very large filing
# history can legitimately take a long time under SEC's rate limit; this
# only bounds the worst case so one company can't stall a chunk forever.


def _run_company_with_timeout(sec: "SECClient", company_id: int, cik: str) -> dict:
    """Same pattern as insider.py's identical helper, including the same
    fix (2026-08-28): a raw `threading.Thread(daemon=True)`, NOT
    `concurrent.futures.ThreadPoolExecutor` -- found live that
    ThreadPoolExecutor's worker threads are non-daemon by default, so
    Python won't let the process exit while an abandoned, still-blocked
    worker thread is alive, even though the logical timeout already fired
    and moved on. A daemon thread lets the interpreter exit immediately
    once the timeout elapses, regardless of what the abandoned thread is
    still doing."""
    import queue
    import threading

    from scrooner_pipeline.db.connection import get_connection

    result_queue: queue.Queue = queue.Queue(maxsize=1)

    def _work() -> None:
        try:
            with get_connection() as company_conn:
                result_queue.put(
                    (
                        "ok",
                        update_beneficial_ownership_for_company(
                            company_conn, sec, company_id, cik
                        ),
                    )
                )
        except Exception as exc:  # noqa: BLE001
            result_queue.put(("error", exc))

    thread = threading.Thread(target=_work, daemon=True)
    thread.start()
    thread.join(timeout=PER_COMPANY_TIMEOUT_SECONDS)
    if thread.is_alive():
        raise TimeoutError(f"company {cik} exceeded {PER_COMPANY_TIMEOUT_SECONDS}s")
    status, payload = result_queue.get_nowait()
    if status == "error":
        raise payload
    return payload


def update_beneficial_ownership(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "timed_out": 0,
        "stakes": 0,
    }
    with SECClient() as sec:
        for cik in sorted(ciks):
            totals["considered"] += 1
            company_id = company_id_by_cik.get(cik)
            if company_id is None:
                totals["no_company"] += 1
                continue
            try:
                stats = _run_company_with_timeout(sec, company_id, cik)
            except TimeoutError:
                logger.warning(
                    "beneficial_ownership.company_timed_out",
                    cik=cik,
                    timeout_seconds=PER_COMPANY_TIMEOUT_SECONDS,
                )
                totals["timed_out"] += 1
                continue
            except Exception:
                # Same lesson as insider.py: one company's failure must not
                # crash the whole chunk and cost every other company in it
                # their own progress on every retry. safe_rollback()
                # tolerates a dead connection (a real, recurring Supabase
                # pooler drop) instead of letting conn.rollback() itself
                # raise a second, uncaught OperationalError that crashes
                # this whole chunk -- found live 2026-09-15, same root
                # cause as concept_fallback.py's identical fix; see
                # common/errors.py's own docstring for the full history.
                logger.exception("beneficial_ownership.company_failed", cik=cik)
                conn = safe_rollback(conn, stage="beneficial_ownership", cik=cik)
                totals["errored"] += 1
                continue
            totals["ok"] += 1
            totals["stakes"] += stats["filings_parsed"]
    logger.info("beneficial_ownership.done", **totals)
    return totals
