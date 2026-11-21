"""mapper/shown_inputs.py::load_shown_cells (one-display-path plan 2026-11-22, step 4): metrics read shown cells only.

Postgres 16: the committed schema plus pending 0130/0133 and the proposed 0135 (cell_display_state.proposed_0135_sql,
which creates analytics.shown_cell). A DISAGREE cell, a hidden row, an OPEN cell and a canonical_fact row with no display
state are absent; a NOT_PRESENTED hidden row is kept (as a zero input) only for a zero_when_absent concept."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import cell_display_state as cds
from scrooner_pipeline.mapper import shown_inputs as si
from scrooner_pipeline.metrics import provenance as prov
from scrooner_pipeline.metrics.registry import get_registry

DB = Path(__file__).parents[2] / "db"
FY = (date(2024, 1, 1), date(2024, 12, 31))


def _file(n: str) -> str:
    found = list(DB.glob(f"pending/{n}_*.sql")) + list(DB.glob(f"migrations/{n}_*.sql"))
    assert len(found) == 1, n
    return found[0].read_text()


def _setup(c):
    c.execute(_file("0130"))
    c.execute(_file("0133"))
    c.execute(cds.proposed_0135_sql())
    cid = c.execute(
        "insert into core.company (cik, company_name) values ('0000000136', 'SHOWN TEST') returning id"
    ).fetchone()[0]
    dur = c.execute(
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
        "values (%s, %s, %s, 'duration', 2024, 'FY') returning id",
        (cid, *FY),
    ).fetchone()[0]
    inst = c.execute(
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
        "values (%s, %s, %s, 'instant', 2024, 'FY') returning id",
        (cid, FY[1], FY[1]),
    ).fetchone()[0]
    concept = {}
    for name in (
        "revenue",
        "gross_profit",
        "net_income",
        "accounts_payable",
        "sga_expense",
        "cash_and_equivalents",
        "total_assets",
        "inventory",
        "research_and_development",
    ):
        concept[name] = c.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode) "
            "values (%s, 'income_statement', 'first_match') on conflict (name) do update set name = excluded.name "
            "returning id",
            (name,),
        ).fetchone()[0]
    return cid, dur, inst, concept


def _fact(c, cid, concept_id, period_id, value):
    return c.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
        "values (%s, %s, %s, %s, '{11}') returning id",
        (cid, concept_id, period_id, value),
    ).fetchone()[0]


def _proof(c, cid, name, grain, start, end, verdict, value=None):
    c.execute(
        "insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end, "
        "shown_value, position_value, position_is_expected_line, verdict, reason_code, detector_version) "
        "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'test')",
        (
            cid,
            name,
            grain,
            start,
            end,
            value,
            value if verdict == "PROVEN" else None,
            True if verdict == "PROVEN" else None,
            verdict,
            "r" if verdict in ("DISAGREE", "NOT_PRESENTED") else None,
        ),
    )


def _state(c, cid, dp, grain, display, hc=None, badge=None, value=None, fact_id=None):
    c.execute(
        "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, hide_class, "
        "badge, value, canonical_fact_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (cid, dp, FY[1], grain, display, hc, badge, value, fact_id),
    )


@pytest.fixture
def loaded(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        cid, dur, inst, k = _setup(c)
        # shown + PROVEN: inputs
        f = _fact(c, cid, k["revenue"], dur, Decimal(1000))
        _proof(c, cid, "revenue", "FY", *FY, "PROVEN", Decimal(1000))
        _state(
            c,
            cid,
            "revenue",
            "FY",
            "SHOWN_VALUE",
            badge="as_printed",
            value=Decimal(1000),
            fact_id=f,
        )
        f = _fact(c, cid, k["gross_profit"], dur, Decimal(400))
        _proof(c, cid, "gross_profit", "FY", *FY, "PROVEN", Decimal(400))
        _state(
            c,
            cid,
            "gross_profit",
            "FY",
            "SHOWN_VALUE",
            badge="derived:revenue-cost_of_revenue",
            value=Decimal(400),
            fact_id=f,
        )
        f = _fact(c, cid, k["cash_and_equivalents"], inst, Decimal(50))
        _proof(c, cid, "cash_and_equivalents", "I", FY[1], FY[1], "PROVEN", Decimal(50))
        _state(
            c,
            cid,
            "cash_and_equivalents",
            "I",
            "SHOWN_VALUE",
            badge="as_printed",
            value=Decimal(50),
            fact_id=f,
        )
        # DISAGREE (even if a stale export marked it shown): absent
        f = _fact(c, cid, k["net_income"], dur, Decimal(90))
        _proof(c, cid, "net_income", "FY", *FY, "DISAGREE", Decimal(90))
        _state(
            c,
            cid,
            "net_income",
            "FY",
            "SHOWN_VALUE",
            badge="as_printed",
            value=Decimal(90),
            fact_id=f,
        )
        # HIDDEN_ROW with a served value: absent
        f = _fact(c, cid, k["accounts_payable"], inst, Decimal(30))
        _proof(c, cid, "accounts_payable", "I", FY[1], FY[1], "UNCHECKED", Decimal(30))
        _state(
            c, cid, "accounts_payable", "I", "HIDDEN_ROW", hc="line_presented_combined"
        )
        # OPEN with a PROVEN proof: absent (the page does not show it)
        f = _fact(c, cid, k["sga_expense"], dur, Decimal(70))
        _proof(c, cid, "sga_expense", "FY", *FY, "PROVEN", Decimal(70))
        _state(c, cid, "sga_expense", "FY", "OPEN")
        # a canonical_fact row with no display state at all: absent
        _fact(c, cid, k["total_assets"], inst, Decimal(5000))
        _proof(c, cid, "total_assets", "I", FY[1], FY[1], "PROVEN", Decimal(5000))
        # NOT_PRESENTED hidden rows: inventory is zero_when_absent (quick_ratio), R&D is not
        _proof(c, cid, "inventory", "I", FY[1], FY[1], "NOT_PRESENTED")
        _state(c, cid, "inventory", "I", "HIDDEN_ROW", hc="structural_not_presented")
        _proof(c, cid, "research_and_development", "FY", *FY, "NOT_PRESENTED")
        _state(
            c,
            cid,
            "research_and_development",
            "FY",
            "HIDDEN_ROW",
            hc="structural_not_presented",
        )
        c.commit()
        yield si.load_shown_cells(c, cid), k, dur, inst


def test_only_shown_proven_cells_are_value_inputs(loaded):
    got, k, dur, _inst = loaded
    assert set(got["by_period_id"]) == {
        k["revenue"],
        k["gross_profit"],
        k["cash_and_equivalents"],
    }
    assert got["by_period_id"][k["revenue"]][dur] == (Decimal(1000), [11])
    assert got["by_end_date"] == {
        k["cash_and_equivalents"]: {FY[1]: (Decimal(50), [11])}
    }
    for absent in (
        "net_income",
        "accounts_payable",
        "sga_expense",
        "total_assets",
        "research_and_development",
    ):
        assert all(cell.concept != absent for cell in got["cells"].values()), absent
        assert k[absent] not in got["by_period_id"]


def test_badges_travel_with_the_cell_and_into_the_metric(loaded):
    got, k, dur, _ = loaded
    gp = got["cells"][(k["gross_profit"], dur)]
    assert (gp.status, gp.badge) == ("PROVEN", "derived:revenue-cost_of_revenue")
    assert prov.metric_badge(got["cells"].values()) == "derived:revenue-cost_of_revenue"


def test_not_presented_zero_only_for_a_zero_when_absent_concept(loaded):
    got, k, _, inst = loaded
    inv = got["cells"][(k["inventory"], inst)]
    assert (inv.status, inv.value) == ("NOT_PRESENTED", Decimal(0))
    # never a zero in the value maps: only a metric that lists it (quick_ratio) reads it as zero, via gate_inputs
    assert k["inventory"] not in got["by_period_id"]
    m = get_registry()["quick_ratio"]
    assert "inventory" in m.zero_when_absent
    values, blocked = prov.gate_inputs(m, {"inventory": inv})
    assert values["inventory"] == 0 and blocked is None


def test_a_missing_input_blocks_the_metric_with_a_reason(loaded):
    got, k, dur, _ = loaded
    net_income = got["cells"].get((k["net_income"], dur))
    assert net_income is None
    m = get_registry()["net_margin"]
    cell = net_income or prov.InputCell(concept="net_income", status="MISSING")
    values, blocked = prov.gate_inputs(
        m, {"net_income": cell, "revenue": got["cells"][(k["revenue"], dur)]}
    )
    assert (
        values["net_income"] is None
        and blocked == "input_not_served:net_income:MISSING"
    )


def test_the_loader_reads_the_view_never_canonical_fact():
    assert "analytics.shown_cell" in si.SHOWN_CELL_SQL
    assert "canonical_fact" not in si.SHOWN_CELL_SQL
