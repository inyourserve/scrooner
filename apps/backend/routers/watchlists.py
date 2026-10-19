"""Authenticated personal watchlist endpoints.

The API owns user scoping even though the table also has RLS as defense in
depth. Company IDs are canonical; ticker and display metadata are resolved at
read time so symbol changes never orphan a saved company.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from scrooner_pipeline.common import staleness
from scrooner_pipeline.common.sector_applicability import (
    BANK_SUPPRESSED_METRICS,
    load_bank_company_ids,
)

from auth import get_current_user_id
from db_pool import get_pooled_connection


router = APIRouter(prefix="/v1/watchlist", tags=["watchlist"])

# Staleness guard (common/staleness.py): the company's own latest filed
# period, selected in the same statement as the rest of the row.
latest_filed_period_sql = staleness.latest_filed_period_sql("w.company_id")


class WatchlistCreate(BaseModel):
    company_id: int = Field(gt=0)


class WatchlistUpdate(BaseModel):
    note: str | None = Field(default=None, max_length=2000)
    mark_reviewed: bool = False


@router.get("")
def list_watchlist(
    company_id: int | None = Query(default=None, gt=0),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                select w.company_id, c.company_name, c.primary_ticker,
                       c.sector, w.created_at, w.note, w.reviewed_at,
                       price.price, price.previous_price, price.bar_timestamp,
                       valuation.value as trailing_pe,
                       filing.form, filing.filing_date, filing.accession_number,
                       (filing.filing_date::timestamptz > coalesce(w.reviewed_at, w.created_at)) as has_unreviewed,
                       c.cik,
                       valuation.period_label as valuation_period_label,
                       valuation.period_end as valuation_period_end,
                       {latest_filed_period_sql} as latest_filed_period
                from app.watchlist_item w
                join core.company c on c.id = w.company_id
                left join lateral (
                    select max(price) filter (where rank = 1) as price,
                           max(price) filter (where rank = 2) as previous_price,
                           max(bar_timestamp) filter (where rank = 1) as bar_timestamp
                    from (
                        select p.price, p.bar_timestamp,
                               row_number() over (order by p.price_date desc) as rank
                        from core.market_price_alpaca p
                        where p.company_id = w.company_id
                        order by p.price_date desc limit 2
                    ) ranked_price
                ) price on true
                left join lateral (
                    select mv.value, mv.period_label, mv.period_end
                    from analytics.metric_value mv
                    join analytics.metric_definition md on md.id = mv.metric_definition_id
                    where mv.company_id = w.company_id and md.metric_name = 'trailing_pe'
                      and mv.value is not null
                    order by (mv.period_label = 'TTM') desc, mv.period_end desc limit 1
                ) valuation on true
                left join lateral (
                    select f.form, f.filing_date, f.accession_number
                    from core.filing f
                    where f.company_id = w.company_id
                      and f.form in ('10-Q', '10-K', '20-F', '40-F')
                    order by f.filing_date desc nulls last limit 1
                ) filing on true
                where w.user_id = %s and (%s::bigint is null or w.company_id = %s)
                order by has_unreviewed desc nulls last, w.created_at desc, w.id desc
                """,
                (user_id, company_id, company_id),
            )
            rows = cur.fetchall()
            company_ids = [row[0] for row in rows]
            fundamentals = {}
            updates = {}
            stale_reasons: dict[int, dict[str, str]] = {}
            latest_filed = {row[0]: row[18] for row in rows}
            for row in rows:
                reason = staleness.staleness_reason(row[17], row[16], row[18]) if row[10] is not None else None
                if reason is not None:
                    stale_reasons.setdefault(row[0], {})["trailing_pe"] = reason
            if company_ids:
                # Bank applicability (common/sector_applicability.py): the
                # fundamentals below include operating_margin, fcf and
                # revenue_growth_yoy, all suppressed for banks.
                bank_ids = load_bank_company_ids(cur, company_ids)
                cur.execute(
                    """
                    with values_ranked as (
                        select mv.company_id, md.metric_name, mv.value, mv.period_end,
                               mv.period_label,
                               row_number() over (partition by mv.company_id, md.metric_name order by mv.period_end desc) as rank
                        from analytics.metric_value mv
                        join analytics.metric_definition md on md.id = mv.metric_definition_id
                        where mv.company_id = any(%s::bigint[])
                          and md.metric_name in ('revenue_growth_yoy', 'operating_margin', 'fcf')
                          and mv.period_label in ('Q1', 'Q2', 'Q3', 'Q4') and mv.value is not null
                    ), eps_ranked as (
                        select cf.company_id, cf.value, p.end_date, p.fiscal_period,
                               row_number() over (partition by cf.company_id order by p.end_date desc) as rank
                        from analytics.canonical_fact cf
                        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
                        join core.period p on p.id = cf.period_id
                        where cf.company_id = any(%s::bigint[]) and cc.name = 'diluted_eps'
                          and p.fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4')
                    )
                    select company_id, metric_name, value::text, period_end::text, period_label, rank
                    from values_ranked where rank in (1, 5)
                    union all
                    select company_id, 'diluted_eps', value::text, end_date::text, fiscal_period, rank
                    from eps_ranked where rank in (1, 5)
                    order by company_id, metric_name, rank
                    """,
                    (company_ids, company_ids),
                )
                fact_rows = cur.fetchall()
                # Staleness guard (common/staleness.py): decided on the LATEST
                # value (rank 1) only. Rank 5 is the year-ago comparative and
                # is naturally about a year older, so it is never judged
                # alone; it goes with its latest value.
                for fact in fact_rows:
                    if fact[5] != 1 or (fact[0] in bank_ids and fact[1] in BANK_SUPPRESSED_METRICS):
                        continue
                    reason = staleness.staleness_reason(fact[3], fact[4], latest_filed.get(fact[0]))
                    if reason is not None:
                        stale_reasons.setdefault(fact[0], {})[fact[1]] = reason
                for fact in fact_rows:
                    if fact[0] in bank_ids and fact[1] in BANK_SUPPRESSED_METRICS:
                        continue
                    if fact[1] in stale_reasons.get(fact[0], {}):
                        continue
                    entry = fundamentals.setdefault(fact[0], {}).setdefault(fact[1], {})
                    entry["latest" if fact[5] == 1 else "previous"] = {
                        "value": fact[2], "period_end": fact[3], "period_label": fact[4]
                    }
                cur.execute(
                    """
                    select company_id, form, filing_date::text, accession_number, cik, is_unreviewed
                    from (
                        select f.company_id, f.form, f.filing_date, f.accession_number, c.cik,
                               (f.filing_date::timestamptz > coalesce(w.reviewed_at, w.created_at)) as is_unreviewed,
                               row_number() over (partition by f.company_id order by f.filing_date desc) as rank
                        from core.filing f
                        join core.company c on c.id = f.company_id
                        join app.watchlist_item w on w.company_id = f.company_id and w.user_id = %s
                        where f.company_id = any(%s::bigint[])
                          and f.form in ('10-Q', '10-K', '20-F', '40-F')
                    ) recent where rank <= 5 order by company_id, filing_date desc
                    """,
                    (user_id, company_ids),
                )
                for update in cur.fetchall():
                    updates.setdefault(update[0], []).append({
                        "form": update[1], "filed_at": update[2], "accession_number": update[3],
                        "is_unreviewed": bool(update[5]),
                        "source_url": f"https://www.sec.gov/Archives/edgar/data/{update[4].lstrip('0')}/{update[3].replace('-', '')}/{update[3]}-index.html",
                    })
    items = [
        {
            "company_id": row[0],
            "company_name": row[1],
            "ticker": row[2],
            "sector": row[3],
            "created_at": str(row[4]),
            "note": row[5],
            "reviewed_at": str(row[6]) if row[6] else None,
            "price": str(row[7]) if row[7] is not None else None,
            "previous_price": str(row[8]) if row[8] is not None else None,
            "price_as_of": str(row[9]) if row[9] else None,
            "valuation": (
                {"label": "P/E", "value": str(row[10])}
                if row[10] is not None and "trailing_pe" not in stale_reasons.get(row[0], {})
                else None
            ),
            "latest_update": ({
                "form": row[11], "filed_at": str(row[12]), "accession_number": row[13],
                "source_url": f"https://www.sec.gov/Archives/edgar/data/{row[15].lstrip('0')}/{row[13].replace('-', '')}/{row[13]}-index.html",
            } if row[11] else None),
            "has_unreviewed": bool(row[14]),
            "next_earnings": None,
            "fundamentals": fundamentals.get(row[0], {}),
            **({"suppressed_reasons": stale_reasons[row[0]]} if row[0] in stale_reasons else {}),
            "updates": updates.get(row[0], []),
        }
        for row in rows
    ]
    return {"contains": bool(items), "items": items}


@router.patch("/{company_id}")
def update_watchlist_item(
    company_id: int,
    body: WatchlistUpdate,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    note = body.note.strip() if body.note is not None else None
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                update app.watchlist_item
                set note = case when %s then %s else note end,
                    reviewed_at = case when %s then now() else reviewed_at end,
                    updated_at = now()
                where user_id = %s and company_id = %s
                returning note, reviewed_at
                """,
                (body.note is not None, note, body.mark_reviewed, user_id, company_id),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Company is not in your watchlist")
            if body.mark_reviewed:
                cur.execute(
                    "insert into app.watchlist_review (user_id, company_id) values (%s, %s)",
                    (user_id, company_id),
                )
    return {"company_id": company_id, "note": row[0], "reviewed_at": str(row[1]) if row[1] else None}


@router.post("", status_code=201)
def add_to_watchlist(
    body: WatchlistCreate,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into app.watchlist_item (user_id, company_id)
                select %s, c.id from core.company c where c.id = %s
                on conflict (user_id, company_id) do nothing
                returning company_id
                """,
                (user_id, body.company_id),
            )
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    "select 1 from core.company where id = %s",
                    (body.company_id,),
                )
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Company not found")
    return {"company_id": body.company_id, "in_watchlist": True}


@router.delete("/{company_id}")
def remove_from_watchlist(
    company_id: int,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                delete from app.watchlist_item
                where user_id = %s and company_id = %s
                returning company_id
                """,
                (user_id, company_id),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Company is not in your watchlist")
    return {"company_id": company_id, "in_watchlist": False}
