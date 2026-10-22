"""Pure parts of the RF-10 dry-run (no database)."""

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper import bs_anchor_dryrun as dr
from scrooner_pipeline.mapper.bs_anchor import LatestEffect, latest_effect

D = Decimal
BS, COVER = date(2026, 6, 27), date(2026, 7, 17)


def test_classes():
    fixed = latest_effect(
        [(COVER, None, "incomplete:numerator"), (BS, D("7.36"), None)], {BS}
    )
    assert dr.classify(fixed) == "fixed"
    assert (
        dr.classify(latest_effect([(BS, D("7.36"), None)], {BS})) == "unchanged_valued"
    )
    assert (
        dr.classify(latest_effect([(BS, None, "incomplete:denominator")], {BS}))
        == "unchanged_blank"
    )
    assert (
        dr.classify(
            latest_effect(
                [(COVER, None, "a"), (BS, None, "incomplete:denominator")], {BS}
            )
        )
        == "still_blank_other_reason"
    )
    assert dr.classify(latest_effect([], {BS})) == "no_rows"


def test_regression_class_is_named_so_it_can_be_gated_to_zero():
    regress = LatestEffect(COVER, D("1"), None, BS, None, "incomplete:denominator")
    assert dr.classify(regress) == "valued_now_blank_after"


def test_summary_counts_fixed_cells_and_filing_mixes():
    rows = [
        {
            "company_id": 1,
            "metric": "book_value_per_share",
            "class": "fixed",
            "mixes_filings": False,
            "reason_after": None,
        },
        {
            "company_id": 2,
            "metric": "book_value_per_share",
            "class": "fixed",
            "mixes_filings": True,
            "reason_after": None,
        },
        {
            "company_id": 3,
            "metric": "book_value_per_share",
            "class": "unchanged_blank",
            "mixes_filings": False,
            "reason_after": "incomplete:denominator",
        },
    ]
    s = dr.summarize(rows)["book_value_per_share"]
    assert s["fixed_cells"] == 2 and s["fixed_mixing_filings"] == 1
    assert s["still_blank_reasons_after"] == {"incomplete:denominator": 1}
    assert dr.summarize(rows)["net_cash_per_share"]["fixed_cells"] == 0
