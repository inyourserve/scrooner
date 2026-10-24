import sys,pickle,collections,datetime
sys.path.insert(0,'.')
from attrib import *
res=pickle.load(open('res.pkl','rb'))
mv={}
for l in open('mv_latest.tsv'):
    f=l.rstrip('\n').split('\t'); mv[(int(f[0]),f[1])]=dict(label=f[2],start=f[3],end=f[4],hv=f[5]=='t',reason=f[6])
facts=collections.defaultdict(list)   # (c,concept)->[(start,end,fp,fy)]
for l in open('facts_recent.tsv'):
    f=l.rstrip('\n').split('\t'); facts[(int(f[0]),f[1])].append((f[2],f[3],f[4],f[5]))
pg=collections.defaultdict(set)  # (c,concept,end)->causes
for l in open('pgap.tsv'):
    f=l.rstrip('\n').split('\t'); pg[(int(f[0]),f[1],f[3])].add(f[4])
d=datetime.date.fromisoformat
def fl(c,n):
    out=[]
    for x in sib(n): out+=facts.get((c,x),[])
    return out
def base_of(n):
    return n
INSTANT_NODES=set(k for k,v in G.items() if v.get('basis')=='instant')
def leafnodes(n):
    """flatten metric/derived node to underlying concept nodes (for diagnosis)"""
    k=G[n]['kind']
    if k in('leaf_concept','resolved_concept'): return [n]
    if k=='derived_concept': return [n]
    if k in('metric','price_metric'):
        out=[]
        for x,_ in G[n]['inputs']:
            if x in G and G[x]['kind']!='external_source' and x!='price': out+=leafnodes(x)
        return list(dict.fromkeys(out))
    return []
def ttm_diag(c,node,asof):
    """why 4 trailing quarters of concept node are not all present"""
    q=[(e,fp,fy) for s,e,fp,fy in fl(c,node) if fp in('Q1','Q2','Q3','Q4')]
    ends=sorted({e for e,_,_ in q},reverse=True)
    if not q:
        fy=[1 for s,e,fp,fy in fl(c,node) if fp=='FY']
        return ('FY_only_no_quarters' if fy else 'no_recent_facts'),None
    e1=d(ends[0]); age=(asof-e1).days
    if age>150: return 'stale_latest_quarter_gt150d',None
    # trailing 4 expected quarter ends by spacing ~91d
    present=0; missing=[]
    cur=e1
    for i in range(4):
        hit=[e for e in ends if abs((d(e)-cur).days)<=20]
        if hit: present+=1
        else: missing.append(cur)
        cur=cur-datetime.timedelta(days=91)
    if present==4: return 'quarters_present_other',None
    causes=set()
    for me in missing:
        for x in sib(node):
            for dd in range(-20,21):
                cs=pg.get((c,x,(me+datetime.timedelta(days=dd)).isoformat()))
                if cs: causes|=cs
    cause='gap_unclassified'
    if 'q4_not_derived' in causes: cause='q4_not_derived'
    elif 'quarter_not_derived' in causes: cause='quarter_not_derived'
    elif causes: cause='other:'+','.join(sorted(causes))
    return 'missing_quarter(s):'+cause,len(missing)
out=[]
for c,m,cl,gr,ri,ex,blanks in res:
    if blanks: continue
    r=mv[(c,m)]; lab=r['label']; end=r['end']; start=r['start']
    nodes=[]
    for t,n in ex:
        if t=='PERIOD': nodes.append(n)
    nodes=list(dict.fromkeys(nodes))
    # flatten to concept-level inputs
    conc=[]
    for n in nodes: conc+=leafnodes(n) if G[n]['kind'] in('metric','price_metric') else [n]
    conc=list(dict.fromkeys(conc))
    causes=[]
    if lab=='TTM' and cl in('D1','C1','C2') and end>='2026-01-01':
        asof=d(end)
        # TTM sums (fcf, ebitda, revenue, ...) : diagnose each concept
        for n in conc:
            if G[n]['basis']=='instant': continue
            cz,_=ttm_diag(c,n,asof)
            causes.append((n,cz))
    else:
        for n in conc:
            inst=G[n]['basis']=='instant'
            fa=fl(c,n)
            if lab=='FY' and cl=='C2':
                causes.append((n,'FY_metric_input_missing_for_named_year'))
                continue
            if inst: ok=any(e==end for s,e,fp,fy in fa)
            else: ok=any(s==start and e==end for s,e,fp,fy in fa)
            if ok: continue
            lastend=max([e for s,e,fp,fy in fa],default=None)
            pgc=set()
            for x in sib(n): pgc|=pg.get((c,x,end),set())
            if pgc: cz='gap:'+','.join(sorted(pgc))
            elif lastend and lastend<end: cz='input_latest_period_before_metric_latest(%s)'%('instant' if inst else 'duration')
            else: cz='absent_at_L_unclassified(%s)'%('instant' if inst else 'duration')
            causes.append((n,cz))
    out.append((c,m,cl,gr,lab,end,causes))
pickle.dump(out,open('period_out.pkl','wb'))
cnt=collections.Counter()
for c,m,cl,gr,lab,end,causes in out:
    cs=sorted({z for n,z in causes}) 
    cnt[(cl,lab,cs[0] if cs else 'NONE')]+=1
for k,v in cnt.most_common(40): print(v,k)
