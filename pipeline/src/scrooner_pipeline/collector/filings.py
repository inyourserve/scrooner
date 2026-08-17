"""Module 5 -- Filing Metadata Collector (doc 06). Doc 08's Day 5 deliverable
(via jobs/incremental.py). Parses SEC's daily index (doc 07 section5:
https://www.sec.gov/Archives/edgar/daily-index/) for a single calendar date
and records what was filed that day into raw.sec_filing_documents --
metadata only (cik, accession_number, form, filing_date, source_url),
download_status='indexed'. Never fetches the filing body itself -- that's
module 6 (Filing Documents), explicitly out of doc 08's 7-day scope ("Do
not necessarily download every possible SEC attachment on Day 1").

Scope decision (stated explicitly, not silently assumed -- see doc 08 Day 5
row and doc/learnings/day-05-incremental-updates.md): the daily index
covers EVERY EDGAR filer -- issuers, funds, and individual insiders filing
Forms 3/4/5, Schedule 13D/G, etc. -- a much broader population than
companyfacts.zip/submissions.zip (which only cover XBRL-tagged reporting
companies). raw.company_universe is Scrooner's actual scope (US-listed
equities the Collector is responsible for), so this module filters daily
index rows to CIKs already known in raw.company_universe by default,
unless the caller passes an explicit `only_ciks` override (golden-set /
--ciks testing, same pattern as companyfacts.py/submissions.py). This is a
scope decision about WHICH ENTITIES the Collector tracks, not an
interpretation of filing CONTENT -- no form-type filtering happens here,
every form a tracked company files gets indexed, exactly as doc 06 module
5 describes ("maintains a structured index of what's collected"). Deciding
which form types matter for metrics is the Normalizer/Mapper's job.

raw.sec_filing_documents is upserted (not append-only, per doc 08's
schema) on (cik, accession_number) -- a filing is immutable once filed, so
"already indexed" is a single global fact, not something scoped to a
run_id/checkpoint the way the append-only companyfacts/submissions tables
are (Day 4's resume design). `ON CONFLICT ... DO NOTHING` is therefore
both the idempotency mechanism AND the definition of "genuinely new" for
this module: a row's insert either succeeds (new filing) or no-ops
(already known, from any prior run, any prior day). No separate
already-known lookup is needed before the insert -- the database is asked,
per row, not assumed from an application-level set.
"""

from datetime import date, datetime
from typing import Iterator

import httpx
import psycopg
import structlog

from scrooner_pipeline.collector.retry import HeartbeatTicker
from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

ARCHIVES_BASE = "https://www.sec.gov/Archives/"


def daily_index_url(for_date: date) -> str:
    """https://www.sec.gov/Archives/edgar/daily-index/{YYYY}/QTR{n}/master.{YYYYMMDD}.idx
    -- doc 07 section5's daily index, the incremental-update source. Verified
    live 2026-08-14: pipe-delimited, fixed 5-column layout (CIK|Company
    Name|Form Type|Date Filed|File Name), header block ends at a line of
    dashes."""
    quarter = (for_date.month - 1) // 3 + 1
    return f"{ARCHIVES_BASE}edgar/daily-index/{for_date.year}/QTR{quarter}/master.{for_date:%Y%m%d}.idx"


def parse_master_index(text: str) -> Iterator[dict]:
    """Yields one dict per filing row from a master.idx's body, skipping
    the fixed header block (description/last-data-received/comments/column
    header, ending at the dashed divider line). A line that doesn't split
    into exactly 5 pipe-delimited fields is logged and skipped, not
    silently dropped -- same discipline as companyfacts.py's
    unrecognized-member handling, in case SEC ever changes this format.
    """
    lines = text.splitlines()
    try:
        divider_idx = next(i for i, line in enumerate(lines) if line.startswith("---"))
    except StopIteration:
        logger.warning("daily_index.no_divider_found", first_lines=lines[:10])
        return
    for line in lines[divider_idx + 1 :]:
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) != 5:
            logger.warning("daily_index.unrecognized_row", line=line)
            continue
        cik_raw, company_name, form, date_filed, filename = parts
        try:
            cik = cik_raw.strip().zfill(10)
            filing_date = datetime.strptime(date_filed.strip(), "%Y%m%d").date()
        except ValueError:
            logger.warning("daily_index.unparseable_row", line=line)
            continue
        filename = filename.strip()
        accession_number = filename.rsplit("/", 1)[-1].removesuffix(".txt")
        yield {
            "cik": cik,
            "company_name": company_name.strip(),
            "form": form.strip(),
            "filing_date": filing_date,
            "accession_number": accession_number,
            "source_url": f"{ARCHIVES_BASE}{filename}",
        }


def fetch_daily_index(client: SECClient, for_date: date) -> list[dict] | None:
    """Returns parsed rows for `for_date`, or None if SEC published no
    index for that date at all (a 404 here means no filings that day --
    weekend/holiday -- not a Collector failure; doc 07 section3's retry policy
    already excludes 404 from the retry set, so this raises immediately on
    a real 404 rather than burning retry attempts on it)."""
    url = daily_index_url(for_date)
    try:
        response = client.get(url)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.info("daily_index.not_published", date=for_date.isoformat(), url=url)
            return None
        raise
    return list(parse_master_index(response.text))


def collect_daily_filings(
    conn: psycopg.Connection,
    for_date: date,
    run_id: int,
    only_ciks: set[str] | None = None,
) -> dict:
    """Fetches for_date's daily index, filters to only_ciks (the caller's
    responsibility to pass raw.company_universe's CIKs for a normal
    incremental run -- see module docstring), and upserts each matching row
    into raw.sec_filing_documents. `new` counts rows whose INSERT actually
    landed (genuinely new filing, never indexed before, from any run);
    `already_known` counts rows that matched an existing (cik,
    accession_number) and were correctly left untouched -- this is the
    directly testable "finds only genuinely new filings" signal doc 08
    asks for: running this same for_date twice must produce new=0 the
    second time.
    """
    stats = {"index_rows": 0, "considered": 0, "new": 0, "already_known": 0, "errors": 0}

    with SECClient() as sec:
        rows = fetch_daily_index(sec, for_date)

    if rows is None:
        stats["no_index_published"] = True
        logger.info("filings.daily.no_index", date=for_date.isoformat())
        return stats

    stats["index_rows"] = len(rows)
    heartbeat = HeartbeatTicker(conn, run_id)

    with conn.cursor() as cur:
        for row in rows:
            if only_ciks is not None and row["cik"] not in only_ciks:
                continue
            stats["considered"] += 1
            try:
                cur.execute(
                    """
                    insert into raw.sec_filing_documents
                        (cik, accession_number, form, filing_date, source_url, download_status, collected_at)
                    values (%s, %s, %s, %s, %s, 'indexed', now())
                    on conflict (cik, accession_number) do nothing
                    returning cik
                    """,
                    (row["cik"], row["accession_number"], row["form"], row["filing_date"], row["source_url"]),
                )
                inserted = cur.fetchone() is not None
                conn.commit()
                if inserted:
                    stats["new"] += 1
                else:
                    stats["already_known"] += 1
                heartbeat.tick()
            except Exception as exc:
                conn.rollback()
                stats["errors"] += 1
                logger.exception(
                    "filings.store_failed", cik=row["cik"], accession_number=row["accession_number"]
                )
                cur.execute(
                    """
                    insert into raw.collector_errors
                        (run_id, cik, source, error_type, message)
                    values (%s, %s, %s, %s, %s)
                    """,
                    (run_id, row["cik"], "filings", type(exc).__name__, str(exc)[:2000]),
                )
                conn.commit()
    heartbeat.flush()
    logger.info("filings.daily.done", date=for_date.isoformat(), **stats)
    return stats
