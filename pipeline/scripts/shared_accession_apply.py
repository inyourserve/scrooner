"""Apply / roll back rule entity.shared_accession_primary_filer@1 with a before-image.

Modes (default is `plan`, which writes NOTHING):

  plan      build the plan from the dry-run checkpoints (--workdir, see
            shared_accession_dryrun.py; missing phases are re-run), print what
            would move, the affected companies and the follow-on commands.
  backup    plan + write the before-image to --backup-dir: the core.filing rows
            that would change owner, the core.filing_registrant rows for those
            accessions, every core.fact row of the primaries (a re-normalize is
            delete-then-reinsert) and of the current owners on the moving
            filings, and every analytics.canonical_fact row of those companies.
            A manifest carries a sha256 digest per table and a digest of the
            plan. Read-only on the database.
  apply     requires the rule ON (SCROONER_RULES_ENABLED), --yes-apply, and a
            backup whose digests still match the live rows (abort otherwise).
            ONE transaction: upsert core.filing_registrant, move
            core.filing.company_id to the primary. Prints the follow-on commands.
            Does not touch core.fact / analytics.canonical_fact: the follow-on
            `normalize facts` does that, and the before-image covers it.
  rollback  from --backup-dir, ONE transaction: restore core.filing owners,
            put core.filing_registrant back exactly as backed up, delete the
            current core.fact / analytics.canonical_fact rows of the affected
            companies and re-insert the backed-up rows with their original ids,
            then re-read and check every digest against the manifest.
            Out of scope (stated, not hidden): core.period rows a re-normalize
            added stay; other analytics.* tables keyed by company
            (metric_value, period_gap, coverage...) are rebuilt by the normal
            recompute chain, not restored here.

Single Postgres connection; statement_timeout set per session.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_accession_dryrun import phase_a, phase_b, phase_c  # noqa: E402

from scrooner_pipeline.common.rule_flags import rule_enabled  # noqa: E402
from scrooner_pipeline.normalizer import shared_accession as sa  # noqa: E402

TABLES = {
    "filing": ("core.filing", "id"),
    "filing_registrant": ("core.filing_registrant", "id"),
    "fact": ("core.fact", "id"),
    "canonical_fact": ("analytics.canonical_fact", "id"),
}


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def _json_default(o):
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    raise TypeError(type(o))


def dumps(obj) -> str:
    return json.dumps(obj, default=_json_default, sort_keys=True, separators=(",", ":"))


def digest(rows: list[dict]) -> str:
    h = hashlib.sha256()
    for r in sorted(rows, key=lambda r: r["id"]):
        h.update(dumps(r).encode())
        h.update(b"\n")
    return h.hexdigest()


def columns(conn, table: str) -> list[str]:
    schema, name = table.split(".")
    return [
        r[0]
        for r in conn.execute(
            "select column_name from information_schema.columns where table_schema=%s and table_name=%s order by ordinal_position",
            (schema, name),
        ).fetchall()
    ]


def fetch(conn, table: str, where: str, params) -> list[dict]:
    cols = columns(conn, table)
    rows = conn.execute(
        f"select {', '.join(cols)} from {table} where {where}", params
    ).fetchall()
    return [dict(zip(cols, r)) for r in rows]


# ---- plan --------------------------------------------------------------------


class Plan:
    def __init__(
        self, decisions, moves, id_by_cik, primary_ids, owner_ids_with_facts, owners
    ):
        self.decisions = decisions
        self.moves = (
            moves  # (accession, filing_id, from_company_id, to_company_id, basis)
        )
        self.id_by_cik = id_by_cik
        self.primary_ids = primary_ids
        self.owner_ids_with_facts = owner_ids_with_facts
        self.owners = owners  # accession -> (filing_id, company_id)

    @property
    def affected_company_ids(self) -> list[int]:
        return sorted(set(self.primary_ids) | set(self.owner_ids_with_facts))

    @property
    def accessions(self) -> list[str]:
        return sorted(m[0] for m in self.moves)

    @property
    def filing_ids(self) -> list[int]:
        return sorted(m[1] for m in self.moves)

    def digest(self) -> str:
        return hashlib.sha256(
            dumps([list(m) for m in sorted(self.moves)]).encode()
        ).hexdigest()


def build(conn, workdir: Path, threads: int, skip_headers: bool) -> Plan:
    companies = conn.execute("select id, cik from core.company").fetchall()
    id_by_cik = {cik: cid for cid, cik in companies}
    filings_by_cik = phase_a(conn, workdir, threads)
    shared = sa.registrants_by_accession(filings_by_cik)
    wanted: dict[str, set[str]] = defaultdict(set)
    for acc, regs in shared.items():
        for cik in regs:
            wanted[cik].add(acc)
    carried = phase_b(conn, workdir, wanted, threads)
    carriers: dict[str, set[str]] = defaultdict(set)
    for cik, c in carried.items():
        for acc in c:
            carriers[acc].add(cik)
    headers = {}
    if not skip_headers:
        need = sorted(
            a
            for a, regs in shared.items()
            if next(iter(regs.values())) in sa.PERIODIC_FORMS or a in carriers
        )
        headers = phase_c(workdir, need)
    decisions = sa.plan_decisions(shared, carriers, headers)
    owners: dict[str, tuple[int, int]] = {}
    accs = sorted(shared)
    for i in range(0, len(accs), 2000):
        for acc, fid, cid in conn.execute(
            "select accession_number, id, company_id from core.filing where accession_number = any(%s)",
            (accs[i : i + 2000],),
        ).fetchall():
            owners[acc] = (fid, cid)
    moves = []
    for d in decisions:
        if d.primary_cik is None:
            continue
        pid = id_by_cik.get(d.primary_cik)
        cur = owners.get(d.accession_number)
        if pid is None or cur is None or cur[1] == pid:
            continue
        moves.append((d.accession_number, cur[0], cur[1], pid, d.basis))
    primary_ids = sorted({m[3] for m in moves})
    fids = [m[1] for m in moves]
    owner_ids_with_facts = (
        sorted(
            r[0]
            for r in conn.execute(
                "select distinct f.company_id from core.fact f join core.filing fl on fl.id = f.filing_id "
                "where f.filing_id = any(%s) and f.company_id = fl.company_id",
                (fids,),
            ).fetchall()
        )
        if fids
        else []
    )
    return Plan(decisions, moves, id_by_cik, primary_ids, owner_ids_with_facts, owners)


def describe(conn, plan: Plan) -> None:
    names = dict(
        conn.execute(
            "select id, coalesce(primary_ticker, '') || ' ' || company_name from core.company where id = any(%s)",
            (plan.affected_company_ids,),
        ).fetchall()
    )
    log(
        f"plan digest {plan.digest()[:16]}: {len(plan.moves)} core.filing rows change owner; "
        f"{sum(1 for d in plan.decisions if d.primary_cik)} primaries, "
        f"{sum(1 for d in plan.decisions if not d.primary_cik)} quarantined"
    )
    by_to: dict[int, int] = defaultdict(int)
    for m in plan.moves:
        by_to[m[3]] += 1
    for cid, n in sorted(by_to.items(), key=lambda kv: -kv[1]):
        log(f"  gains {n:3d} filings: {cid} {names.get(cid, '?')}")
    for cid in plan.owner_ids_with_facts:
        log(f"  holds facts on a moving filing: {cid} {names.get(cid, '?')}")


def follow_on(conn, plan: Plan) -> str:
    ciks = dict(
        conn.execute(
            "select id, cik from core.company where id = any(%s)",
            (plan.affected_company_ids,),
        ).fetchall()
    )
    primaries = ",".join(ciks[i] for i in plan.primary_ids)
    owners = ",".join(ciks[i] for i in plan.owner_ids_with_facts)
    everyone = ",".join(ciks[i] for i in plan.affected_company_ids)
    on = f"SCROONER_RULES_ENABLED={sa.RULE_ID}"
    lines = [
        "# Follow-on, in this order, each with the rule ON (the facts stage needs the primary link):",
        f"{on} uv run scrooner-normalize periods --ciks {primaries}",
        f"{on} uv run scrooner-normalize facts --ciks {everyone}   # primaries gain their combined filings; the "
        f"{len(plan.owner_ids_with_facts)} owners drop the parent's quarter",
        f"{on} uv run scrooner-normalize dedupe --ciks {everyone}",
        f"{on} uv run scrooner-normalize restatements --ciks {everyone}",
        f"{on} uv run scrooner-normalize conflict-latest-filed --ciks {everyone}",
        f"{on} uv run scrooner-normalize derive-interim-quarters --ciks {everyone}",
        f"{on} uv run scrooner-normalize derive-q4 --ciks {everyone}",
        f"{on} uv run scrooner-company-master update-status --ciks {everyone}",
        f"uv run scrooner-map resolve-facts --ciks {everyone}",
        f"uv run scrooner-map resolve-concept-fallbacks --ciks {everyone}",
        f"uv run scrooner-map resolve-statement-fallbacks --ciks {everyone}   # --ciks needs work/engineering/nightly-resolve-stages",
        f"uv run scrooner-map resolve-conflict-fills --ciks {everyone}        # same branch",
        f"uv run scrooner-map calculate --ciks {everyone}",
        f"uv run scrooner-map build-coverage-matrix --ciks {everyone}",
        f"# owners that held the parent's numbers: {owners}",
    ]
    return "\n".join(lines)


# ---- backup ------------------------------------------------------------------


def before_image(conn, plan: Plan) -> dict[str, list[dict]]:
    accs, fids, cids = plan.accessions, plan.filing_ids, plan.affected_company_ids
    img = {
        "filing": fetch(conn, "core.filing", "accession_number = any(%s)", (accs,)),
        "filing_registrant": fetch(
            conn, "core.filing_registrant", "accession_number = any(%s)", (accs,)
        ),
        "fact": fetch(
            conn,
            "core.fact",
            "company_id = any(%s) or (filing_id = any(%s) and company_id = any(%s))",
            (plan.primary_ids, fids, plan.owner_ids_with_facts),
        ),
        "canonical_fact": fetch(
            conn, "analytics.canonical_fact", "company_id = any(%s)", (cids,)
        ),
    }
    return img


def write_backup(backup_dir: Path, plan: Plan, img: dict[str, list[dict]]) -> dict:
    backup_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "rule_id": sa.RULE_ID,
        "taken_at": datetime.now().isoformat(timespec="seconds"),
        "plan_digest": plan.digest(),
        "moves": len(plan.moves),
        "affected_company_ids": plan.affected_company_ids,
        "primary_company_ids": plan.primary_ids,
        "owner_company_ids_with_facts": plan.owner_ids_with_facts,
        "accessions": plan.accessions,
        "filing_ids": plan.filing_ids,
        "tables": {},
    }
    for key, rows in img.items():
        path = backup_dir / f"{key}.jsonl"
        with path.open("w") as fh:
            for r in sorted(rows, key=lambda r: r["id"]):
                fh.write(dumps(r) + "\n")
        manifest["tables"][key] = {
            "rows": len(rows),
            "sha256": digest(rows),
            "file": path.name,
        }
    (backup_dir / "moves.jsonl").write_text(
        "".join(
            dumps({"accession": a, "filing_id": f, "from": c, "to": p, "basis": b})
            + "\n"
            for a, f, c, p, b in sorted(plan.moves)
        )
    )
    (backup_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def read_backup(backup_dir: Path) -> tuple[dict, dict[str, list[dict]]]:
    manifest = json.loads((backup_dir / "manifest.json").read_text())
    img = {}
    for key, meta in manifest["tables"].items():
        rows = [json.loads(l) for l in (backup_dir / meta["file"]).open()]
        if digest(rows) != meta["sha256"]:
            raise SystemExit(
                f"backup file {meta['file']} does not match its manifest digest"
            )
        img[key] = rows
    return manifest, img


def live_digests(conn, manifest: dict) -> dict[str, str]:
    accs = manifest["accessions"]
    fids = manifest["filing_ids"]
    return {
        "filing": digest(
            fetch(conn, "core.filing", "accession_number = any(%s)", (accs,))
        ),
        "filing_registrant": digest(
            fetch(conn, "core.filing_registrant", "accession_number = any(%s)", (accs,))
        ),
        "fact": digest(
            fetch(
                conn,
                "core.fact",
                "company_id = any(%s) or (filing_id = any(%s) and company_id = any(%s))",
                (
                    manifest["primary_company_ids"],
                    fids,
                    manifest["owner_company_ids_with_facts"],
                ),
            )
        ),
        "canonical_fact": digest(
            fetch(
                conn,
                "analytics.canonical_fact",
                "company_id = any(%s)",
                (manifest["affected_company_ids"],),
            )
        ),
    }


def check_digests(conn, manifest: dict, what: str) -> None:
    live = live_digests(conn, manifest)
    bad = [k for k, v in live.items() if v != manifest["tables"][k]["sha256"]]
    if bad:
        raise SystemExit(
            f"{what}: live rows differ from the before-image for {bad}; refusing"
        )
    log(f"{what}: all 4 digests match the before-image")


# ---- apply / rollback --------------------------------------------------------


def apply(conn, plan: Plan, manifest: dict) -> dict:
    if not rule_enabled(sa.RULE_ID):
        raise SystemExit(
            f"{sa.RULE_ID} is not ON (SCROONER_RULES_ENABLED); refusing to apply"
        )
    if plan.digest() != manifest["plan_digest"]:
        raise SystemExit(
            "the plan differs from the one the before-image was taken for; re-run backup"
        )
    check_digests(conn, manifest, "pre-apply")
    # one transaction: sa.apply_decisions issues both executemany calls then one commit
    out = sa.apply_decisions(conn, plan.decisions, plan.id_by_cik)
    moved = conn.execute(
        "select count(*) from core.filing f join core.filing_registrant r "
        "on r.accession_number = f.accession_number and r.role = 'primary' "
        "where f.accession_number = any(%s) and f.company_id = r.company_id",
        (plan.accessions,),
    ).fetchone()[0]
    out["filings_now_owned_by_primary"] = moved
    if moved != len(plan.moves):
        raise SystemExit(
            f"post-apply check failed: {moved} of {len(plan.moves)} filings owned by their primary"
        )
    return out


def _reinsert(conn, table: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    cols = list(rows[0].keys())
    sql = (
        f"insert into {table} ({', '.join(cols)}) overriding system value values "
        f"({', '.join('%(' + c + ')s' for c in cols)})"
    )
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def rollback(conn, backup_dir: Path) -> dict:
    manifest, img = read_backup(backup_dir)
    accs = manifest["accessions"]
    cids = manifest["affected_company_ids"]
    fids = manifest["filing_ids"]
    stats = {}
    with conn.transaction():
        # 1. filing owners back
        with conn.cursor() as cur:
            cur.executemany(
                "update core.filing set company_id = %(company_id)s where accession_number = %(accession_number)s",
                [
                    {
                        "company_id": r["company_id"],
                        "accession_number": r["accession_number"],
                    }
                    for r in img["filing"]
                ],
            )
        stats["filings_restored"] = len(img["filing"])
        # 2. registrant rows exactly as before (usually: none)
        conn.execute(
            "delete from core.filing_registrant where accession_number = any(%s)",
            (accs,),
        )
        stats["registrant_rows_restored"] = _reinsert(
            conn, "core.filing_registrant", img["filing_registrant"]
        )
        # 3. analytics rows of the affected companies, then facts (canonical_fact has no FK to fact,
        #    but company_stock_split.source_fact_id does: clear it for these companies first)
        conn.execute(
            "delete from analytics.company_stock_split where company_id = any(%s)",
            (cids,),
        )
        conn.execute(
            "delete from analytics.canonical_fact where company_id = any(%s)", (cids,)
        )
        conn.execute(
            "delete from core.fact where company_id = any(%s) or (filing_id = any(%s) and company_id = any(%s))",
            (
                manifest["primary_company_ids"],
                fids,
                manifest["owner_company_ids_with_facts"],
            ),
        )
        stats["facts_restored"] = _reinsert(conn, "core.fact", img["fact"])
        stats["canonical_facts_restored"] = _reinsert(
            conn, "analytics.canonical_fact", img["canonical_fact"]
        )
        check_digests(conn, manifest, "post-rollback")
    return stats


# ---- main --------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "mode",
        choices=["plan", "backup", "apply", "rollback"],
        nargs="?",
        default="plan",
    )
    ap.add_argument(
        "--workdir", help="dry-run checkpoints (shared_accession_dryrun.py --workdir)"
    )
    ap.add_argument("--backup-dir", help="before-image directory")
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--skip-headers", action="store_true")
    ap.add_argument("--yes-apply", action="store_true", help="required for apply")
    ap.add_argument("--statement-timeout", default="10min")
    args = ap.parse_args()

    conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=30)
    conn.execute(f"set statement_timeout = '{args.statement_timeout}'")
    conn.commit()
    try:
        if args.mode == "rollback":
            if not args.backup_dir:
                raise SystemExit("--backup-dir is required")
            stats = rollback(conn, Path(args.backup_dir))
            log(f"rollback done: {stats}")
            return 0
        if not args.workdir:
            raise SystemExit("--workdir is required")
        if args.mode in ("plan", "backup"):
            conn.read_only = True
        plan = build(conn, Path(args.workdir), args.threads, args.skip_headers)
        describe(conn, plan)
        if args.mode == "plan":
            print(follow_on(conn, plan))
            log("plan mode: nothing written")
            return 0
        if not args.backup_dir:
            raise SystemExit("--backup-dir is required")
        if args.mode == "backup":
            manifest = write_backup(
                Path(args.backup_dir), plan, before_image(conn, plan)
            )
            log(
                "before-image written: "
                + json.dumps({k: v["rows"] for k, v in manifest["tables"].items()})
            )
            log("backup mode: nothing written to the database")
            return 0
        # apply
        if not args.yes_apply:
            raise SystemExit("apply needs --yes-apply")
        manifest, _img = read_backup(Path(args.backup_dir))
        out = apply(conn, plan, manifest)
        log(f"APPLIED: {out}")
        print(follow_on(conn, plan))
        print(
            f"# rollback: python scripts/shared_accession_apply.py rollback --backup-dir {args.backup_dir}"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
