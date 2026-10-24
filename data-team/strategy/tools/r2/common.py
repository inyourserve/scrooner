import pickle, re, collections, os
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out')
def load():
    D = {'sub': {}, 'tagc': {}, 'pre': {}, 'num': {}, 'dim': {}}
    for q in ('q4', 'q1'):
        d = pickle.load(open(os.path.join(OUT, q + '.pkl'), 'rb'))
        for k in D:
            D[k].update(d[k])
    # one 10-K per CIK: keep latest period
    best = {}
    for a, s in D['sub'].items():
        c = s['cik']
        if c not in best or s['period'] > D['sub'][best[c]]['period']:
            best[c] = a
    D['filings'] = sorted(best.values())
    return D
def family(sic):
    try: s = int(sic)
    except: return 'unknown'
    if s in (6021, 6022, 6029, 6035, 6036) or s in (6712,): return 'bank'
    if 6311 <= s <= 6411: return 'insurer'
    if s == 6798: return 'reit'
    if s == 6770: return 'shell'
    if 6000 <= s <= 6799: return 'other_fin'
    if 4900 <= s <= 4991: return 'utility'
    if 1300 <= s <= 1399 or 2900 <= s <= 2999: return 'energy'
    if 2833 <= s <= 2836 or s == 8731: return 'pharma'
    return 'other'
def is_custom(D, tag, ver):
    t = D['tagc'].get((tag, ver))
    if t: return t[0] == '1'
    return not ver.startswith(('us-gaap', 'dei', 'srt', 'ifrs', 'invest'))
def rows(D, a, stmt, paren=False):
    """rows of the primary (lowest report number) statement of that type, sorted by line"""
    rs = [r for r in D['pre'].get(a, []) if r[0] == stmt and r[3] == ('1' if paren else '0')]
    if not rs and stmt == 'IS':
        rs = [r for r in D['pre'].get(a, []) if r[0] == 'CI' and r[3] == ('1' if paren else '0')]
    if not rs: return []
    rep = min(r[1] for r in rs)
    return sorted([r for r in rs if r[1] == rep], key=lambda r: r[2])
def val(D, a, tag, ver, stmt):
    q = '0' if stmt == 'BS' else '4'
    n = D['num'].get(a, {})
    for u in ('USD', 'shares', 'USD/shares'):
        v = n.get((tag, ver, q, u))
        if v is not None: return v
    return None
def anyval(D, a, tag, q='4', u='USD'):
    for (t, v, qq, uu), x in D['num'].get(a, {}).items():
        if t == tag and qq == q and uu == u: return x
    return None
def dimonly(D, a, tag, q='4'):
    has_dim = any(k[0] == tag and k[2] == q for k in D['dim'].get(a, ()))
    has_plain = any(k[0] == tag and k[2] == q for k in D['num'].get(a, {}))
    return has_dim and not has_plain
