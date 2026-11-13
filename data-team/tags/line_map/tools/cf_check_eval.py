import json,re,collections,sys,importlib.util
from decimal import Decimal as D
sys.path.insert(0,'../wt/pipeline/src')
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m
old=load('cold','checks_old.py'); new=load('cnew','checks_new.py'); eng=load('ceng','checks_eng.py')
vals={}
for f in ['/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794596715308.txt','/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794596767439.txt','/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794596941581.txt','/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794596957924.txt','/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794596855741.txt','/root/.claude/projects/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/tool-results/mcp-Supabase-execute_sql-1794596910790.txt']:
    t=open(f).read(); m=re.search(r'<untrusted-data-[0-9a-f-]+>\\n(.*)\\n</untrusted-data',t,re.S)
    for r in json.loads(json.loads('"'+m.group(1)+'"')): vals[r['acc']]=r['vals']
arcs=json.load(open('cfarcs.json'))
cik_of={}
B=collections.Counter(); A=collections.Counter(); E=collections.Counter(); rows=[]; rows_e=[]
for acc,vs in vals.items():
    cols=collections.defaultdict(dict)
    for s in vs.split('~'):
        x=s.split('|')
        if len(x)<6: continue
        tag,ver,dd,q,v,dc=x[:6]
        cols[(dd,int(q))].setdefault((tag,ver),new.Print(tag,ver,D(v),int(dc) if dc else None,None))
    groups=collections.defaultdict(list)
    for s in (arcs.get(acc) or '').split('~'):
        x=s.split('|')
        if len(x)==6: groups[(x[1],x[2],int(x[0]))].append((x[3],x[4],D(x[5])))
    for (dd,q),col in cols.items():
        o=[c for c in old.check_column('CF',col,{},{}) if c['check_id']=='cf_parts_eq_change']
        n=new.cf_change_check(col,groups)
        e=[c for c in eng.check_column('CF',col,groups,{}) if c['check_id']=='cf_parts_eq_change']
        eb=None if not e else e[0]['ok']
        ob=None if not o else o[0]['ok']; nb=None if n is None else n['ok']
        E[eb]+=1; rows_e.append((acc,dd,q,ob,eb,nb, str(e[0]['lhs']-e[0]['rhs']) if e else ''))
        B[ob]+=1; A[nb]+=1
        rows.append(dict(acc=acc,ddate=dd,qtrs=q,old=ob,new=nb,old_diff=str(o[0]['lhs']-o[0]['rhs']) if o else '',new_diff=str(n['lhs']-n['rhs']) if n else '',form=n['detail'].get('form') if n else '',new_detail=json.dumps(n['detail'],default=str) if n else ''))
import csv
w=csv.DictWriter(open('cf_before_after.csv','w',newline=''),fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print('filings',len(vals),'columns',len(rows)); print('old',B); print('new',A)
print('eng',E); print('eng vs mine',collections.Counter((x[4],x[5]) for x in rows_e)); json.dump(rows_e,open('eng_rows.json','w'),default=str)
print('transitions',collections.Counter((r['old'],r['new']) for r in rows))
print('new forms',collections.Counter((r['form'],r['new']) for r in rows))
