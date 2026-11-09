# Playbook: revenue_sanity_resolved

Card: [`../cards/revenue.md`](../cards/revenue.md) (perimeters: XOM/COP excise, bank `Revenues`, GE; FILING-CHECKED rows there). Method: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows).

## 1. Mapped (`is.revenue_total@1`), 603 of 632

| Rank | Tag on the IS face | Companies |
|---|---|---|
| 1 | `RevenueFromContractWithCustomerExcludingAssessedTax` | 368 |
| 2 | `Revenues` | 240 |
| 3 | `RevenueFromContractWithCustomerIncludingAssessedTax` | 45 |
| 4 | `RegulatedAndUnregulatedOperatingRevenue` | 3 |

(Rows add to more than 603: some filings print two of these, e.g. a contract-revenue subtotal and a `Revenues` total; the `hold_perimeter_*` / `hold_sibling_*` gates in `is_not_extracted.md` decide which one.)

## 2. The 29 gap companies

| Class | Companies | Pattern | Examples |
|---|---|---|---|
| Regional banks: NII + noninterest income, no revenue total | 18 | `InterestAndDividendIncomeOperating`, `InterestExpenseOperating`, `InterestIncomeExpenseNet`, `NoninterestIncome`, no `Revenues` line | COF 927628, CFG 759944, FITB 35527, HBAN 49196, MTB 36270, TFC 92230, USB 36104, CBSH 22356, EWBC 1069157, FHN 36966, FNB 37808, GBCI 868671, ONB 707179, PNFP 2082866, PB 1068851, UMBF 101382, WAL 1212545, WTFC 1015328 |
| Card issuer / broker / universal bank with a printed net-revenue total | 4 | `RevenuesNetOfInterestExpense` "Total revenues net of interest expense" | AXP 0000004962-26-000080 R3 l26; GS 886982; JPM 19617; MS 895421 |
| Custodian | 1 | BNY 1390777: custom `TotalRevenuesIncludingRevenueGeneratedByVariableInterestEntities` "Total revenue" | |
| Mortgage REITs | 2 | NII only (`InterestIncomeExpenseNet`, `InterestExpenseOperating`) | AGNC 1423689, NLY 1043219 |
| Real estate with a rental-income line as the only revenue line | 2 | `OperatingLeaseLeaseIncome` "Rents and other single-family property revenues" / "Rental income" | AMH 0001562401-26-000010 R5 l7; Vivmark 0001193125-26-051433 R4 l2 |
| Statement-class trap (README §2) | 2 | real IS is `stmt=UN` / `CI` | Revvity 0000031791-26-000012 R4; GATX 0000040211-26-000018 R6 |

The current design holds bank, insurer and BDC faces on purpose (`shape_of: hold_sector_*`) and holds `RevenuesNetOfInterestExpense` (`hold_sector_net_revenue`, printed but held). So 25 of the 29 (banks, brokers, custodian, mortgage REITs) are **sector-template decisions, not tag gaps**.

## 3. Candidates (not approved)

1. **`OperatingLeaseLeaseIncome` as revenue, when it is the only line in the face's revenue block** (AMH, Vivmark). Structural test: the line sits directly under a `RevenuesAbstract` / "Revenues" header, or is the first line of the IS before the expenses abstract, and no other revenue-family line exists. It is lease income under ASC 842, which for a landlord is its revenue. Wintrust (1015328) also prints this tag, but it is a bank: the shape hold must win. Coexistence check needed against companies where the tag is a sibling of a `Revenues` total (there it is a component).
2. **`RevenuesNetOfInterestExpense` for brokers and card issuers** (AXP, GS, JPM, MS): this is the industry's own top line (net revenues). It is a perimeter decision for the Standardization Lead or the founder, not a tag question. The tag is unambiguous, and so is its meaning.
3. **Bank revenue = `InterestAndDividendIncomeOperating` + `NoninterestIncome`** (total revenue as screeners show it) or **`InterestIncomeExpenseNet` + `NoninterestIncome`** (net revenue, the common bank convention): a formula choice for the sector template. Both components are safe bank tags (card: interest.md §6, 30/30 FILING-CHECKED). Trap: `InvestmentIncomeInterest` is never bank total interest income (seven banks, three meanings).

## 4. Traps
- `Revenues` at a bank can be net revenue (Citigroup, card FILING-CHECKED).
- Excise and assessed taxes: `...IncludingAssessedTax` (45 companies) includes excise (XOM/COP in the card); including vs excluding assessed tax is a perimeter difference, not a synonym.
- Sub-totals: product/service subtotals (`RevenueFromContractWithCustomer...` with a `ProductOrServiceAxis` member) appear as separate face lines; never sum dimensioned facts with the total.
- The IS face may be classified `UN`/`CI` (README §2).
