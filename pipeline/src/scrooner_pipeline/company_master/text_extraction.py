"""Generalized head-parser / sub-parser framework for extracting real
financial-statement values from SEC filing text when the structured XBRL
Company Facts API doesn't have them (dimensional data stripped, tag not
recognized, cover-page-only disclosure, etc.) -- doc 42's Parser 2
(cover-page text) and Parser 3 (rendered-table text), formalized as a
reusable framework rather than one-off regex code duplicated per
concept.

Proven out first on `shares_outstanding_fallback.py`'s 9 real phrasings
(doc 42, 2026-09-03: 23%->64-80% real extraction success after
generalizing from 2 validated companies to a diverse real sample) --
extracted here so future concepts (a bank's interest-income-as-revenue,
a REIT's rental-revenue equivalent, a rendered R*.htm income-statement
table) reuse the same discipline without re-deriving it from scratch.

A HEAD PARSER owns one extraction TARGET (e.g. "shares outstanding from
a 10-K cover page") and holds an ORDERED list of SUB-PARSERS, each one
an independently-tested regex+combine-function for ONE real phrasing.
`run_head_parser` tries each sub-parser in order -- more specific,
structurally-anchored patterns first, looser ones last, since a looser
pattern's false match can crowd out a correct one further down the list
(found live: a flattened HTML table's trailing number can coincidentally
sit right next to the NEXT row's unrelated label, matching a looser
"number near label" pattern before a more specific "number near label
AND a par-value/date anchor" pattern gets a chance) -- applies a shared
plausibility floor/ceiling to whichever one succeeds, and returns
(value, which_sub_parser_name) so callers can log which patterns are
actually earning their keep. That return value is real telemetry for
the loop doc 42 formalized (measure -> sample failures -> generalize ->
re-verify -> ship): if a sub-parser never fires across a full-population
run, it's a candidate to investigate or retire; if one fires constantly,
it's the highest-value pattern to double-check for edge cases first.

NEVER guesses: if no sub-parser matches confidently, or the matched
value fails the plausibility check, returns None. Same "never guess"
discipline as every other stage in this pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from scrooner_pipeline.company_master.business_text import clean_visible_text

_SCALE_HINT_RE = re.compile(r"in thousands", re.IGNORECASE)


@dataclass(frozen=True)
class SubParser:
    """One independently-tested extraction strategy for one real
    phrasing.

    `combine` turns the regex's `finditer` matches into a single float
    (sum for a repeated per-class pattern, a single captured group for a
    "respectively" pattern, etc. -- deliberately a plain function, not a
    fixed "sum vs single" enum, since combining logic genuinely differs
    per real phrasing) or `None` to reject the match entirely (e.g. a
    "respectively" match whose surrounding text never actually says
    "outstanding" nearby, or a bare-year-shaped false positive). Each
    `re.Match` object carries its own `.string` (the full cleaned text
    it matched against), so a `combine` function can inspect context
    around a match without the framework needing a separate hook for it.

    `gate`, if set, is checked against the FULL cleaned text before this
    sub-parser is even tried -- e.g. a single-class fallback pattern
    must only run when no class/series qualifier appears anywhere on
    the page, to avoid ever under-counting a genuine multi-class company
    by matching just its first class as if it were the total.

    `scale_hint_pattern`, if set, is checked in a window immediately
    before the first match -- e.g. "(in thousands)" a few words before a
    share count means the real value is 1,000x the raw digits (found
    live for Block: missing this would have silently produced a value
    1,000x too small, worse than leaving it null since it looks
    plausible)."""

    name: str
    pattern: re.Pattern
    combine: Callable[[list[re.Match]], float | None]
    gate: Callable[[str], bool] | None = None
    scale_hint_lookback_chars: int | None = None


def _apply_scale_hint(clean: str, match_start: int, value: float, lookback_chars: int) -> float:
    window = clean[max(0, match_start - lookback_chars) : match_start]
    if _SCALE_HINT_RE.search(window):
        return value * 1000
    return value


def run_head_parser(
    raw_html: str,
    sub_parsers: list[SubParser],
    *,
    char_limit: int,
    min_plausible: float,
    max_plausible: float,
) -> tuple[float, str] | None:
    """Cleans raw_html once (inline-XBRL/script/style stripped, HTML
    entities decoded -- the same `clean_visible_text` every text-
    extraction module in this project uses, so a fix to that shared
    cleaner benefits every head parser at once), then tries each
    sub-parser in priority order. Returns (value, sub_parser_name) for
    the first plausible match, or None if nothing matched or every
    candidate failed the plausibility check."""
    clean = clean_visible_text(raw_html)[:char_limit]

    for sub_parser in sub_parsers:
        if sub_parser.gate is not None and not sub_parser.gate(clean):
            continue
        matches = list(sub_parser.pattern.finditer(clean))
        if not matches:
            continue
        value = sub_parser.combine(matches)
        if value is None:
            continue
        if sub_parser.scale_hint_lookback_chars is not None:
            value = _apply_scale_hint(clean, matches[0].start(), value, sub_parser.scale_hint_lookback_chars)
        if min_plausible <= value <= max_plausible:
            return value, sub_parser.name

    return None


def looks_like_a_bare_year(total: float, match_count: int, year_min: int = 1990, year_max: int = 2035) -> bool:
    """Defense in depth for any head parser extracting share/dollar
    counts near a class label or a filing date: a SINGLE lone match
    landing exactly in a plausible calendar-year range is inherently
    suspicious, regardless of which sub-parser produced it -- found live
    2026-09-03 (Beasley Broadcast Group): a filing date's own year sat
    immediately next to an unrelated class label in a flattened table,
    and a looser pattern captured it as if it were a real count."""
    return match_count == 1 and year_min <= total <= year_max
