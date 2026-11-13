"""DB-backed FilingStructure source for the cell proof (schema fsn, migration 0118).

The same structure proof/fsn.py builds from the SEC quarterly files, read per company from the fsn.* tables
the company-wise store already holds: no download, no zstd, no whole-quarter scan of every filer. One query
per table for all of a company's accessions (indexed on fsn.filing.accession / filing_id), never a query per cell.

What is produced is exactly what load_quarter produces, by the same filters:
  pre  fsn.line with stmt in BS/IS/CF/CI/EQ and not inpth (parenthetical), ordered (report, line)
  cal  fsn.calc_arc: one arc per parent kept once in calc_children, per-group (grp as text) in calc_groups,
       custom_parents where the parent tag is a filer extension (version outside the standard prefixes)
  num  fsn.value with iprx = 0 and no co-registrant: dim_id = 0 into .num; with_dims also dim_id > 0 with a
       non-empty fsn.dim.segments into .dim_num under those segments
A filing the store does not hold (no fsn.filing row, or a row with neither lines nor values) is simply absent
from the result; the caller falls back to the files for that one filing and logs it.
"""

from __future__ import annotations

import psycopg

from scrooner_pipeline.proof.fsn import (
    STATEMENTS,
    STD_PREFIXES,
    FilingStructure,
    NumValue,
    PreLine,
)


def load_filings(
    conn: psycopg.Connection, accessions: set[str], with_dims: bool = False
) -> dict[str, FilingStructure]:
    """FilingStructure per accession found in fsn.*; accessions the store does not hold are left out."""
    if not accessions:
        return {}
    out: dict[str, FilingStructure] = {}
    by_id: dict[int, FilingStructure] = {}
    id_of: dict[str, int] = {}
    with conn.cursor() as cur:
        cur.execute(
            "select id, accession, cik, form, filed, period, fy, fp from fsn.filing where accession = any(%s)",
            (sorted(accessions),),
        )
        for fid, acc, cik, form, filed, period, fy, fp in cur.fetchall():
            s = FilingStructure(acc, cik.zfill(10), form, filed, period, fy, fp or None)
            out[acc] = s
            by_id[fid] = s
            id_of[acc] = fid
        if not by_id:
            return {}
        ids = list(by_id)
        has_rows: set[int] = set()
        cur.execute(
            """
            select l.filing_id, l.report, l.line, l.stmt, t.tag, t.version, l.plabel, l.negating
            from fsn.line l join fsn.tag t on t.id = l.tag_id
            where l.filing_id = any(%s) and l.stmt = any(%s) and not l.inpth
            order by l.filing_id, l.report, l.line
            """,
            (ids, list(STATEMENTS)),
        )
        for fid, report, line, stmt, tag, version, plabel, negating in cur.fetchall():
            by_id[fid].pre.append(
                PreLine(report, line, stmt, tag, version, plabel or "", bool(negating))
            )
            has_rows.add(fid)
        cur.execute(
            """
            select a.filing_id, a.grp, pt.tag, pt.version, ct.tag, a.weight
            from fsn.calc_arc a
            join fsn.tag pt on pt.id = a.parent_tag_id
            join fsn.tag ct on ct.id = a.child_tag_id
            where a.filing_id = any(%s)
            order by a.filing_id, a.grp, a.arc
            """,
            (ids,),
        )
        for fid, grp, ptag, pversion, ctag, weight in cur.fetchall():
            s = by_id[fid]
            arc = (ctag, weight < 0)
            if arc not in s.calc_children[ptag]:
                s.calc_children[ptag].append(arc)
            s.calc_groups[ptag][str(grp)].append(arc)
            s.calc_parents[ctag].add(ptag)
            if not (pversion or "").startswith(STD_PREFIXES):
                s.custom_parents[ctag].add(ptag)
        cur.execute(
            f"""
            select v.filing_id, t.tag, t.version, v.ddate, v.qtrs, v.uom, v.value, v.dcml, d.segments
            from fsn.value v
            join fsn.tag t on t.id = v.tag_id
            join fsn.dim d on d.id = v.dim_id
            where v.filing_id = any(%s) and v.iprx = 0 and v.coreg = ''
              and v.value is not null {"" if with_dims else "and v.dim_id = 0"}
            order by v.filing_id, v.id
            """,
            (ids,),
        )
        for (
            fid,
            tag,
            version,
            ddate,
            qtrs,
            uom,
            value,
            dcml,
            segments,
        ) in cur.fetchall():
            has_rows.add(fid)
            nv = NumValue(tag, version, ddate, int(qtrs), uom, value, dcml)
            s = by_id[fid]
            if segments is None or segments == "":
                # no dimension (dim_id 0) or a dimension without segments text (never keyed)
                if segments == "":
                    s.num[(tag, ddate, int(qtrs))].append(nv)
            else:
                s.dim_num[(tag, ddate, int(qtrs), segments)].append(nv)
    # a filing row with neither lines nor values (a co-registrant copy loaded under another company) is not held
    return {acc: s for acc, s in out.items() if id_of[acc] in has_rows}
