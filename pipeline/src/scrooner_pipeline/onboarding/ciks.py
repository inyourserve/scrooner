"""Company lists for the onboarding workflows: tickers or CIKs in, 10-digit CIKs, company ids and predecessor CIKs out.

  resolve --tickers A,B --ciks 1,2   -> comma-separated 10-digit CIKs (tickers through SEC company_tickers.json,
                                        one request through the shared limiter); an unknown ticker is an error
  expand  --ciks ...                 -> the CIKs plus the predecessor source CIKs of those companies' history rows
                                        (core.company_history_source), read-only
  ids     --ciks ...                 -> core.company ids of the CIKs that exist (read-only); an empty line when none
  shards  --ciks ... --width N       -> JSON list of N-or-fewer comma-separated CIK groups (round robin) for a matrix

Every command refuses an empty list: the normalizer falls back to the golden set when --ciks is empty, so the
workflows must never reach it with nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys


def norm_ciks(text: str) -> list[str]:
    """Comma, space or newline separated CIKs -> unique 10-digit strings in order. Raises ValueError on junk. Pure."""
    out: list[str] = []
    for tok in re.split(r"[,\s]+", text.strip()):
        if not tok:
            continue
        if not re.fullmatch(r"\d{1,10}", tok):
            raise ValueError(f"not a CIK: {tok!r}")
        c = tok.zfill(10)
        if c not in out:
            out.append(c)
    return out


def tickers_to_ciks(tickers: list[str], sec_tickers: dict) -> list[str]:
    """Resolve tickers with SEC's company_tickers.json payload ({'0': {'cik_str': 1, 'ticker': 'A'}, ...}). Pure."""
    by = {
        v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in sec_tickers.values()
    }
    missing = [t for t in tickers if t.upper() not in by]
    if missing:
        raise ValueError(f"tickers not in SEC company_tickers.json: {missing}")
    return [by[t.upper()] for t in tickers]


def shard(ciks: list[str], width: int) -> list[str]:
    """Round-robin the CIKs into at most `width` non-empty groups. Pure."""
    if width < 1:
        raise ValueError("width must be at least 1")
    groups = [ciks[i::width] for i in range(min(width, len(ciks)))]
    return [",".join(g) for g in groups if g]


def _conn():
    import psycopg

    return psycopg.connect(
        os.environ.get("SCROONER_DATABASE_URL") or os.environ["DATABASE_URL"]
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve")
    r.add_argument("--tickers", default="")
    r.add_argument("--ciks", default="")
    for name in ("expand", "ids", "shards"):
        p = sub.add_parser(name)
        p.add_argument("--ciks", required=True)
        if name == "shards":
            p.add_argument("--width", type=int, default=1)
    a = ap.parse_args(argv)

    if a.cmd == "resolve":
        ciks = norm_ciks(a.ciks)
        tickers = [t for t in re.split(r"[,\s]+", a.tickers.strip()) if t]
        if tickers:
            from scrooner_pipeline.fsn_store import edgar_fetch

            client = edgar_fetch.EdgarClient(os.environ.get("SEC_USER_AGENT", ""))
            try:
                payload = json.loads(
                    client.get("https://www.sec.gov/files/company_tickers.json").text
                )
            finally:
                client.close()
            ciks += [c for c in tickers_to_ciks(tickers, payload) if c not in ciks]
        if not ciks:
            print("give tickers or ciks", file=sys.stderr)
            return 2
        print(",".join(ciks))
        return 0

    ciks = norm_ciks(a.ciks)
    if not ciks:
        print("empty CIK list", file=sys.stderr)
        return 2
    if a.cmd == "shards":
        print(json.dumps(shard(ciks, a.width)))
        return 0
    with _conn() as conn:
        conn.execute("set statement_timeout = '2min'")
        if a.cmd == "expand":
            preds = [
                x[0]
                for x in conn.execute(
                    """select distinct h.source_cik from core.company_history_source h join core.company c on c.id = h.company_id
                   where c.cik = any(%s) and h.relation = 'predecessor' order by 1""",
                    (ciks,),
                ).fetchall()
            ]
            print(",".join(ciks + [p for p in preds if p not in ciks]))
        else:
            ids = [
                str(x[0])
                for x in conn.execute(
                    "select id from core.company where cik = any(%s) order by id",
                    (ciks,),
                ).fetchall()
            ]
            print(",".join(ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
