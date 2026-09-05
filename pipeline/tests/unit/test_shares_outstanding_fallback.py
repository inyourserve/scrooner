import pytest

from scrooner_pipeline.company_master.shares_outstanding_fallback import _extract_shares


@pytest.mark.unit
class TestExtractShares:
    def test_reddit_style_per_class_three_classes(self):
        text = (
            "As of February 4, 2026, the registrant had outstanding 139,649,508 shares of Class A "
            "common stock, 51,386,276 shares of Class B common stock, and no shares of Class C common "
            "stock each with a par value."
        )
        assert _extract_shares(text) == 191035784.0

    def test_block_style_two_class_respectively_with_thousands_scale(self):
        text = (
            "The number of shares (in thousands) of the registrant's Class A and Class B common stock "
            "outstanding were 539,103 and 59,993, respectively."
        )
        assert _extract_shares(text) == 599096000.0

    def test_class_prefix_no_shares_of_wording(self):
        text = (
            "As of March 13, 2026, there were 29,200,000 Class A ordinary shares, par value $0.0001 per "
            "share, and 12,000,000 Class B ordinary shares, par value $0.0001 per share, of the "
            "registrant issued and outstanding."
        )
        assert _extract_shares(text) == 41200000.0

    def test_series_instead_of_class(self):
        text = (
            "The registrant had outstanding 155,248,477 shares of Series A common stock, par value "
            "$0.001 per share, and 21,702,510 shares of Series B common stock, par value $0.001 per share."
        )
        assert _extract_shares(text) == 176950987.0

    def test_separate_sentences_per_class(self):
        text = (
            "The number of shares of registrant's Class A Common Stock outstanding as of March 11, 2026 "
            "was 246,564,864. The number of shares of registrant's Class B-1 Common Stock outstanding as "
            "of March 11, 2026 was 37,000,000."
        )
        assert _extract_shares(text) == 283564864.0

    def test_table_format_with_par_value(self):
        text = (
            "Class Number of Shares Outstanding Class A Common Stock, par value $.01 per share "
            "172,172,544 Class 1 Common Stock, par value $.01 per share 25,923"
        )
        assert _extract_shares(text) == 172198467.0

    def test_table_format_shares_outstanding_with_trailing_date_year_trap(self):
        """The real Beasley Broadcast bug: a naive class-prefix pattern
        matched the filing date's own year ('2026') as if it were the
        next class's share count, because the year sits immediately
        before the next class's label in this flattened table layout."""
        text = (
            "Class A Common Stock, $.001 par value, 973,170 Shares Outstanding as of April 1, 2026 "
            "Class B Common Stock, $.001 par value, 833,137 Shares Outstanding as of April 1, 2026"
        )
        assert _extract_shares(text) == 1806307.0

    def test_lone_bare_year_result_is_rejected(self):
        """Defense in depth: even if some future pattern matched a lone
        4-digit number that looks like a calendar year, it must not be
        trusted as a real single-class share count."""
        text = "The registrant had outstanding 2026 Class B Common Stock shares as of some date."
        result = _extract_shares(text)
        assert result != 2026.0

    def test_table_format_without_par_value(self):
        text = (
            "The number of shares outstanding of each class of common stock as of November 19, 2025 was: "
            "Class A common stock, 28,428,416 shares Class B common stock, 3,248,420 shares"
        )
        assert _extract_shares(text) == 31676836.0

    def test_two_class_respectively_with_bare_common_stock_on_one_side(self):
        text = (
            "The number of shares outstanding of the registrant's Common Stock and Class A Common Stock "
            "as of March 13, 2026, were 15,622,386 and 6,455,602, respectively."
        )
        assert _extract_shares(text) == 22077988.0

    def test_units_of_beneficial_interest_trust(self):
        text = "The number of units of beneficial interest outstanding as of March 31, 2026, was 40,000,000."
        assert _extract_shares(text) == 40000000.0

    def test_single_class_there_were_n_shares_outstanding(self):
        text = "As of June 2, 2026, there were 17,615,211 shares outstanding."
        assert _extract_shares(text) == 17615211.0

    def test_single_class_pattern_not_tried_when_class_mentioned_elsewhere_on_page(self):
        """The real safety property: a genuinely multi-class company whose
        specific class-pattern all fail to match must NOT fall through to
        the single-class pattern and silently under-count using an
        unrelated bare number near the word 'outstanding' -- e.g. a
        Class A market-value calculation elsewhere on the page."""
        text = (
            "The aggregate market value was $5 billion based on 10,000,000 shares of Class A common "
            "stock. Elsewhere, there were 999 shares outstanding mentioned in an unrelated context."
        )
        assert _extract_shares(text) is None or _extract_shares(text) != 999.0

    def test_no_match_returns_none(self):
        text = "This filing contains no mention of any share count at all."
        assert _extract_shares(text) is None

    def test_implausibly_small_result_rejected(self):
        text = "There were 5 shares of Class A common stock and 3 shares of Class B common stock outstanding."
        assert _extract_shares(text) is None

    def test_html_and_inline_xbrl_are_stripped_before_matching(self):
        text = (
            "<ix:header>us-gaap:SomeHiddenTag garbage 999999999</ix:header>"
            "<div style=\"display:none\">more hidden garbage 888888888</div>"
            "As of June 2, 2026, there were 17,615,211 shares outstanding."
        )
        assert _extract_shares(text) == 17615211.0
