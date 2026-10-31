"""Flag-OFF equivalence of the companyfacts stage before and after the B9 refactor.

normalize_facts_for_cik now delegates to normalize_payload. This runs BOTH
versions (facts.py from a given git ref, and the branch's) for the same CIKs
against the same production read state and compares the core.fact rows each
would write, byte for byte (JSON of every row, sorted). Nothing is written: the
cursor wrapper captures the `insert into core.fact` batch instead of executing
it, every other statement runs inside a transaction that is rolled back.

usage: PYTHONPATH=src python scripts/b9_equivalence_check.py <git_ref> <cik,cik,...> <log_path>
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from decimal import Decimal
from pathlib import Path

import psycopg

from scrooner_pipeline.collector.storage import SupabaseStorageClient


class _CaptureCursor:
    def __init__(self, cur, sink):
        self._cur, self._sink = cur, sink

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self._cur.__exit__(*exc)

    def executemany(self, sql, rows):
        if "insert into core.fact" in " ".join(sql.split()).lower():
            self._sink.extend(dict(r) for r in rows)
            return
        return self._cur.executemany(sql, rows)

    def __getattr__(self, name):
        return getattr(self._cur, name)


class _CaptureConnection:
    def __init__(self, conn, sink):
        self._conn, self._sink = conn, sink

    def cursor(self):
        return _CaptureCursor(self._conn.cursor(), self._sink)

    def commit(self):
        pass  # captured run: never commit

    def __getattr__(self, name):
        return getattr(self._conn, name)


def _load_facts_module(ref: str):
    src = subprocess.run(
        ["git", "show", f"{ref}:pipeline/src/scrooner_pipeline/normalizer/facts.py"],
        capture_output=True,
        text=True,
        check=True,
        cwd=Path(__file__).resolve().parents[2],
    ).stdout
    tmp = Path(tempfile.mkdtemp()) / "facts_at_ref.py"
    tmp.write_text(src)
    spec = importlib.util.spec_from_file_location("facts_at_ref", tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _digest(rows: list[dict]) -> tuple[str, int]:
    def default(o):
        if isinstance(o, Decimal):
            return str(o)
        raise TypeError(type(o))

    lines = sorted(json.dumps(r, sort_keys=True, default=default) for r in rows)
    h = hashlib.sha256()
    for line in lines:
        h.update(line.encode())
        h.update(b"\n")
    return h.hexdigest(), len(lines)


def main(ref: str, ciks: list[str], log_path: Path) -> int:
    from scrooner_pipeline.normalizer import facts as facts_new

    facts_old = _load_facts_module(ref)
    all_equal = True
    with log_path.open("a") as fh, SupabaseStorageClient() as storage:

        def log(msg):
            line = f"{time.strftime('%H:%M:%S')} {msg}"
            print(line, flush=True)
            fh.write(line + "\n")
            fh.flush()

        log(
            f"equivalence check: facts.py at {ref} vs branch; {len(ciks)} CIKs; captured rows, nothing written"
        )
        for cik in ciks:
            conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=30)
            conn.execute("set statement_timeout = '10min'")
            try:
                old_rows: list[dict] = []
                new_rows: list[dict] = []
                r_old = facts_old.normalize_facts_for_cik(
                    storage, _CaptureConnection(conn, old_rows), cik
                )
                r_new = facts_new.normalize_facts_for_cik(
                    storage, _CaptureConnection(conn, new_rows), cik
                )
                d_old, n_old = _digest(old_rows)
                d_new, n_new = _digest(new_rows)
                same = d_old == d_new and n_old == n_new
                all_equal &= same
                log(
                    f"  {cik}: old {n_old} rows {d_old[:16]} | new {n_new} rows {d_new[:16]} | {'IDENTICAL' if same else 'DIFFERENT'} | stats old={ {k: v for k, v in r_old.items() if k != 'cik'} } new={ {k: v for k, v in r_new.items() if k != 'cik'} }"
                )
            except Exception as exc:  # noqa: BLE001
                all_equal = False
                log(f"  {cik}: ERROR {exc!r}")
            finally:
                conn.rollback()
                conn.close()
        log(f"result: {'ALL IDENTICAL' if all_equal else 'DIFFERENCES FOUND'}")
    return 0 if all_equal else 1


if __name__ == "__main__":
    sys.exit(
        main(
            sys.argv[1],
            [c.strip().zfill(10) for c in sys.argv[2].split(",")],
            Path(sys.argv[3]),
        )
    )
