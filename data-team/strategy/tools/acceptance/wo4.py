"""WO-4.1 acceptance tests (group.assign@2) that can run offline on the files in data-team/strategy/data. Prints PASS/FAIL per test and the offenders.
Tests that need a Verifier or the database are NOT_RUN here (AT-4.1f corporate V-tier sample, AT-4.1i loader, AT-4.1j history breaks, AT-4.1k after the P1 reload)."""
import csv, gzip, json, os, sys, collections
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "groups_v2"))
from s2_expected import E
import enum_v2

A = list(csv.DictReader(open(D + "/group_assignment_v2.csv")))
MV = list(csv.DictReader(open(D + "/group_moves_v2.csv")))
Q = list(csv.DictReader(open(D + "/group_review_queue_v2.csv")))
SH = [r for r in csv.DictReader(open(os.path.join(D, "..", "..", "..", "doc/data-moat/team/top1000/shards.csv")))]
cls = json.load(gzip.open(D + "/r4_sector/cls.json.gz"))
res = []
def t(name, ok, detail=""):
    res.append((name, ok)); print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail else ""))

enum_groups = set(enum_v2.GROUPS) | {"excluded." + e for e in enum_v2.EXCLUDED}
inc = [a for a in A if a["cohort_status"] == "cohort_file_v1"]
ids986 = {r["company_id"] for r in SH if not r["excluded"]}
# 4.1a
miss = [a["ticker"] for a in inc if not (a["evidence_accession"] and a["evidence_fy"] and a["effective_from"] and a["history_status"] and a["rule_path"])]
badenum = [a["ticker"] for a in A if a["group"] not in enum_groups]
cnt = collections.Counter(a["company_id"] for a in inc)
t("AT-4.1a rows == cohort file v1 (986), one active row each", {a["company_id"] for a in inc} == ids986 and all(v == 1 for v in cnt.values()), f"rows={len(inc)} missing_ids={len(ids986 - set(cnt))}")
t("AT-4.1a no missing evidence/effective/rule fields", not miss, f"missing={miss[:10]} n={len(miss)}")
t("AT-4.1a groups inside the frozen enum", not badenum, f"non-enum={badenum[:10]} n={len(badenum)}")
# 4.1b: two signals
bad = []
for a in A:
    if a["group"].startswith("excluded") or a["group"] == "corporate": continue
    s = a["signals"]
    if "A_face_R=" not in s or "B_sic=" not in s: bad.append(a["ticker"]); continue
    if a["assignment_basis"] not in ("hand_read", "code", "code_reader", "code_fsds_only", "excluded_rule"): bad.append(a["ticker"])
t("AT-4.1b non-corporate rows carry face + SIC signals or a hand read; no data-value signal exists in the rule", not bad, f"offenders={bad[:10]}")
# 4.1c
by = {a["ticker"]: a for a in A}
diff = [(tk, e, by[tk]["group"]) for tk, e in E.items() if tk in by and by[tk]["group"].split(".")[0] != e]
t("AT-4.1c S2 named results reproduced (symmetric difference)", not diff, f"diff={diff}")
# 4.1d
mv_bad = [m["ticker"] for m in MV if not (m["evidence_accession"] and (m["evidence_bs_rfile"] or m["matched_face_lines"]))]
t("AT-4.1d every moved company has accession + locator evidence", not mv_bad, f"moved={len(MV)} without_evidence={mv_bad[:20]}")
# 4.1e census manifest
small = collections.defaultdict(list)
for a in inc: small[a["group"]].append(a)
cen_bad = []
for g, lst in small.items():
    if len(lst) <= 60:
        for a in lst:
            if not (a["evidence_accession"] and a["evidence_bs_rfile"] and a["evidence_is_rfile"] and a["matched_face_lines"]): cen_bad.append((g, a["ticker"]))
t("AT-4.1e manifest rows (accession, BS+IS R-files, matched lines) for every member of groups with N<=60", not cen_bad, f"offenders={cen_bad[:20]} n={len(cen_bad)}")
# 4.1g shape recall
DIS = list(csv.DictReader(open(D + "/fsds_vs_v2_disagreements.csv")))
dk = {d["ticker"]: d for d in DIS}
R4G = {k: v[0].split("|")[0].replace("excluded.", "") for k, v in enum_v2.R4_MAP.items()}
unres = []
for a in inc:
    f = cls.get(str(int(a["cik"])))
    if not f: continue
    exp = R4G.get(f["fam"], "?")
    g = a["group"].split(".")[0] if not a["group"].startswith("excluded.") else "excluded"
    if exp not in ("?", g):
        d = dk.get(a["ticker"])
        if not d or not d["resolution"] or not d["evidence_accession"]: unres.append((a["ticker"], f["fam"], a["group"]))
t("AT-4.1g every company whose FSDS family disagrees with the v2 group has a resolution row with an accession", not unres, f"disagreements={len(DIS)} unresolved={unres[:15]} n={len(unres)}")
# 4.1h hybrids
hyb = [a["ticker"] for a in inc if a["signals"].count("+") >= 1 and a["overlays"] == "" and a["assignment_basis"] not in ("hand_read", "excluded_rule") and a["group"] in ("corporate", "energy", "utility") and any(k in a["signals"] for k in ("bank", "insurer", "bdc", "reit_equity", "finance_arm"))]
t("AT-4.1h hybrids (>=2 signature families on the face) have an overlay or a single-business note", not hyb, f"offenders={hyb[:15]}")
# 4.1l
fams = set(cls[k]["fam"] for k in cls)
un = [f for f in fams if f not in enum_v2.R4_MAP]
t("AT-4.1l every R4 FSDS family maps to a group or an excluded reason", not un, f"unmapped={un}")
t("OPEN rows == 0 in cohort v1", not [a for a in inc if a["group"] == "OPEN"], "open=" + str([a["ticker"] for a in inc if a["group"] == "OPEN"]))
print(f"{sum(1 for _, ok in res if ok)}/{len(res)} passed; NOT_RUN: AT-4.1f, AT-4.1i, AT-4.1j, AT-4.1k")
