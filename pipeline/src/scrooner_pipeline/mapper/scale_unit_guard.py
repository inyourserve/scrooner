"""Scale and unit publish guard (E2, WO-27, RF-18 ``scale.unit_plausibility@1``): hide with a reason.

Two stored inputs carry values that are off by orders of magnitude:

* ``dividends_per_share`` (and ``_resolved``): a per-share dividend of 1,000 or more is a unit
  error, not a dividend (MOS: DPS 220,000 gives a dividend yield of 12,450 on the live page).
  The only per-share values at or above 1,000 are share prices of the Berkshire A class, which
  pays no dividend, so the bound hides no genuine DPS (negative control: AZO, NVR, BKNG, MELI, FICO
  pay none; Seaboard pays about 12; the guard keeps them all).
* ``public_float`` (``dei:EntityPublicFloat``): outside USD 1M to USD 10T is a scale error
  (DQC_0222, doc 21 section 8; eBay at 31 quintillion, ledger).

Hide = delete the canonical rows of the target concepts for that company and period, plus a
persisted reason (``analytics.cell_blank_reason``). Dependents (payout ratio, dividend yield,
dividend growth) then read a blank and carry their own null reason.

Flag ``scale.unit_plausibility@1`` (SCROONER_RULES_ENABLED), default OFF = no-op. Dry run writes
nothing. Live requires the reason store. Rollback: flag off, rerun the resolve stages for the
manifest ciks.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.cell_blank_reason import BlankReason, BlankReasonStore
from scrooner_pipeline.common.rule_before_image import PlannedChange
from scrooner_pipeline.common.rule_flags import rule_enabled as is_enabled

logger = structlog.get_logger()

RULE_ID = "scale.unit_plausibility@1"
DPS_MAX_ABS = Decimal(1000)
FLOAT_MIN = Decimal(1_000_000)
FLOAT_MAX = Decimal(10_000_000_000_000)

# concept family -> (concepts hidden together, reason code)
FAMILIES: dict[str, tuple[tuple[str, ...], str]] = {
    "dps": (("dividends_per_share", "dividends_per_share_resolved"), "dps_unit_error"),
    "public_float": (("public_float",), "public_float_scale_error"),
}


def implausible(family: str, value: Decimal) -> bool:
    if family == "dps":
        return abs(value) >= DPS_MAX_ABS
    if family == "public_float":
        return value < FLOAT_MIN or value > FLOAT_MAX
    raise KeyError(family)


_LOAD_SQL = """
select cf.company_id, cf.period_id, cc.name, cf.value, p.start_date, p.end_date, co.cik
from analytics.canonical_fact cf
join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id and cc.name = any(%(names)s)
join core.period p on p.id = cf.period_id
join core.company co on co.id = cf.company_id
where cf.company_id = any(%(ids)s)
"""


def _chunks(seq: list[Any], n: int) -> Iterable[list[Any]]:
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def _grain(start: date, end: date) -> str:
    if start == end:
        return "instant"
    days = (end - start).days + 1
    return "FY" if days >= 300 else ("Q" if days <= 105 else "YTD")


def apply_scale_unit_guard(
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
    all_names = sorted({n for names, _ in FAMILIES.values() for n in names})
    with conn.cursor() as cur:
        if ciks:
            cur.execute(
                "select id from core.company where cik = any(%s)", (sorted(ciks),)
            )
        else:
            cur.execute("select id from core.company order by id")
        company_ids = [r[0] for r in cur.fetchall()]
        cur.execute(
            "select id, name from analytics.canonical_concept where name = any(%s)",
            (all_names,),
        )
        concept_ids = {n: i for i, n in cur.fetchall()}
    totals: dict[str, Any] = {
        "companies": 0,
        "companies_with_hides": 0,
        "cells_hidden": 0,
        "dry_run": dry_run,
    }
    for fam in FAMILIES:
        totals[fam] = 0
    planned: list[PlannedChange] = []
    family_of = {n: f for f, (names, _) in FAMILIES.items() for n in names}
    for batch in _chunks(company_ids, chunk):
        with conn.cursor() as cur:
            cur.execute(_LOAD_SQL, {"names": all_names, "ids": batch})
            rows = cur.fetchall()
        by_company: dict[int, list[tuple[Any, ...]]] = defaultdict(list)
        for company_id, period_id, name, value, start, end, cik in rows:
            if implausible(family_of[name], value):
                by_company[company_id].append((period_id, name, value, start, end, cik))
        totals["companies"] += len(batch)
        for company_id, bad in by_company.items():
            totals["companies_with_hides"] += 1
            reasons: list[BlankReason] = []
            # a family hides all its concepts for the period when ANY of them is implausible
            hide_periods: dict[str, set[int]] = defaultdict(set)
            for period_id, name, value, start, end, cik in bad:
                fam = family_of[name]
                hide_periods[fam].add(period_id)
                totals[fam] += 1
                totals["cells_hidden"] += 1
                planned.append(
                    PlannedChange(
                        RULE_ID,
                        cik,
                        company_id,
                        name,
                        end,
                        value,
                        None,
                        f"guard_hidden:{FAMILIES[fam][1]}",
                    )
                )
                reasons.append(
                    BlankReason(
                        company_id,
                        name,
                        _grain(start, end),
                        start,
                        end,
                        "resolved",
                        RULE_ID,
                        FAMILIES[fam][1],
                        {"reason": FAMILIES[fam][1], "value": str(value)},
                    )
                )
            if dry_run:
                continue
            assert reason_store is not None
            reason_store.replace(company_id, RULE_ID, run_id or "adhoc", reasons)
            with conn.cursor() as cur:
                for fam, periods in hide_periods.items():
                    ids = [concept_ids[n] for n in FAMILIES[fam][0] if n in concept_ids]
                    cur.execute(
                        """delete from analytics.canonical_fact
                           where company_id = %s and canonical_concept_id = any(%s) and period_id = any(%s)""",
                        (company_id, ids, sorted(periods)),
                    )
            conn.commit()
    totals["planned"] = planned
    logger.info(
        "scale_unit_guard.done", **{k: v for k, v in totals.items() if k != "planned"}
    )
    return totals
