"""Real shares-outstanding fallback for multi-class share-structure
companies (doc 24/25 follow-up). Company Master's job, NOT the
Normalizer's -- this needs a genuinely new fetch (the 10-K's own cover
page, not already in Storage), and normalizer/ has a hard "no new SEC
network calls" boundary this would violate. Writes to
core.shares_outstanding_fallback, a table separate from core.fact;
mapper/price_metrics.py falls back to it only when the real XBRL-sourced
canonical_fact lookup for shares_outstanding comes up empty -- never
overrides a working value.

Root cause, confirmed live 2026-08-17: Reddit (Class A/B/C) and Block
(Class A/B) both disclose per-class share counts on their 10-K cover
page, dimensionally tagged in XBRL -- the standard Company Facts API
strips dimensional facts entirely (the same limitation doc 22 already
found for segment revenue), so neither company has a single
undimensioned shares-outstanding total anywhere in core.fact.

Two real, different cover-page phrasings confirmed live before writing
this -- NOT one generic regex, deliberately:
- Reddit: "...outstanding 139,649,508 shares of Class A common stock,
  51,386,276 shares of Class B common stock, and no shares of Class C
  common stock..." -- PATTERN_PER_CLASS, one match per class, summed.
- Block: "...number of shares (in thousands) of the registrant's Class A
  and Class B common stock outstanding were 539,103 and 59,993,
  respectively." -- PATTERN_TWO_CLASS_RESPECTIVELY, exactly two classes,
  PLUS a real unit-scale trap: the literal "(in thousands)" qualifier a
  few words earlier, which multiplies the actual share count by 1,000.
  Missing this would have silently produced a value 1,000x too small --
  worse than leaving it null, since it would look plausible. Checked
  explicitly via SCALE_HINT_RE before trusting either pattern's raw
  numbers.

If NEITHER pattern matches confidently, this leaves the company
unresolved rather than guessing at a third format -- same "never guess"
discipline as everywhere else in this project. Only 2 companies in the
golden-10 need this at all; a wider universe would very likely surface
more real phrasings, not yet seen or handled.
"""

import re

import psycopg
import structlog

from scrooner_pipeline.collector.storage import SupabaseStorageClient, strip_bucket_prefix
from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

_TAG_RE = re.compile(r"<[^>]+>")
_SCALE_HINT_RE = re.compile(r"in thousands", re.IGNORECASE)
# Requires at least one digit, not just a bare comma -- a first version
# without \d in the required position matched a stray "," elsewhere in
# Block's filing and crashed on int('').
_PATTERN_PER_CLASS = re.compile(r"([\d][\d,]*)\s+shares?\s+of\s+Class\s+[A-Z]\s+common stock", re.IGNORECASE)
_PATTERN_TWO_CLASS_RESPECTIVELY = re.compile(
    r"Class\s+[A-Z]\s+and\s+Class\s+[A-Z].{0,150}?outstanding\s+were\s+([\d,]+)\s+and\s+([\d,]+)\s*,?\s*respectively",
    re.IGNORECASE | re.DOTALL,
)

# Real 10-Ks repeat "shares of Class X common stock" phrasing throughout
# (RSU/option disclosures, etc.), not just the cover page -- confirmed
# live: RDDT's real cover-page mentions sit at ~20K chars in, a false
# later repeat at ~258K; Block's real two-class disclosure sits at ~48K,
# a false bare-comma match at ~224K. This window comfortably covers both
# real cases and excludes both false ones -- generous, not exact, since
# cover-page length varies by filer.
_COVER_PAGE_CHAR_LIMIT = 60_000


def _extract_shares(cover_text: str) -> float | None:
    clean = _TAG_RE.sub(" ", cover_text)
    clean = re.sub(r"&#\d+;|&nbsp;", " ", clean)
    clean = re.sub(r"\s+", " ", clean)
    clean = clean[:_COVER_PAGE_CHAR_LIMIT]

    per_class_matches = _PATTERN_PER_CLASS.findall(clean)
    if per_class_matches:
        return float(sum(int(m.replace(",", "")) for m in per_class_matches))

    two_class_match = _PATTERN_TWO_CLASS_RESPECTIVELY.search(clean)
    if two_class_match:
        total = sum(int(g.replace(",", "")) for g in two_class_match.groups())
        window = clean[max(0, two_class_match.start() - 100) : two_class_match.start()]
        if _SCALE_HINT_RE.search(window):
            total *= 1000
        return float(total)

    return None


def _load_latest_10k(conn: psycopg.Connection, storage: SupabaseStorageClient, cik: str) -> dict | None:
    """Most recent 10-K's accession_number/primaryDocument/filingDate,
    from the already-fetched raw.sec_submissions (zero new discovery
    fetch, same pattern as ownership/'s own filing-list loading)."""
    import json

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

    best: dict | None = None
    for storage_path in storage_paths:
        payload = json.loads(storage.download(strip_bucket_prefix(storage_path)))
        block = payload["filings"]["recent"] if "filings" in payload else payload
        for i, form in enumerate(block.get("form", [])):
            if form != "10-K":
                continue
            filing_date = block["filingDate"][i]
            if best is None or filing_date > best["filing_date"]:
                best = {
                    "accession_number": block["accessionNumber"][i],
                    "primary_document": block["primaryDocument"][i],
                    "filing_date": filing_date,
                }
    return best


def update_shares_outstanding_fallback(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    stats = {"considered": len(ciks), "no_company": 0, "no_10k": 0, "fetch_failed": 0, "no_pattern_match": 0, "extracted": 0}
    rows = []
    with SupabaseStorageClient() as storage, SECClient() as sec:
        for cik in sorted(ciks):
            company_id = company_id_by_cik.get(cik)
            if company_id is None:
                stats["no_company"] += 1
                continue
            latest = _load_latest_10k(conn, storage, cik)
            if latest is None:
                stats["no_10k"] += 1
                continue
            cik_int = str(int(cik))
            acc_no_dash = latest["accession_number"].replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_dash}/{latest['primary_document']}"
            try:
                resp = sec.get(url)
            except Exception:
                logger.warning("shares_outstanding_fallback.fetch_failed", cik=cik, url=url)
                stats["fetch_failed"] += 1
                continue
            shares = _extract_shares(resp.text)
            if shares is None:
                logger.warning("shares_outstanding_fallback.no_pattern_match", cik=cik, accession_number=latest["accession_number"])
                stats["no_pattern_match"] += 1
                continue
            rows.append(
                {
                    "company_id": company_id,
                    "shares": shares,
                    "accession_number": latest["accession_number"],
                    "filing_date": latest["filing_date"],
                }
            )
            stats["extracted"] += 1

    if rows:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.shares_outstanding_fallback (company_id, shares, accession_number, filing_date)
                values (%(company_id)s, %(shares)s, %(accession_number)s, %(filing_date)s)
                on conflict (company_id) do update
                    set shares = excluded.shares,
                        accession_number = excluded.accession_number,
                        filing_date = excluded.filing_date,
                        extracted_at = now()
                """,
                rows,
            )
        conn.commit()

    logger.info("shares_outstanding_fallback.done", **stats)
    return stats
