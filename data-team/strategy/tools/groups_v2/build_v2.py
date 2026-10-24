"""Build group_assignment_v2.csv + review queue + move log for the cohort (group.assign@2). Deterministic; re-runnable.
Inputs (all local files, outside the repo cache for SEC responses): shards.csv (cohort file v1, 1014 rows, 986 not excluded), draft file,
FSDS-derived flags (R4 cls.json.gz), S2 audit manifest, R-file reads (read_batch.py), hand reads (hand.py)."""
import csv, gzip, json, os, sys, glob, collections, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import groups_v2 as g, strict, strict_decide as sd, hand

REPO = "/Users/vikash/wt-sector-groups/"
DATA = REPO + "data-team/strategy/data/"
SC = os.environ.get("SA_SCRATCH", "/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/w")
shards = list(csv.DictReader(open(REPO + "doc/data-moat/team/top1000/shards.csv")))
draft = {r["company_id"]: r for r in csv.DictReader(open(DATA + "group_assignment_draft.csv"))}
cls = json.load(gzip.open(DATA + "r4_sector/cls.json.gz"))
s2 = json.load(open(DATA + "s2_group_audit/meta.json"))
s2_by_cik = {v.get("cname"): v for v in s2.values()}
s2_sample = {r["cik"]: r for r in csv.DictReader(open(DATA + "s2_group_audit/sample.csv"))}
EXTRA_PARENTS = {"SO": (1081, "0000092122"), "SRE": (2503, "0001032208"), "AEE": (2144, "0001002910"), "ETR": (694, "0000065984"), "CTVA": (5394, "0001755672"),
                 "EIX": (1576, "0000827052"), "CMS": (1525, "0000811156"), "ES": (1008, "0000072741"), "TXNM": (3562, "0001108426")}
EXTRA_SUBS = {"GEORGIA-POWER": (613, "0000041091"), "SOCALGAS": (1080, "0000092108"), "SCE": (1079, "0000092103"), "CONSUMERS-ENERGY": (1165, "0000201533"),
              "AMEREN-ILLINOIS": (257, "0000018654"), "EIDP": (351, "0000030554"), "NSTAR-ELECTRIC": (211, "0000013372"), "PSNM": (1044, "0000081023")}
NATURAL = {"corporate": "corporate", "reit": "reit_equity", "utility": "utility", "bank": "bank", "energy": "energy", "insurer": "insurer",
           "bdc_fund_or_unclassified": "bdc", "other_financial": None, "no_revenue_line": "corporate"}

FEATS_CSV = DATA + "face_features_v2.csv"
_feat_cache = None
def _from_features_csv(cik):
    """offline reproduction path: face_features_v2.csv carries the strict features per filer, so the decision re-runs without the SEC cache"""
    global _feat_cache
    if _feat_cache is None:
        _feat_cache = {}
        if os.path.exists(FEATS_CSV):
            for r in csv.DictReader(open(FEATS_CSV)):
                _feat_cache[r["cik"]] = r
    r = _feat_cache.get(cik)
    if not r: return None
    return {"cik": cik, "name": r["name"], "sic": r["sic_sec"], "acc": r["accession"], "form": r["form"], "filed": r["filed"], "period": r["period_end"],
            "bs": [r["bs_title"], r["bs_r"]] if r["bs_r"] else None, "is": [r["is_title"], r["is_r"]] if r["is_r"] else None, "rows": None, "feats": json.loads(r["features_json"])}

def read(cik):
    p = f"{SC}/reads/{cik}.json"
    if os.path.exists(p):
        r = json.load(open(p))
        if "rows" in r: return r
        return None
    return _from_features_csv(cik)

def fy_label(pe):
    return "FY" + pe[:4] if pe else ""

def overlays_from(sigs, f, group, sic):
    ov = []
    if group not in ("insurer", "managed_care") and "premiums" in f and "claims" in f and ("reserves" in f or "current_assets" not in f):
        ov.append("insurance_operations" if group != "corporate" else "managed_care_operations")
    if group in ("broker_dealer", "asset_manager", "crypto_digital", "insurer") and "deposits" in f and ("loans" in f) and ("provision" in f or "nii" in f):
        ov.append("deposit_taking_operations")
    if group not in ("bank", "lender_nonbank", "bdc", "insurer", "reit_mortgage", "reit_equity") and ("fin_recv" in f or "loans" in f) and ("provision" in f or "fin_is" in f) and "deposits" not in f:
        ov.append("lending_or_captive_finance_candidate")
    if group != "crypto_digital" and "digital" in f:
        ov.append("crypto_holdings_candidate")
    if group in ("corporate",) and "rev" not in f and "rd" in f:
        ov.append("pre_revenue_candidate")
    return ov

def main():
    rows = []
    for r in shards:
        rows.append(dict(src="cohort", **r))
    for tk, (cid, cik) in EXTRA_PARENTS.items():
        rows.append(dict(src="parent_pending_P1", shard="", rank="", company_id=str(cid), cik=cik, ticker=tk, name=tk, sic="", mcap_bn="", cells="", filled="", unexplained_blank="", excluded=""))
    for tk, (cid, cik) in EXTRA_SUBS.items():
        rows.append(dict(src="subsidiary_registrant_outside_cohort", shard="", rank="", company_id=str(cid), cik=cik, ticker=tk, name=tk, sic="", mcap_bn="", cells="", filled="", unexplained_blank="", excluded=""))
    rows.append(dict(src="acquired_outside_cohort", shard="", rank="", company_id="1895", cik="0000915912", ticker="AVB", name="AVALONBAY COMMUNITIES INC", sic="", mcap_bn="", cells="", filled="", unexplained_blank="", excluded=""))
    out = []
    for r in rows:
        tk, cik, sic0 = r["ticker"], r["cik"], r["sic"]
        rd = read(cik)
        fl = cls.get(str(int(cik)))
        fsds = g.decide(sic0, fl["ev"], fl["flags"]) if fl else {"group": None, "basis": "queue", "reason": "not_in_fsds_extract", "shape": "none", "sic_group": g.sic_group(sic0), "shape_evidence": []}
        sic = (rd.get("sic") if rd else None) or sic0
        sic_note = "" if (not rd or (rd.get("sic") or "") == sic0) else f"sic_mismatch cohort={sic0} sec={rd.get('sic')}"
        feats, sigs = ({}, {})
        sdc = (None, [], "none", "no_read")
        if rd:
            feats = rd["feats"] if rd.get("rows") is None else strict.features(rd["rows"]); sigs = strict.signatures(feats)
            sdc = sd.decide_strict(sic, feats, sigs)
        grp, variant, ovs, basis, why, note = None, "", [], "open", "", ""
        h = hand.HAND.get(tk)
        excl = hand.EXCLUDED.get(tk)
        if excl:
            shadow = h[0] if h else (sdc[0] or fsds["group"] or "")
            grp, basis, why, note = "excluded." + excl[0], "excluded_rule", excl[1], excl[2] if len(excl) > 2 else ""
            variant = ""; ovs = list(h[2]) if h else []
        elif h:
            grp, variant, ovs, note = h[0], h[1], list(h[2]), h[3]; basis = "hand_read"; why = "sic/face disagree or ambiguous; hand read"
        elif sdc[2] == "reader_code" and fsds["basis"] == "code" and fsds["group"] == sdc[0]:
            grp, basis, why = sdc[0], "code", "two readers agree + SIC: " + sdc[3]
        elif sdc[2] == "reader_code" and fsds["basis"] == "code" and fsds["group"] != sdc[0]:
            basis, why = "open", f"readers disagree: FSDS->{fsds['group']} R-file->{sdc[0]}"
        elif sdc[2] == "reader_code":
            grp, basis, why = sdc[0], "code_reader", "R-file reader + SIC (FSDS: " + (fsds["reason"]) + "): " + sdc[3]
        elif not rd and fsds["basis"] == "code":
            grp, basis, why = fsds["group"], "code_fsds_only", "FSDS flags + SIC (no R-file read): " + fsds["reason"]
        else:
            basis, why = "open", f"reader:{sdc[3]} | fsds:{fsds['reason']}"
        if basis in ("code", "code_reader", "code_fsds_only") and rd:
            ovs = [o for o in overlays_from(sigs, feats, grp, sic)]
        out.append(dict(r=r, rd=rd, fl=fl, fsds=fsds, sdc=sdc, feats=feats, sigs=sigs, group=grp, variant=variant, overlays=ovs, basis=basis,
                        why=why, note=note, sic=sic, sic_note=sic_note, shadow=(shadow if excl else "")))
    return out

if __name__ == "__main__":
    out = main()
    c = collections.Counter((o["basis"], o["group"]) for o in out if o["r"]["excluded"] == "")
    for k, v in sorted(c.items(), key=str): print(k, v)
