import pickle,collections,sys
sys.path.insert(0,'.')
from agg import bucket
from report_data import norm
res=pickle.load(open('final.pkl','rb'))
cells,comps,frac,bmix,gs=pickle.load(open('leafagg.pkl','rb'))
sysk=lambda k:k.startswith(('ENGINE','COMPANY'))
# top 25 leaves (non-system) by cells explained
rank=[k for k in sorted(cells,key=lambda k:-len(cells[k])) if not sysk(k)][:25]
GR=['corporate','reit','bank','utility','other_financial','insurer','energy','bdc_fund_or_unclassified']
print('| # | leaf | cells | cos | LEGIT | UNEV | FIX | FIX_PER | '+' | '.join(GR)+' |')
for i,k in enumerate(rank,1):
    m=bmix[k]; print(f"| {i} | {k} | {len(cells[k])} | {len(comps[k])} | {m['LEGIT']} | {m['UNEVIDENCED']} | {m['FIX']} | {m['FIX_PERIOD']+m['FEED']} | "+' | '.join(str(gs[k][g]) for g in GR)+' |')
print('SYSTEM')
for k in cells:
    if sysk(k): print(k,len(cells[k]),len(comps[k]),dict(gs[k]))
# top10 fixable leaves
fixc=collections.Counter()
for i,a in enumerate(res):
    for k in {norm(l,cz) for l,cz in a['causes'] if bucket(cz) in('FIX','FIX_PERIOD')}:
        if not sysk(k): fixc[k]+=1
top10=[k for k,_ in fixc.most_common(10)]; print('TOP10 fixable',[(k,fixc[k]) for k in top10])
def gain(T,bk):
    n=0
    for a in res:
        ok=True
        for l,cz in a['causes']:
            if not(norm(l,cz) in T and bucket(cz) in bk): ok=False;break
        n+=ok
    return n
print('A (FIX only)',gain(set(top10),('FIX',)),'B (FIX+PERIOD)',gain(set(top10),('FIX','FIX_PERIOD')))
print('system engine+feed all',gain({k for k in cells if sysk(k)},('ENGINE','FEED')))
allsys=set(top10)|{k for k in cells if sysk(k)}
print('top10+system',gain(allsys,('FIX','FIX_PERIOD','ENGINE','FEED')))
print('all fixable everywhere',gain(set(cells),('FIX','FIX_PERIOD','ENGINE','FEED')))
