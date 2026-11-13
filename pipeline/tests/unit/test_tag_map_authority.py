"""One authoritative copy per disagreeing group of a tag-map company (Dhairya ruling 2026-11-12): rounding class ->
the most precise copy, restatement class -> the latest accepted filing. Pure."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from scrooner_pipeline.normalizer.conflict_latest_filed import (
    RULE_TAGMAP,
    RULE_TAGMAP_PRECISION,
    TagMapCopy,
    choose_tag_map_winner,
)


def copy(fid, value, acc, day, dcml=None, eligible=True, amendment=False):
    at = datetime(2000 + day // 1000, 1, 1, tzinfo=timezone.utc).replace(
        day=1 + day % 28
    )
    return TagMapCopy(
        fid,
        Decimal(value),
        acc,
        at,
        date(at.year, 1, at.day),
        amendment,
        eligible,
        dcml,
    )


def test_rounding_class_the_most_precise_copy_wins_whichever_filing_printed_it():
    # PANW G&A Q2 FY2015: 27,000,000 at -6 (later filing) vs 27,023,000 at -3 (earlier filing)
    got = choose_tag_map_winner(
        [copy(1, "27023000", "A1", 15000, -3), copy(2, "27000000", "A2", 16000, -6)]
    )
    assert got == (1, RULE_TAGMAP_PRECISION)


def test_restatement_class_the_latest_accepted_copy_wins():
    # MSFT S&M FY2016: 14,697 (FY2016/FY2017 10-Ks) vs 14,635 restated in the FY2018 10-K, all at -6
    copies = [
        copy(1, "14697000000", "A16", 16000, -6),
        copy(2, "14697000000", "A17", 17000, -6),
        copy(3, "14635000000", "A18", 18000, -6),
    ]
    assert choose_tag_map_winner(copies) == (3, RULE_TAGMAP)


def test_a_difference_beyond_the_coarser_precision_is_a_restatement_not_rounding():
    # META G&A 2016 Q1: 365 vs 366 ($M, both at -6): one full unit apart -> latest wins
    got = choose_tag_map_winner(
        [copy(1, "365000000", "A1", 16000, -6), copy(2, "366000000", "A2", 17000, -6)]
    )
    assert got == (2, RULE_TAGMAP)


def test_unknown_precision_falls_to_the_latest_accepted_copy():
    got = choose_tag_map_winner(
        [copy(1, "27023000", "A1", 15000, -3), copy(2, "27000000", "A2", 16000, None)]
    )
    assert got == (2, RULE_TAGMAP)


def test_ineligible_copies_count_but_never_win_and_ties_go_to_the_lower_accession():
    assert choose_tag_map_winner(
        [copy(1, "100", "A1", 15000), copy(2, "98", "A2", 16000, eligible=False)]
    ) == (1, RULE_TAGMAP)
    assert choose_tag_map_winner(
        [copy(1, "100", "B", 15000), copy(2, "98", "A", 15000)]
    ) == (2, RULE_TAGMAP)
    assert choose_tag_map_winner([copy(1, "100", "A", 15000, eligible=False)]) is None
