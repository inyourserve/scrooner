import pickle,collections,sys,json,csv,re
sys.path.insert(0,'.')
csv.field_size_limit(10**9)
from agg import bucket
from report_data import norm
res=pickle.load(open('final.pkl','rb'))
# ---- FSDS pair results
X='/private/tmp/claude-501/-Users-vikash-scrooner/99c20ae4-2938-4dd5-8ec6-924194f63d67/scratchpad/fsds/x/'
exec(open('fsds_check.py').read().split("UNEV=")[0].replace("res=pickle.load(open('final.pkl','rb'))","").replace("from agg import bucket",""))
FS={}  # (c,leafnorm)-> 'mapped'|'other'|'none'
def fsds_pair(c,l):
    l2=l
    if l2 in('total_debt','total_debt_split','total_debt_resolved','total_debt(+split, resolved)'): l2='total_debt'
    if l2.endswith('_resolved') and l2[:-9] in PL: l2=l2[:-9]
    if l2 not in PL or c not in pre: return None
    st,pat=PL[l2]; rx=re.compile(pat); stx=re.compile('^('+st+')$')
    tg=[t for s,t,pl in pre[c] if stx.match(s) and rx.search(t)]
    if any(t in M[l2] for t in tg): return 'mapped'
    return 'other' if tg else 'none'
def cellclass(a):
    bs=[bucket(cz) for _,cz in a['causes']]
    if 'LEGIT' in bs: return 'L'
    if 'UNEVIDENCED' in bs: return 'U'
    if 'BLOCKED' in bs or 'OTHER' in bs: return 'B'
    return 'F'
# refine U cells
ref=collections.Counter(); refbyleaf=collections.defaultdict(collections.Counter)
for a in res:
    if cellclass(a)!='U': continue
    outs=[]
    for leaf,cz in a['causes']:
        if bucket(cz)=='UNEVIDENCED':
            r=fsds_pair(a['company_id'],leaf); outs.append(r); refbyleaf[leaf][r]+=1
    if any(o in('mapped','other') for o in outs): ref['U_fsds_line_presented']+=1
    elif all(o=='none' for o in outs): ref['U_fsds_no_line']+=1
    else: ref['U_untested']+=1
print('U refinement',dict(ref))
for k,v in sorted(refbyleaf.items(),key=lambda x:-sum(x[1].values()))[:14]: print(k,dict(v))
pickle.dump(dict(ref),open('uref.pkl','wb'))
