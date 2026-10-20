"""I11 history completeness over the window 2015-01-01 .. latest filing
(founder requirement 2026-10-21, data-team/34 "History window").

Expected periods come from the company's own periodic filings in core.filing
(not from core.period, which also holds odd segment dates): every 10-K gives an
annual period (FY), a Q4 and a fiscal-year-end balance-sheet instant, every
10-Q a quarter (Q) and a quarter-end instant. The window starts at the later of
2015-01-01 and the company's first periodic filing; a company whose first filing
is more than a quarter after 2015-01-01 gets one `history_starts_after_window`
finding (predecessor CIK or a late registrant: needs a person).

Consumed concepts: every canonical concept that feeds at least one metric
(analytics.metric_definition_input, 33 on 2026-10-21), read from the registry.
Balance-sheet concepts are expected as instants, the rest as durations. A
concept is PRESENT for a period when a stored canonical value (either layer)
sits on a matching period: durations of the right length ending within 7 days
of the filing's period, instants within 7 days.

Every missing cell is classified: first by the analytics.period_gap row for the
same concept, kind and period end (q4_not_derived, quarter_not_derived,
no_mapped_tag, no_line_item_filed, not_in_sec_feed, conflict_*,
filing_not_processed); period_gap tracks only 15 concepts, so for the others
`infer_cause` uses the facts stored under the concept's mapped tags
(fact_exists_not_resolved, q4_not_derived, quarter_not_derived, no_mapped_tag),
and only the rest stays `unclassified`. Metrics: a missing metric cell
is classified by its stored is_null_reason; with no row at all it is bucketed
(`classify_no_row`): not_defined_for_period_kind, insufficient_history,
input_gap (the input's cause carried), else `no_row_inputs_present` (a real
Mapper gap). Certification needs zero `unclassified`/`no_row_inputs_present`; classified gaps stay open
findings for their owner until filled. All severities are `review` (a gap is
not a wrong value).

One finding per (concept, kind, cause) lists the missing period ends, so a
company with 40 missing cells for one reason is one row, not 40.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date, timedelta

from .model import REVIEW, Cell, CompanyData, Finding, base_name, finding

TOLERANCE_DAYS = 7
YEAR_MIN, YEAR_MAX = 350, 380
QUARTER_MIN, QUARTER_MAX = 61, 121
KINDS = ("FY", "Q", "Q4", "I")
ANNUAL_FORMS = ("10-K", "10-K/A", "10-KT", "10-KT/A")
LATE_START_DAYS = 120  # first filing later than window start + this -> flagged


def _is_annual(form: str) -> bool:
    return form in ANNUAL_FORMS


def expected_periods(data: CompanyData) -> set[tuple[str, date]]:
    """(kind, period end) cells expected for the window, from filings."""
    if not data.filings:
        return set()
    start = data.window_start
    if data.first_filing_period and data.first_filing_period > start:
        start = data.first_filing_period
    ceiling = data.latest_filed or data.as_of
    out: set[tuple[str, date]] = set()
    for por, form in data.filings:
        if por < start or por > ceiling:
            continue
        out.add(("I", por))
        if _is_annual(form):
            out.add(("FY", por))
            out.add(("Q4", por))
        else:
            out.add(("Q", por))
    return _merge_near(out)


def _merge_near(cells: set[tuple[str, date]]) -> set[tuple[str, date]]:
    """Amendments and 52/53-week quirks give period ends a few days apart; keep
    one cell per kind per 7-day neighbourhood."""
    out: set[tuple[str, date]] = set()
    for kind in KINDS:
        last: date | None = None
        for _, end in sorted(c for c in cells if c[0] == kind):
            if last is not None and (end - last).days <= TOLERANCE_DAYS:
                continue
            out.add((kind, end))
            last = end
    return out


def _matches(cell: Cell, kind: str, end: date) -> bool:
    if abs((cell.end - end).days) > TOLERANCE_DAYS:
        return False
    d = cell.days
    if kind == "I":
        return d is None
    if d is None:
        return False
    if kind == "FY":
        return YEAR_MIN <= d <= YEAR_MAX
    return QUARTER_MIN <= d <= QUARTER_MAX  # Q and Q4


def reason_family(reason: str) -> str:
    """Stored null reasons carry parameters ('missing:fcf(2015),cfo(2014)...',
    'missing:prior_period(2005_FY)'). The family keeps the text before the first
    parenthesis or comma so one finding rule covers them all; the full texts go
    into the evidence."""
    text = re.sub(r"\.\.\.$", "", reason.strip())
    return re.split(r"[(,]", text, maxsplit=1)[0].strip() or "no_row"


UNCLASSIFIED_METRIC_CAUSES = frozenset(
    {"no_row_inputs_present", "input_gap:unclassified"}
)
LOOKBACK_SLACK_DAYS = 45
_T_MINUS = re.compile(r"\[(?:t|FY)-(\d+)\]")
_MOST_RECENT = re.compile(r"(\d+)\s+most recent", re.I)


def declared_kinds(spec) -> set[str]:
    """Period kinds a metric's registry text says it is written for. Text,
    not names, decides: 'FY only' / 'FY periods' / 'per FY' / 'for the fiscal
    year' -> annual; price-date and '(TTM)' metrics are written with the TTM
    label, which has no FY/Q cell; everything else (incl. 'same fiscal_period')
    -> annual and quarterly. Kinds actually written for any company of the
    chunk are added by the caller."""
    text = spec.description
    if (
        re.search(r"\bFY\b|for the fiscal year|per fiscal year", text)
        and "fiscal_period" not in text
    ):
        return {"FY"}
    if spec.requires_price or "(TTM)" in text:
        return set()
    return {"FY", "Q"}


def lookback_days(spec) -> int:
    """How far before the period the metric needs data, read from its registry
    text: '[t-3]' / '[FY-1]' -> years, 'year over year' -> 1, 'N most recent'
    -> N-1, '~1yr ago' / 'prior FY' -> 1. 0 when the text names no lookback."""
    if spec is None:
        return 0
    text = spec.description
    years = [int(x) for x in _T_MINUS.findall(text)]
    if re.search(r"year over year|yoy|~1yr ago|prior FY", text, re.I):
        years.append(1)
    years += [int(x) - 1 for x in _MOST_RECENT.findall(text)]
    return int(max(years, default=0) * 365.25)


def classify_no_row(data, spec, kind, end, q4_ends, lookup):
    """Bucket of a metric cell with no stored row (data decision 2026-10-21):
      insufficient_history  the metric looks back further than the company's
                            first stored period (lookback from the registry text)
      input_gap             a required input concept is itself a missing cell
                            on this period (its cause is carried); an input whose
                            own cause is unclassified makes this
                            `input_gap:unclassified` (blocking)
      no_row_inputs_present every input exists yet no row was written: a real
                            Mapper gap, blocking
    (`not_defined_for_period_kind` is decided earlier, per kind.) Returns
    (bucket, [input causes])."""
    if spec is None:
        return "no_row_inputs_present", []
    lb = lookback_days(spec)
    first = data.first_data_period
    if lb and first and end - timedelta(days=lb + LOOKBACK_SLACK_DAYS) < first:
        return "insufficient_history", []
    causes: list[str] = []
    for base, statement in zip(spec.inputs, spec.input_statements):
        if statement == "balance_sheet":
            ckind = "I"
        elif kind == "FY":
            ckind = "FY"
        else:
            ckind = (
                "Q4"
                if any(abs((end - q).days) <= TOLERANCE_DAYS for q in q4_ends)
                else "Q"
            )
        by_end = lookup.get((base, ckind), {})
        for delta in range(-TOLERANCE_DAYS, TOLERANCE_DAYS + 1):
            cause = by_end.get(end + timedelta(days=delta))
            if cause:
                causes.append(cause)
                break
    if causes:
        if "unclassified" in causes:
            return "input_gap:unclassified", causes
        return "input_gap", causes
    return "no_row_inputs_present", []


def _concept_kinds(statement: str) -> tuple[str, ...]:
    return ("I",) if statement == "balance_sheet" else ("FY", "Q", "Q4")


def _span_days(start: date | None, end: date) -> int | None:
    return None if start is None or start == end else (end - start).days


def _fact_matches(span: tuple[date | None, date], kind: str, end: date) -> bool:
    """A mapped fact's (start, end) is the cell's period: same class, end within 7 days."""
    start, fact_end = span
    if abs((fact_end - end).days) > TOLERANCE_DAYS:
        return False
    d = _span_days(start, fact_end)
    if kind == "I":
        return d is None
    if d is None:
        return False
    return (
        YEAR_MIN <= d <= YEAR_MAX if kind == "FY" else QUARTER_MIN <= d <= QUARTER_MAX
    )


def infer_cause(data: CompanyData, base: str, kind: str, end: date) -> str:
    """Cause of a missing cell with NO analytics.period_gap row (the table tracks
    only 15 concepts). Evidence is the facts stored under the tags mapped to the
    concept (analytics.concept_mapping, not 'rejected'), any authority:

      fact_exists_not_resolved  a fact on this very period exists under a mapped tag
                                (resolver/derivation/authority dropped it)
      q4_not_derived            kind Q4, no Q4-length fact, but the fiscal-year fact exists
      quarter_not_derived       kind Q, no discrete-quarter fact, but a longer
                                year-to-date fact ends on the same date
      no_mapped_tag             no fact under any mapped tag for the period AND the
                                period is otherwise loaded (another concept has data
                                near that date), so the line is not under a mapped tag
      unclassified              the concept has no mapped tag, or the period has no
                                data at all (probable ingestion gap): evidence is
                                insufficient, a person decides

    The last two Q4/quarter causes reuse period_gap's own names for the same
    situation so one cause means one thing across tracked and untracked concepts."""
    if data.mapped_tag_count.get(base, 0) == 0:
        return "unclassified"
    spans = data.mapped_facts.get(base, [])
    if any(_fact_matches(sp, kind, end) for sp in spans):
        return "fact_exists_not_resolved"
    if kind == "Q4" and any(_fact_matches(sp, "FY", end) for sp in spans):
        return "q4_not_derived"
    if kind == "Q" and any(
        abs((fe - end).days) <= TOLERANCE_DAYS
        and (_span_days(st, fe) or 0) > QUARTER_MAX
        for st, fe in spans
    ):
        return "quarter_not_derived"
    loaded = any(abs((c.end - end).days) <= TOLERANCE_DAYS for c in data.cells) or any(
        abs((fe - end).days) <= TOLERANCE_DAYS
        for other in data.mapped_facts.values()
        for _st, fe in other
    )
    return "no_mapped_tag" if loaded else "unclassified"


def _gap_cause(gaps: dict, base: str, kind: str, end: date) -> str | None:
    for delta in range(-TOLERANCE_DAYS, TOLERANCE_DAYS + 1):
        cause = gaps.get((base, kind, end + timedelta(days=delta)))
        if cause:
            return cause
    return None


def history_matrix(data: CompanyData) -> dict:
    """Counts for the report and the findings: {'concepts': Counter keyed
    (year, kind, 'expected'|'present'|'missing'|'unclassified'), 'metrics': same,
    'missing': {(base, kind, cause): [end, ...]}, 'missing_metrics': {...}}."""
    expected = expected_periods(data)
    gaps = {(g.base, g.kind, g.end): g.cause for g in data.period_gaps}
    by_base: dict[str, list[Cell]] = defaultdict(list)
    for c in data.cells:
        by_base[c.base].append(c)
    consumed: dict[str, str] = {}
    for name, statement in data.consumed.items():
        consumed.setdefault(base_name(name), statement)

    concepts: Counter = Counter()
    missing: dict[tuple[str, str, str], list[date]] = defaultdict(list)
    for base, statement in consumed.items():
        cells = by_base.get(base, [])
        for kind, end in sorted(expected):
            if kind not in _concept_kinds(statement):
                continue
            year = end.year
            concepts[(year, kind, "expected")] += 1
            if any(_matches(c, kind, end) for c in cells):
                concepts[(year, kind, "present")] += 1
                continue
            cause = _gap_cause(gaps, base, kind, end) or infer_cause(
                data, base, kind, end
            )
            concepts[(year, kind, "missing")] += 1
            if cause == "unclassified":
                concepts[(year, kind, "unclassified")] += 1
            missing[(base, kind, cause)].append(end)

    metrics: Counter = Counter()
    buckets: Counter = Counter()  # metric cells by bucket (cells, not findings)
    input_causes: Counter = Counter()
    full_reasons: dict[tuple[str, str], set[str]] = defaultdict(set)
    missing_metrics: dict[tuple[str, str, str], list[date]] = defaultdict(list)
    rows: dict[tuple[str, str, date], list] = defaultdict(list)  # (name, 'FY'|'Q', end)
    own_kinds: dict[str, set[str]] = defaultdict(set)
    for m in data.metric_history:
        kind = "FY" if m.label == "FY" else "Q"
        own_kinds[m.name].add(kind)
        rows[(m.name, kind, m.end)].append(m)
    # missing concept cells by (base, kind) -> {end: cause}: the input evidence for (c)
    lookup: dict[tuple[str, str], dict[date, str]] = defaultdict(dict)
    for (base, ckind, cause), ends in missing.items():
        for e in ends:
            lookup[(base, ckind)][e] = cause
    q4_ends = {e for k, e in expected if k == "Q4"}
    for name in sorted(set(data.metric_specs) | set(own_kinds)):
        spec = data.metric_specs.get(name)
        # Kinds actually written for any company of the chunk are authoritative
        # (ROE/ROA/ROIC are written with the TTM label only: a quarter label is
        # not defined for them); the registry text decides only when the chunk
        # has no row of the metric at all.
        observed = data.metric_kinds_seen.get(name, set()) | own_kinds.get(name, set())
        defined = observed or (declared_kinds(spec) if spec else set())
        point_in_time = bool(
            spec
            and spec.inputs
            and all(st == "balance_sheet" for st in spec.input_statements)
        )
        for kind in ("FY", "Q"):
            wanted = {
                e
                for k, e in expected
                if (k == "FY" if kind == "FY" else k in ("Q", "Q4"))
            }
            if kind not in defined:
                buckets["not_defined_for_period_kind"] += len(wanted)
                continue
            for end in sorted(wanted):
                year = end.year
                metrics[(year, kind, "expected")] += 1
                keys = [(name, kind)]
                if point_in_time and kind == "Q" and end in q4_ends:
                    keys.append(
                        (name, "FY")
                    )  # a balance-sheet metric at fiscal-year end is labelled FY
                found = [
                    m
                    for nm, kd in keys
                    for delta in range(-TOLERANCE_DAYS, TOLERANCE_DAYS + 1)
                    for m in rows.get((nm, kd, end + timedelta(days=delta)), [])
                ]
                if any(m.value is not None for m in found):
                    metrics[(year, kind, "present")] += 1
                    continue
                reason = next((m.reason for m in found if m.reason), None)
                metrics[(year, kind, "missing")] += 1
                if reason is not None:
                    family = reason_family(reason)
                    full_reasons[(name, kind)].add(reason)
                else:
                    family, causes = classify_no_row(
                        data, spec, kind, end, q4_ends, lookup
                    )
                    for c in causes:
                        input_causes[c] += 1
                    full_reasons[(name, kind)].add(family)
                buckets[family] += 1
                if family == "no_row_inputs_present" and (
                    spec is None or not spec.inputs
                ):
                    buckets["no_row_inputs_present:metric_has_no_registry_inputs"] += 1
                if family in UNCLASSIFIED_METRIC_CAUSES:
                    metrics[(year, kind, "unclassified")] += 1
                missing_metrics[(name, kind, family)].append(end)
    return {
        "concepts": concepts,
        "metrics": metrics,
        "missing": missing,
        "missing_metrics": missing_metrics,
        "metric_reasons": full_reasons,
        "metric_buckets": buckets,
        "metric_input_causes": input_causes,
    }


def check(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    if not data.consumed:
        return out
    if (
        data.first_filing_period
        and data.first_filing_period
        > data.window_start + timedelta(days=LATE_START_DAYS)
    ):
        out.append(
            finding(
                data,
                "I11",
                REVIEW,
                "history_starts_after_window",
                "history",
                period_end=data.first_filing_period,
                window_start=str(data.window_start),
                # blocks checks_clean: the missing years are not explained until a
                # predecessor-CIK link (or a registration date) is recorded
                classified=False,
                first_filing_period=str(data.first_filing_period),
                note="no periodic filing before this date under this CIK: late registrant or "
                "history lives at a predecessor CIK (needs a Company Master link)",
            )
        )
    if not data.filings:
        out.append(
            finding(
                data,
                "I11",
                REVIEW,
                "no_periodic_filing_in_window",
                "history",
                window_start=str(data.window_start),
                classified=False,
            )
        )
        return out
    m = history_matrix(data)
    for (base, kind, cause), ends in sorted(m["missing"].items()):
        out.append(
            finding(
                data,
                "I11",
                REVIEW,
                f"missing_cell:{cause}",
                base,
                period_end=max(ends),
                kind=kind,
                cause=cause,
                count=len(ends),
                classified=cause != "unclassified",
                period_ends=[str(e) for e in sorted(ends)[:80]],
            )
        )
    for (name, kind, reason), ends in sorted(m["missing_metrics"].items()):
        out.append(
            finding(
                data,
                "I11",
                REVIEW,
                f"missing_metric:{reason}",
                name,
                period_end=max(ends),
                kind=kind,
                cause=reason,
                count=len(ends),
                classified=reason not in UNCLASSIFIED_METRIC_CAUSES,
                reasons_seen=sorted(m["metric_reasons"].get((name, kind), ()))[:5],
                period_ends=[str(e) for e in sorted(ends)[:80]],
            )
        )
    return out
