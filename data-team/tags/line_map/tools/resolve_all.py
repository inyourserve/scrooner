"""Structural resolver for every template data point (read-only), unchanged for 110 or 1,000 companies.
Core statement roles: resolve.py (tree positions); total_debt: total_debt.py; every other data point: rules/roles.csv
(position = statement + calc parent; the element family only ranks candidates; label demotes, a custom line is accepted
only when its own label names the role). Output: one row per filing x data point with value or reason."""
import csv, json, os, re, sys, collections
from decimal import Decimal as D
sys.path.insert(0, '.')
from resolve import parse, face, children, resolve, DPS as CORE_DPS
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
def _here(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', name)
def fill_printed_zero_and_comparative(rows, td):
    """Rulings 2026-11-14 (Dhairya). (a) A line printed on the own face with a dash or zero is served as 0, flag printed_zero
    with its R:line (_printed-zero-2026-11-14.csv: the line is on the face, no own-period fact exists in any dimension, the
    line has values in other columns); a line absent from the face stays not_presented. (b) A value the next 10-K prints in its
    comparative column fills a cell the own filing does not present: column=comparative, that filing's accession and R page
    (_comparative-fill-2026-11-14.csv; total_debt from the comparative column of total_debt_all)."""
    pz = {(r['accession'], r['data_point']): r for r in csv.DictReader(open(os.environ.get('PRINTED_ZERO', _here('_printed-zero-2026-11-14.csv'))))} if os.path.exists(os.environ.get('PRINTED_ZERO', _here('_printed-zero-2026-11-14.csv'))) else {}
    cfp = os.environ.get('COMPARATIVE_FILL', _here('_comparative-fill-2026-11-14.csv'))
    cf = {(r['own_accession'], r['data_point']): r for r in csv.DictReader(open(cfp))} if os.path.exists(cfp) else {}
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
                     nodes=f"{c['tag']}={c['value']} [{c['loc']} of {c['accession']}, comparative column]",
                     why='the own filing does not present the line; the next 10-K prints it in its comparative column (ruling 2026-11-14, FY-1 comparative rule)')
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'comparative_fill', 'printed_zero' if v == 0 else '') if x)
        elif r['data_point'] == 'total_debt':
            t = next((t for t in by.get(r['ticker'], []) if t['period_end'] == r['period_end'] and t['status'] in ('mapped', 'component_sum')), None)
            if t:
                r.update(status=t['status'], value=D(t['value']), tags=t['tags'], accession=t['accession'], column='comparative', nodes=t['parts'] + f" [comparative column of {t['accession']}]",
                         why='total_debt rule on the next 10-K comparative column (the own filing presents no debt line; ruling 2026-11-14)')
                r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'comparative_fill', 'printed_zero' if D(t['value']) == 0 else '') if x)
    return rows
def family_rows(f, notes, raw):
    """Family modules (tools/resolve_bs.py, tools/resolve_cf.py): position logic per family; rows replace the role rows of their data points."""
    out = {}
    bsraw = '~'.join(x for x in (raw or '').split('~') if x.count('|') == 2 and x.split('|')[1] == '0')
    for dp, r in resolve_bs.resolve_family(f, resolve_bs.notes_for(bsraw)).items():
        out[dp] = dict(status=r['status'], tags=r.get('tags', ''), value=r['value'], r_page='', nodes=r.get('nodes', ''), why=r['why'], source='bs_family', flags=r.get('rule', ''))
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
        notes = {}
        for s in (notefacts.get(f['a']) or '').split('~'):
            x = s.split('|')
            if len(x) == 3: notes.setdefault((x[0], int(x[1])), D(x[2]))
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
    td = {(r['accession'], r['column']): r for r in csv.DictReader(open('total_debt_all.csv'))}
    # member-only face facts (_member-face-facts-2026-11-14.csv): a DPS, share count or CI printed on the face whose only own-period
    # fact carries one equity-statement column member (EquityComponents=RetainedEarnings / CommonStock ...) is the consolidated value;
    # share counts equal to shares issued (VZ, C, TMO) were rejected in the file. They enter as note facts, lineage keeps the member
    MF = {}
    _mf = os.environ.get('MEMBER_FACTS', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_member-face-facts-2026-11-14.csv'))
    if os.path.exists(_mf):
        for m in csv.DictReader(open(_mf)):
            have = {tuple(x.split('|')[:2]) for x in (notefacts.get(m['accession']) or '').split('~')}
            if (m['tag'], m['qtrs']) not in have:
                notefacts[m['accession']] = '~'.join(x for x in (notefacts.get(m['accession']), f"{m['tag']}|{m['qtrs']}|{m['value']}") if x)
                MF[(m['accession'], m['tag'])] = m['member']
    rows = run(filings, notefacts, tick, td)
    import resolve_is
    rows = resolve_is.apply(rows, filings, notefacts, tick)  # IS family (resolve_is.py) replaces its six data points where decisive
    rows = fill_printed_zero_and_comparative(rows, td)
    rows = apply_polarity(rows)  # one sign per concept (rules/polarity.csv)
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
