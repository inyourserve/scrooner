"""Build DQC rule tables.

Usage: python3 -I build_dqc.py <download_dir> <out_dir>

Sources:
 - FASB US-GAAP taxonomy releases 2020-2026, folder dqcrules/ (DQC element lists
   published inside the official taxonomy, (c) XBRL US).
 - xbrl.us approved-rules index page (rule id, title, description, version, dates).
 - xbrl.us individual rule pages where they could be downloaded (message template).
"""
import csv
import glob
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

XL = "http://www.w3.org/1999/xlink"
X = lambda a: "{%s}%s" % (XL, a)


def txt(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def strip_tags(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def frag(href):
    f = href.split("#", 1)[1]
    p, n = f.split("_", 1) if "_" in f else ("", f)
    return p, n


def parse_rule_file(path):
    """Return (rule_meta dict, list of element rows)."""
    root = ET.parse(path).getroot()
    meta, rows = {}, []
    labels = {}       # dqcrules abstract name -> label
    elem_ids = defaultdict(set)  # (prefix, name) -> rule element ids
    excl = []
    for ext in root.iter():
        if ext.get(X("type")) != "extended":
            continue
        tag = ext.tag.split("}")[1]
        locs, res, arcs = {}, defaultdict(list), []
        for ch in ext:
            t = ch.get(X("type"))
            if t == "locator":
                locs[ch.get(X("label"))] = frag(ch.get(X("href")))
            elif t == "resource":
                res[ch.get(X("label"))].append(ch)
            elif t == "arc":
                arcs.append(ch)
        if tag == "labelLink":
            for a in arcs:
                p, n = locs[a.get(X("from"))]
                for r in res.get(a.get(X("to")), []):
                    labels[n] = txt(r)
        elif tag == "referenceLink":
            for lab, rs in res.items():
                for r in rs:
                    parts = {c.tag.split("}")[1]: txt(c) for c in r}
                    if "ruleId" in parts:
                        meta = parts
            for a in arcs:
                fr = locs.get(a.get(X("from")))
                for r in res.get(a.get(X("to")), []):
                    parts = {c.tag.split("}")[1]: txt(c) for c in r}
                    if "ruleElementId" in parts and fr:
                        elem_ids[fr].add(parts["ruleElementId"])
                    for k in ("allowableSubString", "disallowableSubString"):
                        if k in parts and fr:
                            excl.append((fr, k, parts[k]))
        elif tag == "definitionLink":
            # parent map for group resolution
            parent = {}
            for a in arcs:
                parent.setdefault(a.get(X("to")), a.get(X("from")))
            for a in arcs:
                fl, tl = a.get(X("from")), a.get(X("to"))
                fp, fn = locs[fl]
                tp, tn = locs[tl]
                arcrole = a.get(X("arcrole")).rstrip("/").rsplit("/", 1)[-1]
                if arcrole == "concept-rule":  # 2020 name of the same group-membership arcrole
                    arcrole = "rule-concept"
                if tp.startswith("dqcrules"):
                    continue  # rule -> group structure
                # nearest dqcrules group ancestor
                g, cur, seen = "", fl, set()
                while cur and cur not in seen:
                    seen.add(cur)
                    cp, cn = locs[cur]
                    if cp.startswith("dqcrules"):
                        g = cn
                        break
                    cur = parent.get(cur)
                rows.append({"group": g, "prefix": tp, "element": tn,
                             "parent_element": "" if fp.startswith("dqcrules") else (fn if fp == "us-gaap" else "%s:%s" % (fp, fn)),
                             "arcrole": arcrole, "weight": a.get("weight") or ""})
    return meta, rows, labels, elem_ids, excl


def group_label(labels, g):
    lb = labels.get(g, g)
    lb = re.sub(r"\s*\[Abstract\]\s*$", "", lb)
    lb = re.sub(r"^DQC\.US\.\d{4}\.?", "", lb).strip()
    return lb or g


def parse_index(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    out = {}
    for blk in s.split('<div class="entryPost">')[1:]:
        m = re.search(r'class="category">\s*([A-Za-z]+_\d{4})', blk)
        if not m:
            continue
        rid = m.group(1).upper()
        title = re.search(r'<h2 class="entry-title"><a href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
        appr = re.search(r"Approved:\s*<br\s*/?>\s*([^<]+)", blk)
        eff = re.search(r"Effective:\s*<br\s*/?>\s*([^<\n]+)", blk)
        upd = re.search(r"Last updated\s*<em>([^<]+)</em>\s*as part of\s*<b>([^<]+)</b>", blk)
        desc = re.search(r"</div>\s*<p>(.*?)</p>", blk[blk.find("entry-title"):], re.S)
        tags = re.findall(r'<span class="dqc-[a-z]+">([^<]+)</span>', blk)
        out[rid] = {
            "rule_id": rid,
            "title": strip_tags(title.group(2)) if title else "",
            "url": title.group(1) if title else "",
            "approved": appr.group(1).strip() if appr else "",
            "effective": eff.group(1).strip() if eff else "",
            "last_updated": upd.group(1).strip() if upd else "",
            "version": upd.group(2).strip() if upd else "",
            "applies_to": "|".join(t.strip() for t in tags),
            "description": strip_tags(desc.group(1)) if desc else "",
        }
    return out


def parse_rule_page(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    t = strip_tags(re.sub(r"<(br|p|div|h\d|li)[^>]*>", "\n", s))
    out = {}
    m = re.search(r"Status:\s*(\w+)", t)
    out["status"] = m.group(1) if m else ""
    m = re.search(r"General message template\s*(.*?)(?:Rule element ID index|Rule version: \$\{ruleVersion\})", t, re.S)
    if not m:
        m = re.search(r"[Mm]essage template\s*(.*?)(?:Rule element ID index|Rule version: \$\{ruleVersion\})", t, re.S)
    mt = m.group(1).strip() if m else ""
    if mt.startswith("contains text"):
        k = mt.find("template", len("contains text"))
        mt = mt[k + len("template"):].strip() if k >= 0 else mt
    out["message_template"] = mt
    return out


def main(dl, out):
    index_path = os.path.join(dl, "xbrlus", "rules.html")
    index = parse_index(index_path) if os.path.exists(index_path) else {}
    pages = {}
    for f in glob.glob(os.path.join(dl, "xbrlus", "rule_pages", "*.html")):
        rid = os.path.basename(f)[:-5].upper()
        pages[rid] = parse_rule_page(f)
    tax_meta = {}
    tax_years = defaultdict(set)
    el_rows = {}   # key -> row with years
    all_labels = {}
    for y in range(2020, 2027):
        byrule = defaultdict(list)
        for f in sorted(glob.glob(os.path.join(dl, "x%d" % y, "*", "dqcrules", "dqcrules-[0-9][0-9][0-9][0-9]-*"))):
            if f.endswith((".xsd", ".xml")):
                byrule[re.search(r"dqcrules-(\d{4})-", os.path.basename(f)).group(1)].append(f)
        for num, files in sorted(byrule.items()):
            meta, rows, labels, elem_ids, excl = {}, [], {}, defaultdict(set), []
            for f in files:
                m2, r2, l2, e2, x2 = parse_rule_file(f)
                meta = meta or m2
                rows += r2
                labels.update(l2)
                all_labels.update(l2)
                for k, v in e2.items():
                    elem_ids[k] |= v
                excl += x2
            rid = "DQC_" + num
            tax_years[rid].add(y)
            if meta:
                tax_meta[rid] = meta  # later years overwrite -> latest
            for r in rows:
                key = (rid, r["group"], r["prefix"], r["element"], r["parent_element"], r["arcrole"], r["weight"])
                e = el_rows.setdefault(key, {"years": set(), "ids": set(),
                                             "role": group_label(labels, r["group"]) if r["group"] else ""})
                e["years"].add(y)
                e["ids"] |= elem_ids.get((r["prefix"], r["element"]), set())
                if r["group"]:
                    e["role"] = group_label(labels, r["group"])
            for (fp, fn), kind, val in excl:
                key = (rid, "exclusion", "", val, fn if fp == "us-gaap" else "%s:%s" % (fp, fn), kind, "")
                e = el_rows.setdefault(key, {"years": set(), "ids": set(), "role": kind + " (regex on extension element names)"})
                e["years"].add(y)
    os.makedirs(out, exist_ok=True)
    ids = sorted(set(index) | set(tax_meta))
    with open(os.path.join(out, "dqc_rules.csv"), "w", newline="", encoding="utf-8") as fh:
        cols = ["rule_id", "title", "description", "message_template", "version", "last_updated", "approved",
                "effective", "applies_to", "status", "url", "taxonomy_rule_name", "taxonomy_rule_documentation",
                "in_fasb_taxonomy_years", "source"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for rid in ids:
            ix, tm, pg = index.get(rid, {}), tax_meta.get(rid, {}), pages.get(rid, {})
            ys = sorted(tax_years.get(rid, []))
            src = []
            if ix: src.append("xbrl.us rules index")
            if pg: src.append("xbrl.us rule page")
            if tm: src.append("FASB taxonomy dqcrules")
            w.writerow({
                "rule_id": rid,
                "title": ix.get("title") or tm.get("ruleName", ""),
                "description": (ix.get("description") or tm.get("ruleDocumentation", ""))[:500],
                "message_template": pg.get("message_template", "")[:500],
                "version": ix.get("version", ""),
                "last_updated": ix.get("last_updated", ""),
                "approved": ix.get("approved", ""),
                "effective": ix.get("effective", ""),
                "applies_to": ix.get("applies_to", ""),
                "status": pg.get("status", ""),
                "url": ix.get("url") or tm.get("URI", ""),
                "taxonomy_rule_name": tm.get("ruleName", ""),
                "taxonomy_rule_documentation": tm.get("ruleDocumentation", "")[:500],
                "in_fasb_taxonomy_years": "%d-%d" % (ys[0], ys[-1]) if ys else "",
                "source": "; ".join(src),
            })
    with open(os.path.join(out, "dqc_rule_elements.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["rule_id", "element", "role_in_rule", "element_prefix", "parent_element", "arcrole", "weight",
                    "rule_element_ids", "first_year", "last_year"])
        for (rid, g, p, el, par, arc, wt), e in sorted(el_rows.items()):
            ys = sorted(e["years"])
            if g and g != "exclusion":
                e["role"] = group_label(all_labels, g)
            w.writerow([rid, el if p in ("us-gaap", "") else "%s:%s" % (p, el), e["role"], p, par, arc, wt,
                        "|".join(sorted(e["ids"])), ys[0], ys[-1]])
    print("rules", len(ids), "index", len(index), "pages", len(pages), "taxonomy rules", len(tax_meta),
          "element rows", len(el_rows))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
