"""Read-only: compact 10-K face-statement extract from an FSDS quarter (dir or zip). Output pickle."""
import sys, csv, io, zipfile, os, pickle, collections
src, out = sys.argv[1], sys.argv[2]
csv.field_size_limit(10**9)
def opener(name):
    if src.endswith('.zip'):
        z = zipfile.ZipFile(src); return io.TextIOWrapper(z.open(name), encoding='utf-8', errors='replace', newline='')
    return open(os.path.join(src, name), encoding='utf-8', errors='replace', newline='')
def rd(name): return csv.DictReader(opener(name), delimiter='\t', quoting=csv.QUOTE_NONE)
sub = {}
for r in rd('sub.txt'):
    if r['form'] == '10-K':
        sub[r['adsh']] = dict(cik=r['cik'], name=r['name'], sic=r['sic'], period=r['period'], fye=r['fye'], afs=r['afs'], fp=r['fp'])
print('10-K', len(sub))
tagc = {}
for r in rd('tag.txt'):
    tagc[(r['tag'], r['version'])] = (r['custom'], r['iord'], r['crdr'], r['datatype'], r['tlabel'])
pre = collections.defaultdict(list); facetags = collections.defaultdict(set)
for r in rd('pre.txt'):
    a = r['adsh']
    if a in sub and r['stmt'] in ('IS', 'BS', 'CF', 'EQ', 'CI'):
        pre[a].append((r['stmt'], int(r['report']), int(r['line']), r['inpth'], r['tag'], r['version'], r['plabel'], r['negating']))
        facetags[a].add(r['tag'])
print('pre filings', len(pre))
EXTRA = set(open(sys.argv[3]).read().split())
num = collections.defaultdict(dict); dimtags = collections.defaultdict(set); other = collections.defaultdict(dict)
n = 0
for r in rd('num.txt'):
    a = r['adsh']
    if a not in sub: continue
    t = r['tag']
    if t not in facetags[a] and t not in EXTRA: continue
    if r['coreg'] or r['ddate'] != sub[a]['period'] or r['qtrs'] not in ('0', '4'): continue
    if r['uom'] not in ('USD', 'shares', 'USD/shares'): continue
    if not r['value']: continue
    key = (t, r['version'], r['qtrs'], r['uom'])
    if r['segments']:
        dimtags[a].add(key); continue
    num[a][key] = float(r['value']); n += 1
print('num kept', n)
pickle.dump(dict(sub=sub, tagc=tagc, pre=dict(pre), num=dict(num), dim={k: v for k, v in dimtags.items()}), open(out, 'wb'))
