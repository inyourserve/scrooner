"""Phase 2 of the predictor fallback: the cell proof decides every predictor slice (rule company_tag_map.era_extend@1).

A slice = the rows the loader wrote for one (company, concept, era) with decided_by tag_expert_predictor. After the
slice was resolved (tagmap-plan) and proved (scrooner-proof run --write), it is KEPT only when every FY cell of its era
has a cell_proof row backing it: verdict PROVEN for a value slice, NOT_PRESENTED for a reason slice. Anything else
(no proof row, DISAGREE, UNCHECKED, a mix) replaces the slice by one not_presented row with reason_class era_unmapped
(decided_by era_guard): never silently blank, never a served value the proof did not back. Re-run tagmap-plan afterwards
so the held cells leave canonical_fact. A reload of the predictor rows of a concept deletes its guard rows too."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

import psycopg

from scrooner_pipeline.mapper import era_extend
from scrooner_pipeline.mapper.company_tag_map_seed import INSERT, normalize
from scrooner_pipeline.mapper.era_predictor import GUARD_BY, PREDICTOR_BY

UNMAPPED = "era_unmapped"
VALUE_DECISIONS = {"concept", "component"}


def verdict_backs(is_value: bool, verdicts: list[str]) -> bool:
    """Pure: all FY cells of the era carry the verdict that backs the slice, and there is at least one."""
    want = "PROVEN" if is_value else "NOT_PRESENTED"
    return bool(verdicts) and all(v == want for v in verdicts)


def hold_unproven(
    conn: psycopg.Connection, company_ids: list[int], *, apply: bool = False
) -> dict:
    with conn.cursor() as cur:
        cur.execute("select name, id from analytics.canonical_concept")
        concept_ids = dict(cur.fetchall())
        names = {i: n for n, i in concept_ids.items()}
        cur.execute(
            """select id, company_id, cik, decision, canonical_concept_id, parent_concept_id, stmt, era_from, era_to,
                      evidence_adsh, serve_note
               from analytics.company_tag_map
               where decided_by = %s and company_id = any(%s)""",
            (PREDICTOR_BY, company_ids),
        )
        rows = [dict(zip([c.name for c in cur.description], r)) for r in cur.fetchall()]
        cur.execute(
            """select company_id, data_point_name, period_end, verdict from analytics.cell_proof
               where company_id = any(%s) and period_grain = 'FY' and basis = 'latest'""",
            (company_ids,),
        )
        proofs: dict[tuple[int, str], list[tuple[date, str]]] = defaultdict(list)
        for cid, name, end, verdict in cur.fetchall():
            proofs[(cid, name.removesuffix("_resolved"))].append((end, verdict))
    slices: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        key = r["canonical_concept_id"] or r["parent_concept_id"]
        slices[(r["company_id"], key, r["era_from"], r["era_to"])].append(r)
    report: dict = {"slices": len(slices), "kept": 0, "held": 0, "held_cells": []}
    inserts: dict[int, list[dict]] = defaultdict(list)
    deletes: dict[int, list[int]] = defaultdict(list)
    for (cid, key, era_from, era_to), group in sorted(
        slices.items(), key=lambda kv: (kv[0][0], str(kv[0][2]))
    ):
        name = names[key].removesuffix("_resolved")
        verdicts = [
            v
            for end, v in proofs.get((cid, name), [])
            if era_from <= end <= (era_to or date.max)
        ]
        is_value = group[0]["decision"] in VALUE_DECISIONS
        if verdict_backs(is_value, verdicts):
            report["kept"] += 1
            continue
        report["held"] += 1
        report["held_cells"].append(
            (
                cid,
                name,
                str(era_from),
                str(era_to),
                ",".join(sorted(set(verdicts))) or "no proof",
            )
        )
        g = group[0]
        deletes[cid] += [r["id"] for r in group]
        inserts[cid].append(
            normalize(
                {
                    "company_id": cid,
                    "cik": g["cik"],
                    "stmt": g["stmt"]
                    if g["stmt"] in ("BS", "IS", "CF", "EQ", "CI", "UN")
                    else "UN",
                    "decision": "not_presented",
                    "canonical_concept_id": key,
                    "era_from": era_from,
                    "era_to": era_to,
                    "evidence_adsh": g["evidence_adsh"],
                    "reason": (
                        f"the predictor's candidate for this period was not backed by the cell proof "
                        f"({','.join(sorted(set(verdicts))) or 'no proof row'}): the line is not mapped for this era"
                    ),
                    "reason_class": UNMAPPED,
                    "decided_by": GUARD_BY,
                    "rule_id": era_extend.EXT_RULE_ID,
                    "serve_note": g["serve_note"],
                },
                {},
                concept_ids,
                era_extend.EXT_RULE_ID,
                [],
            )
        )
    report["companies"] = len(inserts)
    if not apply:
        return report
    for cid in sorted(inserts):
        with conn.transaction():
            conn.execute(
                "delete from analytics.company_tag_map where id = any(%s)",
                (deletes[cid],),
            )
            with conn.cursor() as cur:
                cur.executemany(INSERT, inserts[cid])
    report["applied"] = True
    return report
