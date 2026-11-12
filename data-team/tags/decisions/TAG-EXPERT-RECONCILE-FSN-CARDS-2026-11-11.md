# Tag Expert reconcile: Dhairya's four FILING-CHECKED FSN cards (main 9288f86) vs the family cards, 2026-11-11
Inputs: cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md (103 tags) and library/fsn-*.csv; 22-FILING-LESSONS-LEDGER.md (17 new cases); data-team/companies/*.md. `card-notes-51-100-2026-11-11.md` is NOT in any ref I can reach (main, docs/tag-expert-playbooks, work/ritwik-cloud/tag-decisions-2026-11-11): not absorbed.
Rule used: the filing and the founder decisions in doc 02 win over any card, mine included.

## Resolved (winner, evidence)
| # | Topic | Winner | Evidence | Changed |
|---|---|---|---|---|
| C1 | Sign of IncreaseDecreaseInAccountsReceivable / Inventories | **new cards**: stored positive = the asset INCREASED (cash outflow) | SEC companyconcept read today: AAPL FY2025 AR printed (6,682), stored +6,682,000,000; inventory printed 1,400, stored −1,400,000,000 (0000320193-25-000079) | TOP-TAGS rows 66, 67 and 17 movement rows in 096-359 corrected |
| C2 | ProceedsFromIssuanceOfCommonStock always positive | **new** | TRMB stored −32,500,000 (0000864749-26-000108 R7) | TOP-TAGS row 115 |
| C3 | "UN = co-registrant statement" | **both, scoped**: UN is mixed. Co-registrant on CF (DUK 0001326160-26-000014 R14); but Revvity 0000031791-26-000012 R4 (its only income statement) and PLNT 0001193125-15-310710 report 4 (the real entity) are UN too. Rule: a UN statement is excluded only when its columns carry a co-registrant/LegalEntityAxis member other than the registrant; else classify it by its lines | fsn-cash-flow §1.2 needs this scope note |
| C4 | Total liabilities when not printed | **new**: not_presented; derivation retired | doc 02 2026-11-01 item 4 "EPS and instants are never derived" | TOP-TAGS row 37, library `Liabilities`, balance-sheet §1/§7 identity route marked SUPERSEDED |
| C5 | Parent equity from total − NCI | **new**: not_presented when NCI printed and no parent line; the incl-NCI tag maps when no parent and no NCI line | doc 02 item 4 | TOP-TAGS row 70, library row |
| C7 | CCRC on the BS | **new, conditional**: cash only as the sole cash line with a label that names no restricted cash (FITB R2 4,374M); a restricted-cash label = combined (doc 02 item 2: a combined line is never mapped as one concept) | library row, TOP-TAGS row 15 |
| C8 | CashAndDueFromBanks as bank cash | **family card**: a component when interest-bearing deposits are printed beside it (PNC 0000713676-26-000020 R5 6,777M; EWBC); bank cash = the face line(s) equal to CF ending cash | fsn-balance-sheet-assets §18.4 needs the PNC exception |
| C9 | 2020 PP&E + finance-lease ROU tag | **new**: ppe_net with flag `incl_finance_lease_rou`; AMZN prints the same 2019 value 72,705M under PPENet (0001018724-20-000004 R6) and under the new tag (0001018724-21-000004 R6), so it is the same line, not a break | balance-sheet §8 "not comparable" wording narrowed: comparable within a company, flagged across companies |
| C10 | ReceivablesNetCurrent with notes/other | **new**: combined (XOM R5 44,562M; AMZN R6; doc 02 item 2) | library row; my ranks 1-50 ruling (d) CORRECTED |
| C11 | NonoperatingIncomeExpense | **new**: combined by default (AMZN R4 17,336 incl. interest (2,274); GPC R5) | library row (matches my ruling (f)) |
| C12 | Buybacks with excise / withholding wording | **new**: combined (LRCX R6 l17; founder 2026-11-04 item 4 excludes both) | library row |
| C13 | D&A incl. impairment | **new**: combined for perimeter labels (XOM, HPQ, DUK); CF-vs-IS for nuclear-fuel utilities keeps the Verifier ruling (IS D&A) until a DUK IS read | library row |
| C14 | Continuing-ops EPS | **new** (= my net-income §10 decision; VRSN R5 8.83/8.81) | TOP-TAGS row 6 |
| C15 | Cover (dei) share count as PGR alternate | **family card**: never the cover count (other date); PGR = not_presented. EQ rows: period-end only | fsn-balance-sheet-liabilities-equity needs this fix |
| C16 | LongTermDebtCurrent/Noncurrent | no conflict: components of total_debt_resolved; the Mac ranks_1_50 "exclude" (D1) is wrong | — |
| C17 | IntangibleAssetsNetIncludingGoodwill at SCCO | **new**: combined. My "no goodwill line at SCCO" is WITHDRAWN: SCCO files Goodwill 41.9M separately (companyconcept, 0001104659-26-021492) | balance-sheet §8 |
| C18 | PreferredStockValue = par | **both**: not always the carrying amount (MET 0 vs $2,905M preference; PLD at liquidation preference 63,948K); excluded either way | — |

## Ruling questions (not mine to decide; for Dhairya / standardization lead)
- C6 net income = ProfitLoss − NCI (a DURATION, two printed face lines, same column; doc 02 forbids deriving only EPS and instants): my cards allow it with a flag (WELL, PNC); the new CSV blanks it (TFC, PNC). Needs a ruling.
- Sums of printed duration components (TMUS interest, NEE capex, BKNG/SCHW D&A, T cost of revenue, SCCO incurred − capitalised): allowed? Same question.

## Unresolved, need a filing read
- C19 UNH: company note maps ProfitLoss in 1 filing "NetIncomeLoss not printed" vs fsn-income-statement D1 (NetIncomeLoss in all 45). C20 MCK redeemable NCI 1,430M vs 943M (0000927653-26-000069): probably different dates. C13 DUK IS D&A.

## My earlier answers CORRECTED by this reconcile
- TAG-EXPERT-ANSWERS-RITWIK-CLOUD-2026-11-11: **CB cash = 2,470 − 198** and **VZ/T/MO/COP equity = incl-NCI total − MinorityInterest** derive INSTANTS: withdrawn; both are not_presented with reason (doc 02 item 4). **GILD/DHR combined cash tag "map with flag"**: withdrawn; it is a combined line shown under its own label (doc 02 item 2; founder 2026-11-01 sector ruling item 3).
- TAG-EXPERT-ANSWERS-RITWIK-RANKS-1-50: (a) "several classes: sum the classes" withdrawn (instant derivation): not_presented (Dhairya 2026-11-12); (d) "ReceivablesNetCurrent sole line → AR with flag" withdrawn: combined unless the label is plain trade AR; (e) stands (same line, flagged).

## Update 2026-11-11 (later): Dhairya rulings, open items settled, Ritwik card notes 1-30 absorbed
**Dhairya accepted fixes (1)-(3)** (UN scope, PGR not_presented, PNC CashAndDueFromBanks component).
**Rulings (Dhairya 2026-11-11, D3 extended)** — replace the two ruling questions above:
- (a) Sums of PRINTED duration components with their printed signs, same statement and section: ALLOWED (TMUS interest, NEE capex, SCCO incurred − capitalised, BKNG/SCHW D&A, T/VZ/DIS cost of revenue).
- (b) NI = ProfitLoss − NCI: ALLOWED only when both are printed on the face of the same income statement, the NCI line is printed as the deduction, and no NI-attributable-to-parent line (`NetIncomeLoss`) is printed. Never across statements; never for instants (parent equity = total − NCI stays forbidden). My reading: an "attributable to common" line (NIACSB, after preferred) does not block it (PNC 0000713676-26-000020 IS l34-35: 6,997 − 61 = 6,936M, Ritwik note 22) — flagged to Dhairya.
**Open items settled (FSN store = SEC's own Financial Statement and Notes data for the accession; read 2026-11-11)**
- C19 UNH: the 10-Q 0000731766-26-000197 IS prints `ProfitLoss` "Net earnings" l23, NCI l24 AND `NetIncomeLoss` l25 "…attributable to UnitedHealth Group common shareholders". So NI = NetIncomeLoss there too; the UNH company note ("ProfitLoss where NetIncomeLoss is not printed, 1 filing") is WRONG. fsn-income-statement D1 stands.
- C20 MCK: no conflict, different dates: 943M is 2026-03-31; 0 at FY2022-FY2025; 1,271-1,459M FY2015-FY2021. My "1,430M" matched no year-end: withdrawn.
- C13 DUK FY2025 10-K 0001326160-26-000014: IS l15 `CostDepreciationAmortizationAndDepletion` "Depreciation and amortization" 6,324M (2024 5,793; 2023 5,253) vs CF l4 `DepreciationDepletionAndAmortization` "Depreciation, amortization and accretion (including amortization of nuclear fuel)" 7,704M: the CF line is COMBINED; serve the IS line (the Verifier's utility ruling confirmed).
**GILD/DHR reinstated** (Ritwik note 9): BS l3 `CashCashEquivalentsRestrictedCash…` with plain labels "Cash and cash equivalents" (GILD 0000882095-26-000006, = CF ending 7,564M) and "Cash and equivalents" (DHR 0000313616-26-000062, 4,615M), no restricted line: the sole cash line with no restricted wording = cash (the C7 rule). My withdrawal of these two is reversed; no flag needed. CB (note 18, Dhairya): served as printed, labelled "includes restricted cash".
**Ritwik (cloud) card notes 1-30** (data-team/tags/decisions/card-notes-51-100 and -101-200-2026-11-11.md on work/ritwik-cloud/tag-decisions-2026-11-11 35e120ba; DATA-INFERRED from fsn.*) agree with the cards after this reconcile; folded as below. No conflicts except note 22 (see ruling (b) reading).

## Update 2026-11-12: D3 narrowed to doc 02 (Dhairya)
- Sums of printed face lines are allowed for DURATIONS only: operating expenses, cost of revenue, interest, capex, D&A, NI = ProfitLoss − NCI (ruling (b) conditions).
- INSTANTS: no sums, with one exception: total_debt, which the founder defined as a sum including finance leases (doc 02, 2026-11-04 item 5).
- So: total liabilities with no printed line = not_presented; inventory with no printed total = not_presented; shares outstanding printed only per class = not_presented.
- Bank cash split across BS lines (JPM "cash and due from banks" + "deposits with banks" = 343,338M): serve the CF statement's PRINTED ending-cash line (343,338M), labelled. Accepted.
