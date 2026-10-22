import sys,re,os
sys.argv=[sys.argv[0],sys.argv[1]]+sys.argv[2:]
import sec_rpages as fetch
from sec_rpages import get,rows
KEY=re.compile(r'^(total )?(net )?(revenue|sales)|total revenues|operating income|income from operations|operating profit|net (income|earnings|loss)|diluted|total assets|total (stockholders|shareholders|equity)|net cash provided|cash provided by operating|capital expenditures|purchases? of property|additions to property|\d+ months ended|(jun|jul|mar|sep|dec)[a-z]*\. \d+, 20\d\d|total .*equity|^income before|earnings before',re.I)
def page(base,n):
    t=get(base+f'R{n}.htm'); r=[]
    for x in rows(t):
        if x.strip()=='X' or x.startswith('X'): break
        r.append(x)
    return r
def go(cik,acc,pages=range(2,9)):
    base=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-','')}/"
    print('=====',cik,acc)
    for n in pages:
        r=page(base,n)
        if not r: continue
        title=r[0]
        if re.search(r'document and entity|cover',title,re.I): 
            for x in r[:60]:
                if re.search(r'shares outstanding|public float|fiscal year|period end|document type',x,re.I): print('   COVER',x[:140])
            continue
        print('--R%d'%n,title[:110])
        for x in r[1:60]:
            if KEY.search(x): print('    ',x[:150])
if __name__=='__main__':
    go(sys.argv[2],sys.argv[3])
