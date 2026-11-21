"""Migration ledger (0131): scripts/migration_ledger.py, `check_migrations.py --live`.

Pure tests cover the parser and the compare rules; DB tests run the migration's own SQL in an isolated Postgres
clone (CI: postgres:16) and prove the constraints, the same-transaction apply, the read-only backfill probe and the
--live check end to end, invoked the way CI/humans invoke the scripts (subprocess)."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import psycopg
import pytest

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "pipeline" / "db"
LEDGER_SQL = next(iter(list(DB.glob("pending/0131_*.sql")) + list(DB.glob("migrations/0131_*.sql"))))

_spec = importlib.util.spec_from_file_location("migration_ledger", ROOT / "scripts" / "migration_ledger.py")
ml = importlib.util.module_from_spec(_spec)
sys.modules["migration_ledger"] = ml
_spec.loader.exec_module(ml)


def test_parse_objects_finds_creates_and_ignores_comments_and_strings():
    sql = """
    -- create table fake.comment_table (x int);
    create schema if not exists ops;
    create table if not exists ops.a (id int);
    create or replace view ops.v as select 'create table fake.in_string' as s;
    create unique index if not exists a_idx on ops.a (id);
    create or replace function ops.f() returns int language sql as $$ select 1 $$;
    alter table ops.a add column if not exists extra text, add column other int;
    """
    o = ml.parse_objects(sql)
    assert o.schemas == ["ops"]
    assert o.relations == ["ops.a", "ops.v"]
    assert o.indexes == [("ops", "a_idx")]
    assert o.functions == ["ops.f"]
    assert o.columns == [("ops", "a", "extra"), ("ops", "a", "other")]


def test_compare_flags_name_hash_missing_row_and_orphan(tmp_path):
    a = tmp_path / "0001_a.sql"
    a.write_text("select 1;")
    b = tmp_path / "0002_b.sql"
    b.write_text("select 2;")
    files = {1: (a, "migrations"), 2: (b, "migrations")}
    good = {1: ("0001_a.sql", ml.sha256_file(a)), 2: ("0002_b.sql", ml.sha256_file(b))}
    assert ml.compare(files, good) == []
    assert any("hash differs" in f for f in ml.compare(files, {**good, 2: ("0002_b.sql", "0" * 64)}))
    assert any("name differs" in f for f in ml.compare(files, {**good, 2: ("0002_c.sql", good[2][1])}))
    assert any("no ledger row" in f for f in ml.compare(files, {1: good[1]}))
    assert any("no repo file" in f for f in ml.compare(files, {**good, 3: ("0003_x.sql", "0" * 64)}))
    # a pending file may be unapplied: no row is fine
    assert ml.compare({1: (a, "pending")}, {}) == []


def test_row_sql_has_name_and_real_hash(tmp_path):
    f = tmp_path / "0007_x.sql"
    f.write_text("select 1;")
    sql = ml.row_sql(f, "me")
    assert "(7, '0007_x.sql', '" + ml.sha256_file(f) + "', 'me', 'transaction')" in sql


def _fresh(url):
    c = psycopg.connect(url)
    c.execute("drop schema if exists ops cascade")
    c.commit()
    return c


@pytest.fixture
def dburl(isolated_database_url):
    return isolated_database_url


def test_same_transaction_apply_rolls_back_ledger_with_a_failing_migration(dburl, tmp_path):
    with _fresh(dburl) as c:
        c.execute(LEDGER_SQL.read_text())
        c.commit()
        bad = tmp_path / "0999_bad.sql"
        bad.write_text("create table public.ledger_probe_t (a int);\nselect 1/0;")
        with pytest.raises(psycopg.errors.DivisionByZero):
            c.execute(bad.read_text())
            c.execute(ml.row_sql(bad, "t"))
        c.rollback()
        assert c.execute("select count(*) from ops.migration_ledger").fetchone()[0] == 0
        assert c.execute("select to_regclass('public.ledger_probe_t')").fetchone()[0] is None


def test_constraints(dburl):
    with _fresh(dburl) as c:
        c.execute(LEDGER_SQL.read_text())
        ok = "insert into ops.migration_ledger (number, filename, sha256, applied_by) values (%s, %s, %s, 'x')"
        c.execute(ok, (5, "0005_a.sql", "a" * 64))
        for args in [(6, "0005_b.sql", "a" * 64), (7, "0007_a.sql", "xyz"), (5, "0005_c.sql", "a" * 64), (8, "bad name.sql", "a" * 64)]:
            with pytest.raises(psycopg.errors.IntegrityError):
                with c.transaction():
                    c.execute(ok, args)


def test_backfill_probe_is_read_only_and_proposes_only_applied(dburl, tmp_path):
    with _fresh(dburl) as c:
        c.execute(LEDGER_SQL.read_text())
        c.execute("create schema if not exists probe_s; create table probe_s.here (id int)")
        c.commit()
    here = tmp_path / "0001_here.sql"
    here.write_text("create table if not exists probe_s.here (id int);")
    gone = tmp_path / "0002_gone.sql"
    gone.write_text("create table if not exists probe_s.gone (id int);")
    half = tmp_path / "0003_half.sql"
    half.write_text("create table if not exists probe_s.here (id int);\ncreate table probe_s.gone2 (id int);")
    data = tmp_path / "0004_data.sql"
    data.write_text("update probe_s.here set id = 1;")
    files = {i: (p, "migrations") for i, p in enumerate([here, gone, half, data], 1)}
    conn = ml.connect_readonly(dburl)
    try:
        plan = ml.backfill_plan(conn, files)
        with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
            conn.execute("create table probe_s.nope (id int)")
    finally:
        conn.rollback()
        conn.close()
    assert [p["verdict"] for p in plan] == ["APPLIED", "ABSENT", "PARTIAL", "UNPROBEABLE"]
    text = ml.render_plan(plan, True, "backfill-probe")
    assert text.count("insert into ops.migration_ledger") == 1 and "0001_here.sql" in text


def test_check_migrations_live_as_ci_runs_it(dburl):
    env = {**os.environ, "DATABASE_URL": dburl}
    run = lambda: subprocess.run(  # noqa: E731
        [sys.executable, str(ROOT / "scripts" / "check_migrations.py"), "--live"], capture_output=True, text=True, env=env, cwd=ROOT
    )
    with _fresh(dburl) as c:
        r = run()  # ledger missing
        assert r.returncode == 1 and "0131 is not applied" in r.stderr
        c.execute(LEDGER_SQL.read_text())
        c.commit()
        r = run()  # empty ledger: every committed file is unrecorded
        assert r.returncode == 1 and "has no ledger row" in r.stderr
        for n, (path, kind) in ml.repo_files().items():
            if kind == "migrations":
                c.execute(ml.row_sql(path, "test"))
        c.commit()
        r = run()
        assert r.returncode == 0, r.stderr
        c.execute("update ops.migration_ledger set sha256 = %s where number = (select min(number) from ops.migration_ledger)", ("f" * 64,))
        c.commit()
        r = run()
        assert r.returncode == 1 and "hash differs" in r.stderr
