"""Stage 2e-b -- "latest filing wins" for annual and quarterly flow facts Stage 2e
left unresolved (2026-10-04).

Stage 2e (dedupe.py) marks EVERY row of a (company, concept, unit, period)
group non-authoritative when the filings disagree on the value, on the
reasoning that picking even the most recent filing would be a guess. That
leaves the period with no authoritative fact, so resolve() has nothing to
pick and derive_q4 cannot subtract from a missing full year. It was the
largest single cause of the open q4_not_derived findings (~40% of them).

The guess turned out to be a good one, checked rather than assumed. For
2,952 affected companies, every FY period whose filings disagreed was
compared with SEC's own XBRL Frames value (the figure SEC currently
publishes for that company and period):

    tag                                       holes   latest   majority  earliest
    NetIncomeLoss                             4,231   99.8%    73.7%     47.8%
    NetCashProvidedByUsedInOperatingActivities 3,269  99.9%    80.2%     38.3%
    Revenues                                  1,501  100.0%    74.6%     31.6%
    RevenueFromContractWithCustomerExcluding..  1,089  99.7%    74.7%     34.1%
    OperatingIncomeLoss                       3,534   99.9%    71.6%     24.5%
    GrossProfit                               1,687  100.0%    74.2%     30.8%

"Latest filed" held even where the filings differ by more than 2%, i.e. a
real restatement rather than rounding. Majority vote (what
mapper/dedup_majority_resolver.py uses for balance-sheet concepts) was wrong
roughly a quarter of the time on these flow concepts and earliest-filed far
more often, which is why neither is used here.

Quarters were validated the same way on a 400-company sample (2026-10-04),
discrete Q1-Q3 spans of 80-100 days against Frames' CY{year}Q{n} values:

    tag                 holes   latest   earliest
    NetIncomeLoss         823   100.0%    32.9%
    Revenues              440   100.0%    35.0%
    OperatingIncomeLoss 1,131   100.0%    21.4%
    GrossProfit           625   100.0%    27.8%

Deliberately narrow, because Stage 2e's caution was reasonable and only these
cases were measured:
  * annual: the six tags above; quarterly: only the four tags just above
    (cash flow's raw quarterly facts are year-to-date, so it was not measured
    and is not included, nor is RevenueFromContract...);
  * FY (340-380 days) and discrete Q1-Q3 (80-100 days) durations only;
  * only groups where NO row is authoritative and the values genuinely differ;
  * derived facts are never competitors.
It never overrides a fact Stage 2e already marked authoritative.

Every fact it promotes is recorded in core.fact_conflict_resolution (rule,
group size, value spread), so the change is auditable and reversible. Safe to
rerun: a rerun of dedupe.py resets these groups to all-non-authoritative, and
this stage then promotes the same facts again. Run it after dedupe and
restatements, before the derive stages.
"""

import json
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback
from scrooner_pipeline.common.periodic_forms import ANNUAL_FORMS_ALL, QUARTERLY_FORMS
from scrooner_pipeline.common.rule_flags import RULE_PERIODIC_FORM_ONLY, rule_enabled

logger = structlog.get_logger()

RULE = "latest_filed_fy_v1"
RULE_QUARTER = "latest_filed_quarter_v1"

# The tags the rule was validated against (taxonomy, tag).
VALIDATED_TAGS: list[tuple[str, str]] = [
    ("us-gaap", "NetIncomeLoss"),
    ("us-gaap", "NetCashProvidedByUsedInOperatingActivities"),
    ("us-gaap", "Revenues"),
    ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    ("us-gaap", "OperatingIncomeLoss"),
    ("us-gaap", "GrossProfit"),
    # Added 2026-10-17 after scripts/validate_latest_filed_vs_frames.py
    # (--kind fy, 600-company sample, latest-filed vs SEC Frames CY values):
    #   IncomeTaxExpenseBenefit            548/548 = 100.0%  (earliest 18.1%)
    #   IncomeLossFromContinuingOps...BeforeIncomeTaxes...  445/445 = 100.0%  (earliest 20.9%)
    #   NetCashProvidedByUsedInInvestingActivities  400/401 = 99.8%  (earliest 34.4%)
    #   NetCashProvidedByUsedInFinancingActivities  394/394 = 100.0% (earliest 33.5%)
    # The Q4-gap census found these four were the biggest non-authoritative
    # full-year holes outside the original six. Annual only: raw quarterly
    # cash-flow facts are year-to-date and were not measured.
    ("us-gaap", "IncomeTaxExpenseBenefit"),
    (
        "us-gaap",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    ),
    ("us-gaap", "NetCashProvidedByUsedInInvestingActivities"),
    ("us-gaap", "NetCashProvidedByUsedInFinancingActivities"),
]

# Quarterly validation covered only these four (see the docstring table).
VALIDATED_QUARTER_TAGS: list[tuple[str, str]] = [
    ("us-gaap", "NetIncomeLoss"),
    ("us-gaap", "Revenues"),
    ("us-gaap", "OperatingIncomeLoss"),
    ("us-gaap", "GrossProfit"),
]

FULL_YEAR_MIN_DAYS, FULL_YEAR_MAX_DAYS = 340, 380
QUARTER_MIN_DAYS, QUARTER_MAX_DAYS = 80, 100

# Which filings may WIN a period (2026-10-18). A Data Verifier check against the
# original filings of 47 promoted facts found: (1) proxy statements (DEF 14A and
# variants) and 10-Qs won annual values -- 2,798 DEF 14A + ~340 10-Q promotions --
# and a proxy's rounded pay-versus-performance footnote or a 10-Q's AOCI balance
# is not the annual figure; (2) when the copies differ only by sign, the latest
# filing is wrong about half the time (5 of 10), because Frames, the earlier
# validation, publishes the latest filing's own value and so cannot catch a sign
# error in it. Ineligible filings still count as copies of the period (so a lone
# 10-K can win when a proxy disagrees) but can never be the winner.
FY_ELIGIBLE_FORMS = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "8-K",
    "8-K/A",  # recast of prior years after a restatement or discontinued operation
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)
QUARTER_ELIGIBLE_FORMS = (
    "10-Q",
    "10-Q/A",
    "10-QT",
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "8-K",
    "8-K/A",
    "6-K",
    "6-K/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)


def eligible_forms(
    periodic_only: bool | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(annual winner forms, quarter winner forms). With rule
    source.periodic_form_only@1 on, 8-K, 8-K/A and 6-K are no longer eligible
    winners (WTRG: an 8-K furnishing American Water's statements beat WTRG's
    own 10-K; ledger 2026-10-22) and the lists are built from
    common/periodic_forms.py; flag off keeps the historical lists."""
    if periodic_only is None:
        periodic_only = rule_enabled(RULE_PERIODIC_FORM_ONLY)
    if not periodic_only:
        return FY_ELIGIBLE_FORMS, QUARTER_ELIGIBLE_FORMS
    quarter = tuple(dict.fromkeys(QUARTERLY_FORMS + ANNUAL_FORMS_ALL))
    return ANNUAL_FORMS_ALL, quarter


# Picks the latest-filed row of each unresolved group (ties go to the highest
# fact id, i.e. the one inserted last) and records it in the audit table in
# the same statement, so a promoted fact can never be missing its audit row.
PROMOTE_SQL = """
with candidates as (
    select f.id, f.company_id, f.concept_id, f.unit_id, f.period_id, f.value,
           fl.filing_date, f.is_authoritative, f.is_derived,
           case when p.fiscal_period = 'FY' then %(rule)s else %(rule_quarter)s end as rule,
           (   (p.fiscal_period = 'FY' and fl.form = any(%(fy_forms)s))
            or (p.fiscal_period in ('Q1', 'Q2', 'Q3') and fl.form = any(%(quarter_forms)s))
           ) as eligible,
           row_number() over w as rn,
           count(*) over w as n,
           bool_or(f.is_authoritative) over w as any_auth,
           min(f.value) over w as vmin,
           max(f.value) over w as vmax,
           bool_or(f.value > 0) over w as has_pos,
           bool_or(f.value < 0) over w as has_neg,
           min(abs(f.value)) over w as amin,
           max(abs(f.value)) over w as amax
    from core.fact f
    join core.period p on p.id = f.period_id
    join core.filing fl on fl.id = f.filing_id
    where f.company_id = any(%(company_ids)s)
      and not f.is_derived
      and p.period_type = 'duration'
      and (
          (p.fiscal_period = 'FY'
           and f.concept_id = any(%(concept_ids)s)
           and (p.end_date - p.start_date) between %(min_days)s and %(max_days)s)
          or (p.fiscal_period in ('Q1', 'Q2', 'Q3')
              and f.concept_id = any(%(quarter_concept_ids)s)
              and (p.end_date - p.start_date) between %(q_min_days)s and %(q_max_days)s)
      )
    window w as (partition by f.company_id, f.concept_id, f.unit_id, f.period_id
                 order by (   (p.fiscal_period = 'FY' and fl.form = any(%(fy_forms)s))
                           or (p.fiscal_period in ('Q1', 'Q2', 'Q3') and fl.form = any(%(quarter_forms)s))
                          ) desc,
                          fl.filing_date desc, f.id desc
                 rows between unbounded preceding and unbounded following)
),
winners as (
    select id, n, vmin, vmax, rule from candidates
    where rn = 1 and eligible and n > 1 and not any_auth and vmin <> vmax
      -- copies that differ only by sign (same magnitude, both signs present) are
      -- quarantined: no filing can be trusted over another without its own
      -- arithmetic (pre-tax - tax = net income), which this stage does not do
      and not (has_pos and has_neg and amin = amax)
),
promoted as (
    update core.fact f set is_authoritative = true
    from winners w
    where f.id = w.id and not f.is_authoritative
    returning f.id, w.n, w.vmin, w.vmax, w.rule
)
insert into core.fact_conflict_resolution (fact_id, rule, group_size, value_min, value_max)
select id, rule, n, vmin, vmax from promoted
on conflict (fact_id) do update
    set rule = excluded.rule, group_size = excluded.group_size,
        value_min = excluded.value_min, value_max = excluded.value_max,
        resolved_at = now()
"""


def _concept_ids(conn: psycopg.Connection, tags: list[tuple[str, str]]) -> list[int]:
    with conn.cursor() as cur:
        ids = []
        for taxonomy, tag in tags:
            cur.execute(
                "select id from core.concept where taxonomy = %s and tag = %s",
                (taxonomy, tag),
            )
            row = cur.fetchone()
            if row:
                ids.append(row[0])
        return ids


def promote_for_companies(
    conn: psycopg.Connection,
    company_ids: list[int],
    concept_ids: list[int],
    quarter_concept_ids: list[int],
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            PROMOTE_SQL,
            {
                "company_ids": company_ids,
                "concept_ids": concept_ids,
                "quarter_concept_ids": quarter_concept_ids,
                "min_days": FULL_YEAR_MIN_DAYS,
                "max_days": FULL_YEAR_MAX_DAYS,
                "q_min_days": QUARTER_MIN_DAYS,
                "q_max_days": QUARTER_MAX_DAYS,
                "rule": RULE,
                "rule_quarter": RULE_QUARTER,
                "fy_forms": list(eligible_forms()[0]),
                "quarter_forms": list(eligible_forms()[1]),
            },
        )
        promoted = cur.rowcount
    conn.commit()
    return promoted


def _promote_with_split(
    conn: psycopg.Connection,
    ciks: list[str],
    company_ids: list[int],
    concept_ids: list[int],
    quarter_concept_ids: list[int],
    totals: dict,
) -> psycopg.Connection:
    """Promote one batch; if it hits the pooler's hard statement_timeout
    (2 minutes, not overridable from the client -- see pipeline/CLAUDE.md),
    split the batch in half and retry, down to a single company, which is
    only then recorded as an error. A fixed batch size was wrong both ways:
    25 companies timed out on a busy database once quarters were added (every
    failed batch silently skipped its companies and the audit table stayed
    empty), while a safe-for-the-worst-case size would make the common case
    needlessly slow. Safe to retry: the statement is a single atomic update,
    so a cancelled batch changed nothing."""
    try:
        totals["promoted"] += promote_for_companies(
            conn, company_ids, concept_ids, quarter_concept_ids
        )
        totals["batches"] += 1
        return conn
    except psycopg.errors.QueryCanceled as exc:
        conn = safe_rollback(conn, stage="conflict_latest_filed", cik=ciks[0])
        if len(company_ids) > 1:
            totals["splits"] += 1
            mid = len(company_ids) // 2
            for lo, hi in ((0, mid), (mid, len(company_ids))):
                conn = _promote_with_split(
                    conn,
                    ciks[lo:hi],
                    company_ids[lo:hi],
                    concept_ids,
                    quarter_concept_ids,
                    totals,
                )
            return conn
        totals["errored"] += 1
        log_error(conn, "core.normalizer_error", ciks[0], "conflict_latest_filed", exc)
        return safe_rollback(conn, stage="conflict_latest_filed", cik=ciks[0])
    except Exception as exc:
        totals["errored"] += len(company_ids)
        log_error(conn, "core.normalizer_error", ciks[0], "conflict_latest_filed", exc)
        return safe_rollback(conn, stage="conflict_latest_filed", cik=ciks[0])


def resolve_latest_filed(conn: psycopg.Connection, ciks: set[str]) -> dict:
    """Promote the latest-filed fact for each unresolved group of the
    validated tags. Batched by company (index-backed); a batch that times out
    is split and retried, so a full population is many small statements,
    never one large one."""
    concept_ids = _concept_ids(conn, VALIDATED_TAGS)
    quarter_concept_ids = _concept_ids(conn, VALIDATED_QUARTER_TAGS)
    totals = {"considered": 0, "batches": 0, "splits": 0, "errored": 0, "promoted": 0}
    if not concept_ids:
        return totals
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())
    ordered = sorted(company_id_by_cik)
    totals["considered"] = len(ordered)
    batch_size = 10
    for i in range(0, len(ordered), batch_size):
        batch_ciks = ordered[i : i + batch_size]
        batch_ids = [company_id_by_cik[c] for c in batch_ciks]
        conn = _promote_with_split(
            conn, batch_ciks, batch_ids, concept_ids, quarter_concept_ids, totals
        )
    logger.info("conflict_latest_filed.done", rules=[RULE, RULE_QUARTER], **totals)
    return totals


# ---------------------------------------------------------------------------
# Retiring winners the ban makes ineligible (rule source.periodic_form_only@1)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Copy:
    fact_id: int
    value: Decimal
    form: str | None
    filing_date: object
    is_authoritative: bool
    is_derived: bool = False


BAN_VALUE_TO_BLANK = "value_to_blank"
BAN_VALUE_CHANGED = "value_changed"
BAN_VALUE_SAME = "value_same"


def new_winner(
    copies: Sequence[Copy], eligible: Sequence[str], old_winner_id: int
) -> Copy | None:
    """What PROMOTE_SQL would promote for this group once `old_winner_id` is
    demoted: the latest-filed ELIGIBLE copy, only if more than one copy exists,
    none is authoritative, the values differ, and the copies do not differ by
    sign alone. None = the group stays blank."""
    rest = [
        Copy(
            c.fact_id,
            c.value,
            c.form,
            c.filing_date,
            False if c.fact_id == old_winner_id else c.is_authoritative,
            c.is_derived,
        )
        for c in copies
        if not c.is_derived
    ]
    if len(rest) < 2 or any(c.is_authoritative for c in rest):
        return None
    values = [c.value for c in rest]
    if min(values) == max(values):
        return None
    mags = [abs(v) for v in values]
    if (
        any(v > 0 for v in values)
        and any(v < 0 for v in values)
        and min(mags) == max(mags)
    ):
        return None
    ordered = sorted(
        rest, key=lambda c: (c.form in eligible, c.filing_date, c.fact_id), reverse=True
    )
    top = ordered[0]
    return top if top.form in eligible else None


def classify_ban(
    copies: Sequence[Copy], eligible: Sequence[str], old_winner_id: int
) -> str:
    old = next(c for c in copies if c.fact_id == old_winner_id)
    new = new_winner(copies, eligible, old_winner_id)
    if new is None:
        return BAN_VALUE_TO_BLANK
    return BAN_VALUE_SAME if new.value == old.value else BAN_VALUE_CHANGED


WINNERS_NOT_ELIGIBLE_SQL = """
select r.fact_id, r.rule, fl.form
from core.fact_conflict_resolution r
join core.fact f on f.id = r.fact_id
join core.filing fl on fl.id = f.filing_id
where f.company_id = any(%(company_ids)s)
  and (   (r.rule = %(rule)s         and fl.form <> all(%(fy_forms)s))
       or (r.rule = %(rule_quarter)s and fl.form <> all(%(quarter_forms)s)))
order by r.fact_id
"""


def find_ineligible_winners(
    conn: psycopg.Connection, company_ids: Sequence[int]
) -> list[tuple[int, str, str]]:
    """Read-only: promotions already stored whose winner form the ban makes
    ineligible (8-K recasts, and the DEF 14A / DEFR14A residue of the 2026-10-18
    form fix). (fact_id, rule, form). Judged against the BAN lists, whatever the flag."""
    fy, quarter = eligible_forms(periodic_only=True)
    with conn.cursor() as cur:
        cur.execute(
            WINNERS_NOT_ELIGIBLE_SQL,
            {
                "company_ids": list(company_ids),
                "rule": RULE,
                "rule_quarter": RULE_QUARTER,
                "fy_forms": list(fy),
                "quarter_forms": list(quarter),
            },
        )
        return cur.fetchall()


def retire_ineligible_winners(
    conn: psycopg.Connection, winners: Sequence[tuple[int, str, str]], backup_path: Path
) -> dict[str, int]:
    """The only writer: demote these promoted facts and delete their audit rows,
    so the next conflict-latest-filed run promotes the best ELIGIBLE copy (or
    leaves the period blank). Needs a backup file that already holds every id;
    scoped by fact id only; does not commit."""
    ids = sorted({w[0] for w in winners})
    if not ids:
        return {"demoted": 0, "audit_rows_deleted": 0}
    if not backup_path.exists():
        raise FileNotFoundError(
            f"backup {backup_path} missing: refusing to retire winners"
        )
    backed = {
        json.loads(x)["fact_id"]
        for x in backup_path.read_text().splitlines()
        if x.strip()
    }
    if set(ids) - backed:
        raise ValueError(f"{len(set(ids) - backed)} winners are not in the backup")
    demoted = deleted = 0
    with conn.cursor() as cur:
        for i in range(0, len(ids), 5000):
            chunk = ids[i : i + 5000]
            cur.execute(
                "update core.fact set is_authoritative = false where id = any(%s) and is_authoritative",
                (chunk,),
            )
            demoted += cur.rowcount
            cur.execute(
                "delete from core.fact_conflict_resolution where fact_id = any(%s)",
                (chunk,),
            )
            deleted += cur.rowcount
    return {"demoted": demoted, "audit_rows_deleted": deleted}


def write_winner_backup(
    conn: psycopg.Connection, winners: Sequence[tuple[int, str, str]], path: Path
) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with conn.cursor() as cur, path.open("w", encoding="utf-8") as fh:
        for fact_id, rule, form in winners:
            cur.execute(
                "select r.fact_id, r.rule, r.group_size, r.value_min, r.value_max, f.company_id, f.concept_id, f.unit_id, f.period_id, f.value "
                "from core.fact_conflict_resolution r join core.fact f on f.id = r.fact_id where r.fact_id = %s",
                (fact_id,),
            )
            row = cur.fetchone()
            cols = [c.name for c in cur.description]
            fh.write(
                json.dumps(
                    {**dict(zip(cols, row)), "form": form}, default=str, sort_keys=True
                )
                + "\n"
            )
            n += 1
    return n
