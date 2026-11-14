"""Structural resolver for every template data point (read-only), unchanged for 110 or 1,000 companies.
Core statement roles: resolve.py (tree positions); total_debt: total_debt.py; every other data point: rules/roles.csv
(position = statement + calc parent; the element family only ranks candidates; label demotes, a custom line is accepted
only when its own label names the role). Output: one row per filing x data point with value or reason."""
import csv, json, os, re, sys, collections
from decimal import Decimal as D
sys.path.insert(0, '.')
from resolve import parse, face, children, resolve, tol, note_facts, DPS as CORE_DPS
ROLES = list(csv.DictReader(open(os.environ.get('ROLES_CSV', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rules', 'roles.csv')))))
INSTANT_DPS = {'total_assets', 'total_liabilities', 'stockholders_equity', 'current_assets', 'current_liabilities', 'total_debt', 'cash_and_equivalents',
               'accounts_receivable', 'accounts_payable', 'inventory', 'goodwill', 'intangible_assets', 'ppe_net', 'shares_outstanding', 'deposits', 'loans_net'}
import resolve_bs, resolve_cf
FAMILY_DPS = set(resolve_bs.FAMILY) | {'current_assets', 'current_liabilities'} | set(resolve_cf.DPS)
POLARITY = {r['data_point']: r for r in csv.DictReader(open(os.environ.get('POLARITY_CSV', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rules', 'polarity.csv'))))}
def apply_polarity(rows):
    """Ruling 2026-11-14: every concept has one sign. An expense (or payment) read from a single element whose filer polarity
    is reversed (DIS InterestExpense -1,973; V InterestIncomeExpenseNet printed 'Interest expense') is normalised to the
    concept's sign; the flip is recorded in flags (polarity_flip) and the why. Component sums keep their computed sign."""
    for r in rows:
        p = POLARITY.get(r['data_point'])
        v = r.get('value')
        if not p or p['normalise'] != 'Y' or v is None or r['status'] != 'mapped': continue
        if p['sign'] == '+' and D(v) < 0:
            r['value'] = -D(v)
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'polarity_flip') if x)
            r['why'] = (r.get('why') or '') + f"; polarity: the filer reports {v} on an element of the opposite sign; {r['data_point']} is positive (rules/polarity.csv), value normalised"
    return rows
EXT = {'ap': {}, 'ar': {}, 'cf': {}, 'pz': {}, 'lt': {}, 'cor': {}, 'gp': {}}   # derived from the standard extract (tools/standard_inputs.py); the side files below stay the fallback
def fill_printed_zero_and_comparative(rows, td):
    """Rulings 2026-11-14 (Dhairya). (a) A line printed on the own face with a dash or zero is served as 0, flag printed_zero
    with its R:line (EXT['pz'] = standard_inputs.printed_zero over the extract's zlines: the line is on the face, no own-period fact
    exists in any dimension, the line has values in other columns); a line absent from the face stays not_presented. (b) A value the
    next 10-K prints in its comparative column fills a cell the own filing does not present: column=comparative, that filing's accession
    and R page (EXT['cf'] = standard_inputs.comparative_fill over the extract's cvals; total_debt from total_debt's comparative column)."""
    pz = dict(EXT.get('pz', {}))
    cf = {}
    for (own_a, dp), c in EXT.get('cf', {}).items():   # loc = where the later filing itself resolved the data point
        nodes_loc = next((x.get('nodes') or '' for x in rows if x['accession'] == c['accession'] and x['data_point'] == dp), '')
        m = re.search(r'\[(R[^\]]*|NOTE|BS parenthetical[^\]]*)\]', nodes_loc)
        cf[(own_a, dp)] = dict(c, loc=m.group(1) if m else 'NOTE')
    nxt = {}
    by = collections.defaultdict(list)
    for (a, col), t in td.items():
        if col == 'comparative': by[t['ticker']].append(t)
    for r in rows:
        if r['status'] != 'not_presented': continue
        k = (r['accession'], r['data_point'])
        if k in pz:
            z = pz[k]
            r.update(status='mapped', value=D(0), tags=z['tag'], nodes=f"{z['tag']}=0 [{z['r_line']}]",
                     why=f"the own face prints '{z['label']}' with a dash or zero for this period (ruling 2026-11-14: printed dash = 0)")
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'printed_zero') if x)
        elif k in cf:
            c = cf[k]; v = D(c['value'])
            r.update(status='mapped', value=v, tags=c['tag'], accession=c['accession'], column='comparative',
                     nodes=f"{c['tag']}={c['value']} [{c['loc']} of {c['accession']}, {c.get('window') or 'FY-1'} column]",
                     why=f"the own filing does not present the line; a later 10-K prints it in its {c.get('window') or 'FY-1'} column (rulings 2026-11-14: comparative fill from the latest face-eligible filing)")
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'comparative_fill', 'printed_zero' if v == 0 else '') if x)
        elif r['data_point'] == 'total_debt':
            t = next((t for t in by.get(r['ticker'], []) if t['period_end'] == r['period_end'] and t['status'] in ('mapped', 'component_sum')), None)
            if t:
                r.update(status=t['status'], value=D(t['value']), tags=t['tags'], accession=t['accession'], column='comparative', nodes=t['parts'] + f" [comparative column of {t['accession']}]",
                         why='total_debt rule on the next 10-K comparative column (the own filing presents no debt line; ruling 2026-11-14)')
                r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'comparative_fill', 'printed_zero' if D(t['value']) == 0 else '') if x)
    return rows
COR_MX_LB = re.compile(r'(?i)^(total )?costs? of (revenues?|sales|goods sold|goods and services sold)$')
COR_ANY_LB = re.compile(r'(?i)\bcosts? of (revenues?|sales|goods)')
AP_RELATED = re.compile(r'^(AccountsPayableRelatedPartiesCurrent|DueToRelatedPartiesCurrent)$')
AR_RELATED = re.compile(r'^(DueFromRelatedPartiesCurrent|DueFromRelatedParties|DueFromAffiliateCurrent|AccountsReceivableRelatedPartiesCurrent|RelatedPartyTransactionDueFromToRelatedPartyCurrent|NotesAndLoansReceivableRelatedPartiesCurrent)$')
def apply_ar_related(rows, filings):
    """Ruling 2026-11-14 (AR mirrors AP): accounts_receivable = the trade line + a current face line whose own label names a
    receivable from related parties or affiliates (COP, PSX, TMUS, DE, AMD 2020-22), flag ar_related_sum; member splits
    (EXT['ar'] = standard_inputs.related_splits: COP 2023-24, GEV, DELL 2024). A mixed line ('Prepayment and receivables', AMD 2017-19), an 'other receivables
    (including related parties)' line (SCCO) and 'Due from related party' without 'receivable' (DELL) are not added."""
    split = dict(EXT.get('ar', {}))
    F = {f['a']: f for f in filings}
    for r in rows:
        if r['data_point'] != 'accounts_receivable': continue
        a = r['accession']
        if a in split and r['status'] in ('mapped', 'not_presented'):   # member-only face lines leave the row not_presented (GEV, DELL 2024)
            s = split[a]; n, rel = D(s['nonrelated']), D(s['related'])
            r.update(status='component_sum', value=n + rel, tags=f"{s['tag']}+{s['tag']}",
                     nodes=f"{s['tag']}[NonrelatedParty]={n} [face line]; {s['tag']}[RelatedParty]={rel} [face line]",
                     why='the face prints receivables from third parties and from related parties on two lines (RelatedPartyTransactionsByRelatedPartyAxis members): sum (ruling 2026-11-14)')
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'ar_related_sum') if x)
            continue
        if a not in F or r['status'] != 'mapped' or r['value'] is None: continue
        L, _ = parse(F[a])
        rel = [l for l in face(L, 'BS') if l['val'] and AR_RELATED.match(l['tag']) and re.search(r'(?i)receivable', l['lb'] or '') and re.search(r'(?i)related part|affiliate', l['lb'] or '') and not re.search(r'(?i)prepay|other|noncurrent|long-term', l['lb'] or '')]
        if rel:
            l = rel[0]
            r['nodes'] = (r.get('nodes') or '').split(' | why')[0] + f"; {l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]"
            r.update(status='component_sum', value=D(r['value']) + l['val'], tags=(r.get('tags') or '') + '+' + l['tag'],
                     why=f"accounts receivable = the trade line plus '{l['lb']}' (ruling 2026-11-14: AR mirrors AP)")
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'ar_related_sum') if x)
    return rows
def apply_cost_and_opex(rows, filings):
    """(1) cost_of_revenue printed as product and service lines that carry only ProductOrServiceAxis member facts (DIS, GE,
    TMUS, VZ): the sum of the members (EXT['cor'] = standard_inputs.product_service_cor). (2) operating_expenses with no node in the tree: from the printed
    totals, gross profit - operating income (PEP: OI's calc tree skips GP) or total costs and expenses - cost of revenue (QCOM:
    the itemized lines do not tie because 'Other' is filed with the wrong sign). Both are the lines between the top line and OI."""
    split = EXT.get('cor', {})
    F = {f['a']: f for f in filings}
    by = {(r['accession'], r['data_point']): r for r in rows}
    for r in rows:
        if r['data_point'] == 'cost_of_revenue' and r['status'] in ('not_presented', 'no_role') and r['accession'] in split:
            x = split[r['accession']]; p, sv = D(x['product']), D(x['service'])
            t = x.get('tag') or 'CostOfGoodsAndServicesSold'
            r.update(status='component_sum', value=p + sv, tags=f'{t}+{t}',
                     nodes=f"{t}[Product]={p} [IS face line]; {t}[Service]={sv} [IS face line]",
                     why='the income statement prints the cost of products and the cost of services as separate lines carrying ProductOrServiceAxis members only: sum')
            r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'cor_member_sum') if y)
    for r in rows:   # a matrix income statement (MAR): the cost line carries ProductOrService column members only (ruling 2026-11-14)
        x = EXT.get('cor_mx', {}).get(r['accession'])
        if r['data_point'] != 'cost_of_revenue' or r['status'] not in ('not_presented', 'no_role') or not x or r['accession'] not in F: continue
        L, _ = parse(F[r['accession']]); isf = face(L, 'IS')
        cl = next((l for l in isf if l['tag'] == x['tag']), None)
        ce = next((l for l in isf if l['tag'] in ('CostsAndExpenses', 'OperatingCostsAndExpenses', 'OperatingExpenses') and l['val'] is not None and cl and l['ln'] > cl['ln']), None)
        rv = max((l['ln'] for l in isf if l['val'] is not None and cl and l['ln'] < cl['ln'] and re.match(r'^Revenue', l['tag'])), default=None)
        if not (cl and ce and rv is not None): continue
        # the members are columns of one cost-of-revenue line (MAR), not rows of different costs filed under one element: the line's own
        # label names cost of revenue (DE 'Costs and expenses' = cost of sales + other operating expenses, NEM 'Costs applicable to sales'
        # = + reclamation + exploration are rows) and no other face line names a cost of revenue (AT&T 'Other cost of revenues')
        if not COR_MX_LB.match((cl['lb'] or '').strip()) or any(l is not cl and COR_ANY_LB.search(l['lb'] or '') for l in isf if not l['tag'].endswith('Abstract')): continue
        others = [l for l in isf if rv < l['ln'] < ce['ln'] and l is not cl and l['val'] is not None and not l['tag'].endswith('Abstract')]
        tot = D(x['total']); chk = tot + sum((l['val'] for l in others), D(0))
        if abs(chk - ce['val']) > tol(ce['val'], tot, *[l['val'] for l in others]): continue
        r.update(status='component_sum', value=tot, tags='+'.join([x['tag']] * len(x['members'])),
                 nodes='; '.join(f"{x['tag']}[{k}]={v} [IS face line R{cl['rep']}.htm:{cl['ln']}]" for k, v in x['members'].items()),
                 why=f"the income statement is a matrix: '{cl['lb']}' carries only ProductOrService column members; their sum, which with the other cost lines ties to '{ce['lb']}' {ce['val']} (ruling 2026-11-14)")
        r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'cor_member_sum') if y)
    for r in rows:
        if r['data_point'] != 'operating_expenses' or r['status'] not in ('not_presented', 'no_role') or r['accession'] not in F: continue
        if 'no expense line between' in (r.get('why') or ''): continue   # LMT: only other income sits between GP and OI; GP - OI is not an expense
        L, _ = parse(F[r['accession']])
        isf = {l['tag']: l for l in face(L, 'IS') if l['val'] is not None}
        gp, oi = isf.get('GrossProfit'), isf.get('OperatingIncomeLoss')
        ce = isf.get('CostsAndExpenses') or isf.get('CostsAndExpensesAbstract')
        cor = by.get((r['accession'], 'cost_of_revenue'))
        if gp and oi:
            v = gp['val'] - oi['val']; nodes = f"GrossProfit={gp['val']} [R{gp['rep']}.htm:{gp['ln']}]; -OperatingIncomeLoss={oi['val']} [R{oi['rep']}.htm:{oi['ln']}]"; how = 'gross profit - operating income (both printed)'
        elif ce and cor and cor['status'] in ('mapped', 'component_sum') and cor['value'] is not None and oi:
            v = ce['val'] - D(cor['value']); nodes = f"CostsAndExpenses={ce['val']} [R{ce['rep']}.htm:{ce['ln']}]; -cost_of_revenue={cor['value']}"; how = 'total costs and expenses - cost of revenue (both printed)'
        else:
            continue
        r.update(status='component_sum', value=v, tags='printed totals', nodes=nodes, why=f'operating expenses = the lines between the top line and operating income, from {how}')
        r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'opex_from_printed_totals') if y)
    return rows
def derive_gross_profit(rows):
    """Ruling C1 (Dhairya 2026-11-14): gross profit not printed, revenue and cost of revenue printed and resolved in the same
    filing -> DERIVED revenue - cost of revenue (derived_not_printed). An unpresented GrossProfit fact of the same filing
    (EXT['gp'] = standard_inputs.gross_profit_facts) is recorded in calc_check; a difference makes the cell DISAGREE until a reader looks. Cost of revenue
    not resolvable (ORCL: interleaved cost lines) -> gross profit stays not_presented."""
    corr = EXT.get('gp', {})
    by = {(r['accession'], r['data_point']): r for r in rows if (r.get('column') or 'own') == 'own'}
    for r in rows:
        if r['data_point'] != 'gross_profit' or r['status'] != 'not_presented' or (r.get('column') or 'own') != 'own': continue
        rev, cor = by.get((r['accession'], 'revenue')), by.get((r['accession'], 'cost_of_revenue'))
        if not (rev and cor and rev['status'] in ('mapped', 'component_sum') and cor['status'] in ('mapped', 'component_sum')
                and rev['value'] is not None and cor['value'] is not None and (cor.get('column') or 'own') == 'own'): continue
        v = D(rev['value']) - D(cor['value'])
        r.update(status='derived', value=v, tags='revenue-cost_of_revenue', nodes=f"revenue={rev['value']}; -cost_of_revenue={cor['value']}",
                 why='the income statement prints no gross profit; revenue and cost of revenue are printed in the same filing: revenue - cost of revenue (ruling C1)')
        r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'derived_not_printed') if x)
        if r['accession'] in corr:
            g = corr[r['accession']]; ok = abs(g - v) <= tol(g, v)
            r['calc_check'] = ';'.join(x for x in (r.get('calc_check', ''), f"GP corroboration: unpresented GrossProfit fact {g} {'ok' if ok else 'DISAGREE'}") if x)
            if not ok: r['flags'] += ';gp_corroboration_disagree'
    return rows
OTHER_BEYOND = re.compile(r'(?i)\b(and|&|,)\s+other\b|\bothers?\s*$')
WITHIN = {'revenue': r'other (operating )?(revenues?|sales)', 'intangible_assets': r'other intangible', 'ppe_net': r'other property',
          'capex': r'other property', 'depreciation_and_amortization': r'other amortization', 'goodwill': r'other intangible'}
II_BEYOND_TAG = re.compile(r'^(InvestmentIncomeNet|InvestmentIncomeInterestAndDividend|InterestAndDividendIncome\w*|InvestmentIncomeNonoperating)$')
def apply_label_beyond(rows, filings):
    """Ruling 2026-11-14 (Dhairya; MSFT certified by Ritwik): a line whose label (or, for a note fact, whose element) names
    items beyond the data point is combined: 'Depreciation, amortization, and other' (D&A), 'Interest and dividends income' /
    'Investment income' (interest income), 'Receivables - trade and other', 'Repurchase of ... shares and other', 'Total
    revenues and other income'. 'Other X' where X is the data point itself is within it ('Sales and other operating revenues',
    'Trademarks and other intangible assets', 'Parks, resorts and other property', 'other amortization')."""
    F = {f['a']: f for f in filings}
    cache = {}
    for r in rows:
        dp = r['data_point']
        if r['status'] != 'mapped' or (r.get('column') or 'own') != 'own' or dp in ('other_income_expense_net', 'comprehensive_income'): continue
        nodes = r.get('nodes') or ''
        m = re.match(r'-?(\w+)=[-\d.]+ \[R(\d+)(?:\.htm)?:(\d+)\]', nodes)
        lb = None
        if m and r['accession'] in F:
            if r['accession'] not in cache: cache[r['accession']] = parse(F[r['accession']])[0]
            lb = next((l['lb'] or '' for l in cache[r['accession']] if l['tag'] == m.group(1) and l['ln'] == int(m.group(3))), None)
        beyond = None
        if lb is not None:
            if OTHER_BEYOND.search(lb) and not (dp in WITHIN and re.search(WITHIN[dp], lb, re.I)): beyond = f"its label '{lb}' names other items"
            elif dp == 'interest_income' and re.search(r'(?i)dividend|investment(?! income, interest)|and other', lb): beyond = f"its label '{lb}' names more than interest"
        elif dp == 'interest_income':
            t = re.match(r'-?(\w+)=', nodes)
            if t and II_BEYOND_TAG.match(t.group(1)): beyond = f"the element {t.group(1)} reports investment income (interest with dividends and other items)"
        if beyond and dp in ('accounts_receivable', 'cf_ar_change'):
            # AR single-line ruling wins: 'trade and other' is combined only when the face also prints a separate trade line
            L = cache.get(r['accession']) or (parse(F[r['accession']])[0] if r['accession'] in F else [])
            bs = [l for l in face(L, 'BS') if l['val'] is not None]
            trade = [l for l in bs if re.search(r'(?i)^(trade |customer )?(accounts )?receivables?\b|accounts receivable|trade receivables?', l['lb'] or '')
                     and not re.search(r'(?i)\bother\b|related|affiliate|financ|notes?\b|unbilled|income tax', l['lb'] or '')]
            if not trade: beyond = None
        if beyond and dp == 'revenue':
            # ruling 3: the sales / operating-revenue lines printed above 'Total revenues and other income' are revenue
            L = cache.get(r['accession']) or parse(F[r['accession']])[0]
            isf = face(L, 'IS'); ln = int(m.group(3)) if m else 10 ** 6
            sl = [l for l in isf if l['val'] is not None and l['ln'] < ln and re.search(r'(?i)sales|revenues?', l['lb'] or '')
                  and not re.search(r'(?i)other income|equity|gain|interest', l['lb'] or '') and not re.search(r'(?i)^total', l['lb'] or '')]
            if sl:
                r.update(status='mapped' if len(sl) == 1 else 'component_sum', value=sum(l['val'] for l in sl), tags='+'.join(l['tag'] for l in sl),
                         nodes='; '.join(f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]" for l in sl),
                         why="the face prints sales / operating-revenue lines above 'Total revenues and other income': those lines are revenue (ruling 3)")
                r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'revenue_above_other_income') if x)
                continue
        if beyond:
            r.update(status='combined', value=None, why=f"the line holding the role is wider than {dp}: {beyond} (ruling 2026-11-14: a line whose label names items beyond the data point is combined)")
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'label_beyond') if x)
    return rows
def apply_ap_related(rows, filings):
    """Ruling 2026-11-14 (Dhairya): accounts_payable is the sum of every accounts-payable line on the face, third-party and
    related-party (component_sum). A separate current line whose own label names a payable to related parties
    (AccountsPayableRelatedPartiesCurrent / DueToRelatedPartiesCurrent: AMD, WDC, COP, PSX) is added; a face split by the
    RelatedPartyTransactionsByRelatedPartyAxis members (COP 2023-24, PSX 2023-25, SNDK) is summed (EXT['ap'] = standard_inputs.related_splits).
    'Due to related party' without 'payable' (DELL) and a line already 'including related parties' (SCCO) are not added."""
    split = dict(EXT.get('ap', {}))
    F = {f['a']: f for f in filings}
    for r in rows:
        if r['data_point'] != 'accounts_payable': continue
        a = r['accession']
        if a in split and r['status'] in ('mapped', 'not_presented', 'component_sum'):
            s = split[a]; n, rel = D(s['nonrelated']), D(s['related'])
            r.update(status='component_sum', value=n + rel, tags='AccountsPayableCurrent+AccountsPayableCurrent',
                     nodes=f"AccountsPayableCurrent[NonrelatedParty]={n} [face line]; AccountsPayableCurrent[RelatedParty]={rel} [face line]",
                     why='the face prints accounts payable to third parties and to related parties on two lines (members of RelatedPartyTransactionsByRelatedPartyAxis): sum (ruling 2026-11-14)')
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'ap_related_sum') if x)
            continue
        if r['status'] != 'mapped' or a not in F: continue
        L, _ = parse(F[a])
        rel = [l for l in face(L, 'BS') if l['val'] and AP_RELATED.match(l['tag']) and re.search(r'(?i)payable', l['lb'] or '') and re.search(r'(?i)related part', l['lb'] or '')]
        if rel and not re.search(r'(?i)including related', r.get('nodes', '')):
            l = rel[0]
            r['nodes'] = (r.get('nodes') or '').split(' | why')[0] + f"; {l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]"
            r.update(status='component_sum', value=D(r['value']) + l['val'], tags=(r.get('tags') or '') + '+' + l['tag'],
                     why=f"accounts payable = every accounts-payable line on the face: the trade line plus '{l['lb']}' (ruling 2026-11-14)")
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'ap_related_sum') if x)
    return rows
def family_rows(f, notes, raw):
    """Family modules (tools/resolve_bs.py, tools/resolve_cf.py): position logic per family; rows replace the role rows of their data points."""
    out = {}
    bsraw = '~'.join(x for x in (raw or '').split('~') if x.count('|') == 2 and x.split('|')[1] == '0')
    for dp, r in resolve_bs.resolve_family(f, resolve_bs.notes_for(bsraw)).items():
        out[dp] = dict(status=r['status'], tags=r.get('tags', ''), value=r['value'], r_page='', nodes=r.get('nodes', ''), why=r['why'], source='bs_family', flags=';'.join(x for x in (r.get('rule', ''), r.get('flags', '')) if x))
    for dp, r in resolve_cf.resolve_cf(f, notes).items():
        out[dp] = dict(status=r['status'], tags=r.get('tags', ''), value=r['value'], r_page='', nodes=r.get('nodes', ''), why=r['why'], source='cf_family', flags='')
    return out
def descendants(arcs, root, onface):
    out, stack = set(), [root]
    while stack:
        p = stack.pop()
        for c, w in (children(arcs, p, onface) or []):
            if c not in out: out.add(c); stack.append(c)
    return out
def role(f, L, arcs, notes, R):
    dp, stmt = R['data_point'], R['stmt']
    alts = [a.split('+') for a in R['alternatives'].split('|') if a]
    comb = [t for t in R['combined_if'].split('|') if t]
    if stmt != 'NOTE':
        fl = face(L, stmt)
        by = {}
        for l in fl:
            if l['val'] is not None: by.setdefault(l['tag'], l)
        scope = None
        if R['parent'] and R['parent'] in by and R['parent'] in arcs:
            scope = descendants(arcs, R['parent'], by)
        def ok(t): return t in by and (scope is None or t in scope or not scope)
        for parts in alts:
            if all(ok(t) for t in parts):
                ls = [by[t] for t in parts]
                return dict(status='mapped' if len(ls) == 1 else 'component_sum', tags='+'.join(parts), value=sum(l['val'] for l in ls), nodes='; '.join(f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]" for l in ls),
                            r_page='+'.join(sorted({f"R{l['rep']}.htm" for l in ls})), why=f"{stmt} face {'+'.join(parts)}" + (f" under {R['parent']}" if scope else ''))
        for t in comb:
            if ok(t):
                if dp in ('interest_income', 'interest_expense') and R['note_ok'] == 'Y':   # per-series ruling: the gross note fact beside a combined face line (KLAC)
                    n = next(((p, notes.get((p, 4))) for parts in alts for p in parts if len(parts) == 1 and notes.get((p, 4)) is not None), None)
                    if n:
                        return dict(status='mapped', tags=n[0], value=n[1], r_page='NOTE', nodes=f"{n[0]}={n[1]} [NOTE]",
                                    why=f"{stmt} face prints only the combined line {t} '{by[t]['lb']}'; the gross figure is the undimensioned note fact {n[0]} (per-series ruling)")
                return dict(status='combined', tags=t, value=by[t]['val'], r_page=f"R{by[t]['rep']}.htm", why=f"{stmt} face prints only the combined line {t} '{by[t]['lb']}'")
        if R['custom_label']:
            cl = [l for l in fl if l['custom'] and l['val'] is not None and re.search(R['custom_label'], l['lb'], re.I) and (scope is None or l['tag'] in scope or not scope)]
            if len(cl) == 1:
                l = cl[0]
                return dict(status='mapped', tags=l['tag'], value=l['val'], r_page=f"R{l['rep']}.htm", why=f"{stmt} face custom line whose own label names the role: '{l['lb']}'")
    if R['note_ok'] == 'Y' or stmt == 'NOTE':
        # instants (balance-sheet items) read the note fact at qtrs 0; durations at qtrs 4
        q = 0 if (stmt == 'BS' or dp in INSTANT_DPS) else 4
        for parts in alts:
            vs = [notes.get((t, q)) for t in parts]
            if all(v is not None for v in vs):
                return dict(status='mapped' if len(parts) == 1 else 'component_sum', tags='+'.join(parts), value=sum(vs), r_page='NOTE', nodes='; '.join(f"{t}={v} [NOTE]" for t, v in zip(parts, vs)),
                            why=f"undimensioned consolidated fact {'+'.join(parts)} at the filing's own column (§AG)")
    return dict(status='not_presented', tags='', value=None, r_page='',
                why=f"no {dp} line on the {stmt if stmt != 'NOTE' else 'statements'} of this filing" + (' nor an undimensioned note fact' if R['note_ok'] == 'Y' or stmt == 'NOTE' else ''))
def run(filings, notefacts, tick, td_rows):
    out = []
    for f in filings:
        tk = tick.get(f['cik'].zfill(10))
        if not tk: continue
        L, arcs = parse(f)
        notes = note_facts(notefacts.get(f['a']))
        core, checks = resolve(f)
        chk = ';'.join(checks)
        for dp in CORE_DPS:
            r = core.get(dp)
            if dp == 'mezzanine_and_nci': continue
            if r: out.append(dict(ticker=tk, cik=f['cik'], accession=f['a'], period_end=f['p'], data_point=dp, status=r['status'], tags=r['tags'], value=r['value'], r_page='+'.join(sorted({'R' + x.split(':')[0][1:] + '.htm' for x in r['line'].split(';') if x.startswith('R')})), nodes=r.get('nodes') or ('; '.join(f"{t} [{x}]" for t, x in zip(r['tags'].split('+'), r['line'].split(';'))) if r['tags'] else ''), why=r['path'], source='core', calc_check=chk, flags=r.get('note', '')))
            else: out.append(dict(ticker=tk, cik=f['cik'], accession=f['a'], period_end=f['p'], data_point=dp, status='no_role', tags='', value=None, r_page='', nodes='', why='no node holds this role on the face/calc tree', source='core', calc_check=chk, flags=''))
        t = td_rows.get((f['a'], 'own'))
        if t: out.append(dict(ticker=tk, cik=f['cik'], accession=f['a'], period_end=f['p'], data_point='total_debt', status=t['status'], tags=t['tags'], value=D(t['value']) if t['value'] else None, r_page=t['r_pages'], nodes=t['parts'], why='total_debt rule (tools/total_debt.py)', source='total_debt', calc_check=chk, flags=t['flags']))
        corestat = {o['data_point']: o for o in out if o['accession'] == f['a'] and o['source'] == 'core'}
        fam = family_rows(f, notes, notefacts.get(f['a']))
        for dp in ('current_assets', 'current_liabilities'):
            if dp in fam and corestat.get(dp, {}).get('status') in ('no_role', None):
                corestat[dp].update(status=fam[dp]['status'], value=None, why=fam[dp]['why'], source='bs_family')
        for R in ROLES:
            if R.get('fallback') == 'Y':
                c = corestat.get(R['data_point'])
                if c is None or c['status'] != 'no_role': continue      # the tree decided; the role rule is only a fallback
                r = role(f, L, arcs, notes, R)
                if r['status'] == 'not_presented': continue
                c.update(dict(status=r['status'], tags=r['tags'], value=r['value'], r_page=r['r_page'], nodes=r.get('nodes', r['tags']), why='FALLBACK (no calc node): ' + r['why'], source='core_fallback'))
                continue
            if R['data_point'] in fam:
                r = dict(fam.pop(R['data_point'])); src = r.pop('source'); fl_ = r.pop('flags')
                out.append(dict(ticker=tk, cik=f['cik'], accession=f['a'], period_end=f['p'], data_point=R['data_point'], source=src, calc_check=chk, flags=fl_, **r))
                continue
            r = role(f, L, arcs, notes, R)
            r.setdefault('nodes', f"{r['tags']} [{r['r_page']}]" if r['tags'] else '')
            out.append(dict(ticker=tk, cik=f['cik'], accession=f['a'], period_end=f['p'], data_point=R['data_point'], source='roles', calc_check=chk, flags='', **r))
        for dp, r in fam.items():   # family data points with no roles.csv row (e.g. intangible_assets)
            if dp in ('current_assets', 'current_liabilities'): continue
            r = dict(r); src = r.pop('source'); fl_ = r.pop('flags')
            out.append(dict(ticker=tk, cik=f['cik'], accession=f['a'], period_end=f['p'], data_point=dp, source=src, calc_check=chk, flags=fl_, **r))
        # no calc arcs under the balance sheet: total liabilities from the face by position (the printed Liabilities total),
        # else DERIVED = L&SE - equity incl. NCI (or parent equity + NCI) - temporary/redeemable equity, all from this face (C2)
        tl = corestat.get('total_liabilities')
        if tl is not None and tl['status'] == 'no_role':
            bs = face(L, 'BS'); bb = {}
            for l in bs:
                if l['val'] is not None: bb.setdefault(l['tag'], l)
            if 'Liabilities' in bb:
                l = bb['Liabilities']
                tl.update(status='mapped', tags='Liabilities', value=l['val'], r_page=f"R{l['rep']}.htm", nodes=f"Liabilities={l['val']} [R{l['rep']}:{l['ln']}]", why='FALLBACK (no calc arcs): the printed Liabilities total between the asset total and equity', source='core_fallback')
            elif 'LiabilitiesAndStockholdersEquity' in bb:
                lse = bb['LiabilitiesAndStockholdersEquity']
                eq = [bb[t] for t in ('StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',) if t in bb] or [bb[t] for t in ('StockholdersEquity', 'MinorityInterest') if t in bb]
                mez = [l for t, l in bb.items() if re.match(r'^(TemporaryEquity|RedeemableNoncontrollingInterest)\w*(CarryingAmount|Value)\w*$', t)]
                if eq:
                    v = lse['val'] - sum(l['val'] for l in eq + mez)
                    tl.update(status='derived', tags='+'.join(l['tag'] for l in eq + mez), value=v, r_page=f"R{lse['rep']}.htm",
                              nodes=f"LiabilitiesAndStockholdersEquity={lse['val']} [R{lse['rep']}:{lse['ln']}]; " + '; '.join(f"-{l['tag']}={l['val']} [R{l['rep']}:{l['ln']}]" for l in eq + mez),
                              why='FALLBACK (no calc arcs, total liabilities not printed): L&SE minus the printed equity side (C2)', source='core_fallback')
        ni = corestat.get('net_income')
        if ni is not None and ni['status'] == 'no_role':
            isf = {l['tag']: l for l in face(L, 'IS') if l['val'] is not None}
            if 'ProfitLoss' in isf and not any('Noncontrolling' in t for t in isf):
                l = isf['ProfitLoss']
                ni.update(status='mapped', tags='ProfitLoss', value=l['val'], r_page=f"R{l['rep']}.htm", nodes=f"ProfitLoss={l['val']} [R{l['rep']}:{l['ln']}]", why='FALLBACK: the IS ends at ProfitLoss and prints no NCI line, so ProfitLoss is the parent net income', source='core_fallback')
        # rule (C1/S12 generalised): a statement role with no node on a filing whose statement was read is a reason,
        # not a gap: gross profit, opex, operating income, cost of revenue not printed -> not_presented
        isread = any(o['data_point'] == 'revenue' and o['status'] in ('mapped', 'component_sum') for o in out if o['accession'] == f['a'])
        for o in out:
            if o['accession'] == f['a'] and o['status'] == 'no_role' and isread and o['data_point'] in ('gross_profit', 'operating_expenses', 'operating_income', 'cost_of_revenue'):
                o.update(status='not_presented', why=f"the income statement of this filing has no {o['data_point']} node (no line holds the role in the filer's tree; rulings C1/S12)", flags='rule:not_printed_statement_role')
    return out
if __name__ == '__main__':
    filings = json.load(open('filings.json')); notefacts = json.load(open('notefacts.json'))
    tick = {r[1]: r[0] for r in csv.reader(open('tk.csv'))}
    import standard_inputs, total_debt
    def _read(n): p_ = os.environ.get(n.upper().replace('.', '_'), n); return json.load(open(p_)) if os.path.exists(p_) else {}
    memberfacts, compfacts, zlines, clines = _read('memberfacts.json'), _read('compfacts.json'), _read('zlines.json'), _read('clines.json')
    # total_debt from the standard extract (own + comparative columns) and the committed instance evidence (total_debt.load_evidence)
    td = {(r['accession'], r['column']): r for r in total_debt.total_debt_all(filings, standard_inputs.debt_vals(filings, notefacts, compfacts), tick, os.environ.get('INSTANCE_CACHE', 'instances'))}
    # member-only face facts (_member-face-facts-2026-11-14.csv): a DPS, share count or CI printed on the face whose only own-period
    # fact carries one equity-statement column member (EquityComponents=RetainedEarnings / CommonStock ...) is the consolidated value;
    # share counts equal to shares issued (VZ, C, TMO) were rejected in the file. They enter as note facts, lineage keeps the member
    MF = {}
    EXT['lt'] = standard_inputs.amortization_location_total(notefacts, memberfacts)
    EXT['cor'] = standard_inputs.product_service_cor(notefacts, memberfacts)
    EXT['cor_mx'] = {a: x for a, x in standard_inputs.cost_member_sums(notefacts, memberfacts).items() if a not in EXT['cor']}
    EXT['gp'] = standard_inputs.gross_profit_facts(notefacts)
    for m in standard_inputs.member_facts(notefacts, memberfacts, standard_inputs.class_share_filings(filings)):   # the standard extract first
        notefacts[m['accession']] = '~'.join(x for x in (notefacts.get(m['accession']), f"{m['tag']}|{m['qtrs']}|{m['value']}") if x)
        MF[(m['accession'], m['tag'])] = m['member']
    EXT['ap'] = standard_inputs.related_splits(memberfacts, r'AccountsPayable(Current|TradeCurrent|CurrentAndNoncurrent)')   # the AP role elements; payable+accrued (GEV) is combined, not AP
    EXT['ar'] = standard_inputs.related_splits(memberfacts, r'(AccountsAndNotesReceivableNet|AccountsReceivable\w*|Receivables\w*)')
    # a face whose values all carry one LegalEntity member (combined filings, ruling 2026-11-14): the filer's member fills the face;
    # a co-registrant's (CEG FY2021: the predecessor Constellation Energy Generation LLC) or several members is a reason
    LE = standard_inputs.legal_entity_faces(_read('lentity.json'))
    PRED = {}
    for i, f in enumerate(filings):
        if f['a'] not in LE: continue
        x = LE[f['a']]
        if x and not x['coregistrant']: filings[i] = standard_inputs.fill_face_values(f, x['facts'])
        else: PRED[f['a']] = x
    rows = run(filings, notefacts, tick, td)
    for r in rows:
        if r['accession'] in PRED and r['status'] in ('no_role', 'not_presented'):
            x = PRED[r['accession']]
            r.update(status='not_presented', why=f"statements of a predecessor co-registrant ({'LegalEntity ' + x['member'] if x else 'several LegalEntity members'}): the face carries no value of the filer (ruling 2026-11-14)")
            r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'coregistrant_face') if y)
    import resolve_is
    rows = resolve_is.apply(rows, filings, notefacts, tick)  # IS family (resolve_is.py) replaces its six data points where decisive
    rows = apply_cost_and_opex(rows, filings)
    rows = apply_ap_related(rows, filings)
    rows = apply_ar_related(rows, filings)
    EXT['cf'] = standard_inputs.comparative_fill(rows, compfacts, INSTANT_DPS)
    EXT['pz'] = {k: dict(v, accession=k[0], data_point=k[1]) for k, v in standard_inputs.printed_zero(rows, zlines, {r['data_point']: (r['stmt'], [x for x in (r.get('alternatives') or '').split('|') if x]) for r in ROLES}).items()}
    rows = fill_printed_zero_and_comparative(rows, td)
    rows = derive_gross_profit(rows)
    rows = apply_polarity(rows)  # one sign per concept (rules/polarity.csv)
    # a face line that is only part of a total the filing reports by income-statement location (CSCO prints the opex part of
    # intangible amortization; the cost-of-sales part is a member): the location total (standard_inputs.amortization_location_total)
    LT = {}
    for a_, x in EXT.get('lt', {}).items():   # served when the mapped face line is smaller than the location total
        fv = next((D(r['value']) for r in rows if r['accession'] == a_ and r['data_point'] == 'amortization_of_intangibles' and r['status'] == 'mapped' and r['value'] is not None), None)
        if fv is not None and x['value'] > fv:
            LT[a_] = dict(value=str(x['value']), check=' + '.join(f"{k} {v / 10**6:f}".rstrip('0').rstrip('.') for k, v in x['parts'].items()) + (f" = {x['total_member']}" if x['total_member'] else ''))
    for r in rows:
        x = LT.get(r['accession'])
        if x and r['data_point'] == 'amortization_of_intangibles' and r['status'] == 'mapped' and r['value'] is not None and D(x['value']) > D(r['value']):
            r.update(value=D(x['value']), nodes=f"AmortizationOfIntangibleAssets={x['value']} [location total: {x['check']}]; face part {r.get('nodes', '').split(' | why')[0]}",
                     why='the IS face line is the operating-expense part only; the filing reports the total by income-statement location (members sum to it)')
            r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'location_total') if y)
    # a receivable/payable read from a note fact while the face line carries a member-only fact: the face line wins (COP AR)
    for r in rows:
        if r['data_point'] in ('accounts_receivable',) and '[NOTE]' in (r.get('nodes') or '') and r['status'] == 'mapped':
            mf = [(t, m) for (a_, t), m in MF.items() if a_ == r['accession'] and t in ('AccountsAndNotesReceivableNet', 'AccountsReceivableNetCurrent', 'ReceivablesNetCurrent')]
            if mf:
                t = mf[0][0]; v = note_facts(notefacts[r['accession']])[(t, 0)]
                r.update(value=v, tags=t, nodes=f'{t}={v} [NOTE]', status='mapped')
    rows = apply_label_beyond(rows, filings)
    # the ci_incl_nci point reason cites the own 10-K's CI statement line (standard_inputs.ci_face_lines over the extract's clines:
    # fsn.line stmt CI; the figure itself arrives as a note fact)
    CL = standard_inputs.ci_face_lines(clines)
    for r in rows:
        x = CL.get(r['accession'])
        if x and r['data_point'] == 'comprehensive_income' and r['status'] in ('combined', 'mapped') and 'IncludingPortion' in (r.get('nodes') or '') and '[NOTE]' in (r.get('nodes') or ''):
            r['nodes'] = r['nodes'].replace('[NOTE]', f"[R{x['report']}.htm:{x['line']} '{x['label']}', own 10-K {r['accession']}]")
    for r in rows:   # lineage of member-only face facts
        t = (r.get('tags') or '').split('+')[0] or (re.match(r'(\w+)=', r.get('nodes') or '') or [None, ''])[1]
        if (r['accession'], t) in MF and r['status'] == 'mapped' and not re.search(r'\[R\d+', r.get('nodes') or ''):
            mem = MF[(r['accession'], t)]
            r['nodes'] = re.sub(r'\[[^\]]*NOTE[^\]]*\]', f'[face line, member {mem}]', r.get('nodes') or '')
            r['why'] = f"the face line's only own-period fact carries the equity-statement column member {mem}: the consolidated value (member-only face fact rule)"
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'member_face_fact') if x)
    for r in rows: r.setdefault('nodes', '')
    keys = ['ticker', 'cik', 'accession', 'period_end', 'data_point', 'status', 'tags', 'value', 'r_page', 'nodes', 'why', 'source', 'calc_check', 'flags']
    w = csv.DictWriter(open('resolved_all.csv', 'w', newline=''), fieldnames=keys, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    INSTANT = {'total_assets', 'total_liabilities', 'stockholders_equity', 'current_assets', 'current_liabilities', 'total_debt', 'cash_and_equivalents', 'accounts_receivable',
               'accounts_payable', 'inventory', 'goodwill', 'ppe_net', 'shares_outstanding', 'deposits', 'loans_net'}
    DEC = {'mapped': 'mapped', 'component_sum': 'component_sum', 'derived': 'derived_not_printed', 'combined': 'combined', 'not_presented': 'not_presented', 'no_role': 'no_role'}
    spec = []
    for r in rows:
        v = r['value']
        spec.append(dict(cik=r['cik'], ticker=r['ticker'], data_point=r['data_point'], period_end=r['period_end'], grain='I' if r['data_point'] in INSTANT else 'FY',
                         decision=DEC.get(r['status'], r['status']), nodes=(r.get('nodes') or '') + (' | why: ' + r['why'] if r.get('why') else ''),
                         value='' if v is None or r['status'] in ('combined', 'not_presented', 'no_role') else str(D(v).normalize() if D(v) != D(v).to_integral() else D(v).to_integral()),
                         accession=r['accession'], column=r.get('column') or 'own', calc_check=r.get('calc_check', ''), flags=';'.join(x for x in (r['source'], r.get('flags', '')) if x),
                         resolver_version=sys.argv[1] if len(sys.argv) > 1 else 'dev'))
    import os
    name = sys.argv[2] if len(sys.argv) > 2 else 'resolver-all110.csv'
    w = csv.DictWriter(open(name, 'w', newline=''), fieldnames=list(spec[0].keys())); w.writeheader(); w.writerows(spec)
    print(len(rows), collections.Counter(r['status'] for r in rows))
