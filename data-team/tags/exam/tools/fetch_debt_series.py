import json,subprocess,os,re,time,csv,sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'line_map', 'tools'))
import sec_pace
ua=os.environ['SEC_USER_AGENT']; out=open('ie_series.jsonl','w')
def g(u):
    for i in range(3):
        sec_pace.wait()   # the shared machine-wide SEC budget (2 req/s in total)
        r=subprocess.run(['curl','-sS','--max-time','120','-A',ua,u],capture_output=True,text=True)
        if r.returncode==0 and r.stdout: return r.stdout
        time.sleep(3)
    return ''
for tk,cik,acc in csv.reader(open('ie_np.csv')):
    base=f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace("-","")}'
    try: it=json.loads(g(base+'/index.json'))['directory']['item']
    except Exception: out.write(json.dumps({'ticker':tk,'cik':cik,'error':'index'})+'\n'); continue
    n=[i['name'] for i in it if i['name'].endswith('_htm.xml')]
    s=g(f'{base}/{n[0]}') if n else ''
    ctx={}
    for m in re.finditer(r'<(?:xbrli:)?context id="([^"]+)">(.*?)</(?:xbrli:)?context>',s,re.S):
        b=m.group(2); ctx[m.group(1)]=(re.findall(r'dimension="([^"]+)">\s*([^<\s]+)\s*<',b), re.findall(r'<(?:xbrli:)?(?:startDate|endDate)>([^<]+)',b))
    fy=json.loads(open(f'exam/lines_eng/{tk}.jsonl').readline())['per']
    facts=[]
    for m in re.finditer(r'<([a-z\-]+):([A-Za-z]*Interest[A-Za-z]*)\b([^>]*)contextRef="([^"]+)"[^>]*>([-0-9.]+)<',s):
        ns,tag,_,c,v=m.groups()
        if c not in ctx: continue
        d,p=ctx[c]
        if len(p)==2 and p[-1]==fy: facts.append((ns,tag,[x[1] for x in d],[x[0] for x in d],float(v)))
    out.write(json.dumps({'ticker':tk,'cik':cik,'fy':fy,'facts':facts})+'\n'); out.flush()
print('done')
