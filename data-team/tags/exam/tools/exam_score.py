"""Blind-exam scoreboard section. Usage: exam_score.py GRADE_CSV TIMING_CSV DEV_GRADE_CSV > markdown"""
import csv, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grade import cp_upper
STMT = {'BS': {'accounts_payable','accounts_receivable','cash_and_equivalents','current_assets','current_liabilities','goodwill','inventory','ppe_net','shares_outstanding','stockholders_equity','total_assets','total_debt','total_liabilities','deposits','loans_net'},
        'CF': {'capex','cash_flow_financing','cash_flow_investing','cfo','cf_ap_change','cf_ar_change','cf_inventory_change','depreciation_and_amortization','dividends_paid','sbc','share_buybacks'},
        'NOTE-type': {'cash_paid_for_interest','cash_paid_for_income_taxes','amortization_of_intangibles','interest_income','weighted_basic_shares','weighted_diluted_shares','dividends_per_share'}}
def stmt(dp):
    for k, v in STMT.items():
        if dp in v: return k
    return 'IS'
g, t = sys.argv[1], sys.argv[2]
R = [r for r in csv.DictReader(open(g))]
T = {r['ticker']: r for r in csv.DictReader(open(t))}
G = [r for r in R if r['result'] in ('correct', 'wrong')]
def line(rows, name):
    n = len(rows); k = sum(r['result'] == 'wrong' for r in rows)
    return f"| {name} | {n} | {100*(n-k)/max(n,1):.1f}% | {100*cp_upper(k,n):.1f}% |"
print('## Blind exam (predictions committed before each docmap; graded by tools/grade.py)\n')
tick = sorted({r['ticker'] for r in G}, key=lambda x: T.get(x, {}).get('docmap_first_commit', ''))
print(f"Companies graded: {len(tick)}; rows graded {len(G)}; key errors set aside {sum(r['result']=='key_error' for r in R)}; key rows not hand-verified by the reader (set aside) {sum(r['result']=='key_unverified' for r in R)}; no_prediction {sum(r['result']=='no_prediction' for r in R)}.\n")
print('| Scope | Rows | Accuracy | Error upper bound (CP 95%) |\n|---|---|---|---|')
H = [r for r in G if r.get('key_evidence', 'hand') in ('hand', '')]; M = [r for r in G if r.get('key_evidence') == 'machine']
print(line(H, 'HEADLINE: hand-verified key rows'))
print(line(M, 'Machine full-filing key rows'))
print(line(G, 'All graded rows (hand + machine)'))
for i in range(0, len(tick), 100):
    ts = set(tick[i:i+100]); print(line([r for r in G if r['ticker'] in ts], f'Companies {i+1}-{i+len(ts)} (in grading order)'))
for s in ('BS', 'IS', 'CF', 'NOTE-type'):
    print(line([r for r in G if stmt(r['data_point']) == s], f'Statement {s}'))
sp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inputs', 'sectors.csv')
if os.path.exists(sp):
    SEC = {r['ticker']: r for r in csv.DictReader(open(sp))}
    for key, name in (('sector', 'Sector'), ('template_group', 'Template group')):
        vals = sorted({SEC.get(r['ticker'], {}).get(key, '(none)') for r in G})
        for v in vals:
            rows_ = [r for r in G if SEC.get(r['ticker'], {}).get(key, '(none)') == v]
            print(line(rows_, f'{name}: {v} ({len({r["ticker"] for r in rows_})} cos)'))
print('\n### Graduation per data-point class (founder direction 2026-11-12: blind accuracy >= 99% over the last 200 unseen companies AND CP upper error <= 1.5%, hand-verified rows only)\n')
print('| Class (data point) | Companies (last 200) | Hand rows | Hand accuracy | CP upper error (hand) | Graduated | Machine accuracy (rows) | Hand vs machine > 2 pts |\n|---|---|---|---|---|---|---|---|')
last = set(tick[-200:])
for dp in sorted({r['data_point'] for r in G}):
    rows_ = [r for r in H if r['data_point'] == dp and r['ticker'] in last]
    mrows = [r for r in M if r['data_point'] == dp and r['ticker'] in last]
    n = len(rows_); k = sum(r['result'] == 'wrong' for r in rows_); ub = cp_upper(k, n)
    grad = 'yes' if n and (n - k) / n >= 0.99 and ub <= 0.015 and len(last) >= 200 else 'no'
    ma = (100 * sum(r['result'] == 'correct' for r in mrows) / len(mrows)) if mrows else None
    ha = 100 * (n - k) / max(n, 1)
    flag = 'FLAG' if (ma is not None and n and abs(ma - ha) > 2) else ''
    print(f'| {dp} | {len({r["ticker"] for r in rows_})} | {n} | {ha:.1f}% | {100*ub:.1f}% | {grad} | {"" if ma is None else f"{ma:.1f}% ({len(mrows)})"} | {flag} |')
if len(sys.argv) > 3 and os.path.exists(sys.argv[3]):
    D = [r for r in csv.DictReader(open(sys.argv[3])) if r['result'] in ('correct', 'wrong')]
    print(line(D, 'Dev set (ranks 51-100, current predictor; not blind)'))
print('\nBar: 99% line accuracy on unseen companies over the last 200 companies, no sector at or below 95%. Sector = core.company.sector; template group = data-team/strategy/data/s2_group_audit/sample.csv (unmapped where the audit has no row).')
