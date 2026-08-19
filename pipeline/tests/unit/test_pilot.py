from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from scrooner_pipeline.pilot import (
    DEFAULT_DATABASE_LIMIT_BYTES,
    PilotCandidate,
    PilotInventory,
    classify_failure,
    evaluate_readiness,
    issuer_kind,
    market_cap_band,
    mapped_tag_presence,
    sector_group,
    select_stratified_sample,
)


pytestmark = pytest.mark.unit


def candidate(index: int, **overrides) -> PilotCandidate:
    values = {
        "cik": str(index).zfill(10),
        "sector": "manufacturing",
        "market_cap_band": "mid",
        "fiscal_calendar": "calendar",
        "filing_regime": "domestic_reporting_company",
        "issuer_kind": "general",
        "multi_class": False,
        "has_amendment": False,
    }
    values.update(overrides)
    return PilotCandidate(**values)


def healthy_inventory() -> PilotInventory:
    return PilotInventory(
        universe_schema_present=True,
        eligible_primary_count=150,
        raw_companyfacts_ciks=150,
        raw_submissions_ciks=150,
        normalized_company_count=10,
        unresolved_normalizer_errors=0,
        unresolved_mapper_errors=0,
        database_size_bytes=100_000_000,
        scalable_table_bytes=10_000_000,
        mapping_coverage=Decimal("0.97"),
    )


def test_sample_is_exact_deduplicated_and_input_order_independent() -> None:
    rows = [candidate(index) for index in range(120)]
    first = select_stratified_sample(rows, 100)
    second = select_stratified_sample(reversed(rows), 100)
    assert first == second
    assert len(first) == 100
    assert len({row.cik for row in first}) == 100


def test_sample_covers_rare_strata_before_filling() -> None:
    rows = [candidate(index) for index in range(110)]
    rows[109] = candidate(
        109,
        sector="finance_insurance_real_estate",
        market_cap_band="micro",
        issuer_kind="bank",
        multi_class=True,
        has_amendment=True,
    )
    selected = select_stratified_sample(rows, 10)
    assert rows[109] in selected


def test_sample_rejects_insufficient_distinct_companies() -> None:
    with pytest.raises(ValueError, match="need 100"):
        select_stratified_sample([candidate(index) for index in range(99)], 100)


def test_readiness_passes_only_when_every_gate_passes() -> None:
    result = evaluate_readiness(healthy_inventory(), target=100)
    assert result.ready
    assert result.blockers == ()


def test_readiness_reports_all_material_blockers() -> None:
    inventory = replace(
        healthy_inventory(),
        universe_schema_present=False,
        eligible_primary_count=0,
        raw_companyfacts_ciks=90,
        raw_submissions_ciks=10,
        unresolved_normalizer_errors=2,
        unresolved_mapper_errors=20,
        database_size_bytes=400_000_000,
        scalable_table_bytes=100_000_000,
        mapping_coverage=None,
    )
    result = evaluate_readiness(inventory, target=100)
    assert not result.ready
    assert "day6_universe_migration_not_deployed" in result.blockers
    assert "insufficient_eligible_primary_companies:0/100" in result.blockers
    assert "insufficient_companyfacts_payloads:90/100" in result.blockers
    assert "insufficient_submissions_payloads:10/100" in result.blockers
    assert "unresolved_normalizer_errors:2" in result.blockers
    assert "unresolved_mapper_errors:20" in result.blockers
    assert "representative_mapping_coverage_not_measured" in result.blockers
    assert any(row.startswith("projected_database_capacity_exceeded") for row in result.blockers)


def test_mapping_coverage_below_95_percent_fails() -> None:
    inventory = replace(healthy_inventory(), mapping_coverage=Decimal("0.949"))
    result = evaluate_readiness(inventory)
    assert "mapping_coverage_below_gate:94.90%/95%" in result.blockers


def test_capacity_projection_uses_current_normalized_footprint() -> None:
    inventory = healthy_inventory()
    assert inventory.bytes_per_normalized_company == 1_000_000
    assert inventory.projected_database_size(100) == 190_000_000
    assert inventory.projected_database_size(5) == inventory.database_size_bytes
    assert evaluate_readiness(inventory).database_limit_bytes == DEFAULT_DATABASE_LIMIT_BYTES


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "unknown"),
        (Decimal("299999999"), "micro"),
        (Decimal("300000000"), "small"),
        (Decimal("2000000000"), "mid"),
        (Decimal("10000000000"), "large"),
        (Decimal("200000000000"), "mega"),
    ],
)
def test_market_cap_bands(value, expected) -> None:
    assert market_cap_band(value) == expected


def test_sector_and_issuer_classification() -> None:
    assert sector_group("3571") == "manufacturing"
    assert sector_group("6021") == "finance_insurance_real_estate"
    assert sector_group(None) == "unknown"
    assert issuer_kind("6021") == "bank"
    assert issuer_kind("6331") == "insurer"
    assert issuer_kind("6798") == "reit"
    assert issuer_kind("6770") == "blank_check_candidate"


@pytest.mark.parametrize(
    ("stage", "error_type", "message", "expected"),
    [
        ("calculate", "KeyError", "net_debt_ebitda", "code_defect"),
        ("resolve", "LookupError", "unmapped concept", "mapping_gap"),
        ("facts", "NotInBulkArchive", "missing payload", "unavailable_filing_data"),
        ("identity", "ValueError", "CIK mismatch", "universe_error"),
        ("calculate", "ValueError", "structural not applicable", "expected_structural_null"),
        ("collector", "HTTPStatusError", "HTTP 429", "upstream_source_failure"),
        ("other", "ValueError", "unknown", "unreviewed"),
    ],
)
def test_failure_taxonomy(stage, error_type, message, expected) -> None:
    assert classify_failure(stage, error_type, message) == expected


def test_mapped_tag_presence_is_explicitly_per_concept(companyfacts_payload) -> None:
    second = {
        "facts": {
            "us-gaap": {
                "NetIncomeLoss": {"units": {"USD": [{"val": 1}]}},
            }
        }
    }
    report = mapped_tag_presence({"a": companyfacts_payload, "b": second})
    assert report["companies"] == 2
    assert report["concepts"]["revenue"] == {
        "present": 1,
        "missing": 1,
        "presence_rate": "0.5000",
    }
    assert report["concepts"]["net_income"] == {
        "present": 1,
        "missing": 1,
        "presence_rate": "0.5000",
    }
