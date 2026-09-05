from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.ownership import institutional_summary

LATEST = date(2026, 3, 31)
PRIOR = date(2025, 12, 31)


def _holder(filer_name, filer_cik=None, shares=None, value_usd=None):
    return {
        "filer_name": filer_name,
        "filer_cik": filer_cik,
        "shares": Decimal(shares) if shares is not None else None,
        "value_usd": Decimal(value_usd) if value_usd is not None else None,
    }


@pytest.mark.unit
class TestMatchKey:
    def test_uses_filer_cik_when_present(self):
        h = _holder("Vanguard Group Inc", filer_cik="0000102909", shares=100)
        assert institutional_summary._match_key(h) == "0000102909"

    def test_falls_back_to_name_prefixed_key_when_cik_missing(self):
        h = _holder("Some Manager", filer_cik=None, shares=100)
        assert institutional_summary._match_key(h) == "name:Some Manager"


@pytest.mark.unit
class TestBuildInstitutionalSummary:
    def test_total_pct_and_qoq_change(self):
        latest = [_holder("A", "A1", shares=600), _holder("B", "B1", shares=400)]
        prior = [_holder("A", "A1", shares=500), _holder("B", "B1", shares=400)]
        result = institutional_summary.build_institutional_summary(
            1, LATEST, PRIOR, latest, prior, Decimal(2000)
        )
        assert result["total_institutional_pct"] == Decimal(1000) / Decimal(2000)  # 50%
        assert result["total_institutional_pct_prior"] == Decimal(900) / Decimal(2000)  # 45%
        assert result["qoq_change_pct"] == Decimal("0.05")
        assert result["total_holders"] == 2

    def test_missing_shares_outstanding_leaves_pct_fields_null(self):
        latest = [_holder("A", "A1", shares=100)]
        prior = [_holder("A", "A1", shares=90)]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, prior, None)
        assert result["total_institutional_pct"] is None
        assert result["total_institutional_pct_prior"] is None
        assert result["qoq_change_pct"] is None

    def test_zero_shares_outstanding_is_null_not_division_error(self):
        latest = [_holder("A", "A1", shares=100)]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, [], Decimal(0))
        assert result["total_institutional_pct"] is None

    def test_increased_decreased_unchanged_counts(self):
        latest = [
            _holder("A", "A1", shares=110),  # increased
            _holder("B", "B1", shares=90),  # decreased
            _holder("C", "C1", shares=50),  # unchanged
        ]
        prior = [
            _holder("A", "A1", shares=100),
            _holder("B", "B1", shares=100),
            _holder("C", "C1", shares=50),
        ]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, prior, Decimal(1000))
        assert result["holders_increased"] == 1
        assert result["holders_decreased"] == 1
        assert result["new_positions"] == 0
        assert result["exited_positions"] == 0

    def test_new_and_exited_positions_by_filer_cik(self):
        latest = [_holder("A", "A1", shares=100), _holder("New Filer", "N1", shares=50)]
        prior = [_holder("A", "A1", shares=100), _holder("Old Filer", "O1", shares=30)]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, prior, Decimal(1000))
        assert result["new_positions"] == 1
        assert result["exited_positions"] == 1

    def test_same_manager_different_cik_counts_as_new_and_exited(self):
        # Real-world case found live (AAPL/JPM, 2026-08-29): Vanguard's
        # 13F filings switched from a single "VANGUARD GROUP INC" CIK to
        # several new entity CIKs ("VANGUARD CAPITAL MANAGEMENT LLC" etc.)
        # between the two stored quarters. Matching by filer_cik (per the
        # product spec's own instruction) correctly reports this as an
        # exited + new position pair rather than silently reconciling it
        # as "the same holder" -- a real EDGAR-level filer reorganization,
        # not a bug in this matching logic.
        latest = [_holder("Vanguard Capital Management LLC", "V_NEW", shares=900)]
        prior = [_holder("Vanguard Group Inc", "V_OLD", shares=850)]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, prior, Decimal(10000))
        assert result["new_positions"] == 1
        assert result["exited_positions"] == 1
        assert result["holders_increased"] == 0
        assert result["holders_decreased"] == 0

    def test_top_holders_sorted_by_latest_shares_with_status_and_changes(self):
        latest = [
            _holder("Big Fund", "B1", shares=1000, value_usd=50000),
            _holder("Small Fund", "S1", shares=100, value_usd=5000),
        ]
        prior = [
            _holder("Big Fund", "B1", shares=800, value_usd=40000),
            _holder("Small Fund", "S1", shares=150, value_usd=7500),
        ]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, prior, Decimal(10000))
        top = result["top_holders"]
        assert [h["filer_name"] for h in top] == ["Big Fund", "Small Fund"]
        assert top[0]["status"] == "increased"
        assert top[0]["share_change"] == "200"
        assert top[0]["pct_change"] == str(Decimal(200) / Decimal(800))
        assert top[1]["status"] == "decreased"
        assert top[1]["share_change"] == "-50"

    def test_top_holders_new_position_has_null_change_fields(self):
        latest = [_holder("Brand New", "N1", shares=100)]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, [], Decimal(1000))
        top = result["top_holders"]
        assert top[0]["status"] == "new"
        assert top[0]["share_change"] is None
        assert top[0]["pct_change"] is None

    def test_exited_holder_appears_in_top_holders_when_room_remains(self):
        latest = [_holder("Still Here", "A1", shares=100)]
        prior = [_holder("Still Here", "A1", shares=100), _holder("Gone Now", "G1", shares=500)]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, prior, Decimal(1000))
        statuses = {h["filer_name"]: h["status"] for h in result["top_holders"]}
        assert statuses["Gone Now"] == "exited"
        assert statuses["Still Here"] == "unchanged"

    def test_top_holders_capped_at_ten(self):
        latest = [_holder(f"Fund {i}", f"C{i}", shares=100 - i) for i in range(15)]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, [], Decimal(10000))
        assert len(result["top_holders"]) == 10
        assert result["top_holders"][0]["filer_name"] == "Fund 0"  # highest shares first

    def test_total_holders_counts_latest_period_only(self):
        latest = [_holder("A", "A1", shares=10), _holder("B", "B1", shares=20)]
        prior = [_holder("A", "A1", shares=10), _holder("C", "C1", shares=30)]
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, latest, prior, Decimal(1000))
        assert result["total_holders"] == 2

    def test_report_periods_pass_through(self):
        result = institutional_summary.build_institutional_summary(1, LATEST, PRIOR, [], [], Decimal(1000))
        assert result["report_period_latest"] == LATEST
        assert result["report_period_prior"] == PRIOR
        assert result["company_id"] == 1
