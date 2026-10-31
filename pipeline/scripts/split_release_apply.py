"""WRITE split re-base release 1 from its package. Release Manager only, after
the founder's typed approval; never run from a builder session.

Refuses to start unless split.event_basis@1 and pershare.never_derive@1 are
both ON in the environment, the package digest matches its .sha256 file, and
--run-id is given (the rollback handle: canonical_archive.restore_run). Each
company is written in its own transaction only when it still matches its
packaged cells (share_basis.package_mismatches); refused companies are printed
with their reasons and left untouched.
usage: split_release_apply.py <package_dir> --run-id <id> [--companies 1,2,...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import psycopg

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.common.config import settings
from scrooner_pipeline.corporate_actions import share_basis as sb

RELEASE = "split_release_1"


def load_package(pkg_dir: Path) -> dict[int, dict[tuple[str, int], sb.PackageCell]]:
    body = (pkg_dir / f"{RELEASE}_cells.jsonl").read_bytes()
    want = (pkg_dir / f"{RELEASE}_cells.sha256").read_text().split()[0]
    if hashlib.sha256(body).hexdigest() != want:
        raise SystemExit("refusing: package digest does not match its .sha256 file")
    pkg: dict[int, dict[tuple[str, int], sb.PackageCell]] = defaultdict(dict)
    for line in body.decode().splitlines():
        r = json.loads(line)
        if r["release"] != RELEASE:
            raise SystemExit(f"refusing: row of release {r['release']!r}")
        old = Decimal(r["old_value"]) if r["old_value"] is not None else None
        new = Decimal(r["new_value"]) if r["new_value"] is not None else None
        pkg[r["company_id"]][(r["concept"], r["period_id"])] = sb.PackageCell(
            r["concept"], r["period_id"], old, new, r["status"]
        )
    return pkg


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("package_dir", type=Path)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--companies", default="")
    args = ap.parse_args(argv)
    for rule in (sb.RULE_ID, sb.RU1_RULE_ID):
        if not rule_flags.rule_enabled(rule):
            raise SystemExit(f"refusing: {rule} is not ON ({rule_flags.ENV_ENABLED})")
    pkg = load_package(args.package_dir)
    ids = [int(x) for x in args.companies.split(",") if x] or sorted(pkg)
    with psycopg.connect(
        settings.database_url, application_name="split_release_apply"
    ) as conn:
        conn.execute("set statement_timeout = '120s'")
        out = sb.run_split_rebase(conn, ids, run_id=args.run_id, package=pkg)
    print(
        json.dumps(
            {
                "companies": out["companies"],
                "written": out["companies"] - len(out["refused"]),
                "refused": out["refused"],
            },
            indent=1,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
