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
CAPEX_OTHER = re.compile(r"RealEstate|DevelopRealEstate", re.I)
CAPEX_OG = re.compile(r"OilAndGas|ExploreAndDevelop|DrillingAndCompletion|UnprovedProperties|ProvedProperties", re.I)
CAPEX_OG_LABEL = re.compile(r"drilling|completion|(un)?proved (oil|gas|properties|leasehold)|additions to (oil|gas|proved|unproved)|"
                            r"development (costs|expenditures)|exploration and development|oil and (natural )?gas propert", re.I)


def capex_nature(tag, label):
    if re.search(r"property|plant|equipment|premises", label, re.I) and re.search(r"(and|&) other (long.term |non.?current )?assets", label, re.I):
        return "lease_unclear"  # Verifier fills R2 (JEF): PP&E mixed with other assets cannot be split on the face
    if tag == "PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets" or (
            re.search(r"PropertyPlantAndEquipment|ProductiveAssets", tag) and re.search(r"intangible", label, re.I)
            and re.search(r"property|plant|equipment", label, re.I)):
        # NVDA "Purchases of property and equipment and intangible assets" on the PP&E element
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
    if "EquipmentOnLease" in tag or re.search(r"leased to others|equipment on (operating )?lease|(?<!non-)(?<!non )rental (equipment|fleet)|held for rental|(assets|equipment) (under|on) operating leases?|lease fleet", label, re.I):
        return "leased"
    if re.search(r"software", label, re.I) and re.search(r"PropertyPlantAndEquipment|ProductiveAssets", tag) \
            and re.search(r"property|plant|premises|equipment|capital expenditure|building", label, re.I):
        return "ppe"  # ONE printed line covering PP&E and software: the filer's own total, same in both variants
    if "Software" in tag or re.search(r"software|information technology applications?|\bIT applications?", label, re.I):
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
    r"AboveAndBelowMarketLease|LeaseIncentive|DeferredHedge|InventoryStepUp|DefinedBenefit")
# generic elements a filer also uses for intangible amortization (COHR, RRX label the
# deferred-charges element plain "Amortization"): the label decides, else tie-out or hold
SOFT_TAG = re.compile(r"^(Other)?AmortizationOfDeferredCharges$|^AdjustmentForAmortization$")
MIXED_TAG = re.compile(r"AndImpairment|ImpairmentOf.*Intangible|IntangibleAssetsAnd.*Premium")
# DepreciationAmortizationAndAccretionNet is also used for a plain "Depreciation and amortization"
# line (SUI): accretion is decided by the LABEL, never by that element alone
ASSET_DA_TAG = re.compile(
    r"DepreciationDepletionAndAmortization|DepreciationAmortizationAndAccretionNet|"
    r"DepreciationAndAmortization$|^Depreciation$|DepreciationNonproduction|"
    r"AmortizationOfIntangibleAssets|CapitalizedComputerSoftwareAmortization|DepreciationAmortizationAndOther$")
IS_INTANGIBLE_AMORT = re.compile(r"amorti[sz]ation of (acquisition.related |acquired |purchased |other )?(intangible|developed technology|technology)", re.I)


def da_nature(tag, label, custom, label_ok=True):
    # an element named "...Excluding<X>" names what it leaves OUT: X never excludes the line
    # (LSCC DepreciationDepletionAndAmortizationExcludingRightOfUseAssetAndFinanceCosts = D&A)
    tag = re.sub(r"Excluding.*$", "", tag)
    if re.search(r"operating\w*finance|finance\w*operating|operating and finance|finance and operating", tag + " " + label, re.I):
        return "combined_other"  # OperatingAndFinanceLeaseRightOfUseAssetAmortization mixes operating-lease ROU in
    if re.search(r"finance", label, re.I) and re.search(r"lease|right.of.use", label, re.I) and not re.search(r"operating", label, re.I):
        # Verifier V10 (GD Q1 2024 211M): finance-lease ROU assets are depreciated like owned
        # assets, so "amortization of intangible and finance lease ROU assets" is D&A
        return "asset_da"
    if re.search(r"^amorti[sz]ation\s*\(includ", label, re.I):
        return "combined_other"  # IRM: netted against its tagged parenthetical financing part below
    if re.search(r"premium|discount|securit|investment|debt|loan|notes?\b|issuance|financing", label, re.I) and not re.search(
            r"depreciation|depletion|intangible|software", label, re.I):
        return "excluded"  # Verifier V14 (RVMD, PTGX): securities/debt accretion is an excluded item, not a combined D&A line
    if re.search(r"accretion", label, re.I) and re.search(r"depreciation|amorti[sz]ation", label, re.I):
        return "combined_other"  # Verifier V11 (EVR): any case or word order of "... and accretion"
    if not label_ok:
        # FSN pre gave this line the label of another printed line (AMD FY2024:
        # AdjustmentForAmortization shown as "Amortization", plabel = the ROU line's):
        # the label is no evidence; the tag decides, a generic line ties out or holds
        label = ""
    if re.search(r"lease\b.*incentive|incentive.*\blease", label, re.I) or (
            re.search(r"depreciation", label, re.I)
            and re.search(r"(equipment|assets?|property) (on|under|subject to|held for) (operating )?leas|leased to others|leased assets|rental (equipment|fleet)|lease fleet", label, re.I)):
        return "definition_question"  # Verifier: PCAR lessor-equipment depreciation, FTAI lease incentives
    if re.search(r"(above|below)\W{0,3}(\(?(above|below)\)?\W{0,3})?market|market lease|(un)?favou?rable lease", label, re.I):
        return "excluded"  # Verifier V11 (VNO): below-market lease amortization is revenue
    if re.search(r"lease intangible|in.place lease|lease.related intangible|rent.related intangible|ground.lease intangible", label, re.I):
        return "lease_intangible"  # sign decides: printed negative = below-market revenue offset (TRNO)
    if re.search(r"^amorti[sz]ation\s*\(includ", label, re.I):
        return "combined_other"  # IRM: before the exclusions, so the parenthetical netting can run
    if re.search(r"equity (method )?investment|equity.method|excess cost of", label, re.I):
        return "excluded"  # equity-method basis-difference amortization (KMI) is not D&A
    asset_word = re.search(r"depreciation|depletion|intangible|software", label, re.I)
    if MIXED_TAG.search(tag) or (asset_word and re.search(r"accretion|impairment", label, re.I)):
        return "combined_other"  # TTWO amortization-and-impairment, bank/landfill "... and accretion, net"
    lab_wo_excl = re.sub(r"exclud\w*[^,;)]*", "", label, flags=re.I)
    if SOFT_TAG.search(tag):
        if DA_EXCLUDED_LABEL.search(lab_wo_excl) and not asset_word:
            return "excluded"
        return "asset_da" if asset_word and not DA_EXCLUDED_LABEL.search(lab_wo_excl) else (
            "combined_other" if asset_word else "other_amort")
    if asset_word and DA_EXCLUDED_LABEL.search(lab_wo_excl) and not DA_EXCLUDED_TAG.search(tag):
        # one printed line mixing an asset with an excluded item (WPC "... including deferred
        # financing costs", CTAS "intangible assets and capitalized contract costs"): it cannot
        # be split on the face, so it holds like the 2b combined line
        return "combined_other"
    if DA_EXCLUDED_TAG.search(tag) or DA_EXCLUDED_LABEL.search(label):
        return "excluded"
    if re.search(r"^amorti[sz]ation\s*\(includ", label, re.I):
        return "combined_other"  # IRM "Amortization (includes amortization of deferred financing ...)"
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
    skipped = []  # lines read and deliberately NOT summed (proceeds/sale, accrual change): Verifier strata
    og_acq = []  # oil and gas property acquisition lines: perimeter question, the cell holds
    maint = []  # capitalized turnaround / major-maintenance lines: definition question, the cell holds
    other_capex = 0
    if op_i is not None and inv_i is not None and inv_i > op_i:
        block = rows[op_i + 1:inv_i + 1]
        for k, r in enumerate(block, start=op_i + 1):
            t, lab = r["tag"], r["plabel"]
            if CAPEX_OTHER.search(t):
                other_capex += 1 if t in vals and dec(vals[t]) else 0
                continue
            if re.search(r"^\s*(proceeds|sales?\b|disposals?\b)|\(purchases?\)\s*sales?|\bsales? (of|and purchases)|proceeds from (the )?(sale|disposal)|divest", lab, re.I) \
                    and not re.match(r"\s*payments? for \(proceeds", lab, re.I):
                # Verifier V11 (AXS "Proceeds from the (purchase) sale of other assets, net"); also BURL/LGND
                # sale proceeds and MCD "Sales and purchases of restaurant businesses". A payments line
                # "net of disposals" (ACM, RKT) and the "Payments for (Proceeds from)" element (AMD) stay.
                if t in vals and dec(vals[t]):
                    skipped.append({"tag": t, "label": lab, "value": str(dec(vals[t])), "why": "proceeds_or_sale"})
                continue
            if re.search(r"change in|accrued|accrual|increase|decrease", lab, re.I) and not CAPEX_TAG.search(t):
                if t in vals and dec(vals[t]) and re.search(r"capital|property|equipment", lab, re.I):
                    skipped.append({"tag": t, "label": lab, "value": str(dec(vals[t])), "why": "accrual_change"})
                continue  # CHTR "Change in accrued expenses related to capital expenditures"
            if (CAPEX_OG.search(t) or CAPEX_OG_LABEL.search(lab) or re.search(r"property acquisitions|acquisitions? of (oil|gas|proved|unproved|mineral|leasehold)", lab, re.I)) \
                    and not re.search(r"proceeds|sale|disposal|divest|software|site", lab + t, re.I):
                v = dec(vals.get(t))
                if v and re.search(r"acquisition|acquire", lab, re.I):
                    og_acq.append({"tag": t, "label": lab, "value": str(v)})
                    continue  # Verifier fills R2 (FANG "Property acquisitions" 1,193M): founder perimeter question, held
                if v:
                    lines.append({"tag": t, "label": lab, "nature": "ppe", "disc": False, "value": abs(v), "raw": v, "negating": r["negating"], "custom": r["custom"], "og": True})
                continue
            if re.match(r"\s*(additions? (to|of)|capital expenditures? (for|on)|expenditures? (for|on)|payments? for (vessels|aircraft|rigs|towers|ships))\b", lab, re.I) and not re.search(
                    r"real estate|rental propert|investment|loan|securit|intangible|business|software|acquisition|receivable|financ|note|"
                    r"debt|restricted|other (long.term |non.?current )?assets|deposit|escrow|contract", lab, re.I) and t in vals \
                    and not (parents[t] & printed - set(INV_TOTAL)) \
                    and not (re.search(r"held for sale", lab, re.I) and not re.search(r"property|plant|equipment", lab, re.I)):
                # KNX "Expenditures on assets held for sale" is not PP&E; INTC "Additions to held for sale NAND
                # property, plant, and equipment" names PP&E and stays (Verifier-confirmed)
                v = dec(vals[t])
                if v and re.search(r"turnaround|major (repairs|maintenance)|catalyst|dry.?dock", lab, re.I):
                    maint.append({"tag": t, "label": lab, "value": str(v)})
                    continue  # capitalized major maintenance (PBF turnaround 379.1M): definition question, held
                if v and re.search(r"asset purchase|acquisition", lab, re.I):
                    continue  # PBF "Expenditure for PBFX Plains Asset Purchase": an acquisition, not capex
                if v:
                    # nature from the same classifier (OSK "Additions to equipment held for rental" stays leased)
                    lines.append({"tag": t, "label": lab, "nature": capex_nature(t, lab), "disc": bool(re.search(r"discontinued", lab, re.I)),
                                  "value": abs(v), "raw": v, "negating": r["negating"], "custom": r["custom"], "additions_line": True})
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
            lines.append({"tag": t, "label": lab, "nature": capex_nature(t, lab), "disc": disc, "value": abs(v), "raw": v, "negating": r["negating"], "custom": r["custom"]})
        # DIRECTION AS PRINTED (Verifier R1, BWA/ON/AXS): a member counts only if it is a cash OUTFLOW
        # in the filer's own investing section. Printed signs (FSN negating) are trusted only where
        # that section adds up to the filer's investing total with them (93% of filings); if exactly
        # one member's flipped sign makes it add up, that member was mis-printed (INTC NAND: the R
        # page dropped the parentheses); otherwise a standard Payments... element's positive value
        # is an outflow by its definition and any other member's direction is unresolved (hold).
        sec = [r for r in block if r["tag"] in vals and dec(vals[r["tag"]]) and not re.search(r"CashProvidedByUsedIn|Abstract", r["tag"])]
        pres = {}
        for r in sec:
            v = dec(vals[r["tag"]])
            pres.setdefault(r["tag"], -v if r["negating"] else v)
        tot = dec(vals.get("NetCashProvidedByUsedInInvestingActivities") or vals.get("NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"))
        sign_basis = None
        if tot is not None and pres:
            S = sum(pres.values(), Decimal(0))
            tol = runit([tot])
            if abs(S - tot) <= tol:
                sign_basis = "printed"
            else:
                flips = [x["tag"] for x in lines if x["tag"] in pres and abs(S - 2 * pres[x["tag"]] - tot) <= tol]
                if len(set(flips)) == 1:
                    pres[flips[0]] = -pres[flips[0]]
                    sign_basis = "printed_one_member_corrected"
        kept = []
        sign_unresolved = False
        for x in lines:
            if sign_basis and x["tag"] in pres:
                outflow = pres[x["tag"]] < 0
                x["value"] = -pres[x["tag"]] if outflow else pres[x["tag"]]
            elif x["tag"].startswith("Payments"):
                outflow = x["raw"] > 0
            else:
                outflow, sign_unresolved = None, True
            x["direction"] = {True: "outflow", False: "inflow", None: "unresolved"}[outflow]
            if outflow is False:
                skipped.append({"tag": x["tag"], "label": x["label"], "value": str(x["raw"]), "why": "inflow_as_printed"})
                continue
            kept.append(x)
        lines = kept
        for x in lines:
            x["raw"] = str(x["raw"])
    if lines or other_capex or og_acq or maint:
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
        if sign_unresolved:
            interim, reason = None, "capex_sign_unresolved"
        elif og_acq:
            interim, reason = None, "perimeter_og_property_acquisitions"
        elif maint:
            interim, reason = None, "perimeter_turnaround_major_maintenance"
        elif other_capex:
            interim, reason = None, "other_capex_lines_outside_ruling"  # MTDR: oil and gas lines beside midstream capex
        elif net_sibling:
            interim, reason = None, "perimeter_line_unresolved"  # before no-line: JEF's mixed line is the reason
        elif not n_ppe and not n_net and not (leased or soft):
            interim, reason = None, ("other_capex_lines_outside_ruling" if other_capex else "no_continuing_capex_line")
        elif cases:
            interim, reason = None, "perimeter_line_unresolved"
        else:
            interim, reason = narrow, None
        pv = prod[(cik, "capex_resolved")].get((end, q))
        c = dict(cell, family="capex", lines=lines, skipped_lines=skipped, og_property_acquisitions=og_acq, maintenance_lines=maint, sign_basis=sign_basis, cases=cases, net_sibling=net_sibling, other_capex_lines=other_capex,
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
            tol = max(runit([narrow]), runit([pv]))
            summ["capex_published_prod_agrees" if abs(pv - narrow) <= tol else "capex_published_prod_differs"] += 1
        else:
            summ["capex_published_prod_blank"] += 1

    # ---------------- D&A ----------------
    if op_i is None:
        continue
    da = []
    seen_da = set()
    label_tags = defaultdict(set)
    for r in rows[:op_i]:
        label_tags[r["plabel"].strip().lower()].add(r["tag"])
    for r in rows[:op_i]:
        t, lab = r["tag"], r["plabel"]
        # candidate by element, or by the printed label of an operating-adjustment line whatever its
        # element (Verifier V13: OLLI tags its D&A line with the accumulated-depreciation roll-forward element)
        if not ((DA_TAG.search(t) and not DA_TAG_EXCLUDE.search(t))
                or (r["custom"] and re.search(r"depreciation|amorti[sz]ation|depletion", lab, re.I))
                or re.match(r"\s*(depreciation|amorti[sz]ation|depletion)", lab, re.I)):
            continue
        if t not in vals or t in seen_da:
            continue  # a fact printed on two face rows counts once (Verifier: ANF FY2020)
        if parents[t] & printed and any(DA_TAG.search(p) for p in parents[t] & printed):
            continue
        v = dec(vals[t])
        if v is None or v == 0:
            continue
        seen_da.add(t)
        v = -v if r["negating"] else v  # the sign as presented (Verifier: TRNO)
        nat = da_nature(t, lab, r["custom"], len(label_tags[lab.strip().lower()]) == 1)
        if nat == "lease_intangible":
            nat = "excluded" if v < 0 else "asset_da"
        if nat == "combined_other" and re.search(r"includ\w*[^)]*(financing|debt|discount)", lab, re.I):
            # IRM: "Amortization (includes deferred financing costs of $X)": D&A = line - the
            # financing part, when the filer tagged that part for the same column (parenthetical)
            fin = [dec(vals[x["tag"]]) for x in f["face"] if x["stmt"] == "CF" and x["inpth"]
                   and re.search(r"FinancingCost|DebtIssuance|DebtDiscount", x["tag"]) and x["tag"] in vals]
            fin = [x for x in fin if x]
            if len(fin) == 1 and 0 < fin[0] < abs(v):
                v, nat = v - fin[0], "asset_da"
                lab = lab + f" [net of parenthetical financing {fin[0]}]"
        da.append({"tag": t, "label": lab, "nature": nat, "value": v, "custom": r["custom"]})
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
    # the income statement's printed D&A total, same column (Verifier: OMC 333.2M)
    is_da = [dec(vals.get(r["tag"])) for r in is_rows if r["tag"] in vals
             and not re.search(r"accretion|impairment|and other\b(?! amorti)", r["plabel"], re.I) and (
        r["tag"] in ("DepreciationAndAmortization", "DepreciationDepletionAndAmortization")
        or (re.match(r"depreciation,? (depletion,? )?(and )?(other )?amorti[sz]ation", r["plabel"].strip(), re.I)
            and not re.search(r"accretion|impairment|and other\b(?! amorti)", r["plabel"], re.I)))]
    is_da = [x for x in is_da if x]
    is_da_total = is_da[0] if len(set(is_da)) == 1 else None
    tie = None
    if other:
        tol = runit([other_sum] + is_amort) if is_amort else None
        tie = is_sum is not None and abs(other_sum - is_sum) <= tol
    defq = [x for x in da if x["nature"] == "definition_question"]
    label_only = [x for x in da if x["nature"] in ("excluded", "combined_other") and x["value"] > 0
                  and not re.search(r"market|lease (incentive|intangible)|favou?rable|revenue|accretion|financing|debt|discount|premium|"
                                    r"issuance|contract|advance|commission|content|film|stock|compensation|impairment|securit|investment|loan|"
                                    r"deferred|pension|benefit|hedg|derivative|step.up|interest|equity", x["label"], re.I)]
    has_dep = any(re.search(r"depreciation|depletion", x["label"] + x["tag"], re.I) for x in asset)
    is_tie = None
    if is_da_total is not None and not defq:
        base = narrow_da + (other_sum if other and tie else 0)
        with_lo = base + sum((x["value"] for x in label_only), Decimal(0))
        # tolerance = the coarser printed unit of the two NONZERO numbers compared (Verifier
        # V11: runit(0) is the 1M cap, which let EVR and VNO "tie" within a million)
        if base and abs(base - is_da_total) <= max(runit([is_da_total]), runit([base])):
            is_tie = "asset_lines"
        elif other and not tie and abs(base + other_sum - is_da_total) <= max(runit([is_da_total]), runit([base + other_sum])):
            is_tie = "asset_and_generic_amortization"  # Verifier V14 (LYV): the IS D&A equals both lines
            for x in other:
                x["nature"] = "asset_da"
            asset = [x for x in da if x["nature"] == "asset_da"]
            narrow_da = sum((x["value"] for x in asset), Decimal(0))
            other, other_sum, tie = [], Decimal(0), None
        elif label_only:
            # an exact tie of the asset lines plus a subset (<= 3) of label-clean dropped lines to the
            # IS printed D&A (OMC ROU-labelled depreciation; LYV generic "Amortization" on an
            # impairment-named element: 225,770 + 224,206 = 449,976)
            from itertools import combinations
            hit = None
            for n in range(1, min(3, len(label_only)) + 1):
                for combo in combinations(label_only, n):
                    sm = base + sum((x["value"] for x in combo), Decimal(0))
                    if abs(sm - is_da_total) <= max(runit([is_da_total]), runit([sm])):
                        hit = combo
                        break
                if hit:
                    break
            if hit:
                is_tie = "with_label_excluded_lines"
                for x in hit:
                    x["nature"] = "asset_da"
                asset = [x for x in da if x["nature"] == "asset_da"]
                combined = [x for x in da if x["nature"] == "combined_other"]
                narrow_da = sum((x["value"] for x in asset), Decimal(0))
                has_dep = True
    net_low = [x for x in asset if re.search(r"\bnet\b", x["label"], re.I) and is_sum is not None and x["value"] < is_sum]
    if defq:
        value, reason = None, "da_definition_question"
    elif net_low:
        # Verifier V10 (KEY FY2021): a "D&A expense, net" line below the same filing's own
        # intangible amortization is netted with something else; never published as D&A
        value, reason = None, "da_net_line_below_intangible_amortization"
    elif combined:
        value, reason = None, "da_combined_with_other_items"
    elif asset and not has_dep and not is_tie:
        value, reason = None, "no_depreciation_line_on_cf"  # never publish a partial (Verifier: OMC)
    elif other and not tie:
        value, reason = None, "perimeter_line_unresolved"
    elif not asset and not other:
        value, reason = None, "no_da_line"
    else:
        value, reason = narrow_da + (other_sum if other else 0), None
    # INCOME-STATEMENT ANCHOR (Verifier R1: FR, WPC, RSG): when the IS prints a D&A line and the
    # cash-flow composition is held or partial (a non-debt, non-lease amortization line was dropped),
    # the IS line is the value. A complete CF composition stays even where the IS differs (ECHO, DDS).
    dropped = [x for x in da if x["nature"] == "excluded" and not DA_EXCLUDED_TAG.search(x["tag"]) and not re.search(
        r"debt|financ|discount|premium|market|lease|contract|deferred|commission|content|film|right.of.use|revenue|interest|hedg|derivative|step.up|pension|benefit|loan|equity", x["label"], re.I)]
    if is_da_total is not None and is_tie is None and not defq and not net_low and (
            reason in ("da_combined_with_other_items", "perimeter_line_unresolved", "no_depreciation_line_on_cf")
            or (reason is None and dropped and value != is_da_total)):
        value, reason, is_tie = is_da_total, None, "is_anchor"
    # release class (Dhairya 2026-11-02: release 1 = only classes that passed every Verifier round)
    hard_dropped = lambda x: DA_EXCLUDED_TAG.search(x["tag"]) or re.search(  # noqa: E731
        r"debt|financ|discount|premium|issuance|securit|investment|loan|notes?\b", x["label"], re.I)
    n_members = len([x for x in da if x["nature"] == "asset_da"])
    soft_dropped = [x for x in da if x["nature"] != "asset_da" and not hard_dropped(x)]
    if value is None:
        da_class = None
    elif is_tie == "is_anchor":
        da_class = "is_anchor"
    elif n_members == 1 and is_tie:
        da_class = "single_line_ties_is"
    elif n_members == 1 and is_da_total is None and not soft_dropped:
        da_class = "single_line_clean"
    elif is_tie:
        da_class = "multi_member_ties_is"
    else:
        da_class = "multi_member"
    pv = prod[(cik, "depreciation_and_amortization_resolved")].get((end, q))
    c = dict(cell, family="d_and_a", da_class=da_class, lines=[{**x, "value": str(x["value"])} for x in da], is_intangible_amort=str(is_sum) if is_sum is not None else None,
             tie_2a=tie, is_da_tie=is_tie, is_da_total=str(is_da_total) if is_da_total is not None else None, value=str(value) if value is not None else None, reason=reason, narrow_asset_da=str(narrow_da),
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
            tol = max(runit([value]), runit([pv]))
            summ["da_published_prod_agrees" if abs(pv - value) <= tol else "da_published_prod_differs"] += 1
    elif pv is not None:
        summ["da_hidden_prod_shows_value"] += 1

# company rule (Verifier V11, KEY FY2023): once a company's "net" D&A line is shown below its
# own intangible amortization in any period, that label is held in EVERY period of the company
net_labels = defaultdict(set)
for c in cells:
    if c["family"] == "d_and_a" and c["reason"] == "da_net_line_below_intangible_amortization":
        for x in c["lines"]:
            if x["nature"] == "asset_da" and re.search(r"\bnet\b", x["label"], re.I):
                net_labels[c["cik"]].add(x["label"].strip().lower())
for c in cells:
    if c["family"] == "d_and_a" and c["reason"] is None and net_labels.get(c["cik"]) and any(
            x["nature"] == "asset_da" and x["label"].strip().lower() in net_labels[c["cik"]] for x in c["lines"]):
        c["value"], c["reason"], c["da_class"] = None, "da_net_line_below_intangible_amortization", None
        c["company_rule"] = "net_line_failed_in_another_period"
# D&A counters recomputed from the final cells (the company rule changes cells after the pass)
for k in [k for k in summ if k.startswith("da_")]:
    del summ[k]
for t in per_company:
    for k in [k for k in per_company[t] if k.startswith("da_")]:
        del per_company[t][k]
for c in cells:
    if c["family"] != "d_and_a":
        continue
    v = Decimal(c["value"]) if c["value"] is not None else None
    pv = Decimal(c["prod_value"]) if c["prod_value"] is not None else None
    key = c["reason"] or ("published_is_anchor" if c.get("is_da_tie") == "is_anchor"
                          else "published_2a_tie" if c.get("tie_2a") else "published")
    summ["da_cells"] += 1
    summ[f"da_{key}"] += 1
    per_company[c["ticker"]][f"da_{key}"] += 1
    if v is not None:
        if pv is None:
            summ["da_published_prod_blank"] += 1
        else:
            summ["da_published_prod_agrees" if abs(pv - v) <= max(runit([v]), runit([pv])) else "da_published_prod_differs"] += 1
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
