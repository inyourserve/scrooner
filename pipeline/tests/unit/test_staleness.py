"""Staleness guard (common/staleness.py): an annual value more than 1 fiscal
year, or a quarterly/TTM value more than 2 quarters, behind the company's OWN
latest filed period is hidden with a stated reason. Stored values are never
changed and a current value is never touched.

Fixtures are the real stale cells the verifier shards found FILING-CHECKED
(doc/data-moat/team/top1000/status.md, data-team/33 family E). The dates are
representative: each company's fiscal-year end and a plausible latest filed
period (June-Aug 2026), with the stale value's year as reported in the notes.
"""

from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.common import staleness
from scrooner_pipeline.common.staleness import (
    ANNUAL_MAX_GAP_DAYS,
    QUARTERLY_MAX_GAP_DAYS,
    apply_to_metric_rows,
    apply_to_resolved,
    load_latest_filed_periods,
    stale_predicate_sql,
    staleness_reason,
)
from scrooner_pipeline.screener import query as screener_query
from scrooner_pipeline.screener.resolve import (
    _suppress_stale,
    resolve_most_recent_values,
)

D = date.fromisoformat


class FakeCursor:
    def __init__(self, answers):
        self.answers = answers
        self.executed: list[tuple[str, object]] = []
        self._rows: list[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        text = str(sql)
        self.executed.append((text, params))
        self._rows = []
        for needle, rows in self.answers.items():
            if needle in text:
                self._rows = rows
                break

    def fetchall(self):
        return list(self._rows)


class FakeConn:
    def __init__(self, answers):
        self.cur = FakeCursor(answers)

    def cursor(self):
        return self.cur


# (case, label, value period end, company latest filed period, expected year in reason)
REAL_STALE_CASES = [
    ("CME shares 66.6M from 2010 (now 359.6M)", "FY", "2010-12-31", "2026-06-30", 2010),
    ("ACN share count from 2010 (FY ends Aug)", "FY", "2010-08-31", "2026-05-31", 2010),
    ("SNPS interest coverage 266x from FY2024 (FY ends Oct)", "FY", "2024-10-31", "2026-07-31", 2024),
    ("CDNS gross margin 94.5% from 2012", "FY", "2012-12-31", "2026-06-30", 2012),
    ("CDNS total debt 299.9M from 2018", "FY", "2018-12-31", "2026-06-30", 2018),
    ("VRTX total_debt 105M from 2011", "FY", "2011-12-31", "2026-06-30", 2011),
    ("INTU gross margin 82.3% from FY2020 (FY ends Jul)", "FY", "2020-07-31", "2026-04-30", 2020),
    ("GLW capex from 2020", "FY", "2020-12-31", "2026-06-30", 2020),
    ("SBUX gross profit FY2020 (52/53-week, ends Sep)", "FY", "2020-09-27", "2026-06-28", 2020),
    ("ADP operating income 2014 (FY ends Jun)", "FY", "2014-06-30", "2026-06-30", 2014),
    ("LOW interest 2011 (FY ends Jan)", "FY", "2011-01-28", "2026-08-01", 2011),
    ("MRSH accounts receivable 2011", "FY", "2011-12-31", "2026-06-30", 2011),
    ("ETN operating income FY2019", "FY", "2019-12-31", "2026-06-30", 2019),
]


@pytest.mark.unit
@pytest.mark.parametrize("case,label,value_end,latest,year", REAL_STALE_CASES)
def test_each_real_stale_cell_is_hidden_with_the_stated_reason(case, label, value_end, latest, year):
    assert staleness_reason(D(value_end), label, D(latest)) == (
        f"not in the latest filing (last reported FY{year})"
    ), case


@pytest.mark.unit
@pytest.mark.parametrize("case,label,value_end,latest,year", REAL_STALE_CASES)
def test_each_real_stale_cell_through_the_metric_row_path(case, label, value_end, latest, year):
    row = {"metric_name": "m", "value": "1.23", "period_label": label,
           "period_end": value_end, "is_null_reason": None}   # text dates, as the page gets them
    (out,) = apply_to_metric_rows([row], latest)
    assert out["value"] is None, case
    assert out["is_null_reason"] == f"not in the latest filing (last reported FY{year})"
    assert row["value"] == "1.23"                              # input not mutated


@pytest.mark.unit
def test_the_current_value_is_untouched():
    latest = "2026-06-30"
    rows = [
        {"metric_name": "gross_margin", "value": "0.45", "period_label": "TTM",
         "period_end": "2026-06-30", "is_null_reason": None},
        {"metric_name": "net_margin", "value": "0.2", "period_label": "FY",
         "period_end": "2025-12-31", "is_null_reason": None},
        {"metric_name": "roe", "value": "0.1", "period_label": "Q1",
         "period_end": "2026-03-31", "is_null_reason": None},
    ]
    assert apply_to_metric_rows(rows, latest) == rows


@pytest.mark.unit
def test_a_late_filer_whose_own_latest_filing_is_old_keeps_its_latest_values():
    # Latest filing is a 10-Q for 2022-03-31, filed years late. Today is
    # 2026-10; a calendar cutoff would hide everything. Relative to its own
    # latest filing, the latest values are current.
    latest = D("2022-03-31")
    assert staleness_reason(D("2022-03-31"), "TTM", latest) is None
    assert staleness_reason(D("2021-12-31"), "FY", latest) is None
    assert staleness_reason(D("2021-12-31"), "Q4", latest) is None
    # ...but its OWN old values are still caught against its own latest
    assert staleness_reason(D("2019-12-31"), "FY", latest) is not None


@pytest.mark.unit
def test_exactly_one_fiscal_year_behind_is_kept_two_is_hidden():
    # latest = the FY2026 10-K itself
    assert staleness_reason(D("2025-12-31"), "FY", D("2026-12-31")) is None      # 365 days
    assert staleness_reason(D("2024-12-31"), "FY", D("2026-12-31")) is not None  # 730
    # 52/53-week years: Apple FY2023 vs FY2022 is 371 days, still one year
    assert staleness_reason(D("2022-09-24"), "FY", D("2023-09-30")) is None
    # the prior full year while the new one is in progress (latest = Q3)
    assert staleness_reason(D("2025-12-31"), "FY", D("2026-09-30")) is None
    # two years back while latest is only a quarter into the new year
    assert staleness_reason(D("2024-12-31"), "FY", D("2026-03-31")) is not None  # 455


@pytest.mark.unit
def test_quarterly_and_ttm_two_quarters_kept_three_hidden():
    latest = D("2026-06-30")
    for label in ("Q1", "Q2", "Q3", "Q4", "TTM"):
        assert staleness_reason(D("2026-06-30"), label, latest) is None
        assert staleness_reason(D("2025-12-31"), label, latest) is None   # 181 days = 2 quarters
        assert staleness_reason(D("2025-09-30"), label, latest) is not None  # 273 days = 3 quarters
    # a 14-week quarter pair (196 days) is still two quarters
    assert staleness_reason(D("2025-12-16"), "Q4", latest) is None
    assert staleness_reason(D("2025-09-30"), "TTM", latest) == (
        "not in the latest filing (last reported quarter ended 2025-09-30)"
    )


@pytest.mark.unit
def test_the_threshold_is_exact_on_both_sides():
    latest = D("2026-12-31")
    from datetime import timedelta
    assert staleness_reason(latest - timedelta(days=ANNUAL_MAX_GAP_DAYS), "FY", latest) is None
    assert staleness_reason(latest - timedelta(days=ANNUAL_MAX_GAP_DAYS + 1), "FY", latest) is not None
    assert staleness_reason(latest - timedelta(days=QUARTERLY_MAX_GAP_DAYS), "Q2", latest) is None
    assert staleness_reason(latest - timedelta(days=QUARTERLY_MAX_GAP_DAYS + 1), "Q2", latest) is not None


@pytest.mark.unit
def test_threshold_sits_in_the_empty_band_between_kept_and_hidden_gaps():
    # longest "one year behind" (371-day year) and "two quarters behind"
    # (two 14-week quarters) must be kept; shortest "two years behind" (a
    # 12-week first quarter into the new year) and "three quarters behind"
    # (three 12-week quarters) must be hidden.
    assert 371 <= ANNUAL_MAX_GAP_DAYS < 364 + 84
    assert 196 <= QUARTERLY_MAX_GAP_DAYS < 3 * 84


@pytest.mark.unit
def test_a_fiscal_year_end_change_does_not_trip_it():
    # December year-end changes to September; a 9-month transition period
    # ends 2023-09-30. FY2022 (Dec) is one fiscal period behind the latest.
    assert staleness_reason(D("2022-12-31"), "FY", D("2023-09-30")) is None       # 273 days
    # and the first year after the change: Dec-2022 vs Sep-2024 is two years
    assert staleness_reason(D("2022-12-31"), "FY", D("2024-09-30")) is not None   # 639 days
    # September changes to December; the 3-month transition ends 2022-12-31
    assert staleness_reason(D("2022-09-30"), "FY", D("2022-12-31")) is None
    assert staleness_reason(D("2021-09-30"), "FY", D("2022-12-31")) is not None
    # a value dated AFTER the reference (typo or feed order) is never stale
    assert staleness_reason(D("2023-03-31"), "FY", D("2022-12-31")) is None


@pytest.mark.unit
def test_nothing_is_hidden_when_staleness_cannot_be_proved():
    assert staleness_reason(D("2010-12-31"), "FY", None) is None       # no latest filing known
    assert staleness_reason(None, "FY", D("2026-06-30")) is None       # no period
    assert staleness_reason(D("2010-12-31"), None, D("2026-06-30")) is None
    assert staleness_reason(D("2010-12-31"), "H1", D("2026-06-30")) is None   # unknown label
    assert staleness_reason("not a date", "FY", D("2026-06-30")) is None
    assert staleness_reason(D("2010-12-31"), "FY", "garbage") is None


@pytest.mark.unit
def test_fiscal_year_label_names_the_year_when_the_caller_has_it():
    # retail year ending 2020-01-31 is called FY2019 by the filer
    assert staleness_reason(D("2020-01-31"), "FY", D("2026-08-01"), fiscal_year=2019) == (
        "not in the latest filing (last reported FY2019)"
    )


def _entry(value, label, end, reason=None):
    return {"value": value, "period_label": label, "period_end": end,
            "is_null_reason": reason, "formula_version": 1}


@pytest.mark.unit
def test_apply_to_resolved_hides_only_stale_values_and_never_a_null_or_other_company():
    resolved = {
        (1, 10): _entry(Decimal("0.945"), "FY", D("2012-12-31")),          # CDNS: stale
        (1, 11): _entry(Decimal("0.2"), "TTM", D("2026-06-30")),           # current
        (2, 10): _entry(Decimal("0.5"), "FY", D("2012-12-31")),            # late filer: current
        (3, 10): _entry(None, "FY", D("2012-12-31"), "not applicable to banks"),  # bank reason kept
        (4, 10): _entry(Decimal("1"), "FY", D("2012-12-31")),              # no filing known
    }
    latest = {1: D("2026-06-30"), 2: D("2012-12-31"), 3: D("2026-06-30")}
    assert apply_to_resolved(resolved, latest) == 1
    assert resolved[(1, 10)]["value"] is None
    assert resolved[(1, 10)]["is_null_reason"] == "not in the latest filing (last reported FY2012)"
    assert resolved[(1, 11)]["value"] == Decimal("0.2")
    assert resolved[(2, 10)]["value"] == Decimal("0.5")
    assert resolved[(3, 10)]["is_null_reason"] == "not applicable to banks"
    assert resolved[(4, 10)]["value"] == Decimal("1")
    # the period fields stay, so the snapshot still records what the stored value was dated
    assert resolved[(1, 10)]["period_end"] == D("2012-12-31")


@pytest.mark.unit
def test_load_latest_filed_periods_is_one_scoped_set_based_query():
    cur = FakeCursor({"core.filing": [(1, D("2026-06-30")), (2, D("2022-03-31"))]})
    assert load_latest_filed_periods(cur, [2, 1, 1], as_of=D("2026-10-19")) == {
        1: D("2026-06-30"), 2: D("2022-03-31")}
    (sql, params), = cur.executed
    assert "group by company_id" in sql and "company_id = any" in sql
    assert params[0] == [1, 2]                       # deduped, sorted
    assert "10-K" in params[1] and "10-Q" in params[1]
    assert params[2] == D("2026-11-18")              # as_of + 30-day grace: no future typos
    cur2 = FakeCursor({})
    assert load_latest_filed_periods(cur2, []) == {}
    assert cur2.executed == []
    cur3 = FakeCursor({})
    load_latest_filed_periods(cur3, None)
    assert "company_id = any" not in cur3.executed[0][0]   # whole population


@pytest.mark.unit
def test_screener_resolve_hides_the_stale_value_and_keeps_the_current_one():
    conn = FakeConn({"core.filing": [(1, D("2026-06-30")), (2, D("2026-06-30"))]})
    result = {
        (1, 10): _entry(Decimal("0.945"), "FY", D("2012-12-31")),
        (2, 10): _entry(Decimal("0.4"), "FY", D("2025-12-31")),
    }
    assert _suppress_stale(conn, result) == 1
    assert result[(1, 10)]["value"] is None
    assert result[(2, 10)]["value"] == Decimal("0.4")
    assert _suppress_stale(FakeConn({}), {}) == 0   # empty: no query at all


@pytest.mark.unit
def test_resolve_most_recent_values_applies_the_guard_after_the_bank_rule():
    rows = [
        (1, 10, Decimal("0.945"), "FY", D("2012-12-31"), None, 1),   # stale
        (2, 10, Decimal("0.4"), "FY", D("2025-12-31"), None, 1),     # current
    ]
    conn = FakeConn({
        "with ranked as": rows,
        "from core.filing": [(1, D("2026-06-30")), (2, D("2026-06-30"))],
    })
    out = resolve_most_recent_values(conn, [10], as_of=D("2026-10-19"))
    assert out[(1, 10)]["value"] is None
    assert out[(1, 10)]["is_null_reason"].startswith("not in the latest filing")
    assert out[(2, 10)]["value"] == Decimal("0.4")


@pytest.mark.unit
def test_screener_exclusion_names_the_stale_reason_only_when_a_stored_value_was_hidden():
    excluded = {
        1: {"cik": "1", "company_name": "Stale", "missing_metrics": ["gross_margin"]},
        2: {"cik": "2", "company_name": "Genuinely null old row", "missing_metrics": ["gross_margin"]},
        3: {"cik": "3", "company_name": "Recent null", "missing_metrics": ["gross_margin"]},
        4: {"cik": "4", "company_name": "Bank", "missing_metrics": ["gross_margin"],
            "suppressed_reasons": {"gross_margin": "not applicable to banks"}},
    }

    class Cur(FakeCursor):
        def execute(self, sql, params=None):
            text = sql if isinstance(sql, str) else "snapshot"
            self.executed.append((text, params))
            if "company_screening_snapshot" in text or text == "snapshot":
                self._rows = [
                    (1, "FY", D("2012-12-31")),
                    (2, "FY", D("2012-12-31")),
                    (3, "TTM", D("2026-06-30")),
                ]
            elif "from core.filing" in text:
                self._rows = [(1, D("2026-06-30")), (2, D("2026-06-30")), (3, D("2026-06-30"))]
            elif "analytics.metric_value" in text:
                # only company 1 has a stored non-null value at that period
                assert params[0] == [1, 2] and params[1] == [10, 10]
                self._rows = [(1, 10)]

    class Conn(FakeConn):
        def __init__(self):
            self.cur = Cur({})

    # the snapshot select is a psycopg Composed in production (not a str), which
    # the fake recognises by type
    conn = Conn()
    screener_query._annotate_stale_suppression(conn, excluded, 7, {"gross_margin": 10})
    assert excluded[1]["suppressed_reasons"] == {
        "gross_margin": "not in the latest filing (last reported FY2012)"}
    assert "suppressed_reasons" not in excluded[2]     # null was never a value
    assert "suppressed_reasons" not in excluded[3]     # recent, not stale
    assert excluded[4]["suppressed_reasons"] == {"gross_margin": "not applicable to banks"}


@pytest.mark.unit
def test_screener_exclusion_issues_no_query_when_nothing_was_excluded():
    conn = FakeConn({})
    screener_query._annotate_stale_suppression(conn, {}, 7, {"gross_margin": 10})
    assert conn.cur.executed == []


@pytest.mark.unit
def test_sql_predicate_is_pinned_to_the_python_constants():
    sql = stale_predicate_sql("mv.period_label", "mv.period_end", "p.latest")
    assert f"mv.period_end < p.latest - {ANNUAL_MAX_GAP_DAYS}" in sql
    assert f"mv.period_end < p.latest - {QUARTERLY_MAX_GAP_DAYS}" in sql
    assert "mv.period_label = 'FY'" in sql
    assert "in ('Q1', 'Q2', 'Q3', 'Q4', 'TTM')" in sql
    assert "else false end" in sql                    # unknown label: never stale


@pytest.mark.unit
def test_latest_filed_period_sql_scopes_to_periodic_forms_and_ignores_future_typos():
    sql = staleness.latest_filed_period_sql("w.company_id")
    assert "lf.company_id = w.company_id" in sql
    assert "'10-K'" in sql and "'10-Q'" in sql
    assert "'8-K'" not in sql
    assert "current_date + 30" in sql


@pytest.mark.unit
def test_run_query_explains_a_stale_exclusion_and_keeps_a_current_match(monkeypatch):
    """End to end through run_query: the snapshot (built after the guard)
    carries a null for the stale company, a real value for the current one."""
    from scrooner_pipeline.screener.schema import MetricPredicate, ScreenQuery

    identity = {"cik": "", "company_name": "", "sic_code": "7372", "sic_description": "",
                "sector": "", "status": "active", "ticker": ""}
    rows = [
        (1, {**identity, "cik": "0000000001", "company_name": "Stale Co"}, {}),
        (2, {**identity, "cik": "0000000002", "company_name": "Current Co"},
         {"gross_margin": {"value": Decimal("0.80"), "period_label": "TTM",
                           "period_end": D("2026-06-30"), "formula_version": 1}}),
    ]
    monkeypatch.setattr(screener_query, "_select_snapshot_rows", lambda *a, **k: rows)

    class Cur(FakeCursor):
        def execute(self, sql, params=None):
            text = sql if isinstance(sql, str) else "snapshot"
            self.executed.append((text, params))
            self._rows = []
            if text == "snapshot":
                self._rows = [(1, "FY", D("2012-12-31"))]
            elif "from core.filing" in text:
                self._rows = [(1, D("2026-06-30"))]
            elif "analytics.metric_value" in text:
                self._rows = [(1, 10)]

    class Conn(FakeConn):
        def __init__(self):
            self.cur = Cur({})

    result = screener_query.run_query(
        Conn(),
        ScreenQuery(metric_predicates=[MetricPredicate(
            metric_name="gross_margin", operator=">", value=Decimal("0.5"))]),
        dataset_version=1,
        catalog={"gross_margin": 10},
    )
    assert [m["company_name"] for m in result["matched"]] == ["Current Co"]
    (excluded,) = result["excluded_missing_data"]
    assert excluded["company_name"] == "Stale Co"
    assert excluded["suppressed_reasons"] == {
        "gross_margin": "not in the latest filing (last reported FY2012)"}
