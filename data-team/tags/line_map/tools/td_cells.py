"""Per cell (ticker, fiscal year end): the latest-filed copy (next 10-K comparative column, else own 10-K), then backtest."""
import csv, glob, re, collections, os
from decimal import Decimal as D
from datetime import date
TD = list(csv.DictReader(open('total_debt_all.csv')))
by = collections.defaultdict(list)
for r in TD: by[(r['ticker'], r['period_end'][:7])].append(r)
cells = {}
for k, rs in by.items():
    rs = [r for r in rs if r['status'] != 'not_presented' or True]
    comp = sorted([r for r in rs if r['column'] == 'comparative' and r['value']], key=lambda r: r['filing_period'], reverse=True)
    own = [r for r in rs if r['column'] == 'own']
    pick = comp[0] if comp else (own[0] if own else None)
    if pick: cells[k] = dict(pick, alt_own=(own[0]['value'] if own else ''), alt_own_acc=(own[0]['accession'] if own else ''))
def num(s):
    try: return D(str(s).replace(',', ''))
    except Exception: return None
def close(a, b): return a is not None and b is not None and abs(a - b) <= max(D(1000000), abs(b) * D('0.0005'))
res = collections.Counter(); rows = []
# hand keys: fix files and docmap FY0 rows for total_debt
for p in glob.glob('fx/*-fixes-*.csv'):
    tk = os.path.basename(p).split('-fixes')[0]
    for x in csv.DictReader(open(p)):
        if x.get('data_point') != 'total_debt': continue
        c = cells.get((tk, x['period_end'][:7])); kv = num(x.get('printed_value')); dec = (x['decision'] or '').strip()
        if c is None: res[('fix', 'no_cell')] += 1; continue
        if dec in ('mapped', 'component sum', 'component_sum') and kv is not None:
            ok = close(num(c['value']), kv) or close(num(c['alt_own']), kv)
            res[('fix', 'agree' if ok else 'DISAGREE')] += 1
            if not ok: rows.append(dict(src='fix', ticker=tk, period_end=x['period_end'], key=kv, key_tags=x.get('tags', ''), td=c['value'], td_tags=c['tags'], own=c['alt_own'], flags=c['flags']))
        else: res[('fix', 'key_' + dec)] += 1
for p in glob.glob('keys/*.csv'):
    rs = list(csv.reader(open(p))); hi = next(i for i, x in enumerate(rs) if x and x[0] == 'ticker'); hdr = rs[hi]
    for x in [dict(zip(hdr, r)) for r in rs[hi + 1:]]:
        if x.get('data_point') != 'total_debt': continue
        accs = re.findall(r'accn (\d{10}-\d{2}-\d{6}) period [^ ]*?\.\.(\d{4}-\d{2})', x.get('note', ''))
        tk = x['ticker']; kv = num(x['fy0_printed']) or num(x['fy0_api'])
        acc0 = collections.Counter(a for a, _ in accs).most_common(1)
        own = [r for r in TD if r['ticker'] == tk and r['column'] == 'own' and acc0 and r['accession'] == acc0[0][0]]
        if not own: res[('docmap', 'fy0_not_in_fsn')] += 1; continue
        last = own[0]
        st = x['status'].strip()
        if st in ('mapped', 'component sum') and kv is not None:
            ok = close(num(last['value']), kv)
            res[('docmap', 'agree' if ok else 'DISAGREE')] += 1
            if not ok: rows.append(dict(src='docmap' + (' hand' if 'check: hand' in x.get('note', '') else ''), ticker=tk, period_end=last['period_end'], key=kv, key_tags=x['tags'], td=last['value'], td_tags=last['tags'], own=last['value'], flags=last['flags']))
        else: res[('docmap', 'key_' + st)] += 1
# served cells (coverage), any class
served = collections.Counter(); out = []
for x in csv.DictReader(open('cov_now.csv')):
    if x['data_point'] != 'total_debt': continue
    c = cells.get((x['ticker'], x['period_end'][:7]))
    if c is None: served['no_structural_cell'] += 1; continue
    sv = num(x['shown_value'])
    if sv is None: served[('blank', x['class'])] += 1; out.append((x, c, 'fill')); continue
    if close(num(c['value']), sv) or close(num(c['alt_own']), sv): served[('same', x['class'])] += 1
    else: served[('differs', x['class'])] += 1; out.append((x, c, 'replace'))
print(res); print(served)
w = csv.DictWriter(open('td_backtest_disagree.csv', 'w', newline=''), fieldnames=list(rows[0].keys()) if rows else ['x']); w.writeheader(); w.writerows(rows)
fx = []
for x, c, kind in out:
    fx.append(dict(ticker=x['ticker'], data_point='total_debt', fiscal_year=x['fiscal_year'], period_end=x['period_end'], served_value=x['shown_value'], served_class=x['class'], served_reason=x['reason_code'],
                   action=kind, decision=c['status'], tags=c['tags'], value=c['value'], accession=c['accession'], column=c['column'], r_pages=c['r_pages'], parts=c['parts'], flags=c['flags'], fl_loc=c['fl_loc']))
w = csv.DictWriter(open('total_debt_fixrows.csv', 'w', newline=''), fieldnames=list(fx[0].keys())); w.writeheader(); w.writerows(fx)
print('fix rows', len(fx), collections.Counter(r['action'] for r in fx), len({r['ticker'] for r in fx if r['action'] == 'replace'}), 'companies with replacements')
