import pytest

from scrooner_pipeline.parsers.revenue_parser import (
    INCOME_STATEMENT_TITLE_PATTERN,
    _detect_scale,
    _extract_revenue_row,
    _parse_period_end,
)

# Real markup shape, trimmed to the essentials -- modeled on MSP
# Recovery's actual rendered R4.htm (accession 0001193125-25-288180),
# the case that found the footnote-reference-cell misalignment bug
# 2026-09-05: cells[1] is a footnote-reference slot (sometimes a real
# marker like "[1]", sometimes empty) that the date-header row does NOT
# have, so raw cell position drifts out of sync with date_cells
# position -- the whole reason this test exists.
_MSP_RECOVERY_HTML = """
<table>
<tr><td>Condensed Consolidated Statements of Operations</td><td>3 Months Ended</td><td>9 Months Ended</td></tr>
<tr><td>Sep. 30, 2025</td><td>Sep. 30, 2024</td><td>Sep. 30, 2025</td><td>Sep. 30, 2024</td></tr>
<tr><td>Claims recovery income</td><td></td><td>$ 198</td><td>$ 3,577</td><td>$ 1,564</td><td></td><td>$ 9,879</td><td></td></tr>
<tr><td>Other</td><td></td><td>0</td><td>91</td><td>7</td><td></td><td>127</td><td></td></tr>
<tr><td>Total Revenues</td><td></td><td>198</td><td>3,668</td><td>1,571</td><td></td><td>10,006</td><td></td></tr>
<tr><td>Operating expenses</td><td></td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td></td><td>&nbsp;</td><td></td></tr>
<tr><td>Cost of revenues</td><td>[1]</td><td>251</td><td>1,671</td><td>1,076</td><td></td><td>3,453</td><td></td></tr>
</table>
"""

# A real bank's own statement (Arrow Financial-shaped) -- its top total
# is "Total Interest and Dividend Income", which must NOT match
# REVENUE_LABEL_PATTERN (a bank's gross interest figure is not a
# revenue-equivalent, doc 42 Part 1). Deliberately includes a LATER,
# unrelated ASC-606 revenue-disaggregation footnote table in the SAME
# report -- modeled on the real false positive found live 2026-09-05
# (Peoples Financial Corp, BV Financial): both real banks' R4.htm
# rendered BOTH the primary income statement AND a footnote table
# further down with its own "Revenue" row (non-interest fee income, a
# small fraction of the bank's real economics) -- the original fixture
# was too short to ever exercise "the scanner has no boundary and keeps
# going for hundreds of rows", the actual real-world failure shape.
_BANK_HTML = """
<table>
<tr><td>Consolidated Statements of Income</td><td>3 Months Ended</td></tr>
<tr><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td></tr>
<tr><td>INTEREST AND DIVIDEND INCOME</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Interest and Fees on Loans</td><td>$ 47,181</td><td>$ 45,600</td></tr>
<tr><td>Total Interest and Dividend Income</td><td>53,617</td><td>51,573</td></tr>
<tr><td>INTEREST EXPENSE</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Interest-Bearing Checking Accounts</td><td>2,162</td><td>1,941</td></tr>
<tr><td>Net Interest Income</td><td>45,000</td><td>44,000</td></tr>
<tr><td>Noninterest Income</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Service charges</td><td>1,200</td><td>1,100</td></tr>
<tr><td>Non-Interest Expense</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Salaries and benefits</td><td>8,000</td><td>7,500</td></tr>
<tr><td>Net Income</td><td>12,000</td><td>11,500</td></tr>
<tr><td>Revenue from Contract with Customer [Abstract]</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Revenue</td><td>$ 702</td><td>$ 624</td></tr>
</table>
"""

# A SPAC shell (BOXABL-shaped) -- genuinely no revenue line at all,
# must return None, not a G&A expense or SPAC-trust-interest figure.
_SPAC_HTML = """
<table>
<tr><td>Condensed Statements of Operations</td><td>3 Months Ended</td></tr>
<tr><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td></tr>
<tr><td>Operating expenses:</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>General and administrative expenses</td><td>$ 4,555,829</td><td>$ 83,539</td></tr>
<tr><td>Investment income on trust account</td><td>490,166</td><td>842,499</td></tr>
</table>
"""

# A simple, clean single-column-per-period case (no footnote slots at
# all) -- AI Tech Solutions-shaped, "Revenues" bare (no "Total" prefix).
_SIMPLE_HTML = """
<table>
<tr><td>Condensed Consolidated Statements of Operations</td><td>3 Months Ended</td></tr>
<tr><td>May. 31, 2026</td><td>May. 31, 2025</td></tr>
<tr><td>Revenues</td><td>$ 1,831,202</td><td>$ 1,854,837</td></tr>
<tr><td>Cost of revenues:</td><td>&nbsp;</td><td>&nbsp;</td></tr>
</table>
"""

# loanDepot-shaped: a real lender whose legitimate "Total net revenues"
# line comes AFTER its own Interest income/Interest expense section
# (netted INTO a broader revenue build-up, not the whole statement).
# Found live 2026-09-05: the first fix for the bank false positive
# above (adding "Interest Expense" as a stop boundary) broke this real
# case outright -- it stopped scanning at "Interest expense" and never
# reached the real revenue row 7 lines later. This is the regression
# guard for that specific mistake: any future boundary change must
# keep BOTH this test and the bank one passing.
_LOANDEPOT_HTML = """
<table>
<tr><td>Consolidated Statements of Operations</td><td>3 Months Ended</td></tr>
<tr><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td></tr>
<tr><td>REVENUES:</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Interest income</td><td>$ 39,692</td><td>$ 40,946</td></tr>
<tr><td>Interest expense</td><td>(37,433)</td><td>(39,297)</td></tr>
<tr><td>Net interest income</td><td>2,259</td><td>1,649</td></tr>
<tr><td>Gain on origination and sale of loans, net</td><td>176,740</td><td>174,810</td></tr>
<tr><td>Origination income, net</td><td>52,224</td><td>34,931</td></tr>
<tr><td>Servicing fee income</td><td>111,964</td><td>108,209</td></tr>
<tr><td>Total net revenues</td><td>337,321</td><td>282,537</td></tr>
<tr><td>EXPENSES:</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Personnel expense</td><td>180,729</td><td>154,116</td></tr>
</table>
"""


# APA Corp-shaped, real (2026-09-20): "STATEMENT OF CONSOLIDATED
# OPERATIONS" -- "consolidated" AFTER "of", the word-order variant that
# originally made find_income_statement_report() return None for a real,
# well-formed report. Top-line label is "Total revenues and other" (APA's
# own presentation folds derivative gains/losses and divestiture gains
# into the same total), and the title states "$ in Millions" -- a raw
# cell value here is off by 1,000,000x unless scaled.
_APA_CORP_HTML = """
<table>
<tr><td>STATEMENT OF CONSOLIDATED OPERATIONS (Unaudited) - USD ($) shares in Millions, $ in Millions</td><td>3 Months Ended</td><td>6 Months Ended</td></tr>
<tr><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td><td>Jun. 30, 2026</td><td>Jun. 30, 2025</td></tr>
<tr><td>REVENUES AND OTHER:</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Derivative instrument gains (losses), net</td><td>$ 8</td><td>$ 138</td><td>$ (105)</td><td>$ 110</td></tr>
<tr><td>Gain (loss) on divestitures, net</td><td>(2)</td><td>282</td><td>4</td><td>282</td></tr>
<tr><td>Other, net</td><td>20</td><td>14</td><td>36</td><td>28</td></tr>
<tr><td>Total revenues and other</td><td>2,399</td><td>2,612</td><td>4,865</td><td>5,120</td></tr>
<tr><td>OPERATING EXPENSES:</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>Lease operating expenses</td><td>353</td><td>367</td><td>701</td><td>734</td></tr>
</table>
"""


@pytest.mark.unit
def test_apa_corp_total_revenues_and_other_scaled_from_millions():
    result = _extract_revenue_row(_APA_CORP_HTML)
    assert result == {"value": "2399000000", "period_end": "2026-06-30"}


@pytest.mark.unit
def test_income_statement_title_pattern_matches_consolidated_after_of():
    assert INCOME_STATEMENT_TITLE_PATTERN.search("STATEMENT OF CONSOLIDATED OPERATIONS (Unaudited)")
    assert INCOME_STATEMENT_TITLE_PATTERN.search("Consolidated Statements of Operations")
    # Must NOT match a different, real report that happens to share
    # "consolidated" + "income" vocabulary -- comprehensive income is not
    # the primary income statement.
    assert not INCOME_STATEMENT_TITLE_PATTERN.search("STATEMENT OF CONSOLIDATED COMPREHENSIVE INCOME (Unaudited)")


@pytest.mark.unit
@pytest.mark.parametrize(
    "title,expected",
    [
        ("... USD ($) $ in Millions", 1_000_000),
        ("... USD ($) $ in Thousands", 1_000),
        ("... USD ($) $ in Billions", 1_000_000_000),
        ("Condensed Consolidated Statements of Operations", 1),
        ("", 1),
    ],
)
def test_detect_scale(title, expected):
    assert _detect_scale(title) == expected


@pytest.mark.unit
def test_prefers_total_row_over_component_row_and_aligns_period_correctly():
    result = _extract_revenue_row(_MSP_RECOVERY_HTML)
    assert result == {"value": "198", "period_end": "2025-09-30"}


@pytest.mark.unit
def test_bank_gross_interest_income_never_matches_revenue_pattern():
    assert _extract_revenue_row(_BANK_HTML) is None


@pytest.mark.unit
def test_spac_shell_with_no_revenue_line_returns_none():
    assert _extract_revenue_row(_SPAC_HTML) is None


@pytest.mark.unit
def test_bare_revenues_label_with_no_footnote_slots():
    result = _extract_revenue_row(_SIMPLE_HTML)
    assert result == {"value": "1831202", "period_end": "2026-05-31"}


@pytest.mark.unit
def test_lender_total_net_revenues_after_its_own_interest_section():
    result = _extract_revenue_row(_LOANDEPOT_HTML)
    assert result == {"value": "337321", "period_end": "2026-06-30"}


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Sep. 30, 2025", "2025-09-30"),
        ("Jun. 30, 2026", "2026-06-30"),
        ("December 31, 2025", "2025-12-31"),
        ("", None),
        ("not a date", None),
    ],
)
def test_parse_period_end(raw, expected):
    assert _parse_period_end(raw) == expected
