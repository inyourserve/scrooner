"""The resolver's standard inputs from one extract (tools/extract_notefacts.sql), no side files.

build_sql(ciks, tags)   fill the two placeholders of extract_notefacts.sql (sql_path=FACE_SQL_PATH: the companion extract_facelines.sql) (CIK batch, element regex from rules/roles.csv + extra tags).
merge_rows(rows, face)  append the companion query's statement-line / custom facts to vals and cvals.
split_rows(rows)        extract rows (accession, vals, mvals, cvals) -> notefacts, memberfacts, compfacts (accession -> raw string).
member_facts(...)       own-period single-member face facts -> rows of the former _member-face-facts file.
related_splits(...)     RelatedPartyTransactionsByRelatedParty Nonrelated + RelatedParty pair of one tag -> rows of _ap/_ar-related-split.
comparative_fill(...)   not_presented rows filled from the FY-1 / FY-2 column of a later 10-K that resolves the data point to one element
                        -> rows of the former _comparative-fill file.
printed_zero(...)       not_presented rows whose role element is printed on the own face with no own-period fact in any dimension (zlines)
                        -> rows of the former _printed-zero file (ruling 2026-11-14: printed dash = 0).
amortization_location_total(...)  AmortizationOfIntangibleAssets reported by income-statement location: the total -> the former
                        _amortization-location-total file.
debt_vals(...)          own + comparative undimensioned facts in the debtvals.json shape total_debt.run reads.
Side files stay a fallback in resolve_all.py / resolve_is.py until parity is shown (tools/test_standard_inputs.py)."""
import csv, os, re
from datetime import date
from decimal import Decimal as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROLES_CSV = os.path.join(HERE, '..', 'rules', 'roles.csv')
SQL_PATH = os.path.join(HERE, 'extract_notefacts.sql')
FACE_SQL_PATH = os.path.join(HERE, 'extract_facelines.sql')   # companion query: statement-line and custom family elements
MEMBER_AXES = ('EquityComponents', 'RelatedPartyTransactionsByRelatedParty', 'Scenario')
INSTANT_Q = 0


def roles_tags(roles_csv=ROLES_CSV):
    out = set()
    for r in csv.DictReader(open(roles_csv)):
        for col in ('alternatives', 'combined_if', 'parent'):
            for x in re.split(r'[|+]', r.get(col) or ''):
                if x: out.add(x)
    return out


FAMILIES_TXT = os.path.join(HERE, '..', 'rules', 'extract_families.txt')


def families(path=FAMILIES_TXT):
    """Element-family regex fragments (rules/extract_families.txt): the tags the family modules read beyond roles.csv."""
    out = []
    for line in open(path):
        line = line.strip()
        if line and not line.startswith('#'):
            assert re.fullmatch(r'[A-Za-z]+(\\w\*[A-Za-z]*)*', line), line
            out.append(line)
    return out


def build_sql(ciks, extra_tags=(), roles_csv=ROLES_CSV, sql_path=SQL_PATH, families_path=FAMILIES_TXT):
    sql = open(sql_path).read()
    tags = sorted(roles_tags(roles_csv) | set(extra_tags))
    assert all(re.fullmatch(r'\w+', t) for t in tags)
    fam = families(families_path) if families_path and os.path.exists(families_path) else []
    tags = [t for t in tags if not any(re.fullmatch(f.replace('\\w', r'\w'), t) for f in fam)] + fam   # an exact tag a family covers is dropped
    assert all(re.fullmatch(r'\d+', str(c)) for c in ciks)
    sql = sql.replace('/* element families from rules/roles.csv */', '|'.join(tags))
    return sql.replace('/* CIKs */', ','.join(str(int(c)) for c in ciks))


def split_rows(rows):
    """rows: iterable of (accession, vals, mvals, cvals[, zlines]); returns three dicts accession -> string (absent when empty).
    The zlines column is read by zero_lines()."""
    nf, mf, cf = {}, {}, {}
    for a, vals, mvals, cvals, *_ in rows:
        if vals: nf[a] = vals
        if mvals: mf[a] = mvals
        if cvals: cf[a] = cvals
    return nf, mf, cf


def merge_rows(rows, face_rows):
    """Append the companion query's rows (accession, vals, cvals[, clines]; extract_facelines.sql) to the main extract's vals / cvals."""
    face = {a: (v, c) for a, v, c, *_ in face_rows}
    out = []
    for r in rows:
        a, vals, mvals, cvals, *rest = r
        v, c = face.pop(a, (None, None))
        out.append((a, '~'.join(x for x in (vals, v) if x) or None, mvals, '~'.join(x for x in (cvals, c) if x) or None, *rest))
    out += [(a, v, None, c) for a, (v, c) in face.items()]
    return out


def face_clines(face_rows):
    """The companion query's clines column -> {accession: string} (read by ci_face_lines)."""
    return {r[0]: r[3] for r in face_rows if len(r) > 3 and r[3]}


def zero_lines(rows):
    """rows as split_rows; the fifth column (zlines) -> {accession: string}."""
    return {r[0]: r[4] for r in rows if len(r) > 4 and r[4]}


def _facts(raw, n):
    for s in (raw or '').split('~'):
        x = s.split('|')
        if len(x) == n: yield x


def _undim(notefacts, a):
    from resolve import note_facts   # one order-independent pick for duplicate facts
    return note_facts(notefacts.get(a))


COMPONENT_COLUMN = re.compile(r'EquityComponents=(AccumulatedOtherComprehensiveIncome|TreasuryStock|NoncontrollingInterest|AdditionalPaidInCapital|Parent)\w*;')


def _rounded_equal(v, ref):
    """v printed in rounded units (trailing zeros) equals ref at that precision: 441,000,000 vs 440,668,112."""
    z = len(str(int(v))) - len(str(int(v)).rstrip('0'))
    return z > 0 and (ref / D(10) ** z).quantize(D(1)) * D(10) ** z == v


def class_share_filings(filings):
    """Accessions whose balance-sheet parenthetical prints CommonStockSharesOutstanding by ClassOfStock: the class sum is the count."""
    return {f['a'] for f in filings if re.search(r'\|CommonStockSharesOutstanding\|[^~]*ClassOfStock=', f.get('cpv') or '')}


def member_facts(notefacts, memberfacts, class_shares=()):
    """A tag whose own-period column has no undimensioned fact and exactly ONE single-member fact on a statement line: that fact is the
    consolidated value (the former _member-face-facts file). Not the consolidated value, so rejected:
    - a fact in a component column of the equity statement (AOCI holds OCI only: ADP, QCOM comprehensive income; treasury: ACN shares);
    - a share count equal to shares issued; with treasury stock on the face also at the count's rounded precision (VZ, C, TMO, T, BKNG
      print issued in the equity column; TJX retires repurchased shares, so its rounded count is outstanding).
    - a share count of a filing whose parenthetical prints the count by class (class_shares: META, V; the class sum wins)."""
    out = []
    for a, raw in memberfacts.items():
        und = _undim(notefacts, a)
        by = {}
        for t, q, v, seg in _facts(raw, 4):
            by.setdefault((t, int(q)), []).append((seg, D(v)))
        for (t, q), fs in sorted(by.items()):
            if (t, q) in und or len(fs) != 1: continue
            seg, v = fs[0]
            if COMPONENT_COLUMN.match(seg): continue
            if t == 'CommonStockSharesOutstanding' and a in class_shares: continue
            iss = und.get(('CommonStockSharesIssued', q))
            treasury = any(re.fullmatch(r'TreasuryStock\w*(Value|Shares)', k) and x != 0 for (k, _), x in und.items())
            if t == 'CommonStockSharesOutstanding' and iss is not None and (iss == v or (treasury and _rounded_equal(v, iss))): continue
            out.append(dict(accession=a, tag=t, qtrs=str(q), member=seg.rstrip(';'), value=str(v.to_integral_value() if v == v.to_integral_value() else v)))
    return out


def related_splits(memberfacts, tag_re):
    """One tag printed on two face lines by RelatedPartyTransactionsByRelatedParty (NonrelatedParty and RelatedParty members), instant column:
    {accession: dict(tag, nonrelated, related)} (the former _ap-related-split / _ar-related-split files)."""
    out = {}
    for a, raw in memberfacts.items():
        by = {}
        for t, q, v, seg in _facts(raw, 4):
            m = re.fullmatch(r'RelatedPartyTransactionsByRelatedParty=(\w+);', seg)
            if m and int(q) == INSTANT_Q and re.fullmatch(tag_re, t): by.setdefault(t, {})[m.group(1)] = D(v)
        for t, d in sorted(by.items()):
            if set(d) == {'NonrelatedParty', 'RelatedParty'}:
                out[a] = dict(accession=a, tag=t, nonrelated=str(d['NonrelatedParty']), related=str(d['RelatedParty']))
    return out


NOTE_FILL_OK = {'dividends_per_share', 'basic_eps', 'diluted_eps', 'weighted_basic_shares', 'weighted_diluted_shares'}   # per-share / share counts sit in notes
FACE_NODE = re.compile(r'\[(R\d|BS parenthetical)')


def _one_element(r):
    """The ONE element a resolver row resolves to: its tags, else its single node (family rows carry the element in nodes only:
    'Goodwill=154000000 [R6.htm:11]'); a combination or a class member is not one element."""
    if r.get('tags'): return None if '+' in r['tags'] else r['tags']
    m = re.fullmatch(r'(\w+)=[^;\[]*\[[^\]]*\]', (r.get('nodes') or '').split(' | ')[0].strip())
    return m.group(1) if m else None


def comparative_fill(rows, compfacts, instant_dps):
    """rows: resolver rows (run + family replacement). For every own row 'not_presented', the later 10-Ks of the same company (next = FY-1, then FY-2) are
    looked at in order (instants: FY-1 only; the later filing must resolve the data point on its face, R page or BS parenthetical, except
    per-share and share counts), the first that resolves the data point to ONE element (status mapped, a single tag) and holds ONE undimensioned fact of that element
    at the own period_end in its own earlier column gives the value (the former _comparative-fill file: 'the next filing resolves the data point to this element').
    Returns {(own_accession, data_point): dict(accession, tag, value, window)}."""
    by = {}
    for r in rows:
        by.setdefault((r['cik'], r['data_point']), []).append(r)
    out = {}
    for lst in by.values():
        lst.sort(key=lambda r: r['period_end'])
        for r in lst:
            if r['status'] != 'not_presented': continue
            q = 0 if r['data_point'] in instant_dps else 4
            for k, w in ((1, 'FY-1'), (2, 'FY-2'))[:1 if q == 0 else 2]:   # a balance sheet prints two columns: instants fill from FY-1 only
                b = next((x for x in lst if abs((date.fromisoformat(str(x['period_end'])) - date.fromisoformat(str(r['period_end']))).days - 365 * k) <= 45), None)   # a missing year is not FY-1
                if b is None: continue
                tag = _one_element(b)
                if b['status'] != 'mapped' or not tag: continue
                if r['data_point'] not in NOTE_FILL_OK and not FACE_NODE.search(b.get('nodes') or ''): continue   # PM SG&A 162M: a note figure is not the face line
                vals = {D(v) for t, qq, v, dd in _facts(compfacts.get(b['accession']), 4) if t == tag and int(qq) == q and dd == str(r['period_end'])}
                if len(vals) == 1:
                    v = vals.pop()
                    m = re.match(re.escape(tag) + r'=(-?[\d.]+)', b.get('nodes') or '')
                    if m and b.get('value') not in (None, '') and D(b['value']) == -D(m.group(1)) != 0: v = -v   # the later cell is the fact signed by its calc weight (MDT OTTI, weight -1 toward pretax)
                    out[(r['accession'], r['data_point'])] = dict(accession=b['accession'], tag=tag, value=str(v), window=w)
                    break
    return out


def printed_zero(rows, zlines, roles):
    """A not_presented row whose data point's role element (rules/roles.csv alternatives) is a line of its own statement on the own face, with
    no own-period fact in any dimension and values in other columns (the extract's zlines): the face prints a dash or zero for the period.
    Returns {(accession, data_point): dict(tag, stmt, r_line, label)}; the first role element in roles order wins."""
    out = {}
    for r in rows:
        if r['status'] != 'not_presented' or r['data_point'] not in roles: continue
        stmt, alts = roles[r['data_point']]
        z = {}
        for s in (zlines.get(r['accession']) or '').split('~'):
            x = s.split('|')
            if len(x) == 5 and x[1] == stmt: z.setdefault(x[0], x)
        t = next((t for t in alts if t in z), None)
        if t:
            x = z[t]
            out[(r['accession'], r['data_point'])] = dict(tag=t, stmt=stmt, r_line=f"R{x[2]}:{x[3]}", label=x[4])
    return out


LOCATION_AXES = ('IncomeStatementLocation', 'StatementOfIncomeLocationBalance', 'FiniteLivedIntangibleAssetsByMajorClass')   # CSCO 2014-16, 2022 put the location members on the class axis
LOCATION_NAME = re.compile(r'(?i)cost|expense|sales|revenue|charges|operating')   # on the class axis every member must name a location (WFC: asset classes)


def amortization_location_total(notefacts, memberfacts):
    """AmortizationOfIntangibleAssets by income-statement location, own period: the total is the undimensioned fact when two or more location
    members sum to it, else the one member that equals the sum of the others (two or more). {accession: dict(value, parts)}; the resolver
    serves it when the face line it mapped is smaller (CSCO prints the operating-expense part only)."""
    out = {}
    for a, raw in memberfacts.items():
        by = {}
        for t, q, v, seg in _facts(raw, 4):
            m = re.fullmatch(r'(\w+)=(?:[\w-]+:)?(\w+);', seg)
            if t == 'AmortizationOfIntangibleAssets' and int(q) == 4 and m and m.group(1) in LOCATION_AXES:
                if m.group(1) == 'FiniteLivedIntangibleAssetsByMajorClass' and not LOCATION_NAME.search(m.group(2)):
                    by.setdefault(m.group(1), {})['__class__'] = None; continue
                by.setdefault(m.group(1), {})[m.group(2)] = D(v)
        und = _undim(notefacts, a).get(('AmortizationOfIntangibleAssets', 4))
        for ax, d in sorted(by.items()):
            if '__class__' in d: continue
            if und is not None and len(d) >= 2 and sum(d.values()) == und:
                out[a] = dict(value=und, parts=d, total_member=None); break
            tot = [k for k, v in d.items() if len(d) >= 3 and v == sum(d.values()) - v]
            if len(tot) == 1:
                out[a] = dict(value=d[tot[0]], parts={k: v for k, v in d.items() if k != tot[0]}, total_member=tot[0]); break
    return out


def debt_vals(filings, notefacts, compfacts):
    """[{cik, a, p, vals: 'tag|qtrs|ddate|value~...'}]: the own-period and earlier-column undimensioned facts of each filing, the shape
    total_debt.run reads (formerly a separate debtvals extract)."""
    out = []
    for f in filings:
        a, p = f['a'], f['p']
        v = [f"{t}|{q}|{p}|{x}" for t, q, x in _facts(notefacts.get(a), 3)] + [f"{t}|{q}|{d}|{x}" for t, q, x, d in _facts(compfacts.get(a), 4)]
        out.append(dict(cik=f['cik'], a=a, p=p, vals='~'.join(v)))
    return out


def _plain(v):
    return str(v.to_integral_value() if v == v.to_integral_value() else v.normalize())


PRODUCT = re.compile(r'Product\w*')
SERVICE = re.compile(r'Service\w*')


def product_service_cor(notefacts, memberfacts):
    """Cost of revenue printed as a product line and a service line that carry only ProductOrServiceAxis member facts (GE, MMM, TMUS, DIS):
    one CostOf* element with no undimensioned own-period fact, members only Product* (Product / ProductEquipment) and Service*, one distinct
    value per side. {accession: dict(tag, product, service)} (the former _cor-member-split file)."""
    out = {}
    for a, raw in memberfacts.items():
        und = _undim(notefacts, a)
        by = {}
        for t, q, v, seg in _facts(raw, 4):
            m = re.fullmatch(r'ProductOrService=(\w+);', seg)
            if m and int(q) == 4 and t.startswith('CostOf') and (t, 4) not in und: by.setdefault(t, []).append((m.group(1), D(v)))
        if len(by) != 1: continue
        (t, fs), = by.items()
        p = {v for k, v in fs if PRODUCT.fullmatch(k)}; s = {v for k, v in fs if SERVICE.fullmatch(k)}
        if len(p) == 1 and len(s) == 1 and all(PRODUCT.fullmatch(k) or SERVICE.fullmatch(k) for k, _ in fs):
            out[a] = dict(tag=t, product=_plain(p.pop()), service=_plain(s.pop()))
    return out


def gross_profit_facts(notefacts):
    """{accession: GrossProfit} undimensioned own-period fact (the corroboration of a derived gross profit; the former _gp-corroboration file)."""
    out = {}
    for a, raw in notefacts.items():
        v = _undim(notefacts, a).get(('GrossProfit', 4))
        if v is not None: out[a] = D(_plain(v))
    return out


CI_INCL = 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest'


def ci_face_lines(clines):
    """{accession: dict(report, line, label)}: the first line (report, line) of the comprehensive-income statement that carries the CI figure
    including NCI (extract_facelines.sql clines; the former _ci-face-lines file)."""
    out = {}
    for a, raw in clines.items():
        ls = sorted((x for x in _facts(raw, 4) if x[0] == CI_INCL), key=lambda x: (int(x[1]), int(x[2])))
        if ls: out[a] = dict(report=ls[0][1], line=ls[0][2], label=ls[0][3])
    return out


def cost_member_sums(notefacts, memberfacts):
    """A CostOf* line with no undimensioned own-period fact whose own-period facts are ProductOrService column members (MAR prints its
    income statement as a matrix: Reimbursements, Owned/leased): {accession: dict(tag, members {member: value}, total)}. The resolver
    serves the total only when it ties to the costs-and-expenses total with the other cost lines (ruling 2026-11-14)."""
    out = {}
    for a, raw in memberfacts.items():
        und = _undim(notefacts, a)
        by = {}
        for t, q, v, seg in _facts(raw, 4):
            m = re.fullmatch(r'ProductOrService=(\w+);', seg)
            if m and int(q) == 4 and t.startswith('CostOf') and (t, 4) not in und: by.setdefault(t, {}).setdefault(m.group(1), set()).add(D(v))
        if len(by) != 1: continue
        (t, ms), = by.items()
        if len(ms) < 2 or any(len(v) != 1 for v in ms.values()): continue
        mem = {k: ms[k].pop() for k in sorted(ms)}
        out[a] = dict(tag=t, members={k: _plain(v) for k, v in mem.items()}, total=_plain(sum(mem.values())))
    return out


def no_face_value(filings):
    """Accessions whose BS/IS/CF face carries no undimensioned own-period value (extract_legalentity.sql runs for these)."""
    out = []
    for f in filings:
        ls = [l.split('|') for l in (f.get('lines') or '').split('~')]
        if not any(len(x) > 8 and x[0] in ('BS', 'IS', 'CF') and x[8] for x in ls): out.append(f['a'])
    return out


def legal_entity_faces(lentity):
    """{accession: dict(member, coregistrant, facts {(tag, qtrs): value})} from extract_legalentity.sql; None for an accession whose face
    values carry more than one LegalEntity member (ambiguous)."""
    out = {}
    for a, raw in lentity.items():
        fs = list(_facts(raw, 5))
        mem = {(m, c) for _, _, _, m, c in fs}
        if len(mem) != 1: out[a] = None; continue
        (m, c), = mem
        out[a] = dict(member=m, coregistrant=c, facts={(t, int(q)): D(v) for t, q, v, _, _ in fs})
    return out


def fill_face_values(f, facts):
    """The filing's face lines with the filer member's own-period values (BS: qtrs 0, IS/CF: qtrs 4) where the line has none."""
    out = []
    for s in (f.get('lines') or '').split('~'):
        x = s.split('|')
        if len(x) > 8 and x[0] in ('BS', 'IS', 'CF') and not x[8]:
            v = facts.get((x[3], 0 if x[0] == 'BS' else 4))
            if v is not None: x[8] = str(v)
        out.append('|'.join(x))
    return dict(f, lines='~'.join(out))


EXTRACT_FROM = '2014-06-01'   # the extract's period window (extract_notefacts.sql: period>='2014-06-01')


def before_first_10k_rows(rows, filings, compfacts, start=EXTRACT_FROM):
    """Years before a company's first 10-K that its first 10-K prints in the comparative columns (GEV FY2022-23, CRWD FY2018, SNDK FY2023-24):
    one not_presented row per data point and year (flag before_first_10k), so comparative_fill serves what that 10-K prints (instants FY-1 only,
    flows FY-1 and FY-2) and the rest keeps the reason. The year's date is the first 10-K's own earlier column (the most frequent fact date
    330-400 days (FY-1) or 695-765 days (FY-2) before its period)."""
    first = {}
    for f in filings:
        if f['cik'] not in first or f['p'] < first[f['cik']]['p']: first[f['cik']] = f
    tmpl = {}
    for r in rows:
        if (r.get('column') or 'own') == 'own' and r.get('cik'): tmpl.setdefault(r['cik'].zfill(10), (r['ticker'], set()))[1].add(r['data_point'])
    out = []
    for cik, f in first.items():
        per = date.fromisoformat(f['p']); key = cik.zfill(10)
        if key not in tmpl: continue
        dates = {}
        for t, q, v, dd in _facts(compfacts.get(f['a']), 4):
            try: d = date.fromisoformat(dd)
            except ValueError: continue
            k = (per - d).days
            w = 1 if 330 <= k <= 400 else 2 if 695 <= k <= 765 and int(q) == 4 else None
            if w: dates.setdefault(w, {}).setdefault(dd, 0); dates[w][dd] += 1
        ticker, dps = tmpl[key]
        for w, c in sorted(dates.items()):
            dd = max(c, key=lambda x: (c[x], x))
            if dd < start: continue   # before the extract window: a 10-K outside the window covers it
            for dp in sorted(dps):
                out.append(dict(ticker=ticker, cik=key, accession=f'BEFORE:{key}:{dd}', period_end=dd, data_point=dp, status='not_presented', tags='', value=None, r_page='',
                                nodes='', why=f"no 10-K covers this year: it is before the company's first 10-K ({f['a']}), and that 10-K's FY-{w} column does not print the line",
                                source='before_first_10k', calc_check='', flags='before_first_10k'))
    return out


def filer_xbrl_errors(path):
    """rules/filer_xbrl_errors.csv: facts whose XBRL value differs from the value the filing prints (Dhairya ruling 2026-11-14:
    serve the printed value with evidence). {(accession, tag, qtrs): dict(xbrl, printed, evidence)}."""
    out = {}
    if not path or not os.path.exists(path): return out
    for r in csv.DictReader(open(path)):
        out[(r['accession'], r['tag'], int(r['qtrs']))] = dict(xbrl=D(r['xbrl_value']), printed=D(r['printed_value']), evidence=r['evidence'])
    return out


def apply_filer_errors(filings, notefacts, errs):
    """Replace the XBRL value by the printed one in the filing's own face lines and own-column note facts; returns the
    accessions touched. A fact whose stored value is not the listed XBRL value is left alone (the list is evidence, not a patch)."""
    hit = set()
    for (a, tag, q), e in errs.items():
        for f in filings:
            if f['a'] != a: continue
            parts = (f['lines'] or '').split('~')
            for i, s_ in enumerate(parts):
                x = s_.split('|')
                if len(x) >= 9 and x[3] == tag and x[8] not in ('', None) and D(x[8]) == e['xbrl']:
                    x[8] = str(e['printed']); parts[i] = '|'.join(x); hit.add(a)
            f['lines'] = '~'.join(parts)
        nf = notefacts.get(a)
        if isinstance(nf, str):
            parts = nf.split('~')
            for i, s_ in enumerate(parts):
                x = s_.split('|')
                if len(x) == 3 and x[0] == tag and int(x[1]) == q and D(x[2]) == e['xbrl']:
                    x[2] = str(e['printed']); parts[i] = '|'.join(x); hit.add(a)
            notefacts[a] = '~'.join(parts)
    return hit
