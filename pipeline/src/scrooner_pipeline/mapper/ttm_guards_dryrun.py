"""Read-only dry-run of RF-01 (ttm.consecutive_window@1) and RF-02 (ttm.age_guard@1).

Nothing here writes to the database: the session is opened with
`default_transaction_read_only=on`, one connection, an explicit
`statement_timeout`, chunks of at most 100 company ids. It reads the stored
`analytics.metric_value` quarter rows (ebitda, fcf) and `analytics.canonical_fact`
quarter periods (share_buybacks, dividends_paid, revenue), applies the same pure
functions the metric stage uses (`ttm_guards`), and writes one CSV row per
affected cell plus a JSON summary. That CSV is the "reviewed dry-run of proposed
writes" the Release Manager's procedure requires before any live run.

Usage (from pipeline/, DATABASE_URL in .env or the environment):

  python -m scrooner_pipeline.mapper.ttm_guards_dryrun \
      --tickers MTZ,AAL,APD,COST --out /tmp/w1w2_named.csv --summary /tmp/w1w2_named.json

  # population (a chunked scan: run in a quiet window, never beside a heavy job)
  python -m scrooner_pipeline.mapper.ttm_guards_dryrun --all --chunk 50 \
      --out /tmp/w1w2_all.csv --summary /tmp/w1w2_all.json

Cells counted as "affected" are the consumers whose latest stored TTM row has a
non-null value today: those are the values that would turn into a visible blank.
The dry-run cannot tell whether a hidden TTM was "right by luck"; it reports the
failure class so the Verifier can sample each one against the filings.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

from scrooner_pipeline.common.staleness import load_latest_filed_periods
from scrooner_pipeline.mapper import ttm_guards
from scrooner_pipeline.mapper.price_metrics import _latest_quarter, _trailing_quarters
from scrooner_pipeline.mapper.rule_flags import (
    RF01_CONSECUTIVE_WINDOW,
    RF02_AGE_GUARD,
    RF_TSY_STALE,
    RF_TSY_UNEVIDENCED_ZERO,
)

# Consumers per guarded data point, from data-team/strategy/data/metric_dependency_graph.csv.
WINDOW_CONSUMERS = {
    "ebitda": (
        "ebitda",
        "net_debt_ebitda",
        "ebitda_margin",
        "debt_to_ebitda",
        "ev_ebitda",
    ),
    "fcf": ("fcf_per_share", "share_repurchases_pct_fcf", "dividends_pct_fcf"),
}
AGE_CONSUMERS = {
    "share_buybacks": (
        "buyback_yield",
        "share_repurchases_pct_fcf",
        "total_shareholder_yield",
    ),
    "dividends_paid": ("dividends_pct_fcf", "total_shareholder_yield"),
}
# Same value as expanded_metrics.TTM_STALENESS_THRESHOLD_DAYS (existing guard).
LEGACY_STALENESS_DAYS = 150
CHUNK_MAX = 100

CSV_FIELDS = [
    "rule_id",
    "company_id",
    "ticker",
    "data_point",
    "outcome",
    "failure_class",
    "old_ttm",
    "new_ttm",
    "anchor_end",
    "reference_end",
    "lag_days",
    "window_ends",
    "detail",
    "displayed_cells_now",
    "displayed_cells_list",
]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    company_id: int
    data_point: str
    outcome: str  # hidden | changed
    failure_class: str
    old_ttm: Decimal | None
    new_ttm: Decimal | None
    anchor_end: date | None
    reference_end: date | None
    lag_days: int | None
    window_ends: str
    detail: str


def evaluate_window(
    company_id: int,
    data_point: str,
    rows: list[ttm_guards.QuarterRow],
    today: date,
) -> Finding | None:
    """RF-01 for one company/data point. None when there is no legacy TTM to
    guard (fewer than 4 rows or the existing 150-day staleness guard already
    blanks it) or when the guard changes nothing."""
    ordered = sorted(rows, key=lambda r: r.end, reverse=True)
    legacy = ttm_guards.legacy_total(ordered)
    if legacy is None or (today - ordered[0].end).days > LEGACY_STALENESS_DAYS:
        return None
    decision = ttm_guards.contiguous_ttm_window(ordered[:12])
    ends = ",".join(str(r.end) for r in ordered[:4])
    if not decision.ok:
        return Finding(
            RF01_CONSECUTIVE_WINDOW,
            company_id,
            data_point,
            "hidden",
            decision.failure or "",
            legacy,
            None,
            ordered[0].end,
            None,
            None,
            ends,
            decision.detail,
        )
    if decision.total != legacy:
        return Finding(
            RF01_CONSECUTIVE_WINDOW,
            company_id,
            data_point,
            "changed",
            "contiguous_window_differs",
            legacy,
            decision.total,
            ordered[0].end,
            None,
            None,
            ends,
            "",
        )
    return None


def label_ttm(
    by_key: dict[tuple[int, str], tuple[Decimal, date, date]],
) -> tuple[Decimal | None, tuple[int, str] | None]:
    """The stage's label-based TTM (price_metrics._ttm_sum semantics) and its anchor."""
    anchor = _latest_quarter(by_key)
    if anchor is None:
        return None, None
    total = Decimal(0)
    for key in _trailing_quarters(*anchor):
        hit = by_key.get(key)
        if hit is None:
            return None, anchor
        total += hit[0]
    return total, anchor


def evaluate_age(
    company_id: int,
    data_point: str,
    by_key: dict[tuple[int, str], tuple[Decimal, date, date]] | None,
    expected_end: date | None,
    tolerance_days: int = ttm_guards.EXPECTED_PERIOD_TOLERANCE_DAYS,
) -> tuple[Finding | None, ttm_guards.Component]:
    """RF-02 v2 for one company/concept against the EXPECTED period (latest
    periodic filing's period end). Returns the finding (hidden only) and the
    component state, which the composite check and the lag histogram use."""
    ttm, anchor = label_ttm(by_key) if by_key else (None, None)
    anchor_end = by_key[anchor][2] if ttm is not None and anchor and by_key else None
    comp = ttm_guards.component(
        data_point, ttm, anchor_end, expected_end, tolerance_days
    )
    if comp.status not in (ttm_guards.STALE, ttm_guards.NO_REFERENCE):
        return None, comp
    detail = (
        f"anchor {anchor_end} vs expected {expected_end}: {comp.lag_days} days behind"
        if comp.status == ttm_guards.STALE
        else f"anchor {anchor_end}: no periodic filing period end for the company"
    )
    return (
        Finding(
            RF02_AGE_GUARD,
            company_id,
            data_point,
            "hidden",
            "anchor_not_at_expected_period"
            if comp.status == ttm_guards.STALE
            else "no_expected_period",
            ttm,
            None,
            anchor_end,
            expected_end,
            comp.lag_days,
            "",
            detail,
        ),
        comp,
    )


def evaluate_composite(
    company_id: int, components: list[ttm_guards.Component]
) -> list[Finding]:
    """total_shareholder_yield, counted per RULE (they are separate flags):
    tsy.stale_component@1 = a stale component or windows that do not end together;
    composite.unknown_not_zero@1 (RF-08 applied to TSY) = a component with no TTM
    at all (priced as 0 today); hidden as "zero not proven" in the R2 train."""
    d = ttm_guards.composite_decision(company_id, components)
    out = []
    if d.stale_reason:
        classes = [
            c
            for c, on in (
                ("stale_component", d.stale),
                ("misaligned_windows", d.misaligned),
            )
            if on
        ]
        out.append(
            Finding(
                RF_TSY_STALE,
                company_id,
                "total_shareholder_yield",
                "hidden",
                "+".join(classes),
                None,
                None,
                None,
                None,
                None,
                "",
                d.stale_reason,
            )
        )
    if d.unevidenced_reason:
        out.append(
            Finding(
                RF_TSY_UNEVIDENCED_ZERO,
                company_id,
                "total_shareholder_yield",
                "hidden",
                "unevidenced_zero",
                None,
                None,
                None,
                None,
                None,
                "",
                d.unevidenced_reason,
            )
        )
    return out


def lag_bucket(comp: ttm_guards.Component) -> str:
    """Histogram bucket of the anchor against the EXPECTED period end."""
    if comp.status == ttm_guards.ABSENT:
        return "absent"
    if comp.status == ttm_guards.NO_REFERENCE:
        return "no_expected_period"
    lag = comp.lag_days
    assert lag is not None
    if comp.status == ttm_guards.CURRENT:
        return "at_expected(<=7d)"
    if lag < 0:
        return "ahead_of_expected"
    for limit, name in (
        (98, "behind<=1q"),
        (189, "behind<=2q"),
        (280, "behind<=3q"),
        (371, "behind<=1y"),
    ):
        if lag <= limit:
            return name
    return "behind>1y"


def _dkey(f: Finding) -> tuple[int, str]:
    """Displayed-cells key. total_shareholder_yield is reported once per RULE."""
    if f.data_point == "total_shareholder_yield" and f.rule_id != RF02_AGE_GUARD:
        return (f.company_id, f"total_shareholder_yield|{f.rule_id}")
    return (f.company_id, f.data_point)


def summarize(
    findings: list[Finding],
    displayed: dict[tuple[int, str], list[str]],
    lags: Counter[str],
) -> dict[str, Any]:
    by_rule: dict[str, Any] = {}
    for rule in (
        RF01_CONSECUTIVE_WINDOW,
        RF02_AGE_GUARD,
        RF_TSY_STALE,
        RF_TSY_UNEVIDENCED_ZERO,
    ):
        sel = [f for f in findings if f.rule_id == rule]
        by_dp: dict[str, Any] = {}
        for dp in sorted({f.data_point for f in sel}):
            fs = [f for f in sel if f.data_point == dp]
            cells = sum(len(displayed.get(_dkey(f), [])) for f in fs)
            by_dp[dp] = {
                "companies": len({f.company_id for f in fs}),
                "displayed_cells_now": cells,
                "by_failure_class": dict(Counter(f.failure_class for f in fs)),
                "by_outcome": dict(Counter(f.outcome for f in fs)),
            }
        by_rule[rule] = by_dp
    return {"rules": by_rule, "age_lag_distribution": dict(lags)}


# ------------------------------------------------------------------- database


def _connect(statement_timeout_ms: int):  # pragma: no cover - needs a database
    import psycopg

    from scrooner_pipeline.common.config import settings

    return psycopg.connect(
        settings.database_url,
        options=f"-c statement_timeout={statement_timeout_ms} -c default_transaction_read_only=on",
        autocommit=True,
    )


def _client_count(conn: Any) -> int:  # pragma: no cover - needs a database
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from pg_stat_activity where backend_type = 'client backend'"
        )
        return int(cur.fetchone()[0])


def _chunks(ids: list[int], size: int) -> Iterable[list[int]]:
    for i in range(0, len(ids), size):
        yield ids[i : i + size]


def run(  # pragma: no cover - needs a database
    conn: Any,
    company_ids: list[int],
    chunk: int,
    today: date,
    max_chunks: int | None = None,
) -> tuple[
    list[Finding], dict[tuple[int, str], list[str]], Counter[str], dict[int, str]
]:
    with conn.cursor() as cur:
        cur.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            (["share_buybacks", "dividends_paid"],),
        )
        concept = dict(cur.fetchall())
        cur.execute(
            "select metric_name, id from analytics.metric_definition where metric_name = any(%s)",
            (
                [
                    *WINDOW_CONSUMERS["ebitda"],
                    *WINDOW_CONSUMERS["fcf"],
                    *sum(AGE_CONSUMERS.values(), ()),
                    "ebitda",
                    "fcf",
                ],
            ),
        )
        metric = dict(cur.fetchall())
    metric_name = {v: k for k, v in metric.items()}
    concept_name = {v: k for k, v in concept.items()}

    findings: list[Finding] = []
    displayed: dict[tuple[int, str], list[str]] = {}
    lags: Counter[str] = Counter()
    tickers: dict[int, str] = {}

    for n, ids in enumerate(_chunks(company_ids, min(chunk, CHUNK_MAX))):
        if max_chunks is not None and n >= max_chunks:
            break
        with conn.cursor() as cur:
            cur.execute(
                "select id, primary_ticker from core.company where id = any(%s)", (ids,)
            )
            tickers.update({i: t or "" for i, t in cur.fetchall()})
            # latest stored TTM value per consumer metric
            cur.execute(
                """
                select distinct on (mv.company_id, mv.metric_definition_id)
                       mv.company_id, mv.metric_definition_id, mv.value
                from analytics.metric_value mv
                where mv.company_id = any(%s) and mv.period_label = 'TTM'
                  and mv.metric_definition_id = any(%s)
                order by mv.company_id, mv.metric_definition_id, mv.period_end desc
                """,
                (
                    ids,
                    [
                        metric[m]
                        for m in set(sum(WINDOW_CONSUMERS.values(), ()))
                        | set(sum(AGE_CONSUMERS.values(), ()))
                        if m in metric
                    ],
                ),
            )
            ttm_now: dict[tuple[int, str], Decimal | None] = {
                (cid, metric_name[mid]): val for cid, mid, val in cur.fetchall()
            }
            # W1: quarter rows of the two metrics
            cur.execute(
                """
                select mv.company_id, mv.metric_definition_id, mv.value, mv.period_start, mv.period_end, mv.period_label
                from analytics.metric_value mv
                where mv.company_id = any(%s) and mv.metric_definition_id = any(%s)
                  and mv.period_label in ('Q1','Q2','Q3','Q4') and mv.value is not null
                  and mv.period_end >= %s
                """,
                (
                    ids,
                    [metric["ebitda"], metric["fcf"]],
                    today.replace(year=today.year - 3),
                ),
            )
            quarter_rows: dict[tuple[int, str], list[ttm_guards.QuarterRow]] = {}
            for cid, mid, val, start, end, label in cur.fetchall():
                quarter_rows.setdefault((cid, metric_name[mid]), []).append(
                    ttm_guards.QuarterRow(val, start, end, label)
                )
            # W2: expected period (latest periodic filing) and canonical quarters
            expected = load_latest_filed_periods(cur, ids)
            cur.execute(
                """
                select cf.company_id, cf.canonical_concept_id, p.fiscal_year, p.fiscal_period,
                       cf.value, p.start_date, p.end_date
                from analytics.canonical_fact cf
                join core.period p on p.id = cf.period_id
                where cf.company_id = any(%s) and cf.canonical_concept_id = any(%s)
                  and p.fiscal_period in ('Q1','Q2','Q3','Q4')
                """,
                (ids, list(concept.values())),
            )
            facts: dict[
                tuple[int, str], dict[tuple[int, str], tuple[Decimal, date, date]]
            ] = {}
            for cid, conc, fy, fp, val, start, end in cur.fetchall():
                by_key = facts.setdefault((cid, concept_name[conc]), {})
                key = (fy, fp)
                if key not in by_key or end > by_key[key][2]:
                    by_key[key] = (val, start, end)

        for cid in ids:
            for dp in ("ebitda", "fcf"):
                rows = quarter_rows.get((cid, dp))
                if rows:
                    f = evaluate_window(cid, dp, rows, today)
                    if f:
                        findings.append(f)
                        displayed[(cid, dp)] = [
                            m
                            for m in WINDOW_CONSUMERS[dp]
                            if ttm_now.get((cid, m)) is not None
                        ]
            expected_end = expected.get(cid)
            comps = []
            for dp in ("share_buybacks", "dividends_paid"):
                f, comp = evaluate_age(cid, dp, facts.get((cid, dp)), expected_end)
                comps.append(comp)
                if comp.status != ttm_guards.ABSENT or facts.get((cid, dp)):
                    lags[f"{dp}:{lag_bucket(comp)}"] += 1
                if f:
                    findings.append(f)
                    displayed[(cid, dp)] = [
                        m
                        for m in AGE_CONSUMERS[dp]
                        if ttm_now.get((cid, m)) is not None
                    ]
            for composite in evaluate_composite(cid, comps):
                findings.append(composite)
                displayed[_dkey(composite)] = [
                    m
                    for m in ("total_shareholder_yield",)
                    if ttm_now.get((cid, m)) is not None
                ]
    return findings, displayed, lags, tickers


def write_csv(
    path: Path,
    findings: list[Finding],
    displayed: dict[tuple[int, str], list[str]],
    tickers: dict[int, str],
) -> None:
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        for f in sorted(
            findings, key=lambda x: (x.rule_id, x.data_point, x.company_id)
        ):
            cells = displayed.get(_dkey(f), [])
            w.writerow(
                {
                    "rule_id": f.rule_id,
                    "company_id": f.company_id,
                    "ticker": tickers.get(f.company_id, ""),
                    "data_point": f.data_point,
                    "outcome": f.outcome,
                    "failure_class": f.failure_class,
                    "old_ttm": f.old_ttm,
                    "new_ttm": f.new_ttm,
                    "anchor_end": f.anchor_end,
                    "reference_end": f.reference_end,
                    "lag_days": f.lag_days,
                    "window_ends": f.window_ends,
                    "detail": f.detail,
                    "displayed_cells_now": len(cells),
                    "displayed_cells_list": ";".join(cells),
                }
            )


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - needs a database
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    scope = ap.add_mutually_exclusive_group(required=True)
    scope.add_argument("--company-ids")
    scope.add_argument("--tickers")
    scope.add_argument("--sample", type=int)
    scope.add_argument("--all", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--chunk", type=int, default=50)
    ap.add_argument("--max-chunks", type=int)
    ap.add_argument("--statement-timeout-ms", type=int, default=20000)
    ap.add_argument(
        "--max-clients",
        type=int,
        default=14,
        help="abort when more client backends than this are connected",
    )
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--summary", required=True, type=Path)
    args = ap.parse_args(argv)

    conn = _connect(args.statement_timeout_ms)
    clients = _client_count(conn)
    if clients > args.max_clients:
        print(
            f"abort: {clients} client backends connected (limit {args.max_clients})",
            file=sys.stderr,
        )
        return 2
    with conn.cursor() as cur:
        if args.company_ids:
            ids = [int(x) for x in args.company_ids.split(",") if x.strip()]
        elif args.tickers:
            cur.execute(
                "select id from core.company where primary_ticker = any(%s)",
                ([t.strip().upper() for t in args.tickers.split(",")],),
            )
            ids = [r[0] for r in cur.fetchall()]
        else:
            cur.execute("select id from core.company order by id")
            ids = [r[0] for r in cur.fetchall()]
            if args.sample:
                random.Random(args.seed).shuffle(ids)
                ids = sorted(ids[: args.sample])
        cur.execute("select now()")
        watermark = cur.fetchone()[0]
    today = date.today()
    findings, displayed, lags, tickers = run(
        conn, ids, args.chunk, today, args.max_chunks
    )
    write_csv(args.out, findings, displayed, tickers)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parent,
    ).stdout.strip()
    summary = summarize(findings, displayed, lags)
    summary.update(
        {
            "companies_examined": len(ids)
            if args.max_chunks is None
            else min(len(ids), args.max_chunks * min(args.chunk, CHUNK_MAX)),
            "today": str(today),
            "db_watermark": str(watermark),
            "git_sha": sha,
            "parameters": {
                "quarter_days": [
                    ttm_guards.QUARTER_MIN_DAYS,
                    ttm_guards.QUARTER_MAX_DAYS,
                ],
                "adjacent_slack_days": ttm_guards.ADJACENT_SLACK_DAYS,
                "window_days": [ttm_guards.WINDOW_MIN_DAYS, ttm_guards.WINDOW_MAX_DAYS],
                "expected_period_tolerance_days": ttm_guards.EXPECTED_PERIOD_TOLERANCE_DAYS,
            },
        }
    )
    args.summary.write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary["rules"], indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
