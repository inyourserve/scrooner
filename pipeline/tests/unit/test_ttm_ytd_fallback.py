from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper.ttm import FactsByPeriod, _ttm_sum


def _facts(quarters: dict, durations: list) -> FactsByPeriod:
    out = FactsByPeriod(quarters)
    out.durations = durations
    return out


# Symbotic net income ($K): FY2025 is authoritative, FY2025's quarters are
# restated (their Q4 can't be derived), FY2026 Q1-Q3 are present.
FY25 = (date(2024, 9, 29), date(2025, 9, 27), Decimal("-16937"), [1], 100)
NINE_M_25 = (date(2024, 9, 29), date(2025, 6, 28), Decimal("-8902"), [2], 100)
NINE_M_26 = (date(2025, 9, 28), date(2026, 6, 27), Decimal("16244"), [3], 100)
Q3_26 = (Decimal("11673"), [4], date(2026, 3, 29), date(2026, 6, 27))


@pytest.mark.unit
class TestTtmYtdFallback:
    def test_ytd_method_when_a_quarter_is_missing(self):
        facts = _facts({(2026, "Q3"): Q3_26}, [FY25, NINE_M_25, NINE_M_26])
        value, fids = _ttm_sum(facts, 2026, "Q3")
        # 9M FY2026 + FY2025 - 9M FY2025
        assert value == Decimal("16244") + Decimal("-16937") - Decimal("-8902")
        assert sorted(fids) == [1, 2, 3]

    def test_four_quarter_chain_still_wins(self):
        q = {
            (2025, "Q4"): (Decimal("1"), [10], date(2025, 6, 29), date(2025, 9, 27)),
            (2026, "Q1"): (Decimal("2"), [11], date(2025, 9, 28), date(2025, 12, 27)),
            (2026, "Q2"): (Decimal("3"), [12], date(2025, 12, 28), date(2026, 3, 28)),
            (2026, "Q3"): (Decimal("4"), [13], date(2026, 3, 29), date(2026, 6, 27)),
        }
        facts = _facts(q, [FY25, NINE_M_25, NINE_M_26])
        assert _ttm_sum(facts, 2026, "Q3") == (Decimal("10"), [10, 11, 12, 13])

    def test_q4_anchor_uses_the_full_year(self):
        q4 = (Decimal("-5"), [9], date(2025, 6, 29), date(2025, 9, 27))
        facts = _facts({(2025, "Q4"): q4}, [FY25])
        assert _ttm_sum(facts, 2025, "Q4") == (Decimal("-16937"), [1])

    def test_missing_prior_year_ytd_gives_none(self):
        facts = _facts({(2026, "Q3"): Q3_26}, [FY25, NINE_M_26])
        assert _ttm_sum(facts, 2026, "Q3") == (None, [])

    def test_plain_dict_has_no_fallback(self):
        assert _ttm_sum({(2026, "Q3"): Q3_26}, 2026, "Q3") == (None, [])

    def test_pieces_from_different_tags_give_none(self):
        # Plains GP: FY from ProfitLoss (tag 200), YTDs from NetIncomeLoss (100).
        fy_other_tag = FY25[:4] + (200,)
        facts = _facts({(2026, "Q3"): Q3_26}, [fy_other_tag, NINE_M_25, NINE_M_26])
        assert _ttm_sum(facts, 2026, "Q3") == (None, [])
