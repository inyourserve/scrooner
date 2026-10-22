"""group.assign@2 classifier core (Sector Analyst, 2026-10-22).

Two independent signals per company:
  A  face-statement shape  : flags computed from the filer's own latest 10-K face statements (FSDS pre.txt rules via
                             facelib, or the R-file reader for filers missing from the local FSDS extract)
  B  SIC bin               : SIC code from the cohort file (core.company.sic_code, which mirrors SEC submissions)
A mapped data value (e.g. a concept holding a value) and a vendor field are NEVER signals.

Code assigns a group only when A and B agree and the SIC is not on the ambiguous list. Everything else goes to a human read.
"""
import re

AMBIG_SIC = {"6411", "6199", "6211", "6200", "6282", "4610", "4922", "4923", "4924", ""}
BANK_SIC = {"6021", "6022", "6035", "6036"}
INSURER_SIC = {"6311", "6321", "6331", "6351", "6361", "6399"}
MANAGED_SIC = {"6324"}
LENDER_SIC = {"6111", "6141", "6153", "6159", "6162", "6099", "6029"}
REIT_SIC = {"6798", "6500", "6510", "6512", "6513", "6519", "6531", "6552"}
UTIL_SIC = {"4911", "4931", "4932", "4941", "4991", "4900"}
WASTE_SIC = {"4953", "4955"}
ENERGY_SIC = {"1311", "1381", "1382", "1389", "2911", "2990", "1321"}
SPAC_SIC = {"6770"}

STRONG_LONE = ["deposits", "nonint_exp", "provision_credit", "net_interest_inc", "premiums", "claims_liab",
               "claims_exp", "investments_fv", "total_inv_income", "nav", "trust_assets", "partners_cap", "reg_assets"]


def sic_group(sic: str) -> str:
    if sic in AMBIG_SIC:
        return "AMBIG"
    if sic in BANK_SIC:
        return "bank"
    if sic in INSURER_SIC:
        return "insurer"
    if sic in MANAGED_SIC:
        return "managed_care"
    if sic in LENDER_SIC:
        return "lender_or_other_financial"
    if sic in REIT_SIC:
        return "reit"
    if sic in UTIL_SIC:
        return "utility"
    if sic in ENERGY_SIC:
        return "energy"
    if sic in SPAC_SIC:
        return "spac"
    if sic.isdigit() and 6000 <= int(sic) <= 6799:
        return "AMBIG"   # any other financial SIC: not in a tested bin
    return "corporate"   # includes waste 4953/4955 (ordinary corporate shape, S2 FC: WM RSG CLH CWST WCN)


def shape(ev: dict, fl: dict) -> tuple[str, list[str]]:
    """Face-statement shape from flags. Returns (shape_group, evidence list). shape_group is the family whose signature
    (at least two lines) is on the face, 'lone:<flag>' when exactly one strong financial line is on the face,
    'corporate' when no financial line is, or 'none' when the filing has no statements."""
    if ev.get("no_stmts"):
        return "none", []
    e = []
    sigs = []
    n_bank = [k for k in ("loans_line", "nonint_exp", "provision_credit", "net_interest_inc") if ev.get(k)]
    if ev.get("deposits") and len(n_bank) >= 2:
        sigs.append("bank")
        e.append("deposits+" + "+".join(n_bank))
    ins = [k for k in ("premiums", "claims_liab", "claims_exp") if ev.get(k)]
    if len(ins) >= 2:
        sigs.append("insurer")
        e.append("+".join(ins))
    bdc = [k for k in ("investments_fv", "total_inv_income", "nav") if ev.get(k)]
    if len(bdc) >= 2:
        sigs.append("bdc")
        e.append("+".join(bdc))
    if ev.get("real_estate_bs") and ev.get("rental_rev"):
        sigs.append("reit_equity")
        e.append("real_estate_bs+rental_rev")
    if ev.get("reg_assets") and ev.get("util_rev"):
        sigs.append("utility")
        e.append("reg_assets+util_rev")
    if ev.get("partners_cap"):
        sigs.append("partnership")   # secondary only when another family's signature is also on the face (OP units at REITs)
        e.append("partners_cap")
    if ev.get("trust_assets"):
        sigs.append("spac")
        e.append("trust_assets")
    if len(sigs) == 1:
        return sigs[0], e
    if len(sigs) > 1:
        return "multi:" + "|".join(sigs), e
    lone = [k for k in STRONG_LONE if ev.get(k)]
    if lone:
        return "lone:" + "+".join(lone), lone
    return "corporate", []


def fam_of_shape(s: str) -> str:
    return s.split(":")[0]


def decide(sic: str, ev: dict, fl: dict) -> dict:
    """Phase-1 code decision. Returns group (or None), basis, reason."""
    sg = sic_group(sic)
    s, e = shape(ev, fl)
    fam = fam_of_shape(s)
    sigs = s[6:].split("|") if s.startswith("multi:") else [fam]
    if "partnership" in sigs and len(sigs) > 1:
        sigs = [x for x in sigs if x != "partnership"]
        if len(sigs) == 1:
            fam, s = sigs[0], sigs[0]
    out = {"sic_group": sg, "shape": s, "shape_evidence": e}
    if fam == "none":
        return {**out, "group": None, "basis": "queue", "reason": "no_face_statements_in_extract"}
    if sic in AMBIG_SIC or sg == "AMBIG":
        return {**out, "group": None, "basis": "queue", "reason": f"ambiguous_sic_{sic or 'blank'}"}
    if s.startswith("multi:"):
        return {**out, "group": None, "basis": "queue", "reason": "multiple_signatures_on_face"}
    if s.startswith("lone:"):
        return {**out, "group": None, "basis": "queue", "reason": "lone_flag_" + s[5:]}
    if sg == "bank" and fam == "bank":
        return {**out, "group": "bank", "basis": "code", "reason": "sic_bank+face_bank"}
    if sg == "insurer" and fam == "insurer":
        return {**out, "group": "insurer", "basis": "code", "reason": "sic_insurer+face_insurer"}
    if sg == "managed_care" and fam == "insurer":
        return {**out, "group": None, "basis": "queue", "reason": "sic_6324_shape_insurer_check_classified_balance_sheet"}
    if sg == "reit" and fam == "reit_equity":
        return {**out, "group": "reit_equity", "basis": "code", "reason": "sic_reit+face_rental_real_estate"}
    if sg == "utility" and fam == "utility":
        return {**out, "group": "utility", "basis": "code", "reason": "sic_utility+face_regulatory_assets"}
    if sg == "energy" and fam == "corporate":
        return {**out, "group": "energy", "basis": "code", "reason": "sic_energy+corporate_shape_variant"}
    if sg == "corporate" and fam == "corporate":
        return {**out, "group": "corporate", "basis": "code", "reason": "sic_corporate+no_financial_signature_on_face"}
    return {**out, "group": None, "basis": "queue", "reason": f"disagree_sic_{sg}_face_{fam}"}
