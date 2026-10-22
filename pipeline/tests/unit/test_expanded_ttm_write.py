"""expanded_metrics TTM write: advisory lock + scoped delete + upsert in one
transaction (2026-10-22). Order test on a fake connection; semantics on real SQL
(opt-in via SCROONER_TEST_DATABASE_URL)."""

from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import expanded_metrics as em

OUT = {n: i for i, n in enumerate(sorted(em.OUTPUT_METRIC_NAMES), 100)}
DEP = {"market_cap": 1, "trailing_pe": 2, "fcf": 3}
IDS = {**OUT, **DEP}


class Cur:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def execute(self, sql, params=()):
        self.conn.log.append(("execute", " ".join(sql.split()), params))

    def executemany(self, sql, rows):
        self.conn.log.append(("executemany", " ".join(sql.split()), list(rows)))


class Conn:
    def __init__(self):
        self.log = []

    def cursor(self):
        return Cur(self)

    def commit(self):
        self.log.append(("commit", "", ()))


def row(company, name, value, end=date(2026, 10, 22)):
    return {
        "company_id": company,
        "metric_definition_id": IDS[name],
        "period_start": end,
        "period_end": end,
        "period_label": "TTM",
        "value": value,
        "is_null_reason": None,
        "source_fact_ids": None,
    }


def test_lock_then_delete_then_insert_then_commit_in_that_order():
    conn = Conn()
    em._replace_ttm_rows(conn, 7, IDS, [row(7, "ebitda", Decimal(1))])
    kinds = [
        (k, sql.split()[0] + " " + sql.split()[1] if sql else "")
        for k, sql, _ in conn.log
    ]
    assert [k for k, _ in kinds] == ["execute", "execute", "executemany", "commit"]
    assert "pg_advisory_xact_lock" in conn.log[0][1] and conn.log[0][2] == (
        em.TTM_WRITE_LOCK_NAMESPACE,
        7,
    )
    assert conn.log[1][1].startswith("delete from analytics.metric_value")
    assert conn.log[1][2] == (
        7,
        sorted(OUT.values()),
    )  # owned ids only, no dependency ids


def test_output_names_are_exactly_what_the_cleanup_script_assumes():
    import importlib.util
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "expanded_ttm_rows_cleanup_dryrun.py"
    )
    spec = importlib.util.spec_from_file_location("cleanup_dryrun", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert set(mod.OUTPUTS) == set(em.OUTPUT_METRIC_NAMES)


def test_tally_keeps_the_newest_row_per_company_and_metric():
    import importlib.util
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "expanded_ttm_rows_cleanup_dryrun.py"
    )
    spec = importlib.util.spec_from_file_location("cleanup_dryrun2", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rows = [
        (1, "ebitda", date(2026, 10, 20)),
        (1, "ebitda", date(2026, 10, 21)),
        (1, "ebitda", date(2026, 10, 22)),
        (2, "ebitda", date(2026, 10, 22)),
        (1, "ev_ebitda", date(2026, 10, 22)),
    ]
    total, archive = mod.tally(rows)
    assert sum(total.values()) == 5 and sum(archive.values()) == 2
    assert (
        archive[("ebitda", date(2026, 10, 20))] == 1
        and ("ebitda", date(2026, 10, 22)) not in archive
    )


psycopg = pytest.importorskip("psycopg")


@pytest.fixture
def pg(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:  # non-autocommit, like the stage
        c.execute("drop schema if exists analytics cascade; create schema analytics;")
        c.execute(
            "create table analytics.metric_value (company_id bigint, metric_definition_id bigint, period_start date,"
            " period_end date, period_label text, value numeric, is_null_reason text, source_fact_ids bigint[],"
            " unique (company_id, metric_definition_id, period_start, period_end, period_label))"
        )
        c.commit()
        yield c


def seed(pg):
    ebitda, dep, other_label = IDS["ebitda"], IDS["market_cap"], IDS["ebitda"]
    for d in (date(2026, 10, 20), date(2026, 10, 21)):
        for cid in (1, 2):
            pg.execute(
                "insert into analytics.metric_value values (%s,%s,%s,%s,'TTM',1,null,null)",
                (cid, ebitda, d, d),
            )
    pg.execute(
        "insert into analytics.metric_value values (1,%s,%s,%s,'TTM',9,null,null)",
        (dep, date(2026, 10, 20), date(2026, 10, 20)),
    )
    pg.execute(
        "insert into analytics.metric_value values (1,%s,'2026-04-01','2026-06-30','Q2',5,null,null)",
        (other_label,),
    )
    pg.commit()


def test_real_sql_old_ttm_rows_go_other_rows_stay(pg):
    seed(pg)
    em._replace_ttm_rows(pg, 1, IDS, [row(1, n, Decimal(3)) for n in OUT])
    left = pg.execute(
        "select company_id, metric_definition_id, period_end, period_label from analytics.metric_value order by 1,2,3"
    ).fetchall()
    c1_ebitda_ttm = [
        r for r in left if r[0] == 1 and r[1] == IDS["ebitda"] and r[3] == "TTM"
    ]
    assert [r[2] for r in c1_ebitda_ttm] == [date(2026, 10, 22)]  # one row, today's
    assert any(r[0] == 1 and r[3] == "Q2" for r in left)  # the quarter row is untouched
    assert any(
        r[0] == 1 and r[1] == IDS["market_cap"] for r in left
    )  # dependency metric untouched
    assert len([r for r in left if r[0] == 2]) == 2  # other company untouched


def test_real_sql_rerun_same_day_is_idempotent(pg):
    for _ in range(2):
        em._replace_ttm_rows(pg, 1, IDS, [row(1, n, Decimal(3)) for n in OUT])
    assert pg.execute("select count(*) from analytics.metric_value").fetchone()[
        0
    ] == len(OUT)
