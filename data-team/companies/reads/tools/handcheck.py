"""Evidence for the by-hand checks of one batch: python3 -I handcheck.py <first_rank> <last_rank>.
For every flagged item (latest-10-K mismatch / API missing, an ERA GAP row, an era line the tool marked (auto))
print the face rows of the filing's statement page that look like the data point, and where the filing's
MetaLinks.json presents the data point's tag family. Read-only; cached SEC pages, sec.gov only."""
import csv, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import docmap as d
CACHE = os.environ.get("DOCMAP_CACHE", os.path.join(H, "cache"))
MISSING = []


def cached(url, cache):  # cache only: the main run is the one process that talks to sec.gov (0.4 req/s in total)
    p = os.path.join(cache, re.sub(r"\W", "_", url)[-150:])
    if os.path.exists(p):
        return open(p, encoding="utf8").read()
    MISSING.append(url)
    return ""


d.get = cached
BROAD = {"revenue": r"revenue|sales", "cost_of_revenue": r"cost of|costs of", "gross_profit": r"gross",
         "operating_expenses": r"total .*expenses|operating expenses", "sga_expense": r"selling|general|administrative",
         "research_and_development": r"research|development", "operating_income": r"operating (income|profit|earnings)|from operations",
         "interest_expense": r"interest", "income_before_tax": r"before (income )?tax", "income_tax_expense": r"tax",
         "net_income": r"net (income|earnings|loss)", "basic_eps": r"basic", "diluted_eps": r"dilut",
         "weighted_basic_shares": r"weighted|shares", "weighted_diluted_shares": r"weighted|shares|dilut",
         "cash_and_equivalents": r"cash", "accounts_receivable": r"receivable", "inventory": r"inventor",
         "current_assets": r"current assets", "ppe_net": r"property|equipment|plant", "goodwill": r"goodwill",
         "total_assets": r"total assets", "accounts_payable": r"payable", "current_liabilities": r"current liabilities",
         "total_liabilities": r"total liabilities", "stockholders_equity": r"equity", "cfo": r"operating activities",
         "cash_flow_investing": r"investing activities", "cash_flow_financing": r"financing activities",
         "capex": r"capital expenditure|property|equipment|additions", "depreciation_and_amortization": r"depreciation|amortization",
         "sbc": r"stock|share|compensation", "dividends_paid": r"dividend", "share_buybacks": r"repurchase|treasury|buyback",
         "cash_paid_for_interest": r"interest", "cash_paid_for_income_taxes": r"tax"}
SPEC = {x[0]: x for x in d.DP}
cohort = list(csv.DictReader(open(os.environ.get("COHORT_CSV", os.path.join(H, "cohort.csv")))))


def base(cik, a):
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{a.replace('-', '')}/"


def face(cik, a, dp, stmt=None):
    reps = d.find_reports(d.get(base(cik, a) + "FilingSummary.xml", CACHE))
    stmt = stmt or SPEC[dp][1]
    out = []
    for k in ([stmt] + (["BSP"] if stmt == "BS" else []) + (["CI"] if stmt == "IS" else [])):
        if k not in reps:
            out.append(f"    {k}: statement not identified in FilingSummary ({', '.join(f'{x}={y[1]}' for x, y in reps.items())})")
            continue
        p = d.parse_r(d.get(base(cik, a) + reps[k][1], CACHE))
        out.append(f"    {k} {reps[k][1]} '{reps[k][0][:70]}' scale {p['scale']} cols {[(m, str(e)) for m, e in p['cols'][:3]]}")
        for r in p["rows"]:
            if r["tag"] and re.search(BROAD.get(dp, dp), r["label"] + " " + r["tag"], re.I):
                out.append(f"      {r['label'][:75]!r} {r['tag'][:85]} {r['vals'][:2]}")
    return out


def metalinks(cik, a, dp):
    txt = d.get(base(cik, a) + "MetaLinks.json", CACHE)
    try:
        inst = next(iter(json.loads(txt)["instance"].values()))
    except Exception:
        return ["    MetaLinks.json not available (filing predates it or not cached)"]
    role2r = {v.get("role"): (k, v.get("groupType", ""), v.get("shortName", "")) for k, v in inst.get("report", {}).items()}
    full, comp = d.NOTE_FAMILY.get(dp, (SPEC[dp][2], []))
    out = []
    for t in list(dict.fromkeys(SPEC[dp][2] + list(full) + list(comp))):
        x = inst.get("tag", {}).get(f"us-gaap_{t}")
        if x:
            rs = [role2r[r] for r in x.get("presentation", []) if r in role2r][:4]
            out.append(f"    MetaLinks: us-gaap:{t} presented on " + "; ".join(f"{r[0]} ({r[1]}) '{r[2][:50]}'" for r in rs))
    return out or [f"    MetaLinks: none of the {dp} family tags in this filing"]


CF = {}


def cfacts(cik, a, dp):
    """companyfacts facts of the data point's tag family that came from this accession (any page of the filing)."""
    if cik not in CF:
        t = cached(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json", CACHE)
        CF[cik] = json.loads(t) if t.startswith("{") else {}
    full, comp = d.NOTE_FAMILY.get(dp, (SPEC[dp][2], []))
    out = []
    for t in list(dict.fromkeys(SPEC[dp][2] + list(full) + list(comp))):
        fs = [f for u in CF[cik].get("facts", {}).get("us-gaap", {}).get(t, {}).get("units", {}).values() for f in u if f.get("accn") == a]
        if fs:
            fy = sorted({(f.get("start", ""), f["end"], f["val"]) for f in fs}, key=lambda x: x[1], reverse=True)[:2]
            out.append(f"    companyfacts from {a}: us-gaap:{t} {fy}")
    return out or [f"    companyfacts: no {dp} family tag from {a}"]


VERDICTS = []


def verdict(rank, t, dp, issue, cik, a, latest_status, latest_tag=""):
    """the by-hand verdict for one era item, from the filing's face rows and the accession's companyfacts facts."""
    spec = SPEC[dp]
    reps = d.find_reports(cached(base(cik, a) + "FilingSummary.xml", CACHE))
    if spec[1] not in reps:
        return "unresolved", f"{spec[1]} statement page not identified in the FilingSummary of {a}"
    p = d.parse_r(cached(base(cik, a) + reps[spec[1]][1], CACHE))
    fn = reps[spec[1]][1]
    val = [r for r in p["rows"] if r["tag"] and any(v is not None for v in r["vals"])]
    if dp == "operating_expenses":  # ruling 2026-11-12: printed opex total excluding COGS, else every line between GP and OI
        gi = next((i for i, r in enumerate(val) if r["tag"] == "us-gaap:GrossProfit"), None)
        oi = next((i for i, r in enumerate(val) if r["tag"] == "us-gaap:OperatingIncomeLoss"), None)
        if gi is not None and oi is not None and oi > gi + 1:
            comps = [r for r in val[gi + 1:oi] if not re.match(r"\s*total", r["label"], re.I)]
            tot = next((r for r in val[gi + 1:oi] if re.match(r"\s*total", r["label"], re.I)), None)
            target = val[gi]["vals"][0] - val[oi]["vals"][0]
            sm = sum(r["vals"][0] or 0 for r in comps)
            if tot is not None and abs(tot["vals"][0] - target) < 0.5:
                return "printed (total)", f"{a} {fn} prints '{tot['label'][:60]}' on {tot['tag']} {tot['vals'][0]} = GP - OI {target:g}"
            if abs(sm - target) < 0.5:
                return "component sum", f"{a} {fn}: " + " + ".join(f"'{r['label'][:40]}' {r['tag']}" for r in comps) + f" = {sm:g} = GP - OI (ties)"
            return "unresolved", f"{a} {fn}: lines between GP and OI sum to {sm:g}, GP - OI = {target:g}"
        return "not_presented", f"{a} {fn}: no gross profit / operating income pair on the face (opex ruling: no opex served)" + (
            "; consistent with the latest 10-K" if latest_status == "not_presented" else f"; latest 10-K is {latest_status}: era break")
    if latest_tag:
        for r in val:
            if r["tag"] == latest_tag:
                return "printed (latest tag)", f"{a} {fn} prints '{r['label'][:70]}' on {r['tag']} {r['vals'][:1]} (the latest 10-K's tag)"
    hdr = [i for i, r in enumerate(p["rows"]) if r["tag"] and r["tag"].endswith("Abstract") and spec[3] != "^$" and re.search(spec[3], r["label"], re.I)]
    for i in hdr:
        comps = []
        for r in p["rows"][i + 1:]:
            if r["tag"].endswith("Abstract") or not any(v is not None for v in r["vals"]):
                break
            comps.append(r)
        if comps:
            return "component sum", f"{a} {fn}: under the header '{p['rows'][i]['label'][:40]}' the face prints " + " + ".join(
                f"'{r['label'][:30]}' {r['tag']} {r['vals'][0]}" for r in comps[:4]) + " (no printed total)"
    if spec[3] != "^$":
        for r in p["rows"]:
            if r["tag"] and re.search(spec[3], r["label"], re.I) and any(v is not None for v in r["vals"]):
                return "printed (other tag)", f"{a} {reps[spec[1]][1]} prints '{r['label'][:70]}' on {r['tag']} {r['vals'][:1]}: era tag differs from the family"
    fam = cfacts(cik, a, dp)
    if not fam[0].startswith("    companyfacts: no"):
        return "off the face (note)", f"{a} {reps[spec[1]][1]}: no face line; " + "; ".join(x.strip() for x in fam)[:220]
    return "not_presented", f"{a} {reps[spec[1]][1]} ({reps[spec[1]][0][:50]}): no face line; no {dp} family fact from this 10-K in companyfacts" + (
        "; consistent with the latest 10-K (not_presented)" if latest_status == "not_presented" else f"; latest 10-K is {latest_status}: era break")


def main():
    first, last = int(sys.argv[1]), int(sys.argv[2])
    for rank in range(first, last + 1):
        row = cohort[rank - 1]
        t, cik = row["ticker"], row["cik"]
        md = os.path.join(H, "out", f"{t}-docmap-2026-11-12.md")
        if not os.path.exists(md):
            print(f"## {rank} {t}: no docmap yet"); continue
        mdt = open(md).read()
        rows = list(csv.DictReader(open(os.path.join(H, "out", f"{t}-docmap-2026-11-12.csv"))))
        latest = (re.search(r"- 10-K (\S+) \(CIK \d+, filed", mdt) or [None, ""])[1]
        fy15 = (re.search(r"FY2015 10-K (\d{10}-\d{2}-\d{6})", mdt) or [None, ""])[1]
        print(f"## {rank} {t} CIK {cik} latest {latest} FY2015 {fy15 or 'none'}")
        if "FY2015 10-K: none" in mdt:
            print("  ! no FY2015 10-K in companyfacts")
        for r in rows:
            m, dp = r["match"], r["data_point"]
            if m.startswith("N") or m == "API missing":
                custom = r["tags"] and not r["tags"].startswith("us-gaap:")
                VERDICTS.append((rank, t, dp, f"latest 10-K {m}", "printed value stands" if custom else "decided by the filing (printed)",
                                 f"{latest} {r['r_page']} '{r['label'][:60]}' {r['tags'][:70]} printed {r['fy0_printed']}" + (
                                     ": extension tag, companyfacts holds only standard taxonomies" if custom else f" vs API {r['fy0_api']}")))
                print(f"- [{dp}] latest {r['status']} {r['tags'][:70]} printed {r['fy0_printed']}/{r['fy1_printed']} api {r['fy0_api']}/{r['fy1_api']} match {m} {r['r_page']}")
                print("\n".join(face(cik, latest, dp, r["stmt"] if r["stmt"] in ("IS", "BS", "CF") else None)))
            if r["stmt"] == "NOTE" and r["status"] == "mapped":
                title = r["label"]
                if re.search(r"parent company|registrant|condensed financial information|schedule i\b", title, re.I):
                    VERDICTS.append((rank, t, dp, f"note-sourced from {r['r_page']}", "wrong source: parent-company only",
                                     f"{latest} {r['r_page']} '{title[:80]}' is the parent-only schedule, not the consolidated figure: the consolidated face has no such line (not_presented)"))
                elif re.search(r"subsidiar", title, re.I):
                    VERDICTS.append((rank, t, dp, f"note-sourced from {r['r_page']}", "wrong source: subsidiary only",
                                     f"{latest} {r['r_page']} '{title[:80]}' reports one subsidiary, not the consolidated figure: not_presented on the consolidated face"))
                elif not r["fy0_api"]:
                    VERDICTS.append((rank, t, dp, f"note-sourced from {r['r_page']}", "unresolved: no undimensioned value",
                                     f"{latest} {r['r_page']} '{title[:80]}' {r['tags'][:60]}: companyfacts has no undimensioned fact for the period (a dimensioned table, e.g. by segment): no consolidated value proven"))
                else:
                    VERDICTS.append((rank, t, dp, f"note-sourced from {r['r_page']}", "PASS: consolidated note value",
                                     f"{latest} {r['r_page']} '{title[:80]}' {r['tags'][:60]} = {r['fy0_api']} (undimensioned, same accession)"))
            if r["era_from_note"].startswith("ERA GAP"):
                print(f"- [{dp}] {r['era_from_note'][:200]}")
                if fy15:
                    VERDICTS.append((rank, t, dp, "era gap: " + r["era_from_note"].split(": ", 1)[-1][:90], *verdict(rank, t, dp, "gap", cik, fy15, r["status"], r["tags"] if "+" not in r["tags"] else "")))
                else:
                    VERDICTS.append((rank, t, dp, "era gap", "no FY2015 10-K", "company has no FY2015 10-K in companyfacts"))
                if fy15:
                    print("\n".join(face(cik, fy15, dp) + metalinks(cik, fy15, dp) + cfacts(cik, fy15, dp)))
        for ln in mdt.split("\n"):
            m = re.match(r"- (\w+): (FY2015|era) 10-K (\S+) .*\((auto)\)", ln)
            if m:
                dp, _k, a, _ = m.groups()
                st = next((r["status"] for r in rows if r["data_point"] == dp), "")
                lt = next((r["tags"] for r in rows if r["data_point"] == dp and "+" not in r["tags"]), "")
                if not any(v[1] == t and v[2] == dp and a in v[5] for v in VERDICTS):
                    VERDICTS.append((rank, t, dp, f"{_k} 10-K {a}: no row matched (tool)", *verdict(rank, t, dp, "auto", cik, a, st, lt)))
                print(f"- [{dp}] {ln[2:200]}")
                print("\n".join(face(cik, a, dp) + metalinks(cik, a, dp) + cfacts(cik, a, dp)))


main()
OV = {}
if os.path.exists(os.environ.get("HANDCHECK_OVERRIDES", os.path.join(H, "overrides.tsv"))):  # verdicts written by hand after opening the page
    for ln in open(os.environ.get("HANDCHECK_OVERRIDES", os.path.join(H, "overrides.tsv"))):
        if ln.strip() and not ln.startswith("#"):
            tk, dpk, key, vv, ev = ln.rstrip("\n").split("\t")
            OV[(tk, dpk, key)] = (vv, ev)
VERDICTS = [v[:4] + OV.get((v[1], v[2], v[3][:20]), (v[4], v[5])) + (("BY HAND" if (v[1], v[2], v[3][:20]) in OV else "RULE"),) for v in VERDICTS]
with open(os.path.join(H, f"verdicts-{sys.argv[1]}-{sys.argv[2]}.tsv"), "w") as fh:
    for v in VERDICTS:
        fh.write("\t".join(map(str, v)) + "\n")
if MISSING:
    print(f"\n(not in cache, not fetched: {len(MISSING)} pages)")
    open(os.path.join(H, "missing.txt"), "a").write("\n".join(MISSING) + "\n")
