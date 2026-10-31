"""Replay income-statement slot records against companyfacts and production
(dry run, read-only, one connection). The verdict comes from the FILING,
never from production: production's value is carried only to list the
differences.

Per filing the slot (is_detect.py) names the printed line's tag. A value is a
FACE COLUMN of that filing only when its duration is one the form prints
(10-K: 12 months ending at the period or one / two years before; 10-Q:
3, 6 or 9 months ending at the period or one year before) and the fact sits
in THAT accession (companyfacts, never a derived fact, periodic forms only).
Quarterly-data notes in a 10-K (GE: the quarterly `Revenues` facts are GE
Capital's) are therefore never read.

Cell (start, end): the reference observation is the ORIGINAL filing (its
period of report is the end date; earliest filed), else the earliest filing
that prints the column. Every later filing that prints the same column under
a publishable gate is a copy; copies that disagree with the original beyond
the rounding unit make the cell `hide_restated_copies_disagree` (founder
ruling: restated periods whose copies disagree are hidden). Net income G2:
ProfitLoss - NCI lines = NetIncomeLoss on the reference accession within the
filer's rounding unit, else `hold_identity_gap`. A cell never comes from a
subtraction: production's derived Q4 cells are listed, not replaced.

usage: DATABASE_URL=... is_replay.py <is_filing_slots.jsonl> <cik-list|@file> <out_dir>
  writes <out_dir>/is_<family>_cells.jsonl and is_replay_summary.json
"""
import datetime as dt
import json
import os
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).parent))
from common import rounding_unit  # noqa: E402

FAMILIES = ("revenue", "operating_income", "net_income", "cost_of_revenue", "gross_profit")
PROD = {"revenue": "revenue_sanity_resolved", "operating_income": "operating_income_resolved",
        "net_income": "net_income_resolved", "cost_of_revenue": "cost_of_revenue_resolved",
        "gross_profit": "gross_profit_resolved"}
PUBLISHABLE = {"G1_printed_total", "G1_printed_line", "G2_nci_identity", "G1b_profit_loss_no_nci", "G3_calc_sum",
               "G2_gross_identity", "G2b_available_to_common_bridge"}
PERIODIC = ["10-K", "10-K/A", "10-KT", "10-Q", "10-Q/A", "10-QT"]
SINCE = "2015-01-01"


def unit_of(v, cap=Decimal(10) ** 11):
    """printed rounding unit of one value, uncapped up to 1e11 (production can
    show a later filing's billions; the shared rounding_unit caps at 1e6)."""
    return rounding_unit([v], cap=cap)


def d(s):
    return dt.date.fromisoformat(s)


def near(a, b, days=10):
    return abs((a - b).days) <= days


def year_back(x, n):
    try:
        return x.replace(year=x.year - n)
    except ValueError:
        return x.replace(year=x.year - n, day=28)


def face_column(form, period, s, e):
    days = (e - s).days + 1
    if form.startswith("10-K"):
        return 350 <= days <= 380 and any(near(e, year_back(period, n)) for n in (0, 1, 2))
    return any(lo <= days <= hi for lo, hi in ((80, 100), (170, 190), (260, 285))) and \
        any(near(e, year_back(period, n)) for n in (0, 1))


def is_q4_like(s, e):
    return 80 <= (e - s).days + 1 <= 100


def main(slots_path, ciks, out_dir, families=None):
    global FAMILIES
    if families:
        FAMILIES = tuple(families.split(","))
    if ciks.startswith("@"):
        ciks = [x.strip().zfill(10) for x in open(ciks[1:]) if x.strip()]
    else:
        ciks = [x.strip().zfill(10) for x in ciks.split(",")]
    want = set(ciks)
    slots = defaultdict(lambda: defaultdict(dict))  # cik -> family -> adsh -> slot
    for line in open(slots_path):
        s = json.loads(line)
        if s["cik"] in want:
            slots[s["cik"]][s["family"]][s["adsh"]] = s
    out = Path(out_dir)
    fh = {f: open(out / f"is_{f}_cells.jsonl", "w") for f in FAMILIES}
    summary = {f: Counter() for f in FAMILIES}
    conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20)
    conn.read_only = True
    cur = conn.cursor()
    cur.execute("set statement_timeout = '60s'")
    for n, cik in enumerate(ciks):
        tags = set()
        for fam in FAMILIES:
            for s in slots[cik][fam].values():
                if s.get("tag") and s["gate"] in PUBLISHABLE:
                    tags.add(s["tag"])
                if s.get("sum_tags"):
                    tags.update(s["sum_tags"])
                    tags.add(s["check_tag"])
                if s.get("alt"):
                    tags.add(s["alt"]["tag"])
                    tags.add(s["alt"]["tie"]["profit_loss"])
                    tags.update(s["alt"]["tie"]["nci"])
                if s.get("tie") and "nci" in s["tie"]:
                    tags.add(s["tie"]["profit_loss"])
                    tags.update(s["tie"]["nci"])
                elif s.get("tie"):
                    tags.update(s["tie"].values())
        facts = defaultdict(dict)  # accession -> {(tag, start, end): value}
        filing_meta = {}
        if tags:
            cur.execute(
                """
                select co.tag, p.start_date, p.end_date, f.value::numeric, fi.accession_number,
                       fi.period_of_report, fi.form
                from core.fact f
                join core.concept co on co.id = f.concept_id
                join core.period p on p.id = f.period_id
                join core.unit u on u.id = f.unit_id
                join core.company c on c.id = f.company_id
                join core.filing fi on fi.id = f.filing_id
                where c.cik = %s and p.period_type = 'duration' and co.taxonomy = 'us-gaap'
                  and u.unit_name = 'usd' and co.tag = any(%s) and p.end_date >= %s
                  and fi.form = any(%s) and f.is_derived = false
                order by f.is_authoritative desc, f.id desc
                """,
                (cik, sorted(tags), SINCE, PERIODIC),
            )
            for tag, s0, e0, v, acc, por, form in cur.fetchall():
                facts[acc].setdefault((tag, s0, e0), v)
                filing_meta[acc] = (por, form)
        cur.execute(
            """
            select cc.name, p.start_date, p.end_date, cf.value::numeric, cf.id,
                   sco.tag, sfi.accession_number, sf.is_derived, coalesce(array_length(cf.source_fact_ids, 1), 0)
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            join core.company c on c.id = cf.company_id
            left join core.fact sf on sf.id = cf.source_fact_ids[1]
            left join core.concept sco on sco.id = sf.concept_id
            left join core.filing sfi on sfi.id = sf.filing_id
            where c.cik = %s and cc.name = any(%s) and p.period_type = 'duration' and p.end_date >= %s
            """,
            (cik, list(PROD.values()), SINCE),
        )
        prod = defaultdict(dict)
        rev = {v: k for k, v in PROD.items()}
        for name, s0, e0, v, cfid, stag, sacc, sder, nsrc in cur.fetchall():
            # a production cell built from several facts is a computation: its first
            # source's tag is not the cell's tag (operating income = revenue - costs)
            prod[rev[name]][(s0, e0)] = {"value": v, "cf_id": cfid, "tag": stag if nsrc == 1 else f"computed({nsrc})",
                                         "accession": sacc, "derived": sder or nsrc > 1, "n_sources": nsrc}
        for fam in FAMILIES:
            obs = defaultdict(list)  # (start, end) -> [observation]
            for adsh, s in slots[cik][fam].items():
                period = d(s["period"])
                acc_facts = facts.get(adsh, {})
                # every face column this filing prints: from its own facts for the slot tag
                cols = {(k[1], k[2]) for k in acc_facts if k[0] == s.get("tag")}
                if s.get("alt") and not any(face_column(s["form"], period, a0, b0) for a0, b0 in cols):
                    # the printed NetIncomeLoss carries no undimensioned value (combined utility
                    # filing: it is the subsidiaries' columns): the parent's line is the G2b bridge
                    s = {**s, **s["alt"], "gate": "G2b_available_to_common_bridge"}
                    s.pop("alt", None)
                    cols = {(k[1], k[2]) for k in acc_facts if k[0] == s.get("tag")}
                # a non-publishable gate still claims the filing's face columns (from any slot tag fact or none)
                for (s0, e0) in cols:
                    if not face_column(s["form"], period, s0, e0):
                        continue
                    gate, value, extra = s["gate"], acc_facts[(s["tag"], s0, e0)], {}
                    if s.get("sum_tags"):
                        # G3: the printed lines summed (same accession, same column); every member
                        # must be present and the filer's own parent fact, when tagged, must tie
                        vals = [acc_facts.get((t, s0, e0)) for t in s["sum_tags"]]
                        if any(v is None for v in vals):
                            gate = "hold_sum_member_missing"
                            extra["missing"] = [t for t, v in zip(s["sum_tags"], vals) if v is None]
                        else:
                            value = sum(vals)
                            chk = acc_facts.get((s["check_tag"], s0, e0))
                            extra["members"] = {t: str(v) for t, v in zip(s["sum_tags"], vals)}
                            if chk is not None:
                                extra["check_value"] = str(chk)
                                if abs(chk - value) * 2 > max(unit_of(chk), unit_of(value)):
                                    gate = "hold_identity_gap"
                    obs[(s0, e0)].append({"adsh": adsh, "filed": s["filed"], "period": period, "form": s["form"],
                                          "gate": gate, "tag": s.get("tag") if not s.get("sum_tags") else "+".join(s["sum_tags"]),
                                          "label": s.get("label") if not s.get("sum_tags") else "Total revenues (sum of printed lines: " + s.get("label", "") + " + siblings)",
                                          "value": value, "tie": s.get("tie"),
                                          "extra": {**extra, "face_axis": s.get("face_axis", False)}})
                if s["gate"] in PUBLISHABLE and not any(near(e0, period, 3) and face_column(s["form"], period, s0, e0) for s0, e0 in cols):
                    obs[("held", period, s["form"][:4])].append({"adsh": adsh, "gate": "slot_fact_missing_in_companyfacts", "filed": s["filed"]})
                if s["gate"] not in PUBLISHABLE:
                    # held filing: claim the standard columns so production's cells there are classified
                    for back in (0, 1):
                        e0 = year_back(period, back)
                        obs[("held", e0, s["form"][:4])].append({"adsh": adsh, "gate": s["gate"], "filed": s["filed"]})
            held_ends = defaultdict(set)
            for k, v in obs.items():
                if k[0] == "held":
                    for o in v:
                        held_ends[k[1]].add(o["gate"])
            cells = {}
            for key, os_ in obs.items():
                if key[0] == "held":
                    continue
                s0, e0 = key
                os_.sort(key=lambda o: (not near(o["period"], e0, 3), o["filed"], o["adsh"]))
                ref = os_[0]
                cell = {"cik": cik, "family": fam, "start": s0.isoformat(), "end": e0.isoformat(),
                        "accession": ref["adsh"], "form": ref["form"], "slot_tag": ref["tag"], "label": ref["label"],
                        "gate": ref["gate"], "original": near(ref["period"], e0, 3), **(ref.get("extra") or {})}
                v = ref["value"]
                unit = rounding_unit([v])
                state = None
                if ref["gate"] not in PUBLISHABLE:
                    state = ref["gate"]
                elif ref["gate"] in ("G2_nci_identity", "G2b_available_to_common_bridge"):
                    t = ref["tie"]
                    af = facts.get(ref["adsh"], {})
                    pl = af.get((t["profit_loss"], s0, e0))
                    nci = [af.get((x, s0, e0)) for x in t["nci"]]
                    if ref["gate"] == "G2b_available_to_common_bridge" and (pl is None or any(x is None for x in nci)):
                        state = "hold_identity_unverified"  # G2b publishes only with the full bridge tied
                    elif pl is not None and any(x is not None for x in nci):
                        gap = pl - sum(x for x in nci if x is not None) - v
                        tol = rounding_unit([pl, v] + [x for x in nci if x is not None])
                        cell["identity_gap"] = str(gap)
                        if abs(gap) > tol:
                            state = "hold_identity_gap"
                elif ref["gate"] == "G2_gross_identity":
                    # revenue - cost = gross profit on the reference accession (all printed lines)
                    t = ref["tie"]
                    af = facts.get(ref["adsh"], {})
                    rv, cv, gv = (af.get((t[k], s0, e0)) for k in ("revenue", "cost", "gross_profit"))
                    if None not in (rv, cv, gv):
                        gap = rv - cv - gv
                        cell["identity_gap"] = str(gap)
                        # one printed unit, as for the balance-sheet and NCI identities: three
                        # independently rounded lines can miss by one unit (IBM, HRL)
                        if abs(gap) > max(unit_of(rv), unit_of(cv), unit_of(gv)):
                            state = "hold_identity_gap"
                if state is None:
                    copies = [o for o in os_[1:] if o["gate"] in PUBLISHABLE]
                    # a copy agrees only within HALF of the coarser printed unit (3,903 is not a
                    # rounding of 3,902.4; PGR FY2023)
                    bad = [o for o in copies if abs(o["value"] - v) * 2 > max(unit_of(v), unit_of(o["value"]))]
                    cell["copies"] = len(copies)
                    if bad:
                        state = "hide_restated_copies_disagree"
                        cell["copies_disagree"] = [{"accession": o["adsh"], "tag": o["tag"], "value": str(o["value"])} for o in bad[:4]]
                    else:
                        state = "slot_value"
                cell["slot_value"] = str(v) if state in ("slot_value", "hold_identity_gap") or state.startswith("hide") else None
                cell["state"] = state
                cells[(s0, e0)] = cell
            for k, p in prod[fam].items():
                if k not in cells:
                    s0, e0 = k
                    if e0 in held_ends or any(near(e0, h, 3) for h in held_ends):
                        g = sorted(next(v for h, v in held_ends.items() if near(e0, h, 3)))
                        st = "prod_only_filing_held:" + g[0]
                    elif is_q4_like(s0, e0):
                        st = "prod_only_q4_not_a_face_column"
                    elif not slots[cik][fam]:
                        st = "prod_only_company_no_face_rows"
                    else:
                        st = "prod_only_not_a_face_column"
                    cells[k] = {"cik": cik, "family": fam, "start": s0.isoformat(), "end": e0.isoformat(), "state": st}
                c = cells[k]
                c.update(prod_value=str(p["value"]), prod_cf_id=p["cf_id"], prod_tag=p["tag"], prod_n_sources=p["n_sources"],
                         prod_accession=p["accession"], prod_derived=p["derived"])
            for c in cells.values():
                pv = c.get("prod_value")
                if c["state"] == "slot_value":
                    sv = Decimal(c["slot_value"])
                    if pv is None:
                        c["compare"] = "slot_fills_blank"
                    else:
                        diff = abs(sv - Decimal(pv))
                        unit = rounding_unit([sv])
                        punit = unit_of(Decimal(pv))
                        unit = unit_of(sv)
                        same_tag_later = (c.get("prod_tag") == c["slot_tag"] and c.get("prod_accession")
                                          and c.get("prod_accession") != c["accession"])
                        if diff == 0:
                            c["compare"] = "agree"
                        elif diff * 2 <= unit:
                            c["compare"] = "differs_within_rounding"
                        elif punit > unit and diff * 2 <= punit:
                            # production shows a rounding of the filed number (a later filing
                            # printed in millions/billions): less precise, not a different number
                            c["compare"] = "prod_less_precise"
                        elif same_tag_later and not c.get("prod_derived"):
                            # production shows the SAME tag from a later filing with another value:
                            # a disagreeing copy (restatement, recast or a note figure); founder
                            # ruling: restated periods whose copies disagree are hidden
                            c["state"] = "hide_restated_copies_disagree"
                            c["copies_disagree"] = (c.get("copies_disagree") or []) + [
                                {"accession": c["prod_accession"], "tag": c["prod_tag"], "value": c["prod_value"], "via": "production_source"}]
                            c["compare"] = "would_hide"
                        else:
                            c["compare"] = "slot_differs"
                elif c["state"].startswith("hide"):
                    c["compare"] = "would_hide" if pv is not None else "hidden_already_blank"
                else:
                    c["compare"] = "prod_kept" if pv is not None else "both_blank"
                summary[fam][c["state"] + " | " + c["compare"]] += 1
                fh[fam].write(json.dumps(c) + "\n")
        if n % 50 == 0:
            print(f"{n}/{len(ciks)} companies", flush=True)
    conn.close()
    for f in fh.values():
        f.close()
    js = {f: dict(sorted(summary[f].items(), key=lambda x: -x[1])) for f in FAMILIES}
    json.dump(js, open(out / "is_replay_summary.json", "w"), indent=1)
    for f in FAMILIES:
        print(f, json.dumps(js[f], indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:5])
