from datetime import date, timedelta
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import price_metrics
from scrooner_pipeline.common import rule_flags


@pytest.fixture(autouse=True)
def _per_share_rule_on(monkeypatch):
    """RU-1 behaviour is behind pershare.never_derive_ttm@1; test_price_metrics.py keeps the flag-off (legacy) tests."""
    monkeypatch.setenv(rule_flags.ENV_ENABLED, price_metrics.RULE_PER_SHARE_TTM)


class PriceCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        self.conn.executed.append((" ".join(sql.split()), params))

    def executemany(self, sql, rows):
        rows = [dict(row) for row in rows]
        self.conn.rows.extend(rows)
        self.conn.executemany_calls.append((" ".join(sql.split()), rows))


class PriceConnection:
    def __init__(self):
        self.executed = []
        self.rows = []
        self.executemany_calls = []

    def cursor(self):
        return PriceCursor(self)

    def commit(self):
        pass


METRIC_NAMES = (
    "market_cap",
    "trailing_pe",
    "price_to_sales",
    "price_to_book",
    "dividend_yield",
    "fcf_yield",
)
METRIC_IDS = {name: idx for idx, name in enumerate(METRIC_NAMES, 1)}
CONCEPT_IDS = {
    "diluted_eps": 10,
    "revenue": 11,
    "dividends_per_share": 12,
    "cfo": 13,
    "capex": 14,
    "shares_outstanding": 15,
    "stockholders_equity": 16,
    "net_income": 17,
}


def quarterly(value, first_fact_id):
    return {
        (2025, quarter): (Decimal(value), [first_fact_id + offset])
        for offset, quarter in enumerate(("Q1", "Q2", "Q3", "Q4"))
    }


def install_price_inputs(monkeypatch, price):
    by_concept = {
        10: quarterly("2", 100),
        11: quarterly("25", 110),
        12: quarterly("0.25", 120),
        13: quarterly("10", 130),
        14: quarterly("2", 140),
        17: quarterly("30", 170),
    }
    monkeypatch.setattr(
        price_metrics,
        "_load_latest_price",
        lambda _conn, _company: (price, date.today()),
    )
    monkeypatch.setattr(
        price_metrics,
        "_load_latest_diluted_weighted_shares",
        lambda _conn, _company: None,
    )
    monkeypatch.setattr(
        price_metrics, "_load_shares_outstanding_fallback", lambda _conn, _company: None
    )
    monkeypatch.setattr(
        price_metrics,
        "_load_quarterly_facts",
        lambda _conn, _company, concept: by_concept[concept],
    )
    # TTM EPS at the Q4 2025 anchor is the filed FY2025 diluted EPS (4 x 2).
    monkeypatch.setattr(
        price_metrics,
        "_load_annual_facts",
        lambda _conn, _company, concept: (
            {2025: (Decimal("8"), [109], None)} if concept == 10 else {}
        ),
    )
    monkeypatch.setattr(
        price_metrics,
        "_latest_instant_fact",
        lambda _conn, _company, concept: (
            (Decimal("100"), [150], date.today() - timedelta(days=90))
            if concept == 15
            else (Decimal("200"), [160], date(2025, 9, 27))
        ),
    )


@pytest.mark.unit
def test_all_six_price_metrics_compute_with_decimal_lineage(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("10"))
    conn = PriceConnection()

    stats = price_metrics.calculate_price_metrics_for_company(
        conn, 1, METRIC_IDS, CONCEPT_IDS
    )
    rows = {
        name: next(
            r for r in conn.rows if r["metric_definition_id"] == METRIC_IDS[name]
        )
        for name in METRIC_NAMES
    }

    assert stats == {"computed": 6, "null": 0}
    assert rows["market_cap"]["value"] == Decimal("1000")
    assert rows["trailing_pe"]["value"] == Decimal("1.25")
    assert rows["trailing_pe"]["source_fact_ids"] == [
        109
    ]  # the filed FY EPS, not four quarters
    assert rows["price_to_sales"]["value"] == Decimal("10")
    assert rows["price_to_book"]["value"] == Decimal("5")
    assert rows["dividend_yield"]["value"] == Decimal("0.1")
    assert rows["fcf_yield"]["value"] == Decimal("0.032")
    assert rows["fcf_yield"]["source_fact_ids"] == [
        150,
        130,
        131,
        132,
        133,
        140,
        141,
        142,
        143,
    ]
    delete_sql, _params = conn.executed[0]
    assert "period_label = 'TTM'" in delete_sql


@pytest.mark.unit
def test_non_positive_price_fails_closed_instead_of_dividing(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("0"))
    conn = PriceConnection()

    stats = price_metrics.calculate_price_metrics_for_company(
        conn, 1, METRIC_IDS, CONCEPT_IDS
    )

    assert stats == {"computed": 0, "null": 6}
    assert {row["is_null_reason"] for row in conn.rows} == {
        "invalid:non_positive_price"
    }


@pytest.mark.unit
def test_missing_price_null_rows_still_satisfy_required_period_dates(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("10"))
    monkeypatch.setattr(
        price_metrics, "_load_latest_price", lambda _conn, _company: None
    )
    conn = PriceConnection()

    stats = price_metrics.calculate_price_metrics_for_company(
        conn, 1, METRIC_IDS, CONCEPT_IDS
    )

    assert stats == {"computed": 0, "null": 6}
    assert {row["is_null_reason"] for row in conn.rows} == {"missing:real_price"}
    assert all(isinstance(row["period_start"], date) for row in conn.rows)
    assert all(row["period_start"] == row["period_end"] for row in conn.rows)


@pytest.mark.unit
def test_stale_price_fails_closed_instead_of_valuing_at_an_old_bar(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("10"))
    old_bar = date.today() - timedelta(days=price_metrics.MAX_PRICE_AGE_DAYS + 1)
    monkeypatch.setattr(
        price_metrics,
        "_load_latest_price",
        lambda _conn, _company: (Decimal("10"), old_bar),
    )
    conn = PriceConnection()

    stats = price_metrics.calculate_price_metrics_for_company(
        conn, 1, METRIC_IDS, CONCEPT_IDS
    )

    assert stats == {"computed": 0, "null": 6}
    assert {row["is_null_reason"] for row in conn.rows} == {"stale:real_price"}
    assert all(row["period_end"] == old_bar for row in conn.rows)


TODAY = date(2026, 9, 27)
OLD = date(2010, 1, 27)
RECENT = date(2026, 6, 30)


@pytest.mark.unit
def test_fresh_point_in_time_share_count_wins():
    chosen, reason = price_metrics._choose_shares(
        (Decimal("100"), [1], RECENT),
        (Decimal("90"), [2], RECENT),
        (Decimal("95"), [], RECENT),
        TODAY,
    )
    assert chosen == (Decimal("100"), [1]) and reason is None


@pytest.mark.unit
def test_stale_share_count_uses_cover_page_when_it_agrees_with_diluted_average():
    # Visa-shaped: last plain count is from 2010.
    chosen, _ = price_metrics._choose_shares(
        (Decimal("469"), [1], OLD),
        (Decimal("1900"), [2], RECENT),
        (Decimal("1812"), [], RECENT),
        TODAY,
    )
    assert chosen == (Decimal("1812"), [])


@pytest.mark.unit
def test_cover_page_reading_one_class_is_rejected_for_diluted_average():
    # Comcast-shaped: the cover page parser read only Class B.
    chosen, _ = price_metrics._choose_shares(
        (Decimal("2000"), [1], OLD),
        (Decimal("3593"), [2], RECENT),
        (Decimal("9.4"), [], RECENT),
        TODAY,
    )
    assert chosen == (Decimal("3593"), [2])


@pytest.mark.unit
def test_only_stale_inputs_give_a_stale_reason_not_an_old_value():
    chosen, reason = price_metrics._choose_shares(
        (Decimal("469"), [1], OLD), None, None, TODAY
    )
    assert chosen is None and reason == "stale:shares_outstanding"


@pytest.mark.unit
def test_no_inputs_is_missing():
    assert price_metrics._choose_shares(None, None, None, TODAY) == (
        None,
        "missing:shares_outstanding",
    )


@pytest.mark.unit
def test_pe_falls_back_to_market_cap_over_net_income_without_diluted_eps(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("10"))
    original = price_metrics._load_quarterly_facts
    monkeypatch.setattr(
        price_metrics,
        "_load_quarterly_facts",
        lambda conn, company, concept: (
            {} if concept == 10 else original(conn, company, concept)
        ),
    )
    monkeypatch.setattr(
        price_metrics, "_load_annual_facts", lambda _conn, _company, _concept: {}
    )
    conn = PriceConnection()

    price_metrics.calculate_price_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)
    pe = next(
        r for r in conn.rows if r["metric_definition_id"] == METRIC_IDS["trailing_pe"]
    )

    # market cap 1000 (100 shares x $10) / TTM net income 120 (4 x 30)
    assert pe["value"] == Decimal("1000") / Decimal("120")
    assert pe["is_null_reason"] is None
    assert pe["source_fact_ids"] == [150, 170, 171, 172, 173]


# --- RU-1 (WO-2, 2026-10-22): EPS never anchors, never summed; derived
# per-share quarters never used. Each test names the mutant it kills. ---


def series(values_by_key, first_id, *, ends=None, derived=()):
    """A QuarterFacts like the real loader returns."""
    out = price_metrics.QuarterFacts(
        (key, (Decimal(v), [first_id + i]))
        for i, (key, v) in enumerate(values_by_key.items())
    )
    out.end_dates = dict(ends or {})
    out.derived_keys = set(derived)
    return out


Q = ("Q1", "Q2", "Q3", "Q4")


def install(monkeypatch, *, quarterly, annual_eps=None, price=Decimal("10")):
    install_price_inputs(monkeypatch, price)
    monkeypatch.setattr(
        price_metrics,
        "_load_quarterly_facts",
        lambda _c, _co, concept: quarterly.get(concept, {}),
    )
    monkeypatch.setattr(
        price_metrics,
        "_load_annual_facts",
        lambda _c, _co, concept: (annual_eps or {}) if concept == 10 else {},
    )


def run_rows(monkeypatch=None):
    conn = PriceConnection()
    price_metrics.calculate_price_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)
    return {
        name: next(
            r for r in conn.rows if r["metric_definition_id"] == METRIC_IDS[name]
        )
        for name in METRIC_NAMES
    }


@pytest.mark.unit
def test_just_filed_10k_anchors_on_q4_revenue_not_on_eps(monkeypatch):
    # The 10-K is in: Q4 revenue/NI exist (additive, derived), Q4 EPS does not.
    # Kills: anchor = latest EPS quarter (Q3) -> TTM revenue stops at Q3.
    revenue = series({(2025, q): "25" for q in Q} | {(2024, "Q4"): "20"}, 110)
    net_income = series({(2025, q): "30" for q in Q} | {(2024, "Q4"): "28"}, 170)
    eps_q = series({(2025, q): "2" for q in Q[:3]}, 100)
    install(
        monkeypatch,
        quarterly={
            10: eps_q,
            11: revenue,
            17: net_income,
            13: series({(2025, q): "10" for q in Q}, 130),
            14: series({(2025, q): "2" for q in Q}, 140),
        },
    )
    rows = run_rows()
    assert rows["price_to_sales"]["value"] == Decimal("10")  # 1000 / (4 x 25)
    assert (
        113 in rows["price_to_sales"]["source_fact_ids"]
    )  # Q4 2025 revenue is in the window
    assert rows["fcf_yield"]["value"] == Decimal("0.032")


@pytest.mark.unit
def test_q4_anchor_ttm_eps_is_the_filed_fy_eps(monkeypatch):
    # MSFT FY26 shape: FY diluted EPS 17.95 filed; Q4 = 4.80 was derived (filed 4.81).
    # Kills: summing quarters (3.72 + 5.16 + 4.27 + 4.80) or using derived Q4.
    eps_q = series(
        {
            (2026, "Q1"): "3.72",
            (2026, "Q2"): "5.16",
            (2026, "Q3"): "4.27",
            (2026, "Q4"): "4.80",
        },
        100,
        derived={(2026, "Q4")},
    )
    revenue = series(
        {(2026, q): "25" for q in Q}, 110, ends={(2026, "Q4"): date(2026, 6, 30)}
    )
    install(
        monkeypatch,
        quarterly={
            10: eps_q,
            11: revenue,
            17: series({(2026, q): "30" for q in Q}, 170),
        },
        annual_eps={2026: (Decimal("17.95"), [341900], date(2026, 6, 30))},
        price=Decimal("359"),
    )
    pe = run_rows()["trailing_pe"]
    assert pe["value"] == Decimal("359") / Decimal("17.95")
    assert pe["source_fact_ids"] == [341900]


@pytest.mark.unit
def test_q4_anchor_fy_eps_with_other_end_date_is_not_paired(monkeypatch):
    # A fiscal-label error (W5): FY labelled 2026 ends a year away from the Q4 anchor.
    revenue = series(
        {(2026, q): "25" for q in Q}, 110, ends={(2026, "Q4"): date(2026, 6, 30)}
    )
    install(
        monkeypatch,
        quarterly={11: revenue, 17: series({(2026, q): "30" for q in Q}, 170)},
        annual_eps={2026: (Decimal("17.95"), [341900], date(2025, 6, 30))},
    )
    pe = run_rows()["trailing_pe"]
    assert pe["source_fact_ids"] == [
        150,
        170,
        171,
        172,
        173,
    ]  # market cap / TTM NI, not the FY EPS


@pytest.mark.unit
def test_q2_anchor_pe_is_market_cap_over_ttm_net_income(monkeypatch):
    # KLAC shape: the window (Q3, Q4 of FY26, Q1, Q2 of FY27) holds the derived
    # Q4 -22.61 from mixing split bases. Kills: any sum of quarterly EPS.
    keys = [(2026, "Q3"), (2026, "Q4"), (2027, "Q1"), (2027, "Q2")]
    eps_q = series(
        dict(zip(keys, ["9.12", "-22.61", "1.10", "1.15"])), 100, derived={(2026, "Q4")}
    )
    ni = series(dict(zip(keys, ["30", "30", "30", "30"])), 170)
    install(
        monkeypatch,
        quarterly={10: eps_q, 11: series(dict(zip(keys, ["25"] * 4)), 110), 17: ni},
        annual_eps={2026: (Decimal("3.66"), [77564000], None)},
    )
    pe = run_rows()["trailing_pe"]
    assert pe["value"] == Decimal("1000") / Decimal("120")
    assert pe["source_fact_ids"] == [150, 170, 171, 172, 173]
    assert 77564000 not in pe["source_fact_ids"]


@pytest.mark.unit
def test_pe_without_eps_and_without_market_cap_carries_the_share_reason(monkeypatch):
    keys = [(2026, "Q3"), (2026, "Q4"), (2027, "Q1"), (2027, "Q2")]
    install(
        monkeypatch,
        quarterly={
            11: series(dict(zip(keys, ["25"] * 4)), 110),
            17: series(dict(zip(keys, ["30"] * 4)), 170),
        },
    )
    monkeypatch.setattr(
        price_metrics, "_latest_instant_fact", lambda _c, _co, _concept: None
    )
    pe = run_rows()["trailing_pe"]
    assert pe["value"] is None and pe["is_null_reason"] == "missing:shares_outstanding"


@pytest.mark.unit
def test_bank_without_revenue_anchors_on_net_income(monkeypatch):
    install(
        monkeypatch,
        quarterly={17: series({(2025, q): "30" for q in Q}, 170)},
        annual_eps={2025: (Decimal("8"), [109], None)},
    )
    rows = run_rows()
    assert rows["trailing_pe"]["value"] == Decimal("1.25")
    assert rows["price_to_sales"]["is_null_reason"] == "missing:revenue_ttm"


@pytest.mark.unit
def test_years_old_eps_is_ignored_and_pe_uses_current_net_income(monkeypatch):
    # KKR-shaped: plain diluted EPS last filed for FY2018, net income current.
    install(
        monkeypatch,
        quarterly={
            11: series({(2025, q): "25" for q in Q}, 110),
            17: series({(2025, q): "30" for q in Q}, 170),
        },
        annual_eps={2018: (Decimal("2"), [900], None)},
    )
    pe = run_rows()["trailing_pe"]
    assert pe["value"] == Decimal("1000") / Decimal("120")
    assert 900 not in (pe["source_fact_ids"] or [])


@pytest.mark.unit
def test_derived_dps_quarter_is_never_summed_into_dividend_yield(monkeypatch):
    # V FY2025: 0.59 quarterly rate tagged on the FY context made the derived
    # Q4 DPS 0.59 - 1.77 = -1.18 (0001403161-25-000089 R8). Kills: summing it.
    dps = series(
        {
            (2025, "Q1"): "0.59",
            (2025, "Q2"): "0.59",
            (2025, "Q3"): "0.59",
            (2025, "Q4"): "-1.18",
        },
        120,
        derived={(2025, "Q4")},
    )
    install(
        monkeypatch,
        quarterly={
            11: series({(2025, q): "25" for q in Q}, 110),
            12: dps,
            17: series({(2025, q): "30" for q in Q}, 170),
        },
    )
    dy = run_rows()["dividend_yield"]
    assert dy["value"] is None
    assert dy["is_null_reason"] == price_metrics.PER_SHARE_NOT_DERIVED_REASON


@pytest.mark.unit
def test_dividend_yield_after_retirement_names_the_unfiled_q4(monkeypatch):
    # LEA after the derived Q4 is retired: Q1-Q3 filed, Q4 absent.
    dps = series(
        {(2025, "Q1"): "0.77", (2025, "Q2"): "0.77", (2025, "Q3"): "0.77"}, 120
    )
    install(
        monkeypatch,
        quarterly={
            11: series({(2025, q): "25" for q in Q}, 110),
            12: dps,
            17: series({(2025, q): "30" for q in Q}, 170),
        },
    )
    dy = run_rows()["dividend_yield"]
    assert (
        dy["value"] is None
        and dy["is_null_reason"] == price_metrics.PER_SHARE_NOT_DERIVED_REASON
    )


@pytest.mark.unit
def test_non_payer_keeps_the_missing_reason(monkeypatch):
    install(
        monkeypatch,
        quarterly={
            11: series({(2025, q): "25" for q in Q}, 110),
            17: series({(2025, q): "30" for q in Q}, 170),
        },
    )
    assert (
        run_rows()["dividend_yield"]["is_null_reason"]
        == "missing:dividends_per_share_ttm"
    )


@pytest.mark.unit
def test_four_filed_dps_quarters_still_give_a_yield(monkeypatch):
    dps = series({(2025, q): "0.25" for q in Q}, 120)
    install(
        monkeypatch,
        quarterly={
            11: series({(2025, q): "25" for q in Q}, 110),
            12: dps,
            17: series({(2025, q): "30" for q in Q}, 170),
        },
    )
    dy = run_rows()["dividend_yield"]
    assert dy["value"] == Decimal("0.1") and dy["source_fact_ids"] == [
        120,
        121,
        122,
        123,
    ]


@pytest.mark.unit
def test_window_blocked_helper():
    anchor = (2025, "Q2")
    window = {(2024, "Q3"): 1, (2024, "Q4"): 1, (2025, "Q1"): 1, (2025, "Q2"): 1}
    kept = {k: v for k, v in window.items() if k != (2024, "Q4")}
    assert (
        price_metrics._per_share_window_blocked(window, kept, anchor) is True
    )  # derived dropped
    assert (
        price_metrics._per_share_window_blocked(kept, kept, anchor) is True
    )  # Q4 not filed
    assert (
        price_metrics._per_share_window_blocked({}, {}, anchor) is False
    )  # never paid
    assert price_metrics._per_share_window_blocked(window, window, anchor) is False
    assert price_metrics._per_share_window_blocked(window, kept, None) is False


@pytest.mark.unit
def test_q2_anchor_never_uses_an_fy_eps_even_with_the_same_year_label(monkeypatch):
    # A fiscal-label error (W5) can put an FY row under the anchor's year.
    # Kills: taking TTM EPS from the FY at a non-Q4 anchor.
    keys = [(2026, "Q3"), (2026, "Q4"), (2027, "Q1"), (2027, "Q2")]
    install(
        monkeypatch,
        quarterly={
            11: series(dict(zip(keys, ["25"] * 4)), 110),
            17: series(dict(zip(keys, ["30"] * 4)), 170),
        },
        annual_eps={
            2027: (Decimal("8"), [109], None),
            2026: (Decimal("7"), [108], None),
        },
    )
    pe = run_rows()["trailing_pe"]
    assert pe["source_fact_ids"] == [150, 170, 171, 172, 173]
