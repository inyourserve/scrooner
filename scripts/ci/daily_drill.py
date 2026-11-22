#!/usr/bin/env python3
"""Daily blind drill (read-only): pick the next companies outside the certified set, gate the resolver's blind answers.

  daily_drill.py pick   --ranking CSV --approvals DIR --date YYYY-MM-DD --out DIR [--n 20]
        Writes OUT/ciks.txt (comma list), OUT/tk.csv (ticker,cik10 per line, the resolver's input) and OUT/batch.csv.
        Stateless rolling batch: candidates = ranked companies whose ticker has no <TICKER>-certificate-*.md in the approvals
        directory, in rank order; the window starts at (days since EPOCH) * n, modulo the number of candidates, and wraps.
  daily_drill.py fetch  OUT        (the only subcommand that opens the database: ONE read-only connection)
        Writes OUT/proofs.csv (analytics.cell_proof, FY and I grains since 2015) and OUT/checks.csv (failed fsn.filing_check).
  daily_drill.py report --out OUT --date D --reads DIR --drills DIR [--roles CSV --families TXT]
        No database. Reads OUT/resolved_all.csv, filings.json, proofs.csv, checks.csv and the docmaps; writes
        DRILLS/<date>.md, DRILLS/<date>.csv (one row per item, class = rule_gap | data_gap | filer_error) and
        DRILLS/<date>-attempts.csv (one row per ticker x data point x gate x evidence label: compared, agree and the miss
        classes; the denominator data-team/tags/library/pattern_intake.py --drills needs for per-class accuracy).

Evidence labels: a docmap row is FILING-CHECKED only when its own evidence_class says so; proof rows are the production proof
(DATA-INFERRED about the filing); the classification itself is DATA-INFERRED until a Tag Expert reads the filing."""
import argparse, collections, csv, glob, json, os, re, sys
from datetime import date, datetime
from decimal import Decimal as D, InvalidOperation

EPOCH = date(2026, 11, 17)
WINDOW_START = '2015-01-01'
VAL = ('mapped', 'component_sum', 'derived')
REASON = ('not_presented', 'combined')
MAX_FAMILY_ITEMS = 400
ATT_COLS = ['date', 'ticker', 'data_point', 'gate', 'evidence_label', 'compared', 'agree', 'rule_gap', 'data_gap', 'filer_error']
COLS = ['date', 'class', 'kind', 'ticker', 'cik', 'data_point', 'period_end', 'accession', 'tag', 'resolver_status', 'resolver_value',
        'key_source', 'key_value', 'evidence_label', 'evidence', 'detail']


# ---------------------------------------------------------------- pick (pure)
def read_ranking(path):
    out = []
    for i, r in enumerate(csv.DictReader(open(path)), 1):
        m = re.search(r'rank (\d+)', r.get('source', '') or '')
        out.append(dict(rank=int(m.group(1)) if m else i, ticker=r['ticker'], cik=str(int(r['cik'])), name=r.get('name', '')))
    out.sort(key=lambda r: r['rank'])
    return out


def certified_tickers(approvals_dir):
    got = set()
    for p in glob.glob(os.path.join(approvals_dir, '*-certificate-*.md')):
        m = re.match(r'^(.+?)-certificate-', os.path.basename(p))
        if m: got.add(m.group(1))
    return got


def pick(ranking, certified, day, n=20):
    cand = [r for r in ranking if r['ticker'] not in certified]
    if not cand: return []
    n = min(n, len(cand))
    start = ((day - EPOCH).days * n) % len(cand)
    return [cand[(start + k) % len(cand)] for k in range(n)]


def cmd_pick(a):
    day = date.fromisoformat(a.date)
    batch = pick(read_ranking(a.ranking), certified_tickers(a.approvals), day, a.n)
    if not batch: raise SystemExit('no candidates outside the certified set')
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, 'ciks.txt'), 'w').write(','.join(r['cik'] for r in batch) + '\n')
    with open(os.path.join(a.out, 'tk.csv'), 'w', newline='') as f:
        csv.writer(f).writerows([[r['ticker'], r['cik'].zfill(10)] for r in batch])
    with open(os.path.join(a.out, 'batch.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['rank', 'ticker', 'cik', 'name']); w.writeheader(); w.writerows(batch)
    print(f"{len(batch)} companies, ranks {batch[0]['rank']}..{batch[-1]['rank']}: " + ' '.join(r['ticker'] for r in batch))


# ---------------------------------------------------------------- fetch (database, read-only)
def cmd_fetch(a):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import run_extract_sql as rx
    ciks = [int(c) for c in open(os.path.join(a.out, 'ciks.txt')).read().strip().split(',')]
    conn = rx.connect(); rx.assert_read_only(conn)
    with conn.cursor() as cur:
        cur.execute("select co.cik, p.data_point_name, p.period_grain, p.period_end::text, p.verdict, p.shown_value, p.shown_tag, p.shown_accession, "
                    "p.position_value, p.reason_code from analytics.cell_proof p join core.company co on co.id = p.company_id "
                    "where co.cik::bigint = any(%s) and p.basis = 'latest' and p.period_grain in ('FY','I') and p.period_end >= %s",
                    (ciks, WINDOW_START))
        proofs = cur.fetchall()
        cur.execute("select f.cik, f.accession, c.stmt, c.ddate::text, c.qtrs, c.check_id, c.lhs, c.rhs, c.tol from fsn.filing_check c "
                    "join fsn.filing f on f.id = c.filing_id where not c.ok and c.ddate >= %s and f.company_id in "
                    "(select company_id from fsn.filing where cik::bigint = any(%s) and company_id is not null)", (WINDOW_START, ciks))
        checks = cur.fetchall()
    conn.rollback()
    for name, head, rows in (('proofs.csv', ['cik', 'data_point', 'grain', 'period_end', 'verdict', 'shown_value', 'shown_tag', 'shown_accession', 'position_value', 'reason_code'], proofs),
                             ('checks.csv', ['cik', 'accession', 'stmt', 'ddate', 'qtrs', 'check_id', 'lhs', 'rhs', 'tol'], checks)):
        with open(os.path.join(a.out, name), 'w', newline='') as f:
            w = csv.writer(f); w.writerow(head); w.writerows(rows)
        print(name, len(rows), 'rows')


# ---------------------------------------------------------------- gate (pure)
def num(s):
    try: return D(str(s).replace(',', '').strip())
    except (InvalidOperation, ValueError): return None


def unit(v):
    v = abs(v); k = 0
    while k < 9 and v != 0 and v % (10 ** (k + 1)) == 0: k += 1
    return D(10) ** k


def same(a, b):
    """Rounding-aware equality (gate_all.py): within one and a half of the coarser printed unit; small values within a cent."""
    if a is None or b is None: return False
    if abs(b) < 1000: return abs(a - b) <= D('0.011')
    return abs(a - b) <= max(unit(a), unit(b)) * D('1.5')


def days(p, q):
    return abs((date.fromisoformat(p) - date.fromisoformat(q)).days)


class Resolved:
    """resolved_all.csv rows indexed by (ticker, data_point); a period is matched within 10 days (gate_all.find)."""
    def __init__(self, rows):
        self.rows = rows
        self.by = collections.defaultdict(list)
        for r in rows: self.by[(r['ticker'], r['data_point'])].append(r)

    def find(self, ticker, dp, pe, tol=10):
        c = [r for r in self.by.get((ticker, dp), []) if r['period_end'] and days(r['period_end'], pe) <= tol]
        c.sort(key=lambda r: (r['status'] not in VAL, days(r['period_end'], pe)))
        return c[0] if c else None


def failing(checks, accession, pe):
    return [c for c in checks if c['accession'] == accession and c['ddate'] == pe]


def touches(rrow, chk):
    """A failed filer calc check touches a resolver cell when the check's parent element is one of the cell's elements."""
    parent = chk['check_id'].split(':')[1] if chk['check_id'].startswith('calc:') else chk['check_id']
    return bool(parent) and parent in ((rrow.get('tags') or '') + ' ' + (rrow.get('nodes') or ''))


def classify(rrow, checks, pe):
    """(class, why). filer_error when the filer's own calc check fails on the cell's element in that column; data_gap when the
    resolver has no row for the period; otherwise rule_gap (the resolver gave no value or a different value)."""
    if rrow is None: return 'data_gap', 'no resolver row for the period: no 10-K in the FSN store covers it'
    bad = [c for c in failing(checks, rrow['accession'], rrow['period_end']) if touches(rrow, c)]
    if bad:
        c = bad[0]
        return 'filer_error', f"the filer's own check {c['check_id']} fails in {rrow['accession']} ({c['stmt']} {c['ddate']}): lhs {c['lhs']} rhs {c['rhs']} tol {c['tol']}"
    if rrow['status'] in VAL: return 'rule_gap', 'the resolver chose a different line or value than the key'
    return 'rule_gap', f"the resolver returned {rrow['status']}: {(rrow.get('why') or '')[:160]}"


def item(day, cls, kind, rrow, key_source, key_value, label, evidence, ticker='', cik='', dp='', pe='', detail=''):
    r = rrow or {}
    return {'date': day, 'class': cls, 'kind': kind, 'ticker': r.get('ticker', ticker), 'cik': r.get('cik', cik), 'data_point': r.get('data_point', dp),
            'period_end': pe or r.get('period_end', ''), 'accession': r.get('accession', ''), 'tag': (r.get('tags') or '').split('+')[0],
            'resolver_status': r.get('status', 'no_row'), 'resolver_value': r.get('value', ''), 'key_source': key_source,
            'key_value': key_value, 'evidence_label': label, 'evidence': evidence, 'detail': detail}


def tally(att, tk, dp, gate, label, cls=None):
    """One compared key for the per-class attempt table: cls None = agree, else the miss class."""
    if att is None: return
    c = att[(tk, dp, gate, label)]
    c['compared'] += 1
    c[cls or 'agree'] += 1


def gate_proofs(res, proofs, checks, day, cik2tk, att=None):
    stats = collections.Counter(); items = []
    for p in proofs:
        if p['verdict'] not in ('PROVEN', 'NOT_PRESENTED'): continue
        tk = cik2tk.get(str(int(p['cik'])))
        if not tk: continue
        r = res.find(tk, p['data_point'], p['period_end'])
        if p['verdict'] == 'PROVEN':
            stats['proof_compared'] += 1
            ok = r is not None and r['status'] in VAL and same(num(r['value']), num(p['shown_value']))
            if ok: stats['proof_agree'] += 1; tally(att, tk, p['data_point'], 'proof', 'DATA-INFERRED'); continue
            cls, why = classify(r, checks, p['period_end'])
            tally(att, tk, p['data_point'], 'proof', 'DATA-INFERRED', cls)
            items.append(item(day, cls, 'proof_disagree', r, 'cell_proof PROVEN', p['shown_value'], 'DATA-INFERRED',
                              f"proof {p['shown_accession']} {p['shown_tag']}={p['shown_value']}; {why}", tk, str(int(p['cik'])), p['data_point'], p['period_end']))
        else:
            stats['proof_np_compared'] += 1
            if r is not None and r['status'] in VAL:
                tally(att, tk, p['data_point'], 'proof_np', 'DATA-INFERRED', 'rule_gap')
                items.append(item(day, 'rule_gap', 'proof_not_presented_but_valued', r, 'cell_proof NOT_PRESENTED', '', 'DATA-INFERRED',
                                  f"proof says not presented ({p['reason_code']}); the resolver gave {r['value']} from {r.get('tags')}", tk, str(int(p['cik'])), p['data_point'], p['period_end']))
            else: stats['proof_np_agree'] += 1; tally(att, tk, p['data_point'], 'proof_np', 'DATA-INFERRED')
    return stats, items


def read_docmap(path):
    rows = list(csv.DictReader(open(path)))
    out = []
    for r in rows:
        m = re.search(r'period (\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})', r.get('note', '') or '')
        out.append((r, m.group(2) if m else None))
    return out


def gate_docmaps(res, reads_dir, tickers, checks, day, cik_of, att=None):
    stats = collections.Counter(); items = []
    for tk in tickers:
        files = sorted(glob.glob(os.path.join(reads_dir, f'{tk}-docmap-*.csv')))
        if not files: continue
        stats['docmap_companies'] += 1
        for r, pe0 in read_docmap(files[-1]):
            if r.get('evidence_class') != 'FILING-CHECKED': stats['docmap_not_filing_checked'] += 1; continue
            dp = r['data_point']
            if not pe0: stats['docmap_no_period'] += 1; continue
            fy0 = num(r.get('fy0_printed')); fy1 = num(r.get('fy1_printed'))
            if r['status'] in ('not_presented',) and fy0 is None:
                rr = res.find(tk, dp, pe0)
                stats['docmap_np_compared'] += 1
                if rr is not None and rr['status'] in VAL:
                    tally(att, tk, dp, 'docmap_np', 'FILING-CHECKED', 'rule_gap')
                    items.append(item(day, 'rule_gap', 'docmap_not_presented_but_valued', rr, 'docmap not_presented', '', 'FILING-CHECKED',
                                      f"docmap {files[-1]} row {dp}: not presented; resolver gave {rr['value']} from {rr.get('tags')}", tk, cik_of.get(tk, ''), dp, pe0))
                else: stats['docmap_np_agree'] += 1; tally(att, tk, dp, 'docmap_np', 'FILING-CHECKED')
                continue
            for col, v, pe in (('fy0', fy0, pe0), ('fy1', fy1, None)):
                if v is None: continue
                if pe is None:
                    c = [x for x in res.by.get((tk, dp), []) if x['period_end'] and 330 <= days(x['period_end'], pe0) <= 400
                         and date.fromisoformat(x['period_end']) < date.fromisoformat(pe0)]
                    c.sort(key=lambda x: days(x['period_end'], pe0))
                    pe = c[0]['period_end'] if c else None
                    if pe is None:
                        stats['docmap_compared'] += 1
                        tally(att, tk, dp, 'docmap', 'FILING-CHECKED', 'data_gap')
                        items.append(item(day, 'data_gap', 'docmap_disagree', None, f'docmap {col}', str(v), 'FILING-CHECKED',
                                          f"docmap {files[-1]} {dp} {col} printed {v}; no resolver row one year before {pe0}", tk, cik_of.get(tk, ''), dp, ''))
                        continue
                rr = res.find(tk, dp, pe)
                stats['docmap_compared'] += 1
                if rr is not None and rr['status'] in VAL and same(num(rr['value']), v):
                    stats['docmap_agree'] += 1; tally(att, tk, dp, 'docmap', 'FILING-CHECKED'); continue
                cls, why = classify(rr, checks, pe)
                tally(att, tk, dp, 'docmap', 'FILING-CHECKED', cls)
                items.append(item(day, cls, 'docmap_disagree', rr, f'docmap {col}', str(v), 'FILING-CHECKED',
                                  f"docmap {os.path.basename(files[-1])} {dp} {col} printed {v} ({r.get('r_page')}); {why}", tk, cik_of.get(tk, ''), dp, pe))
    return stats, items


def gate_filer_checks(res, checks, day):
    """Resolver values that rest on an element whose own filer calc check fails: the filer's inconsistency, listed for the Tag Expert."""
    items = []; seen = set()
    for r in res.rows:
        if r['status'] not in VAL or not r.get('accession'): continue
        for c in failing(checks, r['accession'], r['period_end']):
            if touches(r, c) and (r['accession'], r['data_point'], c['check_id']) not in seen:
                seen.add((r['accession'], r['data_point'], c['check_id']))
                items.append(item(day, 'filer_error', 'filer_check_failed', r, 'fsn.filing_check', '', 'DATA-INFERRED',
                                  f"the filer's own check {c['check_id']} fails in {r['accession']} ({c['stmt']} {c['ddate']}): lhs {c['lhs']} rhs {c['rhs']} tol {c['tol']}; value served {r['value']}"))
    return items


def gate_no_role(res, day):
    g = collections.defaultdict(list)
    for r in res.rows:
        if r['status'] == 'no_role': g[(r['ticker'], r['data_point'])].append(r)
    items = []
    for (tk, dp), rs in sorted(g.items()):
        rs.sort(key=lambda r: r['period_end'])
        last = rs[-1]
        items.append(item(day, 'rule_gap', 'no_role', last, '', '', 'DATA-INFERRED', f"{len(rs)} period(s) no_role, {rs[0]['period_end']}..{last['period_end']}: {(last.get('why') or '')[:160]}"))
    return items


NODE_TAG = re.compile(r'([A-Za-z][A-Za-z0-9_]*)(?:\[[^\]]*\])?=-?[\d.]+')


def known_tags(roles_csv, families_txt):
    tags, fam = set(), []
    for r in csv.DictReader(open(roles_csv)):
        for k in ('parent', 'alternatives', 'combined_if', 'fallback'):
            for t in re.split(r'[|;+, ]', r.get(k) or ''):
                if re.fullmatch(r'[A-Za-z]\w+', t): tags.add(t)
    for line in open(families_txt):
        line = line.strip()
        if line and not line.startswith('#'):
            try: fam.append(re.compile('^(' + line + ')$'))
            except re.error: pass
    return tags, fam


def gate_families(res, filings, tk_of_cik, known, fam, day):
    used = collections.defaultdict(set)
    for r in res.rows:
        used[r['accession']].update(NODE_TAG.findall(r.get('nodes') or ''))
        used[r['accession']].update(t for t in re.split(r'[+;,]', r.get('tags') or '') if t)
    new = {}
    for f in filings:
        for s in (f.get('lines') or '').split('~'):
            x = s.split('|')
            if len(x) < 9: continue
            st, rep, ln, tag, cus, neg, prole, lb, val = x[:9]
            if st not in ('BS', 'IS', 'CF') or val in ('', None): continue
            if tag in known or tag in used[f['a']] or any(p.match(tag) for p in fam): continue
            e = new.setdefault(tag, dict(n=set(), first=(f, st, rep, ln, lb, val, cus), count=0))
            e['n'].add(tk_of_cik.get(str(int(f['cik'])), f['cik'])); e['count'] += 1
    out = []
    for tag, e in sorted(new.items(), key=lambda kv: (-len(kv[1]['n']), kv[0]))[:MAX_FAMILY_ITEMS]:
        f, st, rep, ln, lb, val, cus = e['first']
        out.append(item(day, 'rule_gap', 'new_element_family', None, '', '', 'DATA-INFERRED',
                        f"{tag} ({'custom' if cus == '1' else 'standard'}) on the {st} face as '{lb}' = {val} [R{rep}.htm:{ln}] in {f['a']}; {len(e['n'])} companies, {e['count']} filings; not read by any resolver rule",
                        ticker=','.join(sorted(e['n']))[:80], cik=str(int(f['cik'])), pe=f['p']) | {'accession': f['a'], 'tag': tag})
    return out, len(new)


def pct(a, b): return f'{100 * a / b:.2f}%' if b else 'n/a (no key)'


def build(rows, filings, proofs, checks, reads_dir, roles_csv, families_txt, day, batch):
    res = Resolved(rows)
    cik2tk = {str(int(b['cik'])): b['ticker'] for b in batch}
    tickers = [b['ticker'] for b in batch]
    cik_of = {b['ticker']: str(int(b['cik'])) for b in batch}
    st = collections.Counter(r['status'] for r in rows)
    tot = len(rows)
    cov = sum(st[k] for k in VAL + REASON)
    att = collections.defaultdict(collections.Counter)
    ps, pi = gate_proofs(res, proofs, checks, day, cik2tk, att)
    ds, di = gate_docmaps(res, reads_dir, tickers, checks, day, cik_of, att)
    fi = gate_filer_checks(res, checks, day)
    nr = gate_no_role(res, day)
    known, fam = known_tags(roles_csv, families_txt)
    fa, nfam = gate_families(res, filings, cik2tk, known, fam, day)
    items = pi + di + nr + fa + fi
    stats = dict(cells=tot, status=dict(st), coverage=pct(cov, tot), proof=dict(ps), docmap=dict(ds), failed_checks=len(checks), filer_check_items=len(fi), new_families=nfam)
    stats['proof_agreement'] = pct(ps['proof_agree'], ps['proof_compared'])
    stats['docmap_agreement'] = pct(ds['docmap_agree'], ds['docmap_compared'])
    stats['attempts'] = [dict(date=day, ticker=tk, data_point=dp, gate=g, evidence_label=lb, **{k: c[k] for k in ATT_COLS[5:]})
                         for (tk, dp, g, lb), c in sorted(att.items())]
    return items, stats


def write_report(items, stats, batch, out_dir, day, code_sha=''):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f'{day}.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(items)
    with open(os.path.join(out_dir, f'{day}-attempts.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=ATT_COLS, lineterminator='\n'); w.writeheader(); w.writerows(stats.get('attempts', []))
    by = collections.Counter((i['class'], i['kind']) for i in items)
    L = [f'# Daily blind drill {day}', '',
         f"Batch: {len(batch)} companies, ranks {batch[0]['rank']}..{batch[-1]['rank']}: " + ' '.join(b['ticker'] for b in batch),
         f'Blind: standard extract + resolver, no hand rows, no fix files. Code {code_sha}. Read-only on the database. The classes below are DATA-INFERRED until a Tag Expert reads the filing; a docmap key is FILING-CHECKED.', '',
         '## Scoreboard', '',
         f"- Resolver cells: {stats['cells']}; status {stats['status']}",
         f"- Coverage (value or reason): {stats['coverage']}",
         f"- Agreement with proof rows (analytics.cell_proof PROVEN): {stats['proof_agreement']} ({stats['proof'].get('proof_agree', 0)}/{stats['proof'].get('proof_compared', 0)}); NOT_PRESENTED proofs checked {stats['proof'].get('proof_np_compared', 0)}",
         f"- Agreement with docmap keys: {stats['docmap_agreement']} ({stats['docmap'].get('docmap_agree', 0)}/{stats['docmap'].get('docmap_compared', 0)}) over {stats['docmap'].get('docmap_companies', 0)} companies with a docmap; skipped: no period {stats['docmap'].get('docmap_no_period', 0)}, not filing-checked {stats['docmap'].get('docmap_not_filing_checked', 0)}",
         f"- Filer calc checks failing in the batch: {stats['failed_checks']}; resolver values resting on one: {stats['filer_check_items']}",
         f"- New element families (face lines no rule reads): {stats['new_families']} distinct tags (first {MAX_FAMILY_ITEMS} by company count in the queue)", '',
         '## Items by class and kind', '', '| class | kind | items |', '|---|---|---|']
    L += [f'| {c} | {k} | {n} |' for (c, k), n in sorted(by.items())]
    for title, kinds in (('Disagreements with a key', ('proof_disagree', 'docmap_disagree', 'proof_not_presented_but_valued', 'docmap_not_presented_but_valued')),
                         ('no_role cells', ('no_role',)), ('New element families', ('new_element_family',)), ('Filer checks that fail', ('filer_check_failed',))):
        sel = [i for i in items if i['kind'] in kinds]
        L += ['', f'## {title} ({len(sel)})', '']
        if not sel: L.append('none'); continue
        L += ['| class | ticker | data point | period | accession | resolver | key | evidence |', '|---|---|---|---|---|---|---|---|']
        for i in sel[:150]:
            L.append(f"| {i['class']} | {i['ticker']} | {i['data_point'] or i['tag']} | {i['period_end']} | {i['accession']} | {i['resolver_status']} {i['resolver_value']} | {i['key_source']} {i['key_value']} | {i['evidence'].replace('|', '/')[:240]} |")
        if len(sel) > 150: L.append(f'\n(first 150 of {len(sel)}; all rows are in {day}.csv)')
    open(os.path.join(out_dir, f'{day}.md'), 'w').write('\n'.join(L) + '\n')


def cmd_report(a):
    rows = list(csv.DictReader(open(os.path.join(a.out, 'resolved_all.csv'))))
    filings = json.load(open(os.path.join(a.out, 'filings.json')))
    rd = lambda n: list(csv.DictReader(open(os.path.join(a.out, n)))) if os.path.exists(os.path.join(a.out, n)) else []
    batch = list(csv.DictReader(open(os.path.join(a.out, 'batch.csv'))))
    for b in batch: b['rank'] = int(b['rank'])
    items, stats = build(rows, filings, rd('proofs.csv'), rd('checks.csv'), a.reads, a.roles, a.families, a.date, batch)
    write_report(items, stats, batch, a.drills, a.date, os.environ.get('GITHUB_SHA', ''))
    print(json.dumps({k: v for k, v in stats.items() if k != 'attempts'}, indent=1)[:1500])


def main(argv=None):
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('pick'); p.add_argument('--ranking', required=True); p.add_argument('--approvals', required=True)
    p.add_argument('--date', required=True); p.add_argument('--out', required=True); p.add_argument('--n', type=int, default=20)
    f = sp.add_parser('fetch'); f.add_argument('out')
    r = sp.add_parser('report'); r.add_argument('--out', required=True); r.add_argument('--date', required=True)
    r.add_argument('--reads', default='data-team/companies/reads'); r.add_argument('--drills', default='data-team/tags/drills')
    r.add_argument('--roles', default='data-team/tags/line_map/rules/roles.csv'); r.add_argument('--families', default='data-team/tags/line_map/rules/extract_families.txt')
    a = ap.parse_args(argv)
    {'pick': cmd_pick, 'fetch': cmd_fetch, 'report': cmd_report}[a.cmd](a)


if __name__ == '__main__':
    main()
