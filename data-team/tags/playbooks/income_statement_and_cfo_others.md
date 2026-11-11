# Playbook: operating income, pre-tax income, income tax, EPS (basic, diluted), CFO

Cards: [`../cards/operating-income.md`](../cards/operating-income.md), [`../cards/net-income-and-shares.md`](../cards/net-income-and-shares.md). Method: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows). This file has the mapped counts; the gap deep-dives come next run.

| Concept | Mapped (of 632) | Tags (companies) | Known gap shape |
|---|---|---|---|
| operating_income_resolved | 466 | `OperatingIncomeLoss` (466) | ~166 without: banks, insurers, REITs, utilities and single-step income statements print no operating income. Never note-sourced (Verifier draw 2026-11-03: a non-dimensional `OperatingIncomeLoss` outside the face was segment profit at MOG-A, SHW, SWK). A "not applicable / not presented" reason, not a tag gap, for most |
| income_before_tax_resolved | 569 | `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` (501), `...MinorityInterestAndIncomeLossFromEquityMethodInvestments` (71) | the second tag is pre-tax **before** equity-method income: a different perimeter from the first when the filer has equity-method income (it sits below tax). Also seen: `IncomeLossIncludingPortionAttributableToNoncontrollingInterest` labelled "Income Before Taxes" at ITW 0000049826-26-000008 R3 l8 (a filer mis-tag; unmapped) |
| income_tax_expense_resolved | 612 | `IncomeTaxExpenseBenefit` (612) | |
| basic_eps_resolved | 611 | `EarningsPerShareBasic` (611) | `EarningsPerShareBasicAndDiluted` (one line for both) is in the diluted rule (p30) only; check basic too |
| diluted_eps_resolved | 610 | `EarningsPerShareDiluted` (610) | multi-class: per-class EPS with `StatementClassOfStockAxis`; the non-dimensional value can be missing |
| cfo_resolved | 632 | `NetCashProvidedByUsedInOperatingActivities` (616), `...ContinuingOperations` (43, rule `cf.cfo_continuing_equals_total@1`) | complete on this measure |

Traps shared by all of these:
- The statement-class trap (README §2) blanks every IS concept for GATX and Revvity.
- EPS for companies with discontinued operations: "income from continuing operations per share" (`IncomeLossFromContinuingOperationsPerBasicShare`) is a different line from total EPS.
- Pre-tax with equity-method income: `...BeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` vs `...MinorityInterestAndIncomeLossFromEquityMethodInvestments` differ by the equity-method line; the rule takes the first at p10 and the second at p20, so a filing printing both gets the first (correct).
