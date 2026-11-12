"""Template points with no face source: note-sourced candidate, template-OUT candidate, or a reason (read-only on the store).

Rebuilt after the Verifier draw of 2026-11-11 (14/34 and 28/63 FAIL). Rules:
  - absence is decided on the FSN STORE (fsn.value, undimensioned, statements AND notes, predecessor filings included),
    over a broad tag set per concept (card libraries + every tag mapped anywhere in the 50 + known variants); a
    companyfacts miss is never evidence;
  - FACE_ONLY points (gross profit, operating income, operating expenses, other income, cost of revenue, SG&A) are
    never note-sourced: outside the face they are often segment totals (ORCL gross margin, JNJ segment OI);
  - a fact whose tag is ALSO a face line of the company is not a note candidate: the face decision is re-checked;
  - a component tag never stands in for its total (Depreciation alone for D&A, a bank's securities interest line).
Usage: candidates.py <tag_map.csv> <template_points.csv> <concepts.csv> <library_dir> <out_note.csv> <out_out.csv>
"""
import collections
import csv
import glob
import os
import sys

import psycopg

tm, tp, cc, libdir, out_note, out_out = sys.argv[1:7]
base = lambda c: c[:-9] if c.endswith("_resolved") else c
ALIAS = {"revenue": "revenue_sanity"}
cat = {r["name"] for r in csv.DictReader(open(cc))}
FACE_ONLY = {"gross_profit", "operating_income", "operating_expenses", "other_income_expense_net", "cost_of_revenue", "sga_expense"}
SKIP = {"employee_count", "public_float", "shares_outstanding", "effective_tax_rate_reported", "total_debt", "total_debt_split",
        "total_liabilities", "dividends_per_share", "collaborative_arrangement_revenue", "net_lease_revenue"}
VARIANTS = {  # concept -> tags that ARE the concept (totals); components listed apart
    "interest_income": ["InvestmentIncomeInterest", "InvestmentIncomeInterestAndDividend", "InterestIncomeOther", "InterestAndOtherIncome",
                        "InterestIncomeOperating", "InterestIncomeNonoperating"],
    "interest_expense": ["InterestExpense", "InterestExpenseNonoperating", "InterestAndDebtExpense", "InterestExpenseOperating"],
    "amortization_of_intangibles": ["AmortizationOfIntangibleAssets"],
    "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
    "depreciation_and_amortization": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet"],
    "research_and_development": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
                                 "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost"],
    "inventory": ["InventoryNet", "InventoryGross"],
    "accounts_receivable": ["AccountsReceivableNetCurrent"],
    "accounts_payable": ["AccountsPayableCurrent", "AccountsPayableTradeCurrent"],
    "cf_ar_change": ["IncreaseDecreaseInAccountsReceivable", "IncreaseDecreaseInReceivables"],
    "cf_ap_change": ["IncreaseDecreaseInAccountsPayable", "IncreaseDecreaseInAccountsPayableTrade"],
    "cf_inventory_change": ["IncreaseDecreaseInInventories"],
    "dividends_paid": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
    "share_buybacks": ["PaymentsForRepurchaseOfCommonStock", "PaymentsForRepurchaseOfEquity"],
    "goodwill": ["Goodwill"],
    "ppe_net": ["PropertyPlantAndEquipmentNet", "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "current_assets": ["AssetsCurrent"], "current_liabilities": ["LiabilitiesCurrent"],
    "cash_and_equivalents": ["CashAndCashEquivalentsAtCarryingValue", "Cash"],
}
COMPONENT_ONLY = {"depreciation_and_amortization": {"Depreciation", "AmortizationOfIntangibleAssets"},
                  "interest_income": {"InterestIncomeDebtSecuritiesAvailableForSaleExcludingAccretionAmortizationOfDiscountPremium"}}

m = list(csv.DictReader(open(tm)))
tick = {r["company_id"]: r["ticker"] for r in m}
tags = collections.defaultdict(set)
for k, v in VARIANTS.items():
    tags[k] |= set(v)
for r in m:  # every tag mapped to the concept anywhere in the 50
    c = base(r["canonical_concept"] if r["decision"] == "concept" else r["parent_concept"] if r["decision"] == "component" else "")
    if c and r["taxonomy"] == "us-gaap":
        tags[c].add(r["tag"])
for p in glob.glob(os.path.join(libdir, "fsn-*.csv")):  # Tag Expert card libraries
    for r in csv.DictReader(open(p)):
        if r.get("decision") == "map" and r.get("canonical_concept_key"):
            tags[base(r["canonical_concept_key"])].add(r["tag"].split(":")[-1])
face = collections.defaultdict(set)  # company -> tags printed on its statements (any decision)
covered = collections.defaultdict(set)
for r in m:
    face[r["company_id"]].add(r["tag"])
    c = base(r["canonical_concept"] if r["decision"] == "concept" else r["parent_concept"] if r["decision"] == "component" else "")
    if c:
        covered[r["company_id"]].add(c)
    if r["decision"] == "combined":
        covered[r["company_id"]] |= {base(x) for x in (r["components"] or "").split(";")}
    POINT_REASON = {"parent_equity_not_printed": "stockholders_equity", "not_sga_broad_operating_costs": "sga_expense",
                    "cost_of_products_not_total_cor": "cost_of_revenue", "component_of_unprinted_total": "cost_of_revenue",
                    "d_and_a_not_presented": "depreciation_and_amortization", "bank_interest_income_component": "interest_income",
                    "total_costs_incl_cost_of_revenue": "operating_expenses", "bank_cash_perimeter": "cash_and_equivalents",
                    "cash_incl_short_term_investments": "cash_and_equivalents"}
    if r["decision"] == "excluded" and r["reason_class"] in POINT_REASON:
        covered[r["company_id"]].add(POINT_REASON[r["reason_class"]])  # a reasoned point is decided, never a candidate
pairs = []
seen = set()
for r in csv.DictReader(open(tp)):
    if r["data_point"] not in cat or r["company_id"] not in tick:
        continue
    b = ALIAS.get(base(r["data_point"]), base(r["data_point"]))
    if b in SKIP or (r["company_id"], b) in seen or b in covered[r["company_id"]]:
        continue
    seen.add((r["company_id"], b))
    pairs.append((r["company_id"], b))

found = collections.defaultdict(dict)  # (company, concept) -> {tag: (n_periods, last)}
with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    conn.execute("set statement_timeout = '60s'")
    by_co = collections.defaultdict(set)
    for c, b in pairs:
        by_co[c].add(b)
    for c, bs in by_co.items():
        want = sorted(set().union(*[tags[b] | COMPONENT_ONLY.get(b, set()) for b in bs]))
        if not want:
            continue
        q = """select t.tag, count(distinct v.ddate), max(v.ddate) from fsn.value v join fsn.tag t on t.id = v.tag_id
               where v.company_id = %s and v.dim_id = 0 and v.coreg = '' and t.tag = any(%s) and v.ddate >= '2015-01-01'
               group by 1"""
        hits = {t: (n, str(d)) for t, n, d in conn.execute(q, (int(c), want)).fetchall()}
        for b in bs:
            found[(c, b)] = {t: hits[t] for t in tags[b] | COMPONENT_ONLY.get(b, set()) if t in hits}

with open(out_note, "w", newline="") as fn, open(out_out, "w", newline="") as fo:
    wn, wo = csv.writer(fn), csv.writer(fo)
    wn.writerow(["company_id", "ticker", "concept", "tags_found", "periods", "check", "verifier_stratum"])
    wo.writerow(["company_id", "ticker", "data_point", "in_template", "reason", "evidence"])
    for c, b in pairs:
        f = found.get((c, b), {})
        totals = {t: v for t, v in f.items() if t not in COMPONENT_ONLY.get(b, set())}
        on_face = sorted(t for t in totals if t in face[c])
        if b in FACE_ONLY:
            wo.writerow([c, tick[c], b, "false", "line_not_presented_on_face",
                         "no face line maps to it; note values are never used for this point (segment-total risk, Verifier 2026-11-11)"])
        elif on_face:
            wn.writerow([c, tick[c], b, ";".join(on_face), max(v[0] for v in totals.values()), "RECHECK: the tag is a face line of this company; re-decide the face row", "face_recheck"])
        elif totals:
            wn.writerow([c, tick[c], b, ";".join(sorted(totals)), max(v[0] for v in totals.values()), "note-only fact (FSN store, undimensioned)", "note_sourced"])
        elif f:
            wo.writerow([c, tick[c], b, "false", "only_component_reported",
                         f"only component tag(s) {';'.join(sorted(f))} reported; a component never stands in for the total"])
        else:
            wo.writerow([c, tick[c], b, "false", "not_reported",
                         f"no fact under {len(tags[b])} tags in the FSN store (statements and notes, predecessor filings included) since 2015"])
print("pairs", len(pairs))
