"""Stage 2 -- Form 4 insider transactions (doc 19). Reads the golden
company's own already-stored raw.sec_submissions payload (Module 4's
output, fetched during the original Collector build) for form='4'/'4/A'
entries -- zero new SEC "discovery" fetch, same mechanism doc 19 Sec 1
found after correcting the first, wrong draft. Downloads each individual
filing's XML body (not previously fetched -- the submissions list only
has accession numbers/dates, not transaction detail) and parses it with
a real XML parser (ElementTree), not regex -- confirmed live against a
real AAPL Form 4 before writing this: exact element paths verified,
not guessed (transactionCoding/transactionCode, not
transactionAmounts/transactionCode -- a real, easy-to-get-wrong path).

issuerCik IS cross-checked, same as Schedule 13D/13G (ownership/
beneficial_ownership.py) -- an earlier version of this docstring claimed
Form 4 didn't need this because "one company can't be an insider of
another." Wrong, found live running the full golden-10: EDGAR's own
submissions.json for a CIK includes every Form 4 where that CIK appears
in *any* role, not just issuer -- a company can itself be the *reporting
owner* on someone else's Form 4 (a 10%+ institutional stake, e.g. real
JPM filings reporting JPMorgan Chase & Co. itself as reporting owner of
an unrelated issuer), or a subsidiary can file under the parent's CIK
(real Alphabet example: "GV 2019 GP, L.L.C.", Alphabet's venture arm,
filing insider disclosures for its own portfolio companies -- 81 such
filings found for GOOGL alone). Same root cause as the Schedule 13G
finding (doc 19 Sec 1), just also true here -- 285 real mismatches found
across the golden-10 by the check that's already enforced below. See
doc/learnings/ownership-and-8k-discovery.md.

Form 3/5 deliberately out of this pass -- Form 4 is doc 10's own named
"core insider-activity feed"; 3/5 are lower-priority supporting context
(doc 19 Sec 1), and Form 3's holding-only structure needs its own
verification pass before being trusted, not assumed from Form 4's shape.

is_10b5_1_plan (doc 23 Stage A, doc 24 Phase 1) is captured from
aff10b5One -- SEC's 2023 Rule 10b5-1(c) trading-plan disclosure,
confirmed live in this exact XML across a real AAPL filing and four real
MSFT filings (including two open-market sales) before writing this.
Document-level, not per-transaction (one <aff10b5One> per filing, before
the transaction tables) -- every transaction in a multi-transaction
Form 4 shares the same flag, a real limitation, not something this
parser can resolve more finely than the source document does. Two real
boolean lexical forms seen in practice ("true"/"false" and "1"/"0") --
handled explicitly, not assumed to be one or the other. NULL (not
False) for any filing that lacks the field entirely -- true for every
Form 4 filed before the rule's 2023-04-01 effective date, same
never-guess discipline as the issuer_cik check above.
"""

import json
from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree as ET

import psycopg
import structlog

from scrooner_pipeline.collector.storage import SupabaseStorageClient, strip_bucket_prefix
from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

FORMS = {"4", "4/A"}


def _text(el: ET.Element | None, path: str) -> str | None:
    if el is None:
        return None
    node = el.find(path)
    if node is None or node.text is None:
        return None
    return node.text.strip() or None


def _decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _bool(value: str | None) -> bool | None:
    """aff10b5One uses two real lexical forms in practice -- "true"/"false"
    (seen live, AAPL) and "1"/"0" (seen live, MSFT) -- both handled
    explicitly, not assumed to be one or the other."""
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in ("true", "1"):
        return True
    if normalized in ("false", "0"):
        return False
    return None


def _latest_submission_files(conn: psycopg.Connection, cik: str) -> list[str]:
    """Base + continuation pages for the most recent fetch batch -- same
    pattern as normalizer/identity.py's _latest_submission_files, needed
    here too because a long-history company's Form 4s can span past the
    base file's own `filings.recent` window into continuation pages."""
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
        return [row[0] for row in cur.fetchall()]


def _load_form4_filings(storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str) -> list[dict]:
    filings: list[dict] = []
    for storage_path in _latest_submission_files(conn, cik):
        payload = json.loads(storage.download(strip_bucket_prefix(storage_path)))
        block = payload["filings"]["recent"] if "filings" in payload else payload
        for i, form in enumerate(block.get("form", [])):
            if form in FORMS:
                filings.append(
                    {
                        "form": form,
                        "accession_number": block["accessionNumber"][i],
                        "filing_date": block["filingDate"][i],
                        "primary_document": block["primaryDocument"][i],
                    }
                )
    return filings


def _parse_form4(xml_bytes: bytes) -> dict | None:
    root = ET.fromstring(xml_bytes)
    issuer_cik = _text(root, "issuer/issuerCik")
    owner = root.find("reportingOwner")
    if owner is None:
        return None
    rel = owner.find("reportingOwnerRelationship")
    transactions = []
    for tx in root.findall(".//nonDerivativeTransaction"):
        transactions.append(
            {
                "security_title": _text(tx, "securityTitle/value"),
                "transaction_date": _text(tx, "transactionDate/value"),
                "transaction_code": _text(tx, "transactionCoding/transactionCode"),
                "shares": _decimal(_text(tx, "transactionAmounts/transactionShares/value")),
                "price_per_share": _decimal(_text(tx, "transactionAmounts/transactionPricePerShare/value")),
                "acquired_disposed_code": _text(tx, "transactionAmounts/transactionAcquiredDisposedCode/value"),
                "shares_owned_following": _decimal(_text(tx, "postTransactionAmounts/sharesOwnedFollowingTransaction/value")),
            }
        )
    return {
        "issuer_cik": issuer_cik,
        "owner_name": _text(owner, "reportingOwnerId/rptOwnerName"),
        "owner_cik": _text(owner, "reportingOwnerId/rptOwnerCik"),
        "is_director": (_text(rel, "isDirector") or "").lower() in ("true", "1"),
        "is_officer": (_text(rel, "isOfficer") or "").lower() in ("true", "1"),
        "is_ten_percent_owner": (_text(rel, "isTenPercentOwner") or "").lower() in ("true", "1"),
        "officer_title": _text(rel, "officerTitle"),
        "is_10b5_1_plan": _bool(_text(root, "aff10b5One")),
        "transactions": transactions,
    }


def update_insider_transactions_for_company(
    conn: psycopg.Connection, sec: SECClient, company_id: int, cik: str
) -> dict:
    with SupabaseStorageClient() as storage:
        filings = _load_form4_filings(storage, conn, cik)

    rows: list[dict] = []
    stats = {"filings_considered": len(filings), "filings_parsed": 0, "transactions": 0, "issuer_mismatch": 0}
    for f in filings:
        acc_no_dash = f["accession_number"].replace("-", "")
        cik_int = str(int(cik))
        # submissions.json's primaryDocument is the XSL-viewer path (e.g.
        # "xslF345X06/form4.xml") -- verified live (AAPL 0001140361-26-025622)
        # that path 404s/returns an unrelated HTML shell; the real raw XML
        # sits at the accession folder's top level under just the basename
        # (confirmed via that filing's own index.json).
        doc_basename = f["primary_document"].rsplit("/", 1)[-1]
        url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_dash}/{doc_basename}"
        try:
            resp = sec.get(url)
        except Exception:
            logger.warning("insider.fetch_failed", cik=cik, accession_number=f["accession_number"])
            continue
        try:
            parsed = _parse_form4(resp.content)
        except ET.ParseError:
            logger.warning("insider.parse_failed", cik=cik, accession_number=f["accession_number"], url=url)
            continue
        if parsed is None:
            continue
        # A missing issuer_cik is inconclusive, not a match -- same
        # discipline as beneficial_ownership.py's stricter check, never
        # default a missing field to "passes."
        if not parsed["issuer_cik"] or parsed["issuer_cik"].lstrip("0") != cik.lstrip("0"):
            stats["issuer_mismatch"] += 1
            continue
        stats["filings_parsed"] += 1
        for idx, tx in enumerate(parsed["transactions"]):
            rows.append(
                {
                    "company_id": company_id,
                    "accession_number": f["accession_number"],
                    "transaction_index": idx,
                    "form": f["form"],
                    "reporting_owner_name": parsed["owner_name"],
                    "reporting_owner_cik": parsed["owner_cik"],
                    "is_director": parsed["is_director"],
                    "is_officer": parsed["is_officer"],
                    "is_ten_percent_owner": parsed["is_ten_percent_owner"],
                    "officer_title": parsed["officer_title"],
                    "is_10b5_1_plan": parsed["is_10b5_1_plan"],
                    "security_title": tx["security_title"],
                    "transaction_date": tx["transaction_date"],
                    "transaction_code": tx["transaction_code"],
                    "shares": tx["shares"],
                    "price_per_share": tx["price_per_share"],
                    "acquired_disposed_code": tx["acquired_disposed_code"],
                    "shares_owned_following": tx["shares_owned_following"],
                    "filing_date": f["filing_date"],
                }
            )
            stats["transactions"] += 1

    with conn.cursor() as cur:
        cur.execute("delete from core.insider_transaction where company_id = %s", (company_id,))
        if rows:
            # ON CONFLICT DO NOTHING (added 2026-08-27): the unique key is
            # (accession_number, transaction_index) *without* company_id, so
            # the per-company delete above doesn't protect against a genuine
            # duplicate row -- found live crashing the whole chunk (a real
            # company's Form 4 history produced the same accession number
            # twice, e.g. via a continuation-page overlap in
            # _load_form4_filings). A silent skip is correct here: an exact
            # duplicate key means the row's content is identical, not a
            # conflicting value needing resolution.
            cur.executemany(
                """
                insert into core.insider_transaction
                    (company_id, accession_number, transaction_index, form, reporting_owner_name,
                     reporting_owner_cik, is_director, is_officer, is_ten_percent_owner, officer_title,
                     is_10b5_1_plan, security_title, transaction_date, transaction_code, shares, price_per_share,
                     acquired_disposed_code, shares_owned_following, filing_date)
                values
                    (%(company_id)s, %(accession_number)s, %(transaction_index)s, %(form)s, %(reporting_owner_name)s,
                     %(reporting_owner_cik)s, %(is_director)s, %(is_officer)s, %(is_ten_percent_owner)s, %(officer_title)s,
                     %(is_10b5_1_plan)s, %(security_title)s, %(transaction_date)s, %(transaction_code)s, %(shares)s, %(price_per_share)s,
                     %(acquired_disposed_code)s, %(shares_owned_following)s, %(filing_date)s)
                on conflict (accession_number, transaction_index) do nothing
                """,
                rows,
            )
        conn.commit()
    logger.info("insider.company_done", cik=cik, **stats)
    return stats


PER_COMPANY_TIMEOUT_SECONDS = 1800  # 30 min -- raised 2026-08-28: chunks are
# now cost-bin-packed by expected Form 4 filing count (see
# scratchpad/build_cost_based_chunks.py), so a heavy company (some have
# 900+ filings in just the recent window) gets its own solo chunk instead
# of blocking 19 others -- a longer, more generous cap here just lets a
# genuinely-working heavy company actually finish instead of being cut off
# every retry with zero progress saved.


def _run_company_with_timeout(sec: "SECClient", company_id: int, cik: str) -> dict:
    """Runs one company's processing on its OWN connection, inside a worker
    thread with a hard wall-clock cap. Added 2026-08-28: found live that a
    single company (43 amendments' worth of decades-old Form 4 filings) can
    stall a whole chunk for 22+ hours despite every individual HTTP call
    already being bounded (sec_client.py: 5 attempts x up to 30s + backoff,
    a few minutes worst case) -- the retry math doesn't explain a stall that
    long, meaning something blocks in a way those bounds don't cover. Rather
    than chase the exact stuck line, this bounds the DAMAGE: if one company
    exceeds PER_COMPANY_TIMEOUT_SECONDS, we give up waiting and move on. The
    company gets its own fresh connection (not the caller's) specifically so
    an abandoned, still-running thread -- Python can't forcibly kill a
    thread -- never touches the connection the main loop keeps using for
    every other company."""
    import concurrent.futures

    from scrooner_pipeline.db.connection import get_connection

    def _work() -> dict:
        with get_connection() as company_conn:
            return update_insider_transactions_for_company(company_conn, sec, company_id, cik)

    # Deliberately NOT a `with` block: ThreadPoolExecutor.__exit__ calls
    # shutdown(wait=True), which blocks until the submitted task actually
    # finishes -- exactly the unbounded wait this whole function exists to
    # avoid. found live 2026-08-28: the timeout never fired because of this
    # exact bug, still stuck past the 300s cap. A pool is created fresh per
    # call and deliberately abandoned (never shut down) on timeout -- the
    # orphaned thread keeps running against its own dedicated connection,
    # harmless to everything else, and disappears whenever this whole CLI
    # process is eventually restarted between chunk retries.
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = pool.submit(_work)
    return future.result(timeout=PER_COMPANY_TIMEOUT_SECONDS)


def update_insider_transactions(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    totals = {"considered": 0, "ok": 0, "no_company": 0, "errored": 0, "timed_out": 0, "transactions": 0}
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
                logger.warning("insider.company_timed_out", cik=cik, timeout_seconds=PER_COMPANY_TIMEOUT_SECONDS)
                totals["timed_out"] += 1
                continue
            except Exception:
                # Added 2026-08-27: one company's unhandled error (e.g. the
                # accession/transaction_index duplicate this same commit
                # adds an ON CONFLICT guard for) used to crash the entire
                # CLI invocation -- with no per-company boundary, that meant
                # every OTHER company in the same chunk had to be
                # reprocessed on every retry too, and a genuinely
                # deterministic bug (not a transient one) made the whole
                # chunk permanently unable to succeed. Same lesson as
                # restatements.py: one company's failure must not cost every
                # other company in the batch its own progress.
                conn.rollback()
                logger.exception("insider.company_failed", cik=cik)
                totals["errored"] += 1
                continue
            totals["ok"] += 1
            totals["transactions"] += stats["transactions"]
    logger.info("insider.done", **totals)
    return totals
