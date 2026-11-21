"""Text-disclosure reader: amounts and explicit zeros a 10-K states only in prose (Dhairya direction 2026-11-16).

    python3 text_disclosure.py fetch CELLS.csv CACHE_DIR          (sec.gov only, the shared machine-wide SEC budget of sec_pace.py, SEC_USER_AGENT)
    python3 text_disclosure.py read  CELLS.csv CACHE_DIR OUT.csv
    python3 text_disclosure.py cells RESOLVER.csv CELLS.csv TICKERS DATA_POINTS [LATER=2]   (open cells: own 10-K + next LATER 10-Ks)

CELLS.csv: cik,ticker,data_point,period_end,accession (the OPEN cells to try; the caller passes only cells with no XBRL fact
and no face line, so XBRL always wins). OUT.csv: one row per cell with decision mapped + value_source text_stated|stated_zero
+ value, or decision open + why; section (item1|item1a|item6|item7|item7a|item8_notes|other) and the exact quoted sentence.

Rules (never infer from silence; ambiguous wording stays open):
  research_and_development  an R&D expense sentence with $ amounts; the amount must pair with the cell's fiscal year:
                            one amount and that year named, or N amounts and N years in the same order. Otherwise open.
  total_debt (zero)         'did not have any (outstanding) debt/borrowings', 'had no (outstanding) debt/borrowings',
                            'no debt outstanding' + the cell's balance-sheet date or fiscal year in the same sentence.
  dividends_paid (zero)     'did not (declare or) pay (any) (cash) dividends' / 'have never (declared or) paid (any) (cash) dividends'
                            / 'have not (declared or) paid (any) (cash) dividends' naming the fiscal year; or 'our dividend (to common
                            shareholders) has been / remains suspended' in the own filing (ruling 2026-11-16).
  dividends_per_share (0)   the same suspension statement, or 'did not declare/pay any dividends' naming the fiscal year.
  share_buybacks (zero)     'we did not (re)purchase any shares ... repurchase program' naming the fiscal year (ruling 2026-11-16: our
                            share_buybacks excludes tax-withholding transfers; the Item 5 Q4 table footnote names no year: open).
  Any 'other than', 'except', 'excluding', 'aside from', 'apart from' in a zero sentence -> open (ambiguous).
"""
import csv, html, json, os, re, sys, time, urllib.request
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sec_pace

UA = os.environ.get('SEC_USER_AGENT', '')


def get(url):
    assert url.startswith('https://www.sec.gov/'), url
    assert UA, 'set SEC_USER_AGENT'
    for i in range(4):
        sec_pace.wait()   # the shared machine-wide budget
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'}), timeout=60) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception:
            if i == 3:
                raise
            time.sleep(2 * (i + 1))


def primary_doc(cik, acc):
    idx = get(f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace("-", "")}/{acc}-index.htm')
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', idx, re.S | re.I):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)
        if len(cells) >= 4 and re.sub(r'<[^>]+>|\s', '', cells[3]).upper() in ('10-K', '10-K405', '10-KT', '20-F', '40-F'):
            m = re.search(r'href="([^"]+)"', cells[2], re.I)
            if m:
                href = m.group(1).replace('/ix?doc=', '')
                return 'https://www.sec.gov' + href if href.startswith('/') else href
    return None


def to_text(doc):
    doc = re.sub(r'(?is)<(script|style|ix:header)[^>]*>.*?</\1>', ' ', doc)
    doc = re.sub(r'(?i)<br\s*/?>|</(p|div|tr|li|h\d|table)>', '\n', doc)
    doc = html.unescape(re.sub(r'<[^>]+>', ' ', doc)).replace('\xa0', ' ')
    out = []
    for ln in (re.sub(r'[ \t]+', ' ', x).strip() for x in doc.split('\n')):
        if not ln:
            continue
        if out and re.match(r'[a-z(]', ln) and not re.search(r'[.:;]$', out[-1]):
            out[-1] += ' ' + ln          # a sentence wrapped across a block break ("...portfolio as we" / "did not have any ...")
        else:
            out.append(ln)
    return '\n'.join(out)


XREF = re.compile(r'(?i)\b(for a (more )?(complete|further|detailed)|see |refer to|discussed in|included in|of this (report|form))')


def sections(text):
    """[(start, name)] from the 10-K item headings (the LAST heading of each name, so the table of contents loses)."""
    marks = {}
    for m in re.finditer(r'(?im)^\s*item\s*(1|1a|5|6|7|7a|8)\s*[.:\-—–][^\n]*', text):
        h = re.sub(r'\s+', ' ', m.group(0)).strip()
        if XREF.search(h):                                # 'Item 1A. Risk Factors for a more complete discussion of risks.' wrapped to a line start
            continue
        if len(h) < 12:                                   # 'Item 7A.' with its title on the next line
            nxt = text[m.end():m.end() + 200].lstrip('\n').split('\n')[0]
            h = f'{h} {nxt.strip()}'
        marks[m.group(1).lower()] = (m.start(), h[:90])
    names = {'1': 'item1', '1a': 'item1a', '5': 'item5', '6': 'item6', '7': 'item7', '7a': 'item7a', '8': 'item8_notes'}
    return sorted((p, names[k], h) for k, (p, h) in marks.items())


def section_at(secs, pos):
    name = 'other'
    for p, n, _ in secs:
        if p <= pos:
            name = n
    return name


def locator(text, secs, pos):
    """'Item 7A. Quantitative and Qualitative Disclosures About Market Risk, p. 52': the item heading above the sentence and the
    page footer below it (the first standalone page-number line within 8,000 characters; omitted when none is printed)."""
    head = 'filing text'
    for p, _, h in secs:
        if p <= pos:
            head = h
    m = re.search(r'(?m)^(?:page\s*)?(\d{1,3})$', text[pos:pos + 8000], re.I)
    return f'{head}, p. {m.group(1)}' if m else head


def sentences(text):
    for m in re.finditer(r'[^.\n]*(?:\.(?!\d)[^.\n]*)*?(?:\.(?=\s|$)|\n)', text):
        s = m.group(0).strip()
        if 20 < len(s) < 1200:
            yield m.start(), s


AMT = re.compile(r'\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|thousand)?', re.I)
YR = re.compile(r'\b(?:fiscal(?: year)?\s*)?((?:19|20)\d{2})\b', re.I)
SCALE = {'thousand': Decimal(1000), 'million': Decimal(10 ** 6), 'billion': Decimal(10 ** 9), None: Decimal(1)}
AMBIG = re.compile(r'\b(other than|except|excluding|aside from|apart from|besides)\b', re.I)
RD = re.compile(r'research and development|\bR&D\b', re.I)
RD_EXP = re.compile(r'\b(expense|expenses|costs|spending|spent|expenditures)\b', re.I)
# the subject must be the company itself ('we', 'the Company'), never one facility or program ("the 2020 Credit Facility had no borrowings")
DEBT0 = re.compile(r"\b(we|the company)\s+(did not have any|had no|have no|has no|does not have any|do not have any)\s+(outstanding\s+)?"
                   r"(debt|borrowings|indebtedness)\b", re.I)
DIV0 = re.compile(r"\b(we|the company)\s+(did not|have not|has not|have never|has never)\s+(declared?\s+(or|and)\s+)?(paid|pay)\s+"
                  r"(any\s+)?(cash\s+)?dividends?\b", re.I)   # GOOG 'any cash dividend' (singular)
# Dhairya rulings 2026-11-16 (BA): a suspended common dividend stated for the filing's own year is a zero for dividends paid and DPS;
# the open-market repurchase program statement is the company's buyback zero (our share_buybacks excludes tax-withholding transfers)
DIV_SUSP = re.compile(r"\b(our|the company's|the)\s+(quarterly\s+)?(cash\s+)?dividends?\s+(to common (shareholders|stockholders)\s+|on (our )?common stock\s+)?(has|have|remains?|remained)\s+(been\s+)?suspended\b", re.I)
DPS0 = re.compile(r"\b(we|the company)\s+(did not|have not|has not|have never|has never)\s+(declare|declared|pay|paid)\s+(or\s+(pay|paid|declare|declared)\s+)?(any\s+)?(cash\s+)?dividends?\b", re.I)
BUY0 = re.compile(r"\b(we|the company)\s+did not\s+(re)?purchase\s+any\s+(shares|common stock)\b[^.]*\brepurchase program\b", re.I)
# absolute statements (no program qualifier): AMZN FY2019 'There were no repurchases of common stock in 2017, 2018, or 2019';
# DHR FY2021 'Except in connection with the Envista Split-Off in 2019, neither the Company nor any "affiliated purchaser" repurchased any
# shares of Company common stock during 2021, 2020 or 2019' (worker findings 2026-11-17)
BUY0_ABS = re.compile(r"\bthere (were|was) no (share )?repurchases? of (our |its |the company's )?common stock (in|during)\b|\b(neither the company nor [^.]{0,80}?|we did not|the company did not)\s+repurchased?\s+any\s+shares\s+of\s+(the |our )?(company )?common stock\s+(in|during)\b", re.I)
AMORT = re.compile(r'\bamortization (expense )?(of|related to|for|on|associated with) (\w+[- ])?(acquired |purchased |finite[- ]lived |definite[- ]lived |identifiable )*intangible|\bintangible assets?\s+amortization expense', re.I)
AMORT_NOT = re.compile(r'\b(estimated|expected|future|will|next|anticipated|remaining|thereafter|impairment|capitaliz|software|tax)\b', re.I)
TABLE_LB = {'amortization_of_intangibles': re.compile(r'^\s*(intangible assets? amortization expense|amortization (expense )?of (acquired |purchased |identifiable )?intangible assets?)\b', re.I),
            'research_and_development': re.compile(r'^\s*research and development( expenses?| costs?)?\b', re.I)}
RD_NOT = re.compile(r'\b(credits?|capitali[sz]ed|tax|carryforwards?|percent|%)', re.I)


def fy_labels(period_end):
    y, m = int(period_end[:4]), int(period_end[5:7])
    return {str(y)} if m >= 6 else {str(y), str(y - 1)}   # Jan-May year ends: 'fiscal 2021' may name either calendar year


def amount(a, unit):
    return Decimal(a.replace(',', '')) * SCALE[unit.lower() if unit else None]


def read_cell(text, cell):
    dp, pe = cell['data_point'], cell['period_end']
    fy = fy_labels(pe)
    own = str(cell.get('own', '1')) != '0'   # a LATER 10-K (Dhairya 2026-11-16): only statements that name the cell's year count
    secs = sections(text)
    found, ambiguous = [], []
    for pos, s in sentences(text):
        sec = section_at(secs, pos)
        if (dp == 'research_and_development' and RD.search(s) and RD_EXP.search(s) and not RD_NOT.search(s)) or \
           (dp == 'amortization_of_intangibles' and AMORT.search(s) and not AMORT_NOT.search(s)):
            amts = AMT.findall(s)
            yrs = [y for y in YR.findall(s)]
            if not amts:
                continue
            uy = list(dict.fromkeys(yrs))
            cand = [k for k, y in enumerate(uy) if y in fy]
            if len(cand) > 1 and pe[:4] in uy and max(uy) == pe[:4]:
                cand = [uy.index(pe[:4])]           # 'during 2021, 2020 and 2019' in the FY ending March 2021: 2021 is the filer's label
            if len(amts) == 1 and len(uy) == 1 and len(cand) == 1:
                found.append((amount(*amts[0]), sec, s, pos))
            elif len(amts) == len(uy) > 1 and len(cand) == 1 and re.search(r'\brespectively\b', s, re.I):
                found.append((amount(*amts[cand[0]]), sec, s, pos))
            elif cand:
                ambiguous.append((sec, s))
        elif dp == 'total_debt' and DEBT0.search(s):
            date_ok = re.search(re.escape(pe[:4]), s) if not own else (any(y in s for y in fy) or re.search(re.escape(pe[:4]), s))
            if AMBIG.search(s) or not date_ok:
                ambiguous.append((sec, s)) if date_ok else None
                continue
            found.append((Decimal(0), sec, s, pos))
        elif own and dp in ('dividends_paid', 'dividends_per_share') and DIV_SUSP.search(s) and not AMBIG.search(s) and not re.search(r'\bpreferred\b', s, re.I) \
                and not re.search(r'\b(until|through|before|prior to)\s+(19|20)\d\d\b', s, re.I):
            # 'Our dividend to common shareholders has been suspended since 2020' in the FY2025 10-K: suspended through the filing's own year
            found.append((Decimal(0), sec, s, pos))
        elif dp == 'dividends_per_share' and DPS0.search(s):
            # BA FY2023 'As a result [of the 2020 suspension], we did not pay any dividends in 2023, 2022 and 2021': the year must be named
            if AMBIG.search(s) or re.search(r'\bpreferred\b', s, re.I):
                ambiguous.append((sec, s)); continue
            if any(re.search(rf'\b{y}\b', s) for y in fy) or re.search(r'\b(have|has) never\b', s, re.I):   # GOOG 'We have never declared or paid any cash dividend'
                found.append((Decimal(0), sec, s, pos))
        elif dp == 'share_buybacks' and (BUY0.search(s) or BUY0_ABS.search(s)):
            # a leading 'Except ... in <year>,' clause takes its years out (DHR 2019, the Envista split-off exchange)
            m = re.match(r'(?is)^\s*except\b([^,]*),', s)
            if m and any(re.search(rf'\b{y}\b', m.group(1)) for y in fy):
                continue
            # the annual statement only: the cell's year named (BA FY2022 Item 7 'During the years ended December 31, 2022, 2021 and 2020,
            # we did not repurchase any shares through our open market share repurchase program'); the Item 5 table footnote speaks
            # for the fourth quarter and names no year, so it never fills the year
            if any(re.search(rf'\b{y}\b', s) for y in fy):
                found.append((Decimal(0), sec, s, pos))
        elif dp == 'dividends_paid' and DIV0.search(s):
            # the sentence must speak for the cell's year: it names the fiscal year, or says 'never' (BA FY2023 10-K: 'we did not pay
            # any dividends in 2023, 2022 and 2021')
            year_ok = any(re.search(rf'\b{y}\b', s) for y in fy) or re.search(r'\b(have|has) never\b', s, re.I)
            if AMBIG.search(s) or re.search(r'\bpreferred\b', s, re.I):
                ambiguous.append((sec, s)); continue
            if not year_ok:
                continue
            found.append((Decimal(0), sec, s, pos))
    # table lines (ETN FY2024 MD&A: '(In millions except for per share data) 2024 2023 2022' / 'Intangible asset amortization expense
    # $ 425 $ 450 $ 499'): own filing only; the header line right above names the years with the cell's year FIRST and carries the
    # scale ('in millions/thousands/billions'); the line's label is the data point's own label; first amount = the cell's year
    if own and not found and dp in TABLE_LB:
        lines = text.split('\n')
        for i, ln in enumerate(lines):
            m = TABLE_LB[dp].match(ln)
            if not m: continue
            amts = re.findall(r'\$\s?\(?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\)?', ln[m.end():])
            if len(amts) < 2: continue
            hdr = next((lines[j] for j in range(i - 1, max(i - 4, -1), -1) if len(re.findall(r'\b(?:19|20)\d{2}\b', lines[j])) >= 2), None)
            if not hdr: continue
            yrs = re.findall(r'\b((?:19|20)\d{2})\b', hdr)
            sc = re.search(r'(?i)\bin (millions|thousands|billions)\b', hdr) or re.search(r'(?i)\bin (millions|thousands|billions)\b', ' '.join(lines[max(i - 4, 0):i]))
            if not sc or yrs[0] not in fy or len(yrs) != len(amts): continue
            pos = text.find(ln)
            found.append((amount(amts[0], sc.group(1).rstrip('s')), section_at(secs, pos), f'{hdr.strip()} / {ln.strip()}', pos))
    if dp == 'sbc' and own and not found:
        found = sbc_total(text, secs, fy, pe)
    vals = {x[0] for x in found}
    if len(vals) == 1:
        v, sec, s, pos = found[0]
        return dict(decision='mapped', value_source='stated_zero' if v == 0 else 'text_stated', value=str(v), section=sec, quote=s,
                    locator=locator(text, secs, pos), quote_period=pe, why=f'stated in the filing text ({sec})')
    if len(vals) > 1:
        return dict(decision='open', value_source='', value='', section=';'.join(sorted({x[1] for x in found})), quote=' || '.join(x[2] for x in found[:3]),
                    why='text states different amounts: ' + ', '.join(str(v) for v in sorted(vals)))
    if ambiguous:
        return dict(decision='open', value_source='', value='', section=ambiguous[0][0], quote=ambiguous[0][1], why='ambiguous wording')
    return dict(decision='open', value_source='', value='', section='', quote='', why='no explicit statement in the text')


SBC_SENT = re.compile(r'(?i)compensation (cost|expense)')
SBC_AWARD = re.compile(r'(?i)\b(stock|share|restricted|option|award|performance|units?|RSUs?|PSUs?)\b')
SBC_NOT = re.compile(r'(?i)\b(ESIP|savings|401|capitaliz\w*|unrecognized|unamortized|not yet recognized|tax benefit|cash (paid|payments?|received)|settled in cash|fair value|granted|expected to be recognized|weighted)')
SBC_AMT = re.compile(r'\$\s?(\()?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*\)?\s*(million|billion|thousand)?', re.I)
AFTER_TAX = re.compile(r'\(\s*\$\s?\(?\s*[\d,.]+\s*\)?\s*after[- ]tax\)', re.I)


def _doc_scale(text):
    """'million' when the document declares its amounts in millions and never in thousands (CVX notes: 'Millions of dollars')."""
    m = len(re.findall(r'(?i)\b(millions of dollars|in millions|\(millions\))', text))
    k = len(re.findall(r'(?i)(?<!shares )\b(thousands of dollars|in thousands(?! of (?!dollars))|\(thousands\))', text))   # never 'in thousands of barrels per day' or 'Shares in thousands' (CVX)
    return 'million' if m >= 3 and k == 0 else None


def sbc_total(text, secs, fy, pe):
    """Verifier round 4 (Dhairya 2026-11-16): the share-based compensation note's own statement of the year's expense.
    One sentence -> it is the total (XOM 'The compensation cost charged against income for the restricted stock and restricted stock units
    was $ 672 million, ... for 2020, 2019, and 2018'). Two sentences, the second opening 'In addition' -> their sum (CVX 'Compensation
    expense for stock options ... was $ 94 ($ 74 after tax), ...' + 'In addition, compensation expense for stock appreciation rights,
    restricted stock, performance shares and restricted stock units was $ 96 ...'). Savings-plan (ESIP), unrecognized, tax-benefit and
    cash-settlement sentences never count; after-tax parentheticals are removed before pairing amounts with years."""
    scale = _doc_scale(text)
    parts, unparsed = [], 0
    for pos, s in sentences(text):
        subj = s.split('$', 1)[0]      # what the figure IS: the words before the first amount (CVX 2023 explains a net benefit by 'fair value' after it)
        if not (SBC_SENT.search(subj) and SBC_AWARD.search(subj)) or SBC_NOT.search(subj) or AFTER_TAX.sub('', s) == s and 'after tax' in s.lower():
            continue
        t = AFTER_TAX.sub('', s)
        yrs = list(dict.fromkeys(YR.findall(t)))
        if not any(y in fy for y in yrs): continue
        amts = SBC_AMT.findall(t)     # (sign, digits, unit); CVX 2023 '$( 100 )' is negative
        if '$' not in t: continue     # no figure stated ('No significant stock-based compensation cost was capitalized ...')
        cand = [k for k, y in enumerate(yrs) if y in fy]
        if len(cand) > 1 and pe[:4] in yrs and max(yrs) == pe[:4]:
            cand = [yrs.index(pe[:4])]
        unit = next((u for _, _, u in amts if u), None) or scale
        if not amts or len(cand) != 1 or not unit or not (len(amts) == len(yrs) and (len(amts) == 1 or re.search(r'\brespectively\b', t, re.I))):
            unparsed += 1; continue          # a sentence for the year that cannot be read: no total from the others
        neg, a, _u = amts[cand[0]]
        v = amount(a, unit)
        parts.append((-v if neg else v, section_at(secs, pos), s, pos))
    if unparsed:
        return []
    if len(parts) == 1:
        return parts
    if len(parts) == 2 and re.match(r'(?i)\s*in addition\b', parts[1][2]):
        v = parts[0][0] + parts[1][0]
        return [(v, parts[0][1], parts[0][2] + ' || ' + parts[1][2], parts[0][3])]
    return []


def fetch(cells_csv, cache):
    os.makedirs(cache, exist_ok=True)
    for c in csv.DictReader(open(cells_csv)):
        p = os.path.join(cache, c['accession'] + '.htm')       # raw document: a parser fix never needs a refetch
        if os.path.exists(p):
            continue
        url = None
        for k in dict.fromkeys((c['cik'], c['accession'][:10])):   # a predecessor's report sits under its own CIK (MRVL 1058057)
            try:
                url = primary_doc(k, c['accession'])
            except Exception:
                url = None
            if url: break
        if not url:
            print('no primary document', c['accession'], file=sys.stderr); continue
        open(p, 'w').write(f'<!-- URL {url} -->\n' + get(url))
        print('fetched', c['ticker'], c['accession'], url)


def read(cells_csv, cache, out_csv):
    rows = []
    for c in csv.DictReader(open(cells_csv)):
        p = os.path.join(cache, c['accession'] + '.htm')
        if not os.path.exists(p):
            rows.append(dict(c, decision='open', value_source='', value='', section='', quote='', why='filing text not fetched')); continue
        text = to_text(open(p).read())
        rows.append(dict(c, **read_cell(text, c)))
    with open(out_csv, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cik', 'ticker', 'data_point', 'period_end', 'accession', 'own', 'decision', 'value_source', 'value', 'section', 'locator', 'quote_period', 'quote', 'why'])
        w.writeheader(); w.writerows({k: r.get(k, '') for k in w.fieldnames} for r in rows)
    return rows


def cells(resolver_csv, out_csv, tickers, dps, later=2):
    """Candidate cells for the reader: every OPEN cell (not_presented / no_role) of the tickers and data points, read in its own 10-K
    (own=1) and in the next `later` 10-Ks of the company (own=0: only statements naming the year count)."""
    tk, dl = set(tickers.split(',')), set(dps.split(','))
    rows = [r for r in csv.DictReader(open(resolver_csv)) if r['ticker'] in tk]
    own_acc = {}
    for r in rows:
        if (r.get('column') or 'own') == 'own' and r['accession']: own_acc.setdefault(r['ticker'], {})[r['period_end']] = (r['cik'], r['accession'])
    out = []
    for r in rows:
        if r['data_point'] not in dl or r['decision'] not in ('not_presented', 'no_role'): continue
        mine = own_acc.get(r['ticker'], {})
        if r['period_end'] in mine:
            out.append(dict(cik=r['cik'], ticker=r['ticker'], data_point=r['data_point'], period_end=r['period_end'], accession=mine[r['period_end']][1], own=1))
        for pe in sorted(p for p in mine if p > r['period_end'])[:int(later)]:
            out.append(dict(cik=r['cik'], ticker=r['ticker'], data_point=r['data_point'], period_end=r['period_end'], accession=mine[pe][1], own=0))
    with open(out_csv, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cik', 'ticker', 'data_point', 'period_end', 'accession', 'own']); w.writeheader(); w.writerows(out)
    print(len(out), 'cells')


if __name__ == '__main__':
    {'fetch': lambda: fetch(*sys.argv[2:4]), 'read': lambda: read(*sys.argv[2:5]), 'cells': lambda: cells(*sys.argv[2:])}[sys.argv[1]]()
