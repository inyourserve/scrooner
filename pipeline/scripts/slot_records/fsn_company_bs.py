"""Balance-sheet lane reader for one company directory of the FSN store
(stdlib, run with -I). Format: data-team/47-fsn-store/FORMATS-v1.md section 1.

Gives the balance-sheet and total-debt detectors their inputs in exactly the
shape the cohort passes built them, so bs_totals_detect, era_detect,
bs_assemble, assemble_fsn and replay_debt_fsn run unchanged on one company:

  bs_pre_rows(d)   rows of fsds_debt_pre.py's cohort_pre_rows (stmt BS, inpth 0,
                   custom = version is the accession), filer's own filings
  bs_dim_rows(d)   rows of fsds_debt_pre.py's numdims_out (dimensional instants of
                   tags on that filing's BS face): adsh cik tag ddate uom dims value
  instants(d, debt_only)
                   filing objects of fsn_company_instants.py (all undimensioned USD
                   instants incl. notes + the BS face rows), same filters
  cal_path(d)      the company's cal table; common.fsn_cal_arcs reads it as it
                   reads a period's cal (same SEC columns)

Only filings whose sub.cik is this company are read (the cohort extracts took
the filer's own filings; a filing where it is only a co-registrant belongs to
the filer's directory). The table reader is fsn_company.table (shared).
"""
import re
from collections import defaultdict
from pathlib import Path

from fsn_company import company_cik, own_ciks, company_dir_list, table  # noqa: F401  (re-exported for the CLIs)

# fsds_debt_pre.FORMS == fsn_company_instants.FORMS (the cohort extracts' form filter)
FORMS = {"10-K", "10-K/A", "10-KT", "10-Q", "10-Q/A", "10-QT"}
STD = ("us-gaap", "srt", "dei", "ifrs")
NO_DIM = "0x00000000"
# fsn_company_instants.DEBT_VOCAB, unchanged
DEBT_VOCAB = re.compile(r"Debt|Borrow|Loan|Notes|CommercialPaper|Lease|LineOfCredit|Convertible|FinanceObligation|"
                        r"^Liabilities|^Assets$|LiabilitiesAndStockholdersEquity|LiabilitiesAndPartnersCapital")


def own_subs(d):
    """{adsh: sub row} for this company's own periodic filings, first fsn_set wins
    (an accession re-published in a later set is the same filing)."""
    cik = company_cik(d)
    own = own_ciks(d)
    subs = {}
    for r in table(d, "sub"):
        if r["cik"].zfill(10) in own and r["form"] in FORMS:
            # a predecessor's filing is this company's history: report it under the company's CIK
            subs.setdefault(r["adsh"], dict(r, cik=cik))
    return subs


def bs_pre_rows(d, subs=None):
    subs = own_subs(d) if subs is None else subs
    out = []
    for r in table(d, "pre"):
        s = subs.get(r["adsh"])
        if s is None or r["stmt"] != "BS" or r["inpth"] != "0":
            continue
        out.append({"adsh": r["adsh"], "cik": s["cik"].zfill(10), "form": s["form"], "period": s["period"],
                    "filed": s["filed"], "report": int(r["report"]), "line": int(r["line"]), "stmt": "BS",
                    "tag": r["tag"], "custom": r["version"] == r["adsh"], "label": r["plabel"]})
    return out


def bs_dim_rows(d, subs=None, pre=None):
    subs = own_subs(d) if subs is None else subs
    pre = bs_pre_rows(d, subs) if pre is None else pre
    bs_tags = {(r["adsh"], r["tag"]) for r in pre}
    segments = {r["dimhash"]: r["segments"] for r in table(d, "dim")}
    out = []
    for r in table(d, "num"):
        if r["dimh"] == NO_DIM or r["qtrs"] != "0" or (r["adsh"], r["tag"]) not in bs_tags:
            continue
        seg = segments.get(r["dimh"], "")
        if not seg:
            continue
        out.append({"adsh": r["adsh"], "cik": subs[r["adsh"]]["cik"].zfill(10), "tag": r["tag"], "ddate": r["ddate"],
                    "uom": r["uom"], "dims": seg, "value": r["value"]})
    return out


def instants(d, debt_only=False, subs=None):
    """fsn_company_instants.py's per-filing objects for this company, in filing (sub) order."""
    subs = own_subs(d) if subs is None else subs
    fil = {a: {"adsh": a, "cik": int(s["cik"]), "form": s["form"], "period": s["period"], "filed": s["filed"],
               "accepted": s.get("accepted") or "", "bs": [], "values": defaultdict(dict), "fsn_period": s["fsn_set"]} for a, s in subs.items()}
    for r in table(d, "pre"):
        if r["adsh"] in fil and r["stmt"] == "BS":
            fil[r["adsh"]]["bs"].append({"report": int(r["report"]), "line": int(r["line"]), "tag": r["tag"],
                                         "plabel": r["plabel"], "custom": not r["version"].startswith(STD)})
    for r in table(d, "num"):
        f = fil.get(r["adsh"])
        if f is None or r["qtrs"] != "0" or r["uom"] != "USD" or r["dimh"] != NO_DIM or r["value"] in ("", None):
            continue
        if (r.get("coreg") or "").strip() or (r.get("iprx") or "0") not in ("0", ""):
            continue
        if debt_only and not DEBT_VOCAB.search(r["tag"]) and r["tag"] not in f.setdefault("_face", {x["tag"] for x in f["bs"]}):
            continue
        f["values"][r["ddate"]][r["tag"]] = r["value"]
    out = []
    for f in fil.values():
        f.pop("_face", None)
        f["bs"].sort(key=lambda x: (x["report"], x["line"]))
        out.append(f)
    return out


def cal_path(d):
    p = Path(d) / "cal.tsv.zst"
    return p if p.exists() else Path(d) / "cal.tsv"


def debt_face_rows(filings):
    """era_detect.py's input (debt_fsn_inputs bs_pre_rows) from instants(d, debt_only=True)."""
    import debt_fsn_inputs as dfi
    return [row for f in filings for row in dfi.face_rows(f)]
