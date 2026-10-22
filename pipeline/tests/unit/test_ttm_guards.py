"""RF-01 ttm.consecutive_window@1 and RF-02 ttm.age_guard@1 (W1/W2), synthetic
connections only; no database.

Fixtures marked REAL carry the dates and values read from analytics.metric_value
on 2026-10-22 (DATA-INFERRED): MasTec (company 225) EBITDA, COST quarter dates.
Values on COST/Apple dates are SYNTHETIC (the stored Q4 EBITDA is null)."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import expanded_metrics, rule_flags, ttm_guards
from scrooner_pipeline.mapper.reason_store import InMemoryReasonSink
from scrooner_pipeline.mapper.ttm_guards import QuarterRow

D = Decimal
TODAY = date(2026, 10, 22)

# REAL: MasTec ebitda quarters (Q3'25 and Q4'25 are null, `incomplete:add`).
MASTEC = [
    QuarterRow(D("349802000"), date(2026, 4, 1), date(2026, 6, 30), "Q2"),
    QuarterRow(D("263702000"), date(2026, 1, 1), date(2026, 3, 31), "Q1"),
    QuarterRow(D("260702000"), date(2025, 4, 1), date(2025, 6, 30), "Q2"),
    QuarterRow(D("145089000"), date(2025, 1, 1), date(2025, 3, 31), "Q1"),
]
# REAL dates (Costco 12/12/12/16 weeks), SYNTHETIC values: Q4'24 is 111 days.
COST = [
    QuarterRow(D("30"), date(2025, 2, 17), date(2025, 5, 11), "Q3"),
    QuarterRow(D("20"), date(2024, 11, 25), date(2025, 2, 16), "Q2"),
    QuarterRow(D("10"), date(2024, 9, 2), date(2024, 11, 24), "Q1"),
    QuarterRow(D("40"), date(2024, 5, 13), date(2024, 9, 1), "Q4"),
]
# Apple FY2023: 53-week year, Q1 is 14 weeks (ledger 2026-10-18); SYNTHETIC values.
APPLE_53 = [
    QuarterRow(D("4"), date(2023, 7, 2), date(2023, 9, 30), "Q4"),
    QuarterRow(D("3"), date(2023, 4, 2), date(2023, 7, 1), "Q3"),
    QuarterRow(D("2"), date(2023, 1, 1), date(2023, 4, 1), "Q2"),
    QuarterRow(D("1"), date(2022, 9, 25), date(2022, 12, 31), "Q1"),
]


# ------------------------------------------------------------------ window


def test_mastec_legacy_sum_reproduces_the_stored_wrong_value():
    assert ttm_guards.legacy_total(MASTEC) == D("1019295000")


def test_mastec_is_rejected_for_the_gap():
    d = ttm_guards.contiguous_ttm_window(MASTEC)
    assert not d.ok and d.total is None
    assert d.failure == ttm_guards.WINDOW_GAP
    assert "2026-01-01" in d.detail or "2025-06-30" in d.detail


def test_cost_12_12_12_16_calendar_is_accepted():
    d = ttm_guards.contiguous_ttm_window(COST)
    assert d.ok and d.total == D("100")


def test_53_week_year_is_accepted():
    d = ttm_guards.contiguous_ttm_window(APPLE_53)
    assert d.ok and d.total == D("10")
    assert (d.window[0].end - d.window[-1].start).days + 1 == 371


def test_calendar_year_quarters_are_accepted_in_any_input_order():
    rows = [
        QuarterRow(D("1"), date(2025, 10, 1), date(2025, 12, 31)),
        QuarterRow(D("2"), date(2026, 1, 1), date(2026, 3, 31)),
        QuarterRow(D("3"), date(2026, 4, 1), date(2026, 6, 30)),
        QuarterRow(D("4"), date(2025, 7, 1), date(2025, 9, 30)),
        QuarterRow(D("9"), date(2025, 4, 1), date(2025, 6, 30)),  # older, unused
    ]
    d = ttm_guards.contiguous_ttm_window(rows)
    assert d.ok and d.total == D("10")


def test_fewer_than_four_rows():
    d = ttm_guards.contiguous_ttm_window(MASTEC[:2])
    assert not d.ok and d.failure == ttm_guards.WINDOW_TOO_FEW
    assert ttm_guards.legacy_total(MASTEC[:2]) is None
    assert not ttm_guards.contiguous_ttm_window([]).ok


def test_year_to_date_row_labelled_as_quarter_is_rejected():
    rows = list(COST)
    rows[0] = QuarterRow(D("30"), date(2024, 9, 2), date(2025, 5, 11), "Q3")  # 9M YTD
    d = ttm_guards.contiguous_ttm_window(rows)
    assert not d.ok and d.failure == ttm_guards.WINDOW_DURATION


def test_overlapping_quarters_are_rejected():
    rows = list(COST)
    rows[1] = QuarterRow(D("20"), date(2024, 11, 25), date(2025, 3, 20), "Q2")
    d = ttm_guards.contiguous_ttm_window(rows)
    assert not d.ok and d.failure == ttm_guards.WINDOW_OVERLAP


def test_four_contiguous_rows_that_do_not_tile_one_year_are_rejected():
    start = date(2025, 1, 1)
    rows = []
    for i in range(4):  # four contiguous 120-day periods = 480 days
        rows.append(
            QuarterRow(
                D("1"),
                start + timedelta(days=120 * i),
                start + timedelta(days=120 * i + 119),
            )
        )
    d = ttm_guards.contiguous_ttm_window(rows)
    assert not d.ok and d.failure == ttm_guards.WINDOW_SPAN


def test_equal_duplicate_period_is_collapsed_conflicting_one_is_ambiguous():
    dup_equal = COST + [COST[0]]
    assert ttm_guards.contiguous_ttm_window(dup_equal).ok
    conflicting = COST + [QuarterRow(D("31"), COST[0].start, COST[0].end, "Q3")]
    d = ttm_guards.contiguous_ttm_window(conflicting)
    assert not d.ok and d.failure == ttm_guards.WINDOW_DUPLICATE


def test_adjacency_slack_boundary():
    def shifted(gap_days):
        rows = list(COST)
        # move Q2's end so the gap to Q3's start is gap_days (1 = adjacent)
        q3_start = rows[0].start
        rows[1] = QuarterRow(
            D("20"), rows[1].start, q3_start - timedelta(days=gap_days), "Q2"
        )
        return ttm_guards.contiguous_ttm_window(rows)

    assert shifted(1).ok
    assert shifted(1 + ttm_guards.ADJACENT_SLACK_DAYS).ok
    assert shifted(2 + ttm_guards.ADJACENT_SLACK_DAYS).failure == ttm_guards.WINDOW_GAP


# --------------------------------------------------------------------- age


def test_aal_buyback_from_fy2021_is_stale_against_current_quarter():
    d = ttm_guards.ttm_age_decision(date(2021, 12, 31), date(2026, 6, 30))
    assert d.stale and d.lag_days > 1500


def test_apd_buyback_from_fy2014_is_stale():
    assert ttm_guards.ttm_age_decision(date(2014, 9, 30), date(2026, 6, 30)).stale


def test_age_boundaries_two_quarters_behind_is_kept_three_is_stale():
    ref = date(2026, 6, 30)
    assert not ttm_guards.ttm_age_decision(ref - timedelta(days=182), ref).stale
    assert not ttm_guards.ttm_age_decision(
        ref - timedelta(days=ttm_guards.MAX_ANCHOR_LAG_DAYS), ref
    ).stale
    assert ttm_guards.ttm_age_decision(
        ref - timedelta(days=ttm_guards.MAX_ANCHOR_LAG_DAYS + 1), ref
    ).stale
    assert ttm_guards.ttm_age_decision(ref - timedelta(days=273), ref).stale


def test_age_guard_never_hides_without_an_anchor_or_reference():
    assert not ttm_guards.ttm_age_decision(None, date(2026, 6, 30)).stale
    assert not ttm_guards.ttm_age_decision(date(2020, 1, 1), None).stale


# ------------------------------------------------------------------- flags


def test_rules_default_off():
    assert (
        rule_flags.rule_mode(rule_flags.RF01_CONSECUTIVE_WINDOW, {}) == rule_flags.OFF
    )
    assert (
        rule_flags.rule_mode(rule_flags.RF02_AGE_GUARD, {rule_flags.ENV_ENABLED: ""})
        == rule_flags.OFF
    )


def test_flag_modes_and_whitespace():
    env = {
        rule_flags.ENV_ENABLED: " ttm.consecutive_window@1 ,, other.rule@2",
        rule_flags.ENV_DRYRUN: "ttm.age_guard@1",
    }
    assert (
        rule_flags.rule_mode(rule_flags.RF01_CONSECUTIVE_WINDOW, env) == rule_flags.ON
    )
    assert rule_flags.rule_mode(rule_flags.RF02_AGE_GUARD, env) == rule_flags.DRY_RUN
    assert rule_flags.rule_mode(rule_flags.RF10_BS_DATE_ANCHOR, env) == rule_flags.OFF


def test_malformed_or_ambiguous_flags_stop_the_run():
    with pytest.raises(ValueError):
        rule_flags.rule_mode(
            "a.b@1", {rule_flags.ENV_ENABLED: "ttm.consecutive_window"}
        )
    with pytest.raises(ValueError):
        rule_flags.rule_mode(
            "a.b@1",
            {rule_flags.ENV_ENABLED: "a.b@1", rule_flags.ENV_DRYRUN: "a.b@1"},
        )


# ------------------------------------------- wiring in expanded_metrics.py


class _FixedDate(date):
    @classmethod
    def today(cls):
        return TODAY


class ScriptedCursor:
    def __init__(self, conn):
        self.conn = conn
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def execute(self, sql, params=()):
        sql = " ".join(sql.split())
        self.conn.executed.append((sql, params))
        if "from analytics.canonical_fact cf" in sql:
            self._rows = self.conn.bounds_rows
        elif "mv.period_start" in sql:  # RF-01 dated query
            ordered = self.conn.ordered(params[1])[:12]
            self._rows = [(r.value, r.start, r.end, r.label) for r in ordered]
        elif "from analytics.metric_value mv" in sql:  # legacy query
            ordered = self.conn.ordered(params[1])[:4]
            self._rows = [(r.value, r.end) for r in ordered]
        else:
            self._rows = []

    def executemany(self, sql, rows):
        self.conn.rows.extend(dict(r) for r in rows)

    def fetchall(self):
        return list(self._rows)


class ScriptedConnection:
    def __init__(self, metric_rows, bounds_rows=()):
        self.metric_rows = metric_rows  # metric_definition_id -> list[QuarterRow]
        self.bounds_rows = list(bounds_rows)
        self.executed = []
        self.rows = []

    def ordered(self, metric_id):
        return sorted(self.metric_rows[metric_id], key=lambda r: r.end, reverse=True)

    def cursor(self):
        return ScriptedCursor(self)

    def commit(self):
        pass


def _conn(metric_rows, bounds_rows=()):
    return ScriptedConnection(metric_rows, bounds_rows)


EBITDA_ID, FCF_ID = 7, 8


@pytest.fixture(autouse=True)
def _fixed_today(monkeypatch):
    monkeypatch.setattr(expanded_metrics, "date", _FixedDate)
    rule_flags.DECISIONS.drain()
    sink = InMemoryReasonSink()
    monkeypatch.setattr(expanded_metrics, "REASON_SINK", sink)
    yield sink
    rule_flags.DECISIONS.drain()


def _env(monkeypatch, enabled="", dry=""):
    monkeypatch.setenv(rule_flags.ENV_ENABLED, enabled)
    monkeypatch.setenv(rule_flags.ENV_DRYRUN, dry)


def test_flag_off_keeps_mastec_legacy_value_and_records_nothing(monkeypatch):
    _env(monkeypatch)
    conn = _conn({EBITDA_ID: MASTEC})
    assert expanded_metrics._ebitda_ttm(conn, 225, EBITDA_ID) == D("1019295000")
    assert rule_flags.DECISIONS.decisions == []
    # exactly the legacy query ran, nothing else
    assert len(conn.executed) == 1


def test_dry_run_keeps_value_but_records_the_would_be_hide(monkeypatch):
    _env(monkeypatch, dry=rule_flags.RF01_CONSECUTIVE_WINDOW)
    conn = _conn({EBITDA_ID: MASTEC})
    assert expanded_metrics._ebitda_ttm(conn, 225, EBITDA_ID) == D("1019295000")
    [dec] = rule_flags.DECISIONS.decisions
    assert (dec.outcome, dec.mode, dec.reason_code) == (
        "hidden",
        rule_flags.DRY_RUN,
        ttm_guards.NON_CONTIGUOUS,
    )
    assert dec.old_value == D("1019295000") and dec.new_value is None
    assert dec.rule_id == "ttm.consecutive_window@1" and dec.company_id == 225
    assert (
        rule_flags.DECISIONS.reason_for(225, "ebitda") is None
    )  # dry run never changes the reason


def test_on_hides_mastec_and_stores_reasons(monkeypatch, _fixed_today):
    _env(monkeypatch, enabled=rule_flags.RF01_CONSECUTIVE_WINDOW)
    conn = _conn({EBITDA_ID: MASTEC})
    assert expanded_metrics._ebitda_ttm(conn, 225, EBITDA_ID) is None
    assert rule_flags.DECISIONS.reason_for(225, "ebitda") == ttm_guards.NON_CONTIGUOUS
    keys = {r.data_point_name for r in _fixed_today.rows}
    assert keys == set(expanded_metrics.WINDOW_CONSUMERS["ebitda"])
    row = _fixed_today.rows[0]
    assert (row.rule_id, row.state, row.defect_class, row.owner) == (
        "ttm.consecutive_window@1",
        "defect",
        "guard_hidden",
        "data_engineer_l2",
    )
    assert row.period_grain == "TTM" and row.basis == "latest"


def test_on_keeps_cost_and_apple_53_week_values(monkeypatch):
    _env(monkeypatch, enabled=rule_flags.RF01_CONSECUTIVE_WINDOW)

    # shift the dates forward (the shape is what matters) so the legacy
    # 150-day staleness check passes at the frozen TODAY
    def shifted(rows):
        delta = (TODAY - timedelta(days=30)) - rows[0].end
        return [
            QuarterRow(r.value, r.start + delta, r.end + delta, r.label) for r in rows
        ]

    cost, apple = shifted(COST), shifted(APPLE_53)
    assert expanded_metrics._ebitda_ttm(_conn({EBITDA_ID: cost}), 1, EBITDA_ID) == D(
        "100"
    )
    assert expanded_metrics._fcf_ttm(_conn({FCF_ID: apple}), 2, FCF_ID) == D("10")
    assert {d.outcome for d in rule_flags.DECISIONS.decisions} == {"kept"}


def test_fcf_uses_the_same_rule(monkeypatch):
    _env(monkeypatch, enabled=rule_flags.RF01_CONSECUTIVE_WINDOW)
    assert expanded_metrics._fcf_ttm(_conn({FCF_ID: MASTEC}), 5, FCF_ID) is None
    assert rule_flags.DECISIONS.reason_for(5, "fcf") == ttm_guards.NON_CONTIGUOUS


# full-company path ---------------------------------------------------------

OUTPUTS = (
    "net_debt_ebitda",
    "institutional_ownership_pct",
    "share_dilution_trend",
    "cash_conversion_cycle",
    "ev_ebitda",
    "ev_sales",
    "peg_ratio",
    "buyback_yield",
    "total_shareholder_yield",
    "ebitda_margin",
    "debt_to_ebitda",
    "fcf_per_share",
    "share_repurchases_pct_fcf",
    "dividends_pct_fcf",
    "ebitda",
)
DEPS = (
    "market_cap",
    "trailing_pe",
    "eps_growth_yoy",
    "dividend_yield",
    "debtor_days",
    "inventory_days",
    "payables_days",
    "fcf",
)
IDS = {n: i for i, n in enumerate(OUTPUTS + DEPS, 100)}
IDS["ebitda"], IDS["fcf"] = EBITDA_ID, FCF_ID
CONCEPTS = {
    "total_debt_resolved": 201,
    "cash_and_equivalents": 202,
    "revenue": 203,
    "share_buybacks": 204,
    "shares_outstanding": 205,
    "dividends_paid": 206,
}


def _qdict(value, years_end=(2026, "Q2")):
    fy, fp = years_end
    out = {}
    q = int(fp[1])
    for i in range(4):
        out[(fy, f"Q{q}")] = (D(value), [i + 1])
        q -= 1
        if q == 0:
            q, fy = 4, fy - 1
    return out


def _company_run(monkeypatch, conn, buyback_end=(2026, "Q2")):
    instant = {
        201: (D("40"), [1], None),
        202: (D("10"), [2], None),
        205: (D("100"), [3], None),
    }
    monkeypatch.setattr(
        expanded_metrics,
        "_latest_instant_fact",
        lambda _c, _co, concept: instant.get(concept),
    )
    monkeypatch.setattr(
        expanded_metrics,
        "_latest_metric_value",
        lambda _c, _co, metric: {IDS["market_cap"]: D("1000")}.get(metric),
    )
    monkeypatch.setattr(
        expanded_metrics, "_institutional_ownership_shares", lambda *_a: None
    )
    monkeypatch.setattr(
        expanded_metrics,
        "_shares_outstanding_now_and_1y_ago",
        lambda *_a: (D("100"), D("100")),
    )
    monkeypatch.setattr(expanded_metrics, "REVENUE_TTM_MATERIALITY_FLOOR", D("0"))
    facts = {203: _qdict("50"), 204: _qdict("5", buyback_end), 206: _qdict("2")}
    monkeypatch.setattr(
        expanded_metrics,
        "_load_quarterly_facts",
        lambda _c, _co, concept: facts[concept],
    )
    stats = expanded_metrics.calculate_expanded_metrics_for_company(
        conn, 225, IDS, CONCEPTS
    )
    return stats, {
        n: next(r for r in conn.rows if r["metric_definition_id"] == IDS[n])
        for n in OUTPUTS
    }


FRESH = [  # four contiguous calendar quarters ending 2026-06-30
    QuarterRow(D("5"), date(2026, 4, 1), date(2026, 6, 30), "Q2"),
    QuarterRow(D("5"), date(2026, 1, 1), date(2026, 3, 31), "Q1"),
    QuarterRow(D("5"), date(2025, 10, 1), date(2025, 12, 31), "Q4"),
    QuarterRow(D("5"), date(2025, 7, 1), date(2025, 9, 30), "Q3"),
]


def _bounds(buyback_end_date):
    rows = []
    for concept, end_q in (
        (203, date(2026, 6, 30)),
        (204, buyback_end_date),
        (206, date(2026, 6, 30)),
    ):
        rows.append((concept, 2026, "Q2", end_q - timedelta(days=89), end_q))
    return rows


def test_company_flags_off_matches_legacy_wording(monkeypatch):
    _env(monkeypatch)
    conn = _conn({EBITDA_ID: MASTEC, FCF_ID: FRESH})
    _stats, rows = _company_run(monkeypatch, conn)
    assert rows["ebitda"]["value"] == D(
        "1019295000"
    )  # the W1 defect, still there when OFF
    assert rows["buyback_yield"]["value"] == D("0.02")


def test_company_w1_on_propagates_the_guard_reason_to_every_dependent(monkeypatch):
    _env(monkeypatch, enabled=rule_flags.RF01_CONSECUTIVE_WINDOW)
    conn = _conn({EBITDA_ID: MASTEC, FCF_ID: FRESH})
    _stats, rows = _company_run(monkeypatch, conn)
    why = "guard:non_contiguous_ttm_window:ebitda"
    for name in (
        "ebitda",
        "net_debt_ebitda",
        "ebitda_margin",
        "debt_to_ebitda",
        "ev_ebitda",
    ):
        assert rows[name]["value"] is None and rows[name]["is_null_reason"] == why, name
    # FCF side is contiguous: untouched
    assert rows["fcf_per_share"]["value"] == D("0.2")


def test_company_w2_on_hides_stale_buyback_consumers_and_tsy(monkeypatch):
    _env(monkeypatch, enabled=rule_flags.RF02_AGE_GUARD)
    conn = _conn({EBITDA_ID: FRESH, FCF_ID: FRESH}, _bounds(date(2021, 12, 31)))
    _stats, rows = _company_run(monkeypatch, conn)
    why = "guard:stale_ttm_input:share_buybacks"
    for name in (
        "buyback_yield",
        "share_repurchases_pct_fcf",
        "total_shareholder_yield",
    ):
        assert rows[name]["value"] is None and rows[name]["is_null_reason"] == why, name
    # the dividend side and everything else is unchanged
    assert rows["dividends_pct_fcf"]["value"] == D("0.4")  # 8 / 20


def test_company_w2_dry_run_changes_nothing_but_records(monkeypatch):
    _env(monkeypatch, dry=rule_flags.RF02_AGE_GUARD)
    conn = _conn({EBITDA_ID: FRESH, FCF_ID: FRESH}, _bounds(date(2021, 12, 31)))
    _stats, rows = _company_run(monkeypatch, conn)
    assert rows["buyback_yield"]["value"] == D("0.02")
    hidden = [d for d in rule_flags.DECISIONS.decisions if d.outcome == "hidden"]
    assert [d.data_point for d in hidden] == ["share_buybacks"]
    assert hidden[0].consumers == expanded_metrics.AGE_CONSUMERS["share_buybacks"]


def test_company_w2_on_keeps_a_current_buyback(monkeypatch):
    _env(monkeypatch, enabled=rule_flags.RF02_AGE_GUARD)
    conn = _conn({EBITDA_ID: FRESH, FCF_ID: FRESH}, _bounds(date(2026, 6, 30)))
    _stats, rows = _company_run(monkeypatch, conn)
    assert rows["buyback_yield"]["value"] == D("0.02")
    assert rows["total_shareholder_yield"]["value"] is not None
