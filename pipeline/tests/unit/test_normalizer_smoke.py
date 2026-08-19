import pytest

from scrooner_pipeline.normalizer.units import canonicalize_unit, extract_distinct_units


@pytest.mark.unit
def test_companyfacts_units_are_extracted_and_canonicalized(companyfacts_payload):
    raw_units = extract_distinct_units(companyfacts_payload)

    assert raw_units == {"USD", "Segment", "segment"}
    assert {canonicalize_unit(unit) for unit in raw_units} == {"usd", "segment"}
