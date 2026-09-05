import pytest

from scrooner_pipeline.company_master.business_text import (
    clean_visible_text,
    extract_about_text,
    extract_employee_headcount,
    extract_website,
)


@pytest.mark.unit
class TestExtractEmployeeHeadcount:
    """Fixtures below are real sentences pulled live 2026-08-30 from real
    10-Ks (Apple, Microsoft, Costco, ST JOE, Dianthus Therapeutics, Latch,
    Dave & Buster's), not fabricated -- see doc 39 and business_text.py's
    own module docstring for how/why this vocabulary was chosen."""

    def test_apple_full_time_equivalent_phrasing(self):
        text = "As of September 27, 2025, the Company had approximately 166,000 full-time equivalent employees."
        result = extract_employee_headcount(text)
        assert result["headcount"] == 166000
        assert result["is_approximate"] is True

    def test_microsoft_people_synonym(self):
        text = "As of June 30, 2026, we employed approximately 223,000 people on a full-time basis, 121,000 in the U.S."
        result = extract_employee_headcount(text)
        assert result["headcount"] == 223000

    def test_costco_worldwide_phrasing(self):
        text = "At the end of 2025, we employed 341,000 employees worldwide."
        result = extract_employee_headcount(text)
        assert result["headcount"] == 341000
        assert result["is_approximate"] is False

    def test_st_joe_picks_total_not_part_time_subcount(self):
        text = "As of February 23, 2026, we employed 906 full-time employees and 225 part-time and seasonal employees."
        result = extract_employee_headcount(text)
        assert result["headcount"] == 906

    def test_dianthus_picks_total_not_rd_subcount(self):
        text = "As of March 4, 2026, we had 92 employees, all of whom were employed full time and 66 of whom were engaged in research and development activities."
        result = extract_employee_headcount(text)
        assert result["headcount"] == 92

    def test_latch_small_company(self):
        text = "As of December 31, 2025, we had approximately 120 full-time employees, all of which were based in the United States."
        result = extract_employee_headcount(text)
        assert result["headcount"] == 120

    def test_dave_and_busters_team_members_synonym(self):
        text = "As of February 3, 2026, we employed approximately 23,610 team members across both of our brands."
        result = extract_employee_headcount(text)
        assert result["headcount"] == 23610

    def test_generic_culture_sentence_is_not_a_false_positive(self):
        """Real false positive found live: a loose 'any sentence containing
        employ' pattern matched this for Dave & Buster's before the number-
        adjacency requirement was added."""
        text = "Our culture, policies, and labor practices contribute to strong relations with our team members and foster employee engagement."
        assert extract_employee_headcount(text) is None

    def test_blank_check_spac_stock_plan_mention_is_not_a_false_positive(self):
        """Real false positive found live: a blank-check SPAC's only
        'employ' mention is about a future employee incentive plan, not an
        actual headcount -- correctly resolves to None."""
        text = "We may issue additional shares under an employee incentive plan after completion of our initial business combination."
        assert extract_employee_headcount(text) is None

    def test_no_employee_mention_at_all(self):
        assert extract_employee_headcount("This filing discusses our products and market strategy.") is None


@pytest.mark.unit
class TestCleanVisibleText:
    def test_strips_hidden_ix_header_block(self):
        """Real hazard found live: the hidden inline-XBRL header block
        contains tag-context text like 'EmployeeStockMember' that a naive
        strip-and-search would match instead of the real sentence."""
        html = "<ix:header><hidden>us-gaap:EmployeeStockMember 2025-06-30</hidden></ix:header><p>We had 100 employees.</p>"
        result = clean_visible_text(html)
        assert "EmployeeStockMember" not in result
        assert "100 employees" in result

    def test_strips_script_and_style(self):
        html = "<script>var x = 1;</script><style>.a{color:red}</style><p>Real text here.</p>"
        result = clean_visible_text(html)
        assert "var x" not in result
        assert "Real text here." in result

    def test_decodes_html_entities(self):
        """Real bug found live 2026-08-31 (user-reported About text
        quality issue): entities were left as literal text like
        '&#8217;' instead of being decoded to the character they
        represent."""
        html = "<p>The Company&#8217;s Mac &#174; line &amp; iPad &#8226; lineup.</p>"
        result = clean_visible_text(html)
        assert "&#8217;" not in result
        assert "&#174;" not in result
        assert "&amp;" not in result
        assert "Company’s Mac ® line & iPad • lineup." in result


@pytest.mark.unit
class TestExtractAboutText:
    def test_skips_table_of_contents_occurrence(self):
        """Real finding: 'Item 1. Business' appears twice in a 10-K -- once
        in the table of contents, once as the real section heading. Only
        the second occurrence has real body text."""
        text = (
            "Item 1. Business 1 Item 1A. Risk Factors 5 "
            "Item 1. Business Company Background The Company designs and sells widgets. "
            "Item 1A. Risk Factors Our business faces many risks."
        )
        result = extract_about_text(text)
        assert result is not None
        assert "widgets" in result
        assert "Risk Factors" not in result or "Our business faces many risks" not in result

    def test_returns_none_when_only_toc_occurrence_exists(self):
        text = "Item 1. Business 1 Item 1A. Risk Factors 5"
        assert extract_about_text(text) is None

    def test_skips_leading_legal_boilerplate_paragraph(self):
        """Real finding: FTI Consulting's actual 10-K opens Item 1 with a
        defined-terms disclaimer before the real description -- the
        boilerplate must not be what gets stored as the company's About
        text."""
        text = (
            "Item 1. Business 1 "
            'Item 1. Business Unless otherwise indicated or required by the context, when we use the terms "Company," '
            '"FTI Consulting," "we," "us" and "our," we mean FTI Consulting, Inc. '
            "Company Overview General FTI Consulting is a leading global expert firm for organizations facing crisis and transformation. "
            "Item 1A. Risk Factors Our business faces many risks."
        )
        result = extract_about_text(text)
        assert result is not None
        assert "leading global expert firm" in result
        assert "Unless otherwise indicated" not in result

    def test_cuts_to_first_two_sentences_not_a_full_paragraph(self):
        """Real user feedback (2026-08-31): the original extraction kept
        going for a full multi-paragraph block instead of a scannable
        summary. Must stop after 2 real sentences."""
        text = (
            "Item 1. Business 1 "
            "Item 1. Business The Company designs and sells widgets worldwide. "
            "It also offers a subscription service for widget maintenance. "
            "The Company was founded in 1990 and is headquartered in Ohio. "
            "A fourth sentence that must not appear in the result. "
            "Item 1A. Risk Factors Our business faces many risks."
        )
        result = extract_about_text(text)
        assert result is not None
        assert "widgets worldwide" in result
        assert "subscription service" in result
        assert "founded in 1990" not in result
        assert "fourth sentence" not in result

    def test_falls_back_to_char_cut_when_no_sentence_boundary_found(self):
        text = "Item 1. Business 1 " + "Item 1. Business " + ("word " * 300) + "Item 1A. Risk Factors X"
        result = extract_about_text(text)
        assert result is not None
        assert len(result) <= 500


@pytest.mark.unit
class TestExtractWebsite:
    """Fixtures pulled live 2026-08-31 from real 10-Ks, checked before
    writing the pattern -- see the module's own comment above
    _WEBSITE_DOMAIN for why the pattern excludes .gov and doesn't
    require a 'www.' prefix."""

    def test_apple_website_after_investor_relations_mention(self):
        text = (
            "Available Information The Company's reports are available at "
            "investor.apple.com/investor-relations/sec-filings when filed. The Company periodically "
            "provides information on its corporate website, www.apple.com, and its investor relations website."
        )
        assert extract_website(text) == "apple.com"

    def test_microsoft_internet_address_phrasing(self):
        text = "Item 1 AVAILABLE INFORMATION Our Internet address is www.microsoft.com. At our Investor Relations website..."
        assert extract_website(text) == "microsoft.com"

    def test_does_not_pick_secs_own_website_over_the_companys(self):
        """Real false positive found live: a naive www.-prefixed search
        picked 'www.sec.gov' for Latch, Inc. instead of the company's own
        site, because Latch's real site (https://DOOR.com) has no 'www.'
        prefix while the SEC boilerplate mention does."""
        text = (
            "Available Information Our internet website address is https://DOOR.com/investors. "
            "We make available, free of charge, through our website or through the SEC's website at "
            "www.sec.gov, our Annual Reports on Form 10-K."
        )
        assert extract_website(text) == "door.com"

    def test_returns_none_when_no_domain_found(self):
        assert extract_website("This filing discusses our products and market strategy.") is None

    def test_skips_table_of_contents_available_information_entry(self):
        """Real bug found live: Nike's own 10-K lists 'Available
        Information and Websites' as a table-of-contents entry (no domain
        follows it) before the real section further in the document. A
        plain whole-document search matches the TOC line first and
        silently returns None even though the real section exists."""
        text = (
            "Available Information and Websites 7 ITEM 1A. Risk Factors 9 "
            "Item 1. Business Item 1. Business We design and sell athletic footwear. "
            "Available Information Our website is www.nike.com, where investors can find our filings. "
            "Item 1A. Risk Factors Our business faces many risks."
        )
        assert extract_website(text) == "nike.com"
