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
import re
import json
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field, replace
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.common.derivation_policy import PERIODIC_FORMS_DOMESTIC
from scrooner_pipeline.mapper import canonical_archive

RULE_RATIO = "retire.derived_ratio_cells@1"
RULE_PROXY = "retire.proxy_form_cells@1"

# Net income including the noncontrolling interest. The net_income concept is
# attributable to the parent: these tags are never preferred, and are used only
# when the company/period has no nonzero NCI income fact (FCX FY2021 5,365M vs
# 4,306M attributable; THC FY2023 1,311M vs 611M; CAT, TXRH, PCG).
NCI_INCLUSIVE_TAGS = frozenset(
    {
        "ProfitLoss",
        "IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest",
    }
)
NCI_INCOME_TAGS = (
    "NetIncomeLossAttributableToNoncontrollingInterest",
    "IncomeLossFromContinuingOperationsAttributableToNoncontrollingEntity",
    "MinorityInterestInNetIncomeLossOfConsolidatedEntities",
)

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
    "proxy_nci_inclusive_only": (
        "only a net income figure that includes noncontrolling interests is filed; not shown"
    ),
    "derived_inputs_disagree": (
        "the filed copies of the year or earlier quarters disagree (restated); not shown"
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
    replacement_was_authoritative: bool | None = None
    replacement_source_ids: tuple[
        int, ...
    ] = ()  # a re-derived quarter: the filed inputs
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
    promote_fact_ids: list[int] = field(
        default_factory=list
    )  # non-authoritative copies to re-promote
    nci_pending: dict[int, FactRow] = field(
        default_factory=dict
    )  # cell id -> NCI-inclusive pick awaiting the face check
    metric_value_ids: list[int] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)

    def digest(self) -> str:
        """Stable fingerprint of exactly what apply() would do."""
        payload = {
            "rule": self.rule_id,
            "facts": sorted(f.fact_id for f in self.facts),
            "promote": sorted(set(self.promote_fact_ids)),
            "cells": sorted(
                (
                    c.canonical_fact_id,
                    c.action,
                    list(c.replacement_source_ids),
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

# Family B candidates: ANY periodic-form fact (authoritative or not, derived or
# not). A proxy fact that conflicts with the 10-K copies makes dedupe mark those
# copies non-authoritative (CHE FY2021, JPM FY2021, GIS FY2024); once the proxy
# fact is demoted they agree, so they are valid candidates.
PERIODIC_COPIES_SQL = (
    FACT_SELECT
    + """
where f.company_id = any(%(ids)s) and f.concept_id = any(%(cids)s)
  and f.period_id = any(%(pids)s) and fl.form = any(%(forms)s)
"""
)

PERIOD_SQL = (
    "select id, start_date, end_date from {core}.period where id = any(%(pids)s)"
)

INPUT_FACTS_SQL = (
    FACT_SELECT
    + """
where f.company_id = any(%(ids)s) and f.concept_id = any(%(cids)s)
  and fl.form = any(%(forms)s) and not f.is_derived
  and p.end_date between %(lo)s and %(hi)s
"""
)

NCI_FACTS_SQL = """
select distinct f.company_id, f.period_id
from {core}.fact f join {core}.concept c on c.id = f.concept_id
where f.company_id = any(%(ids)s) and f.period_id = any(%(pids)s)
  and c.tag = any(%(tags)s) and f.value <> 0
"""

CELL_TAGS_SQL = """
select cc.id, cm.concept_id, cm.priority
from {analytics}.canonical_concept cc
join {analytics}.canonical_concept base
  on base.name = cc.name or base.name || '_resolved' = cc.name
join {analytics}.concept_mapping cm on cm.canonical_concept_id = base.id
where cc.id = any(%(ccids)s) and cm.confidence <> 'rejected'
"""

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


def _sig_digits(v: Decimal) -> int:
    return len(v.normalize().as_tuple().digits)


def _rounded_copy_of(rounded: Decimal, precise: Decimal) -> bool:
    """True when `rounded` is `precise` rounded to the coarseness `rounded` itself
    shows. (A) its own trailing zeros: 3,900,000,000 rounds -3,909,000,000 to
    1e8 (ST); needs 2+ significant digits so 1.0M is never "a rounding" of 1.1M.
    (B) a filing scale (thousands, millions, billions) with 2+ whole digits in it:
    100,000,000 for 100,293,000. A restatement inside half a rounding step is
    indistinguishable from rounding here; the Verifier samples these."""
    exp = rounded.normalize().as_tuple().exponent
    if (
        isinstance(exp, int)
        and exp > 0
        and _sig_digits(rounded) >= 2
        and abs(precise - rounded) <= Decimal(10) ** exp / 2
    ):
        return True
    for scale in (Decimal(10) ** 9, Decimal(10) ** 6, Decimal(10) ** 3):
        if rounded % scale == 0:
            units = abs(rounded) / scale
            return len(str(int(units))) >= 2 and abs(precise - rounded) <= scale / 2
    return False


def _pick_precise(copies: Sequence[FactRow]) -> FactRow | None:
    """Like _pick_one, but the witness is the most PRECISE copy (most significant
    digits; a later rounded restatement of the same figure never replaces the
    precise one: SM, ANET), then the most recently filed. None when the copies
    disagree beyond rounding (vintage or tag conflict: the cell is hidden)."""
    if not copies:
        return None
    top = max(
        copies,
        key=lambda f: (_sig_digits(f.value), f.filing_date or date.min, f.fact_id),
    )
    for other in copies:
        base = max(abs(top.value), abs(other.value))
        if not base or abs(top.value - other.value) / base <= ROUNDING:
            continue
        # a copy rounded to a filing scale (thousands, millions, billions) is the same
        # figure when the precise one rounds to it (SM 770,000,000 vs 770,293,000;
        # WDAY 29M vs 29.373M). The rounded copy needs at least 2 whole digits in its
        # scale (1.0M vs 1.1M is a restatement, not rounding).
        if _rounded_copy_of(other.value, top.value):
            continue
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
    pids = sorted({c[4] for c in cells})
    ccids = sorted({c[2] for c in cells})
    tags_by_cc: dict[int, dict[int, int]] = defaultdict(
        dict
    )  # canonical id -> concept -> priority
    if ccids:
        cur.execute(_q(CELL_TAGS_SQL, core, analytics), {"ccids": ccids})
        for ccid_, cid_, prio_ in cur.fetchall():
            tags_by_cc[ccid_][cid_] = prio_
    all_cids = sorted(
        {by_id[i].concept_id for i in fed} | {c for m in tags_by_cc.values() for c in m}
    )
    copies: dict[tuple[int, int, int], list[FactRow]] = defaultdict(list)
    if all_cids and pids:
        cur.execute(
            _q(PERIODIC_COPIES_SQL, core),
            {
                "ids": ids,
                "cids": all_cids,
                "pids": pids,
                "forms": sorted(PERIODIC_FORMS_DOMESTIC),
            },
        )
        for row in cur.fetchall():
            f = _fact(row)
            copies[(f.company_id, f.concept_id, f.period_id)].append(f)
    nci_nonzero: set[tuple[int, int]] = set()
    if pids:
        cur.execute(
            _q(NCI_FACTS_SQL, core),
            {"ids": ids, "pids": pids, "tags": list(NCI_INCOME_TAGS)},
        )
        nci_nonzero = {(r[0], r[1]) for r in cur.fetchall()}
    picked: dict[int, FactRow] = {}
    meta: dict[
        int, tuple[FactRow, int, int]
    ] = {}  # cell -> (source fact, canonical id, company)
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
        # every tag mapped to the cell's concept, same unit; the best (lowest)
        # priority tag that has any periodic copy decides (MA: ProfitLoss)
        mapped = dict(tags_by_cc.get(ccid, {}))
        mapped.setdefault(src.concept_id, 99)
        by_prio: dict[int, list[FactRow]] = defaultdict(list)
        inclusive: list[FactRow] = []
        for cid_, prio_ in mapped.items():
            for f in copies.get((company, cid_, pid), []):
                if f.unit != src.unit:
                    continue
                if f.tag in NCI_INCLUSIVE_TAGS:
                    inclusive.append(f)
                else:
                    by_prio[prio_].append(f)
        live = [p_ for p_ in sorted(by_prio) if by_prio[p_]]
        cand = by_prio[live[0]] if live else []
        nci_blocked = False
        if not cand and inclusive:
            # NCI-inclusive income only: usable solely when no nonzero NCI income
            # fact exists for the period (then it equals the attributable figure)
            if (company, pid) in nci_nonzero:
                nci_blocked = True
            else:
                cand = inclusive
        pick = _pick_precise(cand)
        meta[cf_id] = (src, ccid, company)
        if nci_blocked:
            pending = _pick_precise(inclusive)
            if pending is not None:
                plan.nci_pending[cf_id] = pending
        if pick is not None:
            picked[cf_id] = pick
            plan.cells.append(
                CellPlan(
                    **base,
                    action=ACT_REPLACE,
                    replacement_fact_id=pick.fact_id,
                    replacement_value=pick.value,
                    replacement_form=pick.form,
                    replacement_accession=pick.accession,
                    replacement_was_authoritative=pick.is_authoritative,
                    note=_gap_bucket(Decimal(value), pick.value),
                )
            )
        else:
            code = (
                "proxy_nci_inclusive_only"
                if nci_blocked
                else "proxy_filed_copies_disagree"
                if cand
                else "proxy_only_source"
            )
            plan.cells.append(
                CellPlan(
                    **base,
                    action=ACT_REMOVE,
                    reason_code=code,
                    note=f"periodic_copies={len(cand)}",
                )
            )
    promote = _vet_and_promote(cur, ids, plan, picked, meta, tags_by_cc, core)
    plan.promote_fact_ids = sorted(promote)
    plan.info["periodic_facts_to_repromote"] = len(promote)
    _metrics(cur, ids, plan, core, analytics)
    return plan


QUARTER_MIN_DAYS, QUARTER_MAX_DAYS = 75, 105


def _rederive(
    groups: Mapping[tuple, list[FactRow]],
    company: int,
    concept: int,
    unit: str,
    qs: date,
    qe: date,
) -> tuple[str, Decimal | None, list[FactRow]]:
    """Quarter [qs, qe] from the PRECISE filed copies of one tag: the year-to-date
    ending qe minus the year-to-date ending the day before qs (Q4 = FY - 9M,
    Q3 = 9M - 6M), else the year-to-date minus the discrete quarters before it.
    Every input must have ONE value across all its filed copies (rounding aside);
    copies that disagree are a restatement and the quarter stays hidden (founder
    ruling). Returns ('ok', value, inputs) | ('disagree', None, []) | ('none', None, [])."""
    day = timedelta(days=1)
    starts = sorted(
        {
            k[3]
            for k in groups
            if k[0] == company
            and k[1] == concept
            and k[2] == unit
            and k[4] == qe
            and k[3] is not None
            and k[3] < qs
            and (qe - k[3]).days <= 380
        }
    )
    verdict = "none"
    for s0 in starts:
        a_copies = groups.get((company, concept, unit, s0, qe), [])
        b_copies = groups.get((company, concept, unit, s0, qs - day), [])
        if a_copies and b_copies:
            pa, pb = _pick_precise(a_copies), _pick_precise(b_copies)
            if pa is None or pb is None:
                verdict = "disagree"
                continue
            return "ok", pa.value - pb.value, [pa, pb]
        # discrete quarters from s0 up to qs - 1
        chain: list[FactRow] = []
        cur_start = s0
        ok = True
        while cur_start < qs and ok:
            nxt = [
                (k, v)
                for k, v in groups.items()
                if k[:3] == (company, concept, unit)
                and k[3] == cur_start
                and k[4] is not None
                and k[4] < qs
                and QUARTER_MIN_DAYS <= (k[4] - cur_start).days + 1 <= QUARTER_MAX_DAYS
            ]
            if len(nxt) != 1:
                ok = False
                break
            pick = _pick_precise(nxt[0][1])
            if pick is None:
                verdict = "disagree"
                ok = False
                break
            chain.append(pick)
            cur_start = nxt[0][0][4] + day
        if ok and chain and cur_start == qs and a_copies:
            pa = _pick_precise(a_copies)
            if pa is None:
                verdict = "disagree"
                continue
            return (
                "ok",
                pa.value - sum((f.value for f in chain), Decimal(0)),
                [pa, *chain],
            )
    return verdict, None, []


def _vet_and_promote(
    cur,
    ids: list[int],
    plan: Plan,
    picked: dict[int, FactRow],
    meta: dict[int, tuple[FactRow, int, int]],
    tags_by_cc: Mapping[int, Mapping[int, int]],
    core: str,
) -> set[int]:
    """Quarter cells (a derived replacement, or a blank quarter) are re-derived
    from the precise filed copies of ATTRIBUTABLE tags already in core.fact
    (verifier B5): EQH-style disagreeing copies stay hidden; HUBS/BAH-style
    cells whose precise derivation equals the stored one are kept (value-based,
    not date-based); STE/HOOD get the precise value; CAG uses the attributable
    tag; SM/WDAY blank quarters are filled. Inputs that are non-authoritative
    are re-promoted. Returns the facts to re-promote."""
    targets = [
        c
        for c in plan.cells
        if c.canonical_fact_id in meta
        and (
            (c.action == ACT_REPLACE and picked[c.canonical_fact_id].is_derived)
            or (
                c.action == ACT_REMOVE
                and c.reason_code in ("proxy_only_source", "proxy_nci_inclusive_only")
            )
        )
    ]
    period: dict[int, tuple[date, date]] = {}
    if targets:
        cur.execute(
            _q(PERIOD_SQL, core), {"pids": sorted({c.period_id for c in targets})}
        )
        period = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    targets = [
        c
        for c in targets
        if QUARTER_MIN_DAYS
        <= (period[c.period_id][1] - period[c.period_id][0]).days + 1
        <= QUARTER_MAX_DAYS
    ]
    groups: dict[tuple, list[FactRow]] = defaultdict(list)
    if targets:
        cids = sorted(
            {
                cid
                for c in targets
                for cid in tags_by_cc.get(meta[c.canonical_fact_id][1], {})
            }
            | {
                picked[c.canonical_fact_id].concept_id
                for c in targets
                if c.canonical_fact_id in picked
            }
        )
        lo = min(period[c.period_id][0] for c in targets) - timedelta(days=400)
        hi = max(period[c.period_id][1] for c in targets)
        cur.execute(
            _q(INPUT_FACTS_SQL, core),
            {
                "ids": sorted({c.company_id for c in targets}),
                "cids": cids,
                "lo": lo,
                "hi": hi,
                "forms": sorted(PERIODIC_FORMS_DOMESTIC),
            },
        )
        for row in cur.fetchall():
            f = _fact(row)
            groups[
                (f.company_id, f.concept_id, f.unit, f.start_date, f.end_date)
            ].append(f)
    tag_of: dict[int, str] = {f.concept_id: f.tag for fs in groups.values() for f in fs}

    used: set[int] = set()
    unverified = same = differs = filled = 0
    for c in targets:
        qs, qe = period[c.period_id]
        src, ccid, company = meta[c.canonical_fact_id]
        prios = tags_by_cc.get(ccid, {})
        ordered = sorted(
            (cid for cid in prios if tag_of.get(cid) not in NCI_INCLUSIVE_TAGS),
            key=lambda cid: prios[cid],
        )
        verdict, value, inputs = "none", None, []
        for cid in ordered:
            v, val, ins = _rederive(groups, company, cid, src.unit, qs, qe)
            if v == "ok":
                verdict, value, inputs = v, val, ins
                break
            if v == "disagree":
                verdict = "disagree"
        i = plan.cells.index(c)
        if verdict == "ok":
            old = picked.get(c.canonical_fact_id)
            if old is not None:
                if abs(old.value - value) <= 1:
                    same += 1
                else:
                    differs += 1
            else:
                filled += 1
            picked.pop(c.canonical_fact_id, None)
            used.update(f.fact_id for f in inputs if not f.is_authoritative)
            plan.cells[i] = replace(
                c,
                action=ACT_REPLACE,
                reason_code=None,
                replacement_fact_id=None,
                replacement_value=value,
                replacement_form="derived: "
                + " - ".join(f.accession or "?" for f in inputs[:2]),
                replacement_accession=None,
                replacement_was_authoritative=None,
                replacement_source_ids=tuple(f.fact_id for f in inputs),
                note=_gap_bucket(c.stored_value, value),
            )
        elif verdict == "disagree":
            picked.pop(c.canonical_fact_id, None)
            plan.cells[i] = replace(
                c,
                action=ACT_REMOVE,
                reason_code="derived_inputs_disagree",
                replacement_fact_id=None,
                replacement_value=None,
                replacement_form=None,
                replacement_accession=None,
                replacement_was_authoritative=None,
                replacement_source_ids=(),
                note="filed input copies disagree",
            )
        elif c.canonical_fact_id in picked:
            unverified += 1  # a stored derived quarter with no filed inputs to re-check
    plan.info["quarters_rederived_same_as_stored"] = same
    plan.info["quarters_rederived_differs_from_stored"] = differs
    plan.info["blank_quarters_filled_from_precise_inputs"] = filled
    plan.info["derived_replacements_unverified_no_inputs"] = unverified
    return {f.fact_id for f in picked.values() if not f.is_authoritative} | used


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


NCI_LABEL = re.compile(r"non-?controlling|minority|attributable to", re.I)


def sec_income_statement_labels(client, cik: str, accession: str) -> list[str] | None:
    """Row labels of the filing's rendered income statement (the filing's face),
    or None when it cannot be located (then there is no evidence either way)."""
    import httpx

    from scrooner_pipeline.parsers import filing_line_evidence as fle
    from scrooner_pipeline.segments.segment_revenue import _filing_summary_reports

    try:
        reports = _filing_summary_reports(client, int(cik), accession)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return None
        raise
    report = fle._pick_report(
        reports, fle.INCOME_STATEMENT_TITLE_PATTERN, fle.EARNINGS_TITLE
    )
    if report is None:
        return None
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"
    return fle._statement_labels(client, base + report["html_file"])


def resolve_nci_face(cur, plan: Plan, labels_for, core: str = "core") -> int:
    """A cell blocked only because an NCI income FACT exists is released when the
    filing's income statement shows NO noncontrolling or attributable line: the
    ProfitLoss bottom line is then the net income (MA 10-K 0001141391-25-000011
    R4 prints one 'Net Income' line). No label evidence keeps the cell hidden."""
    pend = plan.nci_pending
    if not pend:
        return 0
    cur.execute(
        _q("select id, cik from {core}.company where id = any(%(ids)s)", core),
        {"ids": sorted({f.company_id for f in pend.values()})},
    )
    cik = dict(cur.fetchall())
    cache: dict[tuple[int, str | None], list[str] | None] = {}
    promote = set(plan.promote_fact_ids)
    released = 0
    for i, c in enumerate(plan.cells):
        f = pend.get(c.canonical_fact_id)
        if (
            f is None
            or c.action != ACT_REMOVE
            or c.reason_code != "proxy_nci_inclusive_only"
        ):
            continue
        key = (f.company_id, f.accession)
        if key not in cache:
            cache[key] = (
                labels_for(cik[f.company_id], f.accession) if f.accession else None
            )
        labels = cache[key]
        if labels is None or any(NCI_LABEL.search(lab) for lab in labels):
            continue
        plan.cells[i] = replace(
            c,
            action=ACT_REPLACE,
            reason_code=None,
            replacement_fact_id=f.fact_id,
            replacement_value=f.value,
            replacement_form=f.form,
            replacement_accession=f.accession,
            replacement_was_authoritative=f.is_authoritative,
            note="face_has_no_nci_line",
        )
        if not f.is_authoritative:
            promote.add(f.fact_id)
        released += 1
    plan.promote_fact_ids = sorted(promote)
    plan.info["nci_cells_released_by_face_check"] = released
    plan.info["face_filings_read"] = len(cache)
    return released


def merge(plans: Sequence[Plan], family: str, rule_id: str) -> Plan:
    out = Plan(family, rule_id)
    for p in plans:
        out.facts += p.facts
        out.promote_fact_ids += p.promote_fact_ids
        out.nci_pending.update(p.nci_pending)
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
        "facts_to_repromote": len(set(plan.promote_fact_ids)),
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
        "facts_promoted": 0,
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
    promote_ids = sorted(set(plan.promote_fact_ids))
    if promote_ids:
        cur.execute(
            f"""
            with prior as (
                select id, company_id, is_authoritative from {core}.fact
                where id = any(%(ids)s::bigint[]) and not is_authoritative
                for update
            ), logged as (
                insert into {analytics}.fact_authority_retired
                    (fact_id, company_id, rule_id, reason_code, run_id, prior_is_authoritative)
                select id, company_id, %(rule)s, 'promote_periodic_copy', %(run)s, is_authoritative
                from prior
                returning fact_id
            )
            update {core}.fact f set is_authoritative = true
            from logged where f.id = logged.fact_id
            """,
            {"ids": promote_ids, "rule": plan.rule_id, "run": run_id},
        )
        stats["facts_promoted"] = cur.rowcount
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
                    c.replacement_source_ids or (c.replacement_fact_id,),  # type: ignore[arg-type]
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
    face_labels=None,
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
        if fam == "B" and face_labels is not None:
            resolve_nci_face(cur, plan, face_labels)
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
            d["replacement_source_ids"] = ";".join(map(str, c.replacement_source_ids))
            w.writerow([d[k] for k in cols] + [c.reason_text])
    with (out_dir / f"{tag}_metric_values_to_recompute.csv").open(
        "w", newline=""
    ) as fh:
        w = csv.writer(fh)
        w.writerow(["metric_value_id"])
        for i in sorted(set(plan.metric_value_ids)):
            w.writerow([i])


def _sec_labels():
    from scrooner_pipeline.common.sec_client import SECClient

    client = SECClient()
    return lambda cik, accession: sec_income_statement_labels(client, cik, accession)


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
    ap.add_argument(
        "--no-face",
        action="store_true",
        help="skip the SEC income-statement face check",
    )
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
            face_labels=None if args.no_face else _sec_labels(),
        )
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
