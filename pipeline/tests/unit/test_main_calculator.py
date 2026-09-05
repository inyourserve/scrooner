import pytest

from scrooner_pipeline.mapper.main_calculator import METRIC_CALCULATOR_REGISTRY


@pytest.mark.unit
def test_registry_has_no_duplicate_or_conflicting_entries():
    # _register() overwrites on collision -- if two calls registered the
    # same metric_name under DIFFERENT modules, that's a real ownership
    # conflict this test would otherwise hide silently.
    seen: dict[str, str] = {}
    for name, entry in METRIC_CALCULATOR_REGISTRY.items():
        assert name not in seen, f"{name} registered twice"
        seen[name] = entry["module"]


@pytest.mark.unit
def test_every_entry_has_required_fields():
    for name, entry in METRIC_CALCULATOR_REGISTRY.items():
        assert entry["module"], f"{name} missing module"
        assert entry["cli_command"], f"{name} missing cli_command"
        assert entry["description"], f"{name} missing description"


@pytest.mark.unit
def test_known_metrics_route_to_expected_module():
    assert "calculate.py" in METRIC_CALCULATOR_REGISTRY["roic"]["module"]
    assert "ttm.py" in METRIC_CALCULATOR_REGISTRY["roic"]["module"]
    assert METRIC_CALCULATOR_REGISTRY["piotroski_f_score"]["module"] == "mapper/quality_score.py"
    assert METRIC_CALCULATOR_REGISTRY["revenue_growth_yoy"]["module"] == "mapper/ttm.py (compute_growth)"
    assert METRIC_CALCULATOR_REGISTRY["market_cap"]["module"] == "mapper/price_metrics.py"
