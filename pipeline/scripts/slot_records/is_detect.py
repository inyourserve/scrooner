"""Income-statement slot detection (stdlib, run with -I): revenue, operating
income and net income attributable to the parent, per filing, from the
filing's own statement layout (FSN pre face rows + calc arcs written by
fsn_is_pre.py). No values; replay comes later (is_replay.py).

Per filing the PRIMARY statement is the lowest-numbered IS report (else the
lowest CI report carrying a net-income line); rows are sorted by line (FSN
pre is not in statement order). Then one slot per family:

  revenue      the single printed revenue TOTAL: a face line under a
               standard total tag (REV_TOTAL) that no other face revenue line
               totals (calc descendant check over the filing's arcs). Holds:
               bank / insurer / BDC shapes (definition is the Standardization
               Lead's: NII + noninterest income, total revenues incl. gains),
               a total whose label or calc children carry other income or
               gains (XOM 'revenues and other income'), a standard total
               that is itself a child of a custom total (COP), two roots,
               a custom total (no companyfacts value).
  operating    the printed OperatingIncomeLoss line, only above the pretax
               and tax lines and never labelled 'before tax' (PEBO tags
               pretax income with it); bank shapes hold (BANR tags
               noninterest income with it). A custom operating line holds.
  net_income   the printed NetIncomeLoss line (first one: PGR repeats it in
               an EPS block), below the tax line, not labelled as the
               noncontrolling share. Else ProfitLoss when the face carries
               no noncontrolling-interest line (then ProfitLoss is the
               parent's). When ProfitLoss, the NCI line(s) and NetIncomeLoss
               are all printed, the replay checks PL - NCI = NI (G2).

Era = consecutive filings (by filed date) with the same (gate, tag, label
class); written in the slot-record shape assemble_family.py uses.
usage: is_detect.py <is_fsn_dir> <out_dir> [coregistrant_adsh.txt]
  writes <out_dir>/is_filing_slots.jsonl and is_<family>_records.jsonl
"""
import glob
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REV_TOTAL = {
    "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet",
    "SalesRevenueGoodsNet", "SalesRevenueServicesNet", "RegulatedAndUnregulatedOperatingRevenue",
    "RevenuesNetOfInterestExpense",
}
REV_ANY = re.compile(r"Revenue|^Sales")
SIB_TAG_NOT = re.compile(r"Cost|Expense|Deferred|Unearned|Receivable|GainLoss|PerShare|Percent|Tax|Remaining|Allowance|Reserve")
STRUCTURAL_ROW = re.compile(r"(Abstract|Member|Axis|Domain|Table|LineItems|ExtensibleList|ExtensibleEnumeration)$")
SIB_LABEL = re.compile(r"\brevenues?\b|\bsales\b", re.I)
SIB_LABEL_NOT = re.compile(r"cost|expense|marketing|commission|tax|deferred|unearned|per share|%|percent", re.I)
OTHER_INCOME_TAG = re.compile(r"IncomeLossFromEquityMethod|NonoperatingIncome|OtherIncome|InvestmentIncome|GainLoss|GainsLosses")
OTHER_INCOME_LABEL = re.compile(r"\bincome\b|\bgains?\b", re.I)
BANK = {"InterestIncomeExpenseNet", "NoninterestExpense", "NoninterestIncome", "InterestIncomeExpenseAfterProvisionForLoanLoss"}
INSURER_RX = re.compile(r"^PremiumsEarnedNet|^BenefitsLossesAndExpenses$|^PolicyholderBenefitsAndClaimsIncurredNet$")
BDC = {"GrossInvestmentIncomeOperating", "NetInvestmentIncome", "InvestmentIncomeOperatingAfterExpenseAndTax"}
PRETAX_RX = re.compile(r"^IncomeLossFromContinuingOperationsBeforeIncomeTaxes")
TAX = "IncomeTaxExpenseBenefit"
NCI_RX = re.compile(r"^(NetIncomeLossAttributableTo(Redeemable|Nonredeemable)?NoncontrollingInterest|MinorityInterestInNetIncomeLoss\w*|IncomeLossFromContinuingOperationsAttributableToNoncontrollingEntity|IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToNoncontrollingInterest|NetIncomeLossAttributableToNoncontrollingInterestAndRedeemableNoncontrollingInterest)$")
NCI_CUSTOM_RX = re.compile(r"NoncontrollingInterest|MinorityInterest")
SUBSIDIARY_LABEL = re.compile(r"subsidiar", re.I)
REV_PARENT_RX = re.compile(r"Revenue|Sales")
NOT_REV_PARENT_RX = re.compile(r"Cost|Expense|Profit|Margin|OperatingIncome|IncomeLoss")
NCI_LABEL = re.compile(r"non-?controlling|minority", re.I)
NCI_LABEL_OK = re.compile(r"\bless\b|exclud|net of|attributable to (?!non-?controlling|minority)", re.I)
BEFORE_TAX_LABEL = re.compile(r"before (income )?tax|pre-?tax", re.I)
OP_LABEL = re.compile(r"operating (income|profit|loss|earnings)|income from operations|(earnings|profit) from operations", re.I)


def iso(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if d and len(d) == 8 and d.isdigit() else d


def descendants(arcs, tag):
    """every tag reachable below `tag` in the filing's calc arcs."""
    seen, stack = set(), [tag]
    while stack:
        for c in arcs.get(stack.pop(), ()):
            if c not in seen:
                seen.add(c)
                stack.append(c)
    return seen


def parents_of(arcs, tag):
    return {p for p, kids in arcs.items() if tag in kids}


EPS_TAGS = {"EarningsPerShareBasic", "EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted",
            "IncomeLossFromContinuingOperationsPerBasicShare"}


def primary_face(rows, coregistrant=False):
    is_reports = sorted({r["report"] for r in rows if r["stmt"] == "IS"})
    if is_reports and coregistrant:
        # a combined filing (FSN sub.aciks non-empty: ETR, SO, ES, ...) prints one income
        # statement per registrant; the parent's is the one with earnings per share
        # (wholly-owned subsidiaries report none). Release closure 2026-10-31: the
        # lowest report was a subsidiary's for ETR 2023 (ProfitLoss 2,362.3M = consolidated)
        with_eps = [rep for rep in is_reports if any(r["report"] == rep and r["tag"] in EPS_TAGS for r in rows)]
        rep = with_eps[0] if with_eps else is_reports[0]
    elif is_reports:
        rep = is_reports[0]
    else:
        ci = sorted({r["report"] for r in rows if r["stmt"] == "CI" and r["tag"] in ("NetIncomeLoss", "ProfitLoss")})
        if not ci:
            return None, []
        rep = ci[0]
    face = sorted((r for r in rows if r["report"] == rep), key=lambda r: r["line"])
    return rep, face


def shape_of(tags):
    # a bank face: noninterest expense with noninterest income or net interest income,
    # or interest income after the provision. InterestIncomeExpenseNet ALONE is not a
    # bank: 158 commercial cohort companies tag "Interest expense, net" with it and
    # print gross profit (found building the gross-profit family, 2026-10-31)
    if "InterestIncomeExpenseAfterProvisionForLoanLoss" in tags or (
            "NoninterestExpense" in tags and tags & {"NoninterestIncome", "InterestIncomeExpenseNet"}):
        return "bank"
    if any(INSURER_RX.search(t) for t in tags):
        return "insurer"
    if tags & BDC:
        return "bdc"
    return "commercial"


def first(face, pred):
    return next(((i, r) for i, r in enumerate(face) if pred(r)), (None, None))


def revenue_siblings(face, arcs, root):
    """Other top-level revenue lines printed on the face (Verifier IS r1, Snap-on
    Q1 2016: 'Net sales' 834.2M with 'Financial services revenue' 66.3M below it
    and no total line): a standard or custom revenue line that is not the root,
    not totalled by it and not above it in the calc tree."""
    below = descendants(arcs, root)
    above = {p for p in arcs if root in descendants(arcs, p)}
    out, seen = [], set()
    for r in face:
        t = r["tag"]
        if t == root or t in below or t in above or t in seen or STRUCTURAL_ROW.search(t) or "[Member]" in r["label"] \
                or "[Axis]" in r["label"] or "[Domain]" in r["label"]:
            continue
        if r["custom"]:
            ok = SIB_LABEL.search(r["label"]) and not SIB_LABEL_NOT.search(r["label"])
        else:
            ok = REV_ANY.search(t) and not SIB_TAG_NOT.search(t)
        if ok:
            seen.add(t)
            out.append(r)
    return out


def calc_parent_of_exactly(full_arcs, members):
    """A calc parent (printed or not) whose children are exactly `members`, all
    weight +1: the filer's own statement that these lines add to its revenue."""
    want = set(members)
    for p, kids in full_arcs.items():
        if set(kids) == want and all(float(w) == 1.0 for w in kids.values()):
            return p
    return None


def revenue_slot(face, arcs, shape, face_tags, full_arcs=None):
    tlines = [(i, r) for i, r in enumerate(face) if r["tag"] in REV_TOTAL and not r["custom"]]
    seen, uniq = set(), []
    for i, r in tlines:
        if r["tag"] not in seen:
            seen.add(r["tag"])
            uniq.append((i, r))
    if shape != "commercial":
        tag = uniq[0][1]["tag"] if uniq else None
        return {"gate": f"hold_sector_{shape}", "tag": tag}
    if not uniq:
        _, cr = first(face, lambda r: r["custom"] and REV_ANY.search(r["tag"]) and not re.search(r"Cost|Expense", r["tag"]))
        if cr is not None:
            return {"gate": "hold_custom_total", "tag": cr["tag"], "label": cr["label"]}
        return {"gate": "no_printed_revenue_total", "tag": None}
    under = {r["tag"] for _, r in uniq for _, s in uniq if r["tag"] in descendants(arcs, s["tag"]) and r["tag"] != s["tag"]}
    roots = [(i, r) for i, r in uniq if r["tag"] not in under]
    if len(roots) != 1:
        return {"gate": "hold_multiple_roots", "tag": ",".join(r["tag"] for _, r in roots)}
    i, r = roots[0]
    out = {"tag": r["tag"], "line": r["line"], "label": r["label"]}
    kids = descendants(arcs, r["tag"])
    # a revenue-and-other-income style total above the standard one (COP):
    # a revenue-named parent, never gross profit / operating income
    custom_parents = [p for p in parents_of(arcs, r["tag"]) if p in face_tags and p not in REV_TOTAL
                      and REV_PARENT_RX.search(p) and not NOT_REV_PARENT_RX.search(p)]
    if OTHER_INCOME_LABEL.search(r["label"]):
        return {**out, "gate": "hold_perimeter_label"}
    if any(OTHER_INCOME_TAG.search(k) for k in kids):
        return {**out, "gate": "hold_perimeter_children", "detail": sorted(k for k in kids if OTHER_INCOME_TAG.search(k))}
    if custom_parents:
        return {**out, "gate": "hold_child_of_other_total", "detail": custom_parents}
    sibs = revenue_siblings(face, arcs, r["tag"])
    if sibs:
        members = [r["tag"]] + [x["tag"] for x in sibs]
        detail = [{"tag": x["tag"], "label": x["label"], "custom": x["custom"]} for x in sibs]
        if any(x["custom"] for x in sibs):
            return {**out, "gate": "hold_sibling_custom", "detail": detail}
        parent = calc_parent_of_exactly(full_arcs or {}, members)
        if parent is None:
            return {**out, "gate": "hold_sibling_revenue_no_total", "detail": detail}
        # the face prints no total; the filer's calc tree says the printed lines add up
        return {**out, "gate": "G3_calc_sum", "sum_tags": members, "check_tag": parent, "detail": detail}
    if r["tag"] == "RevenuesNetOfInterestExpense":
        return {**out, "gate": "hold_sector_net_revenue"}
    return {**out, "gate": "G1_printed_total"}


def operating_slot(face, shape):
    i_pre, _ = first(face, lambda r: PRETAX_RX.search(r["tag"]))
    i_tax, _ = first(face, lambda r: r["tag"] == TAX)
    i, r = first(face, lambda r: r["tag"] == "OperatingIncomeLoss")
    if r is None:
        _, cr = first(face, lambda r: r["custom"] and OP_LABEL.search(r["label"]) and not BEFORE_TAX_LABEL.search(r["label"]))
        if cr is not None:
            return {"gate": "hold_custom_operating_line", "tag": cr["tag"], "label": cr["label"]}
        return {"gate": "no_printed_operating_line", "tag": None}
    out = {"tag": r["tag"], "line": r["line"], "label": r["label"]}
    if shape == "bank":
        return {**out, "gate": "hold_sector_bank"}
    if BEFORE_TAX_LABEL.search(r["label"]):
        return {**out, "gate": "hold_label_before_tax"}
    if (i_pre is not None and i > i_pre) or (i_tax is not None and i > i_tax):
        return {**out, "gate": "hold_position_below_pretax"}
    return {**out, "gate": "G1_printed_line"}


def available_to_common_bridge(face):
    """G2b (release closure 2026-10-31, ETR / ES): the face bridges ProfitLoss straight
    to 'net income attributable to <parent>' tagged NetIncomeLossAvailableToCommon-
    StockholdersBasic through noncontrolling / SUBSIDIARY-preferred lines only, with no
    parent preferred dividends before it; then that line is the parent's net income.
    Returns {tag, tie} or None. The replay checks ProfitLoss - bridge = it."""
    i_pl, _ = first(face, lambda r: r["tag"] == "ProfitLoss")
    i_atc, atc = first(face, lambda r: r["tag"] == "NetIncomeLossAvailableToCommonStockholdersBasic")
    if i_pl is None or atc is None or i_atc < i_pl:
        return None
    between = [b for b in face[i_pl + 1:i_atc] if not b["tag"].endswith("Abstract")]
    ok = all(not b["custom"] and (NCI_CUSTOM_RX.search(b["tag"]) or ("Preferred" in b["tag"] and SUBSIDIARY_LABEL.search(b["label"])))
             for b in between)
    if not between or not ok:
        return None
    return {"tag": atc["tag"], "line": atc["line"], "label": atc["label"],
            "tie": {"profit_loss": "ProfitLoss", "nci": [b["tag"] for b in between]}}


def net_income_slot(face, all_rows):
    out = _net_income_slot(face, all_rows)
    alt = available_to_common_bridge(face)
    if alt and out["gate"] == "hold_parent_line_not_standard":
        return {**{k: v for k, v in alt.items()}, "gate": "G2b_available_to_common_bridge"}
    if alt and out["gate"] in ("G1_printed_line", "G2_nci_identity"):
        out["alt"] = alt  # used by the replay only when the printed NetIncomeLoss has no undimensioned value
    return out


def _net_income_slot(face, all_rows):
    i_tax, _ = first(face, lambda r: r["tag"] == TAX)
    nci = sorted({r["tag"] for r in all_rows if r["stmt"] in ("IS", "CI") and not r["custom"] and NCI_RX.search(r["tag"])})
    nci_custom = sorted({r["tag"] for r in all_rows if r["stmt"] in ("IS", "CI") and r["custom"] and NCI_CUSTOM_RX.search(r["tag"])
                         and not re.search(r"Comprehensive|PerShare|Equity|Capital|Distribution|Contribution", r["tag"])})
    i, r = first(face, lambda r: r["tag"] == "NetIncomeLoss")
    if r is not None:
        out = {"tag": r["tag"], "line": r["line"], "label": r["label"]}
        if NCI_LABEL.search(r["label"]) and not NCI_LABEL_OK.search(r["label"]):
            return {**out, "gate": "hold_label_noncontrolling"}
        if BEFORE_TAX_LABEL.search(r["label"]):
            return {**out, "gate": "hold_label_before_tax"}
        if i_tax is not None and i < i_tax:
            return {**out, "gate": "hold_position_above_tax"}
        i_pl, pl = first(face, lambda r: r["tag"] == "ProfitLoss")
        # tie terms = the lines printed BETWEEN ProfitLoss and NetIncomeLoss (GE prints the
        # total NCI line there and its continuing/discontinued split further down; only the
        # lines in between are the filer's own bridge)
        between = face[i_pl + 1:i] if pl is not None and i_pl < i else []
        terms = [b["tag"] for b in between if not b["tag"].endswith("Abstract")]
        if pl is not None and terms and all(NCI_RX.search(t) for t in terms):
            return {**out, "gate": "G2_nci_identity", "tie": {"profit_loss": "ProfitLoss", "nci": terms}}
        if pl is not None and terms:
            return {**out, "gate": "G1_printed_line", "detail": {"bridge_not_checkable": terms}}
        return {**out, "gate": "G1_printed_line"}
    i_pl, pl = first(face, lambda r: r["tag"] == "ProfitLoss")
    if pl is not None:
        out = {"tag": "ProfitLoss", "line": pl["line"], "label": pl["label"]}
        # ProfitLoss is the parent's only when NOTHING printed below it takes a share away:
        # any noncontrolling-interest line (ELS OP units, ETR preferred-unit NCI) or a
        # SUBSIDIARY's preferred dividends (PG&E, ETR; NCI in substance). The parent's own
        # preferred dividends come after parent net income and do not count. Release
        # closure 2026-10-31: 14 landed NI cells at 3 companies published consolidated income
        below = [b for b in face[i_pl + 1:] if "PerShare" not in b["tag"] and "Comprehensive" not in b["tag"]
                 and (NCI_CUSTOM_RX.search(b["tag"]) or ("Preferred" in b["tag"] and SUBSIDIARY_LABEL.search(b["label"])))]
        if nci or nci_custom or below:
            return {**out, "gate": "hold_parent_line_not_standard",
                    "detail": nci + nci_custom + [b["tag"] for b in below]}
        return {**out, "gate": "G1b_profit_loss_no_nci"}
    _, cr = first(face, lambda r: r["custom"] and re.search(r"net (income|earnings|loss)", r["label"], re.I)
                 and not NCI_LABEL.search(r["label"]))
    if cr is not None:
        return {"gate": "hold_custom_net_income_line", "tag": cr["tag"], "label": cr["label"]}
    return {"gate": "no_printed_net_income_line", "tag": None}


COR_TOTAL = {"CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"}
COR_EXCL_DA = {"CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
               "CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization"}
COR_LABEL = re.compile(r"\bcosts? of (net )?(sales|revenues?|goods|products|services|merchandise|operations)", re.I)
EXCL_DA_LABEL = re.compile(r"(exclusive of|excluding|excl\.?|before) (depreciation|d&a)", re.I)
GP_LABEL = re.compile(r"gross (profit|margin|income|loss)", re.I)


def cost_slot(face, arcs, shape, full_arcs):
    """the single printed cost-of-revenue total (same root / sibling / calc-sum
    discipline as revenue). A cost line printed EXCLUDING depreciation (BALL)
    holds for the Standardization Lead: a gross margin built on it is not
    comparable."""
    lines, seen = [], set()
    for r in face:
        if not r["custom"] and (r["tag"] in COR_TOTAL or r["tag"] in COR_EXCL_DA) and r["tag"] not in seen:
            seen.add(r["tag"])
            lines.append(r)
    if not lines:
        cr = next((r for r in face if r["custom"] and COR_LABEL.search(r["label"])), None)
        if cr is not None:
            return {"gate": "hold_custom_cost_line", "tag": cr["tag"], "label": cr["label"]}
        return {"gate": "no_printed_cost_line", "tag": None}
    if shape != "commercial":
        return {"gate": f"hold_sector_{shape}", "tag": lines[0]["tag"], "label": lines[0]["label"]}
    under = {r["tag"] for r in lines for s2 in lines if r["tag"] != s2["tag"] and r["tag"] in descendants(arcs, s2["tag"])}
    roots = [r for r in lines if r["tag"] not in under]
    others = [x for x in face if x["custom"] and COR_LABEL.search(x["label"]) and x["tag"] not in descendants(arcs, roots[0]["tag"])
              and not any(x["tag"] in descendants(arcs, rt["tag"]) for rt in roots)
              and x["tag"] not in {p for p in arcs if roots[0]["tag"] in descendants(arcs, p)}]
    members = [r["tag"] for r in roots] + [x["tag"] for x in others]
    r = roots[0]
    out = {"tag": r["tag"], "line": r["line"], "label": r["label"]}
    if len(members) > 1:
        detail = [{"tag": x["tag"], "label": x["label"], "custom": x["custom"]} for x in roots[1:] + others]
        if others:
            return {**out, "gate": "hold_sibling_custom", "detail": detail}
        parent = calc_parent_of_exactly(full_arcs or {}, members)
        if parent is None:
            return {**out, "gate": "hold_multiple_roots", "detail": detail}
        return {**out, "gate": "G3_calc_sum", "sum_tags": members, "check_tag": parent, "detail": detail}
    if r["tag"] in COR_EXCL_DA or EXCL_DA_LABEL.search(r["label"]):
        return {**out, "gate": "hold_perimeter_excl_da"}
    return {**out, "gate": "G1_printed_line"}


def gross_profit_slot(face, shape):
    i, r = first(face, lambda r: r["tag"] == "GrossProfit")
    if r is None:
        cr = next((x for x in face if GP_LABEL.search(x["label"])), None)
        if cr is not None:
            return {"gate": "hold_custom_gross_line", "tag": cr["tag"], "label": cr["label"]}
        return {"gate": "no_printed_gross_profit_line", "tag": None}
    out = {"tag": r["tag"], "line": r["line"], "label": r["label"]}
    if shape != "commercial":
        return {**out, "gate": f"hold_sector_{shape}"}
    if not GP_LABEL.search(r["label"]):
        return {**out, "gate": "hold_label_not_gross"}
    return {**out, "gate": "G1_printed_line"}


def gross_identity(rev, cost, gp):
    """revenue - cost = gross profit on the same filing, when all three are
    single printed lines; the replay holds a cell whose identity does not tie."""
    ok = (rev["gate"] == "G1_printed_total" and cost["gate"] == "G1_printed_line" and gp["gate"] == "G1_printed_line")
    if not ok:
        return
    t = {"revenue": rev["tag"], "cost": cost["tag"], "gross_profit": gp["tag"]}
    cost["gate"], cost["tie"] = "G2_gross_identity", t
    gp["gate"], gp["tie"] = "G2_gross_identity", t


def main(src, out_dir, coreg_path=None):
    coreg = set(open(coreg_path).read().split()) if coreg_path else set()
    # one FSN period at a time: a filing's pre and cal rows live in the period that
    # carries its submission, so memory stays at one period (the all-at-once load
    # was paged out under machine-wide swap pressure)
    out = Path(out_dir)
    slots = []
    gates = {f: Counter() for f in ("revenue", "operating_income", "net_income", "cost_of_revenue", "gross_profit")}
    for p in sorted(glob.glob(f"{src}/*_is_pre.jsonl.gz")):
        period = Path(p).name.split("_")[0]
        rows = defaultdict(list)
        for line in gzip.open(p, "rt"):
            r = json.loads(line)
            rows[r["adsh"]].append(r)
        arcs = defaultdict(lambda: defaultdict(dict))
        for line in gzip.open(f"{src}/{period}_cal.jsonl.gz", "rt"):
            a = json.loads(line)
            if a["adsh"] in rows:
                arcs[a["adsh"]][a["p"]][a["c"]] = a["w"]
        for adsh, rs in rows.items():
            rep, face = primary_face(rs, adsh in coreg)
            if not face:
                continue
            m = rs[0]
            face_tags = {r["tag"] for r in face}
            shape = shape_of(face_tags)
            full = arcs.get(adsh, {})
            a = {pp: set(kids) & face_tags for pp, kids in full.items()}
            base = {"adsh": adsh, "cik": m["cik"], "form": m["form"], "period": iso(m["period"]),
                    "filed": iso(m["filed"]), "fy": m.get("fy"), "fp": m.get("fp"), "report": rep,
                    "shape": shape, "has_cal": bool(arcs.get(adsh)),
                    # a dimensioned face (Snap-on 2019: ProductOrService axis, the undimensioned
                    # Revenues fact is the total of the member columns): own Verifier stratum
                    "face_axis": any(r["tag"].endswith("Axis") for r in face)}
            rev = revenue_slot(face, a, shape, face_tags, full)
            cost = cost_slot(face, a, shape, full)
            gp = gross_profit_slot(face, shape)
            gross_identity(rev, cost, gp)
            for fam, slot in (("revenue", rev),
                              ("operating_income", operating_slot(face, shape)),
                              ("net_income", net_income_slot(face, rs)),
                              ("cost_of_revenue", cost), ("gross_profit", gp)):
                gates[fam][slot["gate"]] += 1
                slots.append({**base, "family": fam, **slot})
    with open(out / "is_filing_slots.jsonl", "w") as f:
        for s in slots:
            f.write(json.dumps(s) + "\n")
    # eras per company and family
    by = defaultdict(list)
    for s in slots:
        by[(s["family"], s["cik"])].append(s)
    for fam in gates:
        n = 0
        with open(out / f"is_{fam}_records.jsonl", "w") as f:
            for (fm, cik), ss in sorted(by.items()):
                if fm != fam:
                    continue
                ss.sort(key=lambda s: (s["filed"], s["adsh"]))
                eras = []
                for s in ss:
                    key = (s["gate"], s.get("tag"))
                    if eras and eras[-1]["_key"] == key:
                        e = eras[-1]
                        e.update(filing_to=s["adsh"], period_to=s["period"], filings_observed=e["filings_observed"] + 1)
                    else:
                        eras.append({"_key": key, "kind": "slot_record", "cik": cik, "canonical_concept": fam,
                                     "rule_type": "slot_printed_line", "status": "proposed",
                                     "gate": s["gate"], "slot_tag": s.get("tag"), "label": s.get("label"),
                                     "shape": s["shape"], "filing_from": s["adsh"], "filing_to": s["adsh"],
                                     "period_from": s["period"], "period_to": s["period"], "filings_observed": 1,
                                     "evidence_accession": s["adsh"], "evidence_level": "FILING-STRUCTURE (FSN pre/cal)",
                                     "source": "is_detect.py", "detail": s.get("detail"), "tie": s.get("tie"),
                                     "sum_tags": s.get("sum_tags"), "check_tag": s.get("check_tag")})
                for e in eras:
                    e.pop("_key")
                    f.write(json.dumps(e) + "\n")
                    n += 1
        print(f"{fam}: records {n}  filing gates {dict(gates[fam].most_common())}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
