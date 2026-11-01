"""Read-only dry-run of the split re-base pass (rule split.event_basis@1,
corporate_actions/share_basis.py) for an explicit list of tickers.

Writes nothing: the session is set read-only, one connection, an explicit
statement_timeout, and it refuses to start when the shared pooler already
has more than --max-backends client backends. Prints per company the events,
the filing-basis status counts, invariant violations and per-class cell
counts, plus a before/after line for every cell that changes or hides; the
full per-cell table goes to --out (CSV).

    uv run python scripts/split_rebase_dryrun.py --tickers AAPL GOOG TSLA \
        --out /path/to/cells.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter

import psycopg
from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.rule_flags import ENV_DRYRUN, ENV_ENABLED
from scrooner_pipeline.corporate_actions import share_basis as sb


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tickers", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", default="20s")
    ap.add_argument(
        "--with-ru1",
        action="store_true",
        help="classify as if pershare.never_derive@1 were on (derived-only cells removed); still read-only",
    )
    ap.add_argument("--max-backends", type=int, default=12)
    ap.add_argument(
        "--show", type=int, default=400, help="max changed cells printed per company"
    )
    args = ap.parse_args(argv)

    with psycopg.connect(settings.database_url, connect_timeout=15) as conn:
        conn.execute(f"set statement_timeout = '{args.timeout}'")
        conn.execute("set default_transaction_read_only = on")
        conn.commit()
        row = conn.execute(
            # Pooler/app sessions only: Supabase's own Storage, PostgREST,
            # exporter and auth-query sessions do not use the shared budget.
            "select count(*) from pg_stat_activity where backend_type = 'client backend'"
            " and usename not in ('supabase_storage_admin', 'authenticator',"
            " 'supabase_admin', 'pgbouncer')"
        ).fetchone()
        backends = row[0] if row else 0
        print(f"pooler/app client backends before start: {backends}")
        if backends > args.max_backends:
            print("refusing: pooler too busy", file=sys.stderr)
            return 2
        tick = conn.execute(
            "select primary_ticker, id from core.company where primary_ticker = any(%s)",
            (args.tickers,),
        ).fetchall()
        ids = dict(tick)
        missing = [t for t in args.tickers if t not in ids]
        if missing:
            print(f"unknown tickers: {missing}", file=sys.stderr)
            return 2
        period_rows = {}
        env = {ENV_DRYRUN: sb.RULE_ID}
        if args.with_ru1:
            env[ENV_ENABLED] = sb.RU1_RULE_ID
        out = sb.run_split_rebase(
            conn, [ids[t] for t in args.tickers], environ=env
        )
        assert out["mode"] == "dry_run"
        with open(args.out, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(
                ["ticker", "company_id", "concept", "period_id", "start", "end",
                 "old_value", "new_value", "class", "status", "factor",
                 "chosen_fact_id", "chosen_accession", "chosen_as_filed",
                 "n_candidates", "candidates", "source_fact_ids"]
            )  # fmt: skip
            for (res, current), ticker in zip(out["results"], args.tickers):
                pids = sorted(
                    {c.period_id for c in res.cells} | {k[1] for k in current}
                )
                for pid, s, e in conn.execute(
                    "select id, start_date, end_date from core.period where id = any(%s)",
                    (pids,),
                ).fetchall():
                    period_rows[pid] = (s, e)
                _report(ticker, res, current, period_rows, w, args.show, out["ru1_on"])
    return 0


def _report(ticker, res: sb.CompanyResult, current, periods, w, show, ru1_on) -> None:
    print(f"\n=== {ticker} (company {res.company_id}) event_hash {res.event_hash}")
    for e in res.events:
        print(
            f"  event ratio={e.ratio} status={e.status} basis_date={e.basis_date} "
            f"window=({e.lo},{e.hi}] kinds={e.kinds} pairs={len(e.pairs)} "
            f"steps={len(e.steps)} disclosures={len(e.disclosures)} {e.note}"
        )
    st = Counter(b.status for b in res.basis.values())
    fac = Counter(str(b.factor) for b in res.basis.values())
    print(f"  filings by basis status {dict(st)}; by factor {dict(fac)}")
    for b in res.basis.values():
        if b.status in ("conflict", "review"):
            print(
                f"    filing {b.filing_id} {b.filing_date} {b.status} factor={b.factor} obs={b.observed_factor} {b.note}"
            )
    print(f"  invariant violations: {len(res.violations)}")
    for p, exp in res.violations[:10]:
        print(
            f"    {p.tag} period {p.period_id}: {p.old.value} ({p.old.accession}) -> "
            f"{p.new.value} ({p.new.accession}) expected ratio {exp}"
        )
    classes: Counter = Counter()
    by_concept: Counter = Counter()
    shown = 0
    cell_keys = set()
    for c in res.cells:
        cell_keys.add((c.concept, c.period_id))
        old = current.get((c.concept, c.period_id))
        old_v = old[1] if old else None
        cls = sb.classify_change(old_v, c, ru1_on=ru1_on)
        classes[cls] += 1
        by_concept[(c.concept, cls)] += 1
        s, e = periods.get(c.period_id, (None, None))
        w.writerow(
            [ticker, res.company_id, c.concept, c.period_id, s, e, old_v, c.value, cls,
             c.status, c.factor, c.chosen.fact_id if c.chosen else None,
             c.chosen.accession if c.chosen else None, c.chosen.value if c.chosen else None,
             len(c.candidates),
             ";".join(f"{i}:{a}:{v}@f{f}={cv}" for i, a, v, f, cv in c.candidates),
             list(c.source_fact_ids)]
        )  # fmt: skip
        if (
            cls
            not in (
                sb.UNCHANGED,
                sb.ROUNDING_ONLY,
                sb.STILL_BLANK,
                sb.KEPT_DERIVED_ONLY,
            )
            and shown < show
        ):
            shown += 1
            print(
                f"    {c.concept:30s} {s}..{e} old={old_v} new={c.value} [{cls}/{c.status}] "
                f"factor={c.factor} src={c.chosen.accession if c.chosen else '-'}"
            )
    # Current cells the pass never evaluates (no mapped fact): left as is.
    for key, (_cid, v, _s) in current.items():
        if key not in cell_keys:
            classes["untouched_no_mapped_fact"] += 1
            s, e = periods.get(key[1], (None, None))
            w.writerow([ticker, res.company_id, key[0], key[1], s, e, v, v,
                        "untouched_no_mapped_fact", "untouched", None, None, None,
                        None, 0, "", []])  # fmt: skip
    print(f"  cell classes: {dict(classes)}")
    print(
        "  by concept: "
        + ", ".join(f"{k[0]}:{k[1]}={n}" for k, n in sorted(by_concept.items()))
    )


if __name__ == "__main__":
    raise SystemExit(main())
