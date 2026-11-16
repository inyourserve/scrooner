#!/usr/bin/env python3
"""Map a git range to the top-100 companies whose resolver rows changed, or to newly added request files.

  top100_changed.py companies BASE HEAD [--summary CSV] [--max N]   -> prints comma-separated company_ids
  top100_changed.py requests  BASE HEAD                              -> prints space-separated request paths

companies: a company is changed when, in data-team/tags/line_map/resolver-all110-*.csv, any row (keyed by
cik,ticker,data_point,period_end,grain) was added, removed or has a different value in any column except
resolver_version (a pure version bump with identical rows reruns nothing); or when a per-ticker rules file
data-team/tags/line_map/<TICKER>.csv changed. Tickers map to company_id through the summary CSV (ticker, company_id).
A ticker not in the summary is reported on stderr and skipped (never guessed). Shared rules (line_map/rules/*) carry
no company key and are NOT fanned out. More than --max (default 256, the flow's limit) companies is an error (exit 3),
never a silent truncation. Empty BASE or an all-zero SHA means no diff is possible: exit 2.
Reads git only; no database, no network."""
import argparse
import csv
import io
import re
import subprocess
import sys

RESOLVER = re.compile(r"^data-team/tags/line_map/resolver-all110-[^/]+\.csv$")
TICKER_FILE = re.compile(r"^data-team/tags/line_map/([A-Z][A-Z0-9.-]*)\.csv$")
REQUEST = re.compile(r"^data-team/strategy/approvals/requests/[A-Za-z0-9.-]+-request-[0-9-]+\.md$")
KEY = ("cik", "ticker", "data_point", "period_end", "grain")


def git(*a, check=True):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"git {' '.join(a)} failed: {r.stderr.strip()}")
    return r


def show(sha, path):
    r = git("show", f"{sha}:{path}", check=False)
    return r.stdout if r.returncode == 0 else None


def valid(sha):
    return bool(sha) and not set(sha) <= {"0"}


def changed_paths(base, head, filt="ACDMR"):
    out = git("diff", "--name-only", f"--diff-filter={filt}", base, head).stdout
    return [p for p in out.splitlines() if p]


def rows(text):
    d = {}
    if text is None:
        return d
    for r in csv.DictReader(io.StringIO(text)):
        k = tuple(r.get(c, "") for c in KEY)
        d[k] = tuple((c, v) for c, v in sorted(r.items()) if c != "resolver_version")
    return d


def changed_tickers(base, head):
    tickers = set()
    for p in changed_paths(base, head):
        if RESOLVER.match(p):
            old, new = rows(show(base, p)), rows(show(head, p))
            for k in set(old) | set(new):
                if old.get(k) != new.get(k):
                    tickers.add(k[1])
        else:
            m = TICKER_FILE.match(p)
            if m:
                tickers.add(m.group(1))
    tickers.discard("")
    return tickers


def companies(base, head, summary, cap):
    ids = {}
    with open(summary, newline="") as fh:
        for r in csv.DictReader(fh):
            ids[r["ticker"].strip()] = r["company_id"].strip()
    out = []
    for t in sorted(changed_tickers(base, head)):
        if t in ids:
            out.append(ids[t])
        else:
            print(f"skipped ticker not in summary: {t}", file=sys.stderr)
    out = list(dict.fromkeys(out))
    if len(out) > cap:
        print(f"{len(out)} companies exceeds the cap {cap}", file=sys.stderr)
        sys.exit(3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["companies", "requests"])
    ap.add_argument("base")
    ap.add_argument("head")
    ap.add_argument("--summary", default="data-team/strategy/top100-coverage-summary.csv")
    ap.add_argument("--max", type=int, default=256)
    a = ap.parse_args()
    if not valid(a.base) or not valid(a.head):
        print("no usable base/head sha", file=sys.stderr)
        return 2
    if a.mode == "companies":
        print(",".join(companies(a.base, a.head, a.summary, a.max)))
    else:
        print(" ".join(p for p in changed_paths(a.base, a.head, "A") if REQUEST.match(p)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
