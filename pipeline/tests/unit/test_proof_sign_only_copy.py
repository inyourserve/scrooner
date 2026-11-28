"""Rule authority_copy_role v2 (2026-11-29): a copy equal to minus the shown value is no disagreement (sign_only).
QCOM cf_inventory_change FY2018 -337M shown vs +337M in the FY2020 10-K; DIS interest_expense FY2021 1,546M vs -1,546M.
Pure; mutation-checked (fails with the sign_only branch removed)."""

from decimal import Decimal

import pytest
from scrooner_pipeline.proof import shown as sh

D = Decimal


@pytest.mark.unit
def test_opposite_sign_copy_is_not_a_disagreement():
    kept, skipped = sh.authority_skips(
        [("B", "337000000")], D("-337000000"), "cf_inventory_change", [], {}
    )
    assert kept == []
    assert skipped == (("B", "337000000", "sign_only"),)


@pytest.mark.unit
def test_a_different_magnitude_still_disagrees():
    kept, skipped = sh.authority_skips(
        [("B", "-1546000001")], D("1546000000"), "interest_expense", [], {}
    )
    assert kept == [("B", "-1546000001")]
    assert skipped == ()


@pytest.mark.unit
def test_zero_shown_has_no_sign_flip():
    kept, _ = sh.authority_skips([("B", "5")], D(0), "interest_expense", [], {})
    assert kept == [("B", "5")]
