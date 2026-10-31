"""Rollback rehearsal for shared_accession_apply.py on a SCRATCH database.

Read-only on production: exports the post-apply rows that the before-image's
selection covers (core.filing for the moved accessions, core.filing_registrant,
core.fact of the primaries and of the owners on the moved filings,
analytics.canonical_fact and analytics.company_stock_split of the affected
companies) plus the rows their foreign keys need (core.company, core.period,
core.concept, core.unit, raw.sec_companyfacts, raw.sec_submissions,
analytics.canonical_concept), and loads them into the scratch database with
their original ids. Then `rollback` of the real driver runs against the
scratch database and its digest check decides. Every step is logged.

usage: DATABASE_URL=<prod> SCRATCH_URL=<scratch> python shared_accession_rehearsal.py <backup_dir> <log_path>
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_accession_apply import live_digests, read_backup  # noqa: E402


def log(fh, msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def copy_rows(
    src: psycopg.Connection, dst: psycopg.Connection, table: str, where: str, params, fh
) -> int:
    cols = [
        r[0]
        for r in src.execute(
            "select column_name from information_schema.columns where table_schema=%s and table_name=%s order by ordinal_position",
            tuple(table.split(".")),
        ).fetchall()
    ]
    # self-referencing keys may point outside the selection: nulled on copy (logged)
    select_cols = [
        "null::bigint as " + c
        if (table, c)
        in {("core.fact", "supersedes_fact_id"), ("core.filing", "amends_filing_id")}
        else c
        for c in cols
    ]
    rows = src.execute(
        f"select {', '.join(select_cols)} from {table} where {where}", params
    ).fetchall()
    rows = [
        tuple(Jsonb(v) if isinstance(v, dict) else v for v in r) for r in rows
    ]  # jsonb columns
    if rows:
        with dst.cursor() as cur:
            cur.executemany(
                f"insert into {table} ({', '.join(cols)}) overriding system value values ({', '.join(['%s'] * len(cols))}) on conflict do nothing",
                rows,
            )
    log(fh, f"  {table}: {len(rows)} rows copied")
    return len(rows)


def main(backup_dir: Path, log_path: Path) -> int:
    manifest, img = read_backup(backup_dir)
    accs = manifest["accessions"]
    fids = manifest["filing_ids"]
    cids = manifest["affected_company_ids"]
    prim = manifest["primary_company_ids"]
    owners = manifest["owner_company_ids_with_facts"]
    with (
        log_path.open("a") as fh,
        psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=30) as src,
        psycopg.connect(os.environ["SCRATCH_URL"]) as dst,
    ):
        src.read_only = True
        src.execute("set statement_timeout = '10min'")
        log(
            fh,
            f"rehearsal of before-image {backup_dir} (plan {manifest['plan_digest'][:16]}, {manifest['moves']} moves)",
        )
        log(
            fh,
            "production is read-only in this session; scratch = "
            + os.environ["SCRATCH_URL"].split("@")[-1],
        )

        # clean the scratch tables we load into: DELETE in dependency order (a
        # TRUNCATE ... CASCADE reaches analytics.cell_evidence, whose append-only
        # trigger rejects it); empty tables are skipped so no trigger fires.
        def clear(table: str, seen: set[str]) -> None:
            if table in seen:
                return
            seen.add(table)
            schema, name = table.split(".")
            deps = dst.execute(
                """
                select distinct n.nspname || '.' || c.relname
                from pg_constraint k
                join pg_class c on c.oid = k.conrelid
                join pg_namespace n on n.oid = c.relnamespace
                where k.contype = 'f' and k.confrelid = (%s)::regclass
                """,
                (table,),
            ).fetchall()
            for (dep,) in deps:
                clear(dep, seen)
            if dst.execute(f"select count(*) from {table}").fetchone()[0]:
                dst.execute(f"delete from {table}")
                log(fh, f"  cleared {table}")

        seen: set[str] = set()
        for t in (
            "core.company",
            "analytics.canonical_concept",
            "core.unit",
            "core.concept",
            "raw.sec_companyfacts",
            "raw.sec_submissions",
            "raw.collector_runs",
        ):
            clear(t, seen)
        dst.commit()
        log(fh, "scratch tables emptied")
        # FK parents first
        registrant_cids = [
            r[0]
            for r in src.execute(
                "select distinct company_id from core.filing_registrant where accession_number = any(%s) and company_id is not null",
                (accs,),
            ).fetchall()
        ]
        company_ids = sorted(
            set(cids) | {r["company_id"] for r in img["filing"]} | set(registrant_cids)
        )
        copy_rows(src, dst, "core.company", "id = any(%s)", (company_ids,), fh)
        copy_rows(src, dst, "analytics.canonical_concept", "true", (), fh)
        copy_rows(src, dst, "core.unit", "true", (), fh)
        fact_where = (
            "company_id = any(%s) or (filing_id = any(%s) and company_id = any(%s))"
        )
        concept_ids = [
            r[0]
            for r in src.execute(
                f"select distinct concept_id from core.fact where {fact_where}",
                (prim, fids, owners),
            ).fetchall()
        ]
        copy_rows(src, dst, "core.concept", "id = any(%s)", (concept_ids,), fh)
        raw_ids = [
            r[0]
            for r in src.execute(
                f"select distinct raw_object_id from core.fact where {fact_where}",
                (prim, fids, owners),
            ).fetchall()
        ]
        sub_ids = [
            r[0]
            for r in src.execute(
                "select distinct raw_submission_id from core.filing where company_id = any(%s) and raw_submission_id is not null",
                (company_ids,),
            ).fetchall()
        ]
        run_ids = [
            r[0]
            for r in src.execute(
                "select distinct run_id from raw.sec_companyfacts where id = any(%s) and run_id is not null "
                "union select distinct run_id from raw.sec_submissions where id = any(%s) and run_id is not null",
                (raw_ids, sub_ids),
            ).fetchall()
        ]
        copy_rows(src, dst, "raw.collector_runs", "id = any(%s)", (run_ids,), fh)
        copy_rows(src, dst, "raw.sec_companyfacts", "id = any(%s)", (raw_ids,), fh)
        copy_rows(src, dst, "raw.sec_submissions", "id = any(%s)", (sub_ids,), fh)
        copy_rows(src, dst, "core.period", "company_id = any(%s)", (company_ids,), fh)
        copy_rows(
            src,
            dst,
            "core.filing",
            "company_id = any(%s) or accession_number = any(%s)",
            (company_ids, accs),
            fh,
        )
        # the rows under test, post-apply state
        copy_rows(
            src,
            dst,
            "core.filing_registrant",
            "accession_number = any(%s)",
            (accs,),
            fh,
        )
        copy_rows(src, dst, "core.fact", fact_where, (prim, fids, owners), fh)
        copy_rows(
            src, dst, "analytics.canonical_fact", "company_id = any(%s)", (cids,), fh
        )
        copy_rows(
            src,
            dst,
            "analytics.company_stock_split",
            "company_id = any(%s)",
            (cids,),
            fh,
        )
        dst.commit()
        before = live_digests(dst, manifest)
        diff = [k for k, v in before.items() if v != manifest["tables"][k]["sha256"]]
        log(
            fh,
            f"scratch post-apply digests vs before-image: differ for {diff} (expected: filing, fact, canonical_fact at least)",
        )
    # the real rollback, same code path as production
    env = dict(os.environ, DATABASE_URL=os.environ["SCRATCH_URL"])
    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent / "shared_accession_apply.py"),
        "rollback",
        "--backup-dir",
        str(backup_dir),
    ]
    with log_path.open("a") as fh:
        log(fh, "running: " + " ".join(cmd[1:]))
        out = subprocess.run(cmd, capture_output=True, text=True, env=env)
        for line in (out.stdout + out.stderr).splitlines():
            if not line.startswith("{"):
                fh.write(line + "\n")
        log(fh, f"rollback exit code {out.returncode}")
        with psycopg.connect(os.environ["SCRATCH_URL"]) as dst:
            after = live_digests(dst, manifest)
        bad = [k for k, v in after.items() if v != manifest["tables"][k]["sha256"]]
        log(
            fh,
            f"post-rollback digests equal the before-image for all {len(after)} tables: {not bad}"
            + (f" (differ: {bad})" if bad else ""),
        )
        return 0 if out.returncode == 0 and not bad else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
