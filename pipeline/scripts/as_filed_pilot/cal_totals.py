"""Parse a calculation linkbase: print parent tags (summation-item parents) = XBRL-declared subtotals/totals. stdlib; run with -I."""
import sys
import xml.etree.ElementTree as ET
t = ET.parse(sys.argv[1]); ns = "{http://www.xbrl.org/2003/linkbase}"; xl = "{http://www.w3.org/1999/xlink}"
parents, children = set(), set()
for link in t.getroot().iter(ns + "calculationLink"):
    loc = {l.get(xl + "label"): l.get(xl + "href").split("#")[-1] for l in link.iter(ns + "loc")}
    for a in link.iter(ns + "calculationArc"):
        p, c = loc.get(a.get(xl + "from")), loc.get(a.get(xl + "to"))
        if p: parents.add(p.split("_", 1)[-1] if "_" in p else p)
        if c: children.add(c.split("_", 1)[-1] if "_" in c else c)
print("PARENTS", ",".join(sorted(parents)))
print("CHILDREN", ",".join(sorted(children)))
