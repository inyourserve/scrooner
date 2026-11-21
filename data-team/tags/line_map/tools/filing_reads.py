"""Filing reads: reviewed reader claims from a full 10-K read (data-team/strategy/open-shown-fixes/<TICKER>-<date>.csv),
turned into resolver claims (Dhairya 2026-11-21, item 0: "VALUE rows become served claims with the CSV's locator and quote,
HIDE rows become hide classes with evidence, RULE rows stay open; rows that contradict a ruling are listed, not applied").

    python3 filing_reads.py import RESOLVER_DIR OUT.csv SKIPPED.csv FILE.csv...
        FILE.csv: ticker,data_point,fiscal_year,outcome,value,element,accession,r_page,quote,rule_proposal,confidence.
        The fiscal year is keyed to the resolver's period for that year (the TRUE fiscal period end; a period-key defect
        of the served layer, PG 2024-09-30 / MU 2023-12-31, never creates a cell here). RULE rows and rows listed in
        rules/filing_read_skips.csv (ticker,data_point,fiscal_year,reason: a conflict with a ruling or an arithmetic
        error in the read) go to SKIPPED.csv with the reason. Everything else goes to OUT.csv (rules/filing_read_cells.csv).

apply(rows, path): the rule, run last in resolve_all (XBRL the resolver resolved itself always wins when it agrees):
  - VALUE, resolver value equal: the row keeps its node; flag `filing_read` (FILING-CHECKED by a reader).
  - VALUE, resolver value equal up to the coarser print's rounding unit: the LATER print wins (ruling e, 2026-11-21:
    "latest print wins even when it is rounded coarser", flag `rounding_vintage`); the resolver keeps its own when its
    accession is the later or the same filing.
  - VALUE, resolver blank (combined / not_presented / no_role / not_in_template) or a different value: the read claim
    is served as a text_stated row (RESOLVER-OUTPUT-FORMAT.md contract: mapped, nodes empty, quote + locator +
    quote_period = period_end; flags `filing_read;text_stated`), accession = the filing read, column own or comparative.
    A derived_not_printed row is replaced the same way (a printed figure beats an own derivation, X67).
  - HIDE: the row carries flags `filing_read_hide;<class>` (structural_not_presented, line_presented_combined, only_after_tax_disclosed,
    never_reported), the quote and locator; a valued row becomes not_presented (the reader's class is the ruling, e.g.
    DE other income FY2022-25 under ruling 9). A derived row stays as it is (counted, not served).
Nothing here is inferred: every applied row carries the exact quote and the R page of the filing read."""
import csv, os, re, sys, collections
from decimal import Decimal as D

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = os.path.join(HERE, '..', 'rules', 'filing_read_cells.csv')
SKIPS = os.path.join(HERE, '..', 'rules', 'filing_read_skips.csv')
OUT_COLS = ['cik', 'ticker', 'data_point', 'period_end', 'fiscal_year', 'outcome', 'value', 'element', 'accession', 'r_page', 'hide_class',
            'quote', 'rule_proposal', 'source_file']
HIDE_RE = re.compile(r'^HIDE\s+(structural_not_presented|line_presented_combined|never_reported|verified_absent|pre_filing|only_after_tax_disclosed)\b')
BLANK = ('combined', 'not_presented', 'no_role', 'not_in_template', 'derived', 'open')
ACC_RE = re.compile(r'\d{10}-\d{2}-\d{6}')


def _unit(v):
    """The rounding unit a figure is printed at (10^k dividing it)."""
    v = abs(D(v))
    if v == 0: return D(1)
    if v != v.to_integral(): return D(10) ** v.normalize().as_tuple().exponent
    u = D(1)
    while u < D(10) ** 9 and v % (u * 10) == 0: u *= 10
    return u


def _yy(acc):
    return (acc[11:13], acc) if acc else ('', '')


def _norm_tag(element):
    m = re.search(r'(?:us-gaap|[a-z]+):(\w+)', element or '')
    return m.group(1) if m else ''


def load(path=None):
    path = path or os.environ.get('FILING_READ_CELLS', CELLS)
    out = collections.defaultdict(list)
    if not os.path.exists(path): return out
    for t in csv.DictReader(open(path)):
        out[(str(t['cik']).lstrip('0'), t['data_point'], t['period_end'])].append(t)
    return out


def _locator(t):
    fy = f"FY{t['fiscal_year']} 10-K" if t.get('fiscal_year') else '10-K'
    el = t.get('element') or ''
    return f"{t['r_page']} ({el}) of {t['accession']}, read {fy}" if el else f"{t['r_page']} of {t['accession']}"


def apply(rows, path=None, log=None):
    """The rule (docstring above). Returns rows; log (a list) collects one tuple per applied row."""
    T = load(path)
    if not T: return rows
    for r in rows:
        if (r.get('column') or 'own') not in ('own', 'comparative') or str(r.get('accession', '')).startswith('BEFORE:'): continue
        cand = T.get((str(r.get('cik') or '').lstrip('0'), r['data_point'], str(r['period_end'])))
        if not cand: continue
        t = cand[0]
        own_acc = r.get('own_accession') or r.get('accession') or ''
        rv = D(r['value']) if r.get('value') not in (None, '') and r['status'] not in BLANK else None
        if t['outcome'] == 'VALUE':
            ev = D(t['value'])
            if rv is not None and rv == ev:
                r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'filing_read') if x)
                if log is not None: log.append(('agree', r['ticker'], r['data_point'], r['period_end']))
                continue
            if rv is not None and _unit(ev) > _unit(rv) and abs(rv - ev) <= _unit(ev) / 2:
                # ruling c (Dhairya 2026-11-21): a coarser rounding of the same figure never replaces the finer value (XOM sbc FY2024 835M, not 0.8B;
                # MRVL total_debt FY2022 4,547,977k over the FY2023 10-K's 4,548.0M). The read agrees; the finer node stays.
                r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'filing_read') if x)
                if log is not None: log.append(('agree_finer', r['ticker'], r['data_point'], r['period_end']))
                continue
            rounding = False
            was = f"{r['status']}={r.get('value')}" if rv is not None else r['status']
            r.update(status='mapped', value=ev, tags='', r_page='', nodes='', calc_check='', accession=t['accession'],
                     column='own' if t['accession'] == own_acc else 'comparative',
                     quote=t['quote'], locator=_locator(t), quote_period=str(r['period_end']),
                     why=(f"filing read ({t['source_file']}): the {('later print rounds the figure the resolver served (' + was + '); the latest print wins (ruling e, 2026-11-21)') if rounding else ('reader found the value in the filing where the resolver had ' + was)}"
                          + (f"; reader note: {t['rule_proposal']}" if t.get('rule_proposal') else '')))
            r['flags'] = ';'.join(x for x in ('filing_read', 'text_stated', 'rounding_vintage' if rounding else '', f"replaces:{was.split('=')[0]}") if x)
            if log is not None: log.append(('rounding_vintage' if rounding else 'value', r['ticker'], r['data_point'], r['period_end'], was, str(ev)))
        elif t['outcome'] == 'HIDE':
            hc = t.get('hide_class') or ''
            if r['status'] in ('derived',):   # counted, not served: the hide class is recorded, the row stays
                r['flags'] = ';'.join(x for x in (r.get('flags', ''), 'filing_read_hide', hc) if x)
                r.update(quote=t['quote'], locator=_locator(t))
                if log is not None: log.append(('hide_derived', r['ticker'], r['data_point'], r['period_end'], hc))
                continue
            was = f"{r['status']}={r.get('value')}" if rv is not None else r['status']
            if rv is not None:
                r.update(status='not_presented', value=None, tags='', r_page='', nodes='', calc_check='',
                         why=f"filing read ({t['source_file']}): {hc}; the resolver served {was}")
            r.update(quote=t['quote'], locator=_locator(t))
            r['flags'] = ';'.join(x for x in (r.get('flags', '') if rv is None else '', 'filing_read_hide', hc) if x)
            if log is not None: log.append(('hide', r['ticker'], r['data_point'], r['period_end'], hc, was))
    return rows


def import_files(resolver_dir, files, skips_path=None):
    """(kept rows, skipped rows) from the evidence files; periods from the resolver output (one annual period per year)."""
    skips = {}
    for s in csv.DictReader(open(skips_path or SKIPS)):
        for fy in re.split(r'[;\s]+', s['fiscal_year']):
            if fy: skips[(s['ticker'], s['data_point'], fy)] = s['reason']
    kept, skipped = [], []
    # X109 precedence (.87): several reads of one cell (the 2026-11-17, -21 and -22 passes) -> the latest-dated file decides;
    # the earlier rows are listed as superseded. Dated by the file name <TICKER>-<YYYY-MM-DD>.csv.
    def _date(fp): m = re.search(r'(\d{4}-\d{2}-\d{2})\.csv$', fp); return m.group(1) if m else ''
    latest = {}
    for fp in files:
        for e in csv.DictReader(open(fp, encoding='utf-8-sig')):
            k = (e['ticker'], e['data_point'], str(e['fiscal_year']))
            latest[k] = max(latest.get(k, ''), _date(fp))
    for fp in files:
        for e in csv.DictReader(open(fp, encoding='utf-8-sig')):
            tk = e['ticker']; src = os.path.basename(fp)
            res = list(csv.DictReader(open(os.path.join(resolver_dir, tk + '.csv'))))
            cik = res[0]['cik'] if res else ''
            pes = sorted({r['period_end'] for r in res if r['period_end'][:4] == str(e['fiscal_year'])})
            row = dict(cik=cik, ticker=tk, data_point=e['data_point'], period_end=pes[0] if len(pes) == 1 else '', fiscal_year=e['fiscal_year'],
                       outcome=e['outcome'], value=e['value'], element=e['element'], accession=e['accession'], r_page=e['r_page'],
                       hide_class='', quote=e['quote'], rule_proposal=e['rule_proposal'], source_file=src)
            why = None
            if _date(fp) < latest[(tk, e['data_point'], str(e['fiscal_year']))]:
                why = f"superseded by the {latest[(tk, e['data_point'], str(e['fiscal_year']))]} read of the same cell"
            elif e['outcome'] == 'RULE': why = 'RULE row: stays open (rule proposal, no value)'
            elif (tk, e['data_point'], str(e['fiscal_year'])) in skips: why = skips[(tk, e['data_point'], str(e['fiscal_year']))]
            elif len(pes) != 1: why = f"no single resolver period for fiscal year {e['fiscal_year']} ({pes})"
            elif e['outcome'] == 'VALUE' and (not e['value'] or not ACC_RE.fullmatch(e['accession'] or '') or not e['r_page'] or not e['quote']):
                why = 'VALUE row without value, accession, R page or quote'
            elif e['outcome'] == 'HIDE':
                m = HIDE_RE.match(e['quote'] or '')
                if not m: why = 'HIDE row without a hide class at the start of the quote'
                else: row['hide_class'] = m.group(1)
            elif e['outcome'] not in ('VALUE',): why = f"unknown outcome {e['outcome']}"
            if why: skipped.append(dict(row, reason=why))
            else: kept.append(row)
    return kept, skipped


if __name__ == '__main__':
    if sys.argv[1] == 'import':
        kept, skipped = import_files(sys.argv[2], sys.argv[5:])
        w = csv.DictWriter(open(sys.argv[3], 'w', newline=''), fieldnames=OUT_COLS); w.writeheader(); w.writerows(kept)
        w = csv.DictWriter(open(sys.argv[4], 'w', newline=''), fieldnames=OUT_COLS + ['reason']); w.writeheader(); w.writerows(skipped)
        print(len(kept), 'kept', len(skipped), 'skipped', collections.Counter(s['reason'].split(':')[0] for s in skipped))
