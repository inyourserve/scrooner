"""Ingestion detector (Data Engineer lane 2): filings with ZERO facts, filings the
index lists but `core.filing` lacks, and SEC companyfacts lag. Read-only.

Why (data-team/strategy/team/S5-derivation-history-fixability.md, doc 44):
  * 348 D1 cells sit behind a latest 10-Q/10-K that is indexed but has 0 facts
    (ABT, KO, F, GD, HUBB, HUM, OMC, FRT ...); 89 such filings in the 986 cohort
    since 2026-07-01.
  * 44 cells sit behind a latest periodic filing that is not in `core.filing` at
    all (DG, HPQ, DE, SJM, BURL, JKHY; T3 list also MDB, IREN, HEI, OLLI).
  * KO: 10-Q 0001628280-26-050503 (filed 2026-07-29) has 0 facts although the
    companyfacts object was fetched 2026-09-29.

What it does NOT do: fetch from SEC, write to any table, change a value. It reads
`core.filing`, `core.fact` (existence only), `core.company`,
`raw.sec_companyfacts` (metadata) and `raw.sec_filing_documents` (the daily-index
listing the collector stored). An optional second stage downloads OUR stored
companyfacts object from Supabase Storage (not SEC) for a bounded number of
filings to tell "SEC companyfacts does not carry the accession" from "the payload
carries it and we did not extract it".

Causes (one per filing; evidence label DATA-INFERRED unless a filing was opened):
  too_recent                      filed less than TOO_RECENT_DAYS ago; wait
  no_companyfacts_object          no raw.sec_companyfacts row for the CIK
  companyfacts_older_than_filing  newest object was fetched before the filing date
                                  -> refetch + renormalize facts
  check_payload                   object fetched after the filing; stage 2 needed
  companyfacts_lacks_accession    stage 2: payload fetched after filing has no entry
                                  with this accn -> SEC companyfacts lag (fallback reader
                                  candidate, see mapper/../filing_instance_selftest.py)
  payload_has_accession_not_extracted  stage 2: payload carries the accn but core.fact has
                                  none -> pipeline defect (normalizer), route to the owner
  not_in_core_filing              (T3) the index lists a periodic filing core.filing lacks

Nightly use: `detect_zero_fact_filings` and `detect_unindexed_filings` issue only
SELECTs (a test asserts it), take an explicit statement_timeout, and are bounded by
`since` and the periodic-form list. A reviewer reads the CSV; nothing is acted on
automatically.

CLI (from pipeline/):
  python -m scrooner_pipeline.sanity.ingestion_detector --since 2026-07-01 \
      --out /tmp/zero_fact.csv --unindexed-out /tmp/unindexed.csv --summary /tmp/ingest.json
  add --check-payload N to run stage 2 on at most N filings (downloads from our storage).
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Iterator

PERIODIC_FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-KT/A")
TOO_RECENT_DAYS = 3
DEFAULT_STATEMENT_TIMEOUT_MS = 20000

CAUSE_TOO_RECENT = "too_recent"
CAUSE_NO_OBJECT = "no_companyfacts_object"
CAUSE_OLDER = "companyfacts_older_than_filing"
CAUSE_CHECK = "check_payload"
CAUSE_LACKS = "companyfacts_lacks_accession"
CAUSE_NOT_EXTRACTED = "payload_has_accession_not_extracted"
CAUSE_NOT_INDEXED = "not_in_core_filing"


@dataclass(frozen=True)
class ZeroFactFiling:
    company_id: int
    cik: str
    ticker: str
    accession: str
    form: str
    filing_date: date
    period_of_report: date | None
    filing_row_created_at: datetime | None
    companyfacts_fetched_at: datetime | None
    companyfacts_storage_path: str | None
    cause: str


@dataclass(frozen=True)
class UnindexedFiling:
    cik: str
    ticker: str
    accession: str
    form: str
    filing_date: date
    report_date: date | None
    latest_core_periodic_date: date | None
    cause: str = CAUSE_NOT_INDEXED


@contextmanager
def _statement_timeout(conn: Any, ms: int) -> Iterator[Any]:
    """Set statement_timeout for the block and restore the caller's value."""
    with conn.cursor() as cur:
        cur.execute("show statement_timeout")
        previous = cur.fetchone()[0]
        cur.execute(f"set statement_timeout = {int(ms)}")
        try:
            yield cur
        finally:
            cur.execute(f"set statement_timeout = '{previous}'")


# ------------------------------------------------------------------ pure parts


def classify_stage1(
    filing_date: date,
    companyfacts_fetched_at: datetime | None,
    today: date,
) -> str:
    if (today - filing_date).days < TOO_RECENT_DAYS:
        return CAUSE_TOO_RECENT
    if companyfacts_fetched_at is None:
        return CAUSE_NO_OBJECT
    if companyfacts_fetched_at.date() <= filing_date:
        return CAUSE_OLDER
    return CAUSE_CHECK


def payload_accessions(payload: dict[str, Any]) -> set[str]:
    """Every accn present in a companyfacts payload (all taxonomies and units)."""
    out: set[str] = set()
    for concepts in payload.get("facts", {}).values():
        for cdata in concepts.values():
            for entries in cdata.get("units", {}).values():
                for entry in entries:
                    accn = entry.get("accn")
                    if accn:
                        out.add(accn)
    return out


def classify_stage2(accession: str, accessions_in_payload: set[str]) -> str:
    return CAUSE_NOT_EXTRACTED if accession in accessions_in_payload else CAUSE_LACKS


def summarize(
    zero: list[ZeroFactFiling], unindexed: list[UnindexedFiling]
) -> dict[str, Any]:
    return {
        "zero_fact_filings": len(zero),
        "zero_fact_companies": len({z.company_id for z in zero}),
        "zero_fact_by_cause": dict(Counter(z.cause for z in zero)),
        "zero_fact_by_form": dict(Counter(z.form for z in zero)),
        "unindexed_filings": len(unindexed),
        "unindexed_companies": len({u.cik for u in unindexed}),
        "unindexed_by_form": dict(Counter(u.form for u in unindexed)),
    }


# --------------------------------------------------------------------- SQL


CHUNK = 100


def _active_companies(cur: Any) -> list[tuple[int, str, str]]:
    cur.execute(
        "select id, cik, primary_ticker from core.company where status = 'active' order by id"
    )
    return [(i, cik, t or "") for i, cik, t in cur.fetchall()]


def _chunks(rows: list[Any], size: int = CHUNK) -> Iterator[list[Any]]:
    for i in range(0, len(rows), size):
        yield rows[i : i + size]


def detect_zero_fact_filings(
    conn: Any,
    since: date,
    today: date | None = None,
    forms: Iterable[str] = PERIODIC_FORMS,
    statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS,
) -> list[ZeroFactFiling]:
    """Periodic filings of active companies since `since` with no row in core.fact.

    Scans active companies in chunks of 100 ids (core.filing has no filing_date
    index; the company_id index keeps every statement small)."""
    today = today or date.today()
    forms = list(forms)
    out: list[ZeroFactFiling] = []
    with _statement_timeout(conn, statement_timeout_ms) as cur:
        for part in _chunks(_active_companies(cur)):
            ids = [c[0] for c in part]
            ticker = {c[0]: c[2] for c in part}
            cur.execute(
                """
                select f.company_id, c.cik, f.accession_number, f.form,
                       f.filing_date, f.period_of_report, f.created_at
                from core.filing f
                join core.company c on c.id = f.company_id
                where f.company_id = any(%s) and f.filing_date >= %s and f.form = any(%s)
                  and not exists (select 1 from core.fact x where x.filing_id = f.id)
                order by f.filing_date desc, f.accession_number
                """,
                (ids, since, forms),
            )
            filings = cur.fetchall()
            if not filings:
                continue
            ciks = sorted({r[1] for r in filings})
            cur.execute(
                """
                select distinct on (cik) cik, fetched_at, storage_path
                from raw.sec_companyfacts
                where cik = any(%s) and storage_path is not null
                order by cik, fetched_at desc
                """,
                (ciks,),
            )
            cf = {cik: (fetched, path) for cik, fetched, path in cur.fetchall()}
            for company_id, cik, accn, form, fdate, period, created in filings:
                fetched, path = cf.get(cik, (None, None))
                out.append(
                    ZeroFactFiling(
                        company_id,
                        cik,
                        ticker[company_id],
                        accn,
                        form,
                        fdate,
                        period,
                        created,
                        fetched,
                        path,
                        classify_stage1(fdate, fetched, today),
                    )
                )
    out.sort(key=lambda z: (z.filing_date, z.accession), reverse=True)
    return out


def detect_unindexed_filings(
    conn: Any,
    since: date,
    forms: Iterable[str] = PERIODIC_FORMS,
    statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS,
) -> list[UnindexedFiling]:
    """Periodic filings the stored index lists (raw.sec_filing_documents) that
    core.filing lacks, for active companies (the T3 class: DG, HPQ, DE, SJM ...)."""
    forms = list(forms)
    out: list[UnindexedFiling] = []
    with _statement_timeout(conn, statement_timeout_ms) as cur:
        for part in _chunks(_active_companies(cur)):
            by_cik = {c[1]: (c[0], c[2]) for c in part}
            cur.execute(
                """
                select d.cik, d.accession_number, d.form, d.filing_date, d.report_date
                from raw.sec_filing_documents d
                where d.cik = any(%s) and d.filing_date >= %s and d.form = any(%s)
                  and not exists (select 1 from core.filing f where f.accession_number = d.accession_number)
                order by d.filing_date desc, d.accession_number
                """,
                (list(by_cik), since, forms),
            )
            missing = cur.fetchall()
            if not missing:
                continue
            ids = sorted({by_cik[m[0]][0] for m in missing})
            cur.execute(
                """
                select f.company_id, max(f.filing_date) from core.filing f
                where f.company_id = any(%s) and f.form = any(%s) group by f.company_id
                """,
                (ids, forms),
            )
            latest = dict(cur.fetchall())
            for cik, accn, form, fdate, rdate in missing:
                company_id, ticker = by_cik[cik]
                out.append(
                    UnindexedFiling(
                        cik, ticker, accn, form, fdate, rdate, latest.get(company_id)
                    )
                )
    out.sort(key=lambda u: (u.filing_date, u.accession), reverse=True)
    return out


# ------------------------------------------------------------ stage 2 (optional)


def check_payloads(  # pragma: no cover - reads our storage bucket
    zero: list[ZeroFactFiling], limit: int, storage: Any | None = None
) -> list[ZeroFactFiling]:
    """Stage 2 for at most `limit` filings still at `check_payload`: download OUR
    stored companyfacts object once per company and look for the accession."""
    from scrooner_pipeline.collector.storage import (
        SupabaseStorageClient,
        strip_bucket_prefix,
    )

    own = storage is None
    storage = storage or SupabaseStorageClient()
    resolved: dict[str, set[str]] = {}
    out: list[ZeroFactFiling] = []
    budget = limit
    try:
        for z in zero:
            if (
                z.cause != CAUSE_CHECK
                or not z.companyfacts_storage_path
                or (budget <= 0 and z.cik not in resolved)
            ):
                out.append(z)
                continue
            if z.cik not in resolved:
                payload = json.loads(
                    storage.download(strip_bucket_prefix(z.companyfacts_storage_path))
                )
                resolved[z.cik] = payload_accessions(payload)
                budget -= 1
            out.append(
                ZeroFactFiling(
                    **{
                        **asdict(z),
                        "cause": classify_stage2(z.accession, resolved[z.cik]),
                    }
                )
            )
    finally:
        if own:
            storage.close()
    return out


# --------------------------------------------------------------------- CLI


def write_csv(path: Path, rows: list[Any]) -> None:
    if not rows:
        path.write_text("")
        return
    fields = list(asdict(rows[0]).keys())
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - database
    import psycopg

    from scrooner_pipeline.common.config import settings

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--since", default="2026-07-01")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--unindexed-out", required=True, type=Path)
    ap.add_argument("--summary", required=True, type=Path)
    ap.add_argument(
        "--check-payload",
        type=int,
        default=0,
        help="stage 2 on at most N companies' stored objects",
    )
    ap.add_argument(
        "--statement-timeout-ms", type=int, default=DEFAULT_STATEMENT_TIMEOUT_MS
    )
    ap.add_argument("--max-clients", type=int, default=14)
    args = ap.parse_args(argv)
    since = date.fromisoformat(args.since)
    conn = psycopg.connect(
        settings.database_url,
        options=f"-c default_transaction_read_only=on -c statement_timeout={args.statement_timeout_ms}",
        autocommit=True,
    )
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from pg_stat_activity where backend_type = 'client backend'"
        )
        clients = int(cur.fetchone()[0])
        if clients > args.max_clients:
            print(
                f"abort: {clients} client backends connected (limit {args.max_clients})",
                file=sys.stderr,
            )
            return 2
        cur.execute("select now()")
        watermark = cur.fetchone()[0]
    zero = detect_zero_fact_filings(
        conn, since, statement_timeout_ms=args.statement_timeout_ms
    )
    if args.check_payload:
        zero = check_payloads(zero, args.check_payload)
    unindexed = detect_unindexed_filings(
        conn, since, statement_timeout_ms=args.statement_timeout_ms
    )
    write_csv(args.out, zero)
    write_csv(args.unindexed_out, unindexed)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).resolve().parent,
    ).stdout.strip()
    summary = {
        **summarize(zero, unindexed),
        "since": str(since),
        "db_watermark": str(watermark),
        "git_sha": sha,
    }
    args.summary.write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
