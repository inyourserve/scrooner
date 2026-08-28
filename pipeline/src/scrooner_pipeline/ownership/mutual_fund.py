"""Mutual fund / ETF holdings via SEC Form N-PORT bulk data set (doc 21
Sec 1). Structurally a near-copy of ownership/institutional.py (Stage 4,
Form 13F) -- same CUSIP-matching mechanism, same "single most-recent
window, golden-company-CUSIP-matched only" scoping discipline, same
delete-then-reinsert write pattern. The crosswalk problem is identical
and already solved: FUND_REPORTED_HOLDING.ISSUER_CUSIP matches directly
against core.beneficial_ownership.cusip (doc 19 Stage 3/4's own capture),
no new crosswalk needed.

What's genuinely different from 13F, confirmed live 2026-08-28 against
the real bulk zip (https://www.sec.gov/files/dera/data/form-n-port-data-
sets/2026q2_nport.zip, 420MB, matching doc 21's own live check) before
writing any parsing code -- doc 21's own description undersold or missed
several real details:

1. SUBMISSION.tsv has NO cik column at all (unlike Form 13F's
   SUBMISSION.tsv). The filer's CIK lives on REGISTRANT.tsv instead
   (REGISTRANT.CIK, keyed by the same ACCESSION_NUMBER) -- doc 21's own
   phrasing ("REGISTRANT/SUBMISSION (fund identity, including the
   registrant's own CIK)") reads as if either table could supply it;
   only REGISTRANT actually can.
2. REGISTRANT.REGISTRANT_NAME is the umbrella trust that files (e.g.
   "MFS SERIES TRUST X"), not the specific named fund an investor would
   recognize -- that lives on a 4th table doc 21 didn't name,
   FUND_REPORTED_INFO (primary key ACCESSION_NUMBER, one row per
   filing), in SERIES_NAME/SERIES_ID. Using REGISTRANT_NAME alone would
   have produced a real ownership table where every row from the same
   trust shows an identical, unhelpful fund name. fund_name here prefers
   SERIES_NAME, falling back to REGISTRANT_NAME only on the rare filing
   with no series row.
3. FUND_REPORTED_HOLDING mixes real equity ownership with derivatives,
   short positions, debt, and other instrument types in one table --
   checked live against the full 14,080 raw golden-10 CUSIP matches
   before choosing a filter: ASSET_CAT == "EC" (Equity - Common, per
   nport_readme.htm's own field-layout table) and PAYOFF_PROFILE ==
   "Long" together account for 13,871 of those 14,080 rows and exclude
   every derivative-category ("DE", always DERIVATIVE_CAT="SWP" in the
   real sample) and every short position -- the same "only real share
   ownership, not derivative/short exposure" line 13F draws with its own
   PUTCALL/SSHPRNAMTTYPE filter, just against N-PORT's different field
   names. UNIT was 100% "NS" (Number of Shares) on every row this filter
   keeps -- checked, not assumed.
4. CURRENCY_VALUE is NOT always USD, unlike Form 13F's VALUE (confirmed
   post-2023-convention USD-only in institutional.py's own docstring).
   ~2% of real golden-10 matches (CAD, TWD) are reported in the fund's
   own filing currency, each with an EXCHANGE_RATE field alongside --
   but that field's multiply-vs-divide convention was not independently
   confirmed against a second source, so no conversion is attempted.
   value_usd is populated only when currency_code == "USD" (a direct
   passthrough); currency_value/currency_code are always stored raw so
   nothing is lost. Same "leave null, never guess" discipline this
   project already applied once to Form 13F's own VALUE field (see
   institutional.py's docstring on the $242T incident) -- applied here
   pre-emptively rather than after a wrong number ships.
5. N-PORT is disseminated quarterly but each individual filing reports
   ONE fund's holdings as of ONE month-end (Form N-PORT is a monthly
   report); REPORT_ENDING_PERIOD in the real data spans well outside any
   single calendar quarter for exactly this reason. A fund can
   legitimately appear more than once in a single quarterly bulk file
   (different months). This is not deduplicated here -- each
   (accession_number, holding_id) row is kept and traces to its own
   filing, same "never silently collapse, let the consumer choose"
   precedent institutional.py already sets for amendments.
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

# Verified live 2026-08-28 against
# https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets
# -- this is the latest quarterly window published as of that date (doc 21
# found the same file, 2026-08-17; it had not rolled to a newer quarter in
# the 11 days since). Update by hand when a newer window is published,
# same "not yet a recurring job" note as institutional.py's own
# BULK_ZIP_URL.
BULK_ZIP_URL = "https://www.sec.gov/files/dera/data/form-n-port-data-sets/2026q2_nport.zip"
BULK_ZIP_WINDOW_LABEL = "2026q2"

# Equity-Common, long positions only -- excludes debt, derivatives (the
# "DE" asset category, always carrying a populated DERIVATIVE_CAT in the
# real data), and short positions. See module docstring point 3.
_REAL_OWNERSHIP_ASSET_CAT = "EC"
_REAL_OWNERSHIP_PAYOFF_PROFILE = "Long"


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
    (doc 19 Stage 3's own capture) -- the identical lookup
    institutional.py already uses, not a second implementation."""
    with conn.cursor() as cur:
        cur.execute("select distinct cusip, company_id from core.beneficial_ownership where cusip is not null")
        return dict(cur.fetchall())


def _load_tsv_dict(zf: zipfile.ZipFile, name: str) -> csv.DictReader:
    return csv.DictReader(io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace"), delimiter="\t")


def _load_submission_lookup(zf: zipfile.ZipFile) -> dict[str, dict]:
    """accession_number -> {report_period, filing_date, is_amendment}.
    Loaded fully into memory up front (SUBMISSION.tsv is ~1MB) -- same
    "load lookups up front, never scan per candidate row" discipline as
    institutional.py and every other batch job in this pipeline. No CIK
    here -- see module docstring point 1; that lives on REGISTRANT.tsv."""
    lookup: dict[str, dict] = {}
    for row in _load_tsv_dict(zf, "SUBMISSION.tsv"):
        lookup[row["ACCESSION_NUMBER"]] = {
            "report_period": _parse_sec_date(row["REPORT_ENDING_PERIOD"]),
            "filing_date": _parse_sec_date(row["FILING_DATE"]),
            "is_amendment": row["SUB_TYPE"].endswith("/A"),
        }
    return lookup


def _load_registrant_lookup(zf: zipfile.ZipFile) -> dict[str, dict]:
    """accession_number -> {fund_cik, registrant_name}, from
    REGISTRANT.tsv (~2MB). REGISTRANT_NAME is the umbrella trust, used
    only as a fallback -- see module docstring point 2."""
    lookup: dict[str, dict] = {}
    for row in _load_tsv_dict(zf, "REGISTRANT.tsv"):
        lookup[row["ACCESSION_NUMBER"]] = {
            "fund_cik": row["CIK"],
            "registrant_name": row["REGISTRANT_NAME"],
        }
    return lookup


def _load_fund_series_lookup(zf: zipfile.ZipFile) -> dict[str, dict]:
    """accession_number -> {series_name, series_id}, from
    FUND_REPORTED_INFO.tsv (~5MB) -- the specific named fund, not the
    umbrella registrant. See module docstring point 2."""
    lookup: dict[str, dict] = {}
    for row in _load_tsv_dict(zf, "FUND_REPORTED_INFO.tsv"):
        series_name = row["SERIES_NAME"].strip()
        # Found live 2026-08-28: 28 of 14,416 real series rows in this
        # window carry the literal string "N/A" as SERIES_NAME (single-
        # series unit investment trusts like SPDR S&P 500 ETF Trust,
        # whose one series has no name distinct from the trust itself) --
        # a real SEC-submitted value, not a parsing gap. Treated the same
        # as a genuinely empty field so it falls through to
        # registrant_name below (a real, recognizable name) rather than
        # writing the literal text "N/A" as a fund name.
        if series_name.upper() == "N/A":
            series_name = ""
        lookup[row["ACCESSION_NUMBER"]] = {
            "series_name": series_name or None,
            "series_id": row["SERIES_ID"] or None,
        }
    return lookup


def _match_holdings(
    zf: zipfile.ZipFile,
    cusip_to_company: dict[str, int],
    submission_lookup: dict[str, dict],
    registrant_lookup: dict[str, dict],
    series_lookup: dict[str, dict],
) -> tuple[list[dict], int]:
    """Streams FUND_REPORTED_HOLDING.tsv (~910MB uncompressed) row by row
    rather than loading it wholesale -- only rows whose CUSIP matches a
    golden company are ever held in memory, same shape as
    institutional.py's own INFOTABLE.tsv stream."""
    matched: list[dict] = []
    total_rows = 0
    for row in _load_tsv_dict(zf, "FUND_REPORTED_HOLDING.tsv"):
        total_rows += 1
        cusip = row["ISSUER_CUSIP"].strip()
        company_id = cusip_to_company.get(cusip)
        if company_id is None:
            continue
        if row.get("ASSET_CAT", "").strip() != _REAL_OWNERSHIP_ASSET_CAT:
            continue
        if row.get("PAYOFF_PROFILE", "").strip() != _REAL_OWNERSHIP_PAYOFF_PROFILE:
            continue
        accession_number = row["ACCESSION_NUMBER"]
        submission = submission_lookup.get(accession_number, {})
        registrant = registrant_lookup.get(accession_number, {})
        series = series_lookup.get(accession_number, {})
        fund_name = series.get("series_name") or registrant.get("registrant_name") or "unknown"
        currency_code = row["CURRENCY_CODE"].strip() or "USD"
        currency_value = _decimal(row["CURRENCY_VALUE"])
        matched.append(
            {
                "company_id": company_id,
                "accession_number": accession_number,
                "holding_id": int(row["HOLDING_ID"]),
                "fund_name": fund_name,
                "fund_cik": registrant.get("fund_cik"),
                "series_id": series.get("series_id"),
                "shares": _decimal(row["BALANCE"]),
                "currency_code": currency_code,
                "currency_value": currency_value,
                # Never a computed conversion -- see module docstring
                # point 4.
                "value_usd": currency_value if currency_code == "USD" else None,
                "pct_of_fund_net_assets": _decimal(row["PERCENTAGE"]),
                "report_period": submission.get("report_period"),
                "filing_date": submission.get("filing_date"),
                "is_amendment": submission.get("is_amendment", False),
            }
        )
    return matched, total_rows


def _write_matched_rows(conn: psycopg.Connection, matched_rows: list[dict]) -> list[int]:
    """Delete-then-reinsert per matched company_id, same idempotent-rerun
    pattern as institutional.py (and Mapper's resolve.py/calculate.py
    before it) -- a plain `on conflict do nothing` upsert alone would
    leave stale rows behind for a company whose holdings shrank between
    runs. Split out from update_mutual_fund_ownership so this write
    behavior is unit-testable against a fake cursor without touching the
    network/zip-parsing path above."""
    company_ids = sorted({r["company_id"] for r in matched_rows})
    with conn.cursor() as cur:
        if company_ids:
            cur.execute(
                "delete from core.fund_ownership where company_id = any(%s)",
                (company_ids,),
            )
        if matched_rows:
            cur.executemany(
                """
                insert into core.fund_ownership
                    (company_id, accession_number, holding_id, fund_name, fund_cik, series_id,
                     shares, currency_code, currency_value, value_usd, pct_of_fund_net_assets,
                     report_period, filing_date, is_amendment, source_zip)
                values
                    (%(company_id)s, %(accession_number)s, %(holding_id)s, %(fund_name)s, %(fund_cik)s, %(series_id)s,
                     %(shares)s, %(currency_code)s, %(currency_value)s, %(value_usd)s, %(pct_of_fund_net_assets)s,
                     %(report_period)s, %(filing_date)s, %(is_amendment)s, %(source_zip)s)
                on conflict (accession_number, holding_id) do nothing
                """,
                [{**r, "source_zip": BULK_ZIP_WINDOW_LABEL} for r in matched_rows],
            )
    return company_ids


def update_mutual_fund_ownership(conn: psycopg.Connection) -> dict:
    cusip_to_company = _load_golden_cusips(conn)
    if not cusip_to_company:
        logger.warning("mutual_fund_ownership.no_cusips")
        return {"matched_rows": 0, "companies": 0, "holding_row_count": 0}

    with SECClient() as sec:
        zip_path = sec.get_cached_bulk_zip(BULK_ZIP_URL, f"nport-{BULK_ZIP_WINDOW_LABEL}")

    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()

    with zipfile.ZipFile(zip_path) as zf:
        submission_lookup = _load_submission_lookup(zf)
        registrant_lookup = _load_registrant_lookup(zf)
        series_lookup = _load_fund_series_lookup(zf)
        matched_rows, holding_row_count = _match_holdings(
            zf, cusip_to_company, submission_lookup, registrant_lookup, series_lookup
        )

    company_ids = _write_matched_rows(conn, matched_rows)
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into raw.sec_nport_bulk_fetch
                (source_url, window_label, sha256, holding_row_count, matched_row_count)
            values (%s, %s, %s, %s, %s)
            on conflict (window_label) do update set
                sha256 = excluded.sha256,
                holding_row_count = excluded.holding_row_count,
                matched_row_count = excluded.matched_row_count,
                fetched_at = now()
            """,
            (BULK_ZIP_URL, BULK_ZIP_WINDOW_LABEL, sha256, holding_row_count, len(matched_rows)),
        )
        conn.commit()

    stats = {
        "matched_rows": len(matched_rows),
        "companies": len(company_ids),
        "holding_row_count": holding_row_count,
        "window_label": BULK_ZIP_WINDOW_LABEL,
    }
    logger.info("mutual_fund_ownership.done", **stats)
    return stats
