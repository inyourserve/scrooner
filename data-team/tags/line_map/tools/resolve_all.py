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
import resolve_bs, resolve_cf, resolve_is, standard_inputs
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
        m = re.search(r'\[(R[^\]]*|NOTE|BSP|BS parenthetical[^\]]*)\]', nodes_loc)
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
                     nodes=f"{s['tag']}[RelatedPartyTransactionsByRelatedParty=NonrelatedParty]={n} [face line]; {s['tag']}[RelatedPartyTransactionsByRelatedParty=RelatedParty]={rel} [face line]",
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
PERSONNEL_LB = re.compile(r'(?i)^(personnel|salaries|compensation and benefits|employee compensation)')


DP_REF = re.compile(r'^(-?)(revenue|cost_of_revenue|gross_profit|operating_income|operating_expenses)(?: (\w+))?=(-?[\d.]+)$')
PART = re.compile(r'^(-?)([A-Za-z_]\w*)(\[[\w;=-]+\])?(?:=(-?[\d.]+))?$')
LOC_R = re.compile(r'^(?:(?:BS|IS|CF) )?R(\d+)(?:\.htm)?(?::(\d+))?\b')
ACC = re.compile(r'\b(\d{10}-\d{2}-\d{6})\b')
NODE_GRAMMAR = re.compile(r'^-?\w+(\[\w+=[\w-]+\])?(=-?[\d.]+)? \[(R\d+\.htm(:\d+)?|NOTE|SE|BSP)(@\d{10}-\d{2}-\d{6})?\]$')


def _split_parts(s):
    """'; '-separated parts, never splitting inside [...] (lease reasons carry '; ' inside their bracket)."""
    out, depth, cur = [], 0, ''
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == '[': depth += 1
        elif ch == ']': depth -= 1
        if depth == 0 and s.startswith('; ', i):
            out.append(cur); cur = ''; i += 2; continue
        cur += ch; i += 1
    if cur: out.append(cur)
    return out


def normalize_nodes(rows, filings):
    """Every node in one grammar (Dhairya 2026-11-14): part := [-]Tag[Axis=Member][=value] [LOC]; LOC := Rn.htm[:line] | NOTE | SE | BSP,
    optionally @ACC when the figure comes from another filing than the row's own (comparative fills); parts joined by '; '. SE = the
    statement of equity, BSP = the balance-sheet parenthetical. A part names a value whenever the row has one; reason rows (combined,
    not_presented) keep the line and may carry no value. A gross profit derived from other cells lists those cells' parts, signed.
    Everything else a builder wrote inside a location bracket moves to why."""
    F = {f['a']: f for f in filings}
    cell = {(r.get('ticker'), str(r.get('period_end')), r['data_point']): r for r in rows}
    def loc_of(text, row_acc, tag):
        acc = ACC.findall(text); m = LOC_R.match(text.strip())
        # a figure read from another filing's column (comparative fill: 'of ACC, FY-1 column', 'comparative column of ACC') names it;
        # the row's own 10-K ('own 10-K ACC') does not
        ext = next((a for a in acc if a != row_acc or re.search(r'(?:of|column of) ' + a, text)), None)
        if m: loc = f"R{m.group(1)}.htm" + (f":{m.group(2)}" if m.group(2) else '')
        elif text.strip().startswith('BS parenthetical') or text.strip().startswith('BSP'): loc = 'BSP'
        elif text.strip().startswith('NOTE'): loc = 'NOTE'
        elif text.strip() == 'SE': loc = 'SE'
        else:
            ps = face_positions(F.get(ext or row_acc), tag)
            loc = f"R{ps[0]['rep']}.htm:{ps[0]['ln']}" if ps else 'NOTE'
        rest = text.strip()
        rest = re.sub(r'^(?:(?:BS|IS|CF) )?R\d+(?:\.htm)?(?::\d+)?|^BS parenthetical( / NOTE)?|^BSP|^NOTE|^SE$', '', rest).strip(' ,')
        return loc + (f"@{ext}" if ext else ''), rest
    def norm(r, depth=0):
        raw = (r.get('nodes') or '').split(' | why')[0]
        if not raw: return '', []
        out, prose = [], []
        for p in _split_parts(raw):
            p = p.strip()
            m_ = re.match(r'^(-?\w+(?:\[[\w;=-]+\])?(?: \w+)?(?:=-?[\d.]+)?)\s*(?:\[([^\]]*)\])?\s*(?:\[comparative column of (\d{10}-\d{2}-\d{6})\])?$', p)
            head, inside, comp = (m_.group(1), m_.group(2) or '', m_.group(3)) if m_ else (p, '', None)
            d = DP_REF.match(head)
            if d and depth == 0:
                ref = cell.get((r.get('ticker'), str(r.get('period_end')), d.group(2)))
                sub_parts = norm(ref, 1)[0].split('; ') if ref is not None and ref.get('nodes') else []
                if sub_parts and sub_parts != ['']:
                    for q in sub_parts:
                        neg = q.startswith('-')
                        out.append((q[1:] if neg else '-' + q) if d.group(1) == '-' else q)
                    continue
                head = f"{d.group(1)}{d.group(3) or d.group(2)}={d.group(4)}"
            m = PART.match(head)
            if not m:
                prose.append(p); continue
            sign, tag, mem, val = m.groups()
            if val is None and r.get('value') not in (None, '') and len(_split_parts(raw)) == 1 and r.get('status') in ('mapped', 'component_sum', 'derived'):
                val = str(r['value'])
            text = inside + (f' of {comp}' if comp else '')
            loc, rest = loc_of(text, r.get('accession'), tag)
            if rest and not re.fullmatch(r'(?:of )?\d{10}-\d{2}-\d{6}(?:, FY-\d column)?|FY-\d column|own 10-K \d{10}-\d{2}-\d{6}', rest): prose.append(f"{tag}: {rest}")
            out.append(f"{sign}{tag}{mem or ''}{'=' + val if val is not None else ''} [{loc}]")
        # a comparative row's figures all come from the same later filing: every part names it (QCOM: one trailing 'comparative column of')
        accs = {m_.group(1) for q in out for m_ in [re.search(r'@(\d{10}-\d{2}-\d{6})\]$', q)] if m_}
        if len(accs) == 1 and r.get('column') == 'comparative':
            a_ = accs.pop(); out = [q if '@' in q else q[:-1] + f'@{a_}]' for q in out]
        return '; '.join(out), prose
    bad = 0
    for r in rows:
        n, prose = norm(r)
        if not n and not (r.get('nodes') or ''): continue
        if prose: r['why'] = ((r.get('why') or '') + ' | node notes: ' + '; '.join(prose)).strip(' |')
        r['nodes'] = n
        if n and not all(NODE_GRAMMAR.match(q) for q in n.split('; ')): bad += 1
    return bad


CI_PARENT_LB = re.compile(r'(?i)comprehensive (income|earnings|\(loss\) income|income \(loss\)|loss)\b.*\battributable to (?!.*\b(non-?controlling|minority|redeemable)\b)')
NCI_IN_TAG = re.compile(r'Noncontrolling|MinorityInterest|IncludingPortion')


PARENT_SEG = re.compile(r'^(EquityComponents=Parent|ConsolidatedEntities=ParentCompany);$')


def apply_ci_parent(rows, clines, notefacts, memberfacts=None):
    """Ruling 2026-11-14 (PM): 'parent figure not printed' is false when the CI statement prints the parent line: the element
    ComprehensiveIncomeNetOfTax, or a line whose label reads 'attributable to <company>' / '<ticker>' (PM: 'Comprehensive earnings
    attributable to PMI'), with an undimensioned own-period fact. The parent line is served; the reason is never given then."""
    for r in rows:
        if r['data_point'] != 'comprehensive_income' or r['status'] not in ('combined', 'not_presented', 'no_role') or r.get('column', 'own') != 'own': continue
        und = standard_inputs._undim(notefacts, r['accession'])
        cand = []
        for t, rep, ln, lb in standard_inputs._facts(clines.get(r['accession']), 4):
            if NCI_IN_TAG.search(t): continue
            if t == 'ComprehensiveIncomeNetOfTax' or CI_PARENT_LB.search(lb or ''):
                v = und.get((t, 4)); seg = ''
                if v is None:   # WFC FY2021: the parent line's fact carries only parent-scoped members, all equal (19,652)
                    pv = {(sg, D(x)) for t_, q, x, sg in standard_inputs._facts((memberfacts or {}).get(r['accession']), 4) if t_ == t and int(q) == 4 and PARENT_SEG.match(sg)}
                    if pv and len({x for _, x in pv}) == 1: seg, v = sorted(pv)[0][0].rstrip(';'), next(iter(pv))[1]
                if v is not None: cand.append((t != 'ComprehensiveIncomeNetOfTax', int(rep), int(ln), t, lb, v, seg))
        if not cand: continue
        _, rep, ln, t, lb, v, seg = sorted(cand)[0]
        r.update(status='mapped', value=D(standard_inputs._plain(v)), tags=t, nodes=f"{t}{'[' + seg + ']' if seg else ''}={standard_inputs._plain(v)} [R{rep}.htm:{ln}]",
                 why=f"CI statement prints the parent line '{lb}' (R{rep}.htm:{ln}) (ruling 2026-11-14: a line attributable to the company is the parent figure)")
        r['flags'] = ';'.join(x for x in (r.get('flags', '').replace('ci_incl_nci', ''), 'ci_parent_line') if x).replace(';;', ';').strip(';')
    return rows


def finalize_calc(chk, accession, compfacts):
    """Ruling 2026-11-14: never sum an incomplete group. A calc child with no value in this column is MISSING when the filing tags it in
    another column (RTX FY2019: Liabilities 2018 tagged, 2019 printed but untagged): the check is 'skipped: child missing (...)'. A child
    the filing tags in no column (CommitmentsAndContingencies, a caption) is not printed with a value, and a group that foots without the
    child shows it as a dash: in both cases the check stands."""
    tagged = {x[0] for x in standard_inputs._facts(compfacts.get(accession), 4)}
    out = []
    for c in (chk or '').split(';'):
        m = re.match(r'^(calc \w+): (ok|FAIL) \[no value: ([\w+]+)\]$', c)
        if not m: out.append(c); continue
        miss = [t for t in m.group(3).split('+') if t in tagged]
        # a group that foots without the child shows the child as a printed dash (= 0, ruling 2026-11-14: ABT disposal-group
        # liabilities, TSLA temporary equity after conversion); a group that fails with it missing is incomplete, never judged
        out.append(f"{m.group(1)}: skipped: child missing ({'+'.join(miss)})" if miss and m.group(2) == 'FAIL' else f"{m.group(1)}: {m.group(2)}")
    return ';'.join(out)


def face_positions(f, tag):
    """The IS/BS/CF face lines of `f` with this tag, in face order (value or not): their (report, line) are the node location."""
    if not f: return []
    L, _ = parse(f)
    return [l for st in ('IS', 'BS', 'CF') for l in face(L, st) if l['tag'] == tag]


def apply_expenses_by_nature(rows, filings):
    """Dhairya ruling 2026-11-14 (c): an IS that classifies operating expenses by nature (a personnel line spanning functions,
    BKNG: marketing, sales and other, personnel, G&A) and prints no SG&A line has no SG&A: not_presented, expenses_by_nature.
    SG&A is never built from parts that mix functions."""
    nat = {}
    for f in filings:
        L, _ = parse(f)
        isf = [l for l in face(L, 'IS') if l['val'] is not None]
        tags = {l['tag'] for l in isf}
        per = next((l for l in isf if l['tag'] == 'LaborAndRelatedExpense' or PERSONNEL_LB.search(l['lb'] or '')), None)
        if per and not any(t.startswith('SellingGeneralAndAdministrativeExpense') for t in tags):
            nat[f['a']] = per
    for r in rows:
        p = nat.get(r['accession'])
        if p is not None and r['data_point'] == 'sga_expense' and r.get('column', 'own') != 'comparative':
            r.update(status='not_presented', value=None, tags='', nodes=f"{p['tag']}={p['val']} [R{p['rep']}:{p['ln']}]",
                     why=f"the IS classifies operating expenses by nature ('{p['lb']}' spans functions) and prints no SG&A line: SG&A is not built from parts (ruling 2026-11-14 c)")
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'expenses_by_nature') if x)
    return rows


IE_PART_LB = re.compile(r'(?i)^interest expense,? (of|excluding) (.+?)\s*$')


def apply_complement_interest(rows, filings, memberfacts):
    """Ruling 2026-11-14 (Dhairya, CAT): consolidated gross interest expense includes the finance arm's interest even where it sits in
    operating costs. The income statement prints the two parts as 'Interest expense of Financial Products' and 'Interest expense
    excluding Financial Products' (lines, or ProductOrService members AllOtherExcluding<X> and <X> of one line): a part and its
    complement are exhaustive by their own names (member-sum ruling 4), so interest_expense is their sum (flag member_sum)."""
    F = {f['a']: f for f in filings}
    for r in rows:
        if r['data_point'] != 'interest_expense' or r['accession'] not in F: continue
        isf = [l for l in face(parse(F[r['accession']])[0], 'IS') if not l['tag'].endswith('Abstract')]
        mem = {}
        for e in (memberfacts.get(r['accession']) or '').split('~'):
            x = e.split('|')
            if len(x) >= 4 and x[1] == '4':
                m = re.fullmatch(r'ProductOrService=(\w+);', x[3])
                if m: mem.setdefault(x[0], {})[m.group(1)] = D(x[2])
        parts = []
        lab = {l['ln']: IE_PART_LB.match((l['lb'] or '').strip()) for l in isf}
        of = [l for l in isf if lab[l['ln']] and lab[l['ln']].group(1).lower() == 'of']
        ex = [l for l in isf if lab[l['ln']] and lab[l['ln']].group(1).lower() == 'excluding']
        if len(of) == 1 and len(ex) == 1 and lab[of[0]['ln']].group(2).lower() == lab[ex[0]['ln']].group(2).lower():
            for l in (of[0], ex[0]):
                if l['val'] is not None: parts.append((l['tag'], l['val'], l))
                elif len(mem.get(l['tag'], {})) == 1:
                    (k, v), = mem[l['tag']].items(); parts.append((f"{l['tag']}[ProductOrService={k}]", v, l))
        else:
            for l in isf:
                d = mem.get(l['tag'], {})
                if l['val'] is None and re.match(r'^(InterestExpense\w*|InterestAndDebtExpense)$', l['tag']) and len(d) == 2:
                    a_, b_ = sorted(d)
                    if a_ == f'AllOtherExcluding{b_}' or b_ == f'AllOtherExcluding{a_}':
                        parts = [(f"{l['tag']}[ProductOrService={k}]", v, l) for k, v in sorted(d.items())]
        if len(parts) != 2: continue
        r.update(status='component_sum', value=sum(v for _, v, _ in parts), tags='+'.join(t.split('[')[0] for t, _, _ in parts),
                 nodes='; '.join(f"{t}={v} [R{l['rep']}.htm:{l['ln']}]" for t, v, l in parts),
                 why="consolidated gross interest expense: the finance arm's part and its complement as printed (ruling 2026-11-14, CAT: Financial Products interest is interest expense although it sits in operating costs)")
        r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'member_sum') if x)
    return rows


def apply_alt(rows):
    """Last-resort values a family module offered (class-member sums), only where no fill served the year."""
    for r in rows:
        a_ = r.pop('alt', None)
        if a_ and r['status'] == 'not_presented': r.update(a_)
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
            pos = face_positions(F.get(r['accession']), t)   # the product and service lines in face order; the service line by its label
            sl = next((l for l in pos if re.search(r'(?i)service', l['lb'] or '')), None); pl = next((l for l in pos if l is not sl), None)
            if len(pos) == 1: pl = sl = pos[0]   # the FSN keeps the element's one face line; both members are its rows (TMUS R4:15)
            loc = lambda l: f"R{l['rep']}.htm:{l['ln']}" if l else 'NOTE'
            r.update(status='component_sum', value=p + sv, tags=f'{t}+{t}',
                     nodes=f"{t}[ProductOrService={x.get('product_member', 'Product')}]={p} [{loc(pl)}]; {t}[ProductOrService={x.get('service_member', 'Service')}]={sv} [{loc(sl)}]",
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
                 nodes='; '.join(f"{x['tag']}[ProductOrService={k}]={v} [R{cl['rep']}.htm:{cl['ln']}]" for k, v in x['members'].items()),
                 why=f"the income statement is a matrix: '{cl['lb']}' carries only ProductOrService column members; their sum, which with the other cost lines ties to '{ce['lb']}' {ce['val']} (ruling 2026-11-14)")
        r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'cor_member_sum') if y)
    # (not 'Total costs and expenses': QCOM's includes cost of revenue)
    for r in rows:   # PLD 2024-25: a printed 'Total expenses' line between the top line and an operating-income line is the opex (false 'no node' reason)
        if r['data_point'] != 'operating_expenses' or r['status'] not in ('not_presented', 'no_role') or r['accession'] not in F: continue
        isf_ = [l for l in face(parse(F[r['accession']])[0], 'IS') if l['val'] is not None]
        te = next((l for l in isf_ if re.match(r'(?i)^total (operating )?expenses$', (l['lb'] or '').strip())), None)
        oi_ = next((l for l in isf_ if te and l['ln'] > te['ln'] and re.match(r'(?i)^operating (income|loss|profit)', l['lb'] or '')), None)
        rv_ = next((l for l in isf_ if te and l['ln'] < te['ln'] and re.match(r'(?i)^total revenues?$', (l['lb'] or '').strip())), None)
        if te and oi_ and rv_:
            r.update(status='mapped', value=te['val'], tags=te['tag'], nodes=f"{te['tag']}={te['val']} [R{te['rep']}.htm:{te['ln']}]",
                     why=f"IS prints '{te['lb']}' between '{rv_['lb']}' and '{oi_['lb']}'")
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'printed_total_expenses') if x)
    for r in rows:
        # also the 'a line between the top line and OI has no consolidated value' combined reason (ABBV, ACN, CAT, GLW, RTX 2015, SCCO):
        # the printed totals hold the valueless line, so they need no component sum (false-reason sweep 2026-11-14)
        nocv = r['status'] == 'combined' and (r.get('why') or '').startswith('a line between the top line and OI has no consolidated value')
        if r['data_point'] != 'operating_expenses' or (r['status'] not in ('not_presented', 'no_role') and not nocv) or r['accession'] not in F: continue
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
    for r in rows:   # false-reason sweep 2026-11-14: a 'no node' reason where the filing prints opex lines or a wider costs total
        if r['data_point'] != 'operating_expenses' or r['status'] not in ('not_presented', 'no_role') or r['accession'] not in F: continue
        isf = [l for l in face(parse(F[r['accession']])[0], 'IS') if l['val'] is not None]
        cor = by.get((r['accession'], 'cost_of_revenue'))
        tot = next((l for l in isf if l['tag'] in ('CostsAndExpenses', 'BenefitsLossesAndExpenses') or re.match(r'(?i)^total (costs|expenses|costs and (other )?(expenses|deductions))$', (l['lb'] or '').strip())), None)
        cl = next((l for l in isf if cor and cor['status'] == 'mapped' and l['tag'] == cor.get('tags')), None)
        if tot is None and cl is not None:
            # KLAC: no costs total; the operating lines printed after cost of revenue, up to the first
            # nonoperating line (interest, debt extinguishment, other income/expense), are the operating expenses
            ops = []
            for l in (x for x in isf if x['ln'] > cl['ln']):
                if OPEX_LINE.match(l['tag']) or resolve_is.OPER_TAG.match(l['tag']): ops.append(l); continue
                break
            nxt = next((l for l in isf if l['ln'] > (ops[-1]['ln'] if ops else 10**9)), None)
            if len(ops) >= 2 and nxt is not None and NONOP_NEXT.search(nxt['tag'] + ' ' + (nxt['lb'] or '')):
                r.update(status='component_sum', value=sum((l['val'] for l in ops), D(0)), tags='+'.join(l['tag'] for l in ops),
                         nodes='; '.join(f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]" for l in ops),
                         why=f"no operating-income line and no costs total: the operating lines printed after '{cl['lb']}' up to '{nxt['lb']}' (the first nonoperating line)")
                r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'opex_component_lines') if y)
                continue
        if tot is not None:
            isf_all = [l for l in face(parse(F[r['accession']])[0], 'IS') if not l['tag'].endswith(('Abstract', 'Axis', 'Domain', 'Table', 'LineItems'))]   # DIS: cost rows carry members only
            inside = [l for l in isf_all if l['ln'] < tot['ln'] and l['ln'] > max((x['ln'] for x in isf if x['ln'] < tot['ln'] and re.match(r'^(Revenues|RevenuesAndOtherIncome|SalesRevenueNet)$', x['tag'])), default=0)]
            wider = [l['lb'] for l in inside if (cl is not None and l is cl) or COSTLIKE.search(l['tag'] + ' ' + (l['lb'] or ''))]
            if not wider: continue
            r.update(status='combined', value=None, tags=tot['tag'], nodes=f"{tot['tag']}={tot['val']} [R{tot['rep']}.htm:{tot['ln']}]",
                     why=f"the only expense total printed, '{tot['lb']}', also holds " + ', '.join(f"'{w}'" for w in wider[:3]) + " (cost of revenue or nonoperating items); no operating-expense total is printed")
    return rows


OPEX_LINE = re.compile(r'^(SellingGeneralAndAdministrativeExpense|ResearchAndDevelopmentExpense\w*|GeneralAndAdministrativeExpense|SellingAndMarketingExpense|MarketingAndAdvertisingExpense|AmortizationOfIntangibleAssets|GoodwillImpairmentLoss)$')
NONOP_NEXT = re.compile(r'(?i)InterestExpense|ExtinguishmentOfDebt|OtherNonoperating|InterestAndOtherIncome|OtherExpenseIncome|other (expense|income)')
COSTLIKE = re.compile(r'(?i)^(CostOf\w*|CostOfPurchased\w*|\w*Costs\b|RefiningAndMarketingCosts|MineralExtraction\w*|CostOfGoods\w*|InterestExpense\w*|InterestAndDebtExpense|InterestAndOtherFinancialCharges|OtherNonoperating\w*|CostOfServices\w*)\b|cost of (sales|revenues?|products|goods|services)|costs applicable to sales|purchased (crude|commodities)|interest expense|interest and debt|other \(income\)')
def derive_gross_profit(rows):
    """Ruling C1 (Dhairya 2026-11-14): gross profit not printed, revenue and cost of revenue printed and resolved in the same
    filing -> DERIVED revenue - cost of revenue (derived_not_printed). Also when both come from the same later filing's column
    (COP 2016-17: cost of revenue is not in the own 10-K; the later 10-K prints revenue and cost of revenue for the year): cite that
    filing, column comparative, when that column's revenue ties to the own revenue cell. An unpresented GrossProfit fact of the same filing (EXT['gp']) is recorded in calc_check; equal to
    revenue - cost of revenue - D&A is an explained difference (gp_filer_fact_excludes_da: SCCO's cost of sales excludes D&A, SAB 11.B),
    any other difference makes the cell DISAGREE until a reader looks. Cost of revenue not resolvable (ORCL) -> not_presented."""
    corr = EXT.get('gp', {}); comp = EXT.get('comp', {})
    co = lambda r: r.get('cik') or r.get('ticker')
    by = {(co(r), r['period_end'], r['data_point']): r for r in rows}
    own_by_acc = {(r['accession'], r['data_point']): r for r in rows if (r.get('column') or 'own') == 'own'}
    ok_st = ('mapped', 'component_sum')
    for r in rows:
        if r['data_point'] != 'gross_profit' or r['status'] != 'not_presented' or (r.get('column') or 'own') != 'own': continue
        rev, cor = by.get((co(r), r['period_end'], 'revenue')), by.get((co(r), r['period_end'], 'cost_of_revenue'))
        if not (rev and cor and rev['status'] in ok_st and cor['status'] in ok_st and rev['value'] is not None and cor['value'] is not None): continue
        rc, cc = rev.get('column') or 'own', cor.get('column') or 'own'
        if rc == cc == 'own' and rev['accession'] == cor['accession'] == r['accession']:
            v = D(rev['value']) - D(cor['value']); src = None
            nodes = f"revenue={rev['value']}; -cost_of_revenue={cor['value']}"
            why = 'the income statement prints no gross profit; revenue and cost of revenue are printed in the same filing: revenue - cost of revenue (ruling C1)'
        elif cc == 'comparative':
            x = cor['accession']; xr = own_by_acc.get((x, 'revenue'))
            t = standard_inputs._one_element(xr) if xr and xr['status'] == 'mapped' else None
            if t is None: continue
            vals = {D(vv) for tt, q, vv, dd in standard_inputs._facts(comp.get(x), 4) if tt == t and int(q) == 4 and dd == str(r['period_end'])} if t else set()
            if len(vals) != 1: continue
            rv = vals.pop()
            if abs(rv - D(rev['value'])) > tol(rv, D(rev['value'])): continue   # one revenue definition: the later column ties to the own revenue cell (not MPC, NEM)
            v = rv - D(cor['value']); src = x
            nodes = f"revenue {t}={rv}; -cost_of_revenue={cor['value']} [comparative column of {x}]"
            why = f'the own filing prints no cost of revenue; the later 10-K {x} prints revenue and cost of revenue for the year: revenue - cost of revenue from that one column (ruling C1, 2026-11-14)'
        else:
            continue
        r.update(status='derived', value=v, tags='revenue-cost_of_revenue', nodes=nodes, why=why)
        if src: r.update(accession=src, column='comparative')
        r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'derived_not_printed', 'comparative_fill' if src else '') if y)
        g = corr.get(r['accession'])
        if g is not None and not src:
            da = by.get((co(r), r['period_end'], 'depreciation_and_amortization'))
            if abs(g - v) <= tol(g, v): verdict = 'ok'
            elif da and da.get('value') is not None and abs(g - (v - D(da['value']))) <= tol(g, v, D(da['value'])): verdict = 'explained: the filer fact deducts D&A, which its cost of revenue excludes (gp_filer_fact_excludes_da)'
            else: verdict = 'DISAGREE'
            r['calc_check'] = ';'.join(y for y in (r.get('calc_check', ''), f"GP corroboration: unpresented GrossProfit fact {g} {verdict}") if y)
            if verdict == 'DISAGREE': r['flags'] += ';gp_corroboration_disagree'
            elif verdict != 'ok': r['flags'] += ';gp_filer_fact_excludes_da'
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
        if beyond and dp == 'income_before_tax' and m:
            # NEM 'Income (loss) before income and mining tax and other items': the 'other items' are the lines printed after it
            # (income tax, equity income of affiliates) before the continuing-operations result; it is the pretax line itself
            L = cache.get(r['accession']) or parse(F[r['accession']])[0]
            after = []
            for l in (x for x in face(L, 'IS') if x['val'] is not None and x['ln'] > int(m.group(3))):
                if re.match(r'^(ProfitLoss|NetIncomeLoss|IncomeLossFromContinuingOperations\w*)$', l['tag']): break
                after.append(l)
            if after and all(re.search(r'IncomeTax|EquityMethod', l['tag']) for l in after) and any('EquityMethod' in l['tag'] for l in after): beyond = None
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
                     nodes=f"AccountsPayableCurrent[RelatedPartyTransactionsByRelatedParty=NonrelatedParty]={n} [face line]; AccountsPayableCurrent[RelatedPartyTransactionsByRelatedParty=RelatedParty]={rel} [face line]",
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
        out[dp] = dict(status=r['status'], tags=r.get('tags', ''), value=r['value'], r_page='', nodes=r.get('nodes', ''), why=r['why'], source='cf_family', flags='', alt=r.get('alt'))
    return out
def descendants(arcs, root, onface):
    out, stack = set(), [root]
    while stack:
        p = stack.pop()
        for c, w in (children(arcs, p, onface) or []):
            if c not in out: out.add(c); stack.append(c)
    return out
# Ruling 2026-11-14 (Dhairya): the note-only rule (§AG) serves provision_for_credit_losses and loans_net from undimensioned note facts.
# They are bank data points: a trade element (ProvisionForDoubtfulAccounts, NotesReceivableNet) is served from a note only on a bank
# income statement (net interest income printed: MS loans as NotesReceivableNet); CVS / VZ bad-debt provisions are not bank provisions
BANK_NOTE = {'provision_for_credit_losses': re.compile(r'^(ProvisionForLoan\w*|ProvisionForCreditLosses|FinancingReceivableCreditLoss\w*)$'),
             'loans_net': re.compile(r'^(LoansAndLeases\w*|FinancingReceivable\w*)$')}


def bank_face(L):
    return any(l['st'] == 'IS' and (l['tag'] == 'InterestIncomeExpenseAfterProvisionForLoanLoss' or re.match(r'(?i)^net interest( income| revenue)?$', (l['lb'] or '').strip())) for l in L)


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
            if dp in BANK_NOTE and any(not BANK_NOTE[dp].match(t) for t in parts) and not bank_face(L): continue
            vs = [notes.get((t, q)) for t in parts]
            if all(v is not None for v in vs):
                hit = dict(status='mapped' if len(parts) == 1 else 'component_sum', tags='+'.join(parts), value=sum(vs), r_page='NOTE', nodes='; '.join(f"{t}={v} [NOTE]" for t, v in zip(parts, vs)),
                           why=f"undimensioned consolidated fact {'+'.join(parts)} at the filing's own column (§AG)")
                if dp in BANK_NOTE:   # after a later 10-K's printed line for the year (GS 2016: face 182, note -138; C 2023: face 1,762, note 7,786)
                    return dict(status='not_presented', tags='', value=None, r_page='', why=f"no {dp} line on the {stmt} of this filing", alt=hit)
                return hit
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
        if ni is not None and ni.get('tags') == 'NetIncomeLossAvailableToCommonStockholdersBasic':
            isf = {l['tag']: l for l in face(L, 'IS') if l['val'] is not None}
            pref = [t for t in isf if t.startswith('PreferredStockDividends')]
            if 'ProfitLoss' in isf and pref:
                # AVGO FY2019-22: 'Net income' (ProfitLoss) - NCI is net income; the line after preferred dividends is income to common
                l = isf['ProfitLoss']; nci = isf.get('NetIncomeLossAttributableToNoncontrollingInterest')
                if nci is not None and not nci['val']: nci = None   # a printed zero NCI is no part (machine-parseable node: one tag)
                v = l['val'] - (nci['val'] if nci else 0)
                ni.update(status='derived' if nci and nci['val'] else 'mapped', tags='ProfitLoss' + ('-NetIncomeLossAttributableToNoncontrollingInterest' if nci and nci['val'] else ''), value=v, r_page=f"R{l['rep']}.htm",
                          nodes=f"ProfitLoss={l['val']} [R{l['rep']}:{l['ln']}]" + (f"; -NetIncomeLossAttributableToNoncontrollingInterest={nci['val']} [R{nci['rep']}:{nci['ln']}]" if nci else ''),
                          why=f"FALLBACK: net income is the line before preferred dividends ({pref[0]}); the bottom line is income available to common stock", source='core_fallback')
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
    standard_inputs.fsn_dropped_facts(os.environ.get('FSN_DROPPED_FACTS', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rules', 'fsn_dropped_facts.csv')), memberfacts, notefacts)
    # total_debt from the standard extract (own + comparative columns) and the committed instance evidence (total_debt.load_evidence)
    td = {(r['accession'], r['column']): r for r in total_debt.total_debt_all(filings, standard_inputs.debt_vals(filings, notefacts, compfacts), tick, os.environ.get('INSTANCE_CACHE', 'instances'))}
    # member-only face facts (_member-face-facts-2026-11-14.csv): a DPS, share count or CI printed on the face whose only own-period
    # fact carries one equity-statement column member (EquityComponents=RetainedEarnings / CommonStock ...) is the consolidated value;
    # share counts equal to shares issued (VZ, C, TMO) were rejected in the file. They enter as note facts, lineage keeps the member
    MF = {}
    resolve_cf.MEMBER_FACTS = memberfacts
    EXT['lt'] = standard_inputs.amortization_location_total(notefacts, memberfacts)
    EXT['cor'] = standard_inputs.product_service_cor(notefacts, memberfacts)
    EXT['cor_mx'] = {a: x for a, x in standard_inputs.cost_member_sums(notefacts, memberfacts).items() if a not in EXT['cor']}
    EXT['gp'] = standard_inputs.gross_profit_facts(notefacts)
    EXT['comp'] = compfacts
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
    FERR = standard_inputs.filer_xbrl_errors(os.environ.get('FILER_XBRL_ERRORS', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rules', 'filer_xbrl_errors.csv')))
    standard_inputs.apply_filer_errors(filings, notefacts, FERR)
    rows = run(filings, notefacts, tick, td)
    for r in rows:
        if r['accession'] in PRED and r['status'] in ('no_role', 'not_presented'):
            x = PRED[r['accession']]
            r.update(status='not_presented', why=f"statements of a predecessor co-registrant ({'LegalEntity ' + x['member'] if x else 'several LegalEntity members'}): the face carries no value of the filer (ruling 2026-11-14)")
            r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'coregistrant_face') if y)
    import resolve_is
    resolve_is.MEMBER_FACTS = memberfacts
    rows = resolve_is.apply(rows, filings, notefacts, tick)
    rows = apply_complement_interest(rows, filings, memberfacts)  # IS family (resolve_is.py) replaces its six data points where decisive
    rows = apply_ci_parent(rows, clines, notefacts, memberfacts)
    rows = apply_cost_and_opex(rows, filings)
    rows = apply_expenses_by_nature(rows, filings)
    rows = apply_ap_related(rows, filings)
    rows = apply_ar_related(rows, filings)
    rows += standard_inputs.before_first_10k_rows(rows, filings, compfacts)   # years printed only in the first 10-K's comparative columns
    EXT['cf'] = standard_inputs.comparative_fill(rows, compfacts, INSTANT_DPS)
    EXT['pz'] = {k: dict(v, accession=k[0], data_point=k[1]) for k, v in standard_inputs.printed_zero(rows, zlines, {r['data_point']: (r['stmt'], [x for x in (r.get('alternatives') or '').split('|') if x]) for r in ROLES}).items()}
    rows = fill_printed_zero_and_comparative(rows, td)
    rows = apply_alt(rows)
    rows = derive_gross_profit(rows)
    rows = apply_polarity(rows)
    for r in rows:   # cells whose node is a listed filer XBRL error carry the evidence
        for (a, tag, q), e in FERR.items():
            if r['accession'] == a and re.search(r'(^|; |-)' + tag + '=', r.get('nodes') or ''):
                r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'filer_xbrl_error') if x)
                r['why'] = (r.get('why') or '') + f" | filer XBRL error: {tag} stored {e['xbrl']}, printed {e['printed']} served ({e['evidence']})"
  # one sign per concept (rules/polarity.csv)
    # a face line that is only part of a total the filing reports by income-statement location (CSCO prints the opex part of
    # intangible amortization; the cost-of-sales part is a member): the location total (standard_inputs.amortization_location_total)
    LT = {}
    for r in rows:   # ruling 2026-11-14 (PM FY2022): no line and no undimensioned fact, but the filing reports the amortization by location: the member sum
        x = EXT.get('lt', {}).get(r['accession'])
        if x and r['data_point'] == 'amortization_of_intangibles' and r['status'] == 'not_presented' and r.get('column', 'own') == 'own':
            parts = [(k, v) for k, v in x['parts'].items()] if not x['total_member'] else [(x['total_member'], x['value'])]
            r.update(status='component_sum' if len(parts) > 1 else 'mapped', value=D(x['value']), tags='+'.join(['AmortizationOfIntangibleAssets'] * len(parts)),
                     nodes='; '.join(f"AmortizationOfIntangibleAssets[{x['axis']}={k}]={v} [NOTE]" for k, v in parts),
                     why=f"the filing reports intangible amortization by income-statement location only: the members' sum" + (' (another own-period fact of the element equals it)' if x.get('corroborated') else ''))
            r['flags'] = ';'.join(y for y in (r.get('flags', ''), 'location_total') if y)
    for a_, x in EXT.get('lt', {}).items():   # served when the mapped face line is smaller than the location total
        fv = next((D(r['value']) for r in rows if r['accession'] == a_ and r['data_point'] == 'amortization_of_intangibles' and r['status'] == 'mapped' and r['value'] is not None), None)
        if fv is not None and x['value'] > fv:
            LT[a_] = dict(value=str(x['value']), axis=x.get('axis'), total_member=x['total_member'], check=' + '.join(f"{k} {v / 10**6:f}".rstrip('0').rstrip('.') for k, v in x['parts'].items()) + (f" = {x['total_member']}" if x['total_member'] else ''))
    for r in rows:
        x = LT.get(r['accession'])
        if x and r['data_point'] == 'amortization_of_intangibles' and r['status'] == 'mapped' and r['value'] is not None and D(x['value']) > D(r['value']):
            face_part = r.get('nodes', '').split(' | why')[0]
            node = f"AmortizationOfIntangibleAssets[{x['axis']}={x['total_member']}]={x['value']} [NOTE]" if x['total_member'] else f"AmortizationOfIntangibleAssets={x['value']} [NOTE]"
            r.update(value=D(x['value']), nodes=node,
                     why=f"the IS face line is the operating-expense part only ({face_part}); the filing reports the total by income-statement location: {x['check']}")
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
    F = {f['a']: f for f in filings}
    for r in rows:   # lineage of member-only face facts
        t = (r.get('tags') or '').split('+')[0] or (re.match(r'(\w+)=', r.get('nodes') or '') or [None, ''])[1]
        if (r['accession'], t) in MF and r['status'] == 'mapped' and not re.search(r'\[R\d+', r.get('nodes') or ''):
            mem = MF[(r['accession'], t)]
            ps = face_positions(F.get(r['accession']), t) or [dict(rep=x_[1], ln=x_[2]) for x_ in standard_inputs._facts(clines.get(r['accession']), 4) if x_[0] == t][:1]
            seg = mem.rstrip(';')
            r['nodes'] = re.sub(r'^(\w+)=([-\d.]+) \[[^\]]*NOTE[^\]]*\]', lambda m_: f"{m_.group(1)}[{seg}]={m_.group(2)} [" + (f"R{ps[0]['rep']}.htm:{ps[0]['ln']}" if ps else ('SE' if seg.startswith('EquityComponents=') else 'NOTE')) + "]", r.get('nodes') or '')
            r['why'] = f"the face line's only own-period fact carries the equity-statement column member {mem}: the consolidated value (member-only face fact rule)"
            r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'member_face_fact') if x)
    for r in rows: r.setdefault('nodes', '')
    for r in rows: r['calc_check'] = finalize_calc(r.get('calc_check'), r['accession'] if r.get('column', 'own') == 'own' else r.get('own_accession', r['accession']), compfacts) if r.get('calc_check') else r.get('calc_check', '')
    NODE_BAD = normalize_nodes(rows, filings)   # every node in one grammar (ruling 2026-11-14)
    if NODE_BAD: print(f'nodes outside the grammar: {NODE_BAD}', file=sys.stderr)
    for r in rows:
        if str(r.get('accession', '')).startswith('BEFORE:'): r['accession'] = ''   # a year no 10-K covers and no later column printed
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
