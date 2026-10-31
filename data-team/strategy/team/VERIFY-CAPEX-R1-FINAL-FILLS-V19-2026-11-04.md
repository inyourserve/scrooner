# Verify: capex release 1 FINAL (1,903 cells) and fills v19 (1,697) (origin/work/cash-flow/da-capex 757b06b), 2026-11-04

Seed 20261104. Release 1: 25 fresh cells (15 of 428 multi-member + 10 single). Fills: 10. Evidence class: FILING-CHECKED (cash-flow R page). Verifier 2 (scrooner-bc).

## Result
- **Release 1 FINAL: NO (2 cells, the class the last removal targeted).** 23 of 25 right.
  - DVN 9M 2018 adds "Acquisitions of property and equipment" (35M) to capex (1,851M), giving 1,886M. That is an acquisition line, held elsewhere (FANG) and removed elsewhere in this round.
  - DOW FY2024 adds "Investment in gas field developments" (203M) to capital expenditures (2,940M), giving 3,143M. Dow reports this outside its capex; a perimeter call at minimum.
  - Note: MTDR 6M 2019 prints one "Midstream capital expenditures" row without parentheses (64,106) beside a signed one (2,206). The slot treats it as an outflow (416,227K), consistent with the R-page sign drop seen at Intel. Confirm in the document if the cell matters.
- **Fills v19: NO (1 cell).** 8 of 9 readable right; HUT not parsed. AEE FY2021 takes "Capital expenditures" (2,954M) but omits "Wind generation expenditures" (525M), which is PP&E construction. Capex = 3,479M (nuclear fuel 44M excluded, as elsewhere).

## Cell table
| Set | Ticker | Period | Face | Value | Verdict |
|---|---|---|---|---|---|
| R1 multi | VST | 6M 2018 | capex (153) + solar development (21) | 174M | right |
| R1 multi | GLPI | Q1 2022 | project (2,406) + maintenance (15) | 2,421K | right |
| R1 multi | DECK | FY2016 | P&E (65,356); "tangible, intangible and other assets, net" (4,700) excluded | 65,356K | right |
| R1 multi | DVN | 9M 2018 | capex (1,851) + acquisitions of P&E (35) | 1,886M | **leak: acquisition line** |
| R1 multi | ZBH | 6M 2015 | instruments (104.0) + other PP&E (64.8) | 168.8M | right |
| R1 multi | CROX | Q1 2017 | P&E (3,243); intangibles (2,167) excluded | 3,243K | right |
| R1 multi | MTDR | FY2019 | O&G (730,161) + midstream (192,035) + other (3,701) | 925,897K | right |
| R1 multi | CHDN | 6M 2019 | maintenance (26.2) + project (32.6) | 58.8M | right |
| R1 multi | NRG | Q1 2017 | capex (268); emission allowances excluded | 268M | right |
| R1 multi | ZBH | Q1 2018 | 60.4 + 26.7 | 87.1M | right |
| R1 multi | CHDN | 9M 2017 | 26.7 + 62.4 | 89.1M | right |
| R1 multi | Z | Q1 2016 | P&E (15,212); intangibles excluded | 15,212K | right |
| R1 multi | KKR | FY2019 | fixed assets (194,569) + O&G development (12,793) | 207,362K | right |
| R1 multi | MTDR | 6M 2019 | O&G (349,915) + midstream 64,106 (unsigned) + (2,206) | 416,227K | right (sign note) |
| R1 multi | DOW | FY2024 | capex (2,940) + investment in gas field developments (203) | 3,143M | **perimeter leak** |
| R1 single | CWEN, CHWY, GPC, ENTG, SCCO, CHDN, BKNG, IR, UMBF, GSAT | various | the single printed capex line | as printed | right (10) |
| fill | AEE | FY2021 | capex (2,954) + wind generation expenditures (525) | 2,954M | **wrong: 3,479M** |
| fill | INSW | FY2019 | vessels (36,607) + other (574) | 37,181K | right |
| fill | LNT | Q1 2015 | utility (226.0) + corporate/non-regulated (19.8) | 245.8M | right |
| fill | HUT | 6M 2026 | not parsed | 616,182K | not graded |
| fill | LLY | 9M 2025 | (5,294.3) | 5,294.3M | right |
| fill | TPG | FY2021 | fixed assets (1,791) | 1,791K | right |
| fill | IT | 6M 2018 | (40,126) | 40,126K | right |
| fill | KNX | Q1 2026 | (130,037) | 130,037K | right |
| fill | IT | Q1 2021 | (12,521) | 12,521K | right |
| fill | TEX | Q1 2015 | (26.2) | 26.2M | right |

## Findings for the builder
1. Generic acquisition labels ("Acquisitions of property and equipment") belong with the acquisition hold, not only labels naming oil and gas properties.
2. "Investment in gas field developments" (DOW): perimeter list.
3. Utility generation-build lines ("Wind generation expenditures", AEE) are PP&E capex; add them as members.

SEC requests: 70.
