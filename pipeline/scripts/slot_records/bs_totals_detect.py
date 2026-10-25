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
    r"PartnersCapital|MembersEquity|LimitedPartnersCapital|GeneralPartnersCapital|"
    # Verifier BS-V1 item 3: a filer's own equity element (BRKR
    # OthersShareholdersEquity) must never sit in the liabilities members.
    # Lexical balance-type guard until the FASB balance attribute CSV lands.
    r"ShareholdersEquity|Shareholders|StockholdersEquity|EquityAttributable|"
    r"CapitalSurplus|CapitalStock|PaidInCapital|OtherEquity|EquityOther|"
    # Verifier BS-V2 fix 2: MCK 'Other (1)' equity row tagged OtherCapital
    # (0000927653-18-000010 R4); ET ConvertiblePreferredUnits is an
    # equity-section line (0001276187-16-000165 R2)
    r"OtherCapital(?!iz)|PreferredUnits|CommonUnits|LimitedPartnersUnits"
)
MEZZ_RX = re.compile(r"TemporaryEquity|RedeemableNoncontrolling|RedeemablePreferred")
# Verifier BS-V1 item 1 (AWK): a DEBT subtotal whose element name mentions the
# redeemable preferred it includes ('LongTermDebtIncludesRedeemablePreferred
# StockAtRedemptionValue' = Total long-term debt) is a liability line, never
# mezzanine. Debt-reading tags win over the mezzanine pattern.
DEBT_LIKE_RX = re.compile(r"Debt|Borrow|NotesPayable|Loan")
NOISE_RX = re.compile(r"CommitmentsAndContingencies")

EQUITY_TOTAL_TAGS = {
    "StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    "PartnersCapital", "PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest",
    "MembersEquity",
}
CAP_TOTAL_RX = re.compile(r"Capitalization")
TOTAL_LABEL_RX = re.compile(r"^\s*total\b", re.I)


# Asset/equity rows that leak into the liabilities zone on some faces
# (Verifier BS-v0 class 2: MCK's OtherAdditionalCapital equity line, NI's
# PrepaidExpenseCurrent, ET's cash). Lexical guard until the taxonomy
# balance-attribute guard lands (needs the FASB schema, approval pending).
NONLIAB_RX = re.compile(
    r"PrepaidExpense|CashAndCashEquivalents|OtherAdditionalCapital|"
    r"Receivable$|ReceivableNet|ReceivableCurrent|Inventory|"
    r"UnamortizedDebt|DeferredCosts?[A-Z]|RightOfUseAsset"
)


def classify_line(tag, label):
    """Per-line class; works for liabilities-first AND capitalization-format
    (utilities: equity, LTD, Total Capitalization, then liabilities - NI/AWK)."""
    if NOISE_RX.search(tag) or tag in ("Liabilities", "LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital"):
        return "excluded_total_or_noise"
    if tag.endswith("Abstract"):
        return "excluded_abstract"
    if NONLIAB_RX.search(tag):
        return "excluded_nonliability"
    if MEZZ_RX.search(tag) and not DEBT_LIKE_RX.search(tag):
        return "mezz"
    if MEZZ_RX.search(tag):
        return "liab"  # debt subtotal that names the preferred it contains (AWK)
    if tag in EQUITY_TOTAL_TAGS:
        return "equity_total"
    if tag in ("MinorityInterest", "NonredeemableNoncontrollingInterest",
               "PartnersCapitalAttributableToNoncontrollingInterest",
               "MinorityInterestInLimitedPartnerships"):
        return "nci"
    if CAP_TOTAL_RX.search(tag):
        return "excluded_cap_total"  # equity+debt combined subtotal, never summed
    if EQUITY_START_RX.search(tag):
        return "equity_component"
    return "liab"


companies = defaultdict(list)
for adsh, meta in by_filing.items():
    ordered = sorted(rows[adsh])
    tags = [t for _, _, t, _, _ in ordered]
    zone_start = tags.index("Assets") + 1 if "Assets" in tags else 0
    zone = ordered[zone_start:]
    # rows RENDERED AFTER the L&E total are re-renders of lines already inside
    # the totals (Verifier class 3: NI's ARO-current and prepaid after the
    # total) - truncate the zone at the filer's own closing total
    zone_tags = [t for _, _, t, _, _ in zone]
    for lse in ("LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital"):
        if lse in zone_tags:
            zone = zone[: zone_tags.index(lse) + 1]
            break
    zone_lines = []
    for _, _, t, c, lb in zone:
        cls = classify_line(t, lb)
        zone_lines.append(
            {"tag": t, "custom": c, "label": lb, "seg": cls,
             "total_label": bool(TOTAL_LABEL_RX.search(lb or ""))}
        )
    # PERIMETER BY FACE POSITION (Dhairya ruling): a mezzanine-tagged line is
    # 'mezz' only when printed between the liabilities section and equity;
    # printed INSIDE the liabilities run (AWK's redeemable preferred inside
    # total long-term debt) it belongs to liabilities.
    # neighbor-based: a mezz-tagged line whose printed neighbors are both
    # liability lines sits INSIDE the liabilities section (AWK's redeemable
    # preferred inside total long-term debt) - works for capitalization
    # layouts too, where equity prints first and 'no equity seen' fails
    for i, z in enumerate(zone_lines):
        if z["seg"] != "mezz":
            continue
        prev_seg = next((zone_lines[j]["seg"] for j in range(i - 1, -1, -1)
                         if not zone_lines[j]["seg"].startswith("excluded")), None)
        next_seg = next((zone_lines[j]["seg"] for j in range(i + 1, len(zone_lines))
                         if not zone_lines[j]["seg"].startswith("excluded")), None)
        if prev_seg == "liab" and next_seg == "liab":
            z["seg"] = "liab"
    # the RAW liability line list; subtotal dedup happens in the assembler
    # against the filer's own statement-role calc graph (label-run replacement
    # proved wrong: T's 'Total deferred credits...' swallowed Long-Term Debt)
    skeleton = [z["tag"] for z in zone_lines if z["seg"] == "liab"]
    mezz = [z["tag"] for z in zone_lines if z["seg"] == "mezz"]
    anchors = {name: any(t in tagset for _, _, t, _, _ in zone) for name, tagset in ANCHORS.items()}
    fp = tuple(skeleton) + ("||",) + tuple(mezz) + (
        "printedL" if anchors["liabilities_total"] else "noL",
        "nci" if anchors["nci"] else "no_nci",
    )
    companies[meta["cik"]].append(
        (iso(meta["filed"]), iso(meta["period"]), adsh, meta["form"], fp, anchors, zone_lines, skeleton)
    )

eras_out = {}
boundaries = []
for cik, filings in companies.items():
    filings.sort()
    eras = []
    for filed, period, adsh, form, fp, anchors, zone_lines, skeleton in filings:
        if eras and eras[-1]["fp"] == list(fp):
            eras[-1]["last"] = adsh
            eras[-1]["period_to"] = period
            eras[-1]["n"] += 1
        else:
            eras.append(
                {"fp": list(fp), "first": adsh, "last": adsh, "form": form,
                 "period_from": period, "period_to": period, "filed_from": filed,
                 "n": 1, "anchors": anchors, "zone_lines": zone_lines, "skeleton": skeleton}
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
