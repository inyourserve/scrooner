"""NA-15 ADS conversion, tests T1-T12 of data-team/strategy/team/WO-ADS-RATIO-AND-MULTICLASS-2026-10-22.md.
Ratios and counts are the card's FILING-CHECKED inputs; prices and stored values are the card's DATA-INFERRED
reads of 2026-10-22."""

from __future__ import annotations

from datetime import date
from decimal import Decimal as D

import pytest

from scrooner_pipeline.mapper import ads_conversion as a
from scrooner_pipeline.mapper import price_publish_guards as g

AKTX, ZLAB, AMRN, GPCR, SLN, DBVT, KZIA, SCNI = (
    "0001541157", "0001704292", "0000897448", "0001888886", "0001479615", "0001613780", "0001075880", "0001611747",
)  # fmt: skip
CO = "CommonStockSharesOutstanding"
EN = "EntityCommonStockSharesOutstanding"


def obs(value, as_of, filed, tag=CO):
    return a.CountObs(D(str(value)), as_of, filed, tag)


def convert(cik, o):
    d = a.decide(cik, o, conversion_on=True)
    assert d is not None and d.kind == "convert", d
    return d


def mcap(d, old_shares, price):
    r = a.apply_decision(
        d, {"market_cap": D(str(old_shares)) * D(str(price))}, old_shares=D(str(old_shares)),
        market_cap_fact_ids={1}, pe_fact_ids=set(),
    )  # fmt: skip
    return r["market_cap"][0]


# T1
def test_t1_aktx_80000_ratio_gives_17_million_not_1_3_trillion():
    d = convert(AKTX, obs("155758529533", date(2026, 8, 13), date(2026, 8, 13), EN))
    assert abs(mcap(d, "155758529533", "8.76") - D("17055559.6")) < 1


# T2
def test_t2_aktx_with_only_the_10k_cover_filed_before_the_ratio_change_is_hidden():
    d = a.decide(
        AKTX,
        obs("91567009533", date(2026, 3, 1), date(2026, 3, 30), EN),
        conversion_on=True,
    )
    assert (d.kind, d.reason) == ("hide", a.REASON_CHANGED)


# T3
def test_t3_zlab_divides_by_10_and_refuses_pre_subdivision_counts():
    d = convert(ZLAB, obs("1122445390", date(2026, 6, 30), date(2026, 8, 6)))
    assert abs(mcap(d, "1122445390", "23.25") - D("2609685531.75")) < 1
    old = a.decide(
        ZLAB, obs("110000000", date(2021, 12, 31), date(2022, 3, 1)), conversion_on=True
    )
    assert old.reason == a.REASON_CHANGED
    late = a.decide(
        ZLAB, obs("110000000", date(2021, 12, 31), date(2022, 6, 1)), conversion_on=True
    )
    assert (
        late.reason == a.REASON_CHANGED
    )  # filed after the change, counted before the subdivision


# T4
def test_t4_amrn_uses_the_balance_sheet_count_never_the_cover_fact():
    d = convert(AMRN, obs("420044022", date(2026, 6, 30), date(2026, 7, 29)))
    assert abs(mcap(d, "420044022", "11.50") - D("241525312.65")) < 1
    adr = a.decide(
        AMRN,
        obs("20632560", date(2026, 7, 24), date(2026, 7, 29), EN),
        conversion_on=True,
    )
    assert adr.reason == a.REASON_NO_COUNT


# T5
def test_t5_dbvt_cover_includes_treasury_so_it_stays_hidden():
    d = a.decide(
        DBVT,
        obs("296061497", date(2026, 7, 16), date(2026, 7, 16), EN),
        conversion_on=True,
    )
    assert (d.kind, d.reason) == ("hide", a.REASON_TREASURY)


# T6
def test_t6_gpcr_and_sln_divide_by_3():
    g_ = convert(GPCR, obs("213929572", date(2026, 7, 31), date(2026, 8, 6), EN))
    assert abs(mcap(g_, "213929572", "22.20") - D("1583078832.8")) < 1
    s_ = convert(SLN, obs("141740037", date(2026, 7, 31), date(2026, 8, 10), EN))
    stored = D("2783774327")
    r = a.apply_decision(
        s_,
        {"market_cap": stored},
        old_shares=D("141740037"),
        market_cap_fact_ids=set(),
        pe_fact_ids=set(),
    )
    assert abs(r["market_cap"][0] - D("927924775.67")) < 1  # stored was 3x


# T7
@pytest.mark.parametrize("cik", [KZIA, SCNI])
@pytest.mark.parametrize("on", [True, False])
def test_t7_foreign_private_issuers_are_never_computed(cik, on):
    d = a.decide(
        cik, obs("809418734", date(2025, 6, 30), date(2025, 9, 1), EN), conversion_on=on
    )
    assert (d.kind, d.reason) == ("hide", a.REASON_FOREIGN)


# T8/T9: RPAY and TBLA are caught by the scale test, and WASO is never an ADS share count
def test_t8_t9_rpay_tbla_stay_hidden_and_waso_is_not_an_allowed_count_tag():
    o = g.ShareObservations(D("85881082"), None, None)
    assert (
        g.share_basis_reason("0001720592", D("83285379000"), o)
        == "shares_scale_conflict:cover_page"
    )
    o2 = g.ShareObservations(None, D("270155398"), None)
    assert g.share_basis_reason("0001840502", D("290505359000"), o2).startswith(
        "shares_scale_conflict"
    )
    for entry in a.ADS_TABLE.values():
        assert not any("Weighted" in t for t in entry.count_tags)
    d = a.decide(
        AKTX,
        obs(
            "143317469445",
            date(2026, 6, 30),
            date(2026, 8, 13),
            "WeightedAverageNumberOfDilutedSharesOutstanding",
        ),
        conversion_on=True,
    )
    assert d.reason == a.REASON_NO_COUNT


# T10
@pytest.mark.parametrize(
    ("title", "want"),
    [
        ("American Depositary Shares, each representing 80,000 Ordinary Shares", "80000"),
        ("American Depositary Shares each representing 10 Ordinary Shares", "10"),
        ("each representing three ordinary shares (American Depositary Shares)", "3"),
        ("American Depositary Shares, each representing five ordinary shares", "5"),
        ("each ADS representing the right to receive twenty (20) Ordinary Shares (American Depositary Share)", "20"),
        ("American Depositary Shares, each representing five-hundred Ordinary Shares", "500"),
        ("American Depositary Shares, each representing 4,000 ordinary share", "4000"),
        ("American Depositary Shares each representing one-half (1/2) ordinary share", "0.5"),
        ("American Depositary Shares, each representing one Ordinary Share", "1"),
    ],
)  # fmt: skip
def test_t10_ratio_parser(title, want):
    assert a.parse_ads_ratio(title) == D(want)


@pytest.mark.parametrize(
    "title",
    [
        "Warrants to purchase ordinary shares",
        "Preferred Stock Purchase Rights",
        "Common Stock, $0.01 par value",
    ],
)
def test_t10_parser_rejects_non_depositary_titles(title):
    assert a.parse_ads_ratio(title) is None


# T11
@pytest.mark.parametrize(
    "cik", ["0000818686", "0000016875", "0000049938", "0000320193"]
)  # TEVA CP IMO AAPL
def test_t11_negative_controls_are_not_in_the_table(cik):
    assert a.decide(cik, None, conversion_on=True) is None


# T12
STORED = {"market_cap": D("4830506253"), "trailing_pe": D("-164.2857142857"), "dividend_yield": D("0.001"),
          "price_to_sales": D("10"), "price_to_book": D("2"), "fcf_yield": D("0.04")}  # fmt: skip


def test_t12_pe_and_dividend_yield_are_hidden_with_every_ads_reason():
    for cik, o, why in (
        (DBVT, None, a.REASON_TREASURY), (KZIA, None, a.REASON_FOREIGN), (AKTX, None, a.REASON_NO_COUNT),
    ):  # fmt: skip
        d = a.decide(cik, o, conversion_on=True)
        r = a.apply_decision(
            d,
            STORED,
            old_shares=D("420044022"),
            market_cap_fact_ids=set(),
            pe_fact_ids=set(),
        )
        assert r["trailing_pe"] == (None, f"guard:{why}") and r["dividend_yield"] == (
            None,
            f"guard:{why}",
        )
    d = a.decide(
        AMRN, None, conversion_on=False
    )  # conversion OFF: ads_ratio_unverified hides all six
    r = a.apply_decision(
        d,
        STORED,
        old_shares=D("420044022"),
        market_cap_fact_ids=set(),
        pe_fact_ids=set(),
    )
    assert set(r) == set(STORED) and all(
        v[0] is None and v[1] == "guard:ads_ratio_unverified" for v in r.values()
    )


def test_t12_converted_ratios_amrn_pe_per_ads_and_yield_scaled():
    d = convert(AMRN, obs("420044022", date(2026, 6, 30), date(2026, 7, 29)))
    r = a.apply_decision(
        d, STORED, old_shares=D("420044022"), market_cap_fact_ids={1}, pe_fact_ids={9}
    )
    assert abs(r["trailing_pe"][0] - D("-8.2142857")) < D(
        "0.0001"
    )  # card: per-ADS -8.21
    assert r["dividend_yield"][0] == D("0.020")
    assert r["fcf_yield"][0] == D("0.04") / (r["market_cap"][0] / STORED["market_cap"])
    # P/E built from market cap / net income scales with the market cap instead
    r2 = a.apply_decision(
        d, STORED, old_shares=D("420044022"), market_cap_fact_ids={1}, pe_fact_ids={1}
    )
    d2 = a.AdsDecision(
        "convert", None, D(20), D("840088044")
    )  # twice the stored count: f = 2/20
    r3 = a.apply_decision(
        d2, STORED, old_shares=D("420044022"), market_cap_fact_ids={1}, pe_fact_ids={1}
    )
    r4 = a.apply_decision(
        d2, STORED, old_shares=D("420044022"), market_cap_fact_ids={1}, pe_fact_ids={9}
    )
    assert (
        r3["trailing_pe"][0] == STORED["trailing_pe"] / 10
    )  # market-cap path: times f
    assert (
        r4["trailing_pe"][0] == STORED["trailing_pe"] / 20
    )  # EPS path: divided by the ratio


# ------------------------------------------------------------ live hook (fake connection)
class _Cur:
    def __init__(self, c):
        self.c, self.res = c, []

    def __enter__(self):
        return self

    def __exit__(self, *x):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        self.c.sql.append(sql)
        if "co.tag = any" in sql and "core.filing fl" in sql:
            self.res = [self.c.count] if self.c.count else []
        else:
            self.res = []

    def fetchone(self):
        return self.res[0] if self.res else None

    def fetchall(self):
        return self.res


class _Conn:
    def __init__(self, count=None):
        self.count, self.sql = count, []

    def cursor(self):
        return _Cur(self)


NAMES = {
    1: "market_cap",
    2: "trailing_pe",
    3: "price_to_sales",
    4: "price_to_book",
    5: "dividend_yield",
    6: "fcf_yield",
}
MC_ON = {"SCROONER_RULES_ENABLED": g.RULE_MCAP}
ADS_ON = {"SCROONER_RULES_ENABLED": f"{g.RULE_MCAP},{a.RULE_ADS}"}


def rows():
    vals = {
        1: "4830506253",
        2: "-164.2857142857",
        3: "10",
        4: "2",
        5: "0.001",
        6: "0.04",
    }
    return [
        {"company_id": 9, "metric_definition_id": i, "value": D(v), "is_null_reason": None, "source_fact_ids": [100] if i == 1 else [200]}
        for i, v in vals.items()
    ]  # fmt: skip


def by(rs):
    return {NAMES[r["metric_definition_id"]]: r for r in rs}


def test_hook_flags_off_is_untouched():
    c = _Conn()
    rs = rows()
    assert (
        g.apply_price_publish_guards(
            c, 9, AMRN, rs, NAMES, (D("420044022"), [100]), environ={}
        )
        is rs
    )
    assert c.sql == []


@pytest.mark.parametrize("cik", [AMRN, SLN, AKTX, ZLAB, GPCR])
def test_hook_hold_hides_all_six_including_pe_and_yield(cik):
    out = by(
        g.apply_price_publish_guards(
            _Conn(), 9, cik, rows(), NAMES, (D("420044022"), [100]), environ=MC_ON
        )
    )
    assert all(
        r["value"] is None and r["is_null_reason"] == "guard:ads_ratio_unverified"
        for r in out.values()
    )


def test_hook_conversion_on_corrects_amrn_and_keeps_reason_null():
    c = _Conn(count=(D("420044022"), date(2026, 6, 30), date(2026, 7, 29), CO))
    out = by(
        g.apply_price_publish_guards(
            c, 9, AMRN, rows(), NAMES, (D("420044022"), [100]), environ=ADS_ON
        )
    )
    assert (
        out["market_cap"]["value"] == D("4830506253") / 20
        and out["market_cap"]["is_null_reason"] is None
    )
    assert out["dividend_yield"]["value"] == D("0.020")


def test_hook_conversion_on_but_no_count_hides():
    out = by(
        g.apply_price_publish_guards(
            _Conn(), 9, AMRN, rows(), NAMES, (D("420044022"), [100]), environ=ADS_ON
        )
    )
    assert out["market_cap"]["is_null_reason"] == "guard:ads_share_count_unavailable"
    assert out["trailing_pe"]["value"] is None


def test_hook_non_ads_company_untouched_by_ads_flags():
    out = by(
        g.apply_price_publish_guards(
            _Conn(), 9, "0000320193", rows(), NAMES, (D("1000"), [100]), environ=ADS_ON
        )
    )
    assert all(r["value"] is not None for r in out.values())


def test_sln_is_on_the_hold_list_and_in_the_ratio_table():
    assert (
        g.ADS_HOLDS["0001479615"].startswith("SLN")
        and a.ADS_TABLE["0001479615"].ratio == 3
    )
