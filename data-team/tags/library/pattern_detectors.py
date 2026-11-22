"""Pattern detectors: the tag expert hunts every occurrence of a known gap class instead of waiting for a verifier fail.

    python3 data-team/tags/library/pattern_detectors.py                 (repo root; resolver + export detectors, no DB)
    pipeline/.venv/bin/python data-team/tags/library/pattern_detectors.py --live   (+ the FSN detectors, read-only SELECTs)

Founder 2026-11-22: "why were these gaps not found before?" Every check tested cells we already had; none asked what
else the filing states. Each pattern in patterns.csv (id, what, detector, rule id, test, card) has one detector here,
a pure function over rows the resolver (data-team/tags/line_map/resolver/<TICKER>.csv), the display export
(data-team/strategy/top100-coverage.csv) or FSN facts already hold. The run writes pattern_hits.csv (one row per hit
cell); build_library.py folds the hits into each element's known_problems, so the library shows every element's open
pattern hits. Without --live the FSN patterns keep their previous hits (marked by `source`), so a no-DB rebuild never
silently drops them.

Inputs are read, never written; outputs: data-team/tags/library/pattern_hits.csv (PATTERN_OUT overrides the directory).
"""
import argparse, csv, glob, math, os, re, sys, collections
from decimal import Decimal, InvalidOperation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RESOLVER_DIR = os.path.join(ROOT, 'data-team', 'tags', 'line_map', 'resolver')
ROLES_CSV = os.path.join(ROOT, 'data-team', 'tags', 'line_map', 'rules', 'roles.csv')
EXPORT_CSV = os.path.join(ROOT, 'data-team', 'strategy', 'top100-coverage.csv')
PATTERNS_CSV = os.path.join(HERE, 'patterns.csv')
OUT = os.environ.get('PATTERN_OUT') or HERE
HIT_COLUMNS = ['pattern_id', 'ticker', 'data_point', 'period_end', 'element', 'accession', 'layer', 'source', 'detail']
csv.field_size_limit(10 ** 8)

SERVED = ('mapped', 'component_sum', 'derived_not_printed')
SHARE_DPS = ('weighted_basic_shares', 'weighted_diluted_shares', 'shares_outstanding')
INSTANT_DPS = {'accounts_payable', 'accounts_receivable', 'cash_and_equivalents', 'current_assets', 'current_liabilities', 'deposits',
               'goodwill', 'intangible_assets', 'inventory', 'loans_net', 'ppe_net', 'shares_outstanding', 'stockholders_equity',
               'total_assets', 'total_debt', 'total_liabilities'}
NODE_RX = re.compile(r'(?:^|; )(-?)(\w+)(\[[^\]]*\])?=(-?[\d.]+) \[(R\d+\.htm:\d+|NOTE|SE|BSP)[^\]]*\]')


def D(s):
    try:
        return Decimal(str(s).strip()) if str(s).strip() not in ('', 'None') else None
    except InvalidOperation:
        return None


def rows_of(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', errors='ignore') as fh:
        return list(csv.DictReader(fh))


def nodes(r):
    """[(sign, tag, dims, value, loc)] of a resolver row's evidence (the part before ' | why')."""
    return [(s, t, d or '', D(v), loc) for s, t, d, v, loc in NODE_RX.findall((r.get('nodes') or '').split(' | why')[0])]


def hit(pid, r, detail, element='', layer='resolver', source='resolver', period=None, accession=None):
    return dict(pattern_id=pid, ticker=r.get('ticker', ''), data_point=r.get('data_point', ''),
                period_end=period or r.get('period_end', ''), element=element, accession=accession if accession is not None else r.get('accession', ''),
                layer=layer, source=source, detail=detail[:400])


# ---------------------------------------------------------------- P01 text_stated multi-year
# A stated figure: an optional $ and parenthesis, digits with thousands commas, decimals, a scale word. A figure glued to a
# letter (FY2015, R4, Note 9) or that looks like a year is a label, not a figure; one followed by % is a rate.
FIG_RX = re.compile(r'(?<![A-Za-z0-9.,])\(?\s*\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?\s*\)?\s*(billion|million|thousand|[BMK]\b)?(?![\s)]*%)(?![\d,]*[A-Za-z])')
SCALE_WORD = {'billion': 10 ** 9, 'b': 10 ** 9, 'million': 10 ** 6, 'm': 10 ** 6, 'thousand': 10 ** 3, 'k': 10 ** 3}


RUN_GAP = re.compile(r'^[\s|,;:$()\-\u2014\u2013]*(?:and)?[\s|,;:$()\-\u2014\u2013]*$')


def stated_figures(quote):
    """Runs of figures the quote states side by side (one table row or one '..., ... and ...' sentence), each run a list of
    (Decimal figure, decimals, scale or None) in printed order; years and labels skipped. Figures separated by words belong
    to different statements and never to one run."""
    runs, last_end = [], None
    for m in FIG_RX.finditer(quote or ''):
        whole, frac, word = m.group(1), m.group(2), (m.group(3) or '').lower()
        if not frac and not word and ',' not in whole and 1990 <= int(whole) <= 2040:
            last_end = None   # a year ends a run
            continue
        fig = (Decimal(whole.replace(',', '') + ('.' + frac if frac else '')), len(frac or ''), SCALE_WORD.get(word))
        if last_end is not None and runs and RUN_GAP.match(quote[last_end:m.start()]):
            runs[-1].append(fig)
        else:
            runs.append([fig])
        last_end = m.end()
    return runs


def _within(v, fig, dec, scale):
    return abs(abs(v) - fig * scale) <= Decimal(scale) / (10 ** dec) / 2


def p01_text_stated_years(resolver_rows):
    """A text_stated quote that states several figures at the row's scale, where a stated figure is served nowhere at the
    company (any data point, any period, within the printed rounding): the resolver uses fewer years than the filing states.
    GILD FY2024 'Interest income ( 281 ) ( 376 ) ( 106 )': 281 served for 2024, 376 and 106 for 2023/2022 not served."""
    by_co = collections.defaultdict(list)
    for r in resolver_rows:
        by_co[r['ticker']].append(r)
    out, seen = [], set()
    for tk, rows in by_co.items():
        served = [abs(D(r['value'])) for r in rows if r['decision'] in SERVED and D(r['value']) is not None]
        for r in rows:
            v = D(r.get('value'))
            if 'text_stated' not in (r.get('flags') or '') or not v:
                continue
            for figs in stated_figures(r.get('quote')):
                anchor = next(((i, s) for i, (f, dec, w) in enumerate(figs) for s in ([w] if w else [1, 10 ** 3, 10 ** 6, 10 ** 9])
                               if _within(v, f, dec, s)), None)
                if anchor is None or len(figs) < 2:
                    continue
                i, s = anchor
                for j, (f, dec, w) in enumerate(figs):
                    if j == i or (w and w != s) or f == 0 or (tk, r['data_point'], f * s) in seen:
                        continue
                    if not any(_within(x, f, dec, s) for x in served):
                        seen.add((tk, r['data_point'], f * s))
                        yr = int(r['period_end'][:4]) - (j - i)
                        out.append(hit('P01', r, f"quote states {f} (x{s}) for about FY{yr}; no served cell carries it; quote: {r['quote'][:160]}",
                                       period=f"{yr}{r['period_end'][4:]}"))
    return out


# ---------------------------------------------------------------- P02 one figure tagged twice at different decimals
def export_terms(r):
    """[(tag, value, accession)] of a shown export cell: each part ('Tag=value@accession#R'), else its single tag."""
    if r.get('display') != 'SHOWN_VALUE':
        return []
    parts = [re.match(r'^-?(\w+)=(-?[0-9.]+)@([0-9-]+)#', p.strip()) for p in (r.get('parts') or '').split(';') if '[' not in p and p.strip()]
    if any(parts):
        return [(m.group(1), D(m.group(2)), m.group(3)) for m in parts if m]
    tag, v = (r.get('tag') or '').strip(), D(r.get('shown_value'))
    return [(tag, abs(v), r.get('accession', ''))] if re.fullmatch(r'\w+', tag) and v is not None else []


def p02_coarser_duplicate(resolver_rows, dup_facts, export_rows=()):
    """dup_facts: {(accession, tag, ddate[:10], qtrs): [(value, dcml), ...]} with two or more distinct values (FSN, one filing,
    undimensioned). A served node whose value is the coarser of two facts that agree at the coarser precision lost to a
    rounded duplicate: the finer one must win (WMT FY2023 ShortTermBorrowings 372M dcml -6 vs 400M dcml -8)."""
    by_acc_tag = collections.defaultdict(list)
    for (acc, tag, dd, q), vals in dup_facts.items():
        by_acc_tag[(acc, tag)].append((dd, q, vals))
    out = []
    for r in resolver_rows:
        if r['decision'] not in SERVED:
            continue
        want_q = 0 if r['data_point'] in INSTANT_DPS else 4
        for _, tag, dims, val, loc in nodes(r):
            if dims or val is None:
                continue
            for dd, q, vals in by_acc_tag.get((r['accession'], tag), ()):
                if q != want_q or abs((_date(dd) - _date(r['period_end'])).days) > 7:
                    continue
                finest = max(vals, key=lambda x: x[1])
                mine = [x for x in vals if x[0] == val]
                if mine and mine[0][1] < finest[1] and finest[0] != val and _rounds_to(finest[0], mine[0][1], val):
                    out.append(hit('P02', r, f"{tag}={val} (dcml {mine[0][1]}) served; the same filing tags {finest[0]} (dcml {finest[1]}) for the same period", element=tag, source='fsn'))
    for r in export_rows:
        want_q = 0 if r['data_point'] in INSTANT_DPS else 4
        for tag, val, acc in export_terms(r):
            for dd, q, vals in by_acc_tag.get((acc, tag), ()):
                if q != want_q or abs((_date(dd) - _date(r['period_end'])).days) > 7:
                    continue
                finest = max(vals, key=lambda x: x[1])
                mine = [x for x in vals if abs(x[0]) == abs(val)]
                if mine and mine[0][1] < finest[1] and finest[0] != mine[0][0] and _rounds_to(finest[0], mine[0][1], mine[0][0]):
                    out.append(hit('P02', r, f"shown {tag}={val} (dcml {mine[0][1]}); the same filing tags {finest[0]} (dcml {finest[1]}) for the same period",
                                   element=tag, layer='export', source='fsn', accession=acc, period=r['period_end']))
    return out


def _date(s):
    import datetime
    return datetime.date.fromisoformat(str(s)[:10])


def _rounds_to(fine, dcml, coarse):
    q = Decimal(10) ** (-int(dcml))
    return (fine / q).quantize(Decimal(1), rounding='ROUND_HALF_UP') * q == coarse


# ---------------------------------------------------------------- P03 share counts off by 10^3 / 10^6
def _served_values(rows, layer):
    """{(ticker, period_end): {data_point: (value, row)}} of served values in a layer (resolver rows or export rows)."""
    out = collections.defaultdict(dict)
    for r in rows:
        if layer == 'resolver':
            if r['decision'] not in SERVED:
                continue
            v = D(r['value'])
        else:
            if r.get('display') != 'SHOWN_VALUE':
                continue
            v = D(r.get('shown_value'))
        if v is not None:
            out[(r['ticker'], r['period_end'])][r['data_point']] = (v, r)
    return out


def p03_share_scale(rows, layer='resolver'):
    """A share count whose ratio to the same period's net income / basic EPS is within a factor ~3 of 10^3 or 10^6 (either way):
    the count is stored at the printed scale (COP, RTX, SYK). |EPS| under 0.05 says nothing and is skipped."""
    out = []
    for (tk, pe), d in _served_values(rows, layer).items():
        ni, eps = d.get('net_income', (None,))[0], d.get('basic_eps', (None,))[0]
        if not ni or eps is None or abs(eps) < Decimal('0.05'):
            continue
        implied = abs(ni / eps)
        for dp in SHARE_DPS:
            if dp not in d or not d[dp][0]:
                continue
            v, r = d[dp]
            lg = math.log10(float(abs(v) / implied))
            k = min((-6, -3, 3, 6), key=lambda x: abs(lg - x))
            if abs(lg - k) < 0.5:
                el = (nodes(r)[:1] or [('', '')])[0][1] if layer == 'resolver' else (r.get('tag') or '').split('+')[0].strip('-')
                out.append(hit('P03', r, f"{dp}={v} vs net income/basic EPS = {implied:.0f}: off by 10^{k}", layer=layer, source=layer,
                               accession=r.get('accession', ''), element=el))
    return out


# ---------------------------------------------------------------- P04 undimensioned exact multiples of 100M share counts
def p04_round_share_count(resolver_rows):
    """An undimensioned share-count node that is an exact multiple of 10^8 (DIS 1,800,000,000): a cover or note figure rounded
    to hundreds of millions, not the printed count. X111 fixes shares_outstanding when the equity statement prints the count;
    any remaining hit is open."""
    out = []
    for r in resolver_rows:
        if r['data_point'] not in SHARE_DPS or r['decision'] not in SERVED:
            continue
        for _, tag, dims, val, loc in nodes(r):
            if not dims and val and val % (10 ** 8) == 0:
                out.append(hit('P04', r, f"{tag}={val} at {loc} is an exact multiple of 100M", element=tag))
    return out


# ---------------------------------------------------------------- P05 / P06 hidden year that a filing presents
def p05_p06_hidden_presented(export_rows, presented, dp_tags):
    """presented: {ticker: [(accession, form, own_period, tag, ddate, qtrs)]} undimensioned periodic-filing facts (FSN).
    A HIDDEN cell (row or year) at period P is
      P06 when the 10-K whose own period is P has a fact of the row's elements at P (the year's own 10-K presents it: WMT other
          income FY2015);
      P05 when no own 10-K does but a later 10-K or 10-Q prints P as a comparative column (WMT shares FY2024 via a 10-Q)."""
    out = []
    for r in export_rows:
        if r.get('display') not in ('HIDDEN_YEAR', 'HIDDEN_ROW') or not r.get('period_end'):
            continue
        tags = dp_tags.get(r['data_point'], set())
        q = 0 if r['data_point'] in INSTANT_DPS else 4
        pe = _date(r['period_end'])
        own, comp = [], []
        for acc, form, op, tag, dd, qt in presented.get(r['ticker'], ()):
            if tag in tags and qt == q and abs((_date(dd) - pe).days) <= 7:
                (own if form.startswith('10-K') and abs((_date(op) - pe).days) <= 7 else comp).append((acc, form, tag))
        if own:
            out.append(hit('P06', r, f"{r['display']} ({r.get('hide_class') or r.get('reason_code') or '-'}) but its own 10-K {own[0][0]} presents {own[0][2]} at {r['period_end']}",
                           element=own[0][2], layer='export', source='fsn', accession=own[0][0]))
        elif comp:
            out.append(hit('P05', r, f"{r['display']} ({r.get('hide_class') or r.get('reason_code') or '-'}) but {comp[0][1]} {comp[0][0]} prints {comp[0][2]} at {r['period_end']} as a comparative",
                           element=comp[0][2], layer='export', source='fsn', accession=comp[0][0]))
    return out


# ---------------------------------------------------------------- P07 one printed line serving two data points
# Two data points may share one printed line only when they are the same figure by definition (one line, two names) or one
# contains the other (a total and its part). Anything else counts one printed number twice.
SAME_FIGURE = {frozenset(p) for p in (('interest_income', 'total_interest_income'), ('noninterest_expense', 'operating_expenses'))}
SAME_IF_COMBINED_TAG = {frozenset(('basic_eps', 'diluted_eps')), frozenset(('weighted_basic_shares', 'weighted_diluted_shares'))}
CONTAINS = {'operating_expenses': {'sga_expense', 'research_and_development', 'amortization_of_intangibles', 'cost_of_revenue', 'noninterest_expense'},
            'total_liabilities': {'current_liabilities', 'total_debt'}, 'depreciation_and_amortization': {'amortization_of_intangibles'},
            'cost_of_revenue': {'amortization_of_intangibles'}, 'revenue': {'net_interest_income', 'noninterest_income'},
            'total_interest_income': {'interest_income'}}


def _may_share(a, b, tag, both_whole):
    pair = frozenset((a, b))
    if pair in SAME_FIGURE or (pair in SAME_IF_COMBINED_TAG and 'BasicAndDiluted' in tag):
        return True
    if both_whole:
        return False   # two data points each equal to the whole line: only the same figure by definition may do that
    return b in CONTAINS.get(a, ()) or a in CONTAINS.get(b, ())


def p07_line_double_count(resolver_rows):
    """One printed line (filing, period, element, members, R page:line) in two served data points that are neither the same
    figure by definition nor a total and its part (derived rows and differences excluded: a computation may reuse its inputs'
    lines)."""
    by = collections.defaultdict(list)
    for r in resolver_rows:
        if r['decision'] not in ('mapped', 'component_sum'):
            continue
        ns = nodes(r)
        if any(sg == '-' for sg, *_ in ns):
            continue   # a difference of printed lines is a computation (opex = gross profit - operating income), not a sum
        for _, tag, dims, val, loc in ns:
            if loc.startswith('R'):
                by[(r['ticker'], r['accession'], r['period_end'], tag, dims, loc)].append((r, len(ns) == 1))
    out = []
    for (tk, acc, pe, tag, dims, loc), lst in by.items():
        for x in range(len(lst)):
            for y in range(x + 1, len(lst)):
                (ra, wa), (rb, wb) = lst[x], lst[y]
                if ra['data_point'] != rb['data_point'] and not _may_share(ra['data_point'], rb['data_point'], tag, wa and wb):
                    for r, other in ((ra, rb), (rb, ra)):
                        out.append(hit('P07', r, f"{tag}{dims} at {loc} also serves {other['data_point']} ({other['decision']})", element=tag))
    return out


# ---------------------------------------------------------------- P08 derived values without one-filing parts
PART_RX = re.compile(r'^-?(\w+)(?:\[[^\]]*\])?=-?[0-9.]+@([0-9-]*)#(R?\d*)')


def p08_derived_parts(export_rows, resolver_rows=()):
    """A shown DERIVED cell (export class DERIVED, or a derived: badge) whose parts are missing, cite more than one filing, or
    lack an R page; a served derived_not_printed resolver row whose nodes carry no printed page (doc 02: one filing per
    derivation, every part printed)."""
    out = []
    for r in export_rows:
        if r.get('display') != 'SHOWN_VALUE' or not (r.get('class') == 'DERIVED' or (r.get('badge') or '').startswith('derived:')):
            continue
        parts = [PART_RX.match(p.strip()) for p in (r.get('parts') or '').split(';') if p.strip()]
        accs = {m.group(2) for m in parts if m}
        why = ('no parts' if not parts else 'unparseable part' if not all(parts) else
               f"parts cite {len(accs)} filings" if len(accs) > 1 else 'a part has no accession or R page' if any(not m.group(2) or not m.group(3) for m in parts) else '')
        if why:
            out.append(hit('P08', r, f"derived {r.get('tag') or '-'} value {r.get('shown_value')}: {why}", layer='export', source='export',
                           element=(r.get('tag') or '').split('+')[0].strip('-'), period=r.get('period_end')))
    for r in resolver_rows:
        if r['decision'] != 'derived_not_printed' or not D(r.get('value')):
            continue
        ns = nodes(r)
        if not ns or any(not loc.startswith('R') for *_, loc in ns):
            out.append(hit('P08', r, f"derived_not_printed with {'no nodes' if not ns else 'a node off the printed pages'}", element=ns[0][1] if ns else ''))
    return out


# ---------------------------------------------------------------- FSN facts (read-only, --live)
DUP_SQL = """
select f.accession, t.tag, v.ddate::text, v.qtrs, array_agg(distinct v.value::text || '|' || coalesce(v.dcml, 32767))
from fsn.filing f join fsn.value v on v.filing_id = f.id and v.dim_id = 0 and coalesce(v.coreg, '') = '' and v.value is not null
join fsn.tag t on t.id = v.tag_id
where f.accession = any(%(acc)s) and t.tag = any(%(tags)s) and v.qtrs in (0, 4)
group by 1, 2, 3, 4 having count(distinct v.value) > 1
"""
PRESENTED_SQL = """
select f.accession, f.form, f.period::text, t.tag, v.ddate::text, v.qtrs
from fsn.filing f join fsn.value v on v.filing_id = f.id and v.dim_id = 0 and coalesce(v.coreg, '') = '' and v.value is not null
join fsn.tag t on t.id = v.tag_id
where f.cik = %(cik)s and f.form in ('10-K', '10-K/A', '10-KT', '10-Q', '10-Q/A', '20-F', '40-F')
  and t.tag = any(%(tags)s) and v.qtrs in (0, 4) and v.ddate = any(%(dates)s::date[])
"""


def dp_tags_of(roles_csv=ROLES_CSV, resolver_rows=()):
    """data point -> the elements that print the WHOLE row: a single-element alternative of rules/roles.csv (never a part of
    an 'A+B' sum, never combined_if) that the resolver has served alone, as the mapped node of that data point, somewhere.
    A part (AmortizationOfIntangibleAssets for D&A) or a combined line on the face is not the row presented."""
    alts = collections.defaultdict(set)
    for R in rows_of(roles_csv):
        for alt in (R.get('alternatives') or '').split('|'):
            if re.fullmatch(r'\w+', alt or ''):
                alts[R['data_point']].add(alt)
    served = collections.defaultdict(set)
    for r in resolver_rows:
        ns = nodes(r)
        if r['decision'] == 'mapped' and len(ns) == 1 and not ns[0][2]:
            served[r['data_point']].add(ns[0][1])
    return {dp: alts[dp] & served[dp] for dp in alts if alts[dp] & served[dp]}


def live_facts(resolver_rows, export_rows, dp_tags, conn, timeout_ms=60000):
    import datetime
    dup, presented = {}, collections.defaultdict(list)
    cik_of = {r['ticker']: r['cik'] for r in resolver_rows}
    by_co = collections.defaultdict(list)
    for r in resolver_rows:
        by_co[r['ticker']].append(r)
    hidden, shown = collections.defaultdict(list), collections.defaultdict(list)
    for r in export_rows:
        shown[r['ticker']].append(r)
        if r.get('display') in ('HIDDEN_YEAR', 'HIDDEN_ROW') and r.get('period_end'):
            hidden[r['ticker']].append(r)
    with conn.cursor() as cur:
        cur.execute(f"set statement_timeout = {int(timeout_ms)}")
        for tk, rows in sorted(by_co.items()):
            terms = [t for r in shown.get(tk, ()) for t in export_terms(r)]
            acc = sorted({r['accession'] for r in rows if r['decision'] in SERVED and r['accession']} | {t[2] for t in terms if t[2]})
            tags = sorted({n[1] for r in rows if r['decision'] in SERVED for n in nodes(r) if not n[2]} | {t[0] for t in terms})
            if acc and tags:
                cur.execute(DUP_SQL, {'acc': acc, 'tags': tags})
                for a, t, dd, q, vals in cur.fetchall():
                    dup[(a, t, dd, int(q))] = [(Decimal(x.split('|')[0]), int(x.split('|')[1])) for x in vals]
            hs = hidden.get(tk, [])
            if hs and tk in cik_of:
                tags = sorted(set().union(*(dp_tags.get(r['data_point'], set()) for r in hs)))
                dates = sorted({(_date(r['period_end']) + datetime.timedelta(days=k)).isoformat() for r in hs for k in range(-7, 8)})
                if tags:
                    cur.execute(PRESENTED_SQL, {'cik': cik_of[tk], 'tags': tags, 'dates': dates})
                    presented[tk] = [(a, f, p, t, dd, int(q)) for a, f, p, t, dd, q in cur.fetchall()]
            conn.rollback()
    return dup, presented


# ---------------------------------------------------------------- run
FSN_PATTERNS = ('P02', 'P05', 'P06')


def load_patterns(path=PATTERNS_CSV):
    return rows_of(path)


def run(resolver_rows, export_rows, dup=None, presented=None, dp_tags=None, previous=()):
    hits = []
    hits += p01_text_stated_years(resolver_rows)
    hits += p03_share_scale(resolver_rows, 'resolver') + p03_share_scale(export_rows, 'export')
    hits += p04_round_share_count(resolver_rows)
    hits += p07_line_double_count(resolver_rows)
    hits += p08_derived_parts(export_rows, resolver_rows)
    if dup is not None:
        hits += p02_coarser_duplicate(resolver_rows, dup, export_rows)
    if presented is not None:
        hits += p05_p06_hidden_presented(export_rows, presented, dp_tags or {})
    if dup is None or presented is None:   # keep the last live run's FSN hits, marked as such
        keep = [p for p, done in (('P02', dup is not None), ('P05', presented is not None), ('P06', presented is not None)) if not done]
        hits += [dict(h, source=h['source'] if h['source'].startswith('previous:') else 'previous:' + h['source'])
                 for h in previous if h['pattern_id'] in keep]
    return sorted(hits, key=lambda h: (h['pattern_id'], h['ticker'], h['data_point'], h['period_end'], h['layer']))


def summary(hits, patterns=()):
    out = {}
    for p in [x['pattern_id'] for x in patterns] or sorted({h['pattern_id'] for h in hits}):
        hs = [h for h in hits if h['pattern_id'] == p]
        out[p] = dict(companies=len({h['ticker'] for h in hs}), cells=len({(h['ticker'], h['data_point'], h['period_end'], h['layer']) for h in hs}))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--resolver', default=RESOLVER_DIR)
    ap.add_argument('--export', default=EXPORT_CSV)
    ap.add_argument('--live', action='store_true', help='run the FSN detectors (P02, P05, P06) over DATABASE_URL, read-only')
    a = ap.parse_args(argv)
    res = [r for p in sorted(glob.glob(os.path.join(a.resolver, '*.csv'))) for r in rows_of(p)]
    exp = rows_of(a.export)
    tags = dp_tags_of(resolver_rows=res)
    dup = presented = None
    if a.live:
        import psycopg
        with psycopg.connect(os.environ.get('SCROONER_DATABASE_URL') or os.environ['DATABASE_URL']) as conn:
            conn.read_only = True
            dup, presented = live_facts(res, exp, tags, conn)
    hits = run(res, exp, dup, presented, tags, previous=rows_of(os.path.join(OUT, 'pattern_hits.csv')))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'pattern_hits.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=HIT_COLUMNS)
        w.writeheader()
        w.writerows(hits)
    pats = load_patterns()
    for p, s in summary(hits, pats).items():
        name = next((x['name'] for x in pats if x['pattern_id'] == p), '')
        print(f"{p} {name}: {s['companies']} companies x {s['cells']} cells")
    return 0


if __name__ == '__main__':
    sys.exit(main())
