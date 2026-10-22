"""Pure parts of the RF-01/RF-02 dry-run (no database). Fixtures: REAL MasTec and
AAL values read from the stored tables on 2026-10-22 (DATA-INFERRED)."""

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper import ttm_guards_dryrun as dr
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


def test_age_finding_aal_style_and_current_company():
    stale = _by_key(2021, 4, 4, "5", date(2021, 12, 31))
    f, lag = dr.evaluate_age(123, "share_buybacks", stale, date(2026, 6, 30))
    assert (
        f is not None
        and lag == 1642
        and f.new_ttm is None
        and f.rule_id == "ttm.age_guard@1"
    )
    current = _by_key(2026, 2, 4, "5", date(2026, 6, 30))
    f2, lag2 = dr.evaluate_age(123, "share_buybacks", current, date(2026, 6, 30))
    assert f2 is None and lag2 == 0


def test_age_label_ttm_needs_four_consecutive_labels():
    gap = _by_key(2026, 2, 4, "5", date(2026, 6, 30))
    del gap[(2025, "Q4")]
    assert dr.evaluate_age(1, "dividends_paid", gap, date(2026, 6, 30)) == (None, None)


def test_lag_buckets_and_summary_counts():
    assert dr.lag_bucket(None) == "no_reference"
    assert dr.lag_bucket(0) == "current"
    assert dr.lag_bucket(182) == "<=2q"
    assert dr.lag_bucket(200) == "2q..threshold"
    assert dr.lag_bucket(201) == "threshold..3q"
    f = dr.evaluate_window(225, "ebitda", MASTEC, TODAY)
    s = dr.summarize([f], {(225, "ebitda"): ["ebitda", "ev_ebitda"]}, dr.Counter())
    assert s["rules"]["ttm.consecutive_window@1"]["ebitda"]["displayed_cells_now"] == 2
