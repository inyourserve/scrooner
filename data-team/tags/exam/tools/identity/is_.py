import json,re,collections,csv,itertools
from decimal import Decimal as Dm
from datetime import date
t=open('/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794589943242.txt').read()
m=re.search(r'<untrusted-data-[0-9a-f-]+>\\n(.*)\\n</untrusted-data',t,re.S); L=json.loads(json.loads('"'+m.group(1)+'"'))
top={int(r['company_id']):r['ticker'] for r in csv.DictReader(open('v2/sum.csv')) if r['company_id']}; top[1949]='cid1949'
F=collections.defaultdict(list)
for r in L: F[(r['c'],r['p'],int(r['q']))].append(r)
def unit(x):
    x=abs(x); k=0
    while k<9 and x!=0 and x%(10**(k+1))==0: k+=1
    return Dm(10)**k
def tol(*xs): return sum(unit(x)/2 for x in xs)
T=[r for r in json.load(open('id/top.json')) if r['id']!='BS']
out=[]
for r in T:
    c=r['company_id']; ed=date.fromisoformat(r['ed']); sd=date.fromisoformat(r['sd']); days=(ed-sd).days
    q=4 if days>300 else 1 if days<120 else None
    rec=dict(ticker=top.get(c,c),company_id=c,identity='gross_profit' if r['id']=='GP' else 'operating_income',grain=r['fp'] or f'{days}d',period_start=r['sd'],period_end=r['ed'],diff=r['diff'])
    if r['id']=='GP': names=['revenue','cost_of_revenue','gross_profit']
    else: names=['gross_profit' if not r['a'].startswith('R-C') else 'revenue_minus_cor','operating_expenses','operating_income']
    vals=[Dm(r['a'].replace('R-C:','')),Dm(r['l']),Dm(r['e'])]
    rec['served']='; '.join(f'{n}={v}' for n,v in zip(names,vals))
    if q is None:
        rec.update(verdict='c_skip',detail=f'served period of {days} days is not a filed column (neither a quarter nor a year): the identity should skip non-filed spans',accession='');out.append(rec);continue
    cand=[(k,v) for k,v in F.items() if k[0]==c and k[2]==q and abs((date.fromisoformat(k[1])-ed).days)<=20]
    if not cand:
        why='Q4 is derived (FY minus nine months), no filed Q4 column' if (r['fp']=='Q4' or (q==1 and ed.month in (12,1))) else 'no FSN filing with this period as its own column'
        rec.update(verdict='c_skip' if 'Q4' in why else 'unresolved',detail=why,accession='');out.append(rec);continue
    lines=sorted(cand[0][1],key=lambda x:(x['a'],int(x['line'])))
    acc=lines[0]['a']; lines=[x for x in lines if x['a']==acc]
    rec['accession']=acc
    pv=[(x['tag'],x['lb'],Dm(x['val'])) for x in lines]
    def match(v): return [p for p in pv if abs(abs(p[2])-abs(v))<=tol(v,p[2])]
    unm=[(n,v) for n,v in zip(names,vals) if n!='revenue_minus_cor' and not match(v)]
    if unm:
        n,v=unm[0]
        rec.update(verdict='a_wrong_value' if n!='operating_expenses' else 'b_or_a_opex',detail=f'served {n} {v} is not any printed IS line of {acc}; printed: '+'; '.join(f'{p[0]}={p[2]}' for p in pv[:12]))
    else:
        used={match(v)[0][0] for n,v in zip(names,vals) if n!='revenue_minus_cor'}
        diff=Dm(r['diff']); ops=[p for p in pv if p[0] not in used]
        hit=None
        for n_ in range(1,4):
            for comb in itertools.combinations(ops,n_):
                s=sum(o[2] for o in comb)
                if abs(abs(diff)-abs(s))<=tol(*vals)+tol(*[o[2] for o in comb]): hit=comb;break
            if hit: break
        rec.update(verdict='b_false_break' if hit else 'unresolved',detail=('every member is a printed line; missing operand(s): '+'; '.join(f'{o[0]} "{o[1]}" = {o[2]}' for o in hit)) if hit else 'members are printed lines but no printed line explains the diff; printed: '+'; '.join(f'{p[0]}={p[2]}' for p in pv[:14]))
    out.append(rec)
json.dump([{k:str(v) for k,v in o.items()} for o in out],open('id/is_out.json','w'))
print(collections.Counter((o['identity'],o['verdict']) for o in out))
