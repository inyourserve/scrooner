"""Hide the ten total-debt consumers with "definition pending accountant review" until AC-1 is answered.

Decision card DC-TOTAL-DEBT-LEASE-PERIMETER-2026-10-24 section 4.2: the stored values of the metrics below
were wrong in 37 of 37 checked cells and need ONE cross-company lease perimeter that the accountant (AC-1)
has not yet chosen. They are therefore hidden, not published on a guessed perimeter.

Effect of a live run (flag ``debt.metrics_pending_ac1@1``, default OFF): for the listed metrics the stored value
becomes NULL with ``is_null_reason`` = REASON_TEXT, and a reason row is persisted for each cell
(state ``defect``, defect class ``definition_pending``, owner ``accountant``, code ``debt_perimeter_ac1_pending``).
Run it AFTER the metric stages (the nightly metric stages rewrite metric_value). Dry run writes nothing.
Reversal: flag off and recompute the metric stages for the manifest ciks.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.cell_blank_reason import BlankReason, BlankReasonStore
from scrooner_pipeline.common.rule_before_image import PlannedChange
from scrooner_pipeline.common.rule_flags import rule_enabled as is_enabled

logger = structlog.get_logger()

RULE_ID = "debt.metrics_pending_ac1@1"
REASON_TEXT = "definition pending accountant review"
REASON_CODE = "debt_perimeter_ac1_pending"
METRICS = (
    "debt_to_equity",
    "net_cash",
    "net_cash_per_share",
    "net_debt_ebitda",
    "debt_to_ebitda",
    "ev_ebitda",
    "ev_sales",
    "roic",
    "piotroski_f_score",
    "zero_debt",
)
_LOAD_SQL = """
select mv.id, mv.company_id, md.metric_name, mv.period_label, mv.period_start, mv.period_end, mv.value
from analytics.metric_value mv
join analytics.metric_definition md on md.id = mv.metric_definition_id
where mv.company_id = any(%(ids)s) and md.metric_name = any(%(names)s) and mv.value is not null
"""


def grain(label: str) -> str:
    return label if label in ("FY", "TTM") else "Q"


def _chunks(seq: list[Any], n: int) -> Iterable[list[Any]]:
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def apply_debt_metrics_pending(
    conn: psycopg.Connection,
    ciks: set[str] | None = None,
    *,
    dry_run: bool = False,
    reason_store: BlankReasonStore | None = None,
    run_id: str | None = None,
    environ: dict[str, str] | None = None,
    chunk: int = 100,
) -> dict[str, Any]:
    live = is_enabled(RULE_ID, environ) and not dry_run
    if not live and not dry_run:
        return {"skipped": "rule_off", "planned": []}
    if live and reason_store is None:
        raise RuntimeError(
            f"{RULE_ID}: a reason store is required to hide cells (migration 0100)"
        )
    with conn.cursor() as cur:
        if ciks:
            cur.execute(
                "select id, cik from core.company where cik = any(%s)", (sorted(ciks),)
            )
        else:
            cur.execute("select id, cik from core.company order by id")
        companies = cur.fetchall()
    totals: dict[str, Any] = {
        "companies": 0,
        "companies_hidden": 0,
        "cells_hidden": 0,
        "dry_run": dry_run,
    }
    for name in METRICS:
        totals[name] = 0
    planned: list[PlannedChange] = []
    for batch in _chunks(companies, chunk):
        cik_by_id = dict(batch)
        with conn.cursor() as cur:
            cur.execute(_LOAD_SQL, {"ids": list(cik_by_id), "names": list(METRICS)})
            rows = cur.fetchall()
        by_company: dict[int, list[tuple[Any, ...]]] = {}
        for r in rows:
            by_company.setdefault(r[1], []).append(r)
        totals["companies"] += len(batch)
        for company_id, cells in by_company.items():
            totals["companies_hidden"] += 1
            reasons: list[BlankReason] = []
            for _id, _cid, name, label, start, end, value in cells:
                totals[name] += 1
                totals["cells_hidden"] += 1
                planned.append(
                    PlannedChange(
                        RULE_ID,
                        cik_by_id[company_id],
                        company_id,
                        name,
                        end,
                        value,
                        None,
                        REASON_CODE,
                    )
                )
                reasons.append(
                    BlankReason(
                        company_id,
                        name,
                        grain(label) if start != end else "I",
                        start,
                        end,
                        "latest",
                        RULE_ID,
                        REASON_CODE,
                        {"label": label, "text": REASON_TEXT},
                        owner="accountant",
                        defect_class="definition_pending",
                    )
                )
            if dry_run:
                continue
            assert reason_store is not None
            reason_store.replace(company_id, RULE_ID, run_id or "adhoc", reasons)
            with conn.cursor() as cur:
                cur.execute(
                    """update analytics.metric_value set value = null, is_null_reason = %s
                       where id = any(%s)""",
                    (REASON_TEXT, [c[0] for c in cells]),
                )
            conn.commit()
    totals["planned"] = planned
    logger.info(
        "debt_metrics_pending.done",
        **{k: v for k, v in totals.items() if k != "planned"},
    )
    return totals
