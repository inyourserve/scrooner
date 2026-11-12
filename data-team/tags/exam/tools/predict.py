"""Tag Expert blind-exam predictor (deterministic).
Inputs: face lines of a company's latest 10-K from the FSN store (one JSON object per line: cik, acc, per, st, r, ln, pth,
neg, tag, cu, cr, lab, val, dc, q, prior) + data-team/tags/library/standard-tag-library.csv + company-overrides.csv.
Output: one prediction per data point, in the docmap's vocabulary.
Usage: predict.py LINES.jsonl TICKER RANK LIBRARY_DIR > TICKER-prediction.csv
"""
import csv, json, re, sys
DPS = ['accounts_payable','accounts_receivable','amortization_of_intangibles','basic_eps','capex','cash_and_equivalents','cash_flow_financing',
 'cash_flow_investing','cash_paid_for_income_taxes','cash_paid_for_interest','cf_ap_change','cf_ar_change','cf_inventory_change','cfo',
 'comprehensive_income','cost_of_revenue','current_assets','current_liabilities','deposits','depreciation_and_amortization','diluted_eps',
 'dividends_paid','dividends_per_share','goodwill','gross_profit','income_before_tax','income_tax_expense','interest_expense','interest_income',
 'inventory','loans_net','net_income','net_interest_income','noninterest_expense','noninterest_income','operating_expenses','operating_income',
 'other_income_expense_net','ppe_net','provision_for_credit_losses','research_and_development','revenue','sbc','sga_expense','share_buybacks',
 'shares_outstanding','stockholders_equity','total_assets','total_debt','total_interest_income','total_liabilities','weighted_basic_shares',
 'weighted_diluted_shares']
def dp_of(concept):
    c = (concept or '').strip()
    c = {'revenue_sanity_resolved':'revenue'}.get(c, c)
    return c[:-9] if c.endswith('_resolved') else c
# bank data points read from their standard tags (sector template)
BANK = {'deposits':['Deposits'],'loans_net':['LoansAndLeasesReceivableNetReportedAmount','LoansAndLeasesReceivableNetOfDeferredIncome','FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss'],
 'net_interest_income':['InterestIncomeExpenseNet'],'noninterest_income':['NoninterestIncome'],'noninterest_expense':['NoninterestExpense'],
 'provision_for_credit_losses':['ProvisionForLoanLeaseAndOtherLosses','ProvisionForLoanAndLeaseLosses','ProvisionForCreditLossesNet','ProvisionForLoanLossesExpensed'],
 'total_interest_income':['InterestAndDividendIncomeOperating']}
# note-sourced data points: default tag when no face line exists
NOTE = {'cash_paid_for_income_taxes':'IncomeTaxesPaidNet','cash_paid_for_interest':'InterestPaidNet','amortization_of_intangibles':'AmortizationOfIntangibleAssets',
 'interest_income':'InvestmentIncomeInterest','weighted_basic_shares':'WeightedAverageNumberOfSharesOutstandingBasic','weighted_diluted_shares':'WeightedAverageNumberOfDilutedSharesOutstanding',
 'dividends_per_share':'CommonStockDividendsPerShareDeclared','sbc':'ShareBasedCompensation'}
DURATION_SUM = {'cost_of_revenue','operating_expenses','sga_expense','interest_expense','capex','depreciation_and_amortization','research_and_development','revenue','income_tax_expense','total_debt'}
DEMOTE = {
 'interest_expense': r'(?i)(,\s*net\b|net of interest income|and other|interest and other)(?!.*capitaliz)',
 'revenue': r'(?i)and other income',
 'depreciation_and_amortization': r'(?i)impair|accretion|nuclear|and other|gain|loss',
 'share_buybacks': r'(?i)excise|withh|warrant|units|and other|preferred',
 'dividends_paid': r'(?i)preferred|equivalent|units|and other',
 'capex': r'(?i)acquisitions? of (?:business|compan|restaurant)|businesses|and investments|net of (?:proceeds|disposals)',
 'accounts_receivable': r'(?i)and other|notes|other receivable',
 'accounts_payable': r'(?i)accrued|and other',
 'cash_and_equivalents': r'(?i)restricted',
 'goodwill': r'(?i)intangible',
 'other_income_expense_net': r'(?i)interest',
 'cf_ap_change': r'(?i)\band\b|other', 'cf_ar_change': r'(?i)\band\b|other', 'cf_inventory_change': r'(?i)\band\b|other',
}
STMT = {'BS':{'accounts_payable','accounts_receivable','cash_and_equivalents','current_assets','current_liabilities','goodwill','inventory','ppe_net',
 'shares_outstanding','stockholders_equity','total_assets','total_debt','total_liabilities','deposits','loans_net'},
 'CF':{'capex','cash_flow_financing','cash_flow_investing','cfo','cf_ap_change','cf_ar_change','cf_inventory_change','depreciation_and_amortization','dividends_paid','sbc','share_buybacks','cash_paid_for_interest','cash_paid_for_income_taxes'}}
def home(dp):
    for s,v in STMT.items():
        if dp in v: return s
    return 'IS'
def load_lib(d):
    lib = {}
    for r in csv.DictReader(open(f'{d}/standard-tag-library.csv')):
        lib[(r['stmt'], r['tag'])] = r
    import os
    nd = {}
    p = f'{d}/needs-detail-answers-r1r2.csv'
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            nd.setdefault(r['tag'], dp_of(r['concept']))
    ov = {}
    for r in csv.DictReader(open(f'{d}/company-overrides.csv')):
        ov[(r['cik'], r['tag'])] = r
    return lib, ov, nd
def sign(v):
    try: x = float(v)
    except (TypeError, ValueError): return ''
    return '+' if x > 0 else '-' if x < 0 else '0'
def main(lines_path, ticker, rank, libdir):
    lib, ov, nd = load_lib(libdir)
    L = [json.loads(l) for l in open(lines_path) if l.strip()]
    L = [l for l in L if not l.get('missing')]
    for l in L:
        for k in ('pth', 'cu', 'neg', 'r', 'ln'):
            try: l[k] = int(l.get(k) or 0)
            except (TypeError, ValueError): l[k] = 0
        if l.get('val') == '': l['val'] = None
    cik = L[0]['cik'] if L else ''
    tags = {l['tag'] for l in L}
    bank = 'Deposits' in tags and bool(tags & {'InterestAndDividendIncomeOperating','InterestExpenseDeposits','NoninterestIncome','LoansAndLeasesReceivableNetReportedAmount'})
    insurer = bool(tags & {'PremiumsEarnedNet','LiabilityForFuturePolicyBenefits','LiabilityForUnpaidClaimsAndClaimsAdjustmentExpense'})
    classified = 'AssetsCurrent' in tags
    cand = {d: [] for d in DPS}
    for l in L:
        dp_allowed_inpth = False
        o = ov.get((cik, l['tag']))
        r = lib.get((l['st'], l['tag']))
        if r is None:
            r = next((v for (s, t), v in lib.items() if t == l['tag']), None)
        if o is not None:
            c = o['concept']
            if c.startswith('('): continue
            dec, dp = 'map', dp_of(c)
        elif r is not None:
            dec = r['decision']; dp = dp_of(r['concept']) or dp_of(r['parent_concept'])
            if not dp and (dec == 'combined' or 'combined' in (r.get('reason_class') or '')) and l['tag'] in nd:
                dec, dp = 'combined', nd[l['tag']]
        elif l['tag'] in nd:
            dec, dp = 'combined', nd[l['tag']]
        else:
            continue
        if not dp or dp not in cand: continue
        if l['pth'] and dp not in ('shares_outstanding', 'dividends_per_share'): continue
        if l['val'] in (None, '') : continue
        if dec == 'map' and dp in DEMOTE and re.search(DEMOTE[dp], l['lab'] or ''):
            dec = 'combined'
        if dec == 'map' and r is not None and r.get('decision') == 'map' and dp == 'shares_outstanding' and l['st'] not in ('BS', 'EQ'): continue
        cand[dp].append((dec, l))
    out = []
    for dp in DPS:
        c = cand[dp]; h = home(dp)
        maps = [l for d, l in c if d == 'map']
        comps = [l for d, l in c if d == 'component']
        combs = [l for d, l in c if d == 'combined']
        PREF = {'stockholders_equity': 'StockholdersEquity', 'net_income': 'NetIncomeLoss', 'comprehensive_income': 'ComprehensiveIncomeNetOfTax'}
        def pick(ls):
            same = [l for l in ls if l['st'] == h] or ls
            if dp in PREF and any(l['tag'] == PREF[dp] for l in same): same = [l for l in same if l['tag'] == PREF[dp]]
            return max(same, key=lambda l: abs(float(l['val'] or 0)))
        status, chosen, rule = 'not_presented', [], 'no face line'
        if (dp in ('current_assets','current_liabilities','cost_of_revenue','gross_profit','inventory','cf_inventory_change','research_and_development')) and (bank or (insurer and not classified)):
            status, rule = 'OUT', 'sector template (bank/insurer)'
        elif dp in BANK:
            hit = [l for l in L if l['tag'] in BANK[dp] and not l['pth'] and l['val'] not in (None, '')]
            if bank and hit: status, chosen, rule = 'mapped', [pick(hit)], 'bank template tag'
            elif not bank: status, rule = 'OUT', 'not a bank'
        elif dp == 'operating_expenses':
            # Dhairya ruling 2026-11-12 (canonical_concept 53/208): opex = costs below cost of revenue down to OI; never incl. COR
            IS_ = [l for l in L if l['st'] == 'IS' and not l['pth']]
            def first(tag):
                x = [l for l in IS_ if l['tag'] == tag and l['val'] is not None]
                return x[0] if x else None
            fv = lambda l: float(l['val']) if l is not None and l['val'] is not None else None
            oil, gpl = first('OperatingIncomeLoss'), first('GrossProfit')
            corl = next((l for d, l in cand['cost_of_revenue'] if l['st'] == 'IS'), None)
            revs = [l for d, l in cand['revenue'] if d == 'map' and l['st'] == 'IS']
            rev = max((fv(l) for l in revs), key=abs) if revs else None
            oi, gp, cor = fv(oil), fv(gpl), fv(corl)
            if gp is None and rev is not None and cor is not None: gp = rev - cor
            near = lambda a, b: a is not None and b is not None and abs(a - b) <= max(abs(b) * 0.0005, 1)
            tmpl = [t for t in ('NoninterestExpense', 'BenefitsLossesAndExpenses') if first(t)]
            tot = [l for l in IS_ if l['tag'] in ('OperatingExpenses', 'CostsAndExpenses', 'OperatingCostsAndExpenses') and l['val'] is not None]
            excl = [l for l in tot if gp is not None and oi is not None and near(fv(l), gp - oi)]
            incl = [l for l in tot if l not in excl]
            if tmpl and (bank or insurer or corl is None):
                status, chosen, rule = 'mapped', [first(tmpl[0])], 'sector template total'
            elif excl:
                status, chosen, rule = 'mapped', [excl[0]], 'printed opex total excluding cost of revenue (ties to GP - OI)'
            elif gp is not None and oi is not None and oil is not None:
                start = gpl or corl
                band = [l for l in IS_ if l['r'] == oil['r'] and start is not None and l['r'] == start['r'] and start['ln'] < l['ln'] < oil['ln']
                        and l['val'] is not None and l['tag'] not in ('GrossProfit', 'OperatingExpenses', 'CostsAndExpenses', 'OperatingCostsAndExpenses') and not l['tag'].endswith('Abstract')]
                if band and near(sum((-fv(l) if l.get('cr') == 'C' else fv(l)) for l in band), gp - oi):
                    status, chosen, rule = 'component_sum', band, 'every face line between GP/COR and OI; ties to GP - OI'
                elif incl:
                    status, chosen, rule = 'combined', [incl[0]], 'total includes cost of revenue: combined, never opex'
                else:
                    status, rule = 'not_presented', 'opex lines do not tie to GP - OI'
            elif incl:
                status, chosen, rule = ('combined', [incl[0]], 'total includes cost of revenue') if cor is not None else ('not_presented', [], 'one-step corporate IS with no cost of revenue: not_presented (ruling 5)')
            else:
                status, rule = 'not_presented', 'no opex total and no GP/COR anchor'
        elif maps:
            status, chosen, rule = 'mapped', [pick(maps)], 'library map'
        elif comps and (dp in DURATION_SUM) and len({l['st'] for l in comps}) >= 1:
            st = h if any(l['st'] == h for l in comps) else comps[0]['st']
            cs = [l for l in comps if l['st'] == st]
            if len(cs) >= 2 or dp == 'total_debt':
                status, chosen, rule = 'component_sum', cs, 'printed face components (duration sum; total_debt founder sum)'
            elif dp == 'sga_expense' and cs[0]['tag'] in ('GeneralAndAdministrativeExpense', 'SellingGeneralAndAdministrativeExpense'):
                status, chosen, rule = 'mapped', cs, 'lone G&A line'
            elif dp == 'interest_expense' and cs[0]['tag'] == 'InterestExpenseDebt' and not any('Interest' in l['tag'] and l['tag'] != 'InterestExpenseDebt' and l['st'] == 'IS' for l in L):
                status, chosen, rule = 'mapped', cs, 'sole-debt interest rule'
            else:
                status, rule = 'not_presented', 'single component only'
        elif combs:
            status, chosen, rule = 'combined', [pick(combs)], 'combined line (library or label demote)'
        elif dp in ('current_assets', 'current_liabilities') and not classified:
            status, rule = 'not_presented', 'unclassified balance sheet'
        elif dp in NOTE and dp not in ('dividends_per_share', 'interest_income', 'sbc'):
            status, rule = 'mapped', 'note-sourced default tag (no face line)'
            out.append(dict(ticker=ticker, rank=rank, data_point=dp, status=status, tags='us-gaap:' + NOTE[dp], stmt='NOTE', sign='', scale='',
                            era_break='', prior_tag='', value_source='sec_api', acc=L[0]['acc'] if L else '', r_page='', label='', fy0_value='', rule=rule))
            continue
        if chosen:
            l0 = chosen[0]
            era = [l for l in chosen if l.get('prior') and l['prior'] != l['tag']]
            out.append(dict(ticker=ticker, rank=rank, data_point=dp, status=status,
                            tags=';'.join(('us-gaap:' if not l['cu'] else 'custom:') + l['tag'] for l in chosen), stmt=l0['st'],
                            sign=sign(l0['val']), scale=l0.get('dc', ''), era_break='Y' if era else 'N', prior_tag=';'.join(l['prior'] for l in era),
                            value_source='fsn_xbrl' if any(l['cu'] for l in chosen) else 'sec_api', acc=l0['acc'], r_page='R%s' % l0['r'],
                            label=l0['lab'], fy0_value=l0['val'], rule=rule))
        else:
            out.append(dict(ticker=ticker, rank=rank, data_point=dp, status=status, tags='', stmt='', sign='', scale='', era_break='', prior_tag='',
                            value_source='', acc=L[0]['acc'] if L else '', r_page='', label='', fy0_value='', rule=rule))
    w = csv.DictWriter(sys.stdout, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
if __name__ == '__main__':
    main(*sys.argv[1:5])
