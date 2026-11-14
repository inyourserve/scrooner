"""Cash-flow family resolver (read-only): capex, share_buybacks, dividends_paid, sbc, cf_ar_change, cf_inventory_change, cf_ap_change.
Same output format as resolve_all.py (RESOLVER-OUTPUT-FORMAT.md); merge keeps one row per key, these rows replace the 'roles' rows of the same data points.

Position, not a tag list: every CF line is assigned to a section (operating, investing, financing) by the section total that follows it on the face
(a line sits above its own section total). The element family only ranks lines that already sit in the right section.
Sign: the value is the raw XBRL fact (what the served cells store: Payments* positive = cash out; IncreaseDecrease* positive = the balance rose, i.e. a cash use).
It is never the printed sign (negating) and never abs(): the label sign is a presentation property, the stored sign is the element's own.
Rulings: capex = all capital-purchase lines of the investing section (decision register 2026-11-04 item 3: leased fleets, capitalized software, discontinued block,
turnarounds, REIT improvements, CIP; never oil and gas property or acreage); buybacks = own common stock only (item 4); a combined line is a reason, never a value."""
import csv, json, re, sys, os, collections
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve import parse, face, note_facts

TOTAL = re.compile(r'^NetCashProvidedByUsedIn(Operating|Investing|Financing)Activities(ContinuingOperations|DiscontinuedOperations)?$')
SEC = {'Operating': 'O', 'Investing': 'I', 'Financing': 'F'}

def sections(cf):
    """line -> section letter, by the next section total below it (the face lists a section's lines above its total)."""
    out, pend = {}, []
    for l in cf:
        pend.append(l)
        m = TOTAL.match(l['tag'])
        if m:
            for p in pend: out[p['ln']] = SEC[m.group(1)]
            pend = []
    return out

CAPEX = ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', 'PaymentsForProceedsFromProductiveAssets', 'PaymentsToAcquireOtherPropertyPlantAndEquipment',
         'PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets', 'PaymentsForCapitalImprovements', 'PaymentsForConstructionInProcess', 'PaymentsToAcquireOtherProductiveAssets',
         'PaymentsToAcquireAndDevelopSoftware', 'PaymentsToDevelopSoftware', 'PaymentsForSoftware', 'PaymentsToAcquireSoftware', 'PaymentsToAcquireEquipmentOnLease',
         'PaymentsToDevelopRealEstateAssets', 'PaymentsForProceedsFromNuclearFuel', 'PaymentsToAcquireTransportationEquipment', 'PaymentsToAcquireMachineryAndEquipment',
         'PaymentsToAcquireBuildings', 'PaymentsToAcquireLandHeldForUse', 'PaymentsToAcquireOtherPropertyPlantAndEquipmentExcludingBuildings',
         'PaymentsForRepurchaseOfPropertyPlantAndEquipment']
CAPEX_LABEL = re.compile(r'(?i)capital expenditure|purchases? of (property|premises|equipment|fixed assets)|additions? to (property|plant|premises|equipment|fixed)|(acquisition|purchase)s? of (property|premises|equipment)|nuclear fuel|capitalized software|software development|(expenditures|investment) (for|in) (property|plant|equipment|software)')
CORE_PPE = {'PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', 'PaymentsToAcquireOtherPropertyPlantAndEquipment', 'PaymentsForCapitalImprovements',
            'PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets', 'PaymentsToAcquireOtherProductiveAssets', 'PaymentsToAcquireTransportationEquipment', 'PaymentsToAcquireMachineryAndEquipment', 'PaymentsToAcquireBuildings'}
HARD_NOT = re.compile(r'(?i)proceeds|received|sale of|disposal|oil and gas|acreage|businesses|business combinations')
CAPEX_NOT = re.compile(r'(?i)proceeds|sale of|disposal|oil and gas|acreage|businesses|acquisitions? of (business|subsidiar|compan)|equity method|investments? in (unconsolidated|joint|affiliates)|(purchase|acquisition)s? of (securities|investments|intangible)|intangible')
BUY_LABEL = re.compile(r'(?i)(repurchase|purchases?|acquisition|retirement|buyback).*(common|treasury|capital stock|shares|own stock|stock)|treasury (stock|shares)')
BUY_NOT = re.compile(r'(?i)withh|excise|tax|employee|option|exercise|subsidiar|noncontrolling|preferred|swap|accelerated|forward|proceeds|issuance|settlement')
DIV_LABEL = re.compile(r'(?i)dividends?|distributions?')
DIV_NOT = re.compile(r'(?i)noncontrolling|non-controlling|minority|subsidiar|preferred|redeemable|unitholders? of|joint venture|partner.*other')
SBC_LABEL = re.compile(r'(?i)(stock|share|equity)[- ]based (compensation|payment)|stock compensation')
WC = {
    'cf_ar_change': dict(fam=['IncreaseDecreaseInAccountsReceivable', 'IncreaseDecreaseInReceivables', 'IncreaseDecreaseInAccountsAndOtherReceivables', 'IncreaseDecreaseInAccountsAndNotesReceivable'],
                         comb=['IncreaseDecreaseInAccountsReceivableAndOtherOperatingAssets', 'IncreaseDecreaseInReceivablesAndOtherAssets'], label=r'(?i)^(trade |accounts |net )?(accounts )?receivables?[ ,]*(net)?$|^(increase|decrease|change).*receivable'),
    'cf_inventory_change': dict(fam=['IncreaseDecreaseInInventories', 'IncreaseDecreaseInRetailRelatedInventories', 'IncreaseDecreaseInMaterialsAndSupplies'], comb=[], label=r'(?i)^inventor(y|ies)[ ,]*(net)?$'),
    'cf_ap_change': dict(fam=['IncreaseDecreaseInAccountsPayable', 'IncreaseDecreaseInAccountsPayableTrade'],
                         comb=['IncreaseDecreaseInAccountsPayableAndAccruedLiabilities', 'IncreaseDecreaseInAccountsPayableAndOtherOperatingLiabilities'], label=r'(?i)^(trade )?accounts payable[ ,]*(trade)?$'),
}

def fmt(ls):
    return '; '.join(f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]" for l in ls)

def resolve_cf(f, notes):
    """Returns {data_point: dict(status, tags, value, nodes, why, flags)} for one 10-K."""
    L, arcs = parse(f)
    cf = face(L, 'CF')
    sec = sections(cf)
    val = [l for l in cf if l['val'] is not None]
    # undimensioned note facts (own period, qtrs 4); the face line wins when it exists
    def note(tags):
        vs = [(t, notes.get((t, 4))) for t in tags]
        return [(t, v) for t, v in vs if v is not None]
    in_sec = lambda s: [l for l in val if sec.get(l['ln']) == s and not TOTAL.match(l['tag'])]
    out = {}
    def put(dp, status, tags, value, nodes, why, flags=''):
        out[dp] = dict(status=status, tags=tags, value=value, nodes=nodes, why=why, flags=flags)
    # ---- capex: every capital-purchase line of the investing section
    inv = in_sec('I')
    mem = [l for l in inv if l['tag'] in CAPEX and not HARD_NOT.search(l['lb'])]
    if not any(l['tag'] in CORE_PPE for l in mem):   # an extension line counts only when no standard PP&E line is on the section (VLO prints a VIE capex line beside PP&E: inside the standard family, not added)
        mem += [l for l in inv if l['custom'] and CAPEX_LABEL.search(l['lb']) and not CAPEX_NOT.search(l['lb'])]
    tagset = {l['tag'] for l in mem}
    if 'PaymentsToAcquirePropertyPlantAndEquipment' in tagset:   # a productive-assets line beside a PP&E line is something else (MCD restaurant purchases)
        mem = [l for l in mem if l['tag'] != 'PaymentsToAcquireProductiveAssets']
    mt = {l['tag'] for l in mem}   # a member whose calc parent is also a member is inside that parent
    inside = {c for p in mt if p in arcs for g in arcs[p].values() for c, _ in g}
    mem = [l for l in mem if l['tag'] not in inside]
    cmb = [l for l in mem if re.search(r'(?i)\band (other )?investments\b', l['lb'] or '')]
    if cmb and len(cmb) == len(mem):   # NEE: a combined segment line beside other capex lines stays in the sum (Dhairya ruling: NEE capex = sum of the segment lines); PSX 'Capital expenditures and investments': capex printed together with investments in affiliates (founder ruling 2026-11-01 item 3: a combined line is never one concept)
        put('capex', 'combined', '+'.join(l['tag'] for l in cmb), None, fmt(cmb), "CF investing section: the capital-purchase line also holds investments ('" + cmb[0]['lb'] + "'): combined")
    elif mem:
        put('capex', 'mapped' if len(mem) == 1 else 'component_sum', '+'.join(l['tag'] for l in mem), sum(l['val'] for l in mem), fmt(mem),
            "CF investing section: capital-purchase line(s) (register 2026-11-04 item 3)" + ('; sum of ' + str(len(mem)) if len(mem) > 1 else ''))
    else:
        put('capex', 'not_presented', '', None, '', 'no capital-purchase line in the investing section of this filing')
    # ---- buybacks: own common stock, financing section
    fin = in_sec('F')
    bb = [l for l in fin if l['tag'] in ('PaymentsForRepurchaseOfCommonStock', 'PaymentsForRepurchaseOfEquity')]
    if not bb:
        bb = [l for l in fin if l['custom'] and BUY_LABEL.search(l['lb']) and not BUY_NOT.search(l['lb'])]
    if bb:
        put('share_buybacks', 'mapped' if len(bb) == 1 else 'component_sum', '+'.join(l['tag'] for l in bb), sum(l['val'] for l in bb), fmt(bb), 'CF financing: repurchase of own common stock (register item 4)')
    else:
        n = note(['PaymentsForRepurchaseOfCommonStock', 'PaymentsForRepurchaseOfEquity'])
        if n: put('share_buybacks', 'mapped', n[0][0], n[0][1], f'{n[0][0]}={n[0][1]} [NOTE]', 'undimensioned consolidated note fact at the filing own column (par. AG)')
        else: put('share_buybacks', 'not_presented', '', None, '', 'no own-stock repurchase line in the financing section nor an undimensioned note fact')
    # ---- dividends: financing section; common (or the unlabelled total) beside no separate common line
    com = [l for l in fin if l['tag'] in ('PaymentsOfDividendsCommonStock', 'PaymentsOfOrdinaryDividends')]
    tot = [l for l in fin if l['tag'] in ('PaymentsOfDividends', 'PaymentsOfCapitalDistribution', 'CashDistributionsToStockholders')]  # REIT 'Cash distributions to stockholders' (WELL)
    cus = [l for l in fin if l['custom'] and DIV_LABEL.search(l['lb']) and not DIV_NOT.search(l['lb'])]
    ncom = note(['PaymentsOfDividendsCommonStock'])
    pick = com or tot or ([] if ncom else (cus if len(cus) == 1 else []))
    # preferred inside a single generic dividend line: the data point is common dividends (roles.csv: never preferred). When the
    # filing reports preferred dividends and the financing section prints no separate preferred line, a generic line ('Cash
    # dividends paid', BAC; 'Dividends paid to shareholders', GE) holds both: combined. A label naming only common stays mapped;
    # a label naming only preferred means no common dividend line (BA, TMUS)
    pref = [l for l in L if l['val'] and re.search(r'Preferred\w*Dividend|Dividend\w*Preferred', l['tag']) and (not re.search(r'OtherAdjustments', l['tag']) or re.search(r'(?i)preferred', l['lb'] or ''))]  # 'and other adjustments' counts only when its label names preferred (GOOG's Class C adjustment does not)
    cfpref = [l for l in fin if re.search(r'Preferred', l['tag']) and re.search(r'Dividend', l['tag']) or (DIV_LABEL.search(l['lb'] or '') and re.search(r'(?i)preferred', l['lb'] or '') and not re.search(r'(?i)common', l['lb'] or ''))]
    if len(pick) == 1 and pick[0]['tag'] in ('PaymentsOfOrdinaryDividends', 'PaymentsOfDividends') and pref:
        lb = pick[0]['lb'] or ''
        names_c, names_p = bool(re.search(r'(?i)common', lb)), bool(re.search(r'(?i)preferred', lb))
        if names_p and not names_c:
            put('dividends_paid', 'not_presented', '', None, fmt(pick), f"the only financing dividend line '{lb}' is preferred dividends; no common dividend line", flags='dividends_preferred_only'); pick = None
        elif (names_p and names_c) or (not names_c and not [l for l in cfpref if l is not pick[0]]):
            put('dividends_paid', 'combined', pick[0]['tag'], None, fmt(pick) + '; ' + fmt(pref[:1]), f"the single financing line '{lb}' holds common and preferred dividends (the filing reports {pref[0]['tag']}={pref[0]['val']}; no separate preferred line): common dividends are not printed", flags='dividends_incl_preferred'); pick = None
    if pick is None:
        pass
    elif pick:
        put('dividends_paid', 'mapped', '+'.join(l['tag'] for l in pick), sum(l['val'] for l in pick), fmt(pick), 'CF financing: common dividends / distributions (REIT and MLP distributions count; never NCI)')
    else:
        n = note(['PaymentsOfDividendsCommonStock', 'PaymentsOfDividends', 'PaymentsOfOrdinaryDividends'])
        if n: put('dividends_paid', 'mapped', n[0][0], n[0][1], f'{n[0][0]}={n[0][1]} [NOTE]', 'undimensioned consolidated note fact at the filing own column (par. AG)')
        else: put('dividends_paid', 'not_presented', '', None, '', 'no dividend line in the financing section nor an undimensioned note fact')
    # ---- sbc: operating add-back; a custom line that names another item too is not pure
    op = in_sec('O')
    sb = [l for l in op if l['tag'] == 'ShareBasedCompensation']
    if not sb:
        cl = [l for l in op if l['custom'] and SBC_LABEL.search(l['lb']) and not re.search(r'And', re.sub(r'ShareBased|StockBased', '', l['tag']))]
        sb = cl if len(cl) == 1 else []
    # a ShareBasedCompensation line whose own label names no compensation/expense ('Share-based payments', MA FY2014-16: -15 / 22 / 50)
    # and whose value is not the filing's own SBC expense (AllocatedShareBasedCompensationExpense 111 / 122 / 148) is not the
    # add-back (10-K 0001141391-15-000011 note: 'Share-based compensation expense ... $111'): the SBC ruling takes the note fact
    exp = note(['AllocatedShareBasedCompensationExpense'])
    if sb and exp and not re.search(r'(?i)compensation|expense|award|plans?\b', sb[0]['lb'] or '') and sb[0]['val'] != exp[0][1]:
        put('sbc', 'mapped', exp[0][0], exp[0][1], f"{exp[0][0]}={exp[0][1]} [NOTE]; face {fmt(sb)} not used",
            f"the CF line '{sb[0]['lb']}' ({sb[0]['val']}) names no compensation expense and differs from the filing's SBC expense: note fact (SBC ruling)", flags='sbc_face_not_addback')
    elif sb:
        put('sbc', 'mapped', sb[0]['tag'], sb[0]['val'], fmt(sb), 'CF operating section: share-based compensation add-back')
    else:
        n = note(['ShareBasedCompensation', 'AllocatedShareBasedCompensationExpense', 'RestrictedStockExpense'])
        if n: put('sbc', 'mapped', n[0][0], n[0][1], f'{n[0][0]}={n[0][1]} [NOTE]', 'undimensioned consolidated note fact at the filing own column (par. AG)')
        else: put('sbc', 'not_presented', '', None, '', 'no share-based compensation line on the CF nor an undimensioned note fact')
    # ---- working-capital lines: operating section, else the undimensioned note fact; only a combined line on the face is a reason
    for dp, spec in WC.items():
        ln = [l for l in op if l['tag'] in spec['fam']]
        ln = sorted(ln, key=lambda l: spec['fam'].index(l['tag']))[:1]
        if not ln:
            cl = [l for l in op if l['custom'] and re.search(spec['label'], l['lb'])]
            ln = cl if len(cl) == 1 else []
        if not ln and dp == 'cf_ar_change':   # the receivables line filed under the other-receivables element (GEV 'current receivables'), never a vendor/other line beside a trade line
            orl = [l for l in op if l['tag'] == 'IncreaseDecreaseInOtherReceivables' and re.search(r'(?i)receivable', l['lb']) and not re.search(r'(?i)other|vendor|non-?trade|related', l['lb'])]
            ln = orl if len(orl) == 1 else []
        if ln:
            put(dp, 'mapped', ln[0]['tag'], ln[0]['val'], fmt(ln), 'CF operating section: working-capital line')
            continue
        n = note(spec['fam'])
        if len({v for _, v in n}) > 1:
            put(dp, 'no_role', '', None, '; '.join(f'{t}={v} [NOTE]' for t, v in n), 'two undimensioned note facts of this role disagree: reader check', 'READER CHECK ambiguous note facts'); continue
        if n: put(dp, 'mapped', n[0][0], n[0][1], f'{n[0][0]}={n[0][1]} [NOTE]', 'undimensioned consolidated note fact at the filing own column (par. AG); the face prints only aggregates')
        else:
            cm = [l for l in op if l['tag'] in spec['comb']]
            if cm: put(dp, 'combined', cm[0]['tag'], cm[0]['val'], fmt(cm[:1]), f"CF face prints only the combined line {cm[0]['tag']} '{cm[0]['lb']}'")
            else: put(dp, 'not_presented', '', None, '', f'no {dp} line in the operating section nor an undimensioned note fact')
    return out

DPS = ['capex', 'share_buybacks', 'dividends_paid', 'sbc', 'cf_ar_change', 'cf_inventory_change', 'cf_ap_change']

def run(filings, cfnotes, tick, version='resolver-cf-2026-11-14.1'):
    rows = []
    for f in filings:
        tk = tick.get(f['cik'].zfill(10))
        if not tk: continue
        notes = note_facts(cfnotes.get(f['a']))
        res = resolve_cf(f, notes)
        for dp in DPS:
            r = res[dp]; v = r['value']
            rows.append(dict(cik=f['cik'].zfill(10), ticker=tk, data_point=dp, period_end=f['p'], grain='FY', decision=r['status'],
                             nodes=(r['nodes'] + ' | why: ' + r['why']) if r['nodes'] else 'why: ' + r['why'],
                             value='' if v is None or r['status'] in ('combined', 'not_presented') else str(D(v).normalize() if D(v) != D(v).to_integral() else D(v).to_integral()),
                             accession=f['a'], column='own', calc_check='', flags='roles:cf', resolver_version=version))
    return rows

if __name__ == '__main__':
    filings = json.load(open(sys.argv[1])); cfnotes = json.load(open(sys.argv[2]))
    tick = {r[1].zfill(10): r[0] for r in csv.reader(open(sys.argv[3]))}
    rows = run(filings, cfnotes, tick)
    rows.sort(key=lambda r: (r['ticker'], r['period_end'], r['data_point']))
    w = csv.DictWriter(open(sys.argv[4], 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), collections.Counter(r['decision'] for r in rows))
