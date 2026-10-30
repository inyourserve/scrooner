import re, sys, html
def rows(path):
    t=open(path,encoding="utf-8",errors="replace").read()
    title=re.search(r'<th class="tl"[^>]*>(.*?)</th>',t,re.S)
    hdr=re.findall(r'<th class="th"[^>]*>(.*?)</th>',t,re.S)
    out=[]
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',t,re.S):
        m=re.search(r'<td class="pl[^"]*"[^>]*>(.*?)</td>',tr,re.S)
        if not m: continue
        tag=re.search(r"defref_([A-Za-z0-9\-]+_[A-Za-z0-9]+)",tr)
        lab=html.unescape(re.sub(r'<[^>]+>','',m.group(1))).strip()
        vals=[html.unescape(re.sub(r'<[^>]+>','',v)).strip() for v in re.findall(r'<td class="(?:nump|num|text)"[^>]*>(.*?)</td>',tr,re.S)]
        out.append((lab, tag.group(1) if tag else "", vals[:2]))
    return (re.sub(r'<[^>]+>',' ',title.group(1)).strip() if title else ""), [re.sub(r'<[^>]+>',' ',h).strip() for h in hdr][:3], out
if __name__=="__main__":
    p=sys.argv[1]; pat=re.compile(sys.argv[2],re.I) if len(sys.argv)>2 else None
    ti,h,rs=rows(p); print("##",ti,"|",h)
    for i,(l,tg,v) in enumerate(rs):
        if pat is None or pat.search(l) or pat.search(tg): print(f"  [{i}] {l[:70]} | {tg} | {v}")
