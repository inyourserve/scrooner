#!/usr/bin/env python3
"""Approver re-cert token check for the top100-flow certified-guard (CERT-REGISTRY rulings 2026-11-21, item 15).

A token is data-team/strategy/approvals/recert/<TICKER>-<YYYY-MM-DD>.md. It lets a certified company through the
guard ONCE. Valid when the token date is not before the latest certificate's certified_at AND the latest certificate
was not made from a coverage export dated on or after the token (that certificate is the re-certification that
consumed it). No state file: a newer certificate is the consumption record. Dates are day-grained, so the second test
(the certificate's own coverage date) separates a same-day token from the certificate it supersedes.

Prints the token path (relative to --approvals) and exits 0 when valid; prints nothing and exits 1 otherwise.
"""
import argparse
import json
import re
import sys
from pathlib import Path

DATE = r"\d{4}-\d{2}-\d{2}"


def valid_token(approvals: Path, ticker: str) -> str | None:
    tokens = sorted(
        p for p in (approvals / "recert").glob(f"{ticker}-*.md") if re.fullmatch(rf"{re.escape(ticker)}-({DATE})\.md", p.name)
    )
    if not tokens:
        return None
    token = tokens[-1]
    tdate = re.search(DATE, token.name).group(0)
    certs = []
    for p in (approvals / "certificates").glob(f"{ticker}-*.json"):
        try:
            d = json.loads(p.read_text())
        except ValueError:
            continue
        m = re.search(DATE, str(d.get("coverage_path", "")))
        certs.append((str(d.get("certified_at", "")), m.group(0) if m else ""))
    if not certs:
        return None  # no certificate to supersede: the token has nothing to act on
    certified_at, cov_date = max(certs)
    if tdate < certified_at:
        return None  # stale: a certificate was issued after the token
    if cov_date and cov_date >= tdate:
        return None  # consumed: the latest certificate covers an export made on or after the token
    return str(approvals / "recert" / token.name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--approvals", default="data-team/strategy/approvals")
    ap.add_argument("--ticker", required=True)
    a = ap.parse_args()
    t = valid_token(Path(a.approvals), a.ticker)
    if t is None:
        return 1
    print(t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
