"""Key classes and verdict of the capex / D&A store gate (scripts/slot_records/capex_da_store_gate.py), pure.

The gate compares every store capex / D&A key with the lane's Verifier-passed family file. A key the store publishes
that the lane file does not hold with the SAME vintage and value has no Verifier evidence behind it, so those classes
FAIL the gate (they used to pass: "later vintage", "print where the lane derives differently", "key not in the lane").
They stay failing until the Verifier clears each key; a cleared key is named in the optional cleared-keys file the
gate reads, never by loosening a class here."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

# classes that fail the gate, with the reason each is not evidence
FAIL_CLASSES = {
    "store_value_lane_held": "store publishes where the lane holds the same filing",
    "value_differs": "store value differs from the lane's value",
    "store_conflicting_values_in_filing": "store holds two values in one filing",
    "later_vintage_publishes_where_lane_held_the_original": "store publishes a later filing than the one the lane held; no Verifier evidence",
    "store_print_where_lane_derives_differently": "store prints a quarter the lane held or derived to a different value; no Verifier evidence",
    "store_value_key_not_in_lane": "store publishes a key the Verifier-passed lane file does not have",
}
# reported in the key list, not failing: the lane or the calendar explains them
INFO_CLASSES = {
    "store_print_equals_lane_derived_quarter": "store print equals the lane's own derived quarter",
    "store_key_before_lane_window": "2011-2013 comparative: the lane window starts 2014 (out of the data window)",
}


def num(x: Any) -> Decimal | None:
    return None if x in (None, "") else Decimal(str(x))


def classify(
    key: tuple, lane: dict | None, store: dict | None, lane_derived: dict | None
) -> str:
    """key = (cik, concept, grain, fsn_end); lane / store are the cell rows (or None); lane_derived is the lane's
    derived-quarter row on the same key (or None)."""
    av = num(lane["value"]) if lane and lane["state"] == "value" else None
    bv = num(store["value"]) if store and store["state"] == "value" else None
    if (
        store
        and store["state"] == "defect"
        and store.get("reason_code") == "conflicting_values_in_filing"
    ):
        return "store_conflicting_values_in_filing"
    if av is not None and bv is not None:
        return "same_value" if av == bv else "value_differs"
    if av is not None:
        return "lane_value_store_blank"
    if bv is None or store is None:
        return "both_blank"
    if lane and store.get("accession") != lane.get("accession"):
        return "later_vintage_publishes_where_lane_held_the_original"
    if lane:
        return "store_value_lane_held"
    if key[3] < "2014-01-01":
        return "store_key_before_lane_window"
    if lane_derived is not None:
        d = lane_derived
        return (
            "store_print_equals_lane_derived_quarter"
            if d["state"] in ("value", "derived") and num(d["value"]) == bv
            else "store_print_where_lane_derives_differently"
        )
    return "store_value_key_not_in_lane"


def failing_keys(
    rows: list[dict], cleared: frozenset[tuple] | set[tuple] = frozenset()
) -> list[dict]:
    """rows: [{"key": tuple, "class": str}]; the keys whose class fails the gate and the Verifier has not cleared"""
    return [
        r for r in rows if r["class"] in FAIL_CLASSES and tuple(r["key"]) not in cleared
    ]


def verdict(
    rows: list[dict], cleared: frozenset[tuple] | set[tuple] = frozenset()
) -> tuple[str, dict[str, int]]:
    bad = failing_keys(rows, cleared)
    per: dict[str, int] = {}
    for r in bad:
        per[r["class"]] = per.get(r["class"], 0) + 1
    return ("FAIL" if bad else "PASS"), per
