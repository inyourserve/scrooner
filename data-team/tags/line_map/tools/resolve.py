"""Structural resolver (read-only): structure -> role -> node, per 10-K, from FSN face lines + the filer's calc arcs.
Design: data-team/tags/STRUCTURAL-MAPPING.md. Input: filings.json rows {cik, a, p, fd, lines, calc} (see extract.sql).
A tag is only a hint that ranks nodes already holding a role; position on the face and the calc tree decide."""
import json, re, sys, csv, collections
from decimal import Decimal as D

def parse(f):
    L = []
    for s in (f['lines'] or '').split('~'):
        x = s.split('|')
        if len(x) < 9: continue
        st, rep, ln, tag, cus, neg, prole, lb, val = x[:9]
        L.append(dict(st=st, rep=int(rep), ln=int(ln), tag=tag, custom=cus == '1', neg=neg == '1', prole=prole, lb=lb,
                      val=D(val) if val not in ('', None) else None))
    arcs = collections.defaultdict(lambda: collections.defaultdict(list))  # parent -> grp -> [(child, w)]
    for s in (f['calc'] or '').split('~'):
        x = s.split('|')
        if len(x) == 4: arcs[x[1]][x[0]].append((x[2], D(x[3])))
    return L, arcs

def face(L, st):
    reps = collections.Counter(l['rep'] for l in L if l['st'] == st and l['val'] is not None)
    if not reps: return []
    r = reps.most_common(1)[0][0]
    return [l for l in L if l['st'] == st and l['rep'] == r]

def children(arcs, parent, onface):
    """The calc group of `parent` that is the face statement's own tree: its children tie to the parent's printed value
    on the face, then the most children on the face. `onface` maps tag -> face line (with value)."""
    g = arcs.get(parent)
    if not g: return None
    pv = onface[parent]['val'] if isinstance(onface, dict) and parent in onface else None
    def ties(ch):
        if pv is None or not all(c in onface for c, _ in ch): return False
        s = sum(onface[c]['val'] * w for c, w in ch)
        return abs(s - pv) <= tol(pv, *[onface[c]['val'] for c, _ in ch])
    return max(g.values(), key=lambda ch: (ties(ch), sum(c in onface for c, _ in ch), -len(ch)))

def unit(v):
    v = abs(v); k = 0
    while k < 9 and v != 0 and v % (10 ** (k + 1)) == 0: k += 1
    return D(10) ** k

def tol(*vs): return sum((unit(v) / 2 for v in vs if v is not None), D(0)) or D(1)

def cor_top(cn, iby, kids_fn, onis):
    """If the cost-of-revenue nodes found are the children of one printed cost-of-revenue subtotal, use the subtotal."""
    for p in onis:
        if COR_HINT.search(p) and p not in cn:
            ks = {c for c, w in kids_fn(p)}
            if ks and set(cn) <= ks: return [p]
    return cn

def node(l, why): return dict(tag=l['tag'], val=l['val'], ln=l['ln'], rep=l['rep'], lb=l['lb'], why=why)

REV_HINT = re.compile(r'Revenue|Sales')
COR_HINT = re.compile(r'^CostOf|CostOfRevenue|CostOfGoods|CostOfServices|CostDirect')
COS_LABEL = re.compile(r'(?i)^(total )?costs? of|^food (and|&) paper')
def cos_nature(tag, lb): return bool(COR_HINT.search(tag) or COS_LABEL.search(lb or ''))

def resolve(f):
    L, arcs = parse(f)
    out = {}
    def put(dp, status, nodes, value, path, note=''):
        out[dp] = dict(status=status, tags='+'.join(n['tag'] for n in nodes), value=value, path=path,
                       stmt=nodes[0].get('st', '') if nodes else '', line=';'.join(f"R{n['rep']}:{n['ln']}" for n in nodes), note=note)
    # ---------------- balance sheet
    bs = face(L, 'BS'); by = {l['tag']: l for l in bs if l['val'] is not None}
    onbs = by
    lse = by.get('LiabilitiesAndStockholdersEquity')
    if lse is None:  # structural: the last total on the face whose calc children include an equity node
        tots = [l for l in bs if l['val'] is not None and 'total' in (l['prole'] or '').lower()]
        lse = tots[-1] if tots else None
    checks = []
    if lse:
        lsev = lse['val']
        # total assets: the asset-side root = the face total before the liabilities section that equals L&SE
        cand = [l for l in bs if l['val'] is not None and l['ln'] < lse['ln'] and abs(l['val'] - lsev) <= tol(l['val'], lsev) and l is not lse]
        cand.sort(key=lambda l: (l['tag'] != 'Assets', l['ln']))
        if cand:
            a = cand[0]; put('total_assets', 'mapped', [dict(node(a, 'asset root'), st='BS')], a['val'], f"BS R{a['rep']} line {a['ln']} = L&SE root {lse['tag']} {lsev}")
        else: checks.append('no asset root equal to L&SE')
        ch = children(arcs, lse['tag'], onbs) or []
        chf = [(c, w) for c, w in ch if c in by]
        liab = [c for c, w in chf if c == 'Liabilities'] or [c for c, w in chf if c in arcs and 'LiabilitiesCurrent' in {x for x, _ in (children(arcs, c, onbs) or [])}]
        eq_incl = 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'
        eqhdr = next((l['ln'] for l in bs if l['ln'] < lse['ln'] and l['val'] is None and re.search(r'(?i)equity|capital|deficit', l['lb'] + l['tag']) and not re.search(r'(?i)liabilit', l['lb'])), None)
        EQC = re.compile(r'^(CommonStock|AdditionalPaidInCapital|RetainedEarnings|AccumulatedOtherComprehensive|TreasuryStock|PreferredStockValue|StockholdersEquity|MinorityInterest|PartnersCapital|MembersEquity|LimitedLiabilityCompany)')
        def is_eq(c): return bool(EQC.match(c)) or (eqhdr is not None and c in by and by[c]['ln'] > eqhdr)
        def subtotal(c): return c in arcs and len(children(arcs, c, onbs) or []) >= 2
        # parent equity = the equity subtotal node (has its own calc children), never a component line
        eqp = None
        eq_combined = False
        if 'StockholdersEquity' in by: eqp = 'StockholdersEquity'
        elif eq_incl in by:
            sub = children(arcs, eq_incl, onbs) or []
            def eqtotal(c): return c in by and subtotal(c) and not re.match(r'^(AccumulatedOther|RetainedEarnings|CommonStock|AdditionalPaid|Treasury|Preferred)', c) and 'Noncontrolling' not in c and c != 'MinorityInterest'
            eqp = next((c for c, w in sub if eqtotal(c)), None)
            if eqp is None:
                nci = [c for c in by if re.search(r'Noncontrolling|MinorityInterest', c) and c != eq_incl and by[c]['val']]
                if nci: eq_combined = True   # parent equity not printed apart from NCI
                else: eqp = eq_incl          # no NCI on the face: the printed equity total is the parent equity
        if eqp is None and not eq_combined:
            eqc = [c for c, w in chf if is_eq(c) and subtotal(c) and c != eq_incl]
            eqp = eqc[0] if eqc else None
        if eq_combined:
            ncis = [c for c in by if re.search(r'Noncontrolling|MinorityInterest', c) and c != eq_incl and by[c]['val'] and 'Redeemable' not in c and 'Temporary' not in c and by[c]['ln'] < by[eq_incl]['ln']]
            if ncis:
                v = by[eq_incl]['val'] - sum(by[c]['val'] for c in ncis)
                put('stockholders_equity', 'derived', [dict(node(by[eq_incl], ''), st='BS')] + [dict(node(by[c], ''), st='BS') for c in ncis], v,
                    f"parent equity not printed: {eq_incl} {by[eq_incl]['val']} - {'+'.join(ncis)} (same filing; Dhairya ruling 2026-11-13: parent equity excludes NCI)", 'DERIVED')
            else:
                put('stockholders_equity', 'combined', [], None, f"parent equity not printed: only {eq_incl} (includes NCI) on the face")
        if eqp:
            e = by[eqp]; put('stockholders_equity', 'mapped', [dict(node(e, 'parent equity'), st='BS')], e['val'], f"BS R{e['rep']} line {e['ln']}: parent-equity node{' under ' + eq_incl if eq_incl in by else ' under ' + lse['tag']}")
        if liab:
            l_ = by[liab[0]]; put('total_liabilities', 'mapped', [dict(node(l_, 'liabilities subtotal'), st='BS')], l_['val'], f"BS R{l_['rep']} line {l_['ln']}: calc child of {lse['tag']}")
        elif chf:
            # not printed: DERIVED = L&SE - equity-side children (equity incl NCI, or parent equity + NCI + mezzanine), only from this tree
            eqside = [c for c, w in chf if (is_eq(c) or re.search(r'Temporary|Redeemable|Noncontrolling', c)) and c != 'CommitmentsAndContingencies']
            liabside = [c for c, w in chf if c not in eqside and c != 'CommitmentsAndContingencies']
            if eqside and liabside:
                v = lsev - sum(by[c]['val'] * w for c, w in chf if c in eqside)
                put('total_liabilities', 'derived', [dict(node(by[c], 'liability child'), st='BS') for c in liabside], v,
                    f"not printed: {lse['tag']} {lsev} - ({' + '.join(eqside)}) per the filer's calc tree", 'DERIVED')
        # mezzanine / NCI role: every other calc child of L&SE (or of the equity-incl-NCI node) that is not L, E, commitments
        mez = [c for c, w in chf if c not in set(liab) | {eqp, eq_incl, 'CommitmentsAndContingencies'} and c in by and liab and subtotal(c) is not None]
        mez = [c for c in mez if not (EQC.match(c) and not c.startswith(('MinorityInterest', 'StockholdersEquity')))]
        if eq_incl in by:
            mez += [c for c, w in (children(arcs, eq_incl, onbs) or []) if c in by and c != eqp and eqp != eq_incl and (re.search(r'Noncontrolling|MinorityInterest', c) or subtotal(c))]
        if mez:
            put('mezzanine_and_nci', 'component_sum', [dict(node(by[c], 'equity-side child'), st='BS') for c in mez], sum(by[c]['val'] for c in mez),
                f"other calc children of {lse['tag']}" + (f" / {eq_incl}" if eq_incl in by else ''))
        # the filer's own identity on its own numbers
        if chf:
            s = sum(by[c]['val'] * w for c, w in chf)
            checks.append(f"calc {lse['tag']}: {'ok' if abs(s - lsev) <= tol(lsev, *[by[c]['val'] for c, _ in chf]) else 'FAIL'}")
        # current subtotals: calc children of the asset root / liabilities node
        for dp, parent, hint in (('current_assets', out.get('total_assets', {}).get('tags'), 'AssetsCurrent'), ('current_liabilities', (liab or [None])[0], 'LiabilitiesCurrent')):
            if parent and hint in by and any(c == hint for c, _ in (children(arcs, parent, onbs) or [])):
                x = by[hint]; put(dp, 'mapped', [dict(node(x, ''), st='BS')], x['val'], f"BS line {x['ln']}: calc child of {parent}")
            elif hint in by:
                x = by[hint]; put(dp, 'mapped', [dict(node(x, ''), st='BS')], x['val'], f"BS line {x['ln']} (no calc arc to {parent}; tag hint)", 'hint_only')
    # ---------------- income statement
    is_ = face(L, 'IS'); iby = {}
    for l in is_:
        if l['val'] is not None: iby.setdefault(l['tag'], l)
    onis = iby
    isall = {l['tag'] for l in is_}
    def kids(p): return [(c, w) for c, w in (children(arcs, p, onis) or []) if c in iby]
    def novalue(p): return [c for c, w in (children(arcs, p, onis) or []) if c in isall and c not in iby]
    parents = collections.defaultdict(list)
    for p in onis:
        for c, w in kids(p): parents[c].append((p, w))
    gp = iby.get('GrossProfit')
    if gp is None:  # structural GP: a node whose children are one +1 revenue-like and -1 cost lines and which is itself a +1 child
        for p in onis:
            k = kids(p)
            if len(k) >= 2 and sum(w > 0 for _, w in k) == 1 and all(w < 0 for c, w in k if w <= 0) and 'Gross' in iby[p]['lb']:
                gp = iby[p]; break
    rev = None
    if gp is not None:
        k = kids(gp['tag']); plus = [c for c, w in k if w > 0]; minus = [c for c, w in k if w < 0]
        if len(plus) == 1: rev = iby[plus[0]]
        tax = [c for c in minus if re.search(r'(?i)excise|salestax|taxes', c + ' ' + iby[c]['lb'])]
        if tax and rev is not None:
            net = rev['val'] - sum(iby[c]['val'] for c in tax)
            nl = next((l for l in is_ if l['val'] is not None and abs(l['val'] - net) <= tol(net, l['val']) and l['ln'] > rev['ln']), None)
            if nl:  # a net-revenue line is printed after the tax: the tax is a revenue deduction (PM); else it sits in the COR span (MO)
                rev = nl; minus = [c for c in minus if c not in tax]
        if minus:
            cn = [iby[c] for c in minus]
            put('cost_of_revenue', 'mapped' if len(cn) == 1 else 'component_sum', [dict(node(n, ''), st='IS') for n in cn], sum(n['val'] for n in cn),
                f"IS: the -1 child(ren) of {gp['tag']} line {gp['ln']}")
        put('gross_profit', 'mapped', [dict(node(gp, ''), st='IS')], gp['val'], f"IS line {gp['ln']}: calc parent of revenue (+1) and cost (-1)")
    # operating income: the node that adds the top line (GP or revenue) and subtracts operating costs; never a pretax node
    oi = iby.get('OperatingIncomeLoss')
    if oi is None:
        cand = [p for p in onis if any(w > 0 for _, w in kids(p)) and any(w < 0 for _, w in kids(p)) and (gp is None or p != gp['tag'])
                and re.search(r'(?i)operating (income|profit|loss|earnings)|income from operations|earnings from operations|profit from operations', iby[p]['lb']) and not re.search(r'BeforeIncomeTax|PreTax|ExpenseAndIncomeOther|IncomeLossFromContinuingOperations', p)]
        oi = iby[cand[0]] if cand else None
    # revenue: GP's +1 child, else OI's +1 child (one), else the bank shape, else the top line climbed to its revenue total
    if rev is None and oi is not None:
        plus = [c for c, w in kids(oi['tag']) if w > 0]
        if len(plus) == 1: rev = iby[plus[0]]
    if rev is None:
        for p in onis:
            k = kids(p)
            if len(k) >= 2 and all(w > 0 for _, w in k) and any(re.search(r'(?i)noninterest', c + iby[c]['lb']) for c, _ in k) and any(any(w2 < 0 for _, w2 in kids(c)) and re.search(r'(?i)interest', c) for c, _ in k):
                rev = iby[p]; break
    bank_parts = None
    if rev is None:
        nii = next((p for p in onis if any(w > 0 and re.search(r'(?i)interest', c) for c, w in kids(p)) and any(w < 0 and re.search(r'(?i)interestexpense', c) for c, w in kids(p))), None)
        nonint = next((p for p in onis if re.match(r'(?i)^NoninterestIncome$', p) or re.match(r'(?i)^total non-?interest income', iby[p]['lb'])), None)
        if nii and nonint: bank_parts = [iby[nii], iby[nonint]]   # used only when no revenue total is found below
    if rev is None and oi is None:
        ptn = next((t for t in onis if re.search(r'BeforeIncomeTax', t) and kids(t)), None)
        if ptn:
            plus = sorted([iby[c] for c, w in kids(ptn) if w > 0 and not re.search(r'(?i)equity method|other income|nonoperating|gain', c + iby[c]['lb'])], key=lambda l: l['ln'])
            if plus and any(w < 0 for _, w in kids(ptn)) and (len(plus) == 1 or bank_parts is None): rev = plus[0]
    if rev is None and bank_parts is None:
        first = next((l for l in is_ if l['val'] is not None and not re.search(r'PerShare|Shares', l['tag'])), None)
        rev = first; seen = set()
        while rev is not None and rev['tag'] not in seen:
            seen.add(rev['tag'])
            up = [(p, w) for p, w in parents.get(rev['tag'], []) if w > 0 and iby[p]['ln'] > rev['ln'] and not any(w2 < 0 and re.search(r'(?i)cost|expense', c2 + iby[c2]['lb']) for c2, w2 in kids(p))]
            if not up: break
            rev = iby[up[0][0]]
    # filing without a calc arc for the top line: the first printed total that equals the sum of the lines above it
    if rev is not None and not parents.get(rev['tag']) and not kids(rev['tag']):
        acc = D(0); seen_lines = [l for l in is_ if l['val'] is not None and l['ln'] >= rev['ln']]
        for l in seen_lines:
            if 'total' in (l['prole'] or '').lower() and l['ln'] > rev['ln'] and abs(l['val'] - acc) <= tol(l['val'], acc):
                rev = l; break
            acc += l['val']
    # label demotes, never promotes: a 'revenues and other income' total is not revenue; take its sales child
    if rev is not None and re.search(r'(?i)and other income', rev['lb']):
        sub = [iby[c] for c, w in kids(rev['tag']) if w > 0 and not re.search(r'(?i)equity|other income|interest income|dividend|gain|investment|EquityMethod|OtherIncome|Nonoperating', c + ' ' + iby[c]['lb'])]
        if len(sub) == 1: rev = sub[0]
    # revenue after provisions is not revenue: descend to its +1 child (AXP)
    if rev is not None and any(w < 0 and re.search(r'(?i)provision|creditloss', c + iby[c]['lb']) for c, w in kids(rev['tag'])):
        pl = [iby[c] for c, w in kids(rev['tag']) if w > 0]
        if len(pl) == 1: rev = pl[0]
    # a revenue line that is a +1 child of a printed all-additive revenue total climbs to it (ORCL)
    if rev is not None:
        seen = set()
        while rev['tag'] not in seen:
            seen.add(rev['tag'])
            up = [p for p, w in parents.get(rev['tag'], []) if w > 0 and all(ww > 0 for _, ww in kids(p)) and REV_HINT.search(p + iby[p]['lb']) and not re.search(r'(?i)and other income', iby[p]['lb']) and p not in ((gp or {}).get('tag'), (oi or {}).get('tag'))]
            if not up: break
            rev = iby[up[0]]
    if rev is None and bank_parts:
        put('revenue', 'component_sum', [dict(node(n, ''), st='IS') for n in bank_parts], sum(n['val'] for n in bank_parts), 'bank IS without a revenue total: net interest income + noninterest income')
    if rev is not None:
        put('revenue', 'mapped', [dict(node(rev, ''), st='IS')], rev['val'], f"IS line {rev['ln']}: top line" + (f", +1 child of {gp['tag']}" if gp is not None else (f", +1 child of {oi['tag']}" if oi is not None else '')))
    if oi is not None:
        put('operating_income', 'mapped', [dict(node(oi, ''), st='IS')], oi['val'], f"IS line {oi['ln']}")
        k = kids(oi['tag']); top = {gp['tag']} if gp is not None else ({rev['tag']} if rev is not None else set())
        cor_tags = set(out.get('cost_of_revenue', {}).get('tags', '').split('+')) - {''}
        rest = [(c, w) for c, w in k if c not in top and c not in cor_tags]
        holder = oi['tag']; opened = []
        if gp is None and not cor_tags:
            cn = [c for c, w in rest if w < 0 and cos_nature(c, iby[c]['lb']) and kids(c) and all(cos_nature(x, iby[x]['lb']) or True for x, _ in kids(c)) and COS_LABEL.search(iby[c]['lb'] or '')]
            if len(cn) == 1:
                put('cost_of_revenue', 'mapped', [dict(node(iby[cn[0]], ''), st='IS')], iby[cn[0]]['val'], f"IS line {iby[cn[0]]['ln']}: the cost-of-sales subtotal in the band", 'hint_ranked')
                cor_tags = set(cn); rest = [(c, w) for c, w in rest if c not in cor_tags]
        for c, w in list(rest):
            inner = kids(c)
            if w < 0 and inner and (cor_tags & {x for x, _ in inner} or (gp is None and not cor_tags and any(cos_nature(x, iby[x]['lb']) for x, _ in inner)) or any(COR_HINT.search(x) for x in novalue(c))):
                if gp is None and not cor_tags:
                    # BKNG test (Dhairya 2026-11-13): the cost-of-sales lines are every band line up to the last one that is cost of sales by nature
                    order = sorted(inner, key=lambda xw: iby[xw[0]]['ln'])
                    idx = [i for i, (x, ww) in enumerate(order) if cos_nature(x, iby[x]['lb'])]
                    if idx and idx[0] == 0:   # cost-of-sales lines lead the band: the block up to the last one is cost of sales
                        cn = [x for x, ww in order[:idx[-1] + 1] if ww > 0]
                    else:                     # scattered (UNH): only the lines that are cost of sales by nature
                        cn = [order[i][0] for i in idx if order[i][1] > 0]
                    cn = cor_top(cn, iby, kids, onis) if cn else cn
                    cn = cor_top(cn, iby, kids, onis) if cn else cn
                    if cn and not any(COR_HINT.search(x) for x in cn):
                        cor_tags |= set(cn); cn = []   # cost of sales by label only (MCD food & paper): shapes the opex band, no COR value
                    if cn:
                        put('cost_of_revenue', 'mapped' if len(cn) == 1 else 'component_sum', [dict(node(iby[x], ''), st='IS') for x in cn], sum(iby[x]['val'] for x in cn), f"IS: cost-of-revenue child(ren) of {c} (role: costs under OI; tag ranks)", 'hint_ranked')
                        cor_tags |= set(cn)
                rest.remove((c, w)); rest += [(x, -ww) for x, ww in inner if x not in cor_tags]; opened.append(c)
        if gp is None and not cor_tags:
            cn = [c for c, w in rest if w < 0 and COR_HINT.search(c)]
            cn = cor_top(cn, iby, kids, onis) if cn else cn
            if cn:
                rest = [(c, w) for c, w in rest if c not in set(cn) | {x for p in cn for x, _ in kids(p)}]
                put('cost_of_revenue', 'mapped' if len(cn) == 1 else 'component_sum', [dict(node(iby[c], ''), st='IS') for c in cn], sum(iby[c]['val'] for c in cn), f"IS: cost-of-revenue -1 child(ren) of {oi['tag']} (role: costs under OI; tag ranks)", 'hint_ranked')
                cor_tags = set(cn); rest = [(c, w) for c, w in rest if c not in cor_tags]
        if top & {c for c, _ in k} and rest:
            miss = [c for h in [oi['tag']] + opened for c in novalue(h) if c not in cor_tags and not COR_HINT.search(c) and c not in opened]
            neg = [c for c, w in rest if w < 0]
            if miss:
                put('operating_expenses', 'combined', [], None, f"a line between the top line and OI has no consolidated value ({'+'.join(miss)}): no component sum")
            elif len(neg) == 1 and not opened:
                x = iby[neg[0]]; put('operating_expenses', 'mapped', [dict(node(x, ''), st='IS')], x['val'], f"IS line {x['ln']}: the expense node between {'/'.join(top)} and OI" + (' (other lines there are gains/income)' if len(rest) > 1 else ''))
            else:
                v = -sum(iby[c]['val'] * w for c, w in rest)
                put('operating_expenses', 'component_sum', [dict(node(iby[c], ''), st='IS') for c, _ in rest], v, f"IS: -sum(weight x value) of the lines between {'/'.join(top)} and OI" + (f" (opened {'+'.join(opened)} without cost of revenue)" if opened else ''))
    elif 'NoninterestExpense' in iby and rev is not None and re.search(r'(?i)interest', rev['tag'] + rev['lb'] + ' '.join(c for c, _ in kids(rev['tag']))):
        x = iby['NoninterestExpense']; put('operating_expenses', 'mapped', [dict(node(x, ''), st='IS')], x['val'], 'bank IS: the noninterest expense total (ruling: bank opex = NoninterestExpense)')
    # pretax / tax / net income
    ni = iby.get('NetIncomeLoss')
    if ni is not None: put('net_income', 'mapped', [dict(node(ni, ''), st='IS')], ni['val'], f"IS line {ni['ln']} (attributable to parent)")
    after = next((iby[t] for t in ('IncomeLossFromContinuingOperations', 'ProfitLoss', 'NetIncomeLoss') if t in iby and any(w < 0 and 'IncomeTax' in c for c, w in kids(t))), None)
    if after is not None:
        k = kids(after['tag'])
        tx = [iby[c] for c, w in k if w < 0 and 'IncomeTax' in c]
        pt = [iby[c] for c, w in k if w > 0 and 'BeforeIncomeTax' in c] or [iby[c] for c, w in k if w > 0]
        if tx: put('income_tax_expense', 'mapped', [dict(node(tx[0], ''), st='IS')], tx[0]['val'], f"IS: -1 child of {after['tag']}")
        if len(pt) == 1: put('income_before_tax', 'mapped', [dict(node(pt[0], ''), st='IS')], pt[0]['val'], f"IS: +1 child of {after['tag']}")
    # ---------------- cash flow
    cf = face(L, 'CF'); cby = {}
    for l in cf:
        if l['val'] is not None: cby.setdefault(l['tag'], l)
    oncf = cby
    root = next((t for t in ('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',
                             'CashAndCashEquivalentsPeriodIncreaseDecrease', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect',
                             'CashPeriodIncreaseDecrease') if t in cby), None)
    if root:
        k = [(c, w) for c, w in (children(arcs, root, oncf) or []) if c in cby]
        # nested: an ex-fx subtotal under the root
        for c, w in list(k):
            if 'PeriodIncreaseDecrease' in c: k += [(cc, ww) for cc, ww in (children(arcs, c, oncf) or []) if cc in cby]
        for dp, word in (('cfo', 'Operating'), ('cash_flow_investing', 'Investing'), ('cash_flow_financing', 'Financing')):
            secs = [c for c, w in k if word in c and 'Discontinued' not in c]
            tot = [c for c in secs if 'ContinuingOperations' not in c] or secs
            if tot:
                x = cby[tot[0]]; put(dp, 'mapped', [dict(node(x, ''), st='CF')], x['val'], f"CF line {x['ln']}: calc child of {root}")
            elif f'NetCashProvidedByUsedIn{word}Activities' in cby:
                x = cby[f'NetCashProvidedByUsedIn{word}Activities']; put(dp, 'mapped', [dict(node(x, ''), st='CF')], x['val'], f"CF line {x['ln']} (tag hint; not a calc child of {root})", 'hint_only')
        if k:
            s = sum(cby[c]['val'] * w for c, w in k if 'PeriodIncreaseDecrease' not in c)
            checks.append(f"calc {root}: {'ok' if abs(s - cby[root]['val']) <= tol(cby[root]['val'], *[cby[c]['val'] for c, _ in k]) else 'FAIL'}")
    return out, checks

DPS = ['total_assets', 'total_liabilities', 'stockholders_equity', 'current_assets', 'current_liabilities', 'mezzanine_and_nci',
       'revenue', 'cost_of_revenue', 'gross_profit', 'operating_expenses', 'operating_income', 'income_before_tax', 'income_tax_expense', 'net_income',
       'cfo', 'cash_flow_investing', 'cash_flow_financing']
if __name__ == '__main__':
    filings = json.load(open(sys.argv[1])); tick = {r[1]: r[0] for r in csv.reader(open(sys.argv[2]))}; outdir = sys.argv[3]
    import os; os.makedirs(outdir, exist_ok=True)
    rows = collections.defaultdict(list)
    for f in filings:
        tk = tick.get(f['cik'].zfill(10)) or tick.get(f['cik'])
        if not tk: continue
        res, checks = resolve(f)
        for dp in DPS:
            r = res.get(dp)
            rows[tk].append(dict(ticker=tk, cik=f['cik'], accession=f['a'], period_end=f['p'], filed=f['fd'], data_point=dp,
                                 status=r['status'] if r else 'no_role', tags=r['tags'] if r else '', value=str(r['value']) if r else '',
                                 lines=r['line'] if r else '', path=r['path'] if r else 'no node holds this role on the face/calc tree',
                                 flag=r['note'] if r else '', filing_checks=';'.join(checks)))
    for tk, rs in rows.items():
        rs.sort(key=lambda r: (r['period_end'], DPS.index(r['data_point'])))
        w = csv.DictWriter(open(f'{outdir}/{tk}.csv', 'w', newline=''), fieldnames=list(rs[0].keys())); w.writeheader(); w.writerows(rs)
    print(len(rows), 'tickers', sum(len(v) for v in rows.values()), 'rows')
