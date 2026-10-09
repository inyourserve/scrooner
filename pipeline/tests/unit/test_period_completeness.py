import re
from decimal import Decimal
from pathlib import Path

import pytest

from scrooner_pipeline.sanity.period_completeness import CAUSES, _sec_feed_accessions, classify


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
    # base_concept must be one of SPLIT_AWARE_BASE_CONCEPTS for this
    # classification to even be attempted -- see the 2026-10-05 fix below.
    assert cause(conflicting_values=[Decimal("11.89"), Decimal("2.97")], base_concept="diluted_eps") == "conflict_split"
    assert cause(conflicting_values=[Decimal("-4.0"), Decimal("-1.0")], base_concept="diluted_eps") == "conflict_split"
    assert cause(conflicting_values=[Decimal("2.5"), Decimal("1.0")], base_concept="diluted_eps") == "conflict_material"
    assert cause(conflicting_values=[Decimal("4.0"), Decimal("-1.0")], base_concept="diluted_eps") == "conflict_material"


@pytest.mark.unit
def test_conflict_split_is_scoped_to_split_aware_concepts_only():
    """2026-10-05 fix (doc/planning/51 Finding 4): _is_split_ratio() was being
    applied to every concept's conflicting values, mislabeling real material
    disagreements in non-per-share concepts (total_assets, revenue,
    net_income, etc.) as a harmless "split" whenever the ratio happened to
    look clean. Palatin Technologies' real ~1000x unit-scale typo is the
    motivating real-world case -- it must classify as conflict_material,
    not conflict_split, even though 1000 passes _is_split_ratio()'s own
    whole-number-ratio check."""
    # A clean, whole-number ratio (41x) on a non-per-share concept must NOT
    # be classified as a split -- this is exactly the shape that was wrong.
    assert cause(conflicting_values=[Decimal("41"), Decimal("1")], base_concept="total_assets") == "conflict_material"
    assert cause(conflicting_values=[Decimal("1000"), Decimal("1")], base_concept="net_income") == "conflict_material"
    # No base_concept passed at all (the safe default) must also not
    # classify as a split.
    assert cause(conflicting_values=[Decimal("4.0"), Decimal("1.0")]) == "conflict_material"
    # The legitimate per-share/share-count concepts still classify as a
    # split when the ratio genuinely looks like one.
    assert cause(conflicting_values=[Decimal("4.0"), Decimal("1.0")], base_concept="shares_outstanding") == "conflict_split"
    assert cause(conflicting_values=[Decimal("4.0"), Decimal("1.0")], base_concept="dividends_per_share") == "conflict_split"
    assert cause(conflicting_values=[Decimal("4.0"), Decimal("1.0")], base_concept="basic_eps") == "conflict_split"


@pytest.mark.unit
def test_sec_feed_check_overrides_the_inference():
    # PayPal's July 10-Q: latest filing, no facts, absent from SEC's own feed.
    assert cause(filing_has_facts=False, later_filing_has_facts=False, sec_feed_has_filing=False) == "not_in_sec_feed"
    # In SEC's feed but we have no facts: our miss.
    assert cause(filing_has_facts=False, later_filing_has_facts=True, sec_feed_has_filing=True) == "filing_not_processed"


class _FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class _FakeSECClient:
    """Returns a queued response per call to .get(), in order -- mirrors
    _FEED_PROBE_TAGS' own iteration order (dei:EntityCommonStockSharesOutstanding
    first, then us-gaap:Assets)."""

    def __init__(self, responses):
        self._responses = list(responses)

    def get(self, _url):
        return self._responses.pop(0)


@pytest.mark.unit
def test_sec_feed_accessions_treats_an_all_empty_probe_as_unknown_not_absent():
    """2026-10-09 fix: found live that V. F. Corporation, Monro Inc, and
    Masco Corp -- all real, large, actively-filing companies -- return an
    EMPTY units dict from SEC's own companyconcept endpoint for
    us-gaap:Assets, despite the bulk companyfacts endpoint (and our own
    already-fetched raw.sec_companyfacts blob) having 100+ real Assets
    facts for the same CIK. The old code returned on the FIRST 200
    response even when its own accession set was empty, which single-
    handedly mislabeled every missing period for a company hitting this
    SEC-side quirk as "not_in_sec_feed" (data_limit, "not fixable") when
    the real fix is in our own normalizer, not SEC's data."""
    client = _FakeSECClient(
        [
            _FakeResponse(200, {"units": {"shares": {}}}),
            _FakeResponse(200, {"units": {"USD": {}}}),
        ]
    )
    assert _sec_feed_accessions(client, "0000103379") is None


@pytest.mark.unit
def test_sec_feed_accessions_falls_through_to_the_second_probe_tag():
    """A real-but-empty first probe must not short-circuit the second
    probe tag -- only an all-empty result across every probe is unknown."""
    client = _FakeSECClient(
        [
            _FakeResponse(200, {"units": {"shares": {}}}),
            _FakeResponse(
                200,
                {
                    "units": {
                        "USD": [
                            {"accn": "0000912345-26-000001", "end": "2026-03-31"},
                        ]
                    }
                },
            ),
        ]
    )
    assert _sec_feed_accessions(client, "0000912345") == {"0000912345-26-000001"}


@pytest.mark.unit
def test_sec_feed_accessions_returns_the_first_nonempty_probe_without_a_second_call():
    client = _FakeSECClient(
        [
            _FakeResponse(
                200,
                {
                    "units": {
                        "shares": [
                            {"accn": "0000912345-26-000002", "end": "2026-03-31"},
                        ]
                    }
                },
            ),
        ]
    )
    assert _sec_feed_accessions(client, "0000912345") == {"0000912345-26-000002"}
