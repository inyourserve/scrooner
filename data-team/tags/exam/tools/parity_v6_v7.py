import csv,subprocess,sys,io,glob,os
S='/tmp/claude-0/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/scratchpad'
tick=[(r[0],r[1]) for r in csv.reader(open(f'{S}/exam/ranks.csv'))]
bad=0; n=0; rows=0; noids=0
for rk,t in tick:
    f=f'{S}/exam/lines_eng/{t}.jsonl'
    if not os.path.exists(f): continue
    a=subprocess.run(['python3',f'{S}/exam/tools/predict_v6_frozen.py',f,t,rk,f'{S}/exam',f'{S}/exam/notes.jsonl'],capture_output=True,text=True).stdout
    b=subprocess.run(['python3',f'{S}/rulesys/predict_v7.py',f,t,rk,f'{S}/rulesys/rules',f'{S}/exam/notes.jsonl'],capture_output=True,text=True)
    A=list(csv.DictReader(io.StringIO(a))); B=list(csv.DictReader(io.StringIO(b.stdout)))
    n+=1
    if len(A)!=len(B): bad+=1; print('LEN',t,len(A),len(B),b.stderr[-300:]); continue
    for x,y in zip(A,B):
        rows+=1
        if not y.get('rule_ids') and y['status'] not in ('not_presented',): noids+=1
        for k in x:
            if k=='evidence_class': continue
            if x[k]!=y.get(k): bad+=1; print('DIFF',t,x['data_point'],k,repr(x[k])[:60],repr(y.get(k))[:60]); break
        if bad>20: sys.exit(1)
print('companies',n,'rows',rows,'diffs',bad,'non-np rows without rule_ids',noids)
