"""Print calculation-arc parents that contain debt-family children (stdlib, run with -I). usage: cal_tree.py <cal.xml> [regex]"""
import re, sys
import xml.etree.ElementTree as ET
ns = "{http://www.xbrl.org/2003/linkbase}"; xl = "{http://www.w3.org/1999/xlink}"
rx = re.compile(sys.argv[2] if len(sys.argv) > 2 else "Debt|Borrow|Lease|Paper|Notes")
tree = ET.parse(sys.argv[1]).getroot()
tag = lambda h: h.split("#")[-1].split("_", 1)[-1]
for link in tree.iter(ns + "calculationLink"):
    loc = {l.get(xl + "label"): tag(l.get(xl + "href")) for l in link.iter(ns + "loc")}
    kids = {}
    for a in link.iter(ns + "calculationArc"):
        kids.setdefault(loc[a.get(xl + "from")], []).append((loc[a.get(xl + "to")], a.get("weight")))
    for p, ks in kids.items():
        if any(rx.search(k) for k, _ in ks) or rx.search(p):
            print(link.get(xl + "role").rsplit("/", 1)[-1][:40], "|", p, "<-", ", ".join(f"{k}({w})" for k, w in ks if rx.search(k) or True)[:600])
