from datetime import date

import pytest

from scrooner_pipeline.company_master.status import (
    _deregistration_overridden_by_later_filing,
    compute_status,
)


@pytest.mark.unit
class TestDeregistrationOverride:
    def test_later_10k_overrides_confirmed_form15(self):
        """The real 2026-09-02 finding: AMD's Form 15 dates to 1996, but it
        kept filing real 10-Ks for decades after -- the override must fire."""
        assert _deregistration_overridden_by_later_filing(
            latest_filing_date=date(2026, 8, 5), form15_date=date(1996, 2, 9)
        ) is True

    def test_no_later_filing_does_not_override(self):
        """A genuine delisting (American Woodmark-style, doc 23): no
        qualifying filing after the Form 15 -- signal stays trusted."""
        assert _deregistration_overridden_by_later_filing(
            latest_filing_date=date(1996, 1, 1), form15_date=date(1996, 2, 9)
        ) is False

    def test_missing_dates_do_not_override(self):
        assert _deregistration_overridden_by_later_filing(None, date(1996, 2, 9)) is False
        assert _deregistration_overridden_by_later_filing(date(2026, 1, 1), None) is False


@pytest.mark.unit
class TestComputeStatus:
    def test_deregistered_flag_forces_delisted(self):
        status, reason = compute_status(date(2026, 1, 1), date(2026, 8, 1), is_deregistered=True)
        assert status == "delisted"
        assert reason == "form_15_common_stock_confirmed"

    def test_recent_filing_without_deregistration_is_active(self):
        status, _ = compute_status(date(2026, 7, 1), date(2026, 8, 1), is_deregistered=False)
        assert status == "active"

    def test_stale_beyond_threshold(self):
        status, _ = compute_status(date(2020, 1, 1), date(2026, 8, 1), is_deregistered=False)
        assert status == "stale"

    def test_no_filing_is_unknown(self):
        status, reason = compute_status(None, date(2026, 8, 1), is_deregistered=False)
        assert status == "unknown"
        assert reason == "no_qualifying_filing_on_record"
