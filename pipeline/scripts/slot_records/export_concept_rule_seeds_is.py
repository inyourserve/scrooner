"""fsn.concept_rule seed rows for the income-statement lane (stdlib, run with -I).
Format: data-team/47-fsn-store/FORMATS-v1.md section 2. The rows are read from
is_detect.py's own constants (imported, never retyped), so the seed is exactly
the Verifier-passed detector's vocabulary.

Only the UNCONDITIONAL publishable maps become std_tag rows: a printed line
under one of these standard tags is the concept (gate G1). Everything the
detector decides with conditions (sector shapes, label and position holds,
sibling / calc-sum totals, ProfitLoss when no NCI line, the available-to-
common bridge, the cost line excluding D&A) cannot be a plain tag rule
without becoming unconditional; those are listed in NOT_EXTRACTED and stay in
the ported detector (is_detect.py --company).
usage: export_concept_rule_seeds_is.py <out.jsonl> [source_commit]
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import is_detect as d  # noqa: E402

EVIDENCE = ("is_detect slot rule, Verifier-passed (lane handoff INCOME-STATEMENT-2026-11-01); "
            "regression gate: company-mode detector reproduces 223,575 is_core slot rows exactly")
# std_tag maps: (concept, detector symbol, tags held by the detector even when printed)
STD = [
    ("revenue_sanity_resolved", "REV_TOTAL", {"RevenuesNetOfInterestExpense"}, "is.revenue_total@1"),
    ("cost_of_revenue_resolved", "COR_TOTAL", set(), "is.cost_of_revenue_total@1"),
]
SINGLE = [  # the detector's one-tag lines, read from its slot functions' own literals
    ("operating_income_resolved", "OperatingIncomeLoss", "operating_slot", "is.operating_income_line@1"),
    ("net_income_resolved", "NetIncomeLoss", "_net_income_slot", "is.net_income_line@1"),
    ("gross_profit_resolved", "GrossProfit", "gross_profit_slot", "is.gross_profit_line@1"),
]
NOT_EXTRACTED = [
    ("revenue_sanity_resolved", "RevenuesNetOfInterestExpense", "revenue_slot", "gate hold_sector_net_revenue: printed but held"),
    ("revenue_sanity_resolved", "G3_calc_sum", "revenue_slot / calc_parent_of_exactly",
     "sum of printed sibling revenue lines when a calc parent totals exactly them; needs the filing's arcs"),
    ("revenue_sanity_resolved", "hold_perimeter_label / hold_perimeter_children / hold_child_of_other_total",
     "revenue_slot", "OTHER_INCOME_LABEL / OTHER_INCOME_TAG / REV_PARENT_RX regexes demote a standard total"),
    ("revenue_sanity_resolved", "hold_sibling_* ", "revenue_siblings", "REV_ANY / SIB_TAG_NOT / SIB_LABEL regexes"),
    ("cost_of_revenue_resolved", "COR_EXCL_DA", "cost_slot", "printed cost line excluding D&A: hold_perimeter_excl_da (accountant)"),
    ("cost_of_revenue_resolved", "G3_calc_sum / hold_sibling_custom", "cost_slot", "COR_LABEL regex siblings"),
    ("net_income_resolved", "ProfitLoss", "_net_income_slot", "G1b only when the face prints no NCI or preferred line below it"),
    ("net_income_resolved", "NetIncomeLossAvailableToCommonStockholdersBasic", "available_to_common_bridge",
     "G2b only when the face bridges ProfitLoss to it through NCI / subsidiary-preferred lines"),
    ("net_income_resolved", "G2_nci_identity", "_net_income_slot", "tie ProfitLoss - NCI_RX lines = NetIncomeLoss (a filing_check)"),
    ("all", "shape_of: hold_sector_bank / insurer / bdc", "shape_of", "BANK, INSURER_RX, BDC face shapes hold every IS concept"),
    ("operating_income_resolved", "hold_label_before_tax / hold_position_below_pretax", "operating_slot",
     "BEFORE_TAX_LABEL regex and position vs PRETAX_RX / tax line (a label only demotes)"),
    ("net_income_resolved", "hold_label_noncontrolling / hold_position_above_tax", "_net_income_slot", "NCI_LABEL regex, position vs tax"),
    ("gross_profit_resolved", "hold_label_not_gross", "gross_profit_slot", "GP_LABEL regex"),
    ("all", "custom-tag lines (hold_custom_*)", "*_slot", "custom tags are held, never mapped by calc position in this lane"),
    ("all", "G2_gross_identity", "gross_identity", "revenue - cost = gross profit (a filing_check, design section 5)"),
    ("all", "primary_face / EPS_TAGS", "primary_face", "which IS report is the face; co-registrant parent = the one with EPS"),
]


def literal_in(fn_name, tag):
    import inspect
    return f'"{tag}"' in inspect.getsource(getattr(d, fn_name))


def main(out_path, commit=None):
    commit = commit or subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                                      cwd=Path(__file__).parent).stdout.strip()
    rows = []
    for concept, sym, held, rule in STD:
        for tag in sorted(getattr(d, sym) - held):
            rows.append((concept, tag, rule))
    for concept, tag, fn, rule in SINGLE:
        assert literal_in(fn, tag), (fn, tag)  # the tag is the detector's own literal
        rows.append((concept, tag, rule))
    seen = set()
    with open(out_path, "w") as f:
        for concept, tag, rule in rows:
            assert (concept, tag) not in seen
            seen.add((concept, tag))
            f.write(json.dumps({"canonical_concept": concept, "stmt": "IS", "match_kind": "std_tag",
                                "tag": f"us-gaap:{tag}", "position": None, "components": None, "priority": 10,
                                "era_from": None, "era_to": None, "rule_id": rule, "source_commit": commit,
                                "evidence": EVIDENCE}) + "\n")
    print(f"{len(rows)} seed rows -> {out_path}")
    nx = Path(out_path).with_name("is_not_extracted.md")
    with open(nx, "w") as f:
        f.write("# Income-statement rules not expressible as concept_rule seeds (FORMATS-v1)\n\n"
                "They stay in the ported detector (is_detect.py --company); the seed carries only the "
                "unconditional standard-tag maps.\n\n| concept | rule | detector symbol | why |\n|---|---|---|---|\n")
        for row in NOT_EXTRACTED:
            f.write("| " + " | ".join(row) + " |\n")
    print(f"{len(NOT_EXTRACTED)} not extracted -> {nx}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
