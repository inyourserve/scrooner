"""I6 source integrity.

Every stored value (both layers) must be explained by its source facts:

  non_periodic_form     a source fact filed on a form outside the 10-K / 10-Q /
                        20-F / 40-F family (DEF 14A, 8-K, S-1, ...): wrong_value.
                        MDT net income came from a DEF 14A (fact 64871764) at
                        4,801 dollars instead of 4,801 million.
  wrong_unit            the source fact's unit is not the concept's unit family
                        (USD for money, USD/shares for per-share, shares for
                        counts): wrong_value (IVDA: a TWD cash fact).
  non_authoritative     the source fact is not authoritative. If an authoritative
                        copy of the same tag, period and unit exists and the
                        stored value differs from it beyond rounding: wrong_value
                        (the matching-copies rule: copies equal within 0.01% are
                        one value, so a rounded copy never replaces a precise
                        one). If no authoritative copy exists the cell is a
                        conflict fill (analytics/conflict_resolution.py) and is
                        a RECORDED conflict fill (>= 2 non-authoritative copies within
                        15% of each other, stored value is one of them) is `info`
                        (counted, not stored: expected per data-team/20 s2); any other
                        non-authoritative source (a lone copy, copies > 15% apart, or a
                        value that is none of the copies) is `review`.
  value_not_in_sources  the stored value is not what its sources say: for
                        first_match concepts it must equal one source value (or
                        arithmetic of several: sum, a - b, a - rest), for sum
                        concepts the sum of them (within 0.01%). Split-adjusted
                        per-share values must equal source / split ratio.
"""

from __future__ import annotations

from decimal import Decimal
from itertools import combinations, product

from .thresholds import (
    PROXY_ROUNDING_MAX,
    SCALE_RATIO,
    ROUNDING_TOLERANCE,
    CONFLICT_FILL_MAX_SPREAD,
)
from .model import (
    INFO,
    PERIODIC_FORMS,
    REVIEW,
    WRONG_VALUE,
    CompanyData,
    Finding,
    expected_unit,
    finding,
)

# mapper/conflict_resolution.py fills a period whose copies are ALL non-authoritative
# only when the worst-case disagreement is <= 15% (data-team/20 section 2).


def is_recorded_conflict_fill(value: Decimal, source, others) -> bool:
    """A non-authoritative source is a RECORDED conflict fill (expected, not a
    rule break) when the period has no authoritative copy (checked by the
    caller), at least one other non-authoritative copy exists, the copies
    disagree by at most 15% of the largest, and the stored value is one of the
    copies (the resolver's tie-break picks an existing copy; matching copies
    within rounding count as the same copy)."""
    copies = [source, *others]
    if len(copies) < 2:
        return False
    values = [c.value for c in copies]
    biggest = max(abs(v) for v in values)
    if (
        biggest != 0
        and (max(values) - min(values)) / biggest > CONFLICT_FILL_MAX_SPREAD
    ):
        return False
    return any(_close(value, v) for v in values)


def _close(a: Decimal, b: Decimal) -> bool:
    if a == b:
        return True
    denom = max(abs(a), abs(b))
    return denom != 0 and abs(a - b) / denom <= ROUNDING_TOLERANCE


# A split-adjusted per-share value lists the split conversion ratio as an extra
# input (Apple basic EPS 5.43 / 4 = 1.3575; the ratio fact is unit `pure`). It is
# an adjustment factor, not a source of the value, so it is exempt from the unit
# test and the value is compared with the main source divided by the ratio.
ADJUSTMENT_TAG_HINT = "SplitConversionRatio"


def _explained_by_arithmetic(value: Decimal, sources) -> bool:
    """True when `value` is the sum of some of the sources, or one source minus
    another / minus the rest: the resolver's arithmetic fallbacks (gross profit =
    revenue - cost of revenue, total liabilities = assets - equity - NCI,
    operating expenses = sum of parts). Several copies of one tag (restated
    values) are tried one at a time, never added together."""
    by_tag: dict[str, list[Decimal]] = {}
    for s in sources:
        by_tag.setdefault(s.tag, [])
        if s.value not in by_tag[s.tag]:
            by_tag[s.tag].append(s.value)
    tags = list(by_tag)[:8]
    tried = 0
    for choice in product(*(by_tag[t] for t in tags)):
        tried += 1
        if tried > 256:
            break
        vals = list(choice)
        for n in range(2, min(len(vals), 5) + 1):
            for combo in combinations(vals, n):
                if _close(value, sum(combo, Decimal(0))):
                    return True
        for i, a in enumerate(vals):
            rest = [v for j, v in enumerate(vals) if j != i]
            if _close(value, a - sum(rest, Decimal(0))):
                return True
            for b in rest:
                if _close(value, a - b):
                    return True
    return False


def _is_adjustment(tag: str) -> bool:
    return ADJUSTMENT_TAG_HINT in tag


def _proxy_value_wrong(stored: Decimal, copies) -> bool:
    """The stored proxy/8-K number differs from every periodic copy AND the gap is
    the shape of an error, not of a re-presentation: within PROXY_ROUNDING_MAX
    (a proxy prints rounded millions or billions: JPM 48,300M vs 48,334M) or a
    unit-scale gap of SCALE_RATIO or more (SCHW thousands stored as dollars). A
    gap in between is a recast or restated basis (LLY 8-K revenue 4,514.9M vs the
    original 4,865.1M): review."""
    if not copies or any(_close(stored, c.value) for c in copies):
        return False
    for c in copies:
        if c.value == 0 or stored == 0:
            continue
        rel = abs(stored - c.value) / max(abs(stored), abs(c.value))
        ratio = abs(stored / c.value)
        big = ratio if ratio >= 1 else 1 / ratio
        if rel > PROXY_ROUNDING_MAX and big < SCALE_RATIO:
            return False  # at least one copy is a plausible re-presentation basis
    return True


def _non_periodic_findings(data: CompanyData) -> list[Finding]:
    """I6 non_periodic_form over EVERY stored cell (both layers: the Verifier counts
    JPM's 15 wrong cells in `net_income` and `net_income_resolved`). A value taken
    from a proxy or 8-K is a LINEAGE defect (`review`) when a 10-K/10-Q copy gives
    the same number or a plausible re-presentation (MA, MSFT, AVGO, LLY single-input
    cells: right as filed); it is `wrong_value` when `_proxy_value_wrong`
    (data-team/36 items 2 and 7)."""
    out: list[Finding] = []
    for cell in data.cells:
        sources = [s for s in data.source_facts(cell) if not _is_adjustment(s.tag)]
        for s in sources:
            if s.form is None or s.form in PERIODIC_FORMS:
                continue
            copies = data.periodic_copies.get(s.id, [])
            differs = len(sources) == 1 and _proxy_value_wrong(cell.value, copies)
            out.append(
                finding(
                    data,
                    "I6",
                    WRONG_VALUE if differs else REVIEW,
                    "non_periodic_form",
                    cell,
                    other=copies[0].value if differs else s.value,
                    form=s.form,
                    tag=s.tag,
                    accession=s.accession,
                    source_ids=[s.id],
                    fact_authoritative=s.authoritative,
                    differs_from_periodic_copy=differs,
                    periodic_copies=[
                        {
                            "id": c.id,
                            "value": str(c.value),
                            "form": c.form,
                            "accession": c.accession,
                        }
                        for c in copies[:5]
                    ],
                )
            )
    return out


def check(data: CompanyData) -> list[Finding]:
    """Checks the DISPLAYED layer only (the `_resolved` row where one exists):
    the base row of a resolved pair is not shown, and counting both would
    double every finding."""
    findings: list[Finding] = _non_periodic_findings(data)
    for cell in data.display_cells():
        all_sources = data.source_facts(cell)
        sources = [s for s in all_sources if not _is_adjustment(s.tag)]
        ratios = [s for s in all_sources if _is_adjustment(s.tag) and s.value]
        if not sources:
            continue
        for s in sources:
            want = expected_unit(cell.base)
            if want is not None and s.unit is not None and s.unit.lower() != want:
                findings.append(
                    finding(
                        data,
                        "I6",
                        WRONG_VALUE,
                        "wrong_unit_family",
                        cell,
                        other=s.value,
                        unit=s.unit,
                        expected_unit=want,
                        tag=s.tag,
                        accession=s.accession,
                        source_ids=[s.id],
                    )
                )
            if not s.authoritative:
                copies = data.authoritative_copies.get(s.id, [])
                if copies and len(sources) > 1:
                    pass  # a calculated cell is not comparable with one input's copies (TSLA OI FY2017)
                elif copies:
                    differing = [c for c in copies if not _close(cell.value, c.value)]
                    if differing and not any(
                        _close(cell.value, c.value) for c in copies
                    ):
                        findings.append(
                            finding(
                                data,
                                "I6",
                                WRONG_VALUE,
                                "differs_from_authoritative_copy",
                                cell,
                                other=differing[0].value,
                                tag=s.tag,
                                copies=[
                                    {
                                        "id": c.id,
                                        "value": str(c.value),
                                        "form": c.form,
                                        "accession": c.accession,
                                    }
                                    for c in copies
                                ],
                                source_ids=[s.id],
                            )
                        )
                else:
                    others = data.conflict_copies.get(s.id, [])
                    recorded = is_recorded_conflict_fill(cell.value, s, others)
                    findings.append(
                        finding(
                            data,
                            "I6",
                            INFO if recorded else REVIEW,
                            "non_authoritative_source",
                            cell,
                            other=s.value,
                            conflict_filled=recorded,
                            copies=len(others) + 1,
                            tag=s.tag,
                            accession=s.accession,
                            source_ids=[s.id],
                        )
                    )
        tags = {s.tag for s in sources}
        if (
            len(tags) > 1
            and any(
                s.form is not None and s.form not in PERIODIC_FORMS for s in sources
            )
            and any(s.form in PERIODIC_FORMS for s in sources)
        ):
            # R-MIXED-VINTAGE: a calculated cell whose inputs come from a recast filing
            # and from the original periodic filings (LLY gross profit = 8-K revenue
            # minus 10-K cost of sales)
            findings.append(
                finding(
                    data,
                    "I6",
                    WRONG_VALUE,
                    "mixed_vintage",
                    cell,
                    sources=[
                        {
                            "id": s.id,
                            "tag": s.tag,
                            "form": s.form,
                            "accession": s.accession,
                        }
                        for s in sources
                    ],
                )
            )
        if any(s.derived for s in sources):
            continue  # a derived cell is explained by its inputs, checked elsewhere
        mode = data.concept_modes.get(cell.concept, "first_match")
        if ratios:
            divisor = Decimal(1)
            for r in ratios:
                divisor *= r.value
            if not any(
                _close(cell.value, s.value / divisor) or _close(cell.value, s.value)
                for s in sources
            ):
                findings.append(
                    finding(
                        data,
                        "I6",
                        REVIEW,
                        "value_not_in_sources",
                        cell,
                        other=sources[0].value,
                        split_divisor=str(divisor),
                        sources=[
                            {"id": s.id, "tag": s.tag, "value": str(s.value)}
                            for s in sources
                        ],
                    )
                )
        elif mode == "sum":
            total = sum((s.value for s in sources), Decimal(0))
            if not _close(cell.value, total):
                findings.append(
                    finding(
                        data,
                        "I6",
                        REVIEW,
                        "value_not_sum_of_sources",
                        cell,
                        other=total,
                        sources=[
                            {"id": s.id, "tag": s.tag, "value": str(s.value)}
                            for s in sources
                        ],
                    )
                )
        elif not any(_close(cell.value, s.value) for s in sources) and not (
            len(sources) > 1 and _explained_by_arithmetic(cell.value, sources)
        ):
            findings.append(
                finding(
                    data,
                    "I6",
                    REVIEW,
                    "value_not_in_sources",
                    cell,
                    other=sources[0].value,
                    sources=[
                        {"id": s.id, "tag": s.tag, "value": str(s.value)}
                        for s in sources
                    ],
                )
            )
    return findings
