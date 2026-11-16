"""Writer for analytics.cell_display_state (migration 0130, founder approval 2026-11-17).

Input: the coverage export's rows (display and hide_class already set by top100_coverage.apply_display) plus the cells
the resolver puts OUT of a company's template. Output: one table row per (company, data point, period end, grain).
Dry run by default; --write-display-state on the coverage script writes. One transaction per company, a scoped
delete-then-insert by company_id (other companies are untouched), executemany in batches of at most BATCH rows."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

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
HIDDEN = (t100.HIDDEN_ROW, t100.HIDDEN_YEAR)
# the four hide classes apply_display can assign (HIDE_ELIGIBLE's values plus HC_VERIFIED_ABSENT, which apply_display
# assigns directly for VERIFIED_ABSENT_HIDE data points); the table's CHECK holds the same set
HIDE_CLASSES = frozenset(
    {
        t100.HC_STRUCTURAL,
        t100.HC_COMBINED,
        t100.HC_PRE_FILING,
        t100.HC_VERIFIED_ABSENT,
    }
)

INSERT_SQL = (
    f"insert into analytics.cell_display_state ({', '.join(COLUMNS)}) "
    f"values ({', '.join(['%s'] * len(COLUMNS))})"
)


def resolver_version(resolver_dir: Path = t100.RESOLVER_DIR) -> str | None:
    """resolver_version of the newest resolver-all110-*.csv (first data row), or None when there is no file."""
    files = sorted(resolver_dir.glob("resolver-all110-*.csv"))
    if not files:
        return None
    with files[-1].open(newline="") as fh:
        for r in csv.DictReader(fh):
            return (r.get("resolver_version") or "").strip() or None
    return None


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


def state_rows(
    rows: Iterable[dict[str, Any]],
    out_rows: Iterable[dict[str, Any]],
    run_id: str,
    version: str | None,
) -> list[tuple]:
    """Table rows (tuples in COLUMNS order). A cell present twice for one key keeps the last (the key is the PK).
    hide_class is set exactly for hidden cells; a hidden cell whose class is outside HIDE_ELIGIBLE raises."""
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
        )
    return list(out.values())


def write_display_state(conn: Any, table_rows: list[tuple]) -> dict[int, int]:
    """Scoped delete-then-insert, one transaction per company. Returns {company_id: rows written}. The caller passes a
    connection that is not read-only."""
    by_company: dict[int, list[tuple]] = {}
    for t in table_rows:
        by_company.setdefault(t[0], []).append(t)
    written: dict[int, int] = {}
    for cid, rs in sorted(by_company.items()):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "delete from analytics.cell_display_state where company_id = %s",
                    (cid,),
                )
                for i in range(0, len(rs), BATCH):
                    cur.executemany(INSERT_SQL, rs[i : i + BATCH])
        written[cid] = len(rs)
    return written
