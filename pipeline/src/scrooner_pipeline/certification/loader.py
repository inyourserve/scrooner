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

from .thresholds import SOURCE_BATCH
from .model import (
    base_name,
    Cell,
    CompanyData,
    ComponentFact,
    GapRow,
    MetricSpec,
    Metric,
    MetricCell,
    NCI_CLAIM_TAGS,
    Source,
    PERIODIC_FORMS,
    PER_SHARE,
)

from .thresholds import (  # noqa: E402
    LEASE_INCLUSIVE_DEBT_TAGS,
    MAX_DURATION_DAYS,
    MIN_EQUAL_VALUE,
    OLD_COMPARATIVE_DAYS,
)

HISTORY_FLOOR = date(2015, 1, 1)  # doc 38: nothing older is displayed as current
DEBT_CONCEPTS = ("total_debt", "total_debt_split")


@dataclass
class Registry:
    names: dict[int, str] = field(default_factory=dict)
    modes: dict[str, str] = field(default_factory=dict)
    debt_tags: list[str] = field(default_factory=list)
    adjustment_tags: list[str] = field(default_factory=list)
    metrics: dict[str, MetricSpec] = field(default_factory=dict)
    consumed: dict[str, str] = field(
        default_factory=dict
    )  # concept feeding >= 1 metric -> statement
    mapped_ids: dict[int, set[str]] = field(
        default_factory=dict
    )  # core.concept id -> consumed bases it maps to
    mapped_tag_count: dict[str, int] = field(
        default_factory=dict
    )  # consumed base -> number of mapped tags
    tag_roles: dict[tuple[str, str], tuple[int, str]] = field(default_factory=dict)


def execute(cur, sql: str, params, timeout_s: int):
    """Run one statement under an explicit statement_timeout and return all rows."""
    cur.execute(
        "select set_config('statement_timeout', %s, false)",
        (str(int(timeout_s) * 1000),),
    )
    cur.execute(sql, params)
    return cur.fetchall()


def load_registry(cur, timeout_s: int = 60) -> Registry:
    reg = Registry()
    for cid, name, mode in execute(
        cur,
        "select id, name, combination_mode from analytics.canonical_concept",
        None,
        timeout_s,
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
    specs: dict[str, dict] = {}
    for mname, desc, req, cname, cstatement in execute(
        cur,
        """
        select md.metric_name, md.formula_description, md.requires_price, cc.name, cc.statement
        from analytics.metric_definition md
        left join analytics.metric_definition_input i on i.metric_definition_id = md.id
        left join analytics.canonical_concept cc on cc.id = i.canonical_concept_id
        where md.status = 'active'
        """,
        None,
        timeout_s,
    ):
        e = specs.setdefault(mname, {"d": desc or "", "r": bool(req), "i": [], "s": []})
        if cname is not None:
            e["i"].append(base_name(cname))
            e["s"].append(cstatement)
    for mname, e in specs.items():
        reg.metrics[mname] = MetricSpec(
            mname, e["d"], e["r"], tuple(e["i"]), tuple(e["s"])
        )
    bases = {base_name(n) for n in reg.consumed}
    for base, concept_id in execute(
        cur,
        """
        select cc.name, cm.concept_id from analytics.concept_mapping cm
        join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
        where cm.confidence <> 'rejected'
        """,
        None,
        timeout_s,
    ):
        b = base_name(base)
        if b in bases:
            reg.mapped_ids.setdefault(concept_id, set()).add(b)
    for bs in reg.mapped_ids.values():
        for b in bs:
            reg.mapped_tag_count[b] = reg.mapped_tag_count.get(b, 0) + 1
    for cname, tag, priority, confidence in execute(
        cur,
        """
        select cc.name, c.tag, cm.priority, cm.confidence from analytics.concept_mapping cm
        join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
        join core.concept c on c.id = cm.concept_id
        where c.taxonomy = 'us-gaap'
        """,
        None,
        timeout_s,
    ):
        key = (base_name(cname), tag)
        if key not in reg.tag_roles or priority < reg.tag_roles[key][0]:
            reg.tag_roles[key] = (priority, confidence)
    reg.adjustment_tags = sorted(
        {tag for i in IDENTITIES for tag, _ in i.adjustments} | set(NCI_CLAIM_TAGS)
    )
    return reg


def resolve_company_ids(cur, ciks: list[str], timeout_s: int = 60) -> list[int]:
    padded = [c.strip().zfill(10) for c in ciks if c.strip()]
    rows = execute(
        cur,
        "select id from core.company where cik = any(%s) order by id",
        (padded,),
        timeout_s,
    )
    return [r[0] for r in rows]


def _source(row) -> Source:
    (fid, tag, value, auth, derived, form, unit, accession, fdate, start, end) = row
    return Source(
        id=fid,
        tag=tag,
        value=value,
        authoritative=auth,
        derived=derived,
        form=form,
        unit=unit,
        accession=accession,
        filing_date=fdate,
        start=start,
        end=end,
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
        cur,
        "select id, cik, primary_ticker, sic_code from core.company where id = any(%s)",
        (ids,),
        timeout_s,
    ):
        data[cid] = CompanyData(
            company_id=cid, cik=cik, ticker=ticker, sic=sic, as_of=as_of
        )

    # canonical values with their periods
    all_source_ids: set[int] = set()
    for cid, name, value, src, pid, start, end, ptype, fy, fp in execute(
        cur,
        """
        select cf.company_id, cc.name, cf.value, cf.source_fact_ids, p.id, p.start_date, p.end_date,
               p.period_type, p.fiscal_year, p.fiscal_period
        from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        join core.period p on p.id = cf.period_id
        where cf.company_id = any(%s) and (%s::date is null or p.end_date >= %s::date)
          -- a duration longer than MAX_DURATION_DAYS is not a reporting period (AZO's
          -- program-to-date repurchases 1998-01-01..2015-05-09, 6,337 days): not displayed,
          -- not checked
          and (p.start_date is null or p.start_date >= p.end_date
               or p.end_date - p.start_date <= %s)
        """,
        (ids, since, since, MAX_DURATION_DAYS),
        timeout_s,
    ):
        if cid not in data or value is None:
            continue
        src_t = tuple(src or ())
        all_source_ids.update(src_t)
        data[cid].cells.append(
            Cell(
                concept=name,
                value=value,
                period_id=pid,
                start=start,
                end=end,
                period_type=ptype,
                fiscal_year=fy,
                fiscal_period=fp,
                source_ids=src_t,
            )
        )
    for d in data.values():
        d.concept_modes = dict(registry.modes)

    # source facts, batched
    wanted = sorted(all_source_ids)
    all_sources: dict[int, Source] = {}
    for i in range(0, len(wanted), SOURCE_BATCH):
        rows = execute(
            cur,
            _SOURCE_SELECT + " where f.id = any(%s)",
            (wanted[i : i + SOURCE_BATCH],),
            timeout_s,
        )
        all_sources.update({r[0]: _source(r) for r in rows})
    for d in data.values():
        for cell in d.cells:
            for sid in cell.source_ids:
                if sid in all_sources:
                    d.sources[sid] = all_sources[sid]

    # authoritative copies of every NON-authoritative source (matching-copies rule)
    non_auth = sorted(
        {s.id for d in data.values() for s in d.sources.values() if not s.authoritative}
    )
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
                data[cid].authoritative_copies.setdefault(r[0], []).append(
                    _source(r[1:])
                )

    # copies, on a 10-K/10-Q-family form, of every source filed on another form (proxy, 8-K)
    non_periodic = sorted(
        {
            s.id
            for d in data.values()
            for s in d.sources.values()
            if s.form is not None and s.form not in PERIODIC_FORMS
        }
    )
    for i in range(0, len(non_periodic), SOURCE_BATCH):
        rows = execute(
            cur,
            """
            select f1.id, f2.id, c.tag, f2.value, f2.is_authoritative, f2.is_derived, fl.form, u.unit_name,
                   fl.accession_number, fl.filing_date, p.start_date, p.end_date
            from core.fact f1
            join core.fact f2 on f2.company_id = f1.company_id and f2.concept_id = f1.concept_id
                 and f2.period_id = f1.period_id and f2.unit_id = f1.unit_id and f2.id <> f1.id
            join core.concept c on c.id = f2.concept_id
            join core.unit u on u.id = f2.unit_id
            join core.period p on p.id = f2.period_id
            join core.filing fl on fl.id = f2.filing_id
            where f1.id = any(%s) and fl.form = any(%s)
            """,
            (non_periodic[i : i + SOURCE_BATCH], sorted(PERIODIC_FORMS)),
            timeout_s,
        )
        for r in rows:
            cid = owner.get(r[0])
            if cid in data:
                data[cid].periodic_copies.setdefault(r[0], []).append(_source(r[1:]))

    # label-shifted quarters: a discrete quarter whose source filing came > 800 days after the
    # quarter ended carries a value identical (same company, concept, unit) to a fact on the
    # same quarter of a later year, in any filing (SWK Q1 2017 revenue 3,209.3M in the FY2019
    # 10-K = the Q1 2018 figure of the FY2018 10-K, carried on a 2017 context)
    old_quarter_ids = sorted(
        {
            s.id
            for d in data.values()
            for s in d.sources.values()
            if s.filing_date is not None
            and s.start is not None
            and s.end is not None
            and 61 <= (s.end - s.start).days <= 121
            and (s.filing_date - s.end).days > OLD_COMPARATIVE_DAYS
            and abs(s.value) >= MIN_EQUAL_VALUE
        }
    )
    for i in range(0, len(old_quarter_ids), SOURCE_BATCH):
        rows = execute(
            cur,
            """
            select f1.id, p2.end_date, f2.id
            from core.fact f1
            join core.period p1 on p1.id = f1.period_id
            join core.period p2 on p2.end_date between p1.end_date + 340 and p1.end_date + 1130
                 and p2.end_date - p2.start_date between 61 and 121
            join core.fact f2 on f2.period_id = p2.id and f2.company_id = f1.company_id
                 and f2.concept_id = f1.concept_id and f2.unit_id = f1.unit_id
                 and f2.value = f1.value
            where f1.id = any(%s)
            """,
            (old_quarter_ids[i : i + SOURCE_BATCH],),
            timeout_s,
        )
        for sid, end2, fid in rows:
            cid = owner.get(sid)
            if cid in data:
                data[cid].label_twins.setdefault(sid, []).append((end2, fid))

    # copies of per-share sources from every filing (a split restates the comparative columns
    # of the filings after it): the only proof that separates a split from an offering
    per_share_ids = sorted(
        {
            sid
            for d in data.values()
            for c in d.cells
            if c.base in PER_SHARE
            for sid in c.source_ids
        }
    )
    for i in range(0, len(per_share_ids), SOURCE_BATCH):
        rows = execute(
            cur,
            """
            select f1.id, f2.id, c.tag, f2.value, f2.is_authoritative, f2.is_derived, fl.form, u.unit_name,
                   fl.accession_number, fl.filing_date, p.start_date, p.end_date
            from core.fact f1
            join core.fact f2 on f2.company_id = f1.company_id and f2.concept_id = f1.concept_id
                 and f2.period_id = f1.period_id and f2.unit_id = f1.unit_id and f2.id <> f1.id
            join core.concept c on c.id = f2.concept_id
            join core.unit u on u.id = f2.unit_id
            join core.period p on p.id = f2.period_id
            join core.filing fl on fl.id = f2.filing_id
            where f1.id = any(%s) and not f2.is_derived
            """,
            (per_share_ids[i : i + SOURCE_BATCH],),
            timeout_s,
        )
        for r in rows:
            cid = owner.get(r[0])
            if cid in data:
                data[cid].pershare_copies.setdefault(r[0], []).append(_source(r[1:]))

    # fact counts of the 8-K filings used as sources: does the 8-K carry full statements?
    eight_k = sorted(
        {
            s.accession
            for d in data.values()
            for s in d.sources.values()
            if s.form in ("8-K", "8-K/A") and s.accession
        }
    )
    counts: dict[str, int] = {}
    for i in range(0, len(eight_k), 500):
        for acc, n in execute(
            cur,
            "select fl.accession_number, count(*) from core.fact f join core.filing fl on fl.id = f.filing_id "
            "where fl.accession_number = any(%s) group by fl.accession_number",
            (eight_k[i : i + 500],),
            timeout_s,
        ):
            counts[acc] = n
    for d in data.values():
        d.filing_fact_counts = counts
        d.tag_roles = registry.tag_roles

    # other non-authoritative copies (a recorded conflict fill has >= 2 non-authoritative copies)
    for i in range(0, len(non_auth), SOURCE_BATCH):
        rows = execute(
            cur,
            """
            select f1.id, f2.id, c.tag, f2.value, f2.is_authoritative, f2.is_derived, fl.form, u.unit_name,
                   fl.accession_number, fl.filing_date, p.start_date, p.end_date
            from core.fact f1
            join core.fact f2 on f2.company_id = f1.company_id and f2.concept_id = f1.concept_id
                 and f2.period_id = f1.period_id and f2.unit_id = f1.unit_id
                 and not f2.is_authoritative and f2.id <> f1.id
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
                data[cid].conflict_copies.setdefault(r[0], []).append(_source(r[1:]))

    # debt components and balance-sheet adjustment facts (authoritative, USD)
    tags = sorted(
        set(registry.debt_tags)
        | set(LEASE_INCLUSIVE_DEBT_TAGS)
        | set(registry.adjustment_tags)
    )
    debt = set(registry.debt_tags) | set(LEASE_INCLUSIVE_DEBT_TAGS)
    for cid, fid, tag, value, pid, end in execute(
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
    for cid, name, req, label, pend, value, src in execute(
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
            Metric(
                name=name,
                label=label,
                period_end=pend,
                value=value,
                requires_price=req,
                source_ids=src_t,
            )
        )
    metric_src = sorted(
        {i for d in data.values() for m in d.metrics for i in m.source_ids}
        - set(all_sources)
    )
    for i in range(0, len(metric_src), SOURCE_BATCH):
        rows = execute(
            cur,
            _SOURCE_SELECT + " where f.id = any(%s)",
            (metric_src[i : i + SOURCE_BATCH],),
            timeout_s,
        )
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
        cur,
        "select company_id, effective_date, ratio from analytics.company_stock_split where company_id = any(%s)",
        (ids,),
        timeout_s,
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
        (ids,),
        timeout_s,
    ):
        if cid in data:
            data[cid].price = (pdate, price)

    for cid, filed in execute(
        cur,
        "select company_id, filing_date from core.shares_outstanding_fallback where company_id = any(%s)",
        (ids,),
        timeout_s,
    ):
        if cid in data:
            data[cid].shares_fallback_filed = filed

    # bank population (the one definition in sector_applicability) + evidence flags
    cur.execute(
        "select set_config('statement_timeout', %s, false)",
        (str(int(timeout_s) * 1000),),
    )
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


PERIODIC_FILING_FORMS = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "10-Q",
    "10-Q/A",
    "10-QT",
    "10-QT/A",
)


def _load_history(cur, data, ids, registry, since, timeout_s) -> None:
    """I11 inputs: periodic filings, period_gap causes, and every metric_value
    cell of the window. All set-based, one query each, chunk-bounded."""
    floor = since or HISTORY_FLOOR
    for d in data.values():
        d.consumed = dict(registry.consumed)
        d.window_start = floor
    if registry.mapped_ids:
        seen: dict[int, dict[str, set]] = defaultdict(lambda: defaultdict(set))
        for cid, concept_id, start, end in execute(
            cur,
            """
            select distinct f.company_id, f.concept_id, p.start_date, p.end_date
            from core.fact f join core.period p on p.id = f.period_id
            where f.company_id = any(%s) and f.concept_id = any(%s) and p.end_date >= %s
            """,
            (ids, sorted(registry.mapped_ids), floor),
            timeout_s,
        ):
            for b in registry.mapped_ids.get(concept_id, ()):
                seen[cid][b].add((start, end))
        for cid, by_base in seen.items():
            if cid in data:
                data[cid].mapped_facts = {
                    b: sorted(v, key=lambda t: t[1]) for b, v in by_base.items()
                }
    for d in data.values():
        d.mapped_tag_count = dict(registry.mapped_tag_count)
        d.metric_specs = registry.metrics
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
    kinds_seen: dict[str, set[str]] = defaultdict(set)
    for d in data.values():
        for m in d.metric_history:
            kinds_seen[m.name].add("FY" if m.label == "FY" else "Q")
    for cid, first in execute(
        cur,
        "select cf.company_id, min(p.end_date) from analytics.canonical_fact cf "
        "join core.period p on p.id = cf.period_id where cf.company_id = any(%s) group by cf.company_id",
        (ids,),
        timeout_s,
    ):
        if cid in data:
            data[cid].first_data_period = first
    for d in data.values():
        d.metric_kinds_seen = kinds_seen
