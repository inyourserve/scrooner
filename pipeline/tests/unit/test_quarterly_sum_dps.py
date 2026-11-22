"""Quarterly-sum DPS step (resolver .91): registry data_points.csv dividends_per_share step 4, the structural loader
reads the resolver's quarterly_sum rows (C, SYK, COF, CRM, AMGN, LLY were 32 loader rejects), and the direct serve sums
the four quarterly facts of exactly the claim's filing. Pure: no database."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import structural_loader as sl
from scrooner_pipeline.metrics import registry

HEAD = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,quote,locator,quote_period,resolver_version\n"
ACC = "0000831001-17-000038"
Q = [("2016-03-31", "0.0500"), ("2016-06-30", "0.0500"), ("2016-09-30", "0.1600"), ("2016-12-31", "0.1600")]


def _nodes(parts):
    return (
        " | why: no annual per-share fact; the sum of the four quarterly CommonStockDividendsPerShareDeclared facts this "
        "filing reports for its fiscal year | node notes: "
        + "; ".join(f"CommonStockDividendsPerShareDeclared[quarter ending {e}]={v} [NOTE]" for e, v in parts)
    )


def _row(parts=Q, value="0.42", pe="2016-12-31"):
    return (
        f'0000831001,C,dividends_per_share,{pe},FY,component_sum,"{_nodes(parts)}",{value},{ACC},own,'
        "calc LiabilitiesAndStockholdersEquity: ok,roles;quarterly_sum;filing_read,,,,resolver-all110-.91\n"
    )


def _claims(tmp_path, *rows):
    (tmp_path / "C.csv").write_text(HEAD + "".join(rows))
    return sl.read_claims(tmp_path)


def test_a_quarterly_sum_row_loads_as_the_maps_statement_with_its_four_parts(tmp_path):
    claims, rejects, counts = _claims(tmp_path, _row())
    assert rejects == []
    (c,) = claims
    assert c.decision == "not_presented" and c.parts == ()
    assert [(e.isoformat(), v) for _t, e, v in c.quarter_parts] == Q
    assert counts["quarterly_sum_loaded_as_not_presented"] == 1


def test_a_quarterly_sum_row_that_does_not_tie_is_refused_alone(tmp_path):
    _c, rejects, _n = _claims(
        tmp_path,
        _row(value="0.43"),  # the parts sum to 0.42
        _row(parts=Q[:3], pe="2015-12-31"),  # three quarters
        _row(parts=[("2015-03-31", "0.05")] + Q[1:], pe="2016-12-31"),  # a quarter of another year
    )
    whys = sorted(r["why"] for r in rejects)
    assert len(whys) == 3
    assert any("sum to 0.42" in w for w in whys)
    assert any("3 quarter parts" in w for w in whys)
    assert any("not the fiscal year" in w for w in whys)


def test_the_step_is_registry_data():
    d = registry.load_data_points()
    assert all(
        "derived:sum(quarterly_dps)" in v.badges for (n, _s), v in d.items() if n == "dividends_per_share" and v.applies
    )
    assert sl.registry_has_quarterly_step("dividends_per_share")
    assert (
        registry.badge_for("dividends_per_share", "general", {"decision": "component_sum", "flags": "roles;quarterly_sum"}, d)
        == "derived:sum(quarterly_dps)"
    )


def test_the_serve_sums_the_filings_own_quarterly_facts(tmp_path):
    claims, _r, _n = _claims(tmp_path, _row())
    c = sd._claims_by_cik.__wrapped__(str(tmp_path))["0000831001"][0]
    assert c.decision == sd.QUARTERLY
    stored = {
        ("CommonStockDividendsPerShareDeclared", date.fromisoformat(e)): {Decimal(v): {i}} for i, (e, v) in enumerate(Q)
    }
    v, ids, ev = sd.quarterly_value(c, stored)
    assert v == Decimal("0.42") and ids == [0, 1, 2, 3] and ev.count(f"@{ACC}") == 4
    stored[("CommonStockDividendsPerShareDeclared", date(2016, 9, 30))] = {Decimal("0.15"): {9}}
    assert "the resolver node 0.1600" in sd.quarterly_value(c, stored)
    stored[("CommonStockDividendsPerShareDeclared", date(2016, 9, 30))] = {Decimal("0.1600"): {2}}
    del stored[("CommonStockDividendsPerShareDeclared", date(2016, 12, 31))]
    assert "no value" in sd.quarterly_value(c, stored)
