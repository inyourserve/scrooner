import sys, types, datetime as dt, importlib.util
S = sys.argv[1]
sys.argv = ["x", S + "/shared", "/dev/null", "", "", S + "/t/out", "1", "0"]
spec = importlib.util.spec_from_file_location("cp", S + "/check_pass.py"); cp = importlib.util.module_from_spec(spec)
import csv; csv_reader = csv.DictReader
spec.loader.exec_module(cp)
def page(turn_in_investing):
    rows = [("us-gaap:NetCashProvidedByUsedInOperatingActivitiesAbstract", "Cash flows from operating activities", None)]
    if not turn_in_investing:
        rows.append(("us-gaap:PaymentsForTurnaroundCosts", "Turnaround expenditures", "(50)"))
    rows += [("us-gaap:NetCashProvidedByUsedInInvestingActivitiesAbstract", "Cash flows from investing activities", None),
             ("us-gaap:PaymentsToAcquirePropertyPlantAndEquipment", "Capital expenditures", "(200)")]
    if turn_in_investing:
        rows.append(("us-gaap:PaymentsForTurnaroundCosts", "Turnaround expenditures", "(50)"))
    rows.append(("us-gaap:NetCashProvidedByUsedInInvestingActivities", "Net cash used in investing activities", "(250)"))
    tr = "".join(f'<tr><td><a onclick="defref_{t.replace(":", "_")}">{l}</a></td><td>{v or ""}</td></tr>' for t, l, v in rows)
    return ('<table><tr><th>Statements of Cash Flows - USD ($) $ in Millions</th><th>12 Months Ended</th></tr>'
            '<tr><th>Dec. 31, 2025</th></tr>' + tr + '</table>')
for inside in (True, False):
    cp.D.get = lambda url, cache, inside=inside: page(inside)
    r = {"data_point": "capex", "status": "mapped", "tags": "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment", "r_page": "R7.htm",
         "label": "Capital expenditures", "fy0_printed": "-200000000", "note": ""}
    out = cp.capex_rule(r, "b/", dt.date(2025, 12, 31), {}, "a")
    print("inside" if inside else "operating", out, r["status"], r["fy0_printed"])
    assert (out == "capex" and r["fy0_printed"] == "-250000000") if inside else (out is None and r["status"] == "mapped")
print("PASS")
