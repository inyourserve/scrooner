"""Grade predictions against reader docmaps. Usage: grade.py PRED_DIR DOCMAP_DIR [TICKERS...] -> per-row CSV on stdout, summary on stderr.
correct = status matches (component sum == component_sum) and, for mapped/combined/component_sum, the tag set matches (prefix ignored)."""
import csv, glob, os, sys
from math import comb
def norm_status(s): return (s or '').strip().lower().replace(' ', '_')
def tagset(s):
    import re
    return {re.sub(r'\{.*?\}','',t).split(':')[-1].strip().lower() for t in re.split(r'[;,+]', s or '') if t.strip()}
def cp_upper(k, n, a=0.05):
    """Clopper-Pearson two-sided 95% upper bound on the error rate (log-space binomial CDF; no overflow)."""
    from math import lgamma, log, exp
    if n == 0 or k >= n: return 1.0
    def cdf(p):
        lp, lq = log(p), log(1 - p)
        return sum(exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * lp + (n - i) * lq) for i in range(k + 1))
    lo, hi = k / n if k else 0.0, 1.0
    for _ in range(80):
        p = (lo + hi) / 2
        if p <= 0: lo = 1e-12; continue
        lo, hi = (p, hi) if cdf(p) > a / 2 else (lo, p)
    return hi
def cp_upper_one(k, n, a=0.05):
    """One-sided 95% Clopper-Pearson upper bound on the error rate (graduation bar, Dhairya/NOW.md 2026-11-12)."""
    return cp_upper(k, n, 2 * a)
def ks_raw(k): return norm_status(k.get('status'))
_NFL = None
def note_fin_lease_outside_debt(tk):
    """True when no BS line carries leases, the note FinanceLeaseLiability > 0 and the filing's
    FinanceLeaseLiability*StatementOfFinancialPositionExtensibleList puts it outside debt (notes.jsonl fl_loc == 'out').
    Needs GRADE_LINES_DIR and GRADE_NOTES_PATH."""
    import json, re
    global _NFL
    d, npth = os.environ.get('GRADE_LINES_DIR'), os.environ.get('GRADE_NOTES_PATH')
    if not d or not npth: return False
    if _NFL is None:
        _NFL = {}
        for ln in open(npth):
            o = json.loads(ln)
            m = re.search(r'(?:^|\|)FinanceLeaseLiability=0:([-0-9.]+)', o.get('facts') or '')
            _NFL[o['cik']] = (o.get('fl_loc') == 'out' and m is not None and float(m.group(1)) > 0)
    p = os.path.join(d, f'{tk}.jsonl')
    if not os.path.exists(p): return False
    first = None; lease_line = False
    for ln in open(p):
        l = json.loads(ln); first = first or l
        if l.get('st') == 'BS' and re.search(r'(?i)finance lease|capital lease', (l.get('lab') or '') + ' ' + l['tag']) and not re.search(r'(?i)operating|right.of.use|RightOfUse', (l.get('lab') or '') + l['tag']): lease_line = True
    return bool(first) and not lease_line and _NFL.get(first['cik'], False)
_FL = {}
def face_fin_lease(tk):
    """True when the BS face prints a finance-lease liability line and no debt line already includes leases (needs GRADE_LINES_DIR)."""
    import json, re
    d = os.environ.get('GRADE_LINES_DIR')
    if not d: return False
    if tk not in _FL:
        p = os.path.join(d, f'{tk}.jsonl'); fl = incl = False
        if os.path.exists(p):
            for ln in open(p):
                l = json.loads(ln)
                if l.get('st') != 'BS' or str(l.get('pth')) not in ('0', '', 'None') or l.get('val') in (None, ''): continue
                lab = l.get('lab') or ''
                if l['tag'] in ('FinanceLeaseLiabilityNoncurrent', 'FinanceLeaseLiabilityCurrent', 'FinanceLeaseLiability') and not re.search(r'(?i)operating', lab): fl = True
                if re.search(r'CapitalLeaseObligations|FinanceLeaseLiabilityAndLongTermDebt|DebtCurrentAndFinanceLeaseLiability|LongTermDebtAndFinanceLease', l['tag']) or \
                   re.search(r'(?i)(debt|borrowings).{0,40}(and|including)\s+(finance|capital)\s+lease', lab): incl = True
        _FL[tk] = fl and not incl
    return _FL[tk]
def main(pdir, ddir, *only):
    rows = []; keyed = {}
    adj = {}
    ap = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'adjudications.csv')
    if os.path.exists(ap):
        for a in csv.DictReader(open(ap)): adj[(a['ticker'], a['data_point'])] = a['ruling']
    for dm in sorted(glob.glob(f'{ddir}/*-docmap-*.csv')):
        tk = os.path.basename(dm).split('-docmap')[0]
        if only and tk not in only: continue
        pf = f'{pdir}/{tk}-prediction.csv'
        pred = {r['data_point']: r for r in csv.DictReader(open(pf))} if os.path.exists(pf) else None
        K = {r['data_point']: r for r in csv.DictReader(open(dm))}
        def num(x):
            try: return float(x)
            except (TypeError, ValueError): return None
        o, rv, oi, cr = (num(K.get(d, {}).get('fy0_api')) for d in ('operating_expenses', 'revenue', 'operating_income', 'cost_of_revenue'))
        ko = K.get('operating_expenses', {}); kc = K.get('cost_of_revenue', {})
        cor_present = norm_status(kc.get('status')) in ('mapped', 'component_sum', 'combined')
        ce = 'costsandexpenses' in tagset(ko.get('tags'))
        incl = bool(o is not None and rv is not None and oi is not None and abs(o - (rv - oi)) <= max(abs(o) * 0.0005, 1) and cor_present)
        incl = incl or (ce and cor_present and o is not None and cr is not None and abs(o) > abs(cr))
        onestep = ce and not cor_present and norm_status(kc.get('status')) != 'out'
        keyed[tk] = {'cor': incl or onestep}
        for k in csv.DictReader(open(dm)):
            dp = k['data_point']
            if pred is None: rows.append(dict(ticker=tk, data_point=dp, result='no_prediction', error_class='', key_status=k['status'], pred_status='', key_tags=k['tags'], pred_tags='')); continue
            p = pred.get(dp)
            if p is None: rows.append(dict(ticker=tk, data_point=dp, result='wrong', error_class='missed', key_status=k['status'], pred_status='', key_tags=k['tags'], pred_tags='')); continue
            ev_txt = ((k.get('note') or '') + ' ' + (k.get('evidence_class') or '')).lower()
            # Dhairya 2026-11-13 (key-adjudication-2026-11-13.csv): hand only when the note carries 'check: hand'; unmarked tool rows -> 'tool'
            kev = 'hand' if 'check: hand' in (k.get('note') or '').lower() else ('machine' if 'machine-full-filing' in ev_txt else 'tool')
            if 'not hand-verified' in (k.get('note') or '').lower():
                rows.append(dict(ticker=tk, data_point=dp, result='key_unverified', error_class='key row marked not hand-verified by the reader', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            ks, ps = norm_status(k['status']), norm_status(p['status'])
            err = ''
            import re as _re
            rk = None
            if dp == 'interest_expense' and norm_status(k['status']) == 'mapped' and _re.search(r'(?i),\s*net\b|income|net interest|deductions', k.get('label') or ''):
                rk = 'net interest line keyed as gross interest expense (interest card; Dhairya SPGI caption ruling 2026-11-12)'
            if dp == 'depreciation_and_amortization' and norm_status(k['status']) == 'mapped' and _re.search(r'(?i)accretion|impair|nuclear', k.get('label') or ''):
                rk = 'D&A line incl. accretion/impairment keyed as D&A (capex-and-da card; Dhairya DUK ruling 2026-11-12)'
            kt = tagset(k['tags'])
            if dp == 'share_buybacks' and norm_status(k['status']) == 'mapped' and ({'paymentsrelatedtotaxwithholdingforsharebasedcompensation', 'proceedsfromrepurchaseofequity'} & kt):
                rk = 'withholding or non-repurchase tag keyed as buybacks (founder 2026-11-04 item 4)'
            if dp == 'dividends_paid' and norm_status(k['status']) == 'mapped' and ({'paymentsofdividendsminorityinterest', 'paymentsofdividendspreferredstockandpreferencestock', 'paymentstominorityshareholders'} & kt):
                rk = 'NCI or preferred dividends keyed as common dividends (shareholder-returns card)'
            if dp == 'accounts_receivable' and norm_status(k['status']) == 'mapped' and ({'interestreceivable', 'notesreceivablenet', 'financingreceivableexcludingaccruedinterestafterallowanceforcreditloss'} & kt):
                rk = 'interest/notes/financing receivables keyed as accounts receivable (sector-faces card)'
            if ks_raw(k) == 'not_presented' and norm_status(p['status']) == 'out':
                rk = 'data point outside the template group is OUT, not not_presented (Dhairya ruling 2026-11-13: SYF CA/CL; bank/insurer COGS, GP, R&D, inventory)'
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: ' + rk, key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if dp == 'sga_expense' and norm_status(k['status']) == 'mapped' and tagset(k['tags']) == {'generalandadministrativeexpense'} and \
                    any(_re.search(r'selling|marketing', t) for t in tagset(p['tags'])):
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: G&A alone keyed as SG&A while the face prints S&M (Dhairya 2026-11-13; MSFT incident)', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if dp == 'amortization_of_intangibles' and ks == 'not_presented' and norm_status(p['status']) == 'mapped' and (p.get('stmt') or '') == 'NOTE':
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: undimensioned consolidated full-year note fact present -> mapped stmt NOTE (fsn-line-to-concept.md AB; Dhairya 2026-11-13)', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if dp == 'depreciation_and_amortization' and ks == 'mapped' and tagset(k['tags']) == {'depreciationamortizationandaccretionnet'} and norm_status(p['status']) == 'combined':
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: DepreciationAmortizationAndAccretionNet includes accretion -> combined; a label never promotes (DUK ruling; doc 02)', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if dp == 'total_debt' and ks in ('mapped', 'component_sum', 'component sum') and 'lease' not in (k['tags'] or '').lower() and (face_fin_lease(tk) or note_fin_lease_outside_debt(tk)):
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: total_debt omits finance lease liabilities (printed, or in the notes with the XBRL location outside debt; founder 2026-11-04 item 5; Dhairya 2026-11-13)', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if rk and norm_status(p['status']) != 'mapped':
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: ' + rk, key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if (tk, dp) in adj and norm_status(k['status']) != norm_status(p['status']):
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: ' + adj[(tk, dp)], key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if dp == 'operating_expenses' and norm_status(k['status']) == 'mapped' and keyed.get(tk, {}).get('cor'):
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: opex total includes cost of revenue (Dhairya ruling 2026-11-12)', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if dp == 'shares_outstanding' and 'entitycommonstocksharesoutstanding' in tagset(k['tags']):
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: dei cover count (Dhairya ruling 2026-11-12)', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if ks != ps: err = 'status'
            elif ks in ('mapped', 'combined', 'component_sum', 'component_in_note') and tagset(k['tags']) != tagset(p['tags']): err = 'tag'
            rows.append(dict(key_evidence=kev, ticker=tk, data_point=dp, result='correct' if not err else 'wrong', error_class=err, key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags']))
    fields = ['key_evidence'] + [f for f in rows[0].keys() if f != 'key_evidence']
    for r in rows: r.setdefault('key_evidence', '')
    w = csv.DictWriter(sys.stdout, fieldnames=fields); w.writeheader(); w.writerows(rows)
    g = [r for r in rows if r['result'] in ('correct', 'wrong')]; n = len(g); k = sum(r['result'] == 'wrong' for r in g)
    print(f'graded {n} lines, wrong {k}, accuracy {100*(n-k)/max(n,1):.1f}%, error upper bound (CP 95%) {100*cp_upper(k,n):.1f}%; no_prediction {sum(r["result"]=="no_prediction" for r in rows)}; key_errors {sum(r["result"]=="key_error" for r in rows)}; key_unverified {sum(r["result"]=="key_unverified" for r in rows)}', file=sys.stderr)
if __name__ == '__main__':
    main(*sys.argv[1:])
