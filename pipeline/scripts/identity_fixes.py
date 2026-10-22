"""Identity fix list (identity.cik_name_ticker@1): plan (read-only), apply, reverse.
The list is closed and lives in company_master/identity_fixes.py. DRY-RUN FIRST.

  python scripts/identity_fixes.py plan                      # prints every edit old -> new and the plan sha256
  python scripts/identity_fixes.py apply --apply --plan-sha <sha from a plan you reviewed>
  python scripts/identity_fixes.py reverse --apply --run-id <uuid printed by apply>

apply is one transaction: every edit and its core.company_identity_audit row, or
nothing. Needs migration 0100 applied (the audit table). Not run by the author.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.company_master import identity_fixes as fx


def _conn(read_only: bool) -> psycopg.Connection:
    conn = psycopg.connect(settings.database_url, connect_timeout=20)
    if read_only:
        conn.execute("set default_transaction_read_only = on")
    conn.execute("set statement_timeout = 60000")
    n = conn.execute(
        "select count(*) from pg_stat_activity where backend_type = 'client backend'"
    ).fetchone()[0]
    conn.commit()
    if n > 14:
        raise SystemExit(f"ABORT: {n} client connections (limit 14)")
    return conn


def _sha(plans) -> str:
    return hashlib.sha256(
        json.dumps([p.row() for p in plans], sort_keys=True, default=str).encode()
    ).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    a = sub.add_parser("apply")
    a.add_argument("--apply", action="store_true")
    a.add_argument("--plan-sha", required=True)
    r = sub.add_parser("reverse")
    r.add_argument("--apply", action="store_true")
    r.add_argument("--run-id", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "plan":
        conn = _conn(True)
        plans = fx.plan_fixes(conn)
        for p in plans:
            print(
                f"{p.fix.cik} {p.fix.audit_field:18} [{p.fix.evidence_level}] {p.action:16} {p.old_value!r} -> {p.new_value!r}"
            )
            print(f"    {p.fix.accession} | {p.fix.locator} | {p.fix.note}")
        print("plan sha256:", _sha(plans))
        return 0
    if not args.apply:
        raise SystemExit("refusing: pass --apply")
    conn = _conn(False)
    try:
        if args.cmd == "apply":
            plans = fx.plan_fixes(conn)
            if _sha(plans) != args.plan_sha:
                raise SystemExit("plan changed since review: run `plan` again")
            print(fx.apply_fixes(conn, plans))
        else:
            print({"reversed": fx.reverse_run(conn, args.run_id)})
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
