"""Era detection from FSDS face balance-sheet rows (stdlib, run with -I).

Reads the bs_pre_rows.jsonl produced by fsds_debt_pre.py, fingerprints each
filing by its ordered debt-family face tags, collapses consecutive identical
fingerprints into eras per company, and emits the era table plus the list of
BOUNDARY accessions (first filing of each era) whose _cal.xml must be fetched.
usage: era_detect.py <bs_pre_rows.jsonl> <eras_out.json> <boundaries_out.txt>
"""
import json
import re
import sys
from collections import defaultdict

DEBT_RX = re.compile(r"Debt|Borrow|Lease|CommercialPaper|NotesPayable|LineOfCredit|Convertible")
EXCLUDE_RX = re.compile(
    r"PreferredStock|CommonStock|Equity|TreasuryStock|RetainedEarnings|"
    r"AccumulatedOtherComprehensive|CommitmentsAndContingencies|"
    r"DebtSecurities|SecuritiesBorrowed|OtherThanLongtermDebt|"
    r"TemporaryEquity|RedeemableNoncontrolling|RightOfUseAsset"
)

def iso(d: str) -> str:
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if d and len(d) == 8 and d.isdigit() else d


by_filing: dict[str, dict] = {}
lines = defaultdict(list)
for line in open(sys.argv[1]):
    r = json.loads(line)
    by_filing[r["adsh"]] = {
        "cik": r["cik"], "form": r["form"], "period": iso(r["period"]), "filed": iso(r["filed"]),
    }
    if DEBT_RX.search(r["tag"]) and not EXCLUDE_RX.search(r["tag"]):
        lines[r["adsh"]].append((r["report"], r["line"], r["tag"], r["custom"]))

companies = defaultdict(list)
for adsh, meta in by_filing.items():
    fp_tags = tuple(t for _, _, t, _ in sorted(lines.get(adsh, [])))
    companies[meta["cik"]].append((meta["filed"], meta["period"], adsh, meta["form"], fp_tags))

eras_out = {}
boundaries = []
for cik, filings in companies.items():
    filings.sort()  # by filed date
    eras = []
    for filed, period, adsh, form, fp in filings:
        if eras and eras[-1]["fp"] == list(fp):
            eras[-1]["last"] = adsh
            eras[-1]["period_to"] = period
            eras[-1]["n"] += 1
        else:
            eras.append(
                {"fp": list(fp), "first": adsh, "last": adsh, "form": form,
                 "period_from": period, "period_to": period, "filed_from": filed, "n": 1}
            )
            boundaries.append((cik, adsh))
    eras_out[cik] = eras
with open(sys.argv[2], "w") as f:
    json.dump(eras_out, f, indent=1)
with open(sys.argv[3], "w") as f:
    for cik, adsh in boundaries:
        f.write(f"{int(cik)} {adsh}\n")
print(
    f"companies {len(eras_out)}  filings {len(by_filing)}  "
    f"eras {sum(len(v) for v in eras_out.values())}  boundary_cal_fetches {len(boundaries)}"
)
for cik in sorted(eras_out):
    e = eras_out[cik]
    print(f"  {cik}: {len(e)} eras over {sum(x['n'] for x in e)} filings")
