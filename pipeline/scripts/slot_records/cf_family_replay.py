"""CFO and share-buyback slot cells from the cash-flow FACE of each filing
(stdlib, run with -I). Zero SEC requests and zero database reads: inputs are
the FSN extracts (cf_face_rows.py, cf_num_rows.py, the period cal.tsv). The
verdict comes from the filing's own arithmetic, never from production.

A cell is (company, period end, months). Its value comes from the ORIGINAL
filing (the earliest filing whose period of report is the end date, else the
earliest filing carrying the column). Gates, all on that one accession:
  face column  the filer tagged the cash-flow grand total (change in cash) or
               the section total for the same (ddate, qtrs);
  identity     the cash-flow calc root (change in cash) equals its signed
               children within the filer's rounding unit (the cash-flow
               analogue of the balance-sheet L&E identity);
  section      the section total (operating for CFO, financing for buybacks)
               equals its signed calc children when every child has a value;
               a missing child leaves the section informational;
  restatement  every LATER filing that prints the same column, read by the
               same rule, agrees within rounding; otherwise the cell is hidden
               (founder ruling: restated periods whose copies disagree are
               HIDDEN, quarters and full years).

CFO (production `cfo`: the total including discontinued operations first):
  the printed NetCashProvidedByUsedInOperatingActivities line; else the
  continuing-operations line when the face prints NO discontinued operating
  line (the two perimeters are then the same); a face with continuing and
  discontinued lines but no total is held (`cfo_total_not_printed`, the sum is
  carried as a candidate, never published: it would be a derivation).
Buybacks (production `share_buybacks`: repurchases of common stock):
  sum of financing face lines that repurchase common/ordinary/treasury shares.
  Excluded by the rulebook (S3 2.1, RDDT R8 FILING-CHECKED): tax withholding
  on share-based awards / net share settlement. Also excluded: preferred stock,
  noncontrolling interests, partnership units, debt. A line that names a
  repurchase AND withholding is `buyback_combined_with_other_items`; a generic
  equity-repurchase line whose label names no share class is
  `perimeter_line_unresolved`. No printed repurchase line -> no cell (an
  evidenced zero is the reason rules' job, not this replay's).
Memory stays flat: companies are replayed in batches (BATCH CIKs per pass
over the inputs) and the calc arcs come pre-extracted (cf_cal_rows.py).
usage: cf_family_replay.py <cf_face_rows.jsonl.gz> <cf_num_rows.jsonl.gz> <cf_cal_rows.jsonl.gz> <out_dir>
       cf_family_replay.py --company <companies/<cik10>|parent|@list> <out_dir>
Company mode (FSN store port, 2026-11-01): fsn_company_cf.read_cf_inputs reads ONE company directory
(FORMATS-v1) into exactly the shapes load() builds from the three cohort files, and replay_company runs
the same rules; the regression gate (data-team/strategy/team/CF-PERSHARE-PORT-2026-11-01.md) compares the
two modes cell by cell. The rules below are unchanged from run 7 (work/cashflow/v2-emit 2e061bc).
"""
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

BATCH = 100
SINCE = "20140101"  # v2 full population: every period since 2014 (founder data window)

CASH_CHANGE_RX = re.compile(r"^(CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents|CashAndCashEquivalents|Cash)PeriodIncreaseDecrease")
OP_TOTAL, OP_CONT, OP_DISC = ("NetCashProvidedByUsedInOperatingActivities",
                              "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
                              "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations")
FIN_TOTALS = ("NetCashProvidedByUsedInFinancingActivities", "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations")
OP_LABEL_RX = re.compile(r"net cash.*(provided|used|from|generated).*operating activities", re.I)

REPURCHASE_RX = re.compile(r"repurchas|buy ?back|treasury|reacquir|retire(ment)? of (common|ordinary|class)|purchases? of (common|ordinary|company|capital) (stock|shares)", re.I)
WITHHOLD_RX = re.compile(r"withh[oe]l|net share settle|tax(es)? (paid|payments?|remitted|liabilit)|employee tax|tax liabilit", re.I)
EXCLUDED_RX = re.compile(r"preferred|partnership units|\bunits\b|notes|debentures|debt|warrants", re.I)
COMMON_RX = re.compile(r"common|ordinary|treasury|class [a-c]\b|shares|stock", re.I)
# Verifier run 1 (VERIFY-CFO-BUYBACKS-RUN1-2026-10-31): direction first.
INFLOW_RX = re.compile(r"proceeds|issuance|issued|\bsales?\b|\bsold\b|reissu|exercise", re.I)
OUTFLOW_RX = re.compile(r"repurchas|purchas|buy ?back|acqui|reacquir|retire|payments? for", re.I)
NET_RX = re.compile(r"sales?\s*\(purchases?\)|purchases?\s*\(sales?\)|\(purchases?\)|purchases?,?\s+net|net of (sales|issuance|proceeds)|\bnet\b.*(sales|purchases)", re.I)
SUBSIDIARY_RX = re.compile(r"subsidiar|noncontrolling|non-controlling|minority|aspentech|put option", re.I)
NONCASH_RX = re.compile(r"unsettled|accrued|incurred|not yet paid|non-?cash|accounts payable|commitment", re.I)
SWAP_RX = re.compile(r"\bswap\b|exchange program|exchanged for", re.I)
OPTION_RX = re.compile(r"option exercise|options exercised|exercise of (stock )?options|related to (stock )?option", re.I)
COMBINED_RX = re.compile(r"\band other\b|\bother\b.*\b(repurchas|purchas)|includ", re.I)
SBC_PLAN_RX = re.compile(r"\bSBC\b|(stock|share)[- ]based|equity (award|compensation|incentive)|(compensation|incentive|benefit|employee|stock|equity) plans?|for (delivery|settlement|distribution)|to satisfy", re.I)
EXCISE_RX = re.compile(r"excise", re.I)
BUYBACK_TAGS_COMMON = {"PaymentsForRepurchaseOfCommonStock"}
BUYBACK_TAGS_EXCLUDED = {"PaymentsRelatedToTaxWithholdingForShareBasedCompensation", "PaymentsForRepurchaseOfPreferredStockAndPreferenceStock",
                         "PaymentsForRepurchaseOfRedeemablePreferredStock", "PaymentsForRepurchaseOfConvertiblePreferredStock",
                         "PaymentsToMinorityShareholders", "PaymentsForRepurchaseOfRedeemableNoncontrollingInterest"}


def iso(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:]}"


DIV_HIT_RX = re.compile(r"dividend|distribution", re.I)
DIV_PREFERRED_RX = re.compile(r"preferred|preference", re.I)
DIV_NCI_RX = re.compile(r"noncontrolling|non-controlling|minority|subsidiar", re.I)
DIV_EQUIV_RX = re.compile(r"equivalent", re.I)
DIV_PARTNER_RX = re.compile(r"unitholder|unit holder|limited partner|general partner|partners'?\b|\bunits\b|incentive distribution", re.I)
DIV_COMMON_RX = re.compile(r"common|ordinary|shareholder|stockholder|share ?owner", re.I)
DIV_COMMON_TAGS = {"PaymentsOfDividendsCommonStock", "PaymentsOfDividends", "PaymentsOfOrdinaryDividends"}


def dividend_class(tag, label):
    """Dividends paid = cash paid as dividends to the company's common holders
    as printed (by analogy with the founder's buyback ruling 2026-11-04).
    Excluded with a reason: preferred dividends, distributions to
    noncontrolling interests, dividend equivalents on share awards. Held:
    a line combining common with an excluded item, partnership-unit
    distributions (a definition call), a net line, an unnamed distribution."""
    if tag.endswith(("Member", "Axis", "Domain", "Abstract", "Table", "LineItems")) or tag.startswith(("IncreaseDecrease", "Noncash", "Proceeds")):
        return None
    if not (DIV_HIT_RX.search(label) or "Dividend" in tag or "Distribution" in tag):
        return None
    if tag.startswith("EquityMethodInvestment") or re.search(r"received|from (unconsolidated|equity|affiliat)|of equity investment", label, re.I):
        return None  # an inflow from investees, not a dividend the company pays
    if (NONCASH_RX.search(label) or re.search(r"declared|payable", label, re.I) and not re.search(r"paid|payment", label, re.I)
            or re.search(r"\bnot\s+(yet\s+)?paid\b|\bunpaid\b", label, re.I)):
        # Verifier 2026-11-08: BXP "Dividends and distributions declared but not paid" is a non-cash disclosure
        return "excluded_noncash"
    pref, nci = DIV_PREFERRED_RX.search(label) or "Preferred" in tag, DIV_NCI_RX.search(label) or "Minority" in tag or "Noncontrolling" in tag
    common_named = DIV_COMMON_RX.search(label) is not None
    if (pref or nci) and common_named and re.search(r"\band\b|includ|&", label, re.I):
        return "combined"
    if pref:
        return "perimeter_preferred"
    if nci:
        return "perimeter_nci"
    if re.search(r"\bdividends?\s+and\s+distributions?\b|\bdistributions?\s+and\s+dividends?\b", label, re.I):
        # Verifier 2026-11-08: BXP "Dividends and distributions" pays stockholders AND operating-partnership unit
        # holders in one line: combined, never counted as common dividends
        return "combined"
    if DIV_EQUIV_RX.search(label) and not re.search(r"dividends? and (dividend )?equivalents?|dividends?,? including", label, re.I):
        # a standalone equivalents line (EPD); AAPL's "dividends and dividend
        # equivalents" IS its common dividend line (equivalents on unvested shares)
        return "perimeter_dividend_equivalents"
    if DIV_PARTNER_RX.search(label):
        return "perimeter_partnership_distribution"
    if NET_RX.search(label) or re.search(r"net of", label, re.I):
        return "net"
    if re.search(r"dividend", label, re.I) or tag in DIV_COMMON_TAGS:
        return "common"
    return "common" if common_named else "unresolved"


def buyback_class(tag, label):
    """One class per financing face line, by CASH DIRECTION first (Verifier
    run 1: ADBE, CAT, FICO, REG, SNX, MRSH, UBER summed treasury-sale and
    option proceeds as repurchases; CVX, KMI kept a net line's sign).
      inflow     Proceeds* tags and sale/issuance/exercise lines: never a buyback
      net        a purchases-net-of-sales line: held, never sign-kept
      perimeter_* a line whose inclusion is a definition call: held with reason
      common     a repurchase of the company's own common/ordinary shares"""
    if EXCISE_RX.search(label) or "Excise" in tag:
        return "perimeter_excise_tax"
    if tag in BUYBACK_TAGS_EXCLUDED or tag.endswith(("Member", "Axis", "Domain", "Abstract", "Table", "LineItems")) or tag.startswith(("IncreaseDecrease", "Noncash")):
        return "excluded"
    hit = REPURCHASE_RX.search(label) or "Repurchase" in tag or "TreasuryStock" in tag
    if not hit:
        return None
    if SWAP_RX.search(label):
        return "perimeter_share_swap"  # CCL FY2022 "Purchase of treasury stock under the Stock Swap Program"
    if OPTION_RX.search(label):
        return "perimeter_option_exercise"  # HEI "issued, repurchased and retired related to stock option exercises"
    if COMBINED_RX.search(label) and not WITHHOLD_RX.search(label):
        return "combined"  # LDOS "Repurchases of stock and other"
    if NONCASH_RX.search(label):
        return "excluded"  # unsettled / accrued repurchases: a non-cash disclosure, not a cash line
    if WITHHOLD_RX.search(label) and not REPURCHASE_RX.search(label):
        return "excluded"  # tax paid on net share settlement (rulebook S3 2.1, RDDT R8)
    if tag.startswith("PaymentsForProceedsFrom") or tag == "ProceedsFromRepurchaseOfEquity":
        return "net"
    if tag.startswith("Proceeds") or (INFLOW_RX.search(label) and not OUTFLOW_RX.search(label)):
        return "inflow"
    if NET_RX.search(label):
        return "net"
    if WITHHOLD_RX.search(label):
        # a withholding payment named as a repurchase/treasury acquisition (PGR
        # "treasury shares for restricted stock tax liabilities") is a
        # definition call; a line that ALSO counts ordinary repurchases is combined
        return "combined" if re.search(r"includ|\band\b", label, re.I) else "perimeter_tax_withholding_shares"
    if SUBSIDIARY_RX.search(label) or "Subsidiar" in tag:
        return "perimeter_subsidiary_repurchase"
    if SBC_PLAN_RX.search(label):
        return "perimeter_sbc_plan_purchase"
    if re.search(r"preferred", label, re.I):
        return "excluded"
    if EXCLUDED_RX.search(label):
        # "Repurchases of shares and warrants" (KMI): common shares mixed with another instrument
        return "combined" if re.search(r"common|ordinary|\bshares\b", label, re.I) else "excluded"
    if not OUTFLOW_RX.search(label):
        return "unresolved"  # the label names no purchase (FIS "Treasury stock activity"): net or withholding unknown
    if tag in BUYBACK_TAGS_COMMON or "CommonStock" in tag:
        return "common"
    return "common" if COMMON_RX.search(label) else "unresolved"


def primary_face(face):
    """in place: keep the primary cash-flow report of each filing, the lowest-numbered report that
    prints an operating total (a Schedule I parent-only statement comes later)."""
    for adsh, rows in face.items():
        reports = sorted({rp for rp, _l, t, lab, _c, _n in rows if t in (OP_TOTAL, OP_CONT) or OP_LABEL_RX.search(lab)})
        keep = reports[0] if reports else min(rp for rp, *_ in rows)
        face[adsh] = sorted((ln, t, lab, cu, ng) for rp, ln, t, lab, cu, ng in rows if rp == keep)


def load(face_path, num_path, cal_path, ciks):
    """face rows, values and cash-flow arcs of one batch of companies (cohort files)."""
    filings, face = {}, defaultdict(list)
    with gzip.open(face_path, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r["stmt"] != "CF" or r["cik"] not in ciks:
                continue
            filings[r["adsh"]] = {k: r[k] for k in ("cik", "form", "period", "filed", "fy", "fp", "fsn")}
            face[r["adsh"]].append((r["report"], r["line"], r["tag"], r["label"], r["custom"], r["negating"]))
    primary_face(face)
    vals = defaultdict(dict)  # adsh -> {(tag, ddate, qtrs): Decimal}
    durps = defaultdict(dict)  # adsh -> {(ddate, qtrs): durp of the column's section total}
    with gzip.open(num_path, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r["adsh"] in face:
                vals[r["adsh"]].setdefault((r["tag"], r["ddate"], r["qtrs"]), Decimal(r["value"]))
                if r.get("durp") not in (None, "") and (r["tag"] in (OP_TOTAL, OP_CONT) or CASH_CHANGE_RX.search(r["tag"])):
                    durps[r["adsh"]].setdefault((r["ddate"], r["qtrs"]), float(r["durp"]))
    arcs = {}
    with gzip.open(cal_path, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r["adsh"] in face:
                arcs[r["adsh"]] = {p: [(c, Decimal(w)) for c, w in kids] for p, kids in r["arcs"].items()}
    return filings, face, vals, arcs, durps


def tie(total, kids, v):
    """(ties, gap) of total vs signed kids on this column; None when a term is missing."""
    if total not in v or any(k not in v for k, _ in kids):
        return None, None
    terms = [v[k] for k, _ in kids] + [v[total]]
    gap = v[total] - sum(v[k] * w for k, w in kids)
    return abs(gap) <= common.rounding_unit(terms), gap


def read_cell(adsh, ddate, qtrs, arcs, face, vals):
    """Both families' readings of one face column of one filing."""
    v = {t: vals[adsh][(t, ddate, qtrs)] for (t, d, q) in vals[adsh] if d == ddate and q == qtrs}
    rows = face[adsh]
    tags = [t for _ln, t, _lab, _cu, _ng in rows]
    root_tag = next((p for p in arcs if CASH_CHANGE_RX.search(p) and not any(p == c for kids in arcs.values() for c, _ in kids)), None)
    root_tag = root_tag or next((t for t in tags if CASH_CHANGE_RX.search(t)), None)
    face_col = (root_tag in v) or any(t in v for t in (OP_TOTAL, OP_CONT) + FIN_TOTALS)
    ident, ident_gap = (tie(root_tag, arcs[root_tag], v) if root_tag in arcs else (None, None))
    res = {"face_column": face_col, "identity": ident, "identity_gap": str(ident_gap) if ident_gap is not None else None,
           "has_cal": bool(arcs), "root": root_tag}
    # ---- CFO ----
    custom_op = [t for _ln, t, lab, cu, _ng in rows if cu and OP_LABEL_RX.search(lab) and not re.search(r"continuing|discontinued", lab, re.I)]
    if OP_TOTAL in tags:
        cfo_tag, cfo_basis = OP_TOTAL, "printed_total"
    elif custom_op:
        cfo_tag, cfo_basis = custom_op[0], "printed_total_custom"
    elif OP_CONT in tags and not any(t == OP_DISC or (re.search(r"discontinued", lab, re.I) and re.search(r"operating", lab, re.I)) for _ln, t, lab, _cu, _ng in rows):
        cfo_tag, cfo_basis = OP_CONT, "continuing_equals_total"
    elif OP_CONT in tags:
        cfo_tag, cfo_basis = None, "cfo_total_not_printed"
    else:
        cfo_tag, cfo_basis = None, "no_operating_line"
    sec = None
    if cfo_tag and cfo_tag in arcs:
        sec, _g = tie(cfo_tag, arcs[cfo_tag], v)
    res["cfo"] = {"tag": cfo_tag, "basis": cfo_basis, "value": v.get(cfo_tag) if cfo_tag else None, "section": sec,
                  "candidate_sum": (v[OP_CONT] + v[OP_DISC]) if cfo_basis == "cfo_total_not_printed" and OP_CONT in v and OP_DISC in v else None}
    # ---- buybacks ----
    fin_total = next((t for t in FIN_TOTALS if t in arcs), None)
    fin_kids = {c for c, _ in arcs.get(fin_total, [])} if fin_total else set()
    members = []
    div_members = []
    negated_outflows = 0
    for _ln, t, lab, cu, ng in rows:
        if fin_kids and t not in fin_kids:
            continue  # financing section by the filer's own calc tree
        if ng and t.startswith(("Payments", "Repayments")):
            negated_outflows += 1
        cls = buyback_class(t, lab)
        if cls:
            members.append({"tag": t, "label": lab, "class": cls, "custom": cu, "negating": ng, "value": v.get(t)})
        dcls = dividend_class(t, lab)
        if dcls:
            div_members.append({"tag": t, "label": lab, "class": dcls, "custom": cu, "negating": ng, "value": v.get(t)})
    bsec = None
    if fin_total:
        bsec, _g = tie(fin_total, arcs[fin_total], v)
    res["buybacks"] = {"negated_outflows": negated_outflows, "members": members, "section": bsec, "financing_total": fin_total, "section_by_cal": bool(fin_kids)}
    res["dividends_paid"] = {"negated_outflows": negated_outflows, "members": div_members, "section": bsec, "financing_total": fin_total, "section_by_cal": bool(fin_kids)}
    return res


def verdict_cfo(c, cell):
    if not c["face_column"]:
        return "not_a_face_column", None
    if c.get("stub"):
        return "stub_column", None
    b = cell["basis"]
    if b in ("cfo_total_not_printed", "no_operating_line"):
        return b, None
    if cell["value"] is None:
        return "member_value_missing", None
    if not c["has_cal"]:
        return "hold_no_statement_cal", None
    if c["identity"] is None:
        return "hold_identity_terms_missing", None
    if not c["identity"]:
        return "hold_identity_gap", None
    if cell["section"] is False:
        return "hold_section_gap", None
    return "publishable", cell["value"]


# Founder ruling 2026-11-04: buybacks = cash paid to repurchase the company's
# own common stock as printed. These lines are EXCLUDED with their reason (the
# member list carries the class), never summed and no longer a hold; a line
# that combines a buyback with one of them stays held.
FOUNDER_EXCLUDED = {
    "perimeter_tax_withholding_shares",
    "perimeter_excise_tax",
    "perimeter_sbc_plan_purchase",
    "perimeter_option_exercise",
    "perimeter_subsidiary_repurchase",
    "perimeter_share_swap",
}


def verdict_bb(c, cell):
    ms = cell["members"]
    if not ms or all(m["class"] in ("excluded", "inflow") for m in ms):
        return None, None  # no repurchase line on this face: no cell
    if not c["face_column"]:
        return "not_a_face_column", None
    if c.get("stub"):
        return "stub_column", None
    if not any(m["class"] in ("common", "net", "unresolved", "combined") or m["class"].startswith("perimeter_") for m in ms):
        return None, None  # only inflow/excluded lines: no repurchase on this face
    if not any(m["class"] in ("common", "net", "unresolved", "combined") or (m["class"].startswith("perimeter_") and m["class"] not in FOUNDER_EXCLUDED) for m in ms):
        # every repurchase-like line is excluded by definition (PGR tax-withholding
        # treasury shares, EMR/AspenTech): no buyback value, reason kept
        return "excluded_only:" + "+".join(sorted({m["class"] for m in ms if m["class"] in FOUNDER_EXCLUDED})), None
    if any(m["class"] == "combined" for m in ms):
        return "buyback_combined_with_other_items", None
    for cls in ("net", "unresolved"):
        if any(m["class"] == cls and m["value"] not in (None, 0) for m in ms):
            return {"net": "net_treasury_line", "unresolved": "perimeter_line_unresolved"}.get(cls, cls), None
    common_ms = [m for m in ms if m["class"] == "common"]
    if len(common_ms) > 1:
        # two repurchase lines PRINTED, whatever this column's values (ROST Q1
        # FY2021: "Treasury stock purchased" 47.4M beside a zero "Repurchase of
        # common stock"): which one is the program buyback is a definition call
        return "perimeter_multiple_repurchase_lines", None
    # a repurchase printed without parentheses while the other outflow lines
    # of the section are (AAON Q1 2025): the filer's sign is in doubt
    if any(not m["negating"] for m in common_ms) and cell["negated_outflows"] >= 2:
        return "sign_unclear", None
    printed = [m for m in common_ms if m["value"] is not None]
    if not printed:
        return "no_value_this_column", None  # the line is printed but this column is blank (a dash)
    if any(m["value"] < 0 for m in printed):
        return "sign_unclear", None  # an outflow tag with a negative value: never sign-kept
    if not c["has_cal"]:
        return "hold_no_statement_cal", None
    if not cell["section_by_cal"]:
        return "hold_no_financing_calc", None
    if c["identity"] is None:
        return "hold_identity_terms_missing", None
    if not c["identity"]:
        return "hold_identity_gap", None
    if cell["section"] is False:
        return "hold_section_gap", None
    return "publishable", sum((m["value"] for m in printed), Decimal(0))


DIV_EXCLUDED = {"excluded_noncash", "perimeter_preferred", "perimeter_nci", "perimeter_dividend_equivalents"}


def verdict_div(c, cell):
    """Dividends paid: the SUM of the printed common dividend lines (a regular
    and a special dividend are both paid to common holders), outflow only;
    the same face-column, stub, identity and section gates as buybacks."""
    ms = cell["members"]
    if not ms or all(m["class"] in DIV_EXCLUDED for m in ms):
        return (None, None) if not ms or all(m["class"] == "excluded_noncash" for m in ms) else (
            "excluded_only:" + "+".join(sorted({m["class"] for m in ms if m["class"] != "excluded_noncash"})), None)
    if not c["face_column"]:
        return "not_a_face_column", None
    if c.get("stub"):
        return "stub_column", None
    if any(m["class"] == "combined" for m in ms):
        return "dividends_combined_with_other_items", None
    for cls in ("net", "unresolved", "perimeter_partnership_distribution"):
        if any(m["class"] == cls and m["value"] not in (None, 0) for m in ms):
            return {"net": "net_dividend_line", "unresolved": "perimeter_line_unresolved"}.get(cls, cls), None
    common_ms = [m for m in ms if m["class"] == "common"]
    if any(not m["negating"] for m in common_ms) and cell["negated_outflows"] >= 2:
        return "sign_unclear", None
    printed = [m for m in common_ms if m["value"] is not None]
    if not printed:
        return "no_value_this_column", None
    if any(m["value"] < 0 for m in printed):
        return "sign_unclear", None
    if not c["has_cal"]:
        return "hold_no_statement_cal", None
    if not cell["section_by_cal"]:
        return "hold_no_financing_calc", None
    if c["identity"] is None:
        return "hold_identity_terms_missing", None
    if not c["identity"]:
        return "hold_identity_gap", None
    if cell["section"] is False:
        return "hold_section_gap", None
    return "publishable", sum((m["value"] for m in printed), Decimal(0))


# ---------- replay ----------
FAMILIES = ("cfo", "buybacks", "dividends_paid")


def replay_company(cik, filings, face, vals, all_arcs, durps, cells, summary):
    """append one company's cells to cells[fam] and count verdicts in summary[fam]."""
    adshs = sorted((a for a in filings if filings[a]["cik"] == cik), key=lambda a: (filings[a]["filed"], a))
    readings = defaultdict(list)  # (ddate, qtrs) -> [(adsh, reading)]
    for adsh in adshs:
        arcs = all_arcs.get(adsh, {})
        cols = {(d, q) for (_t, d, q) in vals[adsh] if d >= SINCE}
        for d, q in sorted(cols):
            readings[(d, q)].append((adsh, read_cell(adsh, d, q, arcs, face, vals)))
    # STUB columns (Verifier run 1, Valaris 0000314808-21-000102: a 5-month
    # fresh-start successor tagged qtrs=2): a column whose duration offset
    # (FSN durp) is off the company's own usual offset for that number of
    # quarters by more than 0.1 quarter (~9 days). Costco's 12/12/12/16-week
    # calendar keeps one stable offset per qtrs, so it is not a stub.
    usual = defaultdict(Counter)
    for adsh in adshs:
        for (d, q), dp in durps[adsh].items():
            usual[q][round(dp, 1)] += 1
    for (d, q), rs in readings.items():
        mode = usual[q].most_common(1)[0][0] if usual[q] else 0.0
        for a, r in rs:
            dp = durps[a].get((d, q))
            r["stub"] = dp is not None and abs(dp - mode) > 0.1
    for (d, q), rs in sorted(readings.items()):
        # the original: earliest filing whose period of report is the column end, else the earliest that prints it
        orig = next(((a, r) for a, r in rs if filings[a]["period"] == d and r["face_column"]), None) or next(((a, r) for a, r in rs if r["face_column"]), rs[0])
        a0, r0 = orig
        later = [(a, r) for a, r in rs if a != a0 and r["face_column"] and filings[a]["filed"] >= filings[a0]["filed"]]
        for fam, vf in (("cfo", verdict_cfo), ("buybacks", verdict_bb), ("dividends_paid", verdict_div)):
            verdict, value = vf(r0, r0[fam])
            if verdict is None:
                continue
            disagree = []
            if verdict == "publishable":
                for a, r in later:
                    vv, val = vf(r, r[fam])
                    if vv == "publishable" and abs(val - value) > common.rounding_unit([val, value]):
                        disagree.append({"accession": a, "value": str(val)})
                if disagree:
                    verdict = "restated_copies_disagree"
            summary[fam][verdict] += 1
            cells[fam].append({
                "cik": cik, "end": iso(d), "months": q * 3, "durp": durps[a0].get((d, q)), "accession": a0, "form": filings[a0]["form"],
                "verdict": verdict, "value": str(value) if value is not None and verdict == "publishable" else None,
                "candidate": str(value) if value is not None and verdict != "publishable" else None,
                "detail": ({k: (str(v) if isinstance(v, Decimal) else v) for k, v in r0[fam].items() if k != "members"}
                           | ({"members": [{**m, "value": str(m["value"]) if m["value"] is not None else None} for m in r0[fam]["members"]]} if fam in ("buybacks", "dividends_paid") else {})),
                "identity_gap": r0["identity_gap"], "later_disagree": disagree, "later_copies": len(later),
            })

def replay_batch(filings, face, vals, all_arcs, durps, cells, summary):
    by_cik = defaultdict(list)
    for adsh, m in filings.items():
        by_cik[m["cik"]].append(adsh)
    for cik in sorted(by_cik):
        replay_company(cik, {a: filings[a] for a in by_cik[cik]}, face, vals, all_arcs, durps, cells, summary)


def write_outputs(out_dir, cells, summary):
    out_dir.mkdir(parents=True, exist_ok=True)
    for fam in cells:
        with gzip.open(out_dir / f"{fam}_cells.jsonl.gz", "wt") as fo:
            for c in cells[fam]:
                fo.write(json.dumps(c) + "\n")
        s = dict(sorted(summary[fam].items(), key=lambda kv: -kv[1]))
        json.dump({"cells": len(cells[fam]), "companies": len({c["cik"] for c in cells[fam]}),
                   "publishable_companies": len({c["cik"] for c in cells[fam] if c["verdict"] == "publishable"}), "verdicts": s},
                  open(out_dir / f"{fam}_summary.json", "w"), indent=1)
        print(fam, len(cells[fam]), json.dumps(s))


def main(argv):
    cells = {f: [] for f in FAMILIES}
    summary = {f: defaultdict(int) for f in FAMILIES}
    if argv[0] == "--company":
        from fsn_company import company_dir_list
        from fsn_company_cf import read_cf_inputs
        out_dir = Path(argv[2])
        for d in company_dir_list(argv[1]):
            filings, face, vals, all_arcs, durps = read_cf_inputs(d)
            replay_batch(filings, face, vals, all_arcs, durps, cells, summary)
    else:
        face_path, num_path, cal_path, out_dir = argv[0], argv[1], argv[2], Path(argv[3])
        all_ciks = sorted({json.loads(line)["cik"] for line in gzip.open(face_path, "rt")})
        for b0 in range(0, len(all_ciks), BATCH):
            filings, face, vals, all_arcs, durps = load(face_path, num_path, cal_path, set(all_ciks[b0:b0 + BATCH]))
            print(f"  batch {b0 // BATCH + 1}: {len(filings)} filings", flush=True)
            replay_batch(filings, face, vals, all_arcs, durps, cells, summary)
    write_outputs(out_dir, cells, summary)


if __name__ == "__main__":
    main(sys.argv[1:])
