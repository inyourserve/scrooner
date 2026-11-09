"""The FSN-era certification ladder above `checks_clean` (founder approval relayed by Dhairya,
2026-11-09, worded in data-team/strategy/team/CERTIFICATION-BLOCKERS-2026-11-09.md step 2):

  checks_clean  I1-I11 clean: written by `scrooner-certify` (unchanged)
  reconciled    every headline cell PROVEN in analytics.cell_proof, none DISAGREE
  verified      a recorded Verifier check (analytics.verifier_check, 0122) of the headline
                cells, latest FY + latest Q, with accession and locator
  certified     all of the above plus every template cell valued or reasoned

`scrooner-certify-promote` decides the HIGHEST rung that holds today and writes it: it promotes
and it demotes (a new DISAGREE, a superseded Verifier verdict or a changed value takes a
company back down), so the state always reflects current evidence. It never moves a company
out of `uncertified` (only the invariant suite does that) and never creates a row. Run it after
`scrooner-certify`. Dry run by default; --apply writes analytics.company_certification only.

Exact tests, per company (headline data points out of the company's sector template are not
required):
  reconciled  For each headline concept: every served cell in the window was written by the
              hybrid (FSN store: canonical_fact.rule_run_id -> an `fsn.*` rule run; founder
              direction 2026-11-09, one source, the hybrid), at least one served cell exists,
              and EVERY served cell has a cell_proof row (same data point, period start and end,
              basis latest, newest row) that is PROVEN with shown_value equal to the value served
              now (a proof of an older value is stale). No cell_proof row of a headline concept
              is DISAGREE. market_cap is a price metric with no filing line: it is checked by the
              Verifier only.
  verified    For each headline concept, its latest PROVEN cell per grain (flows: FY and Q;
              instants: I) has a `right` verifier_check row for the same grain and period end
              whose shown_value equals the proven shown value. market_cap needs a `right` row
              checked within MARKET_CAP_MAX_AGE_DAYS. The company has no open (not superseded)
              `wrong` or `blank_wrong` row.
  certified   The company has a current sector template (0120), and every in-template data point
              is valued by the hybrid (a served canonical_fact cell under an `fsn.*` rule run, by
              base name; for a metric, a metric_value with a value) or its newest blank reason
              (analytics.cell_blank_reason, latest basis) is classified (not a defect of class
              unclassified). Old-pipeline summaries (company_data_point_coverage) are not read.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from .model import base_name

LADDER = ("uncertified", "checks_clean", "reconciled", "verified", "certified")
RANK = {s: i for i, s in enumerate(LADDER)}

# Doc 34 rung 4: the headline cells, under the names cell_proof and canonical_fact use.
HEADLINE_FLOWS = (
    "revenue_sanity_resolved",
    "operating_income_resolved",
    "net_income_resolved",
    "diluted_eps_resolved",
    "cfo_resolved",
    "capex_resolved",
)
HEADLINE_INSTANTS = (
    "total_assets_resolved",
    "stockholders_equity_resolved",
    "shares_outstanding_resolved",
    "total_debt_resolved",
)
HEADLINE_PROVED = HEADLINE_FLOWS + HEADLINE_INSTANTS
MARKET_CAP = "market_cap"
MARKET_CAP_MAX_AGE_DAYS = 31  # ASSUMED: a market-cap check older than a month is stale
HISTORY_FLOOR = date(2015, 1, 1)


@dataclass
class Evidence:
    company_id: int
    state: str  # current company_certification.state
    template_rows: list[tuple[str, bool]] = field(default_factory=list)
    # concept -> (served cells, proven-and-current cells)
    served: dict[str, tuple[int, int]] = field(default_factory=dict)
    disagree: dict[str, int] = field(default_factory=dict)
    # concept -> served cells written by the hybrid (canonical_fact under an fsn.* rule run)
    hybrid: dict[str, int] = field(default_factory=dict)
    # (concept, grain) -> (period_end, shown_value) of the latest PROVEN cell
    latest: dict[tuple[str, str], tuple[date, Decimal]] = field(default_factory=dict)
    # verifier rows: (data_point, grain, period_end, verdict, shown_value, checked_at)
    checks: list[tuple[str, str, date, str, Decimal | None, datetime]] = field(
        default_factory=list
    )
    open_wrong: int = 0
    template_cells: int = 0
    template_accounted: int = 0


@dataclass(frozen=True)
class Decision:
    company_id: int
    old_state: str
    new_state: str
    blockers: tuple[str, ...]


def template_out(rows: list[tuple[str, bool]]) -> set[str]:
    """Base names OUT of the current template: every row mapping to the base says no."""
    by_base: dict[str, list[bool]] = defaultdict(list)
    for dp, flag in rows:
        by_base[base_name(dp)].append(bool(flag))
    return {b for b, flags in by_base.items() if not any(flags)}


def required(ev: Evidence) -> tuple[list[str], bool]:
    """Headline concepts this company must prove, and whether market cap is required."""
    out = template_out(ev.template_rows)
    concepts = [c for c in HEADLINE_PROVED if base_name(c) not in out]
    return concepts, MARKET_CAP not in out


def _reconciled(ev: Evidence, concepts: list[str]) -> list[str]:
    blockers = []
    for c in concepts:
        served, proven = ev.served.get(c, (0, 0))
        if served == 0:
            blockers.append(f"reconciled:no_served_cell:{c}")
        elif proven < served:
            blockers.append(f"reconciled:unproven:{c}:{served - proven}_of_{served}")
        old = served - ev.hybrid.get(c, served)
        if old > 0:
            blockers.append(f"reconciled:not_hybrid:{c}:{old}_of_{served}")
        if ev.disagree.get(c):
            blockers.append(f"reconciled:disagree:{c}:{ev.disagree[c]}")
    return blockers


def _grains(concept: str) -> tuple[str, ...]:
    return ("I",) if concept in HEADLINE_INSTANTS else ("FY", "Q")


def _verified(
    ev: Evidence, concepts: list[str], need_mcap: bool, now: datetime
) -> list[str]:
    blockers = []
    right = {
        (dp, grain, end, value)
        for dp, grain, end, verdict, value, _at in ev.checks
        if verdict == "right"
    }
    for c in concepts:
        for grain in _grains(c):
            cell = ev.latest.get((c, grain))
            if cell is None:
                blockers.append(f"verified:no_latest_proven_cell:{c}:{grain}")
                continue
            end, value = cell
            if (c, grain, end, value) not in right:
                blockers.append(f"verified:no_right_check:{c}:{grain}:{end}")
    if need_mcap and not any(
        dp == MARKET_CAP
        and verdict == "right"
        and now - at <= timedelta(days=MARKET_CAP_MAX_AGE_DAYS)
        for dp, _g, _e, verdict, _v, at in ev.checks
    ):
        blockers.append("verified:no_recent_right_check:market_cap")
    if ev.open_wrong:
        blockers.append(f"verified:open_wrong_verdicts:{ev.open_wrong}")
    return blockers


def _certified(ev: Evidence) -> list[str]:
    if not ev.template_rows:
        return ["certified:no_sector_template"]
    if ev.template_accounted < ev.template_cells:
        return [
            f"certified:template_cells_unaccounted:{ev.template_cells - ev.template_accounted}"
            f"_of_{ev.template_cells}"
        ]
    return []


def decide(ev: Evidence, now: datetime) -> Decision:
    """The highest rung that holds; a failing rung stops the climb and names why."""
    if ev.state == "uncertified":
        return Decision(
            ev.company_id, ev.state, "uncertified", ("checks_clean:invariant_suite",)
        )
    concepts, need_mcap = required(ev)
    state = "checks_clean"
    for rung, blockers in (
        ("reconciled", lambda: _reconciled(ev, concepts)),
        ("verified", lambda: _verified(ev, concepts, need_mcap, now)),
        ("certified", lambda: _certified(ev)),
    ):
        found = blockers()
        if found:
            return Decision(ev.company_id, ev.state, state, tuple(found))
        state = rung
    return Decision(ev.company_id, ev.state, state, ())


# --------------------------------------------------------------------------- SQL

STATE_SQL = """
    select company_id, state from analytics.company_certification where company_id = any(%(ids)s)
"""

TEMPLATE_SQL = """
    with latest as (
        select company_id, max(effective_from) as effective_from
        from analytics.company_data_point_template
        where company_id = any(%(ids)s) and effective_from <= %(as_of)s
        group by company_id
    )
    select t.company_id, t.data_point, t.in_template
    from analytics.company_data_point_template t
    join latest l on l.company_id = t.company_id and l.effective_from = t.effective_from
"""

SERVED_SQL = """
    select cf.company_id, cc.name, count(*) as served,
           count(*) filter (where pr.verdict = 'PROVEN' and pr.shown_value = cf.value) as proven,
           count(*) filter (where rr.rule_id like 'fsn.%%') as hybrid
    from analytics.canonical_fact cf
    join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
    join core.period p on p.id = cf.period_id
    left join analytics.rule_run rr on rr.run_id = cf.rule_run_id
    left join lateral (
        select cp.verdict, cp.shown_value
        from analytics.cell_proof cp
        where cp.company_id = cf.company_id and cp.data_point_name = cc.name
          and cp.period_start = p.start_date and cp.period_end = p.end_date
          and cp.basis = 'latest'
        order by cp.proved_at desc, cp.id desc
        limit 1
    ) pr on true
    where cf.company_id = any(%(ids)s) and cc.name = any(%(names)s) and p.end_date >= %(floor)s
    group by cf.company_id, cc.name
"""

DISAGREE_SQL = """
    select company_id, data_point_name, count(*)
    from (
        select distinct on (company_id, data_point_name, period_grain, period_start, period_end)
               company_id, data_point_name, verdict
        from analytics.cell_proof
        where company_id = any(%(ids)s) and data_point_name = any(%(names)s) and basis = 'latest'
          and period_end >= %(floor)s
        order by company_id, data_point_name, period_grain, period_start, period_end,
                 proved_at desc, id desc
    ) newest
    where verdict = 'DISAGREE'
    group by company_id, data_point_name
"""

LATEST_PROVEN_SQL = """
    select distinct on (company_id, data_point_name, period_grain)
           company_id, data_point_name, period_grain, period_end, shown_value
    from analytics.cell_proof
    where company_id = any(%(ids)s) and data_point_name = any(%(names)s) and basis = 'latest'
      and verdict = 'PROVEN' and period_grain in ('FY', 'Q', 'I')
    order by company_id, data_point_name, period_grain, period_end desc, proved_at desc, id desc
"""

CHECKS_SQL = """
    select company_id, data_point_name, period_grain, period_end, verdict, shown_value, checked_at
    from analytics.verifier_check
    where company_id = any(%(ids)s) and superseded_at is null and basis = 'latest'
"""

# The cell writer stores concept names (revenue_sanity_resolved, x_resolved); templates and
# reasons may use either layer's name: compare on the base name (model.base_name in SQL).
_BASE = (
    "case when {c} = 'revenue_sanity_resolved' then 'revenue'"
    " else regexp_replace({c}, '_resolved$', '') end"
)

TEMPLATE_COVERAGE_SQL = f"""
    with latest as (
        select company_id, max(effective_from) as effective_from
        from analytics.company_data_point_template
        where company_id = any(%(ids)s) and effective_from <= %(as_of)s
        group by company_id
    ), cells as (
        select t.company_id, t.data_point, {_BASE.format(c="t.data_point")} as base
        from analytics.company_data_point_template t
        join latest l on l.company_id = t.company_id and l.effective_from = t.effective_from
        where t.in_template
    ), hybrid as (
        select distinct cf.company_id, {_BASE.format(c="cc.name")} as base
        from analytics.canonical_fact cf
        join analytics.rule_run rr on rr.run_id = cf.rule_run_id and rr.rule_id like 'fsn.%%'
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        where cf.company_id = any(%(ids)s)
    )
    select c.company_id, count(*) as cells,
           count(*) filter (where exists (
               select 1 from hybrid h where h.company_id = c.company_id and h.base = c.base
           ) or exists (
               select 1 from analytics.metric_value mv
               join analytics.metric_definition md on md.id = mv.metric_definition_id
               where mv.company_id = c.company_id and md.metric_name = c.data_point
                 and md.status = 'active' and mv.value is not null
           ) or (
               select not (b.state = 'defect' and coalesce(b.defect_class, 'unclassified') = 'unclassified')
               from analytics.cell_blank_reason b
               where b.company_id = c.company_id and b.basis = 'latest'
                 and {_BASE.format(c="b.data_point_name")} = c.base
               order by b.created_at desc, b.id desc
               limit 1
           )) as accounted
    from cells c
    group by c.company_id
"""

UPDATE_SQL = """
    update analytics.company_certification set
        state = %(state)s,
        reconciled_at = case when %(rank)s >= 2 then coalesce(reconciled_at, %(now)s) end,
        verified_at = case when %(rank)s >= 3 then coalesce(verified_at, %(now)s) end,
        certified_at = case when %(rank)s >= 4 then coalesce(certified_at, %(now)s) end
    where company_id = %(company_id)s
"""


class MigrationNotAppliedError(RuntimeError):
    pass


def _rows(cur, sql: str, params: dict, timeout_s: int):
    cur.execute(
        "select set_config('statement_timeout', %s, false)", (str(timeout_s * 1000),)
    )
    cur.execute(sql, params)
    return cur.fetchall()


def verifier_table_exists(cur) -> bool:
    cur.execute(
        "select count(*) from pg_catalog.pg_class c join pg_catalog.pg_namespace n "
        "on n.oid = c.relnamespace where n.nspname = 'analytics' and c.relname = 'verifier_check'"
    )
    row = cur.fetchone()
    return bool(row and row[0])


def load_evidence(
    cur, ids: list[int], as_of: date, timeout_s: int = 15
) -> dict[int, Evidence]:
    """Set-based reads for one chunk of companies. Companies without a certification row (the
    invariant suite never ran for them) are left out: promote never creates a row."""
    p = {
        "ids": ids,
        "as_of": as_of,
        "floor": HISTORY_FLOOR,
        "names": list(HEADLINE_PROVED),
    }
    ev = {
        cid: Evidence(cid, state) for cid, state in _rows(cur, STATE_SQL, p, timeout_s)
    }
    for cid, dp, flag in _rows(cur, TEMPLATE_SQL, p, timeout_s):
        if cid in ev:
            ev[cid].template_rows.append((dp, flag))
    for cid, name, served, proven, hybrid in _rows(cur, SERVED_SQL, p, timeout_s):
        if cid in ev:
            ev[cid].served[name] = (int(served), int(proven))
            ev[cid].hybrid[name] = int(hybrid)
    for cid, name, n in _rows(cur, DISAGREE_SQL, p, timeout_s):
        if cid in ev:
            ev[cid].disagree[name] = int(n)
    for cid, name, grain, end, value in _rows(cur, LATEST_PROVEN_SQL, p, timeout_s):
        if cid in ev:
            ev[cid].latest[(name, grain)] = (end, value)
    if verifier_table_exists(cur):
        for cid, dp, grain, end, verdict, value, at in _rows(
            cur, CHECKS_SQL, p, timeout_s
        ):
            if cid not in ev:
                continue
            ev[cid].checks.append((dp, grain, end, verdict, value, at))
            if verdict in ("wrong", "blank_wrong"):
                ev[cid].open_wrong += 1
    for cid, cells, accounted in _rows(cur, TEMPLATE_COVERAGE_SQL, p, timeout_s):
        if cid in ev:
            ev[cid].template_cells, ev[cid].template_accounted = (
                int(cells),
                int(accounted),
            )
    return ev


def promote(
    conn,
    ids: list[int],
    *,
    apply: bool = False,
    as_of: date | None = None,
    now: datetime | None = None,
    chunk_size: int = 50,
    timeout_s: int = 15,
) -> list[Decision]:
    """Decide every company; with apply, write the changed states, one transaction per chunk."""
    as_of = as_of or date.today()
    now = now or datetime.now(timezone.utc)
    decisions: list[Decision] = []
    for i in range(0, len(ids), chunk_size):
        chunk = ids[i : i + chunk_size]
        with conn.cursor() as cur:
            if apply and not verifier_table_exists(cur):
                raise MigrationNotAppliedError(
                    "analytics.verifier_check does not exist: apply migration 0122 first"
                )
            evidence = load_evidence(cur, chunk, as_of, timeout_s)
        got = [decide(evidence[cid], now) for cid in chunk if cid in evidence]
        decisions += got
        if apply:
            with conn.transaction(), conn.cursor() as cur:
                for d in got:
                    cur.execute(
                        UPDATE_SQL,
                        {
                            "state": d.new_state,
                            "rank": RANK[d.new_state],
                            "now": now,
                            "company_id": d.company_id,
                        },  # fmt: skip
                    )
    if apply:
        conn.commit()
    return decisions


def render(decisions: list[Decision], tickers: dict[int, str] | None = None) -> str:
    tickers = tickers or {}
    counts: dict[str, int] = defaultdict(int)
    lines = []
    for d in decisions:
        counts[d.new_state] += 1
        move = "" if d.new_state == d.old_state else f" (was {d.old_state})"
        lines.append(
            f"  {tickers.get(d.company_id, d.company_id)}: {d.new_state}{move}"
        )
        lines += [f"    - {b}" for b in d.blockers[:12]]
        if len(d.blockers) > 12:
            lines.append(f"    - ... {len(d.blockers) - 12} more")
    head = "states: " + ", ".join(f"{s} {counts[s]}" for s in LADDER if counts[s])
    return "\n".join([head, *lines])
