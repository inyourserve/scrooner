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

Family C  rule `retire.derived_per_share_cells@1`
    Derived (is_derived) EPS facts (basic and diluted, a ratio unit such as
    usd/shares). A quarter built as FY EPS minus 9M EPS (or 6M minus 3M) is
    wrong by construction: the share counts differ by period (fix register
    item 12, "no EPS subtraction"). The Normalizer gate stops new ones; this
    retires the 10.5k stored cohort cells (97% Q4). A replacement is a filed
    10-K/10-Q fact of the cell's OWN concept mapping (BasicAndDiluted feeds
    both). With none, the reason follows Item 302(a): a Q4 of a fiscal year
    ending on/after 2021-08-09 is not filed separately; any other quarter was
    filed (10-Q, or the pre-2021 10-K quarterly note), so its blank is a
    capture gap of ours. A *_resolved cell whose value differs from its
    source (split re-based) is left for review: the split-rebase family owns
    the basis. Dividends per share are NOT in scope here (split/dividend
    family, one dividend basis per company).

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

ORDER OF STEPS AFTER ANY APPLY (Release Manager's, not mine to change):
    1. apply_plan for one rule inside one reviewed transaction (flag ON, digest
       equal to the reviewed one);
    2. Normalizer re-run for the affected companies (derived quarters follow the
       demoted/re-promoted facts);
    3. Stage 2e dedupe re-run (so re-promoted copies are not marked
       non-authoritative again);
    4. Verifier sample and a certify re-run; restore(run_id) if it fails.
Restated periods whose filed copies disagree are HIDDEN (founder ruling
2026-10-26), quarters included; QUARTER_RESTATED_POLICY="original_basis" is the
off switch for a later "show confirmed restatements" ruling.

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
from scrooner_pipeline.common.derivation_policy import (
    ITEM_302A_CUTOFF,
    PER_SHARE_NOT_CAPTURED_REASON,
    PER_SHARE_NOT_DERIVED_REASON,
    PERIODIC_FORMS_DOMESTIC,
)
from scrooner_pipeline.common import cell_store
from scrooner_pipeline.common.cell_contract import CellKey
from scrooner_pipeline.mapper import canonical_archive

RULE_RATIO = "retire.derived_ratio_cells@1"
RULE_PROXY = "retire.proxy_form_cells@1"
RULE_PER_SHARE = "retire.derived_per_share_cells@1"
# Canonical EPS concepts of family C (base names; the *_resolved twins follow).
EPS_CANONICAL = ("basic_eps", "diluted_eps")

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
# family C only: the filed 3-month value read from the FSN num rows (bucket fsn-notes), no core.fact row; written
# with empty source_fact_ids and its provenance (FSN period, accession, tag, axis) in analytics.cell_evidence
ACT_REPLACE_FSN = "replace_with_fsn_value"

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
    "derived_inputs_unverified": (
        "the stored quarter has no filed year and year-to-date to check it against; not shown"
    ),
    "derived_scale_unverified": (
        "the quarter mixes reporting scales and the printed scale could not be read; not shown"
    ),
    "derived_inputs_disagree": (
        "the filed copies of the year or earlier quarters disagree (restated); not shown"
    ),
    "per_share_not_filed_separately": PER_SHARE_NOT_DERIVED_REASON,
    "per_share_not_captured": PER_SHARE_NOT_CAPTURED_REASON,
    "per_share_filed_copies_disagree": (
        "filed copies of this per-share value disagree; not shown until resolved"
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
    period_start: date | None = (
        None  # family C FSN replacements: the cell key of the evidence row
    )

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
    quarter_pending: dict[int, tuple[Decimal, tuple[FactRow, ...]]] = field(
        default_factory=dict
    )  # cell id -> quarter derived from NCI-inclusive inputs awaiting the face check
    scale_pending: dict[int, tuple[FactRow, ...]] = field(
        default_factory=dict
    )  # cell id -> inputs whose printed scale must be read from the filing
    scale_log: list[dict] = field(default_factory=list)
    supersede_fact_ids: list[int] = field(
        default_factory=list
    )  # authoritative copies of the same figure demoted beside a promoted precise copy
    authority_exceptions: list[dict] = field(default_factory=list)
    metric_value_ids: list[int] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)

    def digest(self) -> str:
        """Stable fingerprint of exactly what apply() would do."""
        payload = {
            "rule": self.rule_id,
            "facts": sorted(f.fact_id for f in self.facts),
            "promote": sorted(set(self.promote_fact_ids)),
            "supersede": sorted(set(self.supersede_fact_ids)),
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
                # FSN replacements also pin the accession and locator (other families' digests are unchanged)
                + (
                    (c.replacement_accession, c.note)
                    if c.action == ACT_REPLACE_FSN
                    else ()
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
        # a rounding never moves a figure by more than 0.5%: 250M against 247M
        # (company 3460 FY2023) is a restatement, not "250M rounded to 2 digits"
        and (not precise or abs(precise - rounded) / abs(precise) <= Decimal("0.005"))
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


# ------------------------------------------------------------------ family C
def per_share_reason(fiscal_period: str | None, period_end: date | None) -> str:
    """Reason code for a derived EPS cell with no filed copy (Item 302(a) era rule)."""
    if (
        fiscal_period == "Q4"
        and period_end is not None
        and period_end >= ITEM_302A_CUTOFF
    ):
        return "per_share_not_filed_separately"
    return "per_share_not_captured"


def plan_per_share_chunk(
    cur,
    ids: list[int],
    *,
    uids: list[int],
    priority_by_name: Mapping[str, Mapping[int, int]],
    fsn: Mapping[int, Mapping[str, Any]] | None = None,
    core: str = "core",
    analytics: str = "analytics",
) -> Plan:
    """Family C: derived EPS facts and the cells they feed. ``priority_by_name``:
    base canonical name -> {mapped concept id: priority}. ``fsn``: canonical_fact id -> the FSN scan outcome of a
    'not captured' cell (scripts/per_share/eps_fsn_scan.py): replace_with_fsn_value / fsn_copies_disagree, or
    not_in_fsn with ``rejected_axes`` (a copy exists only on an entity/restatement/class axis: review)."""
    plan = Plan("C_per_share_derived", RULE_PER_SHARE)
    cids = sorted({cid for m in priority_by_name.values() for cid in m})
    cur.execute(_q(RATIO_FACTS_SQL, core), {"ids": ids, "cids": cids, "uids": uids})
    facts = [_fact(r) for r in cur.fetchall()]
    by_id = {f.fact_id: f for f in facts}
    plan.facts = [f for f in facts if f.is_authoritative]
    plan.info["derived_per_share_facts_total"] = len(facts)
    plan.info["derived_per_share_facts_authoritative"] = len(plan.facts)
    cells = [
        c
        for c in _cells_for(cur, ids, facts, core, analytics)
        if c[3].removesuffix("_resolved") in priority_by_name
    ]
    pids = sorted({c[4] for c in cells})
    copies = _filed_copies(cur, ids, cids, pids, core)
    for cf_id, company, ccid, cname, pid, pend, value, sources in cells:
        sources_t = tuple(sources)
        retired = tuple(s for s in sources_t if s in by_id)
        base = dict(
            family=plan.family,
            rule_id=RULE_PER_SHARE,
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
        derived = by_id[retired[0]]
        if cname.endswith("_resolved") and Decimal(value) != derived.value:
            plan.cells.append(
                CellPlan(
                    **base, action=ACT_REVIEW, note="split re-based value: split family"
                )
            )
            continue
        mapped = priority_by_name[cname.removesuffix("_resolved")]
        by_prio: dict[int, list[FactRow]] = defaultdict(list)
        for cid, prio in mapped.items():
            for f in copies.get((company, cid, pid), []):
                by_prio[prio].append(f)
        chosen = _pick_one(by_prio[min(by_prio)]) if by_prio else None
        if chosen is not None:
            plan.cells.append(
                CellPlan(**base, action=ACT_REPLACE, replacement_fact_id=chosen.fact_id,
                         replacement_value=chosen.value, replacement_form=chosen.form,
                         replacement_accession=chosen.accession)
            )  # fmt: skip
        else:
            reason = (
                "per_share_filed_copies_disagree"
                if by_prio
                else per_share_reason(derived.fiscal_period, pend)
            )
            got = (fsn or {}).get(cf_id) if reason == "per_share_not_captured" else None
            if got and got["outcome"] == "replace_with_fsn_value":
                plan.cells.append(
                    CellPlan(**base, action=ACT_REPLACE_FSN, replacement_value=Decimal(got["value"]),
                             replacement_form=got["form"], replacement_accession=got["accession"],
                             period_start=date.fromisoformat(got["start"]),
                             note=f"fsn-notes:{got['fsn_period']}/num;tag={got['tag']};qtrs=1;"
                                  f"axis={got.get('axis') or 'none'};copies={got['copies']}"
                                  + (f";face={got['face_check']['accession']}:{got['face_check']['report']}"
                                     if got.get("face_check") else ""))
                )  # fmt: skip
                continue
            if got and got["outcome"] == "fsn_copies_disagree":
                reason = "per_share_filed_copies_disagree"
            elif got and got.get("rejected_axes"):
                plan.cells.append(
                    CellPlan(**base, action=ACT_REVIEW, note="filed only on a non-quarterly axis (entity/restatement/class)")
                )  # fmt: skip
                continue
            plan.cells.append(CellPlan(**base, action=ACT_REMOVE, reason_code=reason))
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
        if pick is not None:
            pick = _prefer_authoritative(pick, cand)
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

# Founder ruling 2026-10-26: HIDE restated periods whose copies disagree, quarters
# included. "original_basis" is the off switch for a later "show confirmed
# restatements" ruling (CLI --original-basis).
QUARTER_RESTATED_POLICY = "hide"  # or "original_basis"
VINTAGE_MAX_GAP_DAYS = 370  # same as the certification cross_vintage_arithmetic test


def _scale_unit(v: Decimal) -> int:
    """Filing scale a value is reported at: 1,000,000 or 1,000 if it is a multiple of
    it, else 1 (capped at millions: a multiple of 1e9 may still be filed in millions)."""
    for g in (10**6, 10**3):
        if v % g == 0:
            return g
    return 1


def _trailing_unit(v: Decimal) -> int:
    """Largest power of ten (1 .. 1e9) dividing v. Trailing zeros only SELECT
    candidates (see _scale_suspect); they never set the unit."""
    for e in range(9, 0, -1):
        if v % 10**e == 0:
            return 10**e
    return 1


def _scale_suspect(inputs: Sequence[FactRow]) -> bool:
    """Candidate for the printed-precision check: the inputs LOOK like different
    printed precisions from their trailing zeros. Trailing zeros prove nothing
    ('96.0', '4,274.0', '12,000' printed in thousands; AKTX), so this only
    selects which quarters to look up on the filing page, never the unit.
    A derived quarter is shown at the COARSEST printed precision among its inputs
    (resolve_scale), so any input that looks coarser than another, down to one
    printed decimal in millions (CSGP FY2023 '374.7', unit 100,000, beside a
    9M printed in thousands), must be looked up, not only whole-million ones."""
    units = [_trailing_unit(f.value) for f in inputs]
    return max(units) >= 10**4 and max(units) > min(units)


def _round_to(value: Decimal, g: Decimal | int) -> Decimal:
    g = Decimal(g)
    q = (abs(value) / g).quantize(Decimal(1), rounding="ROUND_HALF_UP") * g
    return q if value >= 0 else -q


SCALE_WORDS = {"billions": 10**9, "millions": 10**6, "thousands": 10**3}


def scale_from_html(html: str) -> int | None:
    """Printed MONEY scale of a rendered statement from its header ("USD ($) $ in
    Millions" -> 1,000,000; "USD ($)" alone -> 1). A shares phrase ("shares in
    Millions", ABNB) is never the money scale. None when not found."""
    head = html[:4000]
    m = re.search(r"\$\s*in\s+(billions|millions|thousands)", head, re.I) or re.search(
        r"(?<!shares )(?<!shares  )\bin\s+(billions|millions|thousands)\b", head, re.I
    )
    if m:
        return SCALE_WORDS[m.group(1).lower()]
    if re.search(r"USD\s*\(\$\)", head):
        return 1
    return None


def _prefer_authoritative(x: FactRow, copies: Sequence[FactRow]) -> FactRow:
    """Re-promoting a later copy beside an authoritative original leaves two
    authoritative facts for one company/tag/period until Stage 2e re-runs. If an
    authoritative copy of the SAME value exists, use it as the input/source
    (earliest filed) and promote nothing."""
    if x.is_authoritative:
        return x
    same = [f for f in copies if f.is_authoritative and f.value == x.value]
    if not same:
        return x
    return min(same, key=lambda f: (f.filing_date or date.max, f.fact_id))


def _one_vintage(restated: bool, facts: Sequence[FactRow]) -> bool:
    """Original-basis inputs must come from one reporting vintage: filed within
    VINTAGE_MAX_GAP_DAYS of each other. Copies that agree need no such test."""
    if not restated:
        return True
    dates = [f.filing_date for f in facts if f.filing_date]
    return (
        len(dates) == len(facts)
        and (max(dates) - min(dates)).days <= VINTAGE_MAX_GAP_DAYS
    )


def _basis_pick(copies: Sequence[FactRow]) -> tuple[FactRow | None, bool]:
    """(input fact, restated). One value across the copies (rounding aside): the
    precise copy. Copies that disagree were restated: under policy
    'original_basis' the EARLIEST-filed copy is the input (the figure as first
    reported, which pairs with the original year-to-date); under 'hide' there is
    no input."""
    pick = _pick_precise(copies)
    if pick is not None:
        return _prefer_authoritative(pick, copies), False
    if QUARTER_RESTATED_POLICY != "original_basis" or not copies:
        return None, True
    first = min(copies, key=lambda f: (f.filing_date or date.max, f.fact_id))
    return first, True


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
            (pa, ra), (pb, rb) = _basis_pick(a_copies), _basis_pick(b_copies)
            if pa is None or pb is None or not _one_vintage(ra or rb, [pa, pb]):
                verdict = "disagree"
                continue
            return ("ok_original" if ra or rb else "ok"), pa.value - pb.value, [pa, pb]
        # discrete quarters from s0 up to qs - 1
        chain: list[FactRow] = []
        any_restated = False
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
            pick, restated_q = _basis_pick(nxt[0][1])
            if pick is None:
                verdict = "disagree"
                ok = False
                break
            any_restated = any_restated or restated_q
            chain.append(pick)
            cur_start = nxt[0][0][4] + day
        if ok and chain and cur_start == qs and a_copies:
            pa, ra = _basis_pick(a_copies)
            if pa is None or not _one_vintage(ra or any_restated, [pa, *chain]):
                verdict = "disagree"
                continue
            return (
                "ok_original" if ra or any_restated else "ok",
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
    unverified = same = differs = filled = original = rounded_units = 0
    for c in targets:
        qs, qe = period[c.period_id]
        src, ccid, company = meta[c.canonical_fact_id]
        prios = tags_by_cc.get(ccid, {})
        ordered = sorted(
            (cid for cid in prios if tag_of.get(cid) not in NCI_INCLUSIVE_TAGS),
            key=lambda cid: prios[cid],
        )
        verdict, inputs = "none", []
        value: Decimal | None = None
        for cid in ordered:
            v, val, ins = _rederive(groups, company, cid, src.unit, qs, qe)
            if v in ("ok", "ok_original"):
                verdict, value, inputs = "ok", val, ins
                if v == "ok_original":
                    original += 1
                break
            if v == "disagree":
                verdict = "disagree"
        i = plan.cells.index(c)
        pending_q: tuple[Decimal, tuple[FactRow, ...]] | None = None
        if verdict == "none":
            # only an NCI-inclusive tag (ProfitLoss) carries the line: usable if the
            # filings' income statements show no NCI line (VRSN, SAIC); face check later
            for cid in sorted(
                (x for x in prios if tag_of.get(x) in NCI_INCLUSIVE_TAGS),
                key=lambda x: prios[x],
            ):
                v, val, ins = _rederive(groups, company, cid, src.unit, qs, qe)
                if v in ("ok", "ok_original"):
                    assert val is not None
                    pending_q = (val, tuple(ins))
                    break
        if verdict == "ok":
            assert value is not None
            if _scale_suspect(inputs):
                plan.scale_pending[c.canonical_fact_id] = tuple(inputs)
                rounded_units += 1
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
        elif pending_q is not None:
            picked.pop(c.canonical_fact_id, None)
            plan.quarter_pending[c.canonical_fact_id] = pending_q
            plan.cells[i] = replace(
                c,
                action=ACT_REMOVE,
                reason_code="proxy_nci_inclusive_only",
                replacement_fact_id=None,
                replacement_value=None,
                replacement_form=None,
                replacement_accession=None,
                replacement_was_authoritative=None,
                replacement_source_ids=(),
                note="quarter from NCI-inclusive inputs, awaiting the face check",
            )
        elif c.canonical_fact_id in picked:
            # a stored derived quarter with no filed inputs to re-check: hidden, not kept
            unverified += 1
            picked.pop(c.canonical_fact_id)
            plan.cells[i] = replace(
                c,
                action=ACT_REMOVE,
                reason_code="derived_inputs_unverified",
                replacement_fact_id=None,
                replacement_value=None,
                replacement_form=None,
                replacement_accession=None,
                replacement_was_authoritative=None,
                replacement_source_ids=(),
                note="no filed inputs to verify the stored derived quarter",
            )
    plan.info["quarters_pending_printed_scale_check"] = rounded_units
    plan.info["quarters_on_original_basis_after_restatement"] = original
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
# XBRL standard labels of pre-tax lines name the NCI in the element title
# ("Income ... before Income Taxes, Noncontrolling Interest, Total", VRSN): not an NCI line.
NCI_LABEL_IGNORE = re.compile(r"before\s+(provision\s+for\s+)?income\s+tax", re.I)


# "Net Income (Loss), Including Portion Attributable to Noncontrolling Interest"
# (Ambac) is the TOTAL including the NCI, not an NCI-only line.
INCLUDING_NCI = re.compile(
    r"including\s+(the\s+)?(portion\s+)?(attributable\s+to\s+)?non-?controlling", re.I
)


def has_nci_line(labels: Sequence[str]) -> bool:
    return any(
        NCI_LABEL.search(lab)
        and not NCI_LABEL_IGNORE.search(lab)
        and not INCLUDING_NCI.search(lab)
        for lab in labels
    )


class FilingFace:
    """Income statement of one filing, read with the Verifier kit
    (verification/filing_kit.py: statement selection incl. combined
    income + comprehensive-income pages, printed decimals). Cached per filing."""

    def __init__(self, client) -> None:
        self._client = client
        self._cache: dict[tuple[str, str], tuple | None] = {}

    def _get(self, url: str) -> bytes | None:
        import httpx

        try:
            return self._client.get(url).content
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise

    def page(self, cik: str, accession: str):
        """(RPage, money scale or None) or None when the statement is not found."""
        key = (cik, accession)
        if key not in self._cache:
            from scrooner_pipeline.verification import filing_kit as kit

            folder = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"
            out = None
            fs = self._get(folder + "FilingSummary.xml")
            sel = (
                kit.select_income_statement(fs.decode("utf8", "ignore")) if fs else None
            )
            if sel:
                raw = self._get(folder + sel[1])
                if raw:
                    html = raw.decode("utf8", "ignore")
                    out = (kit.parse_rpage(html), scale_from_html(html))
            self._cache[key] = out
        return self._cache[key]

    def labels(self, cik: str, accession: str) -> list[str] | None:
        got = self.page(cik, accession)
        return None if got is None else [r.label for r in got[0].rows]

    def printed_unit(self, cik: str, accession: str, fact: FactRow) -> Decimal | None:
        """Rounding unit of the printed cell that carries `fact`: money scale x
        10^-decimals read from the page (kit RPage.printed_unit), never from
        trailing zeros. None when the cell cannot be found on the page."""
        got = self.page(cik, accession)
        if (
            got is None
            or got[1] is None
            or fact.end_date is None
            or fact.start_date is None
        ):
            return None
        page, mult = got
        page.multiplier = mult
        months = max(1, round((fact.end_date - fact.start_date).days / 30.4375))
        try:
            col = page.column(fact.end_date, months)
        except KeyError:
            try:
                col = page.column(fact.end_date)
            except KeyError:
                return None
        except Exception:  # ambiguous column
            return None
        kinds = (
            ["consolidated"]
            if fact.tag in NCI_INCLUSIVE_TAGS
            else ["attributable", "consolidated"]
        )
        for want in kinds:
            for kind, row in _income_rows(page):
                if kind != want or col >= len(row.values) or row.values[col] is None:
                    continue
                unit = page.printed_unit(row, col)
                if unit == 1 and fact.value % 10**6 == 0:
                    # a whole-dollar page whose figure ends in six zeros was rounded
                    # to millions by the filer (ABNB '1,893,000,000'): unit 1M
                    unit = Decimal(10**6)
                if abs(fact.value - row.values[col] * mult) <= unit / 2 + Decimal(
                    "0.5"
                ):
                    return unit
        return None


def _income_rows(page):
    from scrooner_pipeline.verification import filing_kit as kit

    out = []
    for kind, row in kit.net_income_lines(page):
        if kind == "nci" and INCLUDING_NCI.search(row.label):
            kind = "consolidated"
        out.append((kind, row))
    return out


def resolve_scale(cur, plan: Plan, unit_for, core: str = "core") -> dict[str, int]:
    """For quarters whose inputs look like mixed scales, read the PRINTED scale of
    each input's filing (never infer it from trailing zeros: AKTX -17,298K minus
    -12,000K is -5,298K, both printed in thousands). All inputs printed at one
    scale: the exact value stands. Different scales: the quarter is shown at the
    coarsest printed scale (BAH 193,000,000). A scale that cannot be read hides
    the quarter (`derived_scale_unverified`). unit_for=None hides every pending
    cell."""
    out = {"exact": 0, "rounded": 0, "hidden": 0}
    if not plan.scale_pending:
        return out
    companies = {f.company_id for ins in plan.scale_pending.values() for f in ins}
    cik = {}
    if unit_for is not None:
        cur.execute(
            _q("select id, cik from {core}.company where id = any(%(ids)s)", core),
            {"ids": sorted(companies)},
        )
        cik = dict(cur.fetchall())
    cache: dict[tuple[int, str | None], Decimal | None] = {}
    for i, c in enumerate(plan.cells):
        inputs = plan.scale_pending.get(c.canonical_fact_id)
        if inputs is None or c.action != ACT_REPLACE:
            continue
        scales = []
        for f in inputs:
            key = (f.fact_id, f.accession)
            if key not in cache:
                cache[key] = (
                    unit_for(cik[f.company_id], f.accession, f)
                    if unit_for is not None and f.accession
                    else None
                )
            scales.append(cache[key])
        log = {
            "canonical_fact_id": c.canonical_fact_id,
            "company_id": c.company_id,
            "period_end": c.period_end,
            "value_before": c.replacement_value,
            "input_accessions": ";".join(f.accession or "?" for f in inputs),
            "printed_scales": ";".join(str(x) for x in scales),
        }
        known = [x for x in scales if x is not None]
        if len(known) != len(scales):
            plan.cells[i] = replace(
                c,
                action=ACT_REMOVE,
                reason_code="derived_scale_unverified",
                replacement_fact_id=None,
                replacement_value=None,
                replacement_form=None,
                replacement_source_ids=(),
                note="printed scale of an input could not be read",
            )
            out["hidden"] += 1
            log["outcome"] = "hidden"
        elif max(known) == min(known):
            out["exact"] += 1
            log["outcome"] = "exact"
        else:
            g = max(known)
            assert c.replacement_value is not None
            new = _round_to(c.replacement_value, g)
            new = new.to_integral_value() if new == new.to_integral_value() else new
            plan.cells[i] = replace(
                c,
                replacement_value=new,
                replacement_form=f"{c.replacement_form} (shown at {g:,})",
                note=_gap_bucket(c.stored_value, new),
            )
            out["rounded"] += 1
            log["outcome"] = f"rounded_to_{g}"
            log["value_after"] = new
        plan.scale_log.append(log)
    plan.info["scale_check_exact"] = out["exact"]
    plan.info["scale_check_rounded"] = out["rounded"]
    plan.info["scale_check_hidden"] = out["hidden"]
    return out


AUTH_KEYS_SQL = """
select f.id, f.company_id, f.concept_id, f.unit_id, f.period_id from {core}.fact f
where f.id = any(%(ids)s::bigint[])
"""
AUTH_STATE_SQL = """
select f.id, f.company_id, f.concept_id, f.unit_id, f.period_id, f.is_authoritative, fl.form, f.value
from {core}.fact f
join unnest(%(c)s::bigint[], %(k)s::bigint[], %(u)s::bigint[], %(p)s::bigint[]) as k(c, k, u, p)
  on f.company_id = k.c and f.concept_id = k.k and f.unit_id = k.u and f.period_id = k.p
left join {core}.filing fl on fl.id = f.filing_id
"""


def _same_figure(a: Decimal, b: Decimal) -> bool:
    base = max(abs(a), abs(b))
    return (
        not base
        or abs(a - b) / base <= ROUNDING
        or _rounded_copy_of(a, b)
        or _rounded_copy_of(b, a)
    )


def check_authority(cur, plan: Plan, core: str = "core") -> list[dict]:
    """Every company/tag/unit/period of a PROMOTED or SOURCE fact must end with
    EXACTLY ONE authoritative fact (verifier B11/B13). Resolution, in order:
      1. an authoritative fact filed on a non-periodic form (8-K, proxy) never
         stays beside an authoritative 10-K/10-Q-family fact (company 4938: the
         8-K carries different figures from the 10-K);
      2. further authoritative copies of the SAME figure (a 10-K/A beside its
         10-K, a rounded copy) are demoted (`supersede_fact_ids`);
      3. an authoritative copy of a materially different figure means a later
         filing restated the period: the cells that use the key are hidden
         (`proxy_filed_copies_disagree` / `derived_inputs_disagree`) and their
         promotions dropped (company 3460 FY2023: 247M vs the restated 250M).
    Keys whose proxy fact is only demoted are not checked: nothing is promoted
    there. Returns the remaining exceptions (also counted in plan.info)."""

    def used_ids(with_promote: bool = True) -> set[int]:
        out = set(plan.promote_fact_ids) if with_promote else set()
        for c in plan.cells:
            if c.action == ACT_REPLACE:
                out |= set(c.replacement_source_ids) | (
                    {c.replacement_fact_id} if c.replacement_fact_id else set()
                )
        return out

    ids = sorted(used_ids())
    keys: set[tuple] = set()
    for i in range(0, len(ids), 2000):
        cur.execute(_q(AUTH_KEYS_SQL, core), {"ids": ids[i : i + 2000]})
        keys |= {tuple(r[1:]) for r in cur.fetchall()}
    state: dict[tuple, list[tuple]] = defaultdict(list)
    keys_l = sorted(keys)
    for i in range(0, len(keys_l), 400):
        chunk = keys_l[i : i + 400]
        cur.execute(
            _q(AUTH_STATE_SQL, core),
            {
                "c": [k[0] for k in chunk],
                "k": [k[1] for k in chunk],
                "u": [k[2] for k in chunk],
                "p": [k[3] for k in chunk],
            },
        )
        for fid, co, cn, un, pe, auth, form, val in cur.fetchall():
            state[(co, cn, un, pe)].append((fid, auth, form, Decimal(val)))
    demote = {f.fact_id for f in plan.facts}
    hidden_by_restatement = 0
    supersede: set[int] = set()
    bad: list[dict] = []
    for _pass in range(3):
        used = used_ids()
        promote = set(plan.promote_fact_ids)
        supersede = set()
        bad = []
        for key, facts in state.items():
            auth_now = [
                f for f in facts if (f[1] and f[0] not in demote) or f[0] in promote
            ]
            if len(auth_now) > 1:
                if any(f[2] in PERIODIC_FORMS_DOMESTIC for f in auth_now):
                    supersede |= {
                        f[0] for f in auth_now if f[2] not in PERIODIC_FORMS_DOMESTIC
                    }
                    auth_now = [f for f in auth_now if f[0] not in supersede]
            if len(auth_now) > 1:
                anchor = next(
                    (f for f in auth_now if f[0] in promote),
                    next((f for f in auth_now if f[0] in used), auth_now[0]),
                )
                supersede |= {
                    f[0]
                    for f in auth_now
                    if f[0] != anchor[0] and _same_figure(f[3], anchor[3])
                }
                auth_now = [f for f in auth_now if f[0] not in supersede]
            if len(auth_now) != 1:
                bad.append(
                    {
                        "company_id": key[0],
                        "concept_id": key[1],
                        "unit_id": key[2],
                        "period_id": key[3],
                        "authoritative_after": len(auth_now),
                        "authoritative_fact_ids": ";".join(str(f[0]) for f in auth_now),
                        "all_fact_ids": ";".join(str(f[0]) for f in facts),
                        "_key_ids": {f[0] for f in facts},
                    }
                )
        if not bad:
            break
        # a restated period: hide the cells that use the key, drop their promotions
        bad_ids = set().union(*(b["_key_ids"] for b in bad))
        for i, c in enumerate(plan.cells):
            if c.action != ACT_REPLACE:
                continue
            srcs = set(c.replacement_source_ids) | (
                {c.replacement_fact_id} if c.replacement_fact_id else set()
            )
            if srcs & bad_ids:
                plan.cells[i] = replace(
                    c,
                    action=ACT_REMOVE,
                    reason_code=(
                        "derived_inputs_disagree"
                        if c.replacement_source_ids
                        else "proxy_filed_copies_disagree"
                    ),
                    replacement_fact_id=None,
                    replacement_value=None,
                    replacement_form=None,
                    replacement_accession=None,
                    replacement_was_authoritative=None,
                    replacement_source_ids=(),
                    note="a later filing restates this period",
                )
                hidden_by_restatement += 1
        keep = used_ids(with_promote=False)
        plan.promote_fact_ids = [p for p in plan.promote_fact_ids if p in keep]
    for b in bad:
        b.pop("_key_ids", None)
    plan.supersede_fact_ids = sorted(supersede)
    plan.info["authority_keys_checked"] = len(state)
    plan.info["authority_keys_zero"] = sum(b["authoritative_after"] == 0 for b in bad)
    plan.info["authority_keys_multiple"] = sum(
        b["authoritative_after"] > 1 for b in bad
    )
    plan.info["authoritative_copies_superseded"] = len(supersede)
    plan.info["cells_hidden_because_a_later_filing_restates"] = hidden_by_restatement
    plan.authority_exceptions = bad
    return bad


def resolve_nci_face(cur, plan: Plan, labels_for, core: str = "core") -> int:
    """A cell blocked only because an NCI income FACT exists is released when the
    filing's income statement shows NO noncontrolling or attributable line: the
    ProfitLoss bottom line is then the net income (MA 10-K 0001141391-25-000011
    R4 prints one 'Net Income' line). No label evidence keeps the cell hidden."""
    pend = plan.nci_pending
    qpend = plan.quarter_pending
    if not pend and not qpend:
        return 0
    companies = {f.company_id for f in pend.values()} | {
        f.company_id for _, ins in qpend.values() for f in ins
    }
    cur.execute(
        _q("select id, cik from {core}.company where id = any(%(ids)s)", core),
        {"ids": sorted(companies)},
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
        if labels is None or has_nci_line(labels):
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
    # quarters derived from NCI-inclusive inputs: every input filing's income
    # statement must show no NCI line (VRSN Q4 = 817.6 - 552.9, SAIC 358 - 273)
    for i, c in enumerate(plan.cells):
        got = qpend.get(c.canonical_fact_id)
        if got is None or c.action != ACT_REMOVE:
            continue
        value, inputs = got
        clean = True
        for f in inputs:
            key = (f.company_id, f.accession)
            if key not in cache:
                cache[key] = (
                    labels_for(cik[f.company_id], f.accession) if f.accession else None
                )
            labels = cache[key]
            if labels is None or has_nci_line(labels):
                clean = False
                break
        if not clean:
            continue
        if _scale_suspect(inputs):
            plan.scale_pending[c.canonical_fact_id] = tuple(inputs)
        plan.cells[i] = replace(
            c,
            action=ACT_REPLACE,
            reason_code=None,
            replacement_value=value,
            replacement_form="derived: "
            + " - ".join(f.accession or "?" for f in inputs[:2]),
            replacement_source_ids=tuple(f.fact_id for f in inputs),
            note=_gap_bucket(c.stored_value, value),
        )
        promote.update(f.fact_id for f in inputs if not f.is_authoritative)
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
        out.supersede_fact_ids += p.supersede_fact_ids
        out.nci_pending.update(p.nci_pending)
        out.quarter_pending.update(p.quarter_pending)
        out.scale_pending.update(p.scale_pending)
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
    fact_ids = sorted({f.fact_id for f in plan.facts} | set(plan.supersede_fact_ids))
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
    fsn_cells = [c for c in plan.cells if c.action == ACT_REPLACE_FSN]
    if fsn_cells:
        s = canonical_archive.replace_rows(
            cur,
            [
                canonical_archive.CanonicalRow(
                    c.company_id, c.canonical_concept_id, c.period_id,
                    c.replacement_value, (),  # type: ignore[arg-type]
                )
                for c in fsn_cells
            ],
            reason_code=f"{plan.rule_id}:replace_fsn",
            run_id=run_id,
            schema=analytics,
        )  # fmt: skip
        stats["cells_replaced"] += s["replaced"]
        stats["cells_inserted"] += s["inserted"]
        for c in fsn_cells:
            assert c.period_end is not None and c.period_start is not None
            cell_store.append_evidence(
                cur.connection,
                cell_store.EvidenceRecord(
                    key=CellKey(c.company_id, c.concept.removesuffix("_resolved"), "Q", c.period_start, c.period_end),
                    state_claimed="value", rule_id=plan.rule_id, evidence_kind="detector_audit",
                    evidence_level="DATA-INFERRED", recorded_by="data_engineer",
                    accession=c.replacement_accession, locator=c.note, detector_version="1",
                    source_hash=expected_digest,
                ),
                import_key=hashlib.sha256(f"{run_id}|{c.canonical_fact_id}".encode()).hexdigest(),
            )  # fmt: skip
        stats["evidence_rows"] = len(fsn_cells)
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
def load_fsn_outcomes(path: Path) -> dict[int, dict[str, Any]]:
    """canonical_fact id -> outcome, from eps_fsn_scan.py's nc_fsn_outcomes.json (FSN period from the filed date)."""
    out: dict[int, dict[str, Any]] = {}
    for x in json.loads(path.read_text()):
        if x.get("filed"):
            filed = date(
                int(x["filed"][:4]), int(x["filed"][4:6]), int(x["filed"][6:8])
            )
            x["fsn_period"] = (
                f"{filed.year}q{(filed.month - 1) // 3 + 1}" if filed < date(2025, 10, 1)
                else f"{filed.year}m{filed.month:02d}"
            )  # fmt: skip
        out[int(x["canonical_fact_id"])] = x
    return out


def _cohort(path: Path) -> set[int]:
    with path.open() as fh:
        return {int(r["company_id"]) for r in csv.DictReader(fh) if not r["excluded"]}


def run_dry_run(
    conn,
    out_dir: Path,
    *,
    families: Sequence[str] = ("A", "B"),  # "C": derived EPS (run on its own)
    cohort: set[int] | None = None,
    company_ids: list[int] | None = None,
    chunk: int = 100,
    statement_timeout: str = "60s",
    log=lambda m: print(m, flush=True),
    face_labels=None,
    scale_for=None,
    fsn_outcomes: Path | None = None,
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
    eps_priority: dict[str, dict[int, int]] = {}
    for name in EPS_CANONICAL:
        cur.execute(_q(MAPPED_CONCEPTS_SQL), {"name": name})
        eps_priority[name] = {r[0]: r[1] for r in cur.fetchall()}
    fsn = load_fsn_outcomes(fsn_outcomes) if fsn_outcomes else None
    out_dir.mkdir(parents=True, exist_ok=True)
    plans: dict[str, list[Plan]] = {"A": [], "B": [], "C": []}
    t0 = time.time()
    for i in range(0, len(company_ids), chunk):
        ids = company_ids[i : i + chunk]
        if "A" in families:
            plans["A"].append(
                plan_ratio_chunk(cur, ids, cids=cids, uids=uids, mapped_priority=mapped)
            )
        if "B" in families:
            plans["B"].append(plan_proxy_chunk(cur, ids))
        if "C" in families:
            plans["C"].append(
                plan_per_share_chunk(
                    cur, ids, uids=uids, priority_by_name=eps_priority, fsn=fsn
                )
            )
        log(
            f"companies {min(i + chunk, len(company_ids))}/{len(company_ids)} {time.time() - t0:.0f}s"
        )
    summary: dict[str, Any] = {"companies_scanned": len(company_ids)}
    for fam, family_name, rule in (
        ("A", "A_ratio_derived", RULE_RATIO),
        ("B", "B_proxy_form", RULE_PROXY),
        ("C", "C_per_share_derived", RULE_PER_SHARE),
    ):
        if fam not in families:
            continue
        plan = merge(plans[fam], family_name, rule)
        if fam == "B" and face_labels is not None:
            resolve_nci_face(cur, plan, face_labels)
        if fam == "B":
            resolve_scale(cur, plan, scale_for)
            check_authority(cur, plan)
        summary[family_name] = summarize(plan, cohort)
        _write_csvs(out_dir, plan)
        _write_review_files(out_dir, plan, cohort)
    (out_dir / "retirement_dryrun_summary.json").write_text(
        json.dumps(summary, indent=2, default=str)
    )
    return summary


def _write_review_files(out_dir: Path, plan: Plan, cohort: set[int] | None) -> None:
    """Files for the Release Manager's reviewed plan (nothing here touches the DB)."""
    tag = plan.family
    with (out_dir / f"{tag}_superseded_facts.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fact_id", "is_authoritative_now", "new_is_authoritative"])
        for fid in sorted(set(plan.supersede_fact_ids)):
            w.writerow([fid, True, False])
    if plan.authority_exceptions:
        with (out_dir / f"{tag}_authority_exceptions.csv").open("w", newline="") as fh:
            dw = csv.DictWriter(fh, fieldnames=list(plan.authority_exceptions[0]))
            dw.writeheader()
            dw.writerows(plan.authority_exceptions)
    if plan.scale_log:
        with (out_dir / f"{tag}_scale_check.csv").open("w", newline="") as fh:
            cols = [
                "canonical_fact_id",
                "company_id",
                "period_end",
                "input_accessions",
                "printed_scales",
                "outcome",
                "value_before",
                "value_after",
            ]
            dw = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            dw.writeheader()
            dw.writerows(plan.scale_log)
    users: dict[int, list[int]] = defaultdict(list)
    for c in plan.cells:
        if c.action == ACT_REPLACE:
            for src_id in c.replacement_source_ids or (c.replacement_fact_id,):
                if src_id is not None:
                    users[src_id].append(c.canonical_fact_id)
    with (out_dir / f"{tag}_promote_facts_before_image.csv").open(
        "w", newline=""
    ) as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "fact_id",
                "prior_is_authoritative",
                "new_is_authoritative",
                "used_by_canonical_fact_ids",
            ]
        )
        for fid in sorted(set(plan.promote_fact_ids)):
            w.writerow([fid, False, True, ";".join(map(str, users.get(fid, [])))])
    demote = {f.fact_id: f for f in plan.facts}
    with (out_dir / f"{tag}_proxy_only_recheck.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "canonical_fact_id",
                "company_id",
                "in_cohort",
                "concept",
                "period_end",
                "stored_value",
                "proxy_fact_ids",
                "proxy_accessions",
                "proxy_forms",
            ]
        )
        for c in plan.cells:
            if c.reason_code != "proxy_only_source":
                continue
            fs = [demote[i] for i in c.retired_source_ids if i in demote]
            w.writerow(
                [
                    c.canonical_fact_id,
                    c.company_id,
                    None if cohort is None else c.company_id in cohort,
                    c.concept,
                    c.period_end,
                    c.stored_value,
                    ";".join(map(str, c.retired_source_ids)),
                    ";".join(f.accession or "?" for f in fs),
                    ";".join(f.form or "?" for f in fs),
                ]
            )
    release = {
        "rule_id": plan.rule_id,
        "plan_digest": plan.digest(),
        "enable_with": f"SCROONER_RULES_ENABLED={plan.rule_id} (dispatch input rules='on:{plan.rule_id}')",
        "steps": [
            "1 apply_plan(cur, plan, run_id, expected_digest=<plan_digest>) in ONE reviewed transaction; archive tables must exist (migration 0098 + fact_authority_retired migration)",
            "2 Normalizer re-run for the affected companies",
            "3 Stage 2e dedupe re-run",
            "4 Verifier sample + scrooner-certify re-run",
            "5 on failure: restore(cur, run_id) (cells from canonical_fact_retired, facts from fact_authority_retired)",
        ],
        "counts": {
            "facts_to_demote": len(plan.facts),
            "facts_to_promote": len(set(plan.promote_fact_ids)),
            "facts_to_supersede": len(set(plan.supersede_fact_ids)),
            "cells_replace": sum(c.action == ACT_REPLACE for c in plan.cells),
            "cells_remove": sum(c.action == ACT_REMOVE for c in plan.cells),
            "cells_review_not_retired": sum(c.action == ACT_REVIEW for c in plan.cells),
            "metric_values_to_recompute": len(set(plan.metric_value_ids)),
        },
    }
    (out_dir / f"{tag}_release_plan.json").write_text(
        json.dumps(release, indent=2, default=str)
    )


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


def _sec_face() -> FilingFace:
    from scrooner_pipeline.common.sec_client import SECClient

    return FilingFace(SECClient())


def _face_kwargs() -> dict:
    face = _sec_face()
    return {"face_labels": face.labels, "scale_for": face.printed_unit}


def main(argv: list[str] | None = None) -> int:
    import psycopg

    from scrooner_pipeline.common.config import settings

    ap = argparse.ArgumentParser(
        description="READ-ONLY retirement dry-run (writes files only)"
    )
    ap.add_argument("out_dir")
    ap.add_argument("--family", choices=["A", "B", "C", "both"], default="both")
    ap.add_argument(
        "--cohort-csv", default=None, help="doc/data-moat/team/top1000/shards.csv"
    )
    ap.add_argument("--ciks", default=None)
    ap.add_argument(
        "--fsn-outcomes",
        type=Path,
        default=None,
        help="family C: eps_fsn_scan.py nc_fsn_outcomes.json",
    )
    ap.add_argument("--chunk", type=int, default=100)
    ap.add_argument("--statement-timeout", default="60s")
    ap.add_argument(
        "--no-face",
        action="store_true",
        help="skip the SEC income-statement face check",
    )
    ap.add_argument(
        "--original-basis",
        action="store_true",
        help="OFF-SWITCH for a later 'show confirmed restatements' ruling: derive quarters from the earliest-filed copies instead of hiding them",
    )
    args = ap.parse_args(argv)
    global QUARTER_RESTATED_POLICY
    if args.original_basis:
        QUARTER_RESTATED_POLICY = "original_basis"
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
            fsn_outcomes=args.fsn_outcomes,
            **({} if args.no_face else _face_kwargs()),
        )
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
