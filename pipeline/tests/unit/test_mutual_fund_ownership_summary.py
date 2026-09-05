from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.ownership.mutual_fund_summary import (
    _build_summary,
    _match_key,
    _select_comparable_pair,
)


@pytest.mark.unit
def test_select_comparable_pair_prefers_real_quarterly_cohort_over_adjacent_calendar_month():
    """Real finding (checked live 2026-08-29 against AAPL): N-PORT filers
    cluster into 3 essentially disjoint quarterly cohorts by calendar
    month (a Jan/Apr/Jul/Oct cohort, Feb/May/Aug/Nov cohort, Mar/Jun/Sep/
    Dec cohort), each ~90 days apart -- pairing "latest" with "the very
    next older distinct report_period" (Mar-31 here, only 30 days back)
    would be pairing two near-fully-disjoint fund cohorts. The right
    partner for Apr-30 is Jan-31 (89 days back), not Mar-31."""
    periods = [
        (date(2026, 4, 30), 530),
        (date(2026, 3, 31), 1021),  # adjacent month, wrong cohort -- must be skipped
        (date(2026, 2, 28), 342),
        (date(2026, 1, 31), 465),   # real quarter-cohort partner of Apr-30
        (date(2025, 12, 31), 674),
    ]

    result = _select_comparable_pair(periods)

    assert result == (date(2026, 4, 30), date(2026, 1, 31))


@pytest.mark.unit
def test_select_comparable_pair_walks_back_past_still_filling_in_latest_period():
    """Real finding: AAPL's absolute-latest report_period (2026-05-31) had
    exactly 1 matched fund vs. 342 at its own real quarter-cohort partner
    (2026-02-28, 92 days back) -- not a data error, just N-PORT's
    up-to-~60-day filing grace period meaning most of that cohort's May
    filings hadn't landed yet. A 1-vs-342 pairing would be a false
    "everyone exited" artifact, so the still-filling-in latest (May) must
    be skipped in favor of the next cohort down (Apr-30 paired with its
    own real partner Jan-31)."""
    periods = [
        (date(2026, 5, 31), 1),     # real, but still filling in -- must be skipped as "latest"
        (date(2026, 4, 30), 530),
        (date(2026, 3, 31), 1021),
        (date(2026, 2, 28), 342),   # Would-be partner of May-31, but May itself fails completeness
        (date(2026, 1, 31), 465),
    ]

    result = _select_comparable_pair(periods)

    assert result == (date(2026, 4, 30), date(2026, 1, 31))


@pytest.mark.unit
def test_select_comparable_pair_none_when_only_one_period_on_file():
    assert _select_comparable_pair([(date(2026, 4, 30), 530)]) is None


@pytest.mark.unit
def test_select_comparable_pair_none_when_no_gap_falls_in_cadence_band():
    """Two periods a single calendar month apart (30 days, below
    QUARTER_MIN_DAYS) and nothing else on file -- no valid same-cohort
    pair exists yet, must return None rather than force a wrong-cohort
    comparison."""
    periods = [(date(2026, 4, 30), 530), (date(2026, 3, 31), 1021)]

    assert _select_comparable_pair(periods) is None


@pytest.mark.unit
def test_match_key_uses_series_id_when_present():
    """Real finding: fund_cik alone is not a safe grain -- one real
    fund_cik ('0001100663') covers 77 distinct series_id/fund_name values.
    series_id must be part of the key whenever it's resolvable."""
    holding = {"fund_cik": "0000754510", "series_id": "S000007195", "fund_name": "Fidelity Blue Chip Growth Fund"}

    assert _match_key(holding) == "0000754510:S000007195"


@pytest.mark.unit
def test_match_key_falls_back_to_fund_name_without_series_id():
    holding = {"fund_cik": "0000783740", "series_id": None, "fund_name": "MFS SERIES TRUST X"}

    assert _match_key(holding) == "0000783740:name:MFS SERIES TRUST X"


def _holding(fund_cik, series_id, fund_name, shares, value_usd=None, pct_of_fund_net_assets=None):
    return {
        "fund_cik": fund_cik, "series_id": series_id, "fund_name": fund_name,
        "shares": Decimal(shares) if shares is not None else None,
        "value_usd": Decimal(value_usd) if value_usd is not None else None,
        "pct_of_fund_net_assets": Decimal(pct_of_fund_net_assets) if pct_of_fund_net_assets is not None else None,
    }


@pytest.mark.unit
def test_build_summary_classifies_new_increased_decreased_exited():
    latest = [
        _holding("1", "S1", "Fund A", 1000),   # increased vs prior 800
        _holding("2", "S2", "Fund B", 500),    # decreased vs prior 900
        _holding("3", "S3", "Fund C", 300),    # new
    ]
    prior = [
        _holding("1", "S1", "Fund A", 800),
        _holding("2", "S2", "Fund B", 900),
        _holding("4", "S4", "Fund D", 200),    # exited
    ]

    summary = _build_summary(
        company_id=1,
        report_period_latest=date(2026, 4, 30),
        report_period_prior=date(2026, 1, 31),
        latest_holdings=latest,
        prior_holdings=prior,
        shares_out=Decimal(10000),
    )

    assert summary["total_funds_holding"] == 3
    assert summary["funds_increasing"] == 1
    assert summary["funds_decreasing"] == 1
    assert summary["new_positions"] == 1
    assert summary["exited_positions"] == 1
    # (1000 + 500 + 300) / 10000 = 0.18 ; (800 + 900 + 200) / 10000 = 0.19
    assert summary["total_fund_ownership_pct"] == Decimal("0.18")
    assert summary["total_fund_ownership_pct_prior"] == Decimal("0.19")
    assert summary["change_in_pct"] == Decimal("0.18") - Decimal("0.19")


@pytest.mark.unit
def test_build_summary_top_holders_sorted_by_latest_shares_with_exited_backfill():
    """Top 10 is primarily latest-period holders by shares desc; an
    exited fund (no latest position) can still appear if fewer than 10
    real current holders exist, ranked by its own prior-period shares --
    same backfill precedent as institutional_summary.py's own Top 10."""
    latest = [_holding("1", "S1", "Small Fund", 100)]
    prior = [
        _holding("1", "S1", "Small Fund", 50),
        _holding("2", "S2", "Big Exited Fund", 99999),
    ]

    summary = _build_summary(
        company_id=1, report_period_latest=date(2026, 4, 30), report_period_prior=date(2026, 1, 31),
        latest_holdings=latest, prior_holdings=prior, shares_out=Decimal(1000000),
    )

    assert len(summary["top_holders"]) == 2
    assert summary["top_holders"][0]["fund_name"] == "Small Fund"
    assert summary["top_holders"][0]["status"] == "increased"
    assert summary["top_holders"][0]["share_change"] == "50"
    assert summary["top_holders"][1]["fund_name"] == "Big Exited Fund"
    assert summary["top_holders"][1]["status"] == "exited"
    assert summary["top_holders"][1]["shares"] == "0"
    assert summary["top_holders"][1]["share_change"] == "-99999"


@pytest.mark.unit
def test_build_summary_fund_family_always_none_real_gap_not_fabricated():
    """core.fund_ownership never captures the umbrella registrant/trust
    name once a series name is known -- fund_family must be None, never
    guessed from fund_name/fund_cik."""
    latest = [_holding("1", "S1", "Fund A", 100)]

    summary = _build_summary(
        company_id=1, report_period_latest=date(2026, 4, 30), report_period_prior=date(2026, 1, 31),
        latest_holdings=latest, prior_holdings=[], shares_out=Decimal(1000),
    )

    assert summary["top_holders"][0]["fund_family"] is None


@pytest.mark.unit
def test_build_summary_percentages_null_when_shares_outstanding_unresolved():
    """Same "leave null, never guess" discipline as everywhere else --
    no shares_outstanding means no percentage, not a silent 0 or a
    divide-by-zero crash."""
    summary = _build_summary(
        company_id=1, report_period_latest=date(2026, 4, 30), report_period_prior=date(2026, 1, 31),
        latest_holdings=[_holding("1", "S1", "Fund A", 100)], prior_holdings=[], shares_out=None,
    )

    assert summary["total_fund_ownership_pct"] is None
    assert summary["total_fund_ownership_pct_prior"] is None
    assert summary["change_in_pct"] is None
    assert summary["top_holders"][0]["ownership_pct"] is None
