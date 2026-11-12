"""Per-company full 10-K reads (Verifier, filing-checked) -> one status file. Usage: parse_reads.py <reads_dir> <cohort.csv> <out.csv>"""
import csv, glob, os, re, sys
rd, cohort, out = sys.argv[1:4]
tick = {r["ticker"]: r for r in csv.DictReader(open(cohort))}
rows = []
for f in sorted(glob.glob(os.path.join(rd, "*-read-2026-11-12.md"))):
    t = os.path.basename(f).split("-read-")[0]
    txt = open(f).read()
    m = re.search(r"(?im)^## [^\n]*data points[^\n]*$", txt)
    if not m:
        continue
    head, body = txt[:m.start()], txt[m.end():]
    acc = re.findall(r"\b(\d{10}-\d{2}-\d{6})\b", head)
    for ln in body.split("\n## ")[0].splitlines():
        if not ln.startswith("| ") or ln.startswith("| data point") or ln.startswith("|---"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) >= 7:
            dp, ours, printed, pval, sval, verdict, reason = c[:7]
        elif len(c) == 6:
            dp, ours, printed, sval, verdict, reason = c
            pval = printed
        else:
            continue
        dp_base = re.sub(r"\s*\(.*\)$", "", dp).strip()
        tags = re.findall(r"\b((?:us-gaap|[a-z]{2,5}):[A-Z][A-Za-z0-9]+)", printed + " " + reason)
        rpage = (re.findall(r"\b(R\d+)(?:\.htm)?\b", printed) or [""])[0]
        not_printed = bool(re.search(r"(?i)^not printed|no .* printed|not on (the )?face", printed + " " + pval)) and not re.search(r"\d{2,}", pval)
        rows.append({"ticker": t, "company_id": tick.get(t, {}).get("company_id", ""), "data_point": dp_base, "verdict": verdict.upper(),
                     "our_status": ours[:120], "printed_tag": tags[0] if tags else "", "r_page": rpage, "printed_label": printed[:140],
                     "printed_value": pval[:80], "not_printed": not_printed, "evidence_adsh": acc[0] if acc else "", "reason": reason[:300]})
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
import collections
print(len(rows), "rows,", len({r["ticker"] for r in rows}), "companies;", collections.Counter(r["verdict"] for r in rows).most_common(8))
