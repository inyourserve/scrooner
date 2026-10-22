"""RF-10 balance-sheet-date anchor (W10). AAPL values/dates are REAL
(analytics.canonical_fact / metric_value read 2026-10-22, DATA-INFERRED; the
7.36 acceptance is 10-Q 0000320193-26-000020)."""

from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import bs_anchor, calculate, rule_flags
from scrooner_pipeline.mapper.bs_anchor import latest_effect
from test_mapper_stage_boundaries import MetricConnection

D = Decimal
BS, COVER = date(2026, 6, 27), date(2026, 7, 17)

EQUITY, SHARES, CASH, DEBT = 1, 2, 3, 4
BVPS_INPUTS = [
    ("stockholders_equity", EQUITY, "numerator", True),
    ("shares_outstanding", SHARES, "denominator", True),
]
NCPS_INPUTS = [
    ("cash_and_equivalents", CASH, "add", True),
    ("total_debt_resolved", DEBT, "subtract", True),
    ("shares_outstanding", SHARES, "denominator", True),
]


def aapl_facts():
    """equity/cash/debt at the balance-sheet date; shares at BOTH dates."""
    return {
        "by_period_id": {
            EQUITY: {10: (D("107520000000"), [90351])},
            CASH: {10: (D("39544000000"), [70449])},
            DEBT: {10: (D("84297000000"), [79829, 70848])},
            SHARES: {10: (D("14608963000"), [71681]), 11: (D("14594180000"), [68114])},
        },
        "by_end_date": {
            EQUITY: {BS: (D("107520000000"), [90351])},
            CASH: {BS: (D("39544000000"), [70449])},
            DEBT: {BS: (D("84297000000"), [79829, 70848])},
            SHARES: {
                BS: (D("14608963000"), [71681]),
                COVER: (D("14594180000"), [68114]),
            },
        },
        "periods": {10: (BS, BS, "Q3"), 11: (COVER, COVER, "Q3")},
    }


def run(monkeypatch, enabled="", dry=""):
    monkeypatch.setenv(rule_flags.ENV_ENABLED, enabled)
    monkeypatch.setenv(rule_flags.ENV_DRYRUN, dry)
    monkeypatch.setattr(
        calculate, "_load_canonical_facts", lambda _c, _co: aapl_facts()
    )
    targets = [
        {"id": 31, "name": "book_value_per_share", "inputs": BVPS_INPUTS},
        {"id": 32, "name": "net_cash_per_share", "inputs": NCPS_INPUTS},
    ]
    conn = MetricConnection()
    calculate.calculate_for_company(conn, 7, targets)
    return conn


def by(conn, metric_id):
    return {
        r["period_end"]: r for r in conn.rows if r["metric_definition_id"] == metric_id
    }


@pytest.fixture(autouse=True)
def _clean():
    rule_flags.DECISIONS.drain()
    yield
    rule_flags.DECISIONS.drain()


@pytest.mark.unit
def test_flag_off_reproduces_the_defect_newest_row_is_blank(monkeypatch):
    conn = run(monkeypatch)
    bv = by(conn, 31)
    assert bv[BS]["value"] == D("107520000000") / D("14608963000")
    assert (
        bv[COVER]["value"] is None
        and bv[COVER]["is_null_reason"] == "incomplete:numerator"
    )
    assert by(conn, 32)[COVER]["is_null_reason"] == "incomplete:add"
    assert rule_flags.DECISIONS.decisions == []


@pytest.mark.unit
def test_on_anchors_on_the_balance_sheet_date_only(monkeypatch):
    conn = run(monkeypatch, enabled=rule_flags.RF10_BS_DATE_ANCHOR)
    bv, nc = by(conn, 31), by(conn, 32)
    assert set(bv) == {BS} and set(nc) == {BS}
    assert round(bv[BS]["value"], 2) == D(
        "7.36"
    )  # acceptance: AAPL 10-Q 0000320193-26-000020
    assert nc[BS]["value"] == (D("39544000000") - D("84297000000")) / D("14608963000")
    # share count is the one dated on the balance-sheet date, not the cover date
    assert 71681 in bv[BS]["source_fact_ids"] and 68114 not in bv[BS]["source_fact_ids"]


@pytest.mark.unit
def test_on_does_not_pair_a_cover_dated_count_when_the_bs_date_count_is_missing(
    monkeypatch,
):
    facts = aapl_facts()
    del facts["by_end_date"][SHARES][BS]  # company files only the cover count
    del facts["by_period_id"][SHARES][10]
    monkeypatch.setenv(rule_flags.ENV_ENABLED, rule_flags.RF10_BS_DATE_ANCHOR)
    monkeypatch.setattr(calculate, "_load_canonical_facts", lambda _c, _co: facts)
    conn = MetricConnection()
    calculate.calculate_for_company(
        conn, 7, [{"id": 31, "name": "book_value_per_share", "inputs": BVPS_INPUTS}]
    )
    [row] = conn.rows
    assert row["period_end"] == BS and row["value"] is None
    assert (
        row["is_null_reason"] == "incomplete:denominator"
    )  # visibly unavailable, with a reason


@pytest.mark.unit
def test_dry_run_keeps_legacy_rows_and_records_the_fix(monkeypatch):
    conn = run(monkeypatch, dry=rule_flags.RF10_BS_DATE_ANCHOR)
    assert set(by(conn, 31)) == {BS, COVER}
    got = {d.data_point: d for d in rule_flags.DECISIONS.decisions}
    d = got["book_value_per_share"]
    assert (d.outcome, d.old_value, d.period_end) == ("changed", None, COVER)
    assert (
        round(d.new_value, 2) == D("7.36")
        and d.rule_id == "pershare.balance_sheet_date_anchor@1"
    )


@pytest.mark.unit
def test_other_instant_metrics_keep_their_anchors_when_on(monkeypatch):
    inputs = [
        ("stockholders_equity", EQUITY, "denominator", True),
        ("cash_and_equivalents", CASH, "numerator", True),
    ]
    assert bs_anchor.anchor_inputs("debt_to_equity", [], inputs) == inputs
    assert bs_anchor.anchor_inputs("book_value_per_share", [], BVPS_INPUTS) == [
        BVPS_INPUTS[0]
    ]
    dur = [("net_income", 9, "numerator", False)]
    assert bs_anchor.anchor_inputs("book_value_per_share", dur, BVPS_INPUTS) == dur


@pytest.mark.unit
def test_latest_effect_counts_a_fixed_cell():
    rows = [
        (COVER, None, "incomplete:numerator"),
        (BS, D("7.36"), None),
        (date(2026, 3, 28), D("7.26"), None),
    ]
    e = latest_effect(rows, {BS, date(2026, 3, 28)})
    assert e.fixes_latest_cell and e.end_after == BS and e.changes_latest_row
    healthy = latest_effect([(BS, D("7.36"), None)], {BS})
    assert not healthy.changes_latest_row and not healthy.fixes_latest_cell
    still_null = latest_effect(
        [(COVER, None, "x"), (BS, None, "incomplete:denominator")], {BS}
    )
    assert not still_null.fixes_latest_cell and still_null.changes_latest_row
    assert latest_effect([], {BS}).end_now is None
