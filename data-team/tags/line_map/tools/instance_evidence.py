"""Instance evidence for total_debt, a standard step of standard_run.py (read-only; sec.gov only, at most 3 requests a second,
User-Agent from env SEC_USER_AGENT, cached per accession). FSN drops the facts total_debt needs to locate leases:
  - FinanceLeaseLiability(Current|Noncurrent)StatementOfFinancialPositionExtensibleList: where the finance lease sits (fl_loc
    in / out / none, the rule of exam/tools/build_era_notes.loc_of);
  - pre-842 CapitalLeaseObligations(Current|Noncurrent) facts, undimensioned or by one BalanceSheetLocationAxis member, and the
    calc parents of CapitalLeaseObligations when no location list exists.
  python3 instance_evidence.py fetch filings.json CACHE_DIR    (one JSON per accession in CACHE_DIR; already-cached ones are skipped)
total_debt.load_evidence(cache_dir=CACHE_DIR) reads the cache beside the committed evidence of the 110."""
import json, os, re, sys, time, urllib.request
from datetime import date
from decimal import Decimal as D

DEBT = re.compile(r'Debt|Borrowing|NotesPayable|CommercialPaper|LineOfCredit|LinesOfCredit|LoansPayable|SeniorNotes')
OUTSIDE = re.compile(r'OtherLiabilit|AccruedLiabilit|AccountsPayable|OtherAccrued')
CTX = re.compile(r'<(?:xbrli:)?context\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</(?:xbrli:)?context>', re.S)
CL = re.compile(r'<us-gaap:(CapitalLeaseObligations(?:Current|Noncurrent)?)\b([^>]*)>([^<]*)<')
FL = re.compile(r'<us-gaap:FinanceLeaseLiability(?:Current|Noncurrent)?StatementOfFinancialPositionExtensibleList[^>]*>([^<]*)<')
_last = [0.0]


def _get(url):
    assert url.startswith('https://www.sec.gov/'), url
    for i in range(4):
        w = 0.34 - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': os.environ['SEC_USER_AGENT'], 'Accept-Encoding': 'identity'})
            with urllib.request.urlopen(req, timeout=90) as r: return r.read().decode('utf-8', 'replace')
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    raise err


def loc_of(fl_list, cl_parents):
    if fl_list:
        if any(DEBT.search(x) for x in fl_list) and not any(OUTSIDE.search(x) for x in fl_list): return 'in'
        if all(OUTSIDE.search(x) for x in fl_list): return 'out'
        return 'none'
    P = [x for x in cl_parents or [] if not re.search(r'_(Liabilities|LiabilitiesCurrent|LiabilitiesNoncurrent|LiabilitiesAndStockholdersEquity)$|NetCashProvided|FutureMinimumPayments', x)]
    if P:
        if any(DEBT.search(x) for x in P): return 'in'
        if any(OUTSIDE.search(x) for x in P): return 'out'
    return 'none'


def read_instance(s, per):
    """(fl_list, lease facts [(tag, date, location member or '', value)]) from one instance document."""
    ctx = {}
    for cid, body in CTX.findall(s):
        d = re.search(r'<(?:xbrli:)?instant>([^<]+)<', body)
        ctx[cid] = (d.group(1).strip() if d else None, re.findall(r'dimension="([^"]+)"[^>]*>\s*([^<\s]+)\s*<', body))
    fl = sorted({x.split('#')[-1] for x in FL.findall(s)})
    facts = []
    for tag, attrs, val in CL.findall(s):
        c = re.search(r'contextRef="([^"]+)"', attrs)
        if not c or c.group(1) not in ctx: continue
        dt, dims = ctx[c.group(1)]
        loc = [m for ax, m in dims if ax.endswith('BalanceSheetLocationAxis')]
        if not dt or (dims and not loc) or len(dims) > 1: continue
        try: facts.append([tag, dt, loc[0] if loc else '', str(D(val.strip()))])
        except Exception: continue
    return fl, facts


def fetch(filings, cache):
    os.makedirs(cache, exist_ok=True)
    n = 0
    for f in filings:
        p = os.path.join(cache, f['a'] + '.json')
        if os.path.exists(p): continue
        rec = dict(acc=f['a'], cik=f['cik'], per=f['p'])
        try:
            base = f"https://www.sec.gov/Archives/edgar/data/{int(f['cik'])}/{f['a'].replace('-', '')}/"
            names = [i['name'] for i in json.loads(_get(base + 'index.json'))['directory']['item']]
            inst = [x for x in names if x.endswith('_htm.xml')] or [x for x in names if re.fullmatch(r'[a-z0-9\-]+-\d{8}\.xml', x)]
            if not inst: raise ValueError('no instance')
            rec['instance'] = inst[0]
            rec['fl_list'], rec['lease_facts'] = read_instance(_get(base + inst[0]), f['p'])
            rec['cl_parents'] = []
            if rec['lease_facts'] and not rec['fl_list']:
                cal = [x for x in names if x.endswith('_cal.xml')]
                cs = _get(base + cal[0]) if cal else ''
                lab = dict((m.group(2), m.group(1)) for m in re.finditer(r'<link:loc[^>]*xlink:href="[^"#]*#([^"]+)"[^>]*xlink:label="([^"]+)"', cs))
                par = {fr for fr, to in re.findall(r'<link:calculationArc[^>]*xlink:from="([^"]+)"[^>]*xlink:to="([^"]+)"', cs) if 'CapitalLeaseObligations' in to}
                rec['cl_parents'] = sorted({lab.get(x, x) for x in par})
            rec['fl_loc'] = loc_of(rec['fl_list'], rec['cl_parents'])
        except Exception as e:
            rec['error'] = repr(e)[:200]
        json.dump(rec, open(p, 'w')); n += 1
    return n


def load(cache):
    """(flloc {accession: in/out/none}, leases {accession: {date: [(tag, member, value)]}}) from the cache (errors skipped)."""
    flloc, leases = {}, {}
    if not cache or not os.path.isdir(cache): return flloc, leases
    for name in sorted(os.listdir(cache)):
        if not name.endswith('.json'): continue
        r = json.load(open(os.path.join(cache, name)))
        if r.get('error'): continue
        flloc[r['acc']] = r['fl_loc']
        for tag, dt, loc, v in r.get('lease_facts') or []:
            leases.setdefault(r['acc'], {}).setdefault(dt, []).append((tag, loc, D(v)))
    return flloc, leases


if __name__ == '__main__':
    if sys.argv[1] == 'fetch':
        print(fetch(json.load(open(sys.argv[2])), sys.argv[3]), 'fetched')
