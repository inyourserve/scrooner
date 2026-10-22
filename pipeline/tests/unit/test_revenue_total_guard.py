"""Revenue-total disagreement guard (RF-13). Fixtures are FILING-CHECKED values from
data-team/37-REVENUE-TOTAL-RULE-2026-10-21.md section 2 (USD, full units)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal as D

import pytest

from scrooner_pipeline.common.cell_blank_reason import InMemoryBlankReasonStore
from scrooner_pipeline.mapper import revenue_total_guard as g

RCFC = "RevenueFromContractWithCustomerExcludingAssessedTax"
REV = "Revenues"


def F(tag, value, filing=1):
    return g.RevFact(tag, D(value), filing)


# (name, facts, expected scope) -- every row is a case where the two tags are filed for one period
DISAGREE = [
    (
        "EMR FY2022 (1,660 narrative Revenues vs 13,804 face)",
        [F(RCFC, "13804000000", 1), F(RCFC, "19629000000", 2), F(REV, "1660000000", 3)],
        "cross_filing",
    ),
    (
        "NTAP FY2026 (segment Revenues 6,237 vs face 6,925)",
        [F(RCFC, "6925000000", 1), F(REV, "6237000000", 1)],
        "same_filing",
    ),
    (
        "GE FY2024 (total 38,702 vs equipment/services 35,121)",
        [F(REV, "38702000000", 1), F(RCFC, "35121000000", 1)],
        "same_filing",
    ),
    (
        "MA FY2021 (net 18,884 vs gross 29,845)",
        [F(REV, "18884000000", 1), F(RCFC, "29845000000", 1)],
        "same_filing",
    ),
    (
        "FLS FY2025 (intersegment Revenues 0 vs sales 4,729,260K)",
        [F(RCFC, "4729260000", 1), F(REV, "0", 1)],
        "same_filing",
    ),
    (
        "GIS FY2021 (joint venture 2,189.2 vs 18,127.0)",
        [F(RCFC, "18127000000", 1), F(REV, "2189200000", 1)],
        "same_filing",
    ),
    (
        "BLK FY2024 (related-party 12,794 vs 20,407)",
        [F(RCFC, "20407000000", 1), F(REV, "12794000000", 1)],
        "same_filing",
    ),
    (
        "WMB FY2022 (RCFC 17,773 larger than total 10,965)",
        [F(REV, "10965000000", 1), F(RCFC, "17773000000", 1)],
        "same_filing",
    ),
    (
        "FCX FY2018 (18,628 vs 18,945)",
        [F(REV, "18628000000", 1), F(RCFC, "18945000000", 1)],
        "same_filing",
    ),
    (
        "DVN FY2021 (12,206 vs 13,750)",
        [F(REV, "12206000000", 1), F(RCFC, "13750000000", 1)],
        "same_filing",
    ),
    (
        "THC FY2017 (19,179 vs 20,613)",
        [F(REV, "19179000000", 1), F(RCFC, "20613000000", 1)],
        "same_filing",
    ),
    (
        "GE FY2018 (121,615 vs sales 113,543)",
        [F(REV, "121615000000", 1), F(RCFC, "113543000000", 1)],
        "same_filing",
    ),
]


@pytest.mark.parametrize(
    ("name", "facts", "scope"), DISAGREE, ids=[d[0][:12] for d in DISAGREE]
)
def test_disagreement_is_found_in_both_directions(name, facts, scope):
    d = g.find_disagreement(facts)
    assert d is not None, name
    assert d.scope == scope


def test_agreement_cases_are_not_hidden():
    assert g.find_disagreement([F(REV, "1000"), F(RCFC, "1000")]) is None
    assert g.find_disagreement([F(REV, "1000"), F(RCFC, "1009")]) is None  # inside 1%
    assert g.find_disagreement([F(RCFC, "500")]) is None  # one tag only
    # restated vintage: RCFC {19,629 original, 13,804 restated} agrees with Revenues 13,804
    assert (
        g.find_disagreement(
            [F(RCFC, "19629", 1), F(RCFC, "13804", 2), F(REV, "13804", 3)]
        )
        is None
    )


def test_just_over_one_percent_disagrees():
    assert g.find_disagreement([F(REV, "1000"), F(RCFC, "1011")]) is not None


def _decide(facts, canonical, sic="3600", proven=None):
    return g.decide_company(
        company_id=1,
        cik="0000000001",
        sic_code=sic,
        facts_by_period={10: facts},
        period_end={10: date(2022, 9, 30)},
        canonical=canonical,
        proven=proven,
    )


def test_both_displayed_directions_are_hidden_for_both_concepts():
    emr = DISAGREE[0][1]
    # displayed the bad Revenues value (what revenue_sanity_resolved showed) ...
    r = _decide(
        emr,
        {
            (10, "revenue_sanity_resolved"): D("1660000000"),
            (10, "revenue"): D("13804000000"),
        },
    )
    assert sorted(h[2] for h in r.hidden) == ["revenue", "revenue_sanity_resolved"]
    # ... and the correct RCFC value is hidden too (neither is proven): the stated honest cost
    assert all(p.after is None for p in r.planned)
    assert r.planned[0].reason.startswith("guard_hidden:revenue_total_undecidable")


def test_banks_are_excluded_but_insurers_are_not():
    facts = DISAGREE[2][1]
    canon = {(10, "revenue"): D("1")}
    assert _decide(facts, canon, sic="6021").hidden == []
    assert _decide(facts, canon, sic="6111").hidden == []
    assert len(_decide(facts, canon, sic="6311").hidden) == 1  # MET-type insurer


def test_proven_total_exempts_only_the_matching_value():
    facts = DISAGREE[1][1]
    canon = {
        (10, "revenue"): D("6925000000"),
        (10, "revenue_sanity_resolved"): D("6237000000"),
    }
    r = _decide(facts, canon, proven={(1, 10): D("6925000000")})
    assert [h[2] for h in r.hidden] == ["revenue_sanity_resolved"]
    assert r.stats["exempt_proven"] == 1


def test_period_without_a_canonical_row_changes_nothing():
    assert _decide(DISAGREE[0][1], {}).hidden == []


# ------------------------------------------------------------ database layer with a fake connection
class _Cur:
    def __init__(self, c):
        self.c = c
        self.res = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        self.c.sql.append((sql, params))
        if sql.startswith("select id, cik, sic_code from core.company"):
            self.res = [(1, "0000000001", "3600")]
        elif sql.startswith("select id, name from analytics.canonical_concept"):
            self.res = [(5, "revenue"), (6, "revenue_sanity_resolved")]
        elif "from core.fact f" in sql:
            self.res = [
                (
                    1,
                    10,
                    date(2021, 10, 1),
                    date(2022, 9, 30),
                    RCFC,
                    D("13804000000"),
                    1,
                ),
                (1, 10, date(2021, 10, 1), date(2022, 9, 30), REV, D("1660000000"), 3),
            ]
        elif "from analytics.canonical_fact cf" in sql:
            self.res = [
                (1, 10, "revenue_sanity_resolved", D("1660000000"), 6),
                (1, 10, "revenue", D("13804000000"), 5),
            ]
        else:
            self.res = []

    def fetchall(self):
        return self.res

    def fetchone(self):
        return self.res[0] if self.res else None


class _Conn:
    def __init__(self):
        self.sql = []

    def cursor(self):
        return _Cur(self)

    def commit(self):
        pass

    def writes(self):
        return [s for s, _ in self.sql if s.startswith(("delete", "insert", "update"))]


ON = {"SCROONER_RULES_ENABLED": g.RULE_ID}


def test_flag_off_is_a_noop():
    conn = _Conn()
    assert g.apply_revenue_total_guard(conn, environ={})["skipped"] == "rule_off"
    assert conn.sql == []


def test_dry_run_reads_but_writes_nothing_and_returns_before_image():
    conn = _Conn()
    out = g.apply_revenue_total_guard(conn, dry_run=True, environ={})
    assert conn.writes() == []
    assert out["cells_hidden"] == 2 and out["cross_filing"] == 2
    assert {p.data_point for p in out["planned"]} == {
        "revenue",
        "revenue_sanity_resolved",
    }


def test_live_requires_a_reason_store():
    with pytest.raises(RuntimeError):
        g.apply_revenue_total_guard(_Conn(), environ=ON)


def test_live_deletes_exact_scope_and_stores_reasons():
    conn, store = _Conn(), InMemoryBlankReasonStore()
    out = g.apply_revenue_total_guard(conn, environ=ON, reason_store=store, run_id="r1")
    ((delete_sql, params),) = [(s, p) for s, p in conn.sql if s.startswith("delete")]
    assert "company_id = %s" in delete_sql and "period_id = any(%s)" in delete_sql
    assert params == (1, [5, 6], [10])
    rows = store.all()
    assert len(rows) == 2 and {r.rule_id for r in rows} == {g.RULE_ID}
    assert {r.reason_code for r in rows} == {"revenue_total_undecidable"}
    assert rows[0].period_start == date(2021, 10, 1) and rows[0].period_end == date(
        2022, 9, 30
    )
    assert out["cells_hidden"] == 2
