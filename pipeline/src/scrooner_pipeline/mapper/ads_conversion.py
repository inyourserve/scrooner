"""NA-15 ``mcap.ads_conversion@1``: market cap for an ADS-priced company, corrected by the filed
ADS ratio, or hidden (data-team/strategy/team/WO-ADS-RATIO-AND-MULTICLASS-2026-10-22.md).

The price in ``core.market_price_alpaca`` is per ADS; every share fact we store is per ORDINARY
share (cover and balance sheet), and so is EPS and DPS. Hence
    market cap = ordinary shares outstanding / ratio x ADS price
    P/E (ADS price / EPS per ordinary share) is too small by the ratio:  corrected = stored / ratio
    dividend yield (DPS per ordinary share / ADS price) is too small by the ratio: corrected = stored x ratio
Market-cap ratios scale with the market-cap factor.

Default is HIDE. A value is produced only when ALL hold: the rule flag is on; the company is in
ADS_TABLE with a FILING-CHECKED ratio and no hold; it is not a foreign private issuer (KZIA, SCNI:
20-F filers, V1 scope is the Chief's call, never computed here); an ordinary share count exists in
the allowed tags; no ratio change took effect after that count's filing date (AKTX moved 2,000 to
80,000 on 2026-03-31, so the 10-K cover filed 2026-03-30 is not usable); the count is not from
before the ordinary-share basis date (ZLAB's 1-to-10 subdivision, 2022-03-30).

Never used as the share count: weighted-average counts (the RPAY/TBLA mechanism), an ADR-member
cover fact (AMRN: allowed tags are the balance-sheet tag only), or a count that includes treasury
shares (DBVT: held).

Evidence: ratios and dates are FILING-CHECKED in the card (section 1); SLN's ratio history and
GPCR's exact IPO date are not (the effective_from there is a floor, labelled in ``evidence``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import psycopg

RULE_ADS = "mcap.ads_conversion@1"
EARLIEST = date(2000, 1, 1)

REASON_UNVERIFIED = "ads_ratio_unverified"
REASON_CHANGED = "ads_ratio_changed_since_source"
REASON_NO_COUNT = "ads_share_count_unavailable"
REASON_TREASURY = "ads_treasury_basis_unknown"
REASON_FOREIGN = "ads_foreign_filer_scope"

CS = ("CommonStockSharesOutstanding", "EntityCommonStockSharesOutstanding")


@dataclass(frozen=True)
class AdsEntry:
    ticker: str
    changes: tuple[
        tuple[date, int], ...
    ]  # (effective date, ordinary shares per ADS), ascending
    count_tags: tuple[str, ...] = CS
    basis_from: date | None = (
        None  # ordinary counts before this date are on another basis
    )
    hold: str | None = None  # reason code; never converted
    foreign: bool = False
    evidence: str = ""

    @property
    def ratio(self) -> int:
        return self.changes[-1][1]


ADS_TABLE: dict[str, AdsEntry] = {
    "0001541157": AdsEntry(
        "AKTX",
        ((date(2023, 8, 17), 2000), (date(2026, 3, 31), 80000)),
        evidence="FC 10-Q 0001493152-26-037730 cover and Note 1; 10-K 0001493152-26-013664 Item 5",
    ),
    "0001704292": AdsEntry(
        "ZLAB",
        ((date(2022, 3, 30), 10),),
        count_tags=("CommonStockSharesOutstanding",),
        basis_from=date(2022, 3, 30),
        evidence="FC 10-Q 0001628280-26-053793 cover; subdivision 10-K 0001628280-23-005832",
    ),
    "0000897448": AdsEntry(
        "AMRN",
        ((date(2025, 4, 11), 20),),
        count_tags=("CommonStockSharesOutstanding",),  # never the ADR-member cover fact
        evidence="FC 10-Q 0001193125-26-323845 cover and Note 6; 10-K 0001193125-26-085818",
    ),
    "0001888886": AdsEntry(
        "GPCR",
        ((date(2023, 2, 1), 3),),
        evidence="FC 10-Q 0001104659-26-092057 cover; 10-K 0001104659-26-020562 Note 1 (IPO Feb 2023, day not read)",
    ),
    "0001479615": AdsEntry(
        "SLN",
        ((EARLIEST, 3),),
        evidence="FC 10-Q 0001193125-26-341248 cover; ratio history not read (EARLIEST is a floor)",
    ),
    "0001613780": AdsEntry(
        "DBVT",
        ((date(2024, 11, 29), 5),),
        hold=REASON_TREASURY,
        evidence="FC 10-Q 0001628280-26-048453 cover: count includes treasury shares",
    ),
    "0001075880": AdsEntry(
        "KZIA",
        ((date(2025, 4, 17), 500),),
        foreign=True,
        evidence="FC 20-F 0001193125-25-272284; foreign private issuer, Chief to rule scope",
    ),
    "0001611747": AdsEntry(
        "SCNI",
        ((date(2024, 5, 21), 4000),),
        foreign=True,
        evidence="FC 20-F 0001213900-26-038011; foreign private issuer, Chief to rule scope",
    ),
}


@dataclass(frozen=True)
class CountObs:
    value: Decimal
    as_of: date
    filing_date: date
    tag: str


@dataclass(frozen=True)
class AdsDecision:
    kind: str  # "hide" | "convert"
    reason: str | None = None
    ratio: Decimal | None = None
    shares: Decimal | None = None


def ratio_at(entry: AdsEntry, d: date) -> int | None:
    cur = None
    for eff, ratio in entry.changes:
        if eff <= d:
            cur = ratio
    return cur


def decide(
    cik: str, obs: CountObs | None, *, conversion_on: bool
) -> AdsDecision | None:
    entry = ADS_TABLE.get(cik)
    if entry is None:
        return None
    if entry.foreign:
        return AdsDecision("hide", REASON_FOREIGN)
    if not conversion_on:
        return AdsDecision("hide", REASON_UNVERIFIED)
    if entry.hold:
        return AdsDecision("hide", entry.hold)
    if obs is None:
        return AdsDecision("hide", REASON_NO_COUNT)
    if obs.tag not in entry.count_tags:
        return AdsDecision("hide", REASON_NO_COUNT)
    if ratio_at(entry, obs.filing_date) != entry.ratio:
        return AdsDecision("hide", REASON_CHANGED)
    if entry.basis_from is not None and obs.as_of < entry.basis_from:
        return AdsDecision("hide", REASON_CHANGED)
    return AdsDecision("convert", None, Decimal(entry.ratio), obs.value)


HIDDEN_BY_ADS = (
    "market_cap",
    "price_to_sales",
    "price_to_book",
    "fcf_yield",
    "trailing_pe",
    "dividend_yield",
)


def apply_decision(
    decision: AdsDecision,
    stored: dict[str, Decimal | None],
    *,
    old_shares: Decimal | None,
    market_cap_fact_ids: set[int],
    pe_fact_ids: set[int],
) -> dict[str, tuple[Decimal | None, str | None]]:
    """name -> (new value, null reason). Only names present in ``stored`` are returned."""
    out: dict[str, tuple[Decimal | None, str | None]] = {}
    if decision.kind == "hide":
        reason = f"guard:{decision.reason}"
        return {n: (None, reason) for n in HIDDEN_BY_ADS if n in stored}
    assert decision.ratio is not None and decision.shares is not None
    old_mc = stored.get("market_cap")
    if old_mc is None or not old_shares:
        return {
            n: (None, f"guard:{REASON_NO_COUNT}") for n in HIDDEN_BY_ADS if n in stored
        }
    new_mc = old_mc * (decision.shares / decision.ratio) / old_shares
    f = new_mc / old_mc if old_mc else None
    for n in HIDDEN_BY_ADS:
        v = stored.get(n)
        if n not in stored or v is None:
            continue
        if n == "market_cap":
            out[n] = (new_mc, None)
        elif f is None:
            out[n] = (None, f"guard:{REASON_NO_COUNT}")
        elif n in ("price_to_sales", "price_to_book"):
            out[n] = (v * f, None)
        elif n == "fcf_yield":
            out[n] = (v / f, None)
        elif n == "trailing_pe":
            from_mcap = bool(market_cap_fact_ids & pe_fact_ids)
            out[n] = (v * f if from_mcap else v / decision.ratio, None)
        elif n == "dividend_yield":
            out[n] = (v * decision.ratio, None)
    return out


def load_count(
    conn: psycopg.Connection, company_id: int, entry: AdsEntry
) -> CountObs | None:
    """Latest authoritative undimensioned ordinary-share count in the allowed tags."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.value, p.end_date, fl.filing_date, co.tag
            from core.fact f
            join core.concept co on co.id = f.concept_id and co.tag = any(%s)
            join core.period p on p.id = f.period_id
            join core.filing fl on fl.id = f.filing_id
            where f.company_id = %s and f.is_authoritative and f.value > 0
            order by p.end_date desc, fl.filing_date desc, f.id desc
            limit 1
            """,
            (list(entry.count_tags), company_id),
        )
        row = cur.fetchone()
    return CountObs(row[0], row[1], row[2], row[3]) if row else None


def decide_for_company(
    conn: psycopg.Connection, company_id: int, cik: str, *, conversion_on: bool
) -> AdsDecision | None:
    entry = ADS_TABLE.get(cik)
    if entry is None:
        return None
    obs = None
    if conversion_on and not entry.foreign and not entry.hold:
        obs = load_count(conn, company_id, entry)
    return decide(cik, obs, conversion_on=conversion_on)


# ---------------------------------------------------------------- cover-text ratio parser (census input)
_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}  # fmt: skip
_MULT = {"hundred": 100, "thousand": 1000}
_RATIO = re.compile(
    r"representing\s+(?:the\s+right\s+to\s+receive\s+)?(?P<n>[^;]*?)\s+ordinary\s+shares?\b",
    re.I,
)


def _words_to_number(text: str) -> Decimal | None:
    total, current = 0, 0
    seen = False
    for tok in re.split(r"[\s-]+", text.lower().strip()):
        if tok in _WORDS:
            current += _WORDS[tok]
            seen = True
        elif tok in _MULT:
            current = max(current, 1) * _MULT[tok]
            seen = True
            if _MULT[tok] == 1000:
                total += current
                current = 0
        elif tok in ("and", ""):
            continue
        else:
            return None
    return Decimal(total + current) if seen else None


def parse_ads_ratio(security_title: str) -> Decimal | None:
    """Ordinary shares per ADS from a ``dei:Security12bTitle``; None unless it is a depositary
    share title with a parseable ratio (warrants, rights and preferred titles return None)."""
    if "depositary" not in security_title.lower():
        return None
    m = _RATIO.search(security_title)
    if not m:
        return None
    raw = m.group("n").strip()
    paren = re.search(r"\(([\d,]+)\)", raw)
    if paren:
        return Decimal(paren.group(1).replace(",", ""))
    frac = re.search(r"\((\d+)/(\d+)\)", raw)
    if frac:
        return Decimal(int(frac.group(1))) / Decimal(int(frac.group(2)))
    plain = raw.replace(",", "")
    if re.fullmatch(r"\d+(\.\d+)?", plain):
        return Decimal(plain)
    return _words_to_number(re.sub(r"\(.*?\)", "", raw))
