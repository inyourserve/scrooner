from scrooner_pipeline.mapper.coverage_matrix import (
    BDC_FAMILY_DATA_POINTS,
    BUYBACK_FAMILY_DATA_POINTS,
    CAPITAL_RETURN_FAMILY_DATA_POINTS,
    DIVIDEND_FAMILY_DATA_POINTS,
    POPULATION_QUERIES,
    REVENUE_FAMILY_CONCEPTS,
    SIC_GAP_REASONS,
)


def test_revenue_family_concepts_includes_resolved_and_raw_pairs() -> None:
    # Every raw revenue-statement concept should have its resolved
    # companion covered too -- classify_concept_gaps() is applied to
    # both, and a company missing the raw tag is missing the resolved
    # one for the same structural reason. `revenue` is the one
    # exception to the `<name>_resolved` naming convention -- its
    # resolved concept is `revenue_sanity_resolved` (built by
    # sanity/tag_investigator.py, named for what it fixes, not a
    # simple suffix rule).
    resolved_names = {
        "revenue": "revenue_sanity_resolved",
        "cost_of_revenue": "cost_of_revenue_resolved",
        "gross_profit": "gross_profit_resolved",
        "operating_income": "operating_income_resolved",
        "operating_expenses": "operating_expenses_resolved",
    }
    for raw, resolved in resolved_names.items():
        assert raw in REVENUE_FAMILY_CONCEPTS
        assert resolved in REVENUE_FAMILY_CONCEPTS


def test_sic_gap_reasons_cover_every_verified_bucket() -> None:
    # Found live 2026-09-11 investigating the real revenue coverage gap --
    # each of these was spot-checked against real companies, not assumed
    # from the SIC label alone (see coverage_matrix.py's own comment).
    expected_sics = {
        "Blank Checks",
        "Pharmaceutical Preparations",
        "Biological Products, (No Diagnostic Substances)",
        "Commodity Contracts Brokers & Dealers",
        "Asset-Backed Securities",
        "Real Estate Investment Trusts",
        "State Commercial Banks",
        "National Commercial Banks",
        "Savings Institution, Federally Chartered",
        "Metal Mining",
        "Gold and Silver Ores",
    }
    assert set(SIC_GAP_REASONS.keys()) == expected_sics
    # Every reason is a non-empty, snake_case-ish string -- not blank,
    # not accidentally duplicated across unrelated SICs in a way that
    # would hide a real distinction (banks and REITs deliberately get
    # different reasons even though both are "not GAAP revenue").
    assert len(set(SIC_GAP_REASONS.values())) >= 5
    for reason in SIC_GAP_REASONS.values():
        assert reason and reason == reason.lower()


def test_population_queries_cover_every_named_population_a_data_point_can_reference() -> None:
    # capital_return_company is deliberately NOT in POPULATION_QUERIES --
    # classify_company_populations() builds it as a union of
    # dividend_payer/buyback_company instead of its own query (see that
    # function's own comment) -- so every OTHER family's target
    # population must have a real query to build it from.
    referenced_populations = {"real_operating_company", "dividend_payer", "buyback_company", "bdc_company"}
    assert referenced_populations <= set(POPULATION_QUERIES.keys())


def test_family_data_point_lists_are_disjoint() -> None:
    # Each data point gets exactly one applicable_population override in
    # build_registry() -- a name appearing in two families would mean
    # whichever dict-population wins last silently shadows the other,
    # not a deliberate choice.
    all_families = [
        DIVIDEND_FAMILY_DATA_POINTS,
        BUYBACK_FAMILY_DATA_POINTS,
        CAPITAL_RETURN_FAMILY_DATA_POINTS,
        BDC_FAMILY_DATA_POINTS,
    ]
    seen: set[str] = set()
    for family in all_families:
        overlap = seen & set(family)
        assert not overlap, f"data point(s) {overlap} appear in more than one population family"
        seen |= set(family)
