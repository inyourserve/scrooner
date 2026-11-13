import csv,collections,os,glob,subprocess,io,json
from datetime import date
cov=list(csv.DictReader(open('wt/data-team/strategy/top100-coverage.csv')))
ranks={r[1]:(r[0],r[2]) for r in csv.reader(open('exam/ranks.csv'))}
D=lambda s: date.fromisoformat(s)
preds=collections.defaultdict(list)  # ticker -> [(period_end, acc, {dp:row})]
for tk in sorted({x['ticker'] for x in cov}):
    if os.path.exists(f'exam/lines_eng/{tk}.jsonl') and tk in ranks:
        r=subprocess.run(['python3','wt/data-team/tags/exam/tools/predict.py',f'exam/lines_eng/{tk}.jsonl',tk,ranks[tk][0],'wt/data-team/tags/rules','exam/notes.jsonl'],capture_output=True,text=True)
        rows=list(csv.DictReader(io.StringIO(r.stdout)))
        if rows:
            per=json.loads(open(f'exam/lines_eng/{tk}.jsonl').readline())['per']
            preds[tk].append((D(per),rows[0]['acc'],{x['data_point']:x for x in rows}))
    for f in glob.glob(f'wt/data-team/tags/exam/eras/{tk}-*-prediction.csv'):
        rows=list(csv.DictReader(open(f)))
        if rows: preds[tk].append((D(rows[0]['period']),rows[0]['acc'],{x['data_point']:x for x in rows}))
def pred_for(tk,pe):
    best=None
    for per,acc,m in preds.get(tk,[]):
        d=abs((per-pe).days)
        if d<=10 and (best is None or d<best[0]): best=(d,per,acc,m)
    return best
out=[]; C=collections.Counter()
for x in cov:
    if x['class'] not in ('BLANK','DISAGREE'): continue
    tk,dp,pe=x['ticker'],x['data_point'],D(x['period_end'])
    rc=x['reason_code']; cause=fix=evid=''
    if x['class']=='DISAGREE':
        if rc=='restated_copies_disagree':
            cause,fix='proof: superseded vintages judged against the latest-filed cell (audit R13)','Engineering: compare the shown value with the latest-filed authoritative copy only (prove.py:815-822, shown.py:102-160)'
        else:
            cause,fix=f'proof DISAGREE {rc}','investigate: '+(x['reason'] or '')[:160]
        evid=f"{x['accession']} {x['tag']} shown {x['shown_value']}"
    else:
        if rc.startswith('docmap_') and rc.endswith('_not_loaded'):
            st=rc[len('docmap_'):-len('_not_loaded')]
            cause=f'loader: docmap status {st} decided but not loaded'
            fix=f'load the docmap decision as the cell reason/status ({st}); docmap {x["r_page"]}'
            p=pred_for(tk,pe)
            evid='predictor agrees: '+p[3][dp]['status'] if p and dp in p[3] and p[3][dp]['status'].replace(' ','_')==st.replace(' ','_') else ('predictor: '+p[3][dp]['status'] if p and dp in p[3] else 'no filing-matched prediction')
        elif rc=='restated_copies_disagree':
            cause,fix='proof: superseded vintages (audit R13); no served value',"Engineering: R13 fix"
        else:
            p=pred_for(tk,pe)
            if p and dp in p[3]:
                r=p[3][dp]; st=r['status']
                if st in ('mapped','component_sum','combined','component_in_note') and r['tags']:
                    if st in ('mapped','component_sum'):
                        cause=f'value in the filing, not served (map/era gap): filing {p[2]} prints it as {st} {r["tags"]}'
                        fix=f'company_tag_map {st} {r["tags"]} stmt {r["stmt"]} with an era covering {pe}; value_source {r["value_source"]}'
                    else:
                        cause=f'filing {p[2]}: {st} {r["tags"]}'
                        fix=f'reason {st} (no concept value)'
                    evid=f"{p[2]} {r['r_page'] or 'NOTE'} {r['tags']} = {r['fy0_value'] or r['fy0_api']}"
                elif st in ('not_presented','OUT'):
                    cause=f'filing {p[2]} has no such line ({st})'; fix=f'reason {st}'; evid=f"{p[2]} predictor rule {r['rule'][:80]}"
                else:
                    cause=f'predictor {st}'; fix='review'; evid=p[2]
            else:
                cause='no filing-matched prediction (FY-1, a pre-2015 window, or the 10-K absent from FSN)'
                fix='take the value from the next 10-K comparative column; same tag as the nearest year'
                near=sorted(preds.get(tk,[]),key=lambda q: abs((q[0]-pe).days))
                if near and dp in near[0][2]:
                    r=near[0][2][dp]; evid=f"nearest {near[0][1]} ({near[0][0]}): {r['status']} {r['tags']}"
    C[(x['class'],cause.split(':')[0])]+=1
    out.append(dict(rank=x['rank'],ticker=tk,data_point=dp,fiscal_year=x['fiscal_year'],period_end=x['period_end'],cls=x['class'],coverage_reason=rc,cause=cause,fix=fix,evidence=evid))
w=csv.DictWriter(open('redcells.csv','w',newline=''),fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for k,v in C.most_common(): print(v,k)
