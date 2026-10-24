"""Balance-sheet-totals era detection from the cohort FSDS extract (stdlib, -I).

Per filing: the right-hand side of the balance sheet (every face line from the
first row AFTER the Assets total to the end) is the fingerprint zone for the
bs_totals family. Records which anchor totals the face prints (Liabilities,
StockholdersEquity, the including-NCI total, mezzanine lines), so the
assembler can apply the printed-total-first rule. Eras collapse on the zone's
ordered tag list; boundaries get a cal fetch for member partitioning.
usage: bs_totals_detect.py <cohort_pre_rows.jsonl.gz> <cik,...> <eras_out.json> <boundaries_out.txt>
"""
import gzip
import json
import sys
from collections import defaultdict

ANCHORS = {
    "assets_total": {"Assets"},
    "liabilities_total": {"Liabilities"},
    "equity_parent": {"StockholdersEquity"},
    "equity_incl_nci": {"StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"},
    "nci": {"MinorityInterest"},
    "lse_total": {"LiabilitiesAndStockholdersEquity"},
}

ciks = set(sys.argv[2].split(","))
by_filing = {}
rows = defaultdict(list)
with gzip.open(sys.argv[1], "rt") as f:
    for line in f:
        r = json.loads(line)
        if r["cik"] not in ciks or r.get("stmt") != "BS":
            continue
        by_filing[r["adsh"]] = {
            "cik": r["cik"], "form": r["form"],
            "period": r["period"], "filed": r["filed"],
        }
        rows[r["adsh"]].append((r["report"], r["line"], r["tag"], r["custom"], r["label"]))


def iso(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if d and len(d) == 8 and d.isdigit() else d


import re  # noqa: E402

EQUITY_START_RX = re.compile(
    r"^(Preferred|Common)Stock|AdditionalPaidInCapital|RetainedEarnings|"
    r"AccumulatedOtherComprehensive|TreasuryStock|StockholdersEquity|"
    r"PartnersCapital|MembersEquity|LimitedPartnersCapital|GeneralPartnersCapital"
)
MEZZ_RX = re.compile(r"TemporaryEquity|RedeemableNoncontrolling|RedeemablePreferred")
NOISE_RX = re.compile(r"CommitmentsAndContingencies")

companies = defaultdict(list)
for adsh, meta in by_filing.items():
    ordered = sorted(rows[adsh])
    tags = [t for _, _, t, _, _ in ordered]
    zone_start = tags.index("Assets") + 1 if "Assets" in tags else 0
    zone = ordered[zone_start:]
    # segment the right-hand side by ORDER: current components ... LiabilitiesCurrent
    # subtotal ... noncurrent lines ... [Liabilities] ... mezzanine ... equity
    eq_start = next(
        (i for i, (_, _, t, _, _) in enumerate(zone) if EQUITY_START_RX.search(t) or MEZZ_RX.search(t)),
        len(zone),
    )
    liab_seg = zone[:eq_start]
    rest = zone[eq_start:]
    liab_tags = [t for _, _, t, _, _ in liab_seg]
    lc = liab_tags.index("LiabilitiesCurrent") + 1 if "LiabilitiesCurrent" in liab_tags else 0
    # the summable skeleton: LiabilitiesCurrent subtotal (replaces its
    # components) + every line after it, minus the printed total and noise
    skeleton = (["LiabilitiesCurrent"] if lc else []) + [
        t for t in liab_tags[lc:] if t not in ("Liabilities",) and not NOISE_RX.search(t)
    ]
    mezz = [t for _, _, t, _, _ in rest if MEZZ_RX.search(t)]
    anchors = {name: any(t in tagset for _, _, t, _, _ in zone) for name, tagset in ANCHORS.items()}
    fp = tuple(skeleton) + ("||",) + tuple(mezz) + (
        "printedL" if anchors["liabilities_total"] else "noL",
        "nci" if anchors["nci"] else "no_nci",
    )
    zone_lines = [
        {"tag": t, "custom": c, "label": lb, "seg": "liab" if i < eq_start else "eq_mezz"}
        for i, (_, _, t, c, lb) in enumerate(zone)
    ]
    companies[meta["cik"]].append(
        (iso(meta["filed"]), iso(meta["period"]), adsh, meta["form"], fp, anchors, zone_lines)
    )

eras_out = {}
boundaries = []
for cik, filings in companies.items():
    filings.sort()
    eras = []
    for filed, period, adsh, form, fp, anchors, zone_lines in filings:
        if eras and eras[-1]["fp"] == list(fp):
            eras[-1]["last"] = adsh
            eras[-1]["period_to"] = period
            eras[-1]["n"] += 1
        else:
            eras.append(
                {"fp": list(fp), "first": adsh, "last": adsh, "form": form,
                 "period_from": period, "period_to": period, "filed_from": filed,
                 "n": 1, "anchors": anchors, "zone_lines": zone_lines}
            )
            boundaries.append((cik, adsh))
    eras_out[cik] = eras
json.dump(eras_out, open(sys.argv[3], "w"))
with open(sys.argv[4], "w") as f:
    for cik, adsh in boundaries:
        f.write(f"{int(cik)} {adsh}\n")
print(
    f"companies {len(eras_out)}  filings {len(by_filing)}  "
    f"eras {sum(len(v) for v in eras_out.values())}  boundaries {len(boundaries)}"
)
for cik in sorted(eras_out):
    es = eras_out[cik]
    printed = sum(1 for e in es if e["anchors"]["liabilities_total"])
    print(f"  {cik}: {len(es)} eras, printed-Liabilities-total in {printed}")
