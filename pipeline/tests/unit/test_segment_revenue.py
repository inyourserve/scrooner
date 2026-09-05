import pytest

from scrooner_pipeline.segments.segment_revenue import (
    _parse_value,
    find_segment_report,
    parse_segment_report,
)

# Fixture below is a trimmed, real fragment of Apple's own R46.htm
# ("Segment Information - Information by Reportable Segment (Details)"),
# fetched live 2026-08-31 -- 2 segments x 2 periods instead of the real
# 5 segments x 4 periods, same structure, smaller. Two real bugs were
# found and fixed building this parser against the actual document, not
# assumed: (1) the header <tr> rows have NO class attribute at all
# (only data rows do), which an early version of _ROW's regex required
# and so silently skipped, misaligning every period/value; (2) header
# cell text carries raw &#160; entities that must be decoded, not left
# as literal text.
APPLE_FRAGMENT = """
<table class="report" border="0" cellspacing="2" id="id2">
<tr>
<th class="tl" colspan="1" rowspan="2"><div style="width: 200px;"><strong>Segment Information - Information by Reportable Segment (Details) - USD ($)<br> $ in Millions</strong></div></th>
<th class="th" colspan="2">3 Months Ended</th>
</tr>
<tr>
<th class="th"><div>Jun. 27, 2026</div></th>
<th class="th"><div>Jun. 28, 2025</div></th>
</tr>
<tr class="rh">
<td class="pl" style="border-bottom: 0px;" valign="top"><a class="a" href="javascript:void(0);" onclick="Show.showAR( this, 'defref_us-gaap_StatementBusinessSegmentsAxis=aapl_AmericasSegmentMember', window );">Americas | Operating segments</a></td>
<td class="text">&#160;<span></span></td>
<td class="text">&#160;<span></span></td>
</tr>
<tr class="re">
<td class="pl" style="border-bottom: 0px;" valign="top"><a class="a" href="javascript:void(0);" onclick="Show.showAR( this, 'defref_us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax', window );">Net sales</a></td>
<td class="nump">$ 45,781<span></span></td>
<td class="nump">$ 41,198<span></span></td>
</tr>
<tr class="ro">
<td class="pl" style="border-bottom: 0px;" valign="top"><a class="a" href="javascript:void(0);" onclick="Show.showAR( this, 'defref_us-gaap_CostOfGoodsAndServicesSold', window );">Cost of sales</a></td>
<td class="num">(21,507)<span></span></td>
<td class="num">(22,174)<span></span></td>
</tr>
<tr class="rh">
<td class="pl" style="border-bottom: 0px;" valign="top"><a class="a" href="javascript:void(0);" onclick="Show.showAR( this, 'defref_us-gaap_StatementBusinessSegmentsAxis=aapl_EuropeSegmentMember', window );">Europe | Operating segments</a></td>
<td class="text">&#160;<span></span></td>
<td class="text">&#160;<span></span></td>
</tr>
<tr class="re">
<td class="pl" style="border-bottom: 0px;" valign="top"><a class="a" href="javascript:void(0);" onclick="Show.showAR( this, 'defref_us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax', window );">Net sales</a></td>
<td class="nump">$ 29,395<span></span></td>
<td class="nump">$ 24,014<span></span></td>
</tr>
</table>
"""


@pytest.mark.unit
class TestParseSegmentReport:
    def test_extracts_revenue_rows_for_each_segment_and_period(self):
        rows = parse_segment_report(APPLE_FRAGMENT)
        assert len(rows) == 4
        americas = [r for r in rows if r["segment"] == "Americas"]
        assert len(americas) == 2
        assert americas[0]["value"] == "45781"
        assert americas[0]["period_end"] == "Jun. 27, 2026"
        assert americas[0]["period_type"] == "3 Months Ended"
        assert americas[1]["value"] == "41198"

    def test_excludes_non_revenue_line_items(self):
        """'Cost of sales' must not appear -- only the revenue concept
        row is kept, not every line item in the reconciliation."""
        rows = parse_segment_report(APPLE_FRAGMENT)
        assert all(r["concept_ref"] == "defref_us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax" for r in rows)

    def test_europe_segment_correctly_separated_from_americas(self):
        rows = parse_segment_report(APPLE_FRAGMENT)
        europe = [r for r in rows if r["segment"] == "Europe"]
        assert len(europe) == 2
        assert europe[0]["value"] == "29395"

    def test_empty_table_returns_no_rows(self):
        assert parse_segment_report("<table></table>") == []


@pytest.mark.unit
class TestParseValue:
    def test_plain_number_with_dollar_and_commas(self):
        assert _parse_value("$ 45,781") == "45781"

    def test_parenthesized_value_is_negative(self):
        assert _parse_value("(21,507)") == "-21507"

    def test_nbsp_only_cell_is_none(self):
        assert _parse_value("\xa0") is None

    def test_dash_is_none(self):
        assert _parse_value("—") is None

    def test_non_numeric_text_is_none(self):
        assert _parse_value("Net sales") is None
