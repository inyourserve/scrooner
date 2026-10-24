"""Audit sampling frames for the Verifier lane (group audit standard, WO-REVIEW-sector-analyst section 3.1).
Frames only: the Verifier lane re-draws with ITS OWN seed (draw_audit_sample.py) for the independence rule; the 'proposed' draw here uses a declared seed so the
frame is reproducible. Real filings opened by the Sector Analyst are classification evidence, not audit evidence."""
import csv, json, os, sys, random, hashlib, math, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
DATA = "/Users/vikash/wt-sector-groups/data-team/strategy/data/"
OUT = DATA + "audit_frames/"
SEED = 20261022
SMALL = ["midstream", "asset_manager", "broker_dealer", "crypto_digital", "managed_care", "insurance_broker", "exchange", "lender_nonbank", "bdc", "reit_mortgage"]
SEEDED = ["bank", "insurer", "utility", "energy", "reit_equity"]
SHARDS = {r["company_id"]: r for r in csv.DictReader(open("/Users/vikash/wt-sector-groups/doc/data-moat/team/top1000/shards.csv"))}

def bound(N, n, alpha=0.05):
    """largest k (bad members) such that P(0 bad in a sample of n | k bad among N) > alpha: hypergeometric, one-sided 95%"""
    if n >= N: return 0
    k = 0
    while k < N - n and math.comb(N - k - 1, n) / math.comb(N, n) > alpha: k += 1
    return k

def rows_in_scope():
    A = list(csv.DictReader(open(DATA + "group_assignment_v2.csv")))
    return [a for a in A if a["cohort_status"] == "cohort_file_v1" and not a["group"].startswith("excluded")]

def strata(a):
    rank = int(SHARDS[a["company_id"]]["rank"]) if a["company_id"] in SHARDS and SHARDS[a["company_id"]]["rank"] else 9999
    size = "top100" if rank <= 100 else "rest"
    pe = a["evidence_period_end"]
    fye = "calendar" if pe[5:7] == "12" else ("noncalendar" if pe else "unknown")
    era = a["evidence_filed"][:4] if a["evidence_filed"] else (pe[:4] if pe else "unknown")
    return f"{size}|{fye}|era{era}"

def risk_flags(a):
    f = []
    if a["overlays"]: f.append("overlay")
    DEFAULT_VARIANT = {"bank": {"deposit_taker"}, "reit_equity": {"property_reit"}, "utility": {"regulated"}, "energy": {"exploration_production", "refiner", "oilfield_services", "drilling_services", "exploration_services", "ngl", "refined_products"}}
    if a["variant"] and a["group"] in ("insurer", "reit_equity", "bank", "utility", "energy", "midstream") and a["variant"] not in DEFAULT_VARIANT.get(a["group"], set()):
        f.append("subvariant:" + a["variant"])
    if a["assignment_basis"] in ("hand_read",): f.append("hand_read")
    if a["assignment_basis"] == "code_reader": f.append("fsds_queue_cleared_by_reader")
    if a["moved_from_draft"] == "Y": f.append("moved_from_draft")
    if "sic_mismatch" in a["review_flags"]: f.append("sic_mismatch")
    sic = a["sic_cohort_sec"].split()[0].split("=")[1] if "cohort=" in a["sic_cohort_sec"] else ""
    if sic in ("6411", "6199", "6211", "6200", "6282", "4610", "4922", "4923", "4924", "") : f.append("ambiguous_or_blank_sic")
    if a["evidence_period_end"][5:7] not in ("12", ""): f.append("noncalendar_fye")
    if a["ticker"] in ("PSKY", "VMRK", "XOM", "EQR"): f.append("identity_event")
    return f

def stratified_pick(pool, n, rng, key):
    if n >= len(pool): return list(pool)
    groups = collections.defaultdict(list)
    for p in pool: groups[key(p)].append(p)
    alloc = {k: min(2, len(v)) for k, v in groups.items()}
    while sum(alloc.values()) > n:  # too many strata for n: drop smallest
        k = min(alloc, key=lambda x: (len(groups[x]), x)); alloc[k] -= 1
        if alloc[k] == 0: del alloc[k]
    left = n - sum(alloc.values())
    cap = {k: len(groups[k]) - alloc.get(k, 0) for k in groups}
    tot = sum(cap.values())
    quota = {k: left * cap[k] / tot if tot else 0 for k in groups}
    for k in sorted(groups, key=lambda x: (-(quota[x] - int(quota[x])), x)):
        add = int(quota[k]); alloc[k] = alloc.get(k, 0) + add
    short = n - sum(alloc.values())
    for k in sorted(groups, key=lambda x: (-(quota[x] - int(quota[x])), x)):
        if short <= 0: break
        if alloc.get(k, 0) < len(groups[k]): alloc[k] = alloc.get(k, 0) + 1; short -= 1
    picks = []
    for k in sorted(groups):
        if alloc.get(k, 0) > 0:
            lst = sorted(groups[k], key=lambda x: x["company_id"]); rng.shuffle(lst); picks += lst[:alloc[k]]
    return picks

def main(seed=SEED, outdir=None):
    global OUT
    if outdir: OUT = outdir.rstrip("/") + "/"
    os.makedirs(OUT, exist_ok=True)
    rows = rows_in_scope()
    by = collections.defaultdict(list)
    for a in rows: by[a["group"]].append(a)
    rng = random.Random(seed)
    manifest = {"seed": seed, "source": "group_assignment_v2.csv", "source_sha1": hashlib.sha1(open(DATA + "group_assignment_v2.csv", "rb").read()).hexdigest(),
                "scope": "cohort_file_v1 members not excluded.*", "tiers": {}, "note": "proposed_draw is reproducible but NOT independent; the Verifier lane must re-draw with its own seed (draw_audit_sample.py) before the result counts toward a denominator change. Sector Analyst openings (hand reads, R-file reader) are classification evidence, not audit evidence."}
    cols = ["company_id", "cik", "ticker", "company_name", "group", "variant", "overlays", "assignment_basis", "stratum", "risk_flags", "risk_score", "s2_opened", "tier", "proposed_draw"]
    def emit(name, rowsout):
        with open(OUT + name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rowsout)
    def decorate(a, tier, draw):
        rf = risk_flags(a)
        return dict(company_id=a["company_id"], cik=a["cik"], ticker=a["ticker"], company_name=a["company_name"], group=a["group"], variant=a["variant"], overlays=a["overlays"],
                    assignment_basis=a["assignment_basis"], stratum=strata(a), risk_flags=";".join(rf), risk_score=len(rf), s2_opened=a["s2_opened"], tier=tier, proposed_draw=draw)
    # 1. census, small groups
    census = []
    for g in SMALL:
        for a in by.get(g, []): census.append(decorate(a, "census", "census"))
    emit("frame_census_small_groups.csv", census)
    manifest["tiers"]["census_small_groups"] = {"groups": {g: len(by.get(g, [])) for g in SMALL}, "n": len(census), "reader": "Verifier independent re-read of ALL members", "bound_if_all_clean": "0 wrong of N at the filing date (exact)"}
    # 2. seeded groups: 30 random + 10 risk-selected
    seeded = []; man2 = {}
    for g in SEEDED:
        pool = by.get(g, []); N = len(pool)
        dec = [decorate(a, "H", "") for a in pool]
        byid = {d["company_id"]: d for d in dec}
        rnd = stratified_pick(pool, min(30, N), rng, strata)
        rid = {a["company_id"] for a in rnd}
        rest = [d for d in dec if d["company_id"] not in rid]
        tb = {d["company_id"]: rng.random() for d in rest}   # seeded tie-break; members with no risk flag are filled by seeded draw
        rest.sort(key=lambda d: (-d["risk_score"], tb[d["company_id"]]))
        risk = rest[:10]
        for d in dec:
            d["proposed_draw"] = "random30" if d["company_id"] in rid else ("risk10" if d in risk else "not_drawn")
        seeded += dec
        n_read = len(rid) + len(risk)
        man2[g] = {"N": N, "random": len(rid), "risk": len(risk), "total_read": n_read, "bound_zero_wrong_in_random": bound(N, len(rid)), "note": "random draw alone; risk-selected members add coverage but are not random"}
    emit("frame_seeded_five_groups.csv", seeded)
    manifest["tiers"]["seeded_groups"] = man2
    # 3. corporate: 60 random + 15 risk + 15 negative controls
    corp = by.get("corporate", [])
    eligible_random = [a for a in corp if a["assignment_basis"] in ("code", "code_fsds_only") and a["s2_opened"] == "N" and not a["overlays"]]
    import gzip
    cls = json.load(gzip.open(DATA + "r4_sector/cls.json.gz"))
    FIN = ["deposits", "loans_line", "nonint_exp", "provision_credit", "net_interest_inc", "premiums", "claims_liab", "claims_exp", "real_estate_bs", "rental_rev", "mort_assets", "investments_fv", "total_inv_income", "nav", "fees_mgmt", "brokerage", "partners_cap", "reg_assets", "og_props"]
    def finscore(a):
        f = cls.get(str(int(a["cik"])))
        return sum(1 for k in FIN if f and f["ev"].get(k)) if f else 0
    rnd60 = stratified_pick(eligible_random, min(60, len(eligible_random)), rng, strata)
    rid = {a["company_id"] for a in rnd60}
    pool_rest = [a for a in corp if a["company_id"] not in rid]
    dec_rest = [decorate(a, "V", "") for a in pool_rest]
    dec_rest.sort(key=lambda d: (-d["risk_score"], d["company_id"]))
    risk15 = dec_rest[:15]
    rk = {d["company_id"] for d in risk15}
    neg_pool = sorted([a for a in pool_rest if a["company_id"] not in rk and finscore(a) >= 2 and a["assignment_basis"] in ("code", "code_reader") and not a["overlays"]], key=lambda a: (-finscore(a), a["company_id"]))
    neg15 = neg_pool[:15]
    nid = {a["company_id"] for a in neg15}
    dec = []
    for a in corp:
        d = decorate(a, "V", "random60" if a["company_id"] in rid else ("risk15" if a["company_id"] in rk else ("negctl15" if a["company_id"] in nid else "not_drawn")))
        d["risk_flags"] = d["risk_flags"] + (";finsignals=%d" % finscore(a) if finscore(a) else "")
        dec.append(d)
    emit("frame_corporate.csv", dec)
    N = len(corp)
    manifest["tiers"]["corporate"] = {"N": N, "random_frame_size": len(eligible_random), "random": len(rid), "risk": len(rk), "negative_controls": len(nid), "negative_control_pool": len(neg_pool),
                                      "bound_zero_wrong_in_random": bound(N, len(rid)), "bound_pooled_with_S2_30_even_spaced": bound(N, len(rid) + 30), "note": "negative controls are code-assigned corporates (no hand read, no overlay) with >= 2 FSDS financial-line flags; bound applies to the random part only; the S2 30 are systematic, so the pooled bound is indicative"}
    # 4. moved companies
    mv = list(csv.DictReader(open(DATA + "group_moves_v2.csv")))
    mv_ids = {m["company_id"] for m in mv}
    movedrows = []
    ids = sorted(mv_ids)
    rng2 = random.Random(seed + 1)
    seeded30 = set(rng2.sample(ids, min(30, len(ids))))
    allv1 = [a for a in csv.DictReader(open(DATA + "group_assignment_v2.csv")) if a["cohort_status"] == "cohort_file_v1"]
    for a in allv1:
        if a["company_id"] in mv_ids:
            movedrows.append(decorate(a, "moved", "all_have_evidence;seeded30" if a["company_id"] in seeded30 else "all_have_evidence"))
    emit("frame_moved_companies.csv", movedrows)
    manifest["tiers"]["moved_companies"] = {"n": len(movedrows), "rule": "every moved company has an evidence row (accession + locator) in group_moves_v2.csv; Verifier re-reads the 40 not previously Verifier-checked or a seeded 30"}
    json.dump(manifest, open(OUT + "frames_manifest.json", "w"), indent=1)
    return manifest

if __name__ == "__main__":
    m = main(int(sys.argv[1]) if len(sys.argv) > 1 else SEED, sys.argv[2] if len(sys.argv) > 2 else None)   # Verifier lane: frames.py <own seed> <own outdir>
    print(json.dumps(m, indent=1)[:3000])
