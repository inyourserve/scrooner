"""Convert total_debt-2026-11-13.csv (structural line_map) to reader fix rows + a held list. Run from the repo root.
Usage: python3 data-team/tags/line_map/tools/total_debt_fixes.py [--write]   (default: report only)"""
import csv
import re
import sys
import collections
from decimal import Decimal as D
from pathlib import Path

SRC = Path('data-team/tags/line_map/total_debt-2026-11-13.csv')
FIX = Path('data-team/companies/reads/fixes')
HELD = Path('data-team/tags/line_map/total_debt-held-2026-11-13.csv')
COLS = ['data_point', 'fiscal_year', 'period_end', 'decision', 'tags', 'stmt', 'accession', 'r_page', 'printed_value', 'note']
WRITE = '--write' in sys.argv
rows = list(csv.DictReader(open(SRC)))
out = collections.defaultdict(list)
held = []
cnt = collections.Counter()
for r in rows:
    a = r['action']
    if a == 'keep':
        continue
    if a in ('review_missing_column_value', 'no_structural_node'):
        held.append(dict(ticker=r['ticker'], fiscal_year=r['fiscal_year'], period_end=r['period_end'], action=a,
                         nodes=r['nodes'], flags=r['flags'], accession=r['accession']))
        continue
    t = r['ticker']
    parts = [p for p in re.split(r'; (?=\w+=[\d.-]+ \[)', r['nodes']) if p]
    if a == 'reason_not_presented':
        out[t].append(dict(data_point='total_debt', fiscal_year=r['fiscal_year'], period_end=r['period_end'], decision='not_presented',
                           tags='', stmt='BS', accession=r['accession'], r_page=r['r_pages'], printed_value='',
                           note=f"structural line_map total_debt (tools/total_debt.py); source=line_map; no debt-role node under the balance-sheet liabilities and no lease located outside them in {r['accession']} ({r['column']} column)"))
        cnt[a] += 1
        continue
    tags, stmts, rps = [], [], []
    abs_chk = False
    for p in parts:
        m = re.match(r'(\S+?)=(\S+) \[(BS|NOTE) (.*)\]$', p, re.S)
        tag, why = m.group(1), m.group(4)
        cus = why.rstrip().endswith('custom')
        tags.append(f"{t.lower() if cus else 'us-gaap'}:{tag}")
        stmts.append(m.group(3))
        rm = re.match(r'R(\d+):', why)
        rps.append(f"R{rm.group(1)}.htm" if rm else 'NOTE')
        abs_chk |= 'location by absence: CHECK' in why
    note = f"structural line_map total_debt (tools/total_debt.py); source=line_map; {a}; {r['column']} column of {r['accession']}; sum {r['sum']}"
    if r['flags']:
        note += f"; flags: {r['flags']}"
    if abs_chk:
        note += '; location by absence: CHECK'
    out[t].append(dict(data_point='total_debt', fiscal_year=r['fiscal_year'], period_end=r['period_end'],
                       decision='component sum' if len(tags) > 1 else 'mapped', tags='+'.join(tags), stmt='+'.join(stmts),
                       accession=r['accession'], r_page='+'.join(rps), printed_value=str(D(r['sum']).quantize(D(1))), note=note))
    cnt[a] += 1
    cnt['absence_check'] += abs_chk
print(dict(cnt), 'companies', len(out), 'held', len(held))
msft_diff = []
for t, rs in sorted(out.items()):
    f = FIX / f'{t}-fixes-2026-11-13.csv'
    old = list(csv.DictReader(open(f))) if f.exists() else []
    new_keys = {x['period_end'] for x in rs}
    keep_old = []
    for o in old:
        if o['data_point'] == 'total_debt' and o['period_end'] in new_keys:
            n = next(x for x in rs if x['period_end'] == o['period_end'])
            if t == 'MSFT':
                same = D(o['printed_value']) == D(n['printed_value'])
                msft_diff.append((o['period_end'], o['printed_value'], n['printed_value'], same))
                if not same:
                    keep_old.append(o)
                    rs[:] = [x for x in rs if x['period_end'] != o['period_end']]
                continue
            print('replace old', t, o['period_end'], o['printed_value'], '->', n['printed_value'])
            continue
        keep_old.append(o)
    if WRITE:
        with open(f, 'w', newline='') as fh:
            w = csv.DictWriter(fh, COLS, extrasaction='ignore', lineterminator='\n')
            w.writeheader()
            w.writerows(keep_old + rs)
for m in msft_diff:
    print('MSFT', m)
if WRITE:
    with open(HELD, 'w', newline='') as fh:
        w = csv.DictWriter(fh, list(held[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(held)
