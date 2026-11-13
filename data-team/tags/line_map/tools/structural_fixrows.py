"""structural-fixrows-2026-11-13.csv -> reader fix rows (second input of the line_map fix-row job). Repo root.
Usage: python3 data-team/tags/line_map/tools/structural_fixrows.py <custom.json> [--write]
custom.json: [[accession, tag], ...] tags that are filer-custom in that filing (prefix = ticker lowercase; else us-gaap).
derived_not_printed total_liabilities -> a not_presented fix row so mapper/derived_cells.py (C2) fires;
derived_not_printed stockholders_equity (parent equity) -> unsupported by the loader and derived_cells: held, not faked."""
import csv
import json
import sys
import collections
from pathlib import Path

SRC = Path('data-team/tags/line_map/structural-fixrows-2026-11-13.csv')
FIX = Path('data-team/companies/reads/fixes')
HELD = Path('data-team/tags/line_map/structural-fixrows-held-2026-11-13.csv')
COLS = ['data_point', 'fiscal_year', 'period_end', 'decision', 'tags', 'stmt', 'accession', 'r_page', 'printed_value', 'note']
custom = {tuple(x) for x in json.load(open(sys.argv[1]))}
WRITE = '--write' in sys.argv
out = collections.defaultdict(list)
held = []
cnt = collections.Counter()
for r in csv.DictReader(open(SRC)):
    t, dp = r['ticker'], r['data_point']
    base = dict(data_point=dp, fiscal_year=r['fiscal_year'], period_end=r['period_end'], accession=r['accession'])
    rps = [x.replace(':', '.htm:').split(':')[0] for x in r['r_lines'].split(';') if x]
    if r['decision'] == 'derived_not_printed':
        if dp == 'total_liabilities':
            out[t].append(dict(base, decision='not_presented', tags='', stmt='BS', r_page='', printed_value='',
                               note=f"source=line_map; structural total_liabilities: not printed in {r['accession']} (derived_not_printed, ruling C2); {r['action']}; derived by mapper/derived_cells.py when its operands are PROVEN"))
            cnt['total_liabilities_not_presented'] += 1
        else:
            held.append(dict(ticker=t, data_point=dp, fiscal_year=r['fiscal_year'], period_end=r['period_end'], accession=r['accession'],
                             why='parent equity derived_not_printed: unsupported by docmap_loader and mapper/derived_cells.py (only C1 gross profit, C2 total liabilities)'))
            cnt['equity_derived_unsupported'] += 1
        continue
    tags = [('%s:%s' % (t.lower() if (r['accession'], x) in custom else 'us-gaap', x)) for x in r['tags'].split('+')]
    out[t].append(dict(base, decision='component sum' if r['decision'] == 'component_sum' else r['decision'], tags='+'.join(tags), stmt=r['stmt'],
                       accession=r['accession'], r_page='+'.join(dict.fromkeys(rps)), printed_value=str(int(float(r['value']))) if r['value'] else '',
                       note=f"source=line_map; {r['action']}; " + r['note']))
    cnt[dp + ':' + r['action']] += 1
print(dict(cnt), 'companies', len(out))
for t, rs in sorted(out.items()):
    seen = {}
    for x in rs:  # the source repeats a cell under two actions: keep one, report a value conflict
        k = (x['data_point'], x['period_end'])
        if k in seen and (seen[k]['tags'], seen[k]['printed_value']) != (x['tags'], x['printed_value']):
            print('DUP CONFLICT', t, k, seen[k]['printed_value'], x['printed_value'])
        seen.setdefault(k, x)
    rs[:] = list(seen.values())
    f =FIX / f'{t}-fixes-2026-11-13.csv'
    old = list(csv.DictReader(open(f))) if f.exists() else []
    keys = {(x['data_point'], x['period_end']) for x in rs}
    kept = [o for o in old if (o['data_point'], o['period_end']) not in keys]
    for o in old:
        if (o['data_point'], o['period_end']) in keys:
            n = next(x for x in rs if (x['data_point'], x['period_end']) == (o['data_point'], o['period_end']))
            print('replaces', t, o['data_point'], o['period_end'], o['decision'], o['tags'], o['printed_value'], '->', n['decision'], n['tags'], n['printed_value'])
    if WRITE:
        with open(f, 'w', newline='') as fh:
            w = csv.DictWriter(fh, COLS, extrasaction='ignore', lineterminator='\n')
            w.writeheader()
            w.writerows(kept + rs)
if WRITE and held:
    with open(HELD, 'w', newline='') as fh:
        w = csv.DictWriter(fh, list(held[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(held)
