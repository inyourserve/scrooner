import pickle,collections,sys,json
sys.path.insert(0,'.')
from agg import bucket
res=pickle.load(open('final.pkl','rb'))
def norm(leaf,cz):
    if cz.startswith('ENGINE'): return 'ENGINE:'+cz.split('|')[0]
    if cz.startswith('COMPANY'): return 'COMPANY:latest_10Q_not_in_SEC_facts'
    if leaf in('total_debt','total_debt_split','total_debt_resolved'): return 'total_debt(+split, resolved)'
    return leaf
# cell classes
def cellclass(a):
    bs=[bucket(cz) for _,cz in a['causes']]
    if 'LEGIT' in bs: return '1_legit_absence_propagating'
    if 'UNEVIDENCED' in bs: return '2_unevidenced_absence_or_vocab_unknown'
    if 'BLOCKED' in bs or 'OTHER' in bs: return '5_other_blocked'
    if all(b in('ENGINE',) for b in bs): return '3a_engine_fix'
    if all(b in('ENGINE','FEED') for b in bs): return '3b_engine_or_feed'
    return '3_fixable_leaf_or_period'
cc=collections.Counter(); byc=collections.defaultdict(collections.Counter)
for a in res:
    k=cellclass(a); cc[k]+=1; byc[a['cls']][k]+=1
print('CELL CLASSES',dict(cc),sum(cc.values()))
for k,v in byc.items(): print(k,dict(v),sum(v.values()))
# per group
g=collections.defaultdict(collections.Counter)
for a in res: g[a['group']][cellclass(a)]+=1
for k,v in g.items(): print('GROUP',k,sum(v.values()),dict(v))
# leaf table
cells=collections.defaultdict(set); comps=collections.defaultdict(set); frac=collections.Counter(); bmix=collections.defaultdict(collections.Counter); gsplit=collections.defaultdict(collections.Counter)
for i,a in enumerate(res):
    keys=collections.defaultdict(list)
    for leaf,cz in a['causes']: keys[norm(leaf,cz)].append(cz)
    n=len(keys)
    for k,czs in keys.items():
        cells[k].add(i); comps[k].add(a['company_id']); frac[k]+=1.0/n
        for cz in set(czs): bmix[k][bucket(cz)]+=1
        gsplit[k][a['group']]+=1
rank=sorted(cells,key=lambda k:-len(cells[k]))
out=[]
for k in rank[:40]:
    out.append(dict(leaf=k,cells=len(cells[k]),frac=round(frac[k]),companies=len(comps[k]),mix=dict(bmix[k]),groups=dict(gsplit[k])))
json.dump(out,open('leafrank.json','w'),indent=1)
for o in out[:30]: print(o['leaf'],o['cells'],o['frac'],o['companies'],o['mix'],dict(sorted(o['groups'].items(),key=lambda x:-x[1])[:4]))
pickle.dump((cells,comps,frac,bmix,gsplit),open('leafagg.pkl','wb'))
