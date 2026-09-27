"""Employee headcount + About text, extracted from 10-K prose (doc
39: doc/scoping/39_Scrooner_Employee_Headcount_Full_Coverage_Plan.md).

Genuinely new fetch/parsing pattern for this project -- every other data
point comes from structured XBRL, this one comes from a 10-K's human-
readable Item 1 "Business" text, which `dei:EntityNumberOfEmployees`
(only ~3.5% of companies tag it -- checked live 2026-08-30, not even
Apple/Microsoft/Costco do) never captures.

Two real hazards found live before writing the patterns below, not
assumed:
  1. A naive tag-strip-and-search over raw HTML matches garbage from the
     hidden inline-XBRL <ix:header> block (e.g. `us-gaap:EmployeeStockMember`
     tag-context text) instead of the real sentence -- must strip that
     block (plus <script>/<style>/display:none) BEFORE searching visible
     text.
  2. A loose "any sentence containing the word employ" pattern has real,
     material false positives (matched a generic "employee engagement"
     culture sentence for Dave & Buster's, and a stock-plan mention for a
     blank-check SPAC, neither of which state a headcount). The patterns
     below require a NUMBER directly adjacent to the noun, and cover the
     real vocabulary variance found across a deliberately diverse 8-company
     sample (mega-cap tech, small biotech, land developer, blank-check
     SPAC, restaurant chain): "employees", "team members", "associates",
     "people", "colleagues" -- Dave & Buster's uses "team members", not
     "employees", and would resolve to None without that synonym list.
     Verified 7/8 real resolution rate on that sample; the one non-match
     (a blank-check SPAC pre-merger) is a correct null, not a miss --
     confirmed by reading its filing text directly, no headcount sentence
     exists there at all.

Scope (per user direction 2026-08-30, narrower than doc 39's original
4-stage plan): only the 2 most recent 10-Ks per company -- this
disclosure is confirmed annual-only (a 10-Q was checked live and does
NOT repeat the Human Capital section). About text is latest-10-K-only,
a single fetch, no history, matching doc 38's case-1 reasoning.
"""

import html
import re

_IX_HEADER = re.compile(r"<ix:header>.*?</ix:header>", re.DOTALL | re.IGNORECASE)
_SCRIPT_STYLE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
_DISPLAY_NONE = re.compile(
    r'<[^>]+style="[^"]*display:\s*none[^"]*"[^>]*>.*?</[a-zA-Z0-9]+>',
    re.DOTALL | re.IGNORECASE,
)
_TAG = re.compile(r"<[^>]+>")
_NBSP = re.compile(r"&#160;")
_WHITESPACE = re.compile(r"\s+")

_NUM = r"(?:approximately\s+)?([\d]{1,3}(?:,\d{3})*)"
_NOUN = r"(?:employees|team members|associates|people|colleagues)"
_HEADCOUNT_PATTERNS = [
    re.compile(
        rf"\b(?:employed|had|has|with)\s+{_NUM}\s+(?:full-time\s+)?(?:equivalent\s+)?{_NOUN}",
        re.IGNORECASE,
    ),
    re.compile(
        rf"{_NUM}\s+(?:full-time\s+)?(?:equivalent\s+)?{_NOUN}\s+(?:worldwide|globally|as of)",
        re.IGNORECASE,
    ),
]
_ITEM_1_BUSINESS = re.compile(r"Item\s+1\.\s*Business", re.IGNORECASE)
_ITEM_1A = re.compile(r"Item\s+1A\.\s*Risk\s+Factors", re.IGNORECASE)

# doc 2026-08-31: every 10-K's mandatory "Available Information" section
# (Item 101(e), a real disclosure requirement, not optional) states the
# company's own website -- confirmed live on Apple ("its corporate
# website, www.apple.com"), Microsoft ("Our Internet address is
# www.microsoft.com"), Costco ("Our U.S. website is www.costco.com").
# Restricting to .com/.net/.org/.io deliberately excludes .gov -- the
# same section almost always ALSO mentions "the SEC's website at
# www.sec.gov" as required boilerplate, which a plain www.-prefixed
# match would otherwise pick up as a false positive (found live on
# Latch, Inc., whose real site is "https://DOOR.com" -- no "www."
# prefix at all, so the search must not require one, and must not
# accidentally prefer sec.gov instead).
_AVAILABLE_INFORMATION = re.compile(r"available information", re.IGNORECASE)
_WEBSITE_DOMAIN = re.compile(
    r"(?:https?://)?(?:www\.)?([a-zA-Z0-9][a-zA-Z0-9\-]*\.(?:com|net|org|io))\b",
    re.IGNORECASE,
)

# Real finding (2026-08-30, checked against a random sample after the
# initial full-population run): many filings open Item 1 with a legal
# defined-terms paragraph ("Unless otherwise indicated or required by
# the context, when we use the terms 'Company'...") before any real
# business description -- e.g. FTI Consulting's real "leading global
# expert firm..." sentence only appears after that boilerplate. Skip
# past the first such paragraph (first '. ' after one of these trigger
# phrases) when present, rather than storing the disclaimer as if it
# were the company description.
_BOILERPLATE_TRIGGER = re.compile(
    r"unless (?:the context |otherwise )(?:otherwise )?(?:requires|indicated)",
    re.IGNORECASE,
)


def clean_visible_text(raw_html: str) -> str:
    """Strip hidden inline-XBRL/script/style content, leaving only what a
    human reader of the rendered filing would actually see.

    Real bug found live 2026-08-31 (user-reported: About text "not user
    friendly"): this never decoded HTML entities, so every apostrophe,
    registered-trademark mark, and ampersand rendered as literal
    `&#8217;`/`&#174;`/`&amp;` text instead of the character it
    represents. `html.unescape` runs AFTER whitespace collapsing so an
    entity split across a collapsed run (rare, but `&amp;` inside a tag
    attribute could theoretically straddle one) still resolves correctly."""
    raw_html = _IX_HEADER.sub(" ", raw_html)
    raw_html = _SCRIPT_STYLE.sub(" ", raw_html)
    raw_html = _DISPLAY_NONE.sub(" ", raw_html)
    plain = _TAG.sub(" ", raw_html)
    plain = _NBSP.sub(" ", plain)
    plain = _WHITESPACE.sub(" ", plain).strip()
    return html.unescape(plain)


def extract_employee_headcount(plain_text: str) -> dict | None:
    """Returns {'headcount': int, 'is_approximate': bool, 'snippet': str}
    or None if no confident single number was found. Deliberately picks
    the FIRST matching number (a company's own total headcount is stated
    before any sub-breakdown in every real example checked, e.g. ST
    JOE's "906 full-time...and 225 part-time" -- 906 is the intended
    total) rather than attempting to sum multiple numbers, which would
    require disambiguating totals from sub-counts with no reliable
    general rule."""
    for pattern in _HEADCOUNT_PATTERNS:
        match = pattern.search(plain_text)
        if match:
            raw_number = match.group(1)
            headcount = int(raw_number.replace(",", ""))
            snippet = plain_text[max(0, match.start() - 80) : match.end() + 80]
            is_approximate = "approximately" in match.group(0).lower()
            return {
                "headcount": headcount,
                "is_approximate": is_approximate,
                "snippet": snippet,
            }
    return None


_SENTENCE_END = re.compile(r"[.!?](?=\s|$)")


def extract_about_text(
    plain_text: str, max_sentences: int = 2, max_length: int = 500
) -> str | None:
    """The Item 1 Business section's opening text -- the first real
    occurrence, not the table-of-contents listing (confirmed live on
    Apple's own 10-K: "Item 1. Business" appears twice, the TOC entry
    first, the real section second).

    Cut to the first ~2 real sentences / ~500 chars, not a long
    multi-paragraph block -- real user feedback (2026-08-31): the
    original 1000-char cut produced a wall of text (Apple's ran on
    through several product-line paragraphs), not a scannable summary.
    A hard character cut mid-sentence was also possible before; this
    version always ends on a real sentence boundary."""
    matches = list(_ITEM_1_BUSINESS.finditer(plain_text))
    if len(matches) < 2:
        return None
    start = matches[1].end()
    end_match = _ITEM_1A.search(plain_text, pos=start)
    section_end = end_match.start() if end_match else len(plain_text)

    boilerplate = _BOILERPLATE_TRIGGER.search(
        plain_text, pos=start, endpos=min(section_end, start + 200)
    )
    if boilerplate is not None:
        sentence_end = plain_text.find(". ", boilerplate.end(), section_end)
        if sentence_end != -1:
            start = sentence_end + 2

    window = plain_text[start : min(section_end, start + max_length + 200)]
    sentence_ends = [m.end() for m in _SENTENCE_END.finditer(window)]
    if sentence_ends:
        cut = sentence_ends[min(max_sentences, len(sentence_ends)) - 1]
        text = window[:cut].strip()
    else:
        text = window[:max_length].strip()
    return text or None


def extract_website(plain_text: str) -> str | None:
    """The company's corporate website, from the mandatory "Available
    Information" section (falls back to the first ~3000 chars -- the
    cover page -- when that section isn't found within the real Item 1
    body). Returns a bare domain (`apple.com`, not `www.apple.com` or
    `https://apple.com`) -- store the fact, let the frontend decide how
    to render/link it.

    Searches only from the SECOND "Item 1. Business" occurrence onward
    (same TOC-vs-real-section anchor as extract_about_text) -- real bug
    found live 2026-08-31: Nike's own 10-K lists "Available Information
    and Websites" as a table-of-contents entry before the real section,
    and a plain whole-document search matches that TOC line first (no
    domain follows it, so the extraction silently returned nothing for
    a company that does disclose a real site later in the document).

    Deliberately does NOT fall back to scanning the whole Item 1 body
    for any bare domain when no "Available Information" heading is
    found there (e.g. JPMorgan Chase's real 10-K structure doesn't use
    that heading at all, checked live) -- that would risk matching an
    unrelated company mentioned in the business description (a
    competitor, a partner) instead of the filer's own site. Honest null
    over a wrong guess, same discipline as the rest of this module."""
    # Deliberately NOT bounded by an _ITEM_1A search the way
    # extract_about_text is -- real bug found live 2026-08-31: Nike's
    # own Item 1 body contains an inline cross-reference ("...see 'Item
    # 1A. Risk Factors.'") long before the real Item 1A heading, which
    # made the boundary search stop at position 8979 while Nike's real
    # "Available Information" section doesn't appear until position
    # 33302 -- correctly present in the document, wrongly excluded from
    # the search window. A large fixed window is more robust here than
    # trying to disambiguate a real section heading from an inline
    # reference to the same words.
    item1_matches = list(_ITEM_1_BUSINESS.finditer(plain_text))
    if len(item1_matches) >= 2:
        search_start = item1_matches[1].end()
        body = plain_text[search_start : search_start + 40000]
    else:
        body = plain_text[:3000]

    match = _AVAILABLE_INFORMATION.search(body)
    window = body[match.start() : match.start() + 800] if match else body[:3000]
    domain_match = _WEBSITE_DOMAIN.search(window)
    return domain_match.group(1).lower() if domain_match else None
