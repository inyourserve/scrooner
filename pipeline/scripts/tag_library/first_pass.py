"""First-pass company tag map for cohort ranks FROM..TO (read-only on the store).

For each company: every (stmt, tag) printed on a statement line since 2015, with how often, the latest label and
the calc parent(s). Decision order:
  1. rule     - the tag is a std_tag rule in data-team/47-fsn-store/concept_rules (that statement)
  2. oldmap   - the tag is in analytics.concept_mapping for a concept of that statement family (learning only)
  3. ancestor - a calc ancestor in the same filing is decided by 1/2: component of that concept
  4. cover    - stmt CP/UN: excluded (cover page / parenthetical / unclassified)
  else        - residue (needs judgement)
Usage: first_pass.py <rules_dir> <old_map.csv> <cohort.csv> <from> <to> <out.csv>
"""
import collections
import csv
import json
import os
import sys
from pathlib import Path

import psycopg

rules_dir, old_map, cohort, lo, hi, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
FAM = {"income_statement": {"IS", "CI"}, "balance_sheet": {"BS"}, "cash_flow": {"CF"}}

rule = {}  # (stmt, bare tag) -> concept
for p in Path(rules_dir).glob("*.jsonl"):
    if p.name.startswith("_"):
        continue
    for ln in p.read_text().splitlines():
        r = json.loads(ln)
        if r.get("match_kind") == "std_tag" and r.get("tag"):
            rule.setdefault((r["stmt"], r["tag"].split(":")[-1]), r["canonical_concept"])
old = collections.defaultdict(set)  # bare tag -> {(concept, stmts)}
for r in csv.DictReader(open(old_map)):
    old[r["tag"].split(":")[-1]].add((r["name"], frozenset(FAM.get(r["statement"], set()))))

rows = list(csv.DictReader(open(cohort)))[lo - 1:hi]
Q_LINES = """select l.filing_id, l.stmt, t.tag, t.custom, l.plabel, f.accepted, f.accession, f.period
             from fsn.line l join fsn.filing f on f.id = l.filing_id join fsn.tag t on t.id = l.tag_id
             where f.company_id = %s and f.period >= '2015-01-01'"""
Q_ARCS = """select a.filing_id, p.tag, c.tag from fsn.calc_arc a join fsn.filing f on f.id = a.filing_id
            join fsn.tag p on p.id = a.parent_tag_id join fsn.tag c on c.id = a.child_tag_id
            where f.company_id = %s and f.period >= '2015-01-01'"""

import re

STRUCT = re.compile(r"(Abstract|Table|LineItems|Axis|Domain|Member|RollForward)$")
CROSS = {}  # (stmt, tag) -> (reason_class, reason): a concept of another statement repeated here
for t in ("StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"):
    CROSS[("EQ", t)] = ("equity_rollforward_balance", "opening/closing equity balance; the concept lives on the BS")
for t in ("NetIncomeLoss", "ProfitLoss", "NetIncomeLossAttributableToNoncontrollingInterest"):
    CROSS[("EQ", t)] = ("equity_rollforward_movement", "net income as an equity movement; the concept lives on the IS")
    CROSS[("CF", t)] = ("cf_start_line", "net income as the CF reconciliation start line; the concept lives on the IS")
    CROSS[("CI", t)] = ("ci_start_line", "net income as the CI start line; the concept lives on the IS")
for t in ("CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
          "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
          "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
          "CashAndCashEquivalentsPeriodIncreaseDecrease", "Cash"):
    CROSS[("CF", t)] = ("cash_rollforward", "CF cash roll-forward (start, end or change); the cash concept lives on the BS")
for t in ("OtherComprehensiveIncomeLossNetOfTaxPortionAttributableToParent", "OtherComprehensiveIncomeLossNetOfTax",
          "ComprehensiveIncomeNetOfTax", "Dividends", "DividendsCommonStock", "DividendsCommonStockCash"):
    CROSS[("EQ", t)] = ("equity_rollforward_movement", "equity movement; its own concept lives on another statement or none")
DPS_TAGS = {"CommonStockDividendsPerShareDeclared", "CommonStockDividendsPerShareCashPaid"}
CI_TOTAL = {"ComprehensiveIncomeNetOfTax"}
ASK_EXPERT = {
    "CommonStockSharesOutstanding": "BS-date share count: shares_outstanding concept or excluded? (R2 holds shares_outstanding)",
    "CommonStockSharesIssued": "share count parenthetical: excluded?",
    "InterestPaidNet": "supplemental cash paid for interest: no catalog concept; catalog addition?",
    "InterestPaid": "supplemental cash paid for interest: no catalog concept; catalog addition?",
    "IncomeTaxesPaidNet": "supplemental cash paid for taxes: no catalog concept; catalog addition?",
    "IncomeTaxesPaid": "supplemental cash paid for taxes: no catalog concept; catalog addition?",
}


# tag families with no catalog concept: (stmts, regex, reason_class, reason)
FAMILIES = [
    ({"EQ"}, r"^(StockIssued|StockRepurchased|TreasuryStock|AdjustmentsToAdditionalPaidInCapital|AdjustmentsRelatedToTaxWithholding|"
             r"MinorityInterest|NoncontrollingInterest|CumulativeEffect|StockholdersEquityOther|SharesOutstanding|StockGranted|"
             r"StockholdersEquityReclassification|PartnersCapital|ShareBasedCompensation|StockIssued1|DividendsPreferred|"
             r"TemporaryEquity|SharesIssued|StockholdersEquityNoteStockSplit|ConversionOfStock|StockRedeemed)",
     "equity_movement", "equity roll-forward movement or share count; no catalog concept (buyback cash lives on the CF)"),
    ({"EQ", "BS", "IS", "CF", "CI"}, r"^AccountingStandardsUpdate", "text_element", "text/extensible list element: carries no amount"),
    ({"BS"}, r"^(CommonStock|PreferredStock|TreasuryStock)(Shares|ParOrStatedValue|SharesAuthorized|SharesIssued|SharesOutstanding|"
             r"DividendRatePercentage|LiquidationPreference|CommonShares|ValueOutstanding|NoParValue)",
     "share_terms_parenthetical", "share count, par value or preferred terms printed with the BS; no catalog concept"),
    ({"BS"}, r"^(AllowanceFor|AccumulatedDepreciation|AccumulatedAmortization)", "contra_parenthetical",
     "allowance or accumulated depreciation printed with the BS; the net line carries the concept"),
    ({"BS"}, r"(FairValueDisclosure|FairValue|AmortizedCost)", "fair_value_parenthetical", "fair value or cost basis printed with the BS"),
    ({"CF"}, r"^EffectOfExchangeRateOn", "fx_effect_on_cash", "FX effect on cash in the CF identity; no catalog concept"),
    ({"CF"}, r"^(CapitalExpendituresIncurredButNotYetPaid|RightOfUseAssetObtained|NoncashOrPartNoncash|OtherSignificantNoncash|"
             r"BusinessCombinationConsiderationTransferredEquity|StockIssued1|DebtConversion|LeaseLiabilityArising)",
     "noncash_supplemental", "non-cash supplemental disclosure; never a cash flow"),
    ({"CF"}, r"^(CashCashEquivalentsRestrictedCash|CashAndCashEquivalentsAtCarryingValueIncludingDiscontinued|DisposalGroupIncludingDiscontinuedOperationCash|RestrictedCash)",
     "cash_rollforward", "cash roll-forward or restricted-cash reconciliation line; the cash concept lives on the BS"),
    ({"IS"}, r"^WeightedAverageNumber", "share_count", "weighted-average share count; no catalog concept (proposed catalog addition)"),
    ({"IS", "CI"}, r"^(DiscontinuedOperation|IncomeLossFromDiscontinuedOperations)", "discontinued_operations", "discontinued-operations line; no catalog concept"),
    ({"IS", "CF", "BS", "EQ"}, r"^(StockholdersEquityNoteStockSplit|AntidilutiveSecurities)", "text_element", "ratio/description or share detail, not an amount line"),
]
FAMILIES = [(s, re.compile(rx), rc, why) for s, rx, rc, why in FAMILIES]


def family(stmt, tag):
    for sts, rx, rc, why in FAMILIES:
        if stmt in sts and rx.search(tag):
            return rc, why
    return None


def direct(stmt, tag):
    if (stmt, tag) in rule:
        return "rule", rule[(stmt, tag)]
    hits = [c for c, sts in old.get(tag, ()) if stmt in sts and not c.startswith("total_debt")]
    if len(hits) == 1:
        return "oldmap", hits[0]
    return None, None

out_rows = []
with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    conn.execute("set statement_timeout = '60s'")
    for rank, c in enumerate(rows, start=lo):
        cid = int(c["company_id"])
        lines = conn.execute(Q_LINES, (cid,)).fetchall()
        parents = collections.defaultdict(set)  # (filing, child) -> parents
        for fid, p, ch in conn.execute(Q_ARCS, (cid,)).fetchall():
            parents[(fid, ch)].add(p)
        agg = {}
        for fid, stmt, tag, custom, plabel, accepted, acc, period in lines:
            k = (stmt, tag)
            a = agg.setdefault(k, {"n": 0, "custom": custom, "label": plabel, "last": accepted, "acc": acc, "filings": set(), "anc": collections.Counter(), "par": collections.Counter(), "p0": period, "p1": period})
            a["n"] += 1
            if period and (a["p0"] is None or period < a["p0"]): a["p0"] = period
            if period and (a["p1"] is None or period > a["p1"]): a["p1"] = period
            a["filings"].add(fid)
            if accepted and (a["last"] is None or accepted > a["last"]):
                a["last"], a["label"], a["acc"] = accepted, plabel, acc
            # walk up the calc tree of this filing (bounded)
            seen, frontier = set(), [tag]
            for _ in range(8):
                nxt = []
                for t in frontier:
                    for p in parents.get((fid, t), ()):
                        if p not in seen:
                            seen.add(p)
                            nxt.append(p)
                            a["par"][p] += t == tag
                            how, conc = direct(stmt, p)
                            if conc:
                                a["anc"][(conc, p)] += 1
                frontier = nxt
        for (stmt, tag), a in agg.items():
            how, decision, conc, rc, why = "residue", "", "", "", ""
            if stmt in ("CP", "UN"):
                how, decision, rc, why = "cover", "excluded", "cover_or_parenthetical", "cover page, parenthetical or unclassified statement"
            elif STRUCT.search(tag):
                how, decision, rc, why = "structure", "excluded", "presentation_element", "abstract/table/axis/member/roll-forward heading: carries no value"
            else:
                d_how, d_conc = direct(stmt, tag)
                if d_conc:
                    how, decision, conc = d_how, "concept", d_conc
                elif (stmt, tag) in CROSS:
                    how, decision, rc, why = "rollforward", "excluded", CROSS[(stmt, tag)][0], CROSS[(stmt, tag)][1]
                elif stmt == "EQ" and tag in DPS_TAGS:
                    how, decision, conc, why = "rule_eq_dps", "concept", "dividends_per_share_resolved", "DPS printed on the equity statement (MDT pattern; proposal 0122)"
                elif stmt == "CI" and tag in CI_TOTAL:
                    how, decision, conc = "rule_ci", "concept", "comprehensive_income"
                elif stmt == "CI" and tag.startswith("OtherComprehensiveIncome"):
                    how, decision, rc, why = "rule_ci", "excluded", "oci_component", "OCI component; no catalog concept"
                elif not a["custom"] and family(stmt, tag):
                    rc, why = family(stmt, tag)
                    how, decision = "family", "excluded"
                elif tag in ASK_EXPERT:
                    how, decision, rc, why = "ask_expert", "", "", ASK_EXPERT[tag]
                elif a["anc"]:
                    (anc_conc, parent), _ = a["anc"].most_common(1)[0]
                    how, decision, rc, why = "ancestor", "excluded", "detail_of_printed_total", f"rolls up into {anc_conc} (printed) via {parent}"
            out_rows.append({
                "rank": rank, "company_id": cid, "cik": c["cik"], "ticker": c["ticker"], "taxonomy": "custom" if a["custom"] else "us-gaap",
                "stmt": stmt, "tag": tag, "lines": a["n"], "filings": len(a["filings"]),
                "evidence_plabel": a["label"], "evidence_adsh": a["acc"], "evidence_cal_parent": ";".join(p for p, _ in a["par"].most_common(3)),
                "era_from": a["p0"] or "", "era_to": a["p1"] or "", "decision": decision, "canonical_concept": conc, "reason_class": rc, "reason": why, "decided_by": how,
            })
        print(f"rank {rank} {c['ticker']}: {len(agg)} (stmt,tag) pairs, residue {sum(1 for r in out_rows if r['company_id']==cid and r['decided_by']=='residue')}", flush=True)

with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
    w.writeheader()
    w.writerows(out_rows)
