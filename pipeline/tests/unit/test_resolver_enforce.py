"""A served value must equal its resolver node's value (Dhairya 2026-11-21). The STX dividends_per_share FY2022 and MRVL
total_debt shapes: the resolver held the right value, the serving path took another stored copy. Pure (no DB); the
DB-backed recording of the claim value lives in test_structural_direct.py. Each assertion is mutation-checked."""

from __future__ import annotations

import inspect
from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper import company_tag_map as ctm
from scrooner_pipeline.mapper import structural_direct as sd

PERIODS = {11: (date(2021, 7, 3), date(2022, 7, 1), "duration")}
DPS, DEBT = 7, 8


def _rv(cid, value, acc="0001137789-22-000055", concept="dividends_per_share"):
    return {
        "canonical_concept_id": cid,
        "period_id": 11,
        "value": Decimal(value),
        "accession": acc,
        "concept": concept,
    }


def _cell(cid, value, acc="0001137789-22-099999"):
    return {
        "canonical_concept_id": cid,
        "period_id": 11,
        "value": Decimal(value),
        "_accession": acc,
    }


def test_a_stored_copy_that_differs_from_the_resolver_is_held_with_an_evidenced_blank():
    cells = [_cell(DPS, "2770000")]
    stats = {"held": [], "blanks": []}
    held = sd.enforce_resolver(
        cells, stats, [_rv(DPS, "2.77")], PERIODS, ctm._grain, "r@1"
    )
    assert cells == [] and len(held) == 1
    assert stats["held"] == [
        {
            "canonical_concept_id": DPS,
            "period_id": 11,
            "reason": sd.DIFFERS_FROM_RESOLVER,
        }
    ]
    (b,) = stats["blanks"]
    assert b["reason_code"] == sd.DIFFERS_FROM_RESOLVER and b["state"] == "defect"
    assert (
        "2770000" in b["reason"]
        and "2.77" in b["reason"]
        and "0001137789-22-000055" in b["reason"]
    )
    assert stats["resolver_held"][0]["resolver"] == Decimal("2.77")


def test_an_equal_value_and_an_unclaimed_key_are_served_unchanged():
    cells = [_cell(DPS, "2.7700"), _cell(DEBT, "1000")]
    stats = {"held": [], "blanks": []}
    assert (
        sd.enforce_resolver(
            cells, stats, [_rv(DPS, "2.77")], PERIODS, ctm._grain, "r@1"
        )
        == []
    )
    assert [c["canonical_concept_id"] for c in cells] == [DPS, DEBT]
    assert stats["held"] == [] and stats["blanks"] == []


def test_the_held_key_replaces_an_older_blank_of_that_key():
    cells = [_cell(DEBT, "300", acc="0001835632-22-000010")]
    stats = {
        "held": [],
        "blanks": [
            {"canonical_concept_id": DEBT, "period_id": 11, "reason_code": "old"}
        ],
    }
    sd.enforce_resolver(
        cells,
        stats,
        [_rv(DEBT, "4547977000", concept="total_debt")],
        PERIODS,
        ctm._grain,
        "r@1",
    )
    assert [b["reason_code"] for b in stats["blanks"]] == [sd.DIFFERS_FROM_RESOLVER]


def test_claim_value_reads_the_resolver_value_or_none():
    assert sd._claim_value(type("C", (), {"value": "4,547,977"})()) == Decimal(4547977)
    assert sd._claim_value(type("C", (), {"value": ""})()) is None
    assert sd._claim_value(type("C", (), {"value": "n/a"})()) is None


def test_resolve_for_company_enforces_after_every_cell_producing_step():
    """The check runs after the derived steps, so no later step can refill a held key with another value."""
    src = inspect.getsource(ctm.resolve_for_company)
    at = src.index("sd.enforce_resolver(")
    assert src.index("sd.apply_direct(") < at
    assert src.index("add_derived_cells(conn") < at
    assert src.index("add_derived_quarters(cells") < at


def test_a_coarser_reporting_scale_agrees_and_a_wrong_value_does_not():
    assert sd.agrees(
        Decimal(241500000), Decimal(241539000)
    )  # MRVL sbc: millions, one decimal
    assert sd.agrees(Decimal(241539000), Decimal(241500000))
    assert sd.agrees(Decimal(2600000), Decimal(2599000))
    assert not sd.agrees(Decimal(2770000), Decimal("2.77"))  # STX dps scale error
    assert not sd.agrees(
        Decimal(300000000), Decimal(4547977000)
    )  # short-term part, not total debt
    assert not sd.agrees(Decimal(241600000), Decimal(241539000))
    assert not sd.agrees(Decimal(1000000000), Decimal(1400000000))
    assert not sd.agrees(
        Decimal(3000000), Decimal(2600000)
    )  # one significant digit proves nothing


def test_a_later_filing_restatement_stays_and_a_later_scale_error_is_held():
    """Authority v2: the resolver read the FY2022 10-K (filed 2022-08-05); a copy from a 2023 filing is its restated
    column and stays served (listed); the same later copy off by 10^6 is no restatement and is held."""
    rv = {**_rv(DPS, "2.77"), "filed": date(2022, 8, 5)}
    filed = {
        "0001137789-23-000001": date(2023, 8, 4),
        "0001137789-21-000001": date(2021, 8, 4),
    }
    cells = [_cell(DPS, "2.70", acc="0001137789-23-000001")]
    stats = {"held": [], "blanks": []}
    sd.enforce_resolver(cells, stats, [rv], PERIODS, ctm._grain, "r@1", filed)
    assert len(cells) == 1 and stats["held"] == []
    assert (
        stats["resolver_kept_restated"][0]["served_accession"] == "0001137789-23-000001"
    )
    for v, acc in (
        ("2770000", "0001137789-23-000001"),
        ("2.70", "0001137789-21-000001"),
    ):
        cells, stats = [_cell(DPS, v, acc=acc)], {"held": [], "blanks": []}
        sd.enforce_resolver(cells, stats, [rv], PERIODS, ctm._grain, "r@1", filed)
        assert cells == [] and stats["resolver_kept_restated"] == []


def test_shape_names_scale_sign_and_zero():
    assert sd.shape(Decimal(2770000), Decimal("2.77")) == "scale"
    assert sd.shape(Decimal(-51), Decimal(51)) == "sign"
    assert sd.shape(Decimal(0), Decimal(5)) == "zero_vs_value"
    assert sd.shape(Decimal(90), Decimal(100)) == "other"
