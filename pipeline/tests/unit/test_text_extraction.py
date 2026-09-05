import re

import pytest

from scrooner_pipeline.company_master.text_extraction import SubParser, looks_like_a_bare_year, run_head_parser


@pytest.mark.unit
class TestRunHeadParser:
    def test_first_matching_sub_parser_wins(self):
        parsers = [
            SubParser("first", re.compile(r"first:(\d+)"), lambda m: float(m[0].group(1))),
            SubParser("second", re.compile(r"second:(\d+)"), lambda m: float(m[0].group(1))),
        ]
        result = run_head_parser("second:99", parsers, char_limit=1000, min_plausible=1, max_plausible=1000)
        assert result == (99.0, "second")

    def test_earlier_sub_parser_takes_priority_when_both_match(self):
        parsers = [
            SubParser("first", re.compile(r"first:(\d+)"), lambda m: float(m[0].group(1))),
            SubParser("second", re.compile(r"second:(\d+)"), lambda m: float(m[0].group(1))),
        ]
        result = run_head_parser("first:1 second:2", parsers, char_limit=1000, min_plausible=1, max_plausible=1000)
        assert result == (1.0, "first")

    def test_gate_skips_a_sub_parser_when_false(self):
        parsers = [
            SubParser("gated", re.compile(r"(\d+)"), lambda m: float(m[0].group(1)), gate=lambda text: "allow" in text),
        ]
        assert run_head_parser("123", parsers, char_limit=1000, min_plausible=1, max_plausible=1000) is None
        assert run_head_parser("123 allow", parsers, char_limit=1000, min_plausible=1, max_plausible=1000) == (123.0, "gated")

    def test_combine_returning_none_falls_through_to_next_sub_parser(self):
        parsers = [
            SubParser("rejects", re.compile(r"(\d+)"), lambda m: None),
            SubParser("accepts", re.compile(r"value:(\d+)"), lambda m: float(m[0].group(1))),
        ]
        result = run_head_parser("value:42", parsers, char_limit=1000, min_plausible=1, max_plausible=1000)
        assert result == (42.0, "accepts")

    def test_plausibility_bounds_reject_out_of_range_values(self):
        parsers = [SubParser("only", re.compile(r"(\d+)"), lambda m: float(m[0].group(1)))]
        assert run_head_parser("5", parsers, char_limit=1000, min_plausible=100, max_plausible=1000) is None
        assert run_head_parser("50000", parsers, char_limit=1000, min_plausible=100, max_plausible=1000) is None
        assert run_head_parser("500", parsers, char_limit=1000, min_plausible=100, max_plausible=1000) == (500.0, "only")

    def test_scale_hint_multiplies_when_present_in_lookback_window(self):
        parsers = [
            SubParser("scaled", re.compile(r"value:\s*(\d+)"), lambda m: float(m[0].group(1)), scale_hint_lookback_chars=30),
        ]
        result = run_head_parser("in thousands, value: 5", parsers, char_limit=1000, min_plausible=1, max_plausible=1_000_000)
        assert result == (5000.0, "scaled")

    def test_no_sub_parsers_match_returns_none(self):
        parsers = [SubParser("only", re.compile(r"nomatch(\d+)"), lambda m: float(m[0].group(1)))]
        assert run_head_parser("nothing here", parsers, char_limit=1000, min_plausible=1, max_plausible=1000) is None

    def test_inline_xbrl_and_html_are_cleaned_before_matching(self):
        parsers = [SubParser("only", re.compile(r"value:\s*(\d+)"), lambda m: float(m[0].group(1)))]
        html = '<ix:header>garbage 999</ix:header><div style="display:none">888</div>value: 7'
        result = run_head_parser(html, parsers, char_limit=1000, min_plausible=1, max_plausible=1000)
        assert result == (7.0, "only")


@pytest.mark.unit
class TestLooksLikeABareYear:
    def test_single_match_in_year_range_is_flagged(self):
        assert looks_like_a_bare_year(2026, match_count=1) is True

    def test_multiple_matches_in_year_range_not_flagged(self):
        assert looks_like_a_bare_year(2026, match_count=2) is False

    def test_single_match_outside_year_range_not_flagged(self):
        assert looks_like_a_bare_year(973170, match_count=1) is False
