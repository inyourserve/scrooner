"""The one input loader for metrics: shown cells only (one-display-path plan 2026-11-22, step 4).

load_shown_cells reads analytics.shown_cell (migration 0135, PROPOSED: the view's SQL is
cell_display_state.SHOWN_CELL_VIEW_SQL) and never analytics.canonical_fact. A cell is an input only when the stock page
shows it (display SHOWN_VALUE) and its latest proof is PROVEN for that value; a DISAGREE, UNCHECKED, OPEN, hidden or
out-of-template cell is absent, so the metric gets a null with a reason, never a fallback (plan rule b).

Rule (c) of metrics/provenance.py is wired in: every cell comes back as a provenance.InputCell (status PROVEN, or
NOT_PRESENTED for a line the filing evidences as absent) with its badge, ready for gate_inputs / build_cell_record. A
NOT_PRESENTED cell is returned only for a concept some metric lists as zero_when_absent (quick_ratio's inventory), and
only in `cells`: it never enters by_period_id / by_end_date, so no other metric reads it as zero.

Not wired into any calculator yet (plan step 5, behind the per-company shown_cell_path flag); until 0135 is applied the
view does not exist and nothing calls this. Annual (FY) and instant cells only: the display state has no quarter grain.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from scrooner_pipeline.metrics.provenance import InputCell

SHOWN_CELL_SQL = """select canonical_concept_id, concept_name, period_id, start_date, period_end, fiscal_period,
       period_type, cell_state, value, source_fact_ids, badge, proof_id
from analytics.shown_cell
where company_id = %s"""


def zero_when_absent_union() -> frozenset[str]:
    from scrooner_pipeline.metrics.generate import zero_when_absent_concepts

    return frozenset(c for cs in zero_when_absent_concepts().values() for c in cs)


def load_shown_cells(
    conn: Any, company_id: int, zero_when_absent: Iterable[str] | None = None
) -> dict:
    """The shape of calculate._load_canonical_facts (by_period_id, by_end_date, periods) over SHOWN cells only, plus
    `cells`: (concept_id, period_id) -> provenance.InputCell with status, value, proof id and badge."""
    zwa = (
        frozenset(zero_when_absent)
        if zero_when_absent is not None
        else zero_when_absent_union()
    )
    by_period_id: dict[int, dict[int, tuple]] = {}
    by_end_date: dict[int, dict] = {}
    periods: dict[int, tuple] = {}
    cells: dict[tuple[int, int], InputCell] = {}
    with conn.cursor() as cur:
        cur.execute(SHOWN_CELL_SQL, (company_id,))
        for (
            concept_id,
            name,
            period_id,
            start,
            end,
            fiscal_period,
            period_type,
            state,
            value,
            fact_ids,
            badge,
            proof_id,
        ) in cur.fetchall():
            if state == "value":
                by_period_id.setdefault(concept_id, {})[period_id] = (value, fact_ids)
                if period_type == "instant":
                    by_end_date.setdefault(concept_id, {})[end] = (value, fact_ids)
                cell = InputCell(
                    concept=name,
                    status="PROVEN",
                    value=value,
                    proof_id=proof_id,
                    badge=badge,
                )
            elif state == "not_presented" and name in zwa:
                cell = InputCell(
                    concept=name,
                    status="NOT_PRESENTED",
                    value=Decimal(0),
                    reason="not_presented",
                    proof_id=proof_id,
                )
            else:
                continue
            periods[period_id] = (start, end, fiscal_period)
            cells[(concept_id, period_id)] = cell
    return {
        "by_period_id": by_period_id,
        "by_end_date": by_end_date,
        "periods": periods,
        "cells": cells,
    }
