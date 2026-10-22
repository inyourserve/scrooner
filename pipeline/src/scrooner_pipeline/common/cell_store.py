"""Writer API for the stores created by migration 0100 (Gate A foundation F1).

- analytics.rule_run             manifest of every rule execution (dry run / apply / rollback)
- analytics.cell_blank_reason    why a cell has no value, run-scoped, keyed by dates
- analytics.cell_evidence        append-only durable evidence (never rewritten by a rebuild)
- core.filing_registrant         registrants of a filing, exactly one primary or all quarantined
- core.company_identity_audit    old/new value + accession for every identity edit

Rules this module enforces by construction:
- No function here deletes from cell_evidence or company_identity_audit (the
  triggers reject it too). delete_run_blank_reasons deletes ONLY the rows of
  one run_id, never by company or data point: the delete-scope bug that
  recurred five times in this project (pipeline/CLAUDE.md) cannot be written
  through this API.
- Functions never commit: the caller owns the transaction, so a guard stage
  can write its reasons and its canonical_fact change atomically.
- Inserts are chunked (5,000 rows) like every bulk write in the pipeline.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.common.cell_contract import (
    BLANK_STATES,
    EVIDENCE_KINDS,
    EVIDENCE_LEVELS,
    FLAG_STATES,
    REGISTRANT_ROLES,
    RUN_MODES,
    STATES,
    CellKey,
    parse_rule_id,
    validate_defect,
)

CHUNK = 5000


# --------------------------------------------------------------------------
# Rule-run manifest
# --------------------------------------------------------------------------
def start_rule_run(
    conn: psycopg.Connection,
    rule_id: str,
    mode: str,
    flag_state: str,
    ciks: Sequence[str],
    *,
    train: str | None = None,
    git_commit: str | None = None,
    before_image_ref: str | None = None,
) -> str:
    """Insert the manifest row and return its run_id (uuid as text). The flag
    name of a rule is its rule ID (freeze register 3.1)."""
    _, version = parse_rule_id(rule_id)
    if mode not in RUN_MODES:
        raise ValueError(f"unknown mode {mode!r}")
    if flag_state not in FLAG_STATES:
        raise ValueError(f"unknown flag_state {flag_state!r}")
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into analytics.rule_run
                (rule_id, rule_version, mode, flag_name, flag_state, train, ciks,
                 git_commit, before_image_ref)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning run_id::text
            """,
            (
                rule_id,
                version,
                mode,
                rule_id,
                flag_state,
                train,
                sorted(set(ciks)),
                git_commit,
                before_image_ref,
            ),
        )
        return cur.fetchone()[0]


def finish_rule_run(
    conn: psycopg.Connection, run_id: str, stats: dict[str, Any]
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "update analytics.rule_run set finished_at = now(), stats = %s::jsonb "
            "where run_id = %s::uuid",
            (json.dumps(stats, default=str, sort_keys=True), run_id),
        )
        if cur.rowcount != 1:
            raise LookupError(f"no rule_run {run_id}")


# --------------------------------------------------------------------------
# Blank reasons
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class BlankReason:
    key: CellKey
    state: str
    rule_id: str
    reason_code: str
    defect_class: str | None = None
    owner: str | None = None
    root_cause_class: str | None = None
    reason_text: str | None = None
    input_refs: dict[str, Any] = field(default_factory=dict)
    source_fact_ids: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in BLANK_STATES:
            raise ValueError(
                f"a blank reason carries one of {sorted(BLANK_STATES)}, got {self.state!r} "
                "(value and derived cells have a value, so no reason)"
            )
        parse_rule_id(self.rule_id)
        if not self.reason_code:
            raise ValueError("reason_code is required")
        validate_defect(
            self.state, self.defect_class, self.owner, self.root_cause_class
        )


def guard_hidden(
    key: CellKey,
    rule_id: str,
    reason_code: str,
    owner: str,
    *,
    root_cause_class: str | None = None,
    reason_text: str | None = None,
    input_refs: dict[str, Any] | None = None,
    source_fact_ids: Iterable[int] = (),
) -> BlankReason:
    """A value hidden by a Tier 0 guard is defect(guard_hidden, <family owner>)
    (register section 1), never not_presented."""
    return BlankReason(
        key=key,
        state="defect",
        rule_id=rule_id,
        reason_code=reason_code,
        defect_class="guard_hidden",
        owner=owner,
        root_cause_class=root_cause_class,
        reason_text=reason_text,
        input_refs=input_refs or {},
        source_fact_ids=tuple(source_fact_ids),
    )


_INSERT_REASON = """
insert into analytics.cell_blank_reason
    (run_id, company_id, data_point_name, period_grain, period_start, period_end, basis,
     state, defect_class, owner, root_cause_class, rule_id, reason_code, reason_text,
     input_refs, source_fact_ids)
values
    (%(run_id)s::uuid, %(company_id)s, %(data_point_name)s, %(period_grain)s,
     %(period_start)s, %(period_end)s, %(basis)s, %(state)s, %(defect_class)s, %(owner)s,
     %(root_cause_class)s, %(rule_id)s, %(reason_code)s, %(reason_text)s,
     %(input_refs)s::jsonb, %(source_fact_ids)s)
on conflict (run_id, company_id, data_point_name, period_grain, period_start, period_end, basis)
do update set
    state = excluded.state, defect_class = excluded.defect_class, owner = excluded.owner,
    root_cause_class = excluded.root_cause_class, rule_id = excluded.rule_id,
    reason_code = excluded.reason_code, reason_text = excluded.reason_text,
    input_refs = excluded.input_refs, source_fact_ids = excluded.source_fact_ids
"""


def write_blank_reasons(
    conn: psycopg.Connection, run_id: str, reasons: Iterable[BlankReason]
) -> int:
    """Insert (or, on a retried chunk of the same run, overwrite) reason rows
    of ONE run. Never deletes. Returns rows written."""
    batch: list[dict[str, Any]] = []
    written = 0
    for r in reasons:
        k = r.key
        batch.append(
            {
                "run_id": run_id,
                "company_id": k.company_id,
                "data_point_name": k.data_point_name,
                "period_grain": k.period_grain,
                "period_start": k.period_start,
                "period_end": k.period_end,
                "basis": k.basis,
                "state": r.state,
                "defect_class": r.defect_class,
                "owner": r.owner,
                "root_cause_class": r.root_cause_class,
                "rule_id": r.rule_id,
                "reason_code": r.reason_code,
                "reason_text": r.reason_text,
                "input_refs": json.dumps(r.input_refs, default=str, sort_keys=True),
                "source_fact_ids": list(r.source_fact_ids),
            }
        )
        if len(batch) >= CHUNK:
            written += _flush_reasons(conn, batch)
            batch = []
    if batch:
        written += _flush_reasons(conn, batch)
    return written


def _flush_reasons(conn: psycopg.Connection, batch: list[dict[str, Any]]) -> int:
    with conn.cursor() as cur:
        cur.executemany(_INSERT_REASON, batch)
    return len(batch)


def replace_rule_reasons(
    conn: psycopg.Connection,
    run_id: str,
    company_id: int,
    rule_id: str,
    reasons: Iterable[BlankReason],
) -> int:
    """A guard's per-company write: replace ONLY this rule's rows of this
    company in this run (delete scope = run + company + rule, never wider),
    then insert. Every reason must belong to that company and rule. Idempotent
    on retry; does not commit."""
    parse_rule_id(rule_id)
    batch = list(reasons)
    for r in batch:
        if r.key.company_id != company_id or r.rule_id != rule_id:
            raise ValueError(
                "reason outside the replace scope (company or rule differs)"
            )
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.cell_blank_reason "
            "where run_id = %s::uuid and company_id = %s and rule_id = %s",
            (run_id, company_id, rule_id),
        )
    return write_blank_reasons(conn, run_id, batch)


def delete_run_blank_reasons(conn: psycopg.Connection, run_id: str) -> int:
    """Discard the reasons of one run (a failed or superseded dry run). The
    only delete in this API; its scope is the run_id and nothing else."""
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.cell_blank_reason where run_id = %s::uuid", (run_id,)
        )
        return cur.rowcount


# --------------------------------------------------------------------------
# Evidence (append-only)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class EvidenceRecord:
    key: CellKey
    state_claimed: str
    rule_id: str
    evidence_kind: str
    evidence_level: str
    recorded_by: str
    accession: str | None = None
    locator: str | None = None
    detector_version: str | None = None
    source_hash: str | None = None

    def __post_init__(self) -> None:
        if self.state_claimed not in STATES:
            raise ValueError(f"unknown state_claimed {self.state_claimed!r}")
        parse_rule_id(self.rule_id)
        if self.evidence_kind not in EVIDENCE_KINDS:
            raise ValueError(f"unknown evidence_kind {self.evidence_kind!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise ValueError(f"unknown evidence_level {self.evidence_level!r}")
        if not self.recorded_by:
            raise ValueError("recorded_by is required")
        if self.evidence_kind == "filing_check":
            # Same rule as the table CHECK: a filing check cites its filing.
            if not (self.accession and self.locator):
                raise ValueError("a filing_check needs an accession and a locator")
            if self.evidence_level != "FILING-CHECKED":
                raise ValueError("a filing_check is FILING-CHECKED evidence")


_INSERT_EVIDENCE = """
insert into analytics.cell_evidence
    (company_id, data_point_name, period_grain, period_start, period_end, basis,
     state_claimed, rule_id, detector_version, evidence_kind, accession, locator,
     source_hash, evidence_level, recorded_by, import_key)
values
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
on conflict (import_key) do nothing
returning evidence_id
"""


def append_evidence(
    conn: psycopg.Connection, rec: EvidenceRecord, *, import_key: str | None = None
) -> int | None:
    """Append one evidence row; returns its evidence_id, or None when
    import_key was already loaded (idempotent JSONL reload)."""
    k = rec.key
    with conn.cursor() as cur:
        cur.execute(
            _INSERT_EVIDENCE,
            (
                k.company_id,
                k.data_point_name,
                k.period_grain,
                k.period_start,
                k.period_end,
                k.basis,
                rec.state_claimed,
                rec.rule_id,
                rec.detector_version,
                rec.evidence_kind,
                rec.accession,
                rec.locator,
                rec.source_hash,
                rec.evidence_level,
                rec.recorded_by,
                import_key,
            ),
        )
        row = cur.fetchone()
    return row[0] if row else None


def supersede_evidence(conn: psycopg.Connection, old_id: int, new_id: int) -> None:
    """Retire a wrong evidence row by pointing it at its replacement. This is
    the only mutation the table accepts (the trigger enforces it)."""
    with conn.cursor() as cur:
        cur.execute(
            "update analytics.cell_evidence set superseded_by = %s where evidence_id = %s",
            (new_id, old_id),
        )
        if cur.rowcount != 1:
            raise LookupError(f"no evidence row {old_id}")


# Interim file until the table is applied: one JSON object per line.
def evidence_to_jsonl_line(rec: EvidenceRecord) -> str:
    d = asdict(rec)
    key = d.pop("key")
    d.update(
        company_id=key["company_id"],
        data_point_name=key["data_point_name"],
        period_grain=key["period_grain"],
        period_start=key["period_start"].isoformat(),
        period_end=key["period_end"].isoformat(),
        basis=key["basis"],
    )
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def evidence_from_jsonl_line(line: str) -> EvidenceRecord:
    d = json.loads(line)
    key = CellKey(
        company_id=int(d.pop("company_id")),
        data_point_name=d.pop("data_point_name"),
        period_grain=d.pop("period_grain"),
        period_start=date.fromisoformat(d.pop("period_start")),
        period_end=date.fromisoformat(d.pop("period_end")),
        basis=d.pop("basis", "latest"),
    )
    return EvidenceRecord(
        key=key, **d
    )  # unknown fields raise TypeError: strict on purpose


def append_evidence_jsonl(path: Path, rec: EvidenceRecord) -> None:
    """Validate (constructing the record already did) and append one line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(evidence_to_jsonl_line(rec) + "\n")


def load_evidence_jsonl(conn: psycopg.Connection, path: Path) -> dict[str, int]:
    """Load the interim file verbatim. Idempotent: each line's sha256 is the
    import_key, so a second load inserts nothing. A malformed line aborts the
    load before any row is written (validate first, then insert)."""
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    parsed = [
        (hashlib.sha256(ln.encode()).hexdigest(), evidence_from_jsonl_line(ln))
        for ln in lines
    ]
    inserted = 0
    for import_key, rec in parsed:
        if append_evidence(conn, rec, import_key=import_key) is not None:
            inserted += 1
    return {
        "lines": len(parsed),
        "inserted": inserted,
        "skipped": len(parsed) - inserted,
    }


# --------------------------------------------------------------------------
# Filing registrants
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class RegistrantRow:
    registrant_cik: str
    role: str
    company_id: int | None = None

    def __post_init__(self) -> None:
        if self.role not in REGISTRANT_ROLES:
            raise ValueError(f"unknown role {self.role!r}")


def write_filing_registrants(
    conn: psycopg.Connection,
    accession_number: str,
    rows: Sequence[RegistrantRow],
    *,
    dei_default_cik: str | None,
    header_first_filer_cik: str | None,
    quarantine_reason: str | None = None,
) -> None:
    """Replace the registrant rows of ONE accession (delete scope = that
    accession). Invariant checked before any write: exactly one primary and
    no quarantined row, or every row quarantined with a reason."""
    if not rows:
        raise ValueError("an accession has at least one registrant")
    roles = [r.role for r in rows]
    if len({r.registrant_cik for r in rows}) != len(rows):
        raise ValueError("duplicate registrant CIK in one accession")
    if "quarantined" in roles:
        if set(roles) != {"quarantined"} or not quarantine_reason:
            raise ValueError(
                "a quarantined accession has only quarantined rows and a reason"
            )
    else:
        if roles.count("primary") != 1:
            raise ValueError(
                "a non-quarantined accession has exactly one primary registrant"
            )
        if quarantine_reason:
            raise ValueError("quarantine_reason only with role quarantined")
    with conn.cursor() as cur:
        cur.execute(
            "delete from core.filing_registrant where accession_number = %s",
            (accession_number,),
        )
        cur.executemany(
            """
            insert into core.filing_registrant
                (accession_number, registrant_cik, company_id, role, dei_default_cik,
                 header_first_filer_cik, filer_count, quarantine_reason)
            values (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    accession_number,
                    r.registrant_cik,
                    r.company_id,
                    r.role,
                    dei_default_cik,
                    header_first_filer_cik,
                    len(rows),
                    quarantine_reason if r.role == "quarantined" else None,
                )
                for r in rows
            ],
        )


# --------------------------------------------------------------------------
# Identity audit
# --------------------------------------------------------------------------
def record_identity_audit(
    conn: psycopg.Connection,
    *,
    company_id: int,
    field_name: str,
    old_value: str | None,
    new_value: str | None,
    rule_id: str,
    evidence_level: str,
    accession: str | None = None,
    locator: str | None = None,
    run_id: str | None = None,
) -> int:
    """One row per identity edit; call it in the same transaction as the edit."""
    parse_rule_id(rule_id)
    if old_value == new_value:
        raise ValueError("an audit row records a change: old_value equals new_value")
    if evidence_level not in EVIDENCE_LEVELS:
        raise ValueError(f"unknown evidence_level {evidence_level!r}")
    if evidence_level == "FILING-CHECKED" and not (accession and locator):
        raise ValueError(
            "FILING-CHECKED identity evidence cites an accession and a locator"
        )
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into core.company_identity_audit
                (company_id, field, old_value, new_value, accession, locator,
                 evidence_level, rule_id, run_id)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s::uuid)
            returning id
            """,
            (
                company_id,
                field_name,
                old_value,
                new_value,
                accession,
                locator,
                evidence_level,
                rule_id,
                run_id,
            ),
        )
        return cur.fetchone()[0]


def mark_identity_audit_reversed(conn: psycopg.Connection, audit_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "update core.company_identity_audit set reversed_at = now() where id = %s",
            (audit_id,),
        )
        if cur.rowcount != 1:
            raise LookupError(f"no audit row {audit_id}")


__all__ = [
    "BlankReason",
    "EvidenceRecord",
    "RegistrantRow",
    "append_evidence",
    "append_evidence_jsonl",
    "delete_run_blank_reasons",
    "evidence_from_jsonl_line",
    "evidence_to_jsonl_line",
    "finish_rule_run",
    "guard_hidden",
    "load_evidence_jsonl",
    "mark_identity_audit_reversed",
    "replace_rule_reasons",
    "record_identity_audit",
    "start_rule_run",
    "supersede_evidence",
    "write_blank_reasons",
    "write_filing_registrants",
]
