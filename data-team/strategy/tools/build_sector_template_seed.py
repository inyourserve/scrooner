#!/usr/bin/env python3
"""Build the seeder input for `scrooner-map seed-sector-templates` from the APPROVED
sector templates (data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md, sections 1-3,
with the corrections of section 8, Ritwik, 2026-11-01).

Writes two files (both committed; the test regenerates them and requires equality):
  data-team/strategy/SECTOR-TEMPLATES-SEED-2026-11-01.md   the four seeder tables
  data-team/strategy/data/cohort_v1_1_sic_2026-11-01.csv   cohort v1.1 (1,000) with SIC

Inputs (all committed, read-only, no database):
  data/cohort_v1_1_proposal_2026-10-24.csv   the cohort (section 8.6)
  data/group_assignment_v2.csv               SEC SIC per company (field sic_cohort_sec);
                                             agrees with shards.csv on all 991 shared SICs
  data/cohort_cells.csv                      the 163-data-point catalog (coverage cells)
  data/metric_dependency_graph.csv           each data point's inputs; an OUT
                                             line takes every metric that REQUIRES it with it
                                             (section 6 category A "+ dependent metrics")

Mapping rules (each cites the approval):
  IN / COND            -> in_template yes (COND is decided per company by the FSN step, §4)
  OUT (A, §3) / OUT by definition (C, §8.2) -> in_template no, reason names the category
  REP (sector row replaces the cell)        -> in_template yes with a reason: the cell stays
                                             a defect until the replacement row is defined
                                             (doc 50 rule 4); dependents keep working
  Category B (current assets etc., §8.3)    -> stays IN everywhere except bdc (§8.4)
Run from the repository root:  python3 data-team/strategy/tools/build_sector_template_seed.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data-team/strategy/data"
SEED_MD = ROOT / "data-team/strategy/SECTOR-TEMPLATES-SEED-2026-11-01.md"
COHORT_OUT = DATA / "cohort_v1_1_sic_2026-11-01.csv"

# tv1.1 (2026-11-11): the Verifier FIX rows 1-5 and 8, the insurer D&A ruling and the COND revenue lines below
TEMPLATE_VERSION = "tv1.1-2026.11.11"
EFFECTIVE_FROM = "2026-11-01"

# §1 SIC rules (SIC proposes; sparse codes become one-code ranges). Everything not
# listed is `general` (incl. pharma 2834-2836/8071, managed care 6324, insurance
# brokers 6411, real-estate services 6500-6795, energy).
SIC_TEMPLATES: dict[str, list[int]] = {
    "utility": [4911, 4922, 4923, 4924, 4931, 4932, 4941],
    "bank": [6021, 6022, 6035, 6036],
    "lender": [6141, 6162, 6199],  # 6199 minus the crypto names (company assignment)
    "broker_am": [6200, 6211, 6282],
    "insurer": [6311, 6321, 6331, 6351, 6361, 6399],
    "reit_equity": [6798],  # minus the mortgage REITs (company assignment)
}

# (ticker, cik, template, reason): §1 named exceptions and §8.4-8.5 corrections.
COMPANY_ASSIGNMENT = [
    ("ARCC", "0001287750", "bdc", "§8.4: BDC (ASC 946 investment company); no SIC in the master"),
    ("BXSL", "0001736035", "bdc", "§8.4: BDC (ASC 946 investment company); no SIC in the master"),
    ("CBC", "0002065601", "bank", "§8.5: Central Bancompany, bank holding company; no SIC in the master"),
    ("NLY", "0001043219", "reit_mortgage", "§1: mortgage REIT under SIC 6798 (by name, ASSUMED)"),
    ("AGNC", "0001423689", "reit_mortgage", "§1: mortgage REIT under SIC 6798 (by name, ASSUMED)"),
    # Verifier FIX 2026-11-09 (VERIFY-TEMPLATES-AND-LADDER-2026-11-09, rows 1-3): SIC proposes, the face decides
    ("EQH", "0001333986", "insurer", "Verifier 2026-11-09: premiums and policyholder benefits on the face, no current totals (0001333986-26-000012); SIC 6411"),
    ("ACT", "0001823529", "insurer", "Verifier 2026-11-09: mortgage insurer, premiums and benefits on the face, no current totals (0001823529-26-000060); SIC 6411"),
    ("INVH", "0001687229", "reit_equity", "Verifier 2026-11-09: real estate at cost and accumulated depreciation, no current totals (0001687229-26-000016); SIC 6510"),
    ("TRNO", "0001476150", "reit_equity", "Verifier 2026-11-09: real estate at cost and accumulated depreciation, no current totals (0001476150-26-000011); SIC 6500"),
    ("MSTR", "0001050446", "general", "§1: crypto/AI miner under SIC 6199, corporate statements"),
    ("COIN", "0001679788", "general", "§1: crypto/AI miner under SIC 6199, corporate statements"),
    ("CRCL", "0001876042", "general", "§1: crypto/AI miner under SIC 6199, corporate statements"),
    ("IREN", "0001878848", "general", "§1: crypto/AI miner under SIC 6199, corporate statements"),
    ("HUT", "0001964789", "general", "§1: crypto/AI miner under SIC 6199, corporate statements"),
    ("WULF", "0001083301", "general", "§1: crypto/AI miner under SIC 6199, corporate statements"),
    ("BMNR", "0001829311", "general", "§1: crypto/AI miner under SIC 6199, corporate statements"),
]

TEMPLATES = ["general", "bank", "lender", "broker_am", "insurer", "reit_equity",
             "reit_mortgage", "utility", "bdc"]  # fmt: skip

# §2 matrix rows -> catalog data points.
GP = ["gross_profit", "gross_profit_resolved", "gross_margin", "margin_expanding_3yr",
      "piotroski_f_score"]  # fmt: skip
COR = ["cost_of_revenue", "cost_of_revenue_resolved"]
OPEX = ["operating_expenses", "operating_expenses_resolved"]
OPINC = ["operating_income", "operating_income_resolved", "operating_margin"]
RND = ["research_and_development", "rnd_intensity"]
INV = ["inventory", "inventory_days", "cash_conversion_cycle", "cf_inventory_change",
       "inventory_change_reconciliation_gap"]  # fmt: skip
AR = ["accounts_receivable", "debtor_days", "cf_ar_change", "ar_change_reconciliation_gap"]
AP = ["accounts_payable", "payables_days", "cf_ap_change", "ap_change_reconciliation_gap"]
CURRENT = ["current_assets", "current_assets_resolved", "current_liabilities",
           "current_liabilities_resolved", "current_ratio", "quick_ratio", "working_capital"]  # fmt: skip
EBITDA = ["ebitda", "ebitda_margin", "ev_ebitda", "net_debt_ebitda", "debt_to_ebitda"]
ROIC = ["roic"]
COVERAGE = ["interest_coverage_ratio"]
DE = ["debt_to_equity"]
CAPEX_FCF = ["capex", "capex_resolved", "capex_pct_revenue", "fcf", "fcf_margin", "fcf_yield",
             "fcf_per_share", "fcf_growth_yoy", "fcf_growth_3y_cagr", "fcf_growth_5y_cagr",
             "fcf_gt_net_income"]  # fmt: skip

A = "OUT (A, §3 E1 line evidence, approved §8.1)"
A_INH = "OUT (inherited bank-like default, approved as default only §8.7)"
C = "OUT by definition (C, approved §8.2): not applicable by definition"
BDC_C = "OUT by definition (bdc, §8.4): not applicable to an ASC 946 investment company"
NOT_SECTOR = "OUT: BDC-only sector row (§8.4); not a line of this sector (preparer inference, see report)"


def _out(*groups: list[str], reason: str) -> dict[str, str]:
    return {dp: reason for g in groups for dp in g}


# Per template: data point -> reason for OUT. Everything else is IN.
OUT: dict[str, dict[str, str]] = {
    "general": {},
    "bank": {
        **_out(GP, COR, OPEX, RND, INV, AR, AP, reason=A),
        **_out(OPINC, DE, EBITDA, ROIC, COVERAGE, CAPEX_FCF, reason=C),
    },
    "lender": {
        **_out(GP, COR, OPEX, RND, INV, AR, AP, reason=A_INH),
        **_out(OPINC, DE, reason=A_INH),
        **_out(EBITDA, ROIC, COVERAGE, CAPEX_FCF, reason=C),
    },
    "broker_am": {**_out(GP, RND, INV, reason=A)},
    "insurer": {
        **_out(GP, COR, RND, INV, reason=A),
        **_out(EBITDA, ROIC, COVERAGE, CAPEX_FCF, reason=C),
    },
    "reit_equity": {**_out(GP, RND, INV, reason=A), **_out(CAPEX_FCF, reason=C)},
    "reit_mortgage": {
        **_out(GP, COR, RND, INV, reason=A_INH),
        **_out(OPINC, EBITDA, ROIC, CAPEX_FCF, reason=C),
    },
    "utility": {**_out(GP, RND, reason=A)},
    "bdc": {
        **_out(GP, COR, INV, RND, CURRENT, EBITDA, CAPEX_FCF, reason=BDC_C),
    },
}
# REP (§2, §8.4): the cell stays IN as a defect until the replacement row is defined.
REP: dict[str, dict[str, str]] = {
    "bank": {"revenue": "REP: bank revenue = NII + noninterest income (B7), definition_pending (accountant)"},
    "lender": {"revenue": "REP (inherited bank-like): bank revenue (B7), definition_pending (accountant)"},
    "reit_mortgage": {
        "revenue": "REP: interest income replaces revenue, definition_pending",
        "debt_to_equity": "REP: recourse leverage replaces D/E, definition_pending",
    },
    "bdc": {
        "revenue": "REP (§8.4), RULED by the founder 2026-11-01 (relayed): revenue = total investment income as printed (bdc_total_investment_income)",
        "net_income": "RULED by the founder 2026-11-01 (relayed): the BDC earnings line = net investment income (NII) as printed",
        "bdc_total_investment_income": "RULED by the founder 2026-11-01 (relayed): total investment income as printed is the BDC revenue line",
    },
}

# §3 measured company-level exceptions inside OUT cells (19 line instances; one seed row per
# company x data point). in_template yes; §8.2 wants the evidence accession as the reason:
# not available offline, so the reason names the probe and the FSN step attaches it.
OVERRIDE_EVIDENCE = "company_filing_line_evidence (latest 10-K/10-Q) shows the line on the face"
# Removed by the Verifier FIX 2026-11-09 (rows 4-5): MTB cost_of_revenue (its only cost-like line is "Other costs of
# operations", OtherNoninterestExpense, 0000036270-26-000010 R5) and BNY accounts_receivable (only "Accrued interest
# receivable", InterestReceivable, 0001390777-26-000033 R6): the bank defaults (OUT) stand.
# Insurer D&A ruling 2026-11-11 (Dhairya asked: CB prints no capex and no D&A line). Measured on the latest 10-K
# cash-flow statement of all 41 insurer-template companies (data/insurer_cf_da_capex_lines_2026-11-11.csv, read from
# sec.gov with the declared SEC_USER_AGENT): 31 print a depreciation-type line, so D&A stays IN the insurer template;
# these 10 print none, so D&A is OUT for them (company override, evidence = accession and cash-flow R page). Capex is
# already OUT for every insurer (category C, approved §8.2).
DA_OUT = [
    ("CB", "0000896159", "0000896159-26-000005", "R8.htm", "only investment accretion and purchased-intangible amortization"),
    ("AFL", "0000004977", "0001628280-26-011402", "R10.htm", "only deferred policy acquisition cost amortization"),
    ("ACGL", "0000947484", "0000947484-26-000017", "R8.htm", "only intangible-asset amortization"),
    ("EG", "0001095073", "0001095073-26-000006", "R8.htm", "only bond premium amortization"),
    ("GL", "0000320335", "0000320335-26-000090", "R10.htm", "only deferred acquisition cost amortization"),
    ("ORI", "0000074260", "0000074260-26-000008", "R8.htm", "no depreciation or amortization line"),
    ("JXN", "0001822993", "0001822993-26-000022", "R9.htm", "only investment premium/discount amortization"),
    ("VOYA", "0001535929", "0001535929-26-000043", "R8.htm", "no depreciation or amortization line"),
    ("LNC", "0000059558", "0000059558-26-000016", "R7.htm", "no depreciation or amortization line"),
    ("ACT", "0001823529", "0001823529-26-000060", "R8.htm", "only investment, deferred-cost and intangible amortization"),
]
DA_POINTS = ("depreciation_and_amortization", "depreciation_and_amortization_resolved")

OVERRIDES = [
    ("JPM", "0000019617", "accounts_receivable", "§3: presented combined (2 lines); show under the company's own label (ruling item 3)"),
    ("BAC", "0000070858", "accounts_receivable", "§3: presented combined; show under the company's own label (ruling item 3)"),
    ("BOKF", "0000875357", "accounts_receivable", "§3: presented"),
    ("BPOP", "0000763901", "operating_expenses", "§3: presented"),
    ("C", "0000831001", "operating_expenses", "§3: presented"),
    ("STT", "0000093751", "operating_expenses", "§3: presented"),
    ("RYN", "0000052827", "inventory", "§3: presented"),
    ("LINE", "0001868159", "inventory", "§3: presented"),
    ("SUI", "0000912593", "inventory", "§3: presented"),
    ("WY", "0000106535", "inventory", "§3: presented"),
    ("WY", "0000106535", "gross_profit", "§3: presented"),
    ("BRK-A", "0001067983", "inventory", "§3: presented"),
    ("BRK-A", "0001067983", "cost_of_revenue", "§3: presented"),
    ("SNEX", "0000913760", "inventory", "§3: presented"),
    ("HOOD", "0001783879", "research_and_development", "§3: presented"),
]

OPTIONAL_ROLES = {"alt", "alt_derive", "ttm_optional"}
OPTIONAL_EDGES = {("quick_ratio", "inventory")}  # zero-when-absent (calculate.py)


def _sic(raw: str) -> str:
    m = re.search(r"cohort=(\d+)", raw) or re.search(r"sec=(\d+)", raw)
    return str(int(m.group(1))) if m else ""


def load_catalog() -> tuple[list[str], dict[str, list[tuple[str, str]]]]:
    rows = list(csv.DictReader((DATA / "metric_dependency_graph.csv").open()))
    deps: dict[str, list[tuple[str, str]]] = {}
    for r in rows:
        edges = []
        for part in r["direct_inputs(node:role)"].split(";"):
            if ":" in part:
                node, role = part.split(":", 1)
                edges.append((node.strip(), role.strip()))
        deps[r["data_point"]] = edges
    # The catalog is the 163 coverage-cell data points; the graph also holds `price`,
    # an input node, not a cell.
    cells = {r["data_point_name"] for r in csv.DictReader((DATA / "cohort_cells.csv").open())}
    return sorted(cells), deps


def with_dependents(
    out: dict[str, str], deps: dict[str, list[tuple[str, str]]], keep_in: set[str]
) -> dict[str, str]:
    """Add every data point that REQUIRES an OUT data point (transitively)."""
    out = dict(out)
    changed = True
    while changed:
        changed = False
        for dp, edges in sorted(deps.items()):
            if dp in out or dp in keep_in:
                continue
            for node, role in edges:
                if node in out and role not in OPTIONAL_ROLES and (dp, node) not in OPTIONAL_EDGES:
                    out[dp] = f"OUT: requires {node} (dependent metric, §6 category A/C)"
                    changed = True
                    break
    return out


# COND lines (Mac Ritwik's full coverage test 2026-11-11): in only for a company that has that business. OUT by
# default in every template; IN by company override where the company files a value under the concept's tags
# (data/cohort_cells.csv, the company_data_point_coverage snapshot of 2026-10-31: DATA-INFERRED; the FSN company step,
# SECTOR-TEMPLATES §4 step 2, confirms it from the statements).
COND_LINES = {
    "collaborative_arrangement_revenue": "collaborative-arrangement revenue (a collaboration business)",
    "net_lease_revenue": "net lease revenue (a lessor business)",
}
COND_DEFAULT = "COND (Ritwik coverage test 2026-11-11): in only for a company with {what}; OUT by default"
COND_IN = (
    "COND IN: the company files a value for {what} (cohort_cells.csv, coverage snapshot 2026-10-31, "
    "DATA-INFERRED; the FSN company step confirms)"
)


def cond_overrides(cohort: list[dict]) -> list[tuple[str, str, str]]:
    """(ticker, cik, data point) for every cohort company with a value for a COND line, in cohort order."""
    valued = {
        (r["company_id"], r["data_point_name"])
        for r in csv.DictReader((DATA / "cohort_cells.csv").open())
        if r["data_point_name"] in COND_LINES and r["has_value"] == "t"
    }
    return [(r["ticker"], r["cik"], dp) for r in cohort for dp in COND_LINES if (r["company_id"], dp) in valued]


def build() -> tuple[str, str]:
    catalog, deps = load_catalog()
    cat = set(catalog)
    problems = [f"{t}: {dp} not in catalog"
                for t, m in list(OUT.items()) + list(REP.items()) for dp in m if dp not in cat]  # fmt: skip
    problems += [f"override {o[0]}: {o[2]} not in catalog" for o in OVERRIDES if o[2] not in cat]
    if problems:
        sys.exit("\n".join(problems))

    cohort = list(csv.DictReader((DATA / "cohort_v1_1_proposal_2026-10-24.csv").open()))
    ga = {r["company_id"]: r for r in csv.DictReader((DATA / "group_assignment_v2.csv").open())}
    cohort_lines = ["company_id,cik,ticker,sic"]
    for r in cohort:
        cohort_lines.append(f"{r['company_id']},{r['cik']},{r['ticker']},{_sic(ga[r['company_id']]['sic_cohort_sec'])}")
    by_ticker = {r["ticker"]: r["cik"] for r in cohort}
    for t, cik, *_ in COMPANY_ASSIGNMENT + [(o[0], o[1]) for o in OVERRIDES] + [(o[0], o[1]) for o in DA_OUT]:
        if by_ticker.get(t) != cik:
            sys.exit(f"{t}: cik {cik} != cohort {by_ticker.get(t)}")

    md = [
        "# Sector templates: seeder input (generated, do not edit by hand)",
        "",
        "Generated by `data-team/strategy/tools/build_sector_template_seed.py` from the APPROVED",
        "`SECTOR-TEMPLATES-2026-11-01.md` (sections 1-3 with the section 8 corrections, Ritwik 2026-11-01).",
        "Cohort: `data-team/strategy/data/cohort_v1_1_sic_2026-11-01.csv` (v1.1, 1,000 companies, SEC SIC).",
        "Read by `scrooner-map seed-sector-templates --templates <this file> --cohort <that file>`.",
        "Every data point of the 163-item catalog not listed as `no` for a template is `yes`.",
        "",
        f"template_version: {TEMPLATE_VERSION}",
        f"effective_from: {EFFECTIVE_FROM}",
        "",
        "## Sector assignment",
        "| template | sic_from | sic_to |",
        "|---|---|---|",
    ]
    taken = sorted((s, t) for t, sics in SIC_TEMPLATES.items() for s in sics)
    ranges: list[tuple[int, int, str]] = []
    lo = 0
    for s, t in taken:
        if s > lo:
            ranges.append((lo, s - 1, "general"))
        ranges.append((s, s, t))
        lo = s + 1
    ranges.append((lo, 9999, "general"))
    md += [f"| {t} | {a} | {b} |" for a, b, t in ranges]
    md += ["", "## Company assignment", "| cik | template | reason |", "|---|---|---|"]
    md += [f"| {cik} | {t} | {tk}: {why} |" for tk, cik, t, why in COMPANY_ASSIGNMENT]
    md += ["", "## Sector defaults", "| template | data_point | in_template | reason |", "|---|---|---|---|"]
    for t in TEMPLATES:
        rep = REP.get(t, {})
        out = with_dependents(OUT[t], deps, keep_in=set(rep))
        for dp in catalog:
            if dp in out:
                md.append(f"| {t} | {dp} | no | {out[dp]} |")
            elif dp in COND_LINES:
                md.append(f"| {t} | {dp} | no | {COND_DEFAULT.format(what=COND_LINES[dp])} |")
            elif dp == "bdc_total_investment_income" and t != "bdc":
                md.append(f"| {t} | {dp} | no | {NOT_SECTOR} |")
            else:
                md.append(f"| {t} | {dp} | yes | {rep.get(dp, '')} |")
    md += ["", "## Company overrides", "| cik | data_point | in_template | reason |", "|---|---|---|---|"]
    md += [f"| {cik} | {dp} | yes | {tk}: {why}; {OVERRIDE_EVIDENCE}; accession attached by the FSN company step |"
           for tk, cik, dp, why in OVERRIDES]  # fmt: skip
    md += [f"| {cik} | {dp} | no | {tk}: insurer D&A ruling 2026-11-11, the cash-flow statement prints {why} "
           f"({acc} {page}) |"
           for tk, cik, acc, page, why in DA_OUT for dp in DA_POINTS]  # fmt: skip
    md += [f"| {cik} | {dp} | yes | {tk}: {COND_IN.format(what=COND_LINES[dp])} |"
           for tk, cik, dp in cond_overrides(cohort)]  # fmt: skip
    return "\n".join(md) + "\n", "\n".join(cohort_lines) + "\n"


def main() -> None:
    seed, cohort = build()
    SEED_MD.write_text(seed)
    COHORT_OUT.write_text(cohort)
    print(f"wrote {SEED_MD.relative_to(ROOT)} and {COHORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
