"""Structural total_debt (read-only). total_debt = every debt-role node under the filing's liabilities on the BS face
(deduplicated through the filer's calc tree: a node whose calc parent is also a debt node is inside it), plus the
finance/capital lease nodes the filing locates outside those debt lines:
  - a lease line on the BS face is a debt-role node itself;
  - a note FinanceLeaseLiability(+Current/Noncurrent) is added when the filing's FinanceLeaseLiability*StatementOfFinancialPositionExtensibleList
    places it outside the debt lines (fl_loc 'out'), skipped when 'in' (already inside a debt line), flagged when unknown;
  - a pre-842 CapitalLeaseObligations* note fact is added when its calc parent on the face is not a debt node, skipped when it is.
Per filing, both BS columns: own (period) and comparative (prior year end). Founder perimeter: total_debt includes finance and capital leases."""
import json, re, csv, sys, collections
from decimal import Decimal as D
from datetime import date
sys.path.insert(0, '.')
from resolve import parse, face, children, tol
DEBT = re.compile(r'^(ShortTermBorrowings|OtherShortTermBorrowings|CommercialPaper|DebtCurrent|LongTermDebtCurrent|LongTermDebtNoncurrent|LongTermDebt|'
                  r'LongTermDebtAndCapitalLeaseObligations\w*|DebtAndCapitalLeaseObligations|DebtCurrentAndFinanceLease\w*|LongTermDebtAndFinanceLease\w*|'
                  r'ShortTermBankLoansAndNotesPayable|NotesPayable\w*|LongTermNotesPayable\w*|LinesOfCreditCurrent|LineOfCredit|LongTermLineOfCredit\w*|LoansPayable\w*|'
                  r'SeniorNotes\w*|ConvertibleNotesPayable\w*|ConvertibleDebt\w*|ConvertibleLongTermNotesPayable|SecuredDebt\w*|UnsecuredDebt\w*|OtherLongTermDebt\w*|'
                  r'SubordinatedDebt\w*|DebtLongtermAndShorttermCombinedAmount|UnsecuredLongTermDebt|SecuredLongTermDebt|LongTermNotesAndLoans|LongTermLoansPayable|ShortTermNonBankLoansAndNotesPayable|OtherBorrowings|BankBorrowings|FederalHomeLoanBankAdvances\w*|AdvancesFromFederalHomeLoanBanks|LongTermFederalHomeLoanBankAdvances\w*|'
                  r'FinanceLeaseLiability\w*|CapitalLeaseObligations\w*|DebtInstrumentCarryingAmount|LongTermDebtFairValue)$')
DEBT_MEMBER = re.compile(r'(?i)(Debt|Borrowing|NotesPayable|CommercialPaper|LineOfCredit|Bonds)')
LEASES = {}
NOTDEBT = re.compile(r'(?i)interest payable|accrued interest|operating lease|FairValue|DebtInstrumentCarryingAmount')
AFFIL = re.compile(r'^(DueToAffiliate\w*|DueToRelatedParties\w*|NotesPayableRelatedParties\w*|DueToOfficersOrStockholders\w*)$')
REPO = re.compile(r'^(FederalFundsPurchased\w*|SecuritiesSoldUnderAgreementsToRepurchase\w*|SecuritiesLoaned\w*)$')   # secured funding like deposits: never debt (Dhairya ruling 2026-11-14 d)
LABEL_DEBT = re.compile(r'(?i)\b(debt|borrowings|notes payable|commercial paper|term loans?|senior notes|bonds payable|finance lease|capital lease)\b')
def run(filings, vals, flloc):
    V = {r['a']: r for r in vals}
    out = []
    latest = {}
    for f in filings: latest[f['cik']] = max(latest.get(f['cik'], ''), f['p'] + '|' + f['a'])
    co_loc = collections.defaultdict(set)   # the company's own lease location in its other filings (IBM 2021-23 'in')
    for f in filings:
        if flloc.get(f['a']) in ('in', 'out'): co_loc[f['cik']].add(flloc[f['a']])
    for f in filings:
        L, arcs = parse(f); bs = face(L, 'BS')
        if not bs: continue
        lines = [l for l in bs]
        # liabilities region: after the asset root (the 'Assets' total) and before the equity header / equity totals
        a_ln = next((l['ln'] for l in lines if l['tag'] == 'Assets'), None) or 0
        e_ln = next((l['ln'] for l in lines if l['ln'] > a_ln and (re.match(r'^(StockholdersEquity|CommitmentsAndContingencies|TemporaryEquity|RedeemableNoncontrolling)', l['tag']))), 10 ** 6)
        region = [l for l in lines if a_ln < l['ln'] < e_ln]
        # utilities print a CAPITALIZATION section (equity, then long-term debt) before current liabilities (NEE): a standard
        # debt-role element after the first equity line is still debt; custom lines there are not taken (equity labels)
        region += [l for l in lines if l['ln'] >= e_ln and DEBT.match(l['tag']) and not l['custom']]
        cand = []; header = ''
        for l in region:
            if l['tag'].endswith('Abstract'): header = l['lb']
            elif l['val'] is None and not l['custom']: pass
            if l['val'] is None and l['tag'].endswith('Abstract'): continue
            if l['tag'].endswith('Abstract') or NOTDEBT.search(l['tag'] + ' ' + l['lb']): continue
            if DEBT.match(l['tag']): cand.append((l, 'debt-role tag'))
            elif AFFIL.match(l['tag']) and LABEL_DEBT.search(l['lb']):
                cand.append((l, 'debt from affiliates/related parties: the own label names debt'))   # TMUS 'Long-term debt to affiliates'
            elif l['custom'] and (LABEL_DEBT.search(l['lb']) or LABEL_DEBT.search(header)) and not re.search(r'(?i)interest|operating', l['lb'] + ' ' + l['tag']):
                cand.append((l, 'custom line, debt label' + ('' if LABEL_DEBT.search(l['lb']) else f" (under header '{header}')")))
        # a debt total whose calc children include fed funds purchased / repos (COF 'Total other debt'): its other children
        # replace it when every child is printed on the face; when the repo part is not printed separately, the line is combined
        onbs0 = {l['tag']: l for l in lines if l['val'] is not None}
        repo_comb = []
        for l, why in list(cand):
            kids = [c for c, w in (children(arcs, l['tag'], onbs0) or [])]
            if not any(REPO.match(c) for c in kids): continue
            cand.remove((l, why))
            if all(c in onbs0 for c in kids):
                cand += [(onbs0[c], f"part of '{l['lb']}' without fed funds purchased / repos (ruling 2026-11-14 d)") for c in kids if not REPO.match(c) and c not in {x['tag'] for x, _ in cand}]
            else:
                repo_comb.append(l)
        tags = {l['tag'] for l, _ in cand}
        # dedupe through the calc tree: drop a node whose calc parent is also a selected debt node
        onbs = {l['tag']: l for l in lines if l['val'] is not None}
        parent_of = {}
        for p in tags:
            for c, w in (children(arcs, p, onbs) or []): parent_of[c] = p
        cand = [(l, why) for l, why in cand if parent_of.get(l['tag']) not in tags]
        # non-debt face parents of note lease facts
        lease_parent = {}
        for p, g in arcs.items():
            for grp in g.values():
                for c, w in grp:
                    if re.match(r'^(FinanceLeaseLiability|CapitalLeaseObligations)', c): lease_parent.setdefault(c, set()).add(p)
        from resolve import unit
        vv = collections.defaultdict(dict)
        for s in ((V.get(f['a']) or {}).get('vals') or '').split('~'):
            x = s.split('|')
            if len(x) == 4:
                v = D(x[3]); cur = vv[x[2]].get(x[0])
                # several facts under one tag and date (face line + rounded note figure): keep the most precise
                if cur is None or (unit(v) < unit(cur)): vv[x[2]][x[0]] = v
        per = date.fromisoformat(f['p'])
        cols = sorted(vv.keys(), reverse=True)
        # the columns closest to the period end and to one year before it (a filing also carries other instants: BAC 2015-01-31 is 334 days back)
        own = min((d for d in cols if abs((date.fromisoformat(d) - per).days) <= 20), key=lambda d: abs((date.fromisoformat(d) - per).days), default=f['p'])
        prior = min((d for d in cols if 330 <= (per - date.fromisoformat(d)).days <= 400), key=lambda d: abs((per - date.fromisoformat(d)).days - 365), default=None)
        loc = flloc.get(f['a']) or (flloc.get('FY0:' + f['cik']) if latest[f['cik']].endswith(f['a']) else None)
        for col, kind in ((own, 'own'), (prior, 'comparative')):
            if col is None: continue
            nodes = []; flags = []
            for l, why in cand:
                v = l['val'] if kind == 'own' and l['val'] is not None else vv[col].get(l['tag'])
                if v is None: flags.append(f"{l['tag']} has no value in this column"); continue
                nodes.append((l['tag'], v, f"BS R{l['rep']}:{l['ln']}", why + ('' if not l['custom'] else ', custom')))
            # a face debt line whose tag or label names leases already contains them (e.g. LongTermDebtAndCapitalLeaseObligations)
            on_face_lease = any(re.search(r'CapitalLease|FinanceLease|LeaseObligation', t) for t, *_ in nodes) or any(re.search(r'(?i)lease', l['lb']) for l, _ in cand)
            # a face lease line that is one part only (VRTX 2019-24, ANET 2018: FinanceLeaseLiabilityNoncurrent): the other part is added
            # (total minus the face part when the note total exists, else the note part), unless the filing places it inside a debt line
            # (Dhairya 2026-11-14: one figure per location member, Current + Noncurrent)
            for fam in ('FinanceLeaseLiability', 'CapitalLeaseObligations'):
                face_parts = [t for t, *_ in nodes if t in (fam + 'Current', fam + 'Noncurrent')]
                if len(face_parts) != 1 or loc == 'in': continue
                other = fam + ('Current' if face_parts[0].endswith('Noncurrent') else 'Noncurrent')
                fv = next(v for t, v, *_ in nodes if t == face_parts[0]); tot_ = vv[col].get(fam)
                ov = tot_ - fv if tot_ is not None and tot_ >= fv else vv[col].get(other)
                pars = lease_parent.get(other, set())
                if ov and fam == 'CapitalLeaseObligations' and not (pars and pars & set(onbs) and not pars & tags):
                    # pre-842: absence is not evidence (CVX keeps current capital leases in short-term debt); a non-debt calc parent is
                    flags.append(f'READER CHECK: {other} {ov} beside the face {face_parts[0]} with no location member or non-debt calc parent: not added')
                elif ov and not (pars & tags):
                    nodes.append((other, ov, 'NOTE', f"the other part of the face {face_parts[0]}" + (f" ({fam} {tot_} - {fv})" if tot_ is not None and tot_ >= fv else '') + ('; ExtensibleList: out' if loc == 'out' else '')))
                elif ov:
                    flags.append(f'{other} inside a debt line (calc parent): not added')
            fl = vv[col].get('FinanceLeaseLiability')
            if fl is None and ('FinanceLeaseLiabilityCurrent' in vv[col] or 'FinanceLeaseLiabilityNoncurrent' in vv[col]):
                fl = vv[col].get('FinanceLeaseLiabilityCurrent', D(0)) + vv[col].get('FinanceLeaseLiabilityNoncurrent', D(0))
            if fl and not on_face_lease:
                pars = lease_parent.get('FinanceLeaseLiability', set()) | lease_parent.get('FinanceLeaseLiabilityCurrent', set()) | lease_parent.get('FinanceLeaseLiabilityNoncurrent', set())
                if loc == 'out' or (loc is None and pars and not pars & {t for t, *_ in nodes}):
                    nodes.append(('FinanceLeaseLiability', fl, 'NOTE', f"note lease outside debt lines ({'ExtensibleList: out' if loc == 'out' else 'calc parent ' + '/'.join(sorted(pars))})"))
                elif loc == 'in' or (pars & tags):
                    flags.append('finance lease inside a debt line (ExtensibleList/calc): not added')
                else:
                    # no ExtensibleList and no calc arc: inside a debt line only if a debt note total ties to face debt minus the lease
                    ltd = vv[col].get('LongTermDebt'); face_ltd = sum((v for t, v, *_ in nodes if t.startswith('LongTermDebt')), D(0))
                    if ltd is not None and face_ltd and abs(face_ltd - ltd - fl) <= tol(face_ltd, ltd, fl):
                        flags.append('finance lease inside long-term debt (face LTD = note LongTermDebt + lease): not added')
                    elif co_loc.get(f['cik']) == {'in'}:
                        flags.append("finance lease inside a debt line in the company's other filings (ExtensibleList 'in'): not added")
                    elif any(v == fl for t, v, *_ in nodes):   # COF 2020/2024: 'Other borrowings' 75 / 29 = the note finance lease: the lease is that line
                        flags.append('finance lease equals a face debt line (' + next(t for t, v, *_ in nodes if v == fl) + '): inside it, not added')
                    elif any(re.search(r'FinanceLease', t) and not t.startswith('FinanceLease') and DEBT.match(t) for t in vv[col]):   # a debt-AND-lease total (LongTermDebtAndFinanceLease*), not the lease schedule (FinanceLeaseLiabilityPaymentsDue*)
                        flags.append('a debt-and-finance-lease total exists: not added')
                    else:
                        nodes.append(('FinanceLeaseLiability', fl, 'NOTE', 'note lease; no ExtensibleList and no debt line contains it (location by absence: CHECK)'))
            # pre-842 capital leases (founder perimeter; Dhairya 2026-11-14 MSFT FY2016): note-only obligations, consolidated,
            # whose location is not inside a debt line. Location evidence, strongest first:
            #   1. the instance's BalanceSheetLocationAxis member on the fact (OtherCurrentLiabilities / OtherNoncurrent
            #      Liabilities -> outside debt, added; a debt member -> inside, skipped)  [FSN drops these dimensioned facts]
            #   2. a calc arc from a face debt line (inside) or from a non-debt face line (outside)
            #   3. a face debt line whose tag/label names leases (inside)
            #   4. none of these: not added, flagged READER CHECK (absence is not evidence: TMUS/WFC/CVS/DIS keep them in debt)
            lf = (LEASES.get(f['a']) or {}).get(col, [])
            if not on_face_lease and not fl:
                cap_loc = [(t, m, v) for t, m, v in lf if t.startswith('CapitalLeaseObligations') and m]
                cap_und = {t: v for t, m, v in lf if t.startswith('CapitalLeaseObligations') and not m}
                # the balance-sheet amount is the present value split current + noncurrent; a CapitalLeaseObligations total beside
                # both parts can be the gross minimum payments (AMZN 2015: 7,452 gross = 7,239 present value + 213 imputed interest)
                both = all(t in vv[col] or t in cap_und for t in ('CapitalLeaseObligationsCurrent', 'CapitalLeaseObligationsNoncurrent'))
                cl = None if both else (vv[col].get('CapitalLeaseObligations') or cap_und.get('CapitalLeaseObligations'))
                if cl is None and any(t in vv[col] or t in cap_und for t in ('CapitalLeaseObligationsCurrent', 'CapitalLeaseObligationsNoncurrent')):
                    cl = sum((vv[col].get(t, cap_und.get(t, D(0))) for t in ('CapitalLeaseObligationsCurrent', 'CapitalLeaseObligationsNoncurrent')), D(0))
                pars = set().union(*[lease_parent.get(t, set()) for t in ('CapitalLeaseObligations', 'CapitalLeaseObligationsCurrent', 'CapitalLeaseObligationsNoncurrent')])
                if cap_loc:
                    # one figure per location member: Current + Noncurrent when tagged, else the total; duplicates once
                    bym = {}
                    for t, m, v in sorted(set(cap_loc)):
                        bym.setdefault(m, {})[t] = v
                    cap_loc = []
                    for m, d in bym.items():
                        parts = [t for t in ('CapitalLeaseObligationsCurrent', 'CapitalLeaseObligationsNoncurrent') if t in d]
                        cap_loc += [(t, m, d[t]) for t in parts] if parts else [('CapitalLeaseObligations', m, d['CapitalLeaseObligations'])]
                    outs = [(t, m, v) for t, m, v in cap_loc if not DEBT_MEMBER.search(m)]
                    ins = [(t, m, v) for t, m, v in cap_loc if DEBT_MEMBER.search(m)]
                    for t, m, v in outs:
                        nodes.append((t, v, 'NOTE', f"pre-842 capital lease located in {m.split(':')[-1]} (instance BalanceSheetLocationAxis): outside debt"))
                    if ins: flags.append('capital lease located in a debt line (' + ','.join(m.split(':')[-1] for _, m, _ in ins) + '): not added')
                elif cl:
                    if pars & tags: flags.append('capital lease inside a debt line (calc parent): not added')
                    elif pars and pars & set(onbs):
                        nodes.append(('CapitalLeaseObligations', cl, 'NOTE', f"pre-842 capital lease, calc parent {'/'.join(sorted(pars))} is not a debt line"))
                    else:
                        # no location evidence: TMUS, WFC, CVS and DIS keep capital leases inside their debt-note
                        # totals, so absence is not evidence for capital leases; a reader decides
                        flags.append(f'READER CHECK: capital lease {cl} in a note with no location member, calc arc or lease-named debt line: not added')
            total = sum((v for _, v, *_ in nodes), D(0))
            if repo_comb:
                out.append(dict(cik=f['cik'], accession=f['a'], filing_period=f['p'], column=kind, period_end=col, status='combined',
                                tags='+'.join(l['tag'] for l in repo_comb), parts='; '.join(f"{l['tag']} [BS R{l['rep']}:{l['ln']} holds fed funds purchased / repos with other borrowings]" for l in repo_comb),
                                r_pages='', value='', flags='debt_incl_repos (ruling 2026-11-14 d)', fl_loc=loc or ''))
                continue
            out.append(dict(cik=f['cik'], accession=f['a'], filing_period=f['p'], column=kind, period_end=col,
                            status=('component_sum' if len(nodes) > 1 else 'mapped') if nodes else 'not_presented',
                            tags='+'.join(t for t, *_ in nodes), parts='; '.join(f'{t}={v} [{loc_} {why}]' for t, v, loc_, why in nodes),
                            r_pages='+'.join(loc_ for _, _, loc_, _ in nodes), value=str(total) if nodes else '', flags='; '.join(flags), fl_loc=loc or ''))
    return out
def load_evidence(root=None, cache_dir=None):
    """Committed instance evidence (SEC instances; FSN drops these dimensioned/extensible-list facts):
    - finance-lease location (FinanceLeaseLiability*StatementOfFinancialPositionExtensibleList): exam/eras/inputs-notes-eras.jsonl per
      accession, exam/inputs/notes.jsonl for the latest 10-K of each company ('FY0:' + cik);
    - pre-842 capital leases by BalanceSheetLocationAxis: line_map/_lease-locations-pre842-2026-11-14.csv (fills LEASES).
    Plus the per-accession instance cache of standard_run (instance_evidence.py, cache_dir) for every other filing.
    Returns flloc."""
    import os
    root = root or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
    flloc = {}
    for l in open(os.path.join(root, 'exam', 'eras', 'inputs-notes-eras.jsonl')):
        o = json.loads(l)
        if 'fl_loc' in o: flloc[o['acc']] = o['fl_loc']
    for l in open(os.path.join(root, 'exam', 'inputs', 'notes.jsonl')):
        o = json.loads(l)
        if o.get('fl_loc'): flloc['FY0:' + o['cik']] = o['fl_loc']
    LEASES.clear()
    for r in csv.DictReader(open(os.path.join(root, 'line_map', '_lease-locations-pre842-2026-11-14.csv'))):
        LEASES.setdefault(r['adsh'], {}).setdefault(r['ddate'], []).append((r['tag'], r['balance_sheet_location_member'], D(r['value'])))
    import instance_evidence
    cf, cl = instance_evidence.load(cache_dir)
    for a, v in cf.items(): flloc.setdefault(a, v)
    for a, v in cl.items():
        if a not in LEASES: LEASES[a] = v
    return flloc
def total_debt_all(filings, vals, tick, cache_dir=None):
    """total_debt rows for every filing (own and comparative column) from the standard extract (vals: standard_inputs.debt_vals) and the
    committed instance evidence; the former total_debt_all.csv."""
    rows = run(filings, vals, load_evidence(cache_dir=cache_dir))
    for r in rows: r['ticker'] = tick.get(r['cik'].zfill(10), '')
    return rows
if __name__ == '__main__':
    import standard_inputs
    filings = json.load(open('filings.json')); notefacts = json.load(open('notefacts.json'))
    compfacts = json.load(open('compfacts.json')) if __import__('os').path.exists('compfacts.json') else {}
    tk = {r[1]: r[0] for r in csv.reader(open('tk.csv'))}
    rows = total_debt_all(filings, standard_inputs.debt_vals(filings, notefacts, compfacts), tk)
    w = csv.DictWriter(open('total_debt_all.csv', 'w', newline=''), fieldnames=['ticker'] + [k for k in rows[0] if k != 'ticker']); w.writeheader(); w.writerows(rows)
    print(len(rows), collections.Counter(r['status'] for r in rows))
