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
from collections import defaultdict
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
SERIES_TAGS = ("EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding")

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
SHARE_STEP_REL_TOL = Decimal("0.04")
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

# Restatement policy for a period whose copies disagree on the SAME basis
# (no split between them): "hide" is design 2.8 (accepted in doc 49). The
# restatement display basis itself is open (doc 49 item 12); "leave" would
# keep today's cell untouched. Changing this is a Standardization Lead call.
RESTATEMENT_POLICY = "hide"

# One DPS basis per series while AC-24 (declared vs paid) is open:
# "hide_off_basis" (default) shows a mixed series on the mapping's
# priority-1 tag (CommonStockDividendsPerShareDeclared) and hides only the
# cells that exist solely on another tag; "hide_series" hides the whole
# mixed series. Cohort-1000 counts for both are in
# data-team/strategy/team/SPLIT-REBASE-COHORT-DRYRUN-2026-10-24.md.
DPS_MIXED_POLICY = "hide_off_basis"

HIDDEN_REASON_TEXT = {
    HIDE_BASIS_REVIEW: "share basis under review (a possible split is not confirmed by two kinds of filing evidence)",
    HIDE_BASIS_CONFLICT: "filed copies disagree after converting each to the current share basis",
    HIDE_RESTATED: "filed copies of this period disagree (restated between filings)",
    HIDE_COMPANY_INVARIANT: "share basis under review (filed comparatives contradict the split history)",
    HIDE_NO_FILED_SOURCE: "not filed separately in a 10-K or 10-Q (per-share values are not derived)",
    HIDE_LABEL_ERROR: "the filed quarter equals the full-year value of the same filing (label error)",
    HIDE_DPS_BASIS: "dividend basis pending (declared vs paid, AC-24): this series mixes both",
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
        return not self.is_derived and is_periodic_form(self.form)


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


def ratio_candidates(kind: str) -> tuple[Fraction, ...]:
    if kind == SHARES:
        return tuple(k for k in CLEAN_RATIOS if k not in SHARE_SCALE_RATIOS)
    return CLEAN_RATIOS


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


def build_share_series(facts: Iterable[SourceFact]) -> list[SourceFact]:
    """One share count per periodic filing: the latest-instant cover count,
    else the latest-instant balance-sheet count; median of ties."""
    by_filing: dict[int, dict[str, list[SourceFact]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for f in facts:
        if (
            f.tag in SERIES_TAGS
            and f.unit == "shares"
            and f.usable_source
            and f.value > 0
        ):
            by_filing[f.filing_id][f.tag].append(f)
    series: list[SourceFact] = []
    for tags in by_filing.values():
        for tag in SERIES_TAGS:
            cands = tags.get(tag)
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
        if len(ev.kinds) >= 2:
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
        keep, drop = (a_ev, b_ev) if _support(a_ev) >= _support(b_ev) else (b_ev, a_ev)
        drop.status = "rejected"
        drop.note = f"same ratio as the better-supported event at {keep.basis_date}"
        lo = min(x for x in (a_ev.lo, b_ev.lo) if x is not None)
        hi = max(x for x in (a_ev.hi, b_ev.hi) if x is not None)
        keep.doubt = (lo, hi)

    # A single-kind candidate whose every observation spans >= 2 confirmed
    # events with this product is those events seen across both (TSLA 5x3).
    confirmed = [e for e in events if e.status == "confirmed"]
    for ev in events:
        if ev.status != "review" or ev.hi is None:
            continue
        obs = [(p.lo, p.hi) for p in ev.pairs] + [(st.lo, st.hi) for st in ev.steps]
        if obs and all(
            _spanned_product(confirmed, lo, hi) == ev.ratio for lo, hi in obs
        ):
            ev.status, ev.note = "rejected", "product of confirmed events"
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
    company_hidden: bool,
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

    out: list[CellResult] = []
    for concept, (kind, base) in TARGETS.items():
        tags = mapped_tags.get(base, [])
        unit = UNIT_BY_KIND[kind]
        latest = _latest_converted(facts, tags, basis) if kind == PER_SHARE else {}
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
            if company_hidden:
                out.append(
                    CellResult(
                        concept, pid, HIDE_COMPANY_INVARIANT, None, (), None, None, ()
                    )
                )
                continue
            usable = [
                f for f in cands if f.filing_id in basis and basis[f.filing_id].usable
            ]
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
                fac = basis[f.filing_id].factor
                conv.append((f, fac, convert(f.value, fac, kind)))
            conv.sort(key=lambda x: (x[0].filing_date, x[0].fact_id))
            note = ""
            if kind == SHARES and len(conv) > 2:
                kept = [
                    x
                    for x in conv
                    if not any(
                        is_share_scale_artifact(y[2], x[2], kind) and y[2] > x[2]
                        for y in conv
                    )
                ]
                if len(kept) != len(conv):
                    note = f"dropped {len(conv) - len(kept)} copy(ies) off by a units scale"
                    conv = kept
            agree = _all_agree(conv, kind)
            if not agree and len(conv) > 1:
                # Label shift (Verifier 2026-10-24): a disagreeing copy that
                # equals the same tag's value for ANOTHER period in its own
                # filing is a context error, not a restatement (AMZN FY2012
                # 10-K 0001193125-13-028520 puts 2012 quarters on 2011
                # contexts; NVDA FY2018 10-K puts Q2 0.98 on the 6M context).
                shifted = [
                    x
                    for x in conv
                    if any(
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
                        f"dropped {len(shifted)} label-shifted copy(ies): "
                        + ",".join(x[0].accession for x in shifted)
                    )
                    conv, agree = rest, True
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
            f, fac, value = conv[-1]
            if kind == PER_SHARE and _quarter_is_year_label_error(
                f, value, tags, latest, fac
            ):
                out.append(
                    CellResult(
                        concept, pid, HIDE_LABEL_ERROR, None, (), None, None, cand_view
                    )
                )
                continue
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
    return _one_dividend_basis(out, mapped_tags.get("dividends_per_share", []))


LABEL_ERROR_TOL = Decimal("0.015")  # as-filed cents (ASSUMED), scaled by the factor


def _latest_converted(
    facts: list[SourceFact], tags: list[str], basis: Mapping[int, FilingBasis]
) -> dict[tuple[str, date | None, date], Decimal]:
    """(tag, start, end) -> current-basis value of the latest usable copy."""
    best: dict[tuple[str, date | None, date], tuple[date, int, Decimal]] = {}
    tagset = set(tags)
    for f in facts:
        b = basis.get(f.filing_id)
        if f.tag not in tagset or not f.usable_source or b is None or not b.usable:
            continue
        key = (f.tag, f.start_date, f.end_date)
        cur = best.get(key)
        if cur is None or (f.filing_date, f.fact_id) > cur[:2]:
            best[key] = (
                f.filing_date,
                f.fact_id,
                convert(f.value, b.factor, PER_SHARE),
            )
    return {k: v[2] for k, v in best.items()}


def _quarter_is_year_label_error(
    chosen: SourceFact,
    value: Decimal,
    tags: list[str],
    latest: Mapping,
    factor: Fraction,
) -> bool:
    """A 3-month per-share value that equals the fiscal year's value while
    the 9-month YTD before it is positive cannot be the quarter (ledger row
    30; NVDA FY2015 10-K 0001045810-15-000036 tags the annual 0.34 cash
    dividend on the Q4 context while Q1-Q3 declared 0.085 each). A quarter
    holding the year's only dividend passes (NVDA Q4 FY2013: paid 0.075, 9M
    paid 0; AAPL Q4 FY2012: 2.65, 9M declared 0 as re-presented). Same tag
    first, then the concept's other tags, for both the year and the YTD."""
    if chosen.start_date is None or (chosen.end_date - chosen.start_date).days > 100:
        return False
    tol = LABEL_ERROR_TOL * Decimal(factor.denominator) / Decimal(factor.numerator)
    order = [chosen.tag] + [t for t in tags if t != chosen.tag]

    def pick(pred) -> Decimal | None:
        for t in order:
            hits = sorted(
                (k for k in latest if k[0] == t and k[1] is not None and pred(k)),
                key=lambda k: (k[1], k[2]),
            )
            if hits:
                return latest[hits[0]]
        return None

    year = pick(lambda k: k[2] == chosen.end_date and (k[2] - k[1]).days >= 350)
    if year is None or abs(value - year) > tol:
        return False
    ytd_start = chosen.end_date - timedelta(days=371)
    ytd = pick(
        lambda k: (
            ytd_start <= k[1] < chosen.start_date
            and abs((chosen.start_date - k[2]).days) <= 7
            and (k[2] - k[1]).days >= 250
        )
    )
    return ytd is not None and ytd > tol and abs(value + ytd - year) > tol


def _all_agree(conv: list[tuple[SourceFact, Fraction, Decimal]], kind: str) -> bool:
    return all(
        abs(ca - cb) <= _agree_tol(a, fa, b, fb, kind)
        for i, (a, fa, ca) in enumerate(conv)
        for (b, fb, cb) in conv[i + 1 :]
    )


def _one_dividend_basis(
    cells: list[CellResult], dps_tags: list[str] | None = None
) -> list[CellResult]:
    """One DPS basis per series (Verifier 2026-10-24, LLY: Q3 2018/2019 would
    show CashPaid 0.5625/0.645 next to Declared quarters). AC-24 (declared
    vs paid) is open, so a quarterly or an annual DPS series whose shown
    cells come from more than one tag is hidden with a reason; a series on
    one tag is shown on that tag's basis."""

    def series(c: CellResult) -> str:
        assert c.chosen is not None
        start = c.chosen.start_date
        days = (c.chosen.end_date - start).days if start else 0
        return "annual" if days >= 350 else "interim"

    tags_by_series: dict[str, set[str]] = defaultdict(set)
    for c in cells:
        if (
            c.concept == "dividends_per_share_resolved"
            and c.status == SHOWN
            and c.chosen
        ):
            tags_by_series[series(c)].add(c.chosen.tag)
    mixed = {k for k, v in tags_by_series.items() if len(v) > 1}
    if not mixed:
        return cells
    order = list(dps_tags or [])
    basis_tag = {
        k: next((t for t in order if t in tags_by_series[k]), min(tags_by_series[k]))
        for k in mixed
    }
    out = []
    for c in cells:
        if (
            c.concept == "dividends_per_share_resolved"
            and c.status == SHOWN
            and c.chosen
            and series(c) in mixed
            and (
                DPS_MIXED_POLICY == "hide_series"
                or c.chosen.tag != basis_tag[series(c)]
            )
        ):
            c = CellResult(
                c.concept, c.period_id, HIDE_DPS_BASIS, None, (), c.chosen, c.factor,
                c.candidates, f"series uses {sorted(tags_by_series[series(c)])}",
            )  # fmt: skip
        out.append(c)
    return out


def _agree_tol(
    a: SourceFact, fa: Fraction, b: SourceFact, fb: Fraction, kind: str
) -> Decimal:
    tol = _tol(a, fa, kind) + _tol(b, fb, kind)
    if kind == PER_SHARE and fa != fb:
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
    events = detect_events(pairs, steps, disclosures, filings)
    basis = compute_filing_basis(filings, events, series, steps)
    violations = invariant_violations(pairs, basis, events)
    cells = resolve_cells(
        facts, mapped_tags, basis, events, company_hidden=bool(violations)
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
    tags |= set(SPLIT_RATIO_TAGS)
    for base_tags in mapped_tags.values():
        tags |= set(base_tags)
    return tags


def run_split_rebase(
    conn,
    company_ids: list[int],
    *,
    environ: Mapping[str, str] | None = None,
    run_id: str | None = None,
) -> dict:
    """Entry point. off: no query, legacy writers stay in charge. dry_run:
    read-only compute, returns results. on: compute and write in one
    transaction per company (needs migrations 0098 and 0099 applied)."""
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
    for cid in company_ids:
        facts = load_company_facts(conn, cid, concept_ids)
        res = compute_company(cid, facts, mapped)
        current = load_current_cells(conn, cid)
        results.append((res, current))
        if mode == rule_flags.ON:
            assert run_id is not None
            write_company(conn, res, current, run_id=run_id, remove_derived_only=ru1_on)
    return {
        "mode": mode,
        "companies": len(results),
        "results": results,
        "ru1_on": ru1_on,
    }


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
        shown = [c for c in res.cells if c.status == SHOWN]
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
