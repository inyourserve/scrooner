"""Gates A-D of bs_port_gate.sh (stdlib, run with -I). FAILS CLOSED: every difference is a diff row
{gate, key, class, detail}; the exit code is 1 when any diff is observed, unless --expected names a file
whose diff set equals the observed set EXACTLY (an observed diff missing from it, or an expected diff that
no longer occurs, both fail). The class of each diff is computed from the data (no free text):
  A  old vs ported code, cohort mode: byte-identical files; the debt replay compared cell by cell
  B  company mode vs cohort mode (ported code)
  C  debt replay (company mode) vs report_v4.json (Verifier debt v3 + AMZN)
  D  bs_assemble (company mode) vs bs_records_v3.jsonl (Verifier BS v3)
Writes <work>/observed_diffs.json (sorted) and <work>/gate_report.json.
usage: bs_port_compare.py <work_dir> <report_v4.json> <bs_records_v3.jsonl> [--expected <expected_diffs.json>]
"""
import filecmp
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
work, v4_path, v3_path = Path(args[0]), args[1], args[2]
expected_path = sys.argv[sys.argv.index("--expected") + 1] if "--expected" in sys.argv else None
if expected_path:
    args.remove(expected_path)
old, new, comp = work / "old", work / "new", work / "company"
DIFFS = []


def canon(o):
    return json.dumps(o, sort_keys=True, default=str)


def diff(gate, key, cls, detail):
    DIFFS.append({"gate": gate, "key": key if isinstance(key, str) else canon(key), "class": cls,
                  "detail_sha": hashlib.sha256(canon(detail).encode()).hexdigest()[:16], "detail": detail})


def lines(p):
    return [json.loads(x) for x in open(p) if x.strip()]


# accepted / filed per accession, from the cohort instants extract (both sides read the same file)
ACCEPTED, VALUES = {}, {}
for x in gzip.open(work / "instants.jsonl.gz", "rt"):
    f = json.loads(x)
    ACCEPTED[f["adsh"]] = (f.get("accepted") or "", f["filed"], f["adsh"])
    VALUES[f["adsh"]] = f["values"]


# the non-member facts replay_debt_fsn reads at the instant (note finance leases, LongTermDebt note, current portion)
READ_TAGS = {"FinanceLeaseLiability", "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent", "CapitalLeaseObligations",
             "CapitalLeaseObligationsCurrent", "CapitalLeaseObligationsNoncurrent", "LongTermDebt", "LongTermDebtCurrent",
             "LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths", "DebtAndCapitalLeaseObligations",
             "DebtLongtermAndShorttermCombinedAmount"}


def restated(ref, got):
    """True when the later filing prints a different value, at the same date, for a member tag of either cell"""
    d = ref["period_end"].replace("-", "")
    tags = {m[0] for c in (ref, got) for m in (c.get("members") or [])} | READ_TAGS
    a, b = VALUES.get(ref.get("accession"), {}).get(d, {}), VALUES.get(got.get("accession"), {}).get(d, {})
    return any(t in a and t in b and a[t] != b[t] for t in tags)


def cells_by_key(rep):
    return {(c["ticker"], c["period_end"]): c for c in rep["cells"]}


def norm_cell(c):
    c = dict(c)
    if c["verdict"] in ("prod_blank", "prod_agrees", "prod_differs"):
        c["verdict"] = "publishable"
    c.pop("prod_value", None)
    if c.get("note_finance_lease_negative") is None:
        c.pop("note_finance_lease_negative", None)  # field added by the review fix: null = absent in older outputs
    return c


VALUE = ("slot_lease_inclusive", "slot_borrowings")


def num(x):
    from decimal import Decimal
    return None if x is None else Decimal(x)


def same_values(a, b, fields=VALUE):
    return all(num(a.get(f)) == num(b.get(f)) for f in fields)


def classify_cell(ref, got, fsn_window_from="2015-01-01"):
    """the mechanical class of a replay cell difference (ref = earlier output, got = this code)"""
    if got is None:
        if ref["period_end"] < fsn_window_from:
            return "cell_before_2015_window"
        col = VALUES.get(ref.get("accession"), {}).get(ref["period_end"].replace("-", ""), {})
        if not any(t in col for t in ("LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital")):
            return "old_cell_was_not_a_face_column"  # no closing total at that date in that filing (KKR: a note's Assets)
        return "cell_missing"
    if ref is None:
        return "cell_new"
    if ref.get("accession") != got.get("accession"):
        later = ACCEPTED.get(got.get("accession"), ("",)) > ACCEPTED.get(ref.get("accession"), ("",))
        same = ref["verdict"] == got["verdict"] and same_values(ref, got)
        if not later:
            return "accession_differs_not_later"
        if same:
            return "latest_accepted_print_same_value"
        if ref["verdict"] != got["verdict"]:
            return "latest_accepted_print_verdict_differs"
        if same_values(ref, got, ("slot_lease_inclusive",)):
            return "latest_accepted_print_same_total_borrowings_split_differs"
        if restated(ref, got):
            return "latest_accepted_print_restated"
        if ref.get("note_finance_lease_added") != got.get("note_finance_lease_added"):
            return "latest_accepted_print_note_lease_differs"
        if ref.get("record_filing_from") != got.get("record_filing_from") or ref.get("members") != got.get("members"):
            return "latest_accepted_print_covering_record_differs"
        return "latest_accepted_print_value_differs_unexplained"
    if ref["verdict"] != got["verdict"]:
        if ref["verdict"] == "no_covering_record" and ref.get("record_filing_from") is None:
            return "covered_by_the_filing_s_own_period_record"
        return "verdict_differs"
    if not same_values(ref, got):
        ra, ga = ref.get("note_finance_lease_added"), got.get("note_finance_lease_added")
        if ra and ref.get("slot_lease_inclusive") and got.get("slot_lease_inclusive"):
            from decimal import Decimal
            d_total = Decimal(ref["slot_lease_inclusive"]) - Decimal(got["slot_lease_inclusive"])
            d_note = Decimal(ra) - Decimal(ga or 0)
            if d_total == d_note and d_total > 0:
                return "note_finance_lease_overlap_removed"
        return "value_differs"
    if ref.get("members") != got.get("members"):
        return "members_differ_same_value"
    if any(ref.get(f) != got.get(f) for f in ("note_finance_lease_added", "note_current_portion_added", "note_flag")):
        return "note_fields_differ_same_value"
    if ref.get("record_filing_from") != got.get("record_filing_from"):
        return "covering_record_differs_same_value"  # the record covering the chosen filing's own period
    return None


def compare_replays(gate, ref, got):
    for k in sorted(set(ref) | set(got)):
        a, b = ref.get(k), got.get(k)
        if a is not None and b is not None and canon(norm_cell(a)) == canon(norm_cell(b)):
            continue
        if a is not None and b is not None and same_values(a, b) and canon({**norm_cell(a), **{f: None for f in VALUE}}) == canon({**norm_cell(b), **{f: None for f in VALUE}}):
            continue  # numerically equal values printed differently ("0" vs "0.0000")
        cls = classify_cell(norm_cell(a) if a else None, norm_cell(b) if b else None) or "other_field_differs"
        diff(gate, list(k), cls, {"ref": a and {f: a.get(f) for f in ("verdict", *VALUE, "accession", "note_flag", "note_finance_lease_added")},
                                  "got": b and {f: b.get(f) for f in ("verdict", *VALUE, "accession", "note_flag", "note_finance_lease_added")}})


def compare_sets(gate, name, a, b):
    ca, cb = Counter(map(canon, a)), Counter(map(canon, b))
    for k in sorted((ca - cb).keys()):
        diff(gate, f"{name}:{hashlib.sha256(k.encode()).hexdigest()[:16]}", "only_in_reference", json.loads(k))
    for k in sorted((cb - ca).keys()):
        diff(gate, f"{name}:{hashlib.sha256(k.encode()).hexdigest()[:16]}", "only_in_port", json.loads(k))


# ---------------------------------------------------------------- A
print("== A: old vs ported code, cohort mode")
A_FILES = ["bs_eras.json", "bs_boundaries.txt", "bs_records.jsonl", "debt/bs_pre_rows.jsonl", "debt/adsh_period.json",
           "debt/lease_facts.csv", "debt_eras.json", "debt_boundaries.txt", "debt_records.jsonl"]
for f in A_FILES:
    if not (old / f).exists() or not (new / f).exists():
        diff("A", f, "output_missing", {"old": (old / f).exists(), "new": (new / f).exists()})
        print(f"  MISSING    {f}")
    elif filecmp.cmp(old / f, new / f, shallow=False):
        print(f"  identical  {f}")
    else:
        diff("A", f, "file_differs", {"old_sha": hashlib.sha256((old / f).read_bytes()).hexdigest(),
                                      "new_sha": hashlib.sha256((new / f).read_bytes()).hexdigest()})
        print(f"  DIFFERENT  {f}")
ra, rb = json.load(open(old / "debt_replay.json")), json.load(open(new / "debt_replay.json"))
rf = json.load(open(new / "debt_replay_first_filed.json"))
n0 = len(DIFFS)
# A1: old code vs ported code with the OLD selection: only the review's other fixes may show (2015 cells,
# note-lease overlap, face-column test, latest-copy lease guard needs a later copy so it cannot fire here)
compare_replays("A1", cells_by_key(ra), cells_by_key(rf))
print(f"  debt_replay A1 (old vs ported, first-filed selection): {len(ra['cells'])} -> {len(rf['cells'])} cells, {len(DIFFS) - n0} differ "
      f"{dict(Counter(d['class'] for d in DIFFS[n0:]))}")
n0 = len(DIFFS)
# A2: the selection change alone (design section 4: latest accepted print wins)
compare_replays("A2", cells_by_key(rf), cells_by_key(rb))
print(f"  debt_replay A2 (first-filed vs latest-accepted selection): {len(rf['cells'])} -> {len(rb['cells'])} cells, {len(DIFFS) - n0} differ "
      f"{dict(Counter(d['class'] for d in DIFFS[n0:]))}")

# ---------------------------------------------------------------- B
print("== B: company mode vs cohort mode (ported code, same filings)")
n0 = len(DIFFS)
for f in ("bs_eras.json", "debt_eras.json"):
    a, b = json.load(open(new / f)), json.load(open(comp / f))
    compare_sets("B", f, [{"cik": k, **e} for k, v in a.items() for e in v], [{"cik": k, **e} for k, v in b.items() for e in v])
for f in ("bs_boundaries.txt", "debt_boundaries.txt"):
    compare_sets("B", f, open(new / f).read().split("\n"), open(comp / f).read().split("\n"))
compare_sets("B", "debt_records.jsonl", lines(new / "debt_records.jsonl"), lines(comp / "debt_records.jsonl"))
compare_replays("B", cells_by_key(rb), cells_by_key(json.load(open(comp / "debt_replay.json"))))
# bs_assemble: cohort mode reads the filing's _cal.xml, company mode the FSN cal (+ face_tags)
ka = {(r["cik"], r["filing_from"]): r for r in lines(new / "bs_records.jsonl")}
kb = {(r["cik"], r["filing_from"]): r for r in lines(comp / "bs_records.jsonl")}
for k in sorted(set(ka) | set(kb)):
    a, b = ka.get(k), kb.get(k)
    if a and b:
        fa = {f: v for f, v in a.items() if f not in ("source", "taxonomy_era_from", "taxonomy_era_to")}
        fb = {f: v for f, v in b.items() if f not in ("source", "taxonomy_era_from", "taxonomy_era_to")}
        if canon(fa) == canon(fb):
            continue
        bad = sorted(f for f in fa if canon(fa.get(f)) != canon(fb.get(f)))
        diff("B", ["bs_records", *k], "bs_record_xml_cal_vs_fsn_cal:" + ",".join(bad), {f: [fa.get(f), fb.get(f)] for f in bad})
    else:
        diff("B", ["bs_records", *k], "bs_record_only_in_" + ("cohort" if a else "company"), {})
print(f"  {len(DIFFS) - n0} differences {dict(Counter(d['class'].split(':')[0] for d in DIFFS[n0:]))}")

# ---------------------------------------------------------------- C
print("== C: debt replay, company mode, vs the Verifier-passed report_v4.json")
n0 = len(DIFFS)
v4 = cells_by_key(json.load(open(v4_path)))
got = cells_by_key(json.load(open(comp / "debt_replay.json")))
tickers = {t for t, _ in v4}
compare_replays("C", v4, {k: v for k, v in got.items() if k[0] in tickers})
# the lane's 'securities loaned' candidate hold (BS-PORT-2026-11-01.md 5.1): the covering record is coverage-dirty
# only because of a SecuritiesLoaned / ...AndLoaned asset line matched by era_detect's label net
recs_by_first = {r["filing_from"]: r for r in lines(comp / "debt_records.jsonl")}
for d in DIFFS[n0:]:
    if d["class"] != "verdict_differs":
        continue
    c = got.get(tuple(json.loads(d["key"])))
    rec = recs_by_first.get((c or {}).get("record_filing_from"), {})
    unc = [u["tag"] for u in rec.get("uncovered_candidates", [])]
    if c and c["verdict"] == "not_computable_uncovered_candidates" and unc and all("Loaned" in t for t in unc):
        d["class"] = "held_securities_loaned_candidate"
same = len(v4) - sum(1 for d in DIFFS[n0:] if json.loads(d["key"]) and tuple(json.loads(d["key"])) in v4)
print(f"  v4 cells {len(v4)}; identical {same}; differences {len(DIFFS) - n0} {dict(Counter(d['class'] for d in DIFFS[n0:]))}")

# ---------------------------------------------------------------- D
print("== D: bs_assemble company mode vs the Verifier-passed bs_records_v3.jsonl")
n0 = len(DIFFS)
FIELDS = ("filing_from", "filing_to", "period_from", "period_to", "filings_observed", "total_liabilities_rule",
          "requires_identity_tie", "equity_parent_tag", "nci_tag", "equity_component_tags", "mezzanine_dim_tags", "coverage_clean")


def members(r):
    return [(m["tag"], m.get("weight"), m.get("tax_covered"), m.get("custom")) for m in r["total_liabilities_members"]]


v3 = {(r["cik"], r["filing_from"]): r for r in lines(v3_path)}
mine = {(r["cik"], r["filing_from"]): r for r in lines(comp / "bs_records.jsonl")}
eras = json.load(open(comp / "bs_eras.json"))
guard = {(c, e["first"]): {z["tag"] for z in e["zone_lines"] if z.get("equity_block_guard")} for c, el in eras.items() for e in el}
v3_ciks = {c for c, _ in v3}
identical = 0
for k, ref in sorted(v3.items()):
    g = mine.get(k)
    if g is None:
        cov = [r for r in mine.values() if r["cik"] == k[0] and r["period_from"][:7] < ref["period_from"][:7] <= r["period_to"][:7]]
        diff("D", list(k), "same_era_starts_earlier_in_fsn" if cov else "record_missing_in_port",
             {"v3": [ref["period_from"], ref["period_to"]], "port": cov and [cov[0]["filing_from"], cov[0]["period_from"], cov[0]["period_to"]]})
        continue
    # a field the reference does not carry (v3 predates equity_component_tags) is not compared
    bad = [f for f in FIELDS if f in ref and ref.get(f) != g.get(f)]
    if members(ref) != members(g):
        bad.append("total_liabilities_members")
    if [m["tag"] for m in ref["mezzanine_face"]] != [m["tag"] for m in g["mezzanine_face"]]:
        bad.append("mezzanine_face")
    if (ref.get("cal_source") or "").split(":")[0] != (g.get("cal_source") or "").split(":")[0]:
        bad.append("cal_source")
    if not bad:
        identical += 1
        continue
    det = {f: [ref.get(f), g.get(f)] for f in bad if f in FIELDS} | (
        {"members": [members(ref), members(g)]} if "total_liabilities_members" in bad else {}) | (
        {"cal_source": [ref.get("cal_source"), g.get("cal_source")]} if "cal_source" in bad else {})
    SPAN = {"filing_to", "period_to", "filings_observed"}
    span_sfx = "+era_span" if set(bad) & {"filing_to", "period_to"} else ""
    if "total_liabilities_members" in bad and set(bad) <= {"total_liabilities_members"} | SPAN:
        lost = {m[0] for m in members(ref)} - {m[0] for m in members(g)}
        gained = {m[0] for m in members(g)} - {m[0] for m in members(ref)}
        face = {z["tag"] for e in eras.get(k[0], []) if e["first"] == k[1] for z in e["zone_lines"]}
        cls = ("equity_block_guard_reclassed_a_v3_member" if lost and lost <= guard.get(k, set()) and not gained
               else "fsn_face_has_extra_liability_line" if gained and not lost and gained <= face
               else "member_list_differs") + span_sfx
    elif set(bad) <= {"filing_to", "period_to", "filings_observed"}:
        cls = "era_span_only"
    elif set(bad) - SPAN == {"equity_parent_tag"} and (ref.get("equity_parent_tag") or "StockholdersEquity") == (g.get("equity_parent_tag") or "StockholdersEquity"):
        cls = "equity_parent_tag_none_vs_default" + span_sfx  # bs_replay reads `equity_parent_tag or "StockholdersEquity"`
    elif bad == ["cal_source"] and (ref.get("cal_source") or "") == "own" and (g.get("cal_source") or "").startswith("borrowed:"):
        cls = "fsn_cal_has_no_bs_group_borrowed"  # DVN 0000950170-24-092424 (BS-PORT-2026-11-01.md 4.3)
    else:
        cls = "fields_differ:" + ",".join(sorted(bad))
    diff("D", list(k), cls, det)
v3_first = {}
for (c, _f), r in v3.items():
    v3_first[c] = min(v3_first.get(c, "9999"), r["period_from"])
for k in sorted(k for k in mine if k[0] in v3_ciks and k not in v3):
    r = mine[k]
    if r["period_to"][:7] < v3_first[k[0]][:7]:
        cls = "record_before_v3_window"  # FSN starts 2014q1, the v3 FSDS cohort 2015q1
    elif any(guard.get(k, set())) or any(guard.get((k[0], e["first"]), set()) for e in eras.get(k[0], []) if e["first"] == k[1]):
        cls = "record_split_by_equity_block_guard"
    elif any(q["cik"] == k[0] and r["period_from"][:7] < q["period_from"][:7] <= r["period_to"][:7] for q in v3.values()):
        cls = "same_era_starts_earlier_in_fsn_port_side"  # the twin of a v3 record_missing 'same_era_starts_earlier_in_fsn'
    elif any(q["cik"] == k[0] and q["period_from"][:7] <= r["period_from"][:7] <= q["period_to"][:7] for q in v3.values()):
        cls = "era_split_inside_a_v3_era"  # the twin of an 'era_span_only' difference (FSN vs FSDS face rows)
    else:
        cls = "record_only_in_port"
    diff("D", list(k), cls, {"period": [r["period_from"], r["period_to"]]})
print(f"  v3 records {len(v3)}; identical {identical}; differences {len(DIFFS) - n0} {dict(Counter(d['class'] for d in DIFFS[n0:]))}")

# ---------------------------------------------------------------- verdict
obs = sorted(DIFFS, key=lambda d: (d["gate"], d["key"], d["class"]))
json.dump(obs, open(work / "observed_diffs.json", "w"), indent=1, default=str)
json.dump({"by_gate_class": {f"{g}:{c}": n for (g, c), n in sorted(Counter((d["gate"], d["class"]) for d in obs).items())}},
          open(work / "gate_report.json", "w"), indent=1)
ident = {(d["gate"], d["key"], d["class"], d["detail_sha"]) for d in obs}
print("== verdict")
if not expected_path:
    print(f"  {len(obs)} differences (strict mode: any difference fails) -> {'FAIL' if obs else 'PASS'}")
    sys.exit(1 if obs else 0)
# classes that say "not understood": never pinnable, so an expected file cannot hide a real regression
UNPINNABLE = ("other_field_differs", "value_differs", "file_differs", "output_missing", "accession_differs_not_later",
              "only_in_reference", "only_in_port", "cell_missing", "cell_new", "member_list_differs")
pinned = json.load(open(expected_path))
bad_pins = [d for d in pinned if d["class"] in UNPINNABLE or d["class"].endswith("_unexplained")]
for d in bad_pins:
    print(f"  REFUSED PIN {d['gate']} {d['key']} {d['class']}")
if bad_pins:
    sys.exit(1)
exp = {(d["gate"], d["key"], d["class"], d["detail_sha"]) for d in pinned}
unexpected, vanished = ident - exp, exp - ident
print(f"  {len(obs)} differences; pinned in {expected_path}: {len(exp)}; unexpected {len(unexpected)}; pinned but not seen {len(vanished)}")
for g, k, c, _ in sorted(unexpected)[:20]:
    print(f"  UNEXPECTED {g} {k} {c}")
for g, k, c, _ in sorted(vanished)[:20]:
    print(f"  VANISHED   {g} {k} {c}")
print("  ->", "FAIL" if unexpected or vanished else "PASS (every difference is pinned and explained)")
sys.exit(1 if unexpected or vanished else 0)
