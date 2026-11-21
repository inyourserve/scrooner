"""Pure checks for screener exclusion reasons (screener/missing_reasons.py) and the
include_missing query field: every emitted null-reason code lands in a bucket,
the schema rejects include_missing where it has no meaning, and the cache key
tells the two queries apart."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from scrooner_pipeline.common.derivation_policy import (
    PER_SHARE_NOT_CAPTURED_REASON,
    PER_SHARE_NOT_DERIVED_REASON,
)
from scrooner_pipeline.mapper.quick_ratio_evidence import HIDE_REASONS
from scrooner_pipeline.screener import missing_reasons as mr
from scrooner_pipeline.screener.cache_key import canonicalize, compute_query_hash
from scrooner_pipeline.screener.query import build_exclusion_summary
from scrooner_pipeline.screener.schema import ScreenQuery

# Codes the mapper writes to analytics.metric_value.is_null_reason today
# (mapper/ttm.py, price_metrics.py, calculate.py, quick_ratio_evidence.py,
# tax_reconciliation.py, dividend_streak.py, common/derivation_policy.py).
EMITTED = {
    "missing:prior_period(2024_FY)": mr.HISTORY_HORIZON,
    "missing:prior_period(2023_Q2)": mr.HISTORY_HORIZON,
    "zero_base_value": mr.UNDEFINED_BY_MATH,
    "zero_denominator": mr.UNDEFINED_BY_MATH,
    "zero_invested_capital": mr.UNDEFINED_BY_MATH,
    "zero_pretax_income": mr.UNDEFINED_BY_MATH,
    "immaterial_prior_base": mr.UNDEFINED_BY_MATH,
    "negative_ratio_undefined": mr.UNDEFINED_BY_MATH,
    "negative_ratio_undefined_cagr": mr.UNDEFINED_BY_MATH,
    "non_positive_growth_not_meaningful": mr.UNDEFINED_BY_MATH,
    "incomplete:ttm_net_income": mr.NOT_PRESENTED,
    PER_SHARE_NOT_DERIVED_REASON: mr.NOT_PRESENTED,
    "no_dividend_history": mr.NOT_PRESENTED,
    "stale:shares_outstanding": mr.STALE,
    "stale:real_price": mr.STALE,
    "not_in_template": mr.NOT_IN_TEMPLATE,
    # Our own gaps stay visible as gaps, never dressed up as a legitimate blank.
    PER_SHARE_NOT_CAPTURED_REASON: mr.OPEN_GAP,
    "missing:shares_outstanding": mr.OPEN_GAP,
    "missing:real_price": mr.OPEN_GAP,
    "missing:income_tax_expense": mr.OPEN_GAP,
    "invalid:non_positive_price": mr.OPEN_GAP,
    None: mr.OPEN_GAP,
    "": mr.OPEN_GAP,
    "something_new_nobody_mapped": mr.OPEN_GAP,
}


@pytest.mark.unit
@pytest.mark.parametrize("code,expected", list(EMITTED.items()))
def test_every_emitted_code_has_a_bucket(code, expected):
    assert mr.bucket(code) == expected


@pytest.mark.unit
@pytest.mark.parametrize("code", sorted(HIDE_REASONS.values()))
def test_quick_ratio_evidence_reasons_are_not_presented(code):
    assert mr.bucket(code) == mr.NOT_PRESENTED


@pytest.mark.unit
def test_every_bucket_has_a_label_and_a_known_state():
    assert set(mr.BUCKET_LABELS) == set(mr.BUCKETS)
    for code in EMITTED:
        assert mr.bucket(code) in mr.BUCKETS


def _pred(**kw):
    return {"metric_name": "roe", "operator": ">", "value": "0.1", **kw}


@pytest.mark.unit
@pytest.mark.parametrize("op", ["top_n", "bottom_n"])
def test_include_missing_is_rejected_on_ranked_predicates(op):
    with pytest.raises(ValidationError, match="include_missing"):
        ScreenQuery.model_validate(
            {"metric_predicates": [{"metric_name": "roe", "operator": op, "n": 5, "include_missing": True}]}
        )


@pytest.mark.unit
def test_include_missing_is_rejected_anywhere_under_not():
    nested = {"op": "not", "predicates": [{"op": "and", "predicates": [_pred(include_missing=True)]}]}
    with pytest.raises(ValidationError, match="include_missing"):
        ScreenQuery.model_validate({"where": nested})
    # allowed outside `not`
    ScreenQuery.model_validate({"where": {"op": "or", "predicates": [_pred(include_missing=True)]}})


@pytest.mark.unit
def test_cache_hash_differs_with_include_missing_and_is_unchanged_without_it():
    off = ScreenQuery.model_validate({"metric_predicates": [_pred()]})
    on = ScreenQuery.model_validate({"metric_predicates": [_pred(include_missing=True)]})
    assert compute_query_hash(off, 1) != compute_query_hash(on, 1)
    # A query without the field canonicalizes (and so hashes) exactly as before it existed.
    assert "include_missing" not in canonicalize(off)["flat_and"][0]
    assert canonicalize(on)["flat_and"][0]["include_missing"] is True


@pytest.mark.unit
def test_summary_counts_each_company_once_and_refuses_inconsistent_totals():
    excluded = [
        {"missing_metrics": ["a", "b"], "reasons": {"a": {"bucket": "history_horizon"}, "b": {"bucket": "open_gap"}}},
        {"missing_metrics": ["b"], "reasons": {"b": {"bucket": "open_gap"}}},
    ]
    s = build_exclusion_summary(10, 3, excluded)
    assert (s["matched"], s["excluded"], s["not_matched"]) == (3, 2, 5)
    assert s["by_bucket"] == {"history_horizon": 1, "open_gap": 1}
    assert s["by_metric"] == {"a": {"history_horizon": 1}, "b": {"open_gap": 2}}
    with pytest.raises(RuntimeError):
        build_exclusion_summary(3, 3, excluded)
