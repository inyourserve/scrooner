"""Backtest gate for the structural resolver: compare line_map rows with (1) reader docmap FY0 hand keys, (2) reader fix-file
hand rows, (3) Engineering's served PROVEN cells (coverage), each only where the key's filing is the 10-K that prints the period
as its own column. Output gate.csv (one row per comparison) and a summary."""
import csv, glob, os, re, collections, sys
from decimal import Decimal as D
from datetime import date
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
DPS = ['total_assets','total_liabilities','stockholders_equity','current_assets','current_liabilities','revenue','cost_of_revenue','gross_profit',
       'operating_expenses','operating_income','income_before_tax','income_tax_expense','net_income','cfo','cash_flow_investing','cash_flow_financing']
LM = {}; BYPER = {}
for f in glob.glob(f'{OUT}/*.csv'):
    for r in csv.DictReader(open(f)):
        LM[(r['ticker'], r['accession'], r['data_point'])] = r
        BYPER.setdefault((r['ticker'], r['data_point']), []).append(r)
def unit(v):
    v = abs(v); k = 0
    while k < 9 and v != 0 and v % (10 ** (k + 1)) == 0: k += 1
    return D(10) ** k
def num(s):
    try: return D(str(s).replace(',', '').strip())
    except Exception: return None
def cmp(src, tk, dp, acc, key_status, key_val, key_tags, extra=''):
    r = LM.get((tk, acc, dp))
    if r is None: return None
    st = r['status']; v = num(r['value'])
    ks = (key_status or '').strip().lower().replace(' ', '_')
    if ks in ('mapped', 'component_sum') and key_val is not None:
        if st == 'no_role': res = 'gap_no_role'
        elif v is not None and abs(v - key_val) <= max(unit(v), unit(key_val)) * D('1.5'): res = 'agree' if st != 'derived' else 'agree_derived'
        else: res = 'DISAGREE_value'
    elif ks in ('not_presented', 'combined', 'out', 'not_in_template', 'not_located'):
        res = 'agree_no_value' if st in ('no_role', 'combined') else ('derived_where_key_' + ks if st == 'derived' else 'DISAGREE_value_where_key_' + ks)
    else:
        return None
    return dict(source=src, ticker=tk, data_point=dp, accession=acc, period_end=r['period_end'], key_status=ks, key_value=key_val, key_tags=key_tags,
                lm_status=st, lm_value=r['value'], lm_tags=r['tags'], lm_lines=r['lines'], result=res, lm_path=r['path'], note=extra)
rows = []
# (1) docmap FY0 hand keys: FY0 accession = the most common 'accn' in the notes
for p in glob.glob('keys/*.csv'):
    rs = [x for x in csv.reader(open(p))]
    hdr_i = next(i for i, x in enumerate(rs) if x and x[0] == 'ticker')
    hdr = rs[hdr_i]; recs = [dict(zip(hdr, x)) for x in rs[hdr_i + 1:] if len(x) >= len(hdr) - 2]
    accs = collections.Counter(a for x in recs for a in re.findall(r'accn (\d{10}-\d{2}-\d{6})', x.get('note', '')))
    if not accs: continue
    acc0 = accs.most_common(1)[0][0]
    for x in recs:
        if x['data_point'] not in DPS: continue
        hand = 'check: hand' in x.get('note', '')
        c = cmp('docmap_hand' if hand else 'docmap', x['ticker'], x['data_point'], acc0, x['status'], num(x['fy0_printed']) or num(x['fy0_api']), x['tags'])
        if c: rows.append(c)
# (2) reader fix files (hand rows with filing values)
for p in glob.glob('fx/*-fixes-*.csv'):
    tk = os.path.basename(p).split('-fixes')[0]
    for x in csv.DictReader(open(p)):
        if x.get('data_point') not in DPS or not x.get('accession'): continue
        r = LM.get((tk, x['accession'].strip(), x['data_point']))
        if r is None or abs((date.fromisoformat(r['period_end']) - date.fromisoformat(x['period_end'])).days) > 10: continue
        c = cmp('fix_file', tk, x['data_point'], x['accession'].strip(), x['decision'], num(x.get('printed_value')), x.get('tags') or x.get('tag(s)', ''))
        if c: rows.append(c)
# (3) served PROVEN cells, own-filing only
for x in csv.DictReader(open('cov_now.csv')):
    if x['class'] != 'PROVEN' or x['data_point'] not in DPS or not x['accession']: continue
    r = LM.get((x['ticker'], x['accession'], x['data_point']))
    if r is None or abs((date.fromisoformat(r['period_end']) - date.fromisoformat(x['period_end'])).days) > 10: continue
    c = cmp('proven', x['ticker'], x['data_point'], x['accession'], 'mapped', num(x['shown_value']), x['tag'])
    if c: rows.append(c)
w = csv.DictWriter(open('gate.csv', 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
C = collections.Counter((r['source'], r['result']) for r in rows)
for k, v in sorted(C.items()): print(k, v)
