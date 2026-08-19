import pytest

from scrooner_pipeline.mapper.definitions import METRIC_DEFINITIONS


@pytest.mark.unit
def test_locked_v1_metric_definitions_include_lineage_inputs():
    definitions = {row[0]: row for row in METRIC_DEFINITIONS}

    assert len(definitions) == 20
    assert definitions["net_margin"][4] == [
        ("net_income", "numerator"),
        ("revenue", "denominator"),
    ]
    assert definitions["market_cap"][2] is True
    assert all(inputs for _, _, _, _, inputs in METRIC_DEFINITIONS)
