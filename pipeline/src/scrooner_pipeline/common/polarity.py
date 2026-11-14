"""One sign per concept (Tag Expert ruling, data-team/tags/line_map/rules/polarity.csv).

The mapper's serve path (mapper/company_tag_map.py) and the proof (proof/prove.py) call THIS function, so a cell
and its proof can never apply different polarity tables. Rule: a concept whose table sign is '+' with
normalise 'Y' (expenses, CF payment elements, DPS) is always positive; a SINGLE-ELEMENT mapped value (one printed
fact, or one note fact) that arrives negative because the filer uses the opposite polarity is flipped. Signed
concepts (taxes, credit provisions, other income, net interest, interest income, cfo/cfi/cff) and raw-sign
concepts are never touched. A component sum keeps its computed sign (its parts already carry their own weights),
so this function is never applied to one: that is what prevents a double flip.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

POLARITY_CSV = (
    Path(__file__).resolve().parents[4]
    / "data-team"
    / "tags"
    / "line_map"
    / "rules"
    / "polarity.csv"
)

FLIP_NOTE = "polarity_flip"


@lru_cache(maxsize=1)
def positive_concepts() -> frozenset[str]:
    """Data points whose served sign is fixed positive (sign '+', normalise 'Y')."""
    with POLARITY_CSV.open(newline="", encoding="utf-8") as fh:
        return frozenset(
            r["data_point"].strip()
            for r in csv.DictReader(fh)
            if r["sign"].strip() == "+" and r["normalise"].strip().upper() == "Y"
        )


def _base(name: str) -> str:
    return name.removesuffix("_resolved")


def is_fixed_positive(data_point: str) -> bool:
    return _base(data_point) in positive_concepts()


def apply_polarity(data_point: str, value: Decimal) -> tuple[Decimal, bool]:
    """(served value, flipped?) for a single-element value already carrying its row sign."""
    if value < 0 and is_fixed_positive(data_point):
        return -value, True
    return value, False


def flip_note(raw: Decimal) -> str:
    return f"{FLIP_NOTE}: filer polarity is the opposite of the concept's fixed sign; raw value {raw} kept in lineage"
