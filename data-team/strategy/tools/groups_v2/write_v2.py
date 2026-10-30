"""Write the v2 group assignment outputs from build_v2.main()."""
import csv, json, os, sys, collections, datetime, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_v2 as b, strict, groups_v2 as g, hand

OUTDIR = b.DATA
INSURER_VARIANT = {}
for v, lst in (("pc", "AIG WRB MCY RLI ALL THG ACGL EG MKL AXS CB TRV CINF CNA L HIG PGR RNR AFG KNSL ORI"),
               ("life", "MET PFG JXN CRBG EQH AFL UNM LNC GL RGA PRU VOYA PRI AIZ"), ("mortgage", "MTG ESNT ACT"), ("title", "FNF FAF")):
    for t in lst.split(): INSURER_VARIANT[t] = v
ENERGY_VARIANT = {"1311": "exploration_production", "2911": "refiner", "1381": "drilling_services", "1382": "exploration_services", "1389": "oilfield_services", "1321": "ngl", "2990": "refined_products"}
INS_VARIANT_SIC = {"6331": "pc", "6311": "life", "6321": "health_accident", "6351": "surety_mortgage", "6361": "title", "6399": "other"}
GROUP_KEYS = {
 "bank": ["deposits", "loans", "nii", "nonint_exp", "provision"], "lender_nonbank": ["loans", "fin_recv", "provision", "nii"],
 "insurer": ["premiums", "claims", "reserves"], "managed_care": ["premiums", "claims", "reserves", "current_assets"],
 "insurance_broker": ["brokerage_is", "current_assets"], "reit_equity": ["realestate", "rental", "current_assets"],
 "reit_mortgage": ["nii", "repo_mbs", "loans"], "bdc": ["inv_income", "net_assets", "inv_fv"], "utility": ["reg_assets", "reg_liab", "fuel_is", "util_plant", "current_assets"],
 "energy": ["oilgas", "cogs", "current_assets"], "midstream": ["partners", "cogs", "current_assets"], "broker_dealer": ["brokerage_bs", "brokerage_is", "deposits"],
 "asset_manager": ["am_fees", "inv_fv"], "crypto_digital": ["digital", "cogs", "current_assets"], "exchange": ["brokerage_is", "current_assets"],
 "corporate": ["rev", "cogs", "rd", "current_assets"]}

IDENT_FLAGS = {
 "VMRK": "identity: CIK 0000906107 is Equity Residential renamed Vivmark Residential 2026-08-17 (ticker VMRK from 2026-08-18); reverse acquisition with AvalonBay as accounting acquirer (8-K 0001140361-26-033377, 424B3 0001140361-26-028312). Group read from the PRE-merger FY2025 10-K; history across 2026-08-17 is cross-entity (GATE-A section 1c); not renamed",
 "PSKY": "identity: renamed Skydance Corp 2026-10-06, ticker SKYD (8-K 0001104659-26-113913); group unchanged; our core.company still says Paramount Skydance / PSKY",
 "XOM": "identity: successor holding company; predecessor CIK 0000034088 not in core.company; latest filing read is the 10-Q filed under the predecessor accession prefix",
 "WBD": "identity: acquired 2026-10-06; 15-12G 0001193125-26-423513 (GATE-A section 2)",
 "AVB": "identity: merged into CIK 0000906107; 25-NSE 0000876661-26-000689, 15-12G 0001104659-26-102433 (GATE-A section 1a)",
 "EAI": "identity: Entergy Arkansas holds Entergy Corp combined-filing facts under shared-accession bug (GATE-A section 3b-3c)",
}

def locator(rd, fl):
    if rd and rd.get("acc"):
        return rd["acc"], rd.get("form", ""), rd.get("filed", ""), rd.get("period", ""), (rd["bs"][1] if rd.get("bs") else ""), (rd["is"][1] if rd.get("is") else ""), "R-file reader (Reader 1 regex on FilingSummary + R-files)"
    if fl:
        p = fl.get("period", "")
        return fl.get("adsh", ""), "10-K", "", f"{p[:4]}-{p[4:6]}-{p[6:]}" if p else "", "", "", "FSDS pre.txt flags (no R-file read)"
    return "", "", "", "", "", "", "none"

def matched(o):
    f = o["feats"]
    gk = (o["group"] or "corporate")
    if gk.startswith("excluded."): gk = o.get("shadow") or "corporate"
    keys = GROUP_KEYS.get(gk, [])
    ks = [k for k in keys if k in f]
    ks += [k for k in f if k not in ks and k in ("premiums", "deposits", "digital", "fin_recv", "reg_assets", "realestate", "inv_income", "partners", "am_fees", "brokerage_bs")][:3]
    s = "; ".join(f"{k}={f[k][:34]}" for k in ks[:7])
    if not s and o["rd"] and o["rd"].get("rows"):
        first = [f"IS:{l[:28]}={v[:12]}" for t, l, v in o["rd"]["rows"].get("IS", []) if v][:4]
        s = "; ".join(first)
    return s

def variant_of(o):
    grp = o["group"]; tk = o["r"]["ticker"]; sic = o["sic"]; f = o["feats"]
    if o["variant"]: return o["variant"]
    if grp == "insurer": return INSURER_VARIANT.get(tk) or INS_VARIANT_SIC.get(sic, "")
    if grp == "energy": return ENERGY_VARIANT.get(sic, "")
    if grp == "bank": return "deposit_taker"
    if grp == "reit_equity": return "operating_reit" if "current_assets" in f else "property_reit"
    if grp == "utility":
        return "regulated" if "reg_assets" in f else "unregulated_or_diversified"
    return ""

def main():
    out = b.main()
    gen = datetime.date(2026, 10, 22).isoformat()
    A, MV, Q = [], [], []
    for o in out:
        r = o["r"]; rd = o["rd"]; fl = o["fl"]
        tk = r["ticker"]; excl = o["group"] and o["group"].startswith("excluded.")
        grp = o["group"] or "OPEN"
        acc, form, filed, pe, bsr, isr, how = locator(rd, fl)
        sdc = o["sdc"]; fsds = o["fsds"]
        ovs = ";".join(o["overlays"])
        d = b.draft.get(r["company_id"]) if r["src"] == "cohort" else None
        draft_grp = d["group"] if d else ""
        nat = b.NATURAL.get(draft_grp, "?") if d else ""
        in986 = (r["src"] == "cohort" and r["excluded"] == "")
        moved = ""
        if in986 and not excl:
            moved = "Y" if (nat is None or nat != grp) else "N"
        elif in986 and excl:
            moved = "Y"
        cohort_status = {"cohort": "cohort_file_v1" if r.get("excluded", "") == "" else "cohort_file_row_excluded: " + r["excluded"][:80],
                         "parent_pending_P1": "addition_parent_pending_P1_reload", "subsidiary_registrant_outside_cohort": "outside_cohort_subsidiary_registrant",
                         "acquired_outside_cohort": "outside_cohort_acquired"}[r["src"]]
        if r["src"] == "cohort" and r.get("excluded", "").startswith("added by S000"): cohort_status = "addition_candidate_S101_backfill"
        if tk == "SPCX": cohort_status = "addition_candidate_keep_mcap_understated"
        sics = f"cohort={r['sic']}" + (f" sec={rd.get('sic')}" if rd and rd.get('sic') != r['sic'] else "")
        sig_a = "+".join(o["sigs"].keys()) if o["sigs"] else ("none" if rd else "n/a")
        signals = f"A_face_R={sig_a}; A_face_FSDS={fsds.get('shape')}; B_sic={o['sic']}->{fsds.get('sic_group')}"
        name = (rd.get("name") if rd else None) or r["name"]
        s2c = b.s2_sample.get(r["cik"])
        S2m = None
        for v in b.s2.values():
            if v.get("acc") and rd and v.get("acc") == rd.get("acc"): S2m = v
        s2_open = "Y" if s2c else "N"
        row = dict(company_id=r["company_id"], cik=r["cik"], ticker=tk, company_name=name, cohort_status=cohort_status,
                   group=grp, variant=variant_of(o) if not excl else "", overlays=ovs, shadow_group_if_excluded=o["shadow"],
                   in_fsds_extract=("Y" if fl else "N"), draft_group_v1=draft_grp, moved_from_draft=moved, assignment_basis=o["basis"], rule_path="group.assign@2/1.3: " + o["why"][:160],
                   sic_cohort_sec=sics, signals=signals, review_flags="; ".join(x for x in (o["sic_note"], IDENT_FLAGS.get(tk, "")) if x),
                   evidence_accession=acc, evidence_form=form, evidence_filed=filed, evidence_period_end=pe,
                   evidence_fy=("FY" + pe[:4]) if pe else "", evidence_bs_rfile=bsr, evidence_is_rfile=isr, evidence_source=how,
                   matched_face_lines=matched(o), hand_note=o["note"][:300], s2_opened=s2_open,
                   effective_from=pe, history_status=(f"unverified_before_{pe}" if pe else "unverified"), generated=gen)
        A.append(row)
        if moved == "Y" and in986:
            MV.append({k: row[k] for k in ("company_id", "cik", "ticker", "company_name", "draft_group_v1", "group", "variant", "overlays", "assignment_basis",
                                           "evidence_accession", "evidence_form", "evidence_filed", "evidence_period_end", "evidence_bs_rfile", "evidence_is_rfile", "matched_face_lines", "signals", "hand_note", "s2_opened")})
        # review queue = everything that went to a human read (FSDS queue, reader hand, conflict) or was resolved by exclusion
        went = (fsds["basis"] == "queue") or (sdc[2] == "hand") or o["basis"] in ("open", "hand_read", "excluded_rule") or bool(o["overlays"])
        if went and r["src"] == "cohort" or (r["src"] != "cohort"):
            reasons = []
            if fsds["basis"] == "queue": reasons.append("fsds:" + fsds["reason"])
            if sdc[2] == "hand": reasons.append("reader:" + sdc[3])
            if o["overlays"]: reasons.append("overlay_candidate:" + ";".join(o["overlays"]))
            if o["sic_note"]: reasons.append(o["sic_note"])
            Q.append(dict(company_id=r["company_id"], ticker=tk, company_name=name, sic=o["sic"], queue_reasons=" | ".join(reasons) or "extra row", resolved_by=o["basis"],
                          resolved_group=grp, resolved_overlays=ovs, note=o["note"][:300] or o["why"][:200], evidence_accession=acc, evidence_bs_rfile=bsr, evidence_is_rfile=isr))
    return A, MV, Q

def disagreements(A, out):
    import gzip
    import enum_v2
    cls = json.load(gzip.open(b.DATA + "r4_sector/cls.json.gz"))
    rows = []
    byk = {o["r"]["company_id"]: o for o in out}
    for a in A:
        if a["cohort_status"] != "cohort_file_v1": continue
        f = cls.get(str(int(a["cik"])))
        if not f: continue
        opts = enum_v2.R4_MAP.get(f["fam"], ("?", ""))[0].split("|")
        exp = opts[0].replace("excluded.", "")
        g = a["group"].split(".")[0] if not a["group"].startswith("excluded.") else "excluded"
        if exp == g: continue
        o = byk[a["company_id"]]
        if a["group"].startswith("excluded."): res = "excluded rule: " + (o["why"] or "")[:160]
        elif a["hand_note"]: res = "hand read: " + a["hand_note"][:200]
        elif a["sic_cohort_sec"].split()[0].split("=")[1] in ("4953", "4955"): res = "R4 rule wrong: waste (SIC 4953/4955) has corporate-shaped statements (cost of operations, SG&A); S2 FILING-CHECKED WM RSG CLH CWST WCN"
        elif g in opts: res = f"R4 family {f['fam']} merges {'|'.join(opts)}; v2 group {g} by {a['assignment_basis']} ({o['why'][:100]})"
        else: res = "R4 rule vs v2: " + o["why"][:160]
        rows.append(dict(ticker=a["ticker"], company_id=a["company_id"], r4_family=f["fam"], r4_expected=exp, v2_group=a["group"], resolution=res,
                         evidence_accession=a["evidence_accession"], evidence_bs_rfile=a["evidence_bs_rfile"], evidence_is_rfile=a["evidence_is_rfile"], matched_face_lines=a["matched_face_lines"]))
    return rows

def write(A, MV, Q):
    cols = list(A[0].keys())
    with open(OUTDIR + "group_assignment_v2.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(A)
    with open(OUTDIR + "group_moves_v2.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(MV[0].keys())); w.writeheader(); w.writerows(MV)
    with open(OUTDIR + "group_review_queue_v2.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(Q[0].keys())); w.writeheader(); w.writerows(Q)

def export_features():
    """face_features_v2.csv: the strict features per filer read (labels truncated), enough to re-run the classifier offline."""
    import glob
    rows = []
    for p in sorted(glob.glob(b.SC + "/reads/*.json")):
        r = json.load(open(p))
        if "rows" not in r: continue
        f = strict.features(r["rows"])
        rows.append(dict(cik=r["cik"], ticker=(r.get("tickers") or [""])[0], name=r.get("name", ""), sic_sec=r.get("sic") or "", accession=r["acc"], form=r["form"], filed=r["filed"], period_end=r["period"],
                         bs_title=(r["bs"] or ["", ""])[0], bs_r=(r["bs"] or ["", ""])[1], is_title=(r["is"] or ["", ""])[0], is_r=(r["is"] or ["", ""])[1],
                         n_bs_rows=len(r["rows"].get("BS", [])), n_is_rows=len(r["rows"].get("IS", [])), features_json=json.dumps(f, sort_keys=True)))
    with open(OUTDIR + "face_features_v2.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    A, MV, Q = main()
    write(A, MV, Q)
    D = disagreements(A, b.main())
    with open(OUTDIR + "fsds_vs_v2_disagreements.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(D[0].keys())); w.writeheader(); w.writerows(D)
    print("disagreements with the FSDS-based family:", len(D))
    miss = [{k: a[k] for k in ("company_id", "cik", "ticker", "company_name", "group", "variant", "overlays", "assignment_basis", "evidence_accession", "evidence_form", "evidence_filed", "evidence_period_end", "evidence_bs_rfile", "evidence_is_rfile", "matched_face_lines")} for a in A if a["in_fsds_extract"] == "N" and a["cohort_status"] == "cohort_file_v1"]
    with open(OUTDIR + "fsds_missing_rfile_route_v2.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(miss[0].keys())); w.writeheader(); w.writerows(miss)
    print("R-file route rows (986 not in the local FSDS extract):", len(miss), dict(collections.Counter(m["group"] for m in miss)))
    import glob as _g
    if _g.glob(b.SC + "/reads/*.json"): print("features exported:", export_features())
    else: print("no SEC cache: decisions reproduced from face_features_v2.csv")
    c = collections.Counter(a["group"] for a in A if a["cohort_status"] == "cohort_file_v1")
    print(len(A), "rows;", len(MV), "moved;", len(Q), "queue")
    for k, v in sorted(c.items(), key=lambda x: -x[1]): print(" ", k, v)


