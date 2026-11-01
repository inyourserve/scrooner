"""concept_rule seeds (FORMATS-v1 §2) for the cash-flow families (CFO, buybacks, dividends paid) and the
per-share families (DPS, shares), READ from the ported lane code by import, never retyped:
  cf_family_replay.py         OP_TOTAL / OP_CONT, BUYBACK_TAGS_COMMON, DIV_COMMON_TAGS (run 7 rules, 2e061bc)
  fsn_company_pershare.py     TAGS (the mapper's approved order restricted to share_basis's lane tags)
Rows already in cf.jsonl / per_share.jsonl from other lanes (capex, D&A, EPS) are kept untouched; this
script owns the rule_ids it writes (prefixes below) and replaces only those. Everything the seed format
cannot say (label regexes, exclusions that are not std_tag matches, holds, the Q4 DPS rule) is written to
cf_pershare_not_extracted.md with file:line. Run with the pipeline venv (share_basis imports psycopg).
usage: export_concept_rule_seeds_cf_pershare.py <data-team/47-fsn-store>
"""
import inspect
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import cf_family_replay as cfr  # noqa: E402  (main() is __name__-guarded)
import fsn_company_pershare as fps  # noqa: E402

OUT = Path(sys.argv[1])
COMMIT = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
OWNED = ("cf.cfo_", "cf.buybacks_", "cf.dividends_paid_", "per_share.dps_", "per_share.shares_")
EV = {
    "cfo_resolved": "VERIFY-CFO-BUYBACKS-RUN2-2026-11-01: CFO 15 of 15 right (FILING-CHECKED); run 7 publishable 37,121",
    "share_buybacks_resolved": "VERIFY-BUYBACKS-RUN3-2026-11-01 20/20 + VERIFY-BUYBACKS-R2-2026-11-04 6/6 (founder perimeter ruling)",
    "dividends_paid_resolved": "run 7 (24,610 publishable); founder ruling 2026-11-01: 'dividends and dividend equivalents' is common; no Verifier draw yet",
    "dividends_per_share_resolved": "VERIFY-SPLIT-RELEASE-2-2026-11-04: 10/10 incl. 3 derived Q4 DPS on one basis",
    "shares_outstanding_resolved": "VERIFY-SPLIT-RELEASE-HELD-2026-11-04 (NXPI shares right); share_basis.TARGETS",
}
REL_CF = "pipeline/scripts/slot_records/cf_family_replay.py"
REL_PS = "pipeline/scripts/slot_records/fsn_company_pershare.py"


def line_of(mod, name):
    src = inspect.getsource(mod).splitlines()
    return next(i + 1 for i, s in enumerate(src) if s.startswith((f"{name} =", f"{name}=", f"def {name}(", f"{name}:")))


rows, prov, notx = [], [], []


def add(lane, rule, n, concept, stmt, tag, priority, src, symbol):
    rid = f"{lane}.{rule}@{n}"
    rows.append({"canonical_concept": concept, "stmt": stmt, "match_kind": "std_tag", "tag": f"{tag}" if ":" in tag else f"us-gaap:{tag}",
                 "position": None, "components": None, "priority": priority, "era_from": None, "era_to": None,
                 "rule_id": rid, "source_commit": COMMIT, "evidence": EV[concept]})
    prov.append({"rule_id": rid, "source_file": src, "source_symbol": symbol, "extraction": "import", "bare_tag": tag})


def skip(src, mod, name, item, why):
    notx.append((f"{src}:{line_of(mod, name)}", item, why))


# ---------------- CFO
add("cf", "cfo_printed_total", 1, "cfo_resolved", "CF", cfr.OP_TOTAL, 10, REL_CF, "OP_TOTAL (read_cell: printed_total)")
add("cf", "cfo_continuing_equals_total", 1, "cfo_resolved", "CF", cfr.OP_CONT, 20, REL_CF, "OP_CONT (read_cell: continuing_equals_total)")
skip(REL_CF, cfr, "read_cell", "CFO continuing-operations line counts only when the face prints NO discontinued operating line; "
     "continuing + discontinued without a total -> `cfo_total_not_printed` (sum carried as a candidate, never published)", "condition on sibling lines, held by the detector")
skip(REL_CF, cfr, "read_cell", "CFO custom operating total (custom tag + OP_LABEL_RX label, not continuing/discontinued) -> printed_total_custom", "label rule on a custom tag")
skip(REL_CF, cfr, "OP_LABEL_RX", f"`OP_LABEL_RX` /{cfr.OP_LABEL_RX.pattern}/", "label regex; also picks the primary cash-flow report (primary_face)")
# ---------------- buybacks
for i, t in enumerate(sorted(cfr.BUYBACK_TAGS_COMMON)):
    add("cf", "buybacks_common_tag", i + 1, "share_buybacks_resolved", "CF", t, 10 + i, REL_CF, "BUYBACK_TAGS_COMMON")
skip(REL_CF, cfr, "BUYBACK_TAGS_EXCLUDED", f"BUYBACK_TAGS_EXCLUDED {sorted(cfr.BUYBACK_TAGS_EXCLUDED)}",
     "exclusions: no seed std_tag maps these tags, so a `demote` row would withdraw nothing; the detector classes them `excluded`")
skip(REL_CF, cfr, "buyback_class", "buyback_class: direction first (inflow/net), then perimeter classes (excise, swap, option exercise, "
     "tax withholding, subsidiary, SBC plan), combined, unresolved, common", "label regexes in a function body")
skip(REL_CF, cfr, "FOUNDER_EXCLUDED", f"FOUNDER_EXCLUDED {sorted(cfr.FOUNDER_EXCLUDED)} (founder ruling 2026-11-04)", "excluded with a reason, never summed; a line combining them with a buyback is held")
skip(REL_CF, cfr, "verdict_bb", "buybacks verdict: sum of `common` financing lines; holds combined / net / unresolved / multiple repurchase lines / "
     "sign_unclear; zero printed = a value", "publication gates")
for n in ("REPURCHASE_RX", "WITHHOLD_RX", "EXCLUDED_RX", "COMMON_RX", "INFLOW_RX", "OUTFLOW_RX", "NET_RX", "SUBSIDIARY_RX",
          "NONCASH_RX", "SWAP_RX", "OPTION_RX", "COMBINED_RX", "SBC_PLAN_RX", "EXCISE_RX"):
    skip(REL_CF, cfr, n, f"`{n}` /{getattr(cfr, n).pattern[:90]}/", "label regex, not a tag rule")
# ---------------- dividends paid
for i, t in enumerate(sorted(cfr.DIV_COMMON_TAGS)):
    add("cf", "dividends_paid_common_tag", i + 1, "dividends_paid_resolved", "CF", t, 10 + i, REL_CF, "DIV_COMMON_TAGS")
skip(REL_CF, cfr, "dividend_class", "dividend_class: preferred, NCI and standalone dividend-equivalent lines excluded; "
     "'dividends and (dividend) equivalents' / 'dividends, including' is COMMON (AAPL; founder ruling 2026-11-01); "
     "combined, net, partnership-unit and unresolved held; investee inflows ignored", "label regexes in a function body")
for n in ("DIV_HIT_RX", "DIV_PREFERRED_RX", "DIV_NCI_RX", "DIV_EQUIV_RX", "DIV_PARTNER_RX", "DIV_COMMON_RX"):
    skip(REL_CF, cfr, n, f"`{n}` /{getattr(cfr, n).pattern[:90]}/", "label regex, not a tag rule")
skip(REL_CF, cfr, "verdict_div", "dividends verdict: SUM of printed common dividend lines (regular + special), outflow only, same gates as buybacks", "publication gates")
# ---------------- shared cash-flow gates
skip(REL_CF, cfr, "read_cell", "face column = the change-in-cash root or a section total tagged for the column; identity = calc root ties; "
     "section = the family's section total ties; financing membership by the filer's own calc tree", "filing_checks (design §5), not mapping")
skip(REL_CF, cfr, "replay_company", "original filing wins; a later copy that disagrees -> restated_copies_disagree; stub column by FSN durp "
     "(> 0.1 quarter off the company's usual offset)", "selection / vintage logic (design §4)")
# ---------------- per share
for concept, rule in (("dividends_per_share_resolved", "dps_tag"), ("shares_outstanding_resolved", "shares_tag")):
    stmt = "BS" if concept == fps.SHARES else "IS"
    for i, t in enumerate(fps.TAGS[concept]):
        if t.startswith("Entity"):
            skip(REL_PS, fps, "tag_order", f"{concept} dei:{t} (cover page, mapper priority {i + 1})", "cover-page line (stmt CP): FORMATS-v1 stmt is BS/IS/CF only")
            continue
        add("per_share", rule, i + 1, concept, stmt, t, 10 * (i + 1), REL_PS, "TAGS (mapper CONCEPT_MAPPINGS order, share_basis lane tags)")
skip(REL_PS, fps, "company_cells", "Q4 DPS = filed FY - filed 9M only on one share basis (no split signal in (filed 9M, filed FY]; "
     "share_basis.split_signal_dates_from_rows) and no filed 3-month Q4; both zero = same on every basis", "derivation rule (design §4), founder ruling 2026-11-04")
skip(REL_PS, fps, "company_cells", "EPS is NEVER derived; instants (shares) are never derived", "derivation ban (design §4)")
skip(REL_PS, fps, "tag_order", "basic EPS falls back to EarningsPerShareBasicAndDiluted when the own tag has no copy (the lane's rule)",
     "one tag feeding two concepts by fallback; the seed maps BasicAndDiluted to diluted only (per_share.eps_fsn_tags@3)")
skip("pipeline/scripts/per_share/pershare_fsn_rules.py", __import__("pershare_fsn_rules"), "QUARTERLY_AXIS",
     "per-share copies: dimn 0 or the 10-K quarterly-data axis (QUARTERLY_AXIS, not REJECT_AXIS); copies within 0.005 agree, else hidden; context swaps dropped", "value filters / vintage logic")

# ---------------- checks + write (FORMATS-v1 §2)
assert len({r["rule_id"] for r in rows}) == len(rows)
cr = OUT / "concept_rules"
for lane in ("cf", "per_share"):
    p = cr / f"{lane}.jsonl"
    kept = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
    kept = [r for r in kept if not r["rule_id"].startswith(OWNED)]
    mine = [r for r in rows if r["rule_id"].startswith(lane + ".")]
    allr = kept + mine
    keys = [(r["canonical_concept"], r["stmt"], r["match_kind"], r["tag"]) for r in allr if r["tag"]]
    assert len(keys) == len(set(keys)), "duplicate (concept, stmt, match_kind, tag)"
    p.write_text("".join(json.dumps(r) + "\n" for r in allr))
pp = cr / "_provenance.jsonl"
old = [json.loads(x) for x in pp.read_text().splitlines() if x.strip()]
old = [r for r in old if not str(r.get("rule_id", "")).startswith(OWNED)]
pp.write_text("".join(json.dumps(r) + "\n" for r in old + prov))
with open(cr / "cf_pershare_not_extracted.md", "w") as f:
    f.write(f"# Cash-flow and per-share rules not expressed as concept_rule seeds (source {COMMIT})\n\n"
            "Generated by pipeline/scripts/slot_records/export_concept_rule_seeds_cf_pershare.py. They stay in the ported "
            "readers (cf_family_replay.py --company, fsn_company_pershare.py); the seed carries only the unconditional tag maps.\n\n"
            "| file:line | rule | why not a seed row |\n|---|---|---|\n")
    for loc, item, why in notx:
        f.write(f"| {loc} | {item.replace('|', '\\|').replace('](', ']\\(')} | {why.replace('|', '\\|')} |\n")
print("rows", len(rows), "not_extracted", len(notx), "commit", COMMIT)
for r in rows:
    print(r["rule_id"], r["canonical_concept"], r["tag"], r["priority"])
