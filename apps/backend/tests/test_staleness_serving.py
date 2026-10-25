"""Staleness guard on the company page and the watchlist (2026-10-19,
pipeline common/staleness.py). A value far behind the company's own latest
filed period is returned null with the stated reason; a current value, a late
filer's latest values and a bank's own reason are untouched."""

import copy
from contextlib import contextmanager

import pytest

import company_page
from company_page import (
    get_company_page_data,
    stale_metric_history_names,
    suppress_stale_book_value,
)
from routers import watchlists
from tests.test_company_page_bank_suppression import METRICS, _Conn
from tests.test_watchlists import OWNER, WatchlistConnection

REASON_2012 = "not in the latest filing (last reported FY2012)"


def _page_row(company, metrics, history=(), book_value=None):
    return (
        company, copy.deepcopy(metrics), [], [], [], [], [], None, None, [], book_value,
        list(history), [], None, [], None, None, [], [],
    )


STALE_AND_CURRENT = [
    # CDNS shape: gross margin from FY2012 is the latest row on file
    {"metric_name": "gross_margin", "value": "0.945", "period_label": "FY",
     "period_end": "2012-12-31", "is_null_reason": None},
    {"metric_name": "roe", "value": "0.11", "period_label": "TTM",
     "period_end": "2026-06-30", "is_null_reason": None},
    {"metric_name": "debt_to_equity", "value": "0.3", "period_label": "Q1",
     "period_end": "2025-09-30", "is_null_reason": None},     # 3 quarters back
    {"metric_name": "revenue_growth_yoy", "value": None, "period_label": "FY",
     "period_end": "2012-12-31", "is_null_reason": "incomplete"},  # already null
]


@pytest.mark.unit
def test_company_page_hides_stale_metrics_book_value_and_history_with_reasons():
    company = {"id": 1, "ticker": "CDNS", "is_bank": False,
               "latest_filed_period": "2026-06-30", "book_value_period_end": "2011-12-31"}
    history = [
        {"metric_name": "gross_margin", "value": "0.94", "period_end": "2012-12-31"},
        {"metric_name": "gross_margin", "value": "0.93", "period_end": "2011-12-31"},
        {"metric_name": "roe", "value": "0.1", "period_end": "2025-12-31"},
    ]
    page = get_company_page_data(_Conn(_page_row(company, STALE_AND_CURRENT, history, "105000000")), "cdns")
    m = page["metrics"]
    assert m["gross_margin"]["value"] is None and m["gross_margin"]["is_null_reason"] == REASON_2012
    assert m["debt_to_equity"]["value"] is None
    assert m["debt_to_equity"]["is_null_reason"] == (
        "not in the latest filing (last reported quarter ended 2025-09-30)")
    assert m["roe"]["value"] == "0.11" and m["roe"]["is_null_reason"] is None
    assert m["revenue_growth_yoy"]["is_null_reason"] == "incomplete"     # own reason kept
    assert page["bookValue"] is None
    assert page["bookValueSuppressedReason"].startswith("not in the latest filing")
    assert "gross_margin" not in page["metricHistory"]
    assert "gross_margin" not in page["metricTrendHistory"]
    assert page["metricHistory"]["roe"] == ["0.1"]


@pytest.mark.unit
def test_company_page_current_and_late_filer_pages_are_unchanged():
    current = {"id": 1, "ticker": "X", "is_bank": False, "latest_filed_period": "2026-06-30",
               "book_value_period_end": "2026-06-30"}
    page = get_company_page_data(_Conn(_page_row(current, METRICS, book_value="5")), "x")
    assert page["metrics"]["roe"]["value"] == "0.11"
    assert page["metrics"]["fcf_yield"]["value"] == "0.406"
    assert page["bookValue"] == "5" and page["bookValueSuppressedReason"] is None

    # a late filer: its own latest filing is 2022-03-31, so 2022 values are current
    late = {"id": 2, "ticker": "L", "is_bank": False, "latest_filed_period": "2022-03-31",
            "book_value_period_end": "2022-03-31"}
    rows = [{"metric_name": "roe", "value": "0.2", "period_label": "TTM",
             "period_end": "2022-03-31", "is_null_reason": None}]
    page = get_company_page_data(_Conn(_page_row(late, rows, book_value="9")), "l")
    assert page["metrics"]["roe"]["value"] == "0.2"
    assert page["bookValue"] == "9"

    # no latest filing known: nothing can be proved stale, nothing is hidden
    unknown = {"id": 3, "ticker": "U", "is_bank": False}
    page = get_company_page_data(_Conn(_page_row(unknown, STALE_AND_CURRENT)), "u")
    assert page["metrics"]["gross_margin"]["value"] == "0.945"


@pytest.mark.unit
def test_bank_reason_is_not_overwritten_by_the_stale_reason():
    bank = {"id": 4, "ticker": "B", "is_bank": True, "latest_filed_period": "2026-06-30"}
    rows = [{"metric_name": "fcf_yield", "value": "0.4", "period_label": "FY",
             "period_end": "2012-12-31", "is_null_reason": None}]
    page = get_company_page_data(_Conn(_page_row(bank, rows)), "b")
    assert page["metrics"]["fcf_yield"]["is_null_reason"] == "not applicable to banks"


@pytest.mark.unit
def test_history_and_book_value_helpers():
    rows = [{"metric_name": "a", "value": "1", "period_end": "2012-12-31"},
            {"metric_name": "a", "value": "1", "period_end": "2025-12-31"},   # order independent
            {"metric_name": "b", "value": "1", "period_end": "2012-12-31"}]
    assert stale_metric_history_names(rows, "2026-06-30") == {"b"}
    assert stale_metric_history_names(rows, None) == set()
    assert suppress_stale_book_value(None, "2011-12-31", "2026-06-30") == (None, None)
    assert suppress_stale_book_value("7", "2026-03-31", "2026-06-30") == ("7", None)


@pytest.mark.unit
def test_query_carries_latest_filed_period_and_filters_stale_peer_cells_in_sql():
    sql = company_page._QUERY
    assert "'latest_filed_period'" in sql and "'book_value_period_end'" in sql
    assert "as latest_filed_period" in sql                       # peers carry their own
    assert "not coalesce((case when mv.period_label = 'FY'" in sql
    assert "mv.period_end < p.latest_filed_period - 400" in sql
    assert "mv.period_end < p.latest_filed_period - 230" in sql
    assert "%" not in sql.replace("%(ticker)s", "")             # nothing for psycopg to misread


def _watch_conn(fundamental_rows, valuation_cols=(None, None, None), pe=None, bank_ids=()):
    class C(WatchlistConnection):
        pass
    c = C()
    c.fundamental_rows = fundamental_rows
    c.valuation_cols = valuation_cols
    c.bank_ids = set(bank_ids)
    c.pe = pe
    c.items.add((OWNER, 1))
    return c


def _list(monkeypatch, conn):
    @contextmanager
    def pooled():
        yield conn
    monkeypatch.setattr(watchlists, "get_pooled_connection", pooled)
    return watchlists.list_watchlist(company_id=None, user_id=OWNER)["items"][0]


@pytest.mark.unit
def test_watchlist_hides_a_stale_fundamental_with_its_year_ago_comparative(monkeypatch):
    rows = [
        (1, "operating_margin", "0.3", "2024-12-31", "Q4", 1),      # stale (latest filed 2026-06-30)
        (1, "operating_margin", "0.25", "2023-12-31", "Q4", 5),     # its comparative goes with it
        (1, "diluted_eps", "1.1", "2026-06-30", "Q2", 1),           # current
        (1, "diluted_eps", "0.9", "2025-06-30", "Q2", 5),           # year-ago: never judged alone
    ]
    item = _list(monkeypatch, _watch_conn(rows, ("TTM", "2026-06-30", "2026-06-30")))
    # row[16..18] = valuation label, valuation end, latest filed
    assert "operating_margin" not in item["fundamentals"]
    assert item["suppressed_reasons"] == {
        "operating_margin": "not in the latest filing (last reported quarter ended 2024-12-31)"}
    assert item["fundamentals"]["diluted_eps"]["latest"]["value"] == "1.1"
    assert item["fundamentals"]["diluted_eps"]["previous"]["value"] == "0.9"


@pytest.mark.unit
def test_watchlist_without_staleness_is_unchanged_and_has_no_reasons_key(monkeypatch):
    rows = [(1, "operating_margin", "0.3", "2026-06-30", "Q2", 1)]
    item = _list(monkeypatch, _watch_conn(rows, ("TTM", "2026-06-30", "2026-06-30")))
    assert item["fundamentals"]["operating_margin"]["latest"]["value"] == "0.3"
    assert "suppressed_reasons" not in item
    # no latest filing known: nothing hidden even for an old value
    item = _list(monkeypatch, _watch_conn([(1, "operating_margin", "0.3", "2012-06-30", "Q2", 1)]))
    assert item["fundamentals"]["operating_margin"]["latest"]["value"] == "0.3"


@pytest.mark.unit
def test_watchlist_late_filer_keeps_its_latest_values(monkeypatch):
    rows = [(1, "operating_margin", "0.3", "2022-03-31", "Q1", 1)]
    item = _list(monkeypatch, _watch_conn(rows, ("TTM", "2022-03-31", "2022-03-31")))
    assert item["fundamentals"]["operating_margin"]["latest"]["value"] == "0.3"


@pytest.mark.unit
def test_watchlist_hides_a_stale_pe_and_keeps_a_current_one(monkeypatch):
    stale = _list(monkeypatch, _watch_conn([], ("TTM", "2024-06-30", "2026-06-30"), pe="266"))
    assert stale["valuation"] is None
    assert stale["suppressed_reasons"] == {
        "trailing_pe": "not in the latest filing (last reported quarter ended 2024-06-30)"}
    current = _list(monkeypatch, _watch_conn([], ("TTM", "2026-06-30", "2026-06-30"), pe="21"))
    assert current["valuation"] == {"label": "P/E", "value": "21"}
    assert "suppressed_reasons" not in current
