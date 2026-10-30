"""Open a company's latest 10-K (else latest 10-Q) face statements through FilingSummary + R-files and return rows with
tags and labels. Reader 1 style (regex on the R-file HTML); good enough for shape classification, NOT used as audit evidence."""
import re, sys, json, html
sys.path.insert(0, "/Users/vikash/wt-sector-groups/data-team/strategy/tools/groups_v2")
import sec


def latest_filing(cik10: str):
    sub = sec.get_json(f"https://data.sec.gov/submissions/CIK{cik10}.json")
    if not sub:
        return None, None
    rec = sub["filings"]["recent"]
    best = {}
    for form, acc, fd, rd, pdoc in zip(rec["form"], rec["accessionNumber"], rec["filingDate"], rec["reportDate"], rec["primaryDocument"]):
        if form in ("10-K", "10-K405", "10-KT", "10-Q") and form not in best:
            best[form] = (acc, fd, rd, form)
    pick = best.get("10-K") or best.get("10-KT")
    q = best.get("10-Q")
    # prefer the 10-K unless a later 10-Q is the only periodic filing (no 10-K yet)
    return sub, (pick or q), (q if pick else None)


def reports(cik10: str, acc: str):
    nd = acc.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{nd}/"
    t = sec.get(base + "FilingSummary.xml")
    if not t:
        return base, []
    out = []
    for m in re.finditer(r"<Report[^>]*>(.*?)</Report>", t, re.S):
        blk = m.group(1)
        sn = re.search(r"<ShortName>(.*?)</ShortName>", blk, re.S)
        fn = re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", blk, re.S)
        if sn and fn:
            out.append((html.unescape(sn.group(1)).strip(), fn.group(1).strip()))
    return base, out


BS_RX = re.compile(r"balance sheet|financial condition|financial position|assets and liabilities|statements? of condition", re.I)
IS_RX = re.compile(r"(income|operations|earnings|profit or loss|loss)\b", re.I)
CF_RX = re.compile(r"cash flow", re.I)
BAD = re.compile(r"parenthetical|details|tables?\b|policies|narrative|schedule|note|disclosure|reconcil|segment|per share|supplement", re.I)


def pick_statements(reps):
    bs = is_ = cf = None
    for sn, fn in reps[:30]:
        if BAD.search(sn):
            continue
        if bs is None and BS_RX.search(sn) and not CF_RX.search(sn):
            bs = (sn, fn)
        elif is_ is None and IS_RX.search(sn) and not BS_RX.search(sn) and not CF_RX.search(sn) and not re.search(r"^comprehensive income|^statements? of comprehensive", sn, re.I) :
            is_ = (sn, fn)
        elif cf is None and CF_RX.search(sn):
            cf = (sn, fn)
    if is_ is None:  # combined "operations and comprehensive income" or comprehensive-only statement as the only income statement
        for sn, fn in reps[:30]:
            if not BAD.search(sn) and re.search(r"comprehensive|income|operations|earnings", sn, re.I) and not BS_RX.search(sn) and not CF_RX.search(sn):
                is_ = (sn, fn); break
    return bs, is_, cf


def parse_r(htmltxt: str):
    """rows: (tag, label, first_value_text). Footnote cells (class th with <sup>) are dropped before positional parsing."""
    rows = []
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", htmltxt, re.S):
        tr = m.group(1)
        lab = re.search(r'<td class="pl[^"]*"[^>]*>(.*?)</td>', tr, re.S)
        if not lab:
            continue
        lt = lab.group(1)
        tag = re.search(r"defref_([A-Za-z0-9\-]+_[A-Za-z0-9]+)", lt)
        label = html.unescape(re.sub(r"<[^>]+>", "", lt)).strip()
        vals = re.findall(r'<td class="(?:nump|num|text)[^"]*"[^>]*>(.*?)</td>', tr, re.S)
        v = ""
        for x in vals:
            x = html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
            if x:
                v = x; break
        rows.append((tag.group(1) if tag else "", label, v))
    title = re.search(r"<th[^>]*class=\"tl\"[^>]*>(.*?)</th>", htmltxt, re.S)
    return rows


def read_company(cik10: str):
    sub, pick, q = latest_filing(cik10)
    if not sub:
        return {"err": "no_submissions"}
    res = {"cik": cik10, "name": sub.get("name"), "sic": sub.get("sic"), "sicDescription": sub.get("sicDescription"),
           "tickers": sub.get("tickers"), "formerNames": sub.get("formerNames", [])[:3]}
    if not pick:
        res["err"] = "no_periodic_filing"
        return res
    acc, fd, rd, form = pick
    res.update({"acc": acc, "filed": fd, "period": rd, "form": form})
    base, reps = reports(cik10, acc)
    res["n_reports"] = len(reps)
    bs, is_, cf = pick_statements(reps)
    res["bs"], res["is"], res["cf"] = bs, is_, cf
    ls = {"BS": [], "IS": [], "CF": []}
    rawrows = {}
    for key, st in (("BS", bs), ("IS", is_), ("CF", cf)):
        if st:
            t = sec.get(base + st[1])
            if t:
                rows = parse_r(t)
                rawrows[key] = rows
                ls[key] = [(tg.split("_", 1)[1] if "_" in tg else tg, True, lb, 0, i) for i, (tg, lb, v) in enumerate(rows)]
    res["rows"] = rawrows
    res["ls"] = ls
    return res
