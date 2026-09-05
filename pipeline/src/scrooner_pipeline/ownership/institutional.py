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

Scoped to the two most-recent bulk windows (doc `insider_info.md`'s
Institutional Ownership spec needs a QoQ comparison, not just a single
snapshot -- see ownership/institutional_summary.py, which computes that
comparison from the two report_periods this module now stores) and to
golden-company CUSIP matches only, not the full ~6M-row SEC universe --
storing that would blow the Supabase free-tier budget the same way an
unscoped Normalizer/Mapper backfill would have (doc 09's live-measured
capacity check). A wider multi-quarter trend (3+ windows) is a real
future follow-on, not this pass.
"""

import csv
import hashlib
import io
import re
import zipfile
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import psycopg
import structlog

from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

# Name-based fallback matching (added 2026-09-05). 1,461 of 5,216 active
# companies have never had a Schedule 13D/13G filed against them, so the
# CUSIP crosswalk below never learns their CUSIP and can never match
# their real Form 13F holdings -- even though those holdings exist in the
# bulk data under the company's true CUSIP. INFOTABLE.tsv's own
# NAMEOFISSUER field (read below, previously discarded) gives a second,
# independent way in. Piloted live before building: normalizing both
# sides (uppercase, strip legal-entity suffixes/punctuation) and matching
# only when a normalized name maps to exactly one company (never a
# fuzzy/best-guess match) produced ZERO collisions across all 1,461
# uncovered companies and matched 814 of them from a single bulk window
# see doc/learnings/2026-09-05-institutional-ownership-name-fallback.md.
# Deliberately curated, not exhaustive -- same "curated over fuzzy"
# discipline as ai_query/aliases.py.
_NAME_SUFFIX_RE = re.compile(
    r"\b(INCORPORATED|INC|CORPORATION|CORP|COMPANY|CO|LIMITED|LTD|LLC|LP|L P|PLC|"
    r"HOLDINGS?|GROUP|TRUST|CLASS [A-Z]|CL [A-Z]|COMMON STOCK|COMMON SHARES|"
    r"COM NEW|COM NPV|SHARES?|STOCK|DEL|NEW)\b"
)
_NAME_PUNCT_RE = re.compile(r"[.,\-'&/]")


def normalize_issuer_name(name: str) -> str:
    """Uppercase, strip punctuation and common legal-entity/share-class
    suffixes, collapse whitespace -- deliberately conservative (only
    removes tokens that add no identifying signal), not a general fuzzy
    matcher. Used on BOTH core.company.company_name and Form 13F's
    NAMEOFISSUER so the same transformation applies to both sides."""
    n = name.upper()
    n = _NAME_PUNCT_RE.sub(" ", n)
    n = _NAME_SUFFIX_RE.sub(" ", n)
    return re.sub(r"\s+", " ", n).strip()

# SEC publishes Form 13F bulk data sets on a rolling ~3-month-window basis
# (verified live 2026-08-17 against
# https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets --
# this is the latest window published as of that date; the prior window's
# URL was independently confirmed live/downloadable 2026-08-25 before
# adding it here). Update by hand when a newer window is published, until
# this becomes a recurring job (Part 14/Infra -- not built yet, see doc
# 20). Ordered latest-first; institutional_summary.py's "two most recent
# report_periods actually present for a company" logic doesn't depend on
# this list's order, but keeping it latest-first here matches how it
# reads.
# Found live 2026-08-31: an unbatched executemany over a full-population
# matched set (2.35M+ rows) drops the pooled connection mid-write. 5,000
# is a conservative round-trip size, not tuned against a real failure
# threshold -- safe headroom over "works," not the maximum that would.
INSERT_BATCH_SIZE = 5000
# Deletes scan more of the table per company_id than a plain insert
# round-trip does -- a smaller batch keeps each one comfortably inside
# the connection's statement_timeout even under concurrent load.
DELETE_BATCH_SIZE = 500

BULK_ZIP_WINDOWS: list[tuple[str, str]] = [
    (
        "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip",
        "01mar2026-31may2026",
    ),
    (
        "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01dec2025-28feb2026_form13f.zip",
        "01dec2025-28feb2026",
    ),
]


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


def _load_company_name_lookup(conn: psycopg.Connection, covered_company_ids: set[int]) -> dict[str, int]:
    """normalize_issuer_name(company_name) -> company_id, restricted to
    active companies NOT already covered by a CUSIP (the fallback only
    ever fills a gap CUSIP matching left open, never competes with it)
    and to normalized names that map to exactly ONE company -- a
    collision (two companies normalizing to the same name) means the
    fallback can't disambiguate, so BOTH are dropped from the lookup
    entirely rather than guessing. Verified live 2026-09-05: zero
    collisions across all 1,461 uncovered companies, but this still
    checks live rather than assuming that holds forever as new companies
    are added."""
    with conn.cursor() as cur:
        cur.execute("select id, company_name from core.company where status = 'active'")
        rows = cur.fetchall()

    name_to_ids: dict[str, list[int]] = {}
    for company_id, company_name in rows:
        if company_id in covered_company_ids:
            continue
        norm = normalize_issuer_name(company_name)
        if not norm:
            continue
        name_to_ids.setdefault(norm, []).append(company_id)

    collisions = {name: ids for name, ids in name_to_ids.items() if len(ids) > 1}
    if collisions:
        logger.warning("institutional_ownership.name_lookup_collisions", count=len(collisions))
    return {name: ids[0] for name, ids in name_to_ids.items() if len(ids) == 1}


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
    name_to_company: dict[str, int] | None = None,
) -> tuple[list[dict], int]:
    """Streams INFOTABLE.tsv (~396MB uncompressed) row by row rather than
    loading it wholesale -- only rows whose CUSIP (or, failing that, a
    normalized NAMEOFISSUER match -- see normalize_issuer_name's own
    docstring) matches a tracked company are ever held in memory. PUTCALL
    rows are excluded (a derivative position on the security, not an
    actual share holding); SSHPRNAMTTYPE is required to be 'SH' (shares),
    not 'PRN' (principal amount, for debt-like instruments) -- both
    checked live against a real sample before writing this filter, not
    assumed.

    VALUE is actual dollars, not thousands -- despite the field's name and
    the field-layout spec PDF's "(x$1000)" description, SEC's own bundled
    FORM13F_readme.htm (shipped inside every bulk zip) confirms this
    changed 2023-01-03. This entire bulk data set (a single 2026 window)
    postdates that change, so it's never ambiguous here -- see
    core.institutional_ownership.value_usd's column comment."""
    matched: list[dict] = []
    total_rows = 0
    name_to_company = name_to_company or {}
    for row in _load_tsv_dict(zf, "INFOTABLE.tsv"):
        total_rows += 1
        cusip = row["CUSIP"].strip()
        company_id = cusip_to_company.get(cusip)
        match_method = "cusip"
        if company_id is None and name_to_company:
            company_id = name_to_company.get(normalize_issuer_name(row["NAMEOFISSUER"]))
            match_method = "name"
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
                "match_method": match_method,
            }
        )
    return matched, total_rows


def _process_window(
    conn: psycopg.Connection,
    sec: SECClient,
    cusip_to_company: dict[str, int],
    url: str,
    label: str,
    name_to_company: dict[str, int] | None = None,
) -> dict:
    """Fetch + match one bulk window and write its rows, scoped so this
    window's rerun can never clobber another window's already-written
    rows for the same company -- the delete below is scoped by BOTH
    company_id AND source_zip, not company_id alone, the exact
    shared-table dimension-scoping trap pipeline/CLAUDE.md documents from
    Mapper Day 6 (there: roic/roe sharing a metric_definition_id; here:
    two windows sharing a company_id)."""
    zip_path = sec.get_cached_bulk_zip(url, f"form13f-{label}")
    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()

    with zipfile.ZipFile(zip_path) as zf:
        submission_lookup = _load_submission_lookup(zf)
        filer_name_lookup = _load_filer_name_lookup(zf)
        matched_rows, infotable_row_count = _match_infotable(
            zf, cusip_to_company, submission_lookup, filer_name_lookup, name_to_company
        )

    company_ids = sorted({r["company_id"] for r in matched_rows})
    with conn.cursor() as cur:
        # Batched, not one delete over the whole company_ids array: the
        # name-based fallback above widens this from a CUSIP-only set
        # (~2,500 companies) to potentially the full active population,
        # and a single unbounded delete hit the connection's 2-minute
        # statement_timeout live 2026-09-05. Same "bounded round-trips,
        # not one unbounded one" fix already applied to the INSERT below
        # for the same reason (2026-08-31) -- this table grows past the
        # point a single unindexed-in-practice-at-this-width delete can
        # finish in one shot.
        for i in range(0, len(company_ids), DELETE_BATCH_SIZE):
            batch = company_ids[i : i + DELETE_BATCH_SIZE]
            cur.execute(
                "delete from core.institutional_ownership where company_id = any(%s) and source_zip = %s",
                (batch, label),
            )
        if matched_rows:
            # Batched, not one executemany over the whole set: found live
            # 2026-08-31 that a single executemany over the full
            # full-population matched set (2.35M rows for just this one
            # window, up from golden-10's few thousand) drops the pooled
            # connection mid-write ("SSL connection has been closed
            # unexpectedly") -- Supabase's session pooler doesn't sustain
            # one unbounded network round-trip at that size. Chunking
            # keeps this a single delete-then-reinsert PASS (same cursor,
            # same transaction, same correctness property the module
            # docstring requires) while keeping each individual
            # round-trip small enough to actually complete.
            rows_with_zip = [{**r, "source_zip": label} for r in matched_rows]
            for i in range(0, len(rows_with_zip), INSERT_BATCH_SIZE):
                cur.executemany(
                    """
                    insert into core.institutional_ownership
                        (company_id, accession_number, infotable_sk, filer_name, filer_cik,
                         shares, value_usd, report_period, filing_date, is_amendment, source_zip, match_method)
                    values
                        (%(company_id)s, %(accession_number)s, %(infotable_sk)s, %(filer_name)s, %(filer_cik)s,
                         %(shares)s, %(value_usd)s, %(report_period)s, %(filing_date)s, %(is_amendment)s, %(source_zip)s,
                         %(match_method)s)
                    on conflict (accession_number, infotable_sk) do nothing
                    """,
                    rows_with_zip[i : i + INSERT_BATCH_SIZE],
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
            (url, label, sha256, infotable_row_count, len(matched_rows)),
        )
        conn.commit()

    return {
        "matched_rows": len(matched_rows),
        "companies": len(company_ids),
        "infotable_row_count": infotable_row_count,
    }


def update_institutional_ownership(conn: psycopg.Connection) -> dict:
    cusip_to_company = _load_golden_cusips(conn)
    if not cusip_to_company:
        logger.warning("institutional_ownership.no_cusips")
        return {"matched_rows": 0, "companies": 0, "infotable_row_count": 0, "windows": {}}

    # Name-based fallback (2026-09-05) -- fills the gap for companies with
    # no Schedule 13D/13G on file at all, so the CUSIP crosswalk above
    # never learns their CUSIP. Restricted to companies not already
    # covered by a CUSIP; see _load_company_name_lookup's own docstring.
    name_to_company = _load_company_name_lookup(conn, covered_company_ids=set(cusip_to_company.values()))
    logger.info("institutional_ownership.name_fallback_lookup", unambiguous_names=len(name_to_company))

    window_stats: dict[str, dict] = {}
    with SECClient() as sec:
        for url, label in BULK_ZIP_WINDOWS:
            window_stats[label] = _process_window(conn, sec, cusip_to_company, url, label, name_to_company)
            logger.info("institutional_ownership.window_done", window_label=label, **window_stats[label])

    # "companies" means "distinct companies matched in ANY window" --
    # queried straight from what's actually stored rather than unioned
    # from each window's own company_ids, so this number can never drift
    # from the real table contents.
    with conn.cursor() as cur:
        cur.execute("select count(distinct company_id) from core.institutional_ownership")
        companies = cur.fetchone()[0]

    stats = {
        "matched_rows": sum(w["matched_rows"] for w in window_stats.values()),
        "companies": companies,
        "infotable_row_count": sum(w["infotable_row_count"] for w in window_stats.values()),
        "windows": window_stats,
        "window_labels": [label for _url, label in BULK_ZIP_WINDOWS],
    }
    logger.info("institutional_ownership.done", **{k: v for k, v in stats.items() if k != "windows"})
    return stats
