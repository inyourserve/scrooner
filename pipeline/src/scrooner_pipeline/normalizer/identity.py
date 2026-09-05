"""Stage 2a -- Identity normalization (doc 09). Parses raw.sec_submissions
payloads into core.company, core.listing and core.filing. Read-only against
`raw`, writes only to `core` -- no new SEC network calls, this is purely a
transform over what the Collector already stored.

Company/ticker/exchange data comes from the submissions base file's own
tickers/exchanges arrays, not raw.company_universe -- verified live
2026-08-15 that submissions carries a richer, per-company-authoritative set
(e.g. Block/XYZ's OTC symbol BSQKZ, which company_tickers.json omits).

core.filing is deliberately restricted to the form types doc 03's MVP needs
-- see FORM_ALLOWLIST below. Everything else in a company's filing history
stays fully inspectable in raw.sec_submissions; this table just doesn't
duplicate all of it.
"""

import json
from datetime import date, datetime

import psycopg
import structlog

from scrooner_pipeline.collector.storage import SupabaseStorageClient, strip_bucket_prefix
from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()

# doc 03's MVP scope: 10-K/10-Q for US domestic filers. 20-F/40-F included
# because two golden companies (TSM, ENB) use them and doc 02's Day-7 note
# says identity/filing structure is fine to normalize for foreign filers --
# only their FACTS (Stage 2d) stay out of scope pending doc 02's open
# 20-F/40-F decision. Amendment variants included so is_amendment has
# something real to flag (ARCC's 10-K/A).
#
# 8-K added 2026-08-17 (doc 19, Stage 1) -- a deliberate, verified,
# purely-additive widening of this frozen module, not a boundary change:
# 8-K shares this exact table's shape (accession_number, form, filing_date,
# period_of_report) and this exact parsing code path, so recognizing it
# only adds new core.filing rows, never touches how any already-allowed
# form (10-K/10-Q/20-F/40-F) is parsed. Verified live: rerunning identity
# normalization after this change reproduced identical row counts for
# every pre-existing form type, only 8-K rows were new. See
# doc/learnings/ownership-and-8k-discovery.md.
#
# Form 15 family and SC 14D9 added 2026-08-17 (doc 23 Stages C/D) -- same
# purely-additive widening, same justification: both share this table's
# exact shape, and their mere presence in core.filing (form-type only, no
# document parsing) IS the whole signal doc 23 scoped -- a real,
# evidenced `delisted` status (Form 15/15F) and a tender-offer-target
# flag (SC 14D9), zero new fetches either way.
#
# DEF 14A family added 2026-08-18 (doc 26's coverage push) -- same
# purely-additive widening. Checked live against the full golden-10 first
# (not assumed): the real form-type variety present is {DEF 14A, DEFA14A,
# DEFM14A, DEFR14A, DFAN14A, PRE 14A, PREM14A, PX14A6G, PX14A6N}. Only the
# company's own DEFINITIVE proxy disclosure and its amendment/revision
# variants are included here (DEF 14A itself, plus DEFA14A "additional
# soliciting materials", DEFM14A "merger-related", DEFR14A "revised") --
# deliberately excluding PRE 14A/PREM14A (preliminary, not yet final, by
# definition superseded by the DEF that follows) and DFAN14A/PX14A6G/
# PX14A6N (third-party/activist/non-management exempt solicitations, not
# the company's own disclosure), same curated-not-exhaustive discipline
# as ITEM_LABELS/aliases.py elsewhere in this project. Only the filing's
# presence in core.filing is captured here -- Stage 5's actual document
# parsing (exec comp, insider holdings from the proxy's own tables)
# remains explicitly deferred, per doc 19.
FORM_ALLOWLIST = {
    "10-K", "10-K/A",
    "10-Q", "10-Q/A",
    "20-F", "20-F/A",
    "40-F", "40-F/A",
    "8-K", "8-K/A",
    "15-12G", "15-12G/A", "15-15D", "15-15D/A",
    "15F-12B", "15F-12B/A", "15F-12G", "15F-12G/A",
    "SC 14D9", "SC 14D9/A",
    "DEF 14A", "DEFA14A", "DEFM14A", "DEFR14A",
    # 144/424B5/FWP added 2026-08-29 (zero-new-fetch coverage pass) --
    # same purely-additive widening as everything else in this history.
    # Checked live against the full golden-10 first, not assumed: 144
    # (942 filings, 8/10 companies -- insider restricted-stock resale
    # notices, a Form-4-adjacent signal), 424B5 (182 filings, 6/10 --
    # prospectus supplements), FWP (23,042 filings, 10/10 -- free-writing
    # prospectuses, heavily dominated by JPM's structured-note/ETN
    # issuance program, the same "one CIK, many securities" pattern
    # pipeline/CLAUDE.md already documents for JPM's listings).
    "144", "424B5", "FWP",
}


def _latest_submission_files(conn: psycopg.Connection, cik: str) -> list[tuple[int, str]]:
    """(raw_id, storage_path) for every file (base + continuation pages) in
    the MOST RECENT fetch batch for this CIK -- base and continuations share
    one fetched_at, since collector/submissions.py fetches them together in
    a single run. Earlier batches stay in raw for history; this just picks
    the current snapshot to normalize from."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select id, storage_path
            from raw.sec_submissions
            where cik = %s
              and fetched_at = (select max(fetched_at) from raw.sec_submissions where cik = %s)
            order by storage_path
            """,
            (cik, cik),
        )
        return cur.fetchall()


def _load_json(storage: SupabaseStorageClient, storage_path: str) -> dict:
    raw_bytes = storage.download(strip_bucket_prefix(storage_path))
    return json.loads(raw_bytes)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_filings_block(block: dict) -> list[dict]:
    """`block` is either a base file's filings.recent dict or a continuation
    file's top-level dict -- both are the same shape: parallel arrays keyed
    by field name (verified live 2026-08-15 against AAPL's base file and its
    -submissions-001 continuation page). Zips them into one row per filing,
    dropping anything not in FORM_ALLOWLIST."""
    accession_numbers = block.get("accessionNumber", [])
    forms = block.get("form", [])
    filing_dates = block.get("filingDate", [])
    report_dates = block.get("reportDate", [])
    items = block.get("items", [])
    rows = []
    for i, accession_number in enumerate(accession_numbers):
        form = forms[i] if i < len(forms) else None
        if not accession_number or form not in FORM_ALLOWLIST:
            continue
        item_value = items[i] if i < len(items) else ""
        rows.append(
            {
                "accession_number": accession_number,
                "form": form,
                "filing_date": _parse_date(filing_dates[i] if i < len(filing_dates) else None),
                "period_of_report": _parse_date(report_dates[i] if i < len(report_dates) else None),
                "is_amendment": form.endswith("/A"),
                "items": item_value or None,
            }
        )
    return rows


def load_company_identity(storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str) -> dict | None:
    """Fetches and parses the current submissions snapshot for one CIK.
    Returns None if this CIK has no submissions data collected yet (nothing
    to normalize)."""
    files = _latest_submission_files(conn, cik)
    if not files:
        logger.warning("identity.no_submissions_for_cik", cik=cik)
        return None

    base_payload = None
    filings: list[dict] = []
    raw_submission_id_by_filing: list[tuple[dict, int]] = []
    for raw_id, storage_path in files:
        payload = _load_json(storage, storage_path)
        if "filings" in payload:
            # Base file: entity metadata + filings.recent, plus filings.files
            # pointing at continuation pages (already covered by `files`
            # above -- every row for this fetched_at came from the same
            # query, base and continuations alike).
            base_payload = payload
            block_filings = _parse_filings_block(payload["filings"]["recent"])
        else:
            # Continuation page: flat, same field shape as filings.recent.
            block_filings = _parse_filings_block(payload)
        for f in block_filings:
            raw_submission_id_by_filing.append((f, raw_id))
        filings.extend(block_filings)

    if base_payload is None:
        logger.warning("identity.no_base_file_for_cik", cik=cik, files_seen=len(files))
        return None

    tickers = base_payload.get("tickers", [])
    exchanges = base_payload.get("exchanges", [])
    listings = [
        {
            "ticker": ticker,
            "exchange": exchanges[i] if i < len(exchanges) else None,
        }
        for i, ticker in enumerate(tickers)
    ]

    return {
        "cik": cik,
        "company_name": base_payload["name"],
        "fiscal_year_end": base_payload.get("fiscalYearEnd"),
        "listings": listings,
        "filings": filings,
        "raw_submission_id_by_filing": raw_submission_id_by_filing,
    }


def upsert_company(conn: psycopg.Connection, cik: str, company_name: str, fiscal_year_end: str | None) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into core.company (cik, company_name, fiscal_year_end)
            values (%s, %s, %s)
            on conflict (cik) do update
                set company_name = excluded.company_name,
                    fiscal_year_end = excluded.fiscal_year_end
            returning id
            """,
            (cik, company_name, fiscal_year_end),
        )
        company_id = cur.fetchone()[0]
    conn.commit()
    return company_id


def upsert_listings(conn: psycopg.Connection, company_id: int, listings: list[dict]) -> int:
    if not listings:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            """
            insert into core.listing (company_id, ticker, exchange)
            values (%(company_id)s, %(ticker)s, %(exchange)s)
            on conflict (company_id, ticker) do update set exchange = excluded.exchange
            """,
            [{"company_id": company_id, **listing} for listing in listings],
        )
    conn.commit()
    return len(listings)


def upsert_filings(
    conn: psycopg.Connection,
    company_id: int,
    filings: list[dict],
    raw_submission_id_by_filing: list[tuple[dict, int]],
) -> int:
    if not filings:
        return 0
    raw_id_by_accession = {f["accession_number"]: raw_id for f, raw_id in raw_submission_id_by_filing}
    rows = [
        {
            "company_id": company_id,
            "accession_number": f["accession_number"],
            "form": f["form"],
            "filing_date": f["filing_date"],
            "period_of_report": f["period_of_report"],
            "is_amendment": f["is_amendment"],
            "items": f["items"],
            "raw_submission_id": raw_id_by_accession[f["accession_number"]],
        }
        for f in filings
    ]
    with conn.cursor() as cur:
        cur.executemany(
            """
            insert into core.filing
                (company_id, accession_number, form, filing_date, period_of_report,
                 is_amendment, items, raw_submission_id)
            values
                (%(company_id)s, %(accession_number)s, %(form)s, %(filing_date)s, %(period_of_report)s,
                 %(is_amendment)s, %(items)s, %(raw_submission_id)s)
            on conflict (accession_number) do update
                set filing_date      = excluded.filing_date,
                    period_of_report = excluded.period_of_report,
                    is_amendment     = excluded.is_amendment,
                    items            = excluded.items
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def normalize_identity_for_cik(storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str) -> dict:
    identity = load_company_identity(storage, conn, cik)
    if identity is None:
        return {"cik": cik, "status": "no_data"}

    company_id = upsert_company(conn, identity["cik"], identity["company_name"], identity["fiscal_year_end"])
    listing_count = upsert_listings(conn, company_id, identity["listings"])
    filing_count = upsert_filings(conn, company_id, identity["filings"], identity["raw_submission_id_by_filing"])

    logger.info(
        "identity.normalized",
        cik=cik,
        company_id=company_id,
        listings=listing_count,
        filings=filing_count,
    )
    return {
        "cik": cik,
        "status": "ok",
        "company_id": company_id,
        "listings": listing_count,
        "filings": filing_count,
    }


def normalize_identity(conn: psycopg.Connection, ciks: set[str]) -> dict:
    stats = {"considered": 0, "ok": 0, "no_data": 0, "errored": 0}
    with SupabaseStorageClient() as storage:
        for cik in sorted(ciks):
            stats["considered"] += 1
            try:
                result = normalize_identity_for_cik(storage, conn, cik)
                stats[result["status"]] += 1
            except Exception as exc:
                stats["errored"] += 1
                log_error(conn, "core.normalizer_error", cik, "identity", exc)
    logger.info("identity.normalize.done", **stats)
    return stats
