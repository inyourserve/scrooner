"""Proposed migration 0135 (one-display-path plan 2026-11-22, step 3): the badge CHECK never drifts from
metrics/registry.BADGE_KINDS.

0135 is not claimed or applied (founder's typed words needed; 0133 first). Until its file exists the SQL is rendered by
cell_display_state.proposed_0135_sql(); these tests replay it on Postgres 16 over the committed schema plus pending
0130/0133, and hold every migration file that carries the badge CHECK (pending/ or migrations/) to BADGE_KINDS."""

import re
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import cell_display_state as cds
from scrooner_pipeline.metrics import registry as reg

DB = Path(__file__).parents[2] / "db"


def _file(n: str) -> str:
    found = list(DB.glob(f"pending/{n}_*.sql")) + list(DB.glob(f"migrations/{n}_*.sql"))
    assert len(found) == 1, n
    return found[0].read_text()


def _filled(badge: str) -> str:
    return re.sub(r"<[^>]*>", "Accounts payable and accrued liabilities", badge)


def test_draft_check_admits_exactly_the_registry_badge_kinds():
    assert cds.badge_kinds_in_check(cds.proposed_0135_sql()) == reg.BADGE_KINDS


def test_every_migration_with_the_badge_check_matches_badge_kinds():
    files = sorted(list(DB.glob("pending/*.sql")) + list(DB.glob("migrations/*.sql")))
    for p in files:
        kinds = cds.badge_kinds_in_check(p.read_text())
        if kinds is not None:
            assert kinds == reg.BADGE_KINDS, p.name
    # the parser itself sees a drifted list
    drifted = cds.proposed_0135_sql().replace("|perimeter", "")
    assert cds.badge_kinds_in_check(drifted) != reg.BADGE_KINDS


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute(_file("0130"))
        c.execute(_file("0133"))
        c.execute(cds.proposed_0135_sql())
        cid = c.execute(
            "insert into core.company (cik, company_name) values ('0000000135', 'BADGE TEST') returning id"
        ).fetchone()[0]
        c.commit()
        yield c, cid


def _insert(c, cid, dp, display, badge, hc=None, value=None):
    c.execute(
        "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, hide_class, badge, value) "
        "values (%s, %s, '2024-12-31', 'FY', %s, %s, %s, %s)",
        (cid, dp, display, hc, badge, value),
    )


def test_every_data_points_badge_is_accepted_on_a_shown_cell(db):
    c, cid = db
    badges = sorted(
        {_filled(b) for d in reg.load_data_points().values() for b in d.badges}
    )
    assert any(b.startswith("perimeter:") for b in badges)
    for i, b in enumerate(badges):
        _insert(c, cid, f"dp{i}", "SHOWN_VALUE", b, value=1)
    c.commit()


@pytest.mark.parametrize(
    "display,badge,hc",
    [
        ("SHOWN_VALUE", None, None),  # a shown cell needs a badge
        ("SHOWN_VALUE", "printed", None),  # not a kind
        ("SHOWN_VALUE", "combined:", None),  # a kind with nothing named
        ("SHOWN_VALUE", "derived:  ", None),
        ("SHOWN_VALUE", "as_printed:x", None),
        ("OPEN", "as_printed", None),  # a badge only on a shown cell
        ("HIDDEN_ROW", "as_printed", "structural_not_presented"),
    ],
)
def test_check_refuses(db, display, badge, hc):
    c, cid = db
    with pytest.raises(psycopg.errors.CheckViolation):
        _insert(c, cid, "x", display, badge, hc)


def test_value_only_on_a_shown_cell(db):
    c, cid = db
    with pytest.raises(psycopg.errors.CheckViolation):
        _insert(c, cid, "x", "OPEN", None, value=5)


def test_writer_with_badges_writes_the_three_columns(db):
    from decimal import Decimal

    from scrooner_pipeline.mapper import top100_coverage as t100

    c, cid = db
    rows = [
        {
            "company_id": cid,
            "ticker": "T",
            "data_point": "revenue",
            "period_end": "2024-12-31",
            "display": t100.SHOWN_VALUE,
            "hide_class": "",
            "accession": "0001-24-000001",
            "r_page": "R4.htm",
            "shown_value": "100.5",
            "_badge": "as_printed",
            "_canonical_fact_id": None,
        }
    ]
    cds.write_display_state(c, cds.state_rows(rows, [], "r", "v"), with_badges=True)
    assert c.execute(
        "select badge, value from analytics.cell_display_state where company_id = %s",
        (cid,),
    ).fetchall() == [("as_printed", Decimal("100.5"))]
