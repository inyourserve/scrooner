"""Second pass over machine docmaps (shared docmap.py @558f2f15): re-open the cited R page for every not_presented,
combined, component and NOTE row plus a seeded random 10% of mapped rows, and record agree/disagree.

This is a scripted re-check by a different code path (the row is found again on its own R page by element name and
the FY0 column by period end), NOT a human hand check; rows say so.

Usage: python3 -I check_pass.py <shared_dir> <cohort.csv> <m1_dir> <cache> <out_dir> <rank_from> <rank_to>
"""
import csv, json, math, os, random, re, sys
import datetime as dt

shared, cohort, m1, cache, out_dir, lo, hi = sys.argv[1:8]
sys.path.insert(0, shared)
import docmap as D  # noqa: E402

rows = list(csv.DictReader(open(cohort)))
os.makedirs(out_dir, exist_ok=True)
BS_DP = {d[0] for d in D.DP if d[1] == "BS"}
TEMPLATES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "docmap_templates.json")))
# Dhairya OUT ruling (main @020ebb29): for banks and insurers (and the lender template, per the SYF CA/CL key) these
# data points are outside the template: OUT, not not_presented
OUT_GROUP = {"bank", "insurer", "lender"}
OUT_DPS = {"cost_of_revenue", "gross_profit", "research_and_development", "inventory", "current_assets", "current_liabilities"}
CHECK_STATUSES = {"not_presented", "combined", "component sum", "component_in_note"}


def close(a, b):
    return abs(abs(a) - abs(b)) <= max(0.5, 1e-6 * abs(b))


def page_value(base, rpage, tags, end, stmt, dp, sum_rows=False):
    """Sum of the FY0 values of the rows carrying these elements on these R pages (one tag per page or all on one)."""
    pages = rpage.split("+")
    total, found = 0.0, 0
    zero_rows = []
    for t in tags:
        hit = None
        for pg in dict.fromkeys(pages):
            p = D.parse_r(D.get(base + pg, cache))
            idx = [i for i, (m, e) in enumerate(p["cols"]) if e == end and (stmt in ("BS", "NOTE") or m in (12, None))]
            vals = []
            for r in p["rows"]:
                if r["tag"] == t:
                    for i in idx:
                        if i < len(r["vals"]) and r["vals"][i] is not None:
                            x = r["vals"][i] * p["shares_scale"] if dp == "shares_outstanding" else D.scaled(r["vals"][i], dp, p)
                            vals.append(x)
                            break
                    if vals and not sum_rows:
                        break
            if not vals and len(tags) > 1:
                row = next((r for r in p["rows"] if r["tag"] == t and any(v is not None for v in r["vals"])), None)
                if row is not None and idx:
                    vals = [0.0]  # the line is printed but blank for this period: a zero component
                    zero_rows.append(f"{t} blank in the {end} column on {pg} (0)")
            if vals:
                hit = (sum(vals), pg)
            if hit:
                break
        if hit is None:
            return None, f"{t} not found with a value in the {end} column on {rpage}"
        total += hit[0]
        found += 1
    return total, "; ".join(zero_rows)


# ---------------------------------------------------------------- rule checks (Dhairya / Tag Expert, 2026-11-12)
def metalinks(base):
    txt = D.get(base + "MetaLinks.json", cache)
    try:
        inst = next(iter(json.loads(txt)["instance"].values()))
    except Exception:
        return None
    role2r = {v.get("role"): (k, v.get("groupType", ""), v.get("shortName", "")) for k, v in inst.get("report", {}).items()}
    return inst.get("tag", {}), role2r


def relocate(base, cands, end, dp):
    """First candidate element presented anywhere in the filing -> (tag, R page, value read off that page)."""
    ml = metalinks(base)
    if ml is None:
        return None
    tags, role2r = ml
    for t in cands:
        node = tags.get(f"us-gaap_{t}")
        if not node:
            continue
        rs = sorted((role2r[x] for x in node.get("presentation", []) if x in role2r),
                    key=lambda x: (x[1] != "statement", int(re.sub(r"\D", "", x[0]) or 0)))
        for fn, grp, name in rs:
            v, _why = page_value(base, f"{fn}.htm", [f"us-gaap:{t}"], end, "CF" if grp == "statement" else "NOTE", dp)
            if v is not None:
                return t, f"{fn}.htm", v, grp, name
    return None


RULES = [  # (data point, predicate on (tags, label), ruling, replacement candidates or a status)
    ("share_buybacks", lambda t, l: re.search(r"TaxWithholding|SharesPaidForTax|Withh|Proceeds", t) or re.search(r"withh", l, re.I),
     "withholding-tax payment is not a buyback (founder 2026-11-04 item 4)", ["PaymentsForRepurchaseOfCommonStock"]),
    ("dividends_paid", lambda t, l: re.search(r"MinorityInterest|Noncontrolling|Preferred", t) or re.search(r"noncontrolling|minority|preferred", l, re.I),
     "NCI or preferred dividends are not common dividends (shareholder-returns card)", ["PaymentsOfDividendsCommonStock"]),
    ("accounts_receivable", lambda t, l: re.search(r"InterestReceivable|NotesReceivable|NotesAndLoansReceivable|FinancingReceivable|LoansAndLeasesReceivable|LeaseReceivable", t),
     # tags only: a wider single receivables line (e.g. 'Accounts and notes receivable' on ReceivablesNetCurrent) stays AR
     # under Dhairya's 2026-11-12 wider-receivables ruling
     "interest, notes or financing receivables are not accounts receivable (sector-faces card)", ["AccountsReceivableNetCurrent"]),
    ("interest_expense", lambda t, l: re.search(r"Net\b|Net$|IncomeExpense", t) or re.search(r",\s*net\b(?!\s+of)|net interest|interest.*\bnet\b(?!\s+of)", l, re.I),
     "net interest line: interest_expense is the gross charge only (Dhairya 2026-11-12)", "combined"),
    ("operating_expenses", lambda t, l: "CostsAndExpenses" in t,
     "CostsAndExpenses includes cost of revenue: combined, never opex (Dhairya 2026-11-12)", "combined"),
    ("depreciation_and_amortization", lambda t, l: re.search(r"Accretion|Impairment", t) or re.search(r"accretion|impairment|nuclear fuel", l, re.I),
     "D&A including accretion/impairment is combined (Dhairya 2026-11-12)", "combined"),
    ("cash_paid_for_interest", lambda t, l: t.endswith(":InterestPaid") or ":InterestPaid+" in t,
     "cash interest paid = InterestPaidNet, net of capitalized interest (DQC_0065)", ["InterestPaidNet"]),
]


SM_TAGS = ("us-gaap:SellingAndMarketingExpense", "us-gaap:MarketingExpense", "us-gaap:SellingExpense",
           "us-gaap:MarketingAndAdvertisingExpense", "us-gaap:AdvertisingExpense")


def sga_rule(r, base, end_d, cf, accn):
    """Dhairya 2026-11-13 (MSFT incident): SG&A is never G&A alone when the face prints an S&M or marketing line;
    then it is the component sum G&A + S&M (every such line on the same face page)."""
    if r["data_point"] != "sga_expense" or r["status"] != "mapped" or r["tags"] != "us-gaap:GeneralAndAdministrativeExpense":
        return None
    pg = r["r_page"].split("+")[0]
    p = D.parse_r(D.get(base + pg, cache))
    sm = [x for x in p["rows"] if x["tag"] and x["tag"] != r["tags"] and any(v is not None for v in x["vals"])
          and (x["tag"] in SM_TAGS or (re.search(r"marketing|selling", x["label"], re.I)
                                       and not re.search(r"general|cost of|total|ancillary|operating|home", x["label"], re.I)))]
    if not sm:
        return None
    tags = [r["tags"]] + list(dict.fromkeys(x["tag"] for x in sm))
    v, why = page_value(base, pg, tags, end_d, "IS", "sga_expense")
    old = f"was mapped {r['tags']} '{r['label'][:40]}' on {pg}"
    if v is None:
        r["status"] = "combined"
        r["note"] = f"RULE: SG&A is never G&A alone when the face prints S&M ({', '.join(x['label'][:40] for x in sm)}); {why}; {old}"
        return "sga"
    api = [D.api_value(cf, t, accn, end_d, 12) for t in tags]
    r.update(status="component sum", tags="+".join(tags), label=" + ".join([r["label"][:50]] + [x["label"][:50] for x in sm]),
             fy0_printed=D.fmt(v), fy0_api=D.fmt(sum(api)) if None not in api else "", fy1_printed="", fy1_api="")
    r["match"] = ("Y" if close(v, sum(api)) else "N") if None not in api else ""
    r["note"] = (f"RULE: SG&A is never G&A alone when the face prints an S&M or marketing line (Dhairya 2026-11-13); "
                 f"component sum of {', '.join(tags)} on {pg}; {old}")
    return "sga"


# founder 2026-11-04 item 5 (Dhairya, binding): total_debt includes finance lease liabilities, current and noncurrent,
# never operating leases; not added again when the debt line carries leases (tag or label) or the debt note
# reconciles with leases inside; the note total is used only when no face line carries finance leases
FL_FACE = ("us-gaap:FinanceLeaseLiabilityCurrent", "us-gaap:FinanceLeaseLiabilityNoncurrent", "us-gaap:FinanceLeaseLiability")


def lease_rule(r, base, end_d, cf, accn):
    if r["data_point"] != "total_debt" or r["status"] not in ("mapped", "component sum") or not r["r_page"]:
        return None
    if re.search(r"Lease", r["tags"]) or re.search(r"lease", r["label"], re.I):
        r["note"] = "finance leases already inside the debt line(s) (tag or label): not added; " + r["note"]
        return None
    pg = r["r_page"].split("+")[0]
    p = D.parse_r(D.get(base + pg, cache))
    tags = [t for t in r["tags"].split("+") if t]
    face = [x for x in p["rows"] if x["tag"] and any(v is not None for v in x["vals"])
            and x["tag"] not in tags and not re.search(r"Asset|RightOfUse|Operating", x["tag"])
            and (x["tag"] in FL_FACE or (re.search(r"financ(e|ing) lease", x["label"], re.I)
                                         and re.search(r"liabilit|obligation", x["label"], re.I)
                                         and not re.search(r"operating|asset|right|property|excluding", x["label"], re.I)))]
    face = [x for x in face if x["tag"] != "us-gaap:FinanceLeaseLiability" or len(face) == 1]
    added, src = [], ""
    if face and r["stmt"] != "BS":
        # the keyed debt line is a note total and the same note prints finance leases: reconciled inside, not added
        r["note"] = (f"finance leases are printed in the same debt note as the keyed total ({pg}): the debt note reconciles "
                     "with leases inside, not added; " + r["note"])
        return None
    if face:
        added = list(dict.fromkeys(x["tag"] for x in face))
        v, why = page_value(base, "+".join([r["r_page"]]), tags + added, end_d, "BS", "total_debt")
        src = f"face finance-lease line(s) {', '.join(x['label'][:40] for x in face)} on {pg}"
    else:
        ml = metalinks(base)
        if ml is None:
            return None
        mtags, role2r = ml
        def pages_of(t):
            node = mtags.get(t.replace(":", "_"), {})
            return {role2r[x][0] for x in node.get("presentation", []) if x in role2r and role2r[x][1] != "statement"}
        fl = [t for t in ("us-gaap:FinanceLeaseLiability",) if pages_of(t)] or              [t for t in ("us-gaap:FinanceLeaseLiabilityCurrent", "us-gaap:FinanceLeaseLiabilityNoncurrent") if pages_of(t)]
        if not fl:
            return None
        debt_notes = set().union(*(pages_of(t) for t in tags)) if tags else set()
        if debt_notes & set().union(*(pages_of(t) for t in fl)):
            r["note"] = (f"finance leases are presented inside the debt note ({', '.join(sorted(debt_notes & set().union(*(pages_of(t) for t in fl))))}.htm): "
                         "the debt note reconciles with leases inside, not added; " + r["note"])
            return None
        parts = []
        for t in fl:
            hit = relocate(base, [t.split(":")[-1]], end_d, "total_debt")
            if not hit:
                return None
            parts.append(hit)
        base_v, _w = page_value(base, r["r_page"], tags, end_d, "BS", "total_debt")
        if base_v is None:
            return None
        v = base_v + sum(h[2] for h in parts)
        added = [f"us-gaap:{h[0]}" for h in parts]
        src = "note total " + ", ".join(f"{h[0]} on {h[1]}" for h in parts) + " (no face line carries finance leases)"
    if v is None:
        return None
    old = f"was {r['status']} {r['tags']} = {r['fy0_printed'] or r['fy0_api']}"
    api = [D.api_value(cf, t, accn, end_d, None) for t in tags + added]
    if not face:
        r["r_page"] = "+".join(dict.fromkeys(r["r_page"].split("+") + [h[1] for h in parts]))
    r.update(status="component sum", tags="+".join(tags + added), fy0_printed=D.fmt(v),
             fy0_api=D.fmt(sum(api)) if None not in api else "", fy1_printed="", fy1_api="")
    r["match"] = ("Y" if close(v, sum(api)) else "N") if None not in api else ""
    r["note"] = f"RULE: total_debt includes finance lease liabilities (founder 2026-11-04 item 5): added {src}; {old}"
    return "lease"


def capex_rule(r, base, end_d, cf, accn):
    """Dhairya 2026-11-13: capex includes turnaround spending only when the turnaround line is printed inside
    investing activities (a turnaround line in operating activities is never added)."""
    if r["data_point"] != "capex" or r["status"] != "mapped" or not r["r_page"] or "urnaround" in r["tags"]:
        return None
    pg = r["r_page"].split("+")[0]
    p = D.parse_r(D.get(base + pg, cache))
    rows = p["rows"]
    start = next((i for i, x in enumerate(rows) if re.search(r"investing activities", x["label"], re.I)), None)
    end = next((i for i, x in enumerate(rows) if start is not None and i > start and not x["tag"].endswith("Abstract")
                and x["tag"].startswith("us-gaap:NetCashProvidedByUsedInInvestingActivities")), None)
    if start is None or end is None:
        return None
    turn = [x for x in rows[start:end] if x["tag"] and x["tag"] != r["tags"] and re.search(r"turnaround", x["label"] + x["tag"], re.I)
            and any(v is not None for v in x["vals"])]
    if not turn:
        return None
    tags = [r["tags"]] + [x["tag"] for x in turn]
    v, why = page_value(base, pg, tags, end_d, "CF", "capex")
    if v is None:
        return None
    old = f"was mapped {r['tags']} = {r['fy0_printed']}"
    api = [D.api_value(cf, t, accn, end_d, 12) for t in tags]
    r.update(status="component sum", tags="+".join(tags), label=" + ".join([r["label"][:50]] + [x["label"][:50] for x in turn]),
             fy0_printed=D.fmt(v), fy0_api=D.fmt(sum(api)) if None not in api else "", fy1_printed="", fy1_api="")
    r["match"] = ("Y" if close(v, sum(api)) else "N") if None not in api else ""
    r["note"] = (f"RULE: capex includes turnarounds printed inside investing activities (Dhairya 2026-11-13): added "
                 f"{', '.join(x['label'][:50] for x in turn)} on {pg}; {old}")
    return "capex"


def apply_rules(r, base, end_d, cf=None, accn=""):
    """Returns a note when a rule changed the row (the row is then re-checked as class 'rule')."""
    if r["status"] not in ("mapped", "component sum"):
        return None
    if cf is not None and sga_rule(r, base, end_d, cf, accn):
        return "sga"
    if cf is not None and lease_rule(r, base, end_d, cf, accn):
        return "lease"
    if cf is not None and capex_rule(r, base, end_d, cf, accn):
        return "capex"
    for dp, pred, why, fix in RULES:
        if r["data_point"] != dp or not pred(r["tags"], r["label"]):
            continue
        old = f"was {r['status']} {r['tags']} '{r['label'][:50]}' on {r['r_page']}"
        if fix == "combined":
            r["status"] = "combined"
            r["note"] = f"RULE: {why}; {old}; " + r["note"]
            return why
        hit = relocate(base, fix, end_d, dp)
        if hit:
            t, pg, v, grp, name = hit
            r.update(status="mapped", tags=f"us-gaap:{t}", stmt="CF" if grp == "statement" else "NOTE", r_page=pg,
                     label=name[:120] if grp != "statement" else r["label"], fy0_printed=D.fmt(v), fy0_api="", fy1_printed="",
                     fy1_api="", match="")
            r["note"] = f"RULE: {why}; {old}; replaced by us-gaap:{t} read off {pg} ('{name[:60]}')"
        elif dp == "dividends_paid" and r["r_page"]:
            # the face may print common dividends on an extension tag next to the preferred/NCI line
            pg = r["r_page"].split("+")[0]
            p = D.parse_r(D.get(base + pg, cache))
            com = next((x for x in p["rows"] if x["tag"] and x["tag"] != r["tags"] and any(v is not None for v in x["vals"])
                        and re.search(r"dividend", x["label"], re.I) and re.search(r"common", x["label"], re.I)
                        and not re.search(r"preferred|noncontrolling|minority", x["label"], re.I)), None)
            v = page_value(base, pg, [com["tag"]], end_d, "CF", dp)[0] if com else None
            if com and v is not None:
                wider = bool(re.search(r"equity.award|award holders|participating|and other", com["label"], re.I))
                r.update(status="combined" if wider else "mapped", tags=com["tag"], label=com["label"][:120],
                         fy0_printed=D.fmt(v), fy0_api="", fy1_printed="", fy1_api="", match="")
                r["note"] = (f"RULE: {why}; {old}; common dividends are the face line '{com['label'][:70]}' ({com['tag']}) on {pg}"
                             + ("; it also pays equity-award holders: combined" if wider else ""))
            else:
                r.update(status="not_presented", tags="", stmt="", r_page="", label="", fy0_printed="", fy0_api="",
                         fy1_printed="", fy1_api="", match="")
                r["note"] = f"RULE: {why}; {old}; no common-dividend line on {pg} and none of {', '.join(fix)} in MetaLinks.json: not_presented"
        elif dp == "cash_paid_for_interest":
            r["status"] = "combined"
            r["note"] = f"RULE: {why}; InterestPaidNet not in the filing (MetaLinks.json): InterestPaid is gross of capitalized interest; {old}"
        else:
            r.update(status="not_presented", tags="", stmt="", r_page="", label="", fy0_printed="", fy0_api="",
                     fy1_printed="", fy1_api="", match="")
            r["note"] = f"RULE: {why}; {old}; none of {', '.join(fix)} in MetaLinks.json (whole filing): not_presented"
        return why
    return None


def metalinks_tags(base):
    """Elements presented on at least one rendered R page (a role with no R page carries no fact in this filing)."""
    ml = metalinks(base)
    if ml is None:
        return None
    tags, role2r = ml
    return {k for k, v in tags.items() if any(x in role2r for x in v.get("presentation", []))}


def check_company(rank):
    row = rows[rank - 1]
    tic, cik = row["ticker"], row["cik"]
    src = os.path.join(m1, f"{tic}-docmap-{D.DATE}.csv")
    md = os.path.join(m1, f"{tic}-docmap-{D.DATE}.md")
    if not os.path.exists(src):
        return {"rank": rank, "ticker": tic, "ok": False, "error": "no machine docmap"}
    recs = list(csv.DictReader(open(src)))
    mdt = open(md).read()
    m = re.search(r"- 10-K (\d{10}-\d{2}-\d{6}) \(CIK \d+, filed", mdt)
    accn = m[1] if m else ""
    ends = [r["note"].split("period ..")[-1][:10] for r in recs if "period .." in r["note"]]
    end = max(set(ends), key=lambda e: (ends.count(e) if e[:4] == max(ends)[:4] else -1, e)) if ends else ""
    st = {"rank": rank, "ticker": tic, "ok": bool(recs and accn and end), "rows": len(recs), "checked": 0,
          "by_class": {}, "mapped_sample": 0, "mapped_disagree": 0, "other_disagree": 0}
    if not st["ok"]:
        for r in recs:
            r["check"] = "check: machine-full-filing"
        write(tic, recs, mdt, [], st)
        return st
    end_d = dt.date.fromisoformat(end)
    cft = D.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json", cache)
    cf = json.loads(cft) if cft.startswith("{") else {}
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"
    mapped = [r for r in recs if r["status"] == "mapped" and r["stmt"] != "NOTE"]
    sample = set(id(r) for r in random.Random(tic).sample(mapped, math.ceil(len(mapped) * 0.1))) if mapped else set()
    log = []
    tpl = TEMPLATES.get(cik.zfill(10), "")
    end_c = end_d
    for r in recs:
        # each row is checked at its own period end (a row's note carries it; e.g. a transition-year filer)
        own = r["note"].split("period ..")[-1][:10] if "period .." in r["note"] else ""
        end_d = dt.date.fromisoformat(own) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", own) else end_c
        end = end_d.isoformat()
        r["check"] = "check: machine-full-filing"
        if tpl in OUT_GROUP and r["data_point"] in OUT_DPS and r["status"] == "not_presented":
            r["status"] = "OUT"
            r["note"] = f"OUT of the {tpl} template (Dhairya OUT ruling, main @020ebb29); " + r["note"]
            st["out_rekeyed"] = st.get("out_rekeyed", 0) + 1
        tag_before = r["tags"]
        ruled = apply_rules(r, base, end_d, cf, accn)
        if ruled and r["tags"] != tag_before and r["era_from_note"]:
            r["era_from_note"] = ("ERA GAP (FY2015-latest not covered): re-keyed by rule from " + (tag_before or "none")
                                  + " to " + (r["tags"] or "none") + "; era runs not re-derived for the new key")
        if ruled:
            st["rule_fixes"] = st.get("rule_fixes", 0) + 1
            st["by_class"]["rule"] = st["by_class"].get("rule", 0) + 1
        cls = ("NOTE" if r["stmt"] == "NOTE" else r["status"]) if (r["status"] in CHECK_STATUSES or r["stmt"] == "NOTE") \
            else ("mapped-sample" if id(r) in sample else None)
        if cls is None:
            continue
        st["checked"] += 1
        st["by_class"][cls] = st["by_class"].get(cls, 0) + 1
        if cls == "mapped-sample":
            st["mapped_sample"] += 1
        tags = [t for t in r["tags"].split("+") if t]
        if r["status"] == "not_presented":
            have = metalinks_tags(base)
            spec = next((d for d in D.DP if d[0] == r["data_point"]), None)
            full, comp = D.NOTE_FAMILY.get(r["data_point"], ((spec[2] if spec else []), []))
            if have is None:
                ok, why = None, "MetaLinks.json not available: absence not re-checked"
            else:
                present = [t for t in list(full) + list(comp) if f"us-gaap_{t}" in have]
                ok = not present
                why = ("none of the candidate elements in MetaLinks.json" if ok
                       else "element(s) present in the filing: " + ", ".join(present))
                if present and r["data_point"] != "shares_outstanding":
                    # ruling (2)/(3): found in the filing -> read it off its own R page instead of not_presented
                    hit = relocate(base, [t for t in full if t in present], end_d, r["data_point"])
                    if hit:
                        t, pg, v, grp, name = hit
                        r.update(status="mapped", tags=f"us-gaap:{t}", stmt="NOTE" if grp != "statement" else "FACE",
                                 r_page=pg, label=name[:120], fy0_printed=D.fmt(v), match="")
                        a = D.api_value(cf, f"us-gaap:{t}", accn, end_d, None if r["data_point"] in BS_DP else 12) if cf else None
                        r["fy0_api"] = D.fmt(a)
                        if a is not None:
                            r["match"] = "Y" if close(v, a) else "N"
                        r["note"] = (f"re-check: the machine pass said not_presented, but us-gaap:{t} is presented on {pg} "
                                     f"('{name[:60]}', MetaLinks.json); value read off that page")
                        ok, why = True, f"fixed: {t} read off {pg} ({D.fmt(v)})"
                        st["notpres_fixed"] = st.get("notpres_fixed", 0) + 1
                    elif not [t for t in full if t in present]:
                        ok, why = True, "only component element(s) present: " + ", ".join(present) + " (not the data point)"
                    else:
                        ok, why = True, (f"{', '.join(present)} presented but with no {end} value on any presenting page: "
                                         "nothing to read for this period")
        elif r["status"] == "component_in_note":
            p = D.parse_r(D.get(base + r["r_page"].split("+")[0], cache))
            ok = any(x["tag"] in tags for x in p["rows"])
            why = f"component element on {r['r_page']}" if ok else f"element not on {r['r_page']}"
        elif not r["r_page"] or not tags:
            ok, why = None, "no R page or tag to re-open"
        else:
            v, why = page_value(base, r["r_page"], tags, end_d, r["stmt"], r["data_point"],
                              sum_rows=r["status"] == "component sum" and len(tags) == 1)
            zr = why if v is not None else ""
            ref = r["fy0_printed"] or r["fy0_api"]
            if v is None and r["data_point"] == "shares_outstanding":
                p = D.parse_r(D.get(base + r["r_page"].split("+")[0], cache))
                vals = [x for row in p["rows"] if row["tag"] in tags and D.parse_date(row["label"]) == end_d
                        for x in row["vals"] if x is not None]
                if vals:
                    v = sum(vals) * p["shares_scale"]
                    why = f"equity statement row 'Ending balance ... at {end}' on {r['r_page']}: {D.fmt(v)}"
                    if not r["fy0_printed"]:
                        r["fy0_printed"] = D.fmt(v)
            if v is None and r["stmt"] == "NOTE":
                # the cited note page has no period-end value (e.g. a subsequent-events date): look on every page
                # that presents the element; none -> not_presented (shares: balance-sheet-date count only)
                hit = relocate(base, [t.split(":")[-1] for t in tags], end_d, r["data_point"])
                if hit:
                    t, pg, v, grp, name = hit
                    r.update(r_page=pg, label=name[:120], fy0_printed=D.fmt(v))
                    ok, why = True, f"moved: the cited page had no {end} value; {t} read off {pg} ({D.fmt(v)})"
                else:
                    oldp = r["r_page"]
                    r.update(status="not_presented", tags="", stmt="", r_page="", label="", fy0_printed="", fy0_api="",
                             fy1_printed="", fy1_api="", match="")
                    r["note"] = (f"re-check: {', '.join(tags)} is presented only on {oldp} and at no {end} value anywhere in the "
                                 f"filing (MetaLinks.json, every presenting R page read): not_presented")
                    ok, why = True, "fixed to not_presented: no period-end value on any presenting page"
                    st["notpres_fixed"] = st.get("notpres_fixed", 0) + 1
            elif v is None:
                ok = False
            elif not ref:
                ok, why = True, f"value {D.fmt(v)} read off its own R page (no companyfacts fact to compare)"
            elif "e" in ref.lower() and float(f"{v:.4g}") == float(ref):
                # the shared tool wrote a non-integer sum with %.4g (precision lost): restore the page value
                ok = True
                why = f"page value {round(v)} = printed {ref} at 4 significant digits; fy0_printed restored to the page value"
                if r["fy0_printed"] == ref:
                    r["fy0_printed"] = str(round(v))
                    st["format_fixes"] = st.get("format_fixes", 0) + 1
            else:
                ok = close(v, float(ref))
                why = f"page value {D.fmt(v)} vs {'printed' if r['fy0_printed'] else 'API'} {ref}" + (f"; {zr}" if zr else "")
            if v is not None and r["stmt"] == "NOTE" and not r["fy0_printed"]:
                r["fy0_printed"] = D.fmt(v)  # NOTE value read off its own R page
                if r["fy0_api"]:
                    r["match"] = "Y" if close(v, float(r["fy0_api"])) else "N"
        verdict = "agree" if ok else ("not re-checkable" if ok is None else "DISAGREE")
        if ok is False:
            st["mapped_disagree" if cls == "mapped-sample" else "other_disagree"] += 1
        r["check"] += f"; recheck (script, not hand) {r['r_page'] or 'MetaLinks.json'}: {verdict}: {why}"
        log.append((r["data_point"], cls, verdict, why))
    write(tic, recs, mdt, log, st)
    return st


def write(tic, recs, mdt, log, st):
    cols = list(D.COLS) + ["check"]
    with open(os.path.join(out_dir, f"{tic}-docmap-{D.DATE}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k, "") for k in cols})
    L = ["", "## Check pass",
         "Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens "
         "the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, "
         f"plus a seeded random 10% of mapped rows ({st['mapped_sample']}). This is a scripted re-check, not a human hand check.",
         "", "| data point | class | verdict | detail |", "|---|---|---|---|"]
    L += [f"| {a} | {b} | {c} | {d.replace('|', '/')} |" for a, b, c, d in log]
    open(os.path.join(out_dir, f"{tic}-docmap-{D.DATE}.md"), "w").write(mdt.rstrip("\n") + "\n" + "\n".join(L) + "\n")


for rank in range(int(lo), int(hi) + 1):
    try:
        st = check_company(rank)
    except Exception as exc:  # noqa: BLE001
        st = {"rank": rank, "ticker": rows[rank - 1]["ticker"], "ok": False, "error": repr(exc)[:200]}
    with open(os.path.join(out_dir, f"_check-{lo}-{hi}.jsonl"), "a") as fh:
        fh.write(json.dumps(st) + "\n")
    print(json.dumps(st), flush=True)
