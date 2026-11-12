"""Generated rule cards (LEARNING-SYSTEM.md §1: cards are views of rules + stats; never edit by hand).
Usage: gen_cards.py RULES_DIR LEDGER_CSV OUT_DIR"""
import csv, glob, os, sys, json
from collections import defaultdict
rdir, led, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
st = defaultdict(lambda: [0, 0])
if os.path.exists(led):
    for r in csv.DictReader(open(led)):
        if r['graded_on'].startswith('replay') and r['result'] in ('correct', 'wrong') and r['key_evidence'] in ('hand', ''):
            for rid in filter(None, r['rule_ids'].split(';')):
                st[rid][0] += 1; st[rid][1] += r['result'] == 'wrong'
for f in sorted(glob.glob(os.path.join(rdir, '*.csv'))):
    ns = os.path.basename(f)[:-4]; rows = list(csv.DictReader(open(f)))
    L = [f'# Rules: {ns} (GENERATED from rules/{ns}.csv and exam/results/ledger.csv — do not edit by hand)', '',
         f'{len(rows)} rules. Stats = replay rows with hand-verified keys (fires / wrong / accuracy).', '']
    by = defaultdict(list)
    for r in rows: by[r['data_point'] or '(structural)'].append(r)
    for dp in sorted(by):
        L += [f'## {dp}', '', '| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |', '|---|---|---|---|---|---|---|---|---|']
        for r in by[dp]:
            n, k = st.get(r['rule_id'], (0, 0))
            w = r['when'].replace('|', '\\|')[:140]; t = r['then'].replace('|', '\\|')[:100]
            L.append(f"| {r['rule_id']} | {r['kind']} | {r['scope']} | `{w}` | `{t}` | {(r['evidence'] or '').replace('|','/')[:120]} | {n} | {k} | {'' if not n else f'{100*(n-k)/n:.1f}%'} |")
        L.append('')
    open(os.path.join(out, f'{ns}.md'), 'w').write('\n'.join(L) + '\n')
print('cards written')
