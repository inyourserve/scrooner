"""Read-only: for each pre-842 10-K, stream the XBRL instance from sec.gov and keep only the capital/finance lease
obligation facts with their context date and dimensions (BalanceSheetLocationAxis etc.). <=3 requests/s, declared UA."""
import json, os, re, sys, time, urllib.request
UA = os.environ['SEC_USER_AGENT']
OUT = sys.argv[2]
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)['acc'])
last = [0.0]
def get(url):
    w = 0.34 - (time.time() - last[0])
    if w > 0: time.sleep(w)
    last[0] = time.time()
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r: return r.read()
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    raise err
TAG = re.compile(r'<(us-gaap:(?:CapitalLeaseObligations(?:Current|Noncurrent)?|FinanceLeaseLiability(?:Current|Noncurrent)?|LongTermDebtAndCapitalLeaseObligations\w*|CapitalLeaseObligationsAndFinanceLease\w*))\b([^>]*)>([^<]*)<')
CTX = re.compile(r'<(?:xbrli:)?context\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</(?:xbrli:)?context>', re.S)
for cik, acc, per in json.load(open(sys.argv[1])):
    if acc in done: continue
    rec = dict(cik=cik, acc=acc, per=per, facts=[], err=None)
    try:
        base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/"
        idx = json.loads(get(base + 'index.json'))
        names = [i['name'] for i in idx['directory']['item']]
        inst = [n for n in names if n.endswith('_htm.xml')] or [n for n in names if re.match(r'^[a-z0-9\-]+-\d{8}\.xml$', n)]
        if not inst: rec['err'] = 'no instance'; raise StopIteration
        s = get(base + inst[0]).decode('utf-8', 'replace')
        ctx = {}
        for cid, body in CTX.findall(s):
            d = re.search(r'<(?:xbrli:)?instant>([^<]+)<', body)
            dims = re.findall(r'dimension="([^"]+)"[^>]*>([^<]+)<', body)
            ctx[cid] = (d.group(1) if d else None, dims)
        for tag, attrs, val in TAG.findall(s):
            c = re.search(r'contextRef="([^"]+)"', attrs); dec = re.search(r'decimals="([^"]+)"', attrs)
            if not c or c.group(1) not in ctx: continue
            dt, dims = ctx[c.group(1)]
            rec['facts'].append([tag.split(':')[1], dt, dims, val.strip(), dec.group(1) if dec else None])
        rec['instance'] = inst[0]
    except StopIteration: pass
    except Exception as e: rec['err'] = repr(e)[:200]
    with open(OUT, 'a') as f: f.write(json.dumps(rec) + '\n')
print('done')
