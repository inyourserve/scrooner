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

from scrooner_pipeline.common import filer_xbrl_errors as fxe
from scrooner_pipeline.common import fsn_dropped_facts as fdf
from scrooner_pipeline.proof.fsn import (
    STATEMENTS,
    STD_PREFIXES,
    FilingStructure,
    NumValue,
    PreLine,
    fsn_ddate,
)


def apply_filer_corrections(s: FilingStructure) -> None:
    """The filer's XBRL is wrong where data-team/tags/line_map/rules/filer_xbrl_errors.csv says so: a correcting row
    replaces the stored undimensioned value that equals its xbrl_value (that tag and qtrs) with the printed one; a
    supplying row adds the printed value the filer left untagged, at the filing's own period end, when the tag is a
    line of one of its statements and carries no value there. The proof then reads the printed line. Pure on `s`."""
    for (tag, qtrs), c in sorted(fxe.for_accession(s.adsh).items()):
        if c.supplies:
            line = next((p for p in s.pre if p.tag == tag), None)
            if line is None or s.period is None:
                continue
            dd = fsn_ddate(s.period)
            if s.num.get((tag, dd, qtrs)):
                continue
            s.num[(tag, dd, qtrs)].append(
                NumValue(tag, line.version, dd, qtrs, "USD", c.printed_value, None)
            )
            s.corrections.append(c)
            continue
        hit = False
        for key, vals in s.num.items():
            if key[0] != tag or key[2] != qtrs:
                continue
            for i, v in enumerate(vals):
                if v.value == c.xbrl_value:
                    vals[i] = NumValue(
                        v.tag,
                        v.version,
                        v.ddate,
                        v.qtrs,
                        v.uom,
                        c.printed_value,
                        v.dcml,
                    )
                    hit = True
        if hit:
            s.corrections.append(c)
    for f in fdf.for_accession(s.adsh):
        # a fact the filing prints and the FSN ingest dropped: read as stored, unless the store has caught up
        if f.segment:
            if s.period is None:
                continue
            key = (f.tag, fsn_ddate(s.period), f.qtrs, f.segment)
            if not s.dim_num.get(key):
                s.dim_num[key].append(
                    NumValue(f.tag, "", key[1], f.qtrs, "USD", f.value, None)
                )
                s.corrections.append(f)
        else:
            line = next((p for p in s.pre if p.tag == f.tag), None)
            if line is None or s.period is None:
                continue
            dd = fsn_ddate(s.period)
            if not s.num.get((f.tag, dd, f.qtrs)):
                s.num[(f.tag, dd, f.qtrs)].append(
                    NumValue(f.tag, line.version, dd, f.qtrs, "USD", f.value, None)
                )
                s.corrections.append(f)


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
    for acc in out:
        apply_filer_corrections(out[acc])
    # a filing row with neither lines nor values (a co-registrant copy loaded under another company) is not held
    return {acc: s for acc, s in out.items() if id_of[acc] in has_rows}
