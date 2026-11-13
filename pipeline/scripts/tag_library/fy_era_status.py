"""Per-year status rows FY2015 to latest (Engineering split 2026-11-13: era back-extension of tagged rows is Engineering's;
the per-year status rows and the face-check OPEN periods are the map's). fy_status_rows.py wrote status rows for FY0/FY-1
only, from the latest 10-K read; a status is never carried back to an older year. Each older cell that no map row covers
is decided on that year's OWN 10-K (latest accepted 10-K for the period that prints all three face statements). The FSN
store holds the statement pages only, so the notes are checked through the filing's XBRL facts (core.fact, the companyfacts
copy: standard-taxonomy facts of every page, notes included; custom-tag note facts are not in it):
  1. a candidate tag of the data point on a statement line of that filing -> GAP (a value exists: a concept row is missing)
  2. else a candidate tag among the filing's XBRL facts                   -> GAP note_fact (printed in a note)
  3. else a combined tag spanning the data point                          -> not_in_template, line_presented_combined_with_others
  4. else a label candidate (own statement, or a custom tag anywhere)     -> GAP for review (never a reason)
  5. else, when the filing has XBRL facts at all                          -> not_presented on every statement and in the facts
No 10-K in the FSN store, or no XBRL facts for the filing: no row (counted). A cell that already serves a value (cells.csv
shown_value, e.g. a later 10-K's restated comparative under another tag) never gets a reason row: GAP served_value. Candidate tags are every tag the map serves the concept with,
for any company (the map was built from the FSN history since 2015), plus the combined tags whose components name it.
Usage: fy_era_status.py <tag_map.csv> <cells.csv> <filings.csv> <lines.csv> <facts.csv> <concepts_catalog.csv> <out_map.csv> <out_gaps.csv>
cells.csv: company_id,data_point,period_end (top100-coverage.csv works); filings/lines/facts: fy_era_extract.py."""
import collections
import csv
import re
import sys

SKIP = {"total_debt", "comprehensive_income", "net_interest_income"}  # debt lane / Engineering rule / bank-only reads
STMT = {"income_statement": "IS", "balance_sheet": "BS", "cash_flow": "CF"}
OWN = {"IS": {"IS", "CI"}, "BS": {"BS"}, "CF": {"CF"}}
EQ_TOO = {"dividends_paid", "dividends_per_share", "share_buybacks", "shares_outstanding"}  # also printed on the equity statement
LABEL = {
    "revenue": r"\brevenues?\b|\bnet sales\b|\bsales\b", "cost_of_revenue": r"\bcosts? of (revenues?|sales|goods|products|services)",
    "gross_profit": r"gross (profit|margin)", "operating_expenses": r"operating (costs and )?expenses",
    "sga_expense": r"selling|general and administrative", "research_and_development": r"research",
    "operating_income": r"operating (income|profit|loss|earnings)|(income|earnings|loss) from operations",
    "interest_expense": r"interest expense", "interest_income": r"interest (and dividend )?income",
    "other_income_expense_net": r"other (income|expense|\(income\)|non-?operating)", "income_before_tax": r"before (provision for )?(income )?tax",
    "income_tax_expense": r"income tax", "net_income": r"^net (income|earnings|loss|\(loss\))",
    "basic_eps": r"basic", "diluted_eps": r"dilut", "weighted_basic_shares": r"weighted", "weighted_diluted_shares": r"weighted",
    "cash_and_equivalents": r"cash and (cash )?equivalents", "accounts_receivable": r"receivable", "inventory": r"inventor",
    "current_assets": r"total current assets", "ppe_net": r"property|plant|equipment", "goodwill": r"goodwill",
    "total_assets": r"total assets", "accounts_payable": r"accounts payable|trade payables", "current_liabilities": r"total current liabilities",
    "total_liabilities": r"total liabilities", "stockholders_equity": r"(stockholders|shareholders|shareowners|share owners)['’]? equity",
    "cfo": r"operating activities", "cash_flow_investing": r"investing activities", "cash_flow_financing": r"financing activities",
    "capex": r"capital expenditure|(purchases?|additions?|acquisitions?|payments?) (of|to|for) property",
    "depreciation_and_amortization": r"depreciation", "amortization_of_intangibles": r"amortization of .*intangible",
    "sbc": r"(stock|share|equity)[- ]based compensation|stock compensation", "dividends_paid": r"dividend",
    "dividends_per_share": r"dividends? (declared |paid )?per", "share_buybacks": r"repurchase|treasury|buyback",
    "shares_outstanding": r"shares outstanding|outstanding shares", "cash_paid_for_interest": r"interest paid|paid for interest",
    "cash_paid_for_income_taxes": r"taxes paid|paid for (income )?taxes", "cf_ar_change": r"receivable", "cf_ap_change": r"payable",
    "cf_inventory_change": r"inventor",
}
LABEL = {k: re.compile(v, re.I) for k, v in LABEL.items()}


def base(c):
    return {"revenue_sanity_resolved": "revenue"}.get(c, c.removesuffix("_resolved"))


def candidates(rows):
    """{data_point: tags that serve it} and {data_point: combined tags spanning it}, from every company's map rows."""
    serve, comb = collections.defaultdict(set), collections.defaultdict(set)
    for r in rows:
        if not r["tag"]:
            continue
        if r["decision"] == "concept" and r["canonical_concept"]:
            serve[base(r["canonical_concept"])].add(r["tag"])
        elif r["decision"] == "component" and r["parent_concept"]:
            serve[base(r["parent_concept"])].add(r["tag"])
        elif r["decision"] == "combined":
            for k in (r["components"] or "").split(";"):
                if k and k != "other":
                    comb[base(k)].add(r["tag"])
    if "EarningsPerShareBasicAndDiluted" in serve.get("basic_eps", set()) | serve.get("diluted_eps", set()):
        serve["basic_eps"].add("EarningsPerShareBasicAndDiluted")
        serve["diluted_eps"].add("EarningsPerShareBasicAndDiluted")
    return serve, comb


def covered(rows):
    """{(company, data_point): [(from, to)]} for every map row that serves or reasons the cell."""
    cov = collections.defaultdict(list)
    for r in rows:
        con = r["canonical_concept"] if r["decision"] in ("concept", "not_presented", "not_in_template") else \
            r["parent_concept"] if r["decision"] == "component" else ""
        if con:
            cov[(r["company_id"], base(con))].append((r["era_from"], r["era_to"]))
        if r["decision"] == "combined":
            for k in (r["components"] or "").split(";"):
                if k and k != "other":
                    cov[(r["company_id"], base(k))].append((r["era_from"], r["era_to"]))
    return cov


def own_filing(filings, company, period):
    """The period's own 10-K: latest accepted with all three face statements, period within 10 days of the FY end."""
    def days(a, b):
        y1, m1, d1 = map(int, a.split("-"))
        y2, m2, d2 = map(int, b.split("-"))
        return abs((y1 * 372 + m1 * 31 + d1) - (y2 * 372 + m2 * 31 + d2))
    ok = [f for f in filings.get(company, []) if f["faces"] == "3" and days(f["period"], period) <= 10]
    return max(ok, key=lambda f: f["accepted"]) if ok else None


def acc(a):
    return a.replace("-", "")


def decide(dp, stmt, lines, facts, serve, comb):
    """(kind, detail): kind GAP / note_fact / combined / review / not_presented / no_facts for one data point on one filing's
    statement lines and XBRL fact tags (facts None: the filing has no facts)."""
    hit = [x for x in lines if x["tag"] in serve.get(dp, ())]
    if hit:
        return "GAP", hit[0]
    if facts is None:
        return "no_facts", None
    tag = next((t for t in sorted(serve.get(dp, ())) if t in facts), None)
    if tag:
        return "note_fact", {"rfile": "", "report": "", "line": "", "stmt": "fact", "tag": tag, "plabel": ""}
    hit = [x for x in lines if x["tag"] in comb.get(dp, ())]
    if hit:
        return "combined", hit[0]
    own = OWN.get(stmt, set()) | ({"EQ"} if dp in EQ_TOO else set())
    rx = LABEL.get(dp)
    hit = [x for x in lines if rx and (x["stmt"] in own or x["custom"] == "t") and rx.search(x["plabel"] or "")]
    if hit:
        return "review", hit[0]
    return "not_presented", None


def main(tm, cells, fil, lin, fct, cc, out, gaps_out):
    rows = list(csv.DictReader(open(tm)))
    cols = list(rows[0])
    rows = [r for r in rows if r["decided_by"] != "fy_era_status"]  # rerun-safe
    cat = {base(r["name"]): STMT.get(r["statement"], "IS") for r in csv.DictReader(open(cc))}
    serve, comb = candidates(rows)
    cov = covered(rows)
    meta, names = {}, {}
    for r in rows:
        meta.setdefault(r["company_id"], r)
        if r["canonical_concept"]:
            names.setdefault((r["company_id"], base(r["canonical_concept"])), r["canonical_concept"])
    filings = collections.defaultdict(list)
    for f in csv.DictReader(open(fil)):
        filings[f["company_id"]].append(f)
    lines = collections.defaultdict(list)
    for x in csv.DictReader(open(lin)):
        lines[x["accession"]].append(x)
    facts = collections.defaultdict(set)
    for x in csv.DictReader(open(fct)):
        facts[acc(x["accession"])].add(x["tag"])
    new, gaps, counts, seen = [], [], collections.Counter(), set()
    for c in csv.DictReader(open(cells)):
        cid, dp, p = c["company_id"], c["data_point"], c["period_end"]
        if cid not in meta or dp in SKIP or (cid, dp, p) in seen or p < "2015-01-01":
            continue
        seen.add((cid, dp, p))
        if any(a <= p <= b for a, b in cov.get((cid, dp), [])):
            continue
        f = own_filing(filings, cid, p)
        if not f:
            counts["no_10k_in_fsn"] += 1
            continue
        stmt = cat.get(dp, "IS")
        if c.get("shown_value"):
            counts["served_value"] += 1
            gaps.append({"company_id": cid, "ticker": meta[cid].get("ticker", ""), "data_point": dp, "period": p, "kind": "served_value",
                         "accession": f["accession"], "report": "", "line": "", "stmt": "", "tag": c.get("tag", ""), "plabel": c["shown_value"]})
            continue
        kind, x = decide(dp, stmt, lines.get(f["accession"], []), facts.get(acc(f["accession"])), serve, comb)
        counts[kind] += 1
        m = meta[cid]
        if kind == "no_facts":
            continue
        if kind in ("GAP", "note_fact", "review"):
            gaps.append({"company_id": cid, "ticker": m.get("ticker", ""), "data_point": dp, "period": p, "kind": kind,
                         "accession": f["accession"], "report": x["rfile"] or x["report"], "line": x["line"], "stmt": x["stmt"],
                         "tag": x["tag"], "plabel": x["plabel"]})
            continue
        e = {k: "" for k in cols}
        e.update(company_id=cid, cik=m.get("cik", ""), rank=m.get("rank", ""), ticker=m.get("ticker", ""), stmt=stmt,
                 canonical_concept=names.get((cid, dp), dp),
                 era_from=p, era_to=p, decided_by="fy_era_status", rule_id="tagmap.fy_era_status@1", evidence_adsh=f["accession"],
                 lines="0", filings="1")
        if kind == "combined":
            e.update(decision="not_in_template", reason_class="line_presented_combined_with_others", evidence_report=x["rfile"] or x["report"],
                     evidence_line=x["line"], evidence_plabel=x["plabel"],
                     reason=f"{p}: the period's own 10-K {f['accession']} prints {dp} only inside {x['tag']} ('{x['plabel']}')")
        else:
            e.update(decision="not_presented", reason_class="not_presented_statements_and_xbrl_facts",
                     reason=f"{p}: the period's own 10-K {f['accession']} carries none of the {dp} tags ({len(serve.get(dp, ()))}) on any "
                            f"statement or among its XBRL facts (notes included), and no {dp} label on its {stmt} statement or on a custom tag")
        new.append(e)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows + new)
    with open(gaps_out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["company_id", "ticker", "data_point", "period", "kind", "accession", "report", "line", "stmt", "tag", "plabel"])
        w.writeheader()
        w.writerows(gaps)
    print("fy era status rows", len(new), "| cells", dict(counts))


if __name__ == "__main__":
    main(*sys.argv[1:9])
