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
from scrooner_pipeline.common.fsn_dates import fsn_end_matches
from scrooner_pipeline.mapper import company_tag_map as ctm
from scrooner_pipeline.mapper import dqc_checks as dqc
from scrooner_pipeline.mapper import resolve as resolve_mod

BEFORE_TABLES = ("canonical_fact", "cell_blank_reason", "slot_protected_cell")
DATA_WINDOW_START = date(2015, 1, 1)  # invariant I11
CONCEPT_ALIASES = {
    "revenue": ["revenue_sanity_resolved"],
    "revenue_sanity": ["revenue_sanity_resolved"],
}


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


def expected_cells_from_fy_check(
    path: Path, company_ids: list[int]
) -> dict[int, list[tuple[str, date, str]]]:
    """fy_check_*.csv (company_id, ticker, data_point, fy, period, status): the tag library's expected keys, the
    same ones its coverage check uses (in-template concept x FY0/FY-1 period end, with the library's status)."""
    import csv

    wanted = set(company_ids)
    out: dict[int, list[tuple[str, date, str]]] = defaultdict(list)
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            if int(r["company_id"]) in wanted:
                out[int(r["company_id"])].append(
                    (r["data_point"], date.fromisoformat(r["period"]), r["status"])
                )
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
            if (
                b.get("canonical_concept_id") is not None
                and b.get("period_id") is not None
            ):
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


LIBRARY_STATUS_RULE_ID = "tagmap.library_status@1"


def classify_status(status: str) -> tuple[str, str | None, str | None, str, str]:
    """The tag library's status of an expected cell that carries no value -> (state, defect_class, owner,
    reason_code, reason). Statements of fact, not guesses: held points are DEFECTS pending a definition; points off
    the statements, combined lines and verified template-OUT points are not in this company's template; points not
    printed on the face are not_presented. An unknown status is an open defect, never silently a reason."""
    st = status.strip()
    low = st.lower()
    if low.startswith("held"):
        code = "held_" + (
            st.split()[1].lower() if len(st.split()) > 1 else "definition"
        )
        owner = next(
            (o for pre, o in ctm.HELD_OWNERS if code.startswith(pre)),
            "standardization_lead",
        )
        return ("defect", "guard_hidden", owner, code, f"held by the library: {st}")
    if low.startswith(("read: held", "read: dps_quarterly_only_pending_definition")):
        return (
            "defect",
            "guard_hidden",
            "standardization_lead",
            "held_read",
            f"held by a full 10-K read: {st}",
        )
    if low.startswith("read-verified fail"):
        return (
            "defect",
            "evidence_pending",
            "verifier",
            "read_verified_fail",
            f"the Verifier read failed: {st}",
        )
    if low.startswith(("cover page", "tax note")):
        return (
            "not_in_template",
            None,
            None,
            "off_statement",
            f"off the statements: {st}",
        )
    if low.startswith(("combined", "read: combined")):
        return (
            "not_in_template",
            None,
            None,
            "combined_line",
            f"shown as the company's combined line ({st})",
        )
    if low.startswith("template seed: should be cond"):
        return (
            "not_in_template",
            None,
            None,
            "conditional_point",
            "conditional point, not in this company's template",
        )
    if "template-out" in low:
        return (
            "not_in_template",
            None,
            None,
            "template_out_verified",
            f"read-verified not in the template: {st}",
        )
    if "note-sourced" in low:
        return (
            "not_presented",
            None,
            None,
            "note_sourced_verified",
            f"not printed on the statement face; read-verified: {st}",
        )
    if low.startswith(("read: not_presented", "open:")):
        return ("not_presented", None, None, "not_printed", st)
    if low.startswith("excluded with point reason"):
        return ("not_presented", None, None, "point_reason", st)
    if low.startswith("read: "):
        return ("not_presented", None, None, "read_status", f"full 10-K read: {st[6:]}")
    return (
        "defect",
        "evidence_pending",
        "tag_mapper",
        "unknown_library_status",
        f"unmapped library status: {st}",
    )


def library_status_blanks(
    conn, cid: int, expected, stats: dict, concept_info
) -> list[dict]:
    """Every expected cell with no value whose library status is not 'served' becomes a written reason row (so each
    expected cell is valued or carries a reason). A value wins; a reason the mapper already wrote is kept."""
    names = {n: i for i, (n, _) in concept_info.items()}
    with conn.cursor() as cur:
        cur.execute(
            "select end_date, period_type, start_date, id from core.period where company_id = %s",
            (cid,),
        )
        periods = cur.fetchall()
        cur.execute(
            "select canonical_concept_id, period_id from analytics.canonical_fact where company_id = %s",
            (cid,),
        )
        valued = set(cur.fetchall())
    have = {(b["concept_name"], b["grain"], b["period_end"]) for b in stats["blanks"]}
    out: list[dict] = []
    for dp, period, status in expected:
        if status == "served":
            continue
        cands = [n for n in _candidates(dp) if n in names]
        name = cands[0] if cands else dp
        stmt = concept_info[names[cands[0]]][1] if cands else None
        want = "I" if stmt == "balance_sheet" else "FY"
        found = [
            (pid, start, end)
            for end, ptype, start, pid in periods
            if fsn_end_matches(period, end)
            and ("I" if ptype == "instant" else _grain(start, end, ptype)) == want
        ]
        if cands and any(
            (names[n], pid) in valued for n in cands for pid, _, _ in found
        ):
            continue
        pid, start, end = (
            found[0]
            if found
            else (
                None,
                period if want == "I" else period.replace(year=period.year - 1),
                period,
            )
        )
        if not found and want == "FY":
            from datetime import timedelta

            start = period - timedelta(days=364)
        if any((n, want, e) in have for n in (cands or [dp]) for e in {end, period}):
            continue
        state, dclass, owner, code, reason = classify_status(status)
        out.append(
            {
                "canonical_concept_id": names.get(name),
                "concept_name": name,
                "period_id": pid,
                "state": state,
                "defect_class": dclass,
                "owner": owner,
                "reason_code": code,
                "reason": reason,
                "rule_id": LIBRARY_STATUS_RULE_ID,
                "period_start": start,
                "period_end": end,
                "grain": want,
            }
        )
        have.add((name, want, end))
    return out


def hold_dqc_cells(
    conn: psycopg.Connection,
    cid: int,
    run_id: str,
    hits: list[dqc.Hit],
    stats: dict,
    concept_info,
) -> int:
    """DQC hold (explicit flag only): every served cell named by a HOLD hit is removed from canonical_fact and
    written as a visible defect reason (identity, owner verifier) of this run. A value is never derived."""
    by_cell: dict[tuple[int, int], list[dqc.Hit]] = defaultdict(list)
    for h in hits:
        if h.hold:
            by_cell[(h.canonical_concept_id, h.period_id)].append(h)
    if not by_cell:
        return 0
    blanks: list[dict] = []
    for (concept_id, period_id), hs in by_cell.items():
        h = hs[0]
        conn.execute(
            "delete from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s and period_id = %s",
            (cid, concept_id, period_id),
        )
        blanks.append(
            {
                "canonical_concept_id": concept_id,
                "concept_name": h.data_point,
                "period_id": period_id,
                "state": "defect",
                "defect_class": "identity",
                "owner": "verifier",
                "reason_code": "dqc_" + h.check_id.lower().replace("-", "_"),
                "reason": "held by DQC check "
                + "; ".join(
                    sorted(
                        {
                            f"{x.check_id} {x.values.get('identity', '')}".strip()
                            for x in hs
                        }
                    )
                ),
                "rule_id": dqc.RULE_ID,
                "period_start": h.period_start,
                "period_end": h.period_end,
                "grain": ctm._proof_grain(h.period_start, h.period_end, h.period_type),
            }
        )
    held = set(by_cell)
    stats["cells"] = [
        c
        for c in stats["cells"]
        if (c["canonical_concept_id"], c["period_id"]) not in held
    ]
    stats["blanks"] = stats["blanks"] + blanks
    ctm._write_blanks(conn, cid, run_id, blanks, concept_info)
    return len(blanks)


def _report(
    conn,
    cid: int,
    run_id: str,
    stats: dict,
    expected: list[tuple[str, date, str]],
    concept_info,
) -> dict[str, Any]:
    """Expected cells = the tag library's FY check: every in-template statement concept at the company's last two
    10-K period ends (FY0, FY-1). A key is VALUED (canonical_fact), a written REASONED BLANK (cell_blank_reason of
    this run), covered by a LIBRARY STATUS that is not materialized as a row yet (held, off-statement, read-verified
    ...), or NEITHER (status 'served' expected, but no value and no reason: must be 0)."""
    names = {n: i for i, (n, _) in concept_info.items()}
    with conn.cursor() as cur:
        cur.execute(
            "select end_date, period_type, start_date, id from core.period where company_id = %s",
            (cid,),
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
    blank_list = [(n, g, e) for n, g, e, _, _ in blank_rows]
    reasons = Counter(f"{state}:{code}" for _, _, _, state, code in blank_rows)
    valued_n = blank_n = 0
    library_status: Counter = Counter()
    neither: list[tuple[str, str]] = []
    for dp, period, status in expected:
        cands = [n for n in _candidates(dp) if n in names]
        stmt = concept_info[names[cands[0]]][1] if cands else None
        want = (
            "I" if stmt == "balance_sheet" else "FY"
        )  # an instant at the period end, a full-year duration
        # the library snaps 52/53-week fiscal year ends to month ends: match within 10 days
        pids = [
            (pid, g, end)
            for end, ptype, start, pid in periods
            if fsn_end_matches(period, end)
            and (g := "I" if ptype == "instant" else _grain(start, end, ptype)) == want
        ]
        if cands and any(
            (names[n], pid) in valued for n in cands for pid, _, _ in pids
        ):
            valued_n += 1
        elif any(
            n in (cands or [dp]) and g == want and fsn_end_matches(period, e)
            for n, g, e in blank_list
        ):
            blank_n += 1
        elif status != "served":
            library_status[status.split(" (")[0]] += 1
        else:
            neither.append((dp, period.isoformat()))
    return {
        "template_cells": len(expected),
        "valued": valued_n,
        "reasoned_blank": blank_n,
        "blank_reasons": dict(reasons),
        "library_status_only": sum(
            library_status.values()
        ),  # expected cells whose status is not written (must be 0)
        "library_status_by_kind": dict(library_status.most_common(8)),
        "neither": len(neither),
        "neither_cells": neither,
        "neither_by_data_point": dict(Counter(d for d, _ in neither).most_common(15)),
        "combined_lines": len(stats["combined_lines"]),
        "holds": dict(Counter(h["reason"] for h in stats["held"])),
        "conflict_cells": stats["conflict_cells"],
        "written_rows": stats["resolved"],
    }


def _fy_valued(expected, valued: set, periods, names: dict[str, int]) -> int:
    """How many 'served' FY0/FY-1 template cells hold a value in `valued` ((concept_id, period_id) keys)."""
    n = 0
    for dp, period, status in expected:
        if status != "served":
            continue
        ids = [names[c] for c in _candidates(dp) if c in names]
        pids = [pid for end, _, _, pid in periods if fsn_end_matches(period, end)]
        n += any((i, p) in valued for i in ids for p in pids)
    return n


def era_shortfall(map_rows, period_ends: list[date]) -> dict[int, date]:
    """Concept id -> the first company period end in the data window (I11, from 2015-01-01) that no era of the
    MERGED map (library and docmap rows, value or reason) covers; concepts fully covered are absent. Eras are
    (concept_id, era_from, era_to); a gap between two eras counts. Pure."""
    eras: dict[int, list[tuple[date, date]]] = defaultdict(list)
    for concept_id, era_from, era_to in map_rows:
        if concept_id is not None:
            eras[concept_id].append((era_from, era_to or date.max))
    out: dict[int, date] = {}
    window = sorted(e for e in period_ends if e >= DATA_WINDOW_START)
    for c, spans in eras.items():
        miss = next(
            (e for e in window if not any(lo <= e <= hi for lo, hi in spans)), None
        )
        if miss is not None:
            out[c] = miss
    return out


def coverage_gate_ok(cov: dict) -> bool:
    """Apply a company only when its map covers the data window for every data point, it loses no FY0/FY-1 template
    value, and no value disappears without a reason (Dhairya 2026-11-12, invariant I11)."""
    return (
        not cov["era_short"]
        and cov["fy01_after"] >= cov["fy01_before"]
        and cov["values_lost"] == 0
    )


def coverage(
    conn, cid: int, run_id: str, before: set, expected, concept_info, scope: set[int]
) -> dict[str, Any]:
    """Before -> after for one company inside its plan transaction: eras covered, values in the data window that
    disappear (lost: no reason row; held: a reasoned blank of this run), FY0/FY-1 template cells valued."""
    names = {n: i for i, (n, _) in concept_info.items()}
    with conn.cursor() as cur:
        cur.execute(
            "select end_date, period_type, start_date, id from core.period where company_id = %s",
            (cid,),
        )
        periods = cur.fetchall()
        cur.execute(
            "select canonical_concept_id, period_id from analytics.canonical_fact where company_id = %s",
            (cid,),
        )
        after = set(cur.fetchall())
        cur.execute(
            "select data_point_name, period_end from analytics.cell_blank_reason where company_id = %s and run_id = %s::uuid",
            (cid, run_id),
        )
        reasoned = set(cur.fetchall())
        cur.execute(
            "select coalesce(canonical_concept_id, parent_concept_id), era_from, era_to from analytics.company_tag_map where company_id = %s",
            (cid,),
        )
        map_rows = cur.fetchall()
    end_of = {pid: end for end, _, _, pid in periods}
    gone = [
        (c, p)
        for c, p in before - after
        if c in scope and end_of.get(p, date.min) >= DATA_WINDOW_START
    ]
    held = sum(
        (concept_info[c][0], end_of[p]) in reasoned
        for c, p in gone
        if c in concept_info
    )
    short = era_shortfall(map_rows, [e for e, _, _, _ in periods])
    return {
        "era_from_min": min((e for _, e, _ in map_rows), default=None),
        "era_short": {
            concept_info[c][0]: s.isoformat()
            for c, s in short.items()
            if c in concept_info
        },
        "values_lost": len(gone) - held,
        "values_held_with_reason": held,
        "fy01_before": _fy_valued(expected, before, periods, names),
        "fy01_after": _fy_valued(expected, after, periods, names),
        "fy01_expected": sum(1 for *_, st in expected if st == "served"),
    }


class _Retry(Exception):
    """The first attempt of a company (concept gate scope) found concepts that would lose a value: redo without them."""

    def __init__(self, concepts: set[int]):
        self.concepts = concepts


def concepts_to_skip(
    conn: psycopg.Connection, cid: int, managed: set[int]
) -> tuple[set[int], dict[int, str]]:
    """Per-concept coverage gate, before anything is written: the concepts whose merged-map eras do not cover the
    data window, and the managed concepts the map does not cover at all (resolve would delete their served values).
    -> (concept ids to leave as served today, concept id -> why)."""
    with conn.cursor() as cur:
        cur.execute(
            "select coalesce(canonical_concept_id, parent_concept_id), era_from, era_to "
            "from analytics.company_tag_map where company_id = %s",
            (cid,),
        )
        map_rows = cur.fetchall()
        cur.execute("select end_date from core.period where company_id = %s", (cid,))
        ends = [e for (e,) in cur.fetchall()]
    short = era_shortfall(map_rows, ends)
    why = {c: f"era short from {d.isoformat()}" for c, d in short.items()}
    mapped = {c for c, _, _ in map_rows if c is not None}
    for c in managed - mapped:
        why.setdefault(c, "no map row")
    return set(why), why


def run(
    conn: psycopg.Connection,
    company_ids: list[int],
    expected: dict[int, list[tuple[str, date, str]]],
    *,
    apply: bool,
    gate: bool = False,
    gate_scope: str = "company",
    dqc_checks: list[dqc.Check] | None = None,
    dqc_hold: bool = False,
) -> dict[int, dict]:
    """gate_scope 'company' (default): with gate and apply, a company is committed only when all its concepts pass the
    coverage gate. 'concept': each concept whose merged-map eras cover the data window is rewritten; a concept that
    does not (or the map does not cover at all, or that would lose a value) is left exactly as served today, no
    cell touched, and listed in coverage['skipped_concepts']."""
    managed = resolve_mod._load_managed_concept_ids(conn)
    concept_info = ctm.load_concept_info(conn)
    conn.commit()
    out: dict[int, dict] = {}
    by_concept = gate and gate_scope == "concept"
    for cid in company_ids:
        forced: set[int] = set()
        for _attempt in (0, 1):
            try:
                with conn.transaction():
                    _company(
                        conn,
                        out,
                        cid,
                        expected.get(cid, []),
                        managed,
                        concept_info,
                        apply=apply,
                        gate=gate,
                        by_concept=by_concept,
                        forced=forced,
                        dqc_checks=dqc_checks,
                        dqc_hold=dqc_hold,
                    )
                break
            except _Retry as retry:
                forced |= retry.concepts
            except _PlanRollback:
                break
            except Exception as exc:  # one company failing never hides the others; its transaction is rolled back
                out[cid] = {"error": f"{type(exc).__name__}: {str(exc)[:300]}"}
                break
    return out


def _company(
    conn: psycopg.Connection,
    out: dict[int, dict],
    cid: int,
    expected: list[tuple[str, date, str]],
    managed,
    concept_info,
    *,
    apply: bool,
    gate: bool,
    by_concept: bool,
    forced: set[int],
    dqc_checks: list[dqc.Check] | None = None,
    dqc_hold: bool = False,
) -> None:
    # first statement of the transaction: one snapshot, a concurrent re-seed cannot split it
    conn.execute("set transaction isolation level repeatable read")
    cik = conn.execute("select cik from core.company where id = %s", (cid,)).fetchone()[
        0
    ]
    before = set(
        conn.execute(
            "select canonical_concept_id, period_id from analytics.canonical_fact where company_id = %s",
            (cid,),
        ).fetchall()
    )
    skip: set[int] = set(forced)
    why: dict[int, str] = {c: "would lose a value" for c in forced}
    if by_concept:
        more, w = concepts_to_skip(conn, cid, set(managed))
        skip |= more
        why = {**w, **why}
    run_managed = set(managed) - skip
    conn.execute("set local scrooner.writer = 'company_tag_map'")
    conn.execute("set local scrooner.slot_writer = 'on'")
    run_id = cs.start_rule_run(
        conn, ctm.RULE_ID, "apply" if apply else "dry_run", "on", [cik]
    )
    stats = ctm.resolve_for_company(
        conn,
        cid,
        run_managed,
        concept_info,
        run_id,
        commit=False,
        skip_concept_ids=skip,
    )
    lib = [
        b
        for b in library_status_blanks(conn, cid, expected, stats, concept_info)
        if b.get("canonical_concept_id") not in skip
    ]
    ctm._write_blanks(conn, cid, run_id, lib, concept_info)
    stats["blanks"] = stats["blanks"] + lib
    dqc_hits: list[dqc.Hit] = []
    dqc_held = 0
    if (
        dqc_checks
    ):  # report-only unless dqc_hold: then HOLD hits remove their served cells
        dqc_hits = dqc.check_company(conn, cid, dqc_checks)
        if dqc_hold:
            dqc_held = hold_dqc_cells(conn, cid, run_id, dqc_hits, stats, concept_info)
    scope = sorted(
        run_managed
        | {c["canonical_concept_id"] for c in stats["cells"]}
        | {
            b["canonical_concept_id"]
            for b in stats["blanks"]
            if b.get("canonical_concept_id")
        }
    )
    protected = protect(conn, cid, scope, stats["cells"], stats["blanks"], run_id)
    if apply:
        conn.execute(
            "insert into analytics.company_value_owner (company_id, owner, note) values (%s, 'company_tag_map', 'tag-map write path') "
            "on conflict (company_id) do update set owner = 'company_tag_map'",
            (cid,),
        )
    rep = _report(conn, cid, run_id, stats, expected, concept_info)
    out[cid] = rep
    rep["protected_keys"] = protected
    rep["dqc_hits"] = dqc_hits
    rep["dqc_held"] = dqc_held
    rep["coverage"] = coverage(
        conn, cid, run_id, before, expected, concept_info, set(run_managed)
    )
    if by_concept:
        # a rewritten concept that would still lose a value (no reason row) is dropped from the rewrite and redone
        after_cells = set(
            conn.execute(
                "select canonical_concept_id, period_id from analytics.canonical_fact where company_id = %s",
                (cid,),
            ).fetchall()
        )
        reasoned = {
            (name, end)
            for name, end in conn.execute(
                "select data_point_name, period_end from analytics.cell_blank_reason where company_id = %s and run_id = %s::uuid",
                (cid, run_id),
            ).fetchall()
        }
        ends = dict(
            conn.execute(
                "select id, end_date from core.period where company_id = %s", (cid,)
            ).fetchall()
        )
        bad = {
            c
            for c, p in before - after_cells
            if c in run_managed
            and ends.get(p, date.min) >= DATA_WINDOW_START
            and (concept_info.get(c, ("",))[0], ends.get(p)) not in reasoned
        }
        if bad:
            raise _Retry(bad)
        rep["coverage"]["skipped_concepts"] = {
            concept_info[c][0]: w for c, w in sorted(why.items()) if c in concept_info
        }
        rep["coverage"]["rewritten_concepts"] = len(run_managed)
    if apply and gate and not by_concept and not coverage_gate_ok(rep["coverage"]):
        rep["gated"] = True  # rolled back: stays on its current serving
        raise _PlanRollback
    if apply:
        cs.finish_rule_run(
            conn,
            run_id,
            {
                k: v
                for k, v in rep.items()
                if k not in ("neither_by_data_point", "dqc_hits")
            },
        )
    else:
        raise _PlanRollback
