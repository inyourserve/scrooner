"""Flag-gated retirement of two families of stored rows (Data Engineer,
2026-10-25; founder order after data-team/strategy/team/TRIAGE-I6-AND-TAX-RATE).

The Normalizer deriver gate (normalizer/derived.py, commit "Deriver gate")
only STOPS producing bad rows. Rows stored before it are still authoritative
and still displayed. This module plans (read-only) and, behind a rule flag
that defaults OFF, applies their retirement.

Family A  rule `retire.derived_ratio_cells@1`
    Derived (is_derived) facts on a ratio unit ('pure' or containing '/') for
    the tag EffectiveIncomeTaxRateContinuingOperations. A discrete Q4 rate was
    built as FY rate minus 9M rate; a rate is not additive, so the value is
    wrong by construction (FILING-CHECKED samples: PGR 10-K 0000080661-24-000007
    R3 stored -0.404 vs 20.6% filed; NRG 10-K 0001013871-22-000010 R3 stored
    -0.787 vs 28.2%; triage 2026-10-25). Cells: analytics.canonical_fact rows
    of effective_tax_rate_reported whose source_fact_ids contain such a fact.

Family B  rule `retire.proxy_form_cells@1`
    Facts filed on a proxy statement (DEF 14A family) that feed a displayed
    cell. A proxy prints pay-versus-performance figures rounded or in other
    scales (JPM DEF 14A 0000019617-26-000096 R2 rounded; CHE DEFR14A
    0001562762-26-000052 268,550 in thousands stored unscaled). Scope is the
    facts that actually feed a canonical cell; other proxy facts are only
    counted. 8-K sources are out of scope (a recast 8-K can carry complete
    statements, triage family 5 / certification `recast_8k_lineage`).

Per cell the plan chooses ONE outcome:
    replace_with_filed_fact  an authoritative, non-derived 10-K/10-Q-family
                             fact exists for the same company, period, tag
                             (family A: any tag mapped to the concept; family
                             B: the proxy fact's own tag and unit) with one
                             distinct value: the cell takes that fact.
    remove_with_reason       no such fact (or the filed copies disagree): the
                             cell is archived and removed; the reason code is
                             stored with the archive row and REASON_TEXT is
                             the wording a consumer shows.
    review_not_retired       the cell has other sources besides the retired
                             ones: nothing is changed, a human decides.
A retired FACT is demoted (is_authoritative -> false), never deleted, and its
before-image goes to analytics.fact_authority_retired (DDL draft below, not a
migration yet).

Rollback: restore(cur, run_id) = canonical_archive.restore_run (cells,
migration 0098 analytics.canonical_fact_retired) + re-promotion of the facts
logged in fact_authority_retired for that run.

NOTHING HERE RUNS ITSELF. The plan functions use a read-only session. The
apply function raises unless the rule is in mode ON (common/rule_flags), and
unless the plan digest equals the digest the reviewer saw. It never commits;
the caller owns the transaction. SQL uses {core}/{analytics} placeholders only
so the real-SQL tests can point at a scratch schema.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.common.derivation_policy import PERIODIC_FORMS_DOMESTIC
from scrooner_pipeline.mapper import canonical_archive

RULE_RATIO = "retire.derived_ratio_cells@1"
RULE_PROXY = "retire.proxy_form_cells@1"

TAX_RATE_TAG = "EffectiveIncomeTaxRateContinuingOperations"
TAX_RATE_CANONICAL = "effective_tax_rate_reported"
# Proxy-statement family. The dry-run lists the forms it actually met.
PROXY_FORMS = frozenset(
    {"DEF 14A", "DEFR14A", "DEFA14A", "DEFM14A", "DEFC14A", "PRE 14A", "PREM14A"}
)

ACT_REPLACE = "replace_with_filed_fact"
ACT_REMOVE = "remove_with_reason"
ACT_REVIEW = "review_not_retired"

REASON_TEXT = {
    "ratio_derived_no_filed_value": (
        "not filed for this period (a rate is not derived by subtraction)"
    ),
    "ratio_derived_filed_copies_disagree": (
        "filed copies of this rate disagree; not shown until resolved"
    ),
    "proxy_only_source": (
        "only a proxy statement carries this figure; not shown (use the 10-K or 10-Q)"
    ),
    "proxy_no_authoritative_periodic_copy": (
        "no authoritative 10-K/10-Q copy of this figure yet; not shown"
    ),
    "proxy_filed_copies_disagree": (
        "10-K/10-Q copies of this figure disagree; not shown until resolved"
    ),
}

# Draft only. Needs a migration number from doc 53 (next free is 0110) AND
# migration 0098 (canonical_fact_retired) committed first.
FACT_AUTHORITY_RETIRED_DDL_DRAFT = """
create table if not exists analytics.fact_authority_retired (
    id                     bigint generated always as identity primary key,
    fact_id                bigint not null,
    company_id             bigint not null,
    rule_id                text not null,
    reason_code            text not null,
    run_id                 text not null,
    prior_is_authoritative boolean not null,
    retired_at             timestamptz not null default now(),
    restored_at            timestamptz
);
create index if not exists idx_fact_authority_retired_run
    on analytics.fact_authority_retired (run_id);
create index if not exists idx_fact_authority_retired_fact
    on analytics.fact_authority_retired (fact_id);
"""

ROUNDING = Decimal("0.0001")  # copies within 0.01% are one value (matching-copies rule)


# ----------------------------------------------------------------- records
@dataclass(frozen=True)
class FactRow:
    fact_id: int
    company_id: int
    period_id: int
    concept_id: int
    tag: str
    unit: str
    fiscal_period: str | None
    start_date: date | None
    end_date: date | None
    value: Decimal
    is_authoritative: bool
    is_derived: bool
    form: str | None
    accession: str | None
    filing_date: date | None


@dataclass(frozen=True)
class CellPlan:
    family: str
    rule_id: str
    canonical_fact_id: int
    company_id: int
    canonical_concept_id: int
    concept: str
    period_id: int
    period_end: date | None
    stored_value: Decimal
    source_fact_ids: tuple[int, ...]
    retired_source_ids: tuple[int, ...]
    action: str
    reason_code: str | None = None
    replacement_fact_id: int | None = None
    replacement_value: Decimal | None = None
    replacement_form: str | None = None
    replacement_accession: str | None = None
    note: str = ""

    @property
    def reason_text(self) -> str | None:
        return REASON_TEXT.get(self.reason_code or "")


@dataclass
class Plan:
    family: str
    rule_id: str
    facts: list[FactRow] = field(
        default_factory=list
    )  # facts to demote (authoritative)
    cells: list[CellPlan] = field(default_factory=list)
    metric_value_ids: list[int] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)

    def digest(self) -> str:
        """Stable fingerprint of exactly what apply() would do."""
        payload = {
            "rule": self.rule_id,
            "facts": sorted(f.fact_id for f in self.facts),
            "cells": sorted(
                (
                    c.canonical_fact_id,
                    c.action,
                    c.reason_code,
                    c.replacement_fact_id,
                    str(c.replacement_value),
                    str(c.stored_value),
                    list(c.source_fact_ids),
                )
                for c in self.cells
            ),
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()


# --------------------------------------------------------------------- SQL
FACT_SELECT = """
select f.id, f.company_id, f.period_id, f.concept_id, c.tag, u.unit_name, p.fiscal_period,
       p.start_date, p.end_date, f.value, f.is_authoritative, f.is_derived,
       fl.form, fl.accession_number, fl.filing_date
from {core}.fact f
join {core}.concept c on c.id = f.concept_id
join {core}.unit u on u.id = f.unit_id
join {core}.period p on p.id = f.period_id
left join {core}.filing fl on fl.id = f.filing_id
"""

RATIO_FACTS_SQL = (
    FACT_SELECT
    + """
where f.company_id = any(%(ids)s) and f.is_derived
  and f.concept_id = any(%(cids)s) and f.unit_id = any(%(uids)s)
"""
)

PROXY_FACTS_SQL = (
    FACT_SELECT
    + """
where f.filing_id in (select fl2.id from {core}.filing fl2
                      where fl2.company_id = any(%(ids)s) and fl2.form = any(%(forms)s))
"""
)

FILED_COPIES_SQL = (
    FACT_SELECT
    + """
where f.company_id = any(%(ids)s) and f.concept_id = any(%(cids)s)
  and f.period_id = any(%(pids)s) and f.is_authoritative and not f.is_derived
  and fl.form = any(%(forms)s)
"""
)

NONAUTH_PERIODIC_COUNT_SQL = """
select f.company_id, f.concept_id, f.period_id, count(*)
from {core}.fact f join {core}.filing fl on fl.id = f.filing_id
where f.company_id = any(%(ids)s) and f.concept_id = any(%(cids)s)
  and f.period_id = any(%(pids)s) and not f.is_authoritative and not f.is_derived
  and fl.form = any(%(forms)s)
group by 1, 2, 3
"""

CELLS_SQL = """
select cf.id, cf.company_id, cf.canonical_concept_id, cc.name, cf.period_id, p.end_date,
       cf.value, cf.source_fact_ids
from {analytics}.canonical_fact cf
join {analytics}.canonical_concept cc on cc.id = cf.canonical_concept_id
join {core}.period p on p.id = cf.period_id
where cf.company_id = any(%(ids)s)
  and cf.canonical_concept_id = any(%(ccids)s)
  and cf.source_fact_ids && %(fids)s::bigint[]
"""

CANONICAL_FOR_CONCEPTS_SQL = """
select distinct cc.id
from {analytics}.concept_mapping cm
join {analytics}.canonical_concept base on base.id = cm.canonical_concept_id
join {analytics}.canonical_concept cc on cc.name = base.name or cc.name = base.name || '_resolved'
where cm.concept_id = any(%(cids)s)
"""

MAPPED_CONCEPTS_SQL = """
select cm.concept_id, cm.priority
from {analytics}.concept_mapping cm
join {analytics}.canonical_concept cc on cc.id = cm.canonical_concept_id
where cc.name = %(name)s and cm.confidence <> 'rejected'
"""

METRIC_SQL = """
select mv.id from {analytics}.metric_value mv
where mv.company_id = any(%(ids)s) and mv.source_fact_ids && %(fids)s::bigint[]
"""


def _q(sql: str, core: str = "core", analytics: str = "analytics") -> str:
    return sql.format(core=core, analytics=analytics)


def _fact(row: Sequence[Any]) -> FactRow:
    return FactRow(
        fact_id=row[0],
        company_id=row[1],
        period_id=row[2],
        concept_id=row[3],
        tag=row[4],
        unit=row[5],
        fiscal_period=row[6],
        start_date=row[7],
        end_date=row[8],
        value=Decimal(row[9]),
        is_authoritative=bool(row[10]),
        is_derived=bool(row[11]),
        form=row[12],
        accession=row[13],
        filing_date=row[14],
    )


# ------------------------------------------------------------- shared steps
def _cells_for(
    cur,
    ids: list[int],
    facts: Sequence[FactRow],
    core: str,
    analytics: str,
) -> list[tuple]:
    if not facts:
        return []
    cids = sorted({f.concept_id for f in facts})
    cur.execute(_q(CANONICAL_FOR_CONCEPTS_SQL, core, analytics), {"cids": cids})
    ccids = [r[0] for r in cur.fetchall()]
    if not ccids:
        return []
    cur.execute(
        _q(CELLS_SQL, core, analytics),
        {"ids": ids, "ccids": ccids, "fids": [f.fact_id for f in facts]},
    )
    return cur.fetchall()


def _filed_copies(
    cur, ids: list[int], cids: list[int], pids: list[int], core: str
) -> dict[tuple[int, int, int], list[FactRow]]:
    out: dict[tuple[int, int, int], list[FactRow]] = defaultdict(list)
    if not cids or not pids:
        return out
    cur.execute(
        _q(FILED_COPIES_SQL, core),
        {
            "ids": ids,
            "cids": cids,
            "pids": pids,
            "forms": sorted(PERIODIC_FORMS_DOMESTIC),
        },
    )
    for row in cur.fetchall():
        f = _fact(row)
        out[(f.company_id, f.concept_id, f.period_id)].append(f)
    return out


def _nonauth_periodic(
    cur, ids: list[int], cids: list[int], pids: list[int], core: str
) -> dict[tuple[int, int, int], int]:
    if not cids or not pids:
        return {}
    cur.execute(
        _q(NONAUTH_PERIODIC_COUNT_SQL, core),
        {
            "ids": ids,
            "cids": cids,
            "pids": pids,
            "forms": sorted(PERIODIC_FORMS_DOMESTIC),
        },
    )
    return {(r[0], r[1], r[2]): r[3] for r in cur.fetchall()}


def _pick_one(copies: Sequence[FactRow]) -> FactRow | None:
    """The single filed value, or None when the copies disagree. Copies equal
    within 0.01% are one value; the most recently filed one is the witness."""
    if not copies:
        return None
    ordered = sorted(
        copies, key=lambda f: (f.filing_date or date.min, f.fact_id), reverse=True
    )
    top = ordered[0]
    for other in ordered[1:]:
        base = max(abs(top.value), abs(other.value))
        if base and abs(top.value - other.value) / base > ROUNDING:
            return None
    return top


def _gap_bucket(stored: Decimal, filed: Decimal) -> str:
    if filed == 0:
        return "filed_zero"
    ratio = abs(stored / filed) if stored else Decimal(0)
    if ratio and any(
        abs(ratio / Decimal(s) - 1) < Decimal("0.01")
        or abs(ratio * Decimal(s) - 1) < Decimal("0.01")
        for s in (1000, 1_000_000)
    ):
        return "scale_1e3_or_1e6"
    gap = abs(stored - filed) / abs(filed)
    if gap < Decimal("0.001"):
        return "under_0.1pct"
    if gap < Decimal("0.01"):
        return "0.1_to_1pct"
    if gap < Decimal("0.10"):
        return "1_to_10pct"
    return "10pct_or_more"


# ------------------------------------------------------------------ family A
def plan_ratio_chunk(
    cur,
    ids: list[int],
    *,
    cids: list[int],
    uids: list[int],
    mapped_priority: Mapping[int, int],
    core: str = "core",
    analytics: str = "analytics",
) -> Plan:
    plan = Plan("A_ratio_derived", RULE_RATIO)
    cur.execute(_q(RATIO_FACTS_SQL, core), {"ids": ids, "cids": cids, "uids": uids})
    facts = [_fact(r) for r in cur.fetchall()]
    by_id = {f.fact_id: f for f in facts}
    plan.facts = [f for f in facts if f.is_authoritative]
    plan.info["derived_ratio_facts_total"] = len(facts)
    plan.info["derived_ratio_facts_authoritative"] = len(plan.facts)
    cells = _cells_for(cur, ids, facts, core, analytics)
    pids = sorted({c[4] for c in cells})
    copies = _filed_copies(cur, ids, sorted(mapped_priority), pids, core)
    nonauth = _nonauth_periodic(cur, ids, sorted(mapped_priority), pids, core)
    for cf_id, company, ccid, cname, pid, pend, value, sources in cells:
        sources_t = tuple(sources)
        retired = tuple(s for s in sources_t if s in by_id)
        base = dict(
            family=plan.family,
            rule_id=RULE_RATIO,
            canonical_fact_id=cf_id,
            company_id=company,
            canonical_concept_id=ccid,
            concept=cname,
            period_id=pid,
            period_end=pend,
            stored_value=Decimal(value),
            source_fact_ids=sources_t,
            retired_source_ids=retired,
        )
        if len(retired) != len(sources_t):
            plan.cells.append(
                CellPlan(**base, action=ACT_REVIEW, note="has other sources")
            )
            continue
        # candidate filed values, best mapping priority first
        by_prio: dict[int, list[FactRow]] = defaultdict(list)
        for cid, prio in mapped_priority.items():
            for f in copies.get((company, cid, pid), []):
                by_prio[prio].append(f)
        chosen: FactRow | None = None
        disagree = False
        if by_prio:
            # best (lowest) mapping priority decides; its copies must agree
            chosen = _pick_one(by_prio[min(by_prio)])
            disagree = chosen is None
        if chosen is not None:
            plan.cells.append(
                CellPlan(
                    **base,
                    action=ACT_REPLACE,
                    replacement_fact_id=chosen.fact_id,
                    replacement_value=chosen.value,
                    replacement_form=chosen.form,
                    replacement_accession=chosen.accession,
                )
            )
        else:
            plan.cells.append(
                CellPlan(
                    **base,
                    action=ACT_REMOVE,
                    reason_code="ratio_derived_filed_copies_disagree"
                    if disagree
                    else "ratio_derived_no_filed_value",
                    note=f"nonauth_periodic_copies={sum(v for (c, _, p), v in nonauth.items() if c == company and p == pid)}",
                )
            )
    _metrics(cur, ids, plan, core, analytics)
    return plan


# ------------------------------------------------------------------ family B
def plan_proxy_chunk(
    cur,
    ids: list[int],
    *,
    core: str = "core",
    analytics: str = "analytics",
) -> Plan:
    plan = Plan("B_proxy_form", RULE_PROXY)
    cur.execute(_q(PROXY_FACTS_SQL, core), {"ids": ids, "forms": sorted(PROXY_FORMS)})
    proxy = [_fact(r) for r in cur.fetchall()]
    by_id = {f.fact_id: f for f in proxy}
    plan.info["proxy_facts_total"] = len(proxy)
    plan.info["proxy_facts_authoritative"] = sum(f.is_authoritative for f in proxy)
    forms: dict[str, int] = defaultdict(int)
    for f in proxy:
        forms[f.form or "?"] += 1
    plan.info["proxy_forms_met"] = dict(forms)
    cells = _cells_for(cur, ids, proxy, core, analytics)
    fed = {s for c in cells for s in c[7] if s in by_id}
    plan.facts = [by_id[i] for i in sorted(fed) if by_id[i].is_authoritative]
    plan.info["proxy_facts_feeding_cells"] = len(fed)
    plan.info["proxy_facts_authoritative_not_displayed"] = sum(
        1 for f in proxy if f.is_authoritative and f.fact_id not in fed
    )
    cids = sorted({by_id[i].concept_id for i in fed})
    pids = sorted({c[4] for c in cells})
    copies = _filed_copies(cur, ids, cids, pids, core)
    nonauth = _nonauth_periodic(cur, ids, cids, pids, core)
    for cf_id, company, ccid, cname, pid, pend, value, sources in cells:
        sources_t = tuple(sources)
        retired = tuple(s for s in sources_t if s in by_id)
        if not retired:
            continue  # cell matched on a non-proxy source of the overlap only
        base = dict(
            family=plan.family,
            rule_id=RULE_PROXY,
            canonical_fact_id=cf_id,
            company_id=company,
            canonical_concept_id=ccid,
            concept=cname,
            period_id=pid,
            period_end=pend,
            stored_value=Decimal(value),
            source_fact_ids=sources_t,
            retired_source_ids=retired,
        )
        if len(retired) != len(sources_t):
            plan.cells.append(
                CellPlan(**base, action=ACT_REVIEW, note="has other sources")
            )
            continue
        src = by_id[retired[0]]
        cand = [
            f
            for f in copies.get((company, src.concept_id, pid), [])
            if f.unit == src.unit
        ]
        pick = _pick_one(cand)
        if pick is not None:
            plan.cells.append(
                CellPlan(
                    **base,
                    action=ACT_REPLACE,
                    replacement_fact_id=pick.fact_id,
                    replacement_value=pick.value,
                    replacement_form=pick.form,
                    replacement_accession=pick.accession,
                    note=_gap_bucket(Decimal(value), pick.value),
                )
            )
        else:
            n_non = nonauth.get((company, src.concept_id, pid), 0)
            if cand:
                code = "proxy_filed_copies_disagree"
            elif n_non:
                code = "proxy_no_authoritative_periodic_copy"
            else:
                code = "proxy_only_source"
            plan.cells.append(
                CellPlan(
                    **base,
                    action=ACT_REMOVE,
                    reason_code=code,
                    note=f"nonauth_periodic_copies={n_non}",
                )
            )
    _metrics(cur, ids, plan, core, analytics)
    return plan


def _metrics(cur, ids: list[int], plan: Plan, core: str, analytics: str) -> None:
    """metric_value rows built from a retired fact (recomputed afterwards, not
    retired). Only companies that have a planned cell are scanned, in small
    batches; a batch that hits the statement timeout is split down to single
    companies, and a company that still times out is NAMED in
    plan.info['metric_scan_timeouts'] (a visible gap, never a silent zero)."""
    import psycopg

    by_company: dict[int, set[int]] = defaultdict(set)
    for c in plan.cells:
        by_company[c.company_id].update(c.retired_source_ids)
    sql = _q(METRIC_SQL, core, analytics)

    def scan(companies: list[int]) -> None:
        fids = sorted({f for c in companies for f in by_company[c]})
        try:
            cur.execute(sql, {"ids": companies, "fids": fids})
        except psycopg.errors.QueryCanceled:
            if len(companies) == 1:
                plan.info.setdefault("metric_scan_timeouts", []).append(companies[0])
                return
            mid = len(companies) // 2
            scan(companies[:mid])
            scan(companies[mid:])
            return
        plan.metric_value_ids += [r[0] for r in cur.fetchall()]

    todo = sorted(by_company)
    for k in range(0, len(todo), 10):
        scan(todo[k : k + 10])


def merge(plans: Sequence[Plan], family: str, rule_id: str) -> Plan:
    out = Plan(family, rule_id)
    for p in plans:
        out.facts += p.facts
        out.cells += p.cells
        out.metric_value_ids += p.metric_value_ids
        for k, v in p.info.items():
            if isinstance(v, list):
                out.info.setdefault(k, []).extend(v)
            elif isinstance(v, dict):
                d = out.info.setdefault(k, {})
                for kk, vv in v.items():
                    d[kk] = d.get(kk, 0) + vv
            else:
                out.info[k] = out.info.get(k, 0) + v
    return out


def summarize(plan: Plan, cohort: set[int] | None = None) -> dict[str, Any]:
    """Counts for the review: per action, concept, reason, gap bucket, cohort."""

    def block(cells: Sequence[CellPlan]) -> dict[str, Any]:
        gaps: dict[str, int] = defaultdict(int)
        for c in cells:
            if c.action == ACT_REPLACE and c.family == "B_proxy_form":
                gaps[c.note] += 1
        by = lambda key: _count(cells, key)  # noqa: E731
        return {
            "cells": len(cells),
            "companies": len({c.company_id for c in cells}),
            "by_action": by(lambda c: c.action),
            "by_concept": by(lambda c: c.concept),
            "by_reason": by(lambda c: c.reason_code or "-"),
            "by_replacement_form": by(lambda c: c.replacement_form or "-"),
            "replace_gap_vs_filed_value": dict(gaps),
        }

    out: dict[str, Any] = {
        "family": plan.family,
        "rule_id": plan.rule_id,
        "digest": plan.digest(),
        "facts_to_demote": len(plan.facts),
        "facts_to_demote_companies": len({f.company_id for f in plan.facts}),
        "metric_values_to_recompute": len(set(plan.metric_value_ids)),
        "info": plan.info,
        "all_companies": block(plan.cells),
    }
    if cohort is not None:
        out["cohort"] = block([c for c in plan.cells if c.company_id in cohort])
        out["cohort_facts_to_demote"] = sum(
            1 for f in plan.facts if f.company_id in cohort
        )
    return out


def _count(cells: Sequence[CellPlan], key) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for c in cells:
        out[key(c)] += 1
    return dict(sorted(out.items()))


# --------------------------------------------------------------------- apply
class RuleNotEnabled(RuntimeError):
    pass


class PlanChanged(RuntimeError):
    pass


def apply_plan(
    cur,
    plan: Plan,
    *,
    run_id: str,
    expected_digest: str,
    environ: Mapping[str, str] | None = None,
    core: str = "core",
    analytics: str = "analytics",
) -> dict[str, int]:
    """Archive-then-write inside the caller's transaction. NEVER commits.
    Refuses unless the rule is in mode ON and the plan is exactly the one the
    reviewer saw. Not run by anything in the repository."""
    if rule_flags.rule_mode(plan.rule_id, environ) != rule_flags.ON:
        raise RuleNotEnabled(f"{plan.rule_id} is not in mode on; nothing applied")
    if plan.digest() != expected_digest:
        raise PlanChanged("plan digest differs from the reviewed digest")
    # stale guard: every cell must still hold the value and sources that were reviewed
    ids = [c.canonical_fact_id for c in plan.cells if c.action != ACT_REVIEW]
    if ids:
        cur.execute(
            f"select id, value, source_fact_ids from {analytics}.canonical_fact"
            " where id = any(%s::bigint[])",
            (ids,),
        )
        now = {r[0]: (Decimal(r[1]), tuple(r[2])) for r in cur.fetchall()}
        for c in plan.cells:
            if c.action == ACT_REVIEW:
                continue
            if now.get(c.canonical_fact_id) != (c.stored_value, c.source_fact_ids):
                raise PlanChanged(
                    f"canonical_fact {c.canonical_fact_id} changed since review"
                )
    stats = {
        "facts_demoted": 0,
        "cells_replaced": 0,
        "cells_removed": 0,
        "cells_inserted": 0,
    }
    # 1. fact before-image, then demote (never delete)
    fact_ids = sorted({f.fact_id for f in plan.facts})
    if fact_ids:
        cur.execute(
            f"""
            with prior as (
                select id, company_id, is_authoritative from {core}.fact
                where id = any(%(ids)s::bigint[]) and is_authoritative
                for update
            ), logged as (
                insert into {analytics}.fact_authority_retired
                    (fact_id, company_id, rule_id, reason_code, run_id, prior_is_authoritative)
                select id, company_id, %(rule)s, %(reason)s, %(run)s, is_authoritative from prior
                returning fact_id
            )
            update {core}.fact f set is_authoritative = false
            from logged where f.id = logged.fact_id
            """,
            {
                "ids": fact_ids,
                "rule": plan.rule_id,
                "reason": plan.family,
                "run": run_id,
            },
        )
        stats["facts_demoted"] = cur.rowcount
    # 2. cells
    replaces = [c for c in plan.cells if c.action == ACT_REPLACE]
    removes = [c for c in plan.cells if c.action == ACT_REMOVE]
    if replaces:
        s = canonical_archive.replace_rows(
            cur,
            [
                canonical_archive.CanonicalRow(
                    c.company_id,
                    c.canonical_concept_id,
                    c.period_id,
                    c.replacement_value,  # type: ignore[arg-type]
                    (c.replacement_fact_id,),  # type: ignore[arg-type]
                )
                for c in replaces
            ],
            reason_code=f"{plan.rule_id}:replace",
            run_id=run_id,
            schema=analytics,
        )
        stats["cells_replaced"] = s["replaced"]
        stats["cells_inserted"] = s["inserted"]
    by_reason: dict[str, list[int]] = defaultdict(list)
    for c in removes:
        by_reason[c.reason_code or "unspecified"].append(c.canonical_fact_id)
    for code, cids in by_reason.items():
        stats["cells_removed"] += canonical_archive.archive_and_remove(
            cur,
            cids,
            reason_code=f"{plan.rule_id}:{code}",
            run_id=run_id,
            schema=analytics,
        )
    return stats


def restore(
    cur, run_id: str, *, core: str = "core", analytics: str = "analytics"
) -> dict[str, int]:
    """Undo one apply: cells from canonical_fact_retired, facts from
    fact_authority_retired. Restoring twice is a no-op."""
    cells = canonical_archive.restore_run(cur, run_id, schema=analytics)
    cur.execute(
        f"""
        with back as (
            update {analytics}.fact_authority_retired r set restored_at = now()
            where r.run_id = %(run)s and r.restored_at is null
            returning r.fact_id, r.prior_is_authoritative
        )
        update {core}.fact f set is_authoritative = back.prior_is_authoritative
        from back where f.id = back.fact_id
        """,
        {"run": run_id},
    )
    return {"cell_archive_rows_restored": cells, "facts_restored": cur.rowcount}


# ----------------------------------------------------------- dry-run driver
def _cohort(path: Path) -> set[int]:
    with path.open() as fh:
        return {int(r["company_id"]) for r in csv.DictReader(fh) if not r["excluded"]}


def run_dry_run(
    conn,
    out_dir: Path,
    *,
    families: Sequence[str] = ("A", "B"),
    cohort: set[int] | None = None,
    company_ids: list[int] | None = None,
    chunk: int = 100,
    statement_timeout: str = "60s",
    log=lambda m: print(m, flush=True),
) -> dict[str, Any]:
    """READ-ONLY. One connection. Writes CSV/JSON files into out_dir only."""
    cur = conn.cursor()
    cur.execute(
        "select set_config('statement_timeout', %s, false)", (statement_timeout,)
    )
    cur.execute("set default_transaction_read_only = on")
    cur.execute("show default_transaction_read_only")
    assert cur.fetchone()[0] == "on"
    if company_ids is None:
        cur.execute("select id from core.company order by id")
        company_ids = [r[0] for r in cur.fetchall()]
    cur.execute("select id from core.concept where tag = %s", (TAX_RATE_TAG,))
    cids = [r[0] for r in cur.fetchall()]
    cur.execute(
        "select id from core.unit where unit_name = 'pure' or unit_name like '%%/%%'"
    )
    uids = [r[0] for r in cur.fetchall()]
    cur.execute(_q(MAPPED_CONCEPTS_SQL), {"name": TAX_RATE_CANONICAL})
    mapped = {r[0]: r[1] for r in cur.fetchall()}
    out_dir.mkdir(parents=True, exist_ok=True)
    plans: dict[str, list[Plan]] = {"A": [], "B": []}
    t0 = time.time()
    for i in range(0, len(company_ids), chunk):
        ids = company_ids[i : i + chunk]
        if "A" in families:
            plans["A"].append(
                plan_ratio_chunk(cur, ids, cids=cids, uids=uids, mapped_priority=mapped)
            )
        if "B" in families:
            plans["B"].append(plan_proxy_chunk(cur, ids))
        log(
            f"companies {min(i + chunk, len(company_ids))}/{len(company_ids)} {time.time() - t0:.0f}s"
        )
    summary: dict[str, Any] = {"companies_scanned": len(company_ids)}
    for fam, family_name, rule in (
        ("A", "A_ratio_derived", RULE_RATIO),
        ("B", "B_proxy_form", RULE_PROXY),
    ):
        if fam not in families:
            continue
        plan = merge(plans[fam], family_name, rule)
        summary[family_name] = summarize(plan, cohort)
        _write_csvs(out_dir, plan)
    (out_dir / "retirement_dryrun_summary.json").write_text(
        json.dumps(summary, indent=2, default=str)
    )
    return summary


def _write_csvs(out_dir: Path, plan: Plan) -> None:
    tag = plan.family
    with (out_dir / f"{tag}_facts_to_demote.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "fact_id",
                "company_id",
                "tag",
                "unit",
                "fiscal_period",
                "start_date",
                "end_date",
                "value",
                "form",
                "accession",
            ]
        )
        for f in sorted(plan.facts, key=lambda f: f.fact_id):
            w.writerow(
                [
                    f.fact_id,
                    f.company_id,
                    f.tag,
                    f.unit,
                    f.fiscal_period,
                    f.start_date,
                    f.end_date,
                    f.value,
                    f.form,
                    f.accession,
                ]
            )
    with (out_dir / f"{tag}_cells.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        cols = list(CellPlan.__dataclass_fields__)
        w.writerow(cols + ["reason_text"])
        for c in sorted(plan.cells, key=lambda c: c.canonical_fact_id):
            d = asdict(c)
            d["source_fact_ids"] = ";".join(map(str, c.source_fact_ids))
            d["retired_source_ids"] = ";".join(map(str, c.retired_source_ids))
            w.writerow([d[k] for k in cols] + [c.reason_text])
    with (out_dir / f"{tag}_metric_values_to_recompute.csv").open(
        "w", newline=""
    ) as fh:
        w = csv.writer(fh)
        w.writerow(["metric_value_id"])
        for i in sorted(set(plan.metric_value_ids)):
            w.writerow([i])


def main(argv: list[str] | None = None) -> int:
    import psycopg

    from scrooner_pipeline.common.config import settings

    ap = argparse.ArgumentParser(
        description="READ-ONLY retirement dry-run (writes files only)"
    )
    ap.add_argument("out_dir")
    ap.add_argument("--family", choices=["A", "B", "both"], default="both")
    ap.add_argument(
        "--cohort-csv", default=None, help="doc/data-moat/team/top1000/shards.csv"
    )
    ap.add_argument("--ciks", default=None)
    ap.add_argument("--chunk", type=int, default=100)
    ap.add_argument("--statement-timeout", default="60s")
    args = ap.parse_args(argv)
    fams = ("A", "B") if args.family == "both" else (args.family,)
    cohort = _cohort(Path(args.cohort_csv)) if args.cohort_csv else None
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        ids = None
        if args.ciks:
            cur = conn.cursor()
            cur.execute(
                "select id from core.company where cik = any(%s) order by id",
                ([c.strip().zfill(10) for c in args.ciks.split(",")],),
            )
            ids = [r[0] for r in cur.fetchall()]
        summary = run_dry_run(
            conn,
            Path(args.out_dir),
            families=fams,
            cohort=cohort,
            company_ids=ids,
            chunk=args.chunk,
            statement_timeout=args.statement_timeout,
        )
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
