"""D&A and capex per APPROVAL-DA-CAPEX-2026-10-26, cohort-wide, from the cash-flow
FACE (FSN pre rows + same-accession num values; zero SEC requests). Dry run:
writes cell files and a summary, nothing to the database. Production's value is
carried as information only (a verdict never depends on it).

Cells: one per (company, column) where the filer tagged a cash-flow section total
for that column in that filing (face-column rule, Verifier V3/V4). The original
10-K/10-Q whose period is the column end wins; comparatives only when no original.

Capex (perimeter question open, founder; both variants computed, flag OFF):
  each printed capex-class line in the investing block is classed by NATURE
  (ppe, leased = equipment leased to others, software = capitalized software,
  intangible = excluded, net = PaymentsForProceedsFrom...) and by face SUBSECTION
  (continuing, or discontinued = printed inside the discontinued-operations
  investing block that ends at CashProvidedByUsedInInvestingActivitiesDiscontinued
  Operations). A printed child is never summed beside its printed parent (cal).
  variant_narrow = PP&E purchase lines of the continuing block (the line alone)
  variant_ruling = narrow + leased + software, + discontinued-block capex lines
                   when the CFO that FCF uses is the TOTAL (total CFO printed)
  interim (in force until the founder answers) = narrow, but HIDDEN with
  `perimeter_line_unresolved` wherever the two variants differ; a net_capex line
  printed beside a PP&E line in the continuing block is unresolved in BOTH.
D&A (in force, 2a/2b):
  asset_da lines count; a generic amortization line (AdjustmentForAmortization or a
  custom "Amortization" line) counts only when its label names intangibles or
  software, or its value ties within one rounding unit to the income-statement
  face intangible-amortization lines of the same column (AMD FY2025 2,254 =
  1,031 + 1,223); otherwise the cell is `perimeter_line_unresolved`. A combined
  "depreciation, amortization and other" line is `da_combined_with_other_items`.
  Excluded: debt-cost, premium/discount, content/film, contract-cost, ROU,
  stock compensation, impairment.
usage: cf_da_capex_variants.py <cf_face.jsonl.gz> <prod_cf.jsonl.gz> <out_dir>
"""
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

face_path, prod_path, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out_dir.mkdir(parents=True, exist_ok=True)

OP_TOTAL = ("NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations")
INV_TOTAL = ("NetCashProvidedByUsedInInvestingActivities", "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations")
INV_DISC = "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations"

CAPEX_TAG = re.compile(
    r"PaymentsToAcquireProductiveAssets|PaymentsToAcquirePropertyPlantAndEquipment|"
    r"PaymentsToAcquireOtherPropertyPlantAndEquipment|PaymentsForCapitalImprovements|"
    r"PaymentsToAcquireMachineryAndEquipment|PaymentsForProceedsFromProductiveAssets|"
    r"PaymentsToDevelopSoftware|PaymentsForSoftware|PaymentsToAcquireSoftware|"
    r"PaymentsToAcquireIntangibleAssets|PaymentsToAcquireEquipmentOnLease|"
    r"PaymentsForProceedsFromPropertyPlantAndEquipment|PaymentsToAcquirePropertySubjectToOrAvailableForOperatingLease|"
    r"PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets")
CAPEX_LABEL = re.compile(
    r"capital expenditure|purchases? of (property|premises|plant|equipment|fixed)|"
    r"additions to (property|plant|premises|fixed|equipment)|expenditures? for (property|equipment)|"
    r"leased to others|capitali[sz]ed software|software development|internal.use software", re.I)
CAPEX_EXCLUDE = re.compile(r"Businesses|Investments|Proceeds(From)?Sale|ProceedsFrom(?!.*Productive)", re.I)
# capex-like lines outside this ruling (counted, never summed): oil and gas, real estate
CAPEX_OTHER = re.compile(r"OilAndGas|ExploreAndDevelop|RealEstate|DevelopRealEstate", re.I)


def capex_nature(tag, label):
    if tag == "PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets":
        return "ppe_with_intangibles"  # one printed line (URI non-rental + intangibles): cannot split without notes
    if tag == "PaymentsToAcquirePropertySubjectToOrAvailableForOperatingLease":
        return "leased"  # URI rental fleet
    if re.search(r"IntangibleAssets", tag) or re.search(r"intangible|licen[cs]e|patent|spectrum", label, re.I):
        return "intangible"
    if re.search(r"direct financing lease|sales.type lease", label, re.I):
        return "intangible"  # a lessor's lease receivable is an investment, never capex
    if "EquipmentOnLease" in tag and (re.search(r"previously leased|assumed lease|financing arrangement", label, re.I)
                                      or label.strip().lower() == "payments to acquire equipment on lease"):
        return "lease_unclear"  # element misused or label silent: unresolved in BOTH variants
    if re.search(r"exclud\w* (equipment )?leased", label, re.I):
        return "ppe"  # CAT: "Capital expenditures - excluding equipment leased to others" is the PP&E line
    if "EquipmentOnLease" in tag or re.search(r"leased to others|equipment on (operating )?lease|(?<!non-)(?<!non )rental (equipment|fleet)|lease fleet", label, re.I):
        return "leased"
    if re.search(r"software", label, re.I) and re.search(r"PropertyPlantAndEquipment|ProductiveAssets", tag) \
            and re.search(r"property|plant|premises|equipment|capital expenditure|building", label, re.I):
        return "ppe"  # ONE printed line covering PP&E and software: the filer's own total, same in both variants
    if "Software" in tag or re.search(r"software", label, re.I):
        return "software"
    if tag.startswith("PaymentsForProceedsFrom"):
        # the approval: a net line inside the continuing block whose label does not
        # name its nature stays unresolved; a label naming PP&E reads as PP&E
        return "ppe" if re.search(r"property|plant|equipment|capital expenditure", label, re.I) else "net"
    return "ppe"


DA_TAG = re.compile(r"Depreciation|Amortization|Depletion")
DA_TAG_EXCLUDE = re.compile(r"AccumulatedDepreciation|RightOfUseAsset|AmortizedCost|AvailableForSale")
DA_EXCLUDED_LABEL = re.compile(
    r"debt|financing|issuance|discount|premium|bond|note|content|film|program|contract|"
    r"customer incentive|right.of.use|operating lease|lease (asset|cost)|stock|share.based|"
    r"compensation|impairment|deferred (charges|commission|revenue|policy|acquisition)|"
    # lines whose face label names a nature outside the D&A definition (ruling: the label
    # settles it); genuinely open natures (nuclear fuel, major maintenance, dry-docking,
    # servicing rights, generic "Amortization") still tie out or hold
    r"above.{0,12}below|below.{0,12}above|(above|below).market|lease incentive|straight.line|"
    r"deferred (costs|hedge|gain|loss|settlement)|hedg|derivative|step.up|inventory fair value|"
    r"fair value adjustment|defined benefit|pension|postretirement|non.cash interest|loans? (to|and advances)", re.I)
DA_EXCLUDED_TAG = re.compile(
    r"AmortizationOfDebtDiscount|DebtIssuanceCost|AmortizationOfFinancingCosts|"
    r"AccretionAmortizationOfDiscountsAndPremiums|Premium|Discount|ShareBased|Impairment|"
    r"OperatingLease|RightOfUse|DeferredPolicyAcquisition|DeferredSalesCommission|FilmCost|ContentAsset|"
    r"AboveAndBelowMarketLease|LeaseIncentive|DeferredCharges|DeferredHedge|InventoryStepUp|DefinedBenefit")
ASSET_DA_TAG = re.compile(
    r"DepreciationDepletionAndAmortization|DepreciationAmortizationAndAccretionNet|"
    r"DepreciationAndAmortization$|^Depreciation$|DepreciationNonproduction|"
    r"AmortizationOfIntangibleAssets|CapitalizedComputerSoftwareAmortization|DepreciationAmortizationAndOther$")
IS_INTANGIBLE_AMORT = re.compile(r"amorti[sz]ation of (acquisition.related |acquired |purchased |other )?(intangible|developed technology|technology)", re.I)


def da_nature(tag, label, custom, label_ok=True):
    if not label_ok:
        # FSN pre gave this line the label of another printed line (AMD FY2024:
        # AdjustmentForAmortization shown as "Amortization", plabel = the ROU line's):
        # the label is no evidence; the tag decides, a generic line ties out or holds
        label = ""
    if DA_EXCLUDED_TAG.search(tag) or DA_EXCLUDED_LABEL.search(label):
        return "excluded"
    if re.search(r"depreciation", label, re.I) and re.search(r"\bother\b", label, re.I):
        return "combined_other"  # 2b: "Depreciation, amortization, and other"
    if not custom and ASSET_DA_TAG.search(tag) and not tag.endswith("AndOther"):
        return "asset_da"
    if re.search(r"depreciation|depletion", label, re.I):
        return "asset_da"
    if re.search(r"intangible|software|developed technology", label, re.I):
        return "asset_da"  # the label itself names the asset (approval 2a evidence route)
    return "other_amort"  # generic amortization: needs the income-statement tie-out


def dec(x):
    try:
        return Decimal(x)
    except (InvalidOperation, TypeError):
        return None


def runit(values, cap=Decimal(1000000)):
    unit = cap
    for v in values:
        if v is None or v == 0:
            continue
        while unit > 1 and v % unit != 0:
            unit /= 10
    return unit


def month_end(d):
    """FSN num ddate is the period end ROUNDED to the nearest month end."""
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        first = date(y, m, 1)
        last = first - timedelta(days=1)
    else:
        nxt = date(y + (m == 12), m % 12 + 1, 1)
        last = nxt - timedelta(days=1)
    return last.isoformat()


# production, keyed (cik, concept, rounded month end, quarters)
prod = defaultdict(dict)
for line in gzip.open(prod_path, "rt"):
    cik, name, s, e, v = json.loads(line)
    q = round((date.fromisoformat(e) - date.fromisoformat(s)).days / 91.3)
    if q in (1, 2, 3, 4):
        prod[(cik, name)][(month_end(e), q)] = Decimal(v)

# choose one filing per (cik, column): original whose period is the column end
# pass 1 (streaming; holding every filing swaps): the winning filing per column
best = {}
for line in gzip.open(face_path, "rt"):
    f = json.loads(line)
    cf = [r for r in f["face"] if r["stmt"] == "CF"]
    for col, vals in f["values"].items():
        ddate, q = col.split("|")
        if int(q) not in (1, 2, 3, 4) or ddate < "20150101":
            continue
        if not any(t in vals for t in OP_TOTAL + INV_TOTAL):
            continue  # not a face column of this filing
        if not cf:
            continue
        rank = (ddate == f["period"], not f["form"].endswith("/A"), f["filed"])
        key = (f["cik"], ddate, int(q))
        if key not in best or rank > best[key][0]:
            best[key] = (rank, f["adsh"])

cells = []
summ = Counter()
per_company = defaultdict(Counter)
examples = defaultdict(list)
wanted = defaultdict(list)
for key, (_rank, adsh) in best.items():
    wanted[adsh].append(key)
del best


def chosen():
    """pass 2: stream again, yield only the winning (column, filing) pairs"""
    for line in gzip.open(face_path, "rt"):
        f = json.loads(line)
        for key in wanted.get(f["adsh"], ()):
            yield key, f


for (cik, ddate, q), f in chosen():
    adsh = f["adsh"]
    vals = f["values"][f"{ddate}|{q}"]
    end = f"{ddate[:4]}-{ddate[4:6]}-{ddate[6:]}"
    # the cash-flow face: the CF report with the operating total, in line order
    cf_reports = Counter(r["report"] for r in f["face"] if r["stmt"] == "CF" and r["tag"] in OP_TOTAL + INV_TOTAL)
    if not cf_reports:
        continue
    rep = cf_reports.most_common(1)[0][0]
    rows = [r for r in f["face"] if r["stmt"] == "CF" and r["report"] == rep]
    is_rows = [r for r in f["face"] if r["stmt"] == "IS"]
    idx = {r["tag"]: i for i, r in enumerate(rows)}
    op_i = max((idx[t] for t in OP_TOTAL if t in idx), default=None)
    inv_i = max((idx[t] for t in INV_TOTAL if t in idx), default=None)
    cont_inv_i = idx.get("NetCashProvidedByUsedInInvestingActivitiesContinuingOperations")
    disc_inv_i = idx.get(INV_DISC)
    parents = defaultdict(set)
    for _g, p, c, _w in f.get("cal", []):
        parents[c].add(p)
    printed = {r["tag"] for r in rows}
    cfo_total = "NetCashProvidedByUsedInOperatingActivities" in vals
    cell = {"ticker": f["ticker"], "cik": cik, "end": end, "qtrs": q, "accession": adsh, "form": f["form"]}

    # ---------------- capex ----------------
    lines = []
    other_capex = 0
    if op_i is not None and inv_i is not None and inv_i > op_i:
        block = rows[op_i + 1:inv_i + 1]
        for k, r in enumerate(block, start=op_i + 1):
            t, lab = r["tag"], r["plabel"]
            if CAPEX_OTHER.search(t):
                other_capex += 1 if t in vals and dec(vals[t]) else 0
                continue
            is_cap = (CAPEX_TAG.search(t) and not CAPEX_EXCLUDE.search(t)) or (r["custom"] and CAPEX_LABEL.search(lab) and not re.search(r"proceeds|sale of|disposal", lab, re.I))
            if not is_cap or t not in vals:
                continue
            if parents[t] & printed and any(CAPEX_TAG.search(p) or p in INV_TOTAL for p in parents[t] & printed if p not in INV_TOTAL):
                continue  # a printed child beside its printed capex parent
            v = dec(vals[t])
            if v is None or v == 0:
                continue
            disc = (disc_inv_i is not None and cont_inv_i is not None and cont_inv_i < k <= disc_inv_i) or bool(re.search(r"discontinued", lab, re.I))
            lines.append({"tag": t, "label": lab, "nature": capex_nature(t, lab), "disc": disc, "value": abs(v), "custom": r["custom"]})
    if lines or other_capex:
        n_ppe = [x for x in lines if not x["disc"] and x["nature"] in ("ppe", "ppe_with_intangibles")]
        if any(x["nature"] == "ppe_with_intangibles" for x in lines):
            summ["capex_flag_ppe_line_includes_intangibles"] += 1
            per_company[f["ticker"]]["capex_ppe_with_intangibles"] += 1
        n_net = [x for x in lines if not x["disc"] and x["nature"] == "net"]
        leased = [x for x in lines if not x["disc"] and x["nature"] == "leased"]
        soft = [x for x in lines if not x["disc"] and x["nature"] == "software"]
        disc = [x for x in lines if x["disc"] and x["nature"] in ("ppe", "ppe_with_intangibles", "net", "leased", "software")]
        narrow = sum((x["value"] for x in n_ppe), Decimal(0)) if n_ppe else sum((x["value"] for x in n_net), Decimal(0))
        ruling = narrow + sum((x["value"] for x in leased + soft), Decimal(0)) + (sum((x["value"] for x in disc), Decimal(0)) if cfo_total else 0)
        cases = [c for c, on in (("leased", leased), ("software", soft), ("discontinued", disc and cfo_total)) if on]
        unclear = [x for x in lines if x["nature"] == "lease_unclear"]
        net_sibling = bool(n_ppe and n_net) or bool(unclear)
        if not n_ppe and not n_net and not (leased or soft):
            interim, reason = None, ("other_capex_lines_outside_ruling" if other_capex else "no_continuing_capex_line")
        elif net_sibling:
            interim, reason = None, "perimeter_line_unresolved"
        elif cases:
            interim, reason = None, "perimeter_line_unresolved"
        else:
            interim, reason = narrow, None
        pv = prod[(cik, "capex_resolved")].get((end, q))
        c = dict(cell, family="capex", lines=lines, cases=cases, net_sibling=net_sibling, other_capex_lines=other_capex,
                 cfo_perimeter="total" if cfo_total else "continuing",
                 variant_narrow=str(narrow) if not net_sibling and (n_ppe or n_net) else None,
                 variant_ruling=str(ruling) if not net_sibling and (n_ppe or n_net or leased or soft) else None,
                 interim=str(interim) if interim is not None else None, interim_reason=reason,
                 prod_value=str(pv) if pv is not None else None)
        cells.append(c)
        summ["capex_cells"] += 1
        for cs in cases:
            summ[f"capex_case_{cs}"] += 1
            per_company[f["ticker"]][f"capex_{cs}"] += 1
            if len(examples[f"capex_{cs}"]) < 400:
                examples[f"capex_{cs}"].append(c)
        if cases and not net_sibling:
            summ["capex_variants_differ"] += 1
            if pv is not None:
                tol = runit([narrow, ruling]) or 1
                summ["capex_differ_prod_eq_narrow" if abs(pv - narrow) <= tol else ("capex_differ_prod_eq_ruling" if abs(pv - ruling) <= tol else "capex_differ_prod_other")] += 1
            else:
                summ["capex_differ_prod_blank"] += 1
        if net_sibling:
            summ["capex_net_sibling_unresolved"] += 1
            per_company[f["ticker"]]["capex_net_sibling"] += 1
        if reason:
            summ[f"capex_interim_{reason}"] += 1
        elif pv is not None:
            tol = runit([narrow]) or 1
            summ["capex_published_prod_agrees" if abs(pv - narrow) <= tol else "capex_published_prod_differs"] += 1
        else:
            summ["capex_published_prod_blank"] += 1

    # ---------------- D&A ----------------
    if op_i is None:
        continue
    da = []
    label_tags = defaultdict(set)
    for r in rows[:op_i]:
        label_tags[r["plabel"].strip().lower()].add(r["tag"])
    for r in rows[:op_i]:
        t, lab = r["tag"], r["plabel"]
        if not ((DA_TAG.search(t) and not DA_TAG_EXCLUDE.search(t)) or (r["custom"] and re.search(r"depreciation|amorti[sz]ation|depletion", lab, re.I))):
            continue
        if t not in vals:
            continue
        if parents[t] & printed and any(DA_TAG.search(p) for p in parents[t] & printed):
            continue
        v = dec(vals[t])
        if v is None or v == 0:
            continue
        da.append({"tag": t, "label": lab, "nature": da_nature(t, lab, r["custom"], len(label_tags[lab.strip().lower()]) == 1), "value": v, "custom": r["custom"]})
    if not da:
        continue
    asset = [x for x in da if x["nature"] == "asset_da"]
    other = [x for x in da if x["nature"] == "other_amort"]
    combined = [x for x in da if x["nature"] == "combined_other"]
    is_amort = [dec(vals.get(r["tag"])) for r in is_rows if (r["tag"] == "AmortizationOfIntangibleAssets" or IS_INTANGIBLE_AMORT.search(r["plabel"])) and r["tag"] in vals]
    is_amort = [x for x in is_amort if x is not None]
    is_sum = sum(is_amort, Decimal(0)) if is_amort else None
    narrow_da = sum((x["value"] for x in asset), Decimal(0))
    other_sum = sum((x["value"] for x in other), Decimal(0))
    tie = None
    if other:
        tol = runit([other_sum] + is_amort) if is_amort else None
        tie = is_sum is not None and abs(other_sum - is_sum) <= tol
    if combined and not asset:
        value, reason = None, "da_combined_with_other_items"
    elif combined:
        value, reason = None, "da_combined_with_other_items"
    elif other and not tie:
        value, reason = None, "perimeter_line_unresolved"
    elif not asset and not other:
        value, reason = None, "no_da_line"
    else:
        value, reason = narrow_da + (other_sum if other else 0), None
    pv = prod[(cik, "depreciation_and_amortization_resolved")].get((end, q))
    c = dict(cell, family="d_and_a", lines=[{**x, "value": str(x["value"])} for x in da], is_intangible_amort=str(is_sum) if is_sum is not None else None,
             tie_2a=tie, value=str(value) if value is not None else None, reason=reason, narrow_asset_da=str(narrow_da),
             prod_value=str(pv) if pv is not None else None)
    cells.append(c)
    summ["da_cells"] += 1
    key = reason or ("published_2a_tie" if other else "published")
    summ[f"da_{key}"] += 1
    per_company[f["ticker"]][f"da_{key}"] += 1
    if len(examples[f"da_{key}"]) < 400:
        examples[f"da_{key}"].append(c)
    if value is not None:
        if pv is None:
            summ["da_published_prod_blank"] += 1
        else:
            tol = runit([value]) or 1
            summ["da_published_prod_agrees" if abs(pv - value) <= tol else "da_published_prod_differs"] += 1
    elif pv is not None:
        summ["da_hidden_prod_shows_value"] += 1

with gzip.open(out_dir / "cells.jsonl.gz", "wt") as fo:
    for c in cells:
        fo.write(json.dumps(c, default=str) + "\n")
json.dump({"summary": dict(sorted(summ.items())),
           "companies": {k: dict(v) for k, v in sorted(per_company.items())},
           "companies_with_case": {k: sum(1 for v in per_company.values() if v.get(k)) for k in
                                   ("capex_leased", "capex_software", "capex_discontinued", "capex_net_sibling",
                                    "da_published_2a_tie", "da_perimeter_line_unresolved", "da_da_combined_with_other_items")}},
          open(out_dir / "summary.json", "w"), indent=1, default=str)
with gzip.open(out_dir / "examples.json.gz", "wt") as fo:
    json.dump(examples, fo, default=str)
print(json.dumps(dict(sorted(summ.items())), indent=1))
