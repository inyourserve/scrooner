"""Derived-not-printed cells (mapper/derived_cells.py): gross profit (C1) and total liabilities (C2)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper.derived_cells import LABEL, derive as _derive

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


def derive(cells, st, ci, periods, proven, ops):
    """Operands are printed in filing ACC (the one-filing rule needs the accession of every input)."""
    return _derive(
        cells, st, ci, periods, proven, {}, {k: {ACC: v} for k, v in ops.items()}
    )


ACC = "0000000000-20-000001"


def cell(cid, pid, v, acc=ACC):
    return {
        "canonical_concept_id": cid,
        "period_id": pid,
        "value": Decimal(v * M),
        "_accession": acc,
    }


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


def test_inputs_from_different_filings_are_never_combined_mpc_fy2018():
    """MPC FY2018: revenue 96,504 (FY2019 10-K) - cost of revenue 77,047 (FY2020 10-K) = 19,457 was served; the one
    filing's own figure is 11,048. Inputs of two filings: not derived. Same filing: derived."""
    rev, cor = 96_504, 77_047
    proven = {
        ("revenue", "FY", FYS, FYE): {Decimal(rev * M)},
        ("cost_of_revenue", "FY", FYS, FYE): {Decimal(cor * M)},
    }
    mixed = [cell(1, 10, rev, "FY2019-10K"), cell(2, 10, cor, "FY2020-10K")]
    assert derive(mixed, stats(blank(3, 10, "FY")), CI, PERIODS, proven, {}) == []
    one = [cell(1, 10, rev, "FY2019-10K"), cell(2, 10, cor, "FY2019-10K")]
    out = derive(one, stats(blank(3, 10, "FY")), CI, PERIODS, proven, {})
    assert [o["value"] for o in out] == [Decimal((rev - cor) * M)]


def test_c2_assets_equity_and_operands_from_one_filing():
    cells = [cell(4, 11, 201, "A1"), cell(5, 11, 81, "A2")]
    st = stats(blank(6, 11, "I"))
    ops = {(LSE, 11): {"A1": Decimal(201 * M), "A2": Decimal(201 * M)}}
    assert _derive(cells, st, CI, PERIODS, proven_bs(), {}, ops) == []
    cells = [cell(4, 11, 201, "A1"), cell(5, 11, 81, "A1")]
    # the L&SE is printed only in another filing
    assert (
        _derive(
            cells,
            st,
            CI,
            PERIODS,
            proven_bs(),
            {},
            {(LSE, 11): {"A2": Decimal(201 * M)}},
        )
        == []
    )
    assert len(_derive(cells, st, CI, PERIODS, proven_bs(), {}, ops)) == 1


def test_c2_gild_fy2015_assets_and_equity_cells_recorded_in_two_filings_one_prints_both():
    """GILD FY2015 (ruling 2026-11-21 item 14): total_assets 201 is served from the FY2016 10-K (A2), stockholders
    equity 81 from the FY2015 10-K (A1). The FY2016 10-K also prints the same equity and the L&SE, so every input is
    printed in ONE filing: derived (not hidden as structural_not_presented)."""
    cells = [cell(4, 11, 201, "A2"), cell(5, 11, 81, "A1")]

    def st():
        return stats(blank(6, 11, "I"))

    ops = {
        ("Assets", 11): {"A2": Decimal(201 * M)},
        ("StockholdersEquity", 11): {"A1": Decimal(81 * M), "A2": Decimal(81 * M)},
        (LSE, 11): {"A2": Decimal(201 * M)},
    }
    out = _derive(cells, st(), CI, PERIODS, proven_bs(), {}, ops)
    assert [o["value"] for o in out] == [Decimal(120 * M)]
    ops_bad = {**ops, ("StockholdersEquity", 11): {"A1": Decimal(81 * M), "A2": Decimal(70 * M)}}
    assert _derive(cells, st(), CI, PERIODS, proven_bs(), {}, ops_bad) == []
    # no other filing prints the equity: the two cells' filings stay separate, never combined
    ops_one = {**ops, ("StockholdersEquity", 11): {"A1": Decimal(81 * M)}}
    assert _derive(cells, st(), CI, PERIODS, proven_bs(), {}, ops_one) == []
