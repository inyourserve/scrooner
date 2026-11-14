"""The resolver's standard inputs from one extract (tools/extract_notefacts.sql), no side files.

build_sql(ciks, tags)   fill the two placeholders of extract_notefacts.sql (CIK batch, element regex from rules/roles.csv + extra tags).
split_rows(rows)        extract rows (accession, vals, mvals, cvals) -> notefacts, memberfacts, compfacts (accession -> raw string).
member_facts(...)       own-period single-member face facts -> rows of the former _member-face-facts file.
related_splits(...)     RelatedPartyTransactionsByRelatedParty Nonrelated + RelatedParty pair of one tag -> rows of _ap/_ar-related-split.
comparative_fill(...)   not_presented rows filled from the FY-1 / FY-2 column of a later 10-K that resolves the data point to one element
                        -> rows of the former _comparative-fill file.
Side files stay a fallback in resolve_all.py / resolve_is.py until parity is shown (tools/test_standard_inputs.py)."""
import csv, os, re
from datetime import date
from decimal import Decimal as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROLES_CSV = os.path.join(HERE, '..', 'rules', 'roles.csv')
SQL_PATH = os.path.join(HERE, 'extract_notefacts.sql')
MEMBER_AXES = ('EquityComponents', 'RelatedPartyTransactionsByRelatedParty', 'Scenario')
INSTANT_Q = 0


def roles_tags(roles_csv=ROLES_CSV):
    out = set()
    for r in csv.DictReader(open(roles_csv)):
        for col in ('alternatives', 'combined_if', 'parent'):
            for x in re.split(r'[|+]', r.get(col) or ''):
                if x: out.add(x)
    return out


def build_sql(ciks, extra_tags=(), roles_csv=ROLES_CSV, sql_path=SQL_PATH):
    sql = open(sql_path).read()
    tags = sorted(roles_tags(roles_csv) | set(extra_tags))
    assert all(re.fullmatch(r'\w+', t) for t in tags)
    assert all(re.fullmatch(r'\d+', str(c)) for c in ciks)
    sql = sql.replace('/* element families from rules/roles.csv */', '|'.join(tags))
    return sql.replace('/* CIKs */', ','.join(str(int(c)) for c in ciks))


def split_rows(rows):
    """rows: iterable of (accession, vals, mvals, cvals); returns three dicts accession -> string (absent when empty)."""
    nf, mf, cf = {}, {}, {}
    for a, vals, mvals, cvals in rows:
        if vals: nf[a] = vals
        if mvals: mf[a] = mvals
        if cvals: cf[a] = cvals
    return nf, mf, cf


def _facts(raw, n):
    for s in (raw or '').split('~'):
        x = s.split('|')
        if len(x) == n: yield x


def _undim(notefacts, a):
    return {(t, int(q)): D(v) for t, q, v in _facts(notefacts.get(a), 3)}


def member_facts(notefacts, memberfacts):
    """A tag whose own-period column has no undimensioned fact and exactly ONE single-member fact on a statement line: that fact is the
    consolidated value (the former _member-face-facts file). Share counts equal to shares issued are rejected (the file's rule: VZ, C, TMO)."""
    out = []
    for a, raw in memberfacts.items():
        und = _undim(notefacts, a)
        by = {}
        for t, q, v, seg in _facts(raw, 4):
            by.setdefault((t, int(q)), []).append((seg, D(v)))
        for (t, q), fs in sorted(by.items()):
            if (t, q) in und or len(fs) != 1: continue
            seg, v = fs[0]
            if t == 'CommonStockSharesOutstanding' and und.get(('CommonStockSharesIssued', q)) == v: continue
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


def comparative_fill(rows, compfacts, instant_dps):
    """rows: resolver rows (run + family replacement). For every own row 'not_presented', the later 10-Ks of the same company (next = FY-1, then FY-2) are
    looked at in order: the first that resolves the data point to ONE element (status mapped, a single tag) and holds ONE undimensioned fact of that element
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
            for k, w in ((1, 'FY-1'), (2, 'FY-2')):
                b = next((x for x in lst if abs((date.fromisoformat(str(x['period_end'])) - date.fromisoformat(str(r['period_end']))).days - 365 * k) <= 45), None)   # a missing year is not FY-1
                if b is None: continue
                if b['status'] != 'mapped' or not b.get('tags') or '+' in b['tags']: continue
                vals = {D(v) for t, qq, v, dd in _facts(compfacts.get(b['accession']), 4) if t == b['tags'] and int(qq) == q and dd == str(r['period_end'])}
                if len(vals) == 1:
                    out[(r['accession'], r['data_point'])] = dict(accession=b['accession'], tag=b['tags'], value=str(vals.pop()), window=w)
                    break
    return out
