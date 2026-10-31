"""One split re-base pass: per-share and share-count history on one share
basis (WO-22 / WO-2 item 6, tickets SB-2..SB-5; design
data-team/strategy/team/WO-REVIEW-period-engineer.md section 2; rule
`split.event_basis@1`, default OFF).

Principle (design 2.2): a share basis belongs to a FILING, not to a period.
Every number in one filing is on that filing's own basis, so the factor that
converts a value to today's basis is a property of its SOURCE FILING DATE:

    factor_to_current(F) = product of confirmed split ratios whose
                           basis_date > F.filing_date

A value is never divided because its PERIOD ends before a split (the old
`stock_splits.py` test): a value filed after the split is already re-based
(GOOG Q2 2022 diluted EPS 1.21 in 10-Q 0001652044-22-000071, filed
2022-07-27 after the 2022-07-15 20:1 split; WMT FY2024 0000104169-24-000056).

Events come only from filings, never a vendor, and are identified by
(ratio, observed basis boundary), never by a day window (GOOG's 20:1 sits in
company_stock_split twice, 2022-02-01 and 2022-07-15; NVDA's 4:1 twice, 46
days apart). Evidence kinds (migration 0099 `split_event.evidence_kinds`):

- ratio_fact: StockholdersEquityNoteStockSplitConversionRatio(1) on instant
  AND duration contexts (NVDA 2024 10:1 and ODFL 2020 3:2 exist only on
  duration contexts), classified by stock_splits._classify.
- filed_pair: one tag + period filed in two consecutive periodic filings
  whose values differ by exactly one clean ratio k within rounding (AAPL
  FY2018 diluted EPS 11.91 in 0000320193-19-000119 vs 2.98 in
  0000320193-20-000096).
- share_step: in the filing-dated share-count series, one step of a clean
  ratio between two consecutive filings.

`confirmed` needs two kinds; one kind is `review`, which never re-bases and
hides the cells of the filings it would touch. A share step alone is never a
split (ledger row 113: INCY tender, STE acquisition, DOCU IPO conversion):
a step-only or disclosure-only candidate that ratio-1 filed pairs span is
rejected.

Company invariant (design 2.5): every filed pair must equal
factor(F_old)/factor(F_new) within rounding. A pair whose ratio is a clean
basis change that our factors do not explain hides every per-share and share
cell of that company (`basis_review`), so a double count can never be shown
even through a detector bug.

Cells (design 2.8): candidates are periodic-form, non-derived facts of the
base concept's mapped tags (first_match by priority) in the right unit, each
converted with its own filing's factor. All agree within rounding -> the
LATEST filing's converted value (a re-presented post-split value is filed
evidence and beats our division). Disagree -> hidden with a reason
(`basis_conflict` when the copies sit on different bases,
`restated_between_filings` otherwise). Copies come from every periodic copy
of the period, authoritative or not: Stage 2e marks every copy of a
split-re-presented period non-authoritative because the copies differ by
the ratio; after conversion they are the same economic value, and a
remaining disagreement hides the cell. Derived facts are never candidates
(RU-1: per-share values are not derived).

Writes (mode `on` only) go through mapper/canonical_archive (archive then
replace, one transaction, `restore_run` undoes a run). Mode `dry_run`
computes and returns the proposed cells and writes nothing. Mode `off`
issues no query at all.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_HALF_EVEN, Decimal
from fractions import Fraction

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.common.derivation_policy import is_periodic_form
from scrooner_pipeline.corporate_actions.stock_splits import (
    SPLIT_RATIO_TAGS,
    _classify,
)

RULE_ID = "split.event_basis@1"
# RU-1 owns "per-share values are not derived". Until that rule is on, a cell
# whose only source is a derived fact is left exactly as it is: this pass
# re-bases filed values and never ships RU-1 in pieces.
RU1_RULE_ID = "pershare.never_derive@1"
DETECTOR_VERSION = "share_basis.detector.v1"
BASIS_VERSION = "share_basis.basis.v1"
REASON_CODE = "split_rebase_v1"

PER_SHARE = "per_share"
SHARES = "shares"
UNIT_BY_KIND = {PER_SHARE: "usd/shares", SHARES: "shares"}

# resolved (display) concept -> (kind, base concept whose mapped tags feed it)
TARGETS: dict[str, tuple[str, str]] = {
    "diluted_eps_resolved": (PER_SHARE, "diluted_eps"),
    "basic_eps_resolved": (PER_SHARE, "basic_eps"),
    "dividends_per_share_resolved": (PER_SHARE, "dividends_per_share"),
    "shares_outstanding_resolved": (SHARES, "shares_outstanding"),
}

# Tags read only as basis evidence (filed pairs). Weighted averages are
# re-presented after a split like EPS, so they are good pair evidence.
EVIDENCE_PER_SHARE_TAGS = (
    "EarningsPerShareBasic",
    "EarningsPerShareDiluted",
    "EarningsPerShareBasicAndDiluted",
    "CommonStockDividendsPerShareDeclared",
    "CommonStockDividendsPerShareCashPaid",
)
EVIDENCE_SHARE_TAGS = (
    "CommonStockSharesOutstanding",
    "WeightedAverageNumberOfSharesOutstandingBasic",
    "WeightedAverageNumberOfDilutedSharesOutstanding",
)
# The filing's own current share count, in preference order.
# The filing's own current share count, in preference order; basic weighted
# average shares last, for filers whose cover and balance-sheet counts are
# class-dimensioned or absent (CVNA's 2026 5:1 forward split shows only as
# WASO 137.6M -> 717.7M; Verifier run 4).
SERIES_TAGS = (
    "EntityCommonStockSharesOutstanding",
    "CommonStockSharesOutstanding",
    "WeightedAverageNumberOfSharesOutstandingBasic",
)

# Clean split ratios (new shares per old share). 3:2 and 5:4 are real
# (ODFL 2010/2012/2020 3-for-2, 10-Q 0001564590-20-021054 R16; ledger 109).
_FORWARD = [Fraction(5, 4), Fraction(3, 2), Fraction(5, 2)] + [
    Fraction(k) for k in (2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 50, 100)
]
_REVERSE = [
    Fraction(1, k)
    for k in (
        2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 35, 40, 50, 60, 75, 80,
        100, 150, 200, 250, 300, 400, 500, 1000,
    )
]  # fmt: skip
CLEAN_RATIOS: tuple[Fraction, ...] = tuple(_FORWARD + _REVERSE)
ONE = Fraction(1)
# A share count that moves by exactly 1000x is a scale error (thousands vs
# units), not a split: AAPL 10-Q 0001193125-14-157311 tags 899,213 shares at
# 2013-09-28 where 0001193125-14-024487 tags 899,213,000 (FILING-CHECKED in
# our facts; ledger row 88 RPAY/TBLA scale="3"). Never split evidence for
# share counts; such a copy is dropped from a share cell's candidates.
SHARE_SCALE_RATIOS: tuple[Fraction, ...] = (
    Fraction(1000),
    Fraction(1, 1000),
    Fraction(10**6),
    Fraction(1, 10**6),
)

# Share counts at different dates move with issuance and buybacks; a clean
# step must be within this relative band of k (ASSUMED 4%: AAPL Q3->Q4 FY2020
# is 0.6% off 4x; a 25% issuance stays clear of 5:4 only by being off 1.0).
SHARE_STEP_REL_TOL = Decimal("0.05")
# Per-share values are reported to at least cents (ASSUMED): a stored "3" is
# treated as 3.00, never as +-0.5.
PER_SHARE_MIN_DECIMALS = 2
# Share counts are rounded to at most millions.
SHARES_MAX_UNIT_EXP = 6
# A same-ratio disclosure belongs to an observed event within this distance
# (lesson 74: merge by ratio and event, not a 45-day window).
DISCLOSURE_MERGE_DAYS = 400
DISCLOSURE_WINDOW_PAD = timedelta(days=30)
# A filing within this many days of a basis_date with no share count of its
# own cannot be placed on either side (design 2.6).
BOUNDARY_REVIEW_DAYS = 30
# Two or more ratio-1 filed pairs spanning a candidate refute it.
REFUTE_MIN_PAIRS = 2
OUTPUT_QUANTUM = Decimal("1e-10")
# A per-share copy re-presented after a split can be a sum of up to four
# rounded quarters (AAPL FY2013 DPS: 11.40 in 0001193125-13-416534 is 1.6286
# after the 7:1 split; the FY2014 10-K 0001193125-14-383437 re-presents 1.64 =
# 0.38+0.38+0.44+0.44). Comparing copies on DIFFERENT bases allows this many
# extra half-units of the per-share minimum unit (0.015 at cents).
REPRESENTATION_SLACK_HALF_UNITS = 3

# Cell statuses / hidden reasons.
SHOWN = "shown"
HIDE_BASIS_REVIEW = "basis_review"
HIDE_BASIS_CONFLICT = "basis_conflict"
HIDE_RESTATED = "restated_between_filings"
HIDE_COMPANY_INVARIANT = "basis_review_company_invariant"
HIDE_NO_FILED_SOURCE = "no_filed_source"
HIDE_LABEL_ERROR = "quarter_equals_year_label_error"
HIDE_DPS_BASIS = "dividend_basis_pending"
HIDE_UNITS_SCALE = "units_scale_suspect"
HIDE_ZERO_SHARES = "zero_share_count_filed"
FY_RATE_TOL = Decimal("0.005")
HIDE_DPS_INVALID = "dividend_per_share_invalid"
HIDE_QTR_YTD = "quarter_equals_ytd_context_error"
HIDE_EPS_PAIR = "eps_basic_diluted_impossible"
# A DPS value this many times the company's median DPS of the same series
# (or 1/this) is a units error in its filing (VICI 262,500 for 0.2625 in
# 10-Q 0001705696-18-000086; SWX 2,480; ROST 255; HL 0.25 vs 0.0025).
DPS_SCALE_SUSPECT_RATIO = Decimal(50)
DPS_SCALE_MIN_OTHERS = 3

# Restatement policy for a period whose copies disagree on the SAME basis
# (no split between them): "hide" is design 2.8 (accepted in doc 49). The
# restatement display basis itself is open (doc 49 item 12); "leave" would
# keep today's cell untouched. Changing this is a Standardization Lead call.
RESTATEMENT_POLICY = "hide"

# One dividend basis per COMPANY while AC-24 (declared vs paid) is open
# (Verifier run 5): see company_dividend_basis / _one_dividend_basis.

HIDDEN_REASON_TEXT = {
    HIDE_BASIS_REVIEW: "share basis under review (a possible split is not confirmed by two kinds of filing evidence)",
    HIDE_BASIS_CONFLICT: "filed copies disagree after converting each to the current share basis",
    HIDE_RESTATED: "filed copies of this period disagree (restated between filings)",
    HIDE_COMPANY_INVARIANT: "share basis under review (filed comparatives contradict the split history)",
    HIDE_NO_FILED_SOURCE: "not filed separately in a 10-K or 10-Q (per-share values are not derived)",
    HIDE_LABEL_ERROR: "the filed quarter equals the full-year value of the same filing (label error)",
    HIDE_DPS_BASIS: "dividend basis pending (declared vs paid, AC-24): this series mixes both",
    HIDE_UNITS_SCALE: "filed value looks off by a units scale (thousands or millions)",
    HIDE_ZERO_SHARES: "the filing reports zero shares outstanding",
    HIDE_DPS_INVALID: "dividend per share fails a same-filing check (sign, paid, quarters vs year)",
    HIDE_EPS_PAIR: "basic and diluted EPS of this period cannot both be right (diluted above a positive basic, positive beside a loss, or a units scale apart)",
    HIDE_QTR_YTD: "the filed quarter equals the year-to-date value of the same filing although an earlier quarter paid a dividend",
}


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class SourceFact:
    fact_id: int
    tag: str
    unit: str
    period_id: int
    start_date: date | None
    end_date: date
    period_type: str
    value: Decimal
    filing_id: int
    filing_date: date
    form: str
    accession: str
    is_derived: bool
    is_authoritative: bool

    @property
    def usable_source(self) -> bool:
        # A context ending after its own filing date is a declared future
        # amount, not a reported period value (PPL 10-Q 0000922224-13-000025
        # tags the November 2013 dividend; Verifier other_changed recheck).
        return (
            not self.is_derived
            and is_periodic_form(self.form)
            and self.end_date <= self.filing_date
        )


@dataclass(frozen=True)
class Filing:
    filing_id: int
    filing_date: date
    form: str
    accession: str


# --------------------------------------------------------------------------
# Precision and ratio fitting (exact Decimal / Fraction arithmetic)
# --------------------------------------------------------------------------
def half_unit(value: Decimal, kind: str) -> Decimal:
    """Half of the last reported unit, inferred from the stored digits.
    core.fact keeps no `decimals`; trailing zeros are the best evidence."""
    raw = value.normalize().as_tuple().exponent
    assert isinstance(raw, int)
    exp: int = raw
    if kind == PER_SHARE:
        exp = min(exp, -PER_SHARE_MIN_DECIMALS)
    else:
        exp = min(max(exp, 0), SHARES_MAX_UNIT_EXP)
    return Decimal(1).scaleb(exp) / 2


def _fits_same_period(v_old: Decimal, v_new: Decimal, k: Fraction, kind: str) -> bool:
    """Same tag and period filed twice: does old = new*k (per-share) or
    new = old*k (shares) hold within both copies' rounding?"""
    num, den = Decimal(k.numerator), Decimal(k.denominator)
    t_old, t_new = half_unit(v_old, kind), half_unit(v_new, kind)
    if kind == PER_SHARE:
        # v_old * den == v_new * num
        return abs(v_old * den - v_new * num) <= t_old * den + t_new * num
    return abs(v_new * den - v_old * num) <= t_new * den + t_old * num


# Recurring stock dividends (CBSH 5%, VLY 5%; Verifier other_changed recheck)
# re-present per-share history by 21/20 or 11/10. Re-basing them is not built:
# such a candidate is always 'review' (its earlier filings are held). Only
# per-share filed pairs can raise it; a 5-10% share-count step is ordinary
# issuance as often as not.
STOCK_DIVIDEND_RATIOS: tuple[Fraction, ...] = (Fraction(21, 20), Fraction(11, 10))
STOCK_DIVIDEND_VALUE_TAG = (
    "StockIssuedDuringPeriodValueStockDividend"  # not used as evidence
)


def ratio_candidates(kind: str) -> tuple[Fraction, ...]:
    if kind == SHARES:
        return tuple(k for k in CLEAN_RATIOS if k not in SHARE_SCALE_RATIOS)
    return CLEAN_RATIOS + STOCK_DIVIDEND_RATIOS


def is_share_scale_artifact(v_old: Decimal, v_new: Decimal, kind: str) -> bool:
    return kind == SHARES and any(
        _fits_same_period(v_old, v_new, k, kind) for k in SHARE_SCALE_RATIOS
    )


def fit_pair_ratio(v_old: Decimal, v_new: Decimal, kind: str) -> Fraction | None:
    """The unique ratio in {1} + clean ratios that explains the pair, else
    None (ambiguous, zero, sign change, scale artifact or a non-clean
    difference)."""
    if v_old == 0 or v_new == 0 or (v_old > 0) != (v_new > 0):
        return ONE if v_old == v_new else None
    if is_share_scale_artifact(v_old, v_new, kind):
        return None
    fits = [
        k
        for k in (ONE, *ratio_candidates(kind))
        if _fits_same_period(v_old, v_new, k, kind)
    ]
    return fits[0] if len(fits) == 1 else None


def pair_fits(v_old: Decimal, v_new: Decimal, k: Fraction, kind: str) -> bool:
    if v_old == 0 or v_new == 0:
        return v_old == v_new
    return _fits_same_period(v_old, v_new, k, kind)


def fit_share_step(c_old: Decimal, c_new: Decimal) -> Fraction | None:
    """Consecutive share counts (different dates): the clean ratio within
    SHARE_STEP_REL_TOL, ONE when near 1, else None (ordinary change)."""
    if c_old <= 0 or c_new <= 0:
        return None
    for k in (ONE, *ratio_candidates(SHARES)):
        expect = c_old * Decimal(k.numerator) / Decimal(k.denominator)
        if abs(c_new - expect) <= SHARE_STEP_REL_TOL * expect:
            return k
    return None


def ratio_to_decimal(k: Fraction) -> Decimal:
    return (
        (Decimal(k.numerator) / Decimal(k.denominator))
        .quantize(Decimal("1e-12"), rounding=ROUND_HALF_EVEN)
        .normalize()
    )


def convert(value: Decimal, factor: Fraction, kind: str) -> Decimal:
    """As-filed -> current basis. Per-share divides by the factor, share
    counts multiply. Exact when the factor is 1."""
    if factor == ONE:
        return value
    num, den = Decimal(factor.numerator), Decimal(factor.denominator)
    if kind == PER_SHARE:
        out = (value * den / num).quantize(OUTPUT_QUANTUM, rounding=ROUND_HALF_EVEN)
        return _strip(out)
    return (value * num / den).quantize(Decimal(1), rounding=ROUND_HALF_EVEN)


def _strip(d: Decimal) -> Decimal:
    n = d.normalize()
    exp = n.as_tuple().exponent
    assert isinstance(exp, int)
    return n.quantize(Decimal(1)) if exp > 0 else n


# --------------------------------------------------------------------------
# Evidence
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class FiledPair:
    tag: str
    kind: str
    period_id: int
    old: SourceFact
    new: SourceFact
    ratio: Fraction | None  # unique clean fit, ONE, or None

    @property
    def lo(self) -> date:
        return self.old.filing_date

    @property
    def hi(self) -> date:
        return self.new.filing_date


@dataclass(frozen=True)
class ShareStep:
    old_fact: SourceFact
    new_fact: SourceFact
    ratio: Fraction | None

    @property
    def lo(self) -> date:
        return self.old_fact.filing_date

    @property
    def hi(self) -> date:
        return self.new_fact.filing_date


@dataclass(frozen=True)
class Disclosure:
    fact: SourceFact
    ratio: Fraction
    window_lo: date
    window_hi: date

    @property
    def anchor(self) -> date:
        """The instant date (record/effective date) or the filing date for a
        duration context (its period can predate the split: TSLA's 2022 3:1
        is disclosed on an FY2020 context in 0001318605-23-000011)."""
        if self.fact.period_type == "instant":
            return self.fact.end_date
        return self.fact.filing_date


def _kind_of(fact: SourceFact) -> str | None:
    if fact.unit == UNIT_BY_KIND[PER_SHARE]:
        return PER_SHARE
    if fact.unit == UNIT_BY_KIND[SHARES]:
        return SHARES
    return None


def _is_amendment(f: SourceFact) -> bool:
    """A 10-Q/A or 10-K/A can re-file an OLD period on that period's basis, so
    its cover/share counts do not mark the filing date's basis (SNDK, SYRE Q1
    2024 10-Q/A after a split; Verifier run 4): kept out of the share series.
    Its filed pairs stay evidence (BURU re-bases a reverse split in a 10-K/A,
    ledger row 35)."""
    return f.form.strip().upper().endswith("/A")


def build_filed_pairs(
    facts: Iterable[SourceFact], extra_tags: Iterable[str] = ()
) -> list[FiledPair]:
    """Consecutive copies (by filing date) of one tag/unit/period from
    periodic, non-derived filings. `extra_tags` adds the mapped tags of the
    per-share and share concepts (ET files LP-unit EPS)."""
    groups: dict[tuple[str, str, int], list[SourceFact]] = defaultdict(list)
    evidence_tags = (
        set(EVIDENCE_PER_SHARE_TAGS) | set(EVIDENCE_SHARE_TAGS) | set(extra_tags)
    )
    for f in facts:
        if f.tag in evidence_tags and f.usable_source and _kind_of(f):
            groups[(f.tag, f.unit, f.period_id)].append(f)
    pairs: list[FiledPair] = []
    for (tag, _unit, period_id), copies in groups.items():
        copies.sort(key=lambda f: (f.filing_date, f.fact_id))
        for a, b in itertools.pairwise(copies):
            if a.filing_date >= b.filing_date:
                continue
            kind = _kind_of(a)
            assert kind is not None
            pairs.append(
                FiledPair(
                    tag, kind, period_id, a, b, fit_pair_ratio(a.value, b.value, kind)
                )
            )
    pairs.sort(key=lambda p: (p.hi, p.lo, p.tag, p.period_id))
    return pairs


SERIES_MAX_AGE_DAYS = 130


def build_share_series(facts: Iterable[SourceFact]) -> list[SourceFact]:
    """One share count per periodic filing: the latest-instant cover count,
    else the latest-instant balance-sheet count; median of ties."""
    by_filing: dict[int, dict[str, list[SourceFact]]] = defaultdict(
        lambda: defaultdict(list)
    )
    facts = list(facts)
    # An original count an amendment corrects within 60 days is a typo, not
    # a share step (SNDK 10-Q 114,863,251 vs the 10-Q/A's 144,863,251).
    amended = {
        (g.tag, g.period_id): g
        for g in facts
        if _is_amendment(g) and g.tag in SERIES_TAGS and g.usable_source
    }
    for f in facts:
        g = amended.get((f.tag, f.period_id))
        if (
            f.tag in SERIES_TAGS
            and f.unit == "shares"
            and f.usable_source
            and f.value > 0
            and not _is_amendment(f)
            and not (
                g is not None
                and g.value != f.value
                and 0 <= (g.filing_date - f.filing_date).days <= 60
            )
        ):
            by_filing[f.filing_id][f.tag].append(f)
    series: list[SourceFact] = []
    for tags in by_filing.values():
        for tag in SERIES_TAGS:
            # a count dated long before its own filing is not the filing's
            # current count (LYFT 10-K 2020-02-28: CommonStockSharesOutstanding
            # at 2018-12-31; Verifier run 5)
            cands = [
                c
                for c in tags.get(tag, [])
                if tag == "EntityCommonStockSharesOutstanding"
                or (c.filing_date - c.end_date).days <= SERIES_MAX_AGE_DAYS
            ]
            if not cands:
                continue
            latest = max(c.end_date for c in cands)
            at = sorted(
                (c for c in cands if c.end_date == latest), key=lambda c: c.value
            )
            series.append(at[len(at) // 2])
            break
    series.sort(key=lambda f: (f.filing_date, f.fact_id))
    return series


def build_share_steps(series: list[SourceFact]) -> list[ShareStep]:
    steps = []
    for a, b in itertools.pairwise(series):
        if a.filing_date >= b.filing_date:
            continue
        steps.append(ShareStep(a, b, fit_share_step(a.value, b.value)))
    return steps


def build_disclosures(facts: Iterable[SourceFact]) -> list[Disclosure]:
    out = []
    for f in facts:
        if f.tag not in SPLIT_RATIO_TAGS or not f.usable_source:
            continue
        classified = _classify(f.value)
        if classified is None:
            continue
        ratio = Fraction(str(classified[0]))
        lo_date = (
            f.start_date if f.start_date and f.period_type == "duration" else f.end_date
        )
        out.append(
            Disclosure(
                f,
                ratio,
                lo_date - DISCLOSURE_WINDOW_PAD,
                f.filing_date + DISCLOSURE_WINDOW_PAD,
            )
        )
    out.sort(key=lambda d: (d.anchor, d.fact.fact_id))
    return out


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------
@dataclass
class Event:
    local_id: int
    ratio: Fraction
    lo: date | None  # latest filing date observed on the OLD basis
    hi: date | None  # earliest filing date observed on the NEW basis
    pairs: list[FiledPair] = field(default_factory=list)
    steps: list[ShareStep] = field(default_factory=list)
    disclosures: list[Disclosure] = field(default_factory=list)
    status: str = "review"  # confirmed | review | rejected | pending
    note: str = ""
    restated_shares: bool = False  # filer re-presented share counts by the ratio
    clean: bool = True  # disclosure-only: ratio snaps to a clean split ratio
    doubt: tuple[date, date] | None = None  # window where a duplicate was seen

    @property
    def kinds(self) -> list[str]:
        k = []
        if self.disclosures:
            k.append("ratio_fact")
        if self.pairs:
            k.append("filed_pair")
        if self.steps or self.restated_shares:
            k.append("share_step")
        return k

    @property
    def basis_date(self) -> date:
        """First date from which filings report on the new basis: the
        earliest filing observed on it; with no observation, the latest
        disclosed instant date (design 2.4)."""
        if self.hi is not None:
            return self.hi
        return max(d.anchor for d in self.disclosures)

    def evidence_json(self) -> dict:
        return {
            "ratio_fact": [
                {
                    "fact_id": d.fact.fact_id,
                    "tag": d.fact.tag,
                    "context": d.fact.period_type,
                    "start": _iso(d.fact.start_date),
                    "end": _iso(d.fact.end_date),
                    "accession": d.fact.accession,
                    "filing_date": _iso(d.fact.filing_date),
                    "raw_value": str(d.fact.value),
                }
                for d in self.disclosures
            ],
            "filed_pair": [
                {
                    "tag": p.tag,
                    "period_id": p.period_id,
                    "old_fact_id": p.old.fact_id,
                    "old_value": str(p.old.value),
                    "old_accession": p.old.accession,
                    "new_fact_id": p.new.fact_id,
                    "new_value": str(p.new.value),
                    "new_accession": p.new.accession,
                }
                for p in self.pairs
            ],
            "share_step": [
                {
                    "old_fact_id": s.old_fact.fact_id,
                    "old_value": str(s.old_fact.value),
                    "old_accession": s.old_fact.accession,
                    "new_fact_id": s.new_fact.fact_id,
                    "new_value": str(s.new_fact.value),
                    "new_accession": s.new_fact.accession,
                }
                for s in self.steps
            ],
            "observed_window": [_iso(self.lo), _iso(self.hi)],
            "share_step_from": (
                "series"
                if self.steps
                else ("restated_share_counts" if self.restated_shares else None)
            ),
            "note": self.note,
        }


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _cluster(
    observations: list[tuple[date, date, object]],
) -> list[tuple[date, date, list]]:
    """Greedy interval intersection by `hi`: observations whose (lo, hi]
    windows share a point are one basis boundary."""
    clusters: list[tuple[date, date, list]] = []
    for lo, hi, obs in sorted(observations, key=lambda o: (o[1], o[0])):
        if clusters:
            c_lo, c_hi, members = clusters[-1]
            n_lo, n_hi = max(c_lo, lo), min(c_hi, hi)
            if n_lo < n_hi:
                clusters[-1] = (n_lo, n_hi, members + [obs])
                continue
        clusters.append((lo, hi, [obs]))
    return clusters


def _refine_window(
    lo: date, hi: date, pairs: list[FiledPair], steps: list[ShareStep]
) -> tuple[date, date]:
    """Narrow (lo, hi] with ratio-1 links: a filing inside the window whose
    copy equals (ratio 1) a copy in a filing on a known side is on that side.
    Filings dated <= lo are old basis, >= hi new basis (one event)."""
    links = [(p.old.filing_date, p.new.filing_date) for p in pairs if p.ratio == ONE]
    links += [(s.lo, s.hi) for s in steps if s.ratio == ONE]
    changed = True
    while changed:
        changed = False
        for a, b in links:  # a < b
            if lo < b < hi and a <= lo:  # b equals an old-basis copy
                lo, changed = b, True
            if lo < a < hi and b >= hi:  # a equals a new-basis copy
                hi, changed = a, True
    return lo, hi


def _ratio_one_pairs_spanning(pairs: list[FiledPair], lo: date, hi: date) -> int:
    return sum(1 for p in pairs if p.ratio == ONE and p.lo <= lo and p.hi >= hi)


POWER_OF_TEN = frozenset(
    {Fraction(100), Fraction(1000), Fraction(1, 100), Fraction(1, 1000)}
)
EPS_TAGS = frozenset(
    {
        "EarningsPerShareBasic",
        "EarningsPerShareDiluted",
        "EarningsPerShareBasicAndDiluted",
    }
)
SHARE_COUNT_TAGS = frozenset(EVIDENCE_SHARE_TAGS)
SNAP_REL = Decimal("0.001")


def snap_ratio(r: Fraction) -> Fraction | None:
    """The clean ratio within 0.1% of r (ratio facts are often rounded:
    WRB files 0.6667 for 2/3), else None (an exchange or conversion ratio:
    DUK 0.8708, WTW 0.3775, ACI 2.072)."""
    rd = Decimal(r.numerator) / Decimal(r.denominator)
    cands = list(CLEAN_RATIOS) + [1 / k for k in CLEAN_RATIOS]
    for k in sorted(set(cands)):
        kd = Decimal(k.numerator) / Decimal(k.denominator)
        if abs(rd - kd) <= SNAP_REL * kd:
            return k
    return None


def _disclosure_distance(d: Disclosure, e: Event) -> int:
    """Days from the disclosure's own dates to the event's observed window."""
    assert e.lo is not None and e.hi is not None
    dates = [d.fact.end_date, d.fact.filing_date]
    if d.fact.start_date is not None:
        dates.append(d.fact.start_date)
    best = None
    for x in dates:
        dist = (
            0 if e.lo <= x <= e.hi else min(abs((x - e.lo).days), abs((x - e.hi).days))
        )
        best = dist if best is None else min(best, dist)
    assert best is not None
    return best


def _support(e: Event) -> int:
    return len(e.pairs) + 3 * len(e.steps) + len(e.disclosures)


def detect_events(
    pairs: list[FiledPair],
    steps: list[ShareStep],
    disclosures: list[Disclosure],
    filings: list[Filing],
    stock_dividend_tagged: bool = False,
) -> list[Event]:
    """Pure: evidence -> events with status. Deterministic for fixed input.
    Rules learned on the 1,000-company cohort dry-run (2026-10-24):
    - a disclosure attaches to ONE observed event, the nearest of ratio k or
      1/k (TTD files its 10:1 as 0.1; WAB and CGNX re-disclose old splits in
      later filings, which must not confirm a spurious later cluster);
    - per-share and share-count filed pairs moving inversely, on >= 2
      periods, are the filer's own re-presented share counts and count as
      the share_step kind (MA, CSX, CME: class-dimensioned or missing cover
      counts leave no undimensioned share series);
    - a pair-only candidate from one tag, or a per-share power-of-ten move
      without share-count support, is a context or units error judged per
      cell (TER, BRO, HALO, RGA), not an event;
    - a disclosure-only candidate whose ratio is not a clean split ratio is
      an exchange or conversion ratio (DUK, WTW, ACI), not an event;
    - two confirmed events of one ratio within DISCLOSURE_MERGE_DAYS keep the
      better-supported one; filings between them are basis review (KR)."""
    by_ratio: dict[Fraction, list[tuple[date, date, object]]] = defaultdict(list)
    for p in pairs:
        if p.ratio is not None and p.ratio != ONE:
            by_ratio[p.ratio].append((p.lo, p.hi, p))
    for st in steps:
        if st.ratio is not None and st.ratio != ONE:
            by_ratio[st.ratio].append((st.lo, st.hi, st))

    events: list[Event] = []
    for ratio in sorted(by_ratio):
        for lo, hi, members in _cluster(by_ratio[ratio]):
            ev = Event(len(events), ratio, lo, hi)
            for m in members:
                (ev.pairs if isinstance(m, FiledPair) else ev.steps).append(m)
            ev.lo, ev.hi = _refine_window(lo, hi, pairs, steps)
            per_share_tags = {p.tag for p in ev.pairs if p.kind == PER_SHARE}
            share_pairs = [p for p in ev.pairs if p.kind == SHARES]
            periods = {p.period_id for p in ev.pairs}
            ev.restated_shares = bool(
                share_pairs and len(per_share_tags) >= 2 and len(periods) >= 2
            )
            events.append(ev)

    loose: list[Disclosure] = []
    for d in disclosures:
        k = snap_ratio(d.ratio) or d.ratio
        same = [e for e in events if e.ratio in (k, 1 / k) and e.lo and e.hi]
        near = sorted(
            (_disclosure_distance(d, e), e.ratio != k, e.local_id, e) for e in same
        )
        if near and near[0][0] <= DISCLOSURE_MERGE_DAYS:
            near[0][3].disclosures.append(d)
        else:
            loose.append(d)

    for d in loose:
        snapped = snap_ratio(d.ratio)
        ratio = snapped if snapped is not None else d.ratio
        prev = next(
            (
                e
                for e in events
                if e.hi is None
                and e.ratio == ratio
                and abs((d.anchor - e.basis_date).days) <= DISCLOSURE_MERGE_DAYS
            ),
            None,
        )
        if prev is not None:
            prev.disclosures.append(d)
        else:
            ev = Event(len(events), ratio, None, None, disclosures=[d])
            ev.clean = snapped is not None
            events.append(ev)

    filing_dates = sorted(f.filing_date for f in filings)
    for ev in events:
        if ev.ratio in STOCK_DIVIDEND_RATIOS and ev.hi is not None:
            # Held only with filed stock-dividend evidence (Verifier run 3: 29
            # of 40 sampled holds were restated copies ~5-10% apart at BAC,
            # PAYX, CCI, EQIX...): the stock-dividend value tag, or the same
            # ratio again about a year apart (CBSH every December, VLY May
            # 2011 and May 2012).
            yearly = any(
                o is not ev
                and o.ratio == ev.ratio
                and o.hi is not None
                and 300 <= abs((o.basis_date - ev.basis_date).days) <= 430
                for o in events
            )
            strong = (
                len({p.tag for p in ev.pairs}) >= 2
                and len({p.period_id for p in ev.pairs}) >= 2
            )
            if strong and yearly:
                ev.status, ev.note = (
                    "review",
                    "stock dividend: re-base not built (held)",
                )
            else:
                ev.status, ev.note = (
                    "rejected",
                    "stock-dividend-sized move without filed stock-dividend evidence",
                )
            continue
        if len(ev.kinds) >= 2:
            # E. comparatives that span the boundary unchanged outnumber the
            # re-presented ones: the event is not where the evidence says
            # (ANF 2013, HOMB 2018, UGI's second 2014 3:2, HEI duplicates).
            if ev.lo is not None and ev.hi is not None and not ev.steps:
                one = _ratio_one_pairs_spanning(pairs, ev.lo, ev.hi)
                if one >= REFUTE_MIN_PAIRS and one >= 2 * max(len(ev.pairs), 1):
                    ev.status, ev.note = (
                        "rejected",
                        f"contradicted: {one} comparatives span it unchanged vs {len(ev.pairs)} re-presented",
                    )
                    continue
            ev.status = "confirmed"
            continue
        if ev.hi is None:  # disclosure only
            anchor = ev.basis_date
            if not ev.clean:
                ev.status, ev.note = (
                    "rejected",
                    "not a clean split ratio (exchange/conversion)",
                )
                continue
            if not filing_dates or filing_dates[-1] <= anchor:
                ev.status, ev.note = "pending", "no filing on the new basis yet"
                continue
            if filing_dates[0] >= anchor:
                ev.status, ev.note = "pending", "every held filing post-dates it"
                continue
            span_lo = max((x for x in filing_dates if x <= anchor), default=anchor)
            span_hi = min((x for x in filing_dates if x > anchor), default=anchor)
            if _ratio_one_pairs_spanning(pairs, span_lo, span_hi) >= REFUTE_MIN_PAIRS:
                ev.status, ev.note = (
                    "rejected",
                    "filed comparatives span the date at ratio 1",
                )
                continue
            ev.status, ev.note = "review", "ratio disclosed, no basis change observed"
            continue
        assert ev.lo is not None
        spanning_one = _ratio_one_pairs_spanning(pairs, ev.lo, ev.hi)
        if not ev.pairs and spanning_one >= REFUTE_MIN_PAIRS:
            ev.status, ev.note = (
                "rejected",
                "share-count step only; filed comparatives span it at ratio 1",
            )
            continue
        if not ev.steps:
            pair_tags = {p.tag for p in ev.pairs}
            if not any(p.kind == SHARES for p in ev.pairs):
                ev.status, ev.note = (
                    "rejected",
                    "per-share values moved but no share count did (a restatement, IONS 2021)",
                )
                continue
            if len(pair_tags) < 2:
                ev.status, ev.note = (
                    "rejected",
                    "pairs from one tag only (judged per cell)",
                )
                continue
            if not pair_tags & (EPS_TAGS | SHARE_COUNT_TAGS):
                ev.status, ev.note = (
                    "rejected",
                    "dividend tags only; a split moves EPS (rate/annual context error)",
                )
                continue
            if ev.ratio in POWER_OF_TEN and not any(p.kind == SHARES for p in ev.pairs):
                ev.status, ev.note = (
                    "rejected",
                    "per-share power-of-ten move without share counts: units scale suspect",
                )
                continue
            if spanning_one >= REFUTE_MIN_PAIRS and spanning_one >= 2 * len(ev.pairs):
                ev.status, ev.note = (
                    "rejected",
                    f"{len(ev.pairs)} filed pair(s) contradicted by {spanning_one} ratio-1 pairs",
                )
                continue
        if not ev.pairs and not ev.disclosures and Fraction(1, 2) < ev.ratio < 2:
            # an offering- or buyback-sized share move with no per-share or
            # ratio evidence is not a split candidate (SYRE 2022 and 2025
            # +21% / +28% read as 5:4; Verifier run 5: false holds)
            ev.status, ev.note = (
                "rejected",
                "share-count step only, at an offering-sized ratio",
            )
            continue
        ev.status, ev.note = "review", "one evidence kind only"

    # Same ratio confirmed twice within the merge distance: one economic event.
    conf = sorted(
        (e for e in events if e.status == "confirmed"), key=lambda e: e.basis_date
    )
    for a_ev, b_ev in itertools.combinations(conf, 2):
        if a_ev.status != "confirmed" or b_ev.status != "confirmed":
            continue
        if a_ev.ratio != b_ev.ratio:
            continue
        if abs((b_ev.basis_date - a_ev.basis_date).days) > DISCLOSURE_MERGE_DAYS:
            continue
        # Only when the filings REVERSE between the two boundaries (KR: the
        # share series goes 491M -> 953M -> 485M -> 973M). Real repeated
        # splits months apart show no reversal (CPRT 2:1 Nov 2022 and Sep
        # 2023; AAON 3:2 2013 and 2014; HEI 5:4 2012 and 2018; Verifier 1000).
        win_lo = min(x for x in (a_ev.lo, b_ev.lo) if x is not None)
        win_hi = max(x for x in (a_ev.hi, b_ev.hi) if x is not None)
        inverse = 1 / a_ev.ratio
        reversed_between = any(
            p.ratio == inverse and win_lo <= p.lo and p.hi <= win_hi for p in pairs
        ) or any(
            st.ratio == inverse and win_lo <= st.lo and st.hi <= win_hi for st in steps
        )
        if not reversed_between:
            continue
        keep, drop = (a_ev, b_ev) if _support(a_ev) >= _support(b_ev) else (b_ev, a_ev)
        drop.status = "rejected"
        drop.note = f"same ratio as the better-supported event at {keep.basis_date}"
        lo = min(x for x in (a_ev.lo, b_ev.lo) if x is not None)
        hi = max(x for x in (a_ev.hi, b_ev.hi) if x is not None)
        keep.doubt = (lo, hi)
        # the reversal itself (a 1/k candidate between them) is the same
        # filer inconsistency, not an event of its own
        for ev in events:
            if (
                ev.ratio == inverse
                and ev.status in ("review", "confirmed")
                and ev.lo is not None
                and ev.hi is not None
                and win_lo <= ev.lo
                and ev.hi <= win_hi
            ):
                ev.status, ev.note = (
                    "rejected",
                    "reversal between duplicate observations",
                )

    # A candidate (review, or confirmed without a ratio fact) whose every
    # observation spans >= 2 other confirmed events with this product is those
    # events seen across both (TSLA 5x3; CPRT's 4x across its two 2:1s).
    for ev in events:
        if ev.hi is None or ev.status not in ("review", "confirmed"):
            continue
        if ev.status == "confirmed" and ev.disclosures:
            continue
        others = [e for e in events if e.status == "confirmed" and e is not ev]
        obs = [(p.lo, p.hi) for p in ev.pairs] + [(st.lo, st.hi) for st in ev.steps]
        if obs and all(_spanned_product(others, lo, hi) == ev.ratio for lo, hi in obs):
            ev.status, ev.note = "rejected", "product of confirmed events"
    # A single-kind candidate on the same boundary as a confirmed split of a
    # different ratio is that split plus issuance or scale noise (PRAX 1:15
    # with a concurrent offering gives a 1:10 share step; EOG's 2:1 with a
    # 1/500 pair pattern; Verifier 1000).
    confirmed = [e for e in events if e.status == "confirmed"]
    for ev in events:
        if ev.status == "review" and ev.hi is None and ev.disclosures:
            # a disclosure-only candidate beside a confirmed split of another
            # ratio is that split's disclosure (GSAT 0.6667 at 2025-02-10
            # beside its confirmed 1:15; Verifier run 3)
            near_conf = [
                e
                for e in confirmed
                if e.ratio != ev.ratio
                and abs((e.basis_date - ev.basis_date).days) <= DISCLOSURE_MERGE_DAYS
            ]
            if near_conf:
                ev.status, ev.note = (
                    "rejected",
                    f"disclosure beside the confirmed {near_conf[0].ratio} split at {near_conf[0].basis_date}",
                )
            continue
        if ev.status != "review" or ev.hi is None or ev.lo is None:
            continue
        hit = next(
            (
                e
                for e in confirmed
                if e.ratio != ev.ratio
                and e.lo is not None
                and e.hi is not None
                and max(e.lo, ev.lo) < min(e.hi, ev.hi)
            ),
            None,
        )
        if hit is not None:
            ev.status, ev.note = (
                "rejected",
                f"same boundary as the confirmed {hit.ratio} split at {hit.basis_date}",
            )
    return events


def _spanned_product(events: list[Event], lo: date, hi: date) -> Fraction:
    prod = ONE
    for e in events:
        if lo < e.basis_date <= hi:
            prod *= e.ratio
    return prod


def event_set_hash(events: list[Event]) -> str:
    """Stable digest of the confirmed/review event set (nightly trigger,
    design 2.9)."""
    key = sorted(
        (str(e.ratio), _iso(e.basis_date), e.status, tuple(sorted(e.kinds)))
        for e in events
        if e.status in ("confirmed", "review")
    )
    return hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16]


# --------------------------------------------------------------------------
# Filing basis
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class FilingBasis:
    filing_id: int
    filing_date: date
    factor: Fraction
    event_ids: tuple[int, ...]
    observed_factor: Fraction | None
    status: str  # consistent | date_only | conflict | review
    note: str = ""

    @property
    def usable(self) -> bool:
        return self.status in ("consistent", "date_only")


def compute_filing_basis(
    filings: list[Filing],
    events: list[Event],
    series: list[SourceFact],
    steps: list[ShareStep],
) -> dict[int, FilingBasis]:
    confirmed = [e for e in events if e.status == "confirmed"]
    review = [e for e in events if e.status == "review"]
    rejected_steps = {id(s) for e in events if e.status == "rejected" for s in e.steps}
    count_by_filing = {f.filing_id: f for f in series}
    # Filings an event's own observations place on one side of it.
    placed: dict[int, set[int]] = {}
    for e in events:
        ids: set[int] = set()
        for p in e.pairs:
            ids |= {p.old.filing_id, p.new.filing_id}
        for s in e.steps:
            ids |= {s.old_fact.filing_id, s.new_fact.filing_id}
        placed[e.local_id] = ids

    # Observed factor: chain the clean steps from each filing to the newest
    # count (refuted steps count as 1).
    observed: dict[int, Fraction] = {}
    if series:
        acc = ONE
        observed[series[-1].filing_id] = ONE
        step_by_new = {s.new_fact.filing_id: s for s in steps}
        for i in range(len(series) - 2, -1, -1):
            stp = step_by_new.get(series[i + 1].filing_id)
            if (
                stp is not None
                and stp.ratio is not None
                and id(stp) not in rejected_steps
            ):
                acc *= stp.ratio
            elif stp is not None and stp.ratio is None:
                # A confirmed split inside a step that also carries issuance
                # or a merger (NLY 1:4 in 2022 with offerings: 1.46B -> 0.47B;
                # SIRI 1:10 with the Liberty merger): the step is the split
                # when it lies within 1.5x of the event's ratio.
                inside_step = [
                    e
                    for e in confirmed
                    if stp.old_fact.filing_date
                    < e.basis_date
                    <= stp.new_fact.filing_date
                ]
                if len(inside_step) == 1 and stp.old_fact.value > 0:
                    k = inside_step[0].ratio
                    r = Fraction(stp.new_fact.value) / Fraction(stp.old_fact.value)
                    if k * Fraction(2, 3) <= r <= k * Fraction(3, 2):
                        acc *= k
            observed[series[i].filing_id] = acc

    out: dict[int, FilingBasis] = {}
    for fl in filings:
        applied = [e for e in confirmed if e.basis_date > fl.filing_date]
        factor = ONE
        for e in applied:
            factor *= e.ratio
        obs = observed.get(fl.filing_id)
        status, note = "date_only", ""
        has_count = fl.filing_id in count_by_filing
        inside = [
            e
            for e in confirmed
            if e.lo is not None and e.hi is not None and e.lo < fl.filing_date < e.hi
        ]
        near = [
            e
            for e in confirmed
            if abs((fl.filing_date - e.basis_date).days) <= BOUNDARY_REVIEW_DAYS
            and fl.filing_id not in placed[e.local_id]
        ]
        touched_by_review = [e for e in review if fl.filing_date < e.basis_date]
        in_doubt = [
            e for e in confirmed if e.doubt and e.doubt[0] < fl.filing_date < e.doubt[1]
        ]
        if in_doubt:
            status, note = "review", "between two same-ratio split observations"
        elif touched_by_review:
            status, note = "review", "before an unconfirmed split candidate"
        elif inside and not has_count:
            status, note = (
                "review",
                "inside the observed boundary window, no share count",
            )
        elif has_count:
            status = "consistent" if obs == factor else "conflict"
            if status == "conflict":
                note = f"share series implies {obs}, events imply {factor}"
        elif near:
            status, note = "review", "within 30 days of a basis date, no share count"
        out[fl.filing_id] = FilingBasis(
            fl.filing_id,
            fl.filing_date,
            factor,
            tuple(sorted(e.local_id for e in applied)),
            obs,
            status,
            note,
        )
    return out


# Distinct periods that must show the same unexplained basis ratio between one
# pair of filings before the company is hidden. One period alone is a
# restatement or a context error (AMZN 0001193125-13-028520 swaps two
# quarters' EPS, 0.29 <-> 0.44, which looks like 3:2 and 2:3).
INVARIANT_MIN_PERIODS = 2


def invariant_violations(
    pairs: list[FiledPair], basis: Mapping[int, FilingBasis], events: list[Event]
) -> list[tuple[FiledPair, Fraction]]:
    """Filed pairs showing a SYSTEMATIC basis change our factors do not
    explain (design 2.5): between one old/new filing, at least
    INVARIANT_MIN_PERIODS distinct periods move by the same ratio r, where r
    is 1, one clean split ratio, or a product of this company's own event
    ratios (a double count: GOOG 400 vs 20), and r != factor(old)/factor(new).
    Non-systematic differences are restatements, judged per cell."""
    review = [e for e in events if e.status in ("review", "pending")]
    own = [e.ratio for e in events if e.status in ("confirmed", "review")]
    basis_like: set[Fraction] = {ONE}
    for own_ratio in own:
        basis_like |= {x * own_ratio for x in list(basis_like)} | {
            x / own_ratio for x in list(basis_like)
        }
    groups: dict[tuple[int, int, Fraction], list[tuple[FiledPair, Fraction]]] = (
        defaultdict(list)
    )
    for p in pairs:
        b_old, b_new = basis.get(p.old.filing_id), basis.get(p.new.filing_id)
        if b_old is None or b_new is None:
            continue
        expected = b_old.factor / b_new.factor
        if pair_fits(p.old.value, p.new.value, expected, p.kind):
            continue
        if is_share_scale_artifact(p.old.value, p.new.value, p.kind):
            continue  # a units error in one copy, judged per cell
        if any(p.lo < e.basis_date <= p.hi for e in review):
            continue  # the cells it touches are hidden as review already
        # Only ratios built from this company's own events (or 1) count: a
        # restated small EPS that happens to fit an unrelated clean ratio
        # (CRM 0.09 -> 0.28 ~ 3x, cohort-1000 dry-run) is a restatement; an
        # unrelated real basis change would have formed its own candidate.
        r: Fraction | None = p.ratio if p.ratio in basis_like else None
        if r is None:
            r = next(
                (
                    k
                    for k in sorted(basis_like - {expected})
                    if pair_fits(p.old.value, p.new.value, k, p.kind)
                ),
                None,
            )
        if r is None or r == expected:
            continue
        groups[(p.old.filing_id, p.new.filing_id, r)].append((p, expected))
    out: list[tuple[FiledPair, Fraction]] = []
    for (_o, _n, r), members in groups.items():
        tags = {m[0].tag for m in members}
        if len({m[0].period_id for m in members}) < INVARIANT_MIN_PERIODS:
            continue
        # A basis change moves EPS (or share counts) and more than one tag;
        # DPS alone moving by 2 or 4 is a rate/annual context error (TER, AIG).
        if len(tags) < 2 or not (tags & (EPS_TAGS | SHARE_COUNT_TAGS)):
            continue
        # A per-share power-of-ten units error (RGA, HALO) never reaches here:
        # its ratio is not built from this company's own events (above).
        out.extend(members)
    return out


# --------------------------------------------------------------------------
# Cells
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class CellResult:
    concept: str
    period_id: int
    status: str  # SHOWN or a HIDE_* reason
    value: Decimal | None
    source_fact_ids: tuple[int, ...]
    chosen: SourceFact | None
    factor: Fraction | None
    candidates: tuple[
        tuple[int, str, Decimal, Fraction, Decimal], ...
    ]  # id, accession, as-filed, factor, converted
    note: str = ""


def resolve_cells(
    facts: list[SourceFact],
    mapped_tags: Mapping[str, list[str]],
    basis: Mapping[int, FilingBasis],
    events: list[Event],
    company_hidden: bool | date,
) -> list[CellResult]:
    by_local = {e.local_id: e for e in events}
    by_tag_period: dict[tuple[str, int], list[SourceFact]] = defaultdict(list)
    all_tag_period: dict[tuple[str, int], list[SourceFact]] = defaultdict(list)
    for f in facts:
        all_tag_period[(f.tag, f.period_id)].append(f)
        if f.usable_source:
            by_tag_period[(f.tag, f.period_id)].append(f)

    # (filing, tag, unit) -> period -> values: for label-shift detection.
    same_filing: dict[tuple[int, str, str], dict[int, set[Decimal]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for f in facts:
        if f.usable_source:
            same_filing[(f.filing_id, f.tag, f.unit)][f.period_id].add(f.value)

    # (tag, period) -> the value most usable copies hold (>= 2 and strictly
    # most): the consensus a swapped copy is judged against (run 7)
    consensus: dict[tuple[str, int], Decimal] = {}
    for key, fs_ in by_tag_period.items():
        cnt = Counter(f.value for f in fs_)
        top = cnt.most_common(2)
        if top and top[0][1] >= 2 and (len(top) == 1 or top[0][1] > top[1][1]):
            consensus[key] = top[0][0]
    by_filing_tag: dict[tuple[int, str], dict[int, set[Decimal]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for f in facts:
        if f.usable_source:
            by_filing_tag[(f.filing_id, f.tag)][f.period_id].add(f.value)

    # filing -> other share counts in that filing (cover and weighted averages)
    share_refs: dict[int, list[Decimal]] = defaultdict(list)
    for f in facts:
        if (
            f.usable_source
            and f.unit == "shares"
            and f.value > 0
            and f.tag in ("EntityCommonStockSharesOutstanding", *WASO_TAGS)
        ):
            share_refs[f.filing_id].append(f.value)

    period_days: dict[int, int] = {}
    period_span: dict[int, tuple[date | None, date]] = {}
    paid: dict[tuple[int, date | None, date], Decimal] = {}
    for f in facts:
        period_span[f.period_id] = (f.start_date, f.end_date)
        if f.start_date is not None:
            period_days[f.period_id] = (f.end_date - f.start_date).days
    paid = _common_dividend_paid_evidence(facts, share_refs)

    # (start, end) -> current-basis DPS of the latest usable 3-month copy
    quarter_dps: dict[tuple[date, date], Decimal] = {}
    _q_best: dict[tuple[date, date], tuple] = {}
    for f in facts:
        b_ = basis.get(f.filing_id)
        if (
            f.tag
            in (
                "CommonStockDividendsPerShareDeclared",
                "CommonStockDividendsPerShareCashPaid",
            )
            and f.usable_source
            and f.start_date is not None
            and 80 <= (f.end_date - f.start_date).days <= 100
            and b_ is not None
            and b_.usable
        ):
            k_ = (f.start_date, f.end_date)
            if k_ not in _q_best or (f.filing_date, f.fact_id) > _q_best[k_][:2]:
                _q_best[k_] = (
                    f.filing_date,
                    f.fact_id,
                    convert(f.value, b_.factor, PER_SHARE),
                )
    quarter_dps = {k_: v[2] for k_, v in _q_best.items()}
    # (start, end) -> every usable filed DPS copy on either tag, current basis
    dps_copies_by_span: dict[tuple, list[tuple[SourceFact, Decimal]]] = defaultdict(
        list
    )
    for f in facts:
        b_ = basis.get(f.filing_id)
        if (
            f.tag
            in (
                "CommonStockDividendsPerShareDeclared",
                "CommonStockDividendsPerShareCashPaid",
            )
            and f.usable_source
            and b_ is not None
            and b_.usable
        ):
            dps_copies_by_span[(f.start_date, f.end_date)].append(
                (f, convert(f.value, b_.factor, PER_SHARE))
            )

    all_conv: dict[tuple[str, int], list] = {}
    # concept -> (end, |value|) of every usable filed copy: the local scale a
    # units-scale copy is judged against (BE Q3 2025 -100 vs -0.10)
    local_abs: dict[str, list[tuple[date, Decimal, int]]] = defaultdict(list)
    for concept_, (kind_, base_) in TARGETS.items():
        if kind_ != PER_SHARE:
            continue
        for f in facts:
            if f.tag in mapped_tags.get(base_, []) and f.usable_source and f.value != 0:
                local_abs[concept_].append((f.end_date, abs(f.value), f.period_id))
    out: list[CellResult] = []
    for concept, (kind, base) in TARGETS.items():
        tags = mapped_tags.get(base, [])
        unit = UNIT_BY_KIND[kind]
        periods = sorted({pid for (tag, pid) in all_tag_period if tag in tags})
        for pid in periods:
            chosen_tag = next(
                (
                    t
                    for t in tags
                    if any(f.unit == unit for f in by_tag_period.get((t, pid), []))
                ),
                None,
            )
            if chosen_tag is None:
                out.append(
                    CellResult(
                        concept, pid, HIDE_NO_FILED_SOURCE, None, (), None, None, ()
                    )
                )
                continue
            cands = [f for f in by_tag_period[(chosen_tag, pid)] if f.unit == unit]
            if company_hidden is not False and company_hidden is not None:
                # Hide only what was filed up to the last contradicting filing;
                # later filings are on the current basis (CBSH 2026 filings
                # after its last stock dividend; Verifier run 4).
                cutoff = company_hidden if isinstance(company_hidden, date) else None
                post = [
                    f for f in cands if cutoff is not None and f.filing_date > cutoff
                ]
                if post:
                    cands = post
                    company_hidden_cell = False
                else:
                    company_hidden_cell = True
            else:
                company_hidden_cell = False
            if company_hidden_cell:
                out.append(
                    CellResult(
                        concept, pid, HIDE_COMPANY_INVARIANT, None, (), None, None, ()
                    )
                )
                continue
            usable = [
                f for f in cands if f.filing_id in basis and basis[f.filing_id].usable
            ]
            if (
                not usable
                and kind == PER_SHARE
                and cands
                and all(f.value == 0 for f in cands)
            ):
                # zero is zero on every share basis (QXO Q2 2018; Verifier run 5)
                usable = [f for f in cands if f.filing_id in basis]
            if not usable:
                st = {basis[f.filing_id].status for f in cands if f.filing_id in basis}
                reason = HIDE_BASIS_CONFLICT if "conflict" in st else HIDE_BASIS_REVIEW
                out.append(
                    CellResult(
                        concept,
                        pid,
                        reason,
                        None,
                        (),
                        None,
                        None,
                        (),
                        note=",".join(sorted(st)),
                    )
                )
                continue
            conv = []
            for f in usable:
                b_f = basis[f.filing_id]
                fac = b_f.factor if b_f.usable and b_f.factor is not None else ONE
                conv.append((f, fac, convert(f.value, fac, kind)))
            conv.sort(key=lambda x: (x[0].filing_date, x[0].fact_id))
            all_conv[(concept, pid)] = list(conv)
            note = ""
            if kind == SHARES:
                # Same-filing evidence first (PCG 10-Q 0001004980-13-000025:
                # CommonStockSharesOutstanding 430,718,293,000,000 beside cover
                # 442,173,394 and WASO 434M): a copy 1000x or 10^6 off its own
                # filing's other share counts is a units error.
                # Confirmed against the company's own local series in the
                # post-pass: SAIA/EXEL file weighted averages in thousands, so
                # the own-filing test alone would flag the CORRECT count.
                if any(_off_scale_in_own_filing(x[0], share_refs) for x in conv):
                    note = OWN_FILING_SCALE_NOTE
                if all(x[2] == 0 for x in conv):
                    out.append(
                        CellResult(
                            concept, pid, HIDE_ZERO_SHARES, None, (), None, None, ()
                        )
                    )
                    continue
                conv = [x for x in conv if x[2] != 0] or conv
                # Copies off by a units scale against each other: keep the
                # strict majority, else hide (AAPL 899,213 vs 899,213,000 x2).
                if any(
                    is_share_scale_artifact(x[2], y[2], kind)
                    for x in conv
                    for y in conv
                ):
                    groups: list[list] = []
                    for x in conv:
                        for g in groups:
                            if _all_agree([g[0], x], kind):
                                g.append(x)
                                break
                        else:
                            groups.append([x])
                    groups.sort(key=len, reverse=True)
                    if len(groups) > 1 and len(groups[0]) > len(groups[1]):
                        note = f"dropped {len(conv) - len(groups[0])} copy(ies) off by a units scale"
                        conv = sorted(
                            groups[0], key=lambda x: (x[0].filing_date, x[0].fact_id)
                        )
                    else:
                        out.append(
                            CellResult(
                                concept, pid, HIDE_UNITS_SCALE, None, (), None, None, ()
                            )
                        )
                        continue
            if kind == PER_SHARE and len(conv) > 1:
                kept = _per_share_scale_pick(
                    conv,
                    [
                        (e_, v_)
                        for e_, v_, p_ in local_abs.get(concept, [])
                        if p_ != pid
                    ],
                    conv[0][0].end_date,
                )
                if kept is None:
                    out.append(
                        CellResult(
                            concept, pid, HIDE_UNITS_SCALE, None, (), None, None, ()
                        )
                    )
                    continue
                if len(kept) < len(conv):
                    note = f"dropped {len(conv) - len(kept)} copy(ies) off by a units scale"
                    conv = kept
            # Fix (1), Verifier 1000: the period's OWN ORIGINAL filing (the
            # earliest periodic copy) must be usable and agree with the value
            # shown; a later copy alone never decides (TRMB, DCI shift
            # comparatives by a year; XYL, TSCO, GLPI put the current rate on
            # a prior period; OHI, BWA, WTRG, OGE, TEX one-off errors).
            original = min(cands, key=lambda f: (f.filing_date, f.fact_id))
            if "off by a units scale" in note and not any(
                x[0] is original for x in conv
            ):
                # the original was the units-scale copy (AM 10-K 484,042 vs
                # 484,042,000 in four later filings): the earliest kept copy
                # stands in for it
                original = conv[0][0]
            if not any(x[0] is original for x in conv):
                after = post_event_copies(conv, events)
                if after is not None and _all_agree(after, kind):
                    # Verifier run 6, QXO FY2023 -1.63: the 2023 10-K's basis
                    # is unresolved, but two later 10-Ks filed after every
                    # split event re-present the year on the current basis
                    conv, original = after, after[0][0]
                    note = (note + "; " if note else "") + (
                        f"original's basis unresolved; {len(after)} copies filed after every split event"
                    )
            if not any(x[0] is original for x in conv):
                out.append(
                    CellResult(
                        concept,
                        pid,
                        HIDE_BASIS_REVIEW,
                        None,
                        (),
                        None,
                        None,
                        (),
                        note="original filing's share basis is not resolved",
                    )
                )
                continue
            if concept == "dividends_per_share_resolved":
                # A zero DPS copy in a filing that shows dividends paid for the
                # same period is a filer error (MSI 9M 2011, MORN 2010).
                zeros = [
                    x
                    for x in conv
                    if x[2] == 0
                    and paid.get((x[0].filing_id, x[0].start_date, x[0].end_date))
                ]
                if zeros and len(zeros) < len(conv):
                    conv = [x for x in conv if x not in zeros]
                    if not any(x[0] is original for x in conv):
                        # the original was a contradicted zero (AES Q2 2020)
                        original = min(
                            (x[0] for x in conv),
                            key=lambda f: (f.filing_date, f.fact_id),
                        )
            if concept == "dividends_per_share_resolved" and len(conv) > 1:
                # A DPS on a longer context below the sum of the company's own
                # filed quarters inside it is a quarterly rate on a YTD or
                # annual context (LEA 9M 2014 0.20 in 0000842162-14-000002,
                # while the quarters are 0.20 each).
                low = [x for x in conv if _ytd_below_quarters(x, quarter_dps)]
                if low and len(low) < len(conv):
                    conv = [x for x in conv if x not in low]
                    note = (note + "; " if note else "") + (
                        f"dropped {len(low)} copy(ies) below the sum of filed quarters"
                    )
            agree = _all_agree(conv, kind)
            if not agree and concept == "dividends_per_share_resolved":
                # Two or more copies from the period's own vintage (filed within
                # 180 days of its end) that agree stand over any later majority:
                # dividends are not restated, later filings repeat another
                # year's rate on comparatives (PPL 2022-06: 0.225 in
                # 0000922224-22-000042 and -000049 vs 0.24 in three 2023 10-Qs;
                # Verifier run 3).
                vintage = [
                    x for x in conv if (x[0].filing_date - x[0].end_date).days <= 180
                ]
                if len(vintage) >= 2 and _all_agree(vintage, kind):
                    conv = vintage
                    agree = True
                    note = (note + "; " if note else "") + "own-vintage copies agree"
            if not agree and len(conv) > 1:
                # A DPS rate on a LONGER context equal to a 3-month value in its
                # own filing is a rate error, dropped first (LEA 9M 2014 0.20 in
                # 0000842162-14-000002, either dividend tag).
                rates = [
                    x
                    for x in conv
                    if _rate_on_longer_context(x[0], pid, same_filing, period_days)
                ]
                if rates and len(rates) < len(conv):
                    conv = [x for x in conv if x not in rates]
                    note = (note + "; " if note else "") + (
                        f"dropped {len(rates)} rate-on-longer-context copy(ies)"
                    )
                    agree = _all_agree(conv, kind)
            if not agree and len(conv) > 1:
                # Run 7 (Verifier run 6: SWK Q4 2017 -0.72 in the FY2019 10-K,
                # FORM 9M 2017 0.03 in a 10-K): a copy of a column its filing
                # does not present (a 6M/9M span in a 10-K; an interim period
                # older than the filing's comparatives) is a clerical copy.
                unpresented = [
                    x for x in conv if x[0] is not original and not_presented(x[0])
                ]
                rest = [x for x in conv if x not in unpresented]
                if unpresented and rest and _all_agree(rest, kind):
                    note = (note + "; " if note else "") + (
                        f"dropped {len(unpresented)} copy(ies) of a column the filing does not present"
                    )
                    conv, agree = rest, True
            if (
                not agree
                and len(conv) > 1
                and concept != "dividends_per_share_resolved"
            ):
                # Run 7 (NWSA FY2016 10-K 0001193125-16-679975: Jul-Sep 2014
                # 0.30 and Jul-Sep 2015 0.11, each the OTHER quarter's
                # consensus): a swapped pair is two label errors.
                swapped = [
                    x
                    for x in conv
                    if _is_swapped_copy(x[0], pid, by_tag_period, by_filing_tag)
                ]
                rest = [x for x in conv if x not in swapped]
                if swapped and rest and _all_agree(rest, kind):
                    note = (note + "; " if note else "") + (
                        f"dropped {len(swapped)} swapped copy(ies)"
                    )
                    conv, agree = rest, True
            if (
                not agree
                and len(conv) > 1
                and concept != "dividends_per_share_resolved"
            ):
                # EPS label shift: a NON-original copy equal to the same tag's
                # value for another period in its own filing (AMZN FY2012 10-K
                # 0001193125-13-028520; NVDA FY2018 10-K Q2 0.98 on the 6M
                # context). Not for DPS: equal rates in neighbouring quarters
                # are normal there.
                shifted = [
                    x
                    for x in conv
                    if x[0] is not original
                    and any(
                        x[0].value in vals
                        for other, vals in same_filing[
                            (x[0].filing_id, x[0].tag, x[0].unit)
                        ].items()
                        if other != pid
                    )
                ]
                rest = [x for x in conv if x not in shifted]
                if shifted and rest and _all_agree(rest, kind):
                    note = (note + "; " if note else "") + (
                        f"dropped {len(shifted)} label-shifted copy(ies)"
                    )
                    conv, agree = rest, True
            if not agree and len(conv) > 1 and kind == SHARES:
                # A share count corrected by an amendment filed within 60 days
                # of the original (ANF 10-Q/A next day 68,016,186 vs 86,016,786;
                # BWXT 10-K/A; SNDK 10-Q/A 144,863,251 vs 114,863,251; Verifier
                # run 5): the amendment's count, if no later copy disagrees.
                orig_f = conv_original(conv, original)[0]
                amends = [
                    x
                    for x in conv
                    if _is_amendment(x[0])
                    and 0 <= (x[0].filing_date - orig_f.filing_date).days <= 60
                    and not _all_agree([x, conv_original(conv, original)], kind)
                ]
                if amends:
                    fixed = [
                        x for x in conv if x[0].filing_date >= amends[0][0].filing_date
                    ]
                    if _all_agree(fixed, kind):
                        note = (note + "; " if note else "") + "corrected by amendment"
                        conv, agree = fixed, True
            if not agree and len(conv) > 1:
                # Majority of LATER copies (Verifier other_changed recheck): a
                # lone outlier never beats agreeing later copies (TEX Q2 2020
                # 0.12 vs 0, 0; DCI Q4 FY2015 0.34 vs 0.175 x2; OC; AMGN; COO;
                # TSCO 0.22 vs 1.03 x5). The winner needs >= 2 later copies and
                # strictly more than any other later group; otherwise a real
                # restatement or an unresolved copy is held (MSFT ASC 606 2.10
                # vs 2.56; XYL 0.24 vs one 0.26).
                # Dominion Q1 2024 EPS (Verifier run 3): three filed vintages
                # (0.78 / 0.50 / 0.46), each restating net income: held.
                all_groups: list[list] = []
                for x in conv:
                    for g in all_groups:
                        if _all_agree([g[0], x], kind):
                            g.append(x)
                            break
                    else:
                        all_groups.append([x])
                three_vintages = (
                    concept != "dividends_per_share_resolved" and len(all_groups) >= 3
                )
                later = (
                    [] if three_vintages else [x for x in conv if x[0] is not original]
                )
                vote: list[list] = []
                for x in later:
                    for g in vote:
                        if _all_agree([g[0], x], kind):
                            g.append(x)
                            break
                    else:
                        vote.append([x])
                vote.sort(key=len, reverse=True)
                orig_group = [
                    x
                    for x in conv
                    if _all_agree([x, conv_original(conv, original)], kind)
                ]
                n_groups = (
                    len(vote) + (0 if any(x in vote[0] for x in orig_group) else 1)
                    if vote
                    else 1
                )
                if (
                    vote
                    and len(vote[0]) >= 2
                    and (len(vote) == 1 or len(vote[0]) > len(vote[1]))
                    and not (
                        # PPL 2022-06 (Verifier run 3): three later 10-Qs repeat
                        # the NEXT year's rate on the comparative; two originals
                        # agree. A shifted later majority never beats them.
                        len(orig_group) >= 2
                        and all(
                            _equals_next_year_same_position(
                                x[0], same_filing, period_span
                            )
                            for x in vote[0]
                        )
                    )
                ):
                    note = (note + "; " if note else "") + (
                        f"majority of later copies {len(vote[0])} of {len(later)}"
                    )
                    conv = sorted(
                        vote[0], key=lambda x: (x[0].filing_date, x[0].fact_id)
                    )
                    agree = _all_agree(conv, kind)
                elif (
                    (
                        concept == "dividends_per_share_resolved"
                        # a count at a date is not restated either; a lone later
                        # copy is another date's count (TSCO 2015-03-28 vs the
                        # 2014-09-27 count) or a typo (TTEK 2019-06-30)
                        or (
                            kind == SHARES
                            and (original.filing_date - original.end_date).days
                            <= OWN_VINTAGE_DAYS
                        )
                    )
                    and orig_group
                    and any(x[0] is original for x in conv)
                ):
                    # Dividends are not restated: with no clean later majority
                    # the original filing's value stands (RSG April 2017 0.32,
                    # PPL 2017-11 0.395, OC 2019-09-30 0.22, NSC Q3 2019 0.94,
                    # OGE Q3 2020 0.4025, MSI Q3 2011 0.22; later filings put
                    # another year's rate on the comparative).
                    note = (
                        note + "; " if note else ""
                    ) + "original filing's value (not restated)"
                    conv = sorted(
                        orig_group, key=lambda x: (x[0].filing_date, x[0].fact_id)
                    )
                    agree = _all_agree(conv, kind)
                elif n_groups >= 3:
                    note = (
                        note + "; " if note else ""
                    ) + "three or more filed vintages (Dominion pattern)"
            cand_view = tuple(
                (f.fact_id, f.accession, f.value, fac, c) for f, fac, c in conv
            )
            if not agree:
                factors = {fac for _, fac, _ in conv}
                reason = HIDE_BASIS_CONFLICT if len(factors) > 1 else HIDE_RESTATED
                if reason == HIDE_RESTATED and RESTATEMENT_POLICY == "leave":
                    continue  # not this pass's decision: today's cell stays
                out.append(
                    CellResult(
                        concept, pid, reason, None, (), None, None, cand_view, note
                    )
                )
                continue
            if not any(x[0] is original for x in conv):
                # the original was dropped as a rate-on-longer-context error:
                # the earliest remaining copy is the period's original now
                original = conv[0][0]
            f, fac, value = conv[-1]
            # (the quarter-equals-year guard is retired: Verifier run 3 found
            # SSNC and HST false holds; its real case, NVDA Q4 FY2015, is the
            # annual-on-quarter check in _dps_same_filing_checks)
            ratio_ids: list[int] = []
            for eid in basis[f.filing_id].event_ids:
                ratio_ids.extend(d.fact.fact_id for d in by_local[eid].disclosures[:1])
            out.append(
                CellResult(
                    concept,
                    pid,
                    SHOWN,
                    value,
                    (f.fact_id, *ratio_ids),
                    f,
                    fac,
                    cand_view,
                    note,
                )
            )
    out = _dps_year_solve(
        out, all_conv, dps_copies_by_span, mapped_tags.get("dividends_per_share", [])
    )
    out = _one_dividend_basis(
        out, mapped_tags.get("dividends_per_share", []), dps_copies_by_span, paid
    )
    dps_raw_by_filing: dict[int, list[tuple[date | None, date, Decimal]]] = defaultdict(
        list
    )
    for f in facts:
        if f.usable_source and f.tag in (
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid",
        ):
            dps_raw_by_filing[f.filing_id].append((f.start_date, f.end_date, f.value))
    out = _dps_quarter_equals_ytd(out, dps_raw_by_filing, dps_copies_by_span)
    out = _dps_span_agrees_with_parts(
        out,
        company_dividend_basis(
            dps_copies_by_span, mapped_tags.get("dividends_per_share", [])
        ),
        dps_copies_by_span,
    )
    dps_by_filing: dict[int, list[tuple[date | None, date, Decimal, date]]] = (
        defaultdict(list)
    )
    for f in facts:
        if f.usable_source and f.tag in (
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid",
        ):
            dps_by_filing[f.filing_id].append(
                (f.start_date, f.end_date, f.value, f.filing_date)
            )
    out = _dps_same_filing_checks(
        out, paid, common_dividend_paid_per_share(facts, share_refs), dps_by_filing
    )
    return _eps_pair_check(
        _dps_scale_guard(_dps_scale_guard(out), "shares_outstanding_resolved")
    )


EPS_PAIR_TOL = Decimal("0.011")  # two half-cent roundings
EPS_PAIR_SCALE = Decimal(1000)


def _eps_pair_check(cells: list[CellResult]) -> list[CellResult]:
    """ASC 260: dilution never raises EPS, and with a loss diluted equals
    basic. So for one period, shown basic and diluted EPS cannot be
    (a) basic < 0 < diluted (NWSA Jul-Sep 2015 -0.04 vs 0.30, CDE Q4 2016),
    (b) 0 < basic < diluted beyond rounding, when (a)/(b) come from two
    different filings (a filer-printed pair stands), or (c) a units scale apart
    (ASTS diluted 17,600,000: a share count on the EPS tag). Both cells are
    hidden: the pair alone cannot say which is wrong. Basic > 0 > diluted
    stays (warrant fair-value gains leave the diluted numerator: GSAT, CG)."""
    by_span: dict[tuple, dict[str, CellResult]] = defaultdict(dict)
    for c in cells:
        if (
            c.status == SHOWN
            and c.value is not None
            and c.chosen is not None
            and c.concept in ("basic_eps_resolved", "diluted_eps_resolved")
        ):
            by_span[(c.chosen.start_date, c.chosen.end_date)][c.concept] = c
    bad: set[tuple[str, int]] = set()
    for pair in by_span.values():
        if len(pair) != 2:
            continue
        bc, dc = pair["basic_eps_resolved"], pair["diluted_eps_resolved"]
        b, d = bc.value, dc.value
        assert (
            b is not None
            and d is not None
            and bc.chosen is not None
            and dc.chosen is not None
        )
        scale = (
            b != 0
            and d != 0
            and (abs(d) > EPS_PAIR_SCALE * abs(b) or abs(b) > EPS_PAIR_SCALE * abs(d))
        )
        # Verifier run 7.4: a pair the filer PRINTED together can have diluted
        # above basic (a preferred add-back: NTNX 6M FY2024 0.07 / 0.09, ZWS
        # FY2018 0.51 / 0.62), so a sign or order conflict hides only a pair
        # assembled from two different filings (NWSA Jul-Sep 2015)
        printed = bc.chosen.filing_id == dc.chosen.filing_id
        if scale or (not printed and ((b < 0 < d) or (0 < b and d > b + EPS_PAIR_TOL))):
            bad.update((c.concept, c.period_id) for c in pair.values())
    if not bad:
        return cells
    return [
        CellResult(
            c.concept,
            c.period_id,
            HIDE_EPS_PAIR,
            None,
            (),
            c.chosen,
            c.factor,
            c.candidates,
            "basic and diluted EPS contradict each other",
        )
        if (c.concept, c.period_id) in bad
        else c
        for c in cells
    ]


DIVIDENDS_PAID_TAGS = ("PaymentsOfDividendsCommonStock", "PaymentsOfDividends")
OWN_FILING_SCALE_NOTE = "own filing's other share counts sit a units scale away"
LOCAL_WINDOW_DAYS = 1100


def conv_original(conv, original):
    return next(x for x in conv if x[0] is original)


def _equals_next_year_same_position(f: SourceFact, same_filing, period_span) -> bool:
    """f's value equals the same tag's value, in f's own filing, for the period
    one year later at the same position (start and end +1 year, +-10 days)."""
    if f.start_date is None:
        return False
    for other, vals in same_filing[(f.filing_id, f.tag, f.unit)].items():
        span = period_span.get(other)
        if not span or span[0] is None:
            continue
        ds = (span[0] - f.start_date).days
        de = (span[1] - f.end_date).days
        if 355 <= ds <= 375 and 355 <= de <= 375 and f.value in vals:
            return True
    return False


def _ytd_below_quarters(x, quarter_dps) -> bool:
    f, _fac, value = x
    if f.start_date is None:
        return False
    days = (f.end_date - f.start_date).days
    if days <= 100:
        return False
    inside = [
        v
        for (s_, e_), v in quarter_dps.items()
        if s_ >= f.start_date and e_ <= f.end_date
    ]
    need = round(days / 91.3)
    return len(inside) >= need and value < sum(inside, Decimal(0)) - FY_RATE_TOL


def _rate_on_longer_context(f: SourceFact, pid: int, same_filing, period_days) -> bool:
    """A DPS on a > 100-day context equal to a <= 100-day value of the same
    tag in its own filing (a quarterly rate on a YTD or annual context)."""
    if f.tag not in (
        "CommonStockDividendsPerShareDeclared",
        "CommonStockDividendsPerShareCashPaid",
    ):
        return False
    if period_days.get(pid, 0) <= 100:
        return False
    return any(
        f.value in vals
        for tag in (
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid",
        )
        for other, vals in same_filing[(f.filing_id, tag, f.unit)].items()
        if other != pid and period_days.get(other, 999) <= 100
    )


YEAR_SOLVE_MAX_COMBOS = 256
YEAR_SOLVE_TOL = Decimal("0.0051")


YEAR_SOLVE_NOTE = "set by the fiscal year's filed totals"


PER_SHARE_SCALE_STEPS = (Decimal(1000), Decimal(10**6))


def _per_share_scale_pick(
    conv: list[tuple[SourceFact, Fraction, Decimal]],
    local: list[tuple[date, Decimal]],
    end: date,
) -> list | None:
    """Per-share copies that disagree only by a units scale (x1,000 or
    x1,000,000; NPO Q3 2022 diluted 1.29 vs 1,290,000 in the 10-K, BE Q3 2025
    -0.10 vs -100). Keeps the strict majority; on a tie, the group within 10x
    of the company's local median magnitude (other periods within 1,100
    days) while the other is at least 100x off; None (hide) otherwise.
    Copies with no such relation are returned unchanged."""
    groups: list[list] = []
    for x in conv:
        for g in groups:
            if g[0][2] == x[2]:
                g.append(x)
                break
        else:
            groups.append([x])
    if len(groups) != 2:
        return conv
    a, b = groups[0][0][2], groups[1][0][2]
    if a == 0 or b == 0 or (a > 0) != (b > 0):
        return conv
    hi, lo = (abs(a), abs(b)) if abs(a) > abs(b) else (abs(b), abs(a))
    if not any(abs(hi / lo - k) <= k * Decimal("0.005") for k in PER_SHARE_SCALE_STEPS):
        return conv
    groups.sort(key=len, reverse=True)
    if len(groups[0]) > len(groups[1]):
        keep = groups[0]
    else:
        others = sorted(
            v for e_, v in local if abs((e_ - end).days) <= LOCAL_WINDOW_DAYS
        )
        if len(others) < 3:
            return None
        med = others[len(others) // 2]

        def off(v: Decimal) -> Decimal:
            r = abs(v) / med
            return r if r >= 1 else 1 / r

        g0, g1 = sorted(groups, key=lambda g: off(g[0][2]))
        if not (off(g0[0][2]) <= 10 and off(g1[0][2]) >= 100):
            return None
        keep = g0
    return sorted(keep, key=lambda x: (x[0].filing_date, x[0].fact_id))


def _dps_year_solve(
    cells: list[CellResult],
    all_conv: Mapping[tuple[str, int], list],
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
    tags: list[str],
) -> list[CellResult]:
    """Verifier run 4: an own-vintage or majority copy of a quarterly dividend
    can be wrong (COST Q2 FY2013 0.275 without the $7 special; OKE Q2/Q3 2014
    0.575/0.59 vs 0.56/0.575; COP Q3 2021 0.46 vs 0.43; a 10-Q "declared"
    fact can be declared after quarter end). For each fiscal year with a filed
    total, choose for every quarter one of its FILED values so that the
    quarters add up to the filed 6M, 9M and full-year totals; a unique
    solution sets the quarters, anything else leaves them as they are. No
    value is derived: every chosen value is a filed copy."""
    concept = "dividends_per_share_resolved"
    qcells: dict[int, CellResult] = {}
    spans: dict[int, tuple[date, date]] = {}
    cum_cells: dict[tuple[date, date], CellResult] = {}
    for c in cells:
        if c.concept != concept:
            continue
        copies = all_conv.get((concept, c.period_id))
        if not copies:
            continue
        f0 = copies[0][0]
        if (
            f0.start_date is not None
            and 150 <= (f0.end_date - f0.start_date).days <= 300
        ):
            cum_cells[(f0.start_date, f0.end_date)] = c
        # up to 120 days: 12/12/12/16-week fiscal years (COST Q4 is 16 weeks)
        if f0.start_date is None or not (
            80 <= (f0.end_date - f0.start_date).days <= 120
        ):
            continue
        qcells[c.period_id] = c
        spans[c.period_id] = (f0.start_date, f0.end_date)
    if not qcells:
        return cells
    tag_order = list(tags) + [
        t
        for t in (
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid",
        )
        if t not in tags
    ]

    def total_tag(start: date, end: date) -> str | None:
        copies = span_copies.get((start, end), [])
        for t in tag_order:
            if len({v for f, v in copies if f.tag == t}) == 1:
                return t
        return None

    def total(start: date, end: date) -> Decimal | None:
        """The filed total for a span from the first tag whose copies of it
        all agree; a tag that disagrees with itself is not a total (COP's
        "declared" 9M 2021 copies 0.46 and 1.75; CashPaid gives 1.29)."""
        copies = span_copies.get((start, end), [])
        for t in tag_order:
            vals = {v for f, v in copies if f.tag == t}
            if len(vals) == 1:
                return next(iter(vals))
        return None

    fy_spans = sorted(
        {k for k in span_copies if k[0] is not None and (k[1] - k[0]).days >= 350}
    )
    changes: dict[int, tuple[Decimal, SourceFact]] = {}
    year_tag: dict[int, str | None] = {}
    cum_changes: dict[int, tuple[Decimal, SourceFact] | None] = {}
    for fs, fe in fy_spans:
        fy_total = total(fs, fe)
        if fy_total is None:
            continue
        quarters = sorted(
            (pid for pid, (qs, qe) in spans.items() if qs >= fs and qe <= fe),
            key=lambda pid: spans[pid][1],
        )
        # The quarters must run consecutively from the fiscal year start; with
        # fewer than four filed quarters (a derived-only Q4: COP 2021) the
        # filed 6M / 9M totals still constrain them.
        if (
            not quarters
            or len(quarters) > 4
            or abs((spans[quarters[0]][0] - fs).days) > 7
        ):
            continue
        if any(
            abs((spans[b][0] - spans[a][1]).days) > 7
            for a, b in itertools.pairwise(quarters)
        ):
            continue
        cands: list[list[tuple[Decimal, SourceFact]]] = []
        for pid in quarters:
            seen: dict[Decimal, SourceFact] = {}
            for f, _fac, v in all_conv[(concept, pid)]:
                seen.setdefault(v, f)
            # the other dividend tag's filed copies of the same quarter too
            for f, v in span_copies.get(spans[pid], []):
                seen.setdefault(v, f)
            cands.append(list(seen.items()))
        constraints = [(4, fy_total)] if len(quarters) == 4 else []
        for k, pid in enumerate(quarters[:3], start=1):
            if k < 2:
                continue
            cum = total(fs, spans[pid][1])
            if cum is not None:
                constraints.append((k, cum))
        if not constraints:
            continue
        combos = 1
        for c_ in cands:
            combos *= len(c_)
        if combos > YEAR_SOLVE_MAX_COMBOS or combos == 1:
            continue
        hits = []
        for combo in itertools.product(*cands):
            vals = [v for v, _f in combo]
            ok = all(
                # dividend totals add up to the cent: half a cent, whatever k
                abs(sum(vals[:k], Decimal(0)) - t) <= YEAR_SOLVE_TOL
                for k, t in constraints
            )
            if ok:
                hits.append(combo)
        if len({tuple(v for v, _ in h) for h in hits}) != 1:
            continue
        # a filed 6M / 9M cell must add up to the solved quarters (COP 9M 2021:
        # a later "declared" copy 1.75 against 0.43 x 3 = 1.29)
        for k in (2, 3):
            if k > len(quarters):
                break
            cc = cum_cells.get((fs, spans[quarters[k - 1]][1]))
            if cc is None or cc.status != SHOWN or cc.value is None:
                continue
            want = sum((v for v, _f in hits[0][:k]), Decimal(0))
            if abs(cc.value - want) <= YEAR_SOLVE_TOL:
                continue
            match = next(
                (
                    (v, f)
                    for f, v in [
                        (f_, v_) for f_, _fac, v_ in all_conv[(concept, cc.period_id)]
                    ]
                    + span_copies.get((fs, spans[quarters[k - 1]][1]), [])
                    if abs(v - want) <= YEAR_SOLVE_TOL
                ),
                None,
            )
            cum_changes[cc.period_id] = match
            year_tag[cc.period_id] = total_tag(fs, fe)
        for pid, (v, f) in zip(quarters, hits[0]):
            cur = qcells[pid]
            if cur.status == SHOWN and cur.value == v:
                continue
            if cur.status not in (SHOWN, HIDE_RESTATED, HIDE_BASIS_CONFLICT):
                continue
            changes[pid] = (v, f)
            year_tag[pid] = total_tag(fs, fe)
    if not changes and not cum_changes:
        return cells
    out = []
    for c in cells:
        if c.concept == concept and c.period_id in cum_changes:
            m = cum_changes[c.period_id]
            if m is None:
                out.append(
                    CellResult(
                        c.concept,
                        c.period_id,
                        HIDE_DPS_INVALID,
                        None,
                        (),
                        c.chosen,
                        c.factor,
                        c.candidates,
                        "does not add up to the fiscal year's filed quarters",
                    )
                )
                continue
            changes[c.period_id] = m
        hit = changes.get(c.period_id) if c.concept == concept else None
        if hit is None:
            out.append(c)
            continue
        v, f = hit
        out.append(
            CellResult(
                c.concept,
                c.period_id,
                SHOWN,
                v,
                (f.fact_id,),
                f,
                c.factor,
                c.candidates,
                f"{YEAR_SOLVE_NOTE} ({year_tag.get(c.period_id)})",
            )
        )
    return out


DPS_BASIS_FROM = date(2015, 1, 1)
OWN_VINTAGE_DAYS = 180
PAID_MIN_PER_QUARTER = Decimal("0.01")


def _confirmed_by_own_vintage_copies(
    c: CellResult,
    dps_by_filing: Mapping[int, list[tuple[date | None, date, Decimal, date]]] | None,
) -> bool:
    """Two or more filings file the value for this quarter (either dividend
    tag), one of them within 180 days of the quarter end: a real rate (HL Q3
    2021 0.01125 in 0001437749-21-025360 and 0001193125-22-281241), not one
    filing's annual figure on a quarter."""
    if not dps_by_filing or c.chosen is None:
        return False
    s0, e0, v0 = c.chosen.start_date, c.chosen.end_date, c.value
    dates = {
        fd
        for rows in dps_by_filing.values()
        for s_, e_, v, fd in rows
        if s_ == s0 and e_ == e0 and v == v0
    }
    return len(dates) >= 2 and any((fd - e0).days <= OWN_VINTAGE_DAYS for fd in dates)


def _same_as_prior_year_quarter(
    c: CellResult,
    dps_by_filing: Mapping[int, list[tuple[date | None, date, Decimal, date]]] | None,
) -> bool:
    """The chosen filing also files the same quarter a year earlier at the
    same value: a steady quarterly rate, not an annual amount (VAL Q1 2019
    0.04 beside Q1 2018 0.04 in 0000314808-19-000085)."""
    if not dps_by_filing or c.chosen is None or c.chosen.start_date is None:
        return False
    for s_, e_, v, _fd in dps_by_filing.get(c.chosen.filing_id, []):
        if (
            s_ is not None
            and abs((c.chosen.end_date - e_).days - 365) <= 10
            and abs((c.chosen.start_date - s_).days - 365) <= 10
            and v == c.chosen.value
        ):
            return True
    return False


def _paid_confirms(
    c: CellResult,
    paid_per_share: Mapping[tuple[int, date | None, date], Decimal] | None,
) -> bool:
    """The same filing's common dividends paid over its own share count equal
    the value within 10% (WY Q1 2022 1.63: 1,218M paid, base plus variable;
    VAL Q1 2019 0.04: 4.5M over the re-based weighted shares)."""
    if not paid_per_share or c.chosen is None or c.value is None or c.value <= 0:
        return False
    ps = paid_per_share.get(
        (c.chosen.filing_id, c.chosen.start_date, c.chosen.end_date)
    )
    return ps is not None and abs(ps - c.value) <= Decimal("0.10") * c.value


def common_dividend_paid_per_share(
    facts: list[SourceFact], share_refs: Mapping[int, list[Decimal]]
) -> dict[tuple[int, date | None, date], Decimal]:
    """(filing, start, end) -> PaymentsOfDividendsCommonStock over the
    filing's median share count (cover and weighted averages)."""
    out: dict[tuple[int, date | None, date], Decimal] = {}
    for f in facts:
        if (
            f.tag != "PaymentsOfDividendsCommonStock"
            or not f.usable_source
            or f.value <= 0
        ):
            continue
        refs = sorted(share_refs.get(f.filing_id, []))
        if refs:
            out[(f.filing_id, f.start_date, f.end_date)] = (
                f.value / refs[len(refs) // 2]
            )
    return out


def _common_dividend_paid_evidence(
    facts: list[SourceFact], share_refs: Mapping[int, list[Decimal]]
) -> dict[tuple[int, date | None, date], Decimal]:
    """(filing, start, end) -> evidence that the filing shows a COMMON
    dividend paid for that period: PaymentsOfDividendsCommonStock, or a
    positive CommonStockDividendsPerShareCashPaid. The generic
    PaymentsOfDividends also carries preferred, noncontrolling and
    dividend-equivalent payments (BPOP Q1 2015 620K before its first common
    dividend, WYNN Q1 2021 295K while suspended; Verifier run 5), so it
    counts only when, over the filing's own share count, it is at least a
    cent a quarter and at least a quarter of the company's nearest filed
    quarterly rate."""
    pos_q = sorted(
        (f.end_date, f.value)
        for f in facts
        if f.tag
        in (
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid",
        )
        and f.usable_source
        and f.value > 0
        and f.start_date is not None
        and 80 <= (f.end_date - f.start_date).days <= 120
    )
    out: dict[tuple[int, date | None, date], Decimal] = {}
    for f in facts:
        if not f.usable_source or f.value <= 0:
            continue
        key = (f.filing_id, f.start_date, f.end_date)
        if f.tag in (
            "PaymentsOfDividendsCommonStock",
            "CommonStockDividendsPerShareCashPaid",
        ):
            out[key] = f.value
            continue
        if f.tag != "PaymentsOfDividends" or f.start_date is None:
            continue
        refs = sorted(share_refs.get(f.filing_id, []))
        if not refs:
            out[key] = f.value  # no share count to judge by: keep the guard
            continue
        quarters = max(
            Decimal((f.end_date - f.start_date).days) / Decimal(91), Decimal(1)
        )
        per_q = f.value / refs[len(refs) // 2] / quarters
        near = [
            (abs((e_ - f.end_date).days), v)
            for e_, v in pos_q
            if abs((e_ - f.end_date).days) <= LOCAL_WINDOW_DAYS
        ]
        nearest = min(near)[1] if near else None
        if per_q >= PAID_MIN_PER_QUARTER and (nearest is None or per_q * 4 >= nearest):
            out[key] = f.value
    return out


def _dps_same_filing_checks(
    cells: list[CellResult],
    paid: Mapping[tuple[int, date | None, date], Decimal],
    paid_per_share: Mapping[tuple[int, date | None, date], Decimal] | None = None,
    dps_by_filing: Mapping[int, list[tuple[date | None, date, Decimal, date]]]
    | None = None,
) -> list[CellResult]:
    """Verifier 1000 fix (2), filing evidence only:
    - DPS below zero (OHI Q1 2019 -0.66);
    - DPS zero while the same filing shows dividends paid for that period
      (BWA FY2019, 140M paid);
    - an annual DPS below the sum of its filed quarters (a quarterly rate on
      the full year: WTRG FY2024 0.3255 vs 1.2652; BPOP FY2016 0.15);
    - an interim DPS >= 2.5x its neighbours' median (an annual rate on a
      quarter: OGE Q1 2020 1.505)."""
    dps = [
        c
        for c in cells
        if c.concept == "dividends_per_share_resolved"
        and c.status == SHOWN
        and c.chosen is not None
        and c.value is not None
    ]

    def days(c: CellResult) -> int:
        assert c.chosen is not None
        return (
            (c.chosen.end_date - c.chosen.start_date).days if c.chosen.start_date else 0
        )

    # one quarter per end date, the longest (BX 2014: 04-01 and 04-08 to 06-30)
    _q_by_end: dict[date, CellResult] = {}
    for c in dps:
        if 80 <= days(c) <= 100:
            assert c.chosen is not None
            e_ = c.chosen.end_date
            if e_ not in _q_by_end or days(c) > days(_q_by_end[e_]):
                _q_by_end[e_] = c
    quarters = list(_q_by_end.values())
    bad: dict[tuple[str, int], str] = {}
    for c in dps:
        assert c.chosen is not None and c.value is not None
        key = (c.concept, c.period_id)
        if c.value < 0:
            bad[key] = "negative dividend per share"
            continue
        if c.value == 0 and paid.get(
            (c.chosen.filing_id, c.chosen.start_date, c.chosen.end_date)
        ):
            bad[key] = "zero dividend per share while the filing shows dividends paid"
            continue
        if days(c) >= 350 and c.chosen.start_date is not None:
            inside = [
                q.value
                for q in quarters
                if q.chosen is not None
                and q.chosen.start_date is not None
                and q.chosen.start_date >= c.chosen.start_date
                and q.chosen.end_date <= c.chosen.end_date
                and q.value is not None
            ]
            if len(inside) >= 3 and c.value < sum(inside, Decimal(0)) - FY_RATE_TOL:
                bad[key] = "annual dividend per share below the sum of its quarters"
        elif 80 <= days(c) <= 100:
            # An annual amount on a quarter: equal (0.5%) to the sum of four
            # consecutive filed quarters around it (OGE Q1 2020 1.505 = the
            # 2019 total); a special dividend that matches no such sum stays
            # (HST Q2 2026 0.92; Verifier run 3).
            seq = sorted(
                (
                    q
                    for q in quarters
                    if q is not c and q.chosen is not None and q.value is not None
                ),
                key=lambda q: q.chosen.end_date,  # type: ignore[union-attr]
            )
            for k in range(len(seq) - 3):
                window = seq[k : k + 4]
                if any(not q.value or q.value <= 0 for q in window):
                    continue  # a first dividend year is not an annual total (MSI, MORN)
                if abs((window[-1].chosen.end_date - c.chosen.end_date).days) > 400:  # type: ignore[union-attr]
                    continue
                total = sum((q.value or Decimal(0) for q in window), Decimal(0))
                cv = c.value
                assert cv is not None
                if (
                    total > 0
                    # relative only: HL's sub-cent quarters (0.0025 ...) sit
                    # within an absolute half cent of many sums
                    and abs(cv - total) <= Decimal("0.005") * total
                    and not _paid_confirms(c, paid_per_share)
                    and not _same_as_prior_year_quarter(c, dps_by_filing)
                    and not _confirmed_by_own_vintage_copies(c, dps_by_filing)
                ):
                    bad[key] = (
                        "quarterly dividend per share looks like an annual amount"
                    )
                    break
    if not bad:
        return cells
    return [
        CellResult(
            c.concept,
            c.period_id,
            HIDE_DPS_INVALID,
            None,
            (),
            c.chosen,
            c.factor,
            c.candidates,
            bad[(c.concept, c.period_id)],
        )
        if (c.concept, c.period_id) in bad
        else c
        for c in cells
    ]


WASO_TAGS = (
    "WeightedAverageNumberOfSharesOutstandingBasic",
    "WeightedAverageNumberOfDilutedSharesOutstanding",
)
_SCALE_STEPS = (Decimal(1000), Decimal(10**6))


def _off_scale_in_own_filing(f: SourceFact, refs: Mapping[int, list[Decimal]]) -> bool:
    """True when every other share count in f's own filing sits a factor
    1000 or 10^6 away from f (within 25%), i.e. f carries a units error."""
    others = [v for v in refs.get(f.filing_id, []) if v != f.value]
    if not others or f.value <= 0:
        return False

    def off(v: Decimal) -> bool:
        for k in _SCALE_STEPS:
            for target in (v * k, v / k):
                if abs(f.value - target) <= Decimal("0.25") * target:
                    return True
        return False

    return all(off(v) for v in others)


def _dps_scale_guard(
    cells: list[CellResult], concept: str = "dividends_per_share_resolved"
) -> list[CellResult]:
    """Hide a shown value >= DPS_SCALE_SUSPECT_RATIO x (or <= 1/x) the median
    of the company's other shown values of the same concept and series
    (interim / annual; instants are one series), when at least
    DPS_SCALE_MIN_OTHERS others exist. DPS (VICI 262,500) and share counts on
    the current basis (DLTR 10-K 0000935703-11-000058: 123.5, a count in
    millions with no other share count in the filing); never EPS, which
    legitimately swings this much."""

    def series(c: CellResult) -> str:
        assert c.chosen is not None
        start = c.chosen.start_date
        days = (c.chosen.end_date - start).days if start else 0
        return "annual" if days >= 350 else "interim"

    dps = [
        c
        for c in cells
        if c.concept == concept
        and c.status == SHOWN
        and c.chosen is not None
        and c.value is not None
        and c.value > 0
    ]
    flagged: set[tuple[str, int]] = set()
    for c in dps:
        assert c.value is not None
        assert c.chosen is not None
        others = sorted(
            o.value
            for o in dps
            if o is not c
            and series(o) == series(c)
            and o.value
            and o.chosen is not None
            and abs((o.chosen.end_date - c.chosen.end_date).days) <= LOCAL_WINDOW_DAYS
        )
        if len(others) < DPS_SCALE_MIN_OTHERS:
            # too little local history: an own-filing scale flag decides alone
            if OWN_FILING_SCALE_NOTE in c.note:
                flagged.add((c.concept, c.period_id))
            continue
        med = others[len(others) // 2]
        ratio = c.value / med
        if ratio >= DPS_SCALE_SUSPECT_RATIO or ratio <= 1 / DPS_SCALE_SUSPECT_RATIO:
            flagged.add((c.concept, c.period_id))
    if not flagged:
        return cells
    return [
        CellResult(
            c.concept,
            c.period_id,
            HIDE_UNITS_SCALE,
            None,
            (),
            c.chosen,
            c.factor,
            c.candidates,
            "off the company's median by a units scale",
        )
        if (c.concept, c.period_id) in flagged
        else c
        for c in cells
    ]


def _all_agree(conv: list[tuple[SourceFact, Fraction, Decimal]], kind: str) -> bool:
    return all(
        abs(ca - cb) <= _agree_tol(a, fa, b, fb, kind)
        for i, (a, fa, ca) in enumerate(conv)
        for (b, fb, cb) in conv[i + 1 :]
    )


def company_dividend_basis(
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
    dps_tags: list[str],
) -> str | None:
    """AC-24 default (Verifier run 5): one dividend basis per company. The
    tag with more filed quarters ending 2015-01-01 or later (the whole
    history, then every filed period, when fewer than four); a tie goes to
    Declared (the first mapped tag)."""

    def counts(since: date | None, quarters_only: bool = True) -> Counter:
        n: Counter = Counter()
        for (start, end), copies in span_copies.items():
            if start is None:
                continue
            if quarters_only and not 80 <= (end - start).days <= 120:
                continue
            if since is not None and end < since:
                continue
            for t in {f.tag for f, _ in copies}:
                n[t] += 1
        return n

    count = counts(DPS_BASIS_FROM)
    if sum(count.values()) < 4:  # too few recent quarters: the whole history
        count = counts(None)
    if sum(count.values()) < 4:  # hardly any quarters: every filed period
        count = counts(None, quarters_only=False)
    if not count:
        return None
    order = list(dps_tags) + sorted(t for t in count if t not in dps_tags)
    return max(order, key=lambda t: (count[t], -order.index(t)))


def _equals_basis_quarters(
    value: Decimal,
    span: tuple,
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
    basis_tag: str,
) -> bool:
    """A 6M / 9M / annual value on the other tag that equals the sum of the
    basis tag's filed quarters covering the whole span is the same number on
    both bases (FE FY2016 Declared 1.44 = CashPaid 0.36 x 4)."""
    start, end = span
    if start is None or (end - start).days < 150:
        return False
    by_end: dict[date, tuple[date, Decimal]] = {}
    for (qs, qe), copies in span_copies.items():
        if qs is None or qs < start or qe > end or not 80 <= (qe - qs).days <= 120:
            continue
        vals = {v for f, v in copies if f.tag == basis_tag}
        if len(vals) != 1:
            continue
        if qe not in by_end or qs < by_end[qe][0]:
            by_end[qe] = (qs, next(iter(vals)))
    chain = sorted((qs, qe, v) for qe, (qs, v) in by_end.items())
    if (
        not chain
        or abs((chain[0][0] - start).days) > 7
        or abs((chain[-1][1] - end).days) > 7
    ):
        return False
    if any(abs((b[0] - a[1]).days) > 7 for a, b in itertools.pairwise(chain)):
        return False
    return abs(sum((v for _s, _e, v in chain), Decimal(0)) - value) <= YEAR_SOLVE_TOL


def _one_dividend_basis(
    cells: list[CellResult],
    dps_tags: list[str],
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
    paid: Mapping[tuple[int, date | None, date], Decimal],
) -> list[CellResult]:
    """One dividend basis per company, never mixed (AC-24 default, Verifier
    run 5: AES, AMT, CVI, CWEN, LMT and AFL mixed declared and paid quarters).
    A shown cell on the other tag is replaced by the basis tag's filed value
    when every basis copy of that period agrees and one of them is from the
    period's own vintage; otherwise it is hidden as dividend basis pending.
    A quarter the fiscal year's basis-tag totals fix stays."""
    concept = "dividends_per_share_resolved"
    basis_tag = company_dividend_basis(span_copies, dps_tags)
    if basis_tag is None:
        return cells
    paid_spans = {(s_, e_) for _f, s_, e_ in paid}
    together = declares_and_pays_together(span_copies)
    out = []
    for c in cells:
        if (
            c.concept != concept
            or c.status != SHOWN
            or c.chosen is None
            or c.chosen.tag == basis_tag
        ):
            out.append(c)
            continue
        span = (c.chosen.start_date, c.chosen.end_date)
        on_basis = sorted(
            ((f, v) for f, v in span_copies.get(span, []) if f.tag == basis_tag),
            key=lambda x: (x[0].filing_date, x[0].fact_id),
        )
        vals = {v for _f, v in on_basis}
        own = [
            f
            for f, _v in on_basis
            if (f.filing_date - f.end_date).days <= OWN_VINTAGE_DAYS
        ]
        if (
            len(vals) == 1
            and own
            and not (next(iter(vals)) == 0 and span in paid_spans)
        ):
            f0, v0 = on_basis[0]
            out.append(
                CellResult(
                    c.concept,
                    c.period_id,
                    SHOWN,
                    v0,
                    (f0.fact_id,),
                    f0,
                    c.factor,
                    c.candidates,
                    f"on the company's dividend basis ({basis_tag})",
                )
            )
            continue
        if (
            not vals
            and c.value is not None
            and span[0] is not None
            and (span[1] - span[0]).days >= 80
            and not (c.value == 0 and span in paid_spans)
            and together
        ):
            # Verifier run 6 (MSM 9M FY2021, HL FY2020, WYNN Q1 2021, ~25
            # regular-rate quarters): no basis-tag copy of the period exists
            # and wherever the company filed both tags for a quarter they
            # agree, so the off-basis value is the same number on both bases.
            out.append(
                CellResult(
                    c.concept,
                    c.period_id,
                    SHOWN,
                    c.value,
                    c.source_fact_ids,
                    c.chosen,
                    c.factor,
                    c.candidates,
                    f"no {basis_tag} copy; the company declares and pays in the same quarter",
                )
            )
            continue
        if c.value is not None and _equals_basis_quarters(
            c.value, span, span_copies, basis_tag
        ):
            out.append(
                CellResult(
                    c.concept,
                    c.period_id,
                    SHOWN,
                    c.value,
                    c.source_fact_ids,
                    c.chosen,
                    c.factor,
                    c.candidates,
                    f"equals the sum of its {basis_tag} quarters",
                )
            )
            continue
        out.append(
            CellResult(
                c.concept,
                c.period_id,
                HIDE_DPS_BASIS,
                None,
                (),
                c.chosen,
                c.factor,
                c.candidates,
                f"off the company's dividend basis ({basis_tag})",
            )
        )
    return out


TOGETHER_MIN_QUARTERS = 4


def declares_and_pays_together(
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
) -> bool:
    """True when the company files both dividend tags for at least four
    quarters since 2015 and, in every such quarter, each tag has one value and
    the two are equal (declared and paid in the same quarter). One quarter
    that differs (HWM Q1 2019 declared 0.08, paid 0.06) makes it False."""
    n = 0
    for (start, end), copies in span_copies.items():
        if start is None or end < DPS_BASIS_FROM or not 80 <= (end - start).days <= 120:
            continue
        decl = {v for f, v in copies if f.tag == "CommonStockDividendsPerShareDeclared"}
        paid = {v for f, v in copies if f.tag == "CommonStockDividendsPerShareCashPaid"}
        if not decl or not paid:
            continue
        if len(decl) != 1 or decl != paid:
            return False
        n += 1
    return n >= TOGETHER_MIN_QUARTERS


def post_event_copies(conv: list, events: list[Event]) -> list | None:
    """Copies filed after every non-rejected split event, on the current basis
    (factor 1), from at least two filings; None otherwise. Such a filing has
    seen every share-basis change, so its value needs no conversion."""
    dates = [
        d
        for e in events
        if e.status != "rejected"
        for d in (e.hi, e.lo)
        if d is not None
    ]
    last = max(dates) if dates else None
    post = [x for x in conv if x[1] == 1 and (last is None or x[0].filing_date > last)]
    if len({x[0].filing_id for x in post}) < 2:
        return None
    return sorted(post, key=lambda x: (x[0].filing_date, x[0].fact_id))


def _is_swapped_copy(f: SourceFact, pid: int, by_tag_period, by_filing_tag) -> bool:
    """Two periods' values exchanged inside ONE filing (NWSA FY2016 10-K
    0001193125-16-679975: Jul-Sep 2014 0.30, Jul-Sep 2015 0.11). Evidence both
    ways from the OTHER filings: this copy equals the other period's value
    there, and this filing's copy of the other period equals this period's
    value there."""
    own = {g.value for g in by_tag_period[(f.tag, pid)] if g.filing_id != f.filing_id}
    if len(own) != 1 or f.value in own:
        return False
    for other, vals in by_filing_tag[(f.filing_id, f.tag)].items():
        if other == pid or vals != own:
            continue
        theirs = {
            g.value for g in by_tag_period[(f.tag, other)] if g.filing_id != f.filing_id
        }
        if theirs == {f.value}:
            return True
    return False


NOT_PRESENTED_10K_DAYS = 760
NOT_PRESENTED_10Q_DAYS = 470


def not_presented(f: SourceFact) -> bool:
    """A filed copy of a column its own filing does not present: a 6M/9M span
    in a 10-K (annual reports print quarters or years, never a year-to-date),
    or an interim period ending before the filing's comparatives could reach
    (10-K quarterly data covers two fiscal years; a 10-Q compares with the
    prior year)."""
    if f.start_date is None:
        return False
    days = (f.end_date - f.start_date).days
    if days >= 350:
        return False
    age = (f.filing_date - f.end_date).days
    if f.form.startswith("10-K"):
        return 100 < days < 350 or age > NOT_PRESENTED_10K_DAYS
    return age > NOT_PRESENTED_10Q_DAYS


def _dps_quarter_equals_ytd(
    cells: list[CellResult],
    dps_raw_by_filing: Mapping[int, list[tuple[date | None, date, Decimal]]],
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
) -> list[CellResult]:
    """Verifier run 6, LOGI Oct-Dec 2021 (0001032975-22-000006): the 10-Q
    puts its 9M value 0.95 on the 3-month context too, while Jul-Sep alone
    was 0.95. A filed quarter equal to the same filing's year-to-date value
    that ends on the same day is impossible when an earlier quarter inside
    that year-to-date paid a positive dividend, so the quarter is hidden
    (never replaced by a subtraction)."""
    concept = "dividends_per_share_resolved"
    bad: set[int] = set()
    for c in cells:
        f = c.chosen
        if (
            c.concept != concept
            or c.status != SHOWN
            or f is None
            or f.start_date is None
            or not 80 <= (f.end_date - f.start_date).days <= 100
        ):
            continue
        for s, e, v in dps_raw_by_filing.get(f.filing_id, []):
            if (
                s is None
                or e != f.end_date
                or v != f.value
                or (f.start_date - s).days < 60
                or not 150 <= (e - s).days <= 380
            ):
                continue
            if v <= 0:
                continue
            # the year-to-date did not grow over the quarter: a filed prior
            # year-to-date (same start, ending the day before the quarter)
            # equals it, so the quarter must be zero ...
            prior = [
                (ps, pe, {v_ for _f, v_ in copies})
                for (ps, pe), copies in span_copies.items()
                if ps is not None
                and abs((ps - s).days) <= 7
                and abs((f.start_date - pe).days) <= 7
                and (pe - ps).days
                >= 150  # a real multi-quarter YTD, never Q1 alone (Visa Q2)
            ]
            # LOGI's prior YTD carries two values (0.87 and 0.95): any copy equal
            prior = [x for x in prior if c.value in x[2]]
            if not prior:
                continue
            # ... unless that prior year-to-date is itself contradicted by its
            # own filed quarters (V FY2022: every YTD context carries the
            # quarterly rate 0.375, below its own quarters 0.375 + 0.375)
            ps, pe, _pv = prior[0]
            inside = [
                min(v_ for _f, v_ in copies)
                for (qs, qe), copies in span_copies.items()
                if qs is not None
                and qs >= ps - timedelta(days=7)
                and qe <= pe + timedelta(days=7)
                and 80 <= (qe - qs).days <= 100
                and copies
            ]
            assert c.value is not None
            if sum(inside, Decimal(0)) > c.value + YEAR_SOLVE_TOL:
                continue
            bad.add(c.period_id)
            break
    if not bad:
        return cells
    return [
        CellResult(
            c.concept,
            c.period_id,
            HIDE_QTR_YTD,
            None,
            (),
            c.chosen,
            c.factor,
            c.candidates,
            "quarter carries the filing's year-to-date value",
        )
        if c.concept == concept and c.period_id in bad
        else c
        for c in cells
    ]


def _basis_quarter_sum(
    span: tuple,
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
    basis_tag: str,
) -> Decimal | None:
    chain = _basis_quarter_chain(span, span_copies, basis_tag)
    return None if chain is None else sum((v for _s, _e, v in chain), Decimal(0))


def _basis_quarter_chain(
    span: tuple,
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
    basis_tag: str,
) -> list[tuple[date, date, Decimal]] | None:
    """Sum of the basis tag's filed 3-month quarters chaining over the span
    (one agreed value per quarter), or None when they do not cover it."""
    start, end = span
    by_end: dict[date, tuple[date, Decimal]] = {}
    for (qs, qe), copies in span_copies.items():
        if qs is None or qs < start - timedelta(days=7) or qe > end + timedelta(days=7):
            continue
        if not 80 <= (qe - qs).days <= 120:
            continue
        vals = {v for f, v in copies if f.tag == basis_tag}
        if len(vals) != 1:
            continue
        if qe not in by_end or qs < by_end[qe][0]:
            by_end[qe] = (qs, next(iter(vals)))
    chain = sorted((qs, qe, v) for qe, (qs, v) in by_end.items())
    if (
        not chain
        or abs((chain[0][0] - start).days) > 7
        or abs((chain[-1][1] - end).days) > 7
        or any(abs((b[0] - a[1]).days) > 7 for a, b in itertools.pairwise(chain))
    ):
        return None
    return chain


def _basis_dated_sum(
    span: tuple,
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
    basis_tag: str,
) -> Decimal | None:
    """Sum of the basis tag's DATED facts (one-day contexts: declaration or
    payment dates) inside the span, when every quarter of the span holds at
    least one and each date has one value; else None. AMT 2022: declarations
    03-10 1.40, 05-18 1.43, 09-21 1.47, 12-07 1.56 = 5.86."""
    start, end = span
    by_day: dict[date, set[Decimal]] = defaultdict(set)
    for (s, e), copies in span_copies.items():
        if s is None or s != e or not start <= e <= end:
            continue
        for f, v in copies:
            if f.tag == basis_tag:
                by_day[e].add(v)
    if not by_day or any(len(v) != 1 for v in by_day.values()):
        return None
    n_q = max(1, round(((end - start).days + 1) / 91.3))
    width = ((end - start).days + 1) / n_q
    covered = [min(n_q - 1, int((d - start).days // width)) for d in by_day]
    # exactly one dated fact per quarter (BAC 2016 tags five declaration and
    # announcement dates; two in Q2 make the sum overshoot)
    if sorted(covered) != list(range(n_q)):
        return None
    return sum((next(iter(v)) for v in by_day.values()), Decimal(0))


def _dps_span_agrees_with_parts(
    cells: list[CellResult],
    basis_tag: str | None,
    span_copies: Mapping[tuple, list[tuple[SourceFact, Decimal]]],
) -> list[CellResult]:
    """Verifier run 6 (AMT FY2022 4.30 vs 5.86, FY2023 6.31 vs 6.45): a shown
    6M, 9M or full-year dividend must equal its parts on the company's basis:
    the basis tag's filed quarters, else its dated declaration (or payment)
    facts. On a mismatch the cell takes a FILED copy of the same span that
    equals the parts (AMT's 10-K tags the declared totals as CashPaid), and is
    hidden when no filed copy does. No value is derived."""
    concept = "dividends_per_share_resolved"
    if basis_tag is None:
        return cells
    out = []
    weak_spans: set[tuple] = set()
    for c in cells:
        f = c.chosen
        if (
            c.concept != concept
            or c.status != SHOWN
            or f is None
            or f.start_date is None
            or c.value is None
            or (f.end_date - f.start_date).days < 150
        ):
            out.append(c)
            continue
        span = (f.start_date, f.end_date)
        parts, kind = _basis_quarter_sum(span, span_copies, basis_tag), "quarters"
        if parts is None:
            parts, kind = _basis_dated_sum(span, span_copies, basis_tag), "dated facts"
        if parts is None or abs(c.value - parts) <= YEAR_SOLVE_TOL:
            out.append(c)
            continue
        below = c.value < parts
        match = next(
            (
                (f_, v_)
                for f_, v_ in sorted(
                    span_copies.get(span, []),
                    key=lambda x: (
                        x[0].tag != basis_tag,
                        x[0].filing_date,
                        x[0].fact_id,
                    ),
                )
                if abs(v_ - parts) <= YEAR_SOLVE_TOL
            ),
            None,
        )
        if match is None:
            # Weigh the evidence (LFUS FY2023 2.5 in three agreeing 10-K copies
            # vs a one-copy Q4 0.6): when the span has >= 2 agreeing filings and
            # some chain quarters only one, the one-copy quarters are the
            # suspects and the span stays; otherwise the span is hidden.
            if kind != "quarters":
                # dated facts only CHOOSE between filed copies (AMT): their
                # dates can be announcements that shift a dividend between
                # quarters (JPM 6M 2018), so they never hide a cell
                out.append(c)
                continue
            # direction decides which side is wrong: a span BELOW its quarters
            # carries a quarterly rate (Visa FY 0.375 in three 10-Ks against
            # quarters of 0.375 each); a span ABOVE them has an understated
            # quarter (LFUS one-copy Q4 0.6 against FY 2.5 in three 10-Ks)
            span_filings = {
                f_.filing_id for f_, v_ in span_copies.get(span, []) if v_ == c.value
            }
            weak = []
            if not below and len(span_filings) >= 2:
                for qs, qe, _v in (
                    _basis_quarter_chain(span, span_copies, basis_tag) or []
                ):
                    fids = {
                        f_.filing_id
                        for f_, _ in span_copies.get((qs, qe), [])
                        if f_.tag == basis_tag
                    }
                    if len(fids) == 1:
                        weak.append((qs, qe))
            if weak:
                weak_spans.update(weak)
                out.append(c)
                continue
            out.append(
                CellResult(
                    c.concept,
                    c.period_id,
                    HIDE_DPS_INVALID,
                    None,
                    (),
                    c.chosen,
                    c.factor,
                    c.candidates,
                    f"does not equal its {basis_tag} {kind} ({parts})",
                )
            )
            continue
        f0, v0 = match
        out.append(
            CellResult(
                c.concept,
                c.period_id,
                SHOWN,
                v0,
                (f0.fact_id,),
                f0,
                c.factor,
                c.candidates,
                f"equals its {basis_tag} {kind} (filed copy on {f0.tag})",
            )
        )
    if not weak_spans:
        return out
    return [
        CellResult(
            c.concept,
            c.period_id,
            HIDE_DPS_INVALID,
            None,
            (),
            c.chosen,
            c.factor,
            c.candidates,
            "one-copy quarter disagrees with its year's agreeing filed totals",
        )
        if c.concept == concept
        and c.status == SHOWN
        and c.chosen is not None
        and (c.chosen.start_date, c.chosen.end_date) in weak_spans
        else c
        for c in out
    ]


def _agree_tol(
    a: SourceFact, fa: Fraction, b: SourceFact, fb: Fraction, kind: str
) -> Decimal:
    tol = _tol(a, fa, kind) + _tol(b, fb, kind)
    # The slack is for a re-presented YTD or annual total summed from rounded
    # quarters (AAPL FY2013 DPS 1.64); never for a quarter or an instant,
    # where it let TSCO's next-year rate 0.22 "agree" with 1.03 / 5 = 0.206.
    longer = a.start_date is not None and (a.end_date - a.start_date).days > 100
    if kind == PER_SHARE and fa != fb and longer:
        unit_half = Decimal(1).scaleb(-PER_SHARE_MIN_DECIMALS) / 2
        tol += REPRESENTATION_SLACK_HALF_UNITS * unit_half
    return tol


def _tol(f: SourceFact, factor: Fraction, kind: str) -> Decimal:
    t = half_unit(f.value, kind)
    num, den = Decimal(factor.numerator), Decimal(factor.denominator)
    return t * den / num if kind == PER_SHARE else t * num / den


# --------------------------------------------------------------------------
# Company pass
# --------------------------------------------------------------------------
@dataclass
class CompanyResult:
    company_id: int
    events: list[Event]
    basis: dict[int, FilingBasis]
    violations: list[tuple[FiledPair, Fraction]]
    cells: list[CellResult]
    event_hash: str


def compute_company(
    company_id: int, facts: list[SourceFact], mapped_tags: Mapping[str, list[str]]
) -> CompanyResult:
    filings_by_id: dict[int, Filing] = {}
    for f in facts:
        if f.usable_source:
            filings_by_id.setdefault(
                f.filing_id, Filing(f.filing_id, f.filing_date, f.form, f.accession)
            )
    filings = sorted(filings_by_id.values(), key=lambda x: (x.filing_date, x.filing_id))
    extra = {
        t
        for base in (b for _, b in TARGETS.values())
        for t in mapped_tags.get(base, [])
    }
    extra -= {"EntityCommonStockSharesOutstanding"}  # cover dates differ per filing
    pairs = build_filed_pairs(facts, extra)
    series = build_share_series(facts)
    steps = build_share_steps(series)
    disclosures = build_disclosures(facts)
    # A stock-dividend value tag alone is not split evidence: REIT special
    # distributions paid partly in stock (EQIX 2015, IRM 2014) re-present no
    # per-share history (Verifier run 3). Recurring stock dividends are held
    # from the yearly repetition of their re-presentation (CBSH, VLY).
    events = detect_events(pairs, steps, disclosures, filings)
    basis = compute_filing_basis(filings, events, series, steps)
    violations = invariant_violations(pairs, basis, events)
    cells = resolve_cells(
        facts,
        mapped_tags,
        basis,
        events,
        company_hidden=max(p.hi for p, _ in violations) if violations else False,
    )
    return CompanyResult(
        company_id, events, basis, violations, cells, event_set_hash(events)
    )


# --------------------------------------------------------------------------
# Database (read in every mode but off; write only in mode on)
# --------------------------------------------------------------------------
def load_mapped_tags(conn) -> dict[str, list[str]]:
    rows = conn.execute(
        """
        select cc.name, c.tag
        from analytics.concept_mapping m
        join analytics.canonical_concept cc on cc.id = m.canonical_concept_id
        join core.concept c on c.id = m.concept_id
        where cc.name = any(%s) and m.confidence != 'rejected'
        order by cc.name, m.priority, m.concept_id
        """,
        ([base for _, base in TARGETS.values()],),
    ).fetchall()
    out: dict[str, list[str]] = defaultdict(list)
    for name, tag in rows:
        out[name].append(tag)
    return dict(out)


def load_concept_ids(conn, tags: Iterable[str]) -> list[int]:
    return [
        r[0]
        for r in conn.execute(
            "select id from core.concept where tag = any(%s)", (sorted(set(tags)),)
        ).fetchall()
    ]


def load_company_facts(
    conn, company_id: int, concept_ids: list[int]
) -> list[SourceFact]:
    rows = conn.execute(
        """
        select f.id, c.tag, u.unit_name, f.period_id, p.start_date, p.end_date,
               p.period_type, f.value, f.filing_id, fl.filing_date, fl.form,
               fl.accession_number, f.is_derived, f.is_authoritative
        from core.fact f
        join core.concept c on c.id = f.concept_id
        join core.unit u on u.id = f.unit_id
        join core.period p on p.id = f.period_id
        join core.filing fl on fl.id = f.filing_id
        where f.company_id = %s and f.concept_id = any(%s)
        """,
        (company_id, concept_ids),
    ).fetchall()
    return [SourceFact(*r) for r in rows]


def load_current_cells(
    conn, company_id: int
) -> dict[tuple[str, int], tuple[int, Decimal, tuple[int, ...]]]:
    rows = conn.execute(
        """
        select cc.name, cf.period_id, cf.id, cf.value, cf.source_fact_ids
        from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        where cf.company_id = %s and cc.name = any(%s)
        """,
        (company_id, list(TARGETS)),
    ).fetchall()
    return {(n, pid): (cid, v, tuple(s or ())) for n, pid, cid, v, s in rows}


def all_input_tags(mapped_tags: Mapping[str, list[str]]) -> set[str]:
    tags = set(EVIDENCE_PER_SHARE_TAGS) | set(EVIDENCE_SHARE_TAGS) | set(SERIES_TAGS)
    tags |= (
        set(SPLIT_RATIO_TAGS) | set(DIVIDENDS_PAID_TAGS) | {STOCK_DIVIDEND_VALUE_TAG}
    )
    for base_tags in mapped_tags.values():
        tags |= set(base_tags)
    return tags


@dataclass(frozen=True)
class PackageCell:
    """One cell of a release package: what production held and what the
    pass showed at packaging time."""

    concept: str
    period_id: int
    old_value: Decimal | None
    new_value: Decimal | None
    status: str


def package_mismatches(
    res: CompanyResult,
    current: Mapping,
    pkg: Mapping[tuple[str, int], PackageCell],
    *,
    remove_derived_only: bool,
) -> list[str]:
    """Why this company's write no longer matches its release package (empty
    = it matches). Production can rewrite cells after the dry run, and the
    filings can change the computation, so a release write refuses the
    company unless (a) every packaged cell still holds the value production
    held at packaging, (b) the pass recomputes the packaged value and status,
    and (c) every other cell the write touches is a no-op."""
    out: list[str] = []
    by_key = {(c.concept, c.period_id): c for c in res.cells}
    for key, p in pkg.items():
        hit = current.get(key)
        live = hit[1] if hit else None
        if live != p.old_value:
            out.append(f"{key}: production now {live}, packaged {p.old_value}")
        c = by_key.get(key)
        if c is None or c.status != p.status or c.value != p.new_value:
            got = None if c is None else (c.status, c.value)
            out.append(f"{key}: recomputed {got}, packaged {(p.status, p.new_value)}")
    for c in cells_to_write(res, current):
        key = (c.concept, c.period_id)
        hit = current.get(key)
        if key not in pkg and (hit is None or hit[1] != c.value):
            out.append(f"{key}: would write {c.value} outside the package")
    for c in res.cells:
        key = (c.concept, c.period_id)
        if c.status == SHOWN or key in pkg or key not in current:
            continue
        if c.status == HIDE_NO_FILED_SOURCE and not remove_derived_only:
            continue
        out.append(f"{key}: would remove a cell outside the package")
    return out


def run_split_rebase(
    conn,
    company_ids: list[int],
    *,
    environ: Mapping[str, str] | None = None,
    run_id: str | None = None,
    package: Mapping[int, Mapping[tuple[str, int], PackageCell]] | None = None,
) -> dict:
    """Entry point. off: no query, legacy writers stay in charge. dry_run:
    read-only compute, returns results. on: compute and write in one
    transaction per company (needs migrations 0098 and 0099 applied). With a
    release `package`, a company is written only when it still matches its
    packaged cells (package_mismatches); the others are refused, not forced."""
    mode = rule_flags.rule_mode(RULE_ID, environ)
    if mode == rule_flags.OFF:
        return {"mode": mode, "companies": 0}
    ru1_on = rule_flags.rule_enabled(RU1_RULE_ID, environ)
    if mode == rule_flags.ON:
        if run_id is None:
            raise ValueError("mode on needs a run_id for rollback")
        rule_flags.per_share_pair_enabled(environ)  # raises unless RU-1 is on too
    if not company_ids:
        raise ValueError("split re-base needs an explicit company list (cohort scope)")
    mapped = load_mapped_tags(conn)
    concept_ids = load_concept_ids(conn, all_input_tags(mapped))
    results = []
    refused: dict[int, list[str]] = {}
    for cid in company_ids:
        facts = load_company_facts(conn, cid, concept_ids)
        res = compute_company(cid, facts, mapped)
        current = load_current_cells(conn, cid)
        results.append((res, current))
        if mode == rule_flags.ON:
            assert run_id is not None
            if package is not None:
                why = (
                    package_mismatches(
                        res, current, package[cid], remove_derived_only=ru1_on
                    )
                    if cid in package
                    else ["company is not in the release package"]
                )
                if why:
                    refused[cid] = why[:10]
                    continue
            write_company(conn, res, current, run_id=run_id, remove_derived_only=ru1_on)
    return {
        "mode": mode,
        "companies": len(results),
        "results": results,
        "ru1_on": ru1_on,
        "refused": refused,
    }


# Phase switch (Dhairya decision 2026-10-24, Verifier 1000): phase 1 writes
# every class except `other_changed` (a filed copy replacing a different
# stored value: 13 of 14 sampled were wrong), whose stored value is kept
# untouched; phase 2 writes it too once the Verifier's recheck passes.
WRITE_PHASE = 1


def cells_to_write(
    res: CompanyResult, current: Mapping, *, phase: int = WRITE_PHASE
) -> list[CellResult]:
    out = []
    for c in res.cells:
        if c.status != SHOWN or c.value is None:
            continue
        hit = current.get((c.concept, c.period_id))
        if phase < 2 and classify_change(hit[1] if hit else None, c) == OTHER_CHANGED:
            continue
        out.append(c)
    return out


def cells_to_remove(
    res: CompanyResult, current: Mapping, *, remove_derived_only: bool
) -> list[int]:
    """canonical_fact ids this pass hides. A current cell the pass never
    evaluated (no mapped fact at all) is not ours and stays."""
    out = []
    for c in res.cells:
        if c.status == SHOWN:
            continue
        if c.status == HIDE_NO_FILED_SOURCE and not remove_derived_only:
            continue
        hit = current.get((c.concept, c.period_id))
        if hit is not None:
            out.append(hit[0])
    return out


def write_company(
    conn,
    res: CompanyResult,
    current: Mapping,
    *,
    run_id: str,
    remove_derived_only: bool,
) -> dict:
    """Archive-then-replace in ONE transaction for one company: split_event
    and filing_share_basis rebuilt, every shown cell written, every current
    cell this pass no longer shows archived and removed."""
    from scrooner_pipeline.mapper import canonical_archive as ca

    concept_ids = dict(
        conn.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            (list(TARGETS),),
        ).fetchall()
    )
    with conn.transaction():
        cur = conn.cursor()
        cur.execute(
            "delete from analytics.filing_share_basis where company_id = %s",
            (res.company_id,),
        )
        cur.execute(
            "delete from analytics.split_event where company_id = %s", (res.company_id,)
        )
        db_ids: dict[int, int] = {}
        for e in res.events:
            if e.status not in ("confirmed", "review"):
                continue
            cur.execute(
                """
                insert into analytics.split_event
                    (company_id, ratio, basis_date, evidence, evidence_kinds, status, detector_version)
                values (%s, %s, %s, %s, %s, %s, %s) returning id
                """,
                (
                    res.company_id,
                    ratio_to_decimal(e.ratio),
                    e.basis_date,
                    json.dumps(e.evidence_json()),
                    e.kinds,
                    e.status,
                    DETECTOR_VERSION,
                ),
            )
            row = cur.fetchone()
            assert row is not None
            db_ids[e.local_id] = row[0]
        cur.executemany(
            """
            insert into analytics.filing_share_basis
                (company_id, filing_id, filing_date, factor_to_current, event_ids,
                 observed_factor, status, basis_version)
            values (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    res.company_id,
                    b.filing_id,
                    b.filing_date,
                    ratio_to_decimal(b.factor),
                    [db_ids[i] for i in b.event_ids if i in db_ids],
                    ratio_to_decimal(b.observed_factor) if b.observed_factor else None,
                    b.status,
                    BASIS_VERSION,
                )
                for b in res.basis.values()
            ],
        )
        shown = cells_to_write(res, current)
        rows = [
            ca.CanonicalRow(
                res.company_id,
                concept_ids[c.concept],
                c.period_id,
                c.value,
                c.source_fact_ids,
            )
            for c in shown
            if c.value is not None
        ]
        stats = ca.replace_rows(
            cur,
            rows,
            reason_code=REASON_CODE,
            run_id=run_id,
            basis_version=BASIS_VERSION,
        )
        gone = cells_to_remove(res, current, remove_derived_only=remove_derived_only)
        stats["removed"] = ca.archive_and_remove(
            cur,
            gone,
            reason_code=REASON_CODE,
            run_id=run_id,
            basis_version=BASIS_VERSION,
        )
    return stats


# --------------------------------------------------------------------------
# Dry-run classification (old cell vs proposed cell)
# --------------------------------------------------------------------------
UNCHANGED = "unchanged"
ROUNDING_ONLY = "rounding_only"
WAS_UNADJUSTED = "was_unadjusted"
WAS_DOUBLE_DIVIDED = "was_double_divided"
SHARE_COUNT_REBASED = "share_count_rebased"
OTHER_CHANGED = "other_changed"
NEW_VALUE = "new_value"
NOW_HIDDEN = "now_hidden_with_reason"
STILL_BLANK = "still_blank_with_reason"
KEPT_DERIVED_ONLY = "kept_derived_only_ru1_scope"

_PRODUCTS = sorted(
    {a * b for a in CLEAN_RATIOS for b in CLEAN_RATIOS if a >= b} | set(CLEAN_RATIOS)
)


def classify_change(
    old: Decimal | None, cell: CellResult, *, ru1_on: bool = False
) -> str:
    kind = TARGETS[cell.concept][0]
    new = cell.value
    if cell.status == HIDE_NO_FILED_SOURCE and not ru1_on:
        return KEPT_DERIVED_ONLY if old is not None else STILL_BLANK
    if cell.status != SHOWN:
        return NOW_HIDDEN if old is not None else STILL_BLANK
    assert new is not None
    if old is None:
        return NEW_VALUE
    if old == new:
        return UNCHANGED
    if abs(old - new) <= half_unit(new, kind) + half_unit(old, kind):
        return ROUNDING_ONLY
    if kind == SHARES:
        return SHARE_COUNT_REBASED
    if old == 0 or new == 0:
        return OTHER_CHANGED
    r = old / new
    best = min(
        _PRODUCTS,
        key=lambda k: (
            abs(r - Decimal(k.numerator) / Decimal(k.denominator))
            / (Decimal(k.numerator) / Decimal(k.denominator))
        ),
    )
    kd = Decimal(best.numerator) / Decimal(best.denominator)
    if abs(r - kd) <= Decimal("0.02") * kd or pair_fits(old, new, best, PER_SHARE):
        return WAS_UNADJUSTED if kd > 1 else WAS_DOUBLE_DIVIDED
    for k in _PRODUCTS:  # rounding of a re-presented copy (NVDA 1.74 vs 0.17)
        kd = Decimal(k.numerator) / Decimal(k.denominator)
        if abs(old - new * kd) <= half_unit(old, PER_SHARE) + kd * Decimal("0.005"):
            return WAS_UNADJUSTED if kd > 1 else WAS_DOUBLE_DIVIDED
    return OTHER_CHANGED


# --------------------------------------------------------------------------
# SB-6 writer registry: who writes each owned resolved concept in a mode.
# --------------------------------------------------------------------------
def registered_writers(
    concept: str, environ: Mapping[str, str] | None = None
) -> list[str]:
    from scrooner_pipeline.corporate_actions.stock_splits import (
        RETROACTIVE_ADJUSTMENT_CONCEPTS,
        retroactive_adjustment_active,
    )
    from scrooner_pipeline.mapper.conflict_resolution import (
        SPLIT_LIKE_CONCEPTS,
        active_conflict_fill_targets,
    )
    from scrooner_pipeline.mapper.dedup_majority_resolver import active_safe_concepts

    out = []
    for primary, resolved in active_conflict_fill_targets(environ):
        if resolved == concept:
            out += ["conflict_resolution.baseline", "conflict_resolution.conflict_fill"]
            if primary in SPLIT_LIKE_CONCEPTS:
                out.append("conflict_resolution.split_like")
    if any(r == concept for _, r in active_safe_concepts(environ)):
        out.append("dedup_majority_resolver")
    if (
        retroactive_adjustment_active(environ)
        and concept in RETROACTIVE_ADJUSTMENT_CONCEPTS.values()
    ):
        out.append("stock_splits.retroactive")
    if concept in TARGETS and rule_flags.per_share_pair_enabled(environ):
        out.append("share_basis")
    return out
