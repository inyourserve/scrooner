"""Era instance reads (sec.gov, <=3 req/s, SEC_USER_AGENT from env): finance/capital-lease balance-sheet location and per-series interest."""
import json,subprocess,os,re,time,sys
ua=os.environ['SEC_USER_AGENT']; out=open('eras/instances.jsonl','a')
done={json.loads(l)['acc'] for l in open('eras/instances.jsonl')} if os.path.getsize('eras/instances.jsonl') else set()
last=[0.0]
def g(u):
    for i in range(4):
        w=0.34-(time.time()-last[0])
        if w>0: time.sleep(w)
        last[0]=time.time()
        r=subprocess.run(['curl','-sS','--max-time','120','-A',ua,u],capture_output=True,text=True)
        if r.returncode==0 and r.stdout: return r.stdout
        time.sleep(3*(i+1))
    return ''
from datetime import date
def num(x):
    try: return float(x)
    except Exception: return None
def near(a,b):
    try: return abs((date.fromisoformat(a)-date.fromisoformat(b)).days)<=7
    except Exception: return False
DEBT=r'(Debt|Borrowing|NotesPayable|CommercialPaper|LineOfCredit|LinesOfCredit|LoansPayable)'
for f in sorted(os.listdir('eras/lines')):
    cik,acc=f[:10],f[11:-6]
    if acc in done: continue
    per=json.loads(open(f'eras/lines/{f}').readline())['per']
    base=f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace("-","")}'
    rec={'cik':cik,'acc':acc,'per':per}
    try:
        it=json.loads(g(base+'/index.json'))['directory']['item']; names=[i['name'] for i in it]
    except Exception:
        rec['error']='index'; out.write(json.dumps(rec)+'\n'); out.flush(); continue
    inst=[n for n in names if n.endswith('_htm.xml')] or [n for n in names if re.fullmatch(r'[a-z0-9\-]+-\d{8}\.xml',n)]
    s=g(f'{base}/{inst[0]}') if inst else ''
    if not s: rec['error']='instance'; out.write(json.dumps(rec)+'\n'); out.flush(); continue
    ctx={}
    for m in re.finditer(r'<(?:xbrli:)?context id="([^"]+)">(.*?)</(?:xbrli:)?context>',s,re.S):
        b=m.group(2); ctx[m.group(1)]=(re.findall(r'dimension="([^"]+)">\s*([^<\s]+)\s*<',b), re.findall(r'<(?:xbrli:)?(?:startDate|endDate|instant)>([^<]+)',b))
    # finance-lease location (ASC 842)
    locs=sorted({x.split('#')[-1] for x in re.findall(r'<us-gaap:FinanceLeaseLiability(?:Current|Noncurrent)?StatementOfFinancialPositionExtensibleList[^>]*>([^<]*)<',s)})
    rec['fl_list']=locs
    # per-series interest
    facts=[]
    for m in re.finditer(r'<([a-z\-]+):([A-Za-z]*Interest[A-Za-z]*)\b[^>]*contextRef="([^"]+)"[^>]*>([-0-9.]+)<',s):
        ns,tag,c,v=m.groups()
        if c not in ctx: continue
        d,p=ctx[c]
        if len(p)==2 and near(p[-1],per) and num(v) is not None: facts.append((ns,tag,[x[1] for x in d],[x[0] for x in d],num(v)))
    rec['interest_facts']=facts
    # capital leases (pre-ASC 842): undimensioned BS-date facts + calc parent
    cl={}
    for m in re.finditer(r'<us-gaap:(CapitalLeaseObligations(?:Current|Noncurrent)?)\b[^>]*contextRef="([^"]+)"[^>]*>([-0-9.]+)<',s):
        tag,c,v=m.groups(); d,p=ctx.get(c,([],[]))
        if not d and p and near(p[-1],per) and num(v) is not None: cl[tag]=num(v)
    rec['capital_lease']=cl
    if cl and not locs:
        cal=[n for n in names if n.endswith('_cal.xml')]
        cs=g(f'{base}/{cal[0]}') if cal else ''
        parents=set()
        for m in re.finditer(r'<link:calculationArc[^>]*xlink:from="([^"]+)"[^>]*xlink:to="([^"]+)"',cs):
            fr,to=m.groups()
            if re.search(r'CapitalLeaseObligations(Current|Noncurrent)?$',to.split('_')[-1] if '_' in to else to) or 'CapitalLeaseObligations' in to: parents.add(fr)
        lab={}
        for m in re.finditer(r'<link:loc[^>]*xlink:href="[^"#]*#([^"]+)"[^>]*xlink:label="([^"]+)"',cs): lab[m.group(2)]=m.group(1)
        rec['cl_parents']=sorted({lab.get(p,p) for p in parents})
    out.write(json.dumps(rec)+'\n'); out.flush()
print('done')
