from django.db import connections


def _rows(sql, params=()):
    with connections["warehouse"].cursor() as cursor:
        cursor.execute(sql, params)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def pipeline_dashboard():
    runs = _rows("""
        select id, run_type, started_at, finished_at, status, stats
        from raw.collector_runs order by started_at desc limit 50
    """)
    errors = _rows("""
        select * from (
          select 'collector' source, id, cik, error_type, message, occurred_at
          from raw.collector_errors where not resolved
          union all
          select 'normalizer', id, cik, error_type, message, occurred_at
          from core.normalizer_error where not resolved
          union all
          select 'mapper', id, cik, error_type, message, occurred_at
          from analytics.mapper_error where not resolved
        ) errors order by occurred_at desc limit 100
    """)
    return {"runs": runs, "errors": errors}


def quality_dashboard():
    findings = _rows("""
        select f.id, f.company_id, c.company_name, l.ticker, f.finding_type,
               f.status, f.summary, f.found_at
        from analytics.company_data_finding f
        join core.company c on c.id = f.company_id
        left join lateral (select ticker from core.listing where company_id=c.id order by effective_to desc nulls first limit 1) l on true
        order by (f.status='open') desc, f.found_at desc limit 100
    """)
    sanity = _rows("""
        select s.id, s.company_id, c.company_name, l.ticker, s.metric_name,
               s.pct_diff, s.severity, s.external_source, s.checked_at
        from analytics.data_sanity_check s join core.company c on c.id=s.company_id
        left join lateral (select ticker from core.listing where company_id=c.id order by effective_to desc nulls first limit 1) l on true
        order by case s.severity when 'critical' then 0 when 'warning' then 1 else 2 end, s.checked_at desc limit 100
    """)
    return {"findings": findings, "sanity": sanity}


def search_companies(query):
    query = query.strip()[:120]
    if not query:
        return []
    pattern = f"%{query}%"
    return _rows("""
        select distinct c.id, c.cik, c.company_name, l.ticker, l.exchange
        from core.company c left join core.listing l on l.company_id=c.id
        where c.company_name ilike %s or c.cik ilike %s or l.ticker ilike %s
        order by c.company_name limit 25
    """, [pattern, pattern, pattern])


def company_detail(company_id):
    company = _rows("""
        select c.id, c.cik, c.company_name, c.fiscal_year_end, l.ticker, l.exchange
        from core.company c left join lateral (select ticker, exchange from core.listing where company_id=c.id order by effective_to desc nulls first limit 1) l on true
        where c.id=%s
    """, [company_id])
    if not company:
        return None
    filings = _rows("select accession_number as accession, form, filing_date, period_of_report from core.filing where company_id=%s order by filing_date desc limit 30", [company_id])
    findings = _rows("select finding_type, status, summary, found_at, resolved_at from analytics.company_data_finding where company_id=%s order by found_at desc limit 50", [company_id])
    sanity = _rows("select metric_name, our_value, external_value, pct_diff, severity, checked_at from analytics.data_sanity_check where company_id=%s order by checked_at desc limit 50", [company_id])
    identities = _rows("select identity_name, layer, checked, passed, worst_rel_gap, checked_at from analytics.identity_check_summary where company_id=%s order by checked_at desc limit 50", [company_id])
    return {"company": company[0], "filings": filings, "findings": findings, "sanity": sanity, "identities": identities}


def mapping_dashboard():
    return _rows("""
        select cc.id, cc.name, cc.statement, cc.combination_mode,
               count(distinct cm.id) mapping_count,
               count(distinct ctc.id) candidate_count,
               count(distinct cm.id) filter (where cm.confidence='provisional') provisional_count
        from analytics.canonical_concept cc
        left join analytics.concept_mapping cm on cm.canonical_concept_id=cc.id
        left join analytics.concept_tag_candidate ctc on ctc.canonical_concept_id=cc.id
        group by cc.id order by cc.statement, cc.name limit 500
    """)


def work_queue_sources():
    rows = _rows("""
        select 'company_finding' source_type, f.id::text source_id,
               concat(coalesce(l.ticker, c.company_name), ': ', f.summary) title,
               case when f.finding_type='pipeline_bug' then 'high' else 'medium' end severity,
               case when f.finding_type='pipeline_bug' then 80 else 50 end priority,
               jsonb_build_object('company_id', f.company_id, 'ticker', l.ticker, 'finding_type', f.finding_type, 'summary', f.summary, 'evidence', f.evidence) payload
        from analytics.company_data_finding f
        join core.company c on c.id=f.company_id
        left join lateral (select ticker from core.listing where company_id=c.id order by effective_to desc nulls first limit 1) l on true
        where f.status='open'
        union all
        select 'collector_error', e.id::text, concat('Collector ', e.error_type, ': ', left(e.message, 160)),
               'high', 75, jsonb_build_object('cik', e.cik, 'error_type', e.error_type, 'message', e.message, 'run_id', e.run_id)
        from raw.collector_errors e where not e.resolved
        union all
        select 'normalizer_error', e.id::text, concat('Normalizer ', e.error_type, ': ', left(e.message, 160)),
               'high', 75, jsonb_build_object('cik', e.cik, 'stage', e.stage, 'error_type', e.error_type, 'message', e.message)
        from core.normalizer_error e where not e.resolved
        union all
        select 'mapper_error', e.id::text, concat('Mapper ', e.error_type, ': ', left(e.message, 160)),
               'high', 80, jsonb_build_object('cik', e.cik, 'stage', e.stage, 'error_type', e.error_type, 'message', e.message)
        from analytics.mapper_error e where not e.resolved
        order by priority desc limit 1000
    """)
    return rows


OPEN_SOURCE_SQL = {
    "company_finding": "select id::text from analytics.company_data_finding where status = 'open'",
    "collector_error": "select id::text from raw.collector_errors where not resolved",
    "normalizer_error": "select id::text from core.normalizer_error where not resolved",
    "mapper_error": "select id::text from analytics.mapper_error where not resolved",
}


def open_source_ids():
    """source_type -> ids still open in the warehouse, for every source the
    work queue ingests (the complement of work_queue_sources(), uncapped)."""
    return {kind: {row["id"] for row in _rows(sql)} for kind, sql in OPEN_SOURCE_SQL.items()}
