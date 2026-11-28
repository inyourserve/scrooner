"""Balance-sheet family resolver (read-only): cash_and_equivalents, accounts_receivable, inventory, accounts_payable, goodwill,
intangible_assets, ppe_net, shares_outstanding, and the unclassified-balance-sheet reasons for current_assets / current_liabilities.

Same output format as resolve_all.py (RESOLVER-OUTPUT-FORMAT.md). Rules are data: rules/roles.csv rows for these data points (alternatives,
combined_if, note_ok, custom_label, ruling); this module only supplies the position logic.

What it adds over resolve_all.role():
  1. POSITION, not the calc descendant test: a current-asset role is a face line printed above the AssetsCurrent subtotal (below it for
     liabilities: between the asset total and LiabilitiesCurrent); an unclassified balance sheet uses the whole asset (liability) side.
     The calc tree only ranks (PG InventoryNet and MO InventoryNet sit outside AssetsCurrent's calc group but inside its position).
  2. Instants read note facts at qtrs 0 (resolve_all looked them up at qtrs 4, so every note-only goodwill / inventory / PP&E was
     not_presented: JPM, GS, AXP, COST, TSLA, VLO ...).
  3. Component lines (finished goods, gross inventory) are never the role when a total of the same family is printed.
  4. shares_outstanding: the undimensioned balance-sheet-date count, else the sum over ClassOfStock members of the balance-sheet
     parenthetical (a class sum, never dei), else not_presented.
  5. Unclassified balance sheet (no AssetsCurrent / LiabilitiesCurrent on the face): current assets / liabilities are not_presented
     (Dhairya ruling 2026-11-14).
Rulings: cash = the BS 'cash and cash equivalents' total (BAC 159B, not CashAndDueFromBanks alone); bank goodwill = the undimensioned
fact at the BS date."""
import csv, json, os, re, sys, collections
from decimal import Decimal as D
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from resolve import parse, face, tol, children, note_facts

ROLES_CSV = os.environ.get('ROLES_CSV', os.path.join(HERE, '..', 'rules', 'roles.csv'))
ROLES = {r['data_point']: r for r in csv.DictReader(open(ROLES_CSV))}
FAMILY = ('cash_and_equivalents', 'accounts_receivable', 'inventory', 'accounts_payable', 'goodwill', 'intangible_assets', 'ppe_net', 'shares_outstanding')
COMPONENT = re.compile(r'^(Inventory(FinishedGoods|RawMaterials|WorkInProcess|Gross)|InventoryFinishedGoodsNetOfReserves)')
EQ_STOP = re.compile(r'(?i)preferred|treasury|restricted|unvested|nonvoting')
WIDER_LB = re.compile(r'(?i)\band (other|prepaid|accrued)\b|\bother assets\b')
CLASS_SEG = re.compile(r'ClassOfStock=([A-Za-z0-9_]+)')


def regions(bs):
    """(asset_region, liab_region, classified_assets, classified_liabs): lines with a value, by face position."""
    by = {}
    for l in bs:
        if l['val'] is not None: by.setdefault(l['tag'], l)
    ta = by.get('Assets'); ac = by.get('AssetsCurrent'); lc = by.get('LiabilitiesCurrent'); lse = by.get('LiabilitiesAndStockholdersEquity')
    a_end = (ac or ta or {}).get('ln')
    asset = [l for l in bs if l['val'] is not None and a_end is not None and l['ln'] < a_end]
    l_start = ta['ln'] if ta else 0
    l_end = lc['ln'] if lc else (lse['ln'] if lse else 10 ** 6)
    liab = [l for l in bs if l['val'] is not None and l_start < l['ln'] < l_end]
    return by, asset, liab, ac is not None, lc is not None


CASH_TOTAL = re.compile(r'(?i)^(total )?cash and (cash )?equivalents$')
CASH_RESTRICTED_TOTAL = re.compile(r'(?i)^(total )?cash,? (and )?cash equivalents,? (and )?restricted cash\b')


def cash_subtotal(r, lines, arcs):
    """Ruling 2026-11-14 (Dhairya, AXP 2023 46,596): cash = the face TOTAL labelled cash and cash equivalents. When the picked line is a component
    whose calc parent on the face (in the same asset region) is labelled '(Total) cash and cash equivalents', the parent is the role; climb while
    that holds. A parenthetical in the label ('(includes restricted cash: ...)', AXP 2024) is disclosure of what the printed total contains and is
    flagged. Ruling 2026-11-14 (WFC, PGR; as GE, INTC, PG): when the face's only cash-equivalents total is 'Total cash, cash equivalents, and
    restricted cash', that total is the cell, flagged includes_restricted. A total naming short-term investments / marketable securities stays out."""
    if not arcs or r is None or r.get('rule') != 'face' or r['status'] != 'mapped': return r
    on = {l['tag']: l for l in lines}
    t = r['nodes'].split('=')[0]; climbed = []
    while True:
        par = [p for p in on if p != t and t in {c for c, w in (children(arcs, p, on) or [])} and CASH_TOTAL.match(on[p]['lb'].split('(')[0].strip())]
        if not par and not any(CASH_TOTAL.match(l['lb'].split('(')[0].strip()) for l in lines):   # no cash-and-cash-equivalents total on the face
            par = [p for p in on if p != t and t in {c for c, w in (children(arcs, p, on) or [])} and CASH_RESTRICTED_TOTAL.match(on[p]['lb'])]
        if len(par) != 1: break
        climbed.append(t); t = par[0]
    if not climbed: return r
    l = on[t]; paren = '(' in l['lb']; restr = bool(CASH_RESTRICTED_TOTAL.match(l['lb']))
    return dict(status='mapped', value=l['val'], nodes=f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]", rule='face',
                why=f"BS face total '{l['lb']}' (calc parent of {', '.join(climbed)}): cash is the face total {'including restricted cash (the face prints no cash-and-cash-equivalents total)' if restr else 'labelled cash and cash equivalents'}, not its first component (rulings 2026-11-14)",
                flags='cash_face_subtotal' + (';label_parenthetical' if paren else '') + (';includes_restricted' if restr else ''))


INV_CLASS_LB = re.compile(r'(?i)inventor|materials?|suppl(y|ies)|stockpiles?|products?|finished goods|work[- ]in[- ]process|raw|merchandise|fuel|crude|ore\b|metals?|parts|spares|land held|homes?')   # FSN marks some new standard elements custom (CEG RenewableEnergyCredits)
INV_HEADER = re.compile(r'(?i)^inventor(y|ies)\s*:?$')


def inventory_header_sum(bs, r, notes=None):
    """Ruling 2026-11-14 (Dhairya, FCX): lines printed under an 'Inventories:' header with no inventory total are a component_sum,
    flag header_sum. The group is the run of valued lines after the header while each line is an inventory element or a custom
    line whose label names an inventory class (FCX 'Product', 'Mill and leach stockpiles'; not CEG 'Renewable energy credits'); it ends at the
    first other line, abstract or total
    label; when the filing reports an undimensioned InventoryNet, the group is the shortest run that sums to it (none ties: no header sum).
    A picked face line outside the group (a printed total) stands; a pick inside it, a note fact or none is replaced."""
    hs = [i for i, l in enumerate(bs) if l['tag'].endswith('Abstract') and (INV_HEADER.match((l['lb'] or '').strip()) or re.match(r'^Inventor\w*Abstract$', l['tag']))]
    if len(hs) != 1: return None
    grp = []
    for l in bs[hs[0] + 1:]:
        if l['tag'].endswith('Abstract') or l['prole'] == 'totalLabel' and not re.search(r'(?i)inventor', l['lb'] or '') and grp: break
        if l['prole'] == 'totalLabel' and re.search(r'(?i)inventor', l['lb'] or ''): return None   # an inventory total is printed: the normal pick
        if not (re.search(r'Inventor|Stockpile', l['tag']) or (l['custom'] and INV_CLASS_LB.search(l['lb'] or ''))): break
        if l['val'] is not None: grp.append(l)
    tot = (notes or {}).get('InventoryNet')
    if tot is not None:   # the filing reports its inventory total: the group is the run from the header that sums to it (CEG: RECs follow)
        k = next((k for k in range(2, len(grp) + 1) if abs(sum(l['val'] for l in grp[:k]) - tot) <= tol(tot, *[l['val'] for l in grp[:k]])), None)
        if k is None: return None
        grp = grp[:k]
    if len(grp) < 2: return None
    if r and r.get('rule') == 'face' and not any(l['tag'] in (r.get('nodes') or '') for l in grp): return None
    return dict(status='component_sum', value=sum(l['val'] for l in grp), nodes='; '.join(f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]" for l in grp),
                why=f"BS face lines under the '{bs[hs[0]]['lb']}' header with no inventory total: their sum (ruling 2026-11-14)", rule='face', flags='header_sum')


SALE_RECV = re.compile(r'(?i)from the sale of|commercialization rights')   # MO 2022: 'Receivable from the sale of IQOS System commercialization rights' is not a trade receivable


def pick(R, lines, notes, dp):
    """First alternative (rank order) that holds the role among `lines`; then combined; then custom label; then the instant note fact."""
    alts = [a.split('+') for a in R['alternatives'].split('|') if a]
    comb = [t for t in R['combined_if'].split('|') if t]
    bytag = {}
    for l in lines: bytag.setdefault(l['tag'], l)
    tot_family = {t for t in bytag if not COMPONENT.match(t)} if dp == 'inventory' else None
    for parts in alts:
        if all(t in bytag for t in parts):
            if dp == 'inventory' and len(parts) == 1 and COMPONENT.match(parts[0]) and any(t.startswith('Inventory') and not COMPONENT.match(t) and t != 'InventoryNetAbstract' for t in bytag):
                continue
            ls = [bytag[t] for t in parts]
            return dict(status='mapped' if len(ls) == 1 else 'component_sum', value=sum(l['val'] for l in ls), nodes='; '.join(f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]" for l in ls),
                        why=f"BS face {'+'.join(parts)} by position (printed {'above AssetsCurrent' if dp in ('cash_and_equivalents', 'accounts_receivable', 'inventory') else 'in its section'}; the tag ranks)", rule='face')
    if R['custom_label']:
        cl = [l for l in lines if l['custom'] and re.search(R['custom_label'], l['lb'], re.I) and not SALE_RECV.search(l['lb'])]
        if len(cl) == 1:
            l = cl[0]
            if WIDER_LB.search(l['lb']):   # WELL 'Receivables and other assets' (wave 4A WRONG served value): the line holds other items too
                return dict(status='combined', value=l['val'], nodes=f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]", why=f"BS face prints the role only inside '{l['lb']}', which names other items too: combined", rule='face')
            return dict(status='mapped', value=l['val'], nodes=f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]", why=f"BS face custom line whose own label names the role: '{l['lb']}'", rule='face')
    if dp == 'accounts_receivable':   # WELL FY2019-21 'Receivables and other assets' (OtherAssets): the receivables sit inside a wider face line;
        # a note fact (WELL's AccountsReceivableNet is 'Non real estate loans receivable') never stands in for them (wave 4A)
        wl = [l for l in lines if re.search(r'(?i)\breceivables?\b', l['lb'] or '') and WIDER_LB.search(l['lb'] or '') and l['val'] is not None and not SALE_RECV.search(l['lb'])]
        if len(wl) == 1:
            l = wl[0]
            return dict(status='combined', value=l['val'], nodes=f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]", why=f"BS face prints receivables only inside '{l['lb']}', which names other items too: combined", rule='face')
    if R['note_ok'] == 'Y':
        n = note_value(alts, notes, dp)
        if n: return n          # an undimensioned BS-date fact beats a combined caption (bank goodwill; DIS payable inside payable+accrued)
    for t in comb:
        if t in bytag:
            l = bytag[t]
            return dict(status='combined', value=l['val'], nodes=f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]", why=f"BS face prints only the combined line {t} '{l['lb']}'", rule='face')
    return None


def note_value(alts, notes, dp=''):
    for parts in alts:
        if dp == 'cash_and_equivalents' and any('Restricted' in t for t in parts): continue   # restricted-cash-inclusive total is not a note cash fact
        vs = [notes.get(t) for t in parts]
        if all(v is not None for v in vs):
            return dict(status='mapped' if len(parts) == 1 else 'component_sum', value=sum(vs), nodes='; '.join(f"{t}={v} [NOTE]" for t, v in zip(parts, vs)),
                        why=f"undimensioned consolidated fact {'+'.join(parts)} at the balance-sheet date (qtrs 0), no face line (§AG)", rule='note')
    return None


def _non_economic():
    out = collections.defaultdict(set)
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rules', 'non_economic_share_classes.csv')
    for r in csv.DictReader(open(p)):
        out[r['cik'].zfill(10)].add(r['member'])
    return out


NON_ECONOMIC = _non_economic()
DERIVE_SHARES = os.environ.get('DERIVE_SHARES', '1') == '1'   # issued - treasury (X67): ON since the founder's approval (doc 02, 2026-11-17 item 5) and the loader's DERIVED_DIRECT path


def drop_combined_members(cls):
    """X138 (V FY2026): the parenthetical prints 'Common Class B-1, B-2 And B-3' (member CommonClassB1B2AndB3, 63) beside the B-1, B-2 and B-3
    members (2 + 0 + 61): a member whose name joins other classes with 'And', and whose value equals the sum of the members it names,
    is their total. It is left out so the classes are counted once."""
    sfx = lambda k: re.sub(r'^\w*?Class', '', k.split('=', 1)[1])
    out = collections.OrderedDict(cls)
    for k, (v, _) in list(cls.items()):
        name = sfx(k)
        if 'And' not in name: continue
        parts = [o for o in cls if o != k and 'And' not in sfx(o) and sfx(o) and sfx(o) in name.replace('And', '')]   # 'A' is not in 'B1B2AndB3'
        if len(parts) >= 2 and sum(cls[o][0] for o in parts) == v: out.pop(k, None)
    return out


def shares(f, notes, bsby):
    und = notes.get('CommonStockSharesOutstanding')
    if und is not None:
        return dict(status='mapped', value=und, nodes=f"CommonStockSharesOutstanding={und} [BSP]", why='undimensioned CommonStockSharesOutstanding at the balance-sheet date (never dei)', rule='note')
    cls = collections.OrderedDict()
    for s in (f.get('cpv') or '').split('~'):
        x = s.split('|')
        if len(x) != 6 or x[2] != 'CommonStockSharesOutstanding': continue
        m = CLASS_SEG.findall(x[4]); other = re.sub(r'ClassOfStock=[A-Za-z0-9_]+;?', '', x[4]).strip()
        if len(m) != 1 or other or EQ_STOP.search(m[0] + ' ' + x[3]): continue
        ax = re.search(r'(\w*ClassOfStock)=', x[4]).group(1)
        cls.setdefault(f'{ax}={m[0]}', (D(x[5]), f"R{x[0]}.htm:{x[1]}"))   # the FSN segment verbatim: StatementClassOfStock=CommonClassA
    # a printed all-class total in the parenthetical (Google Inc FY2014: 'Common and Capital Stock, Shares, Outstanding' 680,172,000, Class C
    # filed as capital stock outside CommonStockSharesOutstanding) wins over an incomplete class sum
    tot = [s.split('|') for s in (f.get('cpv') or '').split('~')]
    tot = [x for x in tot if len(x) == 6 and not x[4] and x[2] != 'CommonStockSharesOutstanding' and x[2].endswith('SharesOutstanding')
           and re.search(r'(?i)common', x[2] + ' ' + x[3]) and re.search(r'(?i)outstanding', x[3])]
    if tot and (not cls or D(tot[0][5]) > sum(v for v, _ in cls.values())):
        x = tot[0]
        return dict(status='mapped', value=D(x[5]), nodes=f"{x[2]}={D(x[5])} [R{x[0]}.htm:{x[1]}]",
                    why=f"the balance-sheet parenthetical prints the all-class total '{x[3]}'" + (f" above the class sum {sum(v for v, _ in cls.values())}" if cls else ''), rule='class_total')
    # a class that prints shares issued (and treasury) but no outstanding fact is not missing from the sum: issued - treasury of that class
    # (ACN: Class A issued 657,964,764 - treasury 36,108,842; Class X prints outstanding). Classes without economic rights are left out
    # (rules/non_economic_share_classes.csv, each with its filing quote; Dhairya wave 3A 2026-11-17)
    noneco = NON_ECONOMIC.get(str(f.get('cik') or '').zfill(10), set())
    per = collections.defaultdict(dict)
    for s in (f.get('cpv') or '').split('~'):
        x = s.split('|')
        if len(x) != 6 or x[5] in ('', None) or x[2] not in ('CommonStockSharesIssued', 'TreasuryStockShares', 'TreasuryStockCommonShares'): continue
        m = CLASS_SEG.findall(x[4]); other = re.sub(r'ClassOfStock=[A-Za-z0-9_]+;?', '', x[4]).strip()
        if len(m) != 1 or other or EQ_STOP.search(m[0]): continue   # the member only: the treasury row's own label names treasury
        ax = re.search(r'(\w*ClassOfStock)=', x[4]).group(1)
        per[f'{ax}={m[0]}'].setdefault('iss' if x[2] == 'CommonStockSharesIssued' else 'tre', (x[2], D(x[5]), f"R{x[0]}.htm:{x[1]}"))
    gaps = [k for k in per if k not in cls and 'iss' in per[k] and k.split('=', 1)[1] not in noneco]
    if DERIVE_SHARES and gaps and all('tre' in per[k] and per[k]['iss'][1] >= per[k]['tre'][1] for k in gaps):
        nodes, v = [], D(0)
        for k, (val, r) in cls.items():
            if k.split('=', 1)[1] in noneco: continue
            nodes.append(f"CommonStockSharesOutstanding[{k}]={val} [{r}]"); v += val
        for k in gaps:
            (it, iv, ir), (tt, tv, tr) = per[k]['iss'], per[k]['tre']
            if iv == tv: continue   # fully held in treasury (ACN's 40,000 euro OrdinaryShares): nothing outstanding
            nodes += [f"{it}[{k}]={iv} [{ir}]", f"-{tt}[{k}]={tv} [{tr}]"]; v += iv - tv
        if nodes:
            left = sorted(k for k in list(cls) + gaps if k.split('=', 1)[1] in noneco)
            return dict(status='derived', value=v, nodes='; '.join(nodes),
                        why='class sum of the balance-sheet parenthetical, issued - treasury for a class with no outstanding fact (ruling C2)'
                            + (f"; non-economic class(es) left out: {', '.join(left)} (rules/non_economic_share_classes.csv)" if left else ''),
                        rule='derived_issued_less_treasury')
    cls = collections.OrderedDict((k, v) for k, v in cls.items() if k.split('=', 1)[1] not in noneco)
    cls = drop_combined_members(cls)
    if cls:
        return dict(status='component_sum' if len(cls) > 1 else 'mapped', value=sum(v for v, _ in cls.values()),
                    nodes='; '.join(f"CommonStockSharesOutstanding[{k}]={v} [{r}]" for k, (v, r) in cls.items()),
                    why=f"class sum over ClassOfStock members of the balance-sheet parenthetical ({len(cls)} classes)", rule='class_sum')
    # open-shown queue 2026-11-16 (ABT, COP, CVX, WFC, LIN): the parenthetical prints shares ISSUED and TREASURY shares, not outstanding:
    # outstanding = issued - treasury, same parenthetical and column (ruling C2, derived_not_printed). CVX FY2022 2,442,676,580 -
    # 527,460,237 = 1,915,216,343 = CVX's own equity-statement outstanding fact; LIN FY2022 552,012,862 - 59,555,235 = 492,457,627 likewise
    # founder approval 2026-11-17 (doc 02 item 5): derived instants from printed lines of the same filing are allowed for shares_outstanding;
    # served by structural_loader.DERIVED_DIRECT. DERIVE_SHARES=0 switches it off
    if not DERIVE_SHARES:
        return None
    und_p = [s.split('|') for s in (f.get('cpv') or '').split('~')]
    und_p = [x for x in und_p if len(x) == 6 and not x[4] and x[5] not in ('', None)]
    iss = next((x for x in und_p if x[2] == 'CommonStockSharesIssued'), None)
    tre = next((x for x in und_p if x[2] in ('TreasuryStockShares', 'TreasuryStockCommonShares')), None)
    if iss is not None and tre is not None and D(iss[5]) > D(tre[5]) >= 0:
        v = D(iss[5]) - D(tre[5])
        return dict(status='derived', value=v, nodes=f"CommonStockSharesIssued={D(iss[5])} [R{iss[0]}.htm:{iss[1]}]; -{tre[2]}={D(tre[5])} [R{tre[0]}.htm:{tre[1]}]",
                    why=f"the balance-sheet parenthetical prints shares issued ('{iss[3]}') and treasury shares ('{tre[3]}'), not outstanding: issued - treasury (ruling C2)",
                    rule='derived_issued_less_treasury')
    return None


def resolve_family(f, notes):
    L, arcs = parse(f); bs = face(L, 'BS')
    out = {}
    if not bs: return out
    by, asset, liab, cls_a, cls_l = regions(bs)
    ta = by.get('Assets')
    whole_assets = [l for l in bs if l['val'] is not None and ta is not None and l['ln'] < ta['ln']]
    # noncurrent items (goodwill, intangibles, PP&E) sit anywhere on the asset side
    for dp in FAMILY:
        R = ROLES.get(dp)
        if dp == 'shares_outstanding':
            r = shares(f, notes, by)
        elif R is None:
            continue
        else:
            if dp in ('cash_and_equivalents', 'accounts_receivable', 'inventory'): lines = asset if cls_a else whole_assets
            elif dp == 'accounts_payable': lines = liab
            else: lines = whole_assets
            r = pick(R, lines, notes, dp)
            if dp == 'cash_and_equivalents': r = cash_subtotal(r, lines, arcs)
            if dp == 'inventory': r = inventory_header_sum(bs, r, notes) or r
        if r is None:
            r = dict(status='not_presented', value=None, nodes='', rule='', why=f"no {dp} line on the balance sheet face in its position, and no undimensioned note fact at the balance-sheet date")
        out[dp] = r
    # unclassified balance sheet: current subtotals are not presented (ruling 2026-11-14)
    if 'AssetsCurrent' not in by:
        out['current_assets'] = dict(status='not_presented', value=None, nodes='', rule='unclassified', why='unclassified balance sheet: the face has no AssetsCurrent subtotal (ruling 2026-11-14)')
    if 'LiabilitiesCurrent' not in by:
        out['current_liabilities'] = dict(status='not_presented', value=None, nodes='', rule='unclassified', why='unclassified balance sheet: the face has no LiabilitiesCurrent subtotal (ruling 2026-11-14)')
    return out


def notes_for(raw):
    # duplicate facts for one tag (a rounded text variant beside the XBRL count): resolve.note_facts (most precise, order-independent)
    return {t: v for (t, _), v in note_facts(raw).items()}


def run(filings, notes_all, c2t, version):
    rows = []
    for f in filings:
        tk = c2t.get(str(int(f['cik'])))
        if not tk: continue
        for dp, r in resolve_family(f, notes_for(notes_all.get(f['a']))).items():
            v = r['value']
            rows.append(dict(cik=f['cik'].zfill(10), ticker=tk, data_point=dp, period_end=f['p'], grain='I', decision=r['status'],
                             nodes=(r['nodes'] + ' | ' if r['nodes'] else '') + 'why: ' + r['why'],
                             value='' if v is None or r['status'] in ('combined', 'not_presented', 'no_role') else str(D(v).normalize() if D(v) != D(v).to_integral() else D(v).to_integral()),
                             accession=f['a'], column='own', calc_check='', flags=f"bs_family;{r['rule']}".rstrip(';'), resolver_version=version))
    return rows


if __name__ == '__main__':
    filings = json.load(open(sys.argv[1])); notes = json.load(open(sys.argv[2])); tick = json.load(open(sys.argv[3]))
    c2t = {str(int(v)): k for k, v in tick.items()}
    rows = run(filings, notes, c2t, sys.argv[4] if len(sys.argv) > 4 else 'resolver-bs-dev')
    w = csv.DictWriter(open(sys.argv[5] if len(sys.argv) > 5 else 'resolver-bs.csv', 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), collections.Counter((r['data_point'], r['decision']) for r in rows))
