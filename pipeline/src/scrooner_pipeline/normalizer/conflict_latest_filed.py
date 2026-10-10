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

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback

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

# Picks the latest-filed row of each unresolved group (ties go to the highest
# fact id, i.e. the one inserted last) and records it in the audit table in
# the same statement, so a promoted fact can never be missing its audit row.
PROMOTE_SQL = """
with candidates as (
    select f.id, f.company_id, f.concept_id, f.unit_id, f.period_id, f.value,
           fl.filing_date, f.is_authoritative, f.is_derived,
           case when p.fiscal_period = 'FY' then %(rule)s else %(rule_quarter)s end as rule,
           row_number() over w as rn,
           count(*) over w as n,
           bool_or(f.is_authoritative) over w as any_auth,
           min(f.value) over w as vmin,
           max(f.value) over w as vmax
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
                 order by fl.filing_date desc, f.id desc
                 rows between unbounded preceding and unbounded following)
),
winners as (
    select id, n, vmin, vmax, rule from candidates
    where rn = 1 and n > 1 and not any_auth and vmin <> vmax
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
