import json,collections,csv
exec(open('scripts/stats.py').read().split("fams=[]")[0])  # V1 dict
C33=['accounts_payable','accounts_receivable','basic_eps','capex','cash_and_equivalents','cash_flow_financing','cash_flow_investing','cfo','cost_of_revenue','current_assets','current_liabilities','depreciation_and_amortization_resolved','diluted_eps','dividends_paid','dividends_per_share','goodwill','income_before_tax','income_tax_expense','interest_expense','interest_income','inventory','net_income','operating_income','research_and_development','revenue','sbc','sga_expense','share_buybacks','shares_outstanding','stockholders_equity','total_assets','total_debt_resolved']
R=json.load(open('cls.json'))
top=set(str(int(r['cik'])) for r in csv.DictReader(open('/Users/vikash/scrooner/doc/data-moat/team/top1000/shards.csv')) if not r['excluded'] or r['excluded'].startswith('added'))
EXCL={'SPAC_blank_check','nofin_statements (ABS/other)','commodity_crypto_pool_trust','trust_holding_other_investor'}
# concepts that are conditional by nature (dividends/buybacks depend on activity) -> not counted as template NA
ACTIVITY={'dividends_paid','dividends_per_share','share_buybacks'}
def run(keys,label):
    byf=collections.defaultdict(list)
    for k in keys:
        r=R[k]
        if r['flags']: byf[r['fam']].append(r)
    tot=collections.Counter(); per={}
    for fam,rs in byf.items():
        n=len(rs)
        pc={c:sum(r['flags'][c] for r in rs)/n for c in C33}
        pm={m:sum(all(r['flags'][c] for c in V1[m]) for r in rs)/n for m in V1}
        struct_c=[c for c in C33 if pc[c]<=0.10 and c not in ACTIVITY]
        struct_m=[m for m in V1 if pm[m]<=0.10 and m not in('dividend_yield',)]
        var_c=[c for c in C33 if 0.10<pc[c]<0.95 and c not in ACTIVITY]
        var_m=[m for m in V1 if 0.10<pm[m]<0.95 and m!='dividend_yield']
        absent_var_c=sum(round((1-pc[c])*n) for c in var_c); absent_var_m=sum(round((1-pm[m])*n) for m in var_m)
        absent_other_c=sum(round((1-pc[c])*n) for c in C33 if pc[c]>=0.95 and c not in ACTIVITY)
        per[fam]=dict(n=n,struct_c=len(struct_c),struct_m=len(struct_m),cells_struct=n*(len(struct_c)+len(struct_m)),absent_variable=absent_var_c+absent_var_m,absent_nearly_universal=absent_other_c, struct_c_names=struct_c, struct_m_names=struct_m)
    total_cells=sum(d['n'] for d in per.values())*(len(C33)+len(V1)-1)
    print('==',label,'filers',sum(d['n'] for d in per.values()),'cells (concepts+metrics, excl activity)',total_cells)
    S=0
    for fam,d in sorted(per.items(),key=lambda x:-x[1]['cells_struct']):
        S+=d['cells_struct']
        print(f"{fam:32s} n={d['n']:5d} structNA concepts={d['struct_c']:2d} metrics={d['struct_m']:2d} cells={d['cells_struct']:6d} | variable-absent={d['absent_variable']:6d} | near-universal absent={d['absent_nearly_universal']}")
    print('TOTAL struct NA cells',S, f"{100*S/total_cells:.1f}% of cells")
    return per
allk=[k for k,r in R.items() if r['fam'] not in EXCL]
p_all=run(allk,'FSDS population (real operating shape)')
p_top=run([k for k in allk if k in top],'top-1000 subset')
json.dump(p_all,open('cells_all.json','w'))
