import pytest

from scrooner_pipeline.frames.fetch import period_code


@pytest.mark.unit
class TestPeriodCode:
    def test_duration_period(self):
        assert period_code(2026, 1, instant=False) == "CY2026Q1"

    def test_instant_period(self):
        # Verified live 2026-09-08 against a real Frames response --
        # instant concepts (balance sheet items) need the 'I' suffix,
        # duration concepts (income statement/cash flow) don't.
        assert period_code(2026, 1, instant=True) == "CY2026Q1I"
