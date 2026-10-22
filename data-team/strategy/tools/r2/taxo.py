"""Read-only taxonomy of tagging heterogeneity on 10-K face statements, FSDS 2025q4 + 2026q1."""
import sys, os, re, collections, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
D = load(); F = D['filings']; SUB = D['sub']
def L(r): return r[6].lower()
def V(a, r, stmt): return val(D, a, r[4], r[5], stmt)
def C(r): return is_custom(D, r[4], r[5])
def close(x, y, tol=0.005): return x is not None and y is not None and abs(abs(x) - abs(y)) <= max(1.0, tol * max(abs(x), abs(y)))
def close_signed(x, y, tol=0.005): return x is not None and y is not None and abs(x - y) <= max(1.0, tol * max(abs(x), abs(y)))

COSTRE = re.compile(r'\bcosts?\b|expense|benefits|claims|losses and|provision for|depreciation|salaries|compensation|purchased')
REVRE = re.compile(r'revenue|sales|turnover|fees|income from|premiums')
REVEX = re.compile(r'expense|marketing|cost|interest')
def revenue(a, out):
    rs = rows(D, a, 'IS'); fam = family(SUB[a]['sic'])
    blk = []
    for r in rs:
        if COSTRE.search(L(r)) or r[4] in ('CostOfRevenue','CostOfGoodsAndServicesSold','CostsAndExpenses','OperatingExpenses'): break
        blk.append(r)
    if fam == 'bank': out.add('rev:bank_template_interest_and_noninterest_income'); return None
    rev = [r for r in blk if (REVRE.search(L(r)) and not REVEX.search(L(r)) and not r[4].endswith(('Expense','Fees','ProfessionalFees'))) or r[4] in ('Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','RevenuesNetOfInterestExpense')]
    if not rev:
        out.add('rev:no_revenue_line'); return None
    if any(re.search(r'excise', L(r)) for r in blk): out.add('rev:excise_gross_and_net_both_on_face')
    STD = ('Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','RevenueFromContractWithCustomerIncludingAssessedTax','RevenuesNetOfInterestExpense','RegulatedAndUnregulatedOperatingRevenue')
    tot = [r for r in rev if 'total' in L(r)]
    std = [r for r in rev if r[4] in STD and V(a, r, 'IS') is not None]
    if tot: t = tot[-1]
    elif len(rev) == 1: t = rev[0]
    elif std: t = std[-1]
    else:
        vals = [V(a, r, 'IS') for r in rev]
        if vals[-1] is not None and all(v is not None for v in vals[:-1]) and close(vals[-1], sum(vals[:-1])):
            t = rev[-1]
        elif all(v is None for v in vals) :
            out.add('rev:no_value'); return None
        else:
            out.add('rev:components_only_no_total'); t = None
    if t is not None:
        tv = V(a, t, 'IS')
        if tv is None:
            out.add('rev:total_dimension_only' if dimonly(D, a, t[4]) else 'rev:total_no_fy_value')
        if C(t): out.add('rev:total_custom_tag')
        elif t[4] == 'Revenues': out.add('rev:tag_Revenues')
        elif t[4] == 'RevenueFromContractWithCustomerExcludingAssessedTax': out.add('rev:tag_RCFC')
        else: out.add('rev:tag_other_standard:' + t[4])
        if t[4] == 'Revenues' and re.search(r'net of interest expense|and other income|other income', L(t)): out.add('rev:label_shift_broader_or_net')
        if tv is not None and tv < 0: out.add('rev:negative_total')
    # narrower/broader coexistence anywhere in the filing (undimensioned FY)
    r1 = anyval(D, a, 'Revenues'); r2 = anyval(D, a, 'RevenueFromContractWithCustomerExcludingAssessedTax')
    if r1 is not None and r2 is not None and not close(r1, r2):
        out.add('rev:RCFC_and_Revenues_differ' + ('_RCFC_smaller' if abs(r2) < abs(r1) else '_RCFC_larger'))
    # identity: revenue - cost = gross profit
    gp = anyval(D, a, 'GrossProfit')
    cor = next((x for x in (anyval(D, a, 'CostOfRevenue'), anyval(D, a, 'CostOfGoodsAndServicesSold')) if x is not None), None)
    if t is not None and V(a, t, 'IS') is not None and gp is not None and cor is not None:
        out.add('rev:id_gp_pass' if close_signed(V(a, t, 'IS') - cor, gp) else 'rev:id_gp_fail')
    return t

CORE = re.compile(r'^(total )?costs? of|cost of (revenue|sales|goods|product|service|net revenue|operation)|^cost of')
def cost(a, out):
    rs = rows(D, a, 'IS')
    cr = [r for r in rs if CORE.search(L(r)) and 'and expenses' not in L(r) and 'operating expenses' not in L(r)]
    if not cr:
        out.add('cor:no_cost_of_revenue_line'); return
    tot = [r for r in cr if 'total' in L(r)]
    if tot: t = tot[-1]
    elif len(cr) == 1: t = cr[0]
    else:
        vals = [V(a, r, 'IS') for r in cr]
        if vals[-1] is not None and all(v is not None for v in vals[:-1]) and close(vals[-1], sum(vals[:-1])): t = cr[-1]
        else: out.add('cor:components_only_no_total'); t = None
    if t is not None:
        if C(t): out.add('cor:custom_tag')
        else: out.add('cor:tag:' + t[4])
        if V(a, t, 'IS') is None and dimonly(D, a, t[4]): out.add('cor:dimension_only')
        if V(a, t, 'IS') is not None and V(a, t, 'IS') < 0: out.add('cor:negative_value_stored')
        if t[7] == '1': out.add('cor:negating_label_display')
    if any(re.search(r'exclusive of|excluding|exclude|excludes|ex\. ', L(r)) and re.search(r'depreciation|amortization', L(r)) for r in cr) or (t and 'ExcludingDepreciation' in t[4]):
        out.add('cor:excludes_D&A_by_label_or_tag')
    if any(r[4] in ('CostOfRevenue','CostOfGoodsAndServicesSold') for r in rs) and any(r[4] == 'CostsAndExpenses' for r in rs): pass

OIRE = re.compile(r'operating (income|loss|profit|earnings)|(income|loss|earnings|profit)\s*(\(loss\)\s*)?from operations|income \(loss\) from operations|(loss|income) from operation\b')
def opinc(a, out, revrow):
    rs = rows(D, a, 'IS')
    oi = [r for r in rs if OIRE.search(L(r)) and not re.search(r'before|discontinued|per share|non-?operating|other operating|tax|equity|affiliat', L(r))]
    tagged = [r for r in rs if r[4] == 'OperatingIncomeLoss']
    for r in tagged:
        if re.search(r'before (income )?tax|pre-?tax|net income|noninterest|non-interest|net loss', L(r)): out.add('oi:label_shift_OperatingIncomeLoss_is_other_line')
    if not oi and not tagged:
        out.add('oi:no_operating_income_line'); return
    t = oi[0] if oi else tagged[0]
    if C(t): out.add('oi:custom_tag')
    elif t[4] == 'OperatingIncomeLoss': out.add('oi:tag_OperatingIncomeLoss')
    else: out.add('oi:tag_other_standard:' + t[4])
    v = V(a, t, 'IS')
    # identity: revenue - total costs/expenses line = OI
    if revrow is not None and V(a, revrow, 'IS') is not None and v is not None:
        exp = [r for r in rs if r[4] in ('CostsAndExpenses', 'OperatingCostsAndExpenses', 'OperatingExpenses') or re.search(r'^total (operating )?(costs and )?(operating )?expenses', L(r))]
        gp = anyval(D, a, 'GrossProfit')
        ok = None
        for e in exp:
            ev = V(a, e, 'IS')
            if ev is None: continue
            if close_signed(V(a, revrow, 'IS') - ev, v) or (gp is not None and close_signed(gp - ev, v)): ok = True; break
            ok = False
        if ok is True: out.add('oi:id_rev_minus_total_exp_pass')
        elif ok is False: out.add('oi:id_rev_minus_total_exp_fail')
    ce = anyval(D, a, 'CostsAndExpenses'); rv = V(a, revrow, 'IS') if revrow is not None else None
    if ce is not None and rv is not None and v is not None:
        out.add('oi:CostsAndExpenses_rev_minus_equals_OI' if close_signed(rv - ce, v) else 'oi:CostsAndExpenses_rev_minus_NOT_OI')

def netinc(a, out):
    rs = rows(D, a, 'IS'); tags = {r[4]: r for r in rs}
    ni = anyval(D, a, 'NetIncomeLoss'); pl = anyval(D, a, 'ProfitLoss'); nci = anyval(D, a, 'NetIncomeLossAttributableToNoncontrollingInterest')
    if 'NetIncomeLoss' in tags and 'ProfitLoss' in tags:
        out.add('ni:both_ProfitLoss_and_NetIncomeLoss_on_face')
        if ni is not None and pl is not None and not close_signed(ni, pl): out.add('ni:NCI_nonzero_ProfitLoss_ne_NetIncomeLoss')
        if ni is not None and pl is not None and nci is not None:
            out.add('ni:id_PL_minus_NCI_eq_NI_pass' if close_signed(pl - nci, ni) else 'ni:id_PL_minus_NCI_eq_NI_fail')
    elif 'ProfitLoss' in tags: out.add('ni:ProfitLoss_only_no_NetIncomeLoss_face')
    elif 'NetIncomeLoss' in tags:
        out.add('ni:NetIncomeLoss_only')
        if 'NetIncomeLossAttributableToNoncontrollingInterest' in tags and nci not in (None, 0.0): out.add('ni:NCI_row_but_no_ProfitLoss_tag_consolidated_line_custom_or_missing')
    else:
        nr = [r for r in rs if re.search(r'^net (income|loss|earnings)|net \(loss\)|net income \(loss\)|net loss', L(r)) and 'per share' not in L(r)]
        if nr and any(C(r) for r in nr): out.add('ni:custom_bottom_line')
        elif nr: out.add('ni:other_standard_bottom_line:' + nr[-1][4])
        else: out.add('ni:no_net_income_row_found')
    if 'NetIncomeLossAvailableToCommonStockholdersBasic' in tags:
        av = anyval(D, a, 'NetIncomeLossAvailableToCommonStockholdersBasic')
        if av is not None and ni is not None and not close_signed(av, ni): out.add('ni:available_to_common_differs_from_NI')
    # cross statement
    cf = rows(D, a, 'CF')
    first = next((r for r in cf if V(a, r, 'CF') is not None), None)
    if first is not None:
        fv = V(a, first, 'CF')
        if first[4] in ('NetIncomeLoss', 'ProfitLoss') or re.search(r'net (income|loss|earnings)', L(first)):
            if first[4] == 'ProfitLoss' and 'NetIncomeLoss' in tags and ni is not None and pl is not None and not close_signed(ni, pl): out.add('ni:CF_starts_ProfitLoss_IS_shows_parent')
            if C(first): out.add('ni:CF_start_custom_tag')
            if first[4] == 'IncomeLossFromContinuingOperations' or re.search(r'continuing', L(first)): out.add('ni:CF_starts_continuing_ops')

DARE = re.compile(r'depreciation|amortization|amortisation|depletion')
DAEX = re.compile(r'debt|discount|premium|financing|issuance|right[- ]of[- ]use|\brou\b|lease|loan|contract|deferred (commission|cost|charge)|stock|share|compensation|note|bond|warrant|capitalized (commission|cost)|film|content|program|acquisition cost|deferred policy|origination|investment|securities|dac\b|unearned|prepaid|in excess')
DA1 = {'DepreciationDepletionAndAmortization','DepreciationAndAmortization','DepreciationAmortizationAndAccretionNet','DepreciationAmortizationAndOther'}
def dna(a, out):
    cf = rows(D, a, 'CF')
    op = []
    for r in cf:
        if re.search(r'net cash.*operating|operating activities', L(r)) and V(a, r, 'CF') is not None and r[4].startswith('NetCash'): break
        op.append(r)
    da = [r for r in op if DARE.search(L(r)) and not DAEX.search(L(r))]
    if not da:
        out.add('da:no_DA_line_in_CF'); return
    if len(da) == 1:
        r = da[0]
        if C(r): out.add('da:single_line_custom_tag')
        elif r[4] in DA1: out.add('da:single_line_combined_tag:' + r[4])
        else: out.add('da:single_line_other_tag:' + r[4])
    else:
        out.add('da:split_components_%d_lines' % min(len(da), 3))
        if any(C(r) for r in da): out.add('da:split_has_custom')
        if any(r[4] in DA1 for r in da): out.add('da:split_one_is_combined_tag')
    if any(re.search(r'accretion', L(r)) for r in da): out.add('da:includes_accretion_label')
    if any(re.search(r'depletion', L(r)) for r in da): out.add('da:includes_depletion_label')
    if any(re.search(r'intangible', L(r)) for r in da) or any(r[4] in ('AmortizationOfIntangibleAssets',) for r in da): out.add('da:amortization_of_intangibles_separate')
    if any(re.search(r'right[- ]of[- ]use|operating lease', L(r)) and DARE.search(L(r)) for r in op): out.add('da:ROU_amortization_line_present')
    dd = anyval(D, a, 'DepreciationDepletionAndAmortization'); d2 = anyval(D, a, 'DepreciationAndAmortization')
    if dd is not None and d2 is not None and not close(dd, d2): out.add('da:DDA_and_DA_both_filed_differ')

CAPRE = re.compile(r'\b(purchase|acquisition|addition|payment|investment|expenditure)s?\b.*(property|plant|equipment|premises|fixed assets|capital assets|pp&e|software)|capital expenditure|capitalized software|capex')
def capex(a, out):
    cf = rows(D, a, 'CF')
    i0 = next((i for i, r in enumerate(cf) if r[4].startswith('NetCashProvidedByUsedInOperatingActivities')), None)
    i1 = next((i for i, r in enumerate(cf) if r[4].startswith('NetCashProvidedByUsedInInvestingActivities')), None)
    if i0 is not None and i1 is not None and i1 > i0: cf = cf[i0 + 1:i1]
    cr = [r for r in cf if CAPRE.search(L(r)) and not r[4].startswith(('Repayment', 'CapitalExpendituresIncurred', 'Noncash', 'CapitalizedComputerSoftwareAmort', 'CapitalizedComputerSoftwareImp')) and not re.search(r'proceeds|sale|disposal|accrued|unpaid|non-?cash|included in|accounts payable|financed|supplemental|lease', L(r))]
    if not cr:
        out.add('cx:no_capex_line'); return
    if len(cr) > 1: out.add('cx:multiple_capex_lines')
    for r in cr:
        if C(r): out.add('cx:custom_tag')
        elif r[4] == 'PaymentsToAcquirePropertyPlantAndEquipment': out.add('cx:tag_PaymentsToAcquirePPE')
        else: out.add('cx:tag_other_standard:' + r[4])
        v = V(a, r, 'CF')
        if v is not None and v < 0: out.add('cx:negative_value_stored')
        if re.search(r'net of|net\b', L(r)): out.add('cx:net_of_disposals_label')
    if any(re.search(r'software', L(r)) for r in cr): out.add('cx:software_capex_line')

IXRE = re.compile(r'interest')
def interest(a, out):
    rs = rows(D, a, 'IS')
    if family(SUB[a]['sic']) == 'bank':
        tg = {r[4] for r in rs}
        out.add('ix:bank_total_interest_expense_tag:' + next((t for t in ('InterestExpenseOperating','InterestExpense','InterestExpenseDepositsAndBorrowings') if t in tg), 'other_or_components_only')); return
    ir = [r for r in rs if IXRE.search(L(r)) and not re.search(r'noninterest|non-interest|noncontrolling|non-controlling|per share|dividend income|before', L(r)) and not r[4].startswith(('NetIncomeLoss','IncomeLoss','ProfitLoss'))]
    exp = [r for r in ir if re.search(r'expense|cost|charges|paid|interest, net|net interest|interest \(income\) expense|interest and other|financ', L(r))]
    face_tags = {r[4] for r in rs}
    if not exp:
        if anyval(D, a, 'InterestExpense') is not None or anyval(D, a, 'InterestExpenseNonoperating') is not None or anyval(D, a, 'InterestExpenseDebt') is not None:
            out.add('ix:no_face_line_value_in_notes_only')
        else: out.add('ix:no_interest_expense_line')
        return
    for r in exp:
        net = re.search(r'net\b|\(income\)|income \(expense\)|expense \(income\)|and other', L(r))
        if C(r): out.add('ix:custom_tag')
        elif r[4] in ('InterestExpense','InterestExpenseNonoperating','InterestExpenseDebt','InterestExpenseOperating','InterestAndDebtExpense','InterestExpenseRelatedParty'): out.add('ix:gross_tag:' + r[4])
        elif r[4] in ('InterestIncomeExpenseNet','InterestIncomeExpenseNonoperatingNet','InterestRevenueExpenseNet','InterestIncomeExpenseOperatingNet'): out.add('ix:net_tag:' + r[4])
        else: out.add('ix:other_tag:' + r[4])
        v = V(a, r, 'IS')
        if r[4].startswith('InterestExpense') and v is not None and v < 0: out.add('ix:negative_value_on_gross_expense_tag')
        if r[4].startswith('InterestExpense') and net: out.add('ix:label_shift_gross_tag_on_net_line')
        if r[4] in ('InterestIncomeExpenseNet','InterestIncomeExpenseNonoperatingNet') and not net and 'expense' in L(r): out.add('ix:net_tag_labelled_plain_expense')
    if len(exp) > 1: out.add('ix:multiple_interest_expense_lines')

DEBTRE = re.compile(r'debt|borrowing|notes payable|note payable|commercial paper|credit facilit|line of credit|lines of credit|loans? payable|convertible notes|senior notes|\bbonds?\b|term loan|lease (liabilit|obligation)|advances from|debentures|revolving|financing obligation')
DEBTEX = re.compile(r'issuance cost|interest payable|accrued interest|receivable|investment|available.for|held.to|forgiveness|derivative|discount on|guarantee|warrant')
def debt(a, out):
    bs = rows(D, a, 'BS')
    dr = [r for r in bs if DEBTRE.search(L(r)) and not DEBTEX.search(L(r)) and not r[4].startswith(('Liabilities','Assets','StockholdersEquity'))]
    if not dr:
        out.add('dt:no_debt_line_on_BS')
        if anyval(D, a, 'LongTermDebt', '0') is not None: out.add('dt:debt_only_in_notes')
        return
    n = len(dr); out.add('dt:debt_lines_%s' % ('1' if n == 1 else '2' if n == 2 else '3-4' if n <= 4 else '5+'))
    cls = set()
    for r in dr:
        l = L(r); t = r[4]
        if 'lease' in l and re.search(r'debt|borrow|notes|loan', l): cls.add('combined_debt_and_lease')
        elif 'lease' in l and 'operating' in l: cls.add('operating_lease')
        elif 'lease' in l and re.search(r'finance|capital', l): cls.add('finance_lease')
        elif 'lease' in l: cls.add('lease_unspecified')
        elif 'commercial paper' in l: cls.add('commercial_paper' + ('_combined' if re.search(r'notes|borrow|debt', l) else ''))
        elif re.search(r'advances from|fhlb|federal home loan', l): cls.add('fhlb_advances')
        elif re.search(r'convertible', l): cls.add('convertible')
        elif re.search(r'related part', l): cls.add('related_party_debt')
        else: cls.add('borrowings')
        if C(r): out.add('dt:custom_debt_line')
    for c in cls: out.add('dt:has_' + c)
    if 'combined_debt_and_lease' in cls: pass
    for r in dr:
        if r[4].startswith('LongTermDebtAndCapitalLeaseObligations') or 'AndFinanceLease' in r[4] or 'AndCapitalLease' in r[4]:
            out.add('dt:tag_debt_plus_lease_combined' + ('_label_mentions_lease' if 'lease' in L(r) else '_label_debt_only'))
    ltd = anyval(D, a, 'LongTermDebt', '0')
    if ltd is not None and 'LongTermDebt' not in {r[4] for r in dr}: out.add('dt:LongTermDebt_total_only_in_notes')
    if ltd is not None:
        cur = anyval(D, a, 'LongTermDebtCurrent', '0'); nc = anyval(D, a, 'LongTermDebtNoncurrent', '0')
        if nc is not None:
            s = nc + (cur or 0)
            out.add('dt:id_LTD_eq_cur_plus_noncur_pass' if close_signed(s, ltd) else 'dt:id_LTD_eq_cur_plus_noncur_fail')

CASHRE = re.compile(r'^cash|cash and (cash )?equivalents|cash and due from')
def cash(a, out):
    bs = rows(D, a, 'BS')
    cr = [r for r in bs if CASHRE.search(L(r)) and not re.search(r'held in trust|trust account|segregated|collateral|pledged', L(r)) and not L(r).startswith('restricted')]
    if not cr:
        out.add('ca:no_cash_line_found'); return
    r = cr[0]; l = L(r)
    if C(r): out.add('ca:custom_tag')
    else: out.add('ca:tag:' + r[4])
    if re.search(r'restricted', l) or r[4] == 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents': out.add('ca:BS_cash_includes_restricted')
    if re.search(r'short-term investments|marketable|investments', l): out.add('ca:combined_with_investments')
    if any('restricted' in L(x) and re.search(r'cash', L(x)) for x in bs if x is not r): out.add('ca:restricted_cash_separate_BS_line')
    if r[4] == 'CashAndCashEquivalentsAtCarryingValue' and 'restricted' in l: out.add('ca:label_shift_CCE_tag_labelled_incl_restricted')
    if r[4] == 'Cash' and 'equivalent' in l: out.add('ca:label_shift_Cash_tag_labelled_cash_and_equivalents')
    if len([x for x in cr if V(a, x, 'BS') is not None]) > 1: out.add('ca:multiple_cash_lines')
    # identity: CF ending total vs BS cash (+restricted)
    end = anyval(D, a, 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', '0')
    bv = V(a, r, 'BS')
    if end is not None and bv is not None:
        if close_signed(end, bv): out.add('ca:id_CF_end_eq_BS_cash')
        else:
            rest = sum(V(a, x, 'BS') or 0 for x in bs if 'restricted' in L(x) and 'cash' in L(x) and x is not r)
            out.add('ca:id_CF_end_eq_BS_cash_plus_restricted' if rest and close_signed(end, bv + rest) else 'ca:id_CF_end_ne_BS_cash_needs_recon')

def shares(a, out):
    p = rows(D, a, 'BS', paren=True)
    so = [r for r in p if r[4] == 'CommonStockSharesOutstanding']
    if not so:
        if any(re.search(r'outstanding', L(r)) and 'shares' in L(r) for r in p if C(r)): out.add('sh:BS_outstanding_custom_tag')
        elif any(r[4] == 'CommonStockSharesIssued' for r in p): out.add('sh:BS_issued_only_no_outstanding')
        else: out.add('sh:no_BS_share_count')
    else:
        if any(V(a, r, 'BS') is not None for r in so): out.add('sh:BS_outstanding_undimensioned')
        elif dimonly(D, a, 'CommonStockSharesOutstanding', '0'): out.add('sh:BS_outstanding_dimension_only_multiclass')
        else: out.add('sh:BS_outstanding_no_current_value')
    rs = rows(D, a, 'IS'); tg = {r[4] for r in rs}
    if 'WeightedAverageNumberOfShareOutstandingBasicAndDiluted' in tg: out.add('sh:wavg_combined_BasicAndDiluted_tag')
    elif 'WeightedAverageNumberOfSharesOutstandingBasic' in tg:
        out.add('sh:wavg_basic_tag')
        if anyval(D, a, 'WeightedAverageNumberOfSharesOutstandingBasic', '4', 'shares') is None and dimonly(D, a, 'WeightedAverageNumberOfSharesOutstandingBasic'): out.add('sh:wavg_dimension_only')
    elif any(re.search(r'weighted', L(r)) for r in rs):
        out.add('sh:wavg_custom_or_other' if any(C(r) for r in rs if re.search(r'weighted', L(r))) else 'sh:wavg_other_standard')
    else: out.add('sh:no_wavg_on_IS')

def eps(a, out):
    rs = rows(D, a, 'IS'); tg = {r[4] for r in rs}
    er = [r for r in rs if re.search(r'per (common |ordinary )?share|per unit', L(r)) or 'PerShare' in r[4] or 'PerBasicShare' in r[4] or 'PerDilutedShare' in r[4] or r[4].startswith('EarningsPerShare')]
    if not er: out.add('eps:no_EPS_on_IS'); return
    if 'EarningsPerShareBasicAndDiluted' in tg: out.add('eps:combined_BasicAndDiluted_tag')
    elif 'EarningsPerShareBasic' in tg:
        out.add('eps:EarningsPerShareBasic')
        if anyval(D, a, 'EarningsPerShareBasic', '4', 'USD') is None:
            out.add('eps:basic_dimension_only_per_class' if dimonly(D, a, 'EarningsPerShareBasic') else 'eps:basic_no_fy_value')
    elif any(t.startswith('IncomeLossFromContinuingOperationsPer') for t in tg): out.add('eps:continuing_ops_EPS_only')
    elif any(C(r) for r in er): out.add('eps:custom_tag_only')
    else: out.add('eps:other:' + ','.join(sorted({r[4] for r in er}))[:60])
    if any(C(r) for r in er): out.add('eps:any_custom_EPS_line')
    if 'EarningsPerShareBasic' in tg and any(t.startswith('IncomeLossFromContinuingOperationsPer') for t in tg): out.add('eps:both_total_and_continuing_EPS')

RES = collections.defaultdict(set); FILERS_WITH = collections.Counter()
for a in F:
    out = set()
    if rows(D, a, 'IS'):
        t = revenue(a, out); cost(a, out); opinc(a, out, t); netinc(a, out); interest(a, out); eps(a, out)
    if rows(D, a, 'CF'): dna(a, out); capex(a, out)
    if rows(D, a, 'BS'): debt(a, out); cash(a, out); shares(a, out)
    for p in out: RES[p].add(a)
fams = ['bank','insurer','reit','other_fin','shell','utility','energy','pharma','other','unknown']
famN = collections.Counter(family(SUB[a]['sic']) for a in F)
size = {'1-LAF': 0, '2-ACC': 1, '4-NON': 2}
res = {}
for p in sorted(RES):
    s = RES[p]; byf = collections.Counter(family(SUB[a]['sic']) for a in s)
    ex = sorted(s, key=lambda a: (size.get(SUB[a]['afs'], 3), SUB[a]['name']))
    res[p] = dict(n=len(s), byfam={f: byf[f] for f in fams if byf[f]}, ex=[(a, SUB[a]['name'], SUB[a]['sic']) for a in ex[:6]])
json.dump(dict(N=len(F), famN=famN, res=res), open(os.path.join(OUT, 'taxo.json'), 'w'), indent=0)
for p, d in res.items():
    if d['n'] >= 3: print('%-60s %5d  %s' % (p[:60], d['n'], ' '.join('%s=%d' % kv for kv in d['byfam'].items())))
