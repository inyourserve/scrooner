"""Unit tests for company_master/contact_details.py's pure payload
extraction (2026-08-29 zero-new-fetch coverage pass, items 5/6).
_extract_contact_fields is pure (no DB/storage), same pattern as
normalizer/identity.py's _parse_filings_block -- tested directly with
real-shaped submissions.json fragments (field names/nesting confirmed
live against AAPL's actual payload before writing this module)."""

import pytest

from scrooner_pipeline.company_master.contact_details import _extract_contact_fields


@pytest.mark.unit
def test_real_shaped_payload_extracts_ein_address_and_phone():
    """Real shape confirmed live 2026-08-29 against AAPL's submissions.json
    base file."""
    payload = {
        "ein": "942404110",
        "addresses": {
            "mailing": {"street1": "ONE APPLE PARK WAY", "city": "CUPERTINO", "stateOrCountry": "CA", "zipCode": "95014"},
            "business": {"street1": "ONE APPLE PARK WAY", "city": "CUPERTINO", "stateOrCountry": "CA", "zipCode": "95014"},
        },
        "phone": "(408) 996-1010",
    }

    fields = _extract_contact_fields("0000320193", payload)

    assert fields == {
        "cik": "0000320193",
        "ein": "942404110",
        "business_address_line1": "ONE APPLE PARK WAY",
        "business_address_city": "CUPERTINO",
        "business_address_state": "CA",
        "business_address_zip": "95014",
        "business_phone": "(408) 996-1010",
    }


@pytest.mark.unit
def test_missing_addresses_block_nulls_out_rather_than_crashing():
    """A payload with no addresses key at all (shouldn't happen for a real
    filer, but never assumed) must null every address field, not KeyError."""
    payload = {"ein": "000000000", "phone": None}

    fields = _extract_contact_fields("0001046179", payload)

    assert fields["business_address_line1"] is None
    assert fields["business_address_city"] is None
    assert fields["business_address_state"] is None
    assert fields["business_address_zip"] is None
    assert fields["business_phone"] is None


@pytest.mark.unit
def test_foreign_private_issuer_placeholder_ein_passed_through_verbatim():
    """TSM/ENB (20-F/40-F filers) report ein="000000000" in their own real
    submissions.json -- confirmed live, a genuine SEC placeholder for "no US
    EIN", not something this module should guess-fill or null out."""
    payload = {
        "ein": "000000000",
        "addresses": {"business": {"street1": None, "city": "HSINCHU", "stateOrCountry": None, "zipCode": None}},
        "phone": "886-3-5636688",
    }

    fields = _extract_contact_fields("0001046179", payload)

    assert fields["ein"] == "000000000"
    assert fields["business_address_city"] == "HSINCHU"
    assert fields["business_address_state"] is None
    assert fields["business_phone"] == "886-3-5636688"
