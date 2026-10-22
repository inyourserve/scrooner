"""P1 reload on REAL SQL (isolated test database, scratch schemas s3_c/s3_a;
the real migration 0100 is applied verbatim). Scenario = Entergy 0000065984-26-000174:
the combined 10-K was claimed by Entergy Arkansas (id 142, CIK 7323) because it sorts
first, so Entergy Corp (id 694, CIK 65984) has no facts after 2010."""

import json
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.normalizer import registrant as r
from scrooner_pipeline.normalizer import registrant_loader as rl
from scrooner_pipeline.normalizer import registrant_reload as rr

pytestmark = pytest.mark.integration
MIG = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "0100_cell_evidence_reason_registrant_audit.sql"
)
FX = Path(__file__).resolve().parents[1] / "fixtures" / "sec" / "registrants"
A, C = "s3_a", "s3_c"
K = "0000065984-26-000174"
OWN_K = "0000007323-26-000009"


def _rw(sql):
    return sql.replace("analytics.", f"{A}.").replace("core.", f"{C}.")


class _Cur:
    def __init__(self, c):
        self._c = c

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

    @property
    def description(self):
        return self._c.description


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


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as raw:
        for s in (A, C):
            raw.execute(f"drop schema if exists {s} cascade")
        raw.execute(f"create schema {A}; create schema {C};")
        raw.execute(
            f"create table {C}.company (id bigint primary key, cik text unique)"
        )
        raw.execute(
            f"create table {C}.filing (id bigint primary key, company_id bigint references {C}.company(id), accession_number text unique, form text)"
        )
        raw.execute(
            f"create table {C}.fact (id bigint primary key, company_id bigint, filing_id bigint references {C}.filing(id), "
            f"supersedes_fact_id bigint references {C}.fact(id), value numeric)"
        )
        raw.execute(
            f"create table {A}.company_stock_split (id bigint primary key, source_fact_id bigint references {C}.fact(id))"
        )
        raw.execute(_rw(MIG.read_text()))
        raw.execute(
            f"insert into {C}.company values (142, '0000007323'), (694, '0000065984'), (1, '0000320193')"
        )
        raw.execute(
            f"insert into {C}.filing values (10, 142, '{K}', '10-K'), (11, 142, '{OWN_K}', '10-K'), (12, 1, '0000320193-26-000020', '10-Q')"
        )
        raw.execute(
            f"insert into {C}.fact values (1, 142, 10, null, 12946686000), (2, 142, 10, 1, 71890730000), (3, 142, 11, null, 2784047000), (4, 1, 12, null, 5), (5, 694, 10, null, 1), (6, 142, 11, 1, 7)"
        )
        raw.commit()
        yield raw
        raw.rollback()
        for s in (A, C):
            raw.execute(f"drop schema if exists {s} cascade")
        raw.commit()


def decisions():
    hdr = r.parse_header_filers((FX / f"{K}.header.txt").read_text())
    return [
        r.decide_primary(K, "0000065984", hdr),
        r.decide_primary("0000320193-26-000020", "0000320193", ["0000320193"]),
    ]


@pytest.mark.integration
def test_plan_reports_the_misattribution_and_changes_nothing(db):
    conn = _Conn(db)
    plans = rr.plan_reload(conn, decisions())
    assert [p.accession_number for p in plans] == [
        K
    ]  # the single-filer accession needs no reload
    p = plans[0]
    assert (
        p.primary_company_id,
        p.filing_owner_company_id,
        p.facts_under_owner,
        p.facts_to_delete,
    ) == (694, 142, 3, 2)
    assert p.blockers == [] and any("move core.filing" in a for a in p.actions)
    assert (
        db.execute(
            f"select company_id from {C}.filing where accession_number = '{K}'"
        ).fetchone()[0]
        == 142
    )


@pytest.mark.integration
def test_apply_needs_backup_and_a_clean_plan(db, tmp_path):
    conn = _Conn(db)
    plans = rr.plan_reload(conn, decisions())
    with pytest.raises(FileNotFoundError):
        rr.apply_reload(conn, plans, tmp_path / "none.jsonl")
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    with pytest.raises(ValueError):
        rr.apply_reload(conn, plans, empty)
    db.rollback()
    assert db.execute(f"select count(*) from {C}.fact").fetchone()[0] == 6
    db.execute(f"insert into {A}.company_stock_split values (1, 1)")
    db.commit()
    blocked = rr.plan_reload(conn, decisions())
    assert blocked[0].blockers and "company_stock_split" in blocked[0].blockers[0]
    bk = tmp_path / "bk.jsonl"
    rr.write_backup(conn, blocked, bk)
    with pytest.raises(ValueError):
        rr.apply_reload(conn, blocked, bk)


@pytest.mark.integration
def test_apply_moves_the_filing_deletes_only_the_wrong_facts_and_is_idempotent(
    db, tmp_path
):
    conn = _Conn(db)
    ds = decisions()
    plans = rr.plan_reload(conn, ds)
    bk = tmp_path / "bk.jsonl"
    assert rr.write_backup(conn, plans, bk) == 2
    assert {json.loads(x)["id"] for x in bk.read_text().splitlines()} == {1, 2}
    rr.persist_decisions(conn, ds)
    stats = rr.apply_reload(conn, plans, bk)
    db.commit()
    assert stats == {"filings_moved": 1, "facts_deleted": 2}
    assert (
        db.execute(
            f"select company_id from {C}.filing where accession_number = '{K}'"
        ).fetchone()[0]
        == 694
    )
    # the subsidiary's own 10-K, its fact, and Apple are untouched
    assert (
        db.execute(
            f"select company_id from {C}.filing where accession_number = '{OWN_K}'"
        ).fetchone()[0]
        == 142
    )
    # the primary's own fact (5) survives; fact 6 (kept) no longer points at the deleted fact 1
    assert sorted(x[0] for x in db.execute(f"select id from {C}.fact").fetchall()) == [
        3,
        4,
        5,
        6,
    ]
    assert (
        db.execute(f"select supersedes_fact_id from {C}.fact where id = 6").fetchone()[
            0
        ]
        is None
    )
    # registrant table: exactly one primary, six co-registrants, linked to company ids where known
    rows = db.execute(
        f"select registrant_cik, role, company_id from {C}.filing_registrant where accession_number = '{K}' order by 1"
    ).fetchall()
    assert len(rows) == 7 and [x for x in rows if x[1] == "primary"] == [
        ("0000065984", "primary", 694)
    ]
    assert dict((x[0], x[2]) for x in rows)["0000007323"] == 142
    # second run: nothing left to move or delete
    again = rr.plan_reload(conn, ds)
    assert again[0].facts_to_delete == 0 and again[0].actions == []
    assert rr.apply_reload(conn, again, bk) == {"filings_moved": 0, "facts_deleted": 0}


@pytest.mark.integration
def test_quarantined_accession_loses_its_facts_and_is_not_moved(db, tmp_path):
    conn = _Conn(db)
    hdr = r.parse_header_filers((FX / f"{K}.header.txt").read_text())
    ds = [
        r.decide_primary(K, "0000007323", hdr)
    ]  # dei disagrees with the first header filer
    assert ds[0].quarantined
    plans = rr.plan_reload(conn, ds)
    bk = tmp_path / "bk.jsonl"
    rr.write_backup(conn, plans, bk)
    rr.persist_decisions(conn, ds)
    rr.apply_reload(conn, plans, bk)
    db.commit()
    assert (
        db.execute(
            f"select company_id from {C}.filing where accession_number = '{K}'"
        ).fetchone()[0]
        == 142
    )
    assert (
        db.execute(f"select count(*) from {C}.fact where filing_id = 10").fetchone()[0]
        == 0
    )  # incl. the primary's: nobody may load it
    roles = {
        x[0]
        for x in db.execute(
            f"select role from {C}.filing_registrant where accession_number = '{K}'"
        ).fetchall()
    }
    assert roles == {"quarantined"}


@pytest.mark.integration
def test_registrant_roles_and_filings_to_skip_read_the_table(db, monkeypatch):
    from scrooner_pipeline.common import rule_flags

    conn = _Conn(db)
    rr.persist_decisions(conn, decisions())
    db.commit()
    roles = rl.registrant_roles(conn, "0000007323")
    assert roles[K][0] == "co_registrant" and "0000065984" in roles[K][1]
    assert rl.registrant_roles(conn, "0000065984")[K][0] == "primary"
    monkeypatch.delenv(rule_flags.ENV_VAR, raising=False)
    assert rl.filings_to_skip(conn, "0000007323") == set()
    monkeypatch.setenv(rule_flags.ENV_VAR, rule_flags.RULE_SHARED_ACCESSION_PRIMARY)
    assert rl.filings_to_skip(conn, "0000007323") == {K}
    assert rl.filings_to_skip(conn, "0000065984") == set()
    _ = cs
