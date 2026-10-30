"""Executor for the reviewed Storage retirement manifest (Rule S).

Spec: data-team/strategy/team/STORAGE-DELETE-DRYRUN-2026-10-25.md section 7.1.
Manifest: STORAGE-DELETE-MANIFEST-RULE-S-2026-10-25.csv.gz (columns raw_id,
cik, sha256, fetched_at, storage_path, bytes, referenced_by_core_fact,
keeper_raw_id, keeper_storage_path).

Rule S: for every (cik, sha256) one object (the latest fetched) is kept, and so
is EVERY object referenced by core.fact.raw_object_id. Everything else is a
byte-identical duplicate and may be retired. The raw.sec_companyfacts rows are
never deleted.

Modes (default is dry-run; nothing is written unless a mode says so):
  dry-run   regenerate today's plan from the database, re-check the manifest
            against it, print counts. Writes nothing.
  pilot     execute on a seeded random sample (default 500 objects).
  execute   execute everything that survives the re-check, in batches
            (default 2000). Resumable: already-retired ids are skipped.
  rollback  copy the keeper back to the retired path (server-side), verify the
            etag, remove the redirect row. By batch label or all.
Execute/pilot/rollback need --confirm and the migration 0111 table.

Safety order inside a batch (a failure stops the whole run, never skips on):
  1. referenced_among(batch) must be empty ("0 referenced", re-queried NOW);
  2. keeper and retired object must have equal etag and size;
  3. a byte sample (default 10 pairs per batch) is downloaded and its sha256
     must equal the recorded sha256 for both objects;
  4. redirect rows are written to raw.storage_object_retired FIRST;
  5. objects are deleted;
  6. absence is re-verified; the batch is appended to the JSONL ledger.

Pure planning functions are separate from IO so they are unit-tested; the IO
sits behind two small protocols (Db, Store).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import structlog

logger = structlog.get_logger()

TABLE = "raw.sec_companyfacts"
CONFIRM_TOKEN = "RETIRE-RULE-S"
BUCKET_PREFIX = "raw/"


@dataclass(frozen=True)
class Candidate:
    raw_id: int
    cik: str
    sha256: str
    storage_path: str
    bytes: int
    keeper_raw_id: int
    keeper_storage_path: str


@dataclass
class ObjectRow:
    """One raw.sec_companyfacts row joined to its Storage object (today)."""

    raw_id: int
    cik: str
    sha256: str
    fetched_at: datetime
    storage_path: str
    size: int
    etag: str


class Db(Protocol):
    def fetch_rows(self) -> list[ObjectRow]: ...
    def fetch_referenced(self) -> set[int]: ...
    def referenced_among(self, ids: list[int]) -> set[int]: ...
    def existing_paths(self, paths: list[str]) -> set[str]: ...
    def retired_ids(self) -> set[int]: ...
    def insert_retired(self, rows: list[dict]) -> None: ...
    def fetch_retired(self, batch: str | None) -> list[dict]: ...
    def delete_retired(self, raw_ids: list[int]) -> None: ...
    def table_exists(self) -> bool: ...


class Store(Protocol):
    def download(self, object_path: str) -> bytes: ...
    def delete_many(self, object_paths: list[str]) -> None: ...
    def copy(self, source_path: str, destination_path: str) -> None: ...


# ---------------------------------------------------------------- planning


def read_manifest(path: Path) -> list[Candidate]:
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", newline="") as f:  # type: ignore[operator]
        out = []
        for r in csv.DictReader(f):
            out.append(
                Candidate(
                    raw_id=int(r["raw_id"]),
                    cik=r["cik"],
                    sha256=r["sha256"],
                    storage_path=r["storage_path"],
                    bytes=int(r["bytes"]),
                    keeper_raw_id=int(r["keeper_raw_id"]),
                    keeper_storage_path=r["keeper_storage_path"],
                )
            )
    return out


def build_rule_s_plan(rows: list[ObjectRow], referenced: set[int]) -> dict[int, int]:
    """raw_id -> keeper raw_id for every object Rule S would delete today.

    Keeper of a (cik, sha256) group = the latest fetched (ties: highest id).
    An object is deletable only if it is not that keeper and not referenced
    by core.fact."""
    keeper: dict[tuple[str, str], ObjectRow] = {}
    for r in rows:
        k = (r.cik, r.sha256)
        cur = keeper.get(k)
        if cur is None or (r.fetched_at, r.raw_id) > (cur.fetched_at, cur.raw_id):
            keeper[k] = r
    plan: dict[int, int] = {}
    for r in rows:
        kept = keeper[(r.cik, r.sha256)]
        if r.raw_id == kept.raw_id or r.raw_id in referenced:
            continue
        plan[r.raw_id] = kept.raw_id
    return plan


@dataclass
class Recheck:
    approved: list[Candidate] = field(default_factory=list)
    dropped: list[tuple[int, str]] = field(default_factory=list)


def recheck_manifest(
    manifest: list[Candidate], plan: dict[int, int], rows: list[ObjectRow]
) -> Recheck:
    """Keep only manifest entries that today's plan still agrees with.

    Drop reasons (never silently): not_in_today_plan (now a keeper, now
    referenced, or no longer a duplicate), keeper_changed, object_missing,
    sha_changed, etag_size_mismatch."""
    by_id = {r.raw_id: r for r in rows}
    out = Recheck()
    for c in manifest:
        if c.raw_id not in plan:
            out.dropped.append((c.raw_id, "not_in_today_plan"))
            continue
        if plan[c.raw_id] != c.keeper_raw_id:
            out.dropped.append((c.raw_id, "keeper_changed"))
            continue
        r, k = by_id.get(c.raw_id), by_id.get(c.keeper_raw_id)
        if r is None or k is None:
            out.dropped.append((c.raw_id, "object_missing"))
            continue
        if r.sha256 != c.sha256 or k.sha256 != c.sha256 or r.cik != c.cik:
            out.dropped.append((c.raw_id, "sha_changed"))
            continue
        if (r.etag, r.size) != (k.etag, k.size):
            out.dropped.append((c.raw_id, "etag_size_mismatch"))
            continue
        out.approved.append(c)
    return out


def batches(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def pilot_sample(items: list[Candidate], n: int, seed: int) -> list[Candidate]:
    rng = random.Random(seed)
    ordered = sorted(items, key=lambda c: c.raw_id)
    return rng.sample(ordered, min(n, len(ordered)))


def _obj(path: str) -> str:
    if not path.startswith(BUCKET_PREFIX):
        raise ValueError(f"unexpected storage path {path!r}")
    return path[len(BUCKET_PREFIX) :]


# --------------------------------------------------------------- execution


class Abort(RuntimeError):
    """A safety check failed; nothing further is deleted."""


def _check_bytes(store: Store, c: Candidate, sample_rng: random.Random) -> None:
    for path in (c.storage_path, c.keeper_storage_path):
        digest = hashlib.sha256(store.download(_obj(path))).hexdigest()
        if digest != c.sha256:
            raise Abort(
                f"byte check failed raw_id={c.raw_id} path={path} "
                f"recorded={c.sha256} actual={digest}"
            )


def execute_batch(
    db: Db,
    store: Store,
    batch: list[Candidate],
    rows_by_id: dict[int, ObjectRow],
    label: str,
    sha_sample: int,
    rng: random.Random,
) -> dict:
    ids = [c.raw_id for c in batch]
    hit = db.referenced_among(ids)
    if hit:
        raise Abort(
            f"{len(hit)} object(s) are now referenced by core.fact: {sorted(hit)[:10]}"
        )
    for c in batch:
        r, k = rows_by_id.get(c.raw_id), rows_by_id.get(c.keeper_raw_id)
        if r is None or k is None or (r.etag, r.size) != (k.etag, k.size):
            raise Abort(f"etag/size check failed raw_id={c.raw_id}")
    for c in rng.sample(batch, min(sha_sample, len(batch))):
        _check_bytes(store, c, rng)

    db.insert_retired(
        [
            {
                "source_table": TABLE,
                "raw_id": c.raw_id,
                "cik": c.cik,
                "sha256": c.sha256,
                "retired_storage_path": c.storage_path,
                "keeper_raw_id": c.keeper_raw_id,
                "keeper_storage_path": c.keeper_storage_path,
                "bytes": c.bytes,
                "etag": rows_by_id[c.raw_id].etag,
                "rule": "S",
                "executor_batch": label,
            }
            for c in batch
        ]
    )
    store.delete_many([_obj(c.storage_path) for c in batch])
    still = db.existing_paths([c.storage_path for c in batch])
    if still:
        raise Abort(f"{len(still)} object(s) still present after delete in {label}")
    # the keepers must still be there
    gone = {c.keeper_storage_path for c in batch} - db.existing_paths(
        [c.keeper_storage_path for c in batch]
    )
    if gone:
        raise Abort(f"keeper(s) missing after delete in {label}: {sorted(gone)[:5]}")
    return {"batch": label, "objects": len(batch), "bytes": sum(c.bytes for c in batch)}


def run(
    db: Db,
    store: Store | None,
    manifest: list[Candidate],
    mode: str,
    *,
    batch_size: int = 2000,
    pilot_n: int = 500,
    seed: int = 7,
    sha_sample: int = 10,
    ledger: Path | None = None,
    confirm: str | None = None,
    rollback_batch: str | None = None,
    run_label: str | None = None,
) -> dict:
    if mode not in {"dry-run", "pilot", "execute", "rollback"}:
        raise ValueError(f"unknown mode {mode}")
    rows = db.fetch_rows()
    rows_by_id = {r.raw_id: r for r in rows}
    referenced = db.fetch_referenced()
    plan = build_rule_s_plan(rows, referenced)
    chk = recheck_manifest(manifest, plan, rows)
    reasons: dict[str, int] = {}
    for _id, why in chk.dropped:
        reasons[why] = reasons.get(why, 0) + 1
    already = db.retired_ids() if db.table_exists() else set()
    todo = [c for c in chk.approved if c.raw_id not in already]
    summary: dict[str, Any] = {
        "mode": mode,
        "manifest": len(manifest),
        "today_plan": len(plan),
        "today_plan_bytes": sum(rows_by_id[i].size for i in plan),
        "approved": len(chk.approved),
        "approved_bytes": sum(c.bytes for c in chk.approved),
        "dropped": len(chk.dropped),
        "dropped_reasons": reasons,
        "already_retired": len(chk.approved) - len(todo),
        "referenced_in_approved": len({c.raw_id for c in chk.approved} & referenced),
        "plan_not_in_manifest": len(set(plan) - {c.raw_id for c in manifest}),
        "executed": [],
    }
    if mode == "dry-run":
        return summary

    if confirm != CONFIRM_TOKEN:
        raise Abort(f"--confirm {CONFIRM_TOKEN} required for mode {mode}")
    if store is None:
        raise Abort("a Storage client is required")
    if not db.table_exists():
        raise Abort("raw.storage_object_retired missing: apply migration 0111 first")
    stamp = run_label or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rng = random.Random(seed)

    if mode == "rollback":
        return _rollback(db, store, rollback_batch, summary, ledger)

    if mode == "pilot":
        todo = pilot_sample(todo, pilot_n, seed)
        size = len(todo) or 1
        parts = [todo] if todo else []
        stamp = f"{stamp}-pilot"
    else:
        parts = batches(todo, batch_size)
    for i, part in enumerate(parts, start=1):
        label = f"{stamp}-b{i:04d}"
        res = execute_batch(db, store, part, rows_by_id, label, sha_sample, rng)
        summary["executed"].append(res)
        logger.info("storage_retire.batch_done", **res)
        if ledger is not None:
            with ledger.open("a") as f:
                f.write(
                    json.dumps(
                        {
                            **res,
                            "raw_ids": [c.raw_id for c in part],
                            "at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    + "\n"
                )
    return summary


def _rollback(
    db: Db, store: Store, batch_label: str | None, summary: dict, ledger: Path | None
) -> dict:
    retired = db.fetch_retired(batch_label)
    restored = 0
    for part in batches(retired, 500):
        done_ids = []
        for r in part:
            dst = _obj(r["retired_storage_path"])
            if not db.existing_paths([r["retired_storage_path"]]):
                store.copy(_obj(r["keeper_storage_path"]), dst)
            if not db.existing_paths([r["retired_storage_path"]]):
                raise Abort(f"restore failed raw_id={r['raw_id']}")
            done_ids.append(r["raw_id"])
        db.delete_retired(done_ids)
        restored += len(done_ids)
        if ledger is not None:
            with ledger.open("a") as f:
                f.write(
                    json.dumps({"rollback": batch_label, "raw_ids": done_ids}) + "\n"
                )
    summary["restored"] = restored
    return summary


# ------------------------------------------------------------ real adapters


class PgDb:
    def __init__(
        self, conn
    ) -> None:  # psycopg connection, read/write only in execute modes
        self.conn = conn

    def _q(self, sql: str, args=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, args)
            out = cur.fetchall() if cur.description else []
        self.conn.commit()
        return out

    def fetch_rows(self) -> list[ObjectRow]:
        return [
            ObjectRow(i, cik, sha, fa, sp, int(sz), et)
            for i, cik, sha, fa, sp, sz, et in self._q(
                """
                select r.id, r.cik, r.sha256, r.fetched_at, r.storage_path,
                       (o.metadata->>'size')::bigint, o.metadata->>'eTag'
                from raw.sec_companyfacts r
                join storage.objects o
                  on o.bucket_id = 'raw' and 'raw/' || o.name = r.storage_path
                """
            )
        ]

    def fetch_referenced(self) -> set[int]:
        return {
            r[0]
            for r in self._q(
                "select id from raw.sec_companyfacts r where exists "
                "(select 1 from core.fact f where f.raw_object_id = r.id)"
            )
        }

    def referenced_among(self, ids: list[int]) -> set[int]:
        return {
            r[0]
            for r in self._q(
                "select id from raw.sec_companyfacts r where id = any(%s) and exists "
                "(select 1 from core.fact f where f.raw_object_id = r.id)",
                (ids,),
            )
        }

    def existing_paths(self, paths: list[str]) -> set[str]:
        return {
            r[0]
            for r in self._q(
                "select 'raw/' || name from storage.objects "
                "where bucket_id = 'raw' and 'raw/' || name = any(%s)",
                (paths,),
            )
        }

    def table_exists(self) -> bool:
        return bool(
            self._q("select to_regclass('raw.storage_object_retired') is not null")[0][
                0
            ]
        )

    def retired_ids(self) -> set[int]:
        return {
            r[0]
            for r in self._q(
                "select raw_id from raw.storage_object_retired where source_table = %s",
                (TABLE,),
            )
        }

    def insert_retired(self, rows: list[dict]) -> None:
        with self.conn.cursor() as cur:
            cur.executemany(
                """
                insert into raw.storage_object_retired
                  (source_table, raw_id, cik, sha256, retired_storage_path, keeper_raw_id,
                   keeper_storage_path, bytes, etag, rule, executor_batch)
                values (%(source_table)s, %(raw_id)s, %(cik)s, %(sha256)s, %(retired_storage_path)s,
                        %(keeper_raw_id)s, %(keeper_storage_path)s, %(bytes)s, %(etag)s, %(rule)s,
                        %(executor_batch)s)
                on conflict (source_table, raw_id) do nothing
                """,
                rows,
            )
        self.conn.commit()

    def fetch_retired(self, batch: str | None) -> list[dict]:
        cols = [
            "raw_id",
            "retired_storage_path",
            "keeper_storage_path",
            "executor_batch",
        ]
        rows = self._q(
            "select raw_id, retired_storage_path, keeper_storage_path, executor_batch "
            "from raw.storage_object_retired where source_table = %s "
            "and (%s::text is null or executor_batch = %s) order by raw_id",
            (TABLE, batch, batch),
        )
        return [dict(zip(cols, r)) for r in rows]

    def delete_retired(self, raw_ids: list[int]) -> None:
        self._q(
            "delete from raw.storage_object_retired where source_table = %s and raw_id = any(%s)",
            (TABLE, raw_ids),
        )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument(
        "--mode", default="dry-run", choices=["dry-run", "pilot", "execute", "rollback"]
    )
    ap.add_argument("--batch-size", type=int, default=2000)
    ap.add_argument("--pilot-n", type=int, default=500)
    ap.add_argument("--sha-sample", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--ledger", type=Path, default=None)
    ap.add_argument("--rollback-batch", default=None)
    ap.add_argument("--confirm", default=None)
    args = ap.parse_args(argv)

    from scrooner_pipeline.collector.storage import SupabaseStorageClient
    from scrooner_pipeline.db.connection import get_connection

    manifest = read_manifest(args.manifest)
    with get_connection() as conn:
        conn.execute("set statement_timeout = '120s'")
        db = PgDb(conn)
        if args.mode == "dry-run":
            summary = run(db, None, manifest, "dry-run")
        else:
            with SupabaseStorageClient() as store:
                summary = run(
                    db,
                    store,
                    manifest,
                    args.mode,
                    batch_size=args.batch_size,
                    pilot_n=args.pilot_n,
                    seed=args.seed,
                    sha_sample=args.sha_sample,
                    ledger=args.ledger,
                    confirm=args.confirm,
                    rollback_batch=args.rollback_batch,
                )
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
