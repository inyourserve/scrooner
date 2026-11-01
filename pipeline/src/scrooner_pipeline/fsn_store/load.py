"""Load one company directory into schema fsn (design §2), one transaction per company.

Idempotency key: (company_id, input_sha256, loader_commit) in fsn.company_load;
a match skips the company. Inside the transaction: statement_timeout 5 min,
upsert fsn.tag / fsn.dim, delete the company's filings (cascade), COPY the
filings, reports, lines, values and arcs, upsert company_load. A half-written
company is impossible; rerunning the same command resumes.

Co-registrant filings: a filing row belongs to its registrant (sub.cik). A
company directory may carry filings whose registrant is another company
(Entergy Arkansas holds Entergy's combined 10-K): those are inserted only
when absent (ON CONFLICT accession DO NOTHING) and never deleted by the
co-registrant's reload; fsn.filing.aciks keeps the link.
"""

from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.cell_store import finish_rule_run, start_rule_run
from scrooner_pipeline.fsn_store.company_dir import NO_DIM, read

logger = structlog.get_logger()
RULE_ID = "fsn.store_load@1"
STATEMENT_TIMEOUT = "5min"


def _d8(s: str | None) -> date | None:
    if not s or len(s) < 8:
        return None
    try:
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except ValueError:
        return None


def _ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace(" ", "T"))
    except ValueError:
        return None


def _num(s: str | None) -> Decimal | None:
    if s in (None, ""):
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _int(s: str | None, default: int | None = None) -> int | None:
    try:
        return int(s) if s not in (None, "") else default
    except ValueError:
        return default


def _float(s: str | None) -> float | None:
    try:
        return float(s) if s not in (None, "") else None
    except ValueError:
        return None


def _weight(negative: str | None) -> int:
    """FSN cal.negative is the arc weight itself (+1 / -1), mind entry 2026-10-31; '1' alone means +1."""
    try:
        return -1 if float(negative or "1") < 0 else 1
    except ValueError:
        return 1


def _git_commit() -> str:
    return (
        subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        or "unknown"
    )


def already_loaded(
    conn: psycopg.Connection, company_id: int, input_sha256: str, loader_commit: str
) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "select 1 from fsn.company_load where company_id = %s and input_sha256 = %s and loader_commit = %s",
            (company_id, input_sha256, loader_commit),
        )
        return cur.fetchone() is not None


def _copy(
    cur: psycopg.Cursor, table: str, cols: tuple[str, ...], rows: list[tuple]
) -> int:
    if not rows:
        return 0
    with cur.copy(f"copy {table} ({', '.join(cols)}) from stdin") as cp:
        for r in rows:
            cp.write_row(r)
    return len(rows)


def load_company(
    conn: psycopg.Connection,
    company_dir: Path,
    *,
    loader_commit: str | None = None,
    run_id: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Load one companies/<cik>/ directory. Returns the row counts written (or {"skipped": True})."""
    loader_commit = loader_commit or _git_commit()
    data = read(company_dir)
    m = data["manifest"]
    cik = m["cik"]
    with conn.cursor() as cur:
        cur.execute("select id from core.company where cik = %s", (cik,))
        row = cur.fetchone()
    if row is None:
        raise LookupError(f"no core.company for cik {cik}")
    company_id = row[0]
    if not force and already_loaded(conn, company_id, m["input_sha256"], loader_commit):
        logger.info(
            "fsn_load.skip_already_loaded", cik=cik, input_sha256=m["input_sha256"][:16]
        )
        return {"cik": cik, "company_id": company_id, "skipped": True}
    counts: dict[str, int] = defaultdict(int)
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(f"set local statement_timeout = '{STATEMENT_TIMEOUT}'")
            # --- tags and dims (shared, upsert) ---
            tag_pairs = {(r["tag"], r["version"]) for r in data["tag"]}
            for t in ("pre", "num"):
                tag_pairs |= {(r["tag"], r["version"]) for r in data[t]}
            for r in data["cal"]:
                tag_pairs.add((r["ptag"], r["pversion"]))
                tag_pairs.add((r["ctag"], r["cversion"]))
            tag_meta = {(r["tag"], r["version"]): r for r in data["tag"]}
            cur.executemany(
                """
                insert into fsn.tag (tag, version, custom, abstract, datatype, iord, crdr, tlabel)
                values (%s, %s, %s, %s, %s, %s, %s, %s) on conflict (tag, version) do nothing
                """,
                [
                    (
                        t,
                        v,
                        (tag_meta.get((t, v)) or {}).get("custom") == "1",
                        (tag_meta.get((t, v)) or {}).get("abstract") == "1",
                        (tag_meta.get((t, v)) or {}).get("datatype") or None,
                        (tag_meta.get((t, v)) or {}).get("iord") or None,
                        (tag_meta.get((t, v)) or {}).get("crdr") or None,
                        (tag_meta.get((t, v)) or {}).get("tlabel") or None,
                    )
                    for t, v in sorted(tag_pairs)
                ],
            )
            cur.execute(
                "select id, tag, version from fsn.tag where (tag, version) in (select unnest(%s::text[]), unnest(%s::text[]))",
                ([t for t, _ in tag_pairs], [v for _, v in tag_pairs]),
            )
            tag_id = {(t, v): i for i, t, v in cur.fetchall()}
            dims = {r["dimhash"]: r for r in data["dim"]}
            cur.executemany(
                "insert into fsn.dim (dimh, segments, segt) values (%s, %s, %s) on conflict (dimh) do nothing",
                [
                    (h, r.get("segments") or None, r.get("segt") == "1")
                    for h, r in dims.items()
                    if h != NO_DIM
                ],
            )
            cur.execute(
                "select id, dimh from fsn.dim where dimh = any(%s)",
                (list(dims) + [NO_DIM],),
            )
            dim_id = {h: i for i, h in cur.fetchall()}
            # --- filings: delete this company's own, insert all (others only if absent) ---
            subs = {r["adsh"]: r for r in data["sub"]}
            cur.execute("delete from fsn.filing where company_id = %s", (company_id,))
            counts["filings_deleted"] = cur.rowcount
            cur.execute(
                "select cik, id from core.company where cik = any(%s)",
                (sorted({r["cik"].zfill(10) for r in subs.values()}),),
            )
            cid_of = dict(cur.fetchall())
            cur.executemany(
                """
                insert into fsn.filing (accession, company_id, cik, form, period, fy, fp, fye, filed, accepted,
                                        amendment, prevrpt, aciks, fsn_set, src_sha256)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                on conflict (accession) do nothing
                """,
                [
                    (
                        a,
                        cid_of.get(r["cik"].zfill(10)),
                        r["cik"].zfill(10),
                        r["form"],
                        _d8(r.get("period")),
                        _int(r.get("fy")),
                        r.get("fp") or None,
                        r.get("fye") or None,
                        _d8(r.get("filed")),
                        _ts(r.get("accepted")),
                        r["form"].endswith("/A"),
                        r.get("prevrpt") == "1",
                        [c.zfill(10) for c in (r.get("aciks") or "").split() if c],
                        r["fsn_set"],
                        m.get("file_sha256", {}).get("sub"),
                    )
                    for a, r in subs.items()
                ],
            )
            cur.execute(
                "select accession, id, company_id from fsn.filing where accession = any(%s)",
                (list(subs),),
            )
            filing_rows = cur.fetchall()
            filing_id = {a: i for a, i, _ in filing_rows}
            # rows of filings owned by another company that already existed are not re-inserted
            cur.execute(
                "select filing_id from fsn.line where filing_id = any(%s) limit 1",
                ([i for _, i, c in filing_rows if c != company_id],),
            )
            foreign_loaded = (
                {i for _, i, c in filing_rows if c != company_id}
                if cur.fetchone()
                else set()
            )
            own = {a for a, i, _ in filing_rows if i not in foreign_loaded}
            counts["filings"] = len(own)
            # --- reports ---
            counts["report"] = _copy(
                cur,
                "fsn.report",
                (
                    "filing_id",
                    "report",
                    "rfile",
                    "menucat",
                    "shortname",
                    "longname",
                    "roleuri",
                    "parentreport",
                    "ultparentrpt",
                ),
                [
                    (
                        filing_id[r["adsh"]],
                        _int(r["report"]),
                        r.get("rfile") or None,
                        r.get("menucat") or None,
                        r.get("shortname") or None,
                        r.get("longname") or None,
                        r.get("roleuri") or None,
                        _int(r.get("parentreport")),
                        _int(r.get("ultparentrpt")),
                    )
                    for r in data["ren"]
                    if r["adsh"] in own
                ],
            )
            # --- lines ---
            seen_lines: set[tuple] = set()
            line_rows = []
            for r in data["pre"]:
                if r["adsh"] not in own:
                    continue
                k = (filing_id[r["adsh"]], _int(r["report"]), _int(r["line"]))
                if k in seen_lines:
                    continue
                seen_lines.add(k)
                line_rows.append(
                    (
                        *k,
                        r["stmt"],
                        r.get("inpth") == "1",
                        tag_id[(r["tag"], r["version"])],
                        r.get("prole") or None,
                        r.get("plabel") or None,
                        r.get("negating") == "1",
                    )
                )
            counts["line"] = _copy(
                cur,
                "fsn.line",
                (
                    "filing_id",
                    "report",
                    "line",
                    "stmt",
                    "inpth",
                    "tag_id",
                    "prole",
                    "plabel",
                    "negating",
                ),
                line_rows,
            )
            # --- values ---
            seen_vals: set[tuple] = set()
            val_rows = []
            for r in data["num"]:
                if r["adsh"] not in own:
                    continue
                fid = filing_id[r["adsh"]]
                vk = (
                    fid,
                    tag_id[(r["tag"], r["version"])],
                    _d8(r["ddate"]),
                    _int(r["qtrs"], 0),
                    r["uom"],
                    dim_id.get(r["dimh"], dim_id[NO_DIM]),
                    _int(r.get("iprx"), 0),
                    r.get("coreg") or "",
                )
                if vk in seen_vals:
                    counts["num_duplicate_key"] += 1
                    continue
                seen_vals.add(vk)
                val_rows.append(
                    (
                        *vk,
                        cid_of.get(subs[r["adsh"]]["cik"].zfill(10)),
                        _num(r.get("value")),
                        r.get("footnote") or None,
                        _float(r.get("durp")),
                        _float(r.get("datp")),
                        _int(r.get("dcml")),
                    )
                )
            counts["value"] = _copy(
                cur,
                "fsn.value",
                (
                    "filing_id",
                    "tag_id",
                    "ddate",
                    "qtrs",
                    "uom",
                    "dim_id",
                    "iprx",
                    "coreg",
                    "company_id",
                    "value",
                    "footnote",
                    "durp",
                    "datp",
                    "dcml",
                ),
                val_rows,
            )
            # --- calc arcs ---
            seen_arcs: set[tuple] = set()
            arc_rows = []
            for r in data["cal"]:
                if r["adsh"] not in own:
                    continue
                k = (filing_id[r["adsh"]], _int(r["grp"]), _int(r["arc"]))
                if k in seen_arcs:
                    continue
                seen_arcs.add(k)
                arc_rows.append(
                    (
                        *k,
                        tag_id[(r["ptag"], r["pversion"])],
                        tag_id[(r["ctag"], r["cversion"])],
                        _weight(r.get("negative")),
                    )
                )
            counts["calc_arc"] = _copy(
                cur,
                "fsn.calc_arc",
                ("filing_id", "grp", "arc", "parent_tag_id", "child_tag_id", "weight"),
                arc_rows,
            )
            cur.execute(
                """
                insert into fsn.company_load (company_id, cik, input_sha256, loader_commit, row_counts, run_id)
                values (%s, %s, %s, %s, %s::jsonb, %s::uuid)
                on conflict (company_id) do update set input_sha256 = excluded.input_sha256,
                    loader_commit = excluded.loader_commit, row_counts = excluded.row_counts,
                    run_id = excluded.run_id, loaded_at = now()
                """,
                (
                    company_id,
                    cik,
                    m["input_sha256"],
                    loader_commit,
                    json.dumps(dict(counts)),
                    run_id,
                ),
            )
    logger.info("fsn_load.company", cik=cik, **counts)
    return {"cik": cik, "company_id": company_id, "skipped": False, **counts}


def run(
    conn: psycopg.Connection,
    companies_root: Path,
    ciks: list[str] | None = None,
    *,
    force: bool = False,
    git_commit: str | None = None,
) -> dict[str, Any]:
    """Load every (or the named) company directories; one rule_run for the batch."""
    loader_commit = git_commit or _git_commit()
    dirs = sorted(
        d
        for d in companies_root.iterdir()
        if d.is_dir() and (d / "manifest.json").exists()
    )
    if ciks:
        want = {c.zfill(10) for c in ciks}
        dirs = [d for d in dirs if d.name in want]
    run_id = start_rule_run(
        conn, RULE_ID, "apply", "on", [d.name for d in dirs], git_commit=loader_commit
    )
    conn.commit()
    out: dict[str, Any] = {
        "run_id": run_id,
        "companies": 0,
        "skipped": 0,
        "errors": 0,
        "value": 0,
        "line": 0,
    }
    for d in dirs:
        try:
            r = load_company(
                conn, d, loader_commit=loader_commit, run_id=run_id, force=force
            )
            conn.commit()
        except Exception as exc:  # noqa: BLE001
            conn.rollback()
            logger.warning("fsn_load.company_failed", cik=d.name, error=repr(exc)[:200])
            out["errors"] += 1
            continue
        if r.get("skipped"):
            out["skipped"] += 1
        else:
            out["companies"] += 1
            out["value"] += r.get("value", 0)
            out["line"] += r.get("line", 0)
    finish_rule_run(conn, run_id, out)
    conn.commit()
    return out
