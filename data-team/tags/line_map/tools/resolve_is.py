"""Income-statement family resolver (read-only): other income, interest expense/income, comprehensive income, D&A, amortization.
Position decides, the tag only ranks: the lines between operating income and pretax on the face are classified by their own
tag/label as interest expense (IE), interest income (II), mixed (a line that holds interest and something else) or other.
apply(rows, filings, notefacts, tick) replaces the rows of these data points from resolve_all.run() with the structural result,
keeping the resolve_all row when the family has no decisive evidence. Rulings (Dhairya 2026-11-14):
  other_income_expense_net: the lines printed between OI and pretax, excluding interest expense and interest income printed
    separately; a single nonoperating total that includes interest is combined.
  comprehensive_income: parent ComprehensiveIncomeNetOfTax; a figure including NCI is a point reason (ci_incl_nci).
  D&A including accretion or impairment is combined. Amortization = intangible amortization only (capitalized software out, S5/TXN).
  interest_expense gross; a net line is combined, note-only InterestExpenseDebt takes the NOTE role."""
import re, sys, os, collections
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve import parse, face, children, tol

MINE = ('other_income_expense_net', 'interest_expense', 'interest_income', 'comprehensive_income', 'depreciation_and_amortization', 'amortization_of_intangibles')
PRETAX = re.compile(r'BeforeIncomeTax|IncomeLossFromContinuingOperationsBefore|PretaxIncome|(Income|Earnings)\w*BeforeTax')
PRETAX_LB = re.compile(r'(?i)before (provision for |benefit from )?(income )?tax|pre-?tax')
OI_TAG = re.compile(r'^OperatingIncomeLoss$')
OI_LB = re.compile(r'(?i)^(total )?(operating (income|profit|loss|earnings)|income from operations|(profit|earnings) from operations)')
IE_TAG = re.compile(r'^(InterestExpense\w*|InterestAndDebtExpense|FinanceLeaseInterestExpense\w*|InterestExpenseLesseeAssetsUnderCapitalLease|InterestIncurred\w*|InterestExpenseDebt)$')
IE_LB = re.compile(r'(?i)^(total )?(interest expense|interest and debt expense|interest on|finance lease interest|interest cost)|^interest( and amortization of debt)?$|^(debt|capital leases?|finance leases?|long-term debt)$')
II_TAG = re.compile(r'^(InvestmentIncomeInterest|InterestIncomeOther|InterestAndDividendIncomeOperating|InvestmentIncomeInterestAndDividend|InterestIncomeOperating|InterestIncomeNonoperating|InterestAndOtherIncomeAbstract|InterestIncome\w*|InvestmentIncomeDividend|InvestmentIncomeNet)$')
II_LB = re.compile(r'(?i)^(?!investment income and other)(interest income|investment income|interest and dividend income|dividend and interest income|interest and investment income)')
NET_TAG = re.compile(r'^(InterestIncomeExpenseNet|InterestIncomeExpenseNonoperatingNet|InterestAndOtherIncome|InterestIncomeExpenseAfterProvisionForLoanLoss|InvestmentIncomeInterestAndDebtExpense)$')
NET_LB = re.compile(r'(?i)interest.*(and other|net)|net.*interest|interest and other|other.*interest')


NETINT_LB = re.compile(r'(?i)(interest[^,]*,\s*net\b|interest (income|expense)[^,]*\b(and|\(|/)\s*(interest )?(income|expense)|net interest|interest, net|interest (expense|income)?\W+net\b|interest (expense|income)?\s*[-–—]\s*net)')
MIXED_LB = re.compile(r'(?i)interest.*\b(and|&)\b.*\b(other|investment|dividend|gain|nonoperating|non-operating)\b|other.*\binterest\b|(other|non-?operating).*(income|expense).*interest')


II_NOTE = ('InvestmentIncomeInterest', 'InterestIncomeOther', 'InterestAndDividendIncomeOperating', 'InvestmentIncomeInterestAndDividend')


def kind(l):
    t, lb = l['tag'], l['lb'] or ''
    if MIXED_LB.search(lb) or t in ('InterestAndOtherIncome', 'InterestAndOtherNet', 'InterestAndOtherFinancialCharges', 'InterestAndOtherIncomeExpenseNet'): return 'mixed'
    if NETINT_LB.search(lb) or (NET_TAG.match(t) and not IE_LB.search(lb) and not II_LB.search(lb)): return 'netint'
    if re.search(r'(?i)\b(and|&)\s+other', lb) or t in ('OtherNonoperatingIncomeExpense', 'NonoperatingIncomeExpense', 'OtherNonoperatingIncome'): return 'other'
    if IE_LB.search(lb) or IE_TAG.match(t): return 'IE'
    if re.search(r'(?i)\b(and|&)\s+other', lb) or t in ('OtherNonoperatingIncomeExpense', 'NonoperatingIncomeExpense', 'OtherNonoperatingIncome'): return 'other'
    if II_LB.search(lb) or II_TAG.match(t): return 'II'
    return 'other'


def fmt(l, st='IS'): return f"{l['tag']}={l['val']} [R{l['rep']}.htm:{l['ln']}]"


def band(L, arcs):
    """The valued face lines between operating income and pretax, subtotals removed (a line whose calc children, or whose
    preceding band lines, sum to it is a subtotal of lines already in the band)."""
    fl = face(L, 'IS')
    if not fl: return None
    oi = next((l for l in fl if l['val'] is not None and OI_TAG.match(l['tag'])), None) or next((l for l in fl if l['val'] is not None and OI_LB.search(l['lb'] or '')), None)
    if oi is None:
        # no operating-income line (NEM): the band starts after the printed operating-costs total
        oi = next((l for l in reversed(fl) if l['val'] is not None and l['tag'] in ('CostsAndExpenses', 'OperatingExpenses', 'BenefitsLossesAndExpenses')), None)
        if oi is None: return None
    pt = next((l for l in fl if l['val'] is not None and l['ln'] > oi['ln'] and (PRETAX.search(l['tag']) or PRETAX_LB.search(l['lb'] or ''))), None)
    if pt is None: return None
    raw = [l for l in fl if oi['ln'] < l['ln'] < pt['ln'] and l['val'] is not None]
    by = {l['tag']: l for l in raw}
    drop = set()
    for i, l in enumerate(raw):
        kids = [c for c, w in (children(arcs, l['tag'], by) or []) if c in by and c != l['tag']]
        if len(kids) >= 2: drop.add(l['tag']); continue
        # no calc: a total line equal to the sum of the lines above it within the band
        prev = raw[:i]
        if len(prev) >= 2 and 'total' in (l['prole'] or '').lower():
            for k in range(len(prev) - 1):
                s = sum((-p['val'] if p['neg'] else p['val']) for p in prev[k:])
                if min(abs(s - l['val']), abs(s + l['val'])) <= tol(s, l['val']): drop.add(l['tag']); break
    keep = [l for l in raw if l['tag'] not in drop]
    return oi, pt, keep, [l for l in raw if l['tag'] in drop]


def mk(dp, status, lines, why, flags='', value=None, tags=None, note=False):
    if value is None and lines: value = sum((l['val'] for l in lines), D(0))
    return dict(data_point=dp, status=status, tags='+'.join(l['tag'] for l in lines) if tags is None else tags, value=value if status in ('mapped', 'component_sum', 'derived') else None,
                r_page='+'.join(sorted({f"R{l['rep']}.htm" for l in lines})) if lines else '', nodes='; '.join(fmt(l) for l in lines), why=why, flags=flags)


def resolve_band(L, arcs, notes):
    out = {}
    b = band(L, arcs)
    if b is None: return out
    oi, pt, keep, dropped = b
    ks = [(kind(l), l) for l in keep]
    ie = [l for k, l in ks if k == 'IE']; ii = [l for k, l in ks if k == 'II']; mx = [l for k, l in ks if k == 'mixed']
    nt = [l for k, l in ks if k == 'netint']; ot = [l for k, l in ks if k == 'other']
    where = f"IS lines between {oi['tag']} (R{oi['rep']}:{oi['ln']}) and pretax (R{pt['rep']}:{pt['ln']})"
    if mx:
        out['other_income_expense_net'] = mk('other_income_expense_net', 'combined', mx + ot, f"{where}: '{mx[0]['lb']}' holds interest together with other items; no separate other-income line")
    elif len(ot) == 1 and not (ie or ii or nt) and ot[0]['tag'] == 'NonoperatingIncomeExpense':
        out['other_income_expense_net'] = mk('other_income_expense_net', 'combined', ot, f"{where}: a single nonoperating total ('{ot[0]['lb']}') is printed; it holds interest and other items together")
    elif ot:
        out['other_income_expense_net'] = mk('other_income_expense_net', 'mapped' if len(ot) == 1 else 'component_sum', ot, f"{where}: the line(s) that are not interest expense or interest income", flags='band')
    else:
        out['other_income_expense_net'] = mk('other_income_expense_net', 'not_presented', [], f"{where} holds only interest lines; no other nonoperating line")
    if ie:
        out['interest_expense'] = mk('interest_expense', 'mapped' if len(ie) == 1 else 'component_sum', ie, f"{where}: interest expense line(s), gross", flags='band')
    elif nt or mx:
        note_ie = next((t for t in ('InterestExpense', 'InterestExpenseNonoperating', 'InterestExpenseDebt', 'InterestAndDebtExpense') if notes.get((t, 4)) is not None), None)
        src = (nt + mx)[0]
        if note_ie:
            v = notes[(note_ie, 4)]
            out['interest_expense'] = dict(data_point='interest_expense', status='mapped', tags=note_ie, value=v, r_page='NOTE', nodes=f'{note_ie}={v} [NOTE]',
                                           why=f"{where} prints only '{src['lb']}' (net); gross interest expense is the undimensioned note fact {note_ie} (per-series ruling)", flags='note_only')
        else:
            out['interest_expense'] = mk('interest_expense', 'combined', [src], f"{where}: only '{src['lb']}'; gross interest expense is not printed")
    if ii:
        out['interest_income'] = mk('interest_income', 'mapped' if len(ii) == 1 else 'component_sum', ii, f"{where}: interest income line(s)", flags='band')
    elif (nt or mx) and any(notes.get((t, 4)) is not None for t in II_NOTE):
        t = next(t for t in II_NOTE if notes.get((t, 4)) is not None); v = notes[(t, 4)]; src = (nt + mx)[0]
        out['interest_income'] = dict(data_point='interest_income', status='mapped', tags=t, value=v, r_page='NOTE', nodes=f'{t}={v} [NOTE]',
                                      why=f"{where} prints only '{src['lb']}'; interest income is the undimensioned note fact {t}", flags='note_only')
    elif nt or mx:
        src = (nt + mx)[0]
        out['interest_income'] = mk('interest_income', 'combined', [src], f"{where}: interest income only inside '{src['lb']}'")
    return out


INCL = 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest'
NCI_TAG = re.compile(r'^(?!\w*(IncludingPortion|BeforeIncomeTax|Abstract|IncomeLossFromContinuingOperations))\w*(Noncontrolling|Minority)\w*$')  # any NCI element except totals that include it and pretax totals named after it


def resolve_ci(L, notes):
    allv = [l for l in L if l['val'] is not None and l['st'] in ('CI', 'IS')]
    def line(tag): return next((l for l in allv if l['tag'] == tag), None)
    p = line('ComprehensiveIncomeNetOfTax')
    if p is not None: return mk('comprehensive_income', 'mapped', [p], f"CI statement: parent {p['tag']} (R{p['rep']}:{p['ln']})")
    inc = line(INCL)
    if inc is not None or notes.get((INCL, 4)) is not None:
        # an NCI line is an attribution or balance element; a pretax total whose name merely mentions MinorityInterest (UNP, V) is not
        nci_line = any(NCI_TAG.search(l['tag']) and l['val'] for l in L if l['st'] in ('CI', 'IS', 'BS', 'EQ'))
        # ruling 2026-11-14 (Dhairya; MSFT/JNJ, Ritwik certified): a line whose element or label names items beyond the data
        # point is combined. The NCI-inclusive element names the noncontrolling portion, so it stays the ci_incl_nci point reason
        # even when the filing shows no NCI line (the earlier no-NCI -> parent rule is withdrawn)
        return dict(data_point='comprehensive_income', status='combined', tags=INCL, value=None, r_page=f"R{inc['rep']}.htm" if inc else 'NOTE', nodes=fmt(inc) if inc else f'{INCL} [NOTE]',
                    why='only the figure including noncontrolling interest is printed; the parent figure is not (ruling: point reason)', flags='ci_incl_nci')
    pn = notes.get(('ComprehensiveIncomeNetOfTax', 4))
    if pn is not None: return dict(data_point='comprehensive_income', status='mapped', tags='ComprehensiveIncomeNetOfTax', value=pn, r_page='NOTE', nodes=f'ComprehensiveIncomeNetOfTax={pn} [NOTE]', why='undimensioned consolidated note fact', flags='')
    return None


DA_TOT = re.compile(r'^(DepreciationDepletionAndAmortization|DepreciationAndAmortization|DepreciationAmortizationAndOther|DepreciationAndAmortizationExcludingIntangibleAssetsAndDeferredContractAcquisitionCosts|DepreciationAndAmortizationExcludingAmortizationOfIntangibleAssets|OtherDepreciationAndAmortization|DepreciationAndDepletion|DepreciationAmortizationAndAccretionNet)$')
DA_TOT_LB = re.compile(r'(?i)^(total )?depreciation[,]? (expense )?(depletion )?(and|&) amortization|^depreciation(, depletion)?(,)? (and|&) (amortization|depletion)|^depreciation, amortization|^depreciation and depletion')
DEP_TAG = re.compile(r'^(Depreciation|DepreciationNonproduction|DepreciationDepletionAndAmortizationPropertyPlantAndEquipment|DepreciationOfPropertyPlantAndEquipment|DepreciationExpense)$')
DEP_LB = re.compile(r'(?i)^depreciation( expense)?( and depletion)?$|^depreciation of')
AMORT_TAG = re.compile(r'^(AmortizationOfIntangibleAssets|AmortizationOfAcquiredIntangibleAssets|AdjustmentForAmortization|CapitalizedComputerSoftwareAmortization1?|AmortizationOfDeferredCharges|Amortization)$')
AMORT_LB = re.compile(r'(?i)^amortization( expense)?( of (acquisition-related |purchased |acquired |other |intangible |capitalized |developed )?(intangible|software|assets|technology|customer|contract))?')
NOT_DA = re.compile(r'(?i)accretion|impairment|debt (discount|issuance)|deferred (financing|loan|compensation|income|tax|policy|acquisition)|right-of-use|above|below|premium|investments?\b|securities|bond|discount|contract cost|lease|financing cost|stock|share')
INT_LB = re.compile(r'(?i)^(?!.*inventory)(amortization.*intangible|intangible.*amortization|amortization of (acquired|purchased|acquisition|customer|developed|other acquired)|acquired intangible)')
ACC = re.compile(r'Accretion|Impairment')
ACC_LB = re.compile(r'(?i)accretion|impairment')
# accretion the filing itself reports (rulings 2026-11-14, DUK): liability (ARO) accretion expense and CF accretion lines; discount
# accretion only as a CF line. Acquired-loan accretable yield is interest income, equity accretion is not an IS item: neither counts
ACC_EVID = re.compile(r'^(AssetRetirementObligationAccretionExpense|AccretionExpense\w*)$')
ACC_EVID_CF = re.compile(r'^AccretionAmortizationOfDiscountsAndPremiums\w*$')  # discount accretion counts only as a CF line


def accretion_reported(L, notes):
    """The filing reports accretion for its own period: a nonzero fact or line of an accretion element (ACC_EVID)."""
    if any(ACC_EVID.match(t) and q == 4 and v for (t, q), v in notes.items()): return True
    return any(l['val'] and (ACC_EVID.match(l['tag']) or (l['st'] == 'CF' and ACC_EVID_CF.match(l['tag']))) for l in L)
CAPSW = re.compile(r'(?i)software|CapitalizedComputer')
NOTE_AMORT = ('AmortizationOfIntangibleAssets', 'FiniteLivedIntangibleAssetsAmortizationExpense', 'AmortizationOfAcquiredIntangibleAssets')
NOTE_DA = ('DepreciationDepletionAndAmortization', 'DepreciationAndAmortization', 'DepreciationAmortizationAndOther')


def cfo_lines(L):
    cf = [l for l in face(L, 'CF') if l['val'] is not None]
    end = next((l['ln'] for l in cf if re.match(r'^NetCashProvidedByUsedInOperatingActivities', l['tag'])), 10 ** 6)
    return [l for l in cf if l['ln'] < end], cf


def note_close(v, n):
    """v equals the note fact n within n's own rounding (a note printed as $2.4 billion is rounded to its last nonzero digit)."""
    if n is None or v is None or n == 0: return False
    k = int(abs(n)); z = 0
    while k and k % 10 == 0 and z < 12: k //= 10; z += 1
    step = D(10) ** z
    return step <= abs(n) * D('0.1') and abs(abs(v) - abs(n)) <= step / 2


def dup_labels(lines):
    """Labels carried by two or more face lines with different tags: such a label identifies neither line (AMD 2024 FSN
    labels AdjustmentForAmortization 'Amortization of operating lease right-of-use assets', the label of the next line)."""
    c = collections.Counter((l['lb'] or '').strip().lower() for l in lines)
    return {k for k, n in c.items() if n > 1 and k}


def proven_amort(cfo, notes):
    """A generic amortization CF line (AdjustmentForAmortization, or 'Amortization (expense)', or a line whose label is a
    duplicate) is intangible amortization when its value equals the filing's own intangible-amortization note fact."""
    dl = dup_labels(cfo)
    for t in NOTE_AMORT:
        n = notes.get((t, 4))
        if n is None: continue
        for l in cfo:
            lb = (l['lb'] or '').strip().lower()
            generic = l['tag'] == 'AdjustmentForAmortization' or re.match(r'(?i)^amortization( expense)?$', lb) or lb in dl
            if generic and not CAPSW.search(l['tag']) and l['tag'] not in ('OperatingLeaseRightOfUseAssetAmortizationExpense', 'AmortizationOfFinancingCostsAndDiscounts') and note_close(l['val'], n):
                return l, t, n
    return None


def resolve_da(L, notes):
    cfo, cf = cfo_lines(L)
    isf = [l for l in face(L, 'IS') if l['val'] is not None]
    for src, lines in (('CF', cfo), ('IS', isf)):
        tot = [l for l in lines if (DA_TOT.match(l['tag']) or DA_TOT_LB.search(l['lb'] or '')) and not NOT_DA.search(l['lb'] or '') and not l['custom'] or (DA_TOT_LB.search(l['lb'] or '') and l['custom'] and not NOT_DA.search(l['lb'] or ''))]
        # an accretion/impairment tag is the filer's element choice; the printed label says what the line holds. A line tagged
        # DepreciationAmortizationAndAccretionNet but printed 'Depreciation and amortization' (AAPL, JPM, WMT, RTX, GE ...) is the
        # D&A line; only a label that names accretion or impairment makes it combined (WFC, TSLA, GOOG)
        # ruling 2026-11-14: label plus evidence. The accretion-tagged line is the D&A line only when its label names D&A and not
        # accretion AND the filing reports no accretion of its own (no ARO accretion fact, no accretion line); otherwise combined (DUK)
        acc_rep = accretion_reported(L, notes)
        tot = [l for l in tot if not (l['tag'] == 'DepreciationAmortizationAndAccretionNet' or ACC.search(l['tag'])) or (DA_TOT_LB.search(l['lb'] or '') and not ACC_LB.search(l['lb'] or '') and not acc_rep)]
        if len(tot) >= 1:
            tot.sort(key=lambda l: (not DA_TOT_LB.search(l['lb'] or ''), l['tag'] not in ('DepreciationDepletionAndAmortization', 'DepreciationAndAmortization'), l['ln']))
            t0 = tot[0]
            partial = t0['tag'] in ('Depreciation', 'OtherDepreciationAndAmortization') or re.search(r'Excluding', t0['tag']) or re.search(r'(?i)property|equipment|plant|excluding', t0['lb'] or '')
            ia = [l for l in lines if src == 'CF' and l is not t0 and INT_LB.search(l['lb'] or '') and not re.match(r'(?i)depreciation', l['lb'] or '') and not CAPSW.search(l['lb'] + l['tag']) and not re.search(r'(?i)inventory|above|below|lease|debt|financing', l['lb'] or '')]
            if src == 'CF' and not ia and (partial or t0['tag'] == 'OtherDepreciationAndAmortization'):
                pa = proven_amort(lines, notes)
                if pa and pa[0] is not t0:
                    return mk('depreciation_and_amortization', 'component_sum', [t0, pa[0]], f"CF face: {t0['lb']} (R{t0['rep']}:{t0['ln']}) plus the amortization line {pa[0]['tag']} (R{pa[0]['rep']}:{pa[0]['ln']}) that equals the intangible-amortization note fact {pa[1]}={pa[2]}", flags='face;amort_by_note_equality')
            if partial and ia:
                ls = [t0] + ia
                return mk('depreciation_and_amortization', 'component_sum', ls, f"CF face: {t0['lb']} excludes intangibles; plus the intangible amortization line(s)", flags='face')
            return mk('depreciation_and_amortization', 'mapped', [t0], f"{src} face: the depreciation and amortization line (R{t0['rep']}:{t0['ln']})", flags='face')
        accl = [l for l in lines if (re.match(r'^DepreciationAmortizationAndAccretion', l['tag']) or (ACC.search(l['tag']) and re.search(r'Depreciation', l['tag']))) and (ACC_LB.search(l['lb'] or '') or accretion_reported(L, notes))]
        if src == 'CF' and accl:
            return mk('depreciation_and_amortization', 'combined', accl[:1], f"CF face prints depreciation and amortization together with accretion/impairment (R{accl[0]['rep']}:{accl[0]['ln']}): combined", flags='da_incl_accretion')
        dep = [l for l in lines if (DEP_TAG.match(l['tag']) or DEP_LB.search(l['lb'] or '')) and not NOT_DA.search(l['lb'] or '')]
        am = [l for l in lines if (AMORT_TAG.match(l['tag']) or INT_LB.search(l['lb'] or '') or re.match(r'(?i)^amortization( expense)?$', l['lb'] or '')) and not NOT_DA.search(l['lb'] or '') and l not in dep]
        if src == 'CF' and dep and am:
            ls = dep + am
            return mk('depreciation_and_amortization', 'component_sum', ls, f"CF face prints depreciation and amortization on separate lines; sum of them", flags='face')
        if src == 'CF' and dep and not am:
            # depreciation only: amortization is not on the face; D&A total only from a note total
            pass
    for t in NOTE_DA:
        v = notes.get((t, 4))
        if v is not None: return dict(data_point='depreciation_and_amortization', status='mapped', tags=t, value=v, r_page='NOTE', nodes=f'{t}={v} [NOTE]', why='no D&A total on the CF/IS face; undimensioned consolidated note fact', flags='note_only')
    return None


def resolve_amort(L, notes):
    cfo, cf = cfo_lines(L)
    isf = [l for l in face(L, 'IS') if l['val'] is not None]
    pa = proven_amort(cfo, notes)
    if pa:
        l, t, n = pa
        return mk('amortization_of_intangibles', 'mapped', [l], f"CF face line {l['tag']} (R{l['rep']}:{l['ln']}) equals the filing's intangible-amortization note fact {t}={n} within the note's rounding; the face value is the precise one", flags='face;amort_by_note_equality')
    for src, lines in (('CF', cfo), ('IS', isf)):
        dl = dup_labels(lines) if src == 'CF' else set()  # the IS legitimately repeats a caption in the cost and opex sections
        ls = [l for l in lines if (l['lb'] or '').strip().lower() not in dl and INT_LB.search(l['lb'] or '') and not re.match(r'(?i)depreciation', l['lb'] or '') and not CAPSW.search(l['lb'] or '') and not CAPSW.search(l['tag']) and not re.search(r'(?i)above|below|lease|debt|financing', l['lb'] or '')]
        if ls:
            tagrank = [l for l in ls if l['tag'] in NOTE_AMORT or AMORT_TAG.match(l['tag'])] or ls
            return mk('amortization_of_intangibles', 'mapped' if len(tagrank) == 1 else 'component_sum', tagrank, f"{src} face line(s) naming intangible amortization", flags='face')
    for t in NOTE_AMORT:
        v = notes.get((t, 4))
        if v is not None: return dict(data_point='amortization_of_intangibles', status='mapped', tags=t, value=v, r_page='NOTE', nodes=f'{t}={v} [NOTE]', why="undimensioned consolidated note fact (§AG); capitalized software excluded (S5)", flags='note_only')
    gen = [l for l in cfo if (l['tag'] == 'AdjustmentForAmortization' or re.match(r'(?i)^amortization( expense)?$', l['lb'] or '')) and not CAPSW.search(l['tag'])]
    if gen:
        return dict(data_point='amortization_of_intangibles', status='no_role', tags=gen[0]['tag'], value=None, r_page=f"R{gen[0]['rep']}.htm", nodes=fmt(gen[0]), why=f"CF prints a generic '{gen[0]['lb']}' line; the filing does not name it intangible amortization here (reader check)", flags='generic_amortization')
    return None


def resolve(f, notes):
    L, arcs = parse(f)
    out = {}
    out.update(resolve_band(L, arcs, notes))
    ci = resolve_ci(L, notes)
    if ci: out['comprehensive_income'] = ci
    for fn in (resolve_da, resolve_amort):
        r = fn(L, notes)
        if r: out[r['data_point']] = r
    return out


ACC_FACTS = {}
_af = os.environ.get('ACCRETION_FACTS', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_accretion-facts-2026-11-14.csv'))
if os.path.exists(_af):
    import csv as _csv
    for _r in _csv.DictReader(open(_af)): ACC_FACTS.setdefault(_r['accession'], []).append((_r['tag'], int(_r['qtrs']), D(_r['value'])))


def apply(rows, filings, notefacts, tick):
    """Replace this family's rows with the structural result where it is decisive."""
    F = {f['a']: f for f in filings}
    cache = {}
    new = []
    for r in rows:
        if r['data_point'] not in MINE: new.append(r); continue
        a = r['accession']
        if a not in cache:
            notes = {}
            for s in (notefacts.get(a) or '').split('~'):
                x = s.split('|')
                if len(x) == 3: notes.setdefault((x[0], int(x[1])), D(x[2]))
            for t, q, v in ACC_FACTS.get(a, []): notes.setdefault((t, q), v)
            cache[a] = resolve(F[a], notes)
        m = cache[a].get(r['data_point'])
        if m is None: new.append(r); continue
        n = dict(r); n.update({k: v for k, v in m.items() if k != 'flags'})
        n['source'] = 'roles'; n['flags'] = m.get('flags', '')
        new.append(n)
    return new


def spec_rows(rows, version):
    DEC = {'mapped': 'mapped', 'component_sum': 'component_sum', 'derived': 'derived_not_printed', 'combined': 'combined', 'not_presented': 'not_presented', 'no_role': 'no_role'}
    out = []
    for r in rows:
        if r['data_point'] not in MINE: continue
        v = r.get('value')
        val = '' if v is None or r['status'] in ('combined', 'not_presented', 'no_role') else str(D(v).normalize() if D(v) != D(v).to_integral() else D(v).to_integral())
        out.append(dict(cik=r['cik'], ticker=r['ticker'], data_point=r['data_point'], period_end=r['period_end'], grain='FY', decision=DEC.get(r['status'], r['status']),
                        nodes=(r.get('nodes') or '') + (' | why: ' + r['why'] if r.get('why') else ''), value=val, accession=r['accession'], column='own',
                        calc_check=r.get('calc_check', ''), flags=';'.join(x for x in (r.get('source'), r.get('flags', '')) if x), resolver_version=version))
    return out


if __name__ == '__main__':
    import json, csv
    import resolve_all
    filings = json.load(open(sys.argv[1])); nf = json.load(open(sys.argv[2])); tick = {r[1]: r[0] for r in csv.reader(open(sys.argv[3]))}
    rows = apply(resolve_all.run(filings, nf, tick, {}), filings, nf, tick)
    spec = spec_rows(rows, sys.argv[4])
    w = csv.DictWriter(open(sys.argv[5], 'w', newline=''), fieldnames=list(spec[0].keys())); w.writeheader(); w.writerows(spec)
    print(len(spec), collections.Counter((s['data_point'], s['decision']) for s in spec))
