"""Stage 4 -- Form 13F institutional ownership (doc 19 Sec 5). The
CUSIP<->CIK crosswalk problem this stage was originally deferred behind is
resolved without any external vendor -- see
doc/learnings/form-13f-cusip-crosswalk.md for the live investigation.
Short version: Schedule 13D/13G cover pages carry a mandatory CUSIP field
for the subject security, and ownership/beneficial_ownership.py (Stage 3)
already fetches and now parses that exact document (0010 migration adds
the column). No new fetch is needed to learn a golden company's own
CUSIP; it comes straight from data this project already has.

What IS a genuinely new fetch: SEC's own bulk Form 13F data sets
(SUBMISSION/COVERPAGE/INFOTABLE flat files, all institutional managers,
~100MB per ~3-month filing window as of 2026-08-17) -- 13F is filed
*about* holdings by managers, not *by* the issuer, so it can never appear
in a golden company's own raw.sec_submissions the way every other form
type in doc 19 could. Confirmed live against SEC's own official spec PDF
(https://www.sec.gov/files/form_13f.pdf) before writing this: INFOTABLE
has CUSIP + NAMEOFISSUER but never an issuer CIK, and SUBMISSION.CIK is
explicitly the *filer* (manager), not the issuer -- matching happens by
CUSIP equality, nothing else.

Scoped to a single, most-recent bulk window (a snapshot, not a
multi-quarter trend) and to golden-company CUSIP matches only, not the
full ~6M-row SEC universe -- storing that would blow the Supabase
free-tier budget the same way an unscoped Normalizer/Mapper backfill
would have (doc 09's live-measured capacity check). A multi-quarter
ownership trend is a real future follow-on, not this pass.
"""

import csv
import hashlib
import io
import zipfile
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import psycopg
import structlog

from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

# SEC publishes Form 13F bulk data sets on a rolling ~3-month-window basis
# (verified live 2026-08-17 against
# https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets --
# this is the latest window published as of that date). Update by hand
# when a newer window is published, until this becomes a recurring job
# (Part 14/Infra -- not built yet, see doc 20).
BULK_ZIP_URL = "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip"
BULK_ZIP_WINDOW_LABEL = "01mar2026-31may2026"


def _parse_sec_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d-%b-%Y").date()
    except ValueError:
        return None


def _decimal(value: str) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _load_golden_cusips(conn: psycopg.Connection) -> dict[str, int]:
    """CUSIP -> company_id, sourced from core.beneficial_ownership.cusip
    (Stage 3's own capture -- see that module). A company can legitimately
    have more than one CUSIP on file across old/amended filings; every
    distinct pair found is used as a match key rather than assuming
    exactly one."""
    with conn.cursor() as cur:
        cur.execute("select distinct cusip, company_id from core.beneficial_ownership where cusip is not null")
        return dict(cur.fetchall())


def _load_tsv_dict(zf: zipfile.ZipFile, name: str) -> csv.DictReader:
    return csv.DictReader(io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace"), delimiter="\t")


def _load_submission_lookup(zf: zipfile.ZipFile) -> dict[str, dict]:
    """accession_number -> {filer_cik, report_period, filing_date}. Loaded
    fully into memory up front (SUBMISSION.tsv is ~0.7MB) rather than
    re-scanned per INFOTABLE row -- same "load lookups up front, don't
    query/scan per candidate" discipline as every other batch job in this
    pipeline (see pipeline/CLAUDE.md)."""
    lookup: dict[str, dict] = {}
    for row in _load_tsv_dict(zf, "SUBMISSION.tsv"):
        lookup[row["ACCESSION_NUMBER"]] = {
            "filer_cik": row["CIK"],
            "report_period": _parse_sec_date(row["PERIODOFREPORT"]),
            "filing_date": _parse_sec_date(row["FILING_DATE"]),
            # 404 of 11,761 submissions in the 2026-03..05 window are
            # amendments (checked live) -- an amendment can appear
            # alongside its original in the same bulk window, producing a
            # near-duplicate-looking row for the same manager/quarter.
            # Flagged, not filtered out, same "never silently drop, always
            # flag" discipline as beneficial_ownership.py's is_amendment.
            "is_amendment": row["SUBMISSIONTYPE"].endswith("/A"),
        }
    return lookup


def _load_filer_name_lookup(zf: zipfile.ZipFile) -> dict[str, str]:
    """accession_number -> filing manager name, from COVERPAGE.tsv (~2MB)."""
    lookup: dict[str, str] = {}
    for row in _load_tsv_dict(zf, "COVERPAGE.tsv"):
        lookup[row["ACCESSION_NUMBER"]] = row["FILINGMANAGER_NAME"]
    return lookup


def _match_infotable(
    zf: zipfile.ZipFile,
    cusip_to_company: dict[str, int],
    submission_lookup: dict[str, dict],
    filer_name_lookup: dict[str, str],
) -> tuple[list[dict], int]:
    """Streams INFOTABLE.tsv (~396MB uncompressed) row by row rather than
    loading it wholesale -- only rows whose CUSIP matches a golden
    company are ever held in memory. PUTCALL rows are excluded (a
    derivative position on the security, not an actual share holding);
    SSHPRNAMTTYPE is required to be 'SH' (shares), not 'PRN' (principal
    amount, for debt-like instruments) -- both checked live against a
    real sample before writing this filter, not assumed.

    VALUE is actual dollars, not thousands -- despite the field's name and
    the field-layout spec PDF's "(x$1000)" description, SEC's own bundled
    FORM13F_readme.htm (shipped inside every bulk zip) confirms this
    changed 2023-01-03. This entire bulk data set (a single 2026 window)
    postdates that change, so it's never ambiguous here -- see
    core.institutional_ownership.value_usd's column comment."""
    matched: list[dict] = []
    total_rows = 0
    for row in _load_tsv_dict(zf, "INFOTABLE.tsv"):
        total_rows += 1
        cusip = row["CUSIP"].strip()
        company_id = cusip_to_company.get(cusip)
        if company_id is None:
            continue
        if row.get("PUTCALL", "").strip():
            continue
        if row.get("SSHPRNAMTTYPE", "").strip() != "SH":
            continue
        accession_number = row["ACCESSION_NUMBER"]
        submission = submission_lookup.get(accession_number, {})
        matched.append(
            {
                "company_id": company_id,
                "accession_number": accession_number,
                "infotable_sk": int(row["INFOTABLE_SK"]),
                "filer_name": filer_name_lookup.get(accession_number, "unknown"),
                "filer_cik": submission.get("filer_cik"),
                "shares": _decimal(row["SSHPRNAMT"]),
                "value_usd": _decimal(row["VALUE"]),
                "report_period": submission.get("report_period"),
                "filing_date": submission.get("filing_date"),
                "is_amendment": submission.get("is_amendment", False),
            }
        )
    return matched, total_rows


def update_institutional_ownership(conn: psycopg.Connection) -> dict:
    cusip_to_company = _load_golden_cusips(conn)
    if not cusip_to_company:
        logger.warning("institutional_ownership.no_cusips")
        return {"matched_rows": 0, "companies": 0, "infotable_row_count": 0}

    with SECClient() as sec:
        zip_path = sec.get_cached_bulk_zip(BULK_ZIP_URL, f"form13f-{BULK_ZIP_WINDOW_LABEL}")

    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()

    with zipfile.ZipFile(zip_path) as zf:
        submission_lookup = _load_submission_lookup(zf)
        filer_name_lookup = _load_filer_name_lookup(zf)
        matched_rows, infotable_row_count = _match_infotable(zf, cusip_to_company, submission_lookup, filer_name_lookup)

    company_ids = sorted({r["company_id"] for r in matched_rows})
    with conn.cursor() as cur:
        if company_ids:
            cur.execute(
                "delete from core.institutional_ownership where company_id = any(%s)",
                (company_ids,),
            )
        if matched_rows:
            cur.executemany(
                """
                insert into core.institutional_ownership
                    (company_id, accession_number, infotable_sk, filer_name, filer_cik,
                     shares, value_usd, report_period, filing_date, is_amendment, source_zip)
                values
                    (%(company_id)s, %(accession_number)s, %(infotable_sk)s, %(filer_name)s, %(filer_cik)s,
                     %(shares)s, %(value_usd)s, %(report_period)s, %(filing_date)s, %(is_amendment)s, %(source_zip)s)
                on conflict (accession_number, infotable_sk) do nothing
                """,
                [{**r, "source_zip": BULK_ZIP_WINDOW_LABEL} for r in matched_rows],
            )
        cur.execute(
            """
            insert into raw.sec_13f_bulk_fetch
                (source_url, window_label, sha256, infotable_row_count, matched_row_count)
            values (%s, %s, %s, %s, %s)
            on conflict (window_label) do update set
                sha256 = excluded.sha256,
                infotable_row_count = excluded.infotable_row_count,
                matched_row_count = excluded.matched_row_count,
                fetched_at = now()
            """,
            (BULK_ZIP_URL, BULK_ZIP_WINDOW_LABEL, sha256, infotable_row_count, len(matched_rows)),
        )
        conn.commit()

    stats = {
        "matched_rows": len(matched_rows),
        "companies": len(company_ids),
        "infotable_row_count": infotable_row_count,
        "window_label": BULK_ZIP_WINDOW_LABEL,
    }
    logger.info("institutional_ownership.done", **stats)
    return stats
