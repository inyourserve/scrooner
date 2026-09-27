"""Stage 4a-3 -- Active/stale/unknown/delisted status inference (doc 13,
Sec 4; `delisted` added doc 23 Stage C / doc 24 Phase 1).

No EDGAR field literally says "delisted" -- checked directly, `category`
is a filer-size classification ("Large accelerated filer"), not a
listing-status flag. Filing-recency is the only honest signal for
active/stale/unknown.

Form 15/15F's mere presence is NOT, on its own, a reliable delisting
signal -- found live, the hard way, on the very first real check of this
logic. The golden-10 turned out NOT to be delisting-free after all: the
initial rerun surfaced 4 real Form 15/15D rows for JPMorgan Chase & Co
(CIK 0000019617), which looked like exactly the evidence doc 23 expected
-- until each was actually fetched and read. All four are filed by
"Chase Capital I" / "JPM Capital I" / "JPM Capital II", wholly separate
financing-subsidiary trusts that share JPM's parent CIK for filing
purposes (the same issuer-vs-filer ambiguity doc 19 already found
repeatedly for Schedule 13G and Form 4), deregistering specific debt
instruments ("7.67% Capital Securities, Series A", "7.95%/7.54%
Cumulative Capital Securities") -- not JPM's common stock, and not JPM
itself going private. A large financial-holding-company CIK routinely
registers and deregisters individual debt/trust-preferred security
series under its own CIK as a normal part of running a capital-markets
program; that has nothing to do with whether its common equity is still
listed.

The fix, also confirmed live: every real Form 15's cover page has a
fixed field, "Title of each class of securities covered by this Form"
-- American Woodmark's genuine 2026 delisting says "Common Stock (no
par value)"; JPM's three subsidiary-trust filings say specific debt
instrument names, never "common stock". `_is_common_stock_deregistration`
fetches the filing's full-submission text (same pattern as
beneficial_ownership.py's CUSIP extraction) and requires that field to
actually mention "common stock" before trusting the signal -- doc 23's
original "zero new fetch, form-type presence alone is enough" claim for
this stage was wrong, corrected here with real evidence, not assumed
away.

Four states, deliberately not three:
- delisted: a Form 15/15F-family filing exists in core.filing for this
  company AND its own cover page confirms the deregistered security is
  common stock (checked live via SEC fetch, not inferred from form type
  alone) -- checked BEFORE the recency logic below, since a deregistered
  company's 10-K/10-Q history is expected to just stop, which recency
  alone would otherwise misreport as merely "stale." AND (found live
  2026-09-02) no qualifying 10-K/10-Q was filed after that Form 15's own
  date -- 222 real active companies (AMD, Intel, HP, Caterpillar, US
  Bancorp among them) had a "common stock" Form 15 confirmed correctly by
  the cover-page check above, yet 192 of them kept filing real 10-Ks/10-Qs
  for years or decades afterward. A cover-page match alone isn't proof the
  company itself went dark -- see `_load_latest_form15_dates`'s own
  docstring for the fix.
- active: a 10-K or 10-Q filed within STALE_THRESHOLD_DAYS
- stale: no qualifying filing within that window, reason unconfirmed --
  NEVER 'delisted' unless the real, confirmed common-stock signal above
  is present. This project has no OTHER data source that actually
  confirms delisting, and asserting it anyway would be exactly the
  wrong-but-plausible failure mode Mapper's Day 4 ROIC bug was fixed to
  prevent.
- unknown: no qualifying filing at all (nothing to judge from)

Threshold: 18 months. SEC requires quarterly (10-Q) financial reporting for
a domestic operating company, so even a company that's badly behind on
filings would need an unusual, specific reason to go this long dark while
still technically active -- a generous margin, not a tight one, chosen to
minimize false 'stale' flags rather than to catch every real gap quickly.
"""

import re
from datetime import date, timedelta

import psycopg
import structlog

from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

STALE_THRESHOLD_DAYS = 18 * 30  # ~18 months, see module docstring

QUALIFYING_FORMS = {
    "10-K",
    "10-K/A",
    "10-Q",
    "10-Q/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
}

DEREGISTRATION_FORMS = {
    "15-12G",
    "15-12G/A",
    "15-15D",
    "15-15D/A",
    "15F-12B",
    "15F-12B/A",
    "15F-12G",
    "15F-12G/A",
}

_TAG_RE = re.compile(r"<[^>]+>")
_TITLE_OF_CLASS_RE = re.compile(
    r"([^()]{2,150}?)\s*\(Title of each class of securities covered by this Form\)",
    re.IGNORECASE,
)


def _is_common_stock_deregistration(
    sec: SECClient, cik: str, accession_number: str
) -> bool:
    cik_int = str(int(cik))
    acc_no_dash = accession_number.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_dash}/{accession_number}.txt"
    try:
        resp = sec.get(url)
    except Exception:
        logger.warning(
            "status.form15_fetch_failed", cik=cik, accession_number=accession_number
        )
        return False
    clean = _TAG_RE.sub(" ", resp.text)
    clean = re.sub(r"\s+", " ", clean)
    match = _TITLE_OF_CLASS_RE.search(clean)
    if match is None:
        return False
    return "common stock" in match.group(1).lower()


def _load_latest_filing_dates(
    conn: psycopg.Connection, company_ids: list[int]
) -> dict[int, date | None]:
    if not company_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select company_id, max(filing_date)
            from core.filing
            where company_id = any(%s) and form = any(%s) and filing_date is not null
            group by company_id
            """,
            (company_ids, sorted(QUALIFYING_FORMS)),
        )
        return dict(cur.fetchall())


def _load_latest_form15_dates(
    conn: psycopg.Connection, company_ids: list[int]
) -> dict[int, date | None]:
    """Newest Form 15/15F filing_date per company -- used to sanity-check a
    confirmed common-stock deregistration signal against filing recency
    (see module docstring, 2026-09-02 finding: AMD/Intel/HP/Caterpillar/US
    Bancorp and 188 others all had a decades-old Form 15-12G on record, each
    followed by continuous real 10-K/10-Q filings for years or decades
    after -- almost certainly a historical Section 12(g)-to-12(b) exchange
    up-listing or a specific security-class deregistration under a shared
    CIK, not the company going private. A confirmed 'common stock' cover-
    page match is not sufficient on its own once a qualifying filing exists
    after it."""
    if not company_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select company_id, max(filing_date)
            from core.filing
            where company_id = any(%s) and form = any(%s) and filing_date is not null
            group by company_id
            """,
            (company_ids, sorted(DEREGISTRATION_FORMS)),
        )
        return dict(cur.fetchall())


def _load_candidate_deregistrations(
    conn: psycopg.Connection, company_ids: list[int]
) -> dict[int, list[tuple[str, str]]]:
    """company_id -> [(cik, accession_number), ...] for every Form 15/15F
    filing on record -- candidates only, NOT yet confirmed as a real
    common-stock delisting (see module docstring's JPM finding)."""
    if not company_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.company_id, c.cik, f.accession_number
            from core.filing f join core.company c on c.id = f.company_id
            where f.company_id = any(%s) and f.form = any(%s)
            """,
            (company_ids, sorted(DEREGISTRATION_FORMS)),
        )
        candidates: dict[int, list[tuple[str, str]]] = {}
        for company_id, cik, accession_number in cur.fetchall():
            candidates.setdefault(company_id, []).append((cik, accession_number))
        return candidates


def _confirm_deregistered_company_ids(
    sec: SECClient, candidates: dict[int, list[tuple[str, str]]]
) -> set[int]:
    """Fetches and checks each candidate's own cover page -- only a
    confirmed common-stock deregistration counts, per the module
    docstring's JPM/Chase-Capital-trust finding. Stops at the first
    confirmed hit per company; a company with 3 non-equity Form 15s (like
    JPM) correctly stays un-flagged even after checking all 3."""
    confirmed: set[int] = set()
    for company_id, filings in candidates.items():
        for cik, accession_number in filings:
            if _is_common_stock_deregistration(sec, cik, accession_number):
                confirmed.add(company_id)
                break
    return confirmed


def compute_status(
    latest_filing_date: date | None, as_of: date, is_deregistered: bool = False
) -> tuple[str, str]:
    if is_deregistered:
        return "delisted", "form_15_common_stock_confirmed"
    if latest_filing_date is None:
        return "unknown", "no_qualifying_filing_on_record"
    age_days = (as_of - latest_filing_date).days
    if age_days <= STALE_THRESHOLD_DAYS:
        return "active", f"filed:{latest_filing_date.isoformat()}"
    return "stale", f"no_filing_since:{latest_filing_date.isoformat()}"


def _deregistration_overridden_by_later_filing(
    latest_filing_date: date | None, form15_date: date | None
) -> bool:
    """True when a real qualifying 10-K/10-Q was filed after the newest
    Form 15/15F on record -- see module docstring's 2026-09-02 finding."""
    return (
        latest_filing_date is not None
        and form15_date is not None
        and latest_filing_date > form15_date
    )


def update_status(
    conn: psycopg.Connection, ciks: set[str], as_of: date | None = None
) -> dict:
    as_of = as_of or date.today()
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = {cik: cid for cid, cik in cur.fetchall()}

    company_ids = list(company_id_by_cik.values())
    latest_by_company = _load_latest_filing_dates(conn, company_ids)
    form15_by_company = _load_latest_form15_dates(conn, company_ids)
    candidates = _load_candidate_deregistrations(conn, company_ids)
    with SECClient() as sec:
        deregistered_company_ids = _confirm_deregistered_company_ids(sec, candidates)

    rows = []
    stats = {
        "considered": 0,
        "active": 0,
        "stale": 0,
        "unknown": 0,
        "delisted": 0,
        "no_company": 0,
        "delisting_signal_overridden_by_later_filing": 0,
    }
    for cik in sorted(ciks):
        stats["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            stats["no_company"] += 1
            continue
        latest = latest_by_company.get(company_id)
        is_deregistered = company_id in deregistered_company_ids
        if is_deregistered and _deregistration_overridden_by_later_filing(
            latest, form15_by_company.get(company_id)
        ):
            is_deregistered = False
            stats["delisting_signal_overridden_by_later_filing"] += 1
        status, reason = compute_status(latest, as_of, is_deregistered)
        stats[status] += 1
        rows.append(
            {
                "company_id": company_id,
                "status": status,
                "status_as_of": as_of,
                "status_reason": reason,
            }
        )

    if rows:
        with conn.cursor() as cur:
            cur.executemany(
                """
                update core.company
                   set status = %(status)s, status_as_of = %(status_as_of)s, status_reason = %(status_reason)s
                 where id = %(company_id)s
                """,
                rows,
            )
        conn.commit()

    logger.info("company_master.status.done", **stats)
    return stats
