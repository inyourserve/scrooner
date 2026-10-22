"""Stage 2e -- Duplicate/overlap resolution (doc 09). Resolves
core.fact.is_authoritative for every (company, concept, unit, period) group
with more than one row -- no new writes to raw or reads of companyfacts;
this operates entirely on what Stage 2d already wrote.

Verified live 2026-08-15 across the golden-8: 48,360 (company, concept,
unit, period) groups have more than one core.fact row (the same period
reported in an original filing and again as a later comparative), and
3,178 of those (~6.6%) genuinely DISAGREE on value -- not a rare edge case.
Inspected real examples: these are small, non-material revisions companies
make to prior-period comparatives in later filings WITHOUT filing a formal
10-K/A (e.g. JPM's DerivativeNotionalAmount for 2013-12-31 quietly shifts
from $70.430T to $70.413T starting mid-2014, no amendment on file). Real,
expected EDGAR messiness, not a bug in extraction -- and too common to
"flag" with just a log line, so the flagging mechanism has to be something
actually queryable.

Rule, per doc 09's "deterministic when they agree, flag when they don't":

- Singleton group (1 row): untouched, stays is_authoritative=true (the
  column's default from Stage 2d).
- Duplicate group, all rows agree on value: the EARLIEST-FILED row becomes
  is_authoritative=true, every later repeat becomes false. Earliest-filed
  is the most defensible choice of "primary source" -- it's where the
  value was first disclosed, and it's independent of how many times a
  later filing happens to repeat it as a comparative.
- Duplicate group, rows DISAGREE on value: every row in the group becomes
  is_authoritative=false. This is the "flag, don't silently resolve" case
  -- picking any single value here (even "most recent") would be a guess
  the Mapper shouldn't inherit as settled fact. No new table needed to
  surface this: a group where more than one row exists and NONE is
  authoritative is a genuine unresolved conflict, fully queryable directly
  against core.fact (see conflict_summary below).

Formal restatements (10-K/A) are Stage 2f's job, not this one's -- 2e only
handles same-form-type disagreement (a 10-Q quietly repeating a slightly
different number than the original 10-K), not amendment supersession.

W3 -- rule source.periodic_form_only@1 (RF-03), flag OFF by default
------------------------------------------------------------------
Until 2026-10-22 this stage grouped EVERY fact of a company with no form
filter, so one rounded DEF 14A pay-versus-performance copy (JPM 57,000M vs the
10-K's 57,048M) disagreed with the precise 10-K copies and de-authorized all of
them, and a derived Q4 built on the proxy FY (12,977M) conflicted with the
10-K-derived Q4 (13,025M) so both lost authority and the priority-3
"available to common" tag (12,691M) was displayed (ledger 2026-10-22). With the
flag on (SCROONER_RULES_ENABLED contains the rule ID, common/rule_flags.py):
- facts and derived rows whose filing is not a periodic report
  (common/periodic_forms.PERIODIC_FORMS_ALL) never join a group and are never
  authoritative;
- a group that SHRANK because non-periodic copies left it and now has exactly
  one periodic copy makes that copy authoritative (this is what repairs a cell
  an earlier run had left with no authoritative copy; the derive stages that
  run after this one re-assert their own demotions, so nothing they decided is
  lost);
- a group with no periodic copy has no authoritative fact (a visible blank).
Flag off: byte-for-byte the previous behavior. Unchanged rows are not written
(core.fact is already bloated with dead tuples, plan 2026-10-22).

WO-23 -- rule dedupe.matching_copies@1 (RF-46), flag OFF by default: copies
that differ only by rounding are not a conflict (normalizer/matching_copies.py);
the most precise copy (fewest trailing zeros, then earliest filed) wins.
"""

from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback
from scrooner_pipeline.common.periodic_forms import PERIODIC_FORMS_ALL
from scrooner_pipeline.common.rule_flags import (
    RULE_MATCHING_COPIES,
    RULE_PERIODIC_FORM_ONLY,
    rule_dry_run,
    rule_enabled,
)
from scrooner_pipeline.normalizer.matching_copies import all_consistent, precision_rank

logger = structlog.get_logger()


def _load_fact_rows(conn: psycopg.Connection, company_id: int) -> list[tuple]:
    """(fact_id, concept_id, unit_id, period_id, value, filing_date, filing_id,
    form, is_authoritative, is_derived) for every fact belonging to this
    company, pre-sorted so the first row in each (concept_id, unit_id,
    period_id) group is the earliest-filed (ties broken by fact_id, i.e.
    insertion order) -- makes "earliest wins" a matter of taking members[0],
    not a separate min() pass."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.id, f.concept_id, f.unit_id, f.period_id, f.value, fl.filing_date, f.filing_id,
                   fl.form, f.is_authoritative, f.is_derived
            from core.fact f
            join core.filing fl on fl.id = f.filing_id
            where f.company_id = %s
            order by f.concept_id, f.unit_id, f.period_id, fl.filing_date, f.id
            """,
            (company_id,),
        )
        return cur.fetchall()


# Change classes reported by the population dry-run (collect_changes=True).
CLASS_CONFLICT_CLEARED = "conflict_cleared"  # no authoritative copy -> one (the JPM FY/Q4 cases)
CLASS_NON_PERIODIC_DEMOTED_SAME_VALUE = "non_periodic_demoted_same_value"
CLASS_AUTHORITY_VALUE_CHANGED = "authority_value_changed"  # authoritative value differs after
CLASS_VALUE_TO_NONE = "value_to_none"  # a cell loses its only authoritative copy
CLASS_PERIODIC_CONFLICT_REMAINS = "periodic_conflict_remains"
CLASS_MATCHING_COPIES_RESOLVED = "matching_copies_resolved"  # WO-23
CLASS_OTHER = "other"


@dataclass
class _Member:
    fact_id: int
    value: Decimal
    form: str | None
    is_auth: bool
    is_derived: bool
    periodic: bool


@dataclass
class AuthorityPlan:
    set_true: list[int] = field(default_factory=list)
    set_false: list[int] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)
    # Only filled when collect_changes=True:
    # (class, concept_id, unit_id, period_id, before_values, after_values, nonperiodic_forms)
    changes: list[tuple[Any, ...]] = field(default_factory=list)
    class_counts: Counter = field(default_factory=Counter)


def _final_values(members: list[_Member], desired: dict[int, bool]) -> list[Decimal]:
    return sorted(
        {m.value for m in members if desired.get(m.fact_id, m.is_auth)}, key=Decimal
    )


def plan_authority(
    rows: list[tuple],
    *,
    periodic_only: bool = False,
    matching_copies: bool = False,
    collect_changes: bool = False,
) -> AuthorityPlan:
    """Pure: decide is_authoritative for every group of one company's facts.
    Flags off reproduces the pre-W3 behavior exactly (see module docstring)."""
    groups: dict[tuple, list[_Member]] = {}
    for row in rows:
        fact_id, concept_id, unit_id, period_id, value, _fd, _fid, form, is_auth, is_derived = row
        periodic = (form is not None and form in PERIODIC_FORMS_ALL) if periodic_only else True
        groups.setdefault((concept_id, unit_id, period_id), []).append(
            _Member(fact_id, value, form, bool(is_auth), bool(is_derived), periodic)
        )

    plan = AuthorityPlan()
    agreed = conflicts = non_periodic_demoted = shrunk_promoted = matching_resolved = 0

    for key, members in groups.items():
        periodic_members = [m for m in members if m.periodic]
        non_periodic = [m for m in members if not m.periodic]
        desired: dict[int, bool] = {}
        matching_used = False

        for m in non_periodic:
            desired[m.fact_id] = False
        non_periodic_demoted += sum(1 for m in non_periodic if m.is_auth)

        if len(periodic_members) == 1:
            if non_periodic:
                lone = periodic_members[0]
                desired[lone.fact_id] = True
                shrunk_promoted += 0 if lone.is_auth else 1
            # else: singleton group, untouched (Stage 2d default stays)
        elif len(periodic_members) > 1:
            values = [m.value for m in periodic_members]
            exact = len(set(values)) == 1
            agree = exact
            if not exact and matching_copies and all_consistent(values):
                agree = True
                matching_used = True
            if agree:
                if exact:
                    winner = periodic_members[0]  # earliest filed, by query order
                else:
                    winner = min(
                        enumerate(periodic_members),
                        key=lambda im: (precision_rank(im[1].value), im[0]),
                    )[1]
                desired[winner.fact_id] = True
                for m in periodic_members:
                    if m is not winner:
                        desired[m.fact_id] = False
                agreed += 1
                matching_resolved += matching_used
            else:
                for m in periodic_members:
                    desired[m.fact_id] = False
                conflicts += 1

        for m in members:
            want = desired.get(m.fact_id)
            if want is None or want == m.is_auth:
                continue
            (plan.set_true if want else plan.set_false).append(m.fact_id)

        if collect_changes and (non_periodic or matching_used):
            before = sorted({m.value for m in members if m.is_auth}, key=Decimal)
            after = _final_values(members, desired)
            if not periodic_members:
                klass = CLASS_VALUE_TO_NONE if before else CLASS_OTHER
            elif matching_used and not any(not m.periodic for m in members):
                klass = CLASS_MATCHING_COPIES_RESOLVED
            elif not before and after:
                klass = CLASS_CONFLICT_CLEARED
            elif before and after:
                klass = (
                    CLASS_NON_PERIODIC_DEMOTED_SAME_VALUE
                    if before == after
                    else CLASS_AUTHORITY_VALUE_CHANGED
                )
            elif not before and not after:
                klass = CLASS_PERIODIC_CONFLICT_REMAINS
            else:
                klass = CLASS_VALUE_TO_NONE
            plan.class_counts[klass] += 1
            plan.changes.append(
                (
                    klass,
                    key[0],
                    key[1],
                    key[2],
                    before,
                    after,
                    sorted({m.form for m in non_periodic if m.form}),
                )
            )

    plan.stats = {
        "duplicate_groups": agreed + conflicts,
        "agreed_duplicate_groups": agreed,
        "conflict_groups": conflicts,
        "non_periodic_demoted": non_periodic_demoted,
        "shrunk_group_promoted": shrunk_promoted,
        "matching_copy_groups": matching_resolved,
    }
    return plan


def resolve_authoritative_for_company(
    conn: psycopg.Connection,
    company_id: int,
    *,
    periodic_only: bool | None = None,
    matching_copies: bool | None = None,
) -> dict:
    if periodic_only is None:
        periodic_only = rule_enabled(RULE_PERIODIC_FORM_ONLY)
    if matching_copies is None:
        matching_copies = rule_enabled(RULE_MATCHING_COPIES)
    rows = _load_fact_rows(conn, company_id)
    plan = plan_authority(rows, periodic_only=periodic_only, matching_copies=matching_copies)
    if rule_dry_run(RULE_PERIODIC_FORM_ONLY) or rule_dry_run(RULE_MATCHING_COPIES):
        # dry_run mode: log what the rules WOULD change, write the legacy plan
        would = plan_authority(
            rows,
            periodic_only=periodic_only or rule_dry_run(RULE_PERIODIC_FORM_ONLY),
            matching_copies=matching_copies or rule_dry_run(RULE_MATCHING_COPIES),
        )
        logger.info(
            "dedupe.dry_run",
            company_id=company_id,
            would_write=len(would.set_true) + len(would.set_false),
            legacy_write=len(plan.set_true) + len(plan.set_false),
            **{f"would_{k}": v for k, v in would.stats.items()},
        )

    with conn.cursor() as cur:
        if plan.set_true:
            cur.execute(
                "update core.fact set is_authoritative = true where id = any(%s)",
                (plan.set_true,),
            )
        if plan.set_false:
            cur.execute(
                "update core.fact set is_authoritative = false where id = any(%s)",
                (plan.set_false,),
            )
    conn.commit()

    stats = dict(plan.stats)
    logger.info("dedupe.resolved", company_id=company_id, **stats)
    return stats


def resolve_authoritative(conn: psycopg.Connection, ciks: set[str]) -> dict:
    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "duplicate_groups": 0,
        "agreed_duplicate_groups": 0,
        "conflict_groups": 0,
        "non_periodic_demoted": 0,
        "shrunk_group_promoted": 0,
        "matching_copy_groups": 0,
    }
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = resolve_authoritative_for_company(conn, company_id)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "core.normalizer_error", cik, "dedupe", exc)
            conn = safe_rollback(conn, stage="dedupe", cik=cik)
            continue
        totals["ok"] += 1
        for k in (
            "duplicate_groups",
            "agreed_duplicate_groups",
            "conflict_groups",
            "non_periodic_demoted",
            "shrunk_group_promoted",
            "matching_copy_groups",
        ):
            totals[k] += stats[k]

    logger.info("dedupe.resolve.done", **totals)
    return totals


def conflict_summary(conn: psycopg.Connection, ciks: set[str]) -> list[dict]:
    """Every unresolved conflict group -- for review, not automated
    resolution. A group is a genuine conflict iff it has more than one row
    and none of them is authoritative (see module docstring)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.cik, co.taxonomy, co.tag, u.unit_name, p.start_date, p.end_date, p.period_type,
                   array_agg(f.value order by fl.filing_date) as values,
                   array_agg(fl.form order by fl.filing_date) as forms,
                   array_agg(fl.filing_date order by fl.filing_date) as filing_dates
            from core.fact f
            join core.company c on c.id = f.company_id
            join core.concept co on co.id = f.concept_id
            join core.unit u on u.id = f.unit_id
            join core.period p on p.id = f.period_id
            join core.filing fl on fl.id = f.filing_id
            where c.cik = any(%s)
            group by c.cik, co.taxonomy, co.tag, u.unit_name, p.start_date, p.end_date, p.period_type
            having count(*) > 1 and bool_or(f.is_authoritative) = false
            order by c.cik, co.tag, p.end_date
            """,
            (sorted(ciks),),
        )
        cols = [d.name for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
