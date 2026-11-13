"""S6: the second prior column of a 10-K (its third printed year) bridges an era for a duration only.

GEV (first 10-K FY2024, spun from GE 2024-04, 0001996810-25-000011): the income and cash-flow statements print
FY2022 as well, a balance sheet prints two years. The era extension used to stop one year back and left
FY2022 a no_public_filing_for_period reason although the first 10-K prints the column."""

from test_era_extend import _cmp, _span, acc


def test_third_printed_year_of_a_flow_is_bridged():
    s = _cmp(2024, {2024: [2024, 2023, 2022]})
    assert _span(s) == [
        ("2022-01-01", "2022-12-31", acc(24)),
        ("2023-01-01", "2023-12-31", acc(24)),
    ]


def test_an_instant_is_not_bridged_three_years_back():
    both = {2024: "instant", 2023: "instant", 2022: "instant"}
    assert _span(_cmp(2024, {2024: [2024, 2023, 2022]}, kinds=both)) == [
        ("2023-01-01", "2023-12-31", acc(24)),
    ]
    only_2022 = _cmp(2024, {2024: [2024, 2023, 2022]}, kinds={2022: "instant"})
    assert _span(only_2022) == [("2023-01-01", "2023-12-31", acc(24))]


def test_a_two_column_10k_stops_at_one_year_back():
    s = _cmp(2024, {2024: [2024, 2023]})
    assert _span(s) == [("2023-01-01", "2023-12-31", acc(24))]
