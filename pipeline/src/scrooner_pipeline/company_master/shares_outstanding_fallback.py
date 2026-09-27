"""Real shares-outstanding fallback for multi-class share-structure
companies (doc 24/25 follow-up; generalized doc 42, 2026-09-03). Company
Master's job, NOT the Normalizer's -- this needs a genuinely new fetch
(the 10-K's own cover page, not already in Storage), and normalizer/ has
a hard "no new SEC network calls" boundary this would violate. Writes to
core.shares_outstanding_fallback, a table separate from core.fact;
mapper/price_metrics.py falls back to it only when the real XBRL-sourced
canonical_fact lookup for shares_outstanding comes up empty -- never
overrides a working value.

Root cause, confirmed live 2026-08-17: Reddit (Class A/B/C) and Block
(Class A/B) both disclose per-class share counts on their 10-K cover
page, dimensionally tagged in XBRL -- the standard Company Facts API
strips dimensional facts entirely (the same limitation doc 22 already
found for segment revenue), so neither company has a single
undimensioned shares-outstanding total anywhere in core.fact. Checked
live 2026-09-03 whether `edgartools` (doc 12) has a structured shortcut
around this: it does not -- its own `EntityFacts.shares_outstanding`
tries exactly two single-tag lookups (`dei:EntityCommonStockSharesOutstanding`,
then `us-gaap:CommonStockSharesOutstanding`), the same fundamental
limitation, since both it and this project's Collector ultimately read
the same aggregated Company Facts API that cannot represent per-class
dimensional data at all. Cover-page text is a genuine independent
source precisely because the cover page's own legal purpose (Item
12(b)-25 of Form 10-K) is to state the total by class in prose, which no
single structured tag can.

GENERALIZED 2026-09-03 (doc 42): the original version handled exactly 2
real phrasings (Block, Reddit) and was piloted against 30 real
companies missing shares_outstanding at full population -- only 23%
(7/30) extracted. Reading the real failures (not guessing) surfaced 9
more distinct real-world phrasings (see each SubParser's own `name`/
comment below), pushing real extraction success to 63.6% across two
independent real samples (79.9% excluding genuine no-10-K cases), then
504/504 companies run at full population (333 extracted). If NONE of
the sub-parsers match confidently, this leaves the company unresolved
rather than guessing at an 11th format -- same "never guess" discipline
as everywhere else in this project.

REFACTORED 2026-09-03 onto `company_master/text_extraction.py`'s
generalized head-parser/sub-parser framework -- same patterns, same
priority order, same plausibility/scale-hint/gate logic as the
hand-written version this replaced, now expressed as reusable
`SubParser` objects so future concepts (a bank's revenue-equivalent, a
rendered R*.htm table) can reuse the framework instead of duplicating
this module's own control flow. Behavior-preserving: all 16 pre-existing
tests pass unchanged. This is a living pattern list (see doc 42's
continuous-improvement loop), not a closed one -- extend it the same way
each pattern here was added: read real failures, generalize
deliberately, verify via a re-pilot before trusting a full population
run.
"""

import re

import psycopg
import structlog

from scrooner_pipeline.collector.storage import (
    SupabaseStorageClient,
    strip_bucket_prefix,
)
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.company_master.text_extraction import (
    SubParser,
    looks_like_a_bare_year,
    run_head_parser,
)

logger = structlog.get_logger()

# Shared vocabulary fragments, reused across patterns so a new security-type
# noun or class-label shape only needs to be added once.
_CLASS_LABEL = r"(?:Class|Series)\s+[A-Z0-9](?:-\d+)?\b"
_SECURITY_NOUN = r"(?:common stock|ordinary shares|common shares|Common Voting shares|ordinary common stock)"
_NUM = r"([\d][\d,]*)"
_HAS_CLASS_OR_SERIES = re.compile(
    r"\bClass\s+[A-Z]\b|\bSeries\s+[A-Z]\b", re.IGNORECASE
)


def _sum_group1(matches: list[re.Match]) -> float:
    return float(sum(int(m.group(1).replace(",", "")) for m in matches))


def _sum_group1_reject_bare_year(matches: list[re.Match]) -> float | None:
    total = int(sum(int(m.group(1).replace(",", "")) for m in matches))
    if looks_like_a_bare_year(total, len(matches)):
        return None
    return float(total)


def _two_class_respectively_combine(matches: list[re.Match]) -> float | None:
    # "outstanding" itself is deliberately not anchored to a fixed
    # position in the regex -- two real orderings exist ("...common
    # stock outstanding were N and M, respectively" -- Block, outstanding
    # right before "were"; "shares outstanding of ...X and Y... were N
    # and M, respectively" -- outstanding right at the start). Checked
    # here, over the whole matched span plus a lookback window, rather
    # than forcing one fixed position into the regex and missing the
    # other real shape.
    match = matches[0]
    text = match.string
    span_with_context = text[max(0, match.start() - 80) : match.end()]
    if not re.search(r"\boutstanding\b", span_with_context, re.IGNORECASE):
        return None
    return float(sum(int(g.replace(",", "")) for g in match.groups()))


def _units_of_beneficial_interest_combine(matches: list[re.Match]) -> float:
    match = matches[0]
    captured = match.group(1) or match.group(2)
    return float(int(captured.replace(",", "")))


def _no_class_or_series_on_page(clean_text: str) -> bool:
    # Single-class pattern only fires when the page never mentions
    # "Class"/"Series" at all -- a genuine multi-class company whose
    # more specific patterns all failed to match must stay unresolved,
    # not silently under-counted by matching just its first class.
    return not _HAS_CLASS_OR_SERIES.search(clean_text)


_SUB_PARSERS = [
    # Table-format patterns tried FIRST, ahead of the looser per-class/
    # class-prefix patterns below -- found live 2026-09-03: a flattened
    # "Class A ... 172,172,544 Class 1 ..." table layout coincidentally
    # matches the looser "NUMBER Class X noun" shape too (the first
    # class's trailing number sits directly before the next row's class
    # label), silently attributing class A's count to class 1 and
    # losing the rest of the table. These patterns' "par value"/"Shares
    # Outstanding" anchors are specific enough not to false-match
    # ordinary prose, so trying them first avoids the cross-match.
    SubParser(
        # The "$.01 per share" price clause between "par value" and the
        # real target number is itself made of digits ("01") -- a naive
        # [^0-9]{0,N}? gap stops AT that price's digits instead of
        # skipping past them, capturing "01" instead of the real share
        # count. Consuming the whole "$X.XX per share"-shaped clause
        # explicitly avoids the trap. E.g. Constellation Brands: "Class
        # A Common Stock, par value $.01 per share 172,172,544".
        name="table_format_par_value_per_share",
        pattern=re.compile(
            rf"{_CLASS_LABEL}[^0-9]{{0,80}}?par value\s+\$[\d.]+\s+per\s+share\s+{_NUM}",
            re.IGNORECASE,
        ),
        combine=_sum_group1,
    ),
    SubParser(
        # Same table layout, no "par value" clause -- e.g. "Class A
        # common stock, 28,428,416 shares Class B common stock,
        # 3,248,420 shares". The negative lookbehind is load-bearing:
        # found live 2026-09-03, this shape without it also matches
        # ordinary per-class PROSE lists ("...shares of Class A common
        # stock, 51,386,276 shares of Class B...") by coincidentally
        # landing on the NEXT class's number after a comma -- real
        # tables never have "of" immediately before the class label,
        # real prose lists always do ("shares OF Class A"), so requiring
        # its absence is what actually distinguishes the two shapes.
        name="table_format_simple",
        pattern=re.compile(
            rf"(?<!of\s){_CLASS_LABEL}\s+{_SECURITY_NOUN},\s*{_NUM}\s+shares",
            re.IGNORECASE,
        ),
        combine=_sum_group1,
    ),
    SubParser(
        # A fourth real table shape, found live 2026-09-03 (Beasley
        # Broadcast): "Class X Common Stock, $par value, NUMBER Shares
        # Outstanding as of DATE" -- the trailing date's own year is a
        # real trap: without this pattern taking priority, the looser
        # class-prefix pattern below coincidentally matched "<year>
        # Class B Common Stock" (the first class's trailing date sits
        # immediately before the next class's label in the flattened
        # table) and returned a 4-digit year as if it were a real share
        # count.
        name="table_format_shares_outstanding_as_of_date",
        pattern=re.compile(
            rf"{_CLASS_LABEL}\s+{_SECURITY_NOUN},\s*\$[\d.]+\s+par value,\s*{_NUM}\s+Shares\s+Outstanding",
            re.IGNORECASE,
        ),
        combine=_sum_group1,
    ),
    SubParser(
        # Requires at least one digit, not just a bare comma -- a first
        # version without \d in the required position matched a stray
        # "," elsewhere in Block's filing and crashed on int(''). "N
        # shares of Class/Series X common stock/ordinary shares"
        # repeated, sum. Broadened 2026-09-03: "Class"/"Series",
        # multi-character class suffixes ("Class B-1"), wider noun set.
        name="per_class_shares_of",
        pattern=re.compile(
            rf"{_NUM}\s+shares?\s+of\s+(?:the registrant.s\s+)?{_CLASS_LABEL}\s+{_SECURITY_NOUN}",
            re.IGNORECASE,
        ),
        combine=_sum_group1_reject_bare_year,
        scale_hint_lookback_chars=100,
    ),
    SubParser(
        # "N Class/Series X ordinary/common shares" (no "shares of"
        # prefix), repeated, sum -- e.g. "29,200,000 Class A ordinary
        # shares... and 12,000,000 Class B ordinary shares". Reject-
        # bare-year is defense in depth against the same Beasley-shaped
        # trap the table pattern above already closes structurally.
        name="class_prefix",
        pattern=re.compile(
            rf"{_NUM}\s+{_CLASS_LABEL}\s+{_SECURITY_NOUN}", re.IGNORECASE
        ),
        combine=_sum_group1_reject_bare_year,
        scale_hint_lookback_chars=100,
    ),
    SubParser(
        # "Class X and Class Y ... outstanding were N and M,
        # respectively" -- either side may be a real class with its own
        # noun, a bare class label sharing the next side's noun (Block:
        # "Class A and Class B common stock", only the second class
        # carries the noun), or a bare noun with no class letter at all
        # (found live 2026-09-03: "Common Stock and Class A Common
        # Stock", a company with only one lettered class). Requiring a
        # class letter AND its own noun on both sides (an earlier
        # version) missed both real shapes.
        name="two_class_respectively",
        pattern=re.compile(
            rf"(?:{_CLASS_LABEL}(?:\s+{_SECURITY_NOUN})?|{_SECURITY_NOUN})\s+and\s+"
            rf"(?:{_CLASS_LABEL}(?:\s+{_SECURITY_NOUN})?|{_SECURITY_NOUN}).{{0,150}}?were\s+{_NUM}\s+and\s+{_NUM}\s*,?\s*respectively",
            re.IGNORECASE | re.DOTALL,
        ),
        combine=_two_class_respectively_combine,
        scale_hint_lookback_chars=100,
    ),
    SubParser(
        # "The number of shares of ... Class X outstanding ... was N"
        # repeated as separate sentences (not a single comma-list) --
        # e.g. Alphabet-style disclosures.
        name="separate_sentences_per_class",
        pattern=re.compile(
            rf"number of shares of[^.]{{0,80}}?{_CLASS_LABEL}[^.]{{0,80}}?outstanding[^.]{{0,80}}?was\s+{_NUM}",
            re.IGNORECASE,
        ),
        combine=_sum_group1,
    ),
    SubParser(
        # Royalty trusts (Hugoton, Mesa) -- "units of beneficial
        # interest", no "shares"/"common stock" language at all, a
        # genuinely different security type. Two real orderings found
        # live 2026-09-03: number first ("N units of beneficial
        # interest ... outstanding") or number trailing after "was".
        name="units_of_beneficial_interest",
        pattern=re.compile(
            rf"(?:{_NUM}\s+units of beneficial interest.{{0,40}}?outstanding"
            rf"|units of beneficial interest.{{0,40}}?outstanding.{{0,40}}?was\s+{_NUM})",
            re.IGNORECASE | re.DOTALL,
        ),
        combine=_units_of_beneficial_interest_combine,
    ),
    SubParser(
        # "there were N shares outstanding" -- the single most common
        # real-world case for a company with only one class, tried LAST
        # and gated to only run when the page never mentions "Class"/
        # "Series" at all.
        name="single_class",
        pattern=re.compile(
            rf"there were\s+{_NUM}\s+shares(?:\s+of\s+(?:the registrant.s\s+)?{_SECURITY_NOUN})?\s+outstanding",
            re.IGNORECASE,
        ),
        combine=lambda matches: float(int(matches[0].group(1).replace(",", ""))),
        gate=_no_class_or_series_on_page,
        scale_hint_lookback_chars=100,
    ),
]

# Real 10-Ks repeat "shares of Class X common stock" phrasing throughout
# (RSU/option disclosures, etc.), not just the cover page -- confirmed
# live: RDDT's real cover-page mentions sit at ~20K chars in, a false
# later repeat at ~258K; Block's real two-class disclosure sits at ~48K,
# a false bare-comma match at ~224K. This window comfortably covers both
# real cases and excludes both false ones -- generous, not exact, since
# cover-page length varies by filer.
_COVER_PAGE_CHAR_LIMIT = 60_000

# A sanity floor/ceiling on the RESULT, not a pattern -- catches a
# structurally-successful-looking match that's still obviously wrong
# (e.g. an option-grant count mistaken for the real total). No real
# company in this population has fewer than 1,000 or more than 50
# billion shares outstanding.
_MIN_PLAUSIBLE_SHARES = 1_000
_MAX_PLAUSIBLE_SHARES = 50_000_000_000


def _extract_shares(cover_text: str) -> float | None:
    result = run_head_parser(
        cover_text,
        _SUB_PARSERS,
        char_limit=_COVER_PAGE_CHAR_LIMIT,
        min_plausible=_MIN_PLAUSIBLE_SHARES,
        max_plausible=_MAX_PLAUSIBLE_SHARES,
    )
    return result[0] if result is not None else None


def _load_latest_10k(
    conn: psycopg.Connection, storage: SupabaseStorageClient, cik: str
) -> dict | None:
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


def update_shares_outstanding_fallback(
    conn: psycopg.Connection, ciks: set[str]
) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    stats = {
        "considered": len(ciks),
        "no_company": 0,
        "no_10k": 0,
        "fetch_failed": 0,
        "no_pattern_match": 0,
        "extracted": 0,
    }
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
                logger.warning(
                    "shares_outstanding_fallback.fetch_failed", cik=cik, url=url
                )
                stats["fetch_failed"] += 1
                continue
            shares = _extract_shares(resp.text)
            if shares is None:
                logger.warning(
                    "shares_outstanding_fallback.no_pattern_match",
                    cik=cik,
                    accession_number=latest["accession_number"],
                )
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
