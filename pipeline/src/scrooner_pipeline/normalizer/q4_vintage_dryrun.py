"""Q4 derivation DRY RUN with same-vintage pairing (Period Engineer, 2026-10-18).

Nothing here writes to the database. It takes raw (non-derived) duration
facts for one (company, concept, unit, fiscal year), decides whether a
discrete Q4 can be derived as

    Q4 = FY - 9-month YTD          (formula q4_fy_minus_ytd9_v1)
    Q4 = FY - (Q1 + Q2 + Q3)       (formula q4_fy_minus_q1q2q3_v1)

and emits one candidate record per cell with the inputs, the Decimal
arithmetic, the vintage evidence and, when blocked, the reason.

Why this exists (doc/data-moat/learnings/2026-10-17-...q4-conflicts...):
normalizer/derived.py only sees is_authoritative facts, and most
q4_not_derived cells have no authoritative copy on the FY or 9M side
because filings disagree (restatements, sign flips, rounding). Promoting
the latest-filed value on each side independently (conflict_latest_filed.py)
can pair a RESTATED full year with an ORIGINAL nine months, which yields a
third number that no filing ever reported. Here the two sides must come from
the same restatement vintage or the cell is blocked.

Categories (exactly one per cell):
  derivable_clean              one value per side (every copy identical),
                               an authoritative copy on each side
  derivable_same_vintage       derivable, but only after vintage reasoning
                               (rounding-only copies, or restated/as-filed
                               pairing with evidence)
  blocked_mixed_vintage_only   values exist but no evidenced same-vintage
                               pairing includes the latest FY value
  blocked_sign_conflict        two copies of one period differ only by sign
                               (quarantine, never pick one)
  blocked_no_ytd_source        no usable 9M YTD and no Q1-Q3 chain
  blocked_no_fy_fact           no usable full-year fact
  blocked_non_additive         concept is not on the additive allowlist, or
                               the facts are instants

Vintage rules for a (FY value cluster, YTD value cluster) pair. A cluster is
the set of copies of one period whose values agree within the caller's
tolerance. The first rule that holds wins:
  same_accession          a filing contains both values
  overlap_agreement       the two sides' filings both report some other
                          period of the same concept and every such pair
                          agrees within tolerance (disagreement vetoes)
  unrestated_single_value both sides have a single cluster, so no
                          restatement was observed on either side
  as_filed_original       both are the earliest cluster of their side and the
                          YTD was filed no later than the FY
  reconfirmed_after       one side is single-valued and was re-filed, with
                          the same value, on or after the first filing of
                          the other side's cluster
Anything else is mixed vintage. By default the chosen pair must include the
LATEST FY cluster (the value the resolver publishes); an as-filed-only
pairing is reported in `alternatives` and the cell stays blocked unless the
caller sets allow_non_latest_fy_vintage=True (a Verifier/accounting call).

Tolerance is a REQUIRED parameter (relative and absolute parts). No
precision is invented: core.fact stores no XBRL `decimals`, so the caller
states what rounding it is willing to treat as "the same number".

Weighted-average share counts and per-share/ratio concepts are not additive;
the caller passes the additive allowlist and everything else is
blocked_non_additive (their own methods live in derived.py).
"""

from collections import defaultdict
from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import psycopg
import structlog

logger = structlog.get_logger()

FORMULA_YTD9 = "q4_fy_minus_ytd9_v1"
FORMULA_CHAIN = "q4_fy_minus_q1q2q3_v1"
POLICY_VERSION = "q4_vintage_dryrun_v1"

# Same day-length bands as derived.py / conflict_latest_filed.py for FY.
FULL_YEAR_MIN_DAYS, FULL_YEAR_MAX_DAYS = 340, 380
# Remainder after the YTD end. derived.py uses 80-100; Costco's 16-week
# fiscal Q4 is 112 days, so the default upper bound is wider. Parameters.
DEFAULT_Q4_MIN_DAYS, DEFAULT_Q4_MAX_DAYS = 80, 120
# Spans of the YTD itself (Costco's 36 weeks = 252 days is below derived.py's 260).
YTD9_MIN_DAYS, YTD9_MAX_DAYS = 230, 300
CHAIN_QUARTER_MIN_DAYS, CHAIN_QUARTER_MAX_DAYS = 80, 125

CLEAN = "derivable_clean"
SAME_VINTAGE = "derivable_same_vintage"
BLOCKED_MIXED = "blocked_mixed_vintage_only"
BLOCKED_SIGN = "blocked_sign_conflict"
BLOCKED_NO_YTD = "blocked_no_ytd_source"
BLOCKED_NO_FY = "blocked_no_fy_fact"
BLOCKED_NON_ADDITIVE = "blocked_non_additive"
CATEGORIES = (
    CLEAN,
    SAME_VINTAGE,
    BLOCKED_MIXED,
    BLOCKED_SIGN,
    BLOCKED_NO_YTD,
    BLOCKED_NO_FY,
    BLOCKED_NON_ADDITIVE,
)


@dataclass(frozen=True)
class Tolerance:
    """Two values agree when |a-b| <= max(rel * max(|a|,|b|), abs_tol).
    Required by the caller; there is deliberately no default."""

    rel: Decimal
    abs_tol: Decimal

    def agree(self, a: Decimal, b: Decimal) -> bool:
        if a == b:
            return True
        return abs(a - b) <= max(self.rel * max(abs(a), abs(b)), self.abs_tol)


@dataclass(frozen=True)
class Fact:
    fact_id: int
    value: Decimal
    accession: str
    filing_date: date
    start_date: date | None  # None = instant
    end_date: date
    is_authoritative: bool
    fiscal_period: str | None  # FY / Q1 / Q2 / Q3 / Q4 / None (unlabeled YTD)
    unit: str = "USD"
    is_derived: bool = False


@dataclass
class Q4Candidate:
    company_id: int
    concept_id: int
    unit: str
    category: str
    block_reason: str | None
    policy_version: str = POLICY_VERSION
    formula_id: str | None = None
    fiscal_year_start: date | None = None
    fiscal_year_end: date | None = None
    q4_start: date | None = None
    q4_end: date | None = None
    fy_fact_ids: list[int] = field(default_factory=list)
    ytd_fact_ids: list[int] = field(default_factory=list)
    fy_accessions: list[str] = field(default_factory=list)
    ytd_accessions: list[str] = field(default_factory=list)
    fy_value: Decimal | None = None
    ytd_value: Decimal | None = None
    q4_value: Decimal | None = None
    arithmetic: str | None = None
    vintage_basis: str | None = None
    fy_is_latest_vintage: bool | None = None
    direct_q4_fact_ids: list[int] = field(default_factory=list)
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    tolerance: dict[str, str] | None = None

    def to_record(self) -> dict[str, Any]:
        """JSON-friendly dict (Decimals and dates as strings)."""

        def conv(v: Any) -> Any:
            if isinstance(v, Decimal | date):
                return str(v)
            if isinstance(v, list):
                return [conv(x) for x in v]
            if isinstance(v, dict):
                return {k: conv(x) for k, x in v.items()}
            return v

        return {k: conv(v) for k, v in self.__dict__.items()}


# --------------------------------------------------------------------------
# clustering
# --------------------------------------------------------------------------


@dataclass
class _Cluster:
    facts: list[Fact]  # ordered by (filing_date, fact_id)
    rep: Fact  # authoritative latest-filed copy, else latest-filed copy

    @property
    def value(self) -> Decimal:
        return self.rep.value

    @property
    def first_filed(self) -> date:
        return min(f.filing_date for f in self.facts)

    @property
    def last_filed(self) -> date:
        return max(f.filing_date for f in self.facts)

    @property
    def accessions(self) -> frozenset[str]:
        return frozenset(f.accession for f in self.facts)

    @property
    def exact(self) -> bool:
        return len({f.value for f in self.facts}) == 1

    @property
    def has_authoritative(self) -> bool:
        return any(f.is_authoritative for f in self.facts)


def _make_cluster(facts: list[Fact]) -> _Cluster:
    ordered = sorted(facts, key=lambda f: (f.filing_date, f.fact_id))
    auth = [f for f in ordered if f.is_authoritative]
    return _Cluster(ordered, (auth or ordered)[-1])


def _clusters(facts: Iterable[Fact], tol: Tolerance) -> list[_Cluster]:
    """Greedy grouping by agreement with each cluster's first copy; clusters
    are returned oldest first (by first filing). Tolerance is not transitive,
    so the greedy anchor is the earliest-filed copy of the cluster."""
    groups: list[list[Fact]] = []
    for f in sorted(facts, key=lambda f: (f.filing_date, f.fact_id)):
        for g in groups:
            if tol.agree(g[0].value, f.value):
                g.append(f)
                break
        else:
            groups.append([f])
    out = [_make_cluster(g) for g in groups]
    out.sort(key=lambda c: (c.first_filed, c.rep.fact_id))
    return out


def _has_sign_conflict(clusters: list[_Cluster], tol: Tolerance) -> bool:
    for i, a in enumerate(clusters):
        for b in clusters[i + 1 :]:
            if a.value != 0 and b.value != 0 and tol.agree(a.value, -b.value):
                return True
    return False


# --------------------------------------------------------------------------
# vintage pairing
# --------------------------------------------------------------------------


def _overlap_verdict(
    acc_a: frozenset[str],
    acc_b: frozenset[str],
    context: Collection[Fact],
    tol: Tolerance,
    exclude_spans: set[tuple[date | None, date]],
) -> bool | None:
    """True if filings in acc_a and acc_b both report some other period of
    this concept and every common period agrees; False on any disagreement;
    None when there is no common period (no evidence either way)."""
    by_acc: dict[str, dict[tuple[date | None, date], list[Decimal]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for f in context:
        span = (f.start_date, f.end_date)
        if span in exclude_spans:
            continue
        by_acc[f.accession][span].append(f.value)
    saw = False
    for a in acc_a:
        for b in acc_b:
            if a == b:
                continue
            for span, va in by_acc.get(a, {}).items():
                vb = by_acc.get(b, {}).get(span)
                if not vb:
                    continue
                saw = True
                if not all(tol.agree(x, y) for x in va for y in vb):
                    return False
    return True if saw else None


@dataclass
class _Pair:
    fy: _Cluster
    fy_index: int
    ytd: _Cluster
    ytd_index: int
    basis: str


def _pair_basis(
    fy: _Cluster,
    fy_idx: int,
    n_fy: int,
    ytd: _Cluster,
    ytd_idx: int,
    n_ytd: int,
    context: Collection[Fact],
    tol: Tolerance,
    exclude_spans: set[tuple[date | None, date]],
) -> str | None:
    if fy.accessions & ytd.accessions:
        return "same_accession"
    verdict = _overlap_verdict(
        fy.accessions, ytd.accessions, context, tol, exclude_spans
    )
    if verdict is False:
        return None
    if verdict is True:
        return "overlap_agreement"
    if n_fy == 1 and n_ytd == 1:
        return "unrestated_single_value"
    if fy_idx == 0 and ytd_idx == 0 and ytd.first_filed <= fy.first_filed:
        return "as_filed_original"
    if n_ytd == 1 and ytd.last_filed >= fy.first_filed:
        return "reconfirmed_after"
    if n_fy == 1 and fy.last_filed >= ytd.first_filed:
        return "reconfirmed_after"
    return None


# --------------------------------------------------------------------------
# YTD sources
# --------------------------------------------------------------------------


@dataclass
class _Source:
    kind: str  # "ytd9" | "chain"
    formula_id: str
    clusters: list[_Cluster]
    series: list[list[_Cluster]]  # for sign checks (one list per underlying series)
    end_date: date
    problem: str | None = None  # set when the source exists but is unusable


def _span(f: Fact) -> int:
    assert f.start_date is not None
    return (f.end_date - f.start_date).days


def _ytd9_source(
    facts: list[Fact],
    fy_start: date,
    fy_end: date,
    q4_min: int,
    q4_max: int,
    tol: Tolerance,
) -> _Source | None:
    cand = [
        f
        for f in facts
        if f.start_date == fy_start
        and f.end_date < fy_end
        and f.fiscal_period != "FY"
        and YTD9_MIN_DAYS <= _span(f) <= YTD9_MAX_DAYS
        and q4_min <= (fy_end - f.end_date).days <= q4_max
        and f.fiscal_period in (None, "Q3")
    ]
    if not cand:
        return None
    ends = {f.end_date for f in cand}
    if len(ends) != 1:
        return _Source(
            "ytd9", FORMULA_YTD9, [], [], min(ends), "ytd9_multiple_end_dates"
        )
    cl = _clusters(cand, tol)
    return _Source("ytd9", FORMULA_YTD9, cl, [cl], next(iter(ends)))


def _chain_source(
    facts: list[Fact],
    fy_start: date,
    fy_end: date,
    q4_min: int,
    q4_max: int,
    tol: Tolerance,
) -> _Source | None:
    by_q: dict[str, list[Fact]] = {"Q1": [], "Q2": [], "Q3": []}
    for f in facts:
        if (
            f.fiscal_period in by_q
            and f.start_date is not None
            and f.start_date >= fy_start
            and f.end_date < fy_end
            and CHAIN_QUARTER_MIN_DAYS <= _span(f) <= CHAIN_QUARTER_MAX_DAYS
        ):
            by_q[f.fiscal_period].append(f)
    if not all(by_q.values()):
        return None
    series: list[list[_Cluster]] = []
    spans: list[tuple[date, date]] = []
    for q in ("Q1", "Q2", "Q3"):
        span_set = {(f.start_date, f.end_date) for f in by_q[q]}
        if len(span_set) != 1:
            return _Source(
                "chain", FORMULA_CHAIN, [], [], fy_end, f"{q}_multiple_spans"
            )
        s, e = next(iter(span_set))
        assert s is not None
        spans.append((s, e))
        series.append(_clusters(by_q[q], tol))
    (s1, e1), (s2, e2), (s3, e3) = spans
    if not (
        s1 == fy_start
        and s2 == e1 + timedelta(days=1)
        and s3 == e2 + timedelta(days=1)
        and q4_min <= (fy_end - e3).days <= q4_max
    ):
        return _Source("chain", FORMULA_CHAIN, [], series, e3, "chain_not_contiguous")
    if any(len(s) != 1 for s in series):
        # Per-quarter restatement chains are not paired here (documented limit).
        return _Source(
            "chain", FORMULA_CHAIN, [], series, e3, "chain_member_has_multiple_values"
        )
    members = [s[0] for s in series]
    composite_facts = [m.rep for m in members]
    composite = _Cluster(
        facts=[f for m in members for f in m.facts],
        rep=composite_facts[-1],
    )
    # The chain sum is one synthetic value; carry member reps for lineage.
    composite_obj = _ChainCluster(composite.facts, composite.rep, members)
    return _Source("chain", FORMULA_CHAIN, [composite_obj], series, e3)


class _ChainCluster(_Cluster):
    """A chain of three single-valued quarter clusters acting as one YTD value."""

    def __init__(self, facts: list[Fact], rep: Fact, members: list[_Cluster]) -> None:
        super().__init__(facts, rep)
        self.members = members

    @property
    def value(self) -> Decimal:  # type: ignore[override]
        return sum((m.value for m in self.members), Decimal(0))

    @property
    def first_filed(self) -> date:  # all three must exist
        return max(m.first_filed for m in self.members)

    @property
    def last_filed(self) -> date:  # confirmed only as late as the least-recent member
        return min(m.last_filed for m in self.members)

    @property
    def exact(self) -> bool:
        return all(m.exact for m in self.members)

    @property
    def has_authoritative(self) -> bool:
        return all(m.has_authoritative for m in self.members)


# --------------------------------------------------------------------------
# evaluation
# --------------------------------------------------------------------------


def _arith(fy_v: Decimal, ytd_v: Decimal, q4: Decimal, chain: _Cluster | None) -> str:
    if isinstance(chain, _ChainCluster):
        q = " + ".join(str(m.value) for m in chain.members)
        return f"{fy_v} - ({q}) = {q4}"
    return f"{fy_v} - {ytd_v} = {q4}"


def _result_for_source(
    src: _Source,
    fy_clusters: list[_Cluster],
    context: Collection[Fact],
    tol: Tolerance,
    exclude_spans: set[tuple[date | None, date]],
    allow_non_latest: bool,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str]:
    """Returns (chosen, alternatives, reason_if_none)."""
    if not src.clusters:
        return None, [], src.problem or "source_unusable"
    pairs: list[_Pair] = []
    for i, fyc in enumerate(fy_clusters):
        for j, yc in enumerate(src.clusters):
            basis = _pair_basis(
                fyc,
                i,
                len(fy_clusters),
                yc,
                j,
                len(src.clusters),
                context,
                tol,
                exclude_spans,
            )
            if basis:
                pairs.append(_Pair(fyc, i, yc, j, basis))
    latest_idx = len(fy_clusters) - 1
    on_latest = [p for p in pairs if p.fy_index == latest_idx]
    pool = on_latest if on_latest else (pairs if allow_non_latest else [])
    if not pool:
        alts = [_pair_summary(p, src) for p in pairs]
        if pairs:
            reason = "valid_pairing_exists_only_for_superseded_fy_value"
        else:
            reason = "no_evidenced_same_vintage_pairing"
        return None, alts, reason
    # prefer the latest FY cluster, then the latest YTD cluster
    pool.sort(key=lambda p: (p.fy_index, p.ytd_index))
    best = pool[-1]
    alts = [_pair_summary(p, src) for p in pairs if p is not best]
    return _pair_summary(best, src, with_obj=True), alts, ""


def _pair_summary(p: _Pair, src: _Source, with_obj: bool = False) -> dict[str, Any]:
    q4 = p.fy.value - p.ytd.value
    d: dict[str, Any] = {
        "formula_id": src.formula_id,
        "vintage_basis": p.basis,
        "fy_value": p.fy.value,
        "ytd_value": p.ytd.value,
        "q4_value": q4,
        "fy_cluster_index": p.fy_index,
        "fy_accessions": sorted(p.fy.accessions),
        "ytd_accessions": sorted(p.ytd.accessions),
    }
    if with_obj:
        d["_pair"] = p
    return d


def evaluate_cell(
    facts: Collection[Fact],
    *,
    company_id: int,
    concept_id: int,
    additive: bool,
    tol: Tolerance,
    unit: str = "USD",
    q4_min_days: int = DEFAULT_Q4_MIN_DAYS,
    q4_max_days: int = DEFAULT_Q4_MAX_DAYS,
    context_facts: Collection[Fact] = (),
    allow_non_latest_fy_vintage: bool = False,
) -> Q4Candidate:
    """Classify one (company, concept, unit, fiscal year) cell. `facts` are
    the raw facts of that cell (derived facts are ignored); `context_facts`
    are other-period facts of the same concept, used only as overlap evidence
    for restated vintages."""
    cand = Q4Candidate(
        company_id=company_id,
        concept_id=concept_id,
        unit=unit,
        category=BLOCKED_NO_FY,
        block_reason=None,
        tolerance={"rel": str(tol.rel), "abs_tol": str(tol.abs_tol)},
    )

    def block(category: str, reason: str) -> Q4Candidate:
        cand.category, cand.block_reason = category, reason
        return cand

    if not additive:
        return block(BLOCKED_NON_ADDITIVE, "concept_not_on_additive_allowlist")
    raw = [f for f in facts if not f.is_derived]
    if any(f.unit != unit for f in raw):
        return block(BLOCKED_MIXED, "mixed_units_in_cell")
    durations = [f for f in raw if f.start_date is not None]
    if raw and not durations:
        return block(BLOCKED_NON_ADDITIVE, "instant_facts_only")
    cand.direct_q4_fact_ids = sorted(
        f.fact_id for f in durations if f.fiscal_period == "Q4"
    )

    fy_facts = [
        f
        for f in durations
        if f.fiscal_period == "FY"
        and FULL_YEAR_MIN_DAYS <= _span(f) <= FULL_YEAR_MAX_DAYS
    ]
    if not fy_facts:
        return block(BLOCKED_NO_FY, "no_full_year_fact")
    fy_spans = {(f.start_date, f.end_date) for f in fy_facts}
    if len(fy_spans) != 1:
        return block(BLOCKED_NO_FY, "fy_span_ambiguous")
    fy_start, fy_end = next(iter(fy_spans))
    assert fy_start is not None
    cand.fiscal_year_start, cand.fiscal_year_end = fy_start, fy_end

    others = [f for f in durations if f.fiscal_period != "FY"]
    sources = [
        s
        for s in (
            _ytd9_source(others, fy_start, fy_end, q4_min_days, q4_max_days, tol),
            _chain_source(others, fy_start, fy_end, q4_min_days, q4_max_days, tol),
        )
        if s is not None
    ]
    if not sources:
        return block(BLOCKED_NO_YTD, "no_ytd9_and_no_complete_q1_q3_chain")

    fy_clusters = _clusters(fy_facts, tol)
    if _has_sign_conflict(fy_clusters, tol):
        return block(BLOCKED_SIGN, "fy_copies_differ_only_by_sign")
    for s in sources:
        if any(_has_sign_conflict(ser, tol) for ser in s.series):
            return block(BLOCKED_SIGN, f"{s.kind}_copies_differ_only_by_sign")

    exclude_spans: set[tuple[date | None, date]] = {
        (f.start_date, f.end_date) for f in durations
    }
    ctx = [*context_facts, *durations]
    results = []
    reasons = []
    for s in sources:
        chosen, alts, reason = _result_for_source(
            s, fy_clusters, ctx, tol, exclude_spans, allow_non_latest_fy_vintage
        )
        if chosen is None:
            reasons.append(f"{s.kind}:{reason}")
            cand.alternatives.extend({"source": s.kind, **a} for a in alts)
        else:
            cand.alternatives.extend({"source": s.kind, **a} for a in alts)
            results.append((s, chosen))

    if not results:
        return block(BLOCKED_MIXED, "; ".join(reasons))

    s, chosen = results[0]  # sources are ordered 9M first, then chain
    if len(results) > 1:
        other = results[1][1]
        if not tol.agree(chosen["q4_value"], other["q4_value"]):
            cand.alternatives.append({"source": results[1][0].kind, **_strip(other)})
            return block(BLOCKED_MIXED, "ytd9_and_chain_disagree")
        cand.notes.append("ytd9_and_chain_agree")

    pair: _Pair = chosen["_pair"]
    cand.formula_id = s.formula_id
    cand.fy_fact_ids = [pair.fy.rep.fact_id]
    cand.fy_accessions = [pair.fy.rep.accession]
    cand.fy_value = pair.fy.value
    cand.ytd_value = pair.ytd.value
    if isinstance(pair.ytd, _ChainCluster):
        cand.ytd_fact_ids = [m.rep.fact_id for m in pair.ytd.members]
        cand.ytd_accessions = [m.rep.accession for m in pair.ytd.members]
    else:
        cand.ytd_fact_ids = [pair.ytd.rep.fact_id]
        cand.ytd_accessions = [pair.ytd.rep.accession]
    cand.q4_value = chosen["q4_value"]
    cand.q4_start = s.end_date + timedelta(days=1)
    cand.q4_end = fy_end
    cand.arithmetic = _arith(pair.fy.value, pair.ytd.value, cand.q4_value, pair.ytd)
    cand.vintage_basis = pair.basis
    cand.fy_is_latest_vintage = pair.fy_index == len(fy_clusters) - 1
    if not cand.fy_is_latest_vintage:
        cand.notes.append("fy_value_is_superseded_by_a_later_filing")
    if cand.direct_q4_fact_ids:
        cand.notes.append("direct_reported_q4_exists_prefer_it")

    clean = (
        pair.fy.exact
        and pair.ytd.exact
        and pair.fy.has_authoritative
        and pair.ytd.has_authoritative
        and len(fy_clusters) == 1
        and len(s.clusters) == 1
        and cand.fy_is_latest_vintage
    )
    cand.category = CLEAN if clean else SAME_VINTAGE
    return cand


def _strip(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if k != "_pair"}


# --------------------------------------------------------------------------
# read-only loader
# --------------------------------------------------------------------------

LOAD_SQL = """
select f.id, f.company_id, f.concept_id, u.unit_name, f.value, fl.accession_number,
       fl.filing_date, p.start_date, p.end_date, f.is_authoritative, p.fiscal_period
from core.fact f
join core.period p on p.id = f.period_id
join core.filing fl on fl.id = f.filing_id
join core.unit u on u.id = f.unit_id
where f.company_id = any(%(company_ids)s)
  and f.concept_id = any(%(concept_ids)s)
  and not f.is_derived
  and p.period_type = 'duration'
  and fl.filing_date is not null
  and (
      p.fiscal_period in ('FY', 'Q1', 'Q2', 'Q3', 'Q4')
      or (p.fiscal_period is null
          and (p.end_date - p.start_date) between %(ytd_min)s and %(ytd_max)s)
  )
"""


def _fy_groups(facts: list[Fact]) -> dict[date, list[Fact]]:
    """Attach every non-FY fact to the FY whose [start, end] contains it;
    FY copies sharing a start date form one group (spans are checked later)."""
    fy_by_start: dict[date, date] = {}
    for f in facts:
        if (
            f.fiscal_period == "FY"
            and f.start_date is not None
            and FULL_YEAR_MIN_DAYS
            <= (f.end_date - f.start_date).days
            <= FULL_YEAR_MAX_DAYS
        ):
            fy_by_start[f.start_date] = max(
                fy_by_start.get(f.start_date, f.end_date), f.end_date
            )
    groups: dict[date, list[Fact]] = {s: [] for s in fy_by_start}
    for f in facts:
        if f.start_date is None:
            continue
        for s, e in fy_by_start.items():
            if f.fiscal_period == "FY":
                if f.start_date == s:
                    groups[s].append(f)
                    break
            elif f.start_date >= s and f.end_date <= e:
                groups[s].append(f)
                break
    return groups


def load_candidates(
    conn: psycopg.Connection,
    company_ids: list[int],
    *,
    concept_ids: Collection[int],
    additive_concept_ids: Collection[int],
    tol: Tolerance,
    chunk_size: int = 25,
    q4_min_days: int = DEFAULT_Q4_MIN_DAYS,
    q4_max_days: int = DEFAULT_Q4_MAX_DAYS,
    allow_non_latest_fy_vintage: bool = False,
) -> Iterator[Q4Candidate]:
    """Yield one Q4Candidate per (company, concept, unit, fiscal year).

    READ-ONLY: a single parameterized select per chunk of company ids, no
    writes, no commit. The caller owns the connection (and should not pass a
    pooler connection while a heavy peer job runs -- see CLAUDE.md). Concepts
    outside additive_concept_ids come back as blocked_non_additive without
    their facts being interpreted."""
    additive = set(additive_concept_ids)
    ids = sorted(set(company_ids))
    for i in range(0, len(ids), chunk_size):
        chunk = ids[i : i + chunk_size]
        with conn.cursor() as cur:
            cur.execute(
                LOAD_SQL,
                {
                    "company_ids": chunk,
                    "concept_ids": sorted(concept_ids),
                    "ytd_min": YTD9_MIN_DAYS,
                    "ytd_max": YTD9_MAX_DAYS,
                },
            )
            rows = cur.fetchall()
        by_key: dict[tuple[int, int, str], list[Fact]] = defaultdict(list)
        for fid, cid, concept, unit, value, acc, fdate, start, end, auth, fp in rows:
            by_key[(cid, concept, unit)].append(
                Fact(fid, Decimal(value), acc, fdate, start, end, bool(auth), fp, unit)
            )
        for (cid, concept, unit), facts in sorted(by_key.items()):
            if concept not in additive:
                yield evaluate_cell(
                    [],
                    company_id=cid,
                    concept_id=concept,
                    additive=False,
                    tol=tol,
                    unit=unit,
                )
                continue
            for _start, group in sorted(_fy_groups(facts).items()):
                yield evaluate_cell(
                    group,
                    company_id=cid,
                    concept_id=concept,
                    additive=True,
                    tol=tol,
                    unit=unit,
                    q4_min_days=q4_min_days,
                    q4_max_days=q4_max_days,
                    context_facts=facts,
                    allow_non_latest_fy_vintage=allow_non_latest_fy_vintage,
                )


def summarize(candidates: Iterable[Q4Candidate]) -> dict[str, int]:
    """Category and block-reason counts for the run report."""
    out: dict[str, int] = defaultdict(int)
    for c in candidates:
        out[c.category] += 1
        if c.block_reason:
            out[f"reason:{c.block_reason}"] += 1
    return dict(out)
