"""P1 (entity.shared_accession_primary_filer@1, RF-21) reload: candidates,
decisions and a REVIEWED DRY-RUN before any write. Nothing here has been run
against the population; the SEC step needs scrooner-4d's slot (one fetch
process, the shared limiter, declared User-Agent).

  candidates   read-only DB. Accessions that look shared: (a) the accession's
               filer-ID prefix is the CIK of ANOTHER core.company row than the
               one that owns the filing; (b) companies that stopped filing 10-K/
               10-Q but still file 8-Ks (the victim signature). Prefix is only a
               CANDIDATE signal; the decision never uses it.
  decide       SEC fetch (limited, cached in memory only, nothing written but
               the JSON). For each accession: the submission header FILER blocks
               and the instance's default-context dei:EntityCentralIndexKey
               -> decisions.json (rule normalizer/registrant.decide_primary).
  plan         read-only DB. Reads decisions.json, prints per accession what
               exists today and what apply would do, writes the backup of every
               fact row apply would delete, prints the plan sha256.
  apply        THE ONLY WRITER. Needs --apply, --plan-sha (from a plan you
               reviewed) and the backup. One transaction: persist the registrant
               rows, move the filings, delete the wrong-company facts. Then
               recompute the primary and holder CIKs with the flag on
               (see normalizer/registrant_reload.py).

Examples (read-only first):
  python scripts/p1_reload_dryrun.py candidates --out cands.json
  python scripts/p1_reload_dryrun.py decide --accessions 0000065984-26-000174,0000065984-26-000283 --cik-for 0000065984 --out decisions.json
  python scripts/p1_reload_dryrun.py plan --decisions decisions.json --backup backups/p1_facts.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.normalizer.registrant import (
    AmbiguousDeiCik,
    PrimaryFilerDecision,
    accession_prefix_cik,
    decide_primary,
    extract_default_context_cik,
    parse_header_filers,
)
from scrooner_pipeline.normalizer.registrant_reload import (
    apply_reload,
    persist_decisions,
    plan_reload,
    write_backup,
)

MAX_CLIENT_CONNECTIONS = 14
ARCHIVE = "https://www.sec.gov/Archives/edgar/data"


def _connect(read_only: bool, timeout_ms: int = 20000) -> psycopg.Connection:
    conn = psycopg.connect(settings.database_url, connect_timeout=20)
    if read_only:
        conn.execute("set default_transaction_read_only = on")
    conn.execute(f"set statement_timeout = {int(timeout_ms)}")
    n = conn.execute(
        "select count(*) from pg_stat_activity where backend_type = 'client backend'"
    ).fetchone()[0]
    conn.commit()
    if n > MAX_CLIENT_CONNECTIONS:
        raise SystemExit(
            f"ABORT: {n} client connections (limit {MAX_CLIENT_CONNECTIONS})"
        )
    return conn


def cmd_candidates(args: argparse.Namespace) -> int:
    conn = _connect(read_only=True)
    out: dict[str, list] = {
        "prefix_other_company": [],
        "stopped_periodic_still_files_8k": [],
    }
    with conn.cursor() as cur:
        # (a) owner's CIK differs from the accession prefix and the prefix is another company
        cur.execute(
            """
            select fl.accession_number, owner.cik, pref.cik, fl.form, fl.filing_date
            from core.filing fl
            join core.company owner on owner.id = fl.company_id
            join core.company pref on pref.cik = lpad(split_part(fl.accession_number, '-', 1), 10, '0')
            where fl.form in ('10-K','10-K/A','10-Q','10-Q/A')
              and fl.filing_date >= %s
              and pref.id <> owner.id
            order by fl.filing_date desc
            """,
            (args.since,),
        )
        out["prefix_other_company"] = [list(map(str, r)) for r in cur.fetchall()]
        # (b) victim signature
        cur.execute(
            """
            select c.cik, c.company_name, c.status, max(fl.filing_date) filter (where fl.form in ('10-K','10-Q')) last_periodic,
                   max(fl.filing_date) filter (where fl.form = '8-K') last_8k
            from core.company c join core.filing fl on fl.company_id = c.id
            where c.status in ('stale','unknown')
            group by c.cik, c.company_name, c.status
            having max(fl.filing_date) filter (where fl.form = '8-K') >= %s
               and coalesce(max(fl.filing_date) filter (where fl.form in ('10-K','10-Q')), date '1900-01-01') < %s
            order by 5 desc
            """,
            (args.since, args.since),
        )
        out["stopped_periodic_still_files_8k"] = [
            list(map(str, r)) for r in cur.fetchall()
        ]
    conn.close()
    Path(args.out).write_text(json.dumps(out, indent=1))
    print({k: len(v) for k, v in out.items()})
    return 0


def _fetch_decision(sec, cik_for: str, acc: str) -> dict:
    base = f"{ARCHIVE}/{int(cik_for)}/{acc.replace('-', '')}"
    header = sec.get(f"{base}/{acc}-index-headers.html").text
    filers = parse_header_filers(header)
    index = sec.get_json(f"{base}/index.json")
    names = [i["name"] for i in index["directory"]["item"]]
    instance = next((n for n in names if n.endswith("_htm.xml")), None)
    dei, note = None, None
    if instance is None:
        # inline-only filing: the primary document is the iXBRL
        main = next((n for n in names if re.search(r"-\d{8}\.htm$", n)), None)
        instance = main
    if instance is not None:
        try:
            dei = extract_default_context_cik(sec.get(f"{base}/{instance}").content)
        except AmbiguousDeiCik as exc:
            note = f"ambiguous: {exc}"
        except Exception as exc:  # noqa: BLE001 - recorded, decision will quarantine
            note = f"instance unreadable: {exc!r}"[:200]
    d = decide_primary(acc, dei, filers)
    if note and not d.quarantined:
        d = decide_primary(
            acc, None, filers
        )  # unreadable instance never silently passes a shared accession
    return {
        "accession_number": d.accession_number,
        "registrant_ciks": list(d.registrant_ciks),
        "dei_default_cik": d.dei_default_cik,
        "header_first_filer_cik": d.header_first_filer_cik,
        "primary_cik": d.primary_cik,
        "shared": d.shared,
        "quarantine_reason": d.quarantine_reason
        if not note
        else f"{d.quarantine_reason or ''} {note}".strip(),
        "fetched_instance": instance,
        "note": note,
    }


def cmd_decide(args: argparse.Namespace) -> int:
    from scrooner_pipeline.common.sec_client import SECClient

    accessions = [a for a in args.accessions.split(",") if a]
    if len(accessions) > args.max_accessions:
        raise SystemExit(
            f"{len(accessions)} accessions > --max-accessions {args.max_accessions}"
        )
    out = []
    with SECClient() as sec:
        for acc in accessions:
            cik_for = args.cik_for or accession_prefix_cik(acc)
            out.append(_fetch_decision(sec, cik_for, acc))
            print(acc, out[-1]["primary_cik"], out[-1]["quarantine_reason"])
    Path(args.out).write_text(json.dumps(out, indent=1))
    return 0


def _load_decisions(path: str) -> list[PrimaryFilerDecision]:
    rows = json.loads(Path(path).read_text())
    return [
        decide_primary(
            r["accession_number"], r["dei_default_cik"], r["registrant_ciks"]
        )
        for r in rows
    ]


def _plan_sha(plans) -> str:
    blob = json.dumps([p.__dict__ for p in plans], sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def cmd_plan(args: argparse.Namespace) -> int:
    decisions = _load_decisions(args.decisions)
    conn = _connect(read_only=True, timeout_ms=60000)
    plans = plan_reload(conn, decisions)
    n = write_backup(conn, plans, Path(args.backup))
    conn.close()
    for p in plans:
        print(
            p.accession_number,
            "primary",
            p.primary_cik,
            "quarantined" if p.quarantined else "",
            "| owner",
            p.filing_owner_company_id,
            "| facts",
            p.facts_under_owner,
            "| delete",
            p.facts_to_delete,
            "|",
            "; ".join(p.actions),
            "| BLOCKERS:",
            p.blockers,
        )
    print(f"backup rows: {n} -> {args.backup}")
    print("plan sha256:", _plan_sha(plans))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    if not args.apply:
        raise SystemExit("refusing: pass --apply (and a reviewed --plan-sha)")
    decisions = _load_decisions(args.decisions)
    conn = _connect(read_only=False, timeout_ms=120000)
    plans = plan_reload(conn, decisions)
    if _plan_sha(plans) != args.plan_sha:
        raise SystemExit("plan changed since review: re-run `plan` and review again")
    try:
        persist_decisions(conn, decisions)
        stats = apply_reload(conn, plans, Path(args.backup))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    print(stats)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidates")
    c.add_argument("--out", required=True)
    c.add_argument("--since", default="2024-01-01")
    c.set_defaults(fn=cmd_candidates)
    d = sub.add_parser("decide")
    d.add_argument("--accessions", required=True)
    d.add_argument(
        "--cik-for", help="CIK whose archive path is used (default: accession prefix)"
    )
    d.add_argument("--out", required=True)
    d.add_argument("--max-accessions", type=int, default=60)
    d.set_defaults(fn=cmd_decide)
    p = sub.add_parser("plan")
    p.add_argument("--decisions", required=True)
    p.add_argument("--backup", required=True)
    p.set_defaults(fn=cmd_plan)
    a = sub.add_parser("apply")
    a.add_argument("--decisions", required=True)
    a.add_argument("--backup", required=True)
    a.add_argument("--plan-sha", required=True)
    a.add_argument("--apply", action="store_true")
    a.set_defaults(fn=cmd_apply)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
