"""The FSN write run 42561798991 (2026-11-09) on production fsn.* (~900 companies, 35.6M values):

1. `scrooner-fsn pilot` failed EVERY company with a statement timeout. select.load_company read a company's member
   values by (company_id, tag_id) with no dim_id filter, so it could not use the partial series index and the plan
   walked the (filing_id, tag_id, ...) key by tag_id alone, across every company (EXPLAIN cost 846,820 against
   4,692 with the company's filing ids). The read must give the planner `filing_id` as an index condition.
2. `scrooner-fsn load` shards died when the pooler dropped the connection: rollback() on the dead connection
   raised inside the per-company handler. load.run must reconnect and go on.
"""

from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.fsn_store import load, select

ROOT = Path(__file__).resolve().parents[3]
JPM = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_cf_detectors" / "0000019617"


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    n = c.execute(
        "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'value')"
    ).fetchone()[0]
    if n != 2:
        c.close()
        pytest.skip("needs migration 0118")
    yield c
    c.close()


@pytest.mark.integration
def test_member_value_read_is_bounded_by_the_companys_filings(conn):
    """The plan of the member-value read must use filing_id in an index condition, never tag_id alone."""
    conn.execute(
        "set enable_seqscan = off"
    )  # the production row counts, not the test database's, decide the plan
    plan = "\n".join(
        r[0]
        for r in conn.execute(
            "explain " + select.MEMBER_VALUES_SQL, (1, [1, 2, 3], [10, 11])
        ).fetchall()
    )
    conds = [line for line in plan.splitlines() if "Index Cond" in line]
    assert conds, plan
    assert all("filing_id" in c for c in conds), plan


@pytest.mark.integration
def test_load_reconnects_when_the_pooler_drops_the_connection(
    conn, isolated_database_url, monkeypatch
):
    conn.execute(
        "insert into core.company (cik, company_name) values ('0000019617', 'JPM TEST')"
    )
    conn.commit()
    real = load.load_company
    calls = []

    def drop_once(c, d, **kw):
        calls.append(d.name)
        if (
            len(calls) == 1
        ):  # the pooler drops the backend in the middle of the company's transaction
            c.execute("select pg_terminate_backend(pg_backend_pid())")
        return real(c, d, **kw)

    monkeypatch.setattr(load, "load_company", drop_once)
    opened = []

    def connect():
        opened.append(psycopg.connect(isolated_database_url))
        return opened[-1]

    out = load.run(conn, JPM.parent, ["0000019617"], git_commit="test", connect=connect)
    assert out["reconnects"] == 1 and out["errors"] == 0 and out["companies"] == 1, out
    assert calls == ["0000019617", "0000019617"]
    assert all(c.closed for c in opened)  # the replacement is closed by load.run
    with psycopg.connect(isolated_database_url) as check:
        assert (
            check.execute(
                "select count(*) from fsn.filing f join core.company c on c.id = f.company_id where c.cik = '0000019617'"
            ).fetchone()[0]
            > 0
        )
        # the batch's rule_run is finished on the replacement connection
        assert check.execute(
            "select finished_at is not null from analytics.rule_run where run_id = %s",
            (out["run_id"],),
        ).fetchone()[0]


@pytest.mark.integration
def test_load_without_a_reconnect_stops_with_the_original_error(conn, monkeypatch):
    conn.execute(
        "insert into core.company (cik, company_name) values ('0000019617', 'JPM TEST')"
    )
    conn.commit()

    def drop(c, d, **kw):
        c.execute("select pg_terminate_backend(pg_backend_pid())")

    monkeypatch.setattr(load, "load_company", drop)
    # the ORIGINAL error (the backend was terminated), not a second one from rollback() on the dead connection,
    # which is what main raised: the operator sees why the company failed
    with pytest.raises(psycopg.errors.AdminShutdown):
        load.run(conn, JPM.parent, ["0000019617"], git_commit="test")


@pytest.mark.integration
def test_pilot_goes_on_after_the_pooler_drops_the_connection(
    conn, isolated_database_url, monkeypatch, tmp_path
):
    """`scrooner-fsn pilot`: the first company's connection is dropped mid-company; the command must record that
    company as failed and run the next one on a fresh connection, then write its outputs (it used to die in
    rollback())."""
    from typer.testing import CliRunner

    from scrooner_pipeline.common.config import settings
    from scrooner_pipeline.fsn_store import mapping
    from scrooner_pipeline.jobs import fsn as fsn_job

    conn.execute(
        "insert into core.company (cik, company_name) values ('0000000001', 'A'), ('0000000002', 'B')"
    )
    conn.commit()
    monkeypatch.setattr(settings, "database_url", isolated_database_url)
    seen = []

    def map_company(c, cid, rules, **kw):
        seen.append(cid)
        if len(seen) == 1:
            c.execute("select pg_terminate_backend(pg_backend_pid())")
        c.execute("select 1")  # the second company runs on a live connection
        raise ValueError("stop here")

    monkeypatch.setattr(mapping, "map_company", map_company)
    res = CliRunner().invoke(
        fsn_job.app,
        ["pilot", "--ciks", "0000000001,0000000002", "--out", str(tmp_path)],
    )
    assert res.exit_code == 0, res.output + repr(res.exception)
    assert len(seen) == 2
    failed = (tmp_path / "failed.json").read_text()
    assert "0000000001" in failed and "AdminShutdown" in failed
    assert "0000000002" in failed and "stop here" in failed
