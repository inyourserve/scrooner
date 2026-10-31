"""Lean FSDS pass for era detection (stdlib, run with -I): from one FSDS
quarter zip, write the face presentation rows of the selected CIKs' 10-K/10-Q
filings (tag, report, line, label) as JSONL. No values; the fingerprint later
comes from the ordered family tags per filing.
usage: fsds_debt_pre.py <quarter.zip> <out.jsonl[.gz]> <cik-list-or-@file> [stmts=BS] [numdims_out.jsonl.gz]
  stmts: comma list of FSDS statement codes to keep (BS, CF, IS, ...), or ALL
  cik list may be @path to a file with one 10-digit CIK per line
  numdims_out: also write num.txt rows for the kept filings' BS tags that
  carry dimension members (the API strips these; mezzanine class-of-stock
  lines live here) - instants only, slim
"""
import csv
import gzip
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


def opener(path, mode):
    return gzip.open(path, mode + "t") if str(path).endswith(".gz") else open(path, mode)


def main(zpath, out, ciks, stmts="BS", numdims_out=None):
    keep_all = stmts == "ALL"
    stmts = set(stmts.split(","))
    if ciks.startswith("@"):
        ciks = {line.strip() for line in open(ciks[1:]) if line.strip()}
    else:
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
    bs_tags = set()
    with opener(out, "a") as o:
        for ix, r in rows(z, "pre.txt"):
            a = r[ix["adsh"]]
            if a in subs and (keep_all or r[ix["stmt"]] in stmts) and r[ix["inpth"]] == "0":
                if r[ix["stmt"]] == "BS":
                    bs_tags.add((a, r[ix["tag"]]))
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
    nd = 0
    if numdims_out:
        with opener(numdims_out, "a") as o:
            for ix, r in rows(z, "num.txt"):
                a = r[ix["adsh"]]
                if (a, r[ix["tag"]]) in bs_tags and r[ix["segments"]] and r[ix["qtrs"]] == "0":
                    o.write(
                        json.dumps(
                            {"adsh": a, "cik": subs[a]["cik"], "tag": r[ix["tag"]],
                             "ddate": r[ix["ddate"]], "uom": r[ix["uom"]],
                             "dims": r[ix["segments"]], "value": r[ix["value"]]}
                        ) + "\n"
                    )
                    nd += 1
    print(zpath.rsplit("/", 1)[-1], "filings", len(subs), "pre_rows", n, "dim_rows", nd)


main(*sys.argv[1:6])
