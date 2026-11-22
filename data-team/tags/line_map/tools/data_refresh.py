#!/usr/bin/env python3
"""Resolver DATA refresh (SYSTEMS.md interconnection map, founder 2026-11-22 "close these manual links"): re-run the resolver
with the CURRENT rules and code on new inputs (a new standard extract, or new filing-read files in
data-team/strategy/open-shown-fixes/), gate it, and hand the result to the committing workflow
(.github/workflows/resolver-data-refresh.yml). It never changes a rule, a tool or a test; it only regenerates
resolver/<TICKER>.csv and rules/filing_read_cells.csv for the companies in scope, the way the local resolver lane does by hand
(CHANGELOG.md .86-.89: filing_reads.py import -> resolve_all.py -> split_resolver.py -> line_map tests -> oracle).

Subcommands (paths are repo-relative unless absolute; nothing here touches a database or sec.gov):
  fsn-new-ciks FSN_ROWS.csv                 companies of the resolver set with an FSN annual filing newer than their resolver
                                            output (FSN_ROWS.csv: cik,accession,form,period from fsn.filing) -> comma list
  scope --mode push|extract|dispatch ...    the tickers to refresh -> JSON {tickers, ciks}
  covers MANIFEST.json CIKS                 exit 0 when the extract's manifest holds every CIK
  next-version                              the next data-refresh version from CHANGELOG.md (.89 -> .89.d1, .89.d1 -> .89.d2)
  prepare / resolve / oracle / gate / changelog   the steps of one attempt (see the workflow)

The oracle (the lane's: VALUE reads vs resolver, 0.06%): every latest-dated VALUE read of every open-shown-fixes file is
compared with the resolver row of its cell (fiscal year keyed by filing_reads.fiscal_periods). BAD = the resolver serves no
value there, or a value off by more than 0.06% of the read. The gate: the line_map tests pass AND BAD(after) <= BAD(before),
both counted over the same current fix files (CHANGELOG .89: "112 BAD over the current files -> 9").
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from decimal import Decimal as D, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINE_MAP = HERE.parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / 'pipeline' / 'src'))
import filing_reads  # noqa: E402

csv.field_size_limit(10**8)
FIXES = REPO / 'data-team' / 'strategy' / 'open-shown-fixes'
FIX_RE = re.compile(r'(?:^|/)open-shown-fixes/([A-Z0-9][A-Z0-9.\-]{0,11})-\d{4}-\d{2}-\d{2}\.csv$')
ANNUAL_FORMS = ('10-K', '20-F', '40-F')   # the extract's annual forms (tools/extract.sql: form in ('10-K','20-F','40-F'))
MIN_PERIOD = '2014-06-01'                 # the extract's window (same line)
TOL = D('0.0006')                         # the oracle tolerance, 0.06% of the read
VER_RE = re.compile(r'^\|\s*\.(\d+)(?:\.d(\d+))?\s*\|')


# ---------------------------------------------------------------- resolver files
def resolver_dir(repo: Path = REPO) -> Path:
    return repo / 'data-team' / 'tags' / 'line_map' / 'resolver'


def read_csv(p: Path) -> list[dict]:
    with open(p, newline='', encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def ticker_ciks(rdir: Path) -> dict[str, str]:
    """ticker -> company cik (10 digits) from the resolver files."""
    out = {}
    for p in sorted(rdir.glob('*.csv')):
        with open(p, newline='') as fh:
            for r in csv.DictReader(fh):
                if r.get('ticker') and r.get('cik'):
                    out[r['ticker']] = r['cik'].zfill(10)
                    break
    return out


def latest_by_cik(rdir: Path) -> dict[str, tuple[str, set]]:
    """cik -> (latest own period_end, accessions) of the resolver output."""
    out: dict[str, tuple[str, set]] = {}
    for p in sorted(rdir.glob('*.csv')):
        for r in read_csv(p):
            c = (r.get('cik') or '').zfill(10)
            mx, accs = out.get(c, ('', set()))
            if (r.get('column') or 'own') == 'own' and not str(r.get('accession', '')).startswith('BEFORE:'):
                mx = max(mx, r.get('period_end') or '')
            accs.add(r.get('accession') or '')
            out[c] = (mx, accs)
    return out


# ---------------------------------------------------------------- scope selection
def new_filing_ciks(latest: dict[str, tuple[str, set]], fsn_rows) -> list[str]:
    """Companies of the resolver set with an FSN annual filing (10-K/20-F/40-F, period >= 2014-06-01) whose accession the
    resolver output does not carry AND whose period is after the company's latest resolved period. The period condition
    makes the chain converge: once the resolver serves the new year, the company is not selected again; an old filing the
    resolver drops on purpose (X110 duplicate, pre-window) never re-selects it. Amendments (10-K/A) are not annual forms of
    the extract and are not selected."""
    out = set()
    for f in fsn_rows:
        c = str(f.get('cik') or '').zfill(10)
        if c not in latest or f.get('form') not in ANNUAL_FORMS: continue
        per = str(f.get('period') or '')[:10]
        if per < MIN_PERIOD: continue
        mx, accs = latest[c]
        if f.get('accession') not in accs and per > mx:
            out.add(c)
    return sorted(out)


def fix_file_tickers(paths) -> set[str]:
    """Tickers named by changed open-shown-fixes files (<TICKER>-<YYYY-MM-DD>.csv)."""
    return {m.group(1) for p in paths if (m := FIX_RE.search(p.strip()))}


def cells_changed_tickers(old_rows, new_rows) -> set[str]:
    """Tickers whose filing_read_cells rows differ (as multisets) between two imports."""
    def by(rows):
        d = collections.defaultdict(collections.Counter)
        for r in rows: d[r['ticker']][tuple(sorted(r.items()))] += 1
        return d
    o, n = by(old_rows), by(new_rows)
    return {t for t in set(o) | set(n) if o.get(t) != n.get(t)}


def scope(mode: str, tick_cik: dict[str, str], changed_paths=(), old_cells=(), new_cells=(), extract_ciks=(), tickers=()) -> list[str]:
    """The tickers to refresh. Only tickers with a resolver file are in scope (a new company is onboarding, not a refresh).
      push:     tickers of the changed fix files + tickers whose imported read cells changed
      extract:  tickers whose company cik is in the extract's CIK list
      dispatch: the given tickers, all when none"""
    if mode == 'push':
        want = fix_file_tickers(changed_paths) | cells_changed_tickers(old_cells, new_cells)
    elif mode == 'extract':
        ck = {str(c).strip().zfill(10) for c in extract_ciks if str(c).strip()}
        want = {t for t, c in tick_cik.items() if c in ck}
    elif mode == 'dispatch':
        want = {t.strip() for t in tickers if t.strip()} or set(tick_cik)
    else:
        raise ValueError(mode)
    return sorted(t for t in want if t in tick_cik)


def covers(manifest_ciks: str, need) -> bool:
    have = {c.strip().lstrip('0') for c in str(manifest_ciks).split(',') if c.strip()}
    return all(str(c).lstrip('0') in have for c in need)


def merge_cells(old_rows, new_rows, scope_tickers) -> list[dict]:
    """rules/filing_read_cells.csv after a scoped refresh: the new import's rows for the tickers in scope, the committed rows
    for every other ticker (their resolver files are not regenerated, so their cells must not move ahead of them).
    Tickers keep the new import's order (files are imported sorted by name, so a ticker's rows are contiguous)."""
    sc = set(scope_tickers)
    old_by, new_by, order = collections.defaultdict(list), collections.defaultdict(list), []
    for r in new_rows:
        if r['ticker'] not in new_by: order.append(r['ticker'])
        new_by[r['ticker']].append(r)
    for r in old_rows:
        if r['ticker'] not in new_by and r['ticker'] not in old_by: order.append(r['ticker'])
        old_by[r['ticker']].append(r)
    out = []
    for t in order:
        out += new_by[t] if t in sc else old_by.get(t, [])
    return out


# ---------------------------------------------------------------- oracle and gate
def _dec(v):
    try:
        return D(str(v))
    except (InvalidOperation, TypeError):
        return None


def latest_value_reads(fix_files) -> list[dict]:
    """The latest-dated read of every (ticker, data_point, fiscal_year), kept when it is a VALUE row."""
    best = {}
    for fp in sorted(fix_files):
        m = re.search(r'(\d{4}-\d{2}-\d{2})\.csv$', str(fp)); d = m.group(1) if m else ''
        for e in read_csv(Path(fp)):
            k = (e['ticker'], e['data_point'], str(e['fiscal_year']))
            if k not in best or d >= best[k][0]: best[k] = (d, e)
    return [e for _, e in best.values() if e.get('outcome') == 'VALUE' and _dec(e.get('value')) is not None]


def oracle(rdir: Path, reads) -> dict:
    """{'bad': n, 'checked': n, 'no_period': n, 'bad_cells': [...]} for one resolver directory."""
    blank = set(filing_reads.BLANK)
    res_cache, bad, checked, nop = {}, [], 0, 0
    for e in reads:
        t = e['ticker']
        if t not in res_cache:
            p = rdir / f'{t}.csv'
            res_cache[t] = read_csv(p) if p.exists() else []
        res = res_cache[t]
        pes = filing_reads.fiscal_periods(res, e) if res else []
        if len(pes) != 1:
            nop += 1; continue
        checked += 1
        ev = _dec(e['value'])
        rows = [r for r in res if r['data_point'] == e['data_point'] and r['period_end'] == pes[0]]
        rows.sort(key=lambda r: (r.get('column') or 'own') != 'own')
        vals = [_dec(r['value']) for r in rows if r.get('decision') not in blank and r.get('value') not in (None, '')]
        vals = [v for v in vals if v is not None]
        ok = bool(vals) and (abs(vals[0] - ev) <= TOL * abs(ev) if ev != 0 else vals[0] == 0)
        if not ok:
            bad.append(f"{t}|{e['data_point']}|{e['fiscal_year']}|read={e['value']}|resolver={vals[0] if vals else 'blank'}")
    return dict(bad=len(bad), checked=checked, no_period=nop, bad_cells=sorted(bad))


def gate(tests_ok: bool, before: dict, after: dict) -> tuple[bool, list[str]]:
    """Commit only when the line_map tests pass and oracle BAD did not increase."""
    why = []
    if not tests_ok: why.append('line_map tests failed')
    if after['bad'] > before['bad']:
        new = sorted(set(after['bad_cells']) - set(before['bad_cells']))
        why.append(f"oracle BAD rose {before['bad']} -> {after['bad']} (new: {'; '.join(new[:40])})")
    return (not why), why


# ---------------------------------------------------------------- versions and changelog
def next_version(changelog_text: str) -> str:
    """The data-refresh version after the newest row of the CHANGELOG table: .89 -> .89.d1; .89.d1 -> .89.d2; a later rule
    release (.90) restarts the suffix (.90.d1)."""
    best = None
    for line in changelog_text.splitlines():
        m = VER_RE.match(line)
        if m:
            v = (int(m.group(1)), int(m.group(2) or 0))
            best = v if best is None or v > best else best
    if best is None: raise ValueError('no version row in CHANGELOG.md')
    return f'.{best[0]}.d{best[1] + 1}'


def changelog_row(version, run_id, extract_run, scope_tickers, values_changed, before, after, mode) -> str:
    sc = ','.join(scope_tickers) if len(scope_tickers) <= 25 else f'{len(scope_tickers)} companies'
    trig = {'push': 'new open-shown-fixes files', 'extract': f'new standard extract run {extract_run}', 'dispatch': 'dispatch'}[mode]
    return (f"| {version} | {date.today().isoformat()} | (this commit) | resolver-data-refresh (CI run {run_id}), data refresh: CURRENT rules, no rule change |"
            f" standard-extract artifact of run {extract_run} | every open-shown-fixes file (filing_reads.py import; cells file changed only for the scope) |"
            f" trigger: {trig}; scope {sc}; {values_changed} values changed; oracle (VALUE rows, 0.06%, current files): {before['bad']} -> {after['bad']} BAD |")


# ---------------------------------------------------------------- the steps of one attempt
def _write_csv(p: Path, rows, cols):
    with open(p, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)


def cmd_prepare(a):
    """Import the reads, scope, filtered extract copy, before-copy of the resolver files."""
    repo, work = Path(a.repo), Path(a.work)
    rdir, rules = resolver_dir(repo), repo / 'data-team' / 'tags' / 'line_map' / 'rules'
    work.mkdir(parents=True, exist_ok=True)
    tick_cik = ticker_ciks(rdir)
    fix_files = sorted(str(p) for p in (repo / 'data-team' / 'strategy' / 'open-shown-fixes').glob('*.csv'))
    kept, skipped = filing_reads.import_files(str(rdir), fix_files)
    old_cells = read_csv(rules / 'filing_read_cells.csv') if (rules / 'filing_read_cells.csv').exists() else []
    new_cells = [{k: ('' if v is None else str(v)) for k, v in r.items()} for r in kept]
    sc = scope(a.mode, tick_cik, changed_paths=(a.changed or '').split(','), old_cells=old_cells, new_cells=new_cells,
               extract_ciks=(a.extract_ciks or '').split(','), tickers=(a.tickers or '').split(','))
    _write_csv(rules / 'filing_read_cells.csv', merge_cells(old_cells, new_cells, sc), filing_reads.OUT_COLS)
    _write_csv(work / 'skipped.csv', skipped, filing_reads.OUT_COLS + ['reason'])
    shutil.rmtree(work / 'before', ignore_errors=True); shutil.copytree(rdir, work / 'before')
    json.dump(dict(tickers=sc, ciks=sorted({tick_cik[t] for t in sc})), open(work / 'scope.json', 'w'))
    print(json.dumps(dict(tickers=len(sc), scope=sc if len(sc) <= 25 else f'{len(sc)} companies')))
    if a.extract:   # the resolver input: the extract restricted to the scope's companies, and the filings the resolver has not seen
        ext, x = Path(a.extract), work / 'x'
        shutil.rmtree(x, ignore_errors=True); shutil.copytree(ext, x, ignore=shutil.ignore_patterns('*.jsonl'))
        ck = {tick_cik[t] for t in sc}
        filings = [f for f in json.load(open(ext / 'filings.json')) if str(f['cik']).zfill(10) in ck]
        json.dump(filings, open(x / 'filings.json', 'w'))
        with open(x / 'tk.csv', 'w', newline='') as fh: csv.writer(fh).writerows(sorted((t, c) for t, c in tick_cik.items()))
        known = {acc for _, accs in latest_by_cik(rdir).values() for acc in accs}
        json.dump([f for f in filings if f['a'] not in known], open(work / 'filings-new.json', 'w'))
        print(f"{len(filings)} filings in scope, {sum(1 for f in filings if f['a'] not in known)} new to the resolver")


def rows_key(rows):
    return collections.Counter(tuple((k, v) for k, v in sorted(r.items()) if k != 'resolver_version') for r in rows)


def cmd_resolve(a):
    repo, work = Path(a.repo), Path(a.work)
    rdir, x = resolver_dir(repo), work / 'x'
    sc = json.load(open(work / 'scope.json'))['tickers']
    cache = Path(os.environ.get('INSTANCE_CACHE') or work / 'instances')   # kept across attempts (prepare rebuilds x/)
    cache.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, INSTANCE_CACHE=str(cache.resolve()))
    subprocess.run([sys.executable, str(HERE / 'resolve_all.py'), f'resolver-all110-{a.version}', 'resolver.csv'], cwd=x, env=env, check=True)
    from scrooner_pipeline.mapper.resolver_files import split_all110
    shutil.rmtree(work / 'split', ignore_errors=True)
    counts = split_all110(x / 'resolver.csv', work / 'split', prune=False)
    changed, nvals = [], 0
    for t in sc:
        if t not in counts:
            print(f'::warning::{t}: no resolver rows from this extract; its file is kept'); continue
        new, old = read_csv(work / 'split' / f'{t}.csv'), read_csv(rdir / f'{t}.csv')
        if rows_key(new) == rows_key(old): continue
        ov = {(r['data_point'], r['period_end'], r.get('grain'), r.get('column')): r.get('value') for r in old}
        nvals += sum(1 for r in new if ov.get((r['data_point'], r['period_end'], r.get('grain'), r.get('column'))) != r.get('value'))
        shutil.copyfile(work / 'split' / f'{t}.csv', rdir / f'{t}.csv'); changed.append(t)
    json.dump(dict(changed=changed, values_changed=nvals), open(work / 'changed.json', 'w'))
    print(json.dumps(dict(changed=changed, values_changed=nvals)))


def cmd_oracle(a):
    repo, work = Path(a.repo), Path(a.work)
    reads = latest_value_reads(sorted((repo / 'data-team' / 'strategy' / 'open-shown-fixes').glob('*.csv')))
    out = dict(before=oracle(work / 'before', reads), after=oracle(resolver_dir(repo), reads))
    json.dump(out, open(work / 'oracle.json', 'w'), indent=1)
    print(f"oracle BAD before {out['before']['bad']} after {out['after']['bad']} (checked {out['after']['checked']})")


def cmd_gate(a):
    work = Path(a.work)
    o = json.load(open(work / 'oracle.json'))
    ok, why = gate(a.tests == 'pass', o['before'], o['after'])
    if not ok:
        Path(a.failure).parent.mkdir(parents=True, exist_ok=True)
        ch = json.load(open(work / 'changed.json')) if (work / 'changed.json').exists() else {}
        sc = json.load(open(work / 'scope.json'))
        new_bad = sorted(set(o['after']['bad_cells']) - set(o['before']['bad_cells']))
        Path(a.failure).write_text(
            f"# Resolver data refresh refused ({date.today().isoformat()}, CI run {a.run_id})\n\n"
            f"Nothing was committed. Trigger: {a.mode}; extract run {a.extract_run}; would-be version {a.version}.\n\n"
            + ''.join(f'- {w}\n' for w in why)
            + f"\nScope: {', '.join(sc['tickers'])}\n\nCompanies whose rows would change: {', '.join(ch.get('changed', [])) or 'none'};"
            f" values that would change: {ch.get('values_changed', 0)}.\n\nOracle (VALUE reads vs resolver, 0.06%, current fix files):"
            f" before {o['before']['bad']} BAD, after {o['after']['bad']} BAD.\n\nNew BAD cells:\n"
            + ''.join(f'- {c}\n' for c in new_bad)
            + (f"\nTests (tail):\n\n```\n{Path(a.tests_log).read_text()[-4000:]}\n```\n" if a.tests_log and Path(a.tests_log).exists() else '')
            + '\nOwner: the resolver lane (SYSTEMS.md #8): fix the input or the test, then dispatch resolver-data-refresh.yml.\n')
        print('REFUSED: ' + ' | '.join(why)); sys.exit(1)
    print('gate PASS')


def cmd_changelog(a):
    repo, work = Path(a.repo), Path(a.work)
    p = repo / 'data-team' / 'tags' / 'line_map' / 'CHANGELOG.md'
    o, ch, sc = json.load(open(work / 'oracle.json')), json.load(open(work / 'changed.json')), json.load(open(work / 'scope.json'))
    row = changelog_row(a.version, a.run_id, a.extract_run, sc['tickers'], ch['values_changed'], o['before'], o['after'], a.mode)
    t = p.read_text()
    p.write_text(t.rstrip('\n') + '\n' + row + '\n')
    print(row)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('fsn-new-ciks'); s.add_argument('fsn_rows'); s.add_argument('--repo', default=str(REPO))
    s = sub.add_parser('covers'); s.add_argument('manifest'); s.add_argument('ciks')
    s = sub.add_parser('next-version'); s.add_argument('--repo', default=str(REPO))
    for name in ('prepare', 'resolve', 'oracle', 'gate', 'changelog'):
        s = sub.add_parser(name)
        s.add_argument('--repo', default=str(REPO)); s.add_argument('--work', required=True)
        s.add_argument('--mode', choices=('push', 'extract', 'dispatch'), default='dispatch')
        s.add_argument('--changed', default=''); s.add_argument('--extract-ciks', default=''); s.add_argument('--tickers', default='')
        s.add_argument('--extract', default=''); s.add_argument('--version', default=''); s.add_argument('--run-id', default='local')
        s.add_argument('--extract-run', default=''); s.add_argument('--tests', default=''); s.add_argument('--failure', default=''); s.add_argument('--tests-log', default='')
    a = ap.parse_args(argv)
    if a.cmd == 'fsn-new-ciks':
        print(','.join(c.lstrip('0') for c in new_filing_ciks(latest_by_cik(resolver_dir(Path(a.repo))), read_csv(Path(a.fsn_rows)))))
    elif a.cmd == 'covers':
        sys.exit(0 if covers(json.load(open(a.manifest))['ciks'], [c for c in a.ciks.split(',') if c.strip()]) else 1)
    elif a.cmd == 'next-version':
        print(next_version((Path(a.repo) / 'data-team' / 'tags' / 'line_map' / 'CHANGELOG.md').read_text()))
    else:
        globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
