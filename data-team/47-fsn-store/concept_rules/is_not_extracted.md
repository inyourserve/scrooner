# Income-statement rules not expressible as concept_rule seeds (FORMATS-v1)

They stay in the ported detector (is_detect.py --company); the seed carries only the unconditional standard-tag maps.

| concept | rule | detector symbol | why |
|---|---|---|---|
| revenue_sanity_resolved | RevenuesNetOfInterestExpense | revenue_slot | gate hold_sector_net_revenue: printed but held |
| revenue_sanity_resolved | G3_calc_sum | revenue_slot / calc_parent_of_exactly | sum of printed sibling revenue lines when a calc parent totals exactly them; needs the filing's arcs |
| revenue_sanity_resolved | hold_perimeter_label / hold_perimeter_children / hold_child_of_other_total | revenue_slot | OTHER_INCOME_LABEL / OTHER_INCOME_TAG / REV_PARENT_RX regexes demote a standard total |
| revenue_sanity_resolved | hold_sibling_*  | revenue_siblings | REV_ANY / SIB_TAG_NOT / SIB_LABEL regexes |
| cost_of_revenue_resolved | COR_EXCL_DA | cost_slot | printed cost line excluding D&A: hold_perimeter_excl_da (accountant) |
| cost_of_revenue_resolved | G3_calc_sum / hold_sibling_custom | cost_slot | COR_LABEL regex siblings |
| net_income_resolved | ProfitLoss | _net_income_slot | G1b only when the face prints no NCI or preferred line below it |
| net_income_resolved | NetIncomeLossAvailableToCommonStockholdersBasic | available_to_common_bridge | G2b only when the face bridges ProfitLoss to it through NCI / subsidiary-preferred lines |
| net_income_resolved | G2_nci_identity | _net_income_slot | tie ProfitLoss - NCI_RX lines = NetIncomeLoss (a filing_check) |
| all | shape_of: hold_sector_bank / insurer / bdc | shape_of | BANK, INSURER_RX, BDC face shapes hold every IS concept |
| operating_income_resolved | hold_label_before_tax / hold_position_below_pretax | operating_slot | BEFORE_TAX_LABEL regex and position vs PRETAX_RX / tax line (a label only demotes) |
| net_income_resolved | hold_label_noncontrolling / hold_position_above_tax | _net_income_slot | NCI_LABEL regex, position vs tax |
| gross_profit_resolved | hold_label_not_gross | gross_profit_slot | GP_LABEL regex |
| all | custom-tag lines (hold_custom_*) | *_slot | custom tags are held, never mapped by calc position in this lane |
| all | G2_gross_identity | gross_identity | revenue - cost = gross profit (a filing_check, design section 5) |
| all | primary_face / EPS_TAGS | primary_face | which IS report is the face; co-registrant parent = the one with EPS |
