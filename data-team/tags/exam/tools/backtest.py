"""Backtest gate for the Tag Expert's predictor (LEARNING-SYSTEM.md section 4, step 4-5).

Runs a baseline and a candidate predict.py over every ticker that has a reader docmap (answer key), grades both with
tools/grade.py (unchanged semantics: key_error / key_unverified / adjudications), keeps only hand-verified key rows, and
compares the two per data point x template group.

Usage:
  backtest.py --baseline PATH --candidate PATH [--out PREFIX] [--ledger]
    PATH = a predict.py file or a repo checkout root (then data-team/tags/exam/tools/predict.py inside it).
    Library dir defaults to <checkout>/data-team/tags/library, notes to <checkout>/data-team/tags/exam/inputs/notes.jsonl,
    rules dir (if it exists) to <checkout>/data-team/tags/rules (passed to the predictor as TAG_RULES_DIR).
  Keys:  --keys-dir DIR (else every *-docmap-*.csv on origin/main + origin/work/reads/*, one per ticker, newest commit wins)
  Lines: --lines-dir DIR (else data-team/tags/exam/lines/<TICKER>.jsonl from --lines-ref, default origin/work/tag-expert/exam-lines)
  Groups: --groups-csv FILE (ticker,sector,template_group) or, by default, core.company.sector read-only from the DB
          (DATABASE_URL from the environment or --env-file, default pipeline/.env; written to WORK_DIR/groups.csv)
          (one connection, statement_timeout 30s) + the s2_group_audit template group (sample.csv), else sector -> corporate.

Hand-verified key row: no 'AUTO' marker, no 'not hand-verified', no 'no face row matched', and no 'check: machine-full-filing'
or lowercase 'auto' machine marker unless the row also carries 'check: hand'.

Scoring per row: grade.py 'correct' = right; 'wrong' or 'no_prediction' = wrong (a predictor that emits nothing loses the
row); 'key_error' / 'key_unverified' = set aside. Baseline and candidate are compared on the rows scored for both.

Exit 1 if any class (data point x template group) with baseline accuracy >= 99% and n >= 20 flips a single row
right -> wrong, or if the overall net delta <= 0 while at least one row flipped. Identical results (no flip at all) exit 0
(the baseline == candidate self-check). Otherwise 0.
"""
import argparse, csv, hashlib, os, re, subprocess, sys, tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parents[3]
GRADE = TOOLS / 'grade.py'
COHORT = REPO / 'data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv'
S2_SAMPLE = REPO / 'data-team/strategy/data/s2_group_audit/sample.csv'
LEDGER = TOOLS.parent / 'results' / 'ledger.csv'
LEDGER_FIELDS = ['run_at', 'ticker', 'data_point', 'group', 'version', 'rule_ids', 'predicted', 'key', 'evidence', 'result']
STMT = {'BS': {'accounts_payable', 'accounts_receivable', 'cash_and_equivalents', 'current_assets', 'current_liabilities', 'goodwill',
               'inventory', 'ppe_net', 'shares_outstanding', 'stockholders_equity', 'total_assets', 'total_debt', 'total_liabilities',
               'deposits', 'loans_net'},
        'CF': {'capex', 'cash_flow_financing', 'cash_flow_investing', 'cfo', 'cf_ap_change', 'cf_ar_change', 'cf_inventory_change',
               'depreciation_and_amortization', 'dividends_paid', 'sbc', 'share_buybacks'},
        'NOTE-type': {'cash_paid_for_interest', 'cash_paid_for_income_taxes', 'amortization_of_intangibles', 'interest_income',
                      'weighted_basic_shares', 'weighted_diluted_shares', 'dividends_per_share'}}
GRADUATED_ACC, GRADUATED_N = 0.99, 20
# sector -> template group when the ticker has no s2_group_audit group (only where the sector fixes the template)
SECTOR_GROUP = {'Technology': 'corporate', 'Industrials': 'corporate', 'Healthcare': 'corporate', 'Consumer Discretionary': 'corporate',
                'Consumer Staples': 'corporate', 'Materials': 'corporate', 'Communication Services': 'corporate'}


def statement(dp):
    for k, v in STMT.items():
        if dp in v:
            return k
    return 'IS'


def git(*a, cwd=REPO):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, check=True).stdout


# ---------- key filtering ----------
def hand_verified(row):
    t = ' | '.join((row.get(k) or '') for k in ('evidence_class', 'note', 'check'))
    tl = t.lower()
    if re.search(r'\bAUTO\b', t) or 'not hand-verified' in tl or 'no face row matched' in tl:
        return False
    if ('machine-full-filing' in tl or re.search(r'\bauto\b', tl)) and 'check: hand' not in tl:
        return False
    return True


def load_keys(keys_dir):
    """{ticker: {data_point: key row}} for every docmap in keys_dir."""
    K = {}
    for f in sorted(Path(keys_dir).glob('*-docmap-*.csv')):
        tk = f.name.split('-docmap')[0]
        K.setdefault(tk, {}).update({r['data_point']: r for r in csv.DictReader(open(f))})
    return K


def collect_keys(out_dir):
    """Every docmap on origin/main + origin/work/reads/*; one per ticker (the newest commit wins when versions differ)."""
    brs = ['origin/main'] + [b.strip() for b in git('branch', '-r').splitlines() if b.strip().startswith('origin/work/reads/')]
    best = {}
    for b in brs:
        for p in git('ls-tree', '-r', '--name-only', b, 'data-team/companies/reads/').split():
            if '-docmap-' not in p or not p.endswith('.csv'):
                continue
            tk = os.path.basename(p).split('-docmap')[0]
            blob = git('rev-parse', f'{b}:{p}').strip()
            if tk in best and best[tk][2] == blob:
                continue
            ts = git('log', '-1', '--format=%cI', b, '--', p).strip()
            if tk not in best or ts > best[tk][3]:
                best[tk] = (b, p, blob, ts)
    os.makedirs(out_dir, exist_ok=True)
    for tk, (b, p, blob, ts) in best.items():
        Path(out_dir, os.path.basename(p)).write_bytes(
            subprocess.run(['git', 'cat-file', 'blob', blob], cwd=REPO, capture_output=True, check=True).stdout)
    # key snapshot: the branch heads read (branches move while readers push)
    Path(out_dir, 'SOURCES.txt').write_text(''.join(f'{b} {git("rev-parse", "--short", b).strip()}\n' for b in brs))
    return out_dir


def collect_lines(ref, tickers, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    have = set(git('ls-tree', '--name-only', ref, 'data-team/tags/exam/lines/').split())
    for tk in tickers:
        p = f'data-team/tags/exam/lines/{tk}.jsonl'
        if p in have:
            Path(out_dir, f'{tk}.jsonl').write_bytes(
                subprocess.run(['git', 'show', f'{ref}:{p}'], cwd=REPO, capture_output=True, check=True).stdout)
    return out_dir


# ---------- template groups ----------
def load_groups_csv(path):
    return {r['ticker']: (r.get('sector') or '', r.get('template_group') or '') for r in csv.DictReader(open(path))}


def groups_from_db(tickers, env_file=None):
    """core.company.sector (read-only, one connection, statement_timeout 30s) + s2_group_audit group when mappable.
    DATABASE_URL from the environment, else from env_file (default pipeline/.env of this checkout)."""
    import psycopg
    env = {}
    ef = Path(env_file) if env_file else REPO / 'pipeline/.env'
    if not os.environ.get('DATABASE_URL'):
        for ln in open(ef):
            if '=' in ln and not ln.lstrip().startswith('#'):
                k, v = ln.strip().split('=', 1)
                env[k] = v.strip().strip('"').strip("'")
    cik = {r['ticker']: r['cik'] for r in csv.DictReader(open(COHORT))}
    s2 = {}
    if S2_SAMPLE.exists():
        for r in csv.DictReader(open(S2_SAMPLE)):
            g = (r.get('group') or '').strip()
            if g and not g.isdigit():
                s2[r['ticker']] = g
    sector = {}
    with psycopg.connect(os.environ.get('DATABASE_URL') or env['DATABASE_URL'], options='-c statement_timeout=30s') as c:
        c.read_only = True
        ciks = [cik[t] for t in tickers if t in cik]
        for ck, sec in c.execute('select cik, sector from core.company where cik = any(%s)', (ciks,)).fetchall():
            sector[ck] = sec or ''
    out = {}
    for t in tickers:
        sec = sector.get(cik.get(t), '')
        out[t] = (sec, s2.get(t) or SECTOR_GROUP.get(sec) or (f'{sec or "unknown"}:unclassified'))
    return out


# ---------- predictor ----------
class Predictor:
    def __init__(self, path, lib=None, notes=None, rules=None):
        p = Path(path).resolve()
        self.py = p if p.is_file() else p / 'data-team/tags/exam/tools/predict.py'
        root = self.py.parents[4] if len(self.py.parents) > 4 else self.py.parent
        self.lib = Path(lib) if lib else root / 'data-team/tags/library'
        n = Path(notes) if notes else root / 'data-team/tags/exam/inputs/notes.jsonl'
        self.notes = n if n.exists() else None
        r = Path(rules) if rules else root / 'data-team/tags/rules'
        self.rules = r if r.exists() else None
        src = self.py.read_bytes()
        m = re.search(rb'^VERSION\s*=\s*["\']([^"\']+)["\']', src, re.M)
        self.version = (m.group(1).decode() if m else 'sha-' + hashlib.sha1(src).hexdigest()[:8])

    def run(self, lines_dir, tickers, ranks, out_dir, workers=8):
        os.makedirs(out_dir, exist_ok=True)
        env = dict(os.environ)
        if self.rules:
            env['TAG_RULES_DIR'] = str(self.rules)
        failed = []

        def one(tk):
            lp = Path(lines_dir, f'{tk}.jsonl')
            if not lp.exists():
                return tk, 'no lines'
            args = [sys.executable, str(self.py), str(lp), tk, str(ranks.get(tk, 0)), str(self.lib)]
            if self.notes:
                args.append(str(self.notes))
            r = subprocess.run(args, capture_output=True, text=True, env=env)
            if r.returncode != 0 or not r.stdout.strip():
                return tk, (r.stderr.strip().splitlines() or ['empty output'])[-1]
            Path(out_dir, f'{tk}-prediction.csv').write_text(r.stdout)
            return tk, None

        with ThreadPoolExecutor(workers) as ex:
            for tk, err in ex.map(one, tickers):
                if err:
                    failed.append((tk, err))
        return failed


def grade(grader, pred_dir, keys_dir):
    r = subprocess.run([sys.executable, str(grader), str(pred_dir), str(keys_dir)], capture_output=True, text=True, check=True)
    rows = list(csv.DictReader(r.stdout.splitlines()))
    return {(x['ticker'], x['data_point']): x for x in rows}, r.stderr.strip()


def load_preds(pred_dir):
    P = {}
    for f in Path(pred_dir).glob('*-prediction.csv'):
        for r in csv.DictReader(open(f)):
            P[(r['ticker'], r['data_point'])] = r
    return P


# ---------- comparison ----------
def score(g):
    if g is None:
        return None
    return {'correct': 'right', 'wrong': 'wrong', 'no_prediction': 'wrong'}.get(g['result'])


def compare(keys, base, cand, groups):
    """keys {tk:{dp:row}}, base/cand {(tk,dp): grade row}, groups {tk:(sector, group)} -> (classes, overall, failures)."""
    C = defaultdict(lambda: dict(n=0, base=0, cand=0, r2w=0, w2r=0))
    hand = set_aside = excluded = 0
    for tk, rows in keys.items():
        grp = groups.get(tk, ('', 'unknown'))[1] or 'unknown'
        for dp, k in rows.items():
            if not hand_verified(k):
                excluded += 1
                continue
            hand += 1
            b, c = score(base.get((tk, dp))), score(cand.get((tk, dp)))
            if b is None or c is None:
                set_aside += 1
                continue
            s = C[(dp, grp)]
            s['n'] += 1; s['base'] += b == 'right'; s['cand'] += c == 'right'
            s['r2w'] += b == 'right' and c == 'wrong'; s['w2r'] += b == 'wrong' and c == 'right'
    fails = []
    for (dp, grp), s in sorted(C.items()):
        if s['n'] >= GRADUATED_N and s['base'] / s['n'] >= GRADUATED_ACC and s['r2w'] > 0:
            fails.append(f'{dp} x {grp}: baseline {100*s["base"]/s["n"]:.1f}% n={s["n"]} loses {s["r2w"]} row(s)')
    n = sum(s['n'] for s in C.values())
    O = dict(n=n, base=sum(s['base'] for s in C.values()), cand=sum(s['cand'] for s in C.values()),
             r2w=sum(s['r2w'] for s in C.values()), w2r=sum(s['w2r'] for s in C.values()),
             hand=hand, excluded=excluded, set_aside=set_aside, tickers=len(keys))
    O['net'] = O['w2r'] - O['r2w']
    if O['r2w'] + O['w2r'] and O['net'] <= 0:
        fails.append(f'overall net delta {O["net"]} <= 0 (right->wrong {O["r2w"]}, wrong->right {O["w2r"]})')
    return dict(C), O, fails


def pct(a, n):
    return f'{100*a/n:.1f}' if n else ''


def write_report(prefix, classes, O, fails, meta):
    rows = []
    for (dp, grp), s in sorted(classes.items(), key=lambda x: (statement(x[0][0]), x[0][0], x[0][1])):
        rows.append(dict(statement=statement(dp), data_point=dp, group=grp, n=s['n'], baseline_acc=pct(s['base'], s['n']),
                         candidate_acc=pct(s['cand'], s['n']), delta=f'{100*(s["cand"]-s["base"])/s["n"]:+.1f}' if s['n'] else '',
                         right_to_wrong=s['r2w'], wrong_to_right=s['w2r'],
                         graduated='Y' if s['n'] >= GRADUATED_N and s['base'] / s['n'] >= GRADUATED_ACC else ''))
    with open(f'{prefix}.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['data_point']); w.writeheader(); w.writerows(rows)
    by_st = defaultdict(lambda: [0, 0, 0])
    for (dp, grp), s in classes.items():
        t = by_st[statement(dp)]; t[0] += s['n']; t[1] += s['base']; t[2] += s['cand']
    L = [f'# Predictor backtest ({meta["run_at"]})', '',
         f'Baseline `{meta["baseline"]}` ({meta["bver"]}) vs candidate `{meta["candidate"]}` ({meta["cver"]}). Verdict: **{"FAIL" if fails else "PASS"}**.', '',
         f'Tickers with keys {O["tickers"]}; hand-verified key rows {O["hand"]} (excluded as not hand-verified {O["excluded"]}); '
         f'compared {O["n"]}; set aside (key_error / key_unverified in either) {O["set_aside"]}.', '',
         f'Overall: baseline {pct(O["base"], O["n"])}%, candidate {pct(O["cand"], O["n"])}%, '
         f'right->wrong {O["r2w"]}, wrong->right {O["w2r"]}, net delta {O["net"]:+d}.', '']
    if meta.get('sources'):
        L += [f'Key sources: {meta["sources"]}', '']
    if meta.get('failed'):
        L += [f'Predictor runs without output: {meta["failed"]}', '']
    if fails:
        L += ['## Gate failures', ''] + [f'- {x}' for x in fails] + ['']
    L += ['## By statement', '', '| Statement | n | Baseline | Candidate |', '|---|---|---|---|']
    L += [f'| {k} | {v[0]} | {pct(v[1], v[0])}% | {pct(v[2], v[0])}% |' for k, v in sorted(by_st.items())]
    L += ['', '## Data point x template group', '', '| Stmt | Data point | Group | n | Baseline % | Candidate % | Delta pp | R->W | W->R | Graduated |',
          '|---|---|---|---|---|---|---|---|---|---|']
    L += [f'| {r["statement"]} | {r["data_point"]} | {r["group"]} | {r["n"]} | {r["baseline_acc"]} | {r["candidate_acc"]} | {r["delta"]} | '
          f'{r["right_to_wrong"]} | {r["wrong_to_right"]} | {r["graduated"]} |' for r in rows]
    Path(f'{prefix}.md').write_text('\n'.join(L) + '\n')
    return by_st


def append_ledger(path, keys, cand, preds, groups, version, run_at):
    new = not Path(path).exists()
    os.makedirs(Path(path).parent, exist_ok=True)
    with open(path, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        if new:
            w.writeheader()
        for tk, rows in sorted(keys.items()):
            for dp, k in sorted(rows.items()):
                if not hand_verified(k):
                    continue
                g = cand.get((tk, dp)) or {}
                p = preds.get((tk, dp)) or {}
                w.writerow(dict(run_at=run_at, ticker=tk, data_point=dp, group=groups.get(tk, ('', 'unknown'))[1], version=version,
                                rule_ids=p.get('rule_ids', ''), predicted=f'{p.get("status", "")}|{p.get("tags", "")}' if p else '',
                                key=f'{k.get("status", "")}|{k.get("tags", "")}', evidence='hand', result=g.get('result', 'not_graded')))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--baseline', required=True); ap.add_argument('--candidate', required=True)
    for s in ('baseline', 'candidate'):
        ap.add_argument(f'--{s}-lib'); ap.add_argument(f'--{s}-notes'); ap.add_argument(f'--{s}-rules')
    ap.add_argument('--keys-dir'); ap.add_argument('--lines-dir'); ap.add_argument('--lines-ref', default='origin/work/tag-expert/exam-lines')
    ap.add_argument('--groups-csv'); ap.add_argument('--env-file', help='file with DATABASE_URL (default pipeline/.env)')
    ap.add_argument('--ranks-csv', default=str(COHORT))
    ap.add_argument('--grader', default=str(GRADE)); ap.add_argument('--work-dir')
    ap.add_argument('--out', help='output prefix for .md and .csv (default WORK_DIR/backtest)')
    ap.add_argument('--ledger', nargs='?', const=str(LEDGER), help=f'append per-row candidate results (default {LEDGER})')
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args(argv)
    work = Path(a.work_dir or tempfile.mkdtemp(prefix='backtest-'))
    work.mkdir(parents=True, exist_ok=True)
    keys_dir = a.keys_dir or collect_keys(work / 'keys')
    keys = load_keys(keys_dir)
    tickers = sorted(keys)
    lines_dir = a.lines_dir or collect_lines(a.lines_ref, tickers, work / 'lines')
    ranks = {}
    if a.ranks_csv and Path(a.ranks_csv).is_file():
        ranks = {r['ticker']: i for i, r in enumerate(csv.DictReader(open(a.ranks_csv)), 1)}
    groups = load_groups_csv(a.groups_csv) if a.groups_csv else groups_from_db(tickers, a.env_file)
    with open(work / 'groups.csv', 'w', newline='') as f:
        csv.writer(f).writerows([('ticker', 'sector', 'template_group')] + [(t, *groups.get(t, ('', ''))) for t in tickers])
    B = Predictor(a.baseline, a.baseline_lib, a.baseline_notes, a.baseline_rules)
    Cn = Predictor(a.candidate, a.candidate_lib, a.candidate_notes, a.candidate_rules)
    failed = {}
    for name, P in (('baseline', B), ('candidate', Cn)):
        failed[name] = P.run(lines_dir, tickers, ranks, work / name, a.workers)
    gb, sb = grade(a.grader, work / 'baseline', keys_dir)
    gc, sc = grade(a.grader, work / 'candidate', keys_dir)
    classes, O, fails = compare(keys, gb, gc, groups)
    run_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    prefix = a.out or str(work / 'backtest')
    meta = dict(run_at=run_at, baseline=B.py, candidate=Cn.py, bver=B.version, cver=Cn.version,
                failed={k: len(v) for k, v in failed.items() if v},
                sources='; '.join(Path(keys_dir, 'SOURCES.txt').read_text().split('\n')).strip('; ') if Path(keys_dir, 'SOURCES.txt').exists() else '')
    by_st = write_report(prefix, classes, O, fails, meta)
    if a.ledger:
        append_ledger(a.ledger, keys, gc, load_preds(work / 'candidate'), groups, Cn.version, run_at)
    print(f'grade.py baseline: {sb}\ngrade.py candidate: {sc}', file=sys.stderr)
    for name, v in failed.items():
        if v:
            print(f'{name}: {len(v)} tickers without a prediction, e.g. {v[:3]}', file=sys.stderr)
    print(f'tickers {O["tickers"]}; hand rows {O["hand"]}; compared {O["n"]}; baseline {pct(O["base"], O["n"])}%; '
          f'candidate {pct(O["cand"], O["n"])}%; r->w {O["r2w"]}; w->r {O["w2r"]}; net {O["net"]:+d}; '
          + '; '.join(f'{k} {v[0]} rows {pct(v[2], v[0])}%' for k, v in sorted(by_st.items())))
    print(f'report: {prefix}.md {prefix}.csv')
    for x in fails:
        print('FAIL', x)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
