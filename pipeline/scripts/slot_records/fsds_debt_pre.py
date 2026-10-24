"""Lean FSDS pass for era detection (stdlib, run with -I): from one FSDS
quarter zip, write the face presentation rows of the selected CIKs' 10-K/10-Q
filings (tag, report, line, label) as JSONL. No values; the fingerprint later
comes from the ordered family tags per filing.
usage: fsds_debt_pre.py <quarter.zip> <out.jsonl> <cik,cik,...> [stmts=BS]
  stmts: comma list of FSDS statement codes to keep (BS, CF, IS, ...)
"""
import csv
import io
import json
import sys
import zipfile

csv.field_size_limit(1 << 24)
FORMS = {"10-K", "10-K/A", "10-KT", "10-Q", "10-Q/A", "10-QT"}


def rows(z, name):
    with z.open(name) as f:
        rd = csv.reader(
            io.TextIOWrapper(f, encoding="utf-8", errors="replace", newline=""),
            delimiter="\t",
            quoting=csv.QUOTE_NONE,
        )
        hdr = next(rd)
        ix = {h: i for i, h in enumerate(hdr)}
        for r in rd:
            if len(r) >= len(hdr) - 1:
                yield ix, r + [""] * (len(hdr) - len(r))


def main(zpath, out, ciks, stmts="BS"):
    stmts = set(stmts.split(","))
    ciks = {c.strip() for c in ciks.split(",")}
    z = zipfile.ZipFile(zpath)
    subs = {}
    for ix, r in rows(z, "sub.txt"):
        if r[ix["cik"]].zfill(10) in ciks and r[ix["form"]] in FORMS:
            subs[r[ix["adsh"]]] = {
                "cik": r[ix["cik"]].zfill(10),
                "form": r[ix["form"]],
                "period": r[ix["period"]],
                "filed": r[ix["filed"]],
            }
    n = 0
    with open(out, "a") as o:
        for ix, r in rows(z, "pre.txt"):
            a = r[ix["adsh"]]
            if a in subs and r[ix["stmt"]] in stmts and r[ix["inpth"]] == "0":
                o.write(
                    json.dumps(
                        {
                            "adsh": a,
                            **subs[a],
                            "report": int(r[ix["report"]]),
                            "line": int(r[ix["line"]]),
                            "stmt": r[ix["stmt"]],
                            "tag": r[ix["tag"]],
                            "custom": r[ix["version"]] == a,
                            "label": r[ix["plabel"]],
                        }
                    )
                    + "\n"
                )
                n += 1
    print(zpath.rsplit("/", 1)[-1], "filings", len(subs), "bs_rows", n)


main(*sys.argv[1:5])
