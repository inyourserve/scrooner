"""Per-company mapping notes (Markdown), generated from the tag-map decisions so they always match what is served.

Inputs (all read-only files; nothing here touches the database or git):
  --tag-map     company_tag_map CSV (tag library output, e.g. ranks_1_50.csv)
  --identity    CSV company_id,cik,name,ticker,sic_code,sector (dumped from core.company)
  --exceptions  optional company exceptions CSV (Ritwik cloud: company_id,ticker,stmt,tag,decision,concept,era_from,era_to,n_filings,reason)
  --std-tags    optional cross-company std-tags CSV (rank,tag,statements,decision,concept,reason); resolves undecided (residue) rows
  --templates   optional CSV dumped from analytics.company_data_point_template (company_id,data_point,in_template,reason,template,template_version);
                when a company has rows there they are the template; otherwise the sector default below is used and the note says so
  --out         output directory (one <TICKER>.md per company)
  --tickers     optional comma list to restrict the run
Usage: company_notes.py --tag-map X --identity Y --out DIR [--exceptions E] [--std-tags S] [--templates T] [--tickers MSFT,HD]

Nothing is invented: a template data point with no row in any source is listed "undecided" and as an open item.
"""
import argparse
import collections
import csv
import hashlib
import subprocess
from pathlib import Path

# Statement-line data points the library maps (base names; *_resolved is folded into the base name).
LINE_DATA_POINTS = [
    "revenue", "cost_of_revenue", "gross_profit", "operating_expenses", "sga_expense", "research_and_development",
    "operating_income", "interest_expense", "interest_income", "other_income_expense_net", "income_before_tax",
    "income_tax_expense", "net_income", "basic_eps", "diluted_eps", "dividends_per_share", "comprehensive_income",
    "cash_and_equivalents", "accounts_receivable", "inventory", "current_assets", "ppe_net", "goodwill", "total_assets",
    "accounts_payable", "current_liabilities", "total_liabilities", "total_debt", "stockholders_equity", "shares_outstanding",
    "cfo", "cash_flow_investing", "cash_flow_financing", "capex", "depreciation_and_amortization",
    "amortization_of_intangibles", "sbc", "dividends_paid", "share_buybacks", "cf_ar_change", "cf_inventory_change",
    "cf_ap_change",
]
ALIAS = {"revenue_sanity": "revenue"}

# Sector default OUT lines (SECTOR-TEMPLATES-2026-11-01 s2/s3 matrix; approved categories A and C only, s8 items 1-2).
SECTOR_OUT = {
    "bank": {"gross_profit", "cost_of_revenue", "operating_expenses", "research_and_development", "inventory",
             "accounts_receivable", "accounts_payable", "operating_income", "capex"},
    "lender": {"gross_profit", "inventory"},
    "broker_am": {"gross_profit", "inventory", "research_and_development"},
    "insurer": {"gross_profit", "cost_of_revenue", "inventory", "research_and_development", "capex"},
    "equity_reit": {"gross_profit", "inventory", "research_and_development", "capex"},
    "utility": {"gross_profit", "research_and_development"},
    "general": set(),
}
COMPANY_TEMPLATE = {"0001287750": "bdc", "0001736035": "bdc", "0002065601": "bank"}  # ARCC, BXSL, CBC (doc s8 items 4-5)


def sic_template(sic):
    s = int(sic) if str(sic).isdigit() else 0
    if s in (6021, 6022, 6035, 6036):
        return "bank"
    if s in (6141, 6162):
        return "lender"
    if s in (6200, 6211, 6282):
        return "broker_am"
    if 6311 <= s <= 6399 and s not in (6324, 6411):
        return "insurer"
    if s == 6798:
        return "equity_reit"
    if s in (4911, 4922, 4923, 4924, 4931, 4932, 4941):
        return "utility"
    return "general"


def base(c):
    if not c:
        return c
    c = c[:-9] if c.endswith("_resolved") else c
    return ALIAS.get(c, c)


def era(v):
    v = (v or "").strip()
    return f"20{v[:2]}-{v[2:]}" if len(v) == 4 and v.isdigit() else v


def esc(s):
    return (s or "").replace("|", "/").replace("\n", " ").strip()


def read_csv(p):
    return list(csv.DictReader(open(p, newline=""))) if p else []


def file_version(paths):
    parts = []
    for p in paths:
        if not p:
            continue
        sha = hashlib.sha256(Path(p).read_bytes()).hexdigest()[:10]
        try:
            g = subprocess.run(["git", "log", "-1", "--format=%h", "--", str(Path(p).resolve())], capture_output=True,
                               text=True, cwd=Path(p).resolve().parent).stdout.strip()
        except OSError:
            g = ""
        parts.append(f"{Path(p).name} sha256:{sha}" + (f" (last commit {g})" if g else ""))
    return "; ".join(parts)


def apply_std(rows, std):
    """Resolve undecided rows with the cross-company std-tags decisions. Returns rows (new dicts)."""
    idx = {}
    for s in std:
        for st in s["statements"].split("/"):
            idx[(st, s["tag"].split(":")[-1])] = s
    out = []
    for r in rows:
        r = dict(r)
        s = idx.get((r["stmt"], r["tag"])) if r["decision"] == "" else None
        if s:
            d = s["decision"]
            by = f"std-tags decision rank {s['rank']} (Ritwik cloud 2026-11-11)"
            r["decided_by"] = by
            r["reason"] = s["reason"]
            if d == "map":
                r.update(decision="concept", canonical_concept=s["concept"])
            elif d == "component":
                r.update(decision="component", parent_concept=s["concept"], combine_sign="1")
            elif d == "combined":
                r.update(decision="combined", components=s["concept"])
            elif d == "exclude":
                r.update(decision="excluded", reason_class="std_tags_exclude")
            elif d == "review":
                r.update(decision="review")
        out.append(r)
    return out


def span_months(a, b):
    return (int(b[:4]) * 12 + int(b[5:7])) - (int(a[:4]) * 12 + int(a[5:7]))


def template_for(ident, trows):
    """-> (template name, {dp: out_reason}, source text, template_version)"""
    mine = [t for t in trows if t["company_id"] == ident["company_id"]]
    if mine:
        out = {t["data_point"]: t["reason"] for t in mine if t["in_template"] in ("f", "false", "False", "0")}
        tv = ",".join(sorted({t["template_version"] for t in mine}))
        return mine[0]["template"], {base(k): v for k, v in out.items()}, "analytics.company_data_point_template", tv
    name = COMPANY_TEMPLATE.get(ident["cik"]) or sic_template(ident["sic_code"])
    out = {dp: f"sector default OUT for template '{name}' (SECTOR-TEMPLATES-2026-11-01 s2/s3)" for dp in SECTOR_OUT.get(name, set())}
    src = (f"PROPOSED from SIC {ident['sic_code']} per SECTOR-TEMPLATES-2026-11-01 (analytics.company_data_point_template "
           "has no rows for this company; the template is not yet seeded)")
    return name, out, src, "none (unseeded)"


def build_note(ident, rows, exc, trows, version):
    t_name, t_out, t_src, t_ver = template_for(ident, trows)
    span = [r for r in rows if r["era_from"]]
    lo = min((r["era_from"] for r in span), default="")
    hi = max((r["era_to"] for r in span), default="")
    nfil = max((int(r["filings"]) for r in rows if r.get("filings", "").isdigit()), default=0)
    L = [f"# {ident['name']} ({ident['ticker']}): data mapping note", "",
         "Generated by `pipeline/scripts/tag_library/company_notes.py` from the tag-map decisions; do not edit by hand.", "",
         f"- Company: {ident['name']} | ticker {ident['ticker']} | CIK {ident['cik']} | company_id {ident['company_id']}",
         f"- Sector template: **{t_name}** ({t_src}); template_version {t_ver}; DB sector label {ident.get('sector') or 'n/a'}",
         f"- FSN filings covered: {nfil} (largest per-tag filing count in the library), periods {lo} to {hi}",
         f"- Library version: {version}", ""]
    # ---- table rows
    table = collections.defaultdict(list)  # dp -> list of (status, tag, era, label, sign, evidence, rule)
    extra_dps = []
    seen_dp = set(LINE_DATA_POINTS)

    def add(dp, status, tag, e, label, sign, ev, rule):
        if dp not in seen_dp:
            seen_dp.add(dp)
            extra_dps.append(dp)
        table[dp].append((status, tag, e, label, sign, ev, rule))

    def ev_of(r):
        parts = [r.get("evidence_adsh") or ""]
        if r.get("evidence_report"):
            parts.append(f"report {r['evidence_report']}")
        if r.get("evidence_line"):
            parts.append(f"line {r['evidence_line']}")
        return ", ".join(p for p in parts if p) or "n/a"

    def rule_of(r):
        b = r.get("rule_id") or r.get("decided_by") or ""
        return esc(b + (": " + r["reason"] if r.get("reason") else ""))

    review, residue, overrides = [], [], []
    for r in rows:
        e = f"{r['era_from']} to {r['era_to']}"
        lab = f"{r['stmt']}: {esc(r.get('evidence_plabel'))}"
        d = r["decision"]
        if d == "concept" and r["canonical_concept"]:
            add(base(r["canonical_concept"]), "mapped", f"{r['taxonomy']}:{r['tag']}", e, lab, "as printed (sign not recorded in the library)", ev_of(r), rule_of(r))
        elif d == "component":
            add(base(r["parent_concept"]), "component sum", f"{r['taxonomy']}:{r['tag']}", e, lab, f"{r.get('combine_sign') or '1'} (summed)", ev_of(r), rule_of(r))
        elif d == "combined":
            for c in filter(None, (r.get("components") or "").replace(",", ";").split(";")):
                add(base(c.strip()), "combined", f"{r['taxonomy']}:{r['tag']}", e, lab, "n/a: one line spans several data points; never feeds one", ev_of(r), rule_of(r))
        elif d == "review":
            review.append(r)
        elif d == "":
            residue.append(r)
        if r["decided_by"] in ("company_override",):
            overrides.append(r)
    exc_lines = []
    for x in exc:
        e = f"{era(x['era_from'])} to {era(x['era_to'])}" if x["era_from"] else "all eras"
        d = x["decision"]
        tag = x["tag"] or "n/a"
        rule = esc(f"company exception (Ritwik cloud 2026-11-11): {x['reason']}")
        concepts = [base(c.strip()) for c in x["concept"].split(";") if c.strip() and c.strip() != "all"]
        stat = {"map": "mapped", "component": "component sum", "combined": "combined", "not_presented": "not presented",
                "not_in_template": "not in template"}.get(d)
        if stat:
            for c in concepts:
                add(c, stat, tag, e, f"{x['stmt']}: (see reason)", "see reason", f"{x['n_filings']} filings", rule)
        elif d == "resolved":
            for c in concepts:
                add(c, "mapped", tag, e, f"{x['stmt']}: (see reason)", "see reason", f"{x['n_filings']} filings", rule)
        exc_lines.append(f"- [{d}] {x['stmt']} {tag} {', '.join(concepts) or 'all'} ({e}, {x['n_filings']} filings): {esc(x['reason'])}")
    for r in overrides:
        exc_lines.append(f"- [library company override] {r['stmt']} {r['tag']} -> {base(r['canonical_concept']) or 'excluded'} ({r['era_from']} to {r['era_to']}): {esc(r['reason'])}")

    L += ["## Data points", "",
          "Rows are the statement-line data points the library maps. Derived metrics (ratios, growth, per-share) are computed from these and are not mapped here.", "",
          "| data point | status | tag(s) and era | statement and printed label | sign | evidence (accession, report, line) | rule or ruling |",
          "|---|---|---|---|---|---|---|"]
    undecided, era_holes, pending = [], [], []
    for dp in LINE_DATA_POINTS + extra_dps:
        rs = sorted(table.get(dp, []), key=lambda x: x[2])
        if not rs:
            cov = COVERAGE.get((ident.get("ticker") or "", dp))
            if cov and cov != "GAP":
                L.append(f"| {dp} | {esc(cov)} | none | none | n/a | coverage_full (tag library) | see status |")
                if "candidate" in cov:
                    pending.append((dp, cov))
                continue
            if COVERAGE and not cov:
                L.append(f"| {dp} | not in the approved template (tv1) | n/a | n/a | n/a | coverage_full | none |")
                continue
            if dp in t_out:
                L.append(f"| {dp} | not in template | n/a | n/a | n/a | n/a | {esc(t_out[dp])} |")
            else:
                L.append(f"| {dp} | undecided | none | none | n/a | no row in the tag map or the exceptions | none |")
                undecided.append(dp)
            continue
        for st, tag, e, lab, sign, ev, rule in rs:
            L.append(f"| {dp} | {st} | {tag} ({e}) | {lab} | {sign} | {ev} | {rule} |")
        if dp in t_out:
            L.append(f"| {dp} | note | n/a | n/a | n/a | n/a | the sector default says OUT but this company has a source row: company override to IN, to be seeded with this evidence |")
        eras_ = sorted((e.split(" to ")[0], e.split(" to ")[1]) for st, _, e, *_ in rs if st in ("mapped", "component sum") and " to " in e and e[:1].isdigit())
        if eras_ and lo:
            holes = []
            cur = eras_[0][1]
            if span_months(lo, eras_[0][0]) > 4:
                holes.append(f"starts {eras_[0][0]} (company from {lo})")
            for a, b in eras_[1:]:
                if span_months(cur, a) > 4:
                    holes.append(f"hole {cur}..{a}")
                cur = max(cur, b)
            if span_months(cur, hi) > 4:
                holes.append(f"ends {cur} (company to {hi})")
            if holes:
                era_holes.append((dp, "; ".join(holes)))
    L += ["", "## Company exceptions", "",
          "Places where this company departs from the cross-company library (company exceptions file and library company overrides), with the reason.", ""]
    L += exc_lines or ["- none recorded in either source for this company"]
    L += ["", "## Excluded lines", ""]
    cnt = collections.Counter(r["reason_class"] or "unclassified" for r in rows if r["decision"] == "excluded")
    L.append(f"{sum(cnt.values())} excluded (statement, tag) rows, by reason class (no row dump):")
    L += [f"- {k}: {v}" for k, v in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))] or ["- none"]
    L += ["", "## Open items (these block the certificate)", ""]
    n0 = len(L)
    for dp in undecided:
        L.append(f"- UNDECIDED data point `{dp}`: template says IN, no row in the tag map or the exceptions.")
    for dp, cov in pending:
        L.append(f"- PENDING VERIFIER `{dp}`: {cov}; a filing-checked draw decides note-sourced value or template OUT.")
    for dp, h in era_holes:
        L.append(f"- ERA not covered for `{dp}`: {h}. Needs a source row or a not-presented reason.")
    for r in review:
        L.append(f"- IN REVIEW {r['stmt']} {r['tag']} ({r['era_from']} to {r['era_to']}, {r['filings']} filings): {esc(r.get('reason'))}")
    for x in exc:
        if x["decision"] == "store_scope":
            L.append(f"- ENGINEERING {x['stmt']} store scope: {esc(x['reason'])}")
    for r in sorted(residue, key=lambda r: (r["stmt"], r["tag"])):
        why = esc(r.get("reason")) if r["decided_by"] == "ask_expert" else "no rule matched (residue)"
        L.append(f"- UNDECIDED line {r['stmt']} {r['taxonomy']}:{r['tag']} \"{esc(r.get('evidence_plabel'))}\" ({r['era_from']} to {r['era_to']}, {r['filings']} filings; {r['decided_by']}): {why}")
    if len(L) == n0:
        L.append("- none")
    L += ["", "## Certification", "",
          "- cell_proof PROVEN share: pending",
          "- Verifier sample result: pending",
          "- every blank reasoned: pending", ""]
    return "\n".join(L)


COVERAGE = {}  # (ticker, data_point) -> status from coverage_full (tag library); empty when not given


def load_coverage(path):
    """coverage_full CSV (company_id,ticker,template,data_point,status): the per-point status, in preference to the
    built-in sector default, so a held, reasoned or candidate point is never listed as undecided."""
    COVERAGE.clear()
    for r in read_csv(path):
        COVERAGE[(r["ticker"], r["data_point"])] = r["status"]


def generate(tag_map, identity, out_dir, exceptions=None, std_tags=None, templates=None, tickers=None):
    rows_all = read_csv(tag_map)
    ids = {i["company_id"]: i for i in read_csv(identity)}
    exc = read_csv(exceptions)
    std = read_csv(std_tags)
    trows = read_csv(templates)
    version = file_version([tag_map, exceptions, std_tags])
    by = collections.defaultdict(list)
    for r in rows_all:
        by[r["company_id"]].append(r)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for cid, rs in sorted(by.items(), key=lambda kv: int(kv[1][0]["rank"] or 0)):
        ident = ids.get(cid) or {"company_id": cid, "cik": rs[0]["cik"], "name": "(not in identity file)", "ticker": rs[0]["ticker"], "sic_code": "", "sector": ""}
        if tickers and ident["ticker"] not in tickers:
            continue
        rs = apply_std(rs, std)
        ce = [x for x in exc if x["company_id"] == cid]
        (out / f"{ident['ticker']}.md").write_text(build_note(ident, rs, ce, trows, version) + "\n")
        written.append(ident["ticker"])
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-map", required=True)
    ap.add_argument("--identity", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--exceptions")
    ap.add_argument("--std-tags")
    ap.add_argument("--templates")
    ap.add_argument("--tickers")
    ap.add_argument("--coverage", help="coverage_full CSV from the tag library; preferred over the sector default")
    a = ap.parse_args()
    if a.coverage:
        load_coverage(a.coverage)
    w = generate(a.tag_map, a.identity, a.out, a.exceptions, a.std_tags, a.templates,
                 set(a.tickers.split(",")) if a.tickers else None)
    print(f"wrote {len(w)} notes to {a.out}")
