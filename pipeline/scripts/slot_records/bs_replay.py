"""Replay BS-totals records: anchors + the accounting identity as cross-check.

For each company: compute total_liabilities per its record rule (printed total
or face-sum of skeleton members), equity_parent, nci, mezzanine, at every
instant; identity check |Assets - (L + mezz + equity_incl_nci)| <= tolerance.
Rules inherited: periodic-only facts, authoritative-first, missing member =
hard stop (custom -> needs_instance_reader), no production-derived verdicts.
usage: DATABASE_URL=... bs_replay.py <bs_records.jsonl> <anchors.json> <out.json>
"""
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal

import psycopg
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).parent))
import common  # noqa: E402

records = defaultdict(list)
for line in open(sys.argv[1]):
    r = json.loads(line)
    records[r["cik"]].append(r)
anchors = json.loads(open(sys.argv[2]).read())["anchors"]

# Optional 4th arg: instance-reader evidence JSONL (instance_reader.py). Custom
# member values the API never carries are taken from the filing's OWN instance,
# same accession as the cell (never from another filing), undimensioned
# context only. Rows: {cik, adsh, tag, period_type, end, value, unit, decimals}.
instance_evidence = defaultdict(dict)  # (adsh, end) -> tag -> Decimal   (undimensioned)
instance_dim_sum = defaultdict(lambda: defaultdict(Decimal))  # (adsh, end) -> tag -> sum over dimension members
instance_dim_members = defaultdict(lambda: defaultdict(list))
instance_rows = 0
if len(sys.argv) > 4 and os.path.exists(sys.argv[4]):
    for line in open(sys.argv[4]):
        r = json.loads(line)
        if r.get("period_type") != "instant" or r.get("value") in (None, "") or (r.get("unit") or "USD") != "USD":
            continue
        try:
            v = Decimal(r["value"])
        except Exception:  # noqa: BLE001
            continue
        key = (r["adsh"], r["end"])
        if r.get("dims"):
            # a face line tagged per member of ONE axis (class of stock): the
            # face total is the sum of the members of that axis. In a 10-K the
            # same preferred appears under two axes (TRGP 2021-12-31: 749.7M
            # twice), so members are grouped per axis and ONE axis is used
            # (StatementClassOfStockAxis first, else the axis with most members).
            # Used only for MEZZANINE slots whose undimensioned value is
            # absent; the identity gate still has to tie.
            if r["dims"].count("=") == 1:
                axis, member = r["dims"].split("=", 1)
                instance_dim_members[key][r["tag"]].append((axis, member, v))
            continue
        instance_evidence[key].setdefault(r["tag"], v)
        instance_rows += 1
for key, bytag in instance_dim_members.items():
    for tag, rows in bytag.items():
        per_axis = defaultdict(dict)
        for axis, member, v in rows:
            per_axis[axis].setdefault(member, v)
        axis = "StatementClassOfStockAxis" if "StatementClassOfStockAxis" in per_axis else max(per_axis, key=lambda a: len(per_axis[a]))
        instance_dim_sum[key][tag] = sum(per_axis[axis].values(), Decimal(0))
        instance_dim_members[key][tag] = [f"{axis}={m}" for m in per_axis[axis]]

conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
report = {"anchor_results": [], "identity": defaultdict(int), "per_company": {}}

EXTRA = ["Assets", "Liabilities", "StockholdersEquity", "MinorityInterest",
         "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
         "PartnersCapital", "LiabilitiesAndStockholdersEquity",
         "TemporaryEquityCarryingAmountAttributableToParent",
         "RedeemableNoncontrollingInterestEquityCarryingAmount", "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests"]


def fetch(cik, tags):
    """SAME-ACCESSION inputs (shared common.fetch_instants) plus custom-tag values
    from the same accession's instance (instance reader evidence)."""
    facts = common.fetch_instants(cur, cik, tags)
    for e, day in facts.items():
        acc = day["__accession__"]
        for tag, v in instance_evidence.get((acc, e), {}).items():
            if tag not in day:
                day[tag] = v
                day.setdefault("__instance_filled__", []).append(tag)
        for tag, v in instance_dim_sum.get((acc, e), {}).items():
            if tag in mezz_tags and tag not in day:
                day[tag] = v
                day.setdefault("__dim_mezz__", set()).add(tag)
                day.setdefault("__instance_filled__", []).append(f"{tag}[dims:{len(instance_dim_members[(acc, e)][tag])}]")
    return facts


mezz_tags = {m["tag"] for rs in records.values() for r in rs for m in r["mezzanine_face"]} | {
    t for rs in records.values() for r in rs for t in (r.get("mezzanine_dim_tags") or [])}


def rounding_unit(day):
    """The filer's rounding unit at this instant (shared common.rounding_unit)."""
    return common.rounding_unit([v for k, v in day.items() if not k.startswith("__")])


def covering(cik, end):
    ym = end[:7]
    rec = next((r for r in records[cik] if r["period_from"][:7] <= ym <= r["period_to"][:7]), None)
    if rec is None and end[8:10] <= "03":
        # FSDS month-rounds 52/53-week ends like 2019-01-01 to the prior
        # month (AJG anchor); fall back to the previous month's record
        import datetime
        d = datetime.date.fromisoformat(end).replace(day=1) - datetime.timedelta(days=1)
        ym = str(d)[:7]
        rec = next((r for r in records[cik] if r["period_from"][:7] <= ym <= r["period_to"][:7]), None)
    return rec


MEZZ_FALLBACK = ("TemporaryEquityCarryingAmountAttributableToParent",
                 "RedeemableNoncontrollingInterestEquityCarryingAmount",
                 "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests")


def identity(rec, day, liab):
    """assets - (L + mezzanine + equity incl. NCI) on ONE filing, and the
    filer's rounding unit as tolerance. A face-sum value is PUBLISHED only when
    this ties (Verifier BS-V1: never produce a value beside a flagged gap; the
    identity is the gate, never the source of the value)."""
    # Equity (incl. NCI) read two ways from the filer's own lines: the
    # including-NCI total, and parent equity + NCI. FE 2018-03-31 carries a
    # stray 86M 'including NCI' fact beside a correct 7,375M equity line, so
    # a tie against EITHER reading is accepted (both are the filer's totals).
    cands = []
    for t in ("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
              "PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest"):
        if day.get(t) is not None:
            cands.append(day[t])
    eq_p = day.get(rec["equity_parent_tag"] or "StockholdersEquity")
    if eq_p is not None:
        # NCI under the filer's own face tag (ET 2026-06-30: 15.2B of
        # noncontrolling interest not under MinorityInterest), else MinorityInterest
        nci = day.get(rec.get("nci_tag") or "MinorityInterest")
        if nci is None:
            nci = day.get("MinorityInterest") or Decimal(0)
        cands.append(eq_p + nci)
        if nci:
            # census 2026-10-25 (Carlyle): the filer's 'total partners' capital'
            # line already INCLUDES the noncontrolling interests it also prints,
            # so the parent line alone is the third reading
            cands.append(eq_p)
    if not cands:
        cands.append(Decimal(0))
    # mezzanine ONLY from the record's own face lines (Verifier BS-V2 fix 4:
    # the tag fallback subtracted GE's 408M RedeemableNoncontrollingInterest
    # note value, which is not a face line, and flagged 12 right values)
    # face mezzanine lines, plus the record's dimensioned mezzanine tags (FSDS
    # dims extract) for eras whose face list omits the line (TRGP 2016-12-31,
    # 2018-03-31: Series A preferred tagged only per class of stock)
    face_tags = {m["tag"] for m in rec["mezzanine_face"]}
    dim_only = set(rec.get("mezzanine_dim_tags") or []) - face_tags
    # census 2026-10-25 (698 companies): (1) a filer may tag the SAME
    # mezzanine line twice (ADS: RedeemableNoncontrollingInterest...Common and
    # TemporaryEquity...IncludingNCI both 78,252K) - identical values at one
    # instant are one line; (2) the face mezzanine line's value may sit under
    # a variant tag of the same family (SUI face 'TemporaryEquity', value under
    # TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrolling
    # Interests) - when the face line has no value, a same-accession fact of a
    # recorded dimension tag stands in for it.
    seen_vals = {}
    for t in sorted(face_tags):
        v = day.get(t)
        if v is None:
            continue
        if v in seen_vals.values():
            continue  # same line tagged twice
        seen_vals[t] = v
    if face_tags and not seen_vals:
        for t in sorted(dim_only):
            if day.get(t) is not None:
                seen_vals[t] = day[t]
                break
    # census 2026-10-25 (Vornado 623.8 = 619.3 + 4.5; ADS): a mezzanine TOTAL
    # line printed with its components - when one value equals the sum of the
    # others it is the total and counts once
    vals = list(seen_vals.values())
    for v in vals:
        if len(vals) > 1 and abs(sum(vals) - v - v) <= Decimal(1):
            vals = [v]
            break
    # Verifier census check (ADS over-count): when a mezzanine TOTAL element
    # ('...IncludingPortionAttributableToNoncontrollingInterests' or
    # 'TemporaryEquityCarryingAmount...') is printed beside component lines,
    # the total alone is the mezzanine
    # ... but ET 2015-17 prints two DISTINCT mezzanine items (redeemable NCI 15M
    # beside a 'TemporaryEquity...' line), so the total-only reading is an
    # ALTERNATIVE the identity may tie against, never an override.
    totals = [t for t in seen_vals if "IncludingPortionAttributableToNoncontrollingInterest" in t or t.startswith("TemporaryEquityCarryingAmount")]
    mezz = sum(vals, Decimal(0))
    mezz_total_only = seen_vals[totals[0]] if (len(seen_vals) > 1 and len(totals) == 1) else None
    # a dimension-only mezzanine tag, when the face has NO mezzanine line at
    # all, counts ONLY with its per-class value read from the same accession's
    # instance, never with an undimensioned API fact of the same name (GE:
    # RedeemableNoncontrollingInterestEquityCarryingAmount 408M is a note
    # value, not a face line; Verifier BS-V2 fix 4). For a PRINTED-TOTAL record
    # (cross-check only, nothing withheld) the plain API value is tried as a
    # second reading, so a face value the FSDS face list missed (JEF 406K,
    # Alexandria 12-14M) does not show as a false gap.
    if not face_tags:
        mezz += sum(day[t] for t in dim_only if t in day.get("__dim_mezz__", set()))
    mezz_alt = None
    if not face_tags and rec["total_liabilities_rule"] == "printed_total":
        api_dims = [day[t] for t in dim_only if t in day and t not in day.get("__dim_mezz__", set())]
        if api_dims:
            mezz_alt = mezz + max(api_dims)
    # Right-hand side total: the filer's own 'total liabilities and equity'
    # line (Verifier BS-V1 rule), else total assets. BRKR 2019-03-31 prints
    # assets 2,242.5M against a liabilities side of 2,242.3M: its own face
    # does not tie to assets, but ties to its L&E total exactly.
    rhs = day.get("LiabilitiesAndStockholdersEquity", day["Assets"])
    mezz_readings = [mezz] + ([mezz_alt] if mezz_alt is not None else []) + (
        [mezz_total_only] if mezz_total_only is not None else [])
    gaps = [rhs - (liab + m + e) for m in mezz_readings for e in cands]
    gap = min(gaps, key=abs)
    return gap, rounding_unit(day)


def alt_readings(rec, day, liab):
    """Reading A = all cal roots (liab). Reading B = roots minus the lines a
    taxonomy total (LiabilitiesCurrent / LiabilitiesNoncurrent) printed after
    them covers (TMUS, ALB: the filer's cal omits the total-to-components arc).
    Capitalization-format filers print long-term debt before current
    liabilities, so B is wrong for them and A is right: the identity decides."""
    covered = [m for m in rec["total_liabilities_members"] if m.get("tax_covered") and day.get(m["tag"]) is not None]
    if not covered:
        return [liab]
    return [liab, liab - sum(day[m["tag"]] for m in covered)]


def best_reading(rec, day, liab):
    """(value, gap, tol, reading) for the reading with the smallest identity gap."""
    best = None
    for i, v in enumerate(alt_readings(rec, day, liab)):
        gap, tol = identity(rec, day, v)
        if best is None or abs(gap) < abs(best[1]):
            best = (v, gap, tol, "A_cal_roots" if i == 0 else "B_taxonomy_total_covers")
    return best


def publishable(rec, day, liab):
    """None when the record demands an identity tie and no reading ties."""
    if liab is None or not rec.get("requires_identity_tie"):
        return liab
    v, gap, tol, _ = best_reading(rec, day, liab)
    return v if abs(gap) <= tol else None


def liab_value(rec, day):
    members = rec["total_liabilities_members"]
    if rec["total_liabilities_rule"].startswith("hold"):
        return None, ["__held__:" + rec["total_liabilities_rule"]], []
    if rec["total_liabilities_rule"] == "printed_total":
        v = day.get("Liabilities")
        return (v, [], []) if v is not None else (None, ["Liabilities"], [])
    tot, miss, miss_custom = Decimal(0), [], []
    for m in members:
        v = day.get(m["tag"])
        if v is not None:
            tot += v
        elif m.get("custom"):
            miss_custom.append(m["tag"])
        else:
            miss.append(m["tag"])
    return tot, miss, miss_custom


for cik in sorted(records):
    ticker = records[cik][0]["company"]
    tags = set(EXTRA)
    for r in records[cik]:
        tags.update(m["tag"] for m in r["total_liabilities_members"])
        tags.update(m["tag"] for m in r["mezzanine_face"])
        tags.update(r.get("mezzanine_dim_tags") or [])
        if r["equity_parent_tag"]:
            tags.add(r["equity_parent_tag"])
        if r.get("nci_tag"):
            tags.add(r["nci_tag"])
    tags.add("PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest")
    facts = fetch(cik, tags)
    stats = defaultdict(int)
    for end, day in sorted(facts.items()):
        if end < "2015-01-01":
            continue
        rec = covering(cik, end)
        if rec is None or "Assets" not in day:
            continue
        liab, miss, miss_custom = liab_value(rec, day)
        if miss_custom:
            stats["needs_instance_reader"] += 1
            continue
        if day.get("__instance_filled__"):
            stats["instance_filled"] += 1
        if liab is None:
            stats["not_computable"] += 1
            continue
        if miss:
            # Verifier BS-V2 fix 3: a standard member printed BLANK in this
            # column (DVN 2018-09-30 held-for-sale liabilities) is zero. Proof
            # that it is blank rather than unfetched: the identity ties without
            # it on the same filing. Otherwise the cell stays not computable.
            if rec["total_liabilities_rule"] == "face_sum" and "Assets" in day:
                g, t = identity(rec, day, liab)
                if abs(g) <= t:
                    stats["member_blank_in_column_identity_confirmed"] += 1
                    miss = []
            if miss:
                stats["not_computable"] += 1
                continue
        liab, gap, tol, reading = best_reading(rec, day, liab)
        key = "identity_ties" if abs(gap) <= tol else "identity_gap"
        stats[key] += 1
        if reading != "A_cal_roots" and key == "identity_ties":
            stats["reading_B_taxonomy_total"] += 1
        report["identity"]["ties" if key == "identity_ties" else "gaps"] += 1
        published = liab if (key == "identity_ties" or not rec.get("requires_identity_tie")) else None
        report.setdefault("cells", []).append({
            "ticker": ticker, "cik": cik, "end": end, "accession": day.get("__accession__"),
            "era_first": rec["filing_from"], "era_from": rec["period_from"], "era_to": rec["period_to"],
            "rule": rec["total_liabilities_rule"], "cal_source": rec.get("cal_source"), "reading": reading,
            "total_liabilities": str(published) if published is not None else None,
            "identity": key, "gap": str(gap), "tol": str(tol),
            "equity_parent": str(day.get(rec["equity_parent_tag"] or "StockholdersEquity")),
            "instance_filled": day.get("__instance_filled__", []),
            "boundary_instant": end[:7] == rec["period_from"][:7],
        })
        if key == "identity_gap" and rec.get("requires_identity_tie"):
            stats["withheld_identity_gap"] += 1  # face-sum value NOT published
            report.setdefault("withheld", []).append({
                "ticker": ticker, "end": end, "accession": day.get("__accession__"),
                "face_sum": str(liab), "gap": str(gap), "tol": str(tol),
                "rhs_lse": str(day.get("LiabilitiesAndStockholdersEquity")),
                "assets": str(day["Assets"]),
                "equity_parent": str(day.get(rec["equity_parent_tag"] or "StockholdersEquity")),
                "nci": str(day.get(rec.get("nci_tag") or "MinorityInterest")),
                "equity_incl": str(day.get("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest")),
                "mezz": {m["tag"]: str(day.get(m["tag"])) for m in rec["mezzanine_face"]},
                "members": {m["tag"]: str(day.get(m["tag"])) for m in rec["total_liabilities_members"]},
                "record_from": rec["period_from"], "cal_source": rec.get("cal_source"),
            })
        elif key == "identity_gap":
            stats["printed_total_identity_gap"] += 1  # filer's own total; gap is a cross-check finding
    report["per_company"][ticker] = dict(stats)
    for a in anchors:
        if a["ticker"] != ticker:
            continue
        end = a["period_end"]
        day = facts.get(end, {})
        rec = covering(cik, end)
        if rec is None:
            report["anchor_results"].append({**a, "result": "no_record"})
            continue
        if a.get("kind") == "equity_parent":
            got_v = day.get(rec["equity_parent_tag"] or "StockholdersEquity")
            miss, miss_custom = [], []
        else:
            got_v, miss, miss_custom = liab_value(rec, day)
            if miss and not miss_custom and got_v is not None and "Assets" in day \
                    and rec["total_liabilities_rule"] == "face_sum":
                g, t = identity(rec, day, got_v)
                if abs(g) <= t:
                    miss = []  # member blank in this column, identity-confirmed
            if miss or miss_custom:
                got_v = None  # partial sums are never a value (AWK leaked 7,599M)
            elif got_v is not None and "Assets" in day:
                got_v = publishable(rec, day, got_v)
                if got_v is None:
                    miss = ["__withheld__:identity_gap"]
        got = str(got_v) if got_v is not None else None
        tol = Decimal(a.get("tolerance", "1"))
        ok = (
            a.get("expected") is not None and got_v is not None
            and abs(got_v - Decimal(a["expected"])) <= tol
        )
        report["anchor_results"].append(
            {**a, "got": got, "missing": miss, "missing_custom": miss_custom,
             "result": "PASS" if ok else "CHECK"}
        )
conn.close()
report["identity"] = dict(report["identity"])
json.dump(report, open(sys.argv[3], "w"), indent=1, default=str)
print(json.dumps(report["identity"]))
for t, s in sorted(report["per_company"].items()):
    print(t, dict(s))
for w in report.get("withheld", []):
    print("WITHHELD", w["ticker"], w["end"], w["accession"], "face_sum", w["face_sum"], "gap", w["gap"],
          "tol", w["tol"], "lse", w["rhs_lse"], "A", w["assets"], "eq", w["equity_parent"], "nci", w["nci"],
          "eq_incl", w["equity_incl"], "mezz", w["mezz"], "cal", w["cal_source"])
    print("         members", w["members"])
print("--- anchors:")
for a in report["anchor_results"]:
    print(a["ticker"], a["period_end"], a.get("expected"), "->", a.get("got"), a["result"])
