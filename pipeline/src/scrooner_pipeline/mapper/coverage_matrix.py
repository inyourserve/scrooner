"""Two-table coverage system (2026-09-05, by direct request) --
deliberately simple, no scoring/classification on top:

1. `analytics.data_point_registry` -- every concept/metric/ownership
   section this project tracks, and the SEC tag(s) it needs. Derived
   from `concept_mapping`/`metric_definition_input` (already the
   tag-requirement source of truth) -- rebuilt each run, not hand-
   maintained.
2. `analytics.company_data_point_coverage` -- one row per
   (company, data_point), has_value yes/no. Derived from
   `canonical_fact`/`metric_value`/the ownership tables -- a projection
   of data this project already has, not a new fetch or a new source of
   truth.

Ownership data points have no XBRL tag (Form 4/13F/N-PORT aren't XBRL) --
required_tags holds the SEC form type instead, the closest domain
equivalent to "what do I need to go fetch."
"""

import psycopg
import structlog

logger = structlog.get_logger()

# Scoped to revenue-family concepts only -- verified live 2026-09-11
# investigating why `revenue` coverage sits at 87.4% (693 of 5,216 active
# companies). Every SIC bucket below was spot-checked against real
# companies in that gap population (not assumed from the label alone):
# "Commodity Contracts Brokers & Dealers" turned out to be commodity
# ETF/trusts (SPDR Gold Trust, Grayscale Bitcoin Trust) paying sponsor
# fees, not earning revenue; "Real Estate Investment Trusts" in this gap
# population is exclusively mortgage REITs (AGNC, Annaly, Chimera) earning
# net interest income. Deliberately NOT applied to balance-sheet/cash-flow
# concepts (total_assets, cfo, etc.) -- those weren't checked and a
# company having no "revenue" says nothing about whether it has real
# assets or cash flow.
REVENUE_FAMILY_CONCEPTS = (
    "revenue",
    "revenue_sanity_resolved",
    "cost_of_revenue",
    "cost_of_revenue_resolved",
    "gross_profit",
    "gross_profit_resolved",
    "operating_income",
    "operating_income_resolved",
    "operating_expenses",
    "operating_expenses_resolved",
)

SIC_GAP_REASONS = {
    "Blank Checks": "pre_revenue_spac",
    "Pharmaceutical Preparations": "pre_revenue_biotech_pharma",
    "Biological Products, (No Diagnostic Substances)": "pre_revenue_biotech_pharma",
    "Commodity Contracts Brokers & Dealers": "passthrough_commodity_trust",
    "Asset-Backed Securities": "passthrough_trust",
    "Real Estate Investment Trusts": "reit_net_interest_income_not_revenue",
    "State Commercial Banks": "bank_interest_income_not_revenue",
    "National Commercial Banks": "bank_interest_income_not_revenue",
    "Savings Institution, Federally Chartered": "bank_interest_income_not_revenue",
    # Verified live 2026-09-12: every remaining company under these two
    # SIC codes missing revenue is a real, named, pre-production
    # exploration/development-stage miner (Lithium Americas, Trilogy
    # Metals, Perpetua Resources, Dakota Gold, etc.) -- same structural
    # "genuinely $0, not a data gap" pattern as pre-revenue biotech, just
    # a different sector never previously named for it.
    "Metal Mining": "pre_revenue_mining_exploration",
    "Gold and Silver Ores": "pre_revenue_mining_exploration",
}


def _tag_str(taxonomy: str, tag: str) -> str:
    return f"{taxonomy}:{tag}"


# Evidence-based, not a SIC guess: a company reporting real facts under
# any of these interest/investment-income tags but nothing under any of
# revenue's own mapped tags is a financial institution/lender presenting
# its income statement the GAAP-standard way for that industry (net
# interest income + noninterest income, not a single "Revenue" line) --
# NOT a candidate for adding these tags to revenue's own concept_mapping
# (would repeat the exact "different concept sharing vocabulary" trap
# already documented elsewhere in this file for CostsAndExpenses/
# LongTermDebtNoncurrent, and would blur the same bank/BDC/REIT
# sector-isolation this project deliberately keeps elsewhere). Verified
# live 2026-09-11 on Synchrony Financial (SIC "Finance Services", not
# caught by SIC_GAP_REASONS' bank-specific codes) before trusting this
# as a general rule, not just that one company.
_FINANCIAL_INCOME_TAGS = (
    "InterestIncomeOperating",
    "InterestAndDividendIncomeOperating",
    "NoninterestIncome",
    "GrossInvestmentIncomeOperating",
    "InterestAndFeeIncomeLoansAndLeases",
)

# Confirmed live 2026-09-12 via each company's actual filing history --
# these file 20-F/40-F (foreign private issuer forms), already excluded
# from V1 scope per doc 02/root CLAUDE.md's closed FPI decision (untested
# IFRS-vs-GAAP concept-mapping risk). Not a coverage bug -- a scope
# boundary already decided elsewhere, this just labels it instead of
# leaving it looking like an unexplained gap.
_FPI_COMPANY_IDS = (
    1950,  # Bank of Montreal
    5,  # Enbridge Inc
    239,  # Canadian National Railway Co
    6,  # Taiwan Semiconductor Manufacturing Co Ltd
    3389,  # Sify Technologies Ltd
    5689,  # JBS N.V.
)

# Confirmed live 2026-09-12 by fetching each company's OWN live SEC
# companyfacts payload directly (data.sec.gov/api/xbrl/companyfacts) --
# every one returns zero or near-zero real us-gaap facts under its own
# CIK (Ameren Illinois/Georgia Power/Consumers Energy: only `ffd`
# registration-fee tags from unrelated S-3/424B filings; Public Service
# Co of New Mexico: a completely empty facts payload). All four are
# wholly-owned utility subsidiaries that co-file combined 10-Ks with
# their parent holding company -- the real income-statement data exists
# in that filing, but SEC's Company Facts API aggregates by CIK from the
# XBRL's own entity-identifier contexts, and these subsidiaries' own
# context carries almost nothing. A genuine SEC/EDGAR-side data-
# availability limit for this specific filer pattern, not a Scrooner
# tag-mapping bug -- there is no tag to map, the API has nothing to give.
# Two sibling utility subsidiaries in this same remaining-gap population
# (NSTAR Electric, MGE Energy) were investigated the same day and found
# to have real revenue-shaped tags (`ElectricUtilityRevenue`,
# `RegulatedAndUnregulatedOperatingRevenue`) -- NOT added here because a
# full-population coexistence check found both tags mix a genuine
# company-wide total with dimensional/segment-only values under the same
# bare tag for OTHER companies (Alliant Energy Corp: same tag, $35M vs a
# real $1.03B total for the same period) -- adding either to `revenue`'s
# concept_mapping would have been the exact "different concept sharing
# vocabulary" trap this file already warns against twice elsewhere,
# just discovered one coexistence-check-scale later than usual (a first,
# too-small sample of 5 rows looked consistent; the full check on all
# ~4,800 coexisting pairs was 62% disagreeing). No safe automated fix
# exists for NSTAR/MGE without dimensional-XBRL-aware extraction (doc 23:
# already scoped and confirmed genuinely harder, not yet designed) -- so
# unlike the four below, they're deliberately left in the unexplained
# tail rather than force-classified.
_COREGISTRANT_SUBSIDIARY_COMPANY_IDS = (
    257,  # Ameren Illinois Co
    613,  # Georgia Power Co
    1044,  # Public Service Co of New Mexico
    1165,  # Consumers Energy Co
)

# Confirmed live 2026-09-12 by name -- an explicit, curated list (not a
# regex on "Trust" in company_name, which would also match a real
# operating bank/trust company) of royalty/pass-through trusts found in
# the remaining unexplained gap population: oil & gas royalty trusts
# (Cross Timbers, Hugoton, Marine Petroleum, Mesa, Permian Basin, Sabine,
# San Juan Basin, ECA Marcellus, Gulf Coast Ultra Deep, Permianville,
# PermRock, VOC Energy), a mineral royalty trader (Scully Royalty), a
# music-royalty trust (Mills Music Trust), and two real-estate wind-down
# pass-through trusts (Copper Property CTL, Woodbridge Liquidation) --
# same structural absence as `passthrough_trust` above, just not caught
# by SIC_GAP_REASONS since these span several different SIC codes.
_ROYALTY_AND_PASSTHROUGH_TRUST_COMPANY_IDS = (
    1731,
    1659,
    676,
    1189,
    1214,
    1271,
    1215,  # oil/gas royalty trusts
    2105,
    3006,
    2502,
    5043,
    2322,  # more oil/gas royalty trusts
    237,  # Scully Royalty Ltd
    698,  # Mills Music Trust
    2715,
    5633,  # real estate pass-through/liquidation trusts
)


def classify_concept_gaps(conn: psycopg.Connection) -> dict:
    """Fills `gap_reason` for revenue-family concept rows where has_value
    is false, using the SIC-based structural patterns verified live
    2026-09-11 (see REVENUE_FAMILY_CONCEPTS/SIC_GAP_REASONS above), plus
    an evidence-based financial-institution rule for companies that fall
    outside those specific SIC codes. Concept rows never got a
    gap_reason before this -- only metric rows did (see build_coverage()'s
    own comment) -- so every prior "why is revenue missing" question
    needed a from-scratch manual SIC-clustering pass. Additive: only ever
    sets a reason where a real pattern matches; leaves every other row
    (including the genuinely uninvestigated tail) at NULL rather than
    guessing."""
    sic_list = list(SIC_GAP_REASONS.keys())
    reason_list = list(SIC_GAP_REASONS.values())

    with conn.cursor() as cur:
        cur.execute(
            """
            with sic_reason as (
                select * from unnest(%(sics)s::text[], %(reasons)s::text[]) as t(sic_description, reason)
            )
            update analytics.company_data_point_coverage cov
            set gap_reason = coalesce(
                sr.reason,
                case
                    when comp.sic_description is null and exists (
                        select 1 from analytics.canonical_fact cf2
                        join analytics.canonical_concept cc2 on cc2.id = cf2.canonical_concept_id
                        where cc2.name = 'bdc_total_investment_income' and cf2.company_id = comp.id
                    ) then 'bdc_reports_investment_income_not_revenue'
                    when exists (
                        select 1 from core.fact fa2
                        join core.concept co2 on co2.id = fa2.concept_id
                        where fa2.company_id = comp.id and co2.tag = any(%(financial_income_tags)s)
                    ) then 'financial_institution_interest_income_not_revenue'
                    -- yfinance's own industry classification is more complete
                    -- than our SIC-code rule alone -- checked live 2026-09-12:
                    -- 26 real SPACs (post-Blank-Checks-SIC, e.g. reclassified
                    -- after a name change but before a real merger) caught
                    -- here that SIC_GAP_REASONS missed. Excludes the 31
                    -- companies yfinance still labels "Shell Companies" but
                    -- that already have real revenue data (a completed SPAC
                    -- merger yfinance's own industry tag hasn't caught up to
                    -- yet -- confirmed via canonical_fact, not assumed).
                    when comp.y_industry = 'Shell Companies' then 'pre_revenue_spac'
                    when comp.id = any(%(fpi_ids)s) then 'foreign_private_issuer_sparse_xbrl'
                    when comp.id = any(%(coregistrant_ids)s) then 'coregistrant_subsidiary_sparse_sec_xbrl'
                    when comp.id = any(%(trust_ids)s) then 'passthrough_trust'
                end
            )
            from core.company comp
            left join sic_reason sr on sr.sic_description = comp.sic_description
            where cov.company_id = comp.id
              and cov.has_value = false
              and cov.data_point_name = any(%(concepts)s)
              and cov.gap_reason is null
            """,
            {
                "sics": sic_list,
                "reasons": reason_list,
                "concepts": list(REVENUE_FAMILY_CONCEPTS),
                "financial_income_tags": list(_FINANCIAL_INCOME_TAGS),
                "fpi_ids": list(_FPI_COMPANY_IDS),
                "coregistrant_ids": list(_COREGISTRANT_SUBSIDIARY_COMPANY_IDS),
                "trust_ids": list(_ROYALTY_AND_PASSTHROUGH_TRUST_COMPANY_IDS),
            },
        )
        classified = cur.rowcount
        conn.commit()

    logger.info("coverage_matrix.concept_gaps_classified", rows=classified)
    return {"rows": classified}


# The corrected-coverage-denominator methodology (2026-09-12, see
# doc/data-moat/learnings/2026-09-12-corrected-coverage-denominator-methodology.md),
# generalized from revenue/dividends to the whole registry. Every coverage
# number before this measured against ALL active companies -- wrong for
# any data point that structurally doesn't apply to every company. Each
# named population here is a real, evidence-checked company set, not a
# guess:
#   real_operating_company (~4,816): status='active' MINUS the
#     non-operating gap_reasons already classified above (SPAC,
#     passthrough_trust, passthrough_commodity_trust) -- the corrected
#     replacement for "all active companies" as the DEFAULT population
#     for anything that should apply to a genuine operating business.
#   dividend_payer (~1,954): real, nonzero dividends_paid_resolved OR
#     dividends_per_share in the company's own most recent reported FY
#     (current status, not "ever paid one 10 years ago").
#   buyback_company (~2,449): same shape, for share_buybacks_resolved.
#   capital_return_company: union of the two above -- for metrics that
#     combine dividends AND buybacks (cash_returned_to_shareholders,
#     total_shareholder_yield), which only need EITHER activity to be
#     a real, applicable case.
#   bdc_company (118): has a real bdc_total_investment_income value --
#     the already-established sector-isolated BDC population.
POPULATION_QUERIES = {
    "real_operating_company": """
        select c.id from core.company c
        where c.status = 'active'
          and not exists (
              select 1 from analytics.company_data_point_coverage cov
              where cov.company_id = c.id and cov.data_point_name = 'revenue_sanity_resolved'
                and cov.gap_reason in ('pre_revenue_spac', 'passthrough_trust', 'passthrough_commodity_trust')
          )
    """,
    "dividend_payer": """
        with latest_paid as (
            select cf.company_id, cf.value,
                row_number() over (partition by cf.company_id order by p.fiscal_year desc) as rn
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cc.name = 'dividends_paid_resolved' and p.fiscal_period = 'FY'
        ),
        latest_dps as (
            select cf.company_id, cf.value,
                row_number() over (partition by cf.company_id order by p.fiscal_year desc) as rn
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cc.name = 'dividends_per_share' and p.fiscal_period = 'FY'
        )
        select distinct c.id from core.company c
        where c.status = 'active' and (
            c.id in (select company_id from latest_paid where rn = 1 and value != 0)
            or c.id in (select company_id from latest_dps where rn = 1 and value > 0)
        )
    """,
    "buyback_company": """
        with latest_bb as (
            select cf.company_id, cf.value,
                row_number() over (partition by cf.company_id order by p.fiscal_year desc) as rn
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cc.name = 'share_buybacks_resolved' and p.fiscal_period = 'FY'
        )
        select distinct c.id from core.company c
        where c.status = 'active' and c.id in (select company_id from latest_bb where rn = 1 and value != 0)
    """,
    "bdc_company": """
        select distinct cf.company_id from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        where cc.name = 'bdc_total_investment_income'
    """,
}

# capital_return_company is a union of two other named populations rather
# than its own standalone query -- computed separately in
# classify_company_populations() below.

# Data points that only apply to a real subset of even the real-operating-
# company population -- everything else in the registry defaults to
# real_operating_company (set in build_registry()). Curated, not guessed:
# each family here was checked the same way revenue/dividends were.
DIVIDEND_FAMILY_DATA_POINTS = (
    "dividends_paid",
    "dividends_paid_resolved",
    "dividends_per_share",
    "dividend_growth_streak_years",
    "dividend_yield",
    "dps_growth_yoy",
    "dps_growth_3y_cagr",
    "payout_ratio",
    "dividends_pct_fcf",
)
BUYBACK_FAMILY_DATA_POINTS = (
    "share_buybacks",
    "share_buybacks_resolved",
    "buyback_yield",
    "share_repurchases_pct_fcf",
)
CAPITAL_RETURN_FAMILY_DATA_POINTS = (
    "cash_returned_to_shareholders",
    "total_shareholder_yield",
)
BDC_FAMILY_DATA_POINTS = ("bdc_total_investment_income",)


def classify_company_populations(conn: psycopg.Connection) -> dict:
    """Rebuilds analytics.company_population from scratch -- one row per
    (company, named population) the company genuinely belongs to. A
    company can belong to several (e.g. a real operating company that
    also currently pays a dividend is in both real_operating_company and
    dividend_payer)."""
    with conn.cursor() as cur:
        cur.execute("delete from analytics.company_population")
        total = 0
        for population_name, query in POPULATION_QUERIES.items():
            # select *, not a named column -- POPULATION_QUERIES' own
            # SELECT lists use different column names (id, company_id),
            # and the wrapper shouldn't care which.
            cur.execute(
                f"insert into analytics.company_population (company_id, population_name) select *, %s from ({query}) q",
                (population_name,),
            )
            total += cur.rowcount
        # capital_return_company: union of dividend_payer and buyback_company
        cur.execute(
            """
            insert into analytics.company_population (company_id, population_name)
            select distinct company_id, 'capital_return_company'
            from analytics.company_population
            where population_name in ('dividend_payer', 'buyback_company')
            """
        )
        total += cur.rowcount
        conn.commit()

    logger.info("coverage_matrix.company_populations_classified", rows=total)
    return {"rows": total}


def build_registry(conn: psycopg.Connection) -> dict:
    """Rebuilds analytics.data_point_registry from concept_mapping and
    metric_definition_input -- always a fresh derivation, never edited
    by hand."""
    rows: list[dict] = []

    with conn.cursor() as cur:
        # LEFT JOIN, not INNER -- a concept with zero concept_mapping rows
        # (e.g. total_debt_resolved, populated by concept_fallback.py's
        # own "prefer A else B" logic rather than resolve()'s direct tag
        # matching) still needs a registry row, just with an empty tag
        # list, since canonical_fact rows for it genuinely exist and the
        # coverage table's cross-join below covers every canonical_concept
        # unconditionally.
        cur.execute(
            """
            select cc.name, coalesce(array_agg(distinct c.taxonomy || ':' || c.tag) filter (where c.tag is not null), '{}')
            from analytics.canonical_concept cc
            left join analytics.concept_mapping cm on cm.canonical_concept_id = cc.id
            left join core.concept c on c.id = cm.concept_id
            group by cc.name
            """
        )
        for name, tags in cur.fetchall():
            source = "mapper/resolve.py" if tags else "mapper/concept_fallback.py"
            rows.append(
                {
                    "data_point_name": name,
                    "data_point_type": "concept",
                    "required_tags": tags,
                    "source_module": source,
                }
            )

        cur.execute(
            """
            select md.metric_name, array_agg(distinct c.taxonomy || ':' || c.tag)
            from analytics.metric_definition md
            join analytics.metric_definition_input mdi on mdi.metric_definition_id = md.id
            join analytics.concept_mapping cm on cm.canonical_concept_id = mdi.canonical_concept_id
            join core.concept c on c.id = cm.concept_id
            where md.status = 'active'
            group by md.metric_name
            """
        )
        metric_rows = {name: tags for name, tags in cur.fetchall()}

        # Metrics with no direct concept input (composite metrics reading
        # other metrics' own outputs, e.g. ev_ebitda reading ebitda +
        # market_cap) get an empty tag list here -- correct, not a bug:
        # their real "tags needed" is transitively their input metrics'
        # own registry rows, not a new XBRL tag of their own.
        cur.execute(
            "select metric_name from analytics.metric_definition where status = 'active'"
        )
        for (name,) in cur.fetchall():
            rows.append(
                {
                    "data_point_name": name,
                    "data_point_type": "metric",
                    "required_tags": metric_rows.get(name, []),
                    "source_module": "mapper/",
                }
            )

    # Ownership sections -- no XBRL tag; the SEC form type is the closest
    # equivalent "what do I need to go fetch" signal.
    rows.extend(
        [
            {
                "data_point_name": "insider_ownership",
                "data_point_type": "ownership",
                "required_tags": ["FORM 4"],
                "source_module": "ownership/insider.py",
            },
            {
                "data_point_name": "institutional_ownership",
                "data_point_type": "ownership",
                "required_tags": ["FORM 13F", "SCHEDULE 13D", "SCHEDULE 13G"],
                "source_module": "ownership/institutional.py",
            },
            {
                "data_point_name": "mutual_fund_ownership",
                "data_point_type": "ownership",
                "required_tags": ["FORM N-PORT"],
                "source_module": "ownership/mutual_fund.py",
            },
        ]
    )

    # Assign each data point's applicable_population -- defaults to
    # real_operating_company (set on every row below); the narrower
    # families above override it for the specific data points that only
    # apply to a real subset of that population. See this module's own
    # comment above POPULATION_QUERIES for how each family was verified.
    population_overrides: dict[str, str] = {}
    for name in DIVIDEND_FAMILY_DATA_POINTS:
        population_overrides[name] = "dividend_payer"
    for name in BUYBACK_FAMILY_DATA_POINTS:
        population_overrides[name] = "buyback_company"
    for name in CAPITAL_RETURN_FAMILY_DATA_POINTS:
        population_overrides[name] = "capital_return_company"
    for name in BDC_FAMILY_DATA_POINTS:
        population_overrides[name] = "bdc_company"
    for row in rows:
        row["applicable_population"] = population_overrides.get(
            row["data_point_name"], "real_operating_company"
        )

    with conn.cursor() as cur:
        # Found live 2026-09-06: company_data_point_coverage has a FK to
        # data_point_name, so clearing the registry alone violates it the
        # moment any coverage rows still reference the old registry rows
        # (true on every rerun after the first). build_coverage() always
        # fully rebuilds the coverage table from scratch anyway, so
        # clearing it here first is correct, not just a workaround.
        cur.execute("delete from analytics.company_data_point_coverage")
        cur.execute("delete from analytics.data_point_registry")
        cur.executemany(
            """
            insert into analytics.data_point_registry (data_point_name, data_point_type, required_tags, source_module, applicable_population)
            values (%(data_point_name)s, %(data_point_type)s, %(required_tags)s, %(source_module)s, %(applicable_population)s)
            """,
            rows,
        )
        conn.commit()

    logger.info("coverage_matrix.registry_built", rows=len(rows))
    return {"rows": len(rows)}


def build_coverage(conn: psycopg.Connection) -> dict:
    """Rebuilds analytics.company_data_point_coverage for every active
    company x every registry data point. Batched delete-then-reinsert
    (whole-table, not per-company -- this is a full rebuild, not an
    incremental update) to stay well under the connection's statement
    timeout at ~600K rows, same batching discipline as every other
    full-population write this session."""
    with conn.cursor() as cur:
        # Found live 2026-09-06: the metric insert below (~428K company x
        # metric combinations, each running its own correlated gap_reason
        # subquery) exceeded the connection's default 2-minute
        # statement_timeout. This is a rare, admin-triggered rebuild, not
        # a per-company loop on any hot path, so a longer timeout for
        # just this connection is the right fix, not a query rewrite --
        # the existing idx_metric_value_company_metric index already
        # supports each subquery invocation efficiently, the cost is
        # purely the sheer combination count.
        cur.execute("set statement_timeout = '10min'")
        cur.execute("delete from analytics.company_data_point_coverage")
        conn.commit()

        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)
            select c.id, cc.name, exists (
                select 1 from analytics.canonical_fact cf where cf.company_id = c.id and cf.canonical_concept_id = cc.id
            )
            from core.company c
            cross join analytics.canonical_concept cc
            where c.status = 'active'
            """
        )
        conn.commit()

        # gap_reason is only meaningful when has_value is false -- picked
        # from the most-recent period's is_null_reason (a company can have
        # several metric_value rows across periods, each with a
        # potentially different reason; the latest period is the one a
        # "why is this missing" lookup actually cares about). Left NULL
        # when has_value is true. Concept rows get their own gap_reason
        # pass below (classify_concept_gaps()) for the revenue-family
        # subset with a known structural cause; ownership rows still have
        # no null-reason mechanism.
        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value, gap_reason)
            select
                c.id,
                md.metric_name,
                exists (select 1 from analytics.metric_value mv where mv.company_id = c.id and mv.metric_definition_id = md.id and mv.value is not null),
                (
                    select mv2.is_null_reason from analytics.metric_value mv2
                    where mv2.company_id = c.id and mv2.metric_definition_id = md.id
                    order by mv2.period_end desc limit 1
                )
            from core.company c
            cross join analytics.metric_definition md
            where c.status = 'active' and md.status = 'active'
            """
        )
        conn.commit()

        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)
            select c.id, 'insider_ownership', exists (
                select 1 from core.insider_ownership_summary s where s.company_id = c.id
            )
            from core.company c where c.status = 'active'
            """
        )
        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)
            select c.id, 'institutional_ownership', exists (
                select 1 from core.institutional_ownership o where o.company_id = c.id
            )
            from core.company c where c.status = 'active'
            """
        )
        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)
            select c.id, 'mutual_fund_ownership', exists (
                select 1 from core.fund_ownership_summary s where s.company_id = c.id
            )
            from core.company c where c.status = 'active'
            """
        )
        conn.commit()

        cur.execute(
            "select count(*), count(*) filter (where has_value) from analytics.company_data_point_coverage"
        )
        total, has_value = cur.fetchone()

    # Order matters: classify_concept_gaps() must run first -- it sets the
    # revenue_sanity_resolved gap_reason values (pre_revenue_spac etc.)
    # that POPULATION_QUERIES['real_operating_company'] reads directly.
    gap_stats = classify_concept_gaps(conn)
    population_stats = classify_company_populations(conn)

    logger.info(
        "coverage_matrix.coverage_built",
        total_rows=total,
        has_value=has_value,
        concept_gaps_classified=gap_stats["rows"],
        company_populations_classified=population_stats["rows"],
    )
    return {
        "total_rows": total,
        "has_value": has_value,
        "concept_gaps_classified": gap_stats["rows"],
        "company_populations_classified": population_stats["rows"],
    }


def corrected_coverage_report(conn: psycopg.Connection) -> list[dict]:
    """The actual point of this whole module extension: coverage measured
    against each data point's real applicable_population (from the
    registry), not against every active company by default. Returns one
    row per data point: has_value count, population size, and the
    corrected percentage -- the number that should be reported/trusted,
    not the raw has_value/5216 figure this project used everywhere before
    2026-09-12."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select
                r.data_point_name,
                r.data_point_type,
                r.applicable_population,
                count(*) filter (where cov.has_value) as has_value,
                count(*) as population_size
            from analytics.data_point_registry r
            join analytics.company_population cp on cp.population_name = r.applicable_population
            join analytics.company_data_point_coverage cov
                on cov.company_id = cp.company_id and cov.data_point_name = r.data_point_name
            group by r.data_point_name, r.data_point_type, r.applicable_population
            order by r.data_point_type, r.data_point_name
            """
        )
        columns = (
            "data_point_name",
            "data_point_type",
            "applicable_population",
            "has_value",
            "population_size",
        )
        return [dict(zip(columns, row)) for row in cur.fetchall()]
