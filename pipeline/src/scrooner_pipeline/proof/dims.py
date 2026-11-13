"""Proof of a dimensional cell (company_tag_map rows with dims, 0125): the filing's value of each part tag under the
row's own segments, summed with the row's signs, against the shown value at the filer's stated precision.

A part's value is read ONLY under exactly its segments (FilingStructure.value_dim); the no-dimension total or another
slice is never a stand-in. A part the filing does not print under those segments makes the cell UNCHECKED (unknown,
not a disagreement). The FSN quarter is the SEC's own data set, read by position from the filing (proof/fsn.py)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from scrooner_pipeline.proof.fsn import FilingStructure, fsn_ddate

PROVEN, DISAGREE, UNCHECKED = "PROVEN", "DISAGREE", "UNCHECKED"


@dataclass(frozen=True)
class DimPart:
    tag: str
    dims: str  # fsn.dim.segments format
    sign: int = 1


def prove_dims_cell(
    structure: FilingStructure,
    parts: list[DimPart],
    shown_value: Decimal,
    period_end: date,
    qtrs: int,
    tol: Decimal,
) -> dict:
    """{verdict, reason_code, position_value, parts: [{tag, dims, value}]}; shown within tol of the signed sum of
    the parts' printed values is PROVEN."""
    ddate = fsn_ddate(period_end)
    total = Decimal(0)
    seen = []
    for part in parts:
        nv = structure.value_dim(part.tag, ddate, qtrs, part.dims)
        if nv is None:
            return {
                "verdict": UNCHECKED,
                "reason_code": "no_value_under_segments",
                "position_value": None,
                "parts": seen,
                "missing": {"tag": part.tag, "dims": part.dims},
            }
        total += part.sign * nv.value
        seen.append({"tag": part.tag, "dims": part.dims, "value": str(nv.value)})
    agree = abs(shown_value - total) <= tol
    return {
        "verdict": PROVEN if agree else DISAGREE,
        "reason_code": None if agree else "shown_differs_from_printed_segments",
        "position_value": total,
        "parts": seen,
    }
