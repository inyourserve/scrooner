"""Export fsn.concept_rule seed rows from the closed lanes' code (FORMATS-v1 §2). Read-only, no DB, no network.

Seeds are READ from the lane modules, never retyped: modules without top-level work are imported
(family_config, build_debt_slots, mapper.concepts / expanded_concepts); modules that run work at import
(argv parsing, file IO, env reads) are parsed with `ast` (literal_eval of module-level assignments,
re.compile first argument for regexes, string literals inside named functions / assignments).

FORMATS-v1 has no regex field, so every regex rule and every exclude / negative rule is written to
lanes_not_extracted.md with file:line instead of a seed row. The only names this script supplies by
hand are (a) the lane-slot -> analytics.canonical_concept name aliases below and (b) the one-line
evidence pointers; every TAG comes from the lane code (or, for EPS concept assignment, from the mapper's
own CONCEPT_MAPPINGS).

usage: export_concept_rule_seeds_lanes.py <out_dir>
  writes <out_dir>/concept_rules/{bs,cf,per_share}.jsonl, <out_dir>/concept_rules/_provenance.jsonl,
  <out_dir>/lanes_not_extracted.md
"""

import ast
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent  # pipeline/scripts/slot_records
REPO = HERE.parents[2]
PS = REPO / "pipeline" / "scripts" / "per_share"
SRC = REPO / "pipeline" / "src"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SRC))

import build_debt_slots as bds  # noqa: E402  (main() is __name__-guarded)
import family_config as fc  # noqa: E402
from scrooner_pipeline.mapper import concepts as mc  # noqa: E402
from scrooner_pipeline.mapper import expanded_concepts as mx  # noqa: E402

OUT = Path(sys.argv[1])
COMMIT = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()

F_BS_DETECT = HERE / "bs_totals_detect.py"
F_BS_ASSEMBLE = HERE / "bs_assemble.py"
F_ERA = HERE / "era_detect.py"
F_ASM30 = HERE / "assemble30.py"
F_ASMFAM = HERE / "assemble_family.py"
F_FAMCFG = HERE / "family_config.py"
F_BDS = HERE / "build_debt_slots.py"
F_CFFACE = HERE / "cf_face_rows.py"
F_CFV = HERE / "cf_da_capex_variants.py"
F_EPS = PS / "eps_fsn_scan.py"

# ---------------------------------------------------------------- canonical concept names
# the analytics.canonical_concept names visible in the repo (migrations + mapper seeds); the DB itself
# is not read, so this set is "known in the repo", flagged in the report
KNOWN = set()
for p in list((REPO / "pipeline" / "db" / "migrations").glob("*.sql")) + list(SRC.rglob("*.py")):
    KNOWN.update(a or b for a, b in re.findall(r"'([a-z][a-z0-9_]*_resolved)'|\"([a-z][a-z0-9_]*_resolved)\"", p.read_text()))
for name, *_ in mc.CANONICAL_CONCEPTS + mx.NEW_CANONICAL_CONCEPTS:
    KNOWN.add(name)

# tag -> [(concept, priority)] from the mapper's own approved mappings (used only to name an anchor tag's
# concept and the EPS tags' concepts; never to add a tag)
TAG_CONCEPT = defaultdict(list)
for row in list(mc.CONCEPT_MAPPINGS) + list(mx.NEW_CONCEPT_MAPPINGS):
    name, tax, tag, prio = row[0], row[1], row[2], row[3]
    TAG_CONCEPT[(tax, tag)].append((name, prio))


def resolved(base):
    """the canonical concept a lane slot feeds: <base>_resolved when the repo knows it"""
    for cand in (f"{base}_resolved", base):
        if cand in KNOWN and cand.endswith("_resolved"):
            return cand
    return None


def concept_of_tag(tag):
    hits = sorted(TAG_CONCEPT.get(("us-gaap", tag), []), key=lambda x: x[1])
    return resolved(hits[0][0]) if hits else None


# lane slot / anchor name -> canonical concept (the only hand-written names in this script)
ALIAS = {
    "assets_total": "total_assets_resolved",
    "liabilities_total": "total_liabilities_resolved",
    "equity_parent": "stockholders_equity_resolved",
    "total_liabilities": "total_liabilities_resolved",
    "total_debt": "total_debt_resolved",
    "d_and_a": "depreciation_and_amortization_resolved",
    "capex": "capex_resolved",
}
for v in ALIAS.values():
    assert v in KNOWN, v

EVIDENCE = {
    "total_assets_resolved": "VERIFY-BS-TOTALS-V3-2026-10-25 (bs_totals anchors); identity gate only, no own release draw located",
    "total_liabilities_resolved": "VERIFY-TOTAL-LIABILITIES-DRYRUN-2026-10-26: gate passes, 0 wrong of 175; release 1 NO as packaged (UPS) per VERIFY-BS-RELEASE1-2026-10-26",
    "stockholders_equity_resolved": "lane code (bs_totals equity_parent slot), Verifier evidence not located",
    "total_debt_resolved": "VERIFY-DEBT-RELEASE1-AMZN-2026-11-04: 3 of 3 right",
    "capex_resolved": "VERIFY-CAPEX-R1-FINAL-FILLS-V19-2026-11-04: release 1 NO (23/25, acquisition lines), fills checked",
    "depreciation_and_amortization_resolved": "VERIFY-DA-RELEASE1-2026-11-02: release 1 YES 15/15, class fills 10/10",
    "basic_eps_resolved": "VERIFY-EPS-FAMILY-C-V3-2026-11-02: 15 of 15 right (and VERIFY-EPS-FAMILY-C-2026-11-01)",
    "diluted_eps_resolved": "VERIFY-EPS-FAMILY-C-V3-2026-11-02: 15 of 15 right (and VERIFY-EPS-FAMILY-C-2026-11-01)",
}


# ---------------------------------------------------------------- ast helpers
class Mod:
    def __init__(self, path):
        self.path = path
        self.text = path.read_text()
        self.tree = ast.parse(self.text)
        self.rel = str(path.relative_to(REPO))
        self.consts = {}  # module-level name -> (kind, value, lineno, flags)
        for node in self.tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in tgts:
                    if isinstance(t, ast.Name) and node.value is not None:
                        self.consts[t.id] = self._val(node.value, node.lineno)

    @staticmethod
    def _val(v, lineno):
        if is_compile(v):
            flags = ast.unparse(v.args[1]) if len(v.args) > 1 else ""
            return ("regex", v.args[0].value, lineno, flags)
        try:
            return ("literal", ast.literal_eval(v), lineno, ast_order(v))
        except (ValueError, SyntaxError):
            if isinstance(v, ast.Dict):
                return ("dict", v, lineno, None)
            return ("other", None, lineno, None)

    def func(self, name):
        return next(n for n in ast.walk(self.tree) if isinstance(n, ast.FunctionDef) and n.name == name)

    def assigns(self, target):
        return [n for n in ast.walk(self.tree) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == target for t in n.targets)]


def is_compile(v):
    return (isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr == "compile"
            and isinstance(v.func.value, ast.Name) and v.func.value.id == "re"
            and v.args and isinstance(v.args[0], ast.Constant))


def ast_order(v):
    """source order of string elements of a set/tuple/list literal (sets keep source order in the AST)"""
    if isinstance(v, (ast.Set, ast.Tuple, ast.List)):
        return [e.value for e in v.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
    if isinstance(v, ast.Dict):
        return {k.value: ast_order(val) for k, val in zip(v.keys, v.values) if isinstance(k, ast.Constant)}
    return None


def strs_in_tuples(node):
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Compare) and any(isinstance(o, (ast.In, ast.NotIn)) for o in n.ops):
            for c in n.comparators:
                o = ast_order(c)
                if o:
                    out.append((o, n.lineno))
    return out


def if_returns(fn):
    """(ordinal, test, returned constant, lineno) for each `if <test>: return "<class>"` in source order"""
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.If) and n.body and isinstance(n.body[0], ast.Return) \
                and isinstance(n.body[0].value, ast.Constant) and isinstance(n.body[0].value.value, str):
            out.append((n.lineno, n.test, n.body[0].value.value))
    out.sort(key=lambda x: x[0])
    return out


def final_return(fn):
    r = fn.body[-1]
    assert isinstance(r, ast.Return) and isinstance(r.value, ast.Constant), fn.name
    return r.value.value, r.lineno


def literal_tag_tests(test, tagvar="tag"):
    """sufficient standalone literal tag tests in a classifier test: `tag == "X"` or `tag in (...)`,
    either the whole test or one disjunct of a top-level `or`. Returns (tags, pure) where pure = the
    whole test is that literal test (False: other disjuncts exist that this script does not seed)."""
    parts = test.values if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.Or) else [test]
    tags = []
    for p in parts:
        if isinstance(p, ast.Compare) and isinstance(p.left, ast.Name) and p.left.id == tagvar and len(p.ops) == 1:
            if isinstance(p.ops[0], ast.Eq) and isinstance(p.comparators[0], ast.Constant):
                tags.append(p.comparators[0].value)
            elif isinstance(p.ops[0], ast.In):
                tags.extend(ast_order(p.comparators[0]) or [])
    return tags, len(parts) == 1


# ---------------------------------------------------------------- collection
ROWS = defaultdict(list)  # lane -> rows
PROV = []
NOT = []  # (file:line, item, why)
seen_keys = set()
ordinal = Counter()


def tagref(tag):
    return tag if ":" in tag else f"us-gaap:{tag}"


def add(lane, rule, concept, stmt, kind, priority, mod, symbol, method, tag=None, position=None, components=None):
    key = (concept, stmt, kind, tag, json.dumps(position, sort_keys=True))
    if key in seen_keys:
        PROV.append({"duplicate_of_key": list(map(str, key)), "source_file": mod.rel, "source_symbol": symbol, "extraction": method})
        return
    seen_keys.add(key)
    ordinal[(lane, rule)] += 1
    rid = f"{lane}.{rule}@{ordinal[(lane, rule)]}"
    row = {"canonical_concept": concept, "stmt": stmt, "match_kind": kind,
           "tag": tagref(tag) if tag else None, "position": position, "components": components,
           "priority": priority, "era_from": None, "era_to": None, "rule_id": rid,
           "source_commit": COMMIT, "evidence": EVIDENCE.get(concept, "lane code, Verifier evidence not located")}
    ROWS[lane].append(row)
    PROV.append({"rule_id": rid, "source_file": mod.rel, "source_symbol": symbol, "extraction": method,
                 "bare_tag": tag})


def skip(mod, lineno, item, why):
    NOT.append((f"{mod.rel}:{lineno}", item, why))


def skip_regexes(mod, names, why_by_name=None, default="regex rule; FORMATS-v1 has no pattern field"):
    for n in names:
        kind, val, ln, flags = mod.consts[n]
        assert kind == "regex", n
        why = (why_by_name or {}).get(n, default)
        skip(mod, ln, f"`{n}` = /{val[:90]}{'...' if len(val) > 90 else ''}/{(' ' + flags) if flags else ''}", why)


# ================================================================= BS lane
bsd = Mod(F_BS_DETECT)
bsa = Mod(F_BS_ASSEMBLE)

# 1. ANCHORS: printed anchor totals (std_tag), priority 10 = printed-total-first
_, anchors, ln, order = bsd.consts["ANCHORS"]
for slot, tagset in anchors.items():
    concept = ALIAS.get(slot)
    tags = order[slot]
    assert set(tags) == tagset
    if not concept:
        skip(bsd, ln, f"ANCHORS[{slot!r}] = {sorted(tagset)}", "no analytics.canonical_concept for this slot in the repo (NCI / incl-NCI equity / L&E total are identity inputs only)")
        continue
    for i, t in enumerate(tags):
        add("bs", f"anchors_{slot}", concept, "BS", "std_tag", 10 + i, bsd, f"ANCHORS[{slot!r}]", "ast", tag=t)

# 2. bs_assemble printed_total member literal (same rule as ANCHORS liabilities_total -> dedup)
for a in bsa.assigns("liab_members"):
    try:
        lit = ast.literal_eval(a.value)
    except ValueError:
        continue
    for m in lit:
        if m.get("rule") == "printed_total":
            add("bs", "total_liabilities_printed_total", ALIAS["total_liabilities"], "BS", "std_tag", 10, bsa, "liab_members (printed_total)", "ast", tag=m["tag"])

# 3. EQUITY_PARENT_TAGS (bs_assemble): equity_parent slot, first printed wins; priority = source order
_, eq, ln, order = bsa.consts["EQUITY_PARENT_TAGS"]
for i, t in enumerate(order):
    add("bs", "equity_parent_tags", ALIAS["equity_parent"], "BS", "std_tag", 10 + i, bsa, "EQUITY_PARENT_TAGS", "ast", tag=t)

# 4. calc_position: the liabilities slot ('liab' = classify_line's fall-through class)
cl = bsd.func("classify_line")
liab_slot, liab_ln = final_return(cl)
add("bs", "liab_zone_after_assets", ALIAS["total_liabilities"], "BS", "calc_position", 20, bsd,
    "classify_line + zone_start (tags.index(ANCHORS assets_total)+1)", "ast",
    position={"slot": liab_slot, "anchor_concept": ALIAS["assets_total"], "relation": "sibling_after", "sign": 1})
# bs_assemble: cal_confirmed = child of these statement-role parents
cal_parents = []
for a in bsa.assigns("cal_liab"):
    consts = [n for n in ast.walk(a.value) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    cal_parents += [n.value for n in sorted(consts, key=lambda n: (n.lineno, n.col_offset))]  # source order
for i, p in enumerate(cal_parents):
    anchor = ALIAS["liabilities_total"] if p in bsd.consts["ANCHORS"][1]["liabilities_total"] else concept_of_tag(p)
    if not anchor:
        skip(bsa, bsa.assigns("cal_liab")[0].lineno, f"cal_liab parent {p}", "anchor tag has no canonical concept in the repo; calc_position needs anchor_concept")
        continue
    # NOT a seed (FAMILY-RELEASE-CASE-2026-11-09 §3a): cal_liab names the MEMBERS bs_assemble sums into the face
    # liabilities; the store's calc_position maps a matching line AS the concept, so a member became a second
    # "total" beside the printed Liabilities line (false conflicting_values_in_filing, 4,479 filings). The total
    # is the printed Liabilities line (bs.anchors_liabilities_total) or the derived total (fsn_store.bs_derive).
    skip(bsa, bsa.assigns("cal_liab")[0].lineno, f"cal_liab parent {p}: liability members (child_of)",
         "members of the liabilities total, never the total: a calc_position seed would map each member AS "
         "total_liabilities_resolved (FAMILY-RELEASE-CASE-2026-11-09 §3a)")

# 5. classify_line literal/named tests -> not extracted (regex / exclude / no concept)
for lineno, test, cls in if_returns(cl):
    skip(bsd, lineno, f"classify_line -> `{cls}`: `{ast.unparse(test)[:110]}`",
         "exclude/class rule by regex or set membership; excludes and regexes are not seed rows in FORMATS-v1"
         if cls.startswith("excluded") or "RX" in ast.unparse(test) else "detector class with no canonical concept (equity_total/nci)")
skip(bsd, liab_ln - 4, "classify_line structural guard: ta.is_abstract / ta.balance(tag)=='debit' -> excluded", "taxonomy-attribute lookup at run time, not a tag list")
skip_regexes(bsd, ["EQUITY_START_RX", "MEZZ_RX", "DEBT_LIKE_RX", "NOISE_RX", "CAP_TOTAL_RX", "TOTAL_LABEL_RX", "NONLIAB_RX"],
             {"CAP_TOTAL_RX": "combined line (equity+debt capitalization subtotal) but given as a regex, and its components have no concept names",
              "TOTAL_LABEL_RX": "label regex (face label), not a tag rule",
              "MEZZ_RX": "mezzanine slot by regex + face position; no canonical concept for temporary equity in the repo"})
_, eqt, ln, _o = bsd.consts["EQUITY_TOTAL_TAGS"]
skip(bsd, ln, f"EQUITY_TOTAL_TAGS {sorted(eqt)}", "detector class equity_total mixes parent and incl-NCI totals; not a single canonical concept")
for a in bsa.assigns("nci"):
    for tags, l in strs_in_tuples(a.value):
        skip(bsa, l, f"nci slot tags {tags}", "no analytics.canonical_concept for NCI in the repo")
for a in bsa.assigns("TOTALS"):
    skip(bsa, a.lineno, f"TOTALS {ast.literal_eval(a.value)}", "taxonomy-total coverage by face position (lines printed before a total since the previous one): an alternative reading the replay chooses by identity tie; not one fixed relation")
skip_regexes(bsa, ["MEZZ_RX"], {"MEZZ_RX": "dimensioned mezzanine class-of-stock facts (regex, dims extract), no concept"})
skip(bsa, bsa.consts["NOISE_RX"][2], "`NOISE_RX` (bs_assemble)", "defined but never used in bs_assemble.py")

# ---------------- debt (era_detect + assemble30 -> build_debt_slots), stmt BS
era = Mod(F_ERA)
a30 = Mod(F_ASM30)
bdm = Mod(F_BDS)
# the concept name the debt assembler writes
debt_concepts = [n.values[n.keys.index(k)].value for n in ast.walk(a30.tree) if isinstance(n, ast.Dict)
                 for k in n.keys if isinstance(k, ast.Constant) and k.value == "canonical_concept"]
assert debt_concepts == ["total_debt"], debt_concepts
TD = ALIAS[debt_concepts[0]]
borrow_slot, _ = final_return(bdm.func("classify"))
# PARENTS (imported): a debt member is a statement-role calc child of one of these
for i, p in enumerate(bdm.consts["PARENTS"][3]):
    assert p in bds.PARENTS
    anchor = ALIAS["liabilities_total"] if p in bsd.consts["ANCHORS"][1]["liabilities_total"] else concept_of_tag(p)
    if not anchor:
        skip(bdm, bdm.consts["PARENTS"][2], f"PARENTS member {p}", "anchor tag has no canonical concept in the repo")
        continue
    # NOT a seed (FAMILY-RELEASE-CASE-2026-11-09 §2): the store's calc_position maps a matching custom line AS the
    # concept and never tests the slot, so every custom child of current liabilities (accounts payable, accruals)
    # became total debt; and select takes one line, while total debt is a sum. Total debt comes from the lane run
    # whole (fsn_store.debt: era_detect -> assemble_fsn -> replay_debt_fsn), never from a seed.
    skip(bdm, bdm.consts["PARENTS"][2], f"PARENTS member {p}: debt members ({borrow_slot}, child_of)",
         "members of total debt, never the total: total debt is the lane's sum (fsn_store.debt runs replay_debt_fsn); "
         "a calc_position seed mapped any custom current liability AS total_debt_resolved (FAMILY-RELEASE-CASE-2026-11-09 §2)")
# founder ruling 2026-11-01 (BS port brief): total debt includes finance leases (face or note), a combined
# debt+finance-lease line is part of total debt, operating leases stay combined (never in total debt).
# classify() names the slots; a finance_lease or combined member is a total_debt member exactly like a
# borrowing (replay_debt_fsn sums every non-operating member into the lease-inclusive total).
DEBT_LEASE_EVIDENCE = ("founder 2026-11-01 (BS port): debt includes note finance leases, a combined debt+finance-lease "
                       "line is total debt, operating leases stay combined; replay_debt_fsn report_v4 = Verifier debt v3 "
                       "14/14 + VERIFY-DEBT-RELEASE1-AMZN 3/3")
cls_returns = [c for _l, _t, c in if_returns(bdm.func("classify"))]
for k, slot in enumerate(s for s in ("finance_lease", "combined") if s in cls_returns):
    for i, p in enumerate(bdm.consts["PARENTS"][3]):
        anchor = ALIAS["liabilities_total"] if p in bsd.consts["ANCHORS"][1]["liabilities_total"] else concept_of_tag(p)
        if not anchor:
            continue  # listed once above for the borrowing slot
        # NOT a seed either (see the borrowing slot above): the lane sums these members (DEBT_LEASE_EVIDENCE)
        skip(bdm, bdm.consts["PARENTS"][2], f"PARENTS member {p}: debt members ({slot}, child_of)",
             "summed by the debt lane (fsn_store.debt), never mapped as the total; " + DEBT_LEASE_EVIDENCE)
assert "operating_lease" in cls_returns
skip(bdm, bdm.func("classify").lineno, "classify() -> 'operating_lease': never a total_debt member (replay_debt_fsn.load_records drops the member)",
     "an exclusion; FORMATS-v1 calc_position has no negative slot. Founder 2026-11-01: operating leases stay combined")
rdf = Mod(HERE / "replay_debt_fsn.py")
afs = Mod(HERE / "assemble_fsn.py")
for fn_name, item, why in (
        ("replay", "note-only finance lease (FinanceLeaseLiability / CapitalLeaseObligations total, else current + noncurrent, same accession) added to total debt (option b)",
         "a NOTE fact, not a statement line: detector hook (replay_debt_fsn), founder 2026-11-01 keeps it in total debt"),
        ("replay", "face lease line decomposed by the filer's own operating + finance facts (AMZN): proven, its finance part read from the note",
         "value-tie rule at replay time: detector hook"),
        ("replay", "face lease liability line not carried by the record (custom lease element) -> debt_lease_member_unverified",
         "label + tag regex at replay time: detector hook")):
    skip(rdf, rdf.func(fn_name).lineno, item, why)
skip(afs, afs.func("assemble").lineno, "Verifier V5 (WSO): a member whose calc descendants (any role) include an OperatingLease line -> excluded_mixed_lease",
     "operating leases stay combined (founder 2026-11-01): calc-descendant test per filing, detector hook; the standard taxonomy has no element that mixes borrowings or finance leases with operating leases (us_gaap_2025_elements.csv: 0), so only custom lines reach it")
# The anchors of the debt slots (current_liabilities_resolved = us-gaap:LiabilitiesCurrent) are seeded in
# concept_rules/bs_current.jsonl (main); a second row here would collide with it on uq_fsn_concept_rule.
skip_regexes(era, ["DEBT_RX", "LABEL_RX", "EXCLUDE_RX"], {"LABEL_RX": "label regex (debt candidate by printed label)"})
skip_regexes(bdm, ["EXCLUDE_RX", "AGG_PARENT_RX", "DEBT_RX", "BS_ROLE_RX", "NOTE_ROLE_RX", "FINANCE_LEASE_RX", "OPERATING_LEASE_RX", "BORROWING_RX", "ERA_RX"],
             {"BS_ROLE_RX": "calc-role selector, not a concept rule", "NOTE_ROLE_RX": "calc-role rejector, not a concept rule",
              "ERA_RX": "taxonomy-year parser, not a concept rule"})
for i, (rx, reason) in enumerate(bds.EXCLUDE_CLASSES):
    skip(bdm, bdm.consts["EXCLUDE_CLASSES"][2], f"EXCLUDE_CLASSES[{i}] /{rx.pattern}/ -> {reason}",
         "exclude rule by regex" + ("; it IS the combined AP+accrued line, but as a regex with no component concepts" if "combined" in reason else ""))
_, ct, ln, _o = bdm.consts["COMBINED_TAGS"]
skip(bdm, ln, f"COMBINED_TAGS {sorted(ct)}", "classify() -> 'combined': seeded as the total_debt `combined` calc slot above (founder 2026-11-01: a combined debt+finance-lease line is part of total debt), not as a FORMATS-v1 `combined` row, which would blank it")
_, dm, ln, _o = bdm.consts["DEFINITIONAL_MAYBE"]
skip(bdm, ln, f"DEFINITIONAL_MAYBE {sorted(dm)}", "combined only WITH evidence (own calc children or a same-date lease fact): conditional, and a slot member not a whole-concept std_tag")
fn = bdm.func("classify")
skip(bdm, fn.lineno, "classify(): borrowing AND (finance OR operating lease) -> combined", "regex conjunction in a function body")

# ================================================================= CF lane
cfv = Mod(F_CFV)
fam = Mod(F_FAMCFG)
asf = Mod(F_ASMFAM)
# concept names cf_da_capex_variants reads production under, paired with its family= labels in order
prod_names = [n.slice.elts[1].value for n in ast.walk(cfv.tree) if isinstance(n, ast.Subscript)
              and isinstance(n.value, ast.Name) and n.value.id == "prod" and isinstance(n.slice, ast.Tuple)
              and isinstance(n.slice.elts[1], ast.Constant)]
fam_labels = [k.value.value for n in ast.walk(cfv.tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
              and n.func.id == "dict" for k in n.keywords if k.arg == "family"]
assert [ALIAS[f] for f in fam_labels] == prod_names, (fam_labels, prod_names)
CAPEX, DA = ALIAS["capex"], ALIAS["d_and_a"]

op_total = cfv.consts["OP_TOTAL"][1]
cfo = concept_of_tag(op_total[0])
assert cfo == "cfo_resolved", cfo
# capex block = face lines printed after the operating total up to the investing total
cn = cfv.func("capex_nature")
cn_classes = if_returns(cn)
cn_default, _ = final_return(cn)
# slots in force per the founder rulings in the code (leased, software counted in variant_ruling/interim)
ruling_slots = []
for n in ast.walk(cfv.tree):
    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ("n_ppe", "leased", "soft") for t in n.targets):
        for c in ast.walk(n.value):
            if isinstance(c, ast.Compare) and any(isinstance(o, (ast.Eq, ast.In)) for o in c.ops):
                for cc in c.comparators:
                    vals = ast_order(cc) or ([cc.value] if isinstance(cc, ast.Constant) and isinstance(cc.value, str) else [])
                    ruling_slots += [v for v in vals if v not in ruling_slots]
for i, slot in enumerate(ruling_slots):
    add("cf", "capex_block_member", CAPEX, "CF", "calc_position", 20 + i, cfv, "capex_nature + block rows[op_i+1:inv_i+1]", "ast",
        position={"slot": slot, "anchor_concept": cfo, "relation": "sibling_after", "sign": -1})
# literal tag tests in capex_nature whose class is counted in the ruling perimeter
for k, (lineno, test, cls) in enumerate(cn_classes):
    tags, pure = literal_tag_tests(test)
    for t in tags:
        if cls in ruling_slots:
            add("cf", f"capex_nature_{cls}", CAPEX, "CF", "std_tag", 10 + k, cfv, f"capex_nature -> {cls}", "ast", tag=t)
        else:
            skip(cfv, lineno, f"capex_nature `{t}` -> {cls}", "class not counted in capex")
    if not tags or not pure:
        skip(cfv, lineno, f"capex_nature -> `{cls}`: `{ast.unparse(test)[:110]}`", "label regex / substring / prefix test in a function body" + ("" if not tags else " (the literal-tag disjunct is seeded)"))
# D&A: operating-section lines before the CFO total, class asset_da
dn = cfv.func("da_nature")
add("cf", "da_operating_member", DA, "CF", "calc_position", 20, cfv, "da_nature asset_da + rows[:op_i]", "ast",
    position={"slot": "asset_da", "anchor_concept": cfo, "relation": "child_of", "sign": 1})
assert any(c == "asset_da" for _, _, c in if_returns(dn))
for lineno, test, cls in if_returns(dn):
    skip(cfv, lineno, f"da_nature -> `{cls}`: `{ast.unparse(test)[:110]}`", "label/tag regex test in a function body")
# IS anchor: the income statement's printed D&A total (used when the CF composition holds)
for a in cfv.assigns("is_da"):
    for tags, l in strs_in_tuples(a.value):
        for i, t in enumerate(tags):
            add("cf", "da_is_anchor", DA, "IS", "std_tag", 30 + i, cfv, "is_da (IS printed D&A total)", "ast", tag=t)
for a in cfv.assigns("is_amort"):
    for n in ast.walk(a.value):
        if isinstance(n, ast.Compare) and isinstance(n.ops[0], ast.Eq) and isinstance(n.comparators[0], ast.Constant):
            skip(cfv, n.lineno, f"is_amort `{n.comparators[0].value}` (IS intangible amortization)", "tie-out input for a generic amortization line, no own canonical concept")
skip_regexes(cfv, ["CAPEX_TAG", "CAPEX_LABEL", "CAPEX_EXCLUDE", "CAPEX_OTHER", "CAPEX_OG", "CAPEX_OG_LABEL", "CAPEX_WORD",
                   "MIXED_JOIN", "ASSET_NAMED", "DA_TAG", "DA_TAG_EXCLUDE", "DA_EXCLUDED_LABEL", "DA_EXCLUDED_TAG",
                   "SOFT_TAG", "MIXED_TAG", "ASSET_DA_TAG", "IS_INTANGIBLE_AMORT"],
             {n: "label regex, not a tag rule" for n in ("CAPEX_LABEL", "CAPEX_OG_LABEL", "CAPEX_WORD", "MIXED_JOIN", "ASSET_NAMED", "DA_EXCLUDED_LABEL", "IS_INTANGIBLE_AMORT")})
for n in ("OP_TOTAL", "INV_TOTAL", "INV_DISC"):
    skip(cfv, cfv.consts[n][2], f"`{n}` {cfv.consts[n][1]}", "section anchors used as positions above (cfo_resolved via the mapper); investing totals have no tag->concept mapping in the repo, discontinued-block boundary is a range rule")
# family_config (imported) + assemble_family
for famname, cfg in fc.FAMILIES.items():
    ln = fam.consts["FAMILIES"][2]
    skip(fam, ln, f"FAMILIES[{famname!r}] match /{cfg['match'].pattern[:80]}/, exclude /{cfg['exclude'].pattern}/, {len(cfg['classes'])} class regexes, stmts {sorted(cfg['stmts'])}",
         "regex candidate/exclude/class rules (era fingerprinting for D&A/capex); IS lines are `is_subline`, never the CF total")
for n in ("SECTION_PARENT", "CF_ROLE_RX"):
    skip(asf, asf.consts[n][2], f"assemble_family `{n}`", "section-parent / statement-role regex (section_confirmed), not a concept rule")

# ================================================================= per_share lane
eps = Mod(F_EPS)
_, tags, ln, order = eps.consts["TAGS"]
for t in order:
    hits = sorted(TAG_CONCEPT.get(("us-gaap", t), []), key=lambda x: x[1])
    if not hits:
        skip(eps, ln, f"TAGS {t}", "no mapper concept mapping for this tag")
        continue
    for name, prio in hits:
        c = resolved(name)
        add("per_share", "eps_fsn_tags", c, "IS", "std_tag", 10 * prio, eps, "TAGS (concept from mapper CONCEPT_MAPPINGS)", "ast", tag=t)
skip(eps, ln, "TAGS concept assignment", "eps_fsn_scan reads each cell's own tag order (own tag first, combined BasicAndDiluted as fallback) from its input; the tag->concept pairing above comes from the mapper's CONCEPT_MAPPINGS, not the lane")
for n in ("QUARTERLY_AXIS", "REJECT_AXIS"):
    skip(eps, eps.consts[n][2], f"`{n}` /{eps.consts[n][1][:80]}/", "dimension-axis regex (which one-axis contexts count), not a tag rule")

# cf_face_rows: no concept rules
cff = Mod(F_CFFACE)
skip(cff, cff.consts["STD"][2], f"STD {cff.consts['STD'][1]}", "custom-vs-standard namespace flag; no concept rules in this module")
skip(cff, cff.consts["FORMS"][2], "FORMS + inpth=='0' filter", "input filter (periodic forms, non-parenthetical rows), not a concept rule")

# ---------------------------------------------------------------- function-body logic (prose, file:line)
MANUAL = [
    (bsd, 135, "zone_start = index('Assets')+1; zone truncated at the filer's L&E total", "seeded as the sibling_after row; the L&E truncation has no concept anchor"),
    (bsd, 160, "mezz-tagged line between two liab lines -> liab; inside equity -> equity_component", "neighbour-based reclass, imperative"),
    (bsd, 179, "equity-block guard: liab line after the equity block starts -> equity_component until Total capitalization", "imperative position state machine"),
    (bsd, 194, "era fingerprint = skeleton || mezz + printedL/noL + nci/no_nci; eras collapse on identical fp", "era rule; era_from/era_to are per company, not per rule"),
    (era, 46, "debt era fingerprint = ordered candidate tags; consecutive identical fps collapse", "era rule; per-company, not expressible as rule-level era_from/era_to"),
    (bsa, 61, "company-wide calc graph borrowed when the boundary filing has no cal", "data-dependent fallback"),
    (bsa, 104, "face_sum = roots of the liab line set under the filer's statement-role calc (subtotal keeps itself, drops its printed descendants)", "calc-DAG logic; partially seeded as liab child_of rows"),
    (bsa, 130, "hold_no_cal_for_dedup when no calc graph and no taxonomy total on the face", "hold rule"),
    (bsa, 141, "member weight from the statement-role arc (VMI deferred taxes -1)", "sign comes from the arc, seeded rows carry sign 1"),
    (bsa, 172, "requires_identity_tie for face_sum", "check, not mapping (design §4 filing_check)"),
    (a30, 75, "adjacent eras with identical CAL fingerprints re-collapse", "era rule"),
    (a30, 107, "member whose calc descendants (any role) include an OperatingLease line -> excluded_mixed_lease", "exclude by calc descendants"),
    (a30, 125, "face coverage: every debt candidate is a member or carries a recorded exclusion; else coverage_clean=false", "coverage gate"),
    (a30, 137, "side from /Current$|^ShortTerm/ vs /Noncurrent$|^LongTerm/; standard uncovered face lines admitted via face_admission.admit (4 guards + value tie)", "regex + face_admission guards (face_admission.py carries its own EQUITY_RX/CAP_TOTAL_RX/LSE_TOTALS, not extracted)"),
    (bdm, 214, "debt_observation: member = DEBT_RX child, not EXCLUDE_RX, of PARENTS in BS statement role (not note role); side current iff parent LiabilitiesCurrent", "regex gate on the calc_position rows; seeds do not carry the gate"),
    (bdm, 271, "_apply_lease_evidence: lease classification by same-date lease facts", "evidence-dependent"),
    (asf, 85, "D&A/capex member composition: G1 single root member = printed line; G2 parent whose printed children tie", "calc-DAG composition gate"),
    (cfv, 255, "column/filing winner: original 10-K/10-Q whose period is the column end; face column only if a section total is tagged", "selection (design §4), not mapping"),
    (cfv, 323, "capex block line filters: proceeds/sale labels skipped, accrual-change labels skipped, O&G acquisition labels held, additions/expenditures labels admitted with exclusions, turnaround/major maintenance counted, PBF asset purchase skipped", "label regexes in loop body"),
    (cfv, 377, "a printed capex child beside its printed capex parent is not summed", "calc rule gated by CAPEX_TAG regex"),
    (cfv, 382, "discontinued-block membership: between the continuing investing total and INV_DISC, or 'discontinued' in label", "range + label rule"),
    (cfv, 390, "sign as printed: trust FSN negating only when the investing section sums to its total; one-member flip correction; Payments* positive = outflow; else capex_sign_unresolved", "sign handling"),
    (cfv, 446, "interim/hold reasons (capex_sign_unresolved, capex_line_names_no_asset, other_capex_lines_outside_ruling, perimeter_line_unresolved, no_continuing_capex_line)", "publication gates"),
    (cfv, 496, "D&A candidates: DA_TAG tag, custom line with D&A label, or label starting depreciation/amortization/depletion; same fact on two rows counts once; child of printed D&A parent skipped", "regex + label + calc in loop body"),
    (cfv, 514, "D&A value sign as presented (negating); lease_intangible -> excluded if negative else asset_da", "sign handling"),
    (cfv, 518, "IRM: combined line net of a tagged parenthetical financing part", "arithmetic netting"),
    (cfv, 547, "generic amortization ties to IS intangible amortization (2a); IS D&A total tie classes; label_only subset search <= 3", "tie-out logic"),
    (cfv, 593, "net D&A line below intangible amortization held; company-wide propagation (line 658)", "company rule"),
    (cfv, 610, "income-statement anchor replaces a held/partial CF composition", "seeded as the IS std_tag rows (priority after CF); the replacement condition is not"),
    (eps, 110, "num filters: qtrs 1-4, dimn 0 or 1 (quarterly axis only), iprx 0, no coreg", "value filters (design §4)"),
    (eps, 161, "swapped_copies: context-swap detection between filings", "vintage logic"),
    (eps, 203, "own tag first, combined tag only when the own tag has no copy; copies within 0.005 agree else hidden", "selection logic"),
]
for m, ln, item, why in MANUAL:
    skip(m, ln, item, why)

# ---------------------------------------------------------------- write + checks
cr = OUT / "concept_rules"
cr.mkdir(parents=True, exist_ok=True)
srcs = {p.relative_to(REPO).as_posix(): p.read_text() for p in (F_BS_DETECT, F_BS_ASSEMBLE, F_ERA, F_ASM30, F_ASMFAM, F_FAMCFG, F_BDS, F_CFFACE, F_CFV, F_EPS)}
rid_count = Counter(r["rule_id"] for rows in ROWS.values() for r in rows)
assert all(v == 1 for v in rid_count.values()), [k for k, v in rid_count.items() if v > 1]
pk = Counter((r["canonical_concept"], r["stmt"], r["match_kind"], r["tag"], r["priority"]) for rows in ROWS.values() for r in rows)
uniq = Counter((r["canonical_concept"], r["stmt"], r["match_kind"], r["tag"]) for rows in ROWS.values() for r in rows if r["tag"])
assert all(v == 1 for v in uniq.values()), uniq
for p in PROV:
    if p.get("bare_tag"):
        assert re.search(rf'"{re.escape(p["bare_tag"])}"', srcs[p["source_file"]]), p
for rows in ROWS.values():
    for r in rows:
        assert r["canonical_concept"] in KNOWN and r["stmt"] in ("BS", "IS", "CF")
        if r["match_kind"] == "calc_position":
            assert r["tag"] is None and r["position"]["anchor_concept"] in KNOWN
        else:
            assert r["tag"] and r["position"] is None
for lane in ("bs", "cf", "per_share"):
    with open(cr / f"{lane}.jsonl", "w") as f:
        for r in ROWS[lane]:
            f.write(json.dumps(r) + "\n")
with open(cr / "_provenance.jsonl", "w") as f:
    for p in PROV:
        f.write(json.dumps(p) + "\n")
with open(OUT / "lanes_not_extracted.md", "w") as f:
    f.write(f"# Lane rules not expressed as concept_rule seeds (source {COMMIT})\n\n"
            "Generated by pipeline/scripts/slot_records/export_concept_rule_seeds_lanes.py. FORMATS-v1 §2 has no regex field, "
            "so regex rules and exclude/negative rules are listed here, with function-body logic, sign handling and era rules.\n\n"
            "| file:line | rule | why not a seed row |\n|---|---|---|\n")
    for loc, item, why in sorted(NOT, key=lambda x: (x[0].split(":")[0], int(x[0].split(":")[1]))):
        # `](` would read as a Markdown link to scripts/check_docs.py (ERA_RX `[/-](\\d{4})`): escape the paren
        f.write(f"| {loc} | {item.replace('|', '\\|').replace('](', ']\\(')} | {why.replace('|', '\\|').replace('](', ']\\(')} |\n")

counts = Counter((lane, r["canonical_concept"], r["stmt"], r["match_kind"]) for lane, rows in ROWS.items() for r in rows)
for k, v in sorted(counts.items()):
    print(*k, v)
print("rows", sum(counts.values()), "not_extracted", len(NOT), "duplicates_merged", sum(1 for p in PROV if "duplicate_of_key" in p), "commit", COMMIT)
print("methods", Counter(p["extraction"] for p in PROV if "rule_id" in p))
