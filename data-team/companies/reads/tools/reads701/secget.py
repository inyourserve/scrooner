"""Throttled, cached sec.gov fetcher: 0.4 req/s max, declared SEC_USER_AGENT from the environment, sec.gov hosts only."""
import os, time, hashlib, urllib.request, urllib.error, json
UA = os.environ['SEC_USER_AGENT']
CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
_last = [0.0]; COUNT = [0]
def get(url, binary=False):
    assert url.startswith(('https://www.sec.gov/', 'https://data.sec.gov/')), url
    fn = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest())
    if os.path.exists(fn):
        b = open(fn, 'rb').read()
        if b.startswith(b'__404__'): return None
        return b if binary else b.decode('utf-8', 'replace')
    for attempt in range(6):
        wait = 2.5 - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time(); COUNT[0] += 1
        open(os.path.join(os.path.dirname(CACHE), 'requests.log'), 'a').write(url + '\n')
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=180) as r: b = r.read()
            open(fn, 'wb').write(b)
            return b if binary else b.decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                open(fn, 'wb').write(b'__404__'); return None
            time.sleep(10 * (attempt + 1))
        except Exception:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError('failed ' + url)
def getjson(url):
    t = get(url); return json.loads(t) if t else None
