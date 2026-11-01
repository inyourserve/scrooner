"""share_basis.write_company on real SQL in an isolated test database (mode
on). The split_event / filing_share_basis DDL is read from migration 0099
and the archive DDL from 0098 (foreign keys stripped), so the test also
pins both migrations' columns and CHECKs. Never runs against the shared
database: isolated_database_url refuses anything not named *test*."""

import re
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.corporate_actions import share_basis as sb
from scrooner_pipeline.mapper import canonical_archive as ca
from test_share_basis import (
    MAPPED,
    aapl,
)  # tests/unit is on sys.path (rootdir-relative)

pytestmark = pytest.mark.integration

MIG = Path(__file__).parents[2] / "db/migrations"


def _ddl(file: str, table: str) -> str:
    sql = (MIG / file).read_text()
    ddl = sql[sql.index(f"create table if not exists analytics.{table}") :]
    ddl = ddl[: ddl.index(");") + 2]
    return re.sub(r"references \w+\.\w+ \(id\)", "", ddl)


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists analytics cascade")
        c.execute("create schema analytics")
        c.execute(
            "create table analytics.canonical_concept (id bigint primary key, name text unique)"
        )
        c.execute(
            """
            create table analytics.canonical_fact (
                id bigint generated always as identity primary key,
                company_id bigint not null, canonical_concept_id bigint not null,
                period_id bigint not null, value numeric not null,
                source_fact_ids bigint[] not null,
                resolved_at timestamptz not null default now(),
                unique (company_id, canonical_concept_id, period_id))
            """
        )
        c.execute(
            _ddl(
                "0098_per_share_gap_cause_and_canonical_fact_retired.sql",
                "canonical_fact_retired",
            )
        )
        c.execute(_ddl("0099_split_event_and_filing_share_basis.sql", "split_event"))
        c.execute(
            _ddl("0099_split_event_and_filing_share_basis.sql", "filing_share_basis")
        )
        for i, name in enumerate(sb.TARGETS, start=1):
            c.execute(
                "insert into analytics.canonical_concept values (%s, %s)", (i, name)
            )
        c.commit()
        yield c
        c.rollback()
        c.execute("drop schema if exists analytics cascade")
        c.commit()


def _cells(c):
    return {
        (n, p): v
        for n, p, v in c.execute(
            "select cc.name, cf.period_id, cf.value from analytics.canonical_fact cf"
            " join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id"
        ).fetchall()
    }


def _current(c):
    return {
        (n, p): (i, v, tuple(s))
        for i, n, p, v, s in c.execute(
            "select cf.id, cc.name, cf.period_id, cf.value, cf.source_fact_ids"
            " from analytics.canonical_fact cf"
            " join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id"
        ).fetchall()
    }


def test_write_rebases_idempotent_and_restorable(conn):
    book = aapl()
    res = sb.compute_company(1, book.facts, MAPPED)
    fy18 = book.pid("2017-10-01", "2018-09-29")
    # Today's wrong cell (AAPL FY2018 diluted EPS on the pre-split basis), and a
    # derived-only cell RU-1 owns.
    conn.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)"
        " values (1, 1, %s, 11.91, '{74785,74786}'), (1, 1, 9999, 1.84, '{1}')",
        (fy18,),
    )
    conn.commit()
    before = _cells(conn)

    stats = sb.write_company(
        conn, res, _current(conn), run_id="r1", remove_derived_only=False
    )
    conn.commit()
    after = _cells(conn)
    assert after[("diluted_eps_resolved", fy18)] == Decimal("2.98")
    assert after[("diluted_eps_resolved", 9999)] == Decimal("1.84")  # left to RU-1
    assert stats["replaced"] == 1 and stats["removed"] == 0
    assert stats["inserted"] == sum(1 for c in res.cells if c.status == sb.SHOWN) - 1
    ev = conn.execute(
        "select ratio, basis_date, status, evidence_kinds from analytics.split_event"
    ).fetchall()
    assert [(e[0], str(e[1]), e[2]) for e in ev] == [
        (Decimal(4), "2020-10-30", "confirmed")
    ]
    assert sorted(ev[0][3]) == ["filed_pair", "ratio_fact", "share_step"]
    n_basis = conn.execute(
        "select count(*) from analytics.filing_share_basis"
    ).fetchone()[0]
    assert n_basis == len(res.basis)
    archived = conn.execute(
        "select action, value from analytics.canonical_fact_retired where run_id = 'r1' and action = 'replaced'"
    ).fetchall()
    assert archived == [("replaced", Decimal("11.91"))]

    # Second run on unchanged inputs changes no canonical cell.
    again = sb.write_company(
        conn, res, _current(conn), run_id="r2", remove_derived_only=False
    )
    conn.commit()
    assert again["replaced"] == 0 and again["inserted"] == 0 and again["removed"] == 0
    assert _cells(conn) == after

    # Rollback of the first run restores the pre-run cells exactly.
    with conn.transaction():
        ca.restore_run(conn.cursor(), "r1")
    assert _cells(conn) == before


def test_write_removes_hidden_cells_through_the_archive(conn):
    book = aapl()
    # Same-basis disagreement: hidden with reason, current row archived.
    k = book.filing("X-1", "2021-01-01", "10-K")
    book.add("EarningsPerShareDiluted", "9.00", "2020-09-27", "2020-12-26", k)
    k2 = book.filing("X-2", "2022-01-01", "10-K")
    book.add("EarningsPerShareDiluted", "1.00", "2020-09-27", "2020-12-26", k2)
    res = sb.compute_company(1, book.facts, MAPPED)
    pid = book.pid("2020-09-27", "2020-12-26")
    conn.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)"
        " values (1, 1, %s, 1.00, '{1}')",
        (pid,),
    )
    conn.commit()
    stats = sb.write_company(
        conn, res, _current(conn), run_id="r3", remove_derived_only=False
    )
    conn.commit()
    assert stats["removed"] == 1
    assert ("diluted_eps_resolved", pid) not in _cells(conn)
    row = conn.execute(
        "select action, reason_code from analytics.canonical_fact_retired where run_id = 'r3' and action = 'removed'"
    ).fetchall()
    assert row == [("removed", sb.REASON_CODE)]


def test_split_event_check_rejects_confirmed_with_one_kind(conn):
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute(
            "insert into analytics.split_event (company_id, ratio, basis_date, evidence,"
            " evidence_kinds, status, detector_version) values"
            " (1, 4, '2020-10-30', '{}', array['share_step'], 'confirmed', 'v')"
        )
