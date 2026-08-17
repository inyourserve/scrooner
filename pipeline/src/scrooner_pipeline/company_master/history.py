"""Stage 4a-2 -- Name history and ticker-change dating (doc 13, Sec 2).

Two independent things, both read-only against `raw`, both write only to
`core`:

1. core.company_name_history -- a direct 1:1 capture of the base
   submissions payload's own `formerNames` array, plus the current name as
   the still-open final interval (effective_to=null).

2. core.listing.effective_from/effective_to/source -- ticker-change dating,
   via two signals, neither perfect, both better than guessing:
   - forward detection: compare the two most recent raw.sec_submissions
     snapshots' tickers arrays for a CIK. A ticker appearing in the newer
     snapshot but not the older one gets effective_from = the newer
     snapshot's fetched_at (an exact, observed date). A ticker present in
     the older snapshot but missing from the newer one gets effective_to
     the same way. This only detects changes inside the observation
     window between two stored snapshots -- it cannot date a change that
     happened entirely before the earliest snapshot this project has.
   - former-names proxy: for a ticker with no forward-observed change,
     if the company has at least one closed formerNames interval, the
     ticker's effective_from is proxied to that interval's `to` date
     (source='former_names_backfill') -- a real EDGAR-sourced date, but a
     proxy: a name change and a ticker change aren't guaranteed to
     coincide, so this is never presented as an exact ticker-change date.
   - everything else: effective_from stays null, source='unknown' -- an
     honest gap, not a guess.
"""

import json
from datetime import date, datetime

import psycopg
import structlog

from scrooner_pipeline.collector.storage import SupabaseStorageClient, strip_bucket_prefix

logger = structlog.get_logger()


def _base_submission_snapshots(conn: psycopg.Connection, cik: str) -> list[tuple]:
    """(fetched_at, storage_path) for every distinct BASE-file snapshot of
    this CIK, oldest first -- the full observation history this stage's
    forward-detection signal compares across."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select fetched_at, storage_path
            from raw.sec_submissions
            where cik = %s
              and storage_path not like '%%-submissions-%%.json'
            order by fetched_at
            """,
            (cik,),
        )
        return cur.fetchall()


def _load_json(storage: SupabaseStorageClient, storage_path: str) -> dict:
    raw_bytes = storage.download(strip_bucket_prefix(storage_path))
    return json.loads(raw_bytes)


def _parse_edgar_datetime(value: str | None) -> date | None:
    if not value:
        return None
    # formerNames dates come as e.g. "2021-12-08T05:00:00.000Z"
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


def build_name_history(payload: dict) -> list[dict]:
    """Every formerNames interval, plus the current name as the still-open
    final one.

    Found live 2026-08-16: RDDT's and JPM's formerNames arrays each end with
    an entry whose name is byte-for-byte IDENTICAL to the current name (e.g.
    RDDT: "Reddit, Inc." -> "Reddit, Inc.", `to` = the fetch date) -- not a
    real rename, an EDGAR record-touch artifact. Skipped by exact-string
    equality against the current name -- this correctly keeps AAPL's real
    (if minor) formal registrant-name updates ("APPLE INC" -> "Apple Inc.",
    which differ in case/punctuation, not byte-identical) while dropping the
    artifact rows."""
    current_name = payload["name"]
    rows = []
    for entry in payload.get("formerNames") or []:
        if entry["name"] == current_name:
            continue
        rows.append(
            {
                "company_name": entry["name"],
                "effective_from": _parse_edgar_datetime(entry.get("from")),
                "effective_to": _parse_edgar_datetime(entry.get("to")),
            }
        )
    current_from = None
    if rows:
        # Current name interval opens where the last former name's interval closed.
        current_from = max((r["effective_to"] for r in rows if r["effective_to"]), default=None)
    rows.append({"company_name": payload["name"], "effective_from": current_from, "effective_to": None})
    return rows


def build_ticker_dating(
    snapshots: list[tuple[str, dict]], current_tickers: list[str]
) -> dict[str, dict]:
    """snapshots: (fetched_at, payload) oldest-first, ALL stored snapshots
    for this CIK. Returns ticker -> {effective_from, effective_to, source}.
    """
    ticker_sets: list[tuple] = []
    for fetched_at, payload in snapshots:
        tickers = set(payload.get("tickers") or [])
        ticker_sets.append((fetched_at, tickers))

    result: dict[str, dict] = {t: {"effective_from": None, "effective_to": None, "source": "unknown"} for t in current_tickers}

    # Forward detection: walk consecutive snapshot pairs. A ticker newly
    # appearing gets effective_from = the newer snapshot's fetched_at date;
    # a ticker disappearing gets effective_to the same way.
    for i in range(1, len(ticker_sets)):
        prev_fetched_at, prev_tickers = ticker_sets[i - 1]
        cur_fetched_at, cur_tickers = ticker_sets[i]
        newly_appeared = cur_tickers - prev_tickers
        newly_gone = prev_tickers - cur_tickers
        for t in newly_appeared:
            if t in result and result[t]["effective_from"] is None:
                result[t]["effective_from"] = cur_fetched_at.date()
                result[t]["source"] = "submissions_snapshot"
        for t in newly_gone:
            if t in result and result[t]["effective_to"] is None:
                result[t]["effective_to"] = cur_fetched_at.date()
                result[t]["source"] = "submissions_snapshot"

    return result


# A name-change date is NOT a reliable proxy for a ticker-change date in
# general -- found live 2026-08-16 by applying it universally and checking
# the result against every golden company, not just the one it was designed
# for. AAPL (real 2007 "Computer" drop, real 2019 capitalization
# normalization) and NKE never changed their ticker at all, yet both got
# proxied to a plausible-looking but WRONG date; RDDT and JPM got proxied to
# today's fetch date entirely, from an EDGAR formerNames artifact (see
# build_name_history's docstring). 27 of 38 golden-set listing rows were
# wrong before this was caught. The premise only holds when a rename and a
# ticker change are independently known to be the same corporate action --
# not inferable from core.company_name_history alone. So: detection stays
# automatic, but application requires explicit, reviewed confirmation --
# same discipline as Mapper's approved/provisional/rejected concept_mapping
# states (doc 11), not a blanket default.
CONFIRMED_TICKER_PROXY_CIKS = {
    # Block/Square: SQ -> XYZ ticker change was publicly announced
    # concurrently with the Square, Inc. -> Block, Inc. rename (Dec 2021) --
    # independently verifiable public record, not inferred from this
    # payload alone.
    "0001512673",
}


def candidate_ticker_proxy_date(name_history: list[dict]) -> date | None:
    """The most recent closed formerNames interval's `to` date -- a
    CANDIDATE ticker-change proxy, not applied unless the CIK is in
    CONFIRMED_TICKER_PROXY_CIKS. Always computed and logged so a future
    reviewer has something concrete to confirm or reject, per doc 11's own
    'rank automatically, accept manually' pattern."""
    closed_intervals = [r["effective_to"] for r in name_history if r["effective_to"] is not None]
    return max(closed_intervals) if closed_intervals else None


def apply_confirmed_ticker_proxy(ticker_dating: dict[str, dict], cik: str, candidate_date: date | None) -> None:
    if candidate_date is None or cik not in CONFIRMED_TICKER_PROXY_CIKS:
        return
    for ticker, info in ticker_dating.items():
        if info["effective_from"] is None:
            info["effective_from"] = candidate_date
            info["source"] = "former_names_backfill"


def upsert_name_history(conn: psycopg.Connection, company_id: int, rows: list[dict]) -> int:
    """Delete-then-reinsert per company, not ON CONFLICT -- found live
    2026-08-16: SQL's NULL != NULL means `on conflict (company_id,
    company_name, effective_from)` never matches a row whose
    effective_from is null (every company with no former-names history at
    all, e.g. MSFT/TSM/ARCC/GOOGL/RDDT's single current-name row), so a
    rerun silently duplicated it instead of updating in place. Same fix
    already proven in Mapper's resolve.py/calculate.py -- delete-then-
    reinsert per company sidesteps composite-key-with-nullable-column
    upsert entirely rather than working around it with a NULL sentinel."""
    with conn.cursor() as cur:
        cur.execute("delete from core.company_name_history where company_id = %s", (company_id,))
        if rows:
            cur.executemany(
                """
                insert into core.company_name_history (company_id, company_name, effective_from, effective_to)
                values (%(company_id)s, %(company_name)s, %(effective_from)s, %(effective_to)s)
                """,
                [{"company_id": company_id, **r} for r in rows],
            )
    conn.commit()
    return len(rows)


def update_listing_dating(conn: psycopg.Connection, company_id: int, ticker_dating: dict[str, dict]) -> int:
    if not ticker_dating:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            """
            update core.listing
               set effective_from = %(effective_from)s,
                   effective_to = %(effective_to)s,
                   source = %(source)s
             where company_id = %(company_id)s and ticker = %(ticker)s
            """,
            [{"company_id": company_id, "ticker": t, **info} for t, info in ticker_dating.items()],
        )
    conn.commit()
    return len(ticker_dating)


def update_history_for_cik(storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str) -> dict:
    snapshot_paths = _base_submission_snapshots(conn, cik)
    if not snapshot_paths:
        return {"cik": cik, "status": "no_data"}

    snapshots = [(fetched_at, _load_json(storage, path)) for fetched_at, path in snapshot_paths]
    latest_payload = snapshots[-1][1]

    with conn.cursor() as cur:
        cur.execute("select id from core.company where cik = %s", (cik,))
        row = cur.fetchone()
        if row is None:
            return {"cik": cik, "status": "no_company"}
        company_id = row[0]

    name_history = build_name_history(latest_payload)
    current_tickers = latest_payload.get("tickers") or []
    ticker_dating = build_ticker_dating(snapshots, current_tickers)
    candidate_date = candidate_ticker_proxy_date(name_history)
    apply_confirmed_ticker_proxy(ticker_dating, cik, candidate_date)

    name_rows = upsert_name_history(conn, company_id, name_history)
    listing_rows = update_listing_dating(conn, company_id, ticker_dating)

    logger.info(
        "company_master.history.done",
        cik=cik,
        company_id=company_id,
        name_history_rows=name_rows,
        listing_rows=listing_rows,
        snapshots_compared=len(snapshots),
        ticker_proxy_candidate_date=str(candidate_date) if candidate_date else None,
        ticker_proxy_applied=cik in CONFIRMED_TICKER_PROXY_CIKS,
    )
    return {"cik": cik, "status": "ok", "name_history_rows": name_rows, "listing_rows": listing_rows}


def update_history(conn: psycopg.Connection, ciks: set[str]) -> dict:
    stats = {"considered": 0, "ok": 0, "no_data": 0, "no_company": 0}
    with SupabaseStorageClient() as storage:
        for cik in sorted(ciks):
            stats["considered"] += 1
            result = update_history_for_cik(storage, conn, cik)
            stats[result["status"]] += 1
    logger.info("company_master.history.batch_done", **stats)
    return stats
