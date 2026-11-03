import json,sys
from decimal import Decimal as D
run=sys.argv[1]
cells={(c['ticker'],c['period_end']):c for c in json.load(open(run+'/debt_replay.json'))['cells']}
M=10**6; K=10**3
# (ticker, cell period_end, expected $, Verifier section / source, note)
KEY=[
("DVN","2017-12-31",6864*M,"V1 DVN 2017 rule 3: 115+6,749 (0001564590-19-003382 R4)",""),
("AAPL","2015-09-30",64328*M,"V1 AAPL 2015-09-26: 8,499+2,500+53,329 (0001628280-16-020309 R5)",""),
("EMR","2015-09-30",6841*M,"V1 EMR: 2,552+4,289 (0000032604-16-000105 R5)",""),
("KKR","2015-12-31",18714597*K,"V1 KKR $K 18,714,597 (0001404912-17-000005 R2)",""),
("AMZN","2016-12-31",17830*M,"V1/V3 AMZN: 7,694+1,056+4,000+5,080 (0001018724-18-000005)",""),
("AJG","2015-12-31",D('2316.7')*M,"V1 AJG 245+2,071.7 (0001193125-17-038619 R4)","2,453.7 if premium financing counts"),
("AJG","2015-12-31",D('2453.7')*M,"V1 AJG with premium financing 137","alternative reading"),
("BRKR","2015-12-31",D('265.8')*M,"V1 BRKR 0.6+265.2 (0001047469-17-001114 R2)",""),
("HD","2016-01-31",21216*M,"V1 HD 350+77+20,789 (0000354950-17-000005 R2)",""),
("META","2025-12-31",59928*M,"V2 META 58,744+1,184 (10-K 0001628280-26-003942 R61)","only if 10-Q debt lines equal (Ritwik 6)"),
("META","2022-12-31",10613*M,"V2 META 9,923+690 (0001326801-24-000012 R3,R64)","CONTESTED: 690 is the 2023-12-31 value in FSN; 2022 value 687 (0001326801-23-000013)"),
("NI","2024-12-31",D('13960.3')*M,"V2 NI 604.6+1,281.2+12,074.5 (0001111711-26-000027 R6)",""),
("DIS","2025-09-30",42026*M,"V2 DIS 6,711+35,315 (0001744489-26-000057 R4)",""),
("MSFT","2015-06-30",35292*M,"V2 MSFT 4,985+2,499+27,808 (0001193125-16-662209 R5)",""),
("META","2018-12-31",0,"V3 META (0001326801-19-000009 R2; FY2019 R47 filer context error)",""),
("MSFT","2017-06-30",88732*M,"V3 MSFT 9,072+1,049+76,073+2,538 (0001564590-18-019062 R4,R103)",""),
("GOOG","2024-12-31",13559*M,"V3 GOOG 10,883+999+1,677 (0001652044-26-000018 R3,R67,R61)",""),
("NVDA","2017-01-31",2789*M,"V3 NVDA 2017-01-29: 796+1,983+6+4 (0001045810-17-000027 R4,R50)","cell key is the month-end"),
("WMT","2021-01-31",48871*M,"V4 (0000104169-21-000033 R4)",""),
("WMT","2023-01-31",44622*M,"V4 (0000104169-23-000020 R5)",""),
("WMT","2024-01-31",46891*M,"V4 (0000104169-24-000056 R5)",""),
("WMT","2026-01-31",51523*M,"V4 (0000104169-26-000055 R5)",""),
("NVDA","2016-01-31",1427*M,"V4 NVDA 1,413+0+10+4 (0001045810-16-000205 R4)",""),
("NVDA","2017-04-30",2208*M,"V4 (0001045810-17-000075 R4,R40)",""),
("NVDA","2017-07-31",2076*M,"V4 (0001045810-17-000123 R4,R40)",""),
]
out=[]
for t,p,exp,src,note in KEY:
    c=cells.get((t,p))
    if c is None: out.append((t,p,exp,None,'no cell',src,note,'MISSING')); continue
    got=c['slot_lease_inclusive']
    if c['verdict']!='publishable' or got is None: res='HELD' ; gv=None
    else:
        gv=D(got); res='PASS' if abs(gv-D(exp))<=D(1) else 'WRONG'
    out.append((t,p,exp,gv,c['verdict'],src,note,res))
for o in out: print(o[0],o[1],'expected',D(o[2]).normalize(),'got',None if o[3] is None else o[3].normalize(),o[4],o[7],'|',o[6])
json.dump([dict(ticker=o[0],period=o[1],expected=str(o[2]),got=None if o[3] is None else str(o[3]),verdict=o[4],source=o[5],note=o[6],result=o[7]) for o in out],open(run+'/grade.json','w'),indent=1)
