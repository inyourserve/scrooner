# Playbook: interest_expense_resolved

Card: [`../cards/interest.md`](../cards/interest.md) (meanings, eras, bank pair rule; several rows FILING-CHECKED there). Method and limits: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows).

## What the data point is
Gross interest expense for the period (duration, debit), before netting interest income. Banks: total interest expense (deposits + borrowings), not net interest income.

## 1. Face patterns already mapped (`is.interest_expense_total@1`), 427 of 632

| Rank | Tag on the IS face | Companies | Note |
|---|---|---|---|
| 1 | `InterestExpenseNonoperating` | 235 | 2024+ taxonomy; non-bank, below operating income (AMZN, PLD in the card) |
| 2 | `InterestExpense` | 124 | operating+nonoperating total |
| 3 | `InterestExpenseOperating` | 53 | banks' "Total interest expense" (JPM, BAC, C); also rental/finance companies (HTZ) |
| 4 | `InterestAndDebtExpense` | 16 | may include extinguishment items: perimeter flag (TXN, ODFL, OXY in the card) |

## 2. The 205 gap companies, by what their IS face shows

One class per company, first match wins in this order:

| Class | Companies | What it is | Example (accession, R, line) |
|---|---|---|---|
| Net interest tag only (`InterestIncomeExpenseNonoperatingNet` 76, `InterestIncomeExpenseNet` 21 non-bank, `InterestRevenueExpenseNet`) | 98 | "Interest expense, net", "Financing costs, net", "Interest (income) expense, net". **Not gross interest expense.** | TJX 0000109198-26-000008 R3 l4 `InterestRevenueExpenseNet` "Interest (income) expense, net", stored **+121M** (net INCOME in FY2026: sign trap; FILING-CHECKED R3 prints "Interest (income) expense, net (121)") |
| Other interest wording on a non-interest tag | 30 | interest inside "interest and other", interest income lines, etc. | (mixed) |
| No interest line on the IS face | 22 | interest only in the notes or inside "other income (expense), net" (AAPL 320193, MSFT 789019, GOOGL 1652044 among the 22) | MSFT 789019, AAPL 320193 |
| Custom interest tag | 18 | e.g. `InterestExpenseNet` (custom), `InterestAndOtherFinancialCharges`, `FloorPlanInterestExpense`, `InterestExpenseNetOfAmountCapitalized` | CIKs 28917 31462 75362 85535 753308 874238 946581 1019849 1034054 1043277 1046257 1097149 1099590 1109357 1123360 1289490 1309108 1415404 |
| `InterestExpenseDebt` on the face | 17 | "Interest and debt expense" (CVX 93410 in the card, FILING-CHECKED there), "Interest expense" | CIKs 12659 46619 70145 74208 93410 104169 318154 888491 895417 896878 898173 906107 912593 1051470 1326110 1617640 1943896 |
| Interest inside a combined `NonoperatingIncomeExpense` / `OtherNonoperatingIncomeExpense` / `InterestAndOtherIncome` line | 10 | "Interest and other, net" | CIKs 47217 50863 920371 945841 1035267 1058090 1088856 1109354 1326801 1571996 |
| Insurer face (`BenefitsLossesAndExpenses` etc.) | 9 | interest often `InterestExpenseDebt` inside benefits and expenses (PGR in the card) | CIKs 59558 74260 80661 84246 876437 944695 1099219 1137774 1267238 |
| Bank face | 1 | 820027 (Ameriprise) | |

## 3. What the select step already recovers from the notes

`select.NOTE_TAGS["interest_expense_resolved"]` = `InterestExpense`, `InterestExpenseNonoperating`, `InterestExpenseOperating`, `InterestAndDebtExpense`, plus `InterestExpenseDebt` only when it is the filing's sole interest-family tag (Ritwik's 2026-11-03 sole-debt rule). For the 205 gap companies, the same latest 10-K carries a non-dimensional FY value (`qtrs=4`, `dim_id=0`, `coreg=''`, `ddate = period`) of:

| Gross tags present anywhere in that filing | Companies | Recovered by the current select? |
|---|---|---|
| none of the gross tags below | **113** | no: a real gap |
| `InterestExpenseDebt` only | 31 | yes, via the sole-debt rule, if the label check passes |
| `InterestExpenseNonoperating` | 23 | yes |
| `InterestExpense` | 16 | yes (TJX: note `InterestExpense` 79M FY2026 vs face net +121M) |
| `InterestExpenseDebt` + `InterestExpenseNonoperating` | 8 | yes, via IEN (debt is then a component) |
| `InterestCostsIncurred` only | 5 | no, and correctly so: incurred is **before** capitalised interest, so it differs from expense (CIKs 215466 823768 882184 1001838 2074176) |
| `InterestExpenseOperating` | 3 | yes |
| other combinations | 6 | mostly yes |

So about 87 of the 205 should get a note-sourced cell (marked `source=note`) and **about 118 stay blank**. Those 118 are mostly the net-only presenters with no gross figure tagged anywhere (about 75 of the 98), the no-interest-line large caps, and the custom-tag filers.

## 4. Candidates for the mapping builder (not approved; each needs a coexistence check and a Verifier draw)

1. **Custom interest-expense tags on the IS face (18 companies).** Structural signature: an IS line whose custom tag or label reads "interest expense" / "interest and debt expense" / "financing cost", which is a calc child of the pre-tax subtotal's parent (or of `NonoperatingIncomeExpense`), and the filing has no us-gaap gross interest tag at all. Before taking it, check the label for "net" and check whether an interest-income line sits next to it (the net perimeter; the card counts 388 face rows where a gross tag carries a "net" label).
2. **The 113-company remainder needs a reason, not a value**, unless the founder or the Standardization Lead rules that net interest is acceptable (it is not today: the card's verdict is "never use `InterestIncomeExpenseNet` for non-banks as interest expense"). Proposed reason text: "Company reports interest only net of interest income; gross interest expense is not tagged in the filing." Do **not** map `InterestIncomeExpenseNonoperatingNet` / `InterestRevenueExpenseNet` / non-bank `InterestIncomeExpenseNet` to this concept: same label, different perimeter, and the stored sign flips with the net direction (TJX +121M is income).
3. **GATX and Revvity** lose interest expense (and every IS line) to the statement-class trap in the README, not to a tag gap.

## 5. Banks and insurers (net interest presentation)

- Bank total interest expense = `InterestExpenseOperating` (2024+ filings) or `InterestExpense` (earlier filings and 26 banks still on it). A **period-scoped pair**, 98.6% equal where both exist (card, FILING-CHECKED: EFSC, CIVB). Components `InterestExpenseDeposits` / `InterestExpenseBorrowings` / `InterestExpenseShortTermBorrowings` / `InterestExpenseLongTermDebt` are never the total.
- `InterestIncomeExpenseNet` at a bank is **net interest income**, not interest expense, and never a substitute.
- Brokers (GS, MS, JPM, AXP) print interest expense as an `InterestExpenseOperating` line inside revenue (net revenues = total revenues − interest expense); it is the right total for this concept, but their revenue is a separate question (see [revenue.md](revenue.md)).
- Insurers: interest on debt is `InterestExpenseDebt` (PGR) inside `BenefitsLossesAndExpenses`. "Interest credited to policyholders" (`InterestCreditedToPolicyholdersAccountBalances`, 4 gap companies) is a **benefit**, not interest expense: never map it.
- BDCs: `InterestExpense` = "interest and credit facility fees" (ARCC, card), a cost line, fine for this concept.

## 6. Traps (all from rows above or the card)
- Label "net" does not identify the tag, and the tag does not identify the perimeter (card section 4).
- Stored sign: net tags are credit-signed (`InterestIncomeExpenseNet` -47,159K at ANDE prints 47,159; TJX `InterestRevenueExpenseNet` +121M is net income).
- `InterestCostsIncurred` ≠ expense (before capitalisation). `InterestPaidNet` is cash paid (CF supplemental), not expense.
- `InterestExpenseDebt` is a component wherever another interest-family tag is printed (the sole-debt rule in select).

## 7. External rule that matches this playbook (DQC_0181, effective 2024-08-31)
XBRL US DQC_0181 flags: InterestExpense/IEO as a calc descendant of `NonoperatingIncomeExpense` (should be IEN); InterestExpense/IEN under `InterestIncomeExpenseNet` (should be IEO); InterestExpense/IEN under `OperatingExpenses` (should be IEO). The same three tests can run on FSN `cal` to flag a filer whose interest tag contradicts its position (sources.md row 13).
