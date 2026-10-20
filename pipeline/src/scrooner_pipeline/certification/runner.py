"""Runs the invariant suite over a list of company ids, in chunks.

Read path: `loader.load_chunk` (SELECTs only, explicit statement_timeout each).
Write path (only with apply=True): delete-then-insert of a company's OPEN
findings plus an upsert of its company_certification row, one transaction per
chunk, only into the two certification tables of migration 0097. Without the
migration applied, `apply` refuses with `MigrationNotAppliedError` and a dry run
still works.
"""

from __future__ import annotations

import csv
import json
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Callable

import psycopg
import structlog

from scrooner_pipeline.common.sector_applicability import metric_suppression_reason

from . import (
    composition,
    currency,
    history,
    period_integrity,
    scale,
    sector,
    sign,
    source_integrity,
    splits,
    ties,
)
from .loader import HISTORY_FLOOR, Registry, load_chunk, load_registry
from .model import INFO, INVARIANTS, REVIEW, WRONG_VALUE, CompanyData, Finding

logger = structlog.get_logger()

MAX_CHUNK = 25
DEFAULT_TIMEOUT_S = 60
REPO_ROOT = Path(__file__).resolve().parents[4]
SHARDS_CSV = REPO_ROOT / "doc" / "data-moat" / "team" / "top1000" / "shards.csv"

CHECKS: tuple[Callable[[CompanyData], list[Finding]], ...] = (
    ties.check,
    sign.check,
    scale.check,
    period_integrity.check,
    source_integrity.check,
    currency.check,
    composition.check,
    splits.check,
    sector.check,
    history.check,
)


class MigrationNotAppliedError(RuntimeError):
    pass


@dataclass
class RunResult:
    findings: list[Finding] = field(default_factory=list)
    companies: dict[int, dict] = field(default_factory=dict)  # id -> {ticker, checked}
    errors: list[str] = field(default_factory=list)
    chunk_seconds: list[float] = field(default_factory=list)
    written: int = 0
    history: dict[int, dict] = field(
        default_factory=dict
    )  # company id -> history_matrix
    company_seconds: dict[int, float] = field(default_factory=dict)


def served_view(data: CompanyData) -> CompanyData:
    """Copy of `data` whose metrics are the ones a reader would see after the
    serve-time bank suppression: the sector check tests that path."""
    shown = [
        m
        for m in data.metrics
        if metric_suppression_reason(m.name, data.is_bank) is None
    ]
    return replace(data, metrics=shown)


def run_checks(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    for check in CHECKS:
        target = served_view(data) if check is sector.check else data
        out += check(target)
    seen: set[tuple] = set()
    unique: list[Finding] = []
    for f in out:
        k = (
            f.invariant,
            f.data_point_name,
            f.period_end,
            f.evidence.get("rule"),
            f.stored_value,
        )
        if k in seen:
            continue
        seen.add(k)
        unique.append(f)
    unique.sort(
        key=lambda f: (
            f.company_id,
            INVARIANTS.index(f.invariant),
            f.data_point_name,
            f.period_end or date.min,
        )
    )
    return unique


def chunks(ids: list[int], size: int) -> list[list[int]]:
    size = max(1, min(size, MAX_CHUNK))
    return [ids[i : i + size] for i in range(0, len(ids), size)]


def load_shard_company_ids(shard: str, path: Path = SHARDS_CSV) -> list[int]:
    """Company ids of a campaign shard (S001, ...). Rows marked `excluded` in
    shards.csv left the cohort and are skipped."""
    out: list[int] = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            if (
                row["shard"].strip().upper() == shard.strip().upper()
                and not (row.get("excluded") or "").strip()
            ):
                out.append(int(row["company_id"]))
    if not out:
        raise ValueError(f"no (non-excluded) companies for shard {shard!r} in {path}")
    return out


def tables_exist(cur) -> bool:
    cur.execute(
        "select to_regclass('analytics.certification_finding') is not null "
        "and to_regclass('analytics.company_certification') is not null"
    )
    return bool(cur.fetchone()[0])


def _json_default(o):
    if isinstance(o, (Decimal, date, datetime)):
        return str(o)
    raise TypeError(type(o))


INSERT_FINDING = """
    insert into analytics.certification_finding
        (company_id, invariant, severity, data_point_name, period_end, stored_value,
         expected_or_other_value, evidence, source_fact_ids, found_at)
    values (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
"""

UPSERT_CERTIFICATION = """
    insert into analytics.company_certification (company_id, state, checks_run_at, open_findings)
    values (%s, %s, %s, %s)
    on conflict (company_id) do update set
        checks_run_at = excluded.checks_run_at,
        open_findings = excluded.open_findings,
        state = case
            when excluded.state = 'uncertified' then 'uncertified'
            when analytics.company_certification.state = 'uncertified' then 'checks_clean'
            else analytics.company_certification.state
        end
"""


def is_blocking(f: Finding) -> bool:
    """What blocks `checks_clean` (decision 2026-10-21): a wrong_value finding, or an
    I11 missing cell nobody could classify. `review` and `info` do not block it
    (review blocks `certified`, which this tool never sets)."""
    return f.severity == WRONG_VALUE or (
        f.invariant == "I11" and f.evidence.get("classified") is False
    )


def company_state(findings: list[Finding]) -> str:
    return "uncertified" if any(is_blocking(f) for f in findings) else "checks_clean"


def storable(findings: list[Finding]) -> list[Finding]:
    """`info` findings are counted in the report but never written: the 0097 table
    allows only wrong_value and review."""
    return [f for f in findings if f.severity != INFO]


def apply_chunk(
    conn, company_ids: list[int], findings: list[Finding], now: datetime
) -> int:
    """Idempotent write of one chunk in ONE transaction: open findings of these
    companies are deleted and re-inserted, the certification rows upserted.
    Rows with resolved_at set are history and are never touched."""
    findings = storable(findings)
    by_company: dict[int, list[Finding]] = defaultdict(list)
    for f in findings:
        by_company[f.company_id].append(f)
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.certification_finding where company_id = any(%s) and resolved_at is null",
            (list(company_ids),),
        )
        cur.executemany(
            INSERT_FINDING,
            [
                (
                    f.company_id,
                    f.invariant,
                    f.severity,
                    f.data_point_name,
                    f.period_end,
                    f.stored_value,
                    f.expected_or_other_value,
                    json.dumps(f.evidence, default=_json_default),
                    f.source_fact_ids,
                    now,
                )
                for f in findings
            ],
        )
        cur.executemany(
            UPSERT_CERTIFICATION,
            [
                (
                    cid,
                    company_state(by_company.get(cid, [])),
                    now,
                    len(by_company.get(cid, [])),
                )
                for cid in company_ids
            ],
        )
    conn.commit()
    return len(findings)


def certify(
    conn,
    company_ids: list[int],
    *,
    chunk_size: int = MAX_CHUNK,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    since: date | None = HISTORY_FLOOR,
    apply: bool = False,
    progress: Callable[[str], None] | None = None,
) -> RunResult:
    """Run every invariant for `company_ids`. `conn` must be read-only for a dry
    run; with apply=True the two certification tables must exist."""
    result = RunResult()
    say = progress or (lambda _m: None)
    with conn.cursor() as cur:
        if apply and not tables_exist(cur):
            conn.rollback()
            raise MigrationNotAppliedError(
                "analytics.certification_finding / company_certification do not exist: "
                "migration 0097_certification_tables.sql is not applied. Refusing --apply; "
                "dry-run mode still works."
            )
        registry: Registry = load_registry(cur, timeout_s)
    conn.rollback()
    parts = chunks(company_ids, chunk_size)
    for n, part in enumerate(parts, start=1):
        started = time.monotonic()
        findings: list[Finding] = []
        loaded_ids: list[int] = []
        try:
            findings, loaded_ids = _check_ids(
                conn, part, registry, since, timeout_s, result
            )
        except psycopg.errors.QueryCanceled as exc:
            conn.rollback()
            result.errors.append(
                f"chunk {n}: statement_timeout ({timeout_s}s) on {part}: {exc}"
            )
            say(f"chunk {n}/{len(parts)}: TIMEOUT, retrying per company")
            for cid in part:
                try:
                    f, ok = _check_ids(conn, [cid], registry, since, timeout_s, result)
                    findings += f
                    loaded_ids += ok
                except psycopg.errors.QueryCanceled:
                    conn.rollback()
                    result.errors.append(
                        f"company {cid}: statement_timeout ({timeout_s}s), not checked"
                    )
        conn.rollback()
        result.findings += findings
        if apply and loaded_ids:
            result.written += apply_chunk(
                conn, loaded_ids, findings, datetime.now(timezone.utc)
            )
        result.chunk_seconds.append(time.monotonic() - started)
        say(
            f"chunk {n}/{len(parts)}: {len(loaded_ids)} companies, {len(findings)} findings, "
            f"{result.chunk_seconds[-1]:.1f}s"
        )
    return result


def _check_ids(
    conn, ids, registry, since, timeout_s, result
) -> tuple[list[Finding], list[int]]:
    with conn.cursor() as cur:
        data = load_chunk(cur, ids, registry, since=since, timeout_s=timeout_s)
    findings: list[Finding] = []
    for cid, d in data.items():
        t0 = time.monotonic()
        result.companies[cid] = {"ticker": d.ticker, "cells": len(d.cells)}
        findings += run_checks(d)
        result.history[cid] = history.history_matrix(d) if d.consumed else {}
        result.company_seconds[cid] = time.monotonic() - t0
    conn.rollback()
    return findings, list(data)


def summarize(result: RunResult) -> dict:
    by_inv: dict[str, Counter] = {i: Counter() for i in INVARIANTS}
    by_company: dict[int, Counter] = defaultdict(Counter)
    by_rule: Counter = Counter()
    for f in result.findings:
        by_inv[f.invariant][f.severity] += 1
        by_company[f.company_id][f.invariant] += 1
        by_rule[(f.invariant, f.evidence.get("rule"), f.severity)] += 1
    return {"by_invariant": by_inv, "by_company": by_company, "by_rule": by_rule}


def morning_summary(result: RunResult) -> dict:
    """One-command report: companies per state, wrong_value by invariant, and the
    I11 missing CELLS (not findings) by cause bucket. State is what --apply would
    write (`certified` is never set by this tool)."""
    by_company: dict[int, list[Finding]] = defaultdict(list)
    for f in result.findings:
        by_company[f.company_id].append(f)
    states: Counter = Counter(
        company_state(by_company.get(cid, [])) for cid in result.companies
    )
    wrong: Counter = Counter(
        f.invariant for f in result.findings if f.severity == WRONG_VALUE
    )
    sev: Counter = Counter(f.severity for f in result.findings)
    cells: dict[str, Counter] = {"concepts": Counter(), "metrics": Counter()}
    unclassified_by_kind: Counter = Counter()
    for h in result.history.values():
        for (base, kind, cause), ends in (h.get("missing") or {}).items():
            cells["concepts"][cause] += len(ends)
            if cause == "unclassified":
                unclassified_by_kind[("concept", kind)] += len(ends)
        for (name, kind, cause), ends in (h.get("missing_metrics") or {}).items():
            cells["metrics"][cause] += len(ends)
            if cause == "no_row":
                unclassified_by_kind[("metric", kind)] += len(ends)
    blocking_i11 = sum(
        1 for f in result.findings if f.invariant == "I11" and is_blocking(f)
    )
    return {
        "states": states,
        "wrong_by_invariant": wrong,
        "severity": sev,
        "i11_cells": cells,
        "unclassified_by_kind": unclassified_by_kind,
        "i11_blocking_findings": blocking_i11,
        "companies": len(result.companies),
    }


def render_summary(result: RunResult) -> str:
    m = morning_summary(result)
    lines = [
        f"SUMMARY ({m['companies']} companies checked)",
        "  state (certified is never set here): "
        + ", ".join(f"{k}={m['states'][k]}" for k in ("checks_clean", "uncertified")),
        "  rule: checks_clean = zero wrong_value AND zero unclassified I11 cells; review/info do not block it",
        "  findings by severity: "
        + ", ".join(f"{k}={v}" for k, v in sorted(m["severity"].items())),
        "  wrong_value by invariant: "
        + (
            ", ".join(
                f"{i}={m['wrong_by_invariant'][i]}"
                for i in INVARIANTS
                if m["wrong_by_invariant"][i]
            )
            or "none"
        ),
        "  I11 missing concept cells by cause:",
    ]
    for cause, n in m["i11_cells"]["concepts"].most_common():
        lines.append(f"    {cause:<28} {n}")
    lines.append("  I11 missing metric cells by cause:")
    for cause, n in m["i11_cells"]["metrics"].most_common(12):
        lines.append(f"    {cause:<28} {n}")
    lines.append(
        "  unclassified I11 cells by kind: "
        + (
            ", ".join(
                f"{k[0]}/{k[1]}={v}"
                for k, v in sorted(m["unclassified_by_kind"].items())
            )
            or "none"
        )
    )
    return "\n".join(lines)


def render_text(result: RunResult, show: int = 0, summary_only: bool = False) -> str:
    s = summarize(result)
    head = render_summary(result)
    if summary_only:
        return head
    lines = [head, "", "Findings per invariant (wrong_value / review / info):"]
    for inv in INVARIANTS:
        c = s["by_invariant"][inv]
        lines.append(f"  {inv:<4} {c[WRONG_VALUE]:>6} / {c['review']:<6} / {c['info']}")
    lines.append("")
    lines.append("Findings per rule:")
    for (inv, rule, sev), n in sorted(s["by_rule"].items()):
        lines.append(f"  {inv:<4} {rule:<45} {sev:<11} {n}")
    lines.append("")
    lines.append("Findings per company (ticker: invariant counts):")
    for cid, info in sorted(
        result.companies.items(), key=lambda kv: str(kv[1]["ticker"])
    ):
        counts = s["by_company"].get(cid, Counter())
        body = ", ".join(f"{i}={counts[i]}" for i in INVARIANTS if counts[i]) or "clean"
        lines.append(f"  {info['ticker'] or cid}: {body}")
    if show:
        lines.append("")
        lines.append(f"First {show} findings:")
        for f in result.findings[:show]:
            lines.append(
                f"  [{f.invariant}/{f.severity}] company {f.company_id} {f.data_point_name} "
                f"{f.period_end} stored={f.stored_value} other={f.expected_or_other_value} "
                f"rule={f.evidence.get('rule')}"
            )
    if any(result.history.values()):
        lines.append("")
        lines.append(render_history(result))
    if result.errors:
        lines.append("")
        lines.append("Errors:")
        lines += [f"  {e}" for e in result.errors]
    return "\n".join(lines)


HISTORY_YEARS = (2015, 2018, 2021, 2025)


def _cnt(counter, year: int, kinds: tuple[str, ...], what: str) -> int:
    return sum(counter.get((year, k, what), 0) for k in kinds)


def render_history(result: RunResult, years: tuple[int, ...] = HISTORY_YEARS) -> str:
    """I11 per company: present/expected cells per sampled year, annual (FY) and
    quarterly (Q + Q4), concepts then metrics; `u` = unclassified missing."""
    lines = ["I11 history completeness (present/expected, u = unclassified missing):"]
    for cid, info in sorted(
        result.companies.items(), key=lambda kv: str(kv[1]["ticker"])
    ):
        h = result.history.get(cid) or {}
        if not h:
            lines.append(f"  {info['ticker'] or cid}: no history data")
            continue
        for label, key in (("concepts", "concepts"), ("metrics", "metrics")):
            parts = []
            for y in years:
                for name, kinds in (("A", ("FY",)), ("Q", ("Q", "Q4"))):
                    e = _cnt(h[key], y, kinds, "expected")
                    parts.append(
                        f"{y}{name} {_cnt(h[key], y, kinds, 'present')}/{e} u{_cnt(h[key], y, kinds, 'unclassified')}"
                    )
            lines.append(f"  {info['ticker'] or cid} {label}: " + " | ".join(parts))
        lines.append(
            f"  {info['ticker'] or cid} seconds: {result.company_seconds.get(cid, 0):.2f}"
        )
    return "\n".join(lines)


def dump_json(result: RunResult, path: Path) -> None:
    rows = [
        {
            "company_id": f.company_id,
            "invariant": f.invariant,
            "severity": f.severity,
            "data_point_name": f.data_point_name,
            "period_end": f.period_end,
            "stored_value": f.stored_value,
            "expected_or_other_value": f.expected_or_other_value,
            "evidence": f.evidence,
            "source_fact_ids": f.source_fact_ids,
        }
        for f in result.findings
    ]
    path.write_text(json.dumps(rows, default=_json_default, indent=1))
