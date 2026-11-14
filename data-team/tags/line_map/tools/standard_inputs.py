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
    """Append the companion query's rows (accession, vals, cvals; extract_facelines.sql) to the main extract's vals / cvals."""
    face = {a: (v, c) for a, v, c in face_rows}
    out = []
    for r in rows:
        a, vals, mvals, cvals, *rest = r
        v, c = face.pop(a, (None, None))
        out.append((a, '~'.join(x for x in (vals, v) if x) or None, mvals, '~'.join(x for x in (cvals, c) if x) or None, *rest))
    out += [(a, v, None, c) for a, (v, c) in face.items()]
    return out


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
                    out[(r['accession'], r['data_point'])] = dict(accession=b['accession'], tag=tag, value=str(vals.pop()), window=w)
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
