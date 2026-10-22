"""Market-cap share-basis guard (RF-15) and reporting-currency guard (RF-19).
Real values (DATA-INFERRED 2026-10-22): RPAY WASO 83,285,379,000 vs cover count 85,881,082;
TBLA WASO 290,505,359,000 vs history near 300M; AKTX 155.76B ordinary shares x ADS price 8.76;
CP and IMO file in CAD."""

from __future__ import annotations

from decimal import Decimal as D

import pytest

from scrooner_pipeline.mapper import price_publish_guards as g

MC = {"SCROONER_RULES_ENABLED": g.RULE_MCAP}
CCY = {"SCROONER_RULES_ENABLED": g.RULE_CCY}
BOTH = {"SCROONER_RULES_ENABLED": f"{g.RULE_MCAP},{g.RULE_CCY}"}


def obs(cover=None, inst=None, wavg=None):
    f = lambda x: None if x is None else D(x)  # noqa: E731
    return g.ShareObservations(f(cover), f(inst), f(wavg))


def test_rpay_waso_x1000_against_the_cover_count_is_hidden():
    r = g.share_basis_reason("0001720592", D("83285379000"), obs(cover="85881082"))
    assert r == "shares_scale_conflict:cover_page"


def test_tbla_waso_x1000_against_its_own_history_is_hidden():
    r = g.share_basis_reason("0001840502", D("290505359000"), obs(wavg="305679079"))
    assert r == "shares_scale_conflict:weighted_median"


def test_aktx_and_other_ads_issuers_are_company_scoped_holds():
    assert (
        g.share_basis_reason("0001541157", D("155758529533"), obs())
        == "ads_ratio_unverified"
    )


@pytest.mark.parametrize(
    ("chosen", "observed"),
    [
        ("15000000000", "14900000000"),
        ("20000000", "1000000"),
        ("1000000", "100000000"),
        ("199000000", "1000000"),
    ],
)
def test_normal_buybacks_splits_and_reverse_splits_are_kept(chosen, observed):
    assert g.share_basis_reason("0000000001", D(chosen), obs(cover=observed)) is None


def test_bound_is_200x_both_directions():
    assert g.ratio_out_of_bounds(D(200), D(1)) and g.ratio_out_of_bounds(D(1), D(200))
    assert not g.ratio_out_of_bounds(D("199.9"), D(1))


def test_no_chosen_share_count_is_not_this_guards_business():
    assert g.share_basis_reason("0000000001", None, obs(cover="1")) is None


def test_reporting_currency_from_units():
    assert g.reporting_currency_from_units(["cad"]) == "CAD"  # CP, IMO
    assert g.reporting_currency_from_units(["cad", "usd"]) == "USD"
    assert g.reporting_currency_from_units([]) == "USD"
    assert g.reporting_currency_from_units(["shares", "item"]) == "USD"


# ---------------------------------------------------------------- live hook
class _Cur:
    def __init__(self, c):
        self.c, self.res = c, []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        self.c.sql.append(sql)
        if sql.startswith("select cik from core.company"):
            self.res = [("0000016875",)]
        elif "from core.shares_outstanding_fallback" in sql:
            self.res = [(D("85881082"),)] if self.c.cover else []
        elif "from core.fact f join core.concept co" in sql and "current_date" in sql:
            self.res = []
        elif "u.unit_name" in sql:
            self.res = [(u,) for u in self.c.units]
        else:
            self.res = []

    def fetchall(self):
        return self.res

    def fetchone(self):
        return self.res[0] if self.res else None


class _Conn:
    def __init__(self, units=("usd",), cover=False):
        self.units, self.cover, self.sql = units, cover, []

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


def rows():
    return [
        {
            "company_id": 9,
            "metric_definition_id": i,
            "value": D(i),
            "is_null_reason": None,
            "source_fact_ids": [100] if i in (1, 2, 3) else [200],
        }
        for i in NAMES
    ]


def by_name(rs):
    return {NAMES[r["metric_definition_id"]]: r for r in rs}


def test_flags_off_touch_nothing_and_query_nothing():
    c = _Conn()
    rs = rows()
    out = g.apply_price_publish_guards(
        c, 9, None, rs, NAMES, (D("1"), [100]), environ={}
    )
    assert out is rs and c.sql == [] and all(r["value"] is not None for r in out)


def test_currency_guard_hides_the_five_ratios_but_keeps_market_cap():
    out = by_name(
        g.apply_price_publish_guards(
            _Conn(units=("cad",)),
            9,
            "0000016875",
            rows(),
            NAMES,
            (D("1"), [100]),
            environ=CCY,
        )
    )
    assert out["market_cap"]["value"] is not None
    expected = [
        "trailing_pe",
        "price_to_sales",
        "price_to_book",
        "dividend_yield",
        "fcf_yield",
    ]
    assert list(g.CURRENCY_HIDDEN) == expected
    for m in expected:
        assert out[m]["value"] is None
        assert out[m]["is_null_reason"] == "guard:non_usd_reporter:CAD"


def test_usd_reporter_untouched_by_currency_guard():
    out = by_name(
        g.apply_price_publish_guards(
            _Conn(units=("usd",)),
            9,
            "0000000001",
            rows(),
            NAMES,
            (D("1"), [100]),
            environ=CCY,
        )
    )
    assert all(r["value"] is not None for r in out.values())


def test_share_basis_guard_hides_market_cap_and_its_dependents_only():
    c = _Conn(cover=True)
    out = by_name(
        g.apply_price_publish_guards(
            c, 9, "0001720592", rows(), NAMES, (D("83285379000"), [100]), environ=MC
        )
    )
    for m in ("market_cap", "price_to_sales", "price_to_book", "fcf_yield"):
        assert out[m]["value"] is None and out[m]["is_null_reason"].startswith(
            "guard:shares_scale_conflict"
        )
    assert (
        out["trailing_pe"]["value"] is None
    )  # computed from market cap (shares fact 100 in its sources)
    assert (
        out["dividend_yield"]["value"] is not None
    )  # DPS / price, not share dependent


def test_pe_from_price_over_eps_is_not_hidden_by_the_share_guard():
    rs = rows()
    rs[1]["source_fact_ids"] = [555]  # price / EPS path: no share fact
    out = by_name(
        g.apply_price_publish_guards(
            _Conn(cover=True),
            9,
            "0001720592",
            rs,
            NAMES,
            (D("83285379000"), [100]),
            environ=MC,
        )
    )
    assert out["trailing_pe"]["value"] is not None
