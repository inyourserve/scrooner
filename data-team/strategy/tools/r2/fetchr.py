"""Fetch SEC R-files through the ONE machine-wide SEC budget (pipeline/src/scrooner_pipeline/common/sec_rate.py, 2 req/s
in total), print table rows matching a regex. UA from env SEC_UA or SEC_USER_AGENT (never printed)."""
import sys, os, re, html
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'pipeline' / 'src'))
from scrooner_pipeline.common import sec_rate  # noqa: E402
if os.environ.get('SEC_UA') and not os.environ.get('SEC_USER_AGENT'):
    os.environ['SEC_USER_AGENT'] = os.environ['SEC_UA']
for spec in sys.argv[1:]:
    cik, adsh, rn, rx = spec.split('|', 3)
    url = 'https://www.sec.gov/Archives/edgar/data/%s/%s/R%s.htm' % (cik, adsh.replace('-', ''), rn)
    try:
        t = sec_rate.fetch(url, timeout=30).decode('utf-8', 'replace')
        if '<tr' not in t: raise Exception('no table (len %d)' % len(t))
    except Exception as e:
        print('##', adsh, 'R' + rn, 'ERROR', e); continue
    title = re.search(r'<th[^>]*class="tl"[^>]*>(.*?)</th>', t, re.S)
    hdr = re.findall(r'<th[^>]*>(.*?)</th>', t, re.S)[:5]
    print('##', adsh, 'R' + rn, '|', html.unescape(re.sub('<[^>]+>', ' ', title.group(1))).strip()[:90] if title else '', '| cols:', [re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', h))).strip()[:30] for h in hdr[1:4]])
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S):
        cells = [re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', c))).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if cells and re.search(rx, cells[0], re.I):
            print('   ', ' | '.join(c for c in cells[:4] if c != '')[:160])
