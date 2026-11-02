"""Cash-flow face lines of chosen companies, every FSN set, straight from sec.gov (stdlib, run with -I).
Read-only analysis input: for one FSN set, download the set's zip (one request, SEC_USER_AGENT), keep the
periodic filings of the given CIKs (sub) and their cash-flow face rows (pre: stmt CF, inpth 0), delete the zip.
Output: <out>/<set>.jsonl.gz, one line per face row with the filing's form/period/fy/fp/filed (cf_face_rows.py's
row shape plus `fsn`). Used to classify the FSN-store gap keys by what each filing actually prints.
usage: fsn_sec_cf_faces.py <out_dir> <ciks.txt> <set> [<set> ...]   (env SEC_USER_AGENT)
"""
import gzip
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fsn_sec_fixture import download, rows, set_url  # noqa: E402

FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT"}  # cf_face_rows.FORMS
STD = ("us-gaap", "srt", "dei", "ifrs")


def scan(out, ciks, fsn_set):
    import zipfile

    dest = Path(out) / f"{fsn_set}.jsonl.gz"
    if dest.exists():
        return
    with tempfile.TemporaryDirectory() as tmp:
        z = Path(tmp) / "z.zip"
        download(set_url(fsn_set), z)
        with zipfile.ZipFile(z) as zf:
            subs = {r["adsh"]: r for r in rows(zf, "sub") if int(r["cik"]) in ciks and r["form"] in FORMS}
            n = 0
            with gzip.open(str(dest) + ".part", "wt") as fo:
                for r in rows(zf, "pre"):
                    s = subs.get(r["adsh"])
                    if s is None or r["stmt"] != "CF" or r["inpth"] != "0":
                        continue
                    fo.write(json.dumps({
                        "adsh": r["adsh"], "cik": f"{int(s['cik']):010d}", "form": s["form"], "period": s["period"],
                        "filed": s["filed"], "fy": s["fy"], "fp": s["fp"], "report": int(r["report"]),
                        "line": int(r["line"]), "tag": r["tag"], "custom": not r["version"].startswith(STD),
                        "label": r["plabel"], "negating": r["negating"] == "1", "fsn": fsn_set}) + "\n")
                    n += 1
                # filings with no cash-flow face row at all are recorded too (an empty face is evidence)
                for a, s in subs.items():
                    fo.write(json.dumps({"adsh": a, "cik": f"{int(s['cik']):010d}", "form": s["form"], "period": s["period"],
                                         "filed": s["filed"], "fy": s["fy"], "fp": s["fp"], "filing_only": True, "fsn": fsn_set}) + "\n")
    Path(str(dest) + ".part").rename(dest)
    print(fsn_set, len(subs), "filings", n, "face rows", flush=True)


if __name__ == "__main__":
    out, ciks_path, sets = sys.argv[1], sys.argv[2], sys.argv[3:]
    Path(out).mkdir(parents=True, exist_ok=True)
    ciks = {int(x) for x in open(ciks_path).read().split()}
    for s in sets:
        scan(out, ciks, s)
