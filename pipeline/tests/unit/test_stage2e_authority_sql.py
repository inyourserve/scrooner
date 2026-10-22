"""Stage 2e W3, the conflict-fill loader and the repair list on REAL SQL
(isolated test database, scratch schemas; `core.`/`analytics.` are rewritten to
s2_c/s2_a so no production table is touched). Same JPM / WTRG / MA fixtures as
test_stage2e_authority.py."""

from datetime import date

import psycopg
import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.mapper import conflict_resolution as cr
from scrooner_pipeline.mapper import periodic_source_repair as repair
from scrooner_pipeline.normalizer import dedupe

pytestmark = pytest.mark.integration

A, C = "s2_a", "s2_c"


def _rw(sql: str) -> str:
    return sql.replace("analytics.", f"{A}.").replace("core.", f"{C}.")


class _Cur:
    def __init__(self, cur):
        self._c = cur

    def __enter__(self):
        self._c.__enter__()
        return self

    def __exit__(self, *a):
        return self._c.__exit__(*a)

    def execute(self, sql, params=None):
        self._c.execute(_rw(sql), params)
        return self

    def executemany(self, sql, params):
        self._c.executemany(_rw(sql), params)

    def fetchone(self):
        return self._c.fetchone()

    def fetchall(self):
        return self._c.fetchall()

    @property
    def rowcount(self):
        return self._c.rowcount


class _Conn:
    def __init__(self, c):
        self._c = c

    def cursor(self):
        return _Cur(self._c.cursor())

    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)

    def commit(self):
        self._c.commit()

    def rollback(self):
        self._c.rollback()


SCHEMA = f"""
create schema {C}; create schema {A};
create table {C}.company (id bigint primary key);
create table {C}.filing (id bigint primary key, company_id bigint, accession_number text unique,
                         form text, filing_date date);
create table {C}.period (id bigint primary key, start_date date, end_date date);
create table {C}.fact (
    id bigint primary key, company_id bigint, concept_id bigint, unit_id bigint, period_id bigint,
    filing_id bigint, value numeric, is_derived boolean default false, is_authoritative boolean default true);
create table {A}.canonical_concept (id bigint primary key, name text);
create table {A}.concept_mapping (concept_id bigint, canonical_concept_id bigint, priority int, confidence text);
create table {A}.canonical_fact (
    id bigint generated always as identity primary key, company_id bigint, canonical_concept_id bigint,
    period_id bigint, value numeric, source_fact_ids bigint[],
    unique (company_id, canonical_concept_id, period_id));
insert into {C}.company values (1), (2);
insert into {C}.filing values
  (10, 1, '0001628280-26-008131', '10-K',   '2026-02-13'),
  (11, 1, '0000019617-26-000096', 'DEF 14A','2026-04-06'),
  (20, 2, '0000078128-26-000050', '10-K',   '2026-02-26'),
  (21, 2, '0001193125-26-124163', '8-K',    '2026-03-25');
insert into {C}.period values (100, '2025-01-01', '2025-12-31'), (101, '2025-10-01', '2025-12-31');
insert into {A}.canonical_concept values (1, 'net_income'), (2, 'net_income_resolved'), (3, 'cfo');
insert into {A}.concept_mapping values (500, 1, 1, 'high');
"""


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as raw:
        for s in (A, C):
            raw.execute(f"drop schema if exists {s} cascade")
        raw.execute(SCHEMA)
        # JPM FY2025 NetIncomeLoss (concept 500): all four states as stored on 2026-10-22
        raw.execute(
            f"insert into {C}.fact (id, company_id, concept_id, unit_id, period_id, filing_id, value, is_derived, is_authoritative) values "
            "(29697, 1, 500, 1, 100, 10, 57048000000, false, false),"
            "(733850, 1, 500, 1, 100, 11, 57000000000, false, false),"
            "(340478, 1, 501, 1, 101, 10, 13025000000, true, false),"
            "(182608846, 1, 501, 1, 101, 11, 12977000000, true, false),"
            "(340493, 1, 502, 1, 101, 10, 12691000000, true, true),"
            # WTRG FY2025 CFO: 10-K vs 8-K recast, 8-K promoted by the latest-filed stage
            "(5281880, 2, 600, 1, 100, 20, 1010459000, false, false),"
            "(5281882, 2, 600, 1, 100, 21, 2059000000, false, true)"
        )
        raw.commit()
        yield raw
        raw.rollback()
        for s in (A, C):
            raw.execute(f"drop schema if exists {s} cascade")
        raw.commit()


def auth(db):
    return dict(db.execute(f"select id, is_authoritative from {C}.fact").fetchall())


@pytest.mark.integration
def test_flag_off_leaves_the_proxy_deauthorizing_the_10k(db):
    dedupe.resolve_authoritative_for_company(_Conn(db), 1, periodic_only=False, matching_copies=False)
    st = auth(db)
    assert st[29697] is False and st[733850] is False


@pytest.mark.integration
def test_flag_on_repairs_jpm_fy_q4_and_wtrg(db):
    conn = _Conn(db)
    s1 = dedupe.resolve_authoritative_for_company(conn, 1, periodic_only=True, matching_copies=False)
    s2 = dedupe.resolve_authoritative_for_company(conn, 2, periodic_only=True, matching_copies=False)
    st = auth(db)
    assert st[29697] is True and st[733850] is False  # FY: 57,048M from the 10-K
    assert st[340478] is True and st[182608846] is False  # Q4: 13,025M, not 12,977M
    assert st[340493] is True  # untouched
    assert st[5281880] is True and st[5281882] is False  # WTRG's own 10-K, not the 8-K
    assert s1["shrunk_group_promoted"] == 2 and s2["shrunk_group_promoted"] == 1
    assert s2["non_periodic_demoted"] == 1
    # idempotent: second run writes nothing and changes nothing
    before = auth(db)
    dedupe.resolve_authoritative_for_company(conn, 1, periodic_only=True, matching_copies=False)
    assert auth(db) == before


@pytest.mark.integration
def test_flag_through_the_environment(db, monkeypatch):
    monkeypatch.setenv(rule_flags.ENV_VAR, rule_flags.RULE_PERIODIC_FORM_ONLY)
    dedupe.resolve_authoritative_for_company(_Conn(db), 1)
    assert auth(db)[29697] is True


@pytest.mark.integration
def test_conflict_fill_loader_never_sees_the_proxy_copy(db):
    conn = _Conn(db)
    # Stage 2e not yet run with the flag: the group is an unresolved conflict
    groups_off = cr._load_conflict_groups(conn, 1, periodic_only=False)
    assert [(g[0], g[1], list(g[3])) for g in groups_off] == [(1, 100, [29697, 733850])]
    # the old fill would take the highest fact_id = the rounded proxy copy
    assert cr._safe_fill_value(list(groups_off[0][2]), list(groups_off[0][3]))[1] == 733850
    # periodic-only: the group is just the 10-K copy, which is not a conflict at all
    assert cr._load_conflict_groups(conn, 1, periodic_only=True) == []


@pytest.mark.integration
def test_conflict_fill_loader_flag_from_environment(db, monkeypatch):
    monkeypatch.setenv(rule_flags.ENV_VAR, rule_flags.RULE_PERIODIC_FORM_ONLY)
    assert cr._load_conflict_groups(_Conn(db), 1) == []


@pytest.mark.integration
def test_repair_list_finds_stale_proxy_fills_and_purge_needs_a_backup(db, tmp_path):
    db.execute(
        f"insert into {A}.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values "
        "(1, 2, 100, 57000000000, array[733850]),"      # stale fill from the proxy copy (JPM net_income_resolved)
        "(1, 1, 100, 57048000000, array[29697]),"        # good
        "(1, 3, 100, 123, array[29697, 733850]),"        # combined value that used a proxy copy
        "(2, 3, 100, 2059000000, array[5281882])"        # WTRG: 8-K only
    )
    db.commit()
    conn = _Conn(db)
    cells = repair.find_non_periodic_sourced_cells(conn, [1, 2])
    by = {(c.company_id, c.concept): c for c in cells}
    assert set(by) == {(1, "net_income_resolved"), (1, "cfo"), (2, "cfo")}
    assert by[(1, "net_income_resolved")].klass == repair.CLASS_ALL_NON_PERIODIC
    assert by[(1, "cfo")].klass == repair.CLASS_MIXED
    assert by[(1, "net_income_resolved")].bad_forms == ("DEF 14A",)
    # no backup -> refuses, and nothing is deleted
    with pytest.raises(FileNotFoundError):
        repair.purge_cells(conn, cells, tmp_path / "missing.jsonl")
    # backup that misses an id -> refuses
    partial = tmp_path / "partial.jsonl"
    repair.write_backup(cells[:1], partial)
    with pytest.raises(ValueError):
        repair.purge_cells(conn, cells, partial)
    assert db.execute(f"select count(*) from {A}.canonical_fact").fetchone()[0] == 4
    # full backup -> deletes exactly the listed ids, the good row stays
    full = tmp_path / "full.jsonl"
    assert repair.write_backup(cells, full) == 3
    assert repair.purge_cells(conn, cells, full) == 3
    remaining = db.execute(f"select value from {A}.canonical_fact").fetchall()
    assert [r[0] for r in remaining] == [57048000000]


@pytest.mark.integration
def test_repair_list_is_read_only_and_empty_when_clean(db):
    conn = _Conn(db)
    assert repair.find_non_periodic_sourced_cells(conn, [1, 2]) == []
    assert db.execute(f"select count(*) from {A}.canonical_fact").fetchone()[0] == 0
    _ = date  # fixture dates are in the SQL above
