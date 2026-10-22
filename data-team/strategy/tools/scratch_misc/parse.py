import re,csv,json
sh={r['ticker']:r for r in csv.DictReader(open('../shards.csv'))}
def canon(h):
    h=h.lower()
    if h.startswith('blank'): return 'tot'
    if h in('not_applicable','na'): return 'NA'
    if h in('nr-f',): return 'NRF'
    if h in('snr','unknown: snr') or 'suspected not_reported' in h: return 'SNR'
    if h in('mapping_gap','map'): return 'MAP'
    if h in('derivation_gap','der'): return 'DER'
    if h in('period_gap','per'): return 'PER'
    if h in('upstream_conflict',): return 'CONF'
    if h=='mcs': return 'MCS'
    if h=='fpi': return 'FPI'
    if h.startswith('unknown') or h in('unk','ups','upstream / unknown','ups / unknown'): return 'UNK'
    if h.startswith('wrong'): return None
    return None
rows=[]
for n in [2,3]+list(range(5,20)):
    f=f"S{n:03d}.md"
    t=open(f).read().split('\n')
    inb=False;hdr=None
    for l in t:
        if re.match(r'## (Blanks by cause|Blank counts by cause)',l) or (n==3 and l.startswith('## Baseline used')): inb=True;continue
        if inb and l.startswith('## '): break
        if not inb: continue
        if l.startswith('| Company') or l.startswith('| Ticker'):
            hdr=[x.strip() for x in l.strip().strip('|').split('|')]; continue
        if hdr and l.startswith('|') and not l.startswith('|---') and 'Total' not in l:
            c=[x.strip() for x in l.strip().strip('|').split('|')]
            m=re.match(r'([A-Z\.\-]+)',c[0].replace('**',''))
            if not m: continue
            tk=m.group(1)
            if len(c)<len(hdr)-1: continue
            v={}
            for h,x in zip(hdr[1:],c[1:]):
                k=canon(h)
                if k and re.fullmatch(r'\d+',x.replace('*','')):
                    v[k]=v.get(k,0)+int(x.replace('*',''))
            if n==3:
                # cols: Ticker,id,Blanks,n/a,not_reported,mapping_gap,derivation_gap,period_gap,unknown
                v={'tot':int(c[2]),'NA':int(c[3]),'SNR':int(c[4]),'MAP':int(c[5]),'DER':int(c[6]),'PER':int(c[7]),'UNK':int(c[8])}
            if tk in sh: rows.append((n,tk,v))
            else: print('?',n,tk)
print(len(rows))
json.dump(rows,open('/private/tmp/claude-501/-Users-vikash-scrooner/99c20ae4-2938-4dd5-8ec6-924194f63d67/scratchpad/rows.json','w'))
