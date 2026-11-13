import json,re,collections,csv,itertools
from decimal import Decimal as Dm
from datetime import date
t=open('/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794589849423.txt').read()
m=re.search(r'<untrusted-data-[0-9a-f-]+>\\n(.*)\\n</untrusted-data',t,re.S); L=json.loads(json.loads('"'+m.group(1)+'"'))
top={int(r['company_id']):r['ticker'] for r in csv.DictReader(open('v2/sum.csv')) if r['company_id']}; top[1949]='cid1949'
F=collections.defaultdict(lambda: collections.defaultdict(list))
for r in L:
    if r['val'] is None: continue
    F[(r['c'],r['p'])][(r['a'],r['fm'])].append(r)
T=[r for r in json.load(open('id/top.json')) if r['id']=='BS']
def unit(x):
    x=abs(x); k=0
    while k<9 and x!=0 and x%(10**(k+1))==0: k+=1
    return Dm(10)**k
def tol(*xs): return sum(unit(x)/2 for x in xs)
EQC=re.compile(r'^(StockholdersEquity|PartnersCapital|MembersEquity)')
out=[]
for r in T:
    c=r['company_id']; ed=date.fromisoformat(r['ed'])
    a,l,e=Dm(r['a']),Dm(r['l']),Dm(r['e']); diff=a-l-e
    cand=[(k,v) for (cc,p),v in F.items() if cc==c and abs((date.fromisoformat(p)-ed).days)<=20 for k,v in v.items()]
    cand.sort(key=lambda kv:(kv[0][1] not in ('10-K','10-Q'), kv[0][1]!='10-K' if r['fp']=='FY' else kv[0][1]!='10-Q'))
    rec=dict(ticker=top.get(c,c),company_id=c,identity='balance_sheet',grain=r['fp'] or 'I',period_end=r['ed'],served_assets=a,served_liabilities=l,served_equity=e,diff=diff)
    if not cand:
        rec.update(verdict='unresolved',detail='no FSN 10-K/10-Q balance sheet with this period as its own column',accession='');out.append(rec);continue
    (acc,fm),lines=cand[0]; lines=sorted(lines,key=lambda x:int(x['line']))
    pv={}
    for x in lines: pv.setdefault(x['tag'],Dm(x['val']))
    A,Lp,E,Et,LSE=pv.get('Assets'),pv.get('Liabilities'),pv.get('StockholdersEquity'),pv.get('StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'),pv.get('LiabilitiesAndStockholdersEquity')
    rec['accession']=acc; T_=tol(a,l,e)
    v=d=''
    if A is not None and abs(a-A)>tol(a,A): v,d='a_wrong_value',f'total_assets served {a}, printed Assets {A}'
    elif Lp is not None and abs(l-Lp)>tol(l,Lp): v,d='a_wrong_value',f'total_liabilities served {l}, printed Liabilities {Lp}'
    elif E is not None and abs(e-E)>tol(e,E) and not (Et is not None and abs(e-Et)<=tol(e,Et)): v,d='a_wrong_value',f'stockholders_equity served {e}, printed StockholdersEquity {E}'+(f' (incl NCI {Et})' if Et else '')
    else:
        # operands printed between liabilities and the equity total, or NCI after parent equity
        il=next((i for i,x in enumerate(lines) if x['tag']=='Liabilities'),None)
        ops=[]
        for i,x in enumerate(lines):
            tg=x['tag']
            if tg in ('Assets','Liabilities','LiabilitiesAndStockholdersEquity','StockholdersEquity','StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'): continue
            if il is not None and i<il: continue
            if re.match(r'^(PreferredStock|CommonStock|Treasury|Retained|Accumulated|AdditionalPaid)',tg) and 'Temporary' not in tg and 'Redeemable' not in tg: continue
            ops.append((tg,x['lb'],Dm(x['val'])))
        hit=None
        for n in range(1,min(4,len(ops))+1):
            for comb in itertools.combinations(ops,n):
                s=sum(o[2] for o in comb)
                if abs(diff-s)<=T_+tol(*[o[2] for o in comb]): hit=comb;break
            if hit: break
        if Lp is None and A is not None:
            lse_gap = (LSE - (Et if Et is not None else (E or 0))) if LSE is not None else None
            v,d='c_skip_or_operand',f'no printed Liabilities total (served {l} is derived); '+(f'L&E {LSE} - equity incl NCI {Et if Et is not None else E} = {lse_gap}; ' if lse_gap is not None else '')+(('operands '+'; '.join(f'{o[0]}={o[2]}' for o in hit)) if hit else 'unexplained')
        elif hit:
            v,d='b_false_break','missing operand(s): '+'; '.join(f'{o[0]} "{o[1]}" = {o[2]}' for o in hit)
        else:
            v,d='unresolved',f'printed A {A} L {Lp} E {E} Etot {Et}; diff {diff}; candidates '+'; '.join(f'{o[0]}={o[2]}' for o in ops[:6])
    rec.update(verdict=v,detail=d); out.append(rec)
json.dump([{k:str(v) for k,v in o.items()} for o in out],open('id/bs_out.json','w'))
print(collections.Counter(o['verdict'] for o in out))
