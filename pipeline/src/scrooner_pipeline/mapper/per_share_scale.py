"""Database side of the filer-scale guard (common/per_share_guard.py): the other columns of a filing's per-share tag.
Only suspicious cells (per-share, |value| >= 1000: a handful per company) cost a read; two queries per company."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from scrooner_pipeline.common.per_share_guard import (
    at_or_above_floor,
    filer_scale_error,
)


def other_columns(
    conn: Any, company_id: int, pairs: set[tuple[str, str]]
) -> dict[tuple[str, str], list[Decimal]]:
    """(accession, tag) -> every undimensioned annual or instant value of that tag in that filing (fsn.value and the
    non-derived core.fact), all columns. One batched read per source. Pure read."""
    out: dict[tuple[str, str], list[Decimal]] = defaultdict(list)
    if not pairs:
        return out
    accs = sorted({a for a, _t in pairs})
    tags = sorted({t for _a, t in pairs})
    with conn.cursor() as cur:
        cur.execute(
            """select f.accession, t.tag, v.value
               from fsn.value v join fsn.tag t on t.id = v.tag_id join fsn.filing f on f.id = v.filing_id
               where v.company_id = %s and f.accession = any(%s) and t.tag = any(%s)
                 and v.dim_id = 0 and v.coreg = '' and v.iprx = 0 and v.value is not null
                 and (v.qtrs = 0 or v.qtrs between 3 and 5)""",
            (company_id, accs, tags),
        )
        for acc, tag, val in cur.fetchall():
            out[(acc, tag)].append(Decimal(val))
        cur.execute(
            """select fl.accession_number, c.tag, f.value
               from core.fact f join core.concept c on c.id = f.concept_id join core.filing fl on fl.id = f.filing_id
               where f.company_id = %s and fl.accession_number = any(%s) and c.tag = any(%s) and not f.is_derived""",
            (company_id, accs, tags),
        )
        for acc, tag, val in cur.fetchall():
            out[(acc, tag)].append(Decimal(val))
    return out


def scale_error_cell_indexes(
    conn: Any, company_id: int, cells: list[dict], concept_info: dict
) -> set[int]:
    """Indexes of `cells` (the mapper's cell dicts) that are a filer_scale_error: a per-share concept, |value| >= 1000
    and a same-filing, same-tag other column 10^3 or 10^6 times smaller. The cell's (accession, tag) come from its
    source_fact_ids (core.fact) and source_value_ids (fsn.value)."""
    sus = [
        i
        for i, c in enumerate(cells)
        if at_or_above_floor(concept_info[c["canonical_concept_id"]][0], c["value"])
    ]
    if not sus:
        return set()
    fact_ids = sorted({x for i in sus for x in cells[i].get("source_fact_ids") or []})
    value_ids = sorted({x for i in sus for x in cells[i].get("source_value_ids") or []})
    tag_of: dict[tuple[str, int], tuple[str, str]] = {}
    with conn.cursor() as cur:
        if fact_ids:
            cur.execute(
                """select f.id, fl.accession_number, c.tag from core.fact f join core.concept c on c.id = f.concept_id
                   join core.filing fl on fl.id = f.filing_id where f.id = any(%s)""",
                (fact_ids,),
            )
            for fid, acc, tag in cur.fetchall():
                tag_of[("f", fid)] = (acc, tag)
        if value_ids:
            cur.execute(
                """select v.id, f.accession, t.tag from fsn.value v join fsn.tag t on t.id = v.tag_id
                   join fsn.filing f on f.id = v.filing_id where v.id = any(%s)""",
                (value_ids,),
            )
            for vid, acc, tag in cur.fetchall():
                tag_of[("v", vid)] = (acc, tag)
    pairs_by_cell: dict[int, set[tuple[str, str]]] = {}
    for i in sus:
        c = cells[i]
        keys = [("f", x) for x in c.get("source_fact_ids") or []] + [
            ("v", x) for x in c.get("source_value_ids") or []
        ]
        pairs_by_cell[i] = {tag_of[k] for k in keys if k in tag_of}
    others = other_columns(conn, company_id, set().union(*pairs_by_cell.values()))
    return {
        i
        for i in sus
        if filer_scale_error(
            concept_info[cells[i]["canonical_concept_id"]][0],
            cells[i]["value"],
            [o for p in pairs_by_cell[i] for o in others.get(p, ())],
        )
    }
