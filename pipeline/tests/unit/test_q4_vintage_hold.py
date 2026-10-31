"""Same-vintage Q4 hold (interim period.same_vintage_derivation@1) in derive_q4."""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.normalizer import derived, q4_vintage_hold as vh
from scrooner_pipeline.normalizer.q4_vintage_dryrun import (
    BLOCKED_MIXED,
    BLOCKED_NO_YTD,
    BLOCKED_SIGN,
    CLEAN,
    Q4Candidate,
)


class _Cursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def executemany(self, sql, rows):
        self.conn.batches.append((" ".join(sql.split()), [dict(r) for r in rows]))

    def execute(self, sql, params=None):
        self.conn.statements.append((" ".join(sql.split()), params))


class _Conn:
    def __init__(self):
        self.batches, self.statements, self.commits = [], [], 0

    def cursor(self):
        return _Cursor(self)

    def commit(self):
        self.commits += 1

    def inserted_facts(self):
        return [
            r
            for sql, rows in self.batches
            if "insert into core.fact" in sql
            for r in rows
        ]

    def retired(self):
        return [
            r
            for sql, rows in self.batches
            if "set is_authoritative = false" in sql
            for r in rows
        ]


FY_START, Q3_END, FY_END = date(2025, 1, 1), date(2025, 9, 30), date(2025, 12, 31)
Q4_KEY = (date(2025, 10, 1), FY_END)


def _rows():
    return [
        (1, 10, 1, Decimal("13229"), 1001, 2001, 2025, "FY", FY_START, FY_END),
        (
            2,
            10,
            1,
            Decimal("3300"),
            1002,
            2002,
            2025,
            "Q1",
            FY_START,
            date(2025, 3, 31),
        ),
        (
            3,
            10,
            1,
            Decimal("3200"),
            1003,
            2003,
            2025,
            "Q2",
            date(2025, 4, 1),
            date(2025, 6, 30),
        ),
        (4, 10, 1, Decimal("3317"), 1004, 2004, 2025, "Q3", date(2025, 7, 1), Q3_END),
    ]


def _cand(category, block_reason="latest FY pairs only with a mixed-vintage 9M"):
    return Q4Candidate(
        company_id=1,
        concept_id=10,
        unit="usd",
        category=category,
        block_reason=block_reason,
        fiscal_year_start=FY_START,
        fiscal_year_end=FY_END,
        fy_fact_ids=[1],
        ytd_fact_ids=[2, 3, 4],
        fy_accessions=["0000001413329-26-000012"],
        ytd_accessions=["0000001413329-25-000040"],
        fy_value=Decimal("13229"),
        ytd_value=Decimal("9817"),
    )


@pytest.fixture
def harness(monkeypatch):
    monkeypatch.setattr(derived, "_load_quarterly_candidates", lambda _c, _i: _rows())
    monkeypatch.setattr(derived, "_load_existing_periods", lambda _c, _i: {Q4_KEY: 404})
    monkeypatch.setattr(derived, "_load_reported_duration_keys", lambda _c, _i: set())
    monkeypatch.setattr(
        derived, "_load_authoritative_reported_quarters", lambda _c, _i: {}
    )
    monkeypatch.setattr(derived, "_load_nine_month_ytd", lambda _c, _i: {})
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda _c: set())
    monkeypatch.setattr(derived, "_load_non_additive", lambda _c: (set(), set()))
    monkeypatch.setattr(derived, "_load_unit_names", lambda _c: {1: "usd"})
    monkeypatch.delenv(rf.ENV_ENABLED, raising=False)
    monkeypatch.delenv(rf.ENV_DRYRUN, raising=False)
    return monkeypatch


def _set_verdict(monkeypatch, cand):
    calls = []

    def fake(_conn, company_id, concept_ids, *, tol=None):
        calls.append((company_id, set(concept_ids)))
        return {(10, "usd", FY_START): cand} if cand else {}

    monkeypatch.setattr(vh, "load_vintage_categories", fake)
    return calls


@pytest.mark.unit
def test_flag_off_never_consults_the_evaluator_and_derives(harness):
    calls = _set_verdict(harness, _cand(BLOCKED_MIXED))
    conn = _Conn()
    stats = derived.derive_q4_for_company(conn, 1)
    assert calls == []
    assert stats["derived"] == 1 and stats["held_mixed_vintage"] == 0
    assert conn.inserted_facts()[0]["value"] == Decimal("3412")


@pytest.mark.unit
def test_dry_run_counts_the_hold_but_still_derives(harness):
    harness.setenv(rf.ENV_DRYRUN, vh.RULE_ID)
    calls = _set_verdict(harness, _cand(BLOCKED_MIXED))
    conn = _Conn()
    holds = []
    stats = derived.derive_q4_for_company(conn, 1, holds_out=holds)
    assert calls == [(1, {10})]
    assert stats["derived"] == 1 and stats["held_mixed_vintage"] == 1
    assert len(holds) == 1 and holds[0].category == BLOCKED_MIXED
    assert holds[0].q4_start, holds[0].q4_end == Q4_KEY
    assert conn.inserted_facts()  # dry run: the value is still written


@pytest.mark.unit
@pytest.mark.parametrize(
    "category,stat",
    [(BLOCKED_MIXED, "held_mixed_vintage"), (BLOCKED_SIGN, "held_sign_conflict")],
)
def test_on_holds_the_cell_and_retires_an_earlier_derived_q4(harness, category, stat):
    harness.setenv(rf.ENV_ENABLED, vh.RULE_ID)
    _set_verdict(harness, _cand(category))
    conn = _Conn()
    holds = []
    stats = derived.derive_q4_for_company(conn, 1, holds_out=holds)
    assert stats["derived"] == 0 and stats[stat] == 1
    assert conn.inserted_facts() == []
    assert conn.retired() == [
        {"company_id": 1, "concept_id": 10, "unit_id": 1, "period_id": 404}
    ]
    assert holds[0].reason_code in ("q4_inputs_mixed_vintage", "q4_input_sign_conflict")


@pytest.mark.unit
@pytest.mark.parametrize("category", [CLEAN, BLOCKED_NO_YTD, None])
def test_on_derives_when_the_evaluator_does_not_see_a_vintage_problem(
    harness, category
):
    harness.setenv(rf.ENV_ENABLED, vh.RULE_ID)
    _set_verdict(harness, _cand(category) if category else None)
    conn = _Conn()
    stats = derived.derive_q4_for_company(conn, 1)
    assert stats["derived"] == 1 and stats["held_mixed_vintage"] == 0
    assert conn.retired() == []


@pytest.mark.unit
def test_hold_category_only_for_the_two_vintage_categories():
    assert vh.hold_category(None) is None
    assert vh.hold_category(_cand(CLEAN)) is None
    assert vh.hold_category(_cand(BLOCKED_NO_YTD)) is None
    assert vh.hold_category(_cand(BLOCKED_MIXED)) == BLOCKED_MIXED
    assert vh.hold_category(_cand(BLOCKED_SIGN)) == BLOCKED_SIGN


@pytest.mark.unit
def test_dependents_follow_the_statement_fallbacks():
    deps = vh.dependent_data_points("cost_of_revenue")
    assert "cost_of_revenue_resolved" in deps
    assert "gross_profit_resolved" in deps  # revenue - cost_of_revenue_resolved
    assert "operating_expenses_resolved" in vh.dependent_data_points("gross_profit")
    assert vh.dependent_data_points("net_income") == ["net_income_resolved"]


@pytest.mark.unit
def test_blank_reasons_cover_the_concept_and_its_dependents():
    hold = vh.make_hold(_cand(BLOCKED_MIXED), 1, *Q4_KEY)
    reasons = vh.blank_reasons(7, hold, ["cost_of_revenue"])
    points = {r.key.data_point_name for r in reasons}
    assert {
        "cost_of_revenue",
        "cost_of_revenue_resolved",
        "gross_profit_resolved",
    } <= points
    r = next(r for r in reasons if r.key.data_point_name == "cost_of_revenue")
    assert (
        r.key.company_id,
        r.key.period_grain,
        r.key.period_start,
        r.key.period_end,
    ) == (7, "Q", *Q4_KEY)
    assert (
        r.state == "defect"
        and r.defect_class == "period"
        and r.owner == "period_engineer"
    )
    assert r.rule_id == vh.RULE_ID and r.reason_code == "q4_inputs_mixed_vintage"
    assert set(r.source_fact_ids) == {1, 2, 3, 4}
    assert "13229" in r.reason_text and "0000001413329-26-000012" in r.reason_text


@pytest.mark.unit
def test_presentation_scale_is_the_median_trailing_zero_exponent_capped_at_millions():
    D = Decimal
    assert (
        vh.presentation_scale(
            [D("630587000"), D("631000000"), D("2599000000"), D("500000000")]
        )
        == 6
    )
    assert (
        vh.presentation_scale([D("630587000"), D("1899874000"), D("2599477000")]) == 3
    )
    assert vh.presentation_scale([D("12345"), D("678")]) == 0
    assert vh.presentation_scale([D("0"), D("1000000000000")]) == 6  # capped
    assert vh.presentation_scale([]) == 0


@pytest.mark.unit
def test_rounding_slack_separates_pm_recast_from_nvda_rounding():
    tol = vh.Tolerance(
        rel=vh.HOLD_TOLERANCE.rel, abs_tol=vh.ROUNDING_UNITS_SLACK * Decimal(10) ** 6
    )
    assert not tol.agree(
        Decimal("3412000000"), Decimal("3429000000")
    )  # PM recast, 17M apart
    assert tol.agree(
        Decimal("327000000"), Decimal("326000000")
    )  # sum of rounded quarters
    assert tol.agree(
        Decimal("630587000"), Decimal("631000000")
    )  # thousands -> millions
    assert not tol.agree(
        Decimal("500000000"), Decimal("480000000")
    )  # 20M on a round number
