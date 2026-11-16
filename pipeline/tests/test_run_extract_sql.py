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


class QueryCanceled(Exception):
    pass


class Cur:
    def __init__(self, conn):
        self.c = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.c.log.append(sql)
        if sql.startswith("set statement_timeout"):
            self.c.timeout = int(sql.split("'")[1].rstrip("s"))
        elif not sql.startswith("show") and self.c.fail and self.c.fail(sql, self.c.timeout):
            raise QueryCanceled("canceling statement due to statement timeout")
        self.rows = self.c.ro if sql.startswith("show") else ([] if sql.startswith("set") else self.c.rows)
        self.description = [("a",), ("v",), ("d",)]

    def fetchone(self):
        return self.rows[0]

    def fetchall(self):
        return list(self.rows)

    def __iter__(self):
        return iter(self.rows)


class Conn:
    def __init__(self, rows, ro="on", fail=None):
        self.rows, self.ro, self.log, self.fail, self.timeout = rows, [(ro,)], [], fail, None

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


def _batch(d, name, ciks, secs=55):
    (d / name).write_text(f"set statement_timeout='{secs}s';\nselect {','.join(ciks)} where cik::bigint in ({','.join(ciks)});")


def _regen(kind, cik):
    return f"set statement_timeout='55s';\nselect {cik} where cik::bigint in ({cik});"


def test_timeout_resplits_per_cik_and_retries_doubled(tmp_path):
    _batch(tmp_path, "lines-00.sql", ["1", "2", "3"])
    _batch(tmp_path, "lines-01.sql", ["4"])

    # the 3-CIK batch times out; CIK 2 times out alone at 55s but passes at the 600s retry floor
    def fail(q, t):
        return "in (1,2,3)" in q or ("in (2)" in q and t == 55)
    conn = Conn([("x", "1", "d")], fail=fail)
    counts = rx.run_dir(conn, str(tmp_path), regen=_regen)
    assert counts == {"lines": 4}  # 3 per-CIK units + the next batch, appended to one file
    assert len((tmp_path / "lines.jsonl").read_text().splitlines()) == 4
    r = json.loads((tmp_path / "retries.json").read_text())
    assert [(x["cik"], x["outcome"], x["retry_timeout_s"]) for x in r] == [
        ("1", "ok_alone", None), ("2", "ok_doubled", 600), ("3", "ok_alone", None)]
    assert rx.manifest(str(tmp_path), "1", "s", "1,2,3,4")["retries"] == r


def test_single_cik_still_timing_out_fails_naming_it_and_writes_nothing(tmp_path):
    _batch(tmp_path, "lines-00.sql", ["1", "2"])
    conn = Conn([("x", "1", "d")], fail=lambda q, t: "in (1,2)" in q or "in (2)" in q)
    with pytest.raises(SystemExit) as e:
        rx.run_dir(conn, str(tmp_path), regen=_regen)
    assert "CIK 2" in str(e.value) and "600s" in str(e.value)
    assert not (tmp_path / "lines.jsonl").exists()


def test_doubled_timeout_is_capped_and_other_errors_are_not_retried(tmp_path):
    assert rx.with_timeout("set statement_timeout='600s';\nselect 1;", 1200).startswith("set statement_timeout='900s';")
    assert rx.with_timeout("select 1;", 110).startswith("set statement_timeout='110s';")
    _batch(tmp_path, "lines-00.sql", ["1", "2"])

    def boom(q, t):
        raise ValueError("not a timeout")
    with pytest.raises(ValueError):
        rx.run_dir(Conn([], fail=boom), str(tmp_path), regen=_regen)


def _cf_batch(d, name, cik):
    # the shape of the notes/face queries: the company_filings CTE selects filings f of `co`
    (d / name).write_text(
        "set statement_timeout='55s';\nwith company_filings as (select f.id from core.company co join fsn.filing f on true"
        f" where co.cik::bigint in ({cik}) and true) select {cik} where cik::bigint in ({cik});"
    )


def test_period_slices_partition_the_company_filings_cte():
    sql = "with c as (select 1 from x f where co.cik::bigint in (831001) and f.ok) select 1"
    sl = rx.period_slices(sql, bounds=("2016-01-01", "2020-01-01"))
    assert [b for b, _ in sl] == [(None, "2016-01-01"), ("2016-01-01", "2020-01-01"), ("2020-01-01", None)]
    assert "in (831001) and f.period < date '2016-01-01' and f.ok" in sl[0][1]
    assert "in (831001) and f.period >= date '2016-01-01' and f.period < date '2020-01-01' and" in sl[1][1]
    assert sl[2][1].count("f.period") == 1 and "f.period >= date '2020-01-01'" in sl[2][1]
    # not sliceable: no company_filings anchor (lines/bs queries) or more than one company
    assert rx.period_slices("select 1 where cik::bigint in (1)") == []
    assert rx.period_slices("where co.cik::bigint in (1,2)") == []


def test_one_company_timing_out_alone_runs_per_period_slice(tmp_path):
    # run 43833278049: Citigroup (831001) face timed out alone at 600s; the slices finish at the 900s ceiling
    _cf_batch(tmp_path, "face-00.sql", "831001")
    conn = Conn([("x", "1", "d")], fail=lambda q, t: "f.period" not in q)
    counts = rx.run_dir(conn, str(tmp_path), regen=_regen)
    assert counts == {"face": len(rx.SLICE_BOUNDS) + 1}  # one fake row per slice
    r = json.loads((tmp_path / "retries.json").read_text())
    assert r[0]["outcome"] == "ok_sliced" and r[0]["slice_timeout_s"] == 900 and len(r[0]["slices"]) == len(rx.SLICE_BOUNDS) + 1


def test_a_slice_that_still_times_out_fails_naming_the_cik_and_writes_nothing(tmp_path):
    _cf_batch(tmp_path, "face-00.sql", "831001")
    conn = Conn([("x", "1", "d")], fail=lambda q, t: "f.period" not in q or "date '2018-01-01' and f.period <" in q)
    with pytest.raises(SystemExit) as e:
        rx.run_dir(conn, str(tmp_path), regen=_regen)
    assert "CIK 831001" in str(e.value)
    assert not (tmp_path / "face.jsonl").exists()
