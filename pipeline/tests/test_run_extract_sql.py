"""scripts/ci/run_extract_sql.py on a tiny fixture (fake connection; no database)."""
import importlib.util
import json
import pathlib
from decimal import Decimal

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("run_extract_sql", ROOT / "scripts/ci/run_extract_sql.py")
rx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rx)


class Cur:
    def __init__(self, conn):
        self.c = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.c.log.append(sql)
        self.rows = self.c.ro if sql.startswith("show") else ([] if sql.startswith("set") else self.c.rows)
        self.description = [("a",), ("v",), ("d",)]

    def fetchone(self):
        return self.rows[0]

    def fetchall(self):
        return list(self.rows)

    def __iter__(self):
        return iter(self.rows)


class Conn:
    def __init__(self, rows, ro="on"):
        self.rows, self.ro, self.log = rows, [(ro,)], []

    def cursor(self):
        return Cur(self)

    def rollback(self):
        pass


def _sql(d, name, body="select 1"):
    (d / name).write_text("-- c; with semicolon\nset statement_timeout='55s';\n" + body + ";")


def test_run_dir_appends_batches_decimal_safe(tmp_path):
    _sql(tmp_path, "lines-00.sql")
    _sql(tmp_path, "lines-01.sql")
    _sql(tmp_path, "bs-00.sql")
    conn = Conn([("0000-1", Decimal("1.10"), __import__("datetime").date(2020, 1, 2))])
    counts = rx.run_dir(conn, str(tmp_path))
    assert counts == {"lines": 2, "bs": 1}
    rows = [json.loads(line) for line in (tmp_path / "lines.jsonl").read_text().splitlines()]
    assert rows == [{"a": "0000-1", "v": "1.10", "d": "2020-01-02"}] * 2
    assert "set statement_timeout='55s';" in conn.log
    assert all(not q.rstrip().endswith(";") for q in conn.log if q.startswith("select"))


def test_refuses_float_and_non_read_only_and_long_timeout(tmp_path):
    _sql(tmp_path, "lines-00.sql")
    with pytest.raises(TypeError):
        rx.run_dir(Conn([("a", 1.5, None)]), str(tmp_path))
    with pytest.raises(SystemExit):
        rx.run_dir(Conn([], ro="off"), str(tmp_path))
    (tmp_path / "x-00.sql").write_text("set statement_timeout='1200s';\nselect 1;")
    with pytest.raises(SystemExit):
        rx.split_sql((tmp_path / "x-00.sql").read_text())


def test_ciks_and_manifest(tmp_path):
    p = tmp_path / "c.csv"
    p.write_text("ticker,cik\nA,0000064803\nB,1652044\nC,0000064803\n")
    assert rx.ciks_from_csv(str(p)) == ["64803", "1652044"]
    q = tmp_path / "d.csv"
    q.write_text("company_id\n7\n9\n")
    conn = Conn([("1730168",), ("64803",)])
    assert rx.ciks_from_csv(str(q), lambda: conn) == ["64803", "1730168"]
    (tmp_path / "filings.json").write_text("[1,2]")
    (tmp_path / "lines.jsonl").write_text("{}\n{}\n{}\n")
    m = rx.manifest(str(tmp_path), "9", "abc", "64803,1652044")
    assert m["files"]["filings.json"]["rows"] == 2 and m["files"]["lines.jsonl"]["rows"] == 3
    assert m["n_ciks"] == 2 and len(m["files"]["lines.jsonl"]["sha256"]) == 64
