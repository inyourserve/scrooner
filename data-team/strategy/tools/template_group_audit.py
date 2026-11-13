"""Template-group audit of the top-1,000 cohort: every company's group (tv1.1 seed plan over cohort v1.1) against
how its filing presents its statements (the document-first docmaps on main and the work/reads/* branches)."""
import collections, csv, io, json, re, subprocess, sys
S, REPO, OUT = sys.argv[1], "/home/user/scrooner", sys.argv[2]
plan = json.load(open(f"{S}/tg/plan.json"))
cohort = list(csv.DictReader(open(f"{REPO}/data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv")))
sic = {r["company_id"]: r["sic"] for r in csv.DictReader(open(f"{S}/cohort_sic.csv"))}
branches = ["origin/main"] + [f"origin/work/reads/{a}-{a + 99}" for a in range(201, 1000, 100)]
def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout
dm = {}  # ticker -> (date, branch, path)
for b in branches:
    for p in git("ls-tree", "-r", "--name-only", b, "data-team/companies/reads/").split():
        m = re.search(r"/([A-Z0-9.\-]+)-docmap-(\d{4}-\d{2}-\d{2})\.csv$", p)
        if m and (m[1] not in dm or m[2] >= dm[m[1]][0]):
            dm[m[1]] = (m[2], b, p)
key = collections.defaultdict(list)
for r in csv.DictReader(open(f"{S}/bg.csv")):
    # a reader keyed it OUT, or the grade says the reader's not_presented should have been OUT
    if r["key_status"] == "OUT" or (r["result"] == "key_error" and r["pred_status"] == "OUT"):
        key[r["ticker"]].append(r["data_point"])
FIN = {"bank", "insurer", "lender", "broker_am", "bdc", "reit_mortgage"}
FACE_NONFIN = ["cost_of_revenue", "gross_profit", "inventory", "current_assets", "current_liabilities"]
PRINTED = {"mapped", "component sum", "combined"}
rows, conflicts = [], collections.Counter()
for rank, c in enumerate(cohort, 1):
    cid, tic = c["company_id"], c["ticker"]
    p = plan.get(cid) or plan.get(int(cid) if cid.isdigit() else cid) or {}
    tpl = p.get("template", "")
    s = sic.get(cid, "")
    flags, ev = [], []
    if not tpl:
        flags.append("no_group")
    elif not s and tpl == "general":
        flags.append("no_sic_defaulted_general")
    recs = {}
    if tic in dm:
        d, b, path = dm[tic]
        for r in csv.DictReader(io.StringIO(git("show", f"{b}:{path}"))):
            recs[r["data_point"]] = r
    face = lambda dp: dp in recs and recs[dp]["status"] in PRINTED and recs[dp].get("stmt", "") not in ("NOTE", "")
    absent = lambda dp: dp in recs and recs[dp]["status"] in ("not_presented", "OUT")
    if recs and tpl in FIN:
        hit = [dp for dp in FACE_NONFIN if face(dp)]
        if hit:
            flags.append("financial_template_prints_operating_lines")
            ev.append("; ".join(f"{dp} {recs[dp]['status']} {recs[dp]['tags'][:50]} {recs[dp]['r_page']}" for dp in hit))
    if recs and tpl in ("general", "utility"):
        if all(absent(dp) for dp in ("current_assets", "current_liabilities", "cost_of_revenue", "gross_profit")):
            flags.append("general_template_unclassified_bs_no_cogs")
            ev.append("current_assets, current_liabilities, cost_of_revenue, gross_profit all not printed")
    if tpl == "general" and s and 6000 <= int(s) <= 6799:
        flags.append("general_template_financial_sic")
        ev.append(f"SIC {s}")
    for k in key.get(tic, []):
        if k in p.get("in", []):
            flags.append("seed_in_but_answer_key_out")
            ev.append(f"{k}: OUT in the blind-grade answer key, IN in the {tpl} seed")
    for f in flags:
        conflicts[f] += 1
    rows.append({"rank": rank, "company_id": cid, "cik": c["cik"], "ticker": tic, "sic": s, "template": tpl,
                 "docmap": f"{dm[tic][1].replace('origin/', '')}:{dm[tic][2].split('/')[-1]}" if tic in dm else "",
                 "flags": "|".join(flags), "evidence": " || ".join(ev)})
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(rows[0]))
    w.writeheader(); w.writerows(rows)
print(json.dumps({"companies": len(rows), "with_docmap": sum(1 for r in rows if r["docmap"]),
                  "templates": collections.Counter(r["template"] for r in rows), "flags": conflicts,
                  "flagged_companies": sum(1 for r in rows if r["flags"])}, default=dict, indent=1))
