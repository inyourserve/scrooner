"""The hybrid FSN path's companies (fsn_store/new_path.py) and the old-path writers that skip them.

Founder decisions relayed 2026-11-11: a company written from the FSN store gets its nightly updates from the
hybrid path only; the old normalize/map path skips it at the writer, not per cell. The reprocess script's
writer stages are covered in test_sharded_runner.py; this file covers the membership rule and the sanity
re-merge writer (`scrooner-sanity investigate` -> resolve_company_tag_preferences), the one nightly
canonical_fact writer outside the reprocess script."""

from __future__ import annotations

import psycopg
import pytest
from scrooner_pipeline.fsn_store import new_path
from scrooner_pipeline.sanity import tag_investigator


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if _one(c, "select to_regclass('analytics.slot_protected_cell') is not null and to_regclass('analytics.rule_run') is not null") is not True:
        c.close()
        pytest.skip("needs migrations 0100/0113")
    yield c
    c.close()


def _company(conn, cik: str) -> int:
    return _one(conn, "insert into core.company (cik, company_name) values (%s, %s) returning id", (cik, f"CO {cik}"))


def _concept(conn, name: str) -> int:
    got = conn.execute("select id from analytics.canonical_concept where name = %s", (name,)).fetchone()
    if got:
        return got[0]
    return _one(
        conn,
        "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, 'income_statement', 'first_match') returning id",
        (name,),
    )


def _period(conn, cid: int) -> int:
    return _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) values (%s, '2026-07-01', '2026-09-30', 'duration', 2026, 'Q3') returning id",
        (cid,),
    )


def _run(conn, rule_id: str, mode: str = "apply") -> str:
    return str(
        _one(
            conn,
            "insert into analytics.rule_run (rule_id, rule_version, mode, flag_name, flag_state) values (%s, %s, %s, 'test', 'on') returning run_id",
            (rule_id, int(rule_id.rsplit("@", 1)[1]), mode),
        )
    )


def _protect(conn, cid: int, concept: int, period: int, run_id: str, rule_id: str) -> None:
    conn.execute(
        "insert into analytics.slot_protected_cell (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256) values (%s, %s, %s, %s, 1, %s, 'x')",
        (cid, concept, period, rule_id, run_id),
    )


def test_flag_is_off_by_default(monkeypatch):
    monkeypatch.delenv(new_path.FLAG, raising=False)
    assert new_path.enabled() is False
    monkeypatch.setenv(new_path.FLAG, "on")
    assert new_path.enabled() is True


@pytest.mark.integration
def test_a_company_is_on_the_new_path_once_an_applied_fsn_write_landed(conn, monkeypatch):
    fsn_co, release_co, dry_co, plain = (_company(conn, c) for c in ("0000000011", "0000000012", "0000000013", "0000000014"))
    concept = _concept(conn, "revenue_sanity_resolved")
    fsn_run, release_run, dry_run = _run(conn, "fsn.select@1"), _run(conn, "is.revenue@1"), _run(conn, "fsn.select@1", "dry_run")
    _protect(conn, fsn_co, concept, _period(conn, fsn_co), fsn_run, "fsn.select@1")
    _protect(conn, release_co, concept, _period(conn, release_co), release_run, "is.revenue@1")  # an old patch package
    _protect(conn, dry_co, concept, _period(conn, dry_co), dry_run, "fsn.select@1")
    _period(conn, plain)
    conn.commit()
    assert new_path.company_ids(conn) == {fsn_co}
    assert new_path.ciks(conn) == ["0000000011"]
    monkeypatch.delenv(new_path.FLAG, raising=False)
    assert new_path.excluded_company_ids(conn) == set()  # off: the old path skips nothing
    monkeypatch.setenv(new_path.FLAG, "on")
    assert new_path.excluded_company_ids(conn) == {fsn_co}


@pytest.mark.integration
def test_sanity_remerge_never_writes_a_new_path_company(conn, monkeypatch):
    """resolve_company_tag_preferences copies revenue into revenue_sanity_resolved for every company
    without a preference; with HYBRID_NEW_PATH=on it skips the FSN-written company entirely (no copy,
    no delete), while the old-path company is still refreshed."""
    fsn_co, old_co = _company(conn, "0000000021"), _company(conn, "0000000022")
    revenue, resolved = _concept(conn, "revenue"), _concept(conn, "revenue_sanity_resolved")
    p_fsn, p_old = _period(conn, fsn_co), _period(conn, old_co)
    for cid, pid in ((fsn_co, p_fsn), (old_co, p_old)):
        conn.execute(
            "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, 100, '{}')",
            (cid, revenue, pid),
        )
    _protect(conn, fsn_co, resolved, p_fsn, _run(conn, "fsn.select@1"), "fsn.select@1")
    conn.commit()

    def resolved_rows(cid):
        return _one(conn, "select count(*) from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", (cid, resolved))

    monkeypatch.setenv(new_path.FLAG, "on")
    tag_investigator.resolve_company_tag_preferences(conn, "revenue", "revenue_sanity_resolved")
    conn.commit()
    assert resolved_rows(old_co) == 1
    assert resolved_rows(fsn_co) == 0
    assert _one(conn, "select count(*) from analytics.slot_protected_write_skipped where company_id = %s", (fsn_co,)) == 0  # skipped at the writer, not by the 0113 guard
    monkeypatch.setenv(new_path.FLAG, "off")
    tag_investigator.resolve_company_tag_preferences(conn, "revenue", "revenue_sanity_resolved")
    conn.commit()
    # off: the old writer tries again and only the per-cell 0113 guard stops it (the behaviour before this change)
    assert resolved_rows(fsn_co) == 0
    assert _one(conn, "select count(*) from analytics.slot_protected_write_skipped where company_id = %s", (fsn_co,)) == 1


@pytest.mark.integration
def test_a_read_failure_fails_closed(conn, monkeypatch):
    monkeypatch.setenv(new_path.FLAG, "on")
    conn.execute("alter table analytics.rule_run rename to rule_run_gone")
    with pytest.raises(psycopg.Error):
        new_path.excluded_company_ids(conn)
    conn.rollback()
