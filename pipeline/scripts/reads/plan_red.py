"""Plan the red cells of ranks 61-80 (Dhairya 2026-11-13): one record per cell with the filing to open, the tag(s), the
period and the companyfacts value for that filing; and the fetch request (FilingSummary + statement pages +
MetaLinks.json per accession). usage: plan_red.py red.csv shards.csv red1_dir out_plan.json out_request.csv"""
import csv, gzip, json, re, sys
from datetime import date
from pathlib import Path

red, shards, d1, plan_out, req_out = sys.argv[1:6]
SKIP = {"weighted_basic_shares", "weighted_diluted_shares", "cash_paid_for_income_taxes", "cash_paid_for_interest"}
INSTANT = {"cash_and_equivalents", "accounts_receivable", "inventory", "current_assets", "ppe_net", "goodwill", "total_assets",
           "accounts_payable", "current_liabilities", "total_liabilities", "total_debt", "stockholders_equity", "shares_outstanding"}
ACC = re.compile(r"\d{10}-\d\d-\d{6}")
cik_of = {r["ticker"]: r["cik"] for r in csv.DictReader(open(shards)) if (r["rank"] or "").isdigit()}
rows = [r for r in csv.DictReader(open(red)) if 61 <= int(r["rank"]) <= 80 and r["data_point"] not in SKIP and (
    r["cause"].startswith("value in the filing") or r["cause"].startswith("no filing-matched") or r["cause"].startswith("proof DISAGREE"))]
facts = {}


def cf(t):
    if t not in facts:
        p = Path(d1) / cik_of[t] / "companyfacts.json.gz"
        facts[t] = json.loads(gzip.decompress(p.read_bytes()))["facts"] if p.exists() else {}
    return facts[t]


def tenk_end(t):
    """accession -> (FY0 end, filed) for 10-K/10-KT filings (max end of annual duration facts)."""
    key = ("_tk", t)
    if key in facts:
        return facts[key]
    out = {}
    for node in cf(t).get("us-gaap", {}).values():
        for lst in node.get("units", {}).values():
            for x in lst:
                if x.get("form") not in ("10-K", "10-KT", "10-K/A") or "start" not in x:
                    continue
                e, s = date.fromisoformat(x["end"]), date.fromisoformat(x["start"])
                if 340 <= (e - s).days <= 380:
                    cur = out.get(x["accn"])
                    if not cur or e > cur[0]:
                        out[x["accn"]] = (e, x["filed"], x["form"])
    facts[key] = out
    return out


def cf_vals(t, tag, end, inst):
    """[(accn, value)] for the tag at the period from 10-K filings."""
    tax, name = (tag.split(":") + [""])[:2] if ":" in tag else ("us-gaap", tag)
    node = cf(t).get(tax, {}).get(name, {})
    out = []
    for lst in node.get("units", {}).values():
        for x in lst:
            if x.get("form") not in ("10-K", "10-KT", "10-K/A") or x["end"] != end:
                continue
            if inst != ("start" not in x):
                continue
            if not inst and not 340 <= (date.fromisoformat(x["end"]) - date.fromisoformat(x["start"])).days <= 380:
                continue
            out.append((x["accn"], x["val"]))
    return out


plan, need = [], {}
for r in rows:
    t, dp, end = r["ticker"], r["data_point"], r["period_end"]
    inst = dp in INSTANT
    rec = {k: r[k] for k in ("rank", "ticker", "data_point", "fiscal_year", "period_end", "cause", "fix", "evidence")}
    rec["kind"] = "a" if r["cause"].startswith("value") else ("b" if r["cause"].startswith("no filing") else "c")
    if rec["kind"] == "a":
        m = re.match(r"(\d{10}-\d\d-\d{6}) (\S+) (\S+) = ?(-?[\d.]*)", r["evidence"])
        rec.update(accession=m.group(1), stmt_hint=m.group(2), tags=m.group(3).split(";"), queue_value=m.group(4),
                   status_hint=re.search(r"prints it as (\S+)", r["cause"]).group(1))
    elif rec["kind"] == "c":
        m = re.match(r"(\d{10}-\d\d-\d{6}) (\S+) shown ?(-?[\d.]*)", r["evidence"])
        rec.update(accession=m.group(1), tags=["us-gaap:" + m.group(2)], queue_value=m.group(3), stmt_hint="", status_hint="mapped")
    else:
        m = re.search(r"nearest (\d{10}-\d\d-\d{6}) \((\S+)\): (\S+) ?(\S*)", r["evidence"])
        rec.update(status_hint=m.group(3), tags=[x for x in m.group(4).split(";") if x], nearest=m.group(1), stmt_hint="")
        # the next 10-K: the filing whose FY0 ends after this period and carries the tag at this period (comparative)
        tk = tenk_end(t)
        cands = []
        for tag in rec["tags"] or []:
            for accn, val in cf_vals(t, tag, end, inst):
                if accn in tk:
                    cands.append((tk[accn][0], tk[accn][1], accn, tag, val))
        later = sorted(c for c in cands if c[0] > date.fromisoformat(end))
        same = sorted(c for c in cands if c[0] == date.fromisoformat(end))
        pick = later[0] if later else (same[0] if same else None)
        if pick:
            rec.update(accession=pick[2], cf_value=pick[4], cf_tag=pick[3], comparative=bool(later))
        else:
            # no companyfacts value under the tag: the next 10-K by date (to read its face)
            nxt = sorted((e, f, a) for a, (e, f, form) in tk.items() if e > date.fromisoformat(end) and form != "10-K/A")
            rec.update(accession=nxt[0][2] if nxt else "", cf_value=None, comparative=bool(nxt))
    if rec.get("accession"):
        need.setdefault((cik_of[t], t, rec["accession"]), 0)
        need[(cik_of[t], t, rec["accession"])] += 1
    plan.append(rec)
json.dump(plan, open(plan_out, "w"), indent=0, default=str)
with open(req_out, "w") as f:
    f.write("cik,ticker,accession,statements,extras,pages\n")
    for (c, t, a) in sorted(need):
        if not (Path(d1) / c / a / "FilingSummary.xml").exists():
            f.write(f"{c},{t},{a},1,0,MetaLinks.json\n")
        else:
            f.write(f"{c},{t},{a},0,0,MetaLinks.json\n")
import collections
print(len(plan), "cells;", len(need), "accessions;", collections.Counter(p["kind"] for p in plan),
      "no accession:", sum(1 for p in plan if not p.get("accession")))
