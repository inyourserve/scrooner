"""Insert-only load of the allowlisted dimensional-note facts (decision 2026-11-14, option B).

The shard used to drop every dimensional num row whose tag has no statement pre row (see dim_note_allowlist). This
module adds exactly those rows, for tags on the allowlist, to filings that are ALREADY in fsn.filing: it reads the
bucket's period extracts (sub of record is the database; the bucket is read-only), and inserts into fsn.value
`on conflict do nothing`. It never deletes, never reloads a filing, never touches fsn.line/report/calc_arc/company_load.
fsn.tag and fsn.dim (shared reference tables) are insert-only too (`on conflict do nothing`).

Idempotent: the unique key of fsn.value (filing, tag, ddate, qtrs, uom, dim, iprx, coreg) means a rerun adds nothing.
Dry-run (default) reads only: it counts, per company, the rows an apply would add (a row whose tag or dimension is not
yet in the database is counted as new).

Scope: SEC-set filings (fsn_set not 'edgar:%'). EDGAR-built nightly filings are not covered here.
"""

from __future__ import annotations

import subprocess
from collections import defaultdict
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import structlog

from scrooner_pipeline.fsn_store.company_dir import NO_DIM, STATEMENT_STMTS
from scrooner_pipeline.fsn_store.dim_note_allowlist import Rules, keep_dimensional
from scrooner_pipeline.fsn_store.dim_note_allowlist import load as dim_note_rules
from scrooner_pipeline.fsn_store.load import _d8, _float, _int, _num

logger = structlog.get_logger()
CHUNK = 5000
STATEMENT_TIMEOUT = "5min"
# bucket folders holding a period: the cohort extract, then the predecessor registrants' extract
PREFIXES = ("", "predecessors/")
NEED = ("pre", "num", "tag", "dim")

Fetch = Callable[[str, str, Path, str], Path]  # (period, table, cache, prefix) -> file


def _rows(path: Path) -> Iterator[dict[str, str]]:
    """Rows of a (multi-frame) zstd TSV as dicts; plain splitting (SEC values carry no tab or quote)."""
    proc = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    assert proc.stdout is not None
    it = iter(proc.stdout)
    header = next(it).decode("utf-8", "replace").rstrip("\r\n").split("\t")
    for line in it:
        yield dict(
            zip(header, line.decode("utf-8", "replace").rstrip("\r\n").split("\t"))
        )
    proc.wait()


def candidates(
    paths: dict[str, Path],
    accs: set[str],
    allow: Rules | None = None,
) -> tuple[
    list[dict[str, str]],
    dict[tuple[str, str], dict[str, str]],
    dict[str, dict[str, str]],
]:
    """(num rows, tag meta, dim meta) for the dimensional, not-kept-before, allowlisted rows of `accs`."""
    on_stmt: set[tuple[str, str, str]] = set()
    for r in _rows(paths["pre"]):
        if r["adsh"] in accs and r.get("stmt") in STATEMENT_STMTS:
            on_stmt.add((r["adsh"], r["tag"], r["version"]))
    allow = allow or dim_note_rules()
    dims = {
        r["dimhash"]: r
        for r in _rows(paths["dim"])
        if allow.any_segments(r["segments"])
    }
    out: list[dict[str, str]] = []
    for r in _rows(paths["num"]):
        a = r["adsh"]
        if a not in accs or r["dimh"] == NO_DIM:
            continue
        if (a, r["tag"], r["version"]) in on_stmt:
            continue  # already stored by the shard's statement rule
        d = dims.get(r["dimh"])
        if d is None or not keep_dimensional(
            a,
            r["tag"],
            r["version"],
            d["segments"],
            int(r["qtrs"] or 0),
            on_stmt,
            allow,
        ):
            continue
        out.append(r)
    want_t = {(r["tag"], r["version"]) for r in out}
    want_d = {r["dimh"] for r in out}
    tags = {
        (r["tag"], r["version"]): r
        for r in _rows(paths["tag"])
        if (r["tag"], r["version"]) in want_t
    }
    return out, tags, {h: d for h, d in dims.items() if h in want_d}


def _plan(
    conn: Any,
    rows: list[dict[str, str]],
    tags: dict[tuple[str, str], dict[str, str]],
    dims: dict[str, dict[str, str]],
    acc_info: dict[str, tuple[int, int | None]],
    *,
    apply: bool,
) -> tuple[dict[int | None, int], int]:
    """Per company_id, the rows that were/would be added; and the rows already present."""
    added: dict[int | None, int] = defaultdict(int)
    present = 0
    with conn.cursor() as cur:
        if apply:
            cur.execute(f"set local statement_timeout = '{STATEMENT_TIMEOUT}'")
            cur.executemany(
                "insert into fsn.tag (tag, version, custom, abstract, datatype, iord, crdr, tlabel) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s) on conflict (tag, version) do nothing",
                [
                    (
                        t,
                        v,
                        m.get("custom") == "1",
                        m.get("abstract") == "1",
                        m.get("datatype") or None,
                        m.get("iord") or None,
                        m.get("crdr") or None,
                        m.get("tlabel") or None,
                    )
                    for (t, v), m in sorted(tags.items())
                ],
            )
            cur.executemany(
                "insert into fsn.dim (dimh, segments, segt) values (%s, %s, %s) on conflict (dimh) do nothing",
                [
                    (h, m.get("segments") or None, m.get("segt") == "1")
                    for h, m in dims.items()
                ],
            )
        pairs = sorted({(r["tag"], r["version"]) for r in rows})
        cur.execute(
            "select id, tag, version from fsn.tag where (tag, version) in (select * from unnest(%s::text[], %s::text[]))",
            ([t for t, _ in pairs], [v for _, v in pairs]),
        )
        tag_id = {(t, v): i for i, t, v in cur.fetchall()}
        cur.execute(
            "select id, dimh from fsn.dim where dimh = any(%s)",
            (sorted({r["dimh"] for r in rows}),),
        )
        dim_id = {h: i for i, h in cur.fetchall()}
        keyed: dict[tuple, tuple] = {}
        for r in rows:
            fid, cid = acc_info[r["adsh"]]
            vk = (
                fid,
                tag_id.get(
                    (r["tag"], r["version"]), (r["tag"], r["version"])
                ),  # unknown (dry-run): the name
                _d8(r["ddate"]),
                _int(r["qtrs"], 0),
                r["uom"],
                dim_id.get(
                    r["dimh"], r["dimh"]
                ),  # unknown (dry-run): the hash keeps rows apart
                _int(r.get("iprx"), 0),
                r.get("coreg") or "",
            )
            if vk in keyed:
                continue  # the loader keeps the first of a duplicate key too
            keyed[vk] = (
                cid,
                _num(r.get("value")),
                r.get("footnote") or None,
                _float(r.get("durp")),
                _float(r.get("datp")),
                _int(r.get("dcml")),
            )
        known = [k for k in keyed if isinstance(k[1], int) and isinstance(k[5], int)]
        existing: set[tuple] = set()
        if known:
            cur.execute(
                "select filing_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg from fsn.value "
                "where filing_id = any(%s) and tag_id = any(%s) and dim_id <> 0",
                (sorted({k[0] for k in known}), sorted({k[1] for k in known})),
            )
            existing = set(cur.fetchall())
        todo = [(k, v) for k, v in keyed.items() if k not in existing]
        present = len(keyed) - len(todo)
        for _, v in todo:
            added[v[0]] += 1
        if apply:
            for i in range(0, len(todo), CHUNK):
                cur.executemany(
                    "insert into fsn.value (filing_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg, company_id, "
                    "value, footnote, durp, datp, dcml) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                    "on conflict (filing_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg) do nothing",
                    [(*k, *v) for k, v in todo[i : i + CHUNK]],
                )
    return added, present


def run(
    connect: Callable[[], Any],
    company_ids: list[int],
    fetch: Fetch,
    cache: Path,
    *,
    apply: bool = False,
    periods: list[str] | None = None,
    allow: Rules | None = None,
) -> dict[str, Any]:
    """Dry-run (default) or apply, period by period; each period is one transaction on its own connection
    (read-only when not apply), so a pooler drop costs at most one period and a rerun resumes (idempotent)."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "select accession, id, company_id, fsn_set from fsn.filing "
            "where company_id = any(%s) and fsn_set not like 'edgar:%%'",
            (company_ids,),
        )
        by_set: dict[str, dict[str, tuple[int, int | None]]] = defaultdict(dict)
        for a, fid, cid, fs in cur.fetchall():
            by_set[fs][a] = (fid, cid)
    per_company: dict[int | None, int] = defaultdict(int)
    per_period: dict[str, int] = {}
    missing: list[str] = []
    present_total = 0
    for fs in sorted(by_set):
        if periods and fs not in periods:
            continue
        accs = by_set[fs]
        paths: dict[str, Path] | None = None
        for prefix in PREFIXES:
            try:
                paths = {t: fetch(fs, t, cache, prefix) for t in NEED}
                break
            except FileNotFoundError:
                paths = None
        if paths is None:
            missing.append(fs)
            continue
        try:
            rows, tags, dims = candidates(paths, set(accs), allow)
            with connect() as conn, conn.transaction():
                if not apply:
                    conn.execute("set transaction read only")
                added, present = _plan(conn, rows, tags, dims, accs, apply=apply)
        finally:
            for p in paths.values():
                p.unlink(missing_ok=True)
        for c, n in added.items():
            per_company[c] += n
        per_period[fs] = sum(added.values())
        present_total += present
        logger.info(
            "fsn_dim_note.period",
            period=fs,
            candidates=len(rows),
            added=per_period[fs],
            present=present,
            apply=apply,
        )
    return {
        "mode": "apply" if apply else "dry-run",
        "rows_to_add" if not apply else "rows_added": sum(per_company.values()),
        "already_present": present_total,
        "per_company": dict(sorted(per_company.items(), key=lambda kv: -kv[1])),
        "per_period": per_period,
        "periods_missing_in_bucket": missing,
    }
