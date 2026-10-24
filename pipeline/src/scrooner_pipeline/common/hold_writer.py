"""The shared HOLD WRITER (rule ``holds.blank_writer@1``, flag OFF).

A planner (balance-sheet identity, total-debt guards, split basis, reason rules) that cannot produce a
trustworthy value emits a ``hold`` row. Until now the hold left the stored, known-wrong value in place. This
module turns a plan's holds into the final state of the cell:

  (a) a reason row through the 0100 contract (``cell_store``: analytics.cell_blank_reason, state ``defect``,
      class ``guard_hidden``, owner, root-cause class, a rule-specific ``reason_code``, ``input_refs`` = evidence);
  (b) the stored value is blanked by archive-then-remove (``mapper/canonical_archive``: the row is copied to
      analytics.canonical_fact_retired first, never hard deleted; ``rollback_run`` restores it) and a
      before-image JSONL is written first;
  (c) idempotent: a second run (same or a new run id) changes nothing, because only cells that still carry
      the planned stored value, or that have no reason yet, are pending;
  (d) scoped: one rule manifest per call, company by company, delete scope = run + company + rule.

``summarize`` is the dry-run: per producing rule id, how many stored values would be blanked and the size
distribution of those values (and of their ratio to a reference value when the plan carries one).

Modes (common/rule_flags, rule ``holds.blank_writer@1``): off = nothing, dry_run = summaries only, on = writes.
Only instants (grain ``I``) are supported; other grains raise, so a caller cannot blank the wrong cell.

Wiring: a planner calls ``sink(conn, holds, rule_id)`` with the holds it produced. ``holds_from_plan`` (identity
planner rows or their JSONL dicts) and ``holds_from_debt_plan`` (debt guard rows) adapt the two existing
planners; ``REASON_MAP`` is the mapping reason_code -> (state, defect class, owner, root cause).
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.common.cell_contract import CellKey, parse_rule_id
from scrooner_pipeline.common.rule_flags import DRY_RUN, ON, rule_mode
from scrooner_pipeline.mapper import canonical_archive as ca

WRITER_RULE = "holds.blank_writer@1"


@dataclass(frozen=True)
class ReasonSpec:
    state: str
    defect_class: str
    owner: str
    root_cause_class: str


def _guard(owner: str, root: str) -> ReasonSpec:
    return ReasonSpec("defect", "guard_hidden", owner, root)


# reason_code -> (state, defect class, owner, root cause). A value hidden by a guard is defect(guard_hidden, owner)
# (freeze register section 1); the root cause says which table class the family belongs to.
REASON_MAP: dict[str, ReasonSpec] = {
    # balance-sheet identity (balance.identity_equity_basis@1)
    "mixed_vintage": _guard("data_engineer_l1", "resolver"),
    "no_source_filing": _guard("data_engineer_l1", "resolver"),
    "identity_not_confirmed_by_face_subtotals": _guard(
        "standardization_lead", "composition"
    ),
    "nci_unconfirmed": _guard("standardization_lead", "composition"),
    "nci_not_read": _guard("standardization_lead", "composition"),
    "nci_on_unmapped_partnership_elements": _guard(
        "standardization_lead", "composition"
    ),
    "nci_inclusive_total_without_minority_interest": _guard(
        "standardization_lead", "composition"
    ),
    "nci_inclusive_total_disagrees_with_minority_interest": _guard(
        "standardization_lead", "composition"
    ),
    "redeemable_nci_measurement_only": _guard("standardization_lead", "composition"),
    "redeemable_nci_component_not_proven_on_face": _guard(
        "standardization_lead", "composition"
    ),
    "temporary_equity_generic_not_proven_on_face": _guard(
        "standardization_lead", "composition"
    ),
    "temporary_equity_generic_overlaps_redeemable_nci": _guard(
        "standardization_lead", "composition"
    ),
    "temporary_equity_present_not_read": _guard("data_engineer_l2", "ingestion"),
    # total debt (debt.total_debt_consistency@1): see debt_reason_code()
    "debt_current_block_unexplained": _guard("standardization_lead", "composition"),
    "debt_zero_with_nonzero_tag": _guard("data_engineer_l1", "composition"),
    "debt_below_instrument_tag": _guard("data_engineer_l1", "composition"),
    "debt_below_lease_inclusive_total": _guard("standardization_lead", "composition"),
    "debt_lease_location_unknown": _guard("standardization_lead", "composition"),
    "debt_short_term_overlap": _guard("standardization_lead", "composition"),
    "debt_borrowings_not_separable": _guard("standardization_lead", "composition"),
    "debt_related_party_unresolved": _guard("standardization_lead", "composition"),
    "debt_negative_component": _guard("data_engineer_l1", "composition"),
    "debt_partial_component": _guard("data_engineer_l1", "composition"),
}

# fragments of the debt guards' hold texts (mapper/concept_fallback.py REASON_*), most specific first
_DEBT_TEXT_TO_CODE: tuple[tuple[str, str], ...] = (
    ("is not explained by its filed parts", "debt_current_block_unexplained"),
    ("total would be 0 while a debt tag is nonzero", "debt_zero_with_nonzero_tag"),
    ("below a single filed debt instrument tag", "debt_below_instrument_tag"),
    ("below the filed lease-inclusive debt total", "debt_below_lease_inclusive_total"),
    (
        "cannot be placed inside or outside the current debt line",
        "debt_lease_location_unknown",
    ),
    ("several different short-term borrowing amounts", "debt_short_term_overlap"),
    ("borrowings cannot be separated", "debt_borrowings_not_separable"),
    ("related-party or debt-only current lines", "debt_related_party_unresolved"),
    ("a debt component is negative", "debt_negative_component"),
    ("only current debt portions are filed", "debt_partial_component"),
)


def debt_reason_code(text: str) -> str:
    for fragment, code in _DEBT_TEXT_TO_CODE:
        if fragment in text:
            return code
    raise ValueError(f"no hold reason code for the debt hold text {text!r}")


@dataclass(frozen=True)
class Hold:
    company_id: int
    data_point: str  # canonical concept name, e.g. total_liabilities_resolved
    period_end: date
    rule_id: str  # the PRODUCING rule (identity, debt, ...)
    reason_code: str
    stored_value: (
        Decimal | None
    )  # what the planner saw; the writer blanks only a row that still equals it
    source_fact_ids: tuple[int, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    reference_value: Decimal | None = None  # e.g. total assets, for the relative size
    reason_text: str | None = None
    period_grain: str = "I"
    basis: str = "latest"

    def __post_init__(self) -> None:
        parse_rule_id(self.rule_id)
        if self.reason_code not in REASON_MAP:
            raise ValueError(
                f"reason code {self.reason_code!r} has no entry in REASON_MAP"
            )
        if self.period_grain != "I":
            raise ValueError("the hold writer supports instants (grain I) only")

    @property
    def key(self) -> CellKey:
        return CellKey(
            self.company_id,
            self.data_point,
            "I",
            self.period_end,
            self.period_end,
            self.basis,
        )

    def reason(self) -> cs.BlankReason:
        spec = REASON_MAP[self.reason_code]
        return cs.BlankReason(
            key=self.key,
            state=spec.state,
            rule_id=self.rule_id,
            reason_code=self.reason_code,
            defect_class=spec.defect_class,
            owner=spec.owner,
            root_cause_class=spec.root_cause_class,
            reason_text=self.reason_text,
            input_refs=dict(self.evidence),
            source_fact_ids=self.source_fact_ids,
        )


# ------------------------------------------------------------------ adapters for the existing planners
def _get(row: Any, name: str, default: Any = None) -> Any:
    return (
        row.get(name, default)
        if isinstance(row, Mapping)
        else getattr(row, name, default)
    )


def holds_from_plan(
    rows: Iterable[Any], rule_id: str = "balance.identity_equity_basis@1"
) -> list[Hold]:
    """Identity-planner rows (objects or JSONL dicts) with kind == 'hold'."""
    out = []
    for r in rows:
        if _get(r, "kind") != "hold":
            continue
        before = _get(r, "before")
        out.append(
            Hold(
                company_id=int(_get(r, "company_id")),
                data_point=_get(r, "concept"),
                period_end=date.fromisoformat(str(_get(r, "period_end"))),
                rule_id=rule_id,
                reason_code=_get(r, "basis"),
                stored_value=None if before is None else Decimal(str(before)),
                source_fact_ids=tuple(_get(r, "source_fact_ids") or ()),
                evidence={
                    k: v
                    for k, v in (
                        ("filing_id", _get(r, "filing_id")),
                        ("equity_tag", _get(r, "equity_tag")),
                    )
                    if v is not None
                },
            )
        )
    return out


def holds_from_debt_plan(
    rows: Iterable[Any], rule_id: str = "debt.total_debt_consistency@1"
) -> list[Hold]:
    """Debt dry-run rows (concept_fallback PlannedChange) whose value would be blank (after is None)."""
    out = []
    for r in rows:
        if _get(r, "after") is not None:
            continue
        text = str(_get(r, "reason") or "")
        if "hold=" not in text:
            continue
        before = _get(r, "before")
        out.append(
            Hold(
                company_id=int(_get(r, "company_id")),
                data_point=_get(r, "data_point", "total_debt_resolved"),
                period_end=date.fromisoformat(str(_get(r, "period_end"))),
                rule_id=rule_id,
                reason_code=debt_reason_code(text),
                stored_value=None if before is None else Decimal(str(before)),
                reason_text=text.split("hold=", 1)[1],
                evidence={"guards": text.split(":hold=", 1)[0]},
            )
        )
    return out


# ------------------------------------------------------------------ dry run
MAGNITUDE_BUCKETS = (
    ("<1M", Decimal(10) ** 6),
    ("1M-100M", Decimal(10) ** 8),
    ("100M-1B", Decimal(10) ** 9),
    ("1B-10B", Decimal(10) ** 10),
    ("10B-100B", Decimal(10) ** 11),
    (">=100B", Decimal("Infinity")),
)
RATIO_BUCKETS = (("<1%", Decimal("0.01")), ("1-10%", Decimal("0.1")), ("10-50%", Decimal("0.5")), ("50-100%", Decimal(1)), (">=100%", Decimal("Infinity")))  # fmt: skip


def _bucket(x: Decimal, buckets: tuple[tuple[str, Decimal], ...]) -> str:
    for name, bound in buckets:
        if x < bound:
            return name
    return buckets[-1][0]


def _stored_now(
    conn: Any, holds: list[Hold]
) -> dict[tuple[int, str, date], tuple[int, Decimal]]:
    """(company, data point, end date) -> (canonical_fact id, value) of the stored instant rows, read-only."""
    out: dict[tuple[int, str, date], tuple[int, Decimal]] = {}
    by_company: dict[int, list[Hold]] = defaultdict(list)
    for h in holds:
        by_company[h.company_id].append(h)
    with conn.cursor() as cur:
        for cid, group in by_company.items():
            cur.execute(
                """select cf.id, cc.name, p.end_date, cf.value
                   from analytics.canonical_fact cf
                   join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
                   join core.period p on p.id = cf.period_id
                   where cf.company_id = %s and p.period_type = 'instant'
                     and cc.name = any(%s) and p.end_date = any(%s)""",
                (
                    cid,
                    sorted({h.data_point for h in group}),
                    sorted({h.period_end for h in group}),
                ),
            )
            for fid, name, end, val in cur.fetchall():
                out[(cid, name, end)] = (fid, val)
    return out


def summarize(conn: Any, holds: list[Hold]) -> dict[str, dict[str, Any]]:
    """Per producing rule id: holds, would_blank (a stored row that still equals the planned value), already
    blank, changed since the plan, and the size distribution of the values that would be blanked. Read-only."""
    stored = _stored_now(conn, holds)
    out: dict[str, dict[str, Any]] = {}
    for h in holds:
        s = out.setdefault(
            h.rule_id,
            {"holds": 0, "would_blank": 0, "already_blank": 0, "changed_since_plan": 0,
             "by_reason": Counter(), "magnitude": Counter(), "relative_to_reference": Counter()},
        )  # fmt: skip
        s["holds"] += 1
        row = stored.get((h.company_id, h.data_point, h.period_end))
        if row is None:
            s["already_blank"] += 1
        elif h.stored_value is not None and row[1] != h.stored_value:
            s["changed_since_plan"] += 1
        else:
            s["would_blank"] += 1
            s["by_reason"][h.reason_code] += 1
            s["magnitude"][_bucket(abs(row[1]), MAGNITUDE_BUCKETS)] += 1
            if h.reference_value:
                s["relative_to_reference"][
                    _bucket(abs(row[1]) / abs(h.reference_value), RATIO_BUCKETS)
                ] += 1
    return out


def format_summary(summary: dict[str, dict[str, Any]]) -> str:
    lines = []
    for rule_id, s in sorted(summary.items()):
        lines.append(
            f"{rule_id}: holds={s['holds']} would_blank={s['would_blank']} already_blank={s['already_blank']} "
            f"changed_since_plan={s['changed_since_plan']}"
        )
        lines.append(
            "  by reason: "
            + ", ".join(f"{k}={v}" for k, v in s["by_reason"].most_common())
        )
        lines.append(
            "  value size: "
            + ", ".join(f"{n}={s['magnitude'].get(n, 0)}" for n, _ in MAGNITUDE_BUCKETS)
        )
        if s["relative_to_reference"]:
            lines.append(
                "  vs reference: "
                + ", ".join(
                    f"{n}={s['relative_to_reference'].get(n, 0)}"
                    for n, _ in RATIO_BUCKETS
                )
            )
    return "\n".join(lines)


# ------------------------------------------------------------------ apply
def _existing_reasons(
    conn: Any, company_id: int, rule_id: str, holds: list[Hold]
) -> set[tuple[str, date, str]]:
    with conn.cursor() as cur:
        cur.execute(
            """select data_point_name, period_end, reason_code from analytics.cell_blank_reason
               where company_id = %s and rule_id = %s and period_grain = 'I' and basis = 'latest'
                 and data_point_name = any(%s) and period_end = any(%s)""",
            (
                company_id,
                rule_id,
                sorted({h.data_point for h in holds}),
                sorted({h.period_end for h in holds}),
            ),
        )
        return {(n, e, c) for n, e, c in cur.fetchall()}


def apply_holds(
    conn: Any,
    holds: list[Hold],
    *,
    before_image: Path,
    git_commit: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Blank the stored values of the holds and write their reasons. Requires rule ``holds.blank_writer@1`` ON.
    One rule_run manifest (the writer's), reasons carry the producing rule id; commits per company."""
    if rule_mode(WRITER_RULE, environ if environ is not None else os.environ) != ON:
        raise PermissionError(f"{WRITER_RULE} is not ON; refusing to write")
    stats: dict[str, Any] = {
        "blanked": 0,
        "reasons_written": 0,
        "skipped_changed": 0,
        "skipped_done": 0,
        "companies": 0,
    }
    if not holds:
        return stats
    ciks = _ciks(conn, {h.company_id for h in holds})
    run_id = cs.start_rule_run(
        conn,
        WRITER_RULE,
        "apply",
        "on",
        ciks,
        git_commit=git_commit,
        before_image_ref=str(before_image),
    )
    conn.commit()
    by_company: dict[int, list[Hold]] = defaultdict(list)
    for h in holds:
        by_company[h.company_id].append(h)
    with before_image.open("a") as image:
        for cid, group in sorted(by_company.items()):
            try:
                _apply_company(conn, cid, group, run_id, image, stats)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            stats["companies"] += 1
    cs.finish_rule_run(conn, run_id, stats)
    conn.commit()
    stats["run_id"] = run_id
    return stats


def _ciks(conn: Any, company_ids: set[int]) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select cik from core.company where id = any(%s)", (sorted(company_ids),)
        )
        return [r[0] for r in cur.fetchall()]


def _apply_company(
    conn: Any,
    cid: int,
    group: list[Hold],
    run_id: str,
    image: Any,
    stats: dict[str, Any],
) -> None:
    stored = _stored_now(conn, group)
    by_rule: dict[str, list[Hold]] = defaultdict(list)
    for h in group:
        by_rule[h.rule_id].append(h)
    to_remove: list[int] = []
    for rule_id, rule_holds in by_rule.items():
        done = _existing_reasons(conn, cid, rule_id, rule_holds)
        pending: list[Hold] = []
        for h in rule_holds:
            row = stored.get((cid, h.data_point, h.period_end))
            if (
                row is not None
                and h.stored_value is not None
                and row[1] != h.stored_value
            ):
                stats["skipped_changed"] += (
                    1  # the cell moved since the plan: not blanked, not explained
                )
                continue
            if row is None and (h.data_point, h.period_end, h.reason_code) in done:
                stats["skipped_done"] += 1  # blanked and explained by an earlier run
                continue
            pending.append(h)
            if row is not None:
                to_remove.append(row[0])
                image.write(
                    json.dumps(
                        {"run_id": run_id, "rule_id": rule_id, "company_id": cid, "data_point": h.data_point,
                         "period_end": str(h.period_end), "canonical_fact_id": row[0], "stored_value": str(row[1]),
                         "reason_code": h.reason_code}, sort_keys=True,
                    ) + "\n"
                )  # fmt: skip
        image.flush()
        if pending:
            # earlier-run reasons of other cells are not touched: the delete scope is run + company + rule
            stats["reasons_written"] += cs.replace_rule_reasons(
                conn, run_id, cid, rule_id, [h.reason() for h in pending]
            )
    if to_remove:
        with conn.cursor() as cur:
            stats["blanked"] += ca.archive_and_remove(
                cur,
                to_remove,
                reason_code="hold_writer_blank",
                run_id=run_id,
                basis_version=WRITER_RULE,
            )


def rollback_run(conn: Any, run_id: str) -> dict[str, int]:
    """Undo one apply: restore the archived canonical_fact rows and discard the run's reasons."""
    with conn.cursor() as cur:
        restored = ca.restore_run(cur, run_id)
    discarded = cs.delete_run_blank_reasons(conn, run_id)
    conn.commit()
    return {"restored": restored, "reasons_discarded": discarded}


# ------------------------------------------------------------------ the optional sink planners call
def sink(
    conn: Any,
    holds: list[Hold],
    *,
    before_image: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any] | None:
    """off -> None (legacy behavior: the hold leaves the stored value); dry_run -> the printed summary;
    on -> apply_holds. A planner calls this with the holds it produced."""
    env = environ if environ is not None else os.environ
    mode = rule_mode(WRITER_RULE, env)
    if mode == DRY_RUN:
        summary = summarize(conn, holds)
        print(format_summary(summary))
        return {"summary": summary}
    if mode == ON:
        path = (
            before_image
            or Path(env.get("SCROONER_BEFORE_IMAGE_DIR", "."))
            / "hold_writer_before_image.jsonl"
        )
        return apply_holds(conn, holds, before_image=path, environ=env)
    return None
