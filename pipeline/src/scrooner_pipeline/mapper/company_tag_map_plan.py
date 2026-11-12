"""Plan / apply of the tag-map write path (rule company_tag_map.select@1) for a list of companies.

`scrooner-map tagmap-plan --company-ids ...` runs the tag-map resolve for each company inside ONE transaction and
ROLLS BACK (plan): it reports per company the template cells, valued cells, reasoned blanks (by reason), combined
lines served, conflicts/holds, and the template cells with NEITHER a value NOR a reason (must be 0 to pass).
`--apply` commits instead, after writing a before-image (pilot-prod CSV format, `scrooner-cells restore` reads it).

Per company transaction: session settings scrooner.writer = 'company_tag_map' (0123 lets it through the owner guard)
and scrooner.slot_writer = 'on' (the 0113 guard lets it replace protected cells); the cells are rebuilt by
mapper/company_tag_map.py; every written key is protected (analytics.slot_protected_cell, valued keys with their
value, reasoned blanks with value null) so the nightly cannot overwrite it; with --apply the company is registered in
analytics.company_value_owner (owner 'company_tag_map') so every other stage stays blocked.
"""

from __future__ import annotations

import gzip
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.mapper import company_tag_map as ctm
from scrooner_pipeline.mapper import resolve as resolve_mod

BEFORE_TABLES = ("canonical_fact", "cell_blank_reason", "slot_protected_cell")
DATA_WINDOW_START = date(2015, 1, 1)  # invariant I11
CONCEPT_ALIASES = {"revenue": ["revenue_sanity_resolved"]}


class _PlanRollback(Exception):
    pass


def write_before_image(
    conn: psycopg.Connection, company_ids: list[int], out_dir: Path
) -> dict[str, int]:
    """canonical_fact / cell_blank_reason / slot_protected_cell rows of these companies as csv.gz with header
    (what `scrooner-cells restore --before-image` reads)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ids = ",".join(str(int(i)) for i in company_ids)
    counts: dict[str, int] = {}
    for table in BEFORE_TABLES:
        n = 0
        with (
            gzip.open(out_dir / f"{table}.csv.gz", "wb") as fh,
            conn.cursor().copy(
                f"copy (select * from analytics.{table} where company_id in ({ids}) order by 1) to stdout with csv header"
            ) as cp,
        ):
            for chunk in cp:
                fh.write(bytes(chunk))
        with conn.cursor() as cur:
            cur.execute(
                f"select count(*) from analytics.{table} where company_id in ({ids})"
            )
            n = cur.fetchone()[0]
        counts[table] = n
    return counts


def template_points_from_csv(path: Path, company_ids: list[int]) -> dict[int, set[str]]:
    """template_points_*.csv (company_id, template, data_point): the library's per-company template data points."""
    import csv

    wanted = set(company_ids)
    out: dict[int, set[str]] = defaultdict(set)
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            if int(r["company_id"]) in wanted:
                out[int(r["company_id"])].add(r["data_point"])
    return out


def template_points(
    conn: psycopg.Connection, company_ids: list[int], templates: Path, cohort: Path
) -> dict[int, set[str]]:
    """In-template data points per company: the sector templates file plus company overrides (the same plan
    `seed-sector-templates` builds), so the plan does not depend on that table being seeded."""
    from scrooner_pipeline.mapper import sector_templates as st

    parsed = st.parse_templates(templates.read_text(encoding="utf-8"))
    companies = st.load_cohort(cohort)
    if not st.cohort_has_sic(cohort):
        companies = st.fill_sic_from_db(conn, companies)
    wanted = set(company_ids)
    rows = st.build_plan(parsed, [c for c in companies if c.company_id in wanted])
    out: dict[int, set[str]] = defaultdict(set)
    for r in rows:
        if r.in_template:
            out[r.company_id].add(r.data_point)
    return out


def _grain(start: date, end: date, ptype: str) -> str | None:
    return ctm._grain(start, end, ptype)


def _candidates(dp: str) -> list[str]:
    return [dp, dp + "_resolved", *CONCEPT_ALIASES.get(dp, [])]


def protect(
    conn: psycopg.Connection,
    cid: int,
    scope_ids: list[int],
    cells: list[dict],
    blanks: list[dict],
    run_id: str,
) -> int:
    """The written keys of this company are protected (0113): valued keys with their value, reasoned blanks
    with value null (0115). Rows of the scope that were protected before are replaced by exactly these."""
    nullable = (
        conn.execute(
            "select is_nullable from information_schema.columns where table_schema = 'analytics' "
            "and table_name = 'slot_protected_cell' and column_name = 'value'"
        ).fetchone()
        or ("NO",)
    )[0] == "YES"
    keys: dict[tuple[int, int], tuple[str, Any]] = {}
    if nullable:
        for b in blanks:
            if b.get("canonical_concept_id") is not None:
                keys[(b["canonical_concept_id"], b["period_id"])] = (
                    b["rule_id"] or ctm.RULE_ID,
                    None,
                )
    for c in cells:
        keys[(c["canonical_concept_id"], c["period_id"])] = (ctm.RULE_ID, c["value"])
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.slot_protected_cell where company_id = %s and canonical_concept_id = any(%s)",
            (cid, scope_ids),
        )
        if keys:
            cur.execute(
                """
                insert into analytics.slot_protected_cell
                    (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256)
                select %s, u.c, u.p, u.r, u.v, %s, %s
                from unnest(%s::bigint[], %s::bigint[], %s::text[], %s::numeric[]) as u(c, p, r, v)
                """,
                (
                    cid,
                    run_id,
                    f"company_tag_map:{run_id}",
                    [k[0] for k in keys],
                    [k[1] for k in keys],
                    [v[0] for v in keys.values()],
                    [v[1] for v in keys.values()],
                ),
            )
    return len(keys)


def _report(
    conn, cid: int, run_id: str, stats: dict, template: set[str], concept_info
) -> dict[str, Any]:
    names = {n: i for i, (n, _) in concept_info.items()}
    with conn.cursor() as cur:
        cur.execute(
            "select start_date, end_date, period_type, id from core.period where company_id = %s and end_date >= %s",
            (cid, DATA_WINDOW_START),
        )
        periods = cur.fetchall()
        cur.execute(
            "select canonical_concept_id, period_id from analytics.canonical_fact where company_id = %s",
            (cid,),
        )
        valued = set(cur.fetchall())
        cur.execute(
            "select data_point_name, period_grain, period_end, state, reason_code from analytics.cell_blank_reason where company_id = %s and run_id = %s::uuid",
            (cid, run_id),
        )
        blank_rows = cur.fetchall()
    blank_keys = {(n, g, e) for n, g, e, _, _ in blank_rows}
    reasons = Counter(f"{state}:{code}" for _, _, _, state, code in blank_rows)
    template_cells = valued_n = blank_n = 0
    neither: Counter = Counter()
    metric_points = []
    for dp in sorted(template):
        cands = [n for n in _candidates(dp) if n in names]
        if not cands:
            metric_points.append(dp)
            continue
        statement = concept_info[names[cands[0]]][1]
        for start, end, ptype, pid in periods:
            if (ptype == "instant") != (statement == "balance_sheet"):
                continue
            grain = _grain(start, end, ptype)
            if grain is None:
                continue
            template_cells += 1
            if any((names[n], pid) in valued for n in cands):
                valued_n += 1
            elif any((n, grain, end) in blank_keys for n in cands):
                blank_n += 1
            else:
                neither[dp] += 1
    return {
        "template_cells": template_cells,
        "valued": valued_n,
        "reasoned_blank": blank_n,
        "blank_reasons": dict(reasons),
        "neither": sum(neither.values()),
        "neither_by_data_point": dict(neither.most_common(15)),
        "combined_lines": len(stats["combined_lines"]),
        "holds": dict(Counter(h["reason"] for h in stats["held"])),
        "conflict_cells": stats["conflict_cells"],
        "metric_data_points_not_mapper_cells": len(metric_points),
        "written_rows": stats["resolved"],
    }


def run(
    conn: psycopg.Connection,
    company_ids: list[int],
    templates: dict[int, set[str]],
    *,
    apply: bool,
) -> dict[int, dict]:
    managed = resolve_mod._load_managed_concept_ids(conn)
    concept_info = ctm.load_concept_info(conn)
    conn.commit()
    out: dict[int, dict] = {}
    for cid in company_ids:
        try:
            with conn.transaction():
                cik = conn.execute(
                    "select cik from core.company where id = %s", (cid,)
                ).fetchone()[0]
                conn.execute("set local scrooner.writer = 'company_tag_map'")
                conn.execute("set local scrooner.slot_writer = 'on'")
                run_id = cs.start_rule_run(
                    conn, ctm.RULE_ID, "apply" if apply else "dry_run", "on", [cik]
                )
                stats = ctm.resolve_for_company(
                    conn, cid, managed, concept_info, run_id, commit=False
                )
                scope = sorted(
                    set(managed)
                    | {c["canonical_concept_id"] for c in stats["cells"]}
                    | {
                        b["canonical_concept_id"]
                        for b in stats["blanks"]
                        if b.get("canonical_concept_id")
                    }
                )
                protected = protect(
                    conn, cid, scope, stats["cells"], stats["blanks"], run_id
                )
                if apply:
                    conn.execute(
                        "insert into analytics.company_value_owner (company_id, owner, note) values (%s, 'company_tag_map', 'tag-map write path') "
                        "on conflict (company_id) do update set owner = 'company_tag_map'",
                        (cid,),
                    )
                rep = _report(
                    conn, cid, run_id, stats, templates.get(cid, set()), concept_info
                )
                rep["protected_keys"] = protected
                out[cid] = rep
                if apply:
                    cs.finish_rule_run(
                        conn,
                        run_id,
                        {k: v for k, v in rep.items() if k != "neither_by_data_point"},
                    )
                else:
                    raise _PlanRollback
        except _PlanRollback:
            pass
        except Exception as exc:  # one company failing never hides the others; its transaction is rolled back
            out[cid] = {"error": f"{type(exc).__name__}: {str(exc)[:300]}"}
    return out
