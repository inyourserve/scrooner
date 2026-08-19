from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from scrooner_pipeline.company_master.history import build_ticker_dating
from scrooner_pipeline.company_master.universe import (
    ELIGIBLE,
    EXCLUDED,
    UNCERTAIN,
    UniverseCandidate,
    build_current_universe,
    build_snapshot,
    classify_filing_regime,
    evaluate_candidate,
)


pytestmark = pytest.mark.unit


def candidate(**overrides) -> UniverseCandidate:
    values = {
        "company_id": 1,
        "filer_id": 11,
        "security_id": 21,
        "listing_id": 31,
        "cik": "0000000001",
        "ticker": "BASE",
        "exchange": "Nasdaq",
        "security_type": "Common Stock",
        "company_status": "active",
        "sic_code": "3571",
        "filing_forms": ("10-K", "10-Q"),
    }
    values.update(overrides)
    return UniverseCandidate(**values)


@pytest.mark.parametrize(
    ("overrides", "expected_status", "reason"),
    [
        ({}, ELIGIBLE, "eligible_common_equity"),
        ({"issuer_kind": "bank"}, ELIGIBLE, "eligible_operating_structure:bank"),
        ({"issuer_kind": "insurer"}, ELIGIBLE, "eligible_operating_structure:insurer"),
        ({"issuer_kind": "reit"}, ELIGIBLE, "eligible_operating_structure:reit"),
        ({"issuer_kind": "bdc"}, ELIGIBLE, "eligible_operating_structure:bdc"),
        ({"security_type": "Preferred Stock"}, EXCLUDED, "excluded_preferred_security"),
        ({"security_type": "Warrant"}, EXCLUDED, "excluded_warrant_or_right"),
        ({"security_type": "Unit"}, EXCLUDED, "excluded_unit"),
        ({"security_type": "ETP"}, EXCLUDED, "excluded_fund_security"),
        ({"security_type": "Corporate Bond"}, EXCLUDED, "excluded_debt_or_etn"),
        ({"exchange": "OTC"}, EXCLUDED, "excluded_non_national_exchange"),
        ({"company_status": "delisted"}, EXCLUDED, "excluded_company_delisted"),
        ({"registered_fund_confirmed": True}, EXCLUDED, "excluded_registered_fund"),
        ({"spac_or_shell_confirmed": True}, EXCLUDED, "excluded_spac_or_shell_confirmed"),
        ({"security_type": None}, UNCERTAIN, "uncertain_security_type:unknown"),
        ({"exchange": None}, UNCERTAIN, "uncertain_exchange_missing"),
        ({"company_status": "stale"}, UNCERTAIN, "uncertain_company_status:stale"),
        ({"sic_code": "6770"}, UNCERTAIN, "uncertain_blank_check_sic_requires_confirmation"),
        (
            {"security_type": "ADR", "filing_forms": ("20-F",)},
            UNCERTAIN,
            "uncertain_adr_scope_decision_open",
        ),
        (
            {"filing_forms": ("40-F",)},
            UNCERTAIN,
            "uncertain_foreign_filer_scope_open:canadian_mjds",
        ),
    ],
)
def test_explicit_eligibility_rules(overrides, expected_status, reason) -> None:
    result = evaluate_candidate(candidate(**overrides))
    assert result.eligibility_status == expected_status
    assert reason in result.reason_codes


def test_filing_regimes_are_explicit() -> None:
    assert classify_filing_regime(["10-K", "10-Q"]) == "domestic_reporting_company"
    assert classify_filing_regime(["20-F"]) == "foreign_private_issuer"
    assert classify_filing_regime(["40-F"]) == "canadian_mjds"
    assert classify_filing_regime(["N-1A"]) == "registered_fund"
    assert classify_filing_regime([]) == "unknown"


def test_primary_listing_uses_exchange_priority_not_input_order() -> None:
    rows = [
        candidate(listing_id=32, security_id=22, ticker="SECOND", exchange="NYSE American"),
        candidate(listing_id=31, security_id=21, ticker="PRIMARY", exchange="NYSE"),
    ]
    first = build_snapshot(rows)
    second = build_snapshot(reversed(rows))

    assert first == second
    assert [row.ticker for row in first if row.is_primary] == ["PRIMARY"]
    assert first[0].decision_order == 1
    assert first[1].decision_order == 2


def test_multiple_share_classes_are_not_arbitrarily_resolved() -> None:
    rows = [
        candidate(listing_id=31, security_id=21, ticker="GOOG", exchange="Nasdaq"),
        candidate(listing_id=32, security_id=22, ticker="GOOGL", exchange="Nasdaq"),
    ]

    decisions = build_snapshot(rows)

    assert all(row.eligibility_status == ELIGIBLE for row in decisions)
    assert not any(row.is_primary for row in decisions)
    assert all("primary_ambiguous_multiple_share_classes" in row.reason_codes for row in decisions)


def test_ticker_disappearance_closes_historical_listing() -> None:
    older = datetime(2026, 1, 1, tzinfo=timezone.utc)
    newer = datetime(2026, 2, 1, tzinfo=timezone.utc)
    result = build_ticker_dating(
        [(older, {"tickers": ["OLD"]}), (newer, {"tickers": ["NEW"]})],
        ["NEW"],
    )

    assert result["OLD"] == {
        "effective_from": None,
        "effective_to": newer.date(),
        "source": "submissions_snapshot",
    }
    assert result["NEW"] == {
        "effective_from": newer.date(),
        "effective_to": None,
        "source": "submissions_snapshot",
    }


def test_current_builder_rejects_retroactive_snapshot() -> None:
    yesterday = date.today() - timedelta(days=1)
    with pytest.raises(ValueError, match="only be built for today"):
        build_current_universe(None, yesterday)  # type: ignore[arg-type]
