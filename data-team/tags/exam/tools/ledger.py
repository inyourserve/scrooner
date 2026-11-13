"""Evidence ledger (LEARNING-SYSTEM.md §3). Append graded rows: one row per graded data point.
Usage: ledger.py GRADE_CSV PRED_DIR GRADED_ON LEDGER_CSV [SECTORS_CSV]
GRADED_ON: blind_as_committed (prediction committed before the docmap) or replay_<version> (current rules re-run on read companies)."""
import csv, os, sys, datetime
g, pdir, graded_on, led = sys.argv[1:5]
sec = {}
if len(sys.argv) > 5 and os.path.exists(sys.argv[5]):
    for r in csv.DictReader(open(sys.argv[5])):
        gname = r['template_group']
        if gname in ('', 'unmapped'):
            gname = {'Utilities': 'utility', 'Real Estate': 'reit', 'Energy': 'energy', 'Financials': 'financial (unclassified)'}.get(r['sector'], 'corporate')
        sec[r['ticker']] = gname
COLS = ['ledger_date', 'graded_on', 'ticker', 'data_point', 'template_group', 'predictor_version', 'rule_ids', 'pred_status', 'pred_tags', 'key_status', 'key_tags', 'key_evidence', 'result', 'error_class']
preds = {}
def pred(t):
    if t not in preds:
        f = f'{pdir}/{t}-prediction.csv'
        preds[t] = {r['data_point']: r for r in csv.DictReader(open(f))} if os.path.exists(f) else {}
    return preds[t]
new = not os.path.exists(led)
w = csv.DictWriter(open(led, 'a', newline=''), fieldnames=COLS)
if new: w.writeheader()
today = datetime.date.today().isoformat(); n = 0
for r in csv.DictReader(open(g)):
    if r['result'] not in ('correct', 'wrong', 'key_error', 'key_unverified', 'no_prediction'): continue
    p = pred(r['ticker']).get(r['data_point'], {})
    ver = (p.get('evidence_class') or '').replace('PREDICTED (predict.py ', '').rstrip(')') or ('v1-v4 (no version column)' if p else '')
    w.writerow(dict(ledger_date=today, graded_on=graded_on, ticker=r['ticker'], data_point=r['data_point'], template_group=sec.get(r['ticker'], 'corporate'),
                    predictor_version=ver, rule_ids=p.get('rule_ids', ''), pred_status=r['pred_status'], pred_tags=r['pred_tags'], key_status=r['key_status'],
                    key_tags=r['key_tags'], key_evidence=r.get('key_evidence', ''), result=r['result'], error_class=r['error_class'])); n += 1
print('appended', n)
