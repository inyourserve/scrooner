# Verify: quick_ratio fix re-draw (work/data-engineer/quick-ratio-fix f96d17c, dry-run), 2026-10-25

Verifier 2. Decisions re-computed with the branch's own `quick_ratio_evidence.py` at f96d17c (run read-only on the named, materials and false-NULL-candidate companies); random pools from `quick_ratio_plan_v2.json` (1e17f7e run) and the f96d17c planner run. Seed random.Random(20261104). Each cell checked on the balance sheet of the filing whose period is the cell date. Every planned cell's stored value equals the current ratio, so a cell is a FALSE NULL exactly when its own balance sheet shows no inventory line. FILING-CHECKED.

## Result: GATE FAILS. 14 false NULLs in this draw (15 with BBIO 2023), all still NULL at f96d17c with reason `inventory_presented_not_extracted`.

## 1. The 7 earlier false NULLs and CP
| Cell | f96d17c | Verdict |
|---|---|---|
| INSM 2016-12-31, MELI 2015-06-30, AXSM 2022-03-31, CYTK 2025-09-30, VAL 2018-09-30, WES 2018-06-30 | kept | fixed |
| BBIO 2023-03-31 | NULL (presented_not_extracted) | **FALSE NULL**: the face (0000950170-23-017812 R2) foots without inventory: 407,368 + 34,122 + 49,803 + 10,761 + 25,503 + 25,145 = 552,702 = total current assets. If our stored current lines do not reproduce that, the defect is our extraction, not inventory; the stored 5.722 is right |
| CP 2017-03-31 | NULL (inventory_like_tag_unmapped) | right to blank (face "Materials and supplies" 201); under the founder ruling the reason should read materials_supplies_line_present |

## 2. Fixtures
NKE 2026-08-31, BA 2026-06-30, GAP 2026-08-01, AZO 2026-05-09, XOM 2026-06-30: all NULL (inventory on the face; stored = current ratio = wrong). Right.

## 3. Likely-false-NULL pool (742 cohort cells since 2015 at 33 companies dated before the company's first common inventory-tag fact; 20 drawn, one per company)
Right to NULL (inventory-like current line on the face) 15: AWK 2021-03-31 materials and supplies 52; LUV 2020-12-31 parts and supplies 414; ATO 2017-09-30 gas stored underground; LNT 2016-06-30; NFG 2016-12-31; EME 2023-12-31 inventories 110,774K; EXC 2017-03-31; NSC 2024-09-30; NI 2024-06-30; CSX 2019-03-31; AAL 2024-12-31 aircraft fuel, spare parts and supplies 2,638; Z 2019-06-30 inventory 552,823K; UNP 2017-06-30; IMO 2016-09-30; CP 2016-03-31.
**False NULLs 5** (no inventory line on that balance sheet):
| Cell | Accession | Face current assets |
|---|---|---|
| SWX 2021-06-30 | 0001692115-21-000040 | cash, receivables, accrued utility revenue, tax receivable, deferred purchased gas costs, prepaid = 1,006,795K |
| TGTX 2021-06-30 | 0001558370-21-010837 | cash, STI, receivables, prepaid R&D, other = 455,068K |
| IOVA 2022-09-30 | 0001558370-22-016295 | cash, STI, prepaid = 369,884K |
| IBRX 2020-09-30 | 0001564590-20-052488 | cash, prepaid, securities = 98,018K |
| BBIO 2024-03-31 | 0000950170-24-052165 | cash, securities, receivables, restricted cash, prepaid = 783,424K |

## 4. BBIO-type draw (15 cohort cells with reason presented_not_extracted outside the pool)
Right to NULL 6: HSIC 2018-12-29, SNX 2020-11-30, RL 2024-09-28, NWSA 2024-06-30, AVT 2016-07-02 (inventory lines), LDOS 2018-09-28 ("Inventory, prepaid expenses and other current assets" combined line). EOG 2017-03-31: no filing for that date in core.filing (not checked).
**False NULLs 8**: DVN 2020-03-31 (0001564590-20-021639: cash, restricted cash, receivables, discontinued-ops assets, other), QXO 2018-03-31 (0001185185-18-000864), GOOG 2016-03-31 (0001652044-16-000021), T 2015-06-30 (0000732717-15-000079), MP 2020-09-30 (0001801368-20-000009: pre-merger SPAC, cash and prepaid), RGLD 2015-09-30 (0001104659-15-075966: royalty company), ASTS 2023-09-30 (0000950170-23-063737), VTRS 2020-09-27 (0001193125-20-290294: pre-merger shell, restricted investments 11,413). None shows an inventory line; each stored value is CA/CL.

## 5. Part 2: materials-and-supplies hides (10 drawn from the f96d17c run: cohort 299 cells at 32 companies with a MaterialsSupplies fact)
All 10 (SWKS 2023-03-31, EW 2024-09-30, ENTG 2025-06-28, NXPI 2023-12-31, PWR 2024-12-31, STE 2022-09-30, WTS 2021-12-31, ECHO 2025-03-31, FLEX 2024-03-31, ST 2016-12-31) print an INVENTORY line on the face (e.g. SWKS 1,257,000K; WTS raw materials / WIP / finished goods = 370.7M); none has a current materials-and-supplies face line. Blanking is right (stored = current ratio is wrong), but the reason is wrong: the MaterialsSupplies tag here is an inventory component in a note. The founder ruling covers a current materials-and-supplies FACE line (railroads, utilities, airlines); these cells should carry inventory_presented_not_extracted, and better, a value from the face inventory line.

## Root cause of the remaining false NULLs
`inventory_presented_not_extracted` still comes from the latest-statement evidence whenever the footing test cannot clear the cell; for pre-revenue biotechs, SPAC/shell predecessors, royalty and service companies the footing fails on our stored lines (not on the face), so the fallback NULLs a right value. Rule: if the period's own face shows no inventory line (statement role, current section), keep the value; use latest-statement evidence only for periods with no balance-sheet presentation data at all.
