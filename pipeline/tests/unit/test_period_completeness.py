import re
from decimal import Decimal
from pathlib import Path

import pytest

from scrooner_pipeline.sanity.period_completeness import CAUSES, classify


def cause(**overrides):
    args = dict(
        filing_has_facts=True,
        later_filing_has_facts=True,
        authoritative_facts=0,
        conflicting_values=[],
        ytd_facts=0,
        period_kind="Q",
        fy_present=False,
    )
    args.update(overrides)
    return classify(**args)


@pytest.mark.unit
def test_filing_without_facts_is_unprocessed_unless_a_later_filing_was_processed():
    assert cause(filing_has_facts=False, later_filing_has_facts=False) == "filing_not_processed"
    # Cardinal Health: April 10-Q has no facts, the later 10-K does.
    assert cause(filing_has_facts=False, later_filing_has_facts=True) == "not_in_sec_feed"


@pytest.mark.unit
def test_rounding_conflict_is_separated_from_a_material_one():
    # Airbnb FY2025 net income: $2,511,000,000 vs $2,511,277,000.
    airbnb = [Decimal("2511000000"), Decimal("2511277000")]
    assert cause(conflicting_values=airbnb, period_kind="FY") == "conflict_rounding"
    assert cause(conflicting_values=[Decimal("100"), Decimal("150")]) == "conflict_material"


@pytest.mark.unit
def test_authoritative_fact_without_canonical_value_is_not_resolved():
    assert cause(authoritative_facts=1, conflicting_values=[Decimal("5")]) == "not_resolved"


@pytest.mark.unit
def test_derivation_gaps():
    assert cause(period_kind="Q4", fy_present=True) == "q4_not_derived"
    assert cause(period_kind="Q", ytd_facts=2) == "quarter_not_derived"
    assert cause(period_kind="Q4", fy_present=False) == "no_mapped_tag"
    assert cause() == "no_mapped_tag"


@pytest.mark.unit
def test_every_cause_is_allowed_by_the_migration_and_valid_as_a_finding():
    sql = Path(__file__).parents[2].joinpath("db/migrations/0083_period_completeness.sql").read_text()
    allowed = set(re.findall(r"'([a-z0-9_]+)',?\s+--", sql.split("gap_cause text not null check")[1].split(")),")[0]))
    assert set(CAUSES) == allowed
    assert {finding_type for finding_type, _ in CAUSES.values()} <= {
        "pipeline_bug", "filer_error", "legitimate_absence", "data_limit"
    }
    assert len({summary for _, summary in CAUSES.values()}) == len(CAUSES)


@pytest.mark.unit
def test_split_restated_per_share_values_are_not_a_filer_error():
    # Apple FY2019 diluted EPS before and after the 2020 4-for-1 split.
    assert cause(conflicting_values=[Decimal("11.89"), Decimal("2.97")]) == "conflict_split"
    assert cause(conflicting_values=[Decimal("-4.0"), Decimal("-1.0")]) == "conflict_split"
    assert cause(conflicting_values=[Decimal("2.5"), Decimal("1.0")]) == "conflict_material"
    assert cause(conflicting_values=[Decimal("4.0"), Decimal("-1.0")]) == "conflict_material"


@pytest.mark.unit
def test_sec_feed_check_overrides_the_inference():
    # PayPal's July 10-Q: latest filing, no facts, absent from SEC's own feed.
    assert cause(filing_has_facts=False, later_filing_has_facts=False, sec_feed_has_filing=False) == "not_in_sec_feed"
    # In SEC's feed but we have no facts: our miss.
    assert cause(filing_has_facts=False, later_filing_has_facts=True, sec_feed_has_filing=True) == "filing_not_processed"
