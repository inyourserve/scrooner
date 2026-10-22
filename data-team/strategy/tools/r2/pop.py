import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
D = load()
F = D['filings']
print('distinct 10-K filers', len(F), 'of', len(D['sub']), 'filings')
print(collections.Counter(family(D['sub'][a]['sic']) for a in F))
print('with IS rows', sum(1 for a in F if rows(D, a, 'IS')), 'BS', sum(1 for a in F if rows(D, a, 'BS')), 'CF', sum(1 for a in F if rows(D, a, 'CF')))
print(collections.Counter(D['sub'][a]['afs'] for a in F))
