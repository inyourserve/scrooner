import json,re,collections
DEBT=re.compile(r'Debt|Borrowing|NotesPayable|CommercialPaper|LineOfCredit|LinesOfCredit|LoansPayable|SeniorNotes')
OUTSIDE=re.compile(r'OtherLiabilit|AccruedLiabilit|AccountsPayable|OtherAccrued')
OTHER=r'^(InterestExpense|InterestExpenseNonoperating|InterestExpenseOther|InterestAndDebtExpense|InterestFeeAndBondIssueCostAmortizationExpense|InterestExpenseRelatedParty|InterestExpenseLongTermDebt|InterestExpenseShortTermBorrowings|InterestExpenseBorrowings)$'
inst={}
for l in open('eras/instances.jsonl'):
    d=json.loads(l); inst[d['acc']]=d
stats=collections.Counter()
def loc_of(d):
    L=d.get('fl_list') or []
    if L:
        if any(DEBT.search(x) for x in L) and not any(OUTSIDE.search(x) for x in L): return 'in'
        if all(OUTSIDE.search(x) for x in L): return 'out'
        return 'none'
    P=[x for x in (d.get('cl_parents') or []) if not re.search(r'_(Liabilities|LiabilitiesCurrent|LiabilitiesNoncurrent|LiabilitiesAndStockholdersEquity)$|NetCashProvided|FutureMinimumPayments', x)]
    if P:
        if any(DEBT.search(x) for x in P): return 'in'
        if any(OUTSIDE.search(x) for x in P): return 'out'
    return 'none'
def series_of(d):
    F=d.get('interest_facts') or []
    ser=[f for f in F if f[0]=='us-gaap' and f[1]=='InterestExpenseDebt' and f[3] and 'us-gaap:DebtInstrumentAxis' in f[3]]
    if not ser or [f for f in F if f[0]=='us-gaap' and f[1]=='InterestExpenseDebt' and not f[2]]: return None
    m={tuple(sorted(f[2])):f[4] for f in ser}
    vals=list(m.items()); agg=[k for k,v in vals if len(vals)>2 and abs(v-sum(x for kk,x in vals if kk!=k))<=1000]
    for k in agg: m.pop(k)
    other=[f for f in F if not f[2] and re.search(OTHER,f[1]) and f[4]!=0]
    fl=[f for f in F if not f[2] and f[1] in ('FinanceLeaseInterestExpense','InterestExpenseCapitalLeases') and f[4]>0]
    fac=[f for f in ser if re.search(r'(?i)credit|revolv|termloan|lineof|linesof|facility',' '.join(f[2]))]
    return dict(sum=sum(m.values()),n=len(m),only_series=not other and not fl and not fac,aggregate_tie=bool(agg))
out=[]
for l in open('eras/notes_eras.jsonl'):
    o=json.loads(l); d=inst.get(o['acc'])
    if d and 'error' not in d:
        o['fl_loc']=loc_of(d); stats['fl_loc_'+o['fl_loc']]+=1
        ds=series_of(d)
        if ds: o['debt_series']=ds; stats['debt_series']+=1
        cl=d.get('capital_lease') or {}
        add=[f'{k}=0:{v:.4f}' for k,v in cl.items() if f'{k}=0:' not in (o['facts'] or '')]
        if add: o['facts']='|'.join([x for x in [o['facts']]+add if x]); stats['capital_lease_facts']+=1
    else: stats['no_instance']+=1
    out.append(json.dumps(o))
open('eras/notes_eras2.jsonl','w').write('\n'.join(out)+'\n')
print(stats)
