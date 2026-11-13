"""Post-pass over the shared docmap.py output (reads 501-600): the binding rulings the tool does not apply yet, as
machine rules (each changed row gets 'check: machine-rule <rule>' and keeps the machine value in its note), plus
hand-review flags. Reads only cached SEC files (no requests).
usage: postpass.py <machine_dir> <out_dir> <ticker> [...]   -> prints one JSON line per ticker: changes + flags"""
import csv, glob, importlib.util, json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("dm", os.path.join(os.path.dirname(os.path.abspath(__file__)), "docmap.py"))
dm = importlib.util.module_from_spec(spec); spec.loader.exec_module(dm)
CACHE = os.path.join(S, "sec_cache")
DEBT_NOTE = re.compile(r"debt|borrowing|financing arrangement|notes payable|credit", re.I)
BAD_SRC = re.compile(r"schedule i\b|condensed financial information|registrant|joint venture|equity method|summarized financial|variable interest|\bvie", re.I)
BANK_TAGS = {"InterestIncomeExpenseNet", "NoninterestExpense", "NoninterestIncome", "InterestIncomeExpenseAfterProvisionForLoanLoss"}
INS_RX = re.compile(r"^(PremiumsEarnedNet|BenefitsLossesAndExpenses|PolicyholderBenefitsAndClaimsIncurredNet)")
OUT6 = ("cost_of_revenue", "gross_profit", "research_and_development", "inventory", "current_assets", "current_liabilities")
CAPEX_TAGS = {"PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets", "PaymentsForCapitalImprovements",
              "PaymentsToAcquireOtherProductiveAssets", "PaymentsToAcquireOtherPropertyPlantAndEquipment", "PaymentsForProceedsFromProductiveAssets",
              "PaymentsToDevelopRealEstateAssets", "PaymentsToAcquireAndDevelopRealEstate", "PaymentsToAcquireOilAndGasPropertyAndEquipment"}


def cached(url_part):
    hits = [p for p in glob.glob(os.path.join(CACHE, "*")) if url_part in p]
    return hits[0] if hits else None


def page(cik, acc, rfile):
    p = cached(f"{int(cik)}_{acc.replace('-', '')}_{rfile.replace('.', '_')}")
    return dm.parse_r(open(p, encoding="utf8").read()) if p else None


def fx(cf, tag, acc, end, instant=True):
    for u in cf.get("facts", {}).get("us-gaap", {}).get(tag, {}).get("units", {}).values():
        for r in u:
            if r.get("accn") == acc and r["end"] == end and (not r.get("start")) == instant:
                return r["val"]
    return None


def main(mdir, odir, tickers):
    os.makedirs(odir, exist_ok=True)
    for tk in tickers:
        csvp = os.path.join(mdir, f"{tk}-docmap-2026-11-12.csv")
        if not os.path.exists(csvp):
            print(json.dumps({"ticker": tk, "error": "no machine docmap"})); continue
        rows = list(csv.DictReader(open(csvp)))
        md = open(os.path.join(mdir, f"{tk}-docmap-2026-11-12.md")).read()
        m = re.search(r"10-K (\d{10}-\d{2}-\d{6}) \(CIK (\d{10})", md)
        if not m:
            print(json.dumps({"ticker": tk, "error": "no filing"})); continue
        acc, cik = m.group(1), m.group(2)
        cfp = cached(f"companyfacts_CIK{cik}")
        cf = json.load(open(cfp)) if cfp else {}
        mlp = cached(f"{int(cik)}_{acc.replace('-', '')}_MetaLinks_json")
        inst = next(iter(json.load(open(mlp))["instance"].values())) if mlp else {"report": {}, "tag": {}}
        role2 = {v["role"]: (k, v.get("shortName", ""), v.get("groupType", "")) for k, v in inst["report"].items()}
        def pages_of(tag):
            return [role2[r] for r in inst["tag"].get("us-gaap_" + tag, {}).get("presentation", []) if r in role2]
        by = {r["data_point"]: r for r in rows}
        fy0 = next((mm.group(1) for r in rows for mm in [re.search(r"period \.\.(\d{4}-\d{2}-\d{2})", r["note"])] if mm), None)
        changes, flags = [], []
        def change(r, rule, **kw):
            old = {k: r.get(k, "") for k in kw}
            r.update({k: str(v) for k, v in kw.items()})
            r["note"] += f" | check: machine-rule {rule} (machine value {json.dumps(old)})"
            changes.append(f"{r['data_point']}:{rule}")
        # face pages
        faces = {}
        for k, short in (("IS", r"operations|income|earnings"), ("BS", r"balance sheet|financial (position|condition)"), ("CF", r"cash flow")):
            for rid, sn, gt in role2.values():
                if gt == "statement" and re.search(short, sn, re.I) and not re.search(r"parenthetical|comprehensive", sn, re.I):
                    pg = page(cik, acc, rid + ".htm")
                    if pg:
                        faces[k] = (rid + ".htm", pg)
                        break
        is_tags = {x["tag"].split(":")[-1] for x in (faces.get("IS", ("", {"rows": []}))[1]["rows"])}
        bank = bool(is_tags & BANK_TAGS) or any(INS_RX.search(t) for t in is_tags)
        # R5: banks / insurers: the six data points outside the template group are OUT unless printed
        if bank:
            for dp in OUT6:
                r = by.get(dp)
                if r and r["status"] == "not_presented":
                    change(r, "bank_insurer_out", status="OUT")
        # R2: InterestPaid includes capitalized interest -> combined (DQC_0065: the data point is InterestPaidNet)
        r = by.get("cash_paid_for_interest")
        if r and r["tags"].endswith(":InterestPaid") and r["status"] == "mapped":
            change(r, "interest_paid_gross_combined", status="combined")
        # R3: share counts on NOTE pages scaled by the dollar scale
        for dp in ("weighted_basic_shares", "weighted_diluted_shares", "shares_outstanding"):
            r = by.get(dp)
            try:
                p0, a0 = float(r["fy0_printed"]), float(r["fy0_api"])
            except (TypeError, ValueError, KeyError):
                continue
            for f in (1e3, 1e6):
                if a0 and abs(p0 / a0 - f) < 1e-6:
                    p1 = float(r["fy1_printed"]) / f if r.get("fy1_printed") else ""
                    change(r, "share_count_unscaled", fy0_printed=int(round(p0 / f)), fy1_printed=int(round(p1)) if p1 != "" else "", match="Y")
        # R8: weighted shares printed per class (same tag, several rows) -> class sum
        if "IS" in faces:
            rf, pg = faces["IS"]
            cols = dm.pick_cols(pg, "IS") or [0]
            for dp, tag in (("weighted_basic_shares", "us-gaap:WeightedAverageNumberOfSharesOutstandingBasic"),
                            ("weighted_diluted_shares", "us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding")):
                r = by.get(dp)
                cls = [x for x in pg["rows"] if x["tag"] == tag and cols[0] < len(x["vals"]) and x["vals"][cols[0]] is not None]
                vals = [x["vals"][cols[0]] for x in cls]
                if r and r["stmt"] != "NOTE" and len(cls) >= 2 and len(set(vals)) == len(vals) and not r["fy0_api"]:
                    tot = sum(vals) * pg.get("shares_scale", 1)
                    change(r, "share_classes_summed", status="component sum", fy0_printed=int(round(tot)), label=f"{len(cls)} class rows on {rf}")
        # R6: SG&A is G&A + S&M when a selling / marketing line is printed
        r = by.get("sga_expense")
        if r and r["tags"].endswith(":GeneralAndAdministrativeExpense") and "IS" in faces:
            rf, pg = faces["IS"]
            sm = [x for x in pg["rows"] if re.search(r"SellingAndMarketingExpense|MarketingExpense|SellingExpense|MarketingAndAdvertisingExpense", x["tag"])
                  and any(v is not None for v in x["vals"])]
            if sm:
                flags.append(f"sga_expense: G&A mapped while {sm[0]['tag']} '{sm[0]['label'][:40]}' is printed on {rf} -> component sum G&A + S&M (hand)")
        # R1: total_debt includes finance leases (never operating leases)
        r = by.get("total_debt")
        if r and fy0 and r["status"] in ("mapped", "component sum"):
            has_lease = re.search(r"Lease|Capital", r["tags"]) or re.search(r"lease", r["label"], re.I)
            flc, fln, flt = (fx(cf, t, acc, fy0) for t in ("FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent", "FinanceLeaseLiability"))
            in_debt_note = any(DEBT_NOTE.search(sn) for t in ("FinanceLeaseLiability", "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent")
                               for _, sn, _ in pages_of(t))
            if not has_lease and (flc or fln or flt):
                if in_debt_note:
                    flags.append(f"total_debt: finance leases ({flt or (flc or 0) + (fln or 0)}) appear on a debt note page: check whether the face debt includes them (hand)")
                else:
                    add = (flc or 0) + (fln or 0) if (flc or fln) else flt
                    src = sorted({rid for t in ("FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent", "FinanceLeaseLiability") for rid, _, _ in pages_of(t)})
                    try:
                        new0 = int(float(r["fy0_printed"])) + int(add)
                    except ValueError:
                        new0 = ""
                    tags = r["tags"] + ("+us-gaap:FinanceLeaseLiabilityCurrent+us-gaap:FinanceLeaseLiabilityNoncurrent" if (flc or fln) else "+us-gaap:FinanceLeaseLiability")
                    change(r, "finance_leases_added", status="component sum", tags=tags, fy0_printed=new0,
                           fy0_api=(int(float(r["fy0_api"])) + int(add)) if r["fy0_api"] else "", fy1_printed="", fy1_api="",
                           r_page=r["r_page"] + "+" + "+".join(s + ".htm" for s in src[:2]))
                    flags.append(f"total_debt: finance leases {int(add)} added from {src[:2]} (verify, hand)")
        # flags: sources that are not the company's own statements
        for r in rows:
            if r["stmt"] == "NOTE":
                rid = r["r_page"].split(".")[0]
                sn = next((v[1] for v in role2.values() if v[0] == rid), "")
                if BAD_SRC.search(sn):
                    flags.append(f"{r['data_point']}: NOTE source {r['r_page']} '{sn[:50]}' is not the company's own consolidated figure (hand)")
        # flags: not_presented / missing lines next to a matching printed label
        LAB = {"capex": ("CF", r"purchases? of (property|fixed|equipment)|capital expenditure|additions to property"),
               "dividends_paid": ("CF", r"dividend"), "share_buybacks": ("CF", r"repurchase|treasury"),
               "stockholders_equity": ("BS", r"total .*equity"), "total_debt": ("BS", r"debt|borrowing|notes payable")}
        for dp, (k, rx) in LAB.items():
            r = by.get(dp)
            if r and r["status"] == "not_presented" and k in faces:
                hit = [x for x in faces[k][1]["rows"] if re.search(rx, x["label"], re.I) and any(v is not None for v in x["vals"])]
                if hit:
                    flags.append(f"{dp}: not_presented but {faces[k][0]} prints '{hit[0]['label'][:50]}' ({hit[0]['tag']}) (hand)")
        if "CF" in faces:
            cap = [x for x in faces["CF"][1]["rows"] if x["tag"].split(":")[-1] in CAPEX_TAGS and any(v is not None for v in x["vals"])]
            if len({x["tag"] for x in cap}) >= 2:
                flags.append(f"capex: {len(cap)} capex-tag lines on {faces['CF'][0]} ({', '.join(x['label'][:25] for x in cap[:3])}) (hand)")
        if "BS" in faces and by.get("total_debt"):
            used = set(by["total_debt"]["tags"].replace("+", ";").split(";"))
            extra = [x for x in faces["BS"][1]["rows"] if re.search(r"\bdebt\b|borrowing|notes payable|loans? payable|commercial paper", x["label"], re.I)
                     and x["tag"] not in used and any(v is not None for v in x["vals"]) and not re.search(r"Abstract$|Axis$|Member$", x["tag"])
                     and not re.search(r"issuance|interest|lease", x["label"], re.I)]
            if extra:
                flags.append(f"total_debt: BS line(s) not in the sum: " + "; ".join(f"'{x['label'][:40]}' {x['tag']}" for x in extra[:3]) + " (hand)")
        with open(os.path.join(odir, f"{tk}-docmap-2026-11-12.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
        open(os.path.join(odir, f"{tk}-docmap-2026-11-12.md"), "w").write(md)
        print(json.dumps({"ticker": tk, "bank_or_insurer": bank, "changes": changes, "flags": flags}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
