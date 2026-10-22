import pickle,collections,sys
sys.path.insert(0,'.')
res=pickle.load(open('final.pkl','rb'))
def bucket(cz):
    z=cz.split('|')[0]; e=cz.split('|')[1] if '|' in cz else ''
    if cz.startswith('ENGINE'): return 'ENGINE'
    if cz.startswith('COMPANY'): return 'FEED'
    if cz.startswith('LEGIT') or e.startswith('LEGIT'): return 'LEGIT'
    if cz.startswith('UNEVIDENCED') or e.startswith('UNEVIDENCED'): return 'UNEVIDENCED'
    if cz.startswith('BLOCKED'): return 'BLOCKED'
    if cz.startswith('FIX') or e.startswith('FIX'): return 'FIX'
    if z.startswith(('PERIOD_q4','PERIOD_quarter','PERIOD_latest_quarter_only','PERIOD_ytd','PERIOD_missing_quarter','PERIOD_other_quarters','PERIOD_gap_other','PERIOD_FY_input','PERIOD_FY_other','PERIOD_duration','PERIOD_FY_only','PERIOD_other')): return 'FIX_PERIOD'
    return 'OTHER'
if __name__=='__main__':
    tot=collections.Counter(); byleaf=collections.defaultdict(lambda:collections.Counter())
    for a in res:
        n=len(a['causes'])
        for leaf,cz in a['causes']:
            b=bucket(cz); tot[b]+=1.0/n
            key=('ENGINE:'+cz) if cz.startswith('ENGINE') else leaf
            byleaf[key][b]+=1.0/n
    print({k:round(v) for k,v in tot.items()})
    rank=sorted(byleaf.items(),key=lambda x:-sum(x[1].values()))
    for k,v in rank[:30]: print(k,round(sum(v.values())),{a:round(b) for a,b in v.items()})
    # which nodes dominate ttm_stale unevidenced
    c2=collections.Counter()
    for a in res:
        for leaf,cz in a['causes']:
            if cz.startswith('PERIOD_ttm_stale') : c2[(leaf,cz.split('|')[1] if '|' in cz else '')]+=1
    print(c2.most_common(12))
