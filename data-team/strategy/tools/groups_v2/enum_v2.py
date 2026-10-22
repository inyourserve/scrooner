"""Frozen-enum PROPOSAL for group.assign@2 (AT-4.1l): groups, overlays, excluded reasons, and the mapping of every R4 FSDS family to a group or an excluded reason."""
import csv
GROUPS = ["corporate", "utility", "energy", "midstream", "managed_care", "insurance_broker", "exchange", "crypto_digital", "bank", "lender_nonbank", "insurer",
          "reit_equity", "reit_mortgage", "bdc", "asset_manager", "broker_dealer"]
T3_GROUPS = ["real_estate_operator", "exploration_miner", "pool_trust", "other_trust"]   # families outside the 986 that must not widen the enum later
OVERLAYS = ["pre_revenue", "royalty_land", "captive_finance", "conglomerate_insurer", "insurance_operations", "managed_care_operations", "crypto_holdings",
            "lending_operations (PROPOSED)", "deposit_taking_operations (PROPOSED)"]
EXCLUDED = ["subsidiary_registrant", "no_10k_yet", "successor_cik_pending", "acquired_or_deregistered", "non_screener", "foreign_private_issuer"]
R4_MAP = {  # R4 family -> (v2 group or excluded reason, note)
 "corporate_other": ("corporate", "variants energy/utility/midstream by SIC"), "pre_revenue_rd_overlay": ("corporate", "overlay pre_revenue"), "bank_thrift": ("bank", ""),
 "deposit_taker_nonbank_sic": ("bank", "bank_like (AXP SYF SOFI) when deposits+loans+provision on the face; else broker_dealer + overlay deposit_taking_operations"),
 "nonbank_lender_credit_fintech": ("lender_nonbank", "crypto/fintech 6199 by shape -> crypto_digital or bank"), "broker_dealer_exchange": ("broker_dealer|exchange", "by shape"),
 "asset_manager_adviser": ("asset_manager", "fund vehicles under 6282 -> bdc or non_screener"), "insurer_underwriter": ("insurer|managed_care", "classified balance sheet + SIC 6324 -> managed_care"),
 "insurance_agent_broker": ("insurance_broker", "EQH/ACT -> insurer"), "REIT_equity": ("reit_equity", "operating_reit variant"), "REIT_mortgage": ("reit_mortgage", ""),
 "real_estate_operator": ("corporate", "real-estate services/developers are corporate-shaped (CBRE JLL COMP); T3 may need a group if a shape template is justified"),
 "utility_waste": ("utility|corporate", "waste 4953/4955 -> corporate"), "energy": ("energy|midstream", "SIC 4610/492x by hand read"), "MLP_partnership": ("midstream|energy|corporate", "legal form is a variant, not a group"),
 "BDC_fund": ("bdc", "funds that are not operating cos -> non_screener"), "SPAC_blank_check": ("excluded.non_screener", "trust account assets"),
 "commodity_crypto_pool_trust": ("excluded.non_screener", "pool/ETF trust"), "trust_holding_other_investor": ("excluded.non_screener|corporate", "by hand read if any enters"),
 "exploration_stage_miner": ("corporate", "overlay pre_revenue when no revenue line"), "no_revenue_line_other": ("corporate", "overlay pre_revenue"),
 "nofin_statements (ABS/other)": ("excluded.non_screener", "ABS: no statements"), "no_income_statement_other": ("corporate", "hand read"),
}
if __name__ == "__main__":
    out = "/Users/vikash/wt-sector-groups/data-team/strategy/data/group_enum_v2.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["kind", "value", "note"])
        for g in GROUPS: w.writerow(["group", g, ""])
        for g in T3_GROUPS: w.writerow(["group_t3_reserved", g, "no cohort member; reserved so Gate F does not widen the enum"])
        for o in OVERLAYS: w.writerow(["overlay", o, ""])
        for e in EXCLUDED: w.writerow(["excluded_reason", "excluded." + e, ""])
        for k, (v, n) in R4_MAP.items(): w.writerow(["r4_family_map", k, v + (" | " + n if n else "")])
    print("ok")
