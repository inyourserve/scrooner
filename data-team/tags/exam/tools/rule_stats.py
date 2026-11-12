"""Per-rule scores from the ledger (LEARNING-SYSTEM.md §3). Usage: rule_stats.py LEDGER_CSV RULES_DIR [GRADED_ON_PREFIX] > markdown
Counts hand-verified correct/wrong rows only. Weak = accuracy < 95% over >= 20 fires. Dead = 0 fires."""
import csv, glob, os, sys
from collections import defaultdict
led, rdir = sys.argv[1], sys.argv[2]; pref = sys.argv[3] if len(sys.argv) > 3 else 'replay'
rules = {r['rule_id']: r for f in glob.glob(os.path.join(rdir, '*.csv')) for r in csv.DictReader(open(f))}
st = defaultdict(lambda: [0, 0, ''])
for r in csv.DictReader(open(led)):
    if not r['graded_on'].startswith(pref) or r['result'] not in ('correct', 'wrong') or r['key_evidence'] not in ('hand', ''): continue
    for rid in [x for x in r['rule_ids'].split(';') if x]:
        s = st[rid]; s[0] += 1
        if r['result'] == 'wrong': s[1] += 1; s[2] = f"{r['ticker']} {r['data_point']}: key {r['key_status']} {r['key_tags'][:40]} / pred {r['pred_status']}"
print(f'## Rules\n\nRules: {len(rules)} ({", ".join(f"{ns} {sum(1 for x in rules.values() if x["namespace"] == ns)}" for ns in sorted({x["namespace"] for x in rules.values()}))}). Fired at least once (graded {pref} rows, hand keys): {len(st)}. Dead (0 fires so far): {len([r for r in rules if r not in st])}.\n')
weak = sorted([(100 * (n - k) / n, rid, n, k, last) for rid, (n, k, last) in st.items() if n >= 20 and (n - k) / n < 0.95])
print('### Weak rules (accuracy < 95% over >= 20 fires): repair list\n\n| Rule | Fires | Wrong | Accuracy | Last wrong case |\n|---|---|---|---|---|')
for a, rid, n, k, last in weak: print(f'| {rid} | {n} | {k} | {a:.1f}% | {last} |')
print('\n### Most-fired rules\n\n| Rule | Fires | Wrong | Accuracy |\n|---|---|---|---|')
for rid, (n, k, _) in sorted(st.items(), key=lambda x: -x[1][0])[:25]: print(f'| {rid} | {n} | {k} | {100*(n-k)/n:.1f}% |')
