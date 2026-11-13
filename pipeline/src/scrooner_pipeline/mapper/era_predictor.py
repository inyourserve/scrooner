"""Predictor candidates for the years the FSN era extension could not carry (rule company_tag_map.era_extend@1,
decided_by tag_expert_predictor).

Input: the Tag Expert's per-10-K predictions (data-team/tags/exam/eras/<TICKER>-<accession>-prediction.csv; same
columns as a docmap plus the filing's `period` and the `rules_commit` of the frozen rules). For each docmap data point
whose merged era still starts after the data window, every earlier 10-K that has a prediction row for it becomes one
company_tag_map slice for that fiscal year. A slice is a CANDIDATE: it serves only if the cell proof (analytics.cell_proof)
backs it; era_guard.hold_unproven replaces every unbacked slice by a not_presented row, reason_class era_unmapped.
Total debt and interest expense can be reloaded on their own (`concepts`): the loader replaces only the predictor and
guard rows of those concepts."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import era_extend

PREDICTOR_BY = "tag_expert_predictor"
GUARD_BY = "era_guard"
PRED_BY = (PREDICTOR_BY, GUARD_BY)
MARK = "PREDICTOR-CANDIDATE"
NO_FILING_REASON = "no_public_filing_for_period"


def read_predictions(directory: Path) -> dict[str, dict[date, list[dict]]]:
    """ticker -> filing period end -> prediction rows."""
    out: dict[str, dict[date, list[dict]]] = defaultdict(dict)
    for p in sorted(directory.glob("*-prediction.csv")):
        with p.open(newline="") as fh:
            for r in csv.DictReader(fh):
                if not r.get("period"):
                    continue
                out[r["ticker"].upper()].setdefault(
                    date.fromisoformat(r["period"]), []
                ).append(r)
    return out


def _concept_key(r: dict) -> int | None:
    return r["canonical_concept_id"] or r["parent_concept_id"]


def candidates(
    ticker: str,
    preds: dict[date, list[dict]],
    docrows: list[dl.DocmapRow],
    concept_ids: dict[str, int],
    concept_statement: dict[str, str],
    cid: int,
    cik: str,
    *,
    concepts: set[str] | None = None,
    floor: date = era_extend.FLOOR,
) -> tuple[list[dict], list[dict]]:
    """(seeder-shaped slice rows, rejects). Pure. Slices stay strictly before the data point's merged era_from; each
    covers one fiscal year (from the day after the previous 10-K's period end to its own period end)."""
    rows: list[dict] = []
    rejects: list[dict] = []
    periods = sorted(preds)
    names = set(concept_ids)
    for d in docrows:
        base = dl._base(d.data_point)
        if concepts is not None and base not in concepts:
            continue
        boundary = d.era_from
        if boundary <= floor:
            continue
        for i, period in enumerate(periods):
            if period >= boundary:
                break
            pr = next(
                (
                    r
                    for r in preds[period]
                    if dl.served_concept(
                        r["data_point"].removesuffix("_resolved"), names
                    )
                    == d.data_point
                    or r["data_point"] == base
                ),
                None,
            )
            era_from = max(
                floor,
                periods[i - 1] + timedelta(days=1) if i else dl._fy_start(period),
            )
            era_to = min(
                period
                if i + 1 < len(periods) and periods[i + 1] < boundary
                else boundary - timedelta(days=1),
                boundary - timedelta(days=1),
            )
            if era_from > era_to:
                continue
            if pr is None:
                continue
            status = dl.STATUS_ALIASES.get(pr["status"], pr["status"])
            if status not in dl.STATUSES:
                rejects.append(_rej(d, pr, f"unknown status {pr['status']!r}"))
                continue
            try:
                parts = dl.parse_parts(pr["tags"])
            except ValueError as exc:
                rejects.append(_rej(d, pr, str(exc)))
                continue
            if status in dl.TAGLESS_STATUS:
                parts = parts if status == "combined" else ()
            elif not parts or (status != "component sum" and len(parts) > 1):
                rejects.append(_rej(d, pr, f"{status} row with {len(parts)} tags"))
                continue
            note = (
                f"{MARK}: {pr.get('rule_ids') or pr.get('rule')} ({pr.get('evidence_class')}; rules "
                f"{pr.get('rules_commit')}) on the 10-K {pr['acc']} (FY end {period}); serves only if the cell "
                f"proof backs it, else era_unmapped"
            )
            pd = dl.DocmapRow(
                ticker,
                d.data_point,
                status,
                parts,
                pr["stmt"],
                pr.get("r_page", ""),
                pr.get("label", ""),
                era_from,
                pr["acc"],
                note,
                f"predictor:{pr['acc']}",
                period,
            )
            if status == "component sum" and dl.instant_sum_refused(
                d.data_point, concept_statement[d.data_point]
            ):
                rejects.append(_rej(d, pr, "instant component sum refused"))
                continue
            try:
                for t in dl.table_rows(pd, cid, cik, concept_statement):
                    rows.append(
                        {
                            **t,
                            "era_to": era_to,
                            "rule_id": era_extend.EXT_RULE_ID,
                            "decided_by": PREDICTOR_BY,
                            "serve_note": note,
                            **(
                                {"reason": note, "reason_class": "predictor_candidate"}
                                if status in dl.TAGLESS_STATUS
                                else {}
                            ),
                        }
                    )
            except (ValueError, TypeError, KeyError) as exc:
                rejects.append(_rej(d, pr, f"invalid row: {exc}"))
    return rows, rejects


def _rej(d: dl.DocmapRow, pr: dict, why: str) -> dict[str, Any]:
    return {
        "source": f"predictor:{pr.get('acc')}",
        "ticker": d.ticker,
        "data_point": d.data_point,
        "status": pr.get("status"),
        "why": why,
    }


def no_filing_rows(
    docrows: list[dl.DocmapRow],
    concept_statement: dict[str, str],
    cid: int,
    cik: str,
    *,
    floor: date = era_extend.FLOOR,
) -> list[dict]:
    """A company with no 10-K in the data window before its listing: every uncovered year of every template data
    point is a reasoned blank, reason no_public_filing_for_period (the caller names the CIKs). Pure."""
    out: list[dict] = []
    for d in docrows:
        if d.era_from <= floor:
            continue
        pd = replace(d, status="not_presented", parts=(), base_era=None, era_from=floor)
        (row,) = dl.table_rows(pd, cid, cik, concept_statement)
        out.append(
            {
                **row,
                "era_to": d.era_from - timedelta(days=1),
                "rule_id": era_extend.EXT_RULE_ID,
                "decided_by": "era_extend",
                "reason": "no 10-K was filed for the period (the company was not yet public)",
                "reason_class": NO_FILING_REASON,
                "serve_note": "DATA-INFERRED: no 10-K of this company exists before its first filing",
            }
        )
    return out
