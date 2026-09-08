from decimal import Decimal

import pytest

from scrooner_pipeline.frames.compare import EXACT_MATCH_TOLERANCE_PCT, SEVERITY_MISMATCH, SEVERITY_OK, _pct_diff


@pytest.mark.unit
class TestPctDiff:
    def test_exact_match(self):
        assert _pct_diff(Decimal(100), Decimal(100)) == Decimal(0)

    def test_within_exact_match_tolerance(self):
        # Both sides read the identical filing -- a rounding-noise-scale
        # difference (0.01%) is still 'ok', a real difference isn't.
        diff = _pct_diff(Decimal("100.005"), Decimal(100))
        assert diff <= EXACT_MATCH_TOLERANCE_PCT

    def test_real_mismatch_exceeds_tolerance(self):
        diff = _pct_diff(Decimal(150), Decimal(100))
        assert diff > EXACT_MATCH_TOLERANCE_PCT
