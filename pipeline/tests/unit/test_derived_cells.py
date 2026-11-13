"""Derived-not-printed cells (mapper/derived_cells.py): gross profit (C1) and total liabilities (C2)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper.derived_cells import LABEL, derive

M = 1_000_000
FYS, FYE = date(2023, 1, 1), date(2023, 12, 31)
CI = {
    1: ("revenue_sanity_resolved", "income_statement"),
    2: ("cost_of_revenue_resolved", "income_statement"),
    3: ("gross_profit", "income_statement"),
    4: ("total_assets_resolved", "balance_sheet"),
    5: ("stockholders_equity_resolved", "balance_sheet"),
    6: ("total_liabilities", "balance_sheet"),
}
PERIODS = {10: (FYS, FYE, "duration"), 11: (FYE, FYE, "instant")}


def cell(cid, pid, v):
    return {"canonical_concept_id": cid, "period_id": pid, "value": Decimal(v * M)}


def blank(cid, pid, grain, state="not_presented"):
    return {
        "canonical_concept_id": cid,
        "concept_name": CI[cid][0],
        "period_id": pid,
        "state": state,
        "grain": grain,
    }


def stats(*blanks, held=()):
    return {"blanks": list(blanks), "held": list(held)}


def proven_is(rev=True, cor=True):
    p = {}
    if rev:
        p[("revenue", "FY", FYS, FYE)] = {Decimal(101 * M)}
    if cor:
        p[("cost_of_revenue", "FY", FYS, FYE)] = {Decimal(41 * M)}
    return p


def test_c1_gross_profit_derived_when_not_printed_and_both_proven():
    out = derive(
        [cell(1, 10, 101), cell(2, 10, 41)],
        stats(blank(3, 10, "FY")),
        CI,
        PERIODS,
        proven_is(),
        {},
    )
    assert len(out) == 1
    c = out[0]
    assert c["value"] == Decimal(60 * M) and c["canonical_concept_id"] == 3
    assert c["value_source"] == LABEL == "derived_not_printed"
    assert c["source_fact_ids"] == [] and c["source_value_ids"] == []
    assert LABEL in c["serve_note"]


def test_c1_never_derived_without_proof_template_or_operand():
    cells = [cell(1, 10, 101), cell(2, 10, 41)]
    for kw in (
        dict(proven=proven_is(cor=False)),  # cost of revenue not PROVEN
        dict(proven=proven_is(rev=False)),
        dict(
            proven={
                ("revenue", "FY", FYS, FYE): {Decimal(5 * M)},
                **proven_is(rev=False),
            }
        ),  # judged another value
    ):
        assert (
            derive(cells, stats(blank(3, 10, "FY")), CI, PERIODS, kw["proven"], {})
            == []
        )
    # the template leaves gross profit out (not_in_template): never derived
    assert (
        derive(
            cells,
            stats(blank(3, 10, "FY", "not_in_template")),
            CI,
            PERIODS,
            proven_is(),
            {},
        )
        == []
    )
    # a missing operand cell
    assert (
        derive(cells[:1], stats(blank(3, 10, "FY")), CI, PERIODS, proven_is(), {}) == []
    )
    # held by the mapper
    held = [{"canonical_concept_id": 3, "period_id": 10}]
    assert (
        derive(
            cells, stats(blank(3, 10, "FY"), held=held), CI, PERIODS, proven_is(), {}
        )
        == []
    )
    # already served
    assert (
        derive(
            cells + [cell(3, 10, 60)],
            stats(blank(3, 10, "FY")),
            CI,
            PERIODS,
            proven_is(),
            {},
        )
        == []
    )


LSE = "LiabilitiesAndStockholdersEquity"


def proven_bs():
    return {
        ("total_assets", "I", FYE, FYE): {Decimal(201 * M)},
        ("stockholders_equity", "I", FYE, FYE): {Decimal(81 * M)},
    }


def test_c2_total_liabilities_is_lse_minus_equity_and_mezzanine():
    cells = [cell(4, 11, 201), cell(5, 11, 81)]
    ops = {
        (LSE, 11): Decimal(201 * M),
        ("MinorityInterest", 11): Decimal(4 * M),
        ("RedeemableNoncontrollingInterestEquityCarryingAmount", 11): Decimal(6 * M),
    }
    out = derive(cells, stats(blank(6, 11, "I")), CI, PERIODS, proven_bs(), ops)
    assert len(out) == 1
    # 201 - (81 + 4) - 6
    assert out[0]["value"] == Decimal(110 * M)
    assert out[0]["value_source"] == LABEL
    # equity including NCI printed: used as the equity, the NCI is not added again
    ops2 = {
        **ops,
        (
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            11,
        ): Decimal(85 * M),
    }
    out = derive(cells, stats(blank(6, 11, "I")), CI, PERIODS, proven_bs(), ops2)
    assert out[0]["value"] == Decimal(110 * M)


def test_c2_never_derived_when_an_operand_is_missing_or_unproven():
    cells = [cell(4, 11, 201), cell(5, 11, 81)]
    ops = {(LSE, 11): Decimal(201 * M)}
    st = lambda: stats(blank(6, 11, "I"))  # noqa: E731
    assert derive(cells, st(), CI, PERIODS, proven_bs(), {}) == []  # no printed L&SE
    assert (
        derive(cells[:1], st(), CI, PERIODS, proven_bs(), ops) == []
    )  # no equity cell
    assert derive(cells, st(), CI, PERIODS, {}, ops) == []  # nothing PROVEN
    # the printed L&SE does not equal the proven assets
    assert (
        derive(cells, st(), CI, PERIODS, proven_bs(), {(LSE, 11): Decimal(260 * M)})
        == []
    )
    assert len(derive(cells, st(), CI, PERIODS, proven_bs(), ops)) == 1
