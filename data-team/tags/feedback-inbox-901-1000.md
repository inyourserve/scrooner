# Tag feedback inbox: ranks 901-1000 document-first reads (2026-11-12)

One row per new tag quirk found by data-team/companies/reads/tools/docmap.py (status | ticker | data point | tag | finding | accession R page | evidence). For the Tag Expert to process (data-team/19-TAG-EXPERT.md learning loop).

| status | ticker | data point | tag | finding | where | evidence |
|---|---|---|---|---|---|---|
| new | SWX | operating_expenses | us-gaap:CostsAndExpenses | face line 'Total operating expenses' carries a us-gaap tag outside the usual operating_expenses set | 0001692115-26-000062 R5.htm | FILING-CHECKED |
| new | SWX | interest_expense | us-gaap:InterestIncomeExpenseNonoperatingNet | face line 'Net interest deductions' carries a us-gaap tag outside the usual interest_expense set | 0001692115-26-000062 R5.htm | FILING-CHECKED |
| new | SWX | inventory | us-gaap:MaterialsSuppliesAndOther | face line 'Materials, supplies & gas inventories' carries a us-gaap tag outside the usual inventory set | 0001692115-26-000062 R3.htm | FILING-CHECKED |
| new | SWX | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | not on the face; reported in a note/other page R91.htm 'Income Taxes - Schedule of Income Taxes Paid (Details)' | 0001692115-26-000062 | FILING-CHECKED (MetaLinks) |
| new | SWX | interest_expense | us-gaap:InterestExpense -> us-gaap:InterestIncomeExpenseNonoperatingNet | tag eras from FY2015: InterestExpense FY 2015-12..2022-12; InterestIncomeExpenseNonoperatingNet FY 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | accounts_receivable | us-gaap:AccountsReceivableNetCurrent | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | inventory | us-gaap:MaterialsSuppliesAndOther | era coverage gap: annual facts reach only 2020-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | current_assets | us-gaap:AssetsCurrent | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | ppe_net | us-gaap:PublicUtilitiesPropertyPlantAndEquipmentNet | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | goodwill | us-gaap:Goodwill | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | accounts_payable | us-gaap:AccountsPayableCurrent | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | current_liabilities | us-gaap:LiabilitiesCurrent | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | stockholders_equity | us-gaap:StockholdersEquity | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | cfo | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations -> us-gaap:NetCashProvidedByUsedInOperatingActivities | tag eras from FY2015: NetCashProvidedByUsedInOperatingActivitiesContinuingOperations FY 2015-12..2015-12; NetCashProvidedByUsedInOperatingActivities FY 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | cash_flow_investing | us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations -> us-gaap:NetCashProvidedByUsedInInvestingActivities | tag eras from FY2015: NetCashProvidedByUsedInInvestingActivitiesContinuingOperations FY 2015-12..2015-12; NetCashProvidedByUsedInInvestingActivities FY 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | SWX | cash_flow_financing | us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations -> us-gaap:NetCashProvidedByUsedInFinancingActivities | tag eras from FY2015: NetCashProvidedByUsedInFinancingActivitiesContinuingOperations FY 2015-12..2015-12; NetCashProvidedByUsedInFinancingActivities FY 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | operating_expenses | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:AssetImpairmentCharges+amrx:IntellectualPropertyLegalDevelopmentExpenses+us-gaap:RestructuringCharges+us-gaap:GainLossRelatedToLitigationSettlement+us-gaap:OtherOperatingIncomeExpenseNet | face line 'Selling, general and administrative + Research and development + In-process rese' carries a us-gaap tag outside the usual operating_expenses set | 0001723128-26-000011 R3.htm | FILING-CHECKED |
| new | AMRX | operating_expenses | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:AssetImpairmentCharges+amrx:IntellectualPropertyLegalDevelopmentExpenses+us-gaap:RestructuringCharges+us-gaap:GainLossRelatedToLitigationSettlement+us-gaap:OtherOperatingIncomeExpenseNet | printed face value has no companyfacts fact for the same accession/period | 0001723128-26-000011 R3.htm | FILING-CHECKED |
| new | AMRX | interest_expense | us-gaap:InterestIncomeExpenseNonoperatingNet | face line 'Interest expense, net' carries a us-gaap tag outside the usual interest_expense set | 0001723128-26-000011 R3.htm | FILING-CHECKED |
| new | AMRX | accounts_receivable | us-gaap:AccountsReceivableNetCurrent | printed face value has no companyfacts fact for the same accession/period | 0001723128-26-000011 R6.htm | FILING-CHECKED |
| new | AMRX | accounts_payable | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | printed face value has no companyfacts fact for the same accession/period | 0001723128-26-000011 R6.htm | FILING-CHECKED |
| new | AMRX | depreciation_and_amortization | amrx:DepreciationDepletionAndAmortizationExcludingAmortizationOfDebtIssuanceCosts | face line 'Depreciation and amortization' on a company extension tag, not us-gaap | 0001723128-26-000011 R10.htm | FILING-CHECKED |
| new | AMRX | depreciation_and_amortization | amrx:DepreciationDepletionAndAmortizationExcludingAmortizationOfDebtIssuanceCosts | printed face value has no companyfacts fact for the same accession/period | 0001723128-26-000011 R10.htm | FILING-CHECKED |
| new | AMRX | shares_outstanding | us-gaap:CommonStockSharesOutstanding | not on the face; reported in a note/other page R8.htm 'Consolidated Statement of Changes in Stockholders’ Equity (D' | 0001723128-26-000011 | FILING-CHECKED (MetaLinks) |
| new | AMRX | revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | cost_of_revenue | us-gaap:CostOfGoodsAndServicesSold | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | gross_profit | us-gaap:GrossProfit | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | operating_expenses | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExp | era coverage gap: annual facts reach only none..none | companyfacts | DATA-INFERRED |
| new | AMRX | sga_expense | us-gaap:SellingGeneralAndAdministrativeExpense | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | research_and_development | us-gaap:ResearchAndDevelopmentExpense | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | operating_income | us-gaap:OperatingIncomeLoss | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | interest_expense | us-gaap:InterestIncomeExpenseNonoperatingNet | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | income_before_tax | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNon | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | income_tax_expense | us-gaap:IncomeTaxExpenseBenefit | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | net_income | us-gaap:NetIncomeLoss | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | basic_eps | us-gaap:EarningsPerShareBasic | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | diluted_eps | us-gaap:EarningsPerShareDiluted | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | weighted_basic_shares | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | weighted_diluted_shares | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | cash_and_equivalents | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents -> us-gaap:CashAndCashEquivalentsAtCarryingValue | tag eras from FY2015: CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents FY 2015-12..2015-12; CashAndCashEquivalentsAtCarryingValue FY 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | accounts_receivable | us-gaap:AccountsReceivableNetCurrent | era coverage gap: annual facts reach only 2017-12..2022-12 | companyfacts | DATA-INFERRED |
| new | AMRX | inventory | us-gaap:InventoryNet | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | current_assets | us-gaap:AssetsCurrent | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | ppe_net | us-gaap:PropertyPlantAndEquipmentNet | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | goodwill | us-gaap:Goodwill | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | total_assets | us-gaap:Assets | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | accounts_payable | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | era coverage gap: annual facts reach only 2017-12..2022-12 | companyfacts | DATA-INFERRED |
| new | AMRX | current_liabilities | us-gaap:LiabilitiesCurrent | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | stockholders_equity | us-gaap:StockholdersEquity | era coverage gap: annual facts reach only 2017-10..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | cfo | us-gaap:NetCashProvidedByUsedInOperatingActivities | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | cash_flow_investing | us-gaap:NetCashProvidedByUsedInInvestingActivities | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | cash_flow_financing | us-gaap:NetCashProvidedByUsedInFinancingActivities | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | capex | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | depreciation_and_amortization | amrx:DepreciationDepletionAndAmortizationExcludingAmortizationOfDebtIssuanceCost | era coverage gap: annual facts reach only none..none | companyfacts | DATA-INFERRED |
| new | AMRX | sbc | us-gaap:ShareBasedCompensation | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | cash_paid_for_interest | us-gaap:InterestPaidNet | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | AMRX | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | EPAM | accounts_receivable | epam:TradeReceivablesAndContractAssetsAfterAllowanceForCreditLossCurrent | face line 'Trade receivables and contract assets, net of allowance of $6,350 and $5,612, re' on a company extension tag, not us-gaap | 0001352010-26-000015 R3.htm | FILING-CHECKED |
| new | EPAM | accounts_receivable | epam:TradeReceivablesAndContractAssetsAfterAllowanceForCreditLossCurrent | printed face value has no companyfacts fact for the same accession/period | 0001352010-26-000015 R3.htm | FILING-CHECKED |
| new | EPAM | depreciation_and_amortization | us-gaap:OtherDepreciationAndAmortization | face line 'Depreciation and amortization expense' carries a us-gaap tag outside the usual depreciation_and_amortization set | 0001352010-26-000015 R8.htm | FILING-CHECKED |
| new | EPAM | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | not on the face; reported in a note/other page R99.htm 'INCOME TAXES (Narrative) (Details)' | 0001352010-26-000015 | FILING-CHECKED (MetaLinks) |
| new | EPAM | revenue | us-gaap:Revenues -> us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | tag eras from FY2015: Revenues FY 2015-12..2015-12; RevenueFromContractWithCustomerExcludingAssessedTax FY 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | EPAM | income_before_tax | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic -> us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | tag eras from FY2015: IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic FY 2015-12..2018-12; IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest FY 2019-12..2025-12 | companyfacts | DATA-INFERRED |
| new | EPAM | accounts_receivable | epam:TradeReceivablesAndContractAssetsAfterAllowanceForCreditLossCurrent | era coverage gap: annual facts reach only 2015-12..2018-12 | companyfacts | DATA-INFERRED |
| new | EPAM | depreciation_and_amortization | us-gaap:DepreciationAndAmortization -> us-gaap:OtherDepreciationAndAmortization | tag eras from FY2015: DepreciationAndAmortization FY 2015-12..2017-12; OtherDepreciationAndAmortization FY 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | EPAM | share_buybacks | us-gaap:PaymentsForRepurchaseOfCommonStock | era coverage gap: annual facts reach only 2021-12..2025-12 | companyfacts | DATA-INFERRED |
| new | EPAM | cash_paid_for_interest | us-gaap:InterestPaid -> us-gaap:InterestPaidNet | tag eras from FY2015: InterestPaid FY 2015-12..2016-12; InterestPaidNet FY 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | EPAM | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaid -> us-gaap:IncomeTaxesPaidNet | tag eras from FY2015: IncomeTaxesPaid FY 2015-12..2016-12; IncomeTaxesPaidNet FY 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | operating_expenses | us-gaap:CostsAndExpenses | face line 'Total costs and expenses' carries a us-gaap tag outside the usual operating_expenses set | 0001628280-26-006960 R5.htm | FILING-CHECKED |
| new | LYFT | capex | lyft:PaymentsToAcquirePropertyAndEquipmentAndScooterFleet | face line 'Purchases of property and equipment and scooter fleet' on a company extension tag, not us-gaap | 0001628280-26-006960 R8.htm | FILING-CHECKED |
| new | LYFT | capex | lyft:PaymentsToAcquirePropertyAndEquipmentAndScooterFleet | printed face value has no companyfacts fact for the same accession/period | 0001628280-26-006960 R8.htm | FILING-CHECKED |
| new | LYFT | revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax -> us-gaap:Revenues | tag eras from FY2015: RevenueFromContractWithCustomerExcludingAssessedTax FY 2017-12..2017-12; Revenues FY 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | revenue | us-gaap:Revenues | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | cost_of_revenue | us-gaap:CostOfRevenue | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | operating_expenses | us-gaap:CostsAndExpenses | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | sga_expense | us-gaap:GeneralAndAdministrativeExpense | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | research_and_development | us-gaap:ResearchAndDevelopmentExpense | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | operating_income | us-gaap:OperatingIncomeLoss | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | interest_expense | us-gaap:InterestExpense -> us-gaap:InterestExpenseNonoperating | tag eras from FY2015: InterestExpense FY 2018-12..2021-12; InterestExpenseNonoperating FY 2022-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | interest_expense | us-gaap:InterestExpenseNonoperating | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | income_before_tax | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNon | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | income_tax_expense | us-gaap:IncomeTaxExpenseBenefit | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | net_income | us-gaap:NetIncomeLoss | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | basic_eps | us-gaap:EarningsPerShareBasicAndDiluted -> us-gaap:EarningsPerShareBasic | tag eras from FY2015: EarningsPerShareBasicAndDiluted FY 2017-12..2018-12; EarningsPerShareBasic FY 2019-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | basic_eps | us-gaap:EarningsPerShareBasic | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | diluted_eps | us-gaap:EarningsPerShareBasicAndDiluted -> us-gaap:EarningsPerShareDiluted | tag eras from FY2015: EarningsPerShareBasicAndDiluted FY 2017-12..2018-12; EarningsPerShareDiluted FY 2019-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | diluted_eps | us-gaap:EarningsPerShareDiluted | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | weighted_basic_shares | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | era coverage gap: annual facts reach only 2019-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | weighted_diluted_shares | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | era coverage gap: annual facts reach only 2019-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | cash_and_equivalents | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents -> us-gaap:CashAndCashEquivalentsAtCarryingValue | tag eras from FY2015: CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents FY 2016-12..2016-12; CashAndCashEquivalentsAtCarryingValue FY 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | cash_and_equivalents | us-gaap:CashAndCashEquivalentsAtCarryingValue | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | current_assets | us-gaap:AssetsCurrent | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | ppe_net | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedD | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | goodwill | us-gaap:Goodwill | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | total_assets | us-gaap:Assets | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | accounts_payable | us-gaap:AccountsPayableCurrent | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | current_liabilities | us-gaap:LiabilitiesCurrent | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | total_liabilities | us-gaap:Liabilities | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | stockholders_equity | us-gaap:StockholdersEquity | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | cfo | us-gaap:NetCashProvidedByUsedInOperatingActivities | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | cash_flow_investing | us-gaap:NetCashProvidedByUsedInInvestingActivities | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | cash_flow_financing | us-gaap:NetCashProvidedByUsedInFinancingActivities | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | capex | lyft:PaymentsToAcquirePropertyAndEquipmentAndScooterFleet | era coverage gap: annual facts reach only none..none | companyfacts | DATA-INFERRED |
| new | LYFT | depreciation_and_amortization | us-gaap:DepreciationDepletionAndAmortization | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | sbc | us-gaap:ShareBasedCompensation | era coverage gap: annual facts reach only 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | share_buybacks | us-gaap:PaymentsForRepurchaseOfCommonStock | era coverage gap: annual facts reach only 2022-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | cash_paid_for_interest | us-gaap:InterestPaidNet | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LYFT | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | era coverage gap: annual facts reach only 2018-12..2025-12 | companyfacts | DATA-INFERRED |
| new | POOL | operating_expenses | us-gaap:SellingGeneralAndAdministrativeExpense | face line 'Selling and administrative expenses' carries a us-gaap tag outside the usual operating_expenses set | 0001193125-26-074833 R2.htm | FILING-CHECKED |
| new | POOL | cash_paid_for_interest | us-gaap:InterestPaidNet | not on the face; reported in a note/other page R48.htm 'Organization and Summary of Significant Accounting Policies ' | 0001193125-26-074833 | FILING-CHECKED (MetaLinks) |
| new | POOL | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | not on the face; reported in a note/other page R48.htm 'Organization and Summary of Significant Accounting Policies ' | 0001193125-26-074833 | FILING-CHECKED (MetaLinks) |
| new | POOL | revenue | us-gaap:SalesRevenueNet -> us-gaap:Revenues | tag eras from FY2015: SalesRevenueNet FY 2015-12..2015-12; Revenues FY 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | POOL | cash_and_equivalents | us-gaap:CashAndCashEquivalentsAtCarryingValue -> us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | tag eras from FY2015: CashAndCashEquivalentsAtCarryingValue FY 2015-12..2015-12; CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents FY 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | POOL | cash_paid_for_interest | us-gaap:InterestPaid -> us-gaap:InterestPaidNet | tag eras from FY2015: InterestPaid FY 2015-12..2016-12; InterestPaidNet FY 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | sga_expense | lb:GeneralAndAdministrativeExpensesIncome | face line 'General and administrative expense (income)' on a company extension tag, not us-gaap | 0001193125-26-072404 R4.htm | FILING-CHECKED |
| new | LB | sga_expense | lb:GeneralAndAdministrativeExpensesIncome | printed face value has no companyfacts fact for the same accession/period | 0001193125-26-072404 R4.htm | FILING-CHECKED |
| new | LB | interest_expense | us-gaap:InterestIncomeExpenseNet | face line 'Interest expense, net' carries a us-gaap tag outside the usual interest_expense set | 0001193125-26-072404 R4.htm | FILING-CHECKED |
| new | LB | accounts_receivable | us-gaap:AccountsReceivableNetCurrent | printed face value has no companyfacts fact for the same accession/period | 0001193125-26-072404 R2.htm | FILING-CHECKED |
| new | LB | accounts_payable | us-gaap:AccountsPayableCurrent | printed face value has no companyfacts fact for the same accession/period | 0001193125-26-072404 R2.htm | FILING-CHECKED |
| new | LB | cash_paid_for_interest | us-gaap:InterestPaidNet | not on the face; reported in a note/other page R44.htm 'Additional Financial Statement Information - Schedule of Sup' | 0001193125-26-072404 | FILING-CHECKED (MetaLinks) |
| new | LB | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | not on the face; reported in a note/other page R44.htm 'Additional Financial Statement Information - Schedule of Sup' | 0001193125-26-072404 | FILING-CHECKED (MetaLinks) |
| new | LB | revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | sga_expense | lb:GeneralAndAdministrativeExpensesIncome | era coverage gap: annual facts reach only none..none | companyfacts | DATA-INFERRED |
| new | LB | operating_income | us-gaap:OperatingIncomeLoss | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | interest_expense | us-gaap:InterestIncomeExpenseNet | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | income_before_tax | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNon | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | income_tax_expense | us-gaap:IncomeTaxExpenseBenefit | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | net_income | us-gaap:ProfitLoss -> us-gaap:NetIncomeLoss | tag eras from FY2015: ProfitLoss FY 2023-12..2023-12; NetIncomeLoss FY 2024-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | net_income | us-gaap:NetIncomeLoss | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | basic_eps | us-gaap:EarningsPerShareBasic | era coverage gap: annual facts reach only 2024-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | diluted_eps | us-gaap:EarningsPerShareDiluted | era coverage gap: annual facts reach only 2024-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | weighted_basic_shares | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | era coverage gap: annual facts reach only 2024-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | weighted_diluted_shares | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | era coverage gap: annual facts reach only 2024-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | cash_and_equivalents | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents -> us-gaap:CashAndCashEquivalentsAtCarryingValue | tag eras from FY2015: CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents FY 2022-12..2022-12; CashAndCashEquivalentsAtCarryingValue FY 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | cash_and_equivalents | us-gaap:CashAndCashEquivalentsAtCarryingValue | era coverage gap: annual facts reach only 2022-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | accounts_receivable | us-gaap:AccountsReceivableNetCurrent | era coverage gap: annual facts reach only none..none | companyfacts | DATA-INFERRED |
| new | LB | current_assets | us-gaap:AssetsCurrent | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | ppe_net | us-gaap:PropertyPlantAndEquipmentNet | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | total_assets | us-gaap:Assets | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | accounts_payable | us-gaap:AccountsPayableCurrent | era coverage gap: annual facts reach only none..none | companyfacts | DATA-INFERRED |
| new | LB | current_liabilities | us-gaap:LiabilitiesCurrent | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | total_liabilities | us-gaap:Liabilities | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | stockholders_equity | us-gaap:StockholdersEquity | era coverage gap: annual facts reach only 2024-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | cfo | us-gaap:NetCashProvidedByUsedInOperatingActivities | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | cash_flow_investing | us-gaap:NetCashProvidedByUsedInInvestingActivities | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | cash_flow_financing | us-gaap:NetCashProvidedByUsedInFinancingActivities | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | capex | us-gaap:PaymentsToAcquireProductiveAssets | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | depreciation_and_amortization | us-gaap:DepreciationDepletionAndAmortization | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | sbc | us-gaap:ShareBasedCompensation | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | dividends_paid | us-gaap:PaymentsOfDividends | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | cash_paid_for_interest | us-gaap:InterestPaidNet | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | LB | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | era coverage gap: annual facts reach only 2023-12..2025-12 | companyfacts | DATA-INFERRED |
| new | RIG | operating_expenses | us-gaap:CostsAndExpenses | face line 'Total costs and expenses' carries a us-gaap tag outside the usual operating_expenses set | 0001451505-26-000018 R2.htm | FILING-CHECKED |
| new | RIG | interest_expense | us-gaap:InterestExpenseNonoperating | face line 'Interest expense, net of amounts capitalized' carries a us-gaap tag outside the usual interest_expense set | 0001451505-26-000018 R2.htm | FILING-CHECKED |
| new | RIG | cash_paid_for_interest | us-gaap:InterestPaidNet | not on the face; reported in a note/other page R94.htm 'Supplemental Cash Flow Information (Details)' | 0001451505-26-000018 | FILING-CHECKED (MetaLinks) |
| new | RIG | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | not on the face; reported in a note/other page R80.htm 'Income Taxes (Income Taxes Paid, Net) (Details)' | 0001451505-26-000018 | FILING-CHECKED (MetaLinks) |
| new | RIG | revenue | us-gaap:Revenues -> us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | tag eras from FY2015: Revenues FY 2015-12..2015-12; RevenueFromContractWithCustomerExcludingAssessedTax FY 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | RIG | cost_of_revenue | us-gaap:CostOfGoodsAndServicesSold | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
| new | RIG | interest_expense | us-gaap:InterestExpense -> us-gaap:InterestExpenseNonoperating | tag eras from FY2015: InterestExpense FY 2015-12..2021-12; InterestExpenseNonoperating FY 2022-12..2025-12 | companyfacts | DATA-INFERRED |
| new | RIG | accounts_receivable | us-gaap:ReceivablesNetCurrent -> us-gaap:AccountsReceivableNetCurrent -> us-gaap:ReceivablesNetCurrent | tag eras from FY2015: ReceivablesNetCurrent FY 2015-12..2015-12; AccountsReceivableNetCurrent FY 2016-12..2016-12; ReceivablesNetCurrent FY 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | RIG | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaid -> us-gaap:IncomeTaxesPaidNet | tag eras from FY2015: IncomeTaxesPaid FY 2015-12..2024-12; IncomeTaxesPaidNet FY 2025-12..2025-12 | companyfacts | DATA-INFERRED |
| new | M | interest_expense | us-gaap:InterestIncomeExpenseNonoperatingNet | face line 'Interest expense, net' carries a us-gaap tag outside the usual interest_expense set | 0001628280-26-021721 R3.htm | FILING-CHECKED |
| new | M | weighted_basic_shares | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | not on the face; reported in a note/other page R93.htm 'Earnings Per Share - Computation Of Basic and Diluted Earnin' | 0001628280-26-021721 | FILING-CHECKED (MetaLinks) |
| new | M | weighted_diluted_shares | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | not on the face; reported in a note/other page R93.htm 'Earnings Per Share - Computation Of Basic and Diluted Earnin' | 0001628280-26-021721 | FILING-CHECKED (MetaLinks) |
| new | M | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaidNet | not on the face; reported in a note/other page R75.htm 'Taxes - Cash paid for income taxes, net of refunds received ' | 0001628280-26-021721 | FILING-CHECKED (MetaLinks) |
| new | M | revenue | us-gaap:SalesRevenueNet -> us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax -> us-gaap:Revenues | tag eras from FY2015: SalesRevenueNet FY 2015-01..2016-01; RevenueFromContractWithCustomerExcludingAssessedTax FY 2017-01..2021-01; Revenues FY 2022-01..2026-01 | companyfacts | DATA-INFERRED |
| new | M | interest_expense | us-gaap:InterestExpense -> us-gaap:InterestIncomeExpenseNonoperatingNet | tag eras from FY2015: InterestExpense FY 2015-01..2021-01; InterestIncomeExpenseNonoperatingNet FY 2022-01..2026-01 | companyfacts | DATA-INFERRED |
| new | M | income_before_tax | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments -> us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | tag eras from FY2015: IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments FY 2015-01..2018-02; IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest FY 2019-02..2026-01 | companyfacts | DATA-INFERRED |
| new | M | inventory | us-gaap:InventoryNet | era coverage gap: annual facts reach only 2017-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | operating_expenses | us-gaap:OperatingExpenses | face line 'Total operating expenses' carries a us-gaap tag outside the usual operating_expenses set | 0001628280-26-023250 R5.htm | FILING-CHECKED |
| new | NAVN | revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | cost_of_revenue | us-gaap:CostOfRevenue | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | gross_profit | us-gaap:GrossProfit | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | operating_expenses | us-gaap:OperatingExpenses | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | sga_expense | us-gaap:GeneralAndAdministrativeExpense | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | research_and_development | us-gaap:ResearchAndDevelopmentExpense | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | operating_income | us-gaap:OperatingIncomeLoss | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | interest_expense | us-gaap:InterestExpenseNonoperating | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | income_before_tax | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNon | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | income_tax_expense | us-gaap:IncomeTaxExpenseBenefit | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | net_income | us-gaap:NetIncomeLoss | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | basic_eps | us-gaap:EarningsPerShareBasic | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | diluted_eps | us-gaap:EarningsPerShareDiluted | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | weighted_basic_shares | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | weighted_diluted_shares | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | cash_and_equivalents | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents -> us-gaap:CashAndCashEquivalentsAtCarryingValue | tag eras from FY2015: CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents FY 2023-01..2023-01; CashAndCashEquivalentsAtCarryingValue FY 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | cash_and_equivalents | us-gaap:CashAndCashEquivalentsAtCarryingValue | era coverage gap: annual facts reach only 2023-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | accounts_receivable | us-gaap:AccountsReceivableNetCurrent | era coverage gap: annual facts reach only 2025-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | current_assets | us-gaap:AssetsCurrent | era coverage gap: annual facts reach only 2025-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | ppe_net | us-gaap:PropertyPlantAndEquipmentNet | era coverage gap: annual facts reach only 2025-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | goodwill | us-gaap:Goodwill | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | total_assets | us-gaap:Assets | era coverage gap: annual facts reach only 2025-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | accounts_payable | us-gaap:AccountsPayableCurrent | era coverage gap: annual facts reach only 2025-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | current_liabilities | us-gaap:LiabilitiesCurrent | era coverage gap: annual facts reach only 2025-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | total_liabilities | us-gaap:Liabilities | era coverage gap: annual facts reach only 2025-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | stockholders_equity | us-gaap:StockholdersEquity | era coverage gap: annual facts reach only 2023-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | cfo | us-gaap:NetCashProvidedByUsedInOperatingActivities | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | cash_flow_investing | us-gaap:NetCashProvidedByUsedInInvestingActivities | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | cash_flow_financing | us-gaap:NetCashProvidedByUsedInFinancingActivities | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | capex | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | depreciation_and_amortization | us-gaap:DepreciationDepletionAndAmortization | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | sbc | us-gaap:ShareBasedCompensation | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | cash_paid_for_interest | us-gaap:InterestPaidNet | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | NAVN | cash_paid_for_income_taxes | us-gaap:IncomeTaxesPaid | era coverage gap: annual facts reach only 2024-01..2026-01 | companyfacts | DATA-INFERRED |
| new | QLYS | operating_expenses | us-gaap:OperatingExpenses | face line 'Total operating expenses' carries a us-gaap tag outside the usual operating_expenses set | 0001107843-26-000008 R5.htm | FILING-CHECKED |
| new | QLYS | revenue | us-gaap:Revenues -> us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | tag eras from FY2015: Revenues FY 2015-12..2016-12; RevenueFromContractWithCustomerExcludingAssessedTax FY 2017-12..2025-12 | companyfacts | DATA-INFERRED |
| new | QLYS | income_before_tax | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic -> us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | tag eras from FY2015: IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic FY 2015-12..2018-12; IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest FY 2019-12..2025-12 | companyfacts | DATA-INFERRED |
| new | QLYS | share_buybacks | us-gaap:PaymentsForRepurchaseOfCommonStock | era coverage gap: annual facts reach only 2016-12..2025-12 | companyfacts | DATA-INFERRED |
