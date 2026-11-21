"""Writer for analytics.cell_display_state (migration 0130, founder approval 2026-11-17).

Input: the coverage export's rows (display and hide_class already set by top100_coverage.apply_display) plus the cells
the resolver puts OUT of a company's template. Output: one table row per (company, data point, period end, grain).
Dry run by default; --write-display-state on the coverage script writes. One transaction per company, a scoped
delete-then-insert by company_id (other companies are untouched), executemany in batches of at most BATCH rows."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.mapper import resolver_files as rf
from scrooner_pipeline.mapper import top100_coverage as t100

OUT = "OUT"
BATCH = 5000
COLUMNS = (
    "company_id",
    "data_point",
    "period_end",
    "grain",
    "display",
    "hide_class",
    "evidence_accession",
    "evidence",
    "r_page",
    "resolver_version",
    "run_id",
)
# One-display-path plan 2026-11-22 step 2: a shown cell also carries its badge (metrics/registry.badge_for of the
# resolver step), its value and the canonical_fact row it shows. state_rows appends these after COLUMNS; the table gets
# them with migration 0135 (proposed, not claimed or applied). Until then the writer inserts COLUMNS only.
BADGE_COLUMNS = ("badge", "value", "canonical_fact_id")
# Flip to True in the same change that applies 0135 (and only together with the shown_cell switch: 0135's CHECK
# requires a badge on every SHOWN_VALUE cell, so a shown cell without one must first be OPEN work).
WRITE_BADGE_COLUMNS = False
HIDDEN = (t100.HIDDEN_ROW, t100.HIDDEN_YEAR)
# the hide classes apply_display can assign (HIDE_ELIGIBLE's values plus HC_VERIFIED_ABSENT, which apply_display
# assigns directly for VERIFIED_ABSENT_HIDE data points); the table's CHECK holds the same set
HIDE_CLASSES = frozenset(
    {
        t100.HC_STRUCTURAL,
        t100.HC_COMBINED,
        t100.HC_PRE_FILING,
        t100.HC_VERIFIED_ABSENT,
        t100.HC_AFTER_TAX,
    }
)


def insert_sql(columns: tuple[str, ...] = COLUMNS) -> str:
    return (
        f"insert into analytics.cell_display_state ({', '.join(columns)}) "
        f"values ({', '.join(['%s'] * len(columns))})"
    )


INSERT_SQL = insert_sql()


def resolver_version(resolver_dir: Path = t100.RESOLVER_DIR) -> str | None:
    """resolver_version of the resolver output's first data row (per-company directory, else the newest single file),
    or None when there is no file."""
    return rf.resolver_version(resolver_dir)


def grain_of(data_point: str) -> str:
    return "I" if data_point in t100.INSTANT_DPS else "FY"


def _evidence_accession(r: dict[str, Any], disp: str) -> str | None:
    if disp in HIDDEN:
        return (
            r.get("_oc_accession")
            or r.get("_first_presenting")
            or r.get("accession")
            or None
        )
    return r.get("accession") or None


def _shown_fields(r: dict[str, Any], disp: str) -> tuple:
    if disp != t100.SHOWN_VALUE:
        return (None, None, None)
    sv = r.get("shown_value")
    return (
        r.get("_badge") or None,
        Decimal(str(sv)) if sv not in (None, "") else None,
        r.get("_canonical_fact_id"),
    )


def state_rows(
    rows: Iterable[dict[str, Any]],
    out_rows: Iterable[dict[str, Any]],
    run_id: str,
    version: str | None,
) -> list[tuple]:
    """Table rows (tuples in COLUMNS + BADGE_COLUMNS order). A cell present twice for one key keeps the last (the key is
    the PK). hide_class is set exactly for hidden cells; a hidden cell whose class is outside HIDE_ELIGIBLE raises.
    badge, value and canonical_fact_id are set only on a SHOWN_VALUE cell (badge None when attach_badges could not
    name one step: recorded, not enforced, until the shown_cell switch)."""
    eligible = HIDE_CLASSES
    out: dict[tuple, tuple] = {}
    pairs = [(r, r["display"]) for r in rows] + [(r, OUT) for r in out_rows]
    for r, disp in pairs:
        hc = (r.get("hide_class") or None) if disp in HIDDEN else None
        if disp in HIDDEN and hc not in eligible:
            raise ValueError(
                f"hidden cell without an eligible hide class: {r['ticker']} {r['data_point']} {r['period_end']} {hc!r}"
            )
        key = (
            r["company_id"],
            r["data_point"],
            r["period_end"],
            grain_of(r["data_point"]),
        )
        evidence = (
            ""
            if disp in (t100.SHOWN_VALUE, OUT)
            else (r.get("evidence") or r.get("reason") or "")
        )
        out[key] = (
            *key,
            disp,
            hc,
            None if disp == OUT else _evidence_accession(r, disp),
            evidence or None,
            None if disp == OUT else (r.get("r_page") or None),
            version,
            run_id,
            *_shown_fields(r, disp),
        )
    return list(out.values())


def write_display_state(
    conn: Any, table_rows: list[tuple], with_badges: bool | None = None
) -> dict[int, int]:
    """Scoped delete-then-insert, one transaction per company. Returns {company_id: rows written}. The caller passes a
    connection that is not read-only. Writes COLUMNS, plus BADGE_COLUMNS when with_badges (default
    WRITE_BADGE_COLUMNS; the table has them only after migration 0135)."""
    cols = COLUMNS + (
        BADGE_COLUMNS
        if (WRITE_BADGE_COLUMNS if with_badges is None else with_badges)
        else ()
    )
    sql = insert_sql(cols)
    table_rows = [t[: len(cols)] for t in table_rows]
    by_company: dict[int, list[tuple]] = {}
    for t in table_rows:
        by_company.setdefault(t[0], []).append(t)
    written: dict[int, int] = {}
    for cid, rs in sorted(by_company.items()):
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(
                "delete from analytics.cell_display_state where company_id = %s",
                (cid,),
            )
            for i in range(0, len(rs), BATCH):
                cur.executemany(sql, rs[i : i + BATCH])
        written[cid] = len(rs)
    return written


# ---- Migration 0135 DRAFT (one-display-path plan 2026-11-22, section 4 and step 3) ----------------------------------
# PROPOSED, NOT CLAIMED in doc 53 and NOT a migration file: 0135 needs the founder's typed words and waits for 0133.
# The SQL is rendered here so the badge CHECK can never drift from metrics/registry.BADGE_KINDS: the 0135 author writes
# `python -c "from scrooner_pipeline.mapper.cell_display_state import proposed_0135_sql; print(proposed_0135_sql())"`
# into pipeline/db/pending/0135_shown_cell_badges.sql, and tests/unit/test_shown_cell_migration_draft.py then holds
# that file's CHECK equal to BADGE_KINDS. The iff CHECK is NOT VALID: rows written before 0135 have no badge until the
# next export rewrites the company.
BADGE_CHECK_NAME = "cell_display_state_badge_kind_check"
# a NOT_PRESENTED proof counts as a zero input only on a row hidden because the line is evidenced absent (never a
# pre-filing year and never a combined line: those are not zeros)
ZERO_HIDE_CLASSES = (t100.HC_STRUCTURAL, t100.HC_VERIFIED_ABSENT)


def badge_check_sql() -> str:
    """CHECK body for cell_display_state.badge rendered from BADGE_KINDS: a plain kind exactly, a `kind:` with text."""
    from scrooner_pipeline.metrics.registry import BADGE_KINDS

    plain = ", ".join(f"'{k}'" for k in BADGE_KINDS if not k.endswith(":"))
    kinds = "|".join(k[:-1] for k in BADGE_KINDS if k.endswith(":"))
    return f"badge is null or badge in ({plain}) or badge ~ '^({kinds}):.*[^[:space:]]'"


def badge_kinds_in_check(sql: str) -> tuple[str, ...] | None:
    """The badge kinds a migration's cell_display_state badge CHECK admits, in BADGE_KINDS form (plain kinds, then
    `kind:` prefixes), or None when the SQL has no such CHECK. The drift test parses every migration with this."""
    import re

    m = re.search(
        rf"{BADGE_CHECK_NAME}\s+check\s*\(\s*badge is null or badge in \(([^)]*)\) or badge ~ '\^\(([^)]*)\):",
        sql,
    )
    if not m:
        return None
    plain = tuple(re.findall(r"'([^']+)'", m.group(1)))
    return plain + tuple(f"{k}:" for k in m.group(2).split("|"))


SHOWN_CELL_VIEW_SQL = f"""create or replace view analytics.shown_cell as
with latest_proof as (
    select distinct on (company_id, data_point_name, period_grain, period_start, period_end)
           id as proof_id, company_id, data_point_name, period_grain, period_start, period_end, verdict, shown_value
    from analytics.cell_proof
    where basis = 'latest'
    order by company_id, data_point_name, period_grain, period_start, period_end, proved_at desc, id desc
)
select d.company_id, d.data_point, d.period_end, d.grain, 'value'::text as cell_state,
       f.canonical_concept_id, c.name as concept_name, f.period_id, p.start_date, p.fiscal_period, p.period_type,
       f.value, f.source_fact_ids, d.badge, d.evidence_accession, d.r_page, lp.proof_id, lp.verdict
from analytics.cell_display_state d
join analytics.canonical_fact f
  on f.id = d.canonical_fact_id and f.company_id = d.company_id and f.value = d.value
join analytics.canonical_concept c on c.id = f.canonical_concept_id
join core.period p on p.id = f.period_id
join latest_proof lp
  on lp.company_id = d.company_id and lp.data_point_name = c.name and lp.period_grain = d.grain
 and lp.period_start = p.start_date and lp.period_end = p.end_date
where d.display = 'SHOWN_VALUE' and lp.verdict = 'PROVEN' and lp.shown_value = f.value
union all
select d.company_id, d.data_point, d.period_end, d.grain, 'not_presented'::text as cell_state,
       c.id, c.name, p.id, p.start_date, p.fiscal_period, p.period_type,
       null::numeric, '{{}}'::bigint[], null::text, d.evidence_accession, d.r_page, lp.proof_id, lp.verdict
from analytics.cell_display_state d
join analytics.canonical_concept c on c.name = d.data_point
join latest_proof lp
  on lp.company_id = d.company_id and lp.data_point_name = d.data_point and lp.period_grain = d.grain
 and lp.period_end = d.period_end
join core.period p
  on p.company_id = d.company_id and p.start_date = lp.period_start and p.end_date = lp.period_end
 and p.period_type = case d.grain when 'I' then 'instant' else 'duration' end
where d.display = 'HIDDEN_ROW' and d.hide_class in ({", ".join(f"'{h}'" for h in ZERO_HIDE_CLASSES)})
  and lp.verdict = 'NOT_PRESENTED'"""


def proposed_0135_sql() -> str:
    """The full proposed 0135 (plan section 4): badge/value/canonical_fact_id on cell_display_state with their CHECKs,
    metric_value.badge, and the analytics.shown_cell view. Rollback: drop view analytics.shown_cell; drop the four
    columns."""
    return f"""-- 0135_shown_cell_badges (PROPOSED; rendered by cell_display_state.proposed_0135_sql(); depends on 0130 and 0133)
-- ROLLBACK: drop view analytics.shown_cell; alter table analytics.metric_value drop column badge;
--           alter table analytics.cell_display_state drop column badge, drop column value, drop column canonical_fact_id;
alter table analytics.cell_display_state
    add column if not exists badge text,
    add column if not exists value numeric,
    add column if not exists canonical_fact_id bigint;
alter table analytics.cell_display_state add constraint {BADGE_CHECK_NAME}
    check ({badge_check_sql()});
alter table analytics.cell_display_state add constraint cell_display_state_badge_iff_shown
    check ((badge is not null) = (display = 'SHOWN_VALUE')) not valid;
alter table analytics.cell_display_state add constraint cell_display_state_value_only_shown
    check (display = 'SHOWN_VALUE' or (value is null and canonical_fact_id is null));
alter table analytics.metric_value add column if not exists badge text;
{SHOWN_CELL_VIEW_SQL};
"""
