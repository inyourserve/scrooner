"""Cut test fixtures straight from the SEC FSN data sets (stdlib, run with -I; zstd CLI for the period layout).

For one FSN set (2016q2, 2024q4, ...) download the set's zip from sec.gov (one request, SEC_USER_AGENT
declared), keep only the selected filings' rows, delete the zip. Rows are copied, never edited. Writes both
layouts the lane code reads, from the SAME rows, so cohort mode and company mode see identical inputs:
  <out>/periods/<set>/<set>_{sub,pre,num,cal}.tsv.zst   the bucket layout (cf_face_rows / cf_num_rows / cf_cal_rows)
  <out>/companies/<cik10>/{sub,pre,num,cal,tag,dim,ren}.tsv   FORMATS-v1 section 1 (sub has fsn_set first),
                                                              appended across sets
Selectors: an accession (0000320193-24-000123), or cik:FORM (320193:10-K = every 10-K of that CIK in the set).
num keeps the non-dimensional rows and the one-axis rows (dimn <= 1: the quarterly-data axis EPS reads); tag
and dim keep what the kept rows reference.
usage: fsn_sec_fixture.py <out> <set> <selector> [selector ...]   (env SEC_USER_AGENT)
"""
import csv
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

csv.field_size_limit(1 << 24)
BASE = "https://www.sec.gov/files/dera/data/financial-statement-notes-data-sets/"
TABLES = ("sub", "pre", "num", "cal", "tag", "dim", "ren")
FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT", "10-KT/A", "10-QT/A"}


def set_url(fsn_set):
    if "m" in fsn_set:  # monthly sets since 2025m10: 2025_10_notes.zip
        y, m = fsn_set.split("m")
        return f"{BASE}{y}_{int(m):02d}_notes.zip"
    return f"{BASE}{fsn_set}_notes.zip"


def download(url, dest):
    ua = os.environ.get("SEC_USER_AGENT")
    if not ua:
        raise SystemExit("SEC_USER_AGENT is required (doc 07)")
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=1800) as r, open(dest, "wb") as fo:
        while chunk := r.read(1 << 20):
            fo.write(chunk)
    time.sleep(0.25)  # <= 4 requests per second


def rows(zf, name):
    with zf.open(f"{name}.tsv") as fh:
        yield from csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline=""),
                                  delimiter="\t", quoting=csv.QUOTE_NONE)


def write(path, cols, recs, append=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not (append and path.exists())
    with open(path, "a" if append else "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\", lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(recs)


def main(out, fsn_set, selectors):
    out = Path(out)
    adshs = {s for s in selectors if ":" not in s}
    by_cik = {(int(s.split(":")[0]), s.split(":")[1]) for s in selectors if ":" in s}
    with tempfile.TemporaryDirectory() as tmp:
        z = Path(tmp) / f"{fsn_set}.zip"
        download(set_url(fsn_set), z)
        with zipfile.ZipFile(z) as zf:
            data, cols = {}, {}
            subs = []
            for r in rows(zf, "sub"):
                if r["adsh"] in adshs or ((int(r["cik"]), r["form"]) in by_cik and r["form"] in FORMS):
                    subs.append(r)
            keep = {r["adsh"] for r in subs}
            data["sub"] = subs
            for t in ("pre", "num", "cal", "ren"):
                data[t] = [r for r in rows(zf, t) if r["adsh"] in keep and (t != "num" or int(r["dimn"] or 0) <= 1)]
            tags = {(r["tag"], r["version"]) for t in ("pre", "num") for r in data[t]}
            tags |= {(r[f"{p}tag"], r[f"{p}version"]) for r in data["cal"] for p in ("p", "c")}
            data["tag"] = [r for r in rows(zf, "tag") if (r["tag"], r["version"]) in tags]
            dims = {r["dimh"] for r in data["num"]}
            data["dim"] = [r for r in rows(zf, "dim") if r["dimhash"] in dims]
            for t in TABLES:
                with zf.open(f"{t}.tsv") as fh:
                    cols[t] = fh.readline().decode().rstrip("\r\n").split("\t")
    # bucket layout: one period directory, zstd like the bucket extracts
    pdir = out / "periods" / fsn_set
    for t in ("sub", "pre", "num", "cal"):
        p = pdir / f"{fsn_set}_{t}.tsv"
        write(p, cols[t], data[t])
        subprocess.run(["zstd", "-q", "-f", "--rm", str(p)], check=True)
    # company layout (FORMATS-v1 section 1), appended across sets
    for cik in sorted({int(r["cik"]) for r in data["sub"]}):
        d = out / "companies" / f"{cik:010d}"
        mine = {r["adsh"] for r in data["sub"] if int(r["cik"]) == cik}
        write(d / "sub.tsv", ["fsn_set", *cols["sub"]],
              [{"fsn_set": fsn_set, **r} for r in data["sub"] if r["adsh"] in mine], append=True)
        for t in ("pre", "num", "cal", "ren"):
            write(d / f"{t}.tsv", cols[t], [r for r in data[t] if r["adsh"] in mine], append=True)
        ctags = {(r["tag"], r["version"]) for t in ("pre", "num") for r in data[t] if r["adsh"] in mine}
        ctags |= {(r[f"{p}tag"], r[f"{p}version"]) for r in data["cal"] if r["adsh"] in mine for p in ("p", "c")}
        write(d / "tag.tsv", cols["tag"], [r for r in data["tag"] if (r["tag"], r["version"]) in ctags], append=True)
        cdims = {r["dimh"] for r in data["num"] if r["adsh"] in mine}
        write(d / "dim.tsv", cols["dim"], [r for r in data["dim"] if r["dimhash"] in cdims], append=True)
        m = d / "manifest.json"
        man = json.loads(m.read_text()) if m.exists() else {"cik": f"{cik:010d}", "fsn_sets": [], "accessions": [],
                                                               "source": "sec.gov FSN data sets via fsn_sec_fixture.py"}
        man["fsn_sets"] = sorted(set(man["fsn_sets"]) | {fsn_set})
        man["accessions"] = sorted(set(man["accessions"]) | mine)
        m.write_text(json.dumps(man, indent=1) + "\n")
    print(fsn_set, {t: len(data[t]) for t in TABLES}, sorted(keep))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
