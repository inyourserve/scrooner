import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
D = load()
# args: adsh:STMT:tagregex ...
for spec in sys.argv[1:]:
    a, st, rx = spec.split(':', 2)
    s = D['sub'][a]
    for r in D['pre'].get(a, []):
        if r[0] == st and re.search(rx, r[4]):
            print(a, s['cik'], s['name'][:25], 'R%d' % r[1], 'paren' if r[3] == '1' else '', r[4], '|', r[6], '|', val(D, a, r[4], r[5], 'BS' if st == 'BS' else st))
