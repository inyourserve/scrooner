"""Income-statement lane reader for one company directory of the FSN store
(stdlib, run with -I). Format: data-team/47-fsn-store/FORMATS-v1.md section 1
(companies/<cik10>/{sub,pre,num,cal,ren,tag,dim}.tsv.zst + manifest.json, raw
SEC FSN columns; sub has a first column fsn_set).

read_is_inputs(dir) gives the detector's inputs in exactly the shape the
cohort pass builds them (fsn_is_pre.py's sub_record / pre_record /
cal_record, shared, not copied), so is_detect and is_not_presented run
unchanged on one company:
  rows  {adsh: [IS/CI face rows]}   filings of THIS cik only, forms fsn_is_pre.FORMS
  arcs  {adsh: {parent: {child: weight}}}
  aciks {adsh} filings that name co-registrants (FSN sub.aciks non-empty)
A filing where this company is only a co-registrant (filed under another
CIK) is that filer's filing and is read from the filer's directory.
"""
import csv
import io
import json
import subprocess
from collections import defaultdict
from pathlib import Path

from fsn_is_pre import FORMS, cal_record, pre_record, sub_record

csv.field_size_limit(1 << 24)
TABLES = ("sub", "pre", "num", "cal", "ren", "tag", "dim")


def table(d, name):
    """dict rows of one table, SEC column names; .tsv.zst (store) or .tsv."""
    p = Path(d) / f"{name}.tsv.zst"
    if p.exists():
        proc = subprocess.Popen(["zstd", "-dc", str(p)], stdout=subprocess.PIPE)
        fh = io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace", newline="")
        yield from csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
        proc.wait()
        if proc.returncode:
            raise SystemExit(f"zstd failed on {p}")
        return
    with open(Path(d) / f"{name}.tsv", encoding="utf-8", errors="replace", newline="") as fh:
        yield from csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)


def company_cik(d):
    m = Path(d) / "manifest.json"
    if m.exists():
        return json.load(open(m))["cik"].zfill(10)
    return Path(d).name.zfill(10)


def company_dir_list(arg):
    """a company directory, a parent directory of them, or @file of paths."""
    if arg.startswith("@"):
        return [line.strip() for line in open(arg[1:]) if line.strip()]
    p = Path(arg)
    if (p / "sub.tsv.zst").exists() or (p / "sub.tsv").exists():
        return [str(p)]
    return sorted(str(c) for c in p.iterdir() if c.is_dir())


def read_is_inputs(d):
    cik = company_cik(d)
    subs, aciks = {}, set()
    for r in table(d, "sub"):
        if r["cik"].zfill(10) == cik and r["form"] in FORMS:
            subs[r["adsh"]] = sub_record(r)
            if (r.get("aciks") or "").strip():
                aciks.add(r["adsh"])
    rows = defaultdict(list)
    for r in table(d, "pre"):
        s = subs.get(r["adsh"])
        row = pre_record(r, s) if s is not None else None
        if row is not None:
            rows[r["adsh"]].append(row)
    arcs = defaultdict(lambda: defaultdict(dict))
    for r in table(d, "cal"):
        if r["adsh"] in rows:
            a = cal_record(r)
            arcs[a["adsh"]][a["p"]][a["c"]] = a["w"]
    return rows, arcs, aciks
