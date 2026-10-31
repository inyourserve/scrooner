"""Faithful Python port of apps/app/lib/company/db.ts::getCompanyPageData
(2026-10-03, by explicit founder direction: Next.js must call an API for
the company page, never hold a direct Postgres connection, matching the
Screener's architecture for consistency -- doc 04/17's original "Next.js
reads Postgres directly" design is deliberately superseded here).

The SQL text below is copied verbatim from db.ts (same CTEs, same
column list, same jsonb_build_object shape) with exactly three
mechanical substitutions, none of which change behavior:
  - `${ticker}`         -> `%(ticker)s` (still a bound parameter)
  - `${EQUITY_ONLY_SQL}` -> its own literal text, inlined (it was never
    a parameter, just a reusable SQL fragment in the TS client)
  - `${HISTORY_FLOOR}`  -> the literal '2015-01-01' (a fixed constant in
    db.ts too, never user input)
This is a deliberate choice over re-deriving the query's logic: the SQL
is unchanged, so the only real risk is the substitution itself, checked
by running both versions side by side and diffing output (see
doc/learnings/2026-10-03-company-page-api-port.md).

assembleStatement()/the metric_history grouping are also ported 1:1
from db.ts, same algorithm, same tie-breaks.

Bank applicability (2026-10-19) is the one deliberate addition to that port:
`is_bank` (SIC 6020-6036 plus the company's own bank-shaped filed tags, see
pipeline common/sector_applicability.py) is computed in the same query, and
for a bank the metrics, statement rows, FY history and peer cells in the
suppress list are returned null with a stated reason. A non-bank's output is
unchanged. Cached pages (cache.py) keep the old values until their TTL expires.

Staleness guard (2026-10-19, pipeline common/staleness.py): the company's own
latest filed period comes back inside the same query (`latest_filed_period`),
and a Key Metrics value, a book value, an FY-history series or a peer cell
that is more than 1 fiscal year (annual) / 2 quarters (quarterly, TTM) behind
it is returned null with the reason 'not in the latest filing (last reported
...)'. The statement tables are history grids with explicit period headers and
are left as stored.
"""

from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation

import psycopg

from scrooner_pipeline.common import staleness
from scrooner_pipeline.common.sector_applicability import (
    BANK_SUPPRESSED_METRICS,
    bank_predicate_sql,
    metric_suppression_reason,
    statement_line_suppression_reason,
)

latest_filed_period_sql = staleness.latest_filed_period_sql
stale_predicate_sql = staleness.stale_predicate_sql

_EQUITY_ONLY_SQL = (
    "(l.security_type is null or l.security_type in "
    "('Common Stock', 'ADR', 'REIT', 'MLP', 'Tracking Stk', 'Ltd Part'))"
)
_HISTORY_FLOOR = "2015-01-01"

# Bank applicability (2026-10-19, common/sector_applicability.py): the peer
# table's four metrics, of which a bank peer's suppressed ones are left out in
# SQL so they neither display nor decide the peer ordering.
_PEER_METRIC_NAMES = ("roe", "roic", "revenue_growth_3y_cagr", "net_margin")
_PEER_BANK_SUPPRESSED_SQL = ", ".join(
    f"'{name}'" for name in _PEER_METRIC_NAMES if name in BANK_SUPPRESSED_METRICS
)

_QUERY = f"""
with selected_company as (
  select c.id, c.cik, coalesce(c.display_name, c.company_name) as company_name,
         c.sic_code, c.sic_description,
         c.sector, c.y_sector, c.y_industry, c.status, l.ticker,
         c.about_text, c.y_about_text, c.ein, c.business_address_line1,
         c.business_address_city, c.business_address_state,
         c.business_address_zip, c.business_phone, c.website, c.y_website,
         {bank_predicate_sql("c")} as is_bank
  from core.company c
  join core.listing l on l.company_id = c.id
  where lower(l.ticker) = lower(%(ticker)s) and {_EQUITY_ONLY_SQL}
  order by (l.effective_to is null) desc
  limit 1
),
peer_companies as (
  select distinct on (c.id) c.id, l.ticker, coalesce(c.display_name, c.company_name) as company_name, 'industry'::text as match_basis,
         {bank_predicate_sql("c")} as is_bank,
         {latest_filed_period_sql("c.id")} as latest_filed_period
  from core.company c
  join core.listing l on l.company_id = c.id
  join selected_company company on company.y_industry is not null and c.y_industry = company.y_industry
  where c.status = 'active'
    and c.id != company.id
    and l.effective_to is null
    and l.ticker is not null
    and {_EQUITY_ONLY_SQL}
  order by c.id, (l.security_type = 'Common Stock') desc nulls last
),
peer_metrics as (
  select mv.company_id, md.metric_name, mv.value,
         row_number() over (
           partition by mv.company_id, md.metric_name
           order by (mv.period_label = 'TTM') desc, mv.period_end desc
         ) as rn
  from analytics.metric_value mv
  join analytics.metric_definition md on md.id = mv.metric_definition_id
  join peer_companies p on p.id = mv.company_id
  where md.metric_name in ('roe', 'roic', 'revenue_growth_3y_cagr', 'net_margin')
    and mv.value is not null
    and not (p.is_bank and md.metric_name in ({_PEER_BANK_SUPPRESSED_SQL}))
    and not coalesce({stale_predicate_sql("mv.period_label", "mv.period_end", "p.latest_filed_period")}, false)
    and (md.metric_name = 'revenue_growth_3y_cagr' or (mv.value >= -2.0 and mv.value <= 2.0))
),
ranked_metrics as (
  select md.metric_name, mv.value::text as value, mv.period_label,
         mv.period_end::text as period_end, mv.is_null_reason,
         row_number() over (
           partition by md.metric_name
           order by (mv.period_label = 'TTM') desc, mv.period_end desc
         ) as rank
  from analytics.metric_value mv
  join analytics.metric_definition md on md.id = mv.metric_definition_id
  join selected_company company on company.id = mv.company_id
  where mv.period_end >= '{_HISTORY_FLOOR}' and mv.period_end <= current_date + interval '30 days'
),
annual_fiscal_periods as (
  select distinct fact.company_id, period.fiscal_year, period.fiscal_period
  from analytics.canonical_fact fact
  join core.period period on period.id = fact.period_id
  join selected_company company on company.id = fact.company_id
  where period.fiscal_period = 'FY' and period.end_date >= '{_HISTORY_FLOOR}' and period.end_date <= current_date + interval '30 days'
  order by period.fiscal_year desc
  limit 7
),
quarterly_fiscal_periods_distinct as (
  select distinct fact.company_id, period.fiscal_year, period.fiscal_period
  from analytics.canonical_fact fact
  join core.period period on period.id = fact.period_id
  join selected_company company on company.id = fact.company_id
  where period.fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4') and period.end_date >= '{_HISTORY_FLOOR}' and period.end_date <= current_date + interval '30 days'
),
quarterly_fiscal_periods as (
  select *, row_number() over (order by fiscal_year desc, fiscal_period desc) as rn
  from quarterly_fiscal_periods_distinct
),
annual_periods as (
  select distinct period.id, period.end_date
  from core.period period
  join annual_fiscal_periods afp
    on afp.company_id = period.company_id
   and afp.fiscal_year = period.fiscal_year
   and afp.fiscal_period = period.fiscal_period
),
quarterly_periods as (
  select distinct period.id, period.end_date
  from core.period period
  join (select * from quarterly_fiscal_periods order by rn limit 8) qfp
    on qfp.company_id = period.company_id
   and qfp.fiscal_year = period.fiscal_year
   and qfp.fiscal_period = period.fiscal_period
),
displayed_periods as (
  select id from annual_periods
  union
  select id from quarterly_periods
),
statement_rows as (
  select sl.statement, sl.display_order::numeric as display_order, sl.display_label,
         p.fiscal_year, p.fiscal_period, p.end_date::text as period_end,
         cf.value::text as value
  from analytics.statement_line sl
  cross join selected_company company
  left join analytics.canonical_fact cf
    on cf.canonical_concept_id = sl.canonical_concept_id
   and cf.company_id = company.id
  left join core.period p on p.id = cf.period_id
  where sl.statement in ('income_statement', 'balance_sheet', 'cash_flow')
    and (p.id in (select id from displayed_periods) or p.id is null)
),
ebitda_rows as (
  select 'income_statement'::text as statement,
         5.5::numeric as display_order,
         'EBITDA'::text as display_label,
         p.fiscal_year, p.fiscal_period, p.end_date::text as period_end,
         mv.value::text as value
  from core.period p
  join selected_company company on company.id = p.company_id
  join analytics.metric_value mv
    on mv.company_id = p.company_id
   and mv.period_end = p.end_date
   and mv.period_label = p.fiscal_period
  join analytics.metric_definition md
    on md.id = mv.metric_definition_id and md.metric_name = 'ebitda'
  where p.id in (select id from displayed_periods)
    and mv.value is not null
),
fcf_rows as (
  select 'cash_flow'::text as statement,
         4.5::numeric as display_order,
         'Free Cash Flow'::text as display_label,
         p.fiscal_year, p.fiscal_period, p.end_date::text as period_end,
         mv.value::text as value
  from core.period p
  join selected_company company on company.id = p.company_id
  join analytics.metric_value mv
    on mv.company_id = p.company_id
   and mv.period_end = p.end_date
   and mv.period_label = p.fiscal_period
  join analytics.metric_definition md
    on md.id = mv.metric_definition_id and md.metric_name = 'fcf'
  where p.id in (select id from displayed_periods)
    and mv.value is not null
),
combined_statement_rows as (
  select * from statement_rows
  union all
  select * from ebitda_rows
  union all
  select * from fcf_rows
),
metric_history_rows as (
  select md.metric_name, mv.value::text as value,
         mv.period_end::text as period_end,
         row_number() over (
           partition by md.metric_name order by mv.period_end desc
         ) as rank
  from analytics.metric_value mv
  join analytics.metric_definition md on md.id = mv.metric_definition_id
  join selected_company company on company.id = mv.company_id
  where md.metric_name in (
    'roe', 'roic', 'fcf', 'fcf_margin', 'revenue_growth_yoy',
    'operating_margin', 'net_margin', 'debt_to_equity',
    'net_debt_ebitda', 'share_dilution_trend'
  )
    and mv.period_label = 'FY'
    and mv.period_end >= '{_HISTORY_FLOOR}' and mv.period_end <= current_date + interval '30 days'
)
select
  jsonb_build_object(
    'id', company.id,
    'cik', company.cik,
    'company_name', company.company_name,
    'sic_code', company.sic_code,
    'sic_description', company.sic_description,
    'sector', company.sector,
    'y_industry', company.y_industry,
    'status', company.status,
    'ticker', company.ticker,
    'about_text', coalesce(company.about_text, company.y_about_text),
    'ein', company.ein,
    'business_address_line1', company.business_address_line1,
    'business_address_city', company.business_address_city,
    'business_address_state', company.business_address_state,
    'business_address_zip', company.business_address_zip,
    'business_phone', company.business_phone,
    'website', coalesce(company.website, regexp_replace(company.y_website, '^https?://', '')),
    'is_bank', company.is_bank,
    'latest_filed_period', {latest_filed_period_sql("company.id")}::text,
    'book_value_period_end', (
      select period.end_date::text
      from analytics.canonical_fact fact
      join analytics.canonical_concept concept
        on concept.id = fact.canonical_concept_id
      join core.period period on period.id = fact.period_id
      where fact.company_id = company.id
        and concept.name = 'stockholders_equity'
        and period.end_date >= '{_HISTORY_FLOOR}' and period.end_date <= current_date + interval '30 days'
      order by period.end_date desc
      limit 1
    )
  ) as company,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'metric_name', metric_name,
      'value', value,
      'period_label', period_label,
      'period_end', period_end,
      'is_null_reason', is_null_reason
    ) order by metric_name)
    from ranked_metrics where rank = 1
  ), '[]'::jsonb) as metrics,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'statement', statement,
      'display_order', display_order,
      'display_label', display_label,
      'fiscal_year', fiscal_year,
      'fiscal_period', fiscal_period,
      'period_end', period_end,
      'value', value
    ) order by statement, display_order, period_end)
    from combined_statement_rows
  ), '[]'::jsonb) as statements,
  coalesce((
    select jsonb_agg(to_jsonb(recent) order by recent.filing_date desc)
    from (
      select f.form, f.filing_date::text as filing_date,
             f.accession_number, f.items
      from core.filing f
      where f.company_id = company.id and f.filing_date is not null
      order by f.filing_date desc
      limit 24
    ) recent
  ), '[]'::jsonb) as filings,
  coalesce((
    select jsonb_agg(to_jsonb(recent) order by recent.transaction_date desc)
    from (
      select it.reporting_owner_name, it.officer_title,
             it.is_director, it.is_officer,
             it.is_ten_percent_owner,
             it.transaction_date::text as transaction_date,
             it.transaction_code, it.acquired_disposed_code,
             it.shares::text as shares,
             it.price_per_share::text as price_per_share,
             it.shares_owned_following::text as shares_owned_following,
             it.is_10b5_1_plan, it.accession_number
      from core.insider_transaction it
      where it.company_id = company.id
        and it.transaction_date is not null
        and it.transaction_date >= (current_date - interval '12 months')
      order by it.transaction_date desc
      limit 15
    ) recent
  ), '[]'::jsonb) as insider_transactions,
  coalesce((
    select jsonb_agg(to_jsonb(recent) order by recent.filing_date desc nulls last)
    from (
      select ownership.filer_name, ownership.schedule_type,
             ownership.is_amendment,
             ownership.filing_date::text as filing_date,
             ownership.accession_number
      from core.beneficial_ownership ownership
      where ownership.company_id = company.id
      order by ownership.filing_date desc nulls last
      limit 15
    ) recent
  ), '[]'::jsonb) as beneficial_ownership,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'filer_name', holder.filer_name,
      'shares', holder.shares,
      'value_usd', holder.value_usd,
      'filing_date', holder.filing_date
    ) order by holder.sort_shares desc nulls last)
    from (
      select dedup.filer_name, dedup.shares::text as shares,
             dedup.value_usd::text as value_usd,
             dedup.filing_date::text as filing_date,
             dedup.shares as sort_shares
      from (
        select distinct on (ownership.filer_name)
               ownership.filer_name, ownership.shares,
               ownership.value_usd, ownership.filing_date,
               ownership.is_amendment
        from core.institutional_ownership ownership
        where ownership.company_id = company.id
        order by ownership.filer_name, ownership.is_amendment desc,
                 ownership.filing_date desc nulls last
      ) dedup
      order by dedup.shares desc nulls last
      limit 15
    ) holder
  ), '[]'::jsonb) as institutional_holders,
  (
    select jsonb_build_object(
      'value', fact.value::text,
      'period_end', period.end_date::text
    )
    from analytics.canonical_fact fact
    join analytics.canonical_concept concept
      on concept.id = fact.canonical_concept_id
    join core.period period on period.id = fact.period_id
    where fact.company_id = company.id and concept.name = 'public_float' and period.end_date >= '{_HISTORY_FLOOR}' and period.end_date <= current_date + interval '30 days'
    order by period.end_date desc
    limit 1
  ) as public_float,
  (
    select jsonb_build_object(
      'price', price.price::text,
      'symbol', price.symbol,
      'bar_timestamp', price.bar_timestamp::text,
      'feed', price.feed
    )
    from core.market_price_alpaca price
    where price.company_id = company.id
    order by price.price_date desc
    limit 1
  ) as latest_price,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'date', history.price_date::text,
      'price', history.price::text
    ) order by history.price_date)
    from (
      select price_date, price
      from core.market_price_alpaca
      where company_id = company.id
      order by price_date desc
      limit 3650
    ) history
  ), '[]'::jsonb) as price_history,
  (
    select fact.value::text
    from analytics.canonical_fact fact
    join analytics.canonical_concept concept
      on concept.id = fact.canonical_concept_id
    join core.period period on period.id = fact.period_id
    where fact.company_id = company.id
      and concept.name = 'stockholders_equity'
      and period.end_date >= '{_HISTORY_FLOOR}' and period.end_date <= current_date + interval '30 days'
    order by period.end_date desc
    limit 1
  ) as book_value,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'metric_name', metric_name,
      'value', value,
      'period_end', period_end
    ) order by metric_name, period_end desc)
    from metric_history_rows where rank <= 3
  ), '[]'::jsonb) as metric_history,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'ticker', peer.ticker,
      'company_name', peer.company_name,
      'match_basis', peer.match_basis,
      'roe', (select value::text from peer_metrics where company_id = peer.id and metric_name = 'roe' and rn = 1),
      'roic', (select value::text from peer_metrics where company_id = peer.id and metric_name = 'roic' and rn = 1),
      'revenue_growth_3y_cagr', (select value::text from peer_metrics where company_id = peer.id and metric_name = 'revenue_growth_3y_cagr' and rn = 1),
      'net_margin', (select value::text from peer_metrics where company_id = peer.id and metric_name = 'net_margin' and rn = 1)
    ) order by peer.sort_roic desc nulls last)
    from (
      select p.id, p.ticker, p.company_name, p.match_basis,
             (select value from peer_metrics where company_id = p.id and metric_name = 'roic' and rn = 1) as sort_roic
      from peer_companies p
      order by sort_roic desc nulls last
      limit 10
    ) peer
  ), '[]'::jsonb) as peer_companies,
  (
    select jsonb_build_object(
      'ownership_pct', s.ownership_pct::text,
      'shares_owned_by_insiders', s.shares_owned_by_insiders::text,
      'distinct_insiders_count', s.distinct_insiders_count,
      'is_null_reason', s.is_null_reason
    )
    from core.insider_ownership_summary s
    where s.company_id = company.id
  ) as insider_ownership_summary,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'window_months', w.window_months,
      'shares_bought', w.shares_bought::text,
      'shares_sold', w.shares_sold::text,
      'buy_dollar_volume', w.buy_dollar_volume::text,
      'sell_dollar_volume', w.sell_dollar_volume::text,
      'insiders_buying_count', w.insiders_buying_count,
      'insiders_selling_count', w.insiders_selling_count,
      'largest_purchase_owner_name', w.largest_purchase_owner_name,
      'largest_purchase_date', w.largest_purchase_date::text,
      'largest_purchase_shares', w.largest_purchase_shares::text,
      'largest_purchase_price', w.largest_purchase_price::text,
      'largest_purchase_value', w.largest_purchase_value::text,
      'largest_sale_owner_name', w.largest_sale_owner_name,
      'largest_sale_date', w.largest_sale_date::text,
      'largest_sale_shares', w.largest_sale_shares::text,
      'largest_sale_price', w.largest_sale_price::text,
      'largest_sale_value', w.largest_sale_value::text
    ) order by w.window_months)
    from core.insider_window_summary w
    where w.company_id = company.id
  ), '[]'::jsonb) as insider_window_summary,
  (
    select jsonb_build_object(
      'report_period_latest', ios.report_period_latest::text,
      'report_period_prior', ios.report_period_prior::text,
      'total_institutional_pct', ios.total_institutional_pct::text,
      'total_institutional_pct_prior', ios.total_institutional_pct_prior::text,
      'qoq_change_pct', ios.qoq_change_pct::text,
      'total_holders', ios.total_holders,
      'holders_increased', ios.holders_increased,
      'holders_decreased', ios.holders_decreased,
      'new_positions', ios.new_positions,
      'exited_positions', ios.exited_positions,
      'top_holders', ios.top_holders
    )
    from core.institutional_ownership_summary ios
    where ios.company_id = company.id
  ) as institutional_ownership_summary,
  (
    select jsonb_build_object(
      'report_period_latest', fos.report_period_latest::text,
      'report_period_prior', fos.report_period_prior::text,
      'total_fund_ownership_pct', fos.total_fund_ownership_pct::text,
      'total_fund_ownership_pct_prior', fos.total_fund_ownership_pct_prior::text,
      'change_in_pct', fos.change_in_pct::text,
      'total_funds_holding', fos.total_funds_holding,
      'funds_increasing', fos.funds_increasing,
      'funds_decreasing', fos.funds_decreasing,
      'new_positions', fos.new_positions,
      'exited_positions', fos.exited_positions,
      'top_holders', fos.top_holders
    )
    from core.fund_ownership_summary fos
    where fos.company_id = company.id
  ) as fund_ownership_summary,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'filing_date', h.filing_date::text,
      'headcount', h.headcount,
      'is_approximate', h.is_approximate
    ) order by h.filing_date desc)
    from core.employee_headcount_disclosure h
    where h.company_id = company.id
    limit 4
  ), '[]'::jsonb) as employee_headcount_history,
  coalesce((
    select jsonb_agg(jsonb_build_object(
      'segment_name', sr.segment_name,
      'period_type', sr.period_type,
      'period_end', sr.period_end,
      'value', sr.value::text
    ) order by sr.segment_name, sr.period_type)
    from core.segment_revenue sr
    where sr.company_id = company.id
    limit 60
  ), '[]'::jsonb) as segment_revenue
from selected_company company
"""


def _assemble_statement(rows: list[dict], statement: str, frequency: str) -> dict:
    """Direct port of db.ts's assembleStatement() -- same filter, same
    period-key dedup, same sort, same null-filling for a period a given
    line has no value for."""
    if frequency == "annual":
        matching = [
            r
            for r in rows
            if r["statement"] == statement
            and (r["fiscal_period"] is None or r["fiscal_period"] == "FY")
        ]
    else:
        matching = [
            r
            for r in rows
            if r["statement"] == statement
            and (
                r["fiscal_period"] is None
                or r["fiscal_period"] in ("Q1", "Q2", "Q3", "Q4")
            )
        ]

    period_map: dict[str, dict] = {}
    line_map: dict[float, dict] = {}
    for row in matching:
        display_order = row["display_order"]
        if display_order not in line_map:
            line_map[display_order] = {"label": row["display_label"], "values": {}}
        if row["period_end"] and row["fiscal_year"] and row["fiscal_period"]:
            key = f"{row['fiscal_year']}|{row['fiscal_period']}|{row['period_end']}"
            period_map[key] = {
                "fiscal_year": row["fiscal_year"],
                "fiscal_period": row["fiscal_period"],
                "period_end": row["period_end"],
            }
            line_map[display_order]["values"][key] = row["value"]

    ordered_period_items = sorted(
        period_map.items(), key=lambda kv: kv[1]["period_end"]
    )
    period_keys = [k for k, _ in ordered_period_items]
    periods = [p for _, p in ordered_period_items]
    lines = [
        {
            "label": line["label"],
            "values": [line["values"].get(key) for key in period_keys],
        }
        for _, line in sorted(line_map.items(), key=lambda kv: kv[0])
    ]
    return collapse_duplicate_columns(periods, lines)


# Duplicate-column guard (2026-10-31, the UI half of rule
# period.duplicate_column_merge@1). One accounting column can exist as two
# core.period rows with the same fiscal year/period whose end dates differ by
# a few days (ATI FY 2021 on Dec 31, 2021 and Jan 2, 2022; MSFT Q1 FY2017
# revenue 20,453M vs the 21,928M ASC 606 recast under a one-day-different
# context). Keyed by period_end they rendered as two columns with the same
# label. Columns with the same (fiscal_year, fiscal_period) whose ends are
# within 7 days collapse into one: a line keeps its value only when every copy
# agrees within the filer's rounding; when copies differ the cell is blank with
# a reason, never an arbitrary winner (founder ruling). Same rule as
# apps/app/lib/company/db.ts::collapseDuplicateColumns.
DUPLICATE_COLUMN_MAX_GAP_DAYS = 7


def _trailing_zero_exponent(value: Decimal) -> int:
    if value == 0:
        return 0
    exp = value.normalize().as_tuple().exponent
    return max(0, min(6, exp)) if isinstance(exp, int) else 0


def same_number_within_precision(a: str, b: str) -> bool:
    try:
        x, y = Decimal(a), Decimal(b)
    except (InvalidOperation, TypeError):
        return a == b
    if x == y:
        return True
    scale = max(_trailing_zero_exponent(x), _trailing_zero_exponent(y))
    slack = max(
        Decimal("1.5") * Decimal(10) ** scale, Decimal("0.0005") * max(abs(x), abs(y))
    )
    return abs(x - y) <= slack


def collapse_duplicate_columns(periods: list[dict], lines: list[dict]) -> dict:
    groups: list[list[int]] = []
    assigned: set[int] = set()
    for i, p in enumerate(periods):
        if i in assigned:
            continue
        members = [i]
        for j, q in enumerate(periods):
            if j == i or j in assigned:
                continue
            gap = abs(
                (
                    date.fromisoformat(q["period_end"])
                    - date.fromisoformat(p["period_end"])
                ).days
            )
            if (
                q["fiscal_year"] == p["fiscal_year"]
                and q["fiscal_period"] == p["fiscal_period"]
                and gap <= DUPLICATE_COLUMN_MAX_GAP_DAYS
            ):
                members.append(j)
        assigned.update(members)
        groups.append(members)
    if all(len(g) == 1 for g in groups):
        return {"periods": periods, "lines": lines}

    def filled(i: int) -> int:
        return sum(1 for line in lines if line["values"][i] is not None)

    kept = [max(g, key=lambda i: (filled(i), -i)) for g in groups]
    out_periods = [periods[i] for i in kept]
    out_lines = []
    for line in lines:
        values: list[str | None] = []
        reasons: list[str | None] = []
        for g in groups:
            present = [line["values"][i] for i in g if line["values"][i] is not None]
            if not present:
                values.append(None)
                reasons.append(None)
            elif all(same_number_within_precision(v, present[0]) for v in present):
                values.append(present[0])
                reasons.append(None)
            else:
                values.append(None)
                ends = " and ".join(periods[i]["period_end"] for i in g)
                reasons.append(
                    f"Two filed versions of this period differ ({' vs '.join(present)}; contexts ending {ends}); neither is shown."
                )
        row = {"label": line["label"], "values": values}
        if any(r is not None for r in reasons):
            row["reasons"] = reasons
        out_lines.append(row)
    return {"periods": out_periods, "lines": out_lines}


def suppress_bank_metrics(metrics: list[dict], is_bank: bool) -> list[dict]:
    """Bank applicability (common/sector_applicability.py). For a bank, every
    suppressed metric is returned with value null and the stated reason in
    is_null_reason (the field the page already renders for any null), whether
    or not a stored row exists. A non-bank is returned unchanged. The stored
    analytics.metric_value is not touched."""
    if not is_bank:
        return metrics
    by_name = {m["metric_name"]: dict(m) for m in metrics}
    for name in BANK_SUPPRESSED_METRICS:
        reason = metric_suppression_reason(name, True)
        entry = by_name.get(name)
        if entry is None:
            by_name[name] = {
                "metric_name": name,
                "value": None,
                "period_label": "",
                "period_end": "",
                "is_null_reason": reason,
            }
        else:
            entry["value"] = None
            entry["is_null_reason"] = reason
    return [by_name[name] for name in sorted(by_name)]


def suppress_bank_statement(statement: dict, is_bank: bool) -> dict:
    """Same rule for the statement tables: a suppressed row keeps its label,
    every cell becomes null, and `suppressed_reason` carries the reason. Only
    lines that carry a suppression reason gain the key, so a non-bank's
    statement is byte-identical to before."""
    if not is_bank:
        return statement
    lines = []
    for line in statement["lines"]:
        reason = statement_line_suppression_reason(line["label"], True)
        if reason is None:
            lines.append(line)
        else:
            lines.append(
                {
                    **line,
                    "values": [None] * len(line["values"]),
                    "suppressed_reason": reason,
                }
            )
    return {**statement, "lines": lines}


def stale_metric_history_names(
    history_rows: list[dict], latest_filed_period
) -> set[str]:
    """Names of metrics whose FY history series is stale: if even the series'
    latest year (max period_end, independent of row order) is more than a
    fiscal year behind the company's own latest filed period, the whole series
    is old and is left out (staleness guard)."""
    newest: dict[str, str] = {}
    for entry in history_rows:
        name = entry["metric_name"]
        end = entry.get("period_end")
        if end is not None and (name not in newest or end > newest[name]):
            newest[name] = end
    return {
        name
        for name, end in newest.items()
        if staleness.staleness_reason(end, "FY", latest_filed_period)
    }


def suppress_stale_book_value(
    book_value: str | None, period_end: str | None, latest_filed_period
) -> tuple[str | None, str | None]:
    """Book value is the latest stockholders' equity of any period (a balance
    at a date), so the quarterly threshold applies. Returns (value, reason)."""
    if book_value is None:
        return None, None
    reason = staleness.staleness_reason(period_end, "Q4", latest_filed_period)
    if reason is None:
        return book_value, None
    return None, reason


def get_company_page_data(conn: psycopg.Connection, ticker: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(_QUERY, {"ticker": ticker})
        row = cur.fetchone()
    if row is None:
        return None
    (
        company,
        metrics,
        statements,
        filings,
        insider_transactions,
        beneficial_ownership,
        institutional_holders,
        public_float,
        latest_price,
        price_history,
        book_value,
        metric_history_rows,
        peer_companies,
        insider_ownership_summary,
        insider_window_summary,
        institutional_ownership_summary,
        fund_ownership_summary,
        employee_headcount_history,
        segment_revenue,
    ) = row

    is_bank = bool(company.get("is_bank"))
    metrics = suppress_bank_metrics(metrics, is_bank)
    latest_filed = company.get("latest_filed_period")
    metrics = staleness.apply_to_metric_rows(metrics, latest_filed)
    stale_history_names = stale_metric_history_names(metric_history_rows, latest_filed)
    book_value, book_value_reason = suppress_stale_book_value(
        book_value, company.get("book_value_period_end"), latest_filed
    )

    metric_history: dict[str, list] = defaultdict(list)
    metric_trend_history: dict[str, list] = defaultdict(list)
    for entry in metric_history_rows:
        if is_bank and entry["metric_name"] in BANK_SUPPRESSED_METRICS:
            continue
        if entry["metric_name"] in stale_history_names:
            continue
        metric_history[entry["metric_name"]].append(entry["value"])
        metric_trend_history[entry["metric_name"]].append(
            {"value": entry["value"], "period_end": entry["period_end"]}
        )

    return {
        "company": company,
        "metrics": {m["metric_name"]: m for m in metrics},
        "quarterlyResults": suppress_bank_statement(
            _assemble_statement(statements, "income_statement", "quarterly"), is_bank
        ),
        "incomeStatement": suppress_bank_statement(
            _assemble_statement(statements, "income_statement", "annual"), is_bank
        ),
        "balanceSheet": suppress_bank_statement(
            _assemble_statement(statements, "balance_sheet", "annual"), is_bank
        ),
        "cashFlow": suppress_bank_statement(
            _assemble_statement(statements, "cash_flow", "annual"), is_bank
        ),
        "filings": filings,
        "insiderTransactions": insider_transactions,
        "beneficialOwnership": beneficial_ownership,
        "institutionalHolders": institutional_holders,
        "publicFloat": public_float,
        "latestPrice": latest_price,
        "priceHistory": price_history,
        "bookValue": book_value,
        "bookValueSuppressedReason": book_value_reason,
        "metricHistory": dict(metric_history),
        "metricTrendHistory": dict(metric_trend_history),
        "peerCompanies": peer_companies,
        "insiderOwnershipSummary": insider_ownership_summary,
        "insiderWindowSummary": insider_window_summary,
        "institutionalSummary": institutional_ownership_summary,
        "fundSummary": fund_ownership_summary,
        "employeeHeadcountHistory": employee_headcount_history,
        "segmentRevenue": segment_revenue,
    }
