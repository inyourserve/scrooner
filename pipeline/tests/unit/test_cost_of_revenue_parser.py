from decimal import Decimal

from scrooner_pipeline.parsers.cost_of_revenue_parser import (
    COST_OF_REVENUE_LABEL_PATTERN,
    _extract_cost_of_revenue_rows,
    _pct_diff,
)

# Modeled on Hyatt Hotels' real rendered R2.htm (accession
# 0001468174-26-000025) -- the real case that found this whole pattern
# 2026-09-21: "Costs of goods and services sold" appears THREE times
# (once per segment: Owned & Leased, Distribution, Reimbursed costs)
# under the SAME primary income-statement report, never as a single
# company-wide total -- the standard Company Facts API strips this
# dimensional context entirely, so core.fact never sees it. Trimmed to
# the essentials; real values scaled to millions like the real report.
_HYATT_HTML = """
<table>
<tr><td>CONDENSED CONSOLIDATED STATEMENTS OF INCOME (LOSS) - USD ($) $ in Millions</td><td>3 Months Ended</td></tr>
<tr><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td></tr>
<tr><td>REVENUES:</td><td>&#160;</td><td>&#160;</td></tr>
<tr><td>Total revenues</td><td>$ 1,829</td><td>$ 1,808</td></tr>
<tr><td>DIRECT AND GENERAL AND ADMINISTRATIVE EXPENSES:</td><td>&#160;</td><td>&#160;</td></tr>
<tr><td>General and administrative</td><td>180</td><td>152</td></tr>
<tr><td>Total direct and general and administrative expenses</td><td>1,702</td><td>1,750</td></tr>
<tr><td>Owned and leased</td><td>&#160;</td><td>&#160;</td></tr>
<tr><td>Total revenues</td><td>274</td><td>304</td></tr>
<tr><td>Costs of goods and services sold</td><td>223</td><td>246</td></tr>
<tr><td>Distribution</td><td>&#160;</td><td>&#160;</td></tr>
<tr><td>Total revenues</td><td>225</td><td>262</td></tr>
<tr><td>Costs of goods and services sold</td><td>198</td><td>219</td></tr>
<tr><td>Reimbursed costs</td><td>&#160;</td><td>&#160;</td></tr>
<tr><td>DIRECT AND GENERAL AND ADMINISTRATIVE EXPENSES:</td><td>&#160;</td><td>&#160;</td></tr>
<tr><td>Costs of goods and services sold</td><td>$ 1,020</td><td>$ 949</td></tr>
</table>
"""

# A single, plain (non-dimensional) Cost of Revenue -- the common,
# unsegmented case this parser must also still handle correctly (sums to
# exactly one term, same as picking the one row).
_PLAIN_HTML = """
<table>
<tr><td>Statement of Operations - USD ($) $ in Millions</td><td>3 Months Ended</td></tr>
<tr><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td></tr>
<tr><td>Total revenues</td><td>$ 500</td><td>$ 480</td></tr>
<tr><td>Cost of revenue</td><td>300</td><td>290</td></tr>
<tr><td>Operating expenses</td><td>100</td><td>95</td></tr>
</table>
"""

# Modeled on Ampco Pittsburgh Corp's real rendered R4.htm (accession
# 0001193125-26-343321): "Costs of products sold (excluding depreciation
# and amortization)" -- a real variant (product companies say "products
# sold", not "goods sold") plus a real, common parenthetical qualifier
# clause, the case that found this pattern needed widening 2026-09-21.
_AMPCO_HTML = """
<table>
<tr><td>Condensed Consolidated Statements of Operations (Unaudited) - USD ($) $ in Thousands</td><td>3 Months Ended</td></tr>
<tr><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td></tr>
<tr><td>Total net sales</td><td>102,918</td><td>113,104</td></tr>
<tr><td>Operating costs and expenses:</td><td>&#160;</td><td>&#160;</td></tr>
<tr><td>Costs of products sold (excluding depreciation and amortization)</td><td>80,675</td><td>91,981</td></tr>
<tr><td>Selling and administrative</td><td>12,917</td><td>12,968</td></tr>
</table>
"""

# A report with no cost-of-revenue-shaped row at all (e.g. a bank) --
# must return None, never a spurious zero or a coincidental match.
_NO_MATCH_HTML = """
<table>
<tr><td>Consolidated Statements of Income</td><td>3 Months Ended</td></tr>
<tr><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td></tr>
<tr><td>Total Interest and Dividend Income</td><td>$ 53,617</td><td>$ 51,573</td></tr>
<tr><td>Net Income</td><td>12,000</td><td>11,500</td></tr>
</table>
"""


class TestCostOfRevenueLabelPattern:
    def test_matches_known_concept_mapping_vocabulary(self):
        for label in ["Costs of goods and services sold", "Cost of revenue", "Cost of sales", "Cost of goods sold", "Total cost of revenue"]:
            assert COST_OF_REVENUE_LABEL_PATTERN.match(label), label

    def test_does_not_match_section_header_with_colon(self):
        assert not COST_OF_REVENUE_LABEL_PATTERN.match("DIRECT AND GENERAL AND ADMINISTRATIVE EXPENSES:")

    def test_does_not_match_unrelated_label(self):
        assert not COST_OF_REVENUE_LABEL_PATTERN.match("General and administrative")

    def test_matches_products_sold_variant_with_parenthetical_qualifier(self):
        assert COST_OF_REVENUE_LABEL_PATTERN.match("Costs of products sold (excluding depreciation and amortization)")


class TestExtractCostOfRevenueRows:
    def test_sums_dimensional_segment_rows_hyatt_shaped(self):
        result = _extract_cost_of_revenue_rows(_HYATT_HTML)
        assert result is not None
        # Q2 2025 (second/current-period... actually first data column is
        # most-recent, 2026-06-30): 223 + 198 + 1,020 = 1,441 (millions)
        assert Decimal(result["value"]) == Decimal("1441000000")
        assert result["matched_rows"] == 3
        assert result["period_end"] == "2026-06-30"

    def test_single_plain_row_sums_to_itself(self):
        result = _extract_cost_of_revenue_rows(_PLAIN_HTML)
        assert result is not None
        assert Decimal(result["value"]) == Decimal("300000000")
        assert result["matched_rows"] == 1

    def test_products_sold_variant_with_qualifier_ampco_shaped(self):
        result = _extract_cost_of_revenue_rows(_AMPCO_HTML)
        assert result is not None
        assert Decimal(result["value"]) == Decimal("80675000")
        assert result["matched_rows"] == 1

    def test_no_matching_row_returns_none(self):
        assert _extract_cost_of_revenue_rows(_NO_MATCH_HTML) is None

    def test_too_few_rows_returns_none(self):
        assert _extract_cost_of_revenue_rows("<table><tr><td>only one row</td></tr></table>") is None


class TestPctDiff:
    def test_zero_diff(self):
        assert _pct_diff(Decimal(100), Decimal(100)) == Decimal(0)

    def test_nonzero_diff(self):
        assert _pct_diff(Decimal(110), Decimal(100)) == Decimal(10)

    def test_zero_external_value_does_not_divide_by_zero(self):
        assert _pct_diff(Decimal(5), Decimal(0)) == Decimal(500)
