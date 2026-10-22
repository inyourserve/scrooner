import sys,re,time,urllib.request,os,html
UA="Scrooner research inyourserve@gmail.com"
OUT=sys.argv[1]
os.makedirs(os.path.join(OUT,'pages'),exist_ok=True)
def get(u):
    f=os.path.join(OUT,'pages',re.sub(r'\W','_',u)[-120:])
    if os.path.exists(f): return open(f).read()
    time.sleep(0.6)
    import subprocess
    t=subprocess.run(['curl','-s','-m','40','-A',UA,u],capture_output=True).stdout.decode('utf8','ignore')
    open(f,'w').write(t); return t
def rows(t):
    out=[]
    for tr in re.findall(r'<tr.*?</tr>',t,re.S):
        cells=[html.unescape(re.sub(r'<[^>]+>','',c)).strip() for c in re.findall(r'<t[dh].*?</t[dh]>',tr,re.S)]
        cells=[re.sub(r'\s+',' ',c) for c in cells]
        if any(cells): out.append(' | '.join(cells[:4]))
    return out
def run(cik,acc,pats):
    base=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-','')}/"
    fs=get(base+'FilingSummary.xml')
    reps=re.findall(r'<Report[^>]*>.*?<ShortName>(.*?)</ShortName>.*?<HtmlFileName>(.*?)</HtmlFileName>',fs,re.S)
    res={}
    for name,fn in reps:
        n=html.unescape(name).lower()
        for k,p in pats.items():
            if k not in res and re.search(p,n) and 'parenthetical' not in n and 'details' not in n:
                res[k]=(name,fn)
    print('=====',cik,acc)
    for k,(name,fn) in res.items():
        print('--',k,name,fn)
        for r in rows(get(base+fn))[:int(os.environ.get('N','45'))]: print('  ',r)
if __name__=='__main__':
    cik,acc=sys.argv[2],sys.argv[3]
    pats={'IS':r'(income|operations|earnings)','BS':r'(balance sheet|financial position|financial condition)','CF':r'cash flow'}
    run(cik,acc,pats)
