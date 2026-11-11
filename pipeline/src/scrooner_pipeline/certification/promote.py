"""The FSN-era certification ladder above `checks_clean` (founder approval relayed by Dhairya,
2026-11-09; data-team/strategy/team/CERTIFICATION-BLOCKERS-2026-11-09.md step 2), hardened by
the Verifier FIX of 2026-11-09 (VERIFY-TEMPLATES-AND-LADDER-2026-11-09, holes 1-6 and the two
blank weaknesses):

  checks_clean  I1-I11 clean: written by `scrooner-certify` (unchanged)
  reconciled    every served headline cell hybrid-written and PROVEN with a face read on the latest print,
                and no DISAGREE on any cell of the company
  verified      Verifier records (analytics.verifier_check, 0124, written by the Verifier only): the
                headline cells' latest FY + Q, and a seeded draw over ALL shown cells whose hash still
                matches the cells served now
  certified     all of the above, every template cell valued or reasoned, and a Verifier blank draw
                that confirms the reasons

`scrooner-certify-promote` decides the HIGHEST rung that holds today and writes it: it promotes and it
demotes, so the state always reflects current evidence. It never moves a company out of `uncertified`
and never creates a row. Run it after `scrooner-certify`. Dry run by default; --apply writes
analytics.company_certification only.

Exact tests, per company (headline data points out of the company's sector template are not required):

reconciled
  For each headline concept: at least one served canonical_fact cell since 2015, and every served cell
  (a) was written by the hybrid (rule_run `fsn.*`; founder direction 2026-11-09), and
  (b) has a newest cell_proof row (same data point, start, end, basis latest) that counts as proven
      (`PROVEN_ROW` below):
      - verdict PROVEN on the value served now (a proof of an older value is stale);
      - an independent face read (hole 3): face_value and face_label recorded, face_value (x face_scale)
        equal to the shown value, and the label not a segment line. A derived cell has no face (hole 5):
        it counts only when the proof records checks.derived = true, checks.inputs_proven = true and a
        checks.same_basis_witness. A note-sourced cell is read on its note page like a face;
      - the latest print (hole 4): no later accepted filing of the company prints the shown tag at that
        column (FSN ddate is the month-end-rounded period end, qtrs FY 4 / Q 1 / I 0).
  No cell_proof row of ANY data point of the company is DISAGREE in its newest row (hole 2).
  market_cap has no filing line: Verifier only.

verified
  - For each headline concept, its latest counted cell per grain (flows FY and Q, instants I) has a
    `right` verifier_check row (same grain and period end, the same shown value).
  - market_cap: a `right` row checked within MARKET_CAP_MAX_AGE_DAYS.
  - All shown cells (hole 1, hole 6): the company's newest `all_cells` draw has at least
    ALL_CELLS_DRAW_MIN rows, all `right` or `blank_right`, and its cells_hash equals the hash of the
    cells served now (`company_cells_hash`): any later change to a shown cell or metric value drops the
    company below verified until the Verifier draws again.
  - No open (not superseded) `wrong` or `blank_wrong` row.

certified
  - A current sector template (0120), and every in-template data point valued by the hybrid (a served
    fsn-written cell by base name; for a metric, a metric_value with a value) or with a classified
    newest blank reason.
  - Reasons confirmed (the blank weakness): when the company has reasoned blanks, its newest `blanks`
    draw has at least min(BLANK_DRAW_MIN, reasoned cells) rows, all `blank_right`.

Scope, stated as the Verifier asked: certified proves the headline cells by proof and filing check, and
every other shown cell by the invariant suite plus a seeded random draw. It does not prove each
non-headline cell individually. The sector-template seed FIXes must land before certified is trusted.
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
ALL_CELLS_DRAW_MIN = 20  # ASSUMED (design §5 pilot draws 40 cells per company); a Verifier/approver number
BLANK_DRAW_MIN = 10  # ASSUMED, same basis
HISTORY_FLOOR = date(2015, 1, 1)


@dataclass
class Evidence:
    company_id: int
    state: str  # current company_certification.state
    template_rows: list[tuple[str, bool]] = field(default_factory=list)
    # concept -> (served cells, counted-proven cells)
    served: dict[str, tuple[int, int]] = field(default_factory=dict)
    # concept -> served cells written by the hybrid (canonical_fact under an fsn.* rule run)
    hybrid: dict[str, int] = field(default_factory=dict)
    # data point (any) -> cells whose newest proof row is DISAGREE
    disagree: dict[str, int] = field(default_factory=dict)
    # (concept, grain) -> (period_end, shown_value) of the latest counted-proven cell
    latest: dict[tuple[str, str], tuple[date, Decimal]] = field(default_factory=dict)
    # verifier rows: (data_point, grain, period_end, verdict, shown_value, checked_at, draw_id, draw_kind, cells_hash)
    checks: list[tuple] = field(default_factory=list)
    open_wrong: int = 0
    template_cells: int = 0
    template_accounted: int = 0
    template_reasoned: int = 0
    cells_hash: str | None = None


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
            continue
        old = served - ev.hybrid.get(c, served)
        if old > 0:
            blockers.append(f"reconciled:not_hybrid:{c}:{old}_of_{served}")
        if proven < served:
            blockers.append(f"reconciled:unproven:{c}:{served - proven}_of_{served}")
    for dp, n in sorted(
        ev.disagree.items()
    ):  # hole 2: any data point, not only the headline
        blockers.append(f"reconciled:disagree:{dp}:{n}")
    return blockers


def _grains(concept: str) -> tuple[str, ...]:
    return ("I",) if concept in HEADLINE_INSTANTS else ("FY", "Q")


def _newest_draw(ev: Evidence, kind: str) -> list[tuple]:
    rows = [r for r in ev.checks if r[7] == kind]
    if not rows:
        return []
    newest = max(rows, key=lambda r: r[5])[
        6
    ]  # the draw_id of the newest row of that kind
    return [r for r in rows if r[6] == newest]


def _verified(
    ev: Evidence, concepts: list[str], need_mcap: bool, now: datetime
) -> list[str]:
    blockers = []
    right = {(r[0], r[1], r[2], r[4]) for r in ev.checks if r[3] == "right"}
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
        r[0] == MARKET_CAP
        and r[3] == "right"
        and now - r[5] <= timedelta(days=MARKET_CAP_MAX_AGE_DAYS)
        for r in ev.checks
    ):
        blockers.append("verified:no_recent_right_check:market_cap")
    draw = _newest_draw(ev, "all_cells")
    if len(draw) < ALL_CELLS_DRAW_MIN:
        blockers.append(
            f"verified:all_cells_draw:{len(draw)}_of_min_{ALL_CELLS_DRAW_MIN}"
        )
    else:
        if any(r[3] not in ("right", "blank_right") for r in draw):
            blockers.append("verified:all_cells_draw_not_clean")
        if {r[8] for r in draw} != {ev.cells_hash}:
            blockers.append("verified:cells_changed_since_draw")  # hole 6
    if ev.open_wrong:
        blockers.append(f"verified:open_wrong_verdicts:{ev.open_wrong}")
    return blockers


def _certified(ev: Evidence) -> list[str]:
    if not ev.template_rows:
        return ["certified:no_sector_template"]
    blockers = []
    if ev.template_accounted < ev.template_cells:
        blockers.append(
            f"certified:template_cells_unaccounted:{ev.template_cells - ev.template_accounted}"
            f"_of_{ev.template_cells}"
        )
    if ev.template_reasoned:
        need = min(BLANK_DRAW_MIN, ev.template_reasoned)
        draw = _newest_draw(ev, "blanks")
        good = sum(1 for r in draw if r[3] == "blank_right")
        if len(draw) < need or good < len(draw):
            blockers.append(
                f"certified:blank_draw:{good}_right_of_{len(draw)}_min_{need}"
            )
    return blockers


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

# FSN ddate is the period end rounded to the month end (mind: fsn-data-set-facts-...): day <= 15 -> the
# previous month end, else this month end.
_FSN_DDATE = (
    "case when extract(day from {d}) <= 15 then (date_trunc('month', {d}) - interval '1 day')::date"
    " else (date_trunc('month', {d}) + interval '1 month' - interval '1 day')::date end"
)
_QTRS = "case {g} when 'FY' then 4 when 'Q' then 1 else 0 end"

# A proof row counts as proven (holes 3, 4, 5): PROVEN on the value served now, a face read (or, for a
# derived cell, proven inputs with a same-basis witness), not a segment line, and the latest print.
PROVEN_ROW = f"""(
    pr.verdict = 'PROVEN' and pr.shown_value = {{value}}
    and (
        (pr.face_value is not null and coalesce(btrim(pr.face_label), '') <> ''
         and (pr.face_value = pr.shown_value or pr.face_value * coalesce(pr.face_scale, 1) = pr.shown_value)
         and pr.face_label !~* '\\msegments?\\M')
        or (pr.checks->>'derived' = 'true' and pr.checks->>'inputs_proven' = 'true'
            and coalesce(pr.checks->>'same_basis_witness', '') <> '')
    )
    and not exists (
        select 1
        from fsn.filing f1
        join fsn.filing f2 on f2.company_id = f1.company_id and f2.accepted > f1.accepted
        join fsn.value v on v.filing_id = f2.id and v.dim_id = 0 and v.coreg = '' and v.iprx = 0
        join fsn.tag t on t.id = v.tag_id
        where f1.accession = pr.shown_accession and t.tag = pr.shown_tag
          and v.ddate = {_FSN_DDATE.format(d="pr.period_end")} and v.qtrs = {_QTRS.format(g="pr.period_grain")}
    )
)"""

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

_NEWEST_PROOF = """
    left join lateral (
        select cp.*
        from analytics.cell_proof cp
        where cp.company_id = cf.company_id and cp.data_point_name = cc.name
          and cp.period_start = p.start_date and cp.period_end = p.end_date
          and cp.basis = 'latest'
        order by cp.proved_at desc, cp.id desc
        limit 1
    ) pr on true
"""

SERVED_SQL = f"""
    select cf.company_id, cc.name, count(*) as served,
           count(*) filter (where {PROVEN_ROW.format(value="cf.value")}) as proven,
           count(*) filter (where rr.rule_id like 'fsn.%%') as hybrid
    from analytics.canonical_fact cf
    join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
    join core.period p on p.id = cf.period_id
    left join analytics.rule_run rr on rr.run_id = cf.rule_run_id
    {_NEWEST_PROOF}
    where cf.company_id = any(%(ids)s) and cc.name = any(%(names)s) and p.end_date >= %(floor)s
    group by cf.company_id, cc.name
"""

DISAGREE_SQL = """
    select company_id, data_point_name, count(*)
    from (
        select distinct on (company_id, data_point_name, period_grain, period_start, period_end)
               company_id, data_point_name, verdict
        from analytics.cell_proof
        where company_id = any(%(ids)s) and basis = 'latest' and period_end >= %(floor)s
        order by company_id, data_point_name, period_grain, period_start, period_end,
                 proved_at desc, id desc
    ) newest
    where verdict = 'DISAGREE'
    group by company_id, data_point_name
"""

LATEST_PROVEN_SQL = f"""
    select distinct on (cf.company_id, cc.name, pr.period_grain)
           cf.company_id, cc.name, pr.period_grain, p.end_date, cf.value
    from analytics.canonical_fact cf
    join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
    join core.period p on p.id = cf.period_id
    {_NEWEST_PROOF}
    where cf.company_id = any(%(ids)s) and cc.name = any(%(names)s) and p.end_date >= %(floor)s
      and pr.period_grain in ('FY', 'Q', 'I') and {PROVEN_ROW.format(value="cf.value")}
    order by cf.company_id, cc.name, pr.period_grain, p.end_date desc
"""

CHECKS_SQL = """
    select company_id, data_point_name, period_grain, period_end, verdict, shown_value, checked_at,
           draw_id, draw_kind, cells_hash
    from analytics.verifier_check
    where company_id = any(%(ids)s) and superseded_at is null and basis = 'latest'
"""

# hole 6: one hash over every cell the company shows today (canonical values since 2015 and metric values)
CELLS_HASH_SQL = """
    select c.id, md5(
        coalesce((
            select string_agg(cc.name || '|' || p.start_date || '|' || p.end_date || '|' || cf.value::text,
                              ';' order by cc.name, p.start_date, p.end_date)
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cf.company_id = c.id and p.end_date >= %(floor)s
        ), '') || '#' ||
        coalesce((
            select string_agg(md.metric_name || '|' || mv.period_label || '|' || mv.period_start || '|'
                              || mv.period_end || '|' || coalesce(mv.value::text, 'null'),
                              ';' order by md.metric_name, mv.period_label, mv.period_start, mv.period_end)
            from analytics.metric_value mv
            join analytics.metric_definition md on md.id = mv.metric_definition_id
            where mv.company_id = c.id and mv.period_end >= %(floor)s
        ), '')
    )
    from core.company c
    where c.id = any(%(ids)s)
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
    ), judged as (
        select c.company_id,
               exists (
                   select 1 from hybrid h where h.company_id = c.company_id and h.base = c.base
               ) or exists (
                   select 1 from analytics.metric_value mv
                   join analytics.metric_definition md on md.id = mv.metric_definition_id
                   where mv.company_id = c.company_id and md.metric_name = c.data_point
                     and md.status = 'active' and mv.value is not null
               ) as valued,
               (
                   select not (b.state = 'defect' and coalesce(b.defect_class, 'unclassified') = 'unclassified')
                   from analytics.cell_blank_reason b
                   where b.company_id = c.company_id and b.basis = 'latest'
                     and {_BASE.format(c="b.data_point_name")} = c.base
                   order by b.created_at desc, b.id desc
                   limit 1
               ) as reasoned
        from cells c
    )
    select company_id, count(*) as cells,
           count(*) filter (where valued or coalesce(reasoned, false)) as accounted,
           count(*) filter (where not valued and coalesce(reasoned, false)) as reasoned
    from judged
    group by company_id
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


def company_cells_hash(cur, ids: list[int], timeout_s: int = 15) -> dict[int, str]:
    """The hash the Verifier records on an all_cells draw (and promote compares with)."""
    return {
        int(cid): h
        for cid, h in _rows(
            cur, CELLS_HASH_SQL, {"ids": ids, "floor": HISTORY_FLOOR}, timeout_s
        )
    }


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
        for cid, dp, grain, end, verdict, value, at, draw, kind, h in _rows(
            cur, CHECKS_SQL, p, timeout_s
        ):
            if cid not in ev:
                continue
            ev[cid].checks.append((dp, grain, end, verdict, value, at, draw, kind, h))
            if verdict in ("wrong", "blank_wrong"):
                ev[cid].open_wrong += 1
    for cid, cells, accounted, reasoned in _rows(
        cur, TEMPLATE_COVERAGE_SQL, p, timeout_s
    ):
        if cid in ev:
            ev[cid].template_cells = int(cells)
            ev[cid].template_accounted = int(accounted)
            ev[cid].template_reasoned = int(reasoned)
    for cid, h in company_cells_hash(
        cur, [c for c in ids if c in ev], timeout_s
    ).items():
        ev[cid].cells_hash = h
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
                    "analytics.verifier_check does not exist: apply migration 0124 first"
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
