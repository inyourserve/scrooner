"""Reader-phase decision with strict signatures. Returns (group, overlays, basis, reason) or (None, ..., 'hand', reason)."""
import groups_v2 as g

BENIGN_WITH = {
    "bank": {"asset_mgmt_fees", "brokerage", "partnership"},
    "insurer": {"asset_mgmt_fees", "partnership"},
    "reit_equity": {"partnership", "asset_mgmt_fees"},
    "bdc": {"asset_mgmt_fees", "partnership"},
    "utility": {"oilgas"},
    "energy": {"oilgas", "partnership"},
}

def decide_strict(sic, feats, sigs):
    sg = g.sic_group(sic)
    prim = [k for k in sigs if k in ("bank", "insurer", "insurer_or_managed_care_classified_bs", "bdc", "reit_equity", "utility")]
    other = [k for k in sigs if k not in prim]
    if sic in g.AMBIG_SIC or sg == "AMBIG":
        return None, [], "hand", f"ambiguous_sic_{sic or 'blank'}"
    if "finance_arm" in sigs or "digital_assets" in sigs:
        return None, [], "hand", "finance_arm_or_digital_assets_on_face"
    if len(prim) > 1:
        return None, [], "hand", "multiple_primary_signatures:" + "+".join(prim)
    if len(prim) == 1:
        p = prim[0]
        fam = "insurer" if p.startswith("insurer") else p
        if p == "insurer_or_managed_care_classified_bs":
            if sg == "managed_care":
                return "managed_care", [], "reader_code", "sic_6324+premiums_claims_with_classified_balance_sheet"
            return None, [], "hand", "insurer_signature_with_classified_balance_sheet"
        unexpected = [o for o in other if o not in BENIGN_WITH.get(fam, set())]
        if unexpected:
            return None, [], "hand", f"primary_{fam}_with_other:" + "+".join(unexpected)
        ok = (sg == "bank" and fam == "bank") or (sg == "insurer" and fam == "insurer") or (sg == "reit" and fam == "reit_equity") or (sg == "utility" and fam == "utility") or (sg == "managed_care" and False)
        if ok:
            return ({"reit_equity": "reit_equity"}.get(fam, fam)), [], "reader_code", f"sic_{sg}+strict_{fam}"
        return None, [], "hand", f"disagree_sic_{sg}_strict_{fam}"
    # no primary signature
    if sg in ("bank", "insurer", "managed_care", "reit", "lender_or_other_financial", "spac"):
        return None, [], "hand", f"sic_{sg}_but_no_strict_signature"
    benign = ("oilgas", "asset_mgmt_fees") + (("partnership",) if sg == "energy" else ())
    unexpected = [o for o in other if o not in benign]  # lone fee labels (hotel management fees, etc.) are noise for a corporate SIC
    if unexpected:
        return None, [], "hand", "corporate_sic_with_other_signature:" + "+".join(unexpected)
    if sg == "utility":
        return "utility", [], "reader_code", "sic_utility+no_financial_signature(variant:" + ("regulated" if "reg_assets" in feats else "independent_power") + ")"
    if sg == "energy":
        return "energy", [], "reader_code", "sic_energy+no_financial_signature"
    # corporate
    if "rev" not in feats:
        return None, [], "hand", "no_revenue_line_matched_check_pre_revenue_overlay"
    return "corporate", [], "reader_code", "sic_corporate+no_financial_signature"
