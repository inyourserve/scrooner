"""Reads one chunk of companies into `model.CompanyData`. The only module of the
suite that talks to the database; every statement is a SELECT and runs under an
explicit statement_timeout.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from scrooner_pipeline.common.sector_applicability import (
    BANK_EVIDENCE_DEPOSIT_TAGS,
    BANK_EVIDENCE_EXPENSE_TAG,
    is_bank_sic,
    load_bank_company_ids,
)
from scrooner_pipeline.common.staleness import load_latest_filed_periods
from scrooner_pipeline.sanity.accounting_identity import IDENTITIES

from .model import Cell, CompanyData, ComponentFact, GapRow, Metric, MetricCell, Source

HISTORY_FLOOR = date(2015, 1, 1)  # doc 38: nothing older is displayed as current
SOURCE_BATCH = 20_000
DEBT_CONCEPTS = ("total_debt", "total_debt_split")


@dataclass
class Registry:
    names: dict[int, str] = field(default_factory=dict)
    modes: dict[str, str] = field(default_factory=dict)
    debt_tags: list[str] = field(default_factory=list)
    adjustment_tags: list[str] = field(default_factory=list)
    consumed: dict[str, str] = field(default_factory=dict)  # concept feeding >= 1 metric -> statement


def execute(cur, sql: str, params, timeout_s: int):
    """Run one statement under an explicit statement_timeout and return all rows."""
    cur.execute("select set_config('statement_timeout', %s, false)", (str(int(timeout_s) * 1000),))
    cur.execute(sql, params)
    return cur.fetchall()


def load_registry(cur, timeout_s: int = 60) -> Registry:
    reg = Registry()
    for cid, name, mode in execute(
        cur, "select id, name, combination_mode from analytics.canonical_concept", None, timeout_s
    ):
        reg.names[cid] = name
        reg.modes[name] = mode
    rows = execute(
        cur,
        """
        select distinct c.tag from analytics.concept_mapping cm
        join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
        join core.concept c on c.id = cm.concept_id
        where cc.name = any(%s) and cm.confidence <> 'rejected' and c.taxonomy = 'us-gaap'
        """,
        (list(DEBT_CONCEPTS),),
        timeout_s,
    )
    reg.debt_tags = sorted(r[0] for r in rows)
    for name, statement in execute(
        cur,
        """
        select distinct cc.name, cc.statement from analytics.metric_definition_input i
        join analytics.canonical_concept cc on cc.id = i.canonical_concept_id
        """,
        None,
        timeout_s,
    ):
        reg.consumed[name] = statement
    reg.adjustment_tags = sorted({tag for i in IDENTITIES for tag, _ in i.adjustments})
    return reg


def resolve_company_ids(cur, ciks: list[str], timeout_s: int = 60) -> list[int]:
    padded = [c.strip().zfill(10) for c in ciks if c.strip()]
    rows = execute(cur, "select id from core.company where cik = any(%s) order by id", (padded,), timeout_s)
    return [r[0] for r in rows]


def _source(row) -> Source:
    (fid, tag, value, auth, derived, form, unit, accession, fdate, start, end) = row
    return Source(
        id=fid, tag=tag, value=value, authoritative=auth, derived=derived, form=form,
        unit=unit, accession=accession, filing_date=fdate, start=start, end=end,
    )


_SOURCE_SELECT = """
    select f.id, c.tag, f.value, f.is_authoritative, f.is_derived, fl.form, u.unit_name,
           fl.accession_number, fl.filing_date, p.start_date, p.end_date
    from core.fact f
    join core.concept c on c.id = f.concept_id
    join core.unit u on u.id = f.unit_id
    join core.period p on p.id = f.period_id
    left join core.filing fl on fl.id = f.filing_id
"""


def load_chunk(
    cur,
    company_ids: list[int],
    registry: Registry,
    *,
    since: date | None = HISTORY_FLOOR,
    timeout_s: int = 60,
    as_of: date | None = None,
    history: bool = True,
) -> dict[int, CompanyData]:
    as_of = as_of or date.today()
    ids = sorted(set(company_ids))
    data: dict[int, CompanyData] = {}
    for cid, cik, ticker, sic in execute(
        cur, "select id, cik, primary_ticker, sic_code from core.company where id = any(%s)", (ids,), timeout_s
    ):
        data[cid] = CompanyData(company_id=cid, cik=cik, ticker=ticker, sic=sic, as_of=as_of)

    # canonical values with their periods
    all_source_ids: set[int] = set()
    for (cid, name, value, src, pid, start, end, ptype, fy, fp) in execute(
        cur,
        """
        select cf.company_id, cc.name, cf.value, cf.source_fact_ids, p.id, p.start_date, p.end_date,
               p.period_type, p.fiscal_year, p.fiscal_period
        from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        join core.period p on p.id = cf.period_id
        where cf.company_id = any(%s) and (%s::date is null or p.end_date >= %s::date)
        """,
        (ids, since, since),
        timeout_s,
    ):
        if cid not in data or value is None:
            continue
        src_t = tuple(src or ())
        all_source_ids.update(src_t)
        data[cid].cells.append(
            Cell(concept=name, value=value, period_id=pid, start=start, end=end,
                 period_type=ptype, fiscal_year=fy, fiscal_period=fp, source_ids=src_t)
        )
    for d in data.values():
        d.concept_modes = dict(registry.modes)

    # source facts, batched
    wanted = sorted(all_source_ids)
    all_sources: dict[int, Source] = {}
    for i in range(0, len(wanted), SOURCE_BATCH):
        rows = execute(
            cur, _SOURCE_SELECT + " where f.id = any(%s)", (wanted[i : i + SOURCE_BATCH],), timeout_s
        )
        all_sources.update({r[0]: _source(r) for r in rows})
    for d in data.values():
        for cell in d.cells:
            for sid in cell.source_ids:
                if sid in all_sources:
                    d.sources[sid] = all_sources[sid]

    # authoritative copies of every NON-authoritative source (matching-copies rule)
    non_auth = sorted({s.id for d in data.values() for s in d.sources.values() if not s.authoritative})
    owner = {s.id: d.company_id for d in data.values() for s in d.sources.values()}
    for i in range(0, len(non_auth), SOURCE_BATCH):
        rows = execute(
            cur,
            """
            select f1.id, f2.id, c.tag, f2.value, f2.is_authoritative, f2.is_derived, fl.form, u.unit_name,
                   fl.accession_number, fl.filing_date, p.start_date, p.end_date
            from core.fact f1
            join core.fact f2 on f2.company_id = f1.company_id and f2.concept_id = f1.concept_id
                 and f2.period_id = f1.period_id and f2.unit_id = f1.unit_id
                 and f2.is_authoritative and f2.id <> f1.id
            join core.concept c on c.id = f2.concept_id
            join core.unit u on u.id = f2.unit_id
            join core.period p on p.id = f2.period_id
            left join core.filing fl on fl.id = f2.filing_id
            where f1.id = any(%s)
            """,
            (non_auth[i : i + SOURCE_BATCH],),
            timeout_s,
        )
        for r in rows:
            cid = owner.get(r[0])
            if cid in data:
                data[cid].authoritative_copies.setdefault(r[0], []).append(_source(r[1:]))

    # debt components and balance-sheet adjustment facts (authoritative, USD)
    tags = sorted(set(registry.debt_tags) | set(registry.adjustment_tags))
    debt = set(registry.debt_tags)
    for (cid, fid, tag, value, pid, end) in execute(
        cur,
        """
        select f.company_id, f.id, c.tag, f.value, f.period_id, p.end_date
        from core.fact f
        join core.concept c on c.id = f.concept_id
        join core.unit u on u.id = f.unit_id
        join core.period p on p.id = f.period_id
        where f.company_id = any(%s) and f.is_authoritative and c.taxonomy = 'us-gaap'
          and c.tag = any(%s) and u.unit_name = 'usd'
          and (%s::date is null or p.end_date >= %s::date)
        """,
        (ids, tags, since, since),
        timeout_s,
    ):
        comp = ComponentFact(id=fid, tag=tag, value=value, period_id=pid, end=end)
        if tag in debt:
            data[cid].debt_facts.append(comp)
        if tag in registry.adjustment_tags:
            data[cid].adjustment_facts.append(comp)

    # displayed metrics: latest non-null per metric and label class
    for (cid, name, req, label, pend, value, src) in execute(
        cur,
        """
        select distinct on (mv.company_id, md.metric_name,
                            (case when mv.period_label in ('FY', 'TTM') then mv.period_label else 'Q' end))
               mv.company_id, md.metric_name, md.requires_price, mv.period_label, mv.period_end,
               mv.value, mv.source_fact_ids
        from analytics.metric_value mv
        join analytics.metric_definition md on md.id = mv.metric_definition_id
        where mv.company_id = any(%s) and mv.value is not null
        order by mv.company_id, md.metric_name,
                 (case when mv.period_label in ('FY', 'TTM') then mv.period_label else 'Q' end),
                 mv.period_end desc
        """,
        (ids,),
        timeout_s,
    ):
        src_t = tuple(src or ())
        data[cid].metrics.append(
            Metric(name=name, label=label, period_end=pend, value=value, requires_price=req, source_ids=src_t)
        )
    metric_src = sorted({i for d in data.values() for m in d.metrics for i in m.source_ids} - set(all_sources))
    for i in range(0, len(metric_src), SOURCE_BATCH):
        rows = execute(cur, _SOURCE_SELECT + " where f.id = any(%s)", (metric_src[i : i + SOURCE_BATCH],), timeout_s)
        all_sources.update({r[0]: _source(r) for r in rows})
    for d in data.values():
        for m in d.metrics:
            for sid in m.source_ids:
                if sid in all_sources:
                    d.sources[sid] = all_sources[sid]
    for cid, day in load_latest_filed_periods(cur, ids, as_of).items():
        if cid in data:
            data[cid].latest_filed = day

    for cid, eff, ratio in execute(
        cur, "select company_id, effective_date, ratio from analytics.company_stock_split where company_id = any(%s)",
        (ids,), timeout_s,
    ):
        if cid in data:
            data[cid].splits.append((eff, Decimal(ratio)))

    for cid, pdate, price in execute(
        cur,
        """
        select distinct on (company_id) company_id, price_date, price
        from core.market_price_alpaca where company_id = any(%s)
        order by company_id, price_date desc
        """,
        (ids,), timeout_s,
    ):
        if cid in data:
            data[cid].price = (pdate, price)

    for cid, filed in execute(
        cur, "select company_id, filing_date from core.shares_outstanding_fallback where company_id = any(%s)",
        (ids,), timeout_s,
    ):
        if cid in data:
            data[cid].shares_fallback_filed = filed

    # bank population (the one definition in sector_applicability) + evidence flags
    cur.execute("select set_config('statement_timeout', %s, false)", (str(int(timeout_s) * 1000),))
    bank_ids = load_bank_company_ids(cur, ids)
    evidence: dict[int, set[str]] = defaultdict(set)
    for cid, tag in execute(
        cur,
        """
        select distinct bt.company_id, k.tag from analytics.company_sec_tag bt
        join core.concept k on k.id = bt.concept_id
        where bt.company_id = any(%s) and k.taxonomy = 'us-gaap' and k.tag = any(%s)
        """,
        (ids, [BANK_EVIDENCE_EXPENSE_TAG, *BANK_EVIDENCE_DEPOSIT_TAGS]),
        timeout_s,
    ):
        evidence[cid].add(tag)
    for cid, d in data.items():
        has_evidence = BANK_EVIDENCE_EXPENSE_TAG in evidence[cid] and bool(
            evidence[cid] & set(BANK_EVIDENCE_DEPOSIT_TAGS)
        )
        d.is_bank = cid in bank_ids
        d.bank_sic_without_evidence = is_bank_sic(d.sic) and not has_evidence
        d.bank_evidence_without_sic = has_evidence and not is_bank_sic(d.sic)
    if history:
        _load_history(cur, data, ids, registry, since, timeout_s)
    return data


PERIODIC_FILING_FORMS = ("10-K", "10-K/A", "10-KT", "10-KT/A", "10-Q", "10-Q/A", "10-QT", "10-QT/A")


def _load_history(cur, data, ids, registry, since, timeout_s) -> None:
    """I11 inputs: periodic filings, period_gap causes, and every metric_value
    cell of the window. All set-based, one query each, chunk-bounded."""
    floor = since or HISTORY_FLOOR
    for d in data.values():
        d.consumed = dict(registry.consumed)
        d.window_start = floor
    for cid, first in execute(
        cur,
        "select company_id, min(period_of_report) from core.filing where company_id = any(%s) "
        "and form = any(%s) and period_of_report is not null group by company_id",
        (ids, list(PERIODIC_FILING_FORMS)),
        timeout_s,
    ):
        if cid in data:
            data[cid].first_filing_period = first
    for cid, por, form in execute(
        cur,
        "select distinct company_id, period_of_report, form from core.filing where company_id = any(%s) "
        "and form = any(%s) and period_of_report >= %s",
        (ids, list(PERIODIC_FILING_FORMS), floor),
        timeout_s,
    ):
        if cid in data:
            data[cid].filings.append((por, form))
    for cid, name, kind, end, cause in execute(
        cur,
        """
        select pg.company_id, cc.name, pg.period_kind, pg.period_end, pg.gap_cause
        from analytics.period_gap pg join analytics.canonical_concept cc on cc.id = pg.canonical_concept_id
        where pg.company_id = any(%s) and pg.period_end >= %s
        """,
        (ids, floor),
        timeout_s,
    ):
        if cid in data:
            data[cid].period_gaps.append(GapRow(name, kind, end, cause))
    for cid, name, label, end, value, reason in execute(
        cur,
        """
        select mv.company_id, md.metric_name, mv.period_label, mv.period_end, mv.value, mv.is_null_reason
        from analytics.metric_value mv join analytics.metric_definition md on md.id = mv.metric_definition_id
        where mv.company_id = any(%s) and mv.period_end >= %s
          and mv.period_label in ('FY', 'Q1', 'Q2', 'Q3', 'Q4')
        """,
        (ids, floor),
        timeout_s,
    ):
        if cid in data:
            data[cid].metric_history.append(MetricCell(name, label, end, value, reason))
