"""2026-10-02 -- four real, live-verified parsing gaps found running
doc/create-screen/scrooner-natural-language-screening-flow.md's own
worked example against the real parser: "Show US technology companies
with a market cap above $10 billion and a P/E ratio below 25" came back
entirely unrecognized. Isolating each clause live traced it to four
independent, narrow causes, each fixed separately and locked in here so
a future refactor can't silently regress any one of them:

1. "p/e ratio" (and the p/b/p/s/d/e siblings) had the bare abbreviation
   aliased but not the "... ratio"-suffixed form (aliases.py).
2. A leading article ("a market cap above $10 billion") wasn't stripped
   before metric lookup -- _strip_filler only ran its prefix list once,
   not repeatedly, so "with a market cap" stripped "with " but never got
   a second pass to also strip "a ".
3. "{sector} companies with {metric clause}" (no literal "and"/"or")
   was entirely unrecognized -- a single clause can only carry one of a
   metric OR a categorical predicate, never both, so "software companies
   with ROE above 30%" had no way to become two AND'd clauses the way
   "software companies and ROE above 30%" already does.
4. A leading imperative ("Show ...", "Find ...") and a redundant "US"
   qualifier in front of a sector name were never stripped.

See doc/learnings/2026-10-02-natural-language-screening-gaps.md for the
full investigation."""

import pytest

from scrooner_pipeline.ai_query.interpreter import AmbiguityNote
from scrooner_pipeline.ai_query.rules import interpret


@pytest.mark.unit
@pytest.mark.parametrize(
    "text",
    [
        "Show US technology companies with a market cap above $10 billion and a P/E ratio below 25",
        "software companies with ROE above 30%",
        "a P/E ratio below 25",
        "a market cap above $10 billion",
        "show me software companies with roic above 15%",
        "find banks with p/b ratio below 1",
        "list companies with p/s ratio below 2",
        "US technology companies with roe above 20%",
    ],
)
def test_previously_unrecognized_natural_phrasing_now_parses(text):
    result = interpret(text)
    assert result.query is not None, f"{text!r} unrecognized: {result.unrecognized}"
    assert not result.unrecognized
    assert not result.ambiguous


@pytest.mark.unit
def test_doc_example_produces_exactly_the_three_intended_predicates():
    from decimal import Decimal

    from scrooner_pipeline.screener.schema import CategoricalPredicate, MetricPredicate

    result = interpret(
        "Show US technology companies with a market cap above $10 billion "
        "and a P/E ratio below 25"
    )
    query = result.query
    assert query.categorical_predicates == [
        CategoricalPredicate(field="sector", operator="=", value="Technology")
    ]
    assert query.metric_predicates == [
        MetricPredicate(metric_name="market_cap", operator=">", value=Decimal(10_000_000_000)),
        MetricPredicate(metric_name="trailing_pe", operator="<", value=Decimal(25)),
    ]


@pytest.mark.unit
def test_literal_pe_below_is_never_silently_guarded_against_losses():
    # Deliberate: this project never silently reinterprets a query (doc
    # 02/03's explainability/safety release gate). "P/E below 25" means
    # exactly that -- a negative P/E (a loss-making company) IS
    # numerically below 25 and would correctly match it. Excluding
    # loss-makers is the user's call to make explicit (e.g. "P/E between
    # 0 and 25"), never something this parser silently adds on its own.
    # The guarantee this locks in: exactly one predicate, nothing extra.
    result = interpret("P/E ratio below 25")
    assert len(result.query.metric_predicates) == 1
    only = result.query.metric_predicates[0]
    assert only.metric_name == "trailing_pe"
    assert only.operator == "<"


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected_metric",
    [
        ("p/e ratio", "trailing_pe"),
        ("p/b ratio", "price_to_book"),
        ("p/s ratio", "price_to_sales"),
        ("d/e ratio", "debt_to_equity"),
    ],
)
def test_ratio_suffixed_abbreviations_now_aliased(text, expected_metric):
    from scrooner_pipeline.ai_query.aliases import METRIC_ALIASES

    assert METRIC_ALIASES[text] == expected_metric


@pytest.mark.unit
@pytest.mark.parametrize(
    "text",
    [
        "roe above 30% and debt to equity below 0.5",
        "companies with ROE above 30%",
        "top 5 by roic",
        "software companies",
        "roe above 30% or debt to equity below 0.5",
    ],
)
def test_existing_working_phrasings_unaffected(text):
    # Regression guard for the four widenings above -- none of them may
    # change behavior for phrasing that already worked.
    result = interpret(text)
    assert result.query is not None
    assert not result.unrecognized


# --- Auto-suggest for a near-miss typo on a known metric phrase (2026-10-02) ---


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected_candidate",
    [
        ("markt cap above $10 billion", "market_cap"),
        ("p/e rtio below 25", "trailing_pe"),
        ("retrun on equty above 20%", "roe"),
    ],
)
def test_near_miss_typo_is_offered_as_a_clickable_suggestion_not_silently_fixed(
    text, expected_candidate
):
    result = interpret(text)
    # Never silently corrected -- no confident query from a typo alone.
    assert result.query is None
    assert len(result.ambiguous) == 1
    assert expected_candidate in result.ambiguous[0].candidates


@pytest.mark.unit
def test_unrelated_gibberish_gets_no_false_positive_suggestion():
    result = interpret("xyzzy quux above 5")
    assert result.query is None
    assert result.ambiguous == []
    assert result.unrecognized == ["xyzzy quux above 5"]


@pytest.mark.unit
def test_curated_ambiguous_phrase_still_wins_over_the_fuzzy_fallback():
    # "revenue growth" is a deliberately curated ambiguity (YoY vs. 3Y
    # CAGR) -- it must resolve via AMBIGUOUS_METRIC_PHRASES exactly as
    # before, never be re-routed through the new fuzzy fallback.
    result = interpret("revenue growth above 10%")
    assert result.ambiguous == [
        AmbiguityNote("revenue growth", ["revenue_growth_yoy", "revenue_growth_3y_cagr"])
    ]
