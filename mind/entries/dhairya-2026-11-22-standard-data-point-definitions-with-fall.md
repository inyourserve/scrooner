---
id: dhairya-2026-11-22-standard-data-point-definitions-with-fall
title: Dhairya 2026-11-22: standard data-point definitions with fallback badges; 5 definition calls; combined/perimeter hides reversed
kind: decision
tags: ruling, standard-definitions, data-points, badges, screener
paths: pipeline/src/scrooner_pipeline/metrics/registry/data_points.csv, pipeline/src/scrooner_pipeline/mapper/sector_templates.py
evidence: DATA-INFERRED
status: active
source: Dhairya 2026-11-22 under founder delegation (founder 'go ahead' 2026-11-22: screener, one standard definition)
created: 2026-11-22
verified: 2026-11-22
---
registry/data_points.csv (loaded by metrics/registry.load_data_points) holds one row per display data point x sector: definition, fallback order (as_printed > combined:<what> > derived:<formula, one filing> > perimeter:<diff>), filter note. Hide only for sector not applicable or figure in no filing. Calls: (1) managed-care gross profit = revenue - (medical costs + cost of products sold), one filing, badge perimeter:medical costs as cost of revenue (UNH); (2) a line holding two template data points serves the one its label names first, the other cell is included_in:<dp>, a filter-exclusion reason, never blank or zero; (3) by-nature presenters: SG&A = G&A alone, badge perimeter:general and administrative only (BLK); (4) a printed zero finite-lived intangible balance gives amortization VALUE 0, badge derived:zero_balance:<line>, only when that period's filing prints the zero; (5) banks and insurers: current_assets/current_liabilities sector-level not applicable (unclassified balance sheet), narrows Ritwik approval SECTOR-TEMPLATES s8.3; bdc OUT set (s8.4) added to sector_templates.GROUP_OUT. Reversed: X17 only_combined hide, SECTOR-TEMPLATES s5(a) (combined AP feeds payables days with badge), ruling 2026-11-14 c (SG&A from S&M + G&A of one filing allowed), opex-inside-total-costs hides (derive total - COR - interest). Narrowed: ruling 21 (perimeter badge), X29/X100 (combined shows), ruling 5 of 2026-11-17 (identity derives 0), doc 02 instants-never-derived (one-balance-sheet differences). Kept: one vintage, finer figure wins, one filing per derivation, EPS never derived, polarity, total_debt/capex/buyback perimeters, SBC source rules. Test on 888 hidden/open filing-read cells: 281 convert from their own quotes (114 combined, 89 derived, 14 perimeter, 64 printed/stated values); 177 need a re-read to quote the combined line's number.
