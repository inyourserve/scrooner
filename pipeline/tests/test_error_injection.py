"""Error-injection CI gate (certification/inject.py, pipeline/scripts/error_injection.py).

A fixed small injection set (fixtures/error_injection: export rows of a few companies, the planted errors and the
recorded fsn evidence bundle, no database) is replayed through every certification check. The gate fails when any
error class's recall drops below baseline.json, the recall measured when the fixture was recorded
(data-team/strategy/certification/error-injection-<date>.md has the full-population run).
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import random
from decimal import Decimal

import pytest
from scrooner_pipeline.certification import inject as ij

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIX = pathlib.Path(__file__).parent / "fixtures" / "error_injection"
spec = importlib.util.spec_from_file_location(
    "error_injection", ROOT / "pipeline/scripts/error_injection.py"
)
ei = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ei)


@pytest.fixture(scope="module")
def replayed():
    return ei.replay(FIX, log=lambda s: None)


def test_recall_per_class_not_below_baseline(replayed):
    sc, _ = replayed
    baseline = json.loads((FIX / "baseline.json").read_text())
    assert set(baseline) == {c for c in ij.CLASSES if sc["classes"][c]["planted"]}
    low = {
        cls: (sc["classes"][cls]["recall"], floor)
        for cls, floor in baseline.items()
        if sc["classes"][cls]["recall"] + 1e-9 < floor
    }
    assert not low, f"recall below the measured baseline (got, baseline): {low}"


def test_fixture_plants_every_class(replayed):
    sc, _ = replayed
    assert all(sc["classes"][c]["planted"] >= 1 for c in ij.CLASSES), {
        c: sc["classes"][c]["planted"] for c in ij.CLASSES
    }


def test_untouched_controls_get_no_new_flag(replayed):
    sc, _ = replayed
    assert sc["controls"]["cells"] > 0
    assert sc["controls"]["spillover"] == 0


def test_replayed_injections_change_their_cells():
    _, rows = ij.read_rows(FIX / "export.csv.gz")
    base = ij.by_company(rows)
    injections = ij.read_injections(FIX / "injections.csv")
    mut = ij.apply_injections(base, injections)
    for i in injections:
        before = next(r for r in base[i.ticker] if ij.key(r) == i.key)
        after = next(r for r in mut[i.ticker] if ij.key(r) == i.key)
        assert before != after, i
    # a fixture whose export drifted from the planted cell's before-image is refused, never silently replayed
    i = injections[0]
    bad = [
        ij.Injection(
            i.cls,
            i.ticker,
            i.data_point,
            i.fiscal_year,
            json.dumps({"display": "NOPE"}),
            i.after,
        )
    ]
    with pytest.raises(ValueError):
        ij.apply_injections(base, bad)


# ---------------------------------------------------------------- planting is pure and keeps each cell self-consistent
def _row(**kw):
    r = dict(
        rank="1",
        ticker="T",
        company_id="1",
        data_point="total_debt",
        fiscal_year="2020",
        period_end="2020-12-31",
        display="SHOWN_VALUE",
        shown_value="300",
        tag="A,B",
        accession="0000000001-21-000001",
        r_page="R4.htm",
        parts="A=100@0000000001-21-000001#R4;B=200@0000000001-21-000001#R4",
        hide_class="",
        reason_code="",
        reason="",
        evidence="",
        badge="derived:sum(printed debt lines)+finance_leases",
        sector="general",
    )
    r.update(kw)
    r["class"] = "PROVEN"
    return r


def _parts_sum(r):
    return ij.signed_sum(ij.split_parts(r["parts"]))


@pytest.mark.parametrize(
    "cls", ["scale_x1000", "scale_x1e6", "sign_flip", "dropped_component"]
)
def test_value_classes_keep_parts_adding_up(cls):
    p = ij.Planter({"T": [_row()]}, "s")
    assert p.plant(cls, 1) == 1
    r = p.mut["T"][0]
    assert Decimal(r["shown_value"]) == _parts_sum(r) != Decimal(300)
    assert p.base["T"][0]["shown_value"] == "300"  # the input rows are never mutated


def test_derived_two_filings_cites_a_later_filing():
    rows = [
        _row(),
        _row(
            fiscal_year="2021",
            period_end="2021-12-31",
            accession="0000000001-22-000001",
        ),
    ]
    p = ij.Planter({"T": rows}, "s")
    p.rng = random.Random(0)
    assert p.plant("derived_two_filings", 1) == 1
    r = p.mut["T"][0]
    assert {x["acc"] for x in ij.split_parts(r["parts"])} == {
        "0000000001-21-000001",
        "0000000001-22-000001",
    }
    assert r["shown_value"] == "300"


def test_fact_swap_classes_need_a_filing_read():
    p = ij.Planter(
        {
            "T": [
                _row(
                    data_point="cash_and_equivalents",
                    parts="",
                    tag="CashAndCashEquivalentsAtCarryingValue",
                )
            ]
        },
        "s",
    )
    assert p.plant("restricted_cash_total", 1) == 0  # no facts_for: nothing is invented
