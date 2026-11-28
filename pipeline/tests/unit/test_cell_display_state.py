"""analytics.cell_display_state (migration 0130) and its writer mapper/cell_display_state.py.

Pure tests build the table rows; DB tests run the migration's own SQL (foreign key to core.company stripped, the table
is created in an isolated test database) and prove the writer's scoping and the constraints."""

import re
from decimal import Decimal
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


def _effective_hide_classes() -> set[str]:
    """The hide_class CHECK in force: 0130's column CHECK, replaced by the newest later migration that re-adds
    cell_display_state_hide_class_check (0133 added only_after_tax_disclosed; 0130 is applied and never edited)."""
    listed = set(
        re.findall(
            r"'(\w+)'",
            re.search(
                r"hide_class\s+text\s+check \(hide_class in \(([^)]*)\)",
                _migration_sql(),
            ).group(1),
        )
    )
    later = sorted(
        p
        for p in list(DB.glob("pending/*.sql")) + list(DB.glob("migrations/*.sql"))
        if p.name[:4] > "0130"
    )
    for p in later:
        m = re.search(
            r"add constraint cell_display_state_hide_class_check\s+check \(hide_class in \(([^)]*)\)",
            p.read_text(),
        )
        if m:
            listed = set(re.findall(r"'(\w+)'", m.group(1)))
    return listed


def test_hide_class_values_match_the_classes_apply_display_assigns():
    listed = _effective_hide_classes()
    assert listed == set(cds.HIDE_CLASSES)
    # HIDE_ELIGIBLE's values are a subset; verified_absent is assigned directly by apply_display
    assert set(t100.HIDE_ELIGIBLE.values()) | {t100.HC_VERIFIED_ABSENT} == listed


def test_state_rows_grain_hide_class_and_out():
    rows = [
        _cell(1, "cash_and_equivalents", "2024-12-31", t100.SHOWN_VALUE),
        _cell(
            1,
            "revenue",
            "2024-12-31",
            t100.HIDDEN_ROW,
            "structural_not_presented",
            reason="not presented",
        ),
        _cell(1, "sbc", "2024-12-31", t100.OPEN),
    ]
    out = [_cell(1, "net_interest_income", "2024-12-31", "")]
    got = {(t[1], t[3]): t for t in cds.state_rows(rows, out, "run1", "0.68")}
    assert got[("cash_and_equivalents", "I")][4:6] == ("SHOWN_VALUE", None)
    assert got[("revenue", "FY")][4:6] == ("HIDDEN_ROW", "structural_not_presented")
    assert got[("revenue", "FY")][7] == "not presented"
    assert got[("sbc", "FY")][4:6] == ("OPEN", None)
    assert got[("net_interest_income", "FY")][4:11] == (
        "OUT",
        None,
        None,
        None,
        None,
        "0.68",
        "run1",
    )


def test_shown_cell_has_badge_and_value():
    """One-display-path step 2: a SHOWN_VALUE cell carries badge, value and canonical_fact_id after COLUMNS; every
    other cell carries none of them."""
    rows = [
        _cell(
            1,
            "gross_profit",
            "2024-12-31",
            t100.SHOWN_VALUE,
            shown_value="1234.50",
            _badge="derived:revenue-cost_of_revenue",
            _canonical_fact_id=77,
        ),
        _cell(
            1,
            "revenue",
            "2024-12-31",
            t100.SHOWN_VALUE,
            shown_value="9000",
            _badge="as_printed",
            _canonical_fact_id=78,
        ),
        _cell(
            1,
            "sbc",
            "2024-12-31",
            t100.OPEN,
            shown_value="5",
            _badge="as_printed",
            _canonical_fact_id=79,
        ),
        _cell(
            1, "inventory", "2024-12-31", t100.HIDDEN_ROW, "structural_not_presented"
        ),
    ]
    got = {t[1]: t for t in cds.state_rows(rows, [], "r", "v")}
    assert len(cds.COLUMNS + cds.BADGE_COLUMNS) == 14
    assert all(len(t) == 14 for t in got.values())
    assert got["gross_profit"][11:] == (
        "derived:revenue-cost_of_revenue",
        Decimal("1234.50"),
        77,
    )
    assert got["revenue"][11:] == ("as_printed", Decimal(9000), 78)
    assert got["sbc"][11:] == (None, None, None)
    assert got["inventory"][11:] == (None, None, None)


def test_attach_badges_reads_the_resolver_step_and_records_undecided_cells():
    from datetime import date

    steps = {
        ("T", "gross_profit"): [
            (
                date(2024, 12, 31),
                {
                    "decision": "derived_not_printed",
                    "flags": "core;DERIVED",
                    "nodes": "",
                },
            )
        ],
        # FSN month-end key against a 52/53-week true end
        ("T", "revenue"): [
            (date(2024, 9, 30), {"decision": "mapped", "flags": "core", "nodes": ""})
        ],
        ("T", "other_income_expense_net"): [
            (
                date(2024, 12, 31),
                {"decision": "component_sum", "flags": "roles", "nodes": ""},
            )
        ],
    }
    rows = [
        _cell(1, "gross_profit", "2024-12-31", t100.SHOWN_VALUE, _sector="general"),
        _cell(1, "revenue", "2024-09-28", t100.SHOWN_VALUE, _sector="general"),
        _cell(
            1,
            "other_income_expense_net",
            "2024-12-31",
            t100.SHOWN_VALUE,
            _sector="general",
            parts="OtherNonoperatingIncomeExpense=1@0001-24-000001#R2;InvestmentIncomeInterest=2@0001-24-000001#R2",
        ),
        _cell(
            1, "cash_and_equivalents", "2024-12-31", t100.SHOWN_VALUE, _sector="general"
        ),
        _cell(1, "gross_profit", "2023-12-31", t100.OPEN, _sector="general"),
    ]
    t100.attach_badges(rows, steps)
    assert [r["_badge"] for r in rows] == [
        "derived:revenue-cost_of_revenue",
        "as_printed",
        # a sum of printed non-operating lines has its own step (MA/WMT 2026-11-22)
        "derived:sum(printed nonoperating lines)",
        None,
        None,
    ]
    # a shown cell with no resolver row and no located printed fact fits no step: OPEN with the reason, never shown
    # with a blank badge
    assert rows[3]["_badge_issue"] == "no_resolver_row"
    assert (rows[3]["display"], rows[3]["reason_code"]) == (
        t100.OPEN,
        t100.NO_REGISTRY_STEP,
    )
    assert [r["display"] for r in rows[:3]] == [t100.SHOWN_VALUE] * 3
    assert rows[4]["_badge_issue"] == "" and rows[4]["display"] == t100.OPEN


def test_attach_badges_reads_the_cells_own_evidence_when_the_resolver_names_no_step():
    """MA net_income FY2024-25 (approver 2026-11-22): the resolver says no_role, the cell proof shows ProfitLoss on R3.
    One printed fact -> as_printed; printed parts of one filing that add up -> the additive step; a resolver row that
    names an unplaceable step is never second-guessed; anything else is OPEN no_registry_step. Mutation: drop the
    proof_step fallback and the first two cells lose their badge."""
    from datetime import date

    acc = "0001141391-25-000011"
    rows = [
        _cell(
            1,
            "net_income",
            "2024-12-31",
            t100.SHOWN_VALUE,
            _sector="general",
            accession=acc,
            r_page="R3.htm",
            tag="ProfitLoss",
            shown_value="12874000000",
            parts="",
        ),
        _cell(
            1,
            "shares_outstanding",
            "2024-12-31",
            t100.SHOWN_VALUE,
            _sector="general",
            accession=acc,
            r_page="R6.htm",
            tag="CommonStockSharesOutstanding",
            shown_value="894000000",
            parts=f"CommonStockSharesOutstanding[ClassOfStock=CommonClassA]=887000000@{acc}#R6;"
            f"CommonStockSharesOutstanding[ClassOfStock=CommonClassB]=7000000@{acc}#R6",
        ),
        # parts that do not add up to the shown value: no step
        _cell(
            1,
            "interest_expense",
            "2024-12-31",
            t100.SHOWN_VALUE,
            _sector="general",
            accession=acc,
            r_page="R3.htm",
            tag="A,B",
            shown_value="10",
            parts=f"A=4@{acc}#R3;B=5@{acc}#R3",
        ),
        # the resolver names a step the registry cannot place (inventory has no additive step): stays undecided (no evidence override)
        _cell(
            1,
            "inventory",
            "2024-12-31",
            t100.SHOWN_VALUE,
            _sector="general",
            accession=acc,
            r_page="R2.htm",
            tag="InventoryNet",
            shown_value="5",
            parts="",
        ),
    ]
    steps = {
        ("T", "inventory"): [
            (
                date(2024, 12, 31),
                {"decision": "component_sum", "flags": "", "nodes": ""},
            )
        ]
    }
    t100.attach_badges(rows, steps)
    assert [r["badge"] for r in rows] == [
        "as_printed",
        "derived:sum(class shares outstanding)",
        "",
        "",
    ]
    assert [r["display"] for r in rows] == [
        t100.SHOWN_VALUE,
        t100.SHOWN_VALUE,
        t100.OPEN,
        t100.OPEN,
    ]
    assert rows[3]["_badge_issue"].startswith("badge_undecided")
    assert all(r["reason_code"] == t100.NO_REGISTRY_STEP for r in rows[2:])


def test_writer_writes_the_0130_columns_until_0135():
    assert cds.WRITE_BADGE_COLUMNS is False
    assert "badge" not in cds.INSERT_SQL


def test_hidden_cell_with_a_pipeline_state_class_is_refused():
    with pytest.raises(ValueError):
        cds.state_rows(
            [_cell(1, "sbc", "2024-12-31", t100.HIDDEN_YEAR, "")], [], "r", None
        )
    with pytest.raises(ValueError):
        cds.state_rows(
            [_cell(1, "sbc", "2024-12-31", t100.HIDDEN_YEAR, "era_unmapped")],
            [],
            "r",
            None,
        )


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute(
            "drop schema if exists analytics cascade; drop schema if exists core cascade"
        )
        c.execute("create schema core; create schema analytics")
        c.execute(_migration_sql())
        c.commit()
        yield c


def _count(c, cid):
    return c.execute(
        "select count(*) from analytics.cell_display_state where company_id = %s",
        (cid,),
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
    again = [
        _cell(1, "revenue", "2024-12-31", t100.HIDDEN_ROW, "structural_not_presented")
    ]
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
        [
            _cell(1, "revenue", "2024-12-31", t100.SHOWN_VALUE),
            _cell(1, "sbc", "2024-12-31", t100.OPEN),
        ],
        [],
        "r2",
        None,
    )
    bad = rows + [
        (1, "x", "2024-12-31", "FY", "HIDDEN_ROW", None, None, None, None, None, "r2")
    ]
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


def test_every_flow_coverage_export_writes_display_state():
    flow = (Path(__file__).parents[3] / "scripts" / "top100_flow.sh").read_text()
    calls = [
        ln for ln in flow.splitlines() if "pipeline/scripts/top100_coverage.py" in ln
    ]
    assert len(calls) == 2
    assert all("--write-display-state" in ln for ln in calls)
    assert not any("default_transaction_read_only" in ln for ln in calls)


def test_a_summed_cell_without_parts_is_never_shown_bmy_opex():
    """Verifier 2026-11-22 (BMY operating_expenses FY2017-18, coverage 2a1319707e95): a cell badged derived:sum(...)
    must export the printed parts it adds; without them it is OPEN with the reason, never shown. A read whose element
    lists each line with its value exports those parts. Mutation: drop the derived:sum check in attach_badges."""
    from datetime import date

    steps = {
        ("T", "operating_expenses"): [
            (
                date(2017, 12, 31),
                {
                    "decision": "mapped",
                    "flags": "filing_read;text_stated;derived:sum(printed operating lines)",
                    "nodes": "",
                },
            )
        ],
    }
    bare = _cell(
        1, "operating_expenses", "2017-12-31", t100.SHOWN_VALUE, _sector="general"
    )
    acc = "0000014272-20-000082"
    loc = (
        "R2.htm (us-gaap:SellingGeneralAndAdministrativeExpense=4751000000 + us-gaap:ResearchAndDevelopmentExpense=6468000000"
        " + bmy:AmortizationofAcquiredIntangibleAssets=97000000 (the printed operating lines)) of "
        + acc
        + ", read FY2017 10-K"
    )
    parts = t100.locator_valued_parts(loc, acc, Decimal("11316000000"))
    assert parts == (
        f"SellingGeneralAndAdministrativeExpense=4751000000@{acc}#R2;ResearchAndDevelopmentExpense=6468000000@{acc}#R2;"
        f"AmortizationofAcquiredIntangibleAssets=97000000@{acc}#R2"
    )
    assert (
        t100.locator_valued_parts(loc, acc, Decimal("11316000001")) == ""
    )  # parts must add up
    full = _cell(
        2,
        "operating_expenses",
        "2017-12-31",
        t100.SHOWN_VALUE,
        _sector="general",
        parts=parts,
    )
    full["company_id"] = 1
    t100.attach_badges([bare, full], steps)
    assert (bare["display"], bare["reason_code"]) == (t100.OPEN, t100.NO_REGISTRY_STEP)
    assert "without parts" in bare["reason"]
    assert (full["display"], full["badge"]) == (
        t100.SHOWN_VALUE,
        "derived:sum(printed operating lines)",
    )
