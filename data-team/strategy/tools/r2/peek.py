import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
D = load(); F = D['filings']
stmt = sys.argv[1]; n = int(sys.argv[2]); fam = sys.argv[3] if len(sys.argv) > 3 else None
random.seed(int(sys.argv[4]) if len(sys.argv) > 4 else 1)
pool = [a for a in F if not fam or family(D['sub'][a]['sic']) == fam]
for a in random.sample(pool, n):
    s = D['sub'][a]; print('==', a, s['name'], s['sic'], family(s['sic']))
    for r in rows(D, a, stmt)[:int(sys.argv[5]) if len(sys.argv) > 5 else 14]:
        v = val(D, a, r[4], r[5], stmt)
        print('   %3d %-55s %-45s %s %s neg=%s' % (r[2], r[4][:55], r[6][:45], 'C' if is_custom(D, r[4], r[5]) else ' ', v, r[7]))
