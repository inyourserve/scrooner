"""Build machine-readable tables from the FASB US-GAAP taxonomy releases.

Usage: python3 -I build_taxonomy.py <download_dir> <out_dir>

Reads only XML (xml.etree). Never executes anything from the archives.
Scope: the us-gaap namespace (elts/us-gaap-<ver>.xsd) plus calculation
linkbases under stm/ and dis/. The ebp/ (employee benefit plan) sub-taxonomy
is out of scope.
"""
import csv
import glob
import gzip
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

YEARS = list(range(2014, 2027))
XS = "http://www.w3.org/2001/XMLSchema"
XBRLI = "http://www.xbrl.org/2003/instance"
LINK = "http://www.xbrl.org/2003/linkbase"
XL = "http://www.w3.org/1999/xlink"
XLINK = lambda a: "{%s}%s" % (XL, a)

CALC_ARCROLES = {
    "http://www.xbrl.org/2003/arcrole/summation-item": "2003",
    "https://xbrl.org/2023/arcrole/summation-item": "2023",
}
DEP_ARCROLES = {
    "http://www.xbrl.org/2003/arcrole/essence-alias": "essence-alias",
    "http://www.xbrl.org/2009/arcrole/dep-concept-deprecatedConcept": "concept",
    "http://www.xbrl.org/2009/arcrole/dep-aggregateConcept-deprecatedPartConcept": "aggregateConcept-deprecatedPart",
    "http://www.xbrl.org/2009/arcrole/dep-partConcept-deprecatedAggregateConcept": "partConcept-deprecatedAggregate",
    "http://www.xbrl.org/2009/arcrole/dep-dimensionallyQualifiedConcept-deprecatedConcept": "dimensionallyQualified",
    "http://www.xbrl.org/2009/arcrole/dep-mutuallyExclusiveConcept-deprecatedConcept": "mutuallyExclusive",
}
DEP_LABEL_RE = re.compile(r"\(Deprecated (\d{4})(?:-\d\d-\d\d)?\)\s*$")


def year_root(dl, y):
    roots = glob.glob(os.path.join(dl, "x%d" % y, "us-gaap-*"))
    return roots[0] if len(roots) == 1 else None


def ver_suffix(root):
    # us-gaap-2014-01-31 -> 2014-01-31 ; us-gaap-2026 -> 2026
    return os.path.basename(root)[len("us-gaap-"):]


def frag_to_qname(href):
    """'../elts/us-gaap-2026.xsd#us-gaap_Revenues' -> ('us-gaap','Revenues')."""
    frag = href.split("#", 1)[1]
    if "_" in frag:
        p, n = frag.split("_", 1)
        return p, n
    return "", frag


def qn(p, n):
    return n if p == "us-gaap" else "%s:%s" % (p, n)


def parse_linkbase(path):
    """Yield (link_tag, link_role, locs{label:qname}, resources{label:[(role,text,elem)]}, arcs[(arcrole, from, to, attrib)])."""
    tree = ET.parse(path)
    for ext in tree.getroot().iter():
        if ext.get(XLINK("type")) != "extended":
            continue
        locs, res, arcs = {}, defaultdict(list), []
        for ch in ext:
            t = ch.get(XLINK("type"))
            if t == "locator":
                locs[ch.get(XLINK("label"))] = frag_to_qname(ch.get(XLINK("href")))
            elif t == "resource":
                res[ch.get(XLINK("label"))].append((ch.get(XLINK("role")), ch))
            elif t == "arc":
                arcs.append((ch.get(XLINK("arcrole")), ch.get(XLINK("from")), ch.get(XLINK("to")), ch.attrib))
        yield ext.tag, ext.get(XLINK("role")), locs, res, arcs


def text_of(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def parse_schema(path):
    out = {}
    tree = ET.parse(path)
    for el in tree.getroot().findall("{%s}element" % XS):
        name = el.get("name")
        sg = el.get("substitutionGroup") or ""
        out[name] = {
            "type": el.get("type") or "",
            "balance": el.get("{%s}balance" % XBRLI) or "",
            "period_type": el.get("{%s}periodType" % XBRLI) or "",
            "abstract": "1" if (el.get("abstract") or "false").lower() == "true" else "0",
            "substitution_group": sg,
        }
    return out


def concept_labels(path, roles):
    """Return {(element, role): text} for us-gaap concepts in a label linkbase."""
    out = {}
    for _tag, _role, locs, res, arcs in parse_linkbase(path):
        for arcrole, f, t, _a in arcs:
            if not arcrole.endswith("concept-label"):
                continue
            p, n = locs.get(f, ("", ""))
            if p != "us-gaap":
                continue
            for role, el in res.get(t, []):
                if role in roles:
                    out[(n, role)] = text_of(el)
    return out


def main(dl, out):
    os.makedirs(out, exist_ok=True)
    obtained = [y for y in YEARS if year_root(dl, y)]
    elements = {}  # name -> per-year attrs
    present = defaultdict(set)
    std_label, documentation = {}, {}
    # deprecation evidence
    dep_label_year = {}          # elem -> (year from '(Deprecated YYYY)' label, taxonomy year seen)
    dep_date = {}                # elem -> date from deprecatedDateLabel
    dep_reason = {}              # elem -> reason text
    dep_cn = defaultdict(list)   # elem -> [(TaxonomyVersion, replacement text, label, file)]
    dep_arcs = defaultdict(set)  # elem -> {(kind, from_qname, taxonomy_year, file)}
    dep_listed = defaultdict(set)  # elem -> {years listed in dep/depcon presentation}
    calc = defaultdict(set)      # (parent, child, weight, role, spec) -> years
    calc_rows_per_year = {}

    for y in obtained:
        root = year_root(dl, y)
        v = ver_suffix(root)
        elts = os.path.join(root, "elts")
        sch = parse_schema(os.path.join(elts, "us-gaap-%s.xsd" % v))
        for n, a in sch.items():
            elements.setdefault(n, {})[y] = a
            present[n].add(y)
        lab = concept_labels(os.path.join(elts, "us-gaap-lab-%s.xml" % v), {"http://www.xbrl.org/2003/role/label"})
        for (n, _r), txt in lab.items():
            std_label[(n, y)] = txt
            m = DEP_LABEL_RE.search(txt)
            if m:
                dep_label_year.setdefault(n, (int(m.group(1)), y))
        docroles = {
            "http://www.xbrl.org/2003/role/documentation",
            "http://www.xbrl.org/2009/role/deprecatedDateLabel",
            "http://www.xbrl.org/2009/role/deprecatedLabel",
        }
        doc = concept_labels(os.path.join(elts, "us-gaap-doc-%s.xml" % v), docroles)
        for (n, r), txt in doc.items():
            if r.endswith("/documentation"):
                documentation[(n, y)] = txt
            elif r.endswith("deprecatedDateLabel"):
                dep_date.setdefault(n, (txt, "us-gaap-doc-%s.xml deprecatedDateLabel" % v))
            else:
                dep_reason.setdefault(n, txt)
        # deprecation definition arcs + deprecated-items presentation lists
        for f in sorted(glob.glob(os.path.join(elts, "us-gaap-dep*-%s.xml" % v))):
            bn = os.path.basename(f)
            for tag, _role, locs, res, arcs in parse_linkbase(f):
                for arcrole, fr, to, _a in arcs:
                    pf, nf = locs[fr]
                    pt, nt = locs[to]
                    if arcrole in DEP_ARCROLES and pt == "us-gaap":
                        dep_arcs[nt].add((DEP_ARCROLES[arcrole], qn(pf, nf), y, bn))
                    elif arcrole.endswith("parent-child") and pt == "us-gaap" and "-pre-" in bn:
                        if not nt.endswith("Abstract") or True:
                            dep_listed[nt].add(y)
        # change notes (deprecationNote references), 2017+
        cnf = os.path.join(elts, "us-gaap-cn-ref-%s.xml" % v)
        if os.path.exists(cnf):
            for _tag, _role, locs, res, arcs in parse_linkbase(cnf):
                for arcrole, fr, to, _a in arcs:
                    p, n = locs.get(fr, ("", ""))
                    if p != "us-gaap":
                        continue
                    for role, el in res.get(to, []):
                        parts = {c.tag.split("}")[1]: text_of(c) for c in el}
                        if not ({"DeprecatedLabel", "DeprecationReplacement", "DeprecatedDate"} & set(parts)
                                or parts.get("ElementDeprecated", "").lower() == "true"):
                            continue
                        tv = parts.get("TaxonomyVersion", "")
                        dd = parts.get("DeprecatedDate", "")
                        if not tv and re.match(r"\d{4}", dd):
                            tv = dd[:4]
                        dep_cn[n].append((tv, parts.get("DeprecationReplacement", ""),
                                          parts.get("DeprecatedLabel", ""), os.path.basename(cnf), dd,
                                          (role or "").rsplit("/", 1)[-1]))
                        if dd:
                            dep_date.setdefault(n, (dd, "%s %s DeprecatedDate" % (os.path.basename(cnf), (role or "").rsplit("/", 1)[-1])))
        # calculations
        cnt = 0
        for sub in ("stm", "dis"):
            for f in sorted(glob.glob(os.path.join(root, sub, "*-cal-*.xml"))):
                for tag, role, locs, res, arcs in parse_linkbase(f):
                    rseg = (role or "").rstrip("/").rsplit("/", 1)[-1]
                    for arcrole, fr, to, a in arcs:
                        if arcrole not in CALC_ARCROLES:
                            continue
                        par, chi = qn(*locs[fr]), qn(*locs[to])
                        w = a.get("weight")
                        w = str(float(w)) if w is not None else ""
                        w = w[:-2] if w.endswith(".0") else w
                        calc[(par, chi, w, rseg)].add((y, CALC_ARCROLES[arcrole]))
                        cnt += 1
        calc_rows_per_year[y] = cnt
        print(y, "elements", len(sch), "calc arcs", cnt, file=sys.stderr)

    # ---------- deprecations ----------
    all_dep = set(dep_label_year) | set(dep_date) | set(dep_cn) | set(dep_arcs) | set(dep_listed)
    all_dep = {e for e in all_dep if e in elements or e in dep_arcs}
    dep_rows = {}
    successors = {}
    for e in sorted(all_dep):
        srcs, year, date = [], None, ""
        if e in dep_date:
            date = dep_date[e][0]
            year = int(date[:4]) if re.match(r"\d{4}", date) else None
            srcs.append(dep_date[e][1])
        cn_years = sorted({int(t[0]) for t in dep_cn.get(e, []) if t[0].isdigit()})
        if cn_years:
            srcs.append("cn-ref (deprecation/change note) TaxonomyVersion=%s" % ",".join(map(str, cn_years)))
            if year is None:
                year = cn_years[0]
        if e in dep_label_year:
            ly, seen = dep_label_year[e]
            srcs.append("standard label '(Deprecated %d)' (first seen in %d release)" % (ly, seen))
            if year is None:
                year = ly
        arcs = sorted(dep_arcs.get(e, []), key=lambda t: (t[2], t[0], t[1]))
        if arcs:
            files = sorted({"%s %s" % (t[3], t[0]) for t in arcs})
            srcs.append("def arcs: " + "; ".join(files[:6]) + ("; ..." if len(files) > 6 else ""))
            if year is None:
                year = arcs[0][2]
        if dep_listed.get(e):
            srcs.append("dep/depcon-pre DeprecatedItems list years=%d-%d" % (min(dep_listed[e]), max(dep_listed[e])))
            if year is None:
                year = min(dep_listed[e])
        # successors from arcs (use the latest release's arcs that mention this element)
        kinds = sorted({t[0] for t in arcs})
        succ_concepts, dims = [], []
        if arcs:
            last_y = max(t[2] for t in arcs)
            cur = [t for t in arcs if t[2] == last_y]
            for kind, frm, _y, _f in cur:
                if kind == "dimensionallyQualified":
                    if frm.endswith("Axis") or frm.endswith("Member") or frm.endswith("Domain"):
                        dims.append(frm)
                    else:
                        succ_concepts.append(frm)
                else:
                    succ_concepts.append(frm)
        succ_concepts = sorted(set(succ_concepts))
        cn_repl = sorted({t[1] for t in dep_cn.get(e, []) if t[1]})
        if not succ_concepts and cn_repl:
            for r in cn_repl:
                for tok in re.split(r"[\s,;|]+", r):
                    tok = tok.strip()
                    if ":" in tok or not tok or tok.endswith(("Axis", "Member", "Domain")):
                        continue
                    if tok in elements and tok != e:
                        succ_concepts.append(tok)
            succ_concepts = sorted(set(succ_concepts))
            if succ_concepts:
                srcs.append("replacement parsed from cn-ref DeprecationReplacement text")
        repl = "|".join(succ_concepts)
        if dims:
            repl += " [" + ", ".join(sorted(set(dims))) + "]"
        reason = dep_reason.get(e) or next((t[2] for t in dep_cn.get(e, []) if t[2]), "")
        successors[e] = [s for s in succ_concepts if ":" not in s]
        dep_rows[e] = {
            "element": e,
            "deprecated_in_year": year or "",
            "deprecated_date": date,
            "replacement_element": repl,
            "replacement_text_cn_ref": " || ".join(cn_repl),
            "deprecation_kind": "|".join(kinds),
            "reason": reason[:300],
            "source": " ; ".join(srcs),
        }

    def chains(e, seen=()):
        nxt = [s for s in successors.get(e, []) if s not in seen and s != e]
        if not nxt:
            return [[e]]
        out = []
        for s in nxt:
            if s in successors and successors[s]:
                for c in chains(s, seen + (e,)):
                    out.append([e] + c)
            else:
                out.append([e, s])
        return out

    for e, r in dep_rows.items():
        cs = chains(e)
        r["chain"] = " ; ".join(" -> ".join(c) for c in cs) if successors.get(e) else ""
        r["final_successor"] = "|".join(sorted({c[-1] for c in cs})) if successors.get(e) else ""

    # ---------- write elements.csv ----------
    def latest(d, n):
        ys = [yy for (nn, yy) in d if nn == n]
        return None
    lab_by = defaultdict(dict)
    for (n, y), t in std_label.items():
        lab_by[n][y] = t
    doc_by = defaultdict(dict)
    for (n, y), t in documentation.items():
        doc_by[n][y] = t
    years_present = {}
    el_path = os.path.join(out, "elements.csv")
    with open(el_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "first_year", "last_year", "type", "balance", "period_type", "abstract",
                    "substitution_group", "standard_label", "documentation", "deprecated_year", "replacement"])
        for n in sorted(elements):
            ys = sorted(present[n])
            a = elements[n][ys[-1]]
            lb = lab_by[n][max(lab_by[n])] if lab_by.get(n) else ""
            dc = doc_by[n][max(doc_by[n])] if doc_by.get(n) else ""
            d = dep_rows.get(n, {})
            years_present[n] = compact(ys)
            w.writerow([n, ys[0], ys[-1], a["type"], a["balance"], a["period_type"], a["abstract"],
                        a["substitution_group"], lb, dc[:500], d.get("deprecated_in_year", ""),
                        d.get("replacement_element", "")])
    for fname, cols in (("deprecations.csv", ["element", "deprecated_in_year", "deprecated_date", "replacement_element",
                                               "source", "chain"]),
                        ("deprecations_detail.csv", ["element", "deprecated_in_year", "deprecated_date",
                                                     "replacement_element", "source", "chain", "final_successor",
                                                     "deprecation_kind", "replacement_text_cn_ref", "reason"])):
        with open(os.path.join(out, fname), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for e in sorted(dep_rows):
                w.writerow({k: dep_rows[e].get(k, "") for k in cols})
    with open(os.path.join(out, "elements_years.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "years_present"])
        for n in sorted(years_present):
            w.writerow([n, years_present[n]])
    calc_path = os.path.join(out, "calc.csv")
    with open(calc_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["parent", "child", "weight", "role", "first_year", "last_year"])
        w2fh = open(os.path.join(out, "calc_years.csv"), "w", newline="", encoding="utf-8")
        w2 = csv.writer(w2fh)
        w2.writerow(["parent", "child", "weight", "role", "years", "calc_arcrole_spec"])
        for (p, c, wt, r), yspec in sorted(calc.items()):
            ys = sorted({y for y, _s in yspec})
            spec = "|".join(sorted({s for _y, s in yspec}))
            w.writerow([p, c, wt, r, ys[0], ys[-1]])
            w2.writerow([p, c, wt, r, compact(ys), spec])
        w2fh.close()
    with open(os.path.join(out, "_build_stats.txt"), "w") as fh:
        fh.write("years_obtained=%s\n" % ",".join(map(str, obtained)))
        fh.write("elements=%d\ndeprecations=%d\ncalc_rows=%d\n" % (len(elements), len(dep_rows), len(calc)))
        for y in obtained:
            fh.write("year %d: schema_elements=%d calc_arcs=%d\n" % (
                y, sum(1 for n in present if y in present[n]), calc_rows_per_year[y]))


def compact(ys):
    """[2014,2015,2016,2018] -> '2014-2016,2018'"""
    out, start, prev = [], None, None
    for y in ys:
        if start is None:
            start = prev = y
        elif y == prev + 1:
            prev = y
        else:
            out.append(str(start) if start == prev else "%d-%d" % (start, prev))
            start = prev = y
    if start is not None:
        out.append(str(start) if start == prev else "%d-%d" % (start, prev))
    return ",".join(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
