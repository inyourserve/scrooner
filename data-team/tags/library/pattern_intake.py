"""Pattern intake: every verifier FAIL and every recurring daily-drill miss opens one row for the tag expert.

    python3 data-team/tags/library/pattern_intake.py                      (verifier source; repo root; files only, no DB, no network)
    python3 data-team/tags/library/pattern_intake.py --drills DIR         (drill source: DIR = data-team/tags/drills from branch drills)

Founder 2026-11-22: "everything should be interconnected so well." A FAIL verdict in
data-team/strategy/approvals/registry.csv (written by the approver) is a miss the tag library must learn from: the tag
expert classifies it into a pattern (patterns.csv pattern_id, or a new one) or a company quirk, then closes the row.
This script appends one row to data-team/tags/library/pattern-intake.csv per FAIL registry row not yet in it, keyed by
ticker|date|coverage_sha256 (the registry's own identity of a verdict). Append-only: existing rows are never rewritten,
so the tag expert's status, pattern_id and resolution edits are kept, and a rerun adds nothing (idempotent). A file
with the pre-drill 14-column header is upgraded in place (new columns appended, source = verifier, values unchanged).
Evidence links the approver's draw files for that verdict (approvals/<TICKER>-final-draw-<date>*.md) when present.
Run by .github/workflows/verifier-fail-intake.yml on every push to main that changes registry.csv.

Drill source (--drills DIR, run by the commit job of .github/workflows/pipeline-daily-drill.yml after it pushes branch
`drills`): reads every DIR/<date>.csv (misses, scripts/ci/daily_drill.py report) and DIR/<date>-attempts.csv, and
  1. groups misses by miss class = class | kind | data point | element (element = the resolver's tag, else the proof's shown
     tag, else empty), deduped across days (a cell = ticker, data point, period end, kind counts once however many days
     it recurs), and upserts one source=drill row per class keyed drill|<miss class>: companies, cells, days, first/last
     seen and three example cells are recomputed from all days (a pure function of the drill files); the tag expert's
     owner, status, pattern_id and resolution are kept. flag = rule_proposal when a rule_gap class recurs at >= 2
     companies (the tag expert's rule-proposal queue, rules/inbox/); recurring for a data_gap or filer_error class at
     >= 2 companies (a missing filing or the filer's own inconsistency: not a rule); empty otherwise.
  2. writes drill-class-accuracy.csv (next to the intake): per data-point class, graded attempts = agree + rule_gap
     (data_gap and filer_error are not the predictor's answer and are counted apart), from the latest drill day of
     each ticker x data point x gate (deduped across days). Graduation bar (data-team/NOW.md, founder 2026-11-13):
     N = 200 unseen companies, accuracy >= 99% and a one-sided 95% Clopper-Pearson upper error <= 1.5%, graded only on
     FILING-CHECKED keys (docmap rows); the DATA-INFERRED proof-key columns are shown but never graduate a class.
     Template group is not in the drill files, so the class is the data point alone until it is.
"""
import argparse
import collections
import csv
import datetime as dt
import glob
import hashlib
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
APPROVALS = os.path.join(ROOT, 'data-team', 'strategy', 'approvals')
V1_COLUMNS = ['intake_id', 'opened', 'owner', 'status', 'ticker', 'verdict_date', 'registry_key', 'seed', 'errors',
              'upper_bound_95', 'approver', 'evidence', 'pattern_id', 'resolution']
COLUMNS = V1_COLUMNS + ['source', 'miss_class', 'element', 'data_point', 'companies', 'cells', 'days', 'first_seen',
                        'last_seen', 'examples', 'flag']
EXPERT_FIELDS = ('opened', 'owner', 'status', 'pattern_id', 'resolution')
ACC_COLUMNS = ['class', 'attempts', 'correct', 'accuracy', 'companies', 'cp_upper_error_95', 'fc_attempts', 'fc_correct',
               'fc_accuracy', 'fc_companies', 'fc_cp_upper_error_95', 'data_gap_excluded', 'filer_error_excluded', 'days',
               'graduated']
RULES_DIR = os.path.join(ROOT, 'data-team', 'tags', 'rules', 'inbox')
PROPOSAL_COLUMNS = ['rule_id', 'version', 'namespace', 'data_point', 'scope', 'era', 'kind', 'when', 'then', 'precedence',
                    'evidence', 'author', 'date', 'note', 'proposed_by', 'finding']
STATUS_COLUMNS = ['proposal_file', 'rule_id', 'status', 'backtest_delta', 'date', 'note']
PROPOSAL_FILE = 'drill-auto.csv'
PROPOSER = 'daily-drill-auto'
ELIGIBLE_COLUMNS = ['class', 'graduated_on', 'fc_attempts', 'fc_companies', 'fc_accuracy', 'fc_cp_upper_error_95', 'status']
GRAD_MIN_COMPANIES = 200
GRAD_MIN_ACCURACY = 0.99
GRAD_MAX_UPPER_ERROR = 0.015
DRILL_DAY = re.compile(r'^(\d{4}-\d{2}-\d{2})\.csv$')
PROOF_TAG = re.compile(r'^proof \S+ ([A-Za-z][\w-]*(?::[\w-]+)?)=')
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


# ---------------------------------------------------------------- drill source
def drill_days(drills_dir):
    return sorted(m.group(1) for f in os.listdir(drills_dir) if (m := DRILL_DAY.match(f)))


def element(r):
    if r.get('tag'):
        return r['tag']
    m = PROOF_TAG.match(r.get('evidence') or '')
    return m.group(1) if m else ''


def companies_of(r):
    """new_element_family rows list every company in the ticker field (comma joined); other rows name one company."""
    return [t for t in (r.get('ticker') or '').split(',') if t]


def drill_groups(drills_dir):
    """{miss key: aggregate} over every drill day; a cell recurring on several days counts once (latest day kept)."""
    cells = {}
    for day in drill_days(drills_dir):
        with open(os.path.join(drills_dir, f'{day}.csv'), newline='') as fh:
            for r in csv.DictReader(fh):
                mc = f"{r['class']}|{r['kind']}"
                k = (mc, r.get('data_point', ''), element(r))
                cell = (r.get('ticker', ''), r.get('data_point', ''), r.get('period_end', ''), r['kind'], k[2])
                cells[(k, cell)] = (day, r)
    groups = {}
    for (k, cell), (day, r) in sorted(cells.items(), key=lambda kv: (kv[1][0], kv[0])):
        g = groups.setdefault(k, dict(companies=set(), cells=0, days=set(), examples=[]))
        g['companies'].update(companies_of(r))
        g['cells'] += 1
        g['days'].add(day)
        if len(g['examples']) < 3:
            g['examples'].append(f"{r.get('ticker', '')[:40]} {r.get('data_point') or r.get('tag', '')} {r.get('period_end', '')} "
                                 f"{r.get('accession', '')} resolver={r.get('resolver_status', '')}:{r.get('resolver_value', '')} "
                                 f"key={r.get('key_source', '')}:{r.get('key_value', '')} ({day})".replace(';', ','))
    return groups


def flag_of(miss_class, n_companies):
    if n_companies < 2:
        return ''
    return 'rule_proposal' if miss_class.startswith('rule_gap|') else 'recurring'


def drill_rows(groups, today):
    out = []
    for (mc, dp, el), g in sorted(groups.items()):
        key = f'drill|{mc}|{dp}|{el}'
        cos = sorted(g['companies'])
        days = sorted(g['days'])
        out.append({
            'intake_id': 'PI-DRILL-' + hashlib.sha256(key.encode()).hexdigest()[:10], 'opened': today, 'owner': 'tag-expert',
            'status': 'OPEN', 'ticker': ','.join(cos[:20]) + (f',+{len(cos) - 20}' if len(cos) > 20 else ''),
            'verdict_date': days[-1], 'registry_key': key, 'seed': '', 'errors': str(g['cells']), 'upper_bound_95': '',
            'approver': '', 'evidence': ';'.join(f'drills:data-team/tags/drills/{d}.csv' for d in days[-5:]),
            'pattern_id': '', 'resolution': '', 'source': 'drill', 'miss_class': mc, 'element': el, 'data_point': dp,
            'companies': str(len(cos)), 'cells': str(g['cells']), 'days': str(len(days)), 'first_seen': days[0],
            'last_seen': days[-1], 'examples': ' ; '.join(g['examples']), 'flag': flag_of(mc, len(cos)),
        })
    return out


def proposal_rows(intake_rows, today):
    """One rules/inbox proposal per rule_gap miss class (class x data point x element), linked to the drill evidence.

    A rule_gap is the only miss class a predictor/resolver rule can fix (data_gap = missing filing, filer_error = the filer's
    own inconsistency). The rule body (when/then) is not guessed: kind = proposal_open, the tag expert fills it in and
    accepts only through the backtest (rules/inbox/README.md). rule_id is a pure function of the pattern, so reruns dedupe."""
    out = []
    for r in intake_rows:
        if r.get('source') != 'drill' or not (r.get('miss_class') or '').startswith('rule_gap|'):
            continue
        kind = r['miss_class'].split('|', 1)[1]
        rid = 'drill.%s.%s' % (r['data_point'] or kind, hashlib.sha256(r['registry_key'].encode()).hexdigest()[:8])
        out.append({
            'rule_id': rid, 'version': '', 'namespace': 'drill', 'data_point': r['data_point'], 'scope': 'all', 'era': '',
            'kind': 'proposal_open', 'when': '', 'then': '', 'precedence': '',
            'evidence': r['evidence'], 'author': PROPOSER, 'date': r['first_seen'] or today,
            'note': f"{r['miss_class']} element={r['element']} companies={r['companies']} cells={r['cells']} days={r['days']} "
                    f"last_seen={r['last_seen']} flag={r['flag']}; intake {r['intake_id']}; rule body not yet written",
            'proposed_by': PROPOSER, 'finding': f"{r['intake_id']}: {r['examples']}"})
    return out


def write_proposals(rows, inbox_dir, today):
    """Upsert drill-auto.csv (rows keyed by rule_id; a row the tag expert already edited past kind=proposal_open is kept
    except for its evidence and finding) and append an open row to STATUS.csv for each new rule_id. Returns (new, total)."""
    os.makedirs(inbox_dir, exist_ok=True)
    path = os.path.join(inbox_dir, PROPOSAL_FILE)
    old = {}
    if os.path.exists(path):
        with open(path, newline='') as fh:
            old = {r['rule_id']: r for r in csv.DictReader(fh)}
    new = [r for r in rows if r['rule_id'] not in old]
    for r in rows:
        o = old.get(r['rule_id'])
        if o is None or o['kind'] == 'proposal_open':
            old[r['rule_id']] = r
        else:
            o.update({k: r[k] for k in ('evidence', 'finding')})
    write_csv(path, PROPOSAL_COLUMNS, [old[k] for k in sorted(old)])
    # STATUS.csv is hand-edited (some rows carry unquoted commas): never re-parse and rewrite it, only append new rows
    sp = os.path.join(inbox_dir, 'STATUS.csv')
    text = open(sp, newline='').read() if os.path.exists(sp) else ','.join(STATUS_COLUMNS) + '\n'
    fresh = [r for r in new if f'{PROPOSAL_FILE},{r["rule_id"]},' not in text]
    if fresh:
        with open(sp, 'w', newline='') as fh:
            fh.write(text if text.endswith('\n') else text + '\n')
            w = csv.writer(fh, lineterminator='\n')
            for r in fresh:
                w.writerow([PROPOSAL_FILE, r['rule_id'], 'open', '', today, 'auto-opened from a daily-drill rule_gap miss class'])
    return len(new), len(old)


def eligible_rows(acc, old, today):
    """Auto-map eligibility from the graduation bar (graduated = yes). A class stays eligible while it passes; one that
    drops below the bar is kept with status revoked (never silently deleted)."""
    prev = {r['class']: r for r in old}
    out = {}
    for a in acc:
        if a['graduated'] == 'yes':
            o = prev.get(a['class'])
            out[a['class']] = {'class': a['class'], 'graduated_on': (o or {}).get('graduated_on') or today,
                               'fc_attempts': a['fc_attempts'], 'fc_companies': a['fc_companies'],
                               'fc_accuracy': a['fc_accuracy'], 'fc_cp_upper_error_95': a['fc_cp_upper_error_95'],
                               'status': 'auto-map-eligible'}
    for c, o in prev.items():
        if c not in out:
            out[c] = dict(o, status='revoked')
    return [out[k] for k in sorted(out)]


def cp_upper(n, k, conf=0.95):
    """One-sided Clopper-Pearson upper bound on the error rate for k errors in n (bisection on the binomial CDF)."""
    if n <= 0:
        return None
    if k >= n:
        return 1.0

    def cdf(p):
        return sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                            + i * math.log(p) + (n - i) * math.log1p(-p)) for i in range(k + 1))
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if cdf(mid) > 1 - conf:
            lo = mid
        else:
            hi = mid
    return hi


def class_accuracy(drills_dir):
    """Rows of drill-class-accuracy.csv from every <date>-attempts.csv; the latest day per ticker x data point x gate wins."""
    latest = {}
    for day in drill_days(drills_dir):
        p = os.path.join(drills_dir, f'{day}-attempts.csv')
        if not os.path.exists(p):
            continue
        with open(p, newline='') as fh:
            for r in csv.DictReader(fh):
                latest[(r['ticker'], r['data_point'], r['gate'], r['evidence_label'])] = (day, r)
    agg = collections.defaultdict(lambda: dict(c=collections.Counter(), cos=set(), fc_cos=set(), days=set()))
    for (tk, dp, gate, label), (day, r) in latest.items():
        a = agg[dp]
        n = {k: int(r.get(k) or 0) for k in ('agree', 'rule_gap', 'data_gap', 'filer_error')}
        graded = n['agree'] + n['rule_gap']
        a['days'].add(day)
        a['c']['data_gap'] += n['data_gap']
        a['c']['filer_error'] += n['filer_error']
        a['c']['attempts'] += graded
        a['c']['correct'] += n['agree']
        if graded:
            a['cos'].add(tk)
        if label == 'FILING-CHECKED':
            a['c']['fc_attempts'] += graded
            a['c']['fc_correct'] += n['agree']
            if graded:
                a['fc_cos'].add(tk)
    out = []
    for dp, a in sorted(agg.items()):
        c = a['c']
        up = cp_upper(c['attempts'], c['attempts'] - c['correct'])
        fup = cp_upper(c['fc_attempts'], c['fc_attempts'] - c['fc_correct'])
        acc = c['correct'] / c['attempts'] if c['attempts'] else None
        facc = c['fc_correct'] / c['fc_attempts'] if c['fc_attempts'] else None
        grad = (len(a['fc_cos']) >= GRAD_MIN_COMPANIES and facc is not None and facc >= GRAD_MIN_ACCURACY
                and fup is not None and fup <= GRAD_MAX_UPPER_ERROR)
        f = lambda x: '' if x is None else f'{x:.4f}'
        out.append({'class': dp, 'attempts': c['attempts'], 'correct': c['correct'], 'accuracy': f(acc),
                    'companies': len(a['cos']), 'cp_upper_error_95': f(up), 'fc_attempts': c['fc_attempts'],
                    'fc_correct': c['fc_correct'], 'fc_accuracy': f(facc), 'fc_companies': len(a['fc_cos']),
                    'fc_cp_upper_error_95': f(fup), 'data_gap_excluded': c['data_gap'], 'filer_error_excluded': c['filer_error'],
                    'days': len(a['days']), 'graduated': 'yes' if grad else 'no'})
    return out


def read_intake(path):
    """Existing intake rows, upgraded from the pre-drill header (source = verifier) without touching their values."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return []
    with open(path, newline='') as fh:
        rd = csv.DictReader(fh)
        if rd.fieldnames not in (COLUMNS, V1_COLUMNS):
            sys.exit(f'{path}: header differs from {COLUMNS}; refusing to write')
        rows = list(rd)
    for r in rows:
        for c in COLUMNS:
            r[c] = r.get(c) or ('verifier' if c == 'source' else '')
    return rows


def write_csv(path, cols, rows):
    tmp = path + '.tmp'
    with open(tmp, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def run_drills(a):
    rows = read_intake(a.intake)
    by_key = {r['registry_key']: r for r in rows}
    fresh = drill_rows(drill_groups(a.drills), a.today)
    added = updated = 0
    for r in fresh:
        old = by_key.get(r['registry_key'])
        if old is None:
            rows.append(r)
            by_key[r['registry_key']] = r
            added += 1
            continue
        keep = {k: old[k] for k in EXPERT_FIELDS if old.get(k)}
        if any(old.get(k) != v for k, v in r.items() if k not in keep):
            updated += 1
        old.update(r)
        old.update(keep)
    write_csv(a.intake, COLUMNS, rows)
    acc = class_accuracy(a.drills)
    write_csv(a.accuracy, ACC_COLUMNS, acc)
    n_new, n_prop = write_proposals(proposal_rows(rows, a.today), a.inbox, a.today)
    old_el = []
    if os.path.exists(a.eligible):
        with open(a.eligible, newline='') as fh:
            old_el = list(csv.DictReader(fh))
    el = eligible_rows(acc, old_el, a.today)
    write_csv(a.eligible, ELIGIBLE_COLUMNS, el)
    props = sum(1 for r in rows if r['source'] == 'drill' and r['flag'] == 'rule_proposal')
    print(f'drill intake: {added} new, {updated} updated miss class(es) from {len(drill_days(a.drills))} drill day(s); '
          f'{props} rule_proposal; {n_prop} rules/inbox proposal(s) ({n_new} new); {len(acc)} accuracy class(es), {sum(r["graduated"] == "yes" for r in acc)} graduated; '
          f'{sum(r["status"] == "auto-map-eligible" for r in el)} auto-map-eligible')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--registry', default=os.path.join(APPROVALS, 'registry.csv'))
    ap.add_argument('--intake', default=os.path.join(HERE, 'pattern-intake.csv'))
    ap.add_argument('--approvals', default=APPROVALS)
    ap.add_argument('--drills', help='directory of daily drill files (<date>.csv, <date>-attempts.csv); switches to the drill source')
    ap.add_argument('--accuracy', default=os.path.join(HERE, 'drill-class-accuracy.csv'))
    ap.add_argument('--inbox', default=RULES_DIR, help='rules/inbox dir: drill-auto.csv proposals and STATUS.csv rows (drill source)')
    ap.add_argument('--eligible', default=os.path.join(HERE, 'auto-map-eligible.csv'))
    ap.add_argument('--today', default=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d'))
    a = ap.parse_args(argv)
    if a.drills:
        return run_drills(a)
    with open(a.registry, newline='') as fh:
        reg = list(csv.DictReader(fh))
    old = read_intake(a.intake)
    existing = {r['registry_key'] for r in old}
    rows = new_rows(reg, existing, a.approvals, a.today)
    for r in rows:
        r.update({c: r.get(c, '') for c in COLUMNS})
        r['source'] = 'verifier'
    if rows or not header_is_current(a.intake):
        write_csv(a.intake, COLUMNS, old + rows)
    print(f'pattern intake: {len(rows)} new row(s) from {sum(1 for r in reg if (r.get("verdict") or "").upper() == "FAIL")} FAIL verdict(s)')
    for r in rows:
        print(f"  {r['intake_id']} {r['evidence']}")
    return 0


def header_is_current(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return False
    with open(path, newline='') as fh:
        return next(csv.reader(fh), None) == COLUMNS


if __name__ == '__main__':
    sys.exit(main())
