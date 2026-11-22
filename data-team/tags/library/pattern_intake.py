"""Pattern intake: every verifier FAIL in the certification registry opens one row for the tag expert.

    python3 data-team/tags/library/pattern_intake.py        (repo root; reads files only, no DB, no network)

Founder 2026-11-22: "everything should be interconnected so well." A FAIL verdict in
data-team/strategy/approvals/registry.csv (written by the approver) is a miss the tag library must learn from: the tag
expert classifies it into a pattern (patterns.csv pattern_id, or a new one) or a company quirk, then closes the row.
This script appends one row to data-team/tags/library/pattern-intake.csv per FAIL registry row not yet in it, keyed by
ticker|date|coverage_sha256 (the registry's own identity of a verdict). Append-only: existing rows are never rewritten,
so the tag expert's status, pattern_id and resolution edits are kept, and a rerun adds nothing (idempotent).
Evidence links the approver's draw files for that verdict (approvals/<TICKER>-final-draw-<date>*.md) when present.
Run by .github/workflows/verifier-fail-intake.yml on every push to main that changes registry.csv.
"""
import argparse
import csv
import datetime as dt
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
APPROVALS = os.path.join(ROOT, 'data-team', 'strategy', 'approvals')
COLUMNS = ['intake_id', 'opened', 'owner', 'status', 'ticker', 'verdict_date', 'registry_key', 'seed', 'errors',
           'upper_bound_95', 'approver', 'evidence', 'pattern_id', 'resolution']
TICKER = re.compile(r'^[A-Z][A-Z0-9.\-]{0,9}$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SHA = re.compile(r'^[0-9a-f]{64}$')


def key(r):
    return f"{r['ticker']}|{r['date']}|{r['coverage_sha256']}"


def new_rows(registry_rows, existing_keys, approvals_dir, today):
    out, seen = [], set(existing_keys)
    for r in registry_rows:
        if (r.get('verdict') or '').strip().upper() != 'FAIL':
            continue
        t, d, h = r.get('ticker', ''), r.get('date', ''), r.get('coverage_sha256', '')
        if not (TICKER.match(t) and DATE.match(d) and SHA.match(h)):
            print(f"skipped malformed FAIL row: {t!r} {d!r} {h[:12]!r}", file=sys.stderr)
            continue
        k = key(r)
        if k in seen:
            continue
        seen.add(k)
        ev = sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(approvals_dir, f'{t}-final-draw-{d}*.md')))
        out.append({
            'intake_id': f'PI-{t}-{d}-{h[:8]}', 'opened': today, 'owner': 'tag-expert', 'status': 'OPEN',
            'ticker': t, 'verdict_date': d, 'registry_key': k, 'seed': r.get('seed', ''), 'errors': r.get('errors', ''),
            'upper_bound_95': r.get('upper_bound_95', ''), 'approver': r.get('approver', ''),
            'evidence': ';'.join(ev) or 'data-team/strategy/approvals/registry.csv', 'pattern_id': '', 'resolution': '',
        })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--registry', default=os.path.join(APPROVALS, 'registry.csv'))
    ap.add_argument('--intake', default=os.path.join(HERE, 'pattern-intake.csv'))
    ap.add_argument('--approvals', default=APPROVALS)
    ap.add_argument('--today', default=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d'))
    a = ap.parse_args(argv)
    with open(a.registry, newline='') as fh:
        reg = list(csv.DictReader(fh))
    existing = set()
    if os.path.exists(a.intake):
        with open(a.intake, newline='') as fh:
            rd = csv.DictReader(fh)
            if rd.fieldnames and rd.fieldnames != COLUMNS:
                sys.exit(f'{a.intake}: header differs from {COLUMNS}; refusing to append')
            existing = {r['registry_key'] for r in rd}
    rows = new_rows(reg, existing, a.approvals, a.today)
    fresh = not os.path.exists(a.intake) or os.path.getsize(a.intake) == 0
    if rows or fresh:
        with open(a.intake, 'a', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator='\n')
            if fresh:
                w.writeheader()
            w.writerows(rows)
    print(f'pattern intake: {len(rows)} new row(s) from {sum(1 for r in reg if (r.get("verdict") or "").upper() == "FAIL")} FAIL verdict(s)')
    for r in rows:
        print(f"  {r['intake_id']} {r['evidence']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
