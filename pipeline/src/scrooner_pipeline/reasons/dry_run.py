"""Dry-run: cells closed per rule per cohort company, and the residue that is
still reasonless. Read-only; writes nothing to any database.

    python -m scrooner_pipeline.reasons.dry_run --out DIR [--no-db] [--per-company]

The baseline is the frozen 2026-10-20 scoreboard defect register (map v2.1,
cohort v1, 986 companies x 163 data points). Evidence for rules 2 and 3 is read
live from the database through one read-only connection; with --no-db those two
rules report NOT_RUN and close nothing.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path

from scrooner_pipeline.reasons.inputs import (
    Evidence,
    load_baseline,
    load_f1_removed,
    load_graph,
    load_groups,
    load_template,
)
from scrooner_pipeline.reasons.model import BaselineCell, CellKey, Closure
from scrooner_pipeline.reasons.rules import (
    RULE_ORDER,
    Audited,
    Context,
    reasonless_cells,
    run,
)


def build_context(evidence: Evidence, audited: Audited | None = None) -> Context:
    from scrooner_pipeline.mapper.calculate import ZERO_WHEN_ABSENT_CONCEPTS

    return Context(
        baseline=load_baseline(),
        groups=load_groups(),
        template=load_template(),
        graph=load_graph(),
        evidence=evidence,
        f1_removed=load_f1_removed(),
        zero_when_absent=ZERO_WHEN_ABSENT_CONCEPTS,
        audited=audited or Audited(),
    )


def summarize(ctx: Context, closed: Mapping[CellKey, Closure]) -> dict[str, object]:
    targets = reasonless_cells(ctx.baseline)
    by_rule: dict[str, Counter[str]] = {r: Counter() for r in RULE_ORDER}
    by_rule_dp: dict[str, Counter[str]] = {r: Counter() for r in RULE_ORDER}
    per_company: dict[int, Counter[str]] = defaultdict(Counter)
    for c in closed.values():
        kind = "pending" if c.is_pending else "state"
        by_rule[c.rule_id][kind] += 1
        by_rule[c.rule_id]["total"] += 1
        by_rule[c.rule_id][
            "as:"
            + (c.candidate_state or c.state)
            + ("" if c.is_pending else " (audited)")
        ] += 1
        by_rule_dp[c.rule_id][c.data_point] += 1
        per_company[c.company_id][c.rule_id] += 1
    residue = [b for b in targets if b.key not in closed]
    residue_dp = Counter(b.data_point for b in residue)
    return {
        "targets": len(targets),
        "closed": len(closed),
        "residue": residue,
        "residue_by_dp": residue_dp,
        "by_rule": by_rule,
        "by_rule_dp": by_rule_dp,
        "per_company": per_company,
    }


def write_outputs(
    out: Path,
    ctx: Context,
    closed: Mapping[CellKey, Closure],
    summary: dict[str, object],
) -> None:
    out.mkdir(parents=True, exist_ok=True)
    with (out / "closures.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "company_id",
                "ticker",
                "data_point",
                "rule_id",
                "state",
                "defect_class",
                "owner",
                "candidate_state",
                "wording_key",
                "candidate_wording_key",
                "evidence_level",
                "evidence_kind",
                "evidence_ref",
            ]
        )
        for k in sorted(closed):
            c = closed[k]
            w.writerow(
                [
                    c.company_id,
                    c.ticker,
                    c.data_point,
                    c.rule_id,
                    c.state,
                    c.defect_class or "",
                    c.owner or "",
                    c.candidate_state or "",
                    c.wording_key or "",
                    c.candidate_wording_key or "",
                    c.evidence_level,
                    c.evidence.get("kind", ""),
                    "; ".join(f"{a}={b}" for a, b in c.evidence.items() if a != "kind"),
                ]
            )
    residue: list[BaselineCell] = summary["residue"]  # type: ignore[assignment]
    with (out / "residue_reasonless.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["company_id", "ticker", "data_point", "kind"])
        for b in residue:
            w.writerow([b.company_id, b.ticker, b.data_point, b.kind])
    per_company: dict[int, Counter[str]] = summary["per_company"]  # type: ignore[assignment]
    tickers = {b.company_id: b.ticker for b in ctx.baseline.values()}
    resid_by_co = Counter(b.company_id for b in residue)
    start_by_co = Counter(b.company_id for b in reasonless_cells(ctx.baseline))
    with (out / "per_company.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "company_id",
                "ticker",
                "reasonless_before",
                *RULE_ORDER,
                "closed",
                "residue",
            ]
        )
        for cid in sorted(start_by_co):
            row = per_company.get(cid, Counter())
            w.writerow(
                [
                    cid,
                    tickers.get(cid, ""),
                    start_by_co[cid],
                    *[row[r] for r in RULE_ORDER],
                    sum(row.values()),
                    resid_by_co.get(cid, 0),
                ]
            )


def render(ctx: Context, summary: dict[str, object], per_company: bool) -> str:
    lines: list[str] = []
    by_rule: dict[str, Counter[str]] = summary["by_rule"]  # type: ignore[assignment]
    by_rule_dp: dict[str, Counter[str]] = summary["by_rule_dp"]  # type: ignore[assignment]
    lines.append(f"evidence source: {ctx.evidence.source}")
    lines.append(f"reasonless cells (baseline): {summary['targets']}")
    lines.append(
        f"closed by rules (all pending audit unless noted): {summary['closed']}"
    )
    lines.append(f"residue still reasonless: {len(summary['residue'])}")  # type: ignore[arg-type]
    lines.append("")
    lines.append(
        f"{'rule':28} {'total':>6} {'audited-state':>13} {'evidence_pending':>16}  top data points"
    )
    for r in RULE_ORDER:
        c = by_rule[r]
        top = ", ".join(f"{d} {n}" for d, n in by_rule_dp[r].most_common(5))
        lines.append(
            f"{r:28} {c['total']:>6} {c['state']:>13} {c['pending']:>16}  {top}"
        )
        for k, v in sorted(c.items()):
            if k.startswith("as:"):
                lines.append(f"{'':28}   {k[3:]}: {v}")
    lines.append("")
    lines.append("residue by data point (top 25):")
    for d, n in summary["residue_by_dp"].most_common(25):  # type: ignore[attr-defined]
        lines.append(f"  {n:>5}  {d}")
    if per_company:
        pc: dict[int, Counter[str]] = summary["per_company"]  # type: ignore[assignment]
        tick = {b.company_id: b.ticker for b in ctx.baseline.values()}
        start = Counter(b.company_id for b in reasonless_cells(ctx.baseline))
        res = Counter(b.company_id for b in summary["residue"])  # type: ignore[attr-defined]
        lines.append("")
        lines.append(
            f"{'ticker':8} {'before':>6} "
            + " ".join(
                f"{r.split('.')[0][:5] + '.' + r.split('.')[1][:5]:>11}"
                for r in RULE_ORDER
            )
            + f" {'residue':>7}"
        )
        for cid in sorted(start, key=lambda i: tick.get(i, "")):
            row = pc.get(cid, Counter())
            lines.append(
                f"{tick.get(cid, ''):8} {start[cid]:>6} "
                + " ".join(f"{row[r]:>11}" for r in RULE_ORDER)
                + f" {res.get(cid, 0):>7}"
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument(
        "--no-db", action="store_true", help="skip the read-only evidence queries"
    )
    ap.add_argument("--per-company", action="store_true")
    ap.add_argument("--max-backends", type=int, default=12)
    args = ap.parse_args(argv)

    evidence = Evidence(source="none (--no-db): rules 2 and 3 NOT_RUN")
    if not args.no_db:
        from scrooner_pipeline.reasons import db_evidence

        base = load_baseline()
        ids = sorted({b.company_id for b in base.values()})
        conn = db_evidence.connect_read_only(os.environ.get("DATABASE_URL"))
        try:
            n = db_evidence.check_backend_guard(conn, args.max_backends)
            print(
                f"application backends before ours: {n} (limit {args.max_backends})",
                file=sys.stderr,
            )
            evidence = db_evidence.load_evidence(conn, ids)
        finally:
            conn.rollback()
            conn.close()
    ctx = build_context(evidence)
    closed = run(ctx, RULE_ORDER)
    summary = summarize(ctx, closed)
    write_outputs(args.out, ctx, closed, summary)
    print(render(ctx, summary, args.per_company))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
