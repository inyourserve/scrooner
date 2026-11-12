"""Document-first read (DB-first): FSN filing index + report list + line tags from our DB export,
R pages from sec.gov (only the statements needed), companyfacts from data.sec.gov.
Usage: python3 -I read2.py <outdir> <dbfile> <ranks.json> <rank> [<rank> ...]"""
import sys, os, re, json, csv, html, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import secget, dbload
from docmap import DP, DEBT, DA_PARTS, COMBINED, parse_r, classify, facts_index, api_value, kind_of, full, match, fy_cols, months_between, fmt

DATE = '2026-11-12'
VOCAB = ['revenue', 'cost_of_revenue', 'gross_profit', 'operating_expenses', 'sga_expense', 'research_and_development', 'operating_income',
         'interest_expense', 'interest_income', 'other_income_expense_net', 'income_before_tax', 'income_tax_expense', 'net_income', 'basic_eps',
         'diluted_eps', 'weighted_basic_shares', 'weighted_diluted_shares', 'dividends_per_share', 'comprehensive_income', 'cash_and_equivalents',
         'accounts_receivable', 'inventory', 'current_assets', 'ppe_net', 'goodwill', 'total_assets', 'accounts_payable', 'current_liabilities',
         'total_liabilities', 'total_debt', 'stockholders_equity', 'shares_outstanding', 'cfo', 'cash_flow_investing', 'cash_flow_financing', 'capex',
         'depreciation_and_amortization', 'amortization_of_intangibles', 'sbc', 'dividends_paid', 'share_buybacks', 'cf_ar_change',
         'cf_inventory_change', 'cf_ap_change', 'cash_paid_for_interest', 'cash_paid_for_income_taxes', 'net_interest_income',
         'total_interest_income', 'noninterest_income', 'noninterest_expense', 'provision_for_credit_losses', 'deposits', 'loans_net']
BANKDP = ['net_interest_income', 'total_interest_income', 'noninterest_income', 'noninterest_expense', 'provision_for_credit_losses', 'deposits', 'loans_net']
INSURER_SIC = {'6311', '6321', '6331', '6351', '6361', '6399', '6411'}
EXTRA = ['premiums_earned', 'net_investment_income', 'policy_benefits', 'net_income_incl_nci', 'intangibles_net', 'total_equity_incl_nci']
NEED = {'IS', 'CI', 'BS', 'BSP', 'CF', 'EQP', 'ISP', 'CIP'}

def rpage(base, fname):
    return parse_r(secget.get(base + fname) or '')

def read_filing(cik, adsh, reps, idx, kinds):
    base = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace("-", "")}/'
    picked, seen = [], set()
    for r in reps:
        k = classify(r['s'])
        if k in kinds and k not in seen:
            seen.add(k); picked.append(dict(file=f"R{r['r']}.htm", report=r['r'], short=r['s'], kind=k))
    for p in picked:
        p['page'] = rpage(base, p['file'])
    lines = []
    for r in picked:
        k = r['kind']; p = r['page']; c0, c1 = fy_cols(p)
        for row in p['rows']:
            probe = api_value(idx, row['prefix'], row['tag'], adsh, c0[1] if c0 else None)
            kind = kind_of(row['tag'], probe[1] if probe else None)
            def val(c):
                if not c or c[0] >= len(row['vals']): return None
                return full(row['vals'][c[0]], p, kind)
            f0, f1 = val(c0), val(c1)
            a0 = api_value(idx, row['prefix'], row['tag'], adsh, c0[1] if c0 else None) if not row['member'] else None
            a1 = api_value(idx, row['prefix'], row['tag'], adsh, c1[1] if c1 else None) if not row['member'] else None
            lines.append(dict(stmt=k.rstrip('P') if k in ('ISP', 'CIP') else k, r=r['file'], report=r['report'], short=r['short'], order=row['order'], prefix=row['prefix'],
                              tag=row['tag'], label=row['label'], member=row['member'], fy0=f0, fy1=f1, api0=a0[0] if a0 else None, api1=a1[0] if a1 else None,
                              end0=c0[1]['end'].isoformat() if c0 and c0[1]['end'] else '', end1=c1[1]['end'].isoformat() if c1 and c1[1]['end'] else '',
                              m0=match(f0, a0[0] if a0 else None, p, kind), m1=match(f1, a1[0] if a1 else None, p, kind), kind=kind,
                              custom=row['prefix'] not in ('us-gaap', 'dei', 'srt', 'ifrs-full'), scale=p['scale_money']))
    return dict(reps=picked, lines=lines, base=base)

def cover_shares(cik, adsh, idx):
    base = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace("-", "")}/'
    p = rpage(base, 'R1.htm')
    rows = [r for r in p['rows'] if r['tag'] == 'EntityCommonStockSharesOutstanding']
    vals = []
    for r in rows:
        v = next((x for x in r['vals'] if x is not None), None)
        if v is not None: vals.append((v, r['member'], r['label']))
    api = [f for f in idx.get(('dei', 'EntityCommonStockSharesOutstanding'), []) if f['accn'] == adsh]
    return vals, api

def pick(lines, sic):
    res = {}
    face = [l for l in lines if not l['member'] and l['stmt'] in ('IS', 'BS', 'CF', 'CI', 'EQP')]
    for name, st, tags, how in DP:
        if st == 'COVER': continue
        c = [l for l in face if l['tag'] in tags and (st == '*' or l['stmt'] == st) and l['fy0'] is not None]
        if not c and st == 'IS': c = [l for l in face if l['tag'] in tags and l['stmt'] == 'CI' and l['fy0'] is not None]
        if not c: continue
        l = max(c, key=lambda l: abs(l['fy0'])) if how == 'max' else sorted(c, key=lambda l: (tags.index(l['tag']), l['order']))[0]
        res[name] = dict(status='mapped', lines=[l])
    # a data point printed only as member lines (related party / affiliate / asset class ...): component sum of the members,
    # never for members that repeat across a whole statement (co-registrant or segment copies of the statement)
    mem = [l for l in lines if l['member'] and l['stmt'] in ('IS', 'BS', 'CF') and l['fy0'] is not None]
    share = {}
    for st in ('IS', 'BS', 'CF'):
        n = max(1, sum(1 for l in lines if l['stmt'] == st and not l['member']))
        for m in {l['member'] for l in mem if l['stmt'] == st}:
            share[(st, m)] = sum(1 for l in mem if l['stmt'] == st and l['member'] == m) / n
    for name, st, tags, how in DP:
        if name in res or st not in ('IS', 'BS', 'CF'): continue
        c = [l for l in mem if l['tag'] in tags and l['stmt'] == st and share.get((st, l['member']), 1) <= 0.3]
        c = [l for l in c if l['tag'] == c[0]['tag']] if c else c
        if len({l['member'] for l in c}) >= 2:
            res[name] = dict(status='component sum', lines=c, note='printed only as member lines (' + ', '.join(sorted({l['member'] for l in c})) + '); no undimensioned total on the face')
    if 'accounts_receivable' in res and res['accounts_receivable']['lines'][0]['tag'] != 'AccountsReceivableNetCurrent':
        recv = [l for l in face if l['stmt'] == 'BS' and 'Receivable' in l['tag'] and 'Financing' not in l['tag'] and 'Loans' not in l['tag'] and l['fy0'] is not None]
        if len(recv) != 1:
            res['ar_blocked'] = f"wider receivables tag {res['accounts_receivable']['lines'][0]['tag']} is one of {len(recv)} receivables lines on the BS face (ruling 2026-11-12)"
            del res['accounts_receivable']
    bankish = 'Deposits' in {l['tag'] for l in face}
    if bankish:
        for dp in ('revenue',):
            if dp in res and res[dp]['lines'][0]['tag'] not in ('Revenues', 'RevenuesNetOfInterestExpense'): del res[dp]
        if 'total_interest_income' in res and 'interest_income' not in res: res['interest_income'] = res['total_interest_income']
        if 'noninterest_expense' in res and 'operating_expenses' not in res: res['operating_expenses'] = res['noninterest_expense']
    DEBT_RX = r'(debenture|notes? payable|senior notes|subordinated|borrowings?|\bdebt\b|advances from (the )?federal home loan|fhlb advances|term loan|credit facilit|convertible notes)'
    d = [l for l in face if l['stmt'] == 'BS' and l['fy0'] is not None and (l['tag'] in DEBT or (l['custom'] and re.search(DEBT_RX, l['label'], flags=re.I)))
         and not re.search(r'(accrued interest|interest payable|repurchase|federal funds)', l['label'], flags=re.I) or (l['stmt'] == 'BS' and l['fy0'] is not None and l['tag'] in DEBT and not l['custom'] and False)]
    tg = {l['tag'] for l in d}
    if {'LongTermDebtCurrent', 'LongTermDebtNoncurrent'} <= tg or {'LongTermDebtCurrent', 'LongTermDebtNoncurrent'} & tg and 'LongTermDebt' in tg and len(tg) > 1:
        d = [l for l in d if l['tag'] != 'LongTermDebt']
    if d: res['total_debt'] = dict(status='component sum' if len(d) > 1 else 'mapped', lines=d)
    if 'depreciation_and_amortization' not in res:
        da = [l for l in face if l['stmt'] == 'CF' and l['tag'] in DA_PARTS and l['fy0'] is not None]
        if da: res['depreciation_and_amortization'] = dict(status='component sum' if len(da) > 1 else 'mapped', lines=da)
    elif res['depreciation_and_amortization']['lines'][0]['tag'] == 'DepreciationAmortizationAndOther':
        res['depreciation_and_amortization']['status'] = 'combined'
    if 'depreciation_and_amortization' in res and res['depreciation_and_amortization']['lines'][0]['tag'] in ('Depreciation',) + tuple(DA_PARTS):
        extra = [l for l in face if l['stmt'] == 'CF' and l['custom'] and re.search(r'amortization', l['label'], flags=re.I) and not re.search(r'(debt|financing|lease|deferred|investment|premium|discount|accretion|contract cost)', l['label'], flags=re.I) and l['fy0'] is not None]
        if extra:
            d = res['depreciation_and_amortization']
            d['lines'] = d['lines'] + extra
            d['status'] = 'combined' if any(re.search(r'impairment', l['label'], flags=re.I) for l in extra) else 'component sum'
            if d['status'] == 'combined': d['note'] = 'amortization printed in one line with impairments: ' + '; '.join(f"'{l['label']}'" for l in extra)
    if 'sga_expense' not in res:
        parts = [l for l in face if l['stmt'] == 'IS' and l['tag'] in ('SellingAndMarketingExpense', 'GeneralAndAdministrativeExpense', 'SellingExpense') and l['fy0'] is not None]
        if len(parts) >= 2: res['sga_expense'] = dict(status='component sum', lines=parts)
    if 'goodwill' not in res:
        g = [l for l in face if l['stmt'] == 'BS' and l['tag'] == 'IntangibleAssetsNetIncludingGoodwill' and l['fy0'] is not None]
        if g: res['goodwill'] = dict(status='combined', lines=g[:1], note='goodwill printed in one line with intangible assets')
    for tag, dp in COMBINED.items():
        c = [l for l in face if l['tag'] == tag and l['fy0'] is not None]
        if c and dp not in res: res[dp] = dict(status='combined', lines=c[:1])
    lab = {'depreciation_and_amortization': r'depreciation', 'capex': r'^(capital expenditures?|purchases? of property|additions to property|purchases? of plant)',
           'revenue': r'^(total )?(net )?(operating )?(revenues?|sales|net sales)( net)?$', 'operating_income': r'^(total )?operating (income|profit|earnings)',
           'interest_expense': r'^interest expense', 'net_income': r'^net (income|earnings)( \(loss\))?$', 'sbc': r'(stock|share|equity)[- ]based compensation',
           'dividends_paid': r'dividends paid', 'cash_and_equivalents': r'^cash and cash equivalents$', 'sga_expense': r'^selling, general,? and administrative',
           'cash_paid_for_income_taxes': r'income taxes paid', 'cash_paid_for_interest': r'^(cash paid for )?interest( paid)?', 'share_buybacks': r'(repurchase|purchase)s? of (common )?(stock|shares)', 'cost_of_revenue': r'^(total )?cost of (revenues?|sales|goods sold)'}
    for dp, rx in lab.items():
        if dp in res: continue
        c = [l for l in face if l['custom'] and re.search(rx, l['label'], flags=re.I) and l['fy0'] is not None]
        if c: res[dp] = dict(status='custom tag', lines=c[:1])
    opex_rule(res, face)
    return res

OPEX_TOTALS = ('OperatingExpenses', 'CostsAndExpenses', 'OperatingCostsAndExpenses', 'CostsAndExpensesExcludingCostOfRevenue')
def opex_rule(res, face):
    """Ruling 2026-11-12: operating_expenses never includes cost of revenue. A printed total that excludes COGS is mapped;
    a total that includes COGS is combined; otherwise the component sum of every face line between gross profit and operating income,
    tied exactly to GP - OI."""
    if 'noninterest_expense' in res and res.get('operating_expenses') is res.get('noninterest_expense'): return
    IS = sorted([l for l in face if l['stmt'] == 'IS' and l['fy0'] is not None], key=lambda l: l['order'])
    if not IS: return
    oi = res.get('operating_income', {}).get('lines', [None])[0]
    gp = res.get('gross_profit', {}).get('lines', [None])[0]
    cor = res.get('cost_of_revenue', {}).get('lines', [None])[0]
    rev = res.get('revenue', {}).get('lines', [None])[0]
    tol = lambda n: (IS[0]['scale'] / 2.0) * max(n, 1) + 1e-6
    res.pop('operating_expenses', None)
    tot = [l for l in IS if l['tag'] in OPEX_TOTALS and (not oi or l['order'] < oi['order'])]
    if tot:
        T = tot[-1]
        if cor and rev and oi and abs(abs(T['fy0']) - abs(rev['fy0'] - oi['fy0'])) <= tol(3):
            res['operating_expenses'] = dict(status='combined', lines=[T], note=f"printed total '{T['label']}' {fmt(T['fy0'])} = revenue - operating income: it includes cost of revenue (ruling: never opex)")
            T = None
        elif cor and rev and oi and abs(abs(T['fy0']) - (abs(rev['fy0']) - abs(cor['fy0']) - oi['fy0'])) > tol(3) and T['order'] < cor['order']:
            T = None
        if T is not None and 'operating_expenses' not in res:
            if cor and T['order'] < cor['order'] + 0:
                pass
            res['operating_expenses'] = dict(status='mapped', lines=[T], note=f"printed total '{T['label']}' excludes cost of revenue")
            return
        if 'operating_expenses' in res: 
            pass
    if gp and oi and gp['order'] < oi['order']:
        start = gp['order']
    elif cor and oi and cor['order'] < oi['order']:
        start = cor['order']
    else:
        return
    comp = [l for l in IS if start < l['order'] < oi['order'] and l['tag'] not in OPEX_TOTALS]
    if not comp: return
    target = (gp['fy0'] if gp else (rev['fy0'] - abs(cor['fy0']) if rev and cor else None))
    if target is None: return
    target -= oi['fy0']
    s = sum(l['fy0'] for l in comp)
    if abs(s - target) <= tol(len(comp)):
        if res.get('operating_expenses', {}).get('status') in (None, 'combined'):
            res['operating_expenses'] = dict(status='component sum', lines=comp, note=f"sum of every face line between {'gross profit' if gp else 'cost of revenue'} and operating income = {fmt(s)} = GP - OI {fmt(target)}")
    elif 'operating_expenses' not in res:
        res['opex_untied'] = f"face lines between GP and OI sum to {fmt(s)}, GP - OI = {fmt(target)}: no tie, not mapped"

def sector(sic, lines):
    tags = {l['tag'] for l in lines if not l['member']}
    bank = 'Deposits' in tags and bool(tags & {'InterestAndDividendIncomeOperating', 'InterestExpenseDeposits', 'NoninterestIncome', 'InterestIncomeExpenseNet', 'LoansAndLeasesReceivableNetReportedAmount'})
    classified = 'AssetsCurrent' in tags or 'LiabilitiesCurrent' in tags
    insurer = (str(sic) in INSURER_SIC) or bool(tags & {'PremiumsEarnedNet', 'PolicyholderBenefitsAndClaimsIncurredNet', 'LiabilityForFuturePolicyBenefits', 'LiabilityForClaimsAndClaimsAdjustmentExpense'})
    reit = str(sic) == '6798'
    return dict(bank=bank, insurer=insurer and not classified, reit=reit, classified=classified)

def out_or_np(dp, sec):
    if dp in BANKDP and not sec['bank']: return 'OUT', 'not a bank (no deposits/bank income lines on the face)'
    if (sec['bank'] or sec['insurer']) and dp in ('current_assets', 'current_liabilities', 'cost_of_revenue', 'gross_profit', 'inventory', 'cf_inventory_change', 'research_and_development'):
        return 'OUT', ('bank' if sec['bank'] else 'insurer') + ': unclassified balance sheet / no such line (sector template)'
    if sec['bank'] and dp in ('accounts_receivable', 'accounts_payable', 'operating_income', 'sga_expense'):
        return 'OUT', 'bank: no such line (sector template)'
    return 'not_presented', 'no face line carries this data point in the latest 10-K statements (face lines listed in the md)'

def tenk_list(idx):
    """Original 10-Ks in companyfacts: accn -> (fy, filed, current period end)."""
    ks = {}
    for (tax, tag), lst in idx.items():
        if tax != 'us-gaap': continue          # dei cover facts carry post-year-end dates
        for f in lst:
            if f.get('form') in ('10-K', '10-KT') and f.get('fp') == 'FY' and f.get('fy') and f.get('start') and 11 <= months_between(f['start'], f['end']) <= 13:
                k = ks.setdefault(f['accn'], dict(fy=int(f['fy']), filed=f['filed'], end=f['end']))
                if f['end'] > k['end']: k['end'] = f['end']
    byfy = {}
    for a, k in sorted(ks.items(), key=lambda kv: kv[1]['filed']):
        byfy.setdefault(int(k['end'][:4]), (a, k))   # fiscal year = year of the 10-K's own current-period end (the dei fy focus is often mislabelled); first (original) 10-K wins
    return byfy

def era_map(idx, res, fy0_year):
    """Per data point: the tag each original 10-K (FY2015 .. latest) carries for that data point's current-year value."""
    byfy = tenk_list(idx)
    out = {}
    specs = [(name, tags, False) for name, st, tags, how in DP]
    for name, d in res.items():
        if isinstance(d, dict) and d['status'] == 'component sum':
            extra = DEBT if name == 'total_debt' else DA_PARTS if name == 'depreciation_and_amortization' else []
            specs = [s for s in specs if s[0] != name] + [(name, list(dict.fromkeys([l['tag'] for l in d['lines']] + extra)), True)]
    specs.append(('shares_outstanding', ['CommonStockSharesOutstanding'], False))
    for name, tags, multi in specs:
        if name != 'shares_outstanding' and (name not in res or not isinstance(res[name], dict)): continue
        seq = []
        for fy in range(2015, fy0_year + 1):
            if fy not in byfy: continue
            a, k = byfy[fy]
            found = []
            for tg in tags:
                for f in idx.get(('us-gaap', tg), []):
                    if f['accn'] == a and f['end'] == k['end'] and (not f.get('start') or 11 <= months_between(f['start'], f['end']) <= 13):
                        found.append(tg); break
                if found and not multi: break
            hit = '+'.join(found) if found else None
            seq.append((fy, a, hit))
        segs = []
        for fy, a, tg in seq:
            if segs and segs[-1][2] == tg: segs[-1] = (segs[-1][0], fy, tg, a)
            else: segs.append((fy, fy, tg, a))
        out[name] = segs
    first_fy = min(byfy) if byfy else None
    fy15 = next(((fy, byfy[fy][0]) for fy in sorted(byfy) if fy >= 2015), None)
    return out, fy15, first_fy

def era_scan_unused(idx, res, fy0_end):
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
        last = [str(int(fy0_end[:4]) - k) for k in range(0, 6)]
        for sib in tags:
            if sib == t0: continue
            ys = fys(sib)
            gap = [y for y in last if y in ys and y not in y0]
            if gap: out.setdefault(name, []).append((sib, sorted(gap), ys[max(gap)]))
    return out

def latest_10k_from_api(idx):
    best = None
    for (tax, tag), lst in idx.items():
        if tag not in ('Assets', 'EntityCommonStockSharesOutstanding'): continue
        for f in lst:
            if f.get('form') in ('10-K', '10-KT') and (best is None or f['filed'] > best[1]): best = (f['accn'], f['filed'])
    return best

def reps_from_summary(cik, adsh):
    base = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace("-", "")}/'
    fs = secget.get(base + 'FilingSummary.xml') or ''
    reps = []
    for m in re.finditer(r'<Report instance=.*?</Report>', fs, flags=re.S):
        x = m.group(0); g = lambda t: (re.search(f'<{t}>(.*?)</{t}>', x, flags=re.S) or [None, None])[1]
        if g('MenuCategory') == 'Statements' and g('HtmlFileName'):
            n = re.search(r'R(\d+)\.htm', g('HtmlFileName'))
            if n: reps.append(dict(r=int(n.group(1)), s=html.unescape(g('ShortName') or '')))
    return reps

def run(outdir, db, rk):
    tk, cik, cid = rk['ticker'], rk['cik'], rk['company_id']
    rows = sorted([x for x in db if x['company_id'] == cid], key=lambda x: x['rn'])
    secget.COUNT[0] = 0
    cikp = '%010d' % int(cik)
    cf = secget.getjson(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cikp}.json') or {}
    idx = facts_index(cf)
    S = dict(rank=rk['rank'], ticker=tk, cik=cik, name=cf.get('entityName'))
    sic = ''
    fsn_latest = next((r for r in rows if r['rn'] == 1), None)
    api_latest = latest_10k_from_api(idx)
    newer = api_latest and (not fsn_latest or api_latest[0] != fsn_latest['accession'] and api_latest[1] > str(fsn_latest.get('period') or ''))
    if newer and fsn_latest and any(r['accession'] == api_latest[0] for r in rows): newer = False
    if not fsn_latest and not api_latest:
        S.update(status='no_10K'); write_stub(outdir, S, 'No 10-K in our FSN store (sets to 2026-09) and none in SEC companyfacts.'); return S
    if newer:
        adsh = api_latest[0]; reps = reps_from_summary(cik, adsh); fsn_lines = None; src = f'SEC FilingSummary (10-K filed {api_latest[1]} is newer than the FSN store)'
    else:
        adsh = fsn_latest['accession']; reps = fsn_latest['reps'] or []; fsn_lines = fsn_latest['lines'] or []; src = 'FSN store (fsn.filing, fsn.report)'
    if not reps:
        reps = reps_from_summary(cik, adsh); src += ' + FilingSummary (no statement reports in FSN)'
    rd = read_filing(cik, adsh, reps, idx, NEED)
    sec = sector(sic, rd['lines'])
    res = pick(rd['lines'], sic)
    fy0_end = next((l['end0'] for l in rd['lines'] if l['stmt'] == 'IS' and l['end0']), '') or next((l['end0'] for l in rd['lines'] if l['end0']), '0000')
    fy0_year = int(fy0_end[:4]) if fy0_end[:4].isdigit() else 0
    segs, fy15, first_fy = era_map(idx, res, fy0_year)
    # filings to open: the FY2015 10-K (or the first 10-K after it) always, then the last 10-K of every earlier era (cap 3 era 10-Ks)
    want = []
    if fy15 and fy15[1] != adsh: want.append(fy15[1])
    import collections as _C
    cnt = _C.Counter(s[3] for v in segs.values() for s in v[:-1] if s[3] != adsh)
    for a, n in cnt.most_common():
        if a not in want and len(want) < 5: want.append(a)
    era_reads = []
    for acc in want:
        er = next((r for r in rows if r['accession'] == acc), None)
        ereps = (er or {}).get('reps') or reps_from_summary(cik, acc)
        rr = read_filing(cik, acc, ereps, idx, {'IS', 'BS', 'CF', 'CI', 'EQP'})
        rr['fy'] = next((fy for fy, (a, k) in tenk_list(idx).items() if a == acc), None)
        rr['map'] = pick(rr['lines'], sic)
        era_reads.append((acc, rr))
    eras = dict(segs=segs, fy15=fy15, first_fy=first_fy, fy0=fy0_year, reads=era_reads)
    fsn_tags = {}
    for l in fsn_lines or []:
        fsn_tags.setdefault(int(l['r']), set()).add(l['t'])
    # quirks
    Q = []
    def q(kind, dp, l, note, acc=None):
        Q.append(dict(rank=rk['rank'], ticker=tk, kind=kind, data_point=dp, tag=(f"{l['prefix']}:{l['tag']}" if l else ''), label=(l['label'] if l else ''),
                      printed=fmt(l['fy0']) if l else '', api=fmt(l['api0']) if l else '', period_end=(l['end0'] if l else ''), accession=acc or adsh, r_page=(l['r'] if l else ''), note=note))
    for name, d in [(k, v) for k, v in res.items() if isinstance(v, dict)]:
        for l in d['lines']:
            for m, f, a, end in ((l['m0'], l['fy0'], l['api0'], l['end0']), (l['m1'], l['fy1'], l['api1'], l['end1'])):
                if m == 'N':
                    Q.append(dict(rank=rk['rank'], ticker=tk, kind='printed_vs_api', data_point=name, tag=f"{l['prefix']}:{l['tag']}", label=l['label'], printed=fmt(f), api=fmt(a),
                                  period_end=end, accession=adsh, r_page=l['r'], note=f'printed {fmt(f)} vs companyfacts {fmt(a)}; the filing decides'))
        l = d['lines'][0]
        if d['status'] == 'custom tag': q('custom_tag_line', name, l, 'data-point line carries a company extension tag (not in companyfacts)')
        if d['status'] == 'combined': q('combined_line', name, l, 'combined line; never the pure concept')
    for name, sg in eras['segs'].items():
        tagged = [s for s in sg if s[2]]
        for s0, s1 in zip(tagged, tagged[1:]):
            if s0[2] != s1[2]:
                Q.append(dict(rank=rk['rank'], ticker=tk, kind='era_change', data_point=name, tag=f"{s0[2]} -> {s1[2]}", label=res[name]['lines'][0]['label'] if isinstance(res.get(name), dict) else '',
                              printed='', api='', period_end=f'FY{s0[1]} -> FY{s1[0]}', accession=s0[3], r_page='', note=f'tag switch between the FY{s0[1]} 10-K ({s0[3]}) and the FY{s1[0]} 10-K ({s1[3]})'))
    for acc, er in eras['reads']:
        for name, d in [(k, v) for k, v in er['map'].items() if isinstance(v, dict)]:
            for l in d['lines']:
                if l['m0'] == 'N':
                    Q.append(dict(rank=rk['rank'], ticker=tk, kind='printed_vs_api', data_point=name, tag=f"{l['prefix']}:{l['tag']}", label=l['label'], printed=fmt(l['fy0']), api=fmt(l['api0']),
                                  period_end=l['end0'], accession=acc, r_page=l['r'], note=f'era 10-K: printed {fmt(l["fy0"])} vs companyfacts {fmt(l["api0"])}; the filing decides'))
    for dp in ('diluted_eps', 'basic_eps'):
        if dp in res and res[dp]['lines'][0]['tag'].startswith('IncomeLossFromContinuing'): q('eps_contops_tag', dp, res[dp]['lines'][0], 'EPS printed only under the continuing-operations tag')
    if 'net_income' in res and res['net_income']['lines'][0]['tag'] != 'NetIncomeLoss': q('net_income_tag', 'net_income', res['net_income']['lines'][0], 'no NetIncomeLoss line on the IS face')
    for l in rd['lines']:
        if l['member'] or l['custom']: continue
        if l['tag'] == 'CommercialPaper' and 'short' in l['label'].lower(): q('label_tag', 'total_debt', l, 'CommercialPaper labelled as short-term debt')
        if l['tag'] == 'IntangibleAssetsNetIncludingGoodwill' and 'goodwill' not in l['label'].lower(): q('label_tag', 'goodwill', l, 'goodwill-inclusive tag on a line not labelled goodwill')
        if l['tag'] == 'IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest' and 'before' in l['label'].lower() and 'tax' in l['label'].lower():
            q('label_tag', 'income_before_tax', l, 'after-tax tag on a pretax-labelled line')
    if fsn_lines is not None:
        miss = [l for l in rd['lines'] if l['stmt'] in ('IS', 'BS', 'CF', 'CI') and l['tag'] not in fsn_tags.get(l['report'], set())]
        if miss:
            Q.append(dict(rank=rk['rank'], ticker=tk, kind='fsn_line_missing', data_point='', tag=';'.join(sorted({m['tag'] for m in miss}))[:300], label='', printed='', api='',
                          period_end='', accession=adsh, r_page=';'.join(sorted({m['r'] for m in miss})), note=f'{len(miss)} R-page line(s) whose tag is not an FSN line of the same report (fsn.line)'))
    # shares outstanding
    so = [l for l in rd['lines'] if l['stmt'] in ('BS', 'BSP') and l['tag'] == 'CommonStockSharesOutstanding' and l['fy0'] is not None]
    if not so:
        bs_end = next((l['end0'] for l in rd['lines'] if l['stmt'] == 'BS' and l['end0']), None)
        so = [l for l in rd['lines'] if l['stmt'] == 'EQP' and l['tag'] == 'CommonStockSharesOutstanding' and l['fy0'] is not None and l['end0'] == bs_end]
    plain = [l for l in so if not l['member']]
    use = plain[:1] if plain else so
    res_so = dict(lines=use, tot=sum(l['fy0'] for l in use), n=len(use), api=(sum(l['api0'] for l in use) if all(l['api0'] is not None for l in use) else None),
                  m=('Y' if all(l['m0'].startswith('Y') for l in use) else 'N' if any(l['m0'] == 'N' for l in use) else ('dimensional: class members (companyfacts holds no member facts)' if any(l['member'] for l in use) else 'no companyfacts fact'))) if use else None
    cov_vals = None
    nface = [l for l in rd['lines'] if l['stmt'] in ('IS', 'BS', 'CF', 'CI') and l['fy0'] is not None]
    S.update(status='read', latest=adsh, source=src, fy0_end=fy0_end, statements=len(rd['reps']), face_lines=len(nface),
             face_custom=sum(1 for l in nface if l['custom']), face_dimensional=sum(1 for l in nface if l['member']),
             face_api_equal=sum(1 for l in nface if l['m0'].startswith('Y')), face_api_differ=sum(1 for l in nface if l['m0'] == 'N'),
             face_api_none=sum(1 for l in nface if not l['m0']), sector=('bank' if sec['bank'] else 'insurer' if sec['insurer'] else 'reit' if sec['reit'] else 'general'),
             era_10k=len(era_reads), quirks=len(Q), sec_requests=secget.COUNT[0])
    rowsout = write_csv(outdir, tk, rd, res, eras, sec, adsh, res_so, cov_vals)
    S['dp_mapped'] = sum(1 for r in rowsout if r[2] in ('mapped', 'component sum', 'combined', 'custom tag'))
    S['dp_not_presented'] = sum(1 for r in rowsout if r[2] == 'not_presented'); S['dp_out'] = sum(1 for r in rowsout if r[2] == 'OUT')
    S['dp_value_mismatch'] = sum(1 for x in Q if x['kind'] == 'printed_vs_api')
    write_md(outdir, S, rd, res, eras, era_reads, Q, rowsout, fsn_tags if fsn_lines is not None else None)
    json.dump(Q, open(os.path.join(outdir, 'quirks', tk + '.json'), 'w'), indent=0)
    return S

def era_text(name, eras):
    sg = eras['segs'].get(name, [])
    parts = [f"FY{a}-FY{b}: {tg or 'no standard tag'}" for a, b, tg, acc in sg]
    docs = []
    for acc, er in eras['reads']:
        d = er['map'].get(name)
        if isinstance(d, dict):
            docs.append(f"FY{er.get('fy')} 10-K {acc} {d['lines'][0]['r']} '{d['lines'][0]['label'][:40]}' {';'.join(l['tag'] for l in d['lines'])} ({d['status']}) FILING-CHECKED")
        else:
            docs.append(f"FY{er.get('fy')} 10-K {acc}: no face line")
    start = eras['fy15'][0] if eras['fy15'] else None
    covered = sorted({fy for a, b, tg, acc in sg if tg for fy in range(a, b + 1)})
    if start is None: cov = 'coverage: no 10-K FY2015+ in companyfacts'
    else:
        gaps = [fy for fy in range(start, eras['fy0'] + 1) if fy not in covered]
        cov = f"coverage FY{start}-FY{eras['fy0']}" + (' complete' if not gaps else ' gaps FY' + ','.join(map(str, gaps)) + ' (no standard-tag 10-K fact; see FILING-CHECKED era reads)')
        if start > 2015: cov += f' (first 10-K FY{eras["first_fy"]})'
    return ' | '.join(['companyfacts by 10-K: ' + ('; '.join(parts) or 'none')] + docs + [cov])

def dprow(tk, name, d, eras, adsh):
    ls = d['lines']
    def ssum(k): return sum(l[k] for l in ls) if all(l[k] is not None for l in ls) else None
    s0, s1, a0, a1 = ssum('fy0'), ssum('fy1'), ssum('api0'), ssum('api1')
    ms = [l['m0'] for l in ls] + [l['m1'] for l in ls if l['fy1'] is not None]
    if any(m == 'N' for m in ms): mm = 'N'
    elif all(m.startswith('Y') for m in ms): mm = 'Y (sign differs: printed in parentheses/negated label)' if all('sign' in l['m0'] for l in ls) else 'Y'
    elif any(l['custom'] for l in ls): mm = 'custom tag: no companyfacts fact'
    else: mm = 'no companyfacts fact'
    era = era_text(name, eras)
    note = (d.get('note', '') + ' | ' if d.get('note') else '') + (' + '.join(f"'{l['label']}' {fmt(l['fy0'])}" for l in ls) + ' | ' if len(ls) > 1 else '') + f"accn {adsh} FY0 end {ls[0]['end0']}"
    st = 'component sum' if d['status'] == 'component sum' else d['status']
    return [tk, name, st, ';'.join(f"{l['prefix']}:{l['tag']}" for l in ls), ls[0]['stmt'], '+'.join(sorted({l['r'] for l in ls})),
            ' + '.join(l['label'] for l in ls)[:200], fmt(s0), fmt(a0), fmt(s1), fmt(a1), mm, era, 'FILING-CHECKED', note]

def write_csv(outdir, tk, rd, res, eras, sec, adsh, so, cov_vals):
    rows = []
    for dp in VOCAB:
        if dp == 'shares_outstanding':
            if so:
                ls = so['lines']
                rows.append([tk, dp, 'mapped' if so['n'] == 1 else 'component sum', 'us-gaap:CommonStockSharesOutstanding', ls[0]['stmt'], '+'.join(sorted({l['r'] for l in ls})),
                             ' + '.join(l['label'] for l in ls)[:200] + (f' (classes: {", ".join(l["member"] for l in ls if l["member"])})' if any(l['member'] for l in ls) else ''),
                             fmt(so['tot']), fmt(so['api']), fmt(sum(l['fy1'] or 0 for l in ls)) if all(l['fy1'] is not None for l in ls) else '', '', so['m'], '', 'FILING-CHECKED',
                             f"shares outstanding at the balance-sheet date {ls[0]['end0']} (ruling 2026-11-12: never the dei cover count) | accn {adsh}"])
            else:
                rows.append([tk, dp, 'not_presented', '', 'BS', '', '', '', '', '', '', '', '', 'FILING-CHECKED', 'no CommonStockSharesOutstanding at the balance-sheet date on the BS or its parenthetical (ruling 2026-11-12: the dei cover count is never used)'])
            continue
        if dp in res and (dp not in BANKDP or sec['bank']):
            d = res[dp]
            if d['status'] == 'custom tag':
                r = dprow(tk, dp, dict(d, status='mapped'), eras, adsh); r[14] = 'company extension tag on the face line; ' + r[14]; rows.append(r)
            else:
                rows.append(dprow(tk, dp, d, eras, adsh))
        else:
            st, why = out_or_np(dp, sec)
            if dp == 'operating_expenses' and res.get('opex_untied'): why = res['opex_untied']
            if dp == 'accounts_receivable' and res.get('ar_blocked'): why = res['ar_blocked']
            rows.append([tk, dp, st, '', next((s for n, s, t, h in DP if n == dp), ''), '', '', '', '', '', '', '', '', 'FILING-CHECKED', why])
    fn = os.path.join(outdir, f'{tk}-docmap-{DATE}.csv')
    with open(fn, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ticker', 'data_point', 'status', 'tags', 'stmt', 'r_page', 'label', 'fy0_printed', 'fy0_api', 'fy1_printed', 'fy1_api', 'match', 'era_from_note', 'evidence_class', 'note'])
        w.writerows(rows)
    return rows

def write_stub(outdir, S, why):
    open(os.path.join(outdir, f"{S['ticker']}-docmap-{DATE}.md"), 'w').write(f"# {S['ticker']} document-first map {DATE} (rank {S['rank']})\n\n**Status: {S['status']}.** {why}\n")
    with open(os.path.join(outdir, f"{S['ticker']}-docmap-{DATE}.csv"), 'w', newline='') as f:
        csv.writer(f).writerow(['ticker', 'data_point', 'status', 'tags', 'stmt', 'r_page', 'label', 'fy0_printed', 'fy0_api', 'fy1_printed', 'fy1_api', 'match', 'era_from_note', 'evidence_class', 'note'])
    json.dump([], open(os.path.join(outdir, 'quirks', S['ticker'] + '.json'), 'w'))

def write_md(outdir, S, rd, res, eras, era_reads, Q, rows, fsn_tags):
    tk = S['ticker']
    L = [f"# {tk} document-first map {DATE} (rank {S['rank']}, read-only)", '',
         'Evidence: FILING-CHECKED unless a row says otherwise. Printed values come from the R pages of the 10-K on sec.gov; tags from each R-page row\'s element reference; API = SEC companyfacts (undimensioned, same accession, same period); FSN = our fsn.line rows for the same filing and report.', '',
         f"Company: {S.get('name')} (CIK {int(S['cik']):010d}); sector shape read from the face: {S['sector']}.", '',
         '## Filings opened', f"- Latest 10-K {S['latest']} (index from {S['source']}): " + ', '.join(f"{r['file']} {r['short']} [{r['kind']}]" for r in rd['reps']) + '.']
    for acc, er in eras['reads']:
        L.append(f"- Era 10-K {acc} (FY{er.get('fy')}): " + ', '.join(f"{r['file']} {r['short']}" for r in er['reps']) + '.')
    L += ['- companyfacts: one call to data.sec.gov.', f"- sec.gov requests for this company: {S['sec_requests']}.", '',
          'FY0 = the latest fiscal-year column, FY1 = the prior year. Values in full units (printed value × the R-page scale); EPS per share; shares in shares.', '',
          '## Data points (the CSV holds exactly these rows)', '| data point | status | tag(s) | R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match |', '|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        L.append('| ' + ' | '.join([r[1], r[2], r[3].replace('us-gaap:', ''), r[5], r[6][:70], r[7], r[8], r[9], r[10], r[11] if r[2] not in ('OUT', 'not_presented') else r[14][:70]]) + ' |')
    ex = [(n, res[n]) for n in EXTRA if n in res]
    if ex:
        L += ['', 'Sector lines also on the face (not in the graded vocabulary): ' + '; '.join(f"{n} = {d['lines'][0]['tag']} '{d['lines'][0]['label'][:50]}' {fmt(d['lines'][0]['fy0'])}" for n, d in ex) + '.']
    L += ['', f"## Eras FY2015 to FY{eras['fy0']} (every data point; companyfacts tag per original 10-K, and the era 10-Ks opened: FY2015 always, plus the last 10-K of each earlier era)"]
    if eras['fy15'] and eras['fy15'][0] > 2015: L.append(f"- First 10-K in companyfacts is FY{eras['first_fy']}: no FY2015 10-K exists for this registrant.")
    L += ['| data point | latest status | eras (companyfacts) | era 10-K reads (FILING-CHECKED) | coverage |', '|---|---|---|---|---|']
    for r in rows:
        if r[2] in ('OUT', 'not_presented'): continue
        et = era_text(r[1], eras).split(' | ')
        L.append(f"| {r[1]} | {r[2]} | {et[0].replace('companyfacts by 10-K: ', '')} | {'; '.join(et[1:-1])} | {et[-1]} |")
    L += ['', '## Quirks and mismatches (the filing decides)']
    L += [f"- [{x['kind']}] {x['data_point']}: {x['tag']} '{x['label'][:80]}' — {x['note']} ({x['accession']} {x['r_page']} {x['period_end']})" for x in Q] or ['- none']
    L += ['', '## Every face line (printed page → tag → FSN → companyfacts)', '| R | stmt | # | label | tag | member | FY0 printed | FY0 API | match | in FSN |', '|---|---|---|---|---|---|---|---|---|---|']
    for l in rd['lines']:
        infsn = '' if fsn_tags is None else ('Y' if l['tag'] in fsn_tags.get(l['report'], set()) else 'N')
        L.append(f"| {l['r']} | {l['stmt']} | {l['order']} | {l['label'][:60]} | {l['prefix']}:{l['tag']} | {l['member'] or ''} | {fmt(l['fy0'])} | {fmt(l['api0'])} | {l['m0'] or ('custom' if l['custom'] else 'dimensional' if l['member'] else '')} | {infsn} |")
    L += ['', f"Totals: {S['face_lines']} IS/BS/CF/CI face lines with an FY0 value; {S['face_api_equal']} equal companyfacts, {S['face_api_differ']} differ, {S['face_api_none']} without a companyfacts fact ({S['face_custom']} custom-tag, {S['face_dimensional']} dimensional)."]
    open(os.path.join(outdir, f'{tk}-docmap-{DATE}.md'), 'w').write('\n'.join(L) + '\n')

if __name__ == '__main__':
    outdir, dbf, rkf = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(os.path.join(outdir, 'quirks'), exist_ok=True)
    db = dbload.load(dbf); ranks = {r['rank']: r for r in json.load(open(rkf))}
    for rank in map(int, sys.argv[4:]):
        try:
            print(json.dumps(run(outdir, db, ranks[rank])), flush=True)
        except Exception as e:
            import traceback; traceback.print_exc()
            print(json.dumps(dict(rank=rank, ticker=ranks[rank]['ticker'], status='error', error=str(e)[:200])), flush=True)
