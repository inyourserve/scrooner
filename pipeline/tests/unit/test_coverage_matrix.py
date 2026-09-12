from scrooner_pipeline.mapper.coverage_matrix import REVENUE_FAMILY_CONCEPTS, SIC_GAP_REASONS


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
