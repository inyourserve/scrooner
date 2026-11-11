"""canonical_archive on the REAL analytics schema with the slot-protected-cell
guard (migrations 0113/0115): the archive rows and the counts follow the
ACTUAL update, not the attempt. Found 2026-11-10 in the share-basis writer,
which does not set scrooner.slot_writer."""

from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.mapper import canonical_archive as ca
from scrooner_pipeline.mapper.canonical_archive import CanonicalRow

pytestmark = pytest.mark.integration

RUN = "sb-protected-test"


def _one(c, sql, params=()):
    return c.execute(sql, params).fetchone()[0]


@pytest.fixture
def seeded(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    have = _one(
        c,
        "select count(*) from information_schema.tables where table_schema = 'analytics'"
        " and table_name in ('slot_protected_cell', 'slot_protected_write_skipped', 'canonical_fact_retired')",
    )
    if have != 3:
        c.close()
        pytest.skip("needs the migrated schema with migrations 0098 and 0113")
    company = _one(
        c,
        "insert into core.company (cik, company_name) values ('0000000777', 'PROT') returning id",
    )
    cc = _one(
        c,
        "insert into analytics.canonical_concept (name, statement, combination_mode)"
        " values ('prot_test_eps', 'income_statement', 'first_match') returning id",
    )
    periods = [
        _one(
            c,
            "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)"
            " values (%s, %s, %s, 'duration', %s, 'Q4') returning id",
            (company, f"{fy}-10-01", f"{fy}-12-31", fy),
        )
        for fy in (2019, 2020, 2021)
    ]
    cells = [
        _one(
            c,
            "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)"
            " values (%s, %s, %s, %s, %s) returning id",
            (company, cc, p, Decimal("10"), [p]),
        )
        for p in periods[:2]
    ]
    # periods[0] is protected (a slot release wrote it); periods[1] is not.
    c.execute(
        "insert into analytics.slot_protected_cell (company_id, canonical_concept_id, period_id, rule_id,"
        " value, run_id, package_sha256) values (%s, %s, %s, 'test_rule', 10, 'slot-run', repeat('0', 64))",
        (company, cc, periods[0]),
    )
    c.commit()
    yield {"c": c, "company": company, "cc": cc, "periods": periods, "cells": cells}
    c.close()


def _value(c, cell):
    return _one(c, "select value from analytics.canonical_fact where id = %s", (cell,))


def _skipped(c, company, cc, period):
    return c.execute(
        "select operation from analytics.slot_protected_write_skipped"
        " where company_id = %s and canonical_concept_id = %s and period_id = %s",
        (company, cc, period),
    ).fetchall()


def test_replace_rows_archives_and_counts_only_what_really_changed(seeded):
    c, co, cc, per, cells = (
        seeded[k] for k in ("c", "company", "cc", "periods", "cells")
    )
    rows = [
        CanonicalRow(co, cc, per[0], Decimal("2.5"), (per[0],)),  # protected
        CanonicalRow(co, cc, per[1], Decimal("2.5"), (per[1],)),  # unprotected
    ]
    with c.cursor() as cur:
        stats = ca.replace_rows(cur, rows, reason_code="split_rebase", run_id=RUN)
    c.commit()
    assert stats == {
        "unchanged": 0,
        "replaced": 1,
        "inserted": 0,
        "skipped_protected": 1,
    }
    assert _value(c, cells[0]) == Decimal("10")  # protected value unchanged
    assert _value(c, cells[1]) == Decimal("2.5")
    archived = c.execute(
        "select canonical_fact_id, action, value from analytics.canonical_fact_retired where run_id = %s",
        (RUN,),
    ).fetchall()
    assert archived == [
        (cells[1], "replaced", Decimal("10"))
    ]  # before-image, none for the protected key
    assert [r[0] for r in _skipped(c, co, cc, per[0])] == ["UPDATE"]
    assert _skipped(c, co, cc, per[1]) == []


def test_replace_rows_insert_of_a_protected_blank_is_skipped_not_logged(seeded):
    c, co, cc, per = (seeded[k] for k in ("c", "company", "cc", "periods"))
    # periods[2] has no stored row but is a protected blank (migration 0115).
    c.execute(
        "insert into analytics.slot_protected_cell (company_id, canonical_concept_id, period_id, rule_id,"
        " value, run_id, package_sha256) values (%s, %s, %s, 'test_rule', null, 'slot-run', repeat('0', 64))",
        (co, cc, per[2]),
    )
    c.commit()
    with c.cursor() as cur:
        stats = ca.replace_rows(
            cur,
            [CanonicalRow(co, cc, per[2], Decimal("3"), (1,))],
            reason_code="split_rebase",
            run_id=RUN,
        )
    c.commit()
    assert stats["inserted"] == 0 and stats["skipped_protected"] == 1
    assert (
        _one(
            c,
            "select count(*) from analytics.canonical_fact where period_id = %s",
            (per[2],),
        )
        == 0
    )
    assert (
        _one(
            c,
            "select count(*) from analytics.canonical_fact_retired where run_id = %s",
            (RUN,),
        )
        == 0
    )
    assert [r[0] for r in _skipped(c, co, cc, per[2])] == ["INSERT"]


def test_archive_and_remove_archives_only_what_was_really_deleted(seeded):
    c, co, cc, per, cells = (
        seeded[k] for k in ("c", "company", "cc", "periods", "cells")
    )
    with c.cursor() as cur:
        n = ca.archive_and_remove(cur, cells, reason_code="split_rebase", run_id=RUN)
    c.commit()
    assert n == 1  # only the unprotected row went
    assert _value(c, cells[0]) == Decimal("10")  # protected row still there
    assert c.execute(
        "select id from analytics.canonical_fact where id = any(%s)", (cells,)
    ).fetchall() == [(cells[0],)]
    archived = c.execute(
        "select canonical_fact_id, action from analytics.canonical_fact_retired where run_id = %s",
        (RUN,),
    ).fetchall()
    assert archived == [(cells[1], "removed")]
    assert [r[0] for r in _skipped(c, co, cc, per[0])] == ["DELETE"]
