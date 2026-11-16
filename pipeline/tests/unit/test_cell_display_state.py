"""analytics.cell_display_state (migration 0130) and its writer mapper/cell_display_state.py.

Pure tests build the table rows; DB tests run the migration's own SQL (foreign key to core.company stripped, the table
is created in an isolated test database) and prove the writer's scoping and the constraints."""

import re
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import cell_display_state as cds
from scrooner_pipeline.mapper import top100_coverage as t100

DB = Path(__file__).parents[2] / "db"


def _migration_sql() -> str:
    found = list(DB.glob("pending/0130_cell_display_state.sql")) + list(
        DB.glob("migrations/0130_cell_display_state.sql")
    )
    assert len(found) == 1
    sql = found[0].read_text()
    return re.sub(r"references core\.company \(id\)", "", sql)


def _cell(cid, dp, end, display, hc="", **kw):
    r = {
        "company_id": cid,
        "ticker": "T",
        "data_point": dp,
        "period_end": end,
        "display": display,
        "hide_class": hc,
        "accession": "0001-24-000001",
        "r_page": "R2.htm",
        "evidence": "",
        "reason": "",
    }
    r.update(kw)
    return r


def test_hide_class_values_match_the_classes_apply_display_assigns():
    sql = _migration_sql()
    listed = set(
        re.findall(
            r"'(\w+)'",
            re.search(r"hide_class\s+text\s+check \(hide_class in \(([^)]*)\)", sql).group(1),
        )
    )
    assert listed == set(cds.HIDE_CLASSES)
    # HIDE_ELIGIBLE's values are a subset; verified_absent is assigned directly by apply_display
    assert set(t100.HIDE_ELIGIBLE.values()) | {t100.HC_VERIFIED_ABSENT} == listed


def test_state_rows_grain_hide_class_and_out():
    rows = [
        _cell(1, "cash_and_equivalents", "2024-12-31", t100.SHOWN_VALUE),
        _cell(1, "revenue", "2024-12-31", t100.HIDDEN_ROW, "structural_not_presented", reason="not presented"),
        _cell(1, "sbc", "2024-12-31", t100.OPEN),
    ]
    out = [_cell(1, "net_interest_income", "2024-12-31", "")]
    got = {(t[1], t[3]): t for t in cds.state_rows(rows, out, "run1", "0.68")}
    assert got[("cash_and_equivalents", "I")][4:6] == ("SHOWN_VALUE", None)
    assert got[("revenue", "FY")][4:6] == ("HIDDEN_ROW", "structural_not_presented")
    assert got[("revenue", "FY")][7] == "not presented"
    assert got[("sbc", "FY")][4:6] == ("OPEN", None)
    assert got[("net_interest_income", "FY")][4:] == ("OUT", None, None, None, None, "0.68", "run1")


def test_hidden_cell_with_a_pipeline_state_class_is_refused():
    with pytest.raises(ValueError):
        cds.state_rows([_cell(1, "sbc", "2024-12-31", t100.HIDDEN_YEAR, "")], [], "r", None)
    with pytest.raises(ValueError):
        cds.state_rows([_cell(1, "sbc", "2024-12-31", t100.HIDDEN_YEAR, "era_unmapped")], [], "r", None)


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists analytics cascade; drop schema if exists core cascade")
        c.execute("create schema core; create schema analytics")
        c.execute(_migration_sql())
        c.commit()
        yield c


def _count(c, cid):
    return c.execute(
        "select count(*) from analytics.cell_display_state where company_id = %s", (cid,)
    ).fetchone()[0]


def test_writer_replaces_only_the_exported_company(db):
    base = [
        _cell(1, "revenue", "2023-12-31", t100.SHOWN_VALUE),
        _cell(1, "revenue", "2024-12-31", t100.SHOWN_VALUE),
        _cell(2, "revenue", "2024-12-31", t100.SHOWN_VALUE),
        _cell(2, "sbc", "2024-12-31", t100.OPEN),
    ]
    cds.write_display_state(db, cds.state_rows(base, [], "r1", "0.68"))
    assert (_count(db, 1), _count(db, 2)) == (2, 2)
    # re-export company 1 alone with one cell now hidden and one fewer row: company 2 is untouched
    again = [_cell(1, "revenue", "2024-12-31", t100.HIDDEN_ROW, "structural_not_presented")]
    written = cds.write_display_state(db, cds.state_rows(again, [], "r2", "0.69"))
    assert written == {1: 1}
    assert (_count(db, 1), _count(db, 2)) == (1, 2)
    assert db.execute(
        "select distinct run_id from analytics.cell_display_state where company_id = 2"
    ).fetchall() == [("r1",)]
    assert db.execute(
        "select display, hide_class from analytics.cell_display_state where company_id = 1"
    ).fetchall() == [("HIDDEN_ROW", "structural_not_presented")]


def test_writer_batches_and_rolls_back_a_company_on_error(db):
    cells = [_cell(1, "revenue", "2024-12-31", t100.SHOWN_VALUE)]
    cds.write_display_state(db, cds.state_rows(cells, [], "r1", None))
    rows = cds.state_rows(
        [_cell(1, "revenue", "2024-12-31", t100.SHOWN_VALUE), _cell(1, "sbc", "2024-12-31", t100.OPEN)],
        [],
        "r2",
        None,
    )
    bad = rows + [(1, "x", "2024-12-31", "FY", "HIDDEN_ROW", None, None, None, None, None, "r2")]
    with pytest.raises(psycopg.errors.CheckViolation):
        cds.write_display_state(db, bad)
    # the failed company transaction rolled back: the old row is still there
    assert db.execute(
        "select run_id from analytics.cell_display_state where company_id = 1"
    ).fetchall() == [("r1",)]


def test_batch_size_is_capped():
    assert cds.BATCH <= 5000


@pytest.mark.parametrize(
    "display,hc",
    [
        ("HIDDEN_ROW", None),
        ("HIDDEN_YEAR", None),
        ("SHOWN_VALUE", "pre_filing"),
        ("OPEN", "verified_absent"),
        ("OUT", "structural_not_presented"),
        ("HIDDEN_YEAR", "era_unmapped"),
        ("MAYBE", None),
    ],
)
def test_constraint_refuses_bad_combinations(db, display, hc):
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, hide_class) "
            "values (1, 'x', '2024-12-31', 'FY', %s, %s)",
            (display, hc),
        )


@pytest.mark.parametrize(
    "display,hc",
    [
        ("HIDDEN_ROW", "structural_not_presented"),
        ("HIDDEN_YEAR", "line_presented_combined"),
        ("HIDDEN_YEAR", "pre_filing"),
        ("HIDDEN_ROW", "verified_absent"),
        ("SHOWN_VALUE", None),
        ("OUT", None),
        ("OPEN", None),
    ],
)
def test_constraint_accepts_valid_combinations(db, display, hc):
    db.execute(
        "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, hide_class) "
        "values (1, 'x', '2024-12-31', 'FY', %s, %s)",
        (display, hc),
    )

