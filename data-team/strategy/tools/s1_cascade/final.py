import sys,csv,re,collections,datetime,pickle
sys.path.insert(0,'.')
from attrib import *   # G, has, reason, lin, grp, tmpl, cls, sib, present, rel_inputs
d=datetime.date.fromisoformat
mv={}
for l in open('mv_latest.tsv'):
    f=l.rstrip('\n').split('\t'); mv[(int(f[0]),f[1])]=dict(label=f[2],start=f[3],end=f[4],hv=f[5]=='t',reason=f[6])
facts=collections.defaultdict(list)
for l in open('facts_recent.tsv'):
    f=l.rstrip('\n').split('\t'); facts[(int(f[0]),f[1])].append((f[2],f[3],f[4],f[5]))
fyf=collections.defaultdict(set)
for l in open('fy_facts.tsv'):
    f=l.rstrip('\n').split('\t'); fyf[(int(f[0]),f[1])].add(int(f[2]) if f[2] else -1)
pg=collections.defaultdict(set)
for l in open('pgap.tsv'):
    f=l.rstrip('\n').split('\t'); pg[(int(f[0]),f[1],f[3])].add(f[4])
evid={}
for l in open('evid.tsv'):
    f=l.rstrip('\n').split('\t'); evid[(int(f[0]),f[1])]=(f[2],f[3]=='t')
def fl(c,n):
    out=[]
    for x in sib(n): out+=facts.get((c,x),[])
    return out
def leafnodes(n):
    k=G[n]['kind']
    if k in('leaf_concept','resolved_concept','derived_concept'): return [n]
    if k in('metric','price_metric'):
        out=[]
        for x,_ in G[n]['inputs']:
            if x in G and G[x]['kind']!='external_source': out+=leafnodes(x)
        return list(dict.fromkeys(out))
    return []
def baseleaf(n):
    # report leaf at base-concept level
    if n in('gross_profit_resolved',): return 'gross_profit'
    if n=='cost_of_revenue_resolved': return 'cost_of_revenue'
    if n=='operating_expenses_resolved': return 'operating_expenses'
    if n=='operating_income_resolved': return 'operating_income'
    if n=='revenue_sanity_resolved': return 'revenue'
    if n.endswith('_resolved') and n[:-9] in G: return n[:-9]
    return n
def expand(c,n):
    k=G.get(n,{}).get('kind')
    if n.startswith('?'): return [('UNKNOWN',n)]
    if k in('leaf_concept','external_source'):
        return [('BLANK',n)] if not present(c,n) else [('PERIOD',n)]
    if k=='resolved_concept':
        return [('PERIOD',n)] if present(c,n) else [('BLANK',baseleaf(n))]
    if k=='derived_concept':
        if present(c,n): return [('PERIOD',n)]
        out=[]
        for a,ro in G[n]['inputs']:
            if present(c,a): continue
            out+=expand(c,a)
        return out or [('UNKNOWN',n)]
    if k in('metric','price_metric'):
        if present(c,n): return [('PERIOD',n)]
        r=reason.get((c,n),'')
        if n=='market_cap': return [('BLANK','price_or_shares')]
        if cls(r) in('C1','C2','D1') or (n=='ebitda' and r.startswith('missing:4')):
            ri=[x for x,_ in G[n]['inputs']] if n=='ebitda' else rel_inputs(n,r)
        elif cls(r) in ('U0',):
            ri=[x for x,_ in G[n]['inputs']]
        else:
            return [('METRIC_BLANK_RULE',n+'|'+r)]
        out=[]
        for x in ri: out+=expand(c,x)
        return out or [('UNKNOWN',n)]
    return [('UNKNOWN',n)]
# ---------------- classification of a blank leaf --------------
SECTOR_REASONS=('financial_institution_interest_income_not_revenue','bank_interest_income_not_revenue','reit_net_interest_income_not_revenue','bdc_reports_investment_income_not_revenue')
def leaf_class(c,leaf):
    if leaf=='price_or_shares': return 'BLOCKED_price_or_shares'
    if leaf=='institutional_ownership': return 'BLOCKED_ownership_source'
    lr=None
    for x in sib(leaf):
        if reason.get((c,x)): lr=reason[(c,x)]; break
    ev=evid.get((c,leaf))
    if lr in('line_not_presented_in_filing','line_presented_combined_with_others'): return 'LEGIT_line_not_presented'
    if lr in SECTOR_REASONS: return 'LEGIT_sector_model'
    if lr and lr.startswith('pre_revenue'): return 'LEGIT_pre_revenue'
    if lr=='line_in_filing_not_extracted': return 'FIX_extraction'
    if ev and ev[0]=='false': return 'LEGIT_line_not_presented'
    L=lin.get((c,leaf),{})
    if L.get('nmap',0)>0: return 'FIX_mapped_tag_filed_no_value'
    if L.get('ncand',0)>0: return 'FIX_vocab_candidate_tags'
    t=tmpl.get(leaf,{}).get(grp.get(c,'?'))
    if t is not None and t>=90: return 'LEGIT_group_template'
    return 'UNEVIDENCED_no_tag_filed'
# ---------------- residual (all inputs present somewhere) -------------
def ttm_diag(c,node,asof):
    q=[(e,fp) for s,e,fp,fy in fl(c,node) if fp in('Q1','Q2','Q3','Q4')]
    ends=sorted({e for e,_ in q},reverse=True)
    allf=fl(c,node)
    if not allf: return 'PERIOD_stopped_no_fact_since_2023-06'
    if not q: return 'PERIOD_FY_only_no_quarterly_facts'
    e1=d(ends[0]); age=(asof-e1).days
    if age>150:
        mx=max(e for s_,e,fp,fy in allf)
        if (d(mx)-e1).days>30: return 'PERIOD_latest_quarter_only_as_YTD_not_derived'
        return 'PERIOD_ttm_stale_gt150d'
    present=0; missing=[]; cur=e1
    for i in range(4):
        if any(abs((d(e)-cur).days)<=20 for e in ends): present+=1
        else: missing.append(cur)
        cur=cur-datetime.timedelta(days=91)
    if present==4: return 'PERIOD_other_quarters_present'
    causes=set()
    for me in missing:
        for x in sib(node):
            for dd in range(-20,21): causes|=pg.get((c,x,(me+datetime.timedelta(days=dd)).isoformat()),set())
    if 'q4_not_derived' in causes: return 'PERIOD_q4_not_derived'
    if 'quarter_not_derived' in causes: return 'PERIOD_quarter_not_derived'
    if causes: return 'PERIOD_gap_other:'+'+'.join(sorted(causes))
    return 'PERIOD_missing_quarter_unclassified'
def inst_diag(c,n,L,anchor_shares):
    fa=fl(c,n); end=L['end']
    if any(e==end for s,e,fp,fy in fa): return None
    last=max([e for s,e,fp,fy in fa],default=None)
    if last is None: return 'PERIOD_stopped_no_fact_since_2023-06'
    lag=(d(end)-d(last)).days
    if lag>120: return 'PERIOD_stopped_gt120d'
    if anchor_shares: return 'ENGINE_cover_date_anchor'
    if lag<=0: return 'PERIOD_other'
    return 'PERIOD_instant_missing_at_latest_date'
def dur_diag(c,n,L):
    fa=fl(c,n); s0,e0=L['start'],L['end']
    if any(s==s0 and e==e0 for s,e,fp,fy in fa): return None
    for x in sib(n):
        cs=pg.get((c,x,e0))
        if cs:
            if 'q4_not_derived' in cs: return 'PERIOD_q4_not_derived'
            if 'quarter_not_derived' in cs: return 'PERIOD_quarter_not_derived'
            return 'PERIOD_gap_other:'+'+'.join(sorted(cs))
    if any(e==e0 for s,e,fp,fy in fa): return 'PERIOD_ytd_only_quarter_not_derived'
    last=max([e for s,e,fp,fy in fa],default=None)
    if last is None: return 'PERIOD_stopped_no_fact_since_2023-06'
    if (d(e0)-d(last)).days>120: return 'PERIOD_stopped_gt120d'
    return 'PERIOD_duration_missing_at_latest_unclassified'
recent=collections.defaultdict(lambda:{'mapped':[], 'cand':[]})
for l in open('recent_tags.tsv'):
    f=l.rstrip('\n').split('\t'); recent[(int(f[0]),f[1])][f[2]].append((f[3],f[4]))
def enrich(c,leaf):
    ev=evid.get((c,leaf))
    if ev and ev[0]=='false': return 'LEGIT_line_not_presented_now'
    # newest canonical data for the concept (base or resolved sibling)
    lat=[lin[(c,x)]['latest'] for x in sib(leaf) if (c,x) in lin and lin[(c,x)]['latest']]
    latest=max(lat) if lat else '0000-00-00'
    cutoff=(d(latest)+datetime.timedelta(days=30)).isoformat() if lat else '0000-00-00'
    rr=recent.get((c,leaf)) or recent.get((c,leaf+'_resolved')) or {'mapped':[],'cand':[]}
    if any(e>cutoff for t,e in rr['mapped']): return 'FIX_mapped_tag_has_newer_data_than_canonical'
    if any(e>cutoff for t,e in rr['cand']): return 'FIX_vocab_drift_candidate_tag_has_newer_data'
    return 'UNEVIDENCED_no_newer_tag_data'
fresh={}
for l in open('fresh.tsv'):
    f=l.rstrip('\n').split('\t')
    fresh[int(f[0])]=(f[1],f[3])
def feedlag(c):
    p,e=fresh.get(c,('',''))
    return bool(p and e and (d(p)-d(e)).days>45)
def fy_years_from_reason(r):
    return [int(y) for y in re.findall(r'\((\d{4})\)',r)]
def residual(c,m,cl,gr,nodes):
    L=mv[(c,m)]; lab=L['label']; out=[]
    conc=[]
    for n in nodes:
        conc+=leafnodes(n) if G[n]['kind'] in('metric','price_metric') else [n]
    conc=[x for x in dict.fromkeys(conc) if x in G]
    if gr.startswith('missing:share_count_1y_ago'):
        # shares_outstanding: need a fact 350-380d before latest
        fa=fl(c,'shares_outstanding'); fa=[e for s,e,fp,fy in fa]
        if not fa: return [('shares_outstanding','PERIOD_stopped_no_fact_since_2023-06')]
        latest=d(max(fa)); ok=any(350<=(latest-d(e)).days<=380 for e in fa)
        return [('shares_outstanding','ENGINE_share_1y_ago_window_350-380d' if not ok else 'PERIOD_other')]
    if lab=='FY' and cl=='C2':
        yrs=set(fy_years_from_reason(gr))
        if m=='piotroski_f_score' and yrs: yrs={max(yrs),max(yrs)-1}
        def haveyrs(n):
            h=set()
            for x in sib(n): h|=fyf.get((c,x),set())
            if n in('gross_profit_resolved','gross_profit'):
                h|=(fyf.get((c,'revenue'),set())|fyf.get((c,'revenue_sanity_resolved'),set())) & (fyf.get((c,'cost_of_revenue'),set())|fyf.get((c,'cost_of_revenue_resolved'),set()))
            return h
        out=[]
        for n in conc:
            if G[n]['basis']=='instant' and False: pass
            miss=[y for y in yrs if y not in haveyrs(n)]
            if miss: out.append((n,'PERIOD_FY_input_missing_for_named_year'))
        return out or [(conc[0] if conc else '?','PERIOD_FY_other')]
    anchor_shares = any(x=='shares_outstanding' for x,_ in G[m]['inputs']) and any(e==L['end'] for s,e,fp,fy in fl(c,'shares_outstanding'))
    for n in conc:
        if lab=='TTM' and L['end']>='2026-01-01' and G[n]['basis']!='instant':
            z=ttm_diag(c,n,d(L['end']))
            if z!='PERIOD_other_quarters_present': out.append((n,z))
            continue
        if G[n]['basis']=='instant':
            z=inst_diag(c,n,L,anchor_shares and n!='shares_outstanding')
        else:
            z=dur_diag(c,n,L)
        if z: out.append((n,z))
    if not out and conc and lab=='TTM': out=[(conc[0],'PERIOD_other_quarters_present')]
    if feedlag(c):
        out=[(n,'COMPANY_feed_lag_latest_10Q_not_in_facts') if z.startswith(('PERIOD_ttm_stale','PERIOD_stopped_gt120d','PERIOD_instant_missing','PERIOD_duration_missing','PERIOD_latest_quarter_only')) else (n,z) for n,z in out]
    out=[(n,z+'|'+enrich(c,baseleaf(n))) if (z.startswith(('PERIOD_stopped','PERIOD_ttm_stale','PERIOD_instant_missing','PERIOD_duration_missing','PERIOD_FY_only')) ) else (n,z) for n,z in out]
    return out
if __name__=='__main__':
    allres=[]
    for r in cells:
        if r['has_value']=='t': continue
        cl=cls(r['gap_reason'])
        if cl not in('C1','C2','D1'): continue
        c=int(r['company_id']); m=r['data_point_name']; gr=r['gap_reason']
        ri=rel_inputs(m,gr); ex=[]
        for n in ri: ex+=expand(c,n)
        blanks=sorted({b for t,b in ex if t=='BLANK'})
        if blanks:
            causes=[(baseleaf(b),leaf_class(c,baseleaf(b))) for b in blanks]
            causes=list(dict.fromkeys(causes)); typ='BLANK_LEAF'
        else:
            nodes=list(dict.fromkeys(n for t,n in ex if t=='PERIOD'))
            rules=[n for t,n in ex if t=='METRIC_BLANK_RULE']
            if nodes:
                causes=residual(c,m,cl,gr,nodes); typ='PERIOD_RESIDUAL'
                if not causes: causes=[('?','UNDIAGNOSED')]
            else:
                causes=[(rules[0].split('|')[0] if rules else '?','METRIC_BLANK_BY_RULE:'+(rules[0].split('|')[1] if rules else ''))]; typ='RULE'
        allres.append(dict(company_id=c,metric=m,cls=cl,reason=gr,group=grp.get(c,'?'),typ=typ,causes=causes))
    pickle.dump(allres,open('final.pkl','wb'))
    cnt=collections.Counter()
    for a in allres:
        for leaf,cz in a['causes']: cnt[(a['typ'],cz)]+=1.0/len(a['causes'])
    for k,v in sorted(cnt.items(),key=lambda x:-x[1])[:45]: print(round(v,1),k)
    print(len(allres), collections.Counter(a['typ'] for a in allres))
