"""Pure parts of the RF-01/RF-02 dry-run (no database). Fixtures: REAL MasTec and
AAL values read from the stored tables on 2026-10-22 (DATA-INFERRED)."""

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper import ttm_guards, ttm_guards_dryrun as dr
from scrooner_pipeline.mapper.ttm_guards import QuarterRow

D = Decimal
TODAY = date(2026, 10, 22)
MASTEC = [
    QuarterRow(D("349802000"), date(2026, 4, 1), date(2026, 6, 30), "Q2"),
    QuarterRow(D("263702000"), date(2026, 1, 1), date(2026, 3, 31), "Q1"),
    QuarterRow(D("260702000"), date(2025, 4, 1), date(2025, 6, 30), "Q2"),
    QuarterRow(D("145089000"), date(2025, 1, 1), date(2025, 3, 31), "Q1"),
]
CLEAN = [
    QuarterRow(D("1"), date(2026, 4, 1), date(2026, 6, 30), "Q2"),
    QuarterRow(D("1"), date(2026, 1, 1), date(2026, 3, 31), "Q1"),
    QuarterRow(D("1"), date(2025, 10, 1), date(2025, 12, 31), "Q4"),
    QuarterRow(D("1"), date(2025, 7, 1), date(2025, 9, 30), "Q3"),
]


def test_window_finding_for_mastec():
    f = dr.evaluate_window(225, "ebitda", MASTEC, TODAY)
    assert f is not None
    assert (f.rule_id, f.outcome, f.failure_class) == (
        "ttm.consecutive_window@1",
        "hidden",
        "gap_between_quarters",
    )
    assert f.old_ttm == D("1019295000") and f.new_ttm is None


def test_window_no_finding_for_clean_or_already_stale_or_short():
    assert dr.evaluate_window(1, "ebitda", CLEAN, TODAY) is None
    assert (
        dr.evaluate_window(1, "ebitda", MASTEC, date(2027, 6, 1)) is None
    )  # legacy 150-day guard blanks it already
    assert dr.evaluate_window(1, "ebitda", CLEAN[:3], TODAY) is None


def _by_key(last_fy, last_q, n_quarters, value, last_end):
    out, fy, q, end = {}, last_fy, last_q, last_end
    for _ in range(n_quarters):
        out[(fy, f"Q{q}")] = (D(value), end, end)
        q -= 1
        if q == 0:
            q, fy = 4, fy - 1
    return out


EXPECTED = date(2026, 6, 30)


def test_age_finding_aal_style_and_current_company():
    stale = _by_key(2021, 4, 4, "5", date(2021, 12, 31))
    f, comp = dr.evaluate_age(123, "share_buybacks", stale, EXPECTED)
    assert f is not None and comp.lag_days == 1642 and f.new_ttm is None
    assert (
        f.rule_id == "ttm.age_guard@2"
        and f.failure_class == "anchor_not_at_expected_period"
    )
    current = _by_key(2026, 2, 4, "5", EXPECTED)
    f2, comp2 = dr.evaluate_age(123, "share_buybacks", current, EXPECTED)
    assert f2 is None and comp2.status == "current" and comp2.lag_days == 0


def test_age_missing_reference_is_hidden_and_absent_is_not_a_finding():
    current = _by_key(2026, 2, 4, "5", EXPECTED)
    f, comp = dr.evaluate_age(1, "share_buybacks", current, None)
    assert f is not None and f.failure_class == "no_expected_period"
    f2, comp2 = dr.evaluate_age(1, "share_buybacks", None, EXPECTED)
    assert f2 is None and comp2.status == "absent"


def test_age_label_ttm_needs_four_consecutive_labels():
    gap = _by_key(2026, 2, 4, "5", EXPECTED)
    del gap[(2025, "Q4")]
    f, comp = dr.evaluate_age(1, "dividends_paid", gap, EXPECTED)
    assert (
        f is None and comp.status == "absent"
    )  # no label-consecutive TTM exists at all


def test_composite_is_counted_per_rule():
    cur = _by_key(2026, 2, 4, "5", EXPECTED)
    stale = _by_key(2021, 4, 4, "5", date(2021, 12, 31))
    _f1, b = dr.evaluate_age(1, "share_buybacks", stale, EXPECTED)
    _f2, d = dr.evaluate_age(1, "dividends_paid", None, EXPECTED)
    found = {f.rule_id: f for f in dr.evaluate_composite(1, [b, d])}
    assert set(found) == {"tsy.stale_component@1", "tsy.unevidenced_zero@1"}
    assert found["tsy.stale_component@1"].detail == "stale_ttm_input:share_buybacks"
    assert found["tsy.unevidenced_zero@1"].detail == "unevidenced_zero:dividends_paid"
    _g, c1 = dr.evaluate_age(1, "share_buybacks", cur, EXPECTED)
    _h, c2 = dr.evaluate_age(1, "dividends_paid", cur, EXPECTED)
    assert dr.evaluate_composite(1, [c1, c2]) == []
    only_absent = dr.evaluate_composite(1, [c1, d])
    assert [f.rule_id for f in only_absent] == ["tsy.unevidenced_zero@1"]


def test_summary_counts_the_two_tsy_rules_separately():
    cur = _by_key(2026, 2, 4, "5", EXPECTED)
    stale = _by_key(2021, 4, 4, "5", date(2021, 12, 31))
    _a, b = dr.evaluate_age(1, "share_buybacks", stale, EXPECTED)
    _c, d = dr.evaluate_age(1, "dividends_paid", None, EXPECTED)
    findings = dr.evaluate_composite(1, [b, d])
    displayed = {dr._dkey(f): ["total_shareholder_yield"] for f in findings}
    s = dr.summarize(findings, displayed, dr.Counter())["rules"]
    assert (
        s["tsy.stale_component@1"]["total_shareholder_yield"]["displayed_cells_now"]
        == 1
    )
    assert s["tsy.unevidenced_zero@1"]["total_shareholder_yield"][
        "by_failure_class"
    ] == {"unevidenced_zero": 1}


def test_lag_histogram_is_against_the_expected_period():
    def bucket(anchor_end, expected=EXPECTED):
        return dr.lag_bucket(
            ttm_guards.component("share_buybacks", D("1"), anchor_end, expected)
        )

    assert bucket(EXPECTED) == "at_expected(<=7d)"
    assert bucket(date(2026, 3, 31)) == "behind<=1q"
    assert bucket(date(2025, 12, 31)) == "behind<=2q"
    assert bucket(date(2025, 9, 30)) == "behind<=3q"
    assert bucket(date(2025, 6, 30)) == "behind<=1y"
    assert bucket(date(2021, 12, 31)) == "behind>1y"
    assert bucket(date(2026, 9, 30)) == "ahead_of_expected"
    assert bucket(EXPECTED, None) == "no_expected_period"
    assert (
        dr.lag_bucket(ttm_guards.component("share_buybacks", None, None, EXPECTED))
        == "absent"
    )


def test_summary_counts():
    f = dr.evaluate_window(225, "ebitda", MASTEC, TODAY)
    s = dr.summarize([f], {(225, "ebitda"): ["ebitda", "ev_ebitda"]}, dr.Counter())
    assert s["rules"]["ttm.consecutive_window@1"]["ebitda"]["displayed_cells_now"] == 2
