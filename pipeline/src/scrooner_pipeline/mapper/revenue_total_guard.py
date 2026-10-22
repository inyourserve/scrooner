"""Revenue-total disagreement guard, both directions (RF-13 ``revenue.total_disagreement@1``).

Spec: data-team/strategy/team/NA-DEFINITIONS-AND-FOUNDER-SHEET-2026-10-22.md NA-8; evidence
data-team/37-REVENUE-TOTAL-RULE-2026-10-21.md. No such guard existed in code before this module.

Rule. For a non-bank company and a duration period, collect the undimensioned (companyfacts
carries no dimensions) USD facts of the revenue-family tags below from periodic filings. If two of
those tags have NO pair of values within 1% of each other, neither is proven to be the printed
total, so revenue for that company-period is hidden with reason
``revenue_total_undecidable`` -- whichever tag is currently displayed. Hidden are the
``revenue`` and ``revenue_sanity_resolved`` canonical rows of that period, so every consumer sees
a blank with a stored reason (``analytics.cell_blank_reason`` via the reason store), never a wrong
value. The structural pick (NA-9) is the thing that converts hides into values; see
``revenue_structure_total.py``. ``proven`` lets that pick exempt a period once it exists.

Honest cost (NA-8): in doc 37's sample 15 of 22 displayed periods were right, so this hides many
correct values. The dry run reports the breakdown (same filing vs across filings, displayed tag)
for the Verifier's hidden-correct count; this module cannot know which hidden values were right.

Placement. Called twice, flag-gated and idempotent: (1) right after ``resolve-facts``
(``scrooner-map apply-revenue-total-guard``) so the arithmetic fallbacks that read base ``revenue``
(gross profit, cost of revenue) never see a hidden period; (2) inside
``resolve_all_conflict_fills`` after the revenue fill and before the operating-income arithmetic,
because the conflict fill would otherwise re-insert the hidden periods.

Known limits (not handled, reported by the dry run as ``derived_rows_not_followed``): a derived Q4
value that subtracts from a hidden FY is not followed here (the Period Engineer's derived-fact
lineage, migration 0103, is the proper tool).

Rollback: flag off, then rerun the resolve stages for the manifest ciks (never hand SQL).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.cell_blank_reason import BlankReason, BlankReasonStore
from scrooner_pipeline.common.rule_before_image import PlannedChange
from scrooner_pipeline.common.rules_enabled import is_enabled

logger = structlog.get_logger()

RULE_ID = "revenue.total_disagreement@1"
REASON_DETAIL = "revenue_total_undecidable"
CANDIDATE_TAGS = (
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "RegulatedAndUnregulatedOperatingRevenue",
    "RevenuesNetOfInterestExpense",
)
TARGET_CONCEPTS = ("revenue", "revenue_sanity_resolved")
TOLERANCE = Decimal(
    "0.01"
)  # 1% of the larger value (core.fact keeps no decimals attribute)
# Domestic periodic forms (20-F/40-F are outside V1; one shared constant is AT-DE-09's job).
PERIODIC_FORMS = frozenset(
    {"10-K", "10-K/A", "10-KT", "10-KT/A", "10-Q", "10-Q/A", "10-QT"}
)
# Banks and thrifts have their own revenue template (doc 21 section 5: SIC 60xx-61xx).
BANK_SIC_PREFIXES = ("60", "61")


@dataclass(frozen=True)
class RevFact:
    tag: str
    value: Decimal
    filing_id: int


@dataclass(frozen=True)
class Disagreement:
    tag_a: str
    tag_b: str
    scope: str  # "same_filing" | "cross_filing"
    values_a: tuple[Decimal, ...]
    values_b: tuple[Decimal, ...]


def values_agree(a: Decimal, b: Decimal, tol: Decimal = TOLERANCE) -> bool:
    if a == b:
        return True
    larger = max(abs(a), abs(b))
    return larger != 0 and abs(a - b) <= tol * larger


def find_disagreement(
    facts: Iterable[RevFact], tol: Decimal = TOLERANCE
) -> Disagreement | None:
    """Two candidate tags that have no pair of values within ``tol``; None when all agree.

    Tag-level, not value-level, so a restated value filed later under one tag does not
    disagree with an older vintage of the same period (A={19629, 13804} agrees with B={13804})."""
    by_tag: dict[str, list[RevFact]] = defaultdict(list)
    for f in facts:
        by_tag[f.tag].append(f)
    tags = sorted(by_tag)
    for i, ta in enumerate(tags):
        for tb in tags[i + 1 :]:
            if any(
                values_agree(a.value, b.value, tol)
                for a in by_tag[ta]
                for b in by_tag[tb]
            ):
                continue
            filings_a = {a.filing_id for a in by_tag[ta]}
            filings_b = {b.filing_id for b in by_tag[tb]}
            scope = "same_filing" if filings_a & filings_b else "cross_filing"
            return Disagreement(
                ta,
                tb,
                scope,
                tuple(sorted({a.value for a in by_tag[ta]})),
                tuple(sorted({b.value for b in by_tag[tb]})),
            )
    return None


def is_bank(sic_code: str | None) -> bool:
    return bool(sic_code) and sic_code.startswith(BANK_SIC_PREFIXES)  # type: ignore[union-attr]


@dataclass
class GuardResult:
    hidden: list[tuple[int, int, str]] = field(
        default_factory=list
    )  # (company_id, period_id, concept)
    planned: list[PlannedChange] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)


def decide_company(
    *,
    company_id: int,
    cik: str,
    sic_code: str | None,
    facts_by_period: Mapping[int, list[RevFact]],
    period_end: Mapping[int, date],
    canonical: Mapping[tuple[int, str], Decimal],
    proven: Mapping[tuple[int, int], Decimal] | None = None,
) -> GuardResult:
    """Pure decision for one company. ``canonical`` maps (period_id, concept) to the stored value;
    ``proven`` maps (company_id, period_id) to a structurally proven total (NA-9), which exempts
    a canonical row only when it equals that total."""
    res = GuardResult()
    res.stats = {
        "same_filing": 0,
        "cross_filing": 0,
        "skipped_bank": 0,
        "exempt_proven": 0,
    }
    if is_bank(sic_code):
        res.stats["skipped_bank"] = 1
        return res
    for (period_id, concept), value in sorted(canonical.items()):
        facts = facts_by_period.get(period_id)
        if not facts:
            continue
        dis = find_disagreement(facts)
        if dis is None:
            continue
        pv = (proven or {}).get((company_id, period_id))
        if pv is not None and values_agree(pv, value):
            res.stats["exempt_proven"] += 1
            continue
        res.stats[dis.scope] += 1
        res.hidden.append((company_id, period_id, concept))
        res.planned.append(
            PlannedChange(
                rule_id=RULE_ID,
                cik=cik,
                company_id=company_id,
                data_point=concept,
                period_end=period_end.get(period_id),
                before=value,
                after=None,
                reason=f"guard_hidden:{REASON_DETAIL}:{dis.scope}:{dis.tag_a}<>{dis.tag_b}",
            )
        )
    return res


# ---------------------------------------------------------------- database layer

_FACT_SQL = """
select f.company_id, f.period_id, p.start_date, p.end_date, c.tag, f.value, f.filing_id
from core.fact f
join core.concept c on c.id = f.concept_id and c.taxonomy = 'us-gaap' and c.tag = any(%(tags)s)
join core.unit u on u.id = f.unit_id and u.unit_name = 'usd'
join core.period p on p.id = f.period_id and p.period_type = 'duration'
join core.filing fl on fl.id = f.filing_id and fl.form = any(%(forms)s)
where f.company_id = any(%(ids)s)
"""

_CANON_SQL = """
select cf.company_id, cf.period_id, cc.name, cf.value, cc.id
from analytics.canonical_fact cf
join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id and cc.name = any(%(names)s)
where cf.company_id = any(%(ids)s)
"""


def _chunks(seq: list[Any], n: int) -> Iterable[list[Any]]:
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def apply_revenue_total_guard(
    conn: psycopg.Connection,
    ciks: set[str] | None = None,
    *,
    dry_run: bool = False,
    reason_store: BlankReasonStore | None = None,
    run_id: str | None = None,
    environ: dict[str, str] | None = None,
    proven: Mapping[tuple[int, int], Decimal] | None = None,
    chunk: int = 100,
) -> dict[str, Any]:
    """No-op unless the rule is enabled or ``dry_run``. A dry run writes nothing at all and
    returns ``planned`` (the before-image). A live run REQUIRES a reason store: a guard may not
    hide a cell it cannot explain."""
    live = is_enabled(RULE_ID, environ) and not dry_run
    if not live and not dry_run:
        return {"skipped": "rule_off", "planned": []}
    if live and reason_store is None:
        raise RuntimeError(
            f"{RULE_ID}: a reason store is required to hide cells (migration 0100)"
        )

    with conn.cursor() as cur:
        if ciks:
            cur.execute(
                "select id, cik, sic_code from core.company where cik = any(%s)",
                (sorted(ciks),),
            )
        else:
            cur.execute("select id, cik, sic_code from core.company order by id")
        companies = cur.fetchall()
        cur.execute(
            "select id, name from analytics.canonical_concept where name = any(%s)",
            (list(TARGET_CONCEPTS),),
        )
        concept_ids = {name: cid for cid, name in cur.fetchall()}

    totals: dict[str, Any] = {
        "companies": 0,
        "companies_with_hides": 0,
        "cells_hidden": 0,
        "same_filing": 0,
        "cross_filing": 0,
        "skipped_bank": 0,
        "exempt_proven": 0,
        "dry_run": dry_run,
    }
    planned: list[PlannedChange] = []
    for batch in _chunks(companies, chunk):
        ids = [c[0] for c in batch]
        meta = {c[0]: (c[1], c[2]) for c in batch}
        facts: dict[int, dict[int, list[RevFact]]] = defaultdict(
            lambda: defaultdict(list)
        )
        period_info: dict[int, tuple[date, date]] = {}
        canon: dict[int, dict[tuple[int, str], Decimal]] = defaultdict(dict)
        with conn.cursor() as cur:
            cur.execute(
                _FACT_SQL,
                {
                    "tags": list(CANDIDATE_TAGS),
                    "forms": sorted(PERIODIC_FORMS),
                    "ids": ids,
                },
            )
            for (
                company_id,
                period_id,
                start,
                end,
                tag,
                value,
                filing_id,
            ) in cur.fetchall():
                facts[company_id][period_id].append(RevFact(tag, value, filing_id))
                period_info[period_id] = (start, end)
            cur.execute(_CANON_SQL, {"names": list(TARGET_CONCEPTS), "ids": ids})
            for company_id, period_id, name, value, _cid in cur.fetchall():
                canon[company_id][(period_id, name)] = value
        for company_id in ids:
            cik, sic = meta[company_id]
            totals["companies"] += 1
            res = decide_company(
                company_id=company_id,
                cik=cik,
                sic_code=sic,
                facts_by_period=facts.get(company_id, {}),
                period_end={p: se[1] for p, se in period_info.items()},
                canonical=canon.get(company_id, {}),
                proven=proven,
            )
            for k in ("same_filing", "cross_filing", "skipped_bank", "exempt_proven"):
                totals[k] += res.stats[k]
            if not res.hidden:
                continue
            totals["companies_with_hides"] += 1
            totals["cells_hidden"] += len(res.hidden)
            planned.extend(res.planned)
            if dry_run:
                continue
            assert reason_store is not None
            reasons = [
                BlankReason(
                    company_id=company_id,
                    data_point=concept,
                    period_grain=_grain(*period_info[period_id]),
                    period_start=period_info[period_id][0],
                    period_end=period_info[period_id][1],
                    basis="resolved",
                    rule_id=RULE_ID,
                    reason_code="guard_hidden",
                    detail={
                        "reason": REASON_DETAIL,
                        "evidence": pc.reason,
                        "before": str(pc.before),
                    },
                )
                for (_c, period_id, concept), pc in zip(
                    res.hidden, res.planned, strict=True
                )
            ]
            reason_store.replace(company_id, RULE_ID, run_id or "adhoc", reasons)
            period_ids = sorted({p for _c, p, _n in res.hidden})
            with conn.cursor() as cur:
                # exact scope: this company, the two target concepts, only the hidden periods
                cur.execute(
                    """delete from analytics.canonical_fact
                       where company_id = %s and canonical_concept_id = any(%s) and period_id = any(%s)""",
                    (
                        company_id,
                        [concept_ids[n] for n in TARGET_CONCEPTS if n in concept_ids],
                        period_ids,
                    ),
                )
            conn.commit()
    totals["planned"] = planned
    logger.info(
        "revenue_total_guard.done",
        **{k: v for k, v in totals.items() if k != "planned"},
    )
    return totals


def _grain(start: date, end: date) -> str:
    days = (end - start).days + 1
    if days >= 300:
        return "FY"
    return "Q" if days <= 105 else "YTD"
