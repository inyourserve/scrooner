"""Fetch SEC R-files (<=2 req/s), print table rows matching a regex. UA from env SEC_UA (never printed)."""
import sys, os, re, time, urllib.request, html
UA = os.environ['SEC_UA']
for spec in sys.argv[1:]:
    cik, adsh, rn, rx = spec.split('|', 3)
    url = 'https://www.sec.gov/Archives/edgar/data/%s/%s/R%s.htm' % (cik, adsh.replace('-', ''), rn)
    try:
        import subprocess
        t = subprocess.run(['curl', '-s', '--max-time', '30', '-A', UA, url], capture_output=True).stdout.decode('utf-8', 'replace')
        if '<tr' not in t: raise Exception('no table (len %d)' % len(t))
    except Exception as e:
        print('##', adsh, 'R' + rn, 'ERROR', e); time.sleep(0.6); continue
    title = re.search(r'<th[^>]*class="tl"[^>]*>(.*?)</th>', t, re.S)
    hdr = re.findall(r'<th[^>]*>(.*?)</th>', t, re.S)[:5]
    print('##', adsh, 'R' + rn, '|', html.unescape(re.sub('<[^>]+>', ' ', title.group(1))).strip()[:90] if title else '', '| cols:', [re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', h))).strip()[:30] for h in hdr[1:4]])
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S):
        cells = [re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', c))).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if cells and re.search(rx, cells[0], re.I):
            print('   ', ' | '.join(c for c in cells[:4] if c != '')[:160])
    time.sleep(0.6)
