"""Clear or reject a write plan: seeded stratified sample of planned cells, each read against its cited filing.
Usage: python3 clear_plan.py plan.csv out.csv [n=200] [seed=20261111]
plan.csv needs: cik, data_point, grain (FY/Q), period_end, value (blank for a reasoned blank), accession; optional reason_code, start.
The cited accession's statement page must print the value at the column (within half a printed unit after scale);
a derived quarter is checked as YTD(this) - YTD(prior) from the same company's filings (hand-read when no accession pair is given)."""
import sys, csv, hashlib, collections
from decimal import Decimal
sys.path.insert(0, sys.path[0])
import akey
MAP = {"revenue_sanity_resolved":"revenue","revenue_resolved":"revenue","net_income_resolved":"net_income","operating_income_resolved":"operating_income",
       "gross_profit_resolved":"gross_profit","cost_of_revenue_resolved":"cost_of_revenue","pretax_income_resolved":"pretax_income","income_tax_resolved":"income_tax",
       "interest_expense_resolved":"interest_expense","cfo_resolved":"cfo","share_buybacks_resolved":"share_buybacks","dividends_paid_resolved":"dividends_paid",
       "basic_eps_resolved":"eps_basic","diluted_eps_resolved":"eps_diluted","dividends_per_share":"dps","dividends_per_share_resolved":"dps","shares_outstanding_resolved":"shares_outstanding"}
KIND = {"cfo":"cf","share_buybacks":"cf","dividends_paid":"cf","eps_basic":"eps","eps_diluted":"eps","dps":"eps","shares_outstanding":"sh"}
def main(plan, out, n=200, seed="20261111"):
    n = int(n)
    rows = list(csv.DictReader(open(plan)))
    strata = collections.defaultdict(list)
    for r in rows:
        dp = MAP.get(r["data_point"], r["data_point"]); r["_dp"] = dp
        strata[(dp, r["grain"], "value" if r.get("value") else "blank")].append(r)
    pick = []; per = max(1, n // max(1, len(strata)))
    for k, xs in strata.items():
        xs.sort(key=lambda r: hashlib.md5(f"{seed}:{r['cik']}:{r['data_point']}:{r['grain']}:{r['period_end']}".encode()).hexdigest())
        pick += xs[:per]
    pick = pick[:n]
    w = csv.writer(open(out, "w")); w.writerow(["cik","data_point","grain","period_end","plan_value","filing_value","verdict","locator"])
    tally = collections.Counter()
    for r in pick:
        dp = r["_dp"]; kind = KIND.get(dp, "is")
        if dp not in akey.TAGS: w.writerow([r["cik"], r["data_point"], r["grain"], r["period_end"], r.get("value",""), "", "NOT_CHECKED(no reader)", ""]); tally["not_checked"] += 1; continue
        months = 12 if r["grain"] == "FY" else 3
        try:
            hits = akey.read(r["cik"].lstrip("0"), r["accession"], dp, kind, r["period_end"], months, instant=(kind == "sh"))
        except Exception as ex:
            hits = []; r["_err"] = str(ex)[:80]
        fv = hits[0][1] if hits else None
        pv = Decimal(r["value"]) if r.get("value") else None
        if pv is None: verdict = "BLANK_CHECK_REASON" if fv is None else "WRONG_BLANK(filing prints a value)"
        elif fv is None: verdict = "HAND_CHECK(no printed line at the column)"
        else: verdict = "RIGHT" if abs(pv - fv) <= Decimal("0.5") * (Decimal(1) if dp in ("eps_basic","eps_diluted","dps") else Decimal(10**5)) * (Decimal("0.01") if dp in ("eps_basic","eps_diluted","dps") else 1) else "WRONG"
        tally[verdict.split("(")[0]] += 1
        w.writerow([r["cik"], r["data_point"], r["grain"], r["period_end"], r.get("value",""), str(fv) if fv is not None else "", verdict, f"{r['accession']} {hits[0][4] if hits else r.get('_err','')}"])
    print(dict(tally))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(sys.argv[3:]))
