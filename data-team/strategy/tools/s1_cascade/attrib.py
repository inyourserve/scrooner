import sys,csv,re,collections,json,datetime
sys.path.insert(0,'.')
import graph_def as g
G=g.G
D='/Users/vikash/scrooner/data-team/strategy/data/'
cells=list(csv.DictReader(open(D+'cohort_cells.csv')))
grp={int(r['company_id']):r['group'] for r in csv.DictReader(open(D+'group_assignment_draft.csv'))}
tmpl={}
for r in csv.DictReader(open(D+'empirical_template_candidates.csv')):
    tmpl[r['data_point']]={k[:-10]:float(v) for k,v in r.items() if k.endswith('_blank_pct') and v!=''}
has={}; reason={}
for r in cells:
    k=(int(r['company_id']),r['data_point_name']); has[k]=(r['has_value']=='t'); reason[k]=r['gap_reason']
lin={}
for line in open('lineage.tsv'):
    f=line.rstrip('\n').split('\t')
    lin[(int(f[0]),f[1])]=dict(has=f[2]=='t',latest=f[3],nsrc=int(f[4]),nmap=int(f[5]),ncand=int(f[6]),reason=f[7],cand=f[8],mapped=f[9])
def cls(r):
    if not r: return 'U0'
    if r.startswith('incomplete:'): return 'C1'
    if r.startswith('missing:') and r.endswith('_ttm'): return 'D1'
    if r.startswith('missing:prior_period') or 'fewer_than_3' in r or r=='missing:4_consecutive_quarters' or 'non_consecutive' in r: return 'H1'
    if r.startswith('missing:'): return 'C2'
    return 'other'
TTMNAME={'ttm_operating_income':'operating_income','ttm_income_tax_expense':'income_tax_expense','ttm_income_before_tax':'income_before_tax','ttm_net_income':'net_income'}
def sib(n):
    out=[n]
    if n.endswith('_resolved'): out.append(n[:-9])
    elif n+'_resolved' in G: out.append(n+'_resolved')
    if n=='revenue_sanity_resolved': out.append('revenue')
    if n=='revenue': out.append('revenue_sanity_resolved')
    return out
def present(c,n):
    return any(has.get((c,x),False) for x in sib(n) if (c,x) in has)
def rel_inputs(m,r):
    """direct input nodes named by reason r for metric m"""
    ins=G[m]['inputs']; out=[]
    body=r.split(':',1)[1] if ':' in r else r
    if r.startswith('incomplete:'):
        for tok in body.split(','):
            roles=[n for n,ro in ins if ro==tok]
            if roles: out+=roles; continue
            if tok in TTMNAME: out.append(TTMNAME[tok]); continue
            if tok in G: out.append(tok); continue
            out.append('?'+tok)
        return list(dict.fromkeys(out))
    # missing:
    body=re.sub(r'\.\.\.$','',body)
    toks=[re.sub(r'\(.*?\)','',t) for t in re.split(r',(?![^()]*\))',body)]
    # piotroski truncated: use all required
    if m=='piotroski_f_score': return [n for n,_ in ins]
    for t in toks:
        t=re.sub(r'\(\d{4}.*','',t)
        if t=='total_debt': out.append('total_debt_resolved')
        elif t=='total_debt_or_cash': out+= ['total_debt_resolved','cash_and_equivalents']
        elif t=='share_count_1y_ago': out.append('shares_outstanding')
        elif t=='institutional_holdings': out.append('institutional_ownership')
        elif t=='shares_outstanding': out.append('shares_outstanding')
        elif t.endswith('_ttm') and t[:-4] in G: out.append(t[:-4])
        elif t in G: out.append(t)
        else: out.append('?'+t)
    return list(dict.fromkeys(out))
def expand(c,n,depth=0):
    """returns list of ('BLANK',leaf) or ('PERIOD',node) or ('UNKNOWN',node)"""
    k=G.get(n,{}).get('kind')
    if k in ('leaf_concept','external_source') or n.startswith('?'):
        if n.startswith('?'): return [('UNKNOWN',n)]
        return [('BLANK',n)] if not present(c,n) else [('PERIOD',n)]
    if k=='resolved_concept':
        if present(c,n): return [('PERIOD',n)]
        return [('BLANK',G[n]['inputs'][0][0])]
    if k=='derived_concept':
        if present(c,n): return [('PERIOD',n)]
        out=[]
        for a,ro in G[n]['inputs']:
            if present(c,a): continue
            out+=expand(c,a,depth+1) if G[a]['kind']!='leaf_concept' else [('BLANK',a)]
        return out or [('UNKNOWN',n)]
    if k in ('metric','price_metric'):
        if present(c,n): return [('PERIOD',n)]
        r=reason.get((c,n),'')
        if cls(r) in('C1','C2','D1') or n=='ebitda' and r.startswith('missing:4'):
            if n=='ebitda': ri=[x for x,_ in G[n]['inputs']]
            else: ri=rel_inputs(n,r)
        elif n in('market_cap',):
            return [('BLANK','price_or_shares')]
        else:
            return [('METRIC_BLANK_OTHER',n+'|'+(r or 'U0'))]
        out=[]
        for x in ri: out+=expand(c,x,depth+1)
        return out or [('UNKNOWN',n)]
    return [('UNKNOWN',n)]
def leaf_class(c,leaf):
    """classify a BLANK leaf concept cell for company c"""
    lr=None
    for x in sib(leaf):
        if (c,x) in reason and reason[(c,x)]: lr=reason[(c,x)]; break
    L=lin.get((c,leaf),{})
    for x in sib(leaf):
        if x in ('revenue','revenue_sanity_resolved'): pass
    if lr in('line_not_presented_in_filing','line_presented_combined_with_others'): return 'LEGIT_line_not_presented'
    if lr in('financial_institution_interest_income_not_revenue','bank_interest_income_not_revenue','reit_net_interest_income_not_revenue','bdc_reports_investment_income_not_revenue'): return 'LEGIT_sector_model'
    if lr and lr.startswith('pre_revenue'): return 'LEGIT_pre_revenue'
    if lr=='line_in_filing_not_extracted': return 'FIX_extraction'
    if L.get('nmap',0)>0: return 'FIX_pipeline_mapped_tag_filed'
    if L.get('ncand',0)>0: return 'FIX_vocab_candidate_tags'
    # no evidence
    gname=grp.get(c,'?')
    t=tmpl.get(leaf,{}).get(gname)
    if t is not None and t>=90: return 'LEGIT_group_template'
    return 'UNEVIDENCED_no_relevant_tag_filed'
if __name__=='__main__':
    res=[]
    for r in cells:
        if r['has_value']=='t': continue
        cl=cls(r['gap_reason'])
        if cl not in('C1','C2','D1'): continue
        c=int(r['company_id']); m=r['data_point_name']
        ri=rel_inputs(m,r['gap_reason'])
        ex=[]
        for n in ri: ex+=expand(c,n)
        blanks=sorted({b for t,b in ex if t=='BLANK'})
        res.append((c,m,cl,r['gap_reason'],ri,ex,blanks))
    kinds=collections.Counter()
    for c,m,cl,gr,ri,ex,blanks in res:
        if blanks: kinds['has_blank_leaf']+=1
        else:
            ts={t for t,_ in ex}
            kinds['no_blank:'+('/'.join(sorted(ts)))]+=1
    print(len(res),kinds)
    import pickle; pickle.dump(res,open('res.pkl','wb'))
