import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
D = load(); T = json.load(open(os.path.join(OUT, 'taxo.json')))
pat, stmt, rx = sys.argv[1], sys.argv[2], re.compile(sys.argv[3], re.I)
k = int(sys.argv[4]) if len(sys.argv) > 4 else 3
for a, name, sic in T['res'][pat]['ex'][:k]:
    print('==', a, name, sic)
    for r in rows(D, a, stmt, paren=(stmt == 'BSP')) if stmt != 'BSP' else rows(D, a, 'BS', paren=True):
        if rx.search(r[6]) or rx.search(r[4]):
            print('   %3d %-58s %-48s %s %s neg=%s' % (r[2], r[4][:58], r[6][:48], 'C' if is_custom(D, r[4], r[5]) else ' ', val(D, a, r[4], r[5], 'BS' if stmt.startswith('BS') else stmt), r[7]))
