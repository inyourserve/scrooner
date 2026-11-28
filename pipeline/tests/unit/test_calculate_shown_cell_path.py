"""calculate.py behind serve.shown_cell_path@1 (one-display-path plan step 5, M3). The shown loader is faked as the view
analytics.shown_cell would return it (draft 0135 is not applied): the unproven cell is simply absent."""

from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import calculate, rule_flags, shown_inputs
from test_bs_anchor import BS, CASH, DEBT, NCPS_INPUTS, SHARES, aapl_facts
from test_mapper_stage_boundaries import MetricConnection

D = Decimal
RULE = "serve.shown_cell_path@1"
TARGET = [{"id": 32, "name": "net_cash_per_share", "inputs": NCPS_INPUTS}]


def _without_debt():
    f = aapl_facts()
    f["by_period_id"].pop(DEBT)
    f["by_end_date"].pop(DEBT)
    return f


def _run(monkeypatch, on, shown):
    if on:
        monkeypatch.setenv(rule_flags.ENV_ENABLED, RULE)
    else:
        monkeypatch.delenv(rule_flags.ENV_ENABLED, raising=False)
    monkeypatch.delenv(rule_flags.ENV_DRYRUN, raising=False)
    monkeypatch.setattr(
        calculate, "_load_canonical_facts", lambda _c, _co: aapl_facts()
    )
    monkeypatch.setattr(shown_inputs, "load_shown_cells", lambda _c, _co: shown)
    conn = MetricConnection()
    calculate.calculate_for_company(conn, 7, TARGET)
    return {r["period_end"]: r for r in conn.rows}


@pytest.mark.unit
def test_flag_is_registered_and_default_off():
    assert RULE in rule_flags.RULES
    assert rule_flags.rule_mode(RULE, {}) == rule_flags.OFF


@pytest.mark.unit
def test_flag_off_ignores_the_shown_loader(monkeypatch):
    # the shown view lacks debt, but flag off reads canonical_fact exactly as today
    rows = _run(monkeypatch, False, _without_debt())
    assert rows[BS]["value"] == (D("39544000000") - D("84297000000")) / D("14608963000")
    assert rows[BS]["is_null_reason"] is None


@pytest.mark.unit
def test_flag_on_all_inputs_shown_gives_the_same_value(monkeypatch):
    rows = _run(monkeypatch, True, aapl_facts())
    assert rows[BS]["value"] == (D("39544000000") - D("84297000000")) / D("14608963000")


@pytest.mark.unit
def test_flag_on_unproven_input_is_excluded_with_a_reason(monkeypatch):
    rows = _run(monkeypatch, True, _without_debt())
    assert rows[BS]["value"] is None
    assert rows[BS]["is_null_reason"] == "input_not_served:total_debt_resolved"
    assert (
        rows[BS]["source_fact_ids"] is None or 79829 not in rows[BS]["source_fact_ids"]
    )


@pytest.mark.unit
def test_flag_on_reads_through_the_loader_not_canonical_fact(monkeypatch):
    monkeypatch.setenv(rule_flags.ENV_ENABLED, RULE)

    def boom(*_a):
        raise AssertionError("canonical_fact read with the flag on")

    monkeypatch.setattr(calculate, "_load_canonical_facts", boom)
    monkeypatch.setattr(shown_inputs, "load_shown_cells", lambda _c, _co: aapl_facts())
    calculate.calculate_for_company(MetricConnection(), 7, TARGET)
