"""Document-first read of one company: latest 10-K R pages (+ era 10-Ks) -> tag -> SEC companyfacts.
Usage: python3 -I docmap.py <outdir> <rank> <ticker> <cik>
Writes <outdir>/<TICKER>-docmap-2026-11-12.{md,csv} and <outdir>/quirks/<TICKER>.json; prints a one-line summary JSON.
"""
import sys, os, re, json, html, csv, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import secget

DATE = '2026-11-12'
MON = {m: i for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}

# ---------------- data points: tag lists in priority order ----------------
DP = [
    ('revenue', 'IS', ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax', 'SalesRevenueNet', 'RevenuesNetOfInterestExpense', 'RegulatedAndUnregulatedOperatingRevenue', 'SalesRevenueGoodsNet', 'OperatingLeaseLeaseIncome', 'RevenueMineralSales', 'ElectricUtilityRevenue', 'RevenuesExcludingInterestAndDividends'], 'max'),
    ('cost_of_revenue', 'IS', ['CostOfRevenue', 'CostOfGoodsAndServicesSold', 'CostOfGoodsSold', 'CostOfServices', 'CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization'], 'max'),
    ('gross_profit', 'IS', ['GrossProfit'], 'first'),
    ('sga_expense', 'IS', ['SellingGeneralAndAdministrativeExpense', 'GeneralAndAdministrativeExpense'], 'first'),
    ('research_and_development', 'IS', ['ResearchAndDevelopmentExpense', 'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost'], 'first'),
    ('operating_expenses', 'IS', ['OperatingExpenses', 'CostsAndExpenses', 'OperatingCostsAndExpenses', 'BenefitsLossesAndExpenses'], 'first'),
    ('operating_income', 'IS', ['OperatingIncomeLoss'], 'first'),
    ('interest_expense', 'IS', ['InterestExpense', 'InterestExpenseNonoperating', 'InterestExpenseOperating', 'InterestAndDebtExpense', 'InterestExpenseDebt', 'InterestIncomeExpenseNonoperatingNet'], 'first'),
    ('total_interest_income', 'IS', ['InterestAndDividendIncomeOperating', 'InterestIncomeOperating', 'InterestAndFeeIncomeLoansAndLeases'], 'max'),
    ('interest_income', 'IS', ['InvestmentIncomeInterest', 'InvestmentIncomeInterestAndDividend', 'InterestIncomeOther', 'InterestIncomeOperating'], 'first'),
    ('other_income_expense_net', 'IS', ['OtherNonoperatingIncomeExpense', 'NonoperatingIncomeExpense', 'OtherNonoperatingIncome'], 'first'),
    ('net_interest_income', 'IS', ['InterestIncomeExpenseNet', 'InterestIncomeExpenseAfterProvisionForLoanLoss'], 'first'),
    ('provision_for_credit_losses', 'IS', ['ProvisionForLoanLeaseAndOtherLosses', 'ProvisionForCreditLosses', 'ProvisionForLoanLossesExpensed', 'ProvisionForLoanAndLeaseLossesAndOtherCreditLosses', 'ProvisionForLoanAndLeaseLosses', 'CreditLossExpenseReversal', 'FinancingReceivableCreditLossExpenseReversal'], 'first'),
    ('noninterest_income', 'IS', ['NoninterestIncome'], 'first'),
    ('noninterest_expense', 'IS', ['NoninterestExpense'], 'first'),
    ('premiums_earned', 'IS', ['PremiumsEarnedNet', 'PremiumsEarnedNetPropertyAndCasualty', 'PremiumsEarnedNetLife'], 'max'),
    ('net_investment_income', 'IS', ['NetInvestmentIncome', 'InvestmentIncomeNet'], 'first'),
    ('policy_benefits', 'IS', ['PolicyholderBenefitsAndClaimsIncurredNet', 'IncurredClaimsPropertyCasualtyAndLiability', 'BenefitsLossesAndExpenses'], 'first'),
    ('income_before_tax', 'IS', ['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic'], 'first'),
    ('income_tax_expense', 'IS', ['IncomeTaxExpenseBenefit', 'IncomeTaxExpenseBenefitContinuingOperations'], 'first'),
    ('net_income', 'IS', ['NetIncomeLoss', 'NetIncomeLossAvailableToCommonStockholdersBasic', 'ProfitLoss', 'IncomeLossFromContinuingOperations'], 'first'),
    ('net_income_incl_nci', 'IS', ['ProfitLoss', 'IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest'], 'first'),
    ('basic_eps', 'IS', ['EarningsPerShareBasic', 'EarningsPerShareBasicAndDiluted', 'IncomeLossFromContinuingOperationsPerBasicShare'], 'first'),
    ('diluted_eps', 'IS', ['EarningsPerShareDiluted', 'EarningsPerShareBasicAndDiluted', 'IncomeLossFromContinuingOperationsPerDilutedShare'], 'first'),
    ('weighted_basic_shares', 'IS', ['WeightedAverageNumberOfSharesOutstandingBasic', 'WeightedAverageNumberOfShareOutstandingBasicAndDiluted'], 'first'),
    ('weighted_diluted_shares', 'IS', ['WeightedAverageNumberOfDilutedSharesOutstanding', 'WeightedAverageNumberOfShareOutstandingBasicAndDiluted'], 'first'),
    ('dividends_per_share', '*', ['CommonStockDividendsPerShareDeclared', 'CommonStockDividendsPerShareCashPaid'], 'first'),
    ('comprehensive_income', 'CI', ['ComprehensiveIncomeNetOfTax', 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest'], 'first'),
    ('cash_and_equivalents', 'BS', ['CashAndCashEquivalentsAtCarryingValue', 'CashAndDueFromBanks', 'Cash', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 'CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations'], 'first'),
    ('accounts_receivable', 'BS', ['AccountsReceivableNetCurrent', 'ReceivablesNetCurrent', 'AccountsNotesAndLoansReceivableNetCurrent', 'AccountsAndOtherReceivablesNetCurrent', 'AccountsReceivableNet'], 'first'),
    ('inventory', 'BS', ['InventoryNet', 'InventoryFinishedGoodsNetOfReserves', 'InventoryGross'], 'first'),
    ('current_assets', 'BS', ['AssetsCurrent'], 'first'),
    ('ppe_net', 'BS', ['PropertyPlantAndEquipmentNet', 'PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization', 'RealEstateInvestmentPropertyNet'], 'first'),
    ('goodwill', 'BS', ['Goodwill'], 'first'),
    ('intangibles_net', 'BS', ['IntangibleAssetsNetExcludingGoodwill', 'FiniteLivedIntangibleAssetsNet', 'IntangibleAssetsNetIncludingGoodwill'], 'first'),
    ('total_assets', 'BS', ['Assets'], 'first'),
    ('accounts_payable', 'BS', ['AccountsPayableCurrent', 'AccountsPayableTradeCurrent', 'AccountsPayableCurrentAndNoncurrent'], 'first'),
    ('current_liabilities', 'BS', ['LiabilitiesCurrent'], 'first'),
    ('total_liabilities', 'BS', ['Liabilities'], 'first'),
    ('deposits', 'BS', ['Deposits'], 'first'),
    ('loans_net', 'BS', ['LoansAndLeasesReceivableNetReportedAmount', 'FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss', 'LoansAndLeasesReceivableNetOfDeferredIncome', 'NotesReceivableNet', 'FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLossNotPartOfDisposalGroup'], 'first'),
    ('stockholders_equity', 'BS', ['StockholdersEquity'], 'first'),
    ('total_equity_incl_nci', 'BS', ['StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'], 'first'),
    ('cfo', 'CF', ['NetCashProvidedByUsedInOperatingActivities', 'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations'], 'first'),
    ('cash_flow_investing', 'CF', ['NetCashProvidedByUsedInInvestingActivities', 'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations'], 'first'),
    ('cash_flow_financing', 'CF', ['NetCashProvidedByUsedInFinancingActivities', 'NetCashProvidedByUsedInFinancingActivitiesContinuingOperations'], 'first'),
    ('capex', 'CF', ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', 'PaymentsForCapitalImprovements', 'PaymentsToAcquireOilAndGasPropertyAndEquipment', 'PaymentsToAcquireRealEstate', 'PaymentsToDevelopRealEstateAssets'], 'first'),
    ('depreciation_and_amortization', 'CF', ['DepreciationDepletionAndAmortization', 'DepreciationAndAmortization', 'DepreciationAmortizationAndAccretionNet', 'DepreciationAmortizationAndOther'], 'first'),
    ('sbc', 'CF', ['ShareBasedCompensation', 'AllocatedShareBasedCompensationExpense'], 'first'),
    ('dividends_paid', 'CF', ['PaymentsOfDividendsCommonStock', 'PaymentsOfDividends', 'PaymentsOfOrdinaryDividends'], 'first'),
    ('share_buybacks', 'CF', ['PaymentsForRepurchaseOfCommonStock', 'PaymentsForRepurchaseOfEquity'], 'first'),
    ('amortization_of_intangibles', 'CF', ['AmortizationOfIntangibleAssets'], 'first'),
    ('cf_ar_change', 'CF', ['IncreaseDecreaseInAccountsReceivable', 'IncreaseDecreaseInReceivables', 'IncreaseDecreaseInAccountsAndOtherReceivables', 'IncreaseDecreaseInAccountsAndNotesReceivable'], 'first'),
    ('cf_inventory_change', 'CF', ['IncreaseDecreaseInInventories'], 'first'),
    ('cf_ap_change', 'CF', ['IncreaseDecreaseInAccountsPayable', 'IncreaseDecreaseInAccountsPayableTrade'], 'first'),
    ('shares_outstanding', 'COVER', ['EntityCommonStockSharesOutstanding'], 'sum'),
    ('cash_paid_for_interest', 'CF', ['InterestPaidNet', 'InterestPaid'], 'first'),
    ('cash_paid_for_income_taxes', 'CF', ['IncomeTaxesPaidNet', 'IncomeTaxesPaid'], 'first'),
]
DEBT = ['ShortTermBorrowings', 'CommercialPaper', 'DebtCurrent', 'LongTermDebtCurrent', 'LongTermDebtNoncurrent', 'LongTermDebt',
        'LongTermDebtAndCapitalLeaseObligations', 'LongTermDebtAndCapitalLeaseObligationsCurrent', 'NotesPayable', 'NotesPayableCurrent',
        'LongTermNotesPayable', 'SeniorNotes', 'SeniorLongTermNotes', 'LineOfCredit', 'LongTermLineOfCredit', 'OtherShortTermBorrowings',
        'AdvancesFromFederalHomeLoanBanks', 'FederalHomeLoanBankAdvances', 'SubordinatedDebt', 'JuniorSubordinatedNotes', 'SecuredDebt',
        'UnsecuredDebt', 'ConvertibleNotesPayable', 'ConvertibleNotesPayableCurrent', 'ConvertibleDebtNoncurrent', 'FinanceLeaseLiabilityCurrent',
        'FinanceLeaseLiabilityNoncurrent', 'FinanceLeaseLiability', 'OtherBorrowings', 'DebtInstrumentCarryingAmount', 'LongTermDebtFairValue',
        'SecuredOvernightFinancingRateSofrOvernightIndexSwapRateMember', 'ShortTermDebtAndCurrentPortionOfLongTermDebt',
        'DebtNoncurrent', 'OperatingLeaseLiability', 'LongTermDebtNoncurrentAndFinanceLease', 'UnsecuredLongTermDebt', 'SecuredLongTermDebt', 'ConvertibleLongTermNotesPayable', 'OtherLongTermDebtNoncurrent', 'OtherLongTermDebtCurrent', 'LongTermNotesPayableCurrent', 'NotesPayableRelatedPartiesClassifiedCurrent', 'NotesPayableRelatedPartiesNoncurrent', 'DebtLongtermAndShorttermCombinedAmount', 'LongTermDebtAndFinanceLeasesNoncurrent', 'LongTermDebtAndFinanceLeasesCurrent']
DEBT = [t for t in DEBT if t not in ('LongTermDebtFairValue', 'DebtInstrumentCarryingAmount', 'SecuredOvernightFinancingRateSofrOvernightIndexSwapRateMember', 'OperatingLeaseLiability')]
DA_PARTS = ['Depreciation', 'AmortizationOfIntangibleAssets', 'DepreciationNonproduction', 'AmortizationOfDeferredCharges', 'DepreciationAndAmortizationExcludingAmortizationOfIntangibles', 'DepletionOfOilAndGasProperties', 'AmortizationOfFinancingCosts']
COMBINED = {'AccountsPayableAndAccruedLiabilitiesCurrent': 'accounts_payable', 'AccountsPayableAndOtherAccruedLiabilitiesCurrent': 'accounts_payable',
            'IncreaseDecreaseInAccountsPayableAndAccruedLiabilities': 'cf_ap_change', 'AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent': 'accounts_payable',
            'SellingGeneralAndAdministrativeExpenseIncludingResearchAndDevelopment': 'sga_expense', 'CostOfGoodsAndServicesSoldIncludingDepreciation': 'cost_of_revenue'}

# ---------------- R page parsing ----------------
def txt(s):
    s = re.sub(r'<sup.*?</sup>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).replace('\xa0', ' ').strip()

def pdate(s):
    m = re.search(r'([A-Z][a-z]{2})\.? (\d{1,2}), (\d{4})', s)
    if not m: return None
    mo = MON.get(m.group(1).lower()[:3])
    return dt.date(int(m.group(3)), mo, int(m.group(2))) if mo else None

def pnum(s):
    s = re.sub(r'\[\d+\]', '', s).replace('$', '').replace(',', '').strip()
    if s in ('', '—', '-', '–'): return None
    neg = s.startswith('(') and s.endswith(')')
    s = s.strip('()').strip()
    try: v = float(s)
    except ValueError: return None
    return -v if neg else v

def parse_r(htmltext):
    t = htmltext[htmltext.find('<table'):]
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, flags=re.S)
    head = []
    body = []
    for r in rows:
        if '<th' in r and not body:
            head.append([(int((re.search(r'colspan="(\d+)"', c) or [0, 1])[1]), txt(c)) for c in re.findall(r'<th[^>]*>.*?</th>', r, flags=re.S)])
        else:
            body.append(r)
    title = head[0][0][1] if head else ''
    # columns
    cols = []
    if len(head) >= 2:
        groups = []
        for span, label in head[0][1:]:
            groups += [label] * span
        dates = [c[1] for c in head[1]]
        for i, d in enumerate(dates):
            g = groups[i] if i < len(groups) else ''
            mm = re.search(r'(\d+) Months Ended', g)
            cols.append(dict(months=int(mm.group(1)) if mm else 0, end=pdate(d), hdr=(g + ' ' + d).strip()))
    elif head:
        for span, label in head[0][1:]:
            for _ in range(span):
                mm = re.search(r'(\d+) Months Ended', label)
                cols.append(dict(months=int(mm.group(1)) if mm else 0, end=pdate(label), hdr=label))
    scale_money = 1e6 if '$ in Millions' in title else 1e3 if '$ in Thousands' in title else 1e9 if '$ in Billions' in title else 1
    scale_sh = 1e6 if 'shares in Millions' in title else 1e3 if 'shares in Thousands' in title else 1e9 if 'shares in Billions' in title else 1
    out = []; member = None; order = 0
    for r in body:
        tds = re.findall(r'<td[^>]*>.*?</td>', r, flags=re.S)
        if not tds: continue
        tds = tds[:1] + [c for c in tds[1:] if not re.match(r'<td class="th"', c)]   # drop footnote-marker cells
        mh = re.search(r"defref_[^']*?Axis=([A-Za-z0-9\-]+?_[A-Za-z0-9]+)'", tds[0])
        if mh or 'class="rh"' in r[:40]:
            member = mh.group(1) if mh else txt(tds[0])
            continue
        m = re.search(r"defref_([A-Za-z0-9\-]+?)_([A-Za-z0-9]+)'", tds[0])
        label = txt(tds[0])
        vals = [pnum(txt(c)) for c in tds[1:1 + len(cols)]] if cols else []
        if not m:
            continue
        prefix, tag = m.group(1), m.group(2)
        if tag.endswith('Member') or tag.endswith('Domain'):
            member = tag if not tag.endswith('Domain') else None
            continue
        if tag.endswith(('Abstract', 'Axis', 'Table', 'LineItems')): continue
        order += 1
        out.append(dict(order=order, prefix=prefix, tag=tag, label=label, vals=vals, member=member))
    return dict(title=title, cols=cols, rows=out, scale_money=scale_money, scale_sh=scale_sh)

def classify(short):
    s = short.lower()
    par = 'parenthetical' in s
    if 'comprehensive' in s and not any(k in s for k in ('operations and comprehensive', 'income and comprehensive', 'earnings and comprehensive', 'loss and comprehensive')):
        k = 'CI'
    elif any(k in s for k in ('balance sheet', 'financial condition', 'financial position', 'assets and liabilities', 'condition')):
        k = 'BS'
    elif 'cash flow' in s:
        k = 'CF'
    elif any(k in s for k in ('equity', 'stockholders', 'shareholders', 'capital', 'changes in net assets', "partners")):
        k = 'EQ'
    elif any(k in s for k in ('operations', 'income', 'earnings', 'loss')):
        k = 'IS'
    else:
        k = 'UN'
    return k + ('P' if par else '')

def statements(cik, adsh):
    base = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace("-", "")}/'
    fs = secget.get(base + 'FilingSummary.xml')
    if not fs: return None, base
    reps = []
    for m in re.finditer(r'<Report instance=.*?</Report>', fs, flags=re.S):
        x = m.group(0)
        g = lambda t: (re.search(f'<{t}>(.*?)</{t}>', x, flags=re.S) or [None, None])[1]
        if g('MenuCategory') == 'Statements' and g('HtmlFileName'):
            reps.append(dict(file=g('HtmlFileName'), short=html.unescape(g('ShortName') or ''), kind=classify(html.unescape(g('ShortName') or ''))))
    for r in reps:
        r['page'] = parse_r(secget.get(base + r['file']) or '')
    return reps, base

# ---------------- companyfacts matching ----------------
def facts_index(cf):
    idx = {}
    for tax in ('us-gaap', 'dei', 'srt', 'ifrs-full'):
        for tag, d in (cf.get('facts', {}).get(tax) or {}).items():
            for unit, lst in d.get('units', {}).items():
                for f in lst:
                    idx.setdefault((tax, tag), []).append(dict(f, unit=unit))
    return idx

def months_between(s, e):
    a = dt.date.fromisoformat(s); b = dt.date.fromisoformat(e)
    return round((b - a).days / 30.44)

def api_value(idx, prefix, tag, adsh, col):
    lst = idx.get((prefix, tag))
    if not lst or not col or not col['end']: return None
    end = col['end'].isoformat()
    cands = [f for f in lst if f['accn'] == adsh and f['end'] == end]
    if col['months']:
        cands = [f for f in cands if f.get('start') and abs(months_between(f['start'], f['end']) - col['months']) <= 1]
    else:
        cands = [f for f in cands if not f.get('start')]
    if not cands: return None
    return cands[0]['val'], cands[0]['unit']

def kind_of(tag, unit):
    if unit and '/' in unit: return 'pershare'
    if unit == 'shares': return 'shares'
    if unit: return 'money'
    t = tag.lower()
    if 'pershare' in t or 'earningspershare' in t: return 'pershare'
    if 'numberofshares' in t or t.endswith('shares') or 'sharesoutstanding' in t or 'sharesissued' in t: return 'shares'
    return 'money'

def full(v, page, kind):
    if v is None: return None
    if kind == 'money': return v * page['scale_money']
    if kind == 'shares': return v * page['scale_sh']
    return v

def match(printed, api, page, kind):
    if printed is None or api is None: return ''
    sc = page['scale_money'] if kind == 'money' else page['scale_sh'] if kind == 'shares' else 0.01
    tol = max(sc / 2.0 + 1e-6, 0.005 if kind == 'pershare' else 0.5)
    if abs(printed - api) <= tol: return 'Y'
    if abs(printed + api) <= tol: return 'Y (sign differs: printed in parentheses/negated label)'
    return 'N'

def fy_cols(page):
    cols = [(i, c) for i, c in enumerate(page['cols']) if c['end']]
    if not cols: return None, None
    dur = [x for x in cols if x[1]['months'] in (12, 13, 11, 52)] or [x for x in cols if x[1]['months'] == 0] or cols
    dur.sort(key=lambda x: x[1]['end'], reverse=True)
    seen = []
    for i, c in dur:
        if not seen or c['end'] != seen[-1][1]['end']:
            seen.append((i, c))
    return (seen[0] if seen else None), (seen[1] if len(seen) > 1 else None)

# ---------------- main read ----------------
def read_filing(cik, adsh, idx):
    reps, base = statements(cik, adsh)
    if reps is None: return None
    lines = []
    for r in reps:
        k = r['kind']; p = r['page']
        c0, c1 = fy_cols(p)
        for row in p['rows']:
            unit_probe = api_value(idx, row['prefix'], row['tag'], adsh, c0[1] if c0 else None)
            kind = kind_of(row['tag'], unit_probe[1] if unit_probe else None)
            def val(c):
                if not c or c[0] >= len(row['vals']): return None
                return full(row['vals'][c[0]], p, kind)
            f0, f1 = val(c0), val(c1)
            a0 = api_value(idx, row['prefix'], row['tag'], adsh, c0[1] if c0 else None)
            a1 = api_value(idx, row['prefix'], row['tag'], adsh, c1[1] if c1 else None)
            lines.append(dict(stmt=k, r=r['file'], short=r['short'], order=row['order'], prefix=row['prefix'], tag=row['tag'], label=row['label'],
                              member=row['member'], fy0=f0, fy1=f1, api0=a0[0] if a0 else None, api1=a1[0] if a1 else None,
                              end0=c0[1]['end'].isoformat() if c0 and c0[1]['end'] else '', end1=c1[1]['end'].isoformat() if c1 and c1[1]['end'] else '',
                              m0=match(f0, a0[0] if a0 else None, p, kind), m1=match(f1, a1[0] if a1 else None, p, kind), kind=kind,
                              custom=row['prefix'] not in ('us-gaap', 'dei', 'srt', 'ifrs-full')))
    return dict(reps=reps, lines=lines, base=base)

def pick_dps(lines):
    res = {}
    face = [l for l in lines if not l['member'] and l['stmt'] in ('IS', 'BS', 'CF', 'CI', 'EQ', 'EQP', 'BSP', 'ISP')]
    for name, st, tags, how in DP:
        c = [l for l in face if l['tag'] in tags and (st == '*' or l['stmt'] == st) and l['fy0'] is not None]
        if not c and st == 'IS':
            c = [l for l in face if l['tag'] in tags and l['stmt'] in ('CI',) and l['fy0'] is not None]
        if not c: continue
        if how == 'max':
            l = max(c, key=lambda l: abs(l['fy0']))
        else:
            l = sorted(c, key=lambda l: (tags.index(l['tag']), l['order']))[0]
        res[name] = dict(status='mapped', lines=[l])
    # debt: component sum of BS debt lines (never a total and its own parts: drop LongTermDebt if Current/Noncurrent both present)
    d = [l for l in face if l['stmt'] == 'BS' and l['tag'] in DEBT and l['fy0'] is not None]
    tags = {l['tag'] for l in d}
    if {'LongTermDebtCurrent', 'LongTermDebtNoncurrent'} <= tags: d = [l for l in d if l['tag'] != 'LongTermDebt']
    if d: res['total_debt'] = dict(status='component sum' if len(d) > 1 else 'mapped', lines=d)
    if 'depreciation_and_amortization' not in res:
        da = [l for l in face if l['stmt'] == 'CF' and l['tag'] in DA_PARTS and l['fy0'] is not None]
        if da: res['depreciation_and_amortization'] = dict(status='component sum' if len(da) > 1 else 'mapped', lines=da)
    elif res['depreciation_and_amortization']['lines'][0]['tag'] == 'DepreciationAmortizationAndOther':
        res['depreciation_and_amortization']['status'] = 'combined'
    for tag, dp in COMBINED.items():
        c = [l for l in face if l['tag'] == tag and l['fy0'] is not None]
        if c and dp not in res: res[dp] = dict(status='combined', lines=c[:1])
    # custom-tag lines whose label names a data point we have not mapped
    lab = {'depreciation_and_amortization': r'depreciation', 'capex': r'(capital expenditure|purchases? of property|additions to property)',
           'revenue': r'^(total )?(net )?(revenues?|sales|net sales)( net)?$', 'operating_income': r'^(total )?operating (income|profit|earnings)',
           'interest_expense': r'^interest expense', 'net_income': r'^net (income|earnings)( \(loss\))?$', 'sbc': r'(stock|share)[- ]based compensation',
           'dividends_paid': r'dividends paid', 'share_buybacks': r'(repurchase|purchase)s? of (common )?(stock|shares)'}
    for dp, rx in lab.items():
        if dp in res: continue
        c = [l for l in face if l['custom'] and re.search(rx, l['label'], flags=re.I) and l['fy0'] is not None]
        if c: res[dp] = dict(status='custom tag', lines=c[:1])
    return res

def era_scan(idx, res, fy0_end):
    """For each mapped dp, years in the last 5 FYs where its latest tag has no 10-K FY value but a sibling does."""
    out = {}
    for name, st, tags, how in DP:
        if name not in res or res[name]['status'] != 'mapped': continue
        t0 = res[name]['lines'][0]['tag']
        if t0 not in tags: continue
        def fys(tag):
            ys = {}
            for f in idx.get(('us-gaap', tag), []):
                if f.get('form', '').startswith('10-K') and f.get('fp') == 'FY' and f.get('start') and 11 <= months_between(f['start'], f['end']) <= 13:
                    ys.setdefault(f['end'][:4], f['accn'])
            return ys
        y0 = fys(t0)
        last5 = [str(int(fy0_end[:4]) - k) for k in range(0, 6)]
        for sib in tags:
            if sib == t0: continue
            ys = fys(sib)
            gap = [y for y in last5 if y in ys and y not in y0]
            if gap:
                out.setdefault(name, []).append((sib, sorted(gap), ys[max(gap)]))
    return out

def fmt(v):
    if v is None: return ''
    return ('%.2f' % v).rstrip('0').rstrip('.') if abs(v) < 1000 and v != int(v) else str(int(round(v)))

def run(outdir, rank, ticker, cik):
    os.makedirs(os.path.join(outdir, 'quirks'), exist_ok=True)
    cikp = '%010d' % int(cik)
    sub = secget.getjson(f'https://data.sec.gov/submissions/CIK{cikp}.json')
    r = sub['filings']['recent']
    tenk = [dict(adsh=r['accessionNumber'][i], filed=r['filingDate'][i], period=r['reportDate'][i], form=r['form'][i])
            for i, f in enumerate(r['form']) if f in ('10-K', '10-KT')]
    quirks = []
    summary = dict(rank=rank, ticker=ticker, cik=cik, name=sub.get('name'), sic=sub.get('sic'), fye=sub.get('fiscalYearEnd'))
    if not tenk:
        forms = sorted(set(r['form'][:200]))
        summary.update(status='no_10K', forms=forms[:12])
        write_md(outdir, ticker, summary, None, {}, {}, [], [], quirks)
        return summary
    latest = tenk[0]
    cf = secget.getjson(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cikp}.json') or {}
    idx = facts_index(cf)
    rd = read_filing(cik, latest['adsh'], idx)
    if rd is None:
        summary.update(status='no_filing_summary', latest=latest['adsh'])
        write_md(outdir, ticker, summary, latest, {}, {}, [], [], quirks)
        return summary
    res = pick_dps(rd['lines'])
    fy0_end = next((l['end0'] for l in rd['lines'] if l['stmt'] == 'IS' and l['end0']), latest['period'])
    eras = era_scan(idx, res, fy0_end)
    era_reads = []
    for acc in sorted({e[2] for v in eras.values() for e in v})[-2:]:
        if acc == latest['adsh']: continue
        er = read_filing(cik, acc, idx)
        if er: era_reads.append((acc, er))
    # quirks
    for name, d in res.items():
        for l in d['lines']:
            for m, f, a, end in ((l['m0'], l['fy0'], l['api0'], l['end0']), (l['m1'], l['fy1'], l['api1'], l['end1'])):
                if m == 'N':
                    quirks.append(dict(kind='printed_vs_api', dp=name, tag=l['tag'], label=l['label'], printed=fmt(f), api=fmt(a), end=end, r=l['r'], adsh=latest['adsh'],
                                       note=f'printed {fmt(f)} vs companyfacts {fmt(a)}: the filing wins'))
        if d['status'] in ('combined', 'custom tag'):
            l = d['lines'][0]
            quirks.append(dict(kind=d['status'].replace(' ', '_'), dp=name, tag=f"{l['prefix']}:{l['tag']}", label=l['label'], printed=fmt(l['fy0']), api=fmt(l['api0']), end=l['end0'], r=l['r'], adsh=latest['adsh'],
                               note=('custom extension tag on a data-point line (not in companyfacts)' if d['status'] == 'custom tag' else 'combined line, never the pure concept')))
    for name, lst in eras.items():
        for sib, years, acc in lst:
            quirks.append(dict(kind='era_change', dp=name, tag=f"{sib} -> {res[name]['lines'][0]['tag']}", label=res[name]['lines'][0]['label'], printed='', api='', end=','.join(years), r='', adsh=acc,
                               note=f'companyfacts: {sib} carries FY {",".join(years)}; latest 10-K uses {res[name]["lines"][0]["tag"]}'))
    if 'diluted_eps' in res and res['diluted_eps']['lines'][0]['tag'].startswith('IncomeLossFromContinuing'):
        l = res['diluted_eps']['lines'][0]
        quirks.append(dict(kind='eps_contops_tag', dp='diluted_eps', tag=l['tag'], label=l['label'], printed=fmt(l['fy0']), api=fmt(l['api0']), end=l['end0'], r=l['r'], adsh=latest['adsh'], note='diluted EPS printed only under the continuing-operations tag'))
    if 'net_income' in res and res['net_income']['lines'][0]['tag'] != 'NetIncomeLoss':
        l = res['net_income']['lines'][0]
        quirks.append(dict(kind='net_income_tag', dp='net_income', tag=l['tag'], label=l['label'], printed=fmt(l['fy0']), api=fmt(l['api0']), end=l['end0'], r=l['r'], adsh=latest['adsh'], note='no NetIncomeLoss line on the IS face'))
    for l in rd['lines']:
        if not l['member'] and not l['custom'] and l['stmt'] in ('IS', 'BS', 'CF') and l['tag'] == 'CommercialPaper' and 'short' in l['label'].lower():
            quirks.append(dict(kind='label_tag', dp='total_debt', tag='CommercialPaper', label=l['label'], printed=fmt(l['fy0']), api=fmt(l['api0']), end=l['end0'], r=l['r'], adsh=latest['adsh'], note='CommercialPaper labelled as short-term debt'))
    nface = [l for l in rd['lines'] if l['stmt'] in ('IS', 'BS', 'CF', 'CI') and l['fy0'] is not None]
    summary.update(status='read', latest=latest['adsh'], fy0_end=fy0_end, statements=len(rd['reps']), face_lines=len(nface),
                   face_custom=sum(1 for l in nface if l['custom']), face_dimensional=sum(1 for l in nface if l['member']),
                   face_api_Y=sum(1 for l in nface if l['m0'].startswith('Y')), face_api_N=sum(1 for l in nface if l['m0'] == 'N'),
                   face_api_none=sum(1 for l in nface if not l['m0']),
                   dps_mapped=len(res), dp_mismatch=sum(1 for q in quirks if q['kind'] == 'printed_vs_api'), era_10k=len(era_reads), quirks=len(quirks),
                   requests=secget.COUNT[0])
    write_md(outdir, ticker, summary, latest, rd, res, eras, era_reads, quirks)
    write_csv(outdir, ticker, rd, res, eras, era_reads, latest)
    json.dump(quirks, open(os.path.join(outdir, 'quirks', ticker + '.json'), 'w'), indent=0)
    return summary

def write_csv(outdir, ticker, rd, res, eras, era_reads, latest):
    fn = os.path.join(outdir, f'{ticker}-docmap-{DATE}.csv')
    w = csv.writer(open(fn, 'w', newline=''))
    w.writerow(['ticker', 'data_point', 'status', 'tags', 'stmt', 'r_page', 'label', 'fy0_printed', 'fy0_api', 'fy1_printed', 'fy1_api', 'match', 'era_from_note', 'evidence_class', 'note'])
    dpof = {}
    for name, d in res.items():
        for l in d['lines']: dpof.setdefault(id(l), name)
        ls = d['lines']
        tg = '+'.join(f"{l['prefix']}:{l['tag']}" for l in ls)
        s0 = sum(l['fy0'] or 0 for l in ls) if all(l['fy0'] is not None for l in ls) else None
        s1 = sum(l['fy1'] or 0 for l in ls) if all(l['fy1'] is not None for l in ls) else None
        a0 = sum(l['api0'] for l in ls) if all(l['api0'] is not None for l in ls) else None
        a1 = sum(l['api1'] for l in ls) if all(l['api1'] is not None for l in ls) else None
        mm = 'Y' if all(l['m0'].startswith('Y') and (not l['fy1'] or l['m1'].startswith('Y')) for l in ls) else ('N' if any('N' == l['m0'] or 'N' == l['m1'] for l in ls) else 'no API fact')
        if all('sign' in l['m0'] for l in ls): mm = 'Y (sign differs: printed in parentheses/negated label)'
        era = '; '.join(f"{s} for FY {','.join(y)} ({a})" for s, y, a in eras.get(name, []))
        note = ' + '.join(f"'{l['label']}'" for l in ls) if len(ls) > 1 else ''
        w.writerow([ticker, name, d['status'], tg, ls[0]['stmt'], '+'.join(sorted({l['r'] for l in ls})), ' + '.join(l['label'] for l in ls)[:200],
                    fmt(s0), fmt(a0), fmt(s1), fmt(a1), mm, era or 'no tag change in last 5 FY (companyfacts)', 'FILING-CHECKED',
                    (note + ' | ' if note else '') + f"accn {latest['adsh']} FY0 end {ls[0]['end0']}"])
    for name, st, tags, how in DP:
        if name not in res and name in ('gross_profit', 'operating_income', 'total_liabilities', 'current_assets', 'current_liabilities', 'interest_expense', 'cost_of_revenue', 'inventory', 'accounts_receivable', 'accounts_payable'):
            w.writerow([ticker, name, 'not_presented', '', st, '', '', '', '', '', '', '', '', 'FILING-CHECKED', f'no face line with a {name} tag in the latest 10-K statements (labels read: see face lines below)'])
    for l in rd['lines']:
        w.writerow([ticker, dpof.get(id(l), ''), 'face_line' + (' (member: ' + l['member'] + ')' if l['member'] else ''), f"{l['prefix']}:{l['tag']}", l['stmt'], l['r'], l['label'][:200],
                    fmt(l['fy0']), fmt(l['api0']), fmt(l['fy1']), fmt(l['api1']), l['m0'] or ('custom: no companyfacts' if l['custom'] else 'no API fact'), '', 'FILING-CHECKED', f"{l['short']} | FY0 end {l['end0']}"])
    for acc, er in era_reads:
        for l in er['lines']:
            if l['member'] or l['stmt'] not in ('IS', 'BS', 'CF'): continue
            w.writerow([ticker, 'era:' + dpname(l['tag']), 'era_face_line', f"{l['prefix']}:{l['tag']}", l['stmt'], l['r'], l['label'][:200],
                        fmt(l['fy0']), fmt(l['api0']), fmt(l['fy1']), fmt(l['api1']), l['m0'] or 'no API fact', acc, 'FILING-CHECKED', f"era 10-K {acc} | FY0 end {l['end0']}"])

def dpname(tag):
    for name, st, tags, how in DP:
        if tag in tags: return name
    return ''

def write_md(outdir, ticker, s, latest, rd, res, eras, era_reads, quirks):
    fn = os.path.join(outdir, f'{ticker}-docmap-{DATE}.md')
    L = [f"# {ticker} document-first map {DATE} (rank {s['rank']}, read-only)", '',
         'Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references; API = SEC companyfacts, undimensioned, same accession, same period). DATA-INFERRED rows say so.', '',
         f"Company: {s.get('name')} (CIK {int(s['cik']):010d}), SIC {s.get('sic')}, fiscal year end {s.get('fye')}.", '']
    if s.get('status') != 'read':
        L += [f"**Status: {s.get('status')}.** " + ('No 10-K in the EDGAR submissions list (recent forms: ' + ', '.join(s.get('forms', [])) + ').' if s.get('status') == 'no_10K' else f"FilingSummary.xml missing for {s.get('latest')}."), '']
        open(fn, 'w').write('\n'.join(L) + '\n'); return
    L += ['## Filings opened', f"- Latest 10-K {latest['adsh']} (filed {latest['filed']}, period {latest['period']}): " + ', '.join(f"{r['file']} {r['short']} [{r['kind']}]" for r in rd['reps']) + '.',
          f"- Base: {rd['base']}", '- companyfacts (one call).']
    for acc, er in era_reads:
        L.append(f"- Era 10-K {acc}: " + ', '.join(f"{r['file']} {r['short']}" for r in er['reps']) + '.')
    L += ['', 'FY0 = the latest fiscal year column; FY1 = the prior year. Values in full USD (printed value × the R-page scale); EPS per share; shares in shares.', '',
          '## Data points', '| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match |', '|---|---|---|---|---|---|---|---|---|---|']
    for name, d in res.items():
        ls = d['lines']
        s0 = sum(l['fy0'] or 0 for l in ls) if all(l['fy0'] is not None for l in ls) else None
        s1 = sum(l['fy1'] or 0 for l in ls) if all(l['fy1'] is not None for l in ls) else None
        a0 = sum(l['api0'] for l in ls) if all(l['api0'] is not None for l in ls) else None
        a1 = sum(l['api1'] for l in ls) if all(l['api1'] is not None for l in ls) else None
        m = ', '.join(sorted({l['m0'] or ('custom: no companyfacts' if l['custom'] else 'no API fact') for l in ls}))
        L.append(f"| {name} | {d['status']} | {'+'.join(l['tag'] for l in ls)} | {ls[0]['stmt']} {'+'.join(sorted({l['r'] for l in ls}))} | {' + '.join(l['label'] for l in ls)[:90]} | {fmt(s0)} | {fmt(a0)} | {fmt(s1)} | {fmt(a1)} | {m} |")
    missing = [n for n in ('revenue', 'gross_profit', 'operating_income', 'net_income', 'diluted_eps', 'total_assets', 'total_liabilities', 'stockholders_equity', 'cfo', 'capex', 'total_debt', 'depreciation_and_amortization') if n not in res]
    L += ['', '## Not presented on the face (headline data points)', ', '.join(missing) if missing else 'none', '']
    L += ['## Era checks (tag changes in the last ~5 fiscal years, from companyfacts; era 10-K read where one was found)']
    if eras:
        for n, lst in eras.items():
            for sib, y, a in lst: L.append(f"- {n}: {sib} for FY {', '.join(y)} (10-K {a}); latest uses {res[n]['lines'][0]['tag']}.")
    else:
        L.append('- none flagged')
    L += ['', '## Quirks and mismatches (the filing decides)']
    L += [f"- [{q['kind']}] {q['dp']}: {q['tag']} '{q['label'][:80]}' {q['note']} ({q['adsh']} {q['r']} {q['end']})" for q in quirks] or ['- none']
    nface = [l for l in rd['lines'] if l['stmt'] in ('IS', 'BS', 'CF', 'CI') and l['fy0'] is not None]
    L += ['', '## Face-line totals', f"{len(nface)} face lines with an FY0 value (IS/BS/CF/CI): {sum(1 for l in nface if l['m0'].startswith('Y'))} equal companyfacts, {sum(1 for l in nface if l['m0']=='N')} differ, {sum(1 for l in nface if not l['m0'])} have no companyfacts fact ({sum(1 for l in nface if l['custom'])} custom-tag lines, {sum(1 for l in nface if l['member'])} dimensional member lines). Every face line is in the CSV.", '']
    open(fn, 'w').write('\n'.join(L) + '\n')

if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])))
