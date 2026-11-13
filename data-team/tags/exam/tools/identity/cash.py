import json,re,collections,csv
from decimal import Decimal as Dm
t=open('/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794590024533.txt').read()
m=re.search(r'<untrusted-data-[0-9a-f-]+>\\n(.*)\\n</untrusted-data',t,re.S); R=json.loads(json.loads('"'+m.group(1)+'"'))
top={int(r['company_id']):r['ticker'] for r in csv.DictReader(open('v2/sum.csv')) if r['company_id']}; top[1949]='cid1949'
FX=('EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents','EffectOfExchangeRateOnCashAndCashEquivalents')
CH=('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect','CashAndCashEquivalentsPeriodIncreaseDecrease','CashPeriodIncreaseDecrease')
EX=('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect','CashAndCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect')
PR={'cfo':'NetCashProvidedByUsedInOperatingActivities','cash_flow_investing':'NetCashProvidedByUsedInInvestingActivities','cash_flow_financing':'NetCashProvidedByUsedInFinancingActivities'}
DISC=('CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations','CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations','CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations','CashProvidedByUsedInDiscontinuedOperations')
out=[]
for r in R:
    s={k:Dm(v) for k,v in json.loads(r['served']).items()}; p={k:Dm(str(v)) for k,v in json.loads(r['printed']).items()}
    ch=next((p[t] for t in CH if t in p),None); fx=next((p[t] for t in FX if t in p),None)
    if ch is None: continue  # v5 skips: no printed change
    flows=sum(s.values()); diff=flows+(fx or 0)-ch
    rec=dict(ticker=top.get(r['c'],r['c']),company_id=r['c'],identity='cash_change',grain='FY',period_end=r['ed'],accession=r['accession'],diff=diff,served='; '.join(f'{k}={v}' for k,v in s.items()))
    wrong=[(k,v,p[PR[k]]) for k,v in s.items() if PR[k] in p and abs(v-p[PR[k]])>2000000]
    disc=[(t,p[t]) for t in DISC if t in p]
    if fx is None and any(t in p for t in EX):
        v,d='c_skip','no exchange-rate line printed: v5 skips'
    elif wrong:
        v,d='a_wrong_value','; '.join(f'served {k} {a} vs printed {PR[k]} {b}' for k,a,b in wrong)
    elif disc and abs(diff+sum(x for _,x in disc))<=3000000 or (disc and abs(diff-sum(x for _,x in disc))<=3000000):
        v,d='b_false_break','missing operand(s): '+'; '.join(f'{t}={x}' for t,x in disc)
    elif fx is None:
        v,d='c_skip','no exchange-rate line printed: v5 skips (my check assumed 0)'
    else:
        cont=[t for t in ('NetCashProvidedByUsedInOperatingActivitiesContinuingOperations','NetCashProvidedByUsedInInvestingActivitiesContinuingOperations','NetCashProvidedByUsedInFinancingActivitiesContinuingOperations') if t in p]
        v,d='unresolved',f'printed change {ch}, fx {fx}, flows {flows}; printed flows '+'; '.join(f'{k}={p.get(PR[k])}' for k in PR)+('; continuing-ops lines: '+','.join(cont) if cont else '')
    rec.update(verdict=v,detail=d); out.append(rec)
json.dump([{k:str(v) for k,v in o.items()} for o in out],open('id/cash_out.json','w'))
print(len(R),len(out),collections.Counter(o['verdict'] for o in out))
for o in out:
    if o['verdict'] in ('unresolved','a_wrong_value'): print(o['ticker'],o['period_end'],o['diff'],o['detail'][:230])
