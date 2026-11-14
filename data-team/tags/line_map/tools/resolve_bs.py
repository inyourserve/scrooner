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
from resolve import parse, face, tol, children

ROLES_CSV = os.environ.get('ROLES_CSV', os.path.join(HERE, '..', 'rules', 'roles.csv'))
ROLES = {r['data_point']: r for r in csv.DictReader(open(ROLES_CSV))}
FAMILY = ('cash_and_equivalents', 'accounts_receivable', 'inventory', 'accounts_payable', 'goodwill', 'intangible_assets', 'ppe_net', 'shares_outstanding')
COMPONENT = re.compile(r'^(Inventory(FinishedGoods|RawMaterials|WorkInProcess|Gross)|InventoryFinishedGoodsNetOfReserves)')
EQ_STOP = re.compile(r'(?i)preferred|treasury|restricted|unvested|nonvoting')
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
        cl = [l for l in lines if l['custom'] and re.search(R['custom_label'], l['lb'], re.I)]
        if len(cl) == 1:
            l = cl[0]
            return dict(status='mapped', value=l['val'], nodes=f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]", why=f"BS face custom line whose own label names the role: '{l['lb']}'", rule='face')
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


def shares(f, notes, bsby):
    und = notes.get('CommonStockSharesOutstanding')
    if und is not None:
        return dict(status='mapped', value=und, nodes=f"CommonStockSharesOutstanding={und} [BS parenthetical / NOTE]", why='undimensioned CommonStockSharesOutstanding at the balance-sheet date (never dei)', rule='note')
    cls = collections.OrderedDict()
    for s in (f.get('cpv') or '').split('~'):
        x = s.split('|')
        if len(x) != 6 or x[2] != 'CommonStockSharesOutstanding': continue
        m = CLASS_SEG.findall(x[4]); other = re.sub(r'ClassOfStock=[A-Za-z0-9_]+;?', '', x[4]).strip()
        if len(m) != 1 or other or EQ_STOP.search(m[0] + ' ' + x[3]): continue
        cls.setdefault(m[0], (D(x[5]), f"R{x[0]}.htm:{x[1]}"))
    if cls:
        return dict(status='component_sum' if len(cls) > 1 else 'mapped', value=sum(v for v, _ in cls.values()),
                    nodes='; '.join(f"CommonStockSharesOutstanding[{k}]={v} [{r}]" for k, (v, r) in cls.items()),
                    why=f"class sum over ClassOfStock members of the balance-sheet parenthetical ({len(cls)} classes)", rule='class_sum')
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
    # duplicate facts for one tag (a rounded text variant beside the XBRL count): keep the most precise (fewest trailing zeros)
    out = {}
    for x in (raw or '').split('~'):
        if x.count('|') != 2: continue
        t, _, v = x.split('|'); v = D(v)
        if t not in out or (len(str(int(v))) - len(str(int(v)).rstrip('0'))) < (len(str(int(out[t]))) - len(str(int(out[t])).rstrip('0'))): out[t] = v
    return out


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
