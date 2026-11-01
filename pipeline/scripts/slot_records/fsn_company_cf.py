"""Cash-flow lane reader for one company directory of the FSN store (stdlib, run with -I).
Format: data-team/47-fsn-store/FORMATS-v1.md section 1.

read_cf_inputs(dir) returns (filings, face, vals, arcs, durps) in exactly the shapes
cf_family_replay.load() builds from the three cohort files, with the same filters:
  filings/face  cf_face_rows.py: this CIK's periodic filings (its FORMS), stmt CF, inpth 0; custom =
                version not in the standard namespaces; then cf_family_replay.primary_face
  vals/durps    cf_num_rows.py: tags on that filing's cash-flow face, qtrs 1-4, USD, no dimension,
                no co-registrant, iprx 0; first row wins (setdefault), as in load()
  arcs          cf_cal_rows.py: common.fsn_cal_arcs's cash-flow group (CashFlow#), weights as Decimal
A filing that appears in two FSN sets keeps its first set's sub row (cf_face_rows' `seen`).
"""
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402
from cf_family_replay import CASH_CHANGE_RX, OP_CONT, OP_TOTAL, primary_face  # noqa: E402
from fsn_company import company_cik, table  # noqa: E402

FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT"}  # cf_face_rows.FORMS
STD = ("us-gaap", "srt", "dei", "ifrs")  # cf_face_rows.STD
NO_DIM = "0x00000000"  # cf_num_rows.NO_DIM


def read_cf_inputs(d):
    d = Path(d)
    cik = company_cik(d)
    subs = {}
    for r in table(d, "sub"):
        if r["cik"].zfill(10) == cik and r["form"] in FORMS and r["adsh"] not in subs:
            subs[r["adsh"]] = r
    filings, face, face_tags = {}, defaultdict(list), defaultdict(set)
    for r in table(d, "pre"):
        s = subs.get(r["adsh"])
        if s is None or r["stmt"] != "CF" or r["inpth"] != "0":
            continue
        filings[r["adsh"]] = {"cik": cik, "form": s["form"], "period": s["period"], "filed": s["filed"],
                              "fy": s["fy"], "fp": s["fp"], "fsn": s["fsn_set"]}
        face[r["adsh"]].append((int(r["report"]), int(r["line"]), r["tag"], r["plabel"],
                                not r["version"].startswith(STD), r["negating"] == "1"))
        face_tags[r["adsh"]].add(r["tag"])
    primary_face(face)
    vals, durps = defaultdict(dict), defaultdict(dict)
    for r in table(d, "num"):
        tags = face_tags.get(r["adsh"])
        if not tags or r["tag"] not in tags or r["qtrs"] not in ("1", "2", "3", "4"):
            continue
        if r["uom"] != "USD" or r["value"] in ("", None) or r.get("dimh", NO_DIM) != NO_DIM:
            continue
        if (r.get("coreg") or "").strip() or (r.get("iprx") or "0") not in ("0", ""):
            continue
        q = int(r["qtrs"])
        vals[r["adsh"]].setdefault((r["tag"], r["ddate"], q), Decimal(r["value"]))
        if r.get("durp") not in (None, "") and (r["tag"] in (OP_TOTAL, OP_CONT) or CASH_CHANGE_RX.search(r["tag"])):
            durps[r["adsh"]].setdefault((r["ddate"], q), float(r["durp"]))
    cal = d / "cal.tsv.zst" if (d / "cal.tsv.zst").exists() else d / "cal.tsv"
    arcs = {}
    for adsh in face:
        got = common.fsn_cal_arcs(cal, adsh)
        arcs[adsh] = {p: [(c, Decimal(w)) for c, w, _cu in kids] for (role, p), kids in got.items() if role.startswith("CashFlow#")}
    common._FSN_CAL_CACHE.pop(str(cal), None)  # one company in memory at a time
    return filings, face, vals, arcs, durps
