"""Rate-limited sec.gov reader for the verifier (<=4 req/s, sec.gov only, disk cache)."""
import os, re, ssl, sys, time, html, hashlib, urllib.request, json
sys.path.insert(0, "/home/user/scrooner/pipeline/src")
from scrooner_pipeline.verification import filing_kit as fk
UA = "Scrooner research inyourserve@gmail.com"  # declared UA from doc/data-moat/team/top1000/tools/sec_rpages.py
DL = "/tmp/claude-0/-home-user-scrooner/23969552-d6dc-56b1-b7f0-44ecbb5ec1ad/scratchpad/dl"
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
COUNT_F = os.path.join(DL, "_count")
_last = [0.0]
def get(url):
    assert re.match(r"https://www\.sec\.gov/", url), url
    p = os.path.join(DL, hashlib.sha1(url.encode()).hexdigest())
    if os.path.exists(p):
        return open(p, "rb").read()
    for attempt in range(4):
        wait = 0.3 - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        n = int(open(COUNT_F).read()) if os.path.exists(COUNT_F) else 0
        open(COUNT_F, "w").write(str(n + 1))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
            b = urllib.request.urlopen(req, context=CTX, timeout=30).read()
            open(p, "wb").write(b); return b
        except Exception as e:
            if getattr(e, "code", None) == 404: raise RuntimeError("404 " + url)
            print("retry", url, e, file=sys.stderr); time.sleep(2 ** attempt)
    raise RuntimeError(url)

def folder(cik, adsh):
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-','')}/"

def reports(cik, adsh):
    fs = get(folder(cik, adsh) + "FilingSummary.xml").decode("utf8", "ignore")
    return fk._reports(fs), fk.find_report_files(fs)

def rows_with_tags(page_html):
    """[(label, [element tags], [cell texts])] per <tr> in order, raw."""
    out = []
    for tr in re.findall(r"<tr.*?</tr>", page_html, re.DOTALL | re.I):
        tags = re.findall(r"defref_([\w-]+?_[\w]+)", tr)
        cells = fk._cells3(tr)
        if not cells: continue
        out.append((cells[0][1], tags, [t for c, t, _ in cells[1:] if c not in ("fn", "th")]))
    return out

def page(cik, adsh, fname):
    h = get(folder(cik, adsh) + fname).decode("utf8", "ignore")
    return fk.parse_rpage(h), rows_with_tags(h)
