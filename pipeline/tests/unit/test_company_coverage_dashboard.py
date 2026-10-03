import pytest

from scrooner_pipeline.mapper.company_coverage_dashboard import (
    _friendly_note,
    render_markdown_company,
    render_markdown_population,
    summarize_company,
)


class _FakeCursor:
    def __init__(self, company_row, population_rows, coverage_rows):
        self._company_row = company_row
        self._population_rows = population_rows
        self._coverage_rows = coverage_rows
        self._last = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        s = sql.strip()
        if "from core.company" in s:
            self._last = ("one", self._company_row)
        elif "from analytics.company_population" in s:
            self._last = ("all", self._population_rows)
        elif "from analytics.company_data_point_coverage" in s:
            self._last = ("all", self._coverage_rows)

    def fetchone(self):
        kind, value = self._last
        return value if kind == "one" else None

    def fetchall(self):
        kind, value = self._last
        return value if kind == "all" else []


class _FakeConnection:
    def __init__(self, company_row, population_rows, coverage_rows):
        self._company_row = company_row
        self._population_rows = population_rows
        self._coverage_rows = coverage_rows

    def cursor(self):
        return _FakeCursor(self._company_row, self._population_rows, self._coverage_rows)


@pytest.mark.unit
class TestFriendlyNote:
    def test_structural_reason_gets_full_sentence(self):
        note = _friendly_note("bank_interest_income_not_revenue", not_applicable=True)
        assert "Bank/savings institution" in note

    def test_missing_input_is_humanized(self):
        note = _friendly_note("missing:dividends_per_share_ttm", not_applicable=False)
        assert note == "Missing a required input: dividends per share ttm."

    def test_incomplete_is_humanized(self):
        note = _friendly_note("incomplete:numerator", not_applicable=False)
        assert "numerator" in note

    def test_null_reason_genuine_gap(self):
        assert "genuine" in _friendly_note(None, not_applicable=False).lower()

    def test_null_reason_not_applicable(self):
        assert _friendly_note(None, not_applicable=True) == "Not applicable to this company."

    def test_unknown_reason_falls_back_to_deslugged_code(self):
        note = _friendly_note("some_weird_new_code", not_applicable=False)
        assert note == "some weird new code"


@pytest.mark.unit
class TestSummarizeCompany:
    def test_visa_shaped_case_cost_of_revenue_not_applicable_eps_is_gap(self):
        # Mirrors the real Visa investigation (2026-10-03): Visa has no
        # Cost of Revenue (a payment network, not a goods seller -- but
        # no structural gap_reason has been written for it, so this test
        # intentionally leaves gap_reason null and relies purely on the
        # applicable_population exclusion path) and a genuine EPS gap
        # (gap_reason null, no applicable_population) that should read
        # as "gap," not "not_applicable."
        conn = _FakeConnection(
            company_row=("0001403161", "VISA INC", "Visa Inc.", "Services-Business Services, NEC", "active"),
            population_rows=[("real_operating_company",)],
            coverage_rows=[
                ("revenue", "concept", None, True, None),
                ("cost_of_revenue", "concept", "goods_seller_company", False, None),
                ("basic_eps", "metric", None, False, None),
            ],
        )
        summary = summarize_company(conn, company_id=5718)
        by_name = {i["data_point_name"]: i for i in summary["items"]}
        assert by_name["revenue"]["status"] == "present"
        assert by_name["cost_of_revenue"]["status"] == "not_applicable"
        assert by_name["basic_eps"]["status"] == "gap"
        assert "genuine" in by_name["basic_eps"]["note"].lower()

    def test_structural_gap_reason_is_not_applicable_even_without_population_exclusion(self):
        conn = _FakeConnection(
            company_row=("0000000001", "SOME BANK", None, "National Commercial Banks", "active"),
            population_rows=[("real_operating_company",)],
            coverage_rows=[("revenue", "concept", None, False, "bank_interest_income_not_revenue")],
        )
        summary = summarize_company(conn, company_id=1)
        assert summary["items"][0]["status"] == "not_applicable"

    def test_coverage_pct_excludes_not_applicable_from_denominator(self):
        conn = _FakeConnection(
            company_row=("0000000001", "CO", None, "desc", "active"),
            population_rows=[],
            coverage_rows=[
                ("a", "concept", None, True, None),
                ("b", "concept", None, False, None),  # genuine gap
                ("c", "concept", "dividend_payer", False, None),  # not applicable (no population row)
            ],
        )
        summary = summarize_company(conn, company_id=1)
        # 1 present / (1 present + 1 gap) = 50%, "c" excluded entirely
        assert summary["coverage_pct"] == 50.0
        assert summary["counts"]["not_applicable"] == 1

    def test_unknown_company_raises(self):
        conn = _FakeConnection(company_row=None, population_rows=[], coverage_rows=[])
        with pytest.raises(ValueError):
            summarize_company(conn, company_id=999999)


@pytest.mark.unit
class TestRenderMarkdown:
    def test_render_markdown_company_includes_header_and_rows(self):
        summary = {
            "company_name": "Visa Inc.",
            "cik": "0001403161",
            "sic_description": "Services",
            "status": "active",
            "populations": ["real_operating_company"],
            "coverage_pct": 75.0,
            "counts": {"present": 3, "gap": 1, "not_applicable": 0},
            "items": [
                {"data_point_name": "revenue", "data_point_type": "concept", "status": "present", "note": None},
                {"data_point_name": "basic_eps", "data_point_type": "metric", "status": "gap", "note": "genuine gap"},
            ],
        }
        md = render_markdown_company(summary)
        assert "Visa Inc." in md
        assert "revenue" in md
        assert "basic_eps" in md
        assert "75.0%" in md

    def test_render_markdown_population_ranks_worst_first_by_default(self):
        rows = [
            {"company_name": "Good Co", "cik": "1", "coverage_pct": 90.0, "present": 9, "gap": 1, "not_applicable": 0},
            {"company_name": "Bad Co", "cik": "2", "coverage_pct": 10.0, "present": 1, "gap": 9, "not_applicable": 0},
        ]
        md = render_markdown_population(rows, limit=10)
        assert md.index("Bad Co") < md.index("Good Co")
