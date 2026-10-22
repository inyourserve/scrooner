"""Identity invariant against per-CIK SEC submissions (identity.cik_name_ticker@1).
READ-ONLY on the database; SEC fetches go through common/sec_client.py (declared
User-Agent, shared limiter; one process). Writes a CSV of CANDIDATE findings, never
an edit. Needs scrooner-4d's slot for a population run; --ciks for a few.

  python scripts/identity_check.py --ciks 0000906107,0002041610 --out findings.csv
  python scripts/identity_check.py --active-top 1000 --out findings.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.company_master.identity_check import (
    SecIdentity,
    StoredIdentity,
    compare_identity,
)

EVENT_FORMS = {
    "25",
    "25-NSE",
    "15-12G",
    "15-12B",
    "15-15D",
    "15F-12G",
    "15F-12B",
    "15F-15D",
}


def sec_identity(sec: SECClient, cik: str) -> SecIdentity:
    doc = sec.get_json(f"https://data.sec.gov/submissions/CIK{cik}.json")
    rec = doc["filings"]["recent"]
    items = rec.get("items", [""] * len(rec["form"]))
    events = [
        {
            "accessionNumber": rec["accessionNumber"][i],
            "form": f,
            "filingDate": rec["filingDate"][i],
            "items": items[i],
        }
        for i, f in enumerate(rec["form"])
        if f in EVENT_FORMS or f == "8-K"
    ]
    return SecIdentity.from_submissions({**doc, "events": events})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--ciks")
    ap.add_argument(
        "--active-top",
        type=int,
        default=0,
        help="N active companies by id (smoke); 0 = use --ciks",
    )
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    conn = psycopg.connect(settings.database_url, connect_timeout=20)
    conn.execute("set default_transaction_read_only = on")
    conn.execute("set statement_timeout = 60000")
    ciks = [c for c in (args.ciks or "").split(",") if c]
    with conn.cursor() as cur:
        if ciks:
            cur.execute("select id, cik from core.company where cik = any(%s)", (ciks,))
        else:
            cur.execute(
                "select id, cik from core.company where status = 'active' order by id limit %s",
                (args.active_top,),
            )
        targets = cur.fetchall()
    out = csv.writer(open(args.out, "w", newline=""))
    out.writerow(["cik", "kind", "detail", "accessions"])
    n = 0
    with SECClient() as sec:
        for company_id, cik in targets:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select c.company_name, c.display_name, c.primary_ticker, c.status,
                           (select max(filing_date) from core.filing f where f.company_id = c.id and f.form in ('10-K','10-Q','10-K/A','10-Q/A'))
                    from core.company c where c.id = %s
                    """,
                    (company_id,),
                )
                name, display, ticker, status, last_periodic = cur.fetchone()
                subsidiary = False
                cur.execute("select to_regclass('core.filing_registrant') is not null")
                if cur.fetchone()[0]:  # migration 0100 applied
                    cur.execute(
                        "select exists (select 1 from core.filing_registrant where registrant_cik = %s and role = 'co_registrant')",
                        (cik,),
                    )
                    subsidiary = cur.fetchone()[0]
            conn.commit()
            stored = StoredIdentity(
                cik, name, display, ticker, status, last_periodic, bool(subsidiary)
            )
            for f in compare_identity(stored, sec_identity(sec, cik)):
                out.writerow([f.cik, f.kind, f.detail, ";".join(f.accessions)])
                n += 1
    print(
        f"{len(targets)} companies, {n} candidate findings -> {args.out} ({date.today()})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
