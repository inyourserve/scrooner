# Template-group audit, top 1,000 (2026-11-13)

For Dhairya. Every cohort v1.1 company's template group (tv1.1-2026.11.11 seed plan built by
`scrooner_pipeline.mapper.sector_templates` over the v1.1 cohort with SEC SIC), checked against how its filing presents
the statements (the 519 document-first docmaps on main and the work/reads/* branches) and against the blind-grade answer
key on main. Per company: `data-team/strategy/data/template_group_audit_top1000_2026-11-13.csv` (rank, CIK, ticker, SIC,
template, docmap used, flags, evidence). Tool: `data-team/strategy/tools/template_group_audit.py`.

## Counts
- Companies with no group: **0 of 1,000**. 997 are assigned by SIC range. The 3 with no SIC in the master have explicit
  overrides: ARCC and BXSL (bdc), CBC (bank).
- Groups: general 765, reit_equity 53, utility 51, bank 42, insurer 41, broker_am 37, lender 7, bdc 2, reit_mortgage 2.
- Companies with a group that conflicts with the filing or the answer key: **50** (only 519 of 1,000 have a docmap yet), as follows.

| conflict | companies | what it is |
|---|---|---|
| Seed keeps the line IN, but the OUT ruling or the answer key keys it OUT | 46 | Template layer, not company assignment: the bank (19), insurer (16), lender (3) and broker_am (SF) seeds keep current_assets and current_liabilities IN; broker_am keeps cost_of_revenue IN (SF). The general (6) and utility (1) seeds keep net_interest_income IN, which the key keys OUT. Bank sga_expense: ONB, CFR. BRK-A: its seed override keeps cost_of_revenue and inventory IN, the key OUT. UHAL (general) is keyed OUT for current_assets, current_liabilities, gross_profit and R&D. |
| Financial group, but the face prints operating lines | 7 | SEIC, EVR (broker_am: classified balance sheet, AssetsCurrent/LiabilitiesCurrent on R3); FRHC, JEF (broker_am: CostOfGoodsAndServicesSold on the face); SOFI (lender: CostOfRevenue on R5); AGNC (reit_mortgage: AssetsCurrent on R2, to re-read); L (insurer: cost_of_revenue keyed on l:OperatingExpensesAndOther, a reader error, not a group problem). |
| General group, unclassified balance sheet and no cost-of-revenue line | 3 | PHM, LEN (homebuilders), GATX (lessor). Likely right as general; the readers should key these lines not_presented, not OUT. |
| Informational: general group with a financial SIC (6000-6799) | 30 | Managed care (UNH, ELV, CI, HUM, CNC, MOH, OSCR), insurance brokers (MRSH, AJG, AON, WTW, BRO, ERIE, RYAN), crypto/miners (MSTR, COIN, CRCL, BMNR, IREN, HUT, WULF), real-estate services (CBRE, JLL, COMP), royalty/IP (TPL, LB, RGLD, SSRM, IDCC, DLB). These follow the approved SECTOR-TEMPLATES section 1 rules; listed only so a reader expects general. |

## What I fixed and what is left
- **Not fixed on main.** This session pushes only to its work branches, and the groups come from the approved
  SECTOR-TEMPLATES-2026-11-01.md (Ritwik approval), so a seed change needs that approval. The proposed change: OUT for
  current_assets and current_liabilities in the bank, insurer, lender, broker_am and reit_mortgage templates (bdc already
  OUT); OUT for net_interest_income in general and utility; then rebuild the seed and re-run the coverage snapshot.
  Until then the readers apply the ruling in their docmaps.
- **Readers:** until the seed changes, apply the OUT ruling in the docmaps for not_presented rows of cost_of_revenue,
  gross_profit, research_and_development, inventory, current_assets and current_liabilities in the bank, insurer, lender,
  broker_am, bdc and reit_mortgage groups (the SF key errors show broker_am needs it too). Rows the filing prints stay
  mapped (SEIC, EVR, FRHC, JEF). The 601-700 docmaps from this session are superseded by the Actions rerun (eec462b4),
  so this session does not re-key them; the rule is in `data-team/strategy/tools/docmap_check_pass.py` history
  (OUT_GROUP) if the hand pass wants it.
