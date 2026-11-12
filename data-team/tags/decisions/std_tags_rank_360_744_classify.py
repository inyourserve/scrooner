import csv, re, sys
rows=[x for x in csv.DictReader(open('prio.csv')) if 360<=int(x['rank'])<=744]
# hand decisions: tag -> (decision, concept, reason)
H={
'CommonStockDividendsPerShareCashPaid':('map','dividends_per_share','DPS paid; already a library tag (C6: DPS held until the share-basis guard)'),
'CashAndDueFromBanks':('map','cash_and_equivalents','bank template cash line (seen C, AXP, COF)'),
'PaymentsOfOrdinaryDividends':('map','dividends_paid','common dividends; already a library tag'),
'InterestAndDebtExpense':('map','interest_expense','already a library tag'),
'Cash':('map','cash_and_equivalents','already a library tag'),
'IncomeLossAttributableToParent':('map','income_before_tax',"std label 'Income (Loss) Attributable to Parent, before Tax'; FSN plabel 'income before income taxes' at MRVL, COP, TMUS; lower priority than the two std pretax tags"),
'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost':('map','research_and_development','R&D face line excluding acquired IPR&D'),
'AllocatedShareBasedCompensationExpense':('map','sbc','share-based compensation (CF add-back or IS line)'),
'AccountsReceivableNet':('map','accounts_receivable','receivables net (no current/noncurrent split)'),
'AccountsPayableTradeCurrent':('map','accounts_payable','trade payables when no AccountsPayableCurrent line'),
'NetCashProvidedByUsedInFinancingActivitiesContinuingOperations':('map','cash_flow_financing','only where no total financing line is printed'),
'InterestExpenseDebt':('map','interest_expense',"when it is the only face interest line (WELL, PGR); with an affiliates line beside it (TMUS) it is a component"),
'OtherDepreciationAndAmortization':('map','depreciation_and_amortization',"when it is the CF's only D&A line (MRVL, QCOM, WELL)"),
'PaymentsToAcquireOtherProductiveAssets':('map','capex',"VZ 'capital expenditures (including capitalized software)'; per company"),
'PaymentsForRepurchaseOfEquity':('review','share_buybacks','may include preferred or other equity: per company'),
'OperatingCostsAndExpenses':('review','operating_expenses','total costs and expenses: includes cost of revenue at some filers; per company'),
'IntangibleAssetsNetIncludingGoodwill':('combined','goodwill','goodwill and intangibles on one line'),
'AccountsAndOtherReceivablesNetCurrent':('combined','accounts_receivable','trade plus other receivables'),
'AccountsNotesAndLoansReceivableNetCurrent':('combined','accounts_receivable','accounts plus notes receivable'),
'AccountsPayableAndOtherAccruedLiabilitiesCurrent':('combined','accounts_payable','payables plus accrued liabilities'),
'IncreaseDecreaseInOtherAccountsPayableAndAccruedLiabilities':('exclude','','other payables change; not cf_ap_change'),
'IncreaseDecreaseInAccountsPayableAndOtherOperatingLiabilities':('combined','cf_ap_change','AP change combined with other liabilities'),
'IncreaseDecreaseInAccountsAndNotesReceivable':('combined','cf_ar_change','AR change combined with notes'),
'DepreciationNonproduction':('component','depreciation_and_amortization','depreciation only; D&A = depreciation + amortization lines (BKNG)'),
'PaymentsToAcquireOtherPropertyPlantAndEquipment':('component','capex','a capex line beside the main PP&E line'),
'PaymentsToDevelopSoftware':('component','capex','capitalized software is capex (founder 2026-11-04 item 3)'),
'PaymentsForSoftware':('component','capex','capitalized software is capex (founder 2026-11-04 item 3)'),
'PaymentsForCapitalImprovements':('review','capex','REIT capital improvements: REIT capex definition (founder TI ruling)'),
'PaymentsToDevelopRealEstateAssets':('review','capex','REIT development spend: capex for REITs?'),
'PaymentsToAcquireRealEstate':('exclude','','property acquisitions are acquisitions, not capex'),
'PaymentsForProceedsFromProductiveAssets':('combined','capex','capex net of disposal proceeds'),
'CapitalLeaseObligationsIncurred':('exclude','','non-cash finance lease additions'),
'InterestExpenseLongTermDebt':('component','interest_expense','one interest line of several'),
'InterestExpenseShortTermBorrowings':('component','interest_expense','one interest line of several'),
'InterestExpenseOther':('component','interest_expense','one interest line of several'),
'InterestExpenseDeposits':('component','interest_expense','bank deposit interest (bank template)'),
'CurrentIncomeTaxExpenseBenefit':('component','income_tax_expense','current part; total = current + deferred'),
'InterestPaidCapitalized':('exclude','','capitalized interest (supplemental)'),
'CommercialPaper':('component','total_debt','face debt line (CommercialPaper must be included: MSFT P-4)'),
'LineOfCredit':('component','total_debt','face debt line'),'LinesOfCreditCurrent':('component','total_debt','face debt line'),'LongTermLineOfCredit':('component','total_debt','face debt line'),
'SecuredDebt':('component','total_debt','face debt line'),'UnsecuredDebt':('component','total_debt','face debt line'),
'ConvertibleDebtNoncurrent':('component','total_debt','face debt line'),'ConvertibleDebtCurrent':('component','total_debt','face debt line'),'ConvertibleLongTermNotesPayable':('component','total_debt','face debt line'),
'OtherShortTermBorrowings':('component','total_debt','face debt line'),'OtherBorrowings':('component','total_debt','face debt line'),
'FinanceLeaseLiabilityCurrent':('component','total_debt','finance leases are debt (founder 2026-11-04 item 5)'),
'SecuritiesSoldUnderAgreementsToRepurchase':('exclude','','bank funding; not corporate debt (bank template)'),
'OperatingLeaseLiability':('exclude','','operating leases are excluded from total debt'),
'NetIncomeLossAvailableToCommonStockholdersDiluted':('exclude','','diluted EPS numerator'),
'IncomeLossIncludingPortionAttributableToNoncontrollingInterest':('exclude','','net income including NCI (net_income is attributable to parent)'),
'AssetsNoncurrent':('exclude','','subtotal not in template'),
'LiabilitiesOfDisposalGroupIncludingDiscontinuedOperation':('exclude','','held-for-sale block'),
'AssetsOfDisposalGroupIncludingDiscontinuedOperation':('exclude','','held-for-sale block'),
'NoninterestIncome':('component','revenue','bank revenue component (bank template: revenue = NII + noninterest income)'),
'InterestAndFeeIncomeLoansAndLeases':('component','revenue','bank interest income component'),
'PremiumsEarnedNet':('component','revenue','insurer revenue component'),
'NetInvestmentIncome':('component','revenue','insurer revenue component'),
'InterestIncomeExpenseAfterProvisionForLoanLoss':('exclude','','bank subtotal after provisions'),
'BenefitsLossesAndExpenses':('exclude','','insurer total benefits and expenses'),
'InterestIncomeOperating':('map','interest_income','interest income line'),
'InvestmentIncomeInterestAndDividend':('combined','interest_income','interest and dividend income'),
'InterestIncomeOther':('component','interest_income','other interest income'),
'InvestmentIncomeNet':('combined','interest_income','investment income incl. gains (label often says interest income: FTNT)'),
'InterestAndOtherIncome':('combined','interest_income','interest and other income'),
'OtherInterestAndDividendIncome':('component','interest_income','component'),
'InterestIncomeSecuritiesTaxable':('component','interest_income','bank component'),
'CommonStocksIncludingAdditionalPaidInCapital':('exclude','','equity component'),
'AccumulatedDistributionsInExcessOfNetIncome':('exclude','','REIT equity component'),
'DeferredRevenueNoncurrent':('exclude','','not a template data point'),
'RealEstateInvestmentPropertyNet':('review','ppe_net','REIT property net: PP&E for REITs?'),
'PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetBeforeAccumulatedDepreciationAndAmortization':('exclude','','gross PP&E incl. ROU'),
'OtherIntangibleAssetsNet':('exclude','','intangibles, not goodwill'),
'MarketingAndAdvertisingExpense':('component','sga_expense','opex line'),
'ProfessionalFees':('component','operating_expenses','opex line'),
'PreferredStockDividendsAndOtherAdjustments':('exclude','','preferred dividends'),
'DividendsPreferredStock':('exclude','','preferred dividends'),
'PaymentsForRepurchaseOfPreferredStockAndPreferenceStock':('exclude','','not common stock (founder buyback ruling)'),
'PaymentsForRepurchaseOfRedeemablePreferredStock':('exclude','','not common stock'),
'ProceedsFromSaleOfTreasuryStock':('exclude','','issuance, not repurchase'),
'RestrictedCashAndCashEquivalentsNoncurrent':('exclude','','restricted cash is not cash and equivalents'),
'CommunicationsAndInformationTechnology':('component','operating_expenses','bank opex line'),
'InformationTechnologyAndDataProcessing':('component','operating_expenses','bank opex line'),
'AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivities':('exclude','','subtotal of CF adjustments'),
'CapitalizedContractCostNetNoncurrent':('exclude','','BS component'),
'IncomeTaxPaidFederalAfterRefundReceived':('exclude','','supplemental cash paid'),
'BusinessCombinationConsiderationTransferredEquityInterestsIssuedAndIssuable':('exclude','','non-cash acquisition consideration'),
'ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff':('exclude','','acquired IPR&D write-off (not R&D expense)'),
'PaymentOfFinancingAndStockIssuanceCosts':('exclude','','financing costs'),
'PaidInKindInterest':('exclude','','non-cash PIK interest (CF add-back)'),
'OperatingLeaseLeaseIncome':('component','revenue','REIT rental revenue (often the top revenue line)'),
'DirectCostsOfLeasedAndRentedPropertyOrEquipment':('component','cost_of_revenue','lessor direct costs'),
'OtherNonoperatingIncome':('component','other_income_expense_net','component'),
'OtherNonoperatingExpense':('component','other_income_expense_net','component'),
'DividendsPayableCurrentAndNoncurrent':('exclude','','dividends payable (BS), not dividends paid'),
}
def auto(tag, st):
    if re.search(r'(Abstract|Axis|Domain|Member)$', tag): return ('exclude','','structural element (abstract/axis/member), never a value')
    if re.search(r'^IncreaseDecrease', tag): return ('exclude','','working-capital change line other than AR/AP/inventory (not a template data point)')
    if re.search(r'OtherComprehensiveIncome|ComprehensiveIncome', tag): return ('exclude','','comprehensive income statement line')
    if re.search(r'NoncontrollingInterest|NoncontrollingEntity|MinorityShareholders', tag): return ('exclude','','noncontrolling-interest line')
    if re.search(r'DiscontinuedOperation|DisposalGroup', tag): return ('exclude','','discontinued operations / disposal group line')
    if re.search(r'^Noncash|Noncash|NonCash|Incurred(But)?|Assumed1|AcquisitionValue|FairValueOfAssetsAcquired|ConversionOfStock', tag): return ('exclude','','non-cash supplemental disclosure')
    if re.search(r'^(Proceeds|Repayments|Payments)', tag) and st.startswith('CF'): return ('exclude','','cash-flow line that is not a template data point')
    if re.search(r'^TemporaryEquity|^PreferredStock|Preferred', tag): return ('exclude','','preferred / temporary equity')
    if re.search(r'(Impairment|Restructuring|Litigation|GainLoss|Gains?Losses)', tag): return ('exclude','','gain/loss or special item: not a template data point')
    if re.search(r'Derivative|Hedge', tag): return ('exclude','','derivative line')
    if re.search(r'Pension|Postretirement|DefinedBenefit', tag): return ('exclude','','pension line')
    if re.search(r'Policy|Premium|Claims|Reinsurance|Unearned', tag): return ('exclude','','insurer balance or flow (insurer template components)')
    if re.search(r'Deposit|Loans?(Receivable|AndLeases)|FinancingReceivable|HeldForSale|ProvisionFor', tag): return ('exclude','','bank balance or flow (bank template components)')
    if re.search(r'Regulatory', tag): return ('exclude','','regulatory asset/liability (utility)')
    if re.search(r'Securities|Investments?$|Investment(s)?[A-Z]|EquitySecurities|MarketableSecurities', tag): return ('exclude','','investment holdings line')
    if re.search(r'Lease', tag): return ('exclude','','lease line (operating leases are not debt)')
    if re.search(r'Receivable|Prepaid|Inventory|Land$|Gross$|Machinery|Buildings|ConstructionInProgress|Accumulated', tag): return ('exclude','','balance-sheet component line, not a template data point')
    if re.search(r'Liabilit|Payable|Accrued|Obligation|Contingent', tag): return ('exclude','','liability component line, not a template data point')
    if re.search(r'^CommonStock|SharesIssued|SharesOutstanding|SharesAuthorized|ParValue', tag): return ('exclude','','share capital line / share counts on BS')
    if re.search(r'PerShare', tag): return ('exclude','','per-share line other than EPS/DPS')
    if re.search(r'Expense|Costs|Fees|Charges|Amortization|Taxes', tag) and 'IS' in st: return ('exclude','','operating expense line, not a template data point')
    if re.search(r'Income|Revenue', tag) and 'IS' in st: return ('exclude','','income line, not a template data point')
    if re.search(r'CashCashEquivalents|^Cash', tag): return ('exclude','','cash-flow reconciliation / restricted-cash line')
    return None
out=[]; un=[]
for x in rows:
    t,st=x['tag'],x['statements']
    d=H.get(t) or auto(t,st)
    if d is None: un.append((x['rank'],t,st)); continue
    out.append([x['rank'],'us-gaap:'+t,st,d[0],d[1],d[2]])
print('unclassified',len(un)); print(un)
csv.writer(open('ranks360_744.csv','w')).writerows([['rank','tag','statements','decision','concept','reason']]+out)
