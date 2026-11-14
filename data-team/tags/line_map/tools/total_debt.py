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
LABEL_DEBT = re.compile(r'(?i)\b(debt|borrowings|notes payable|commercial paper|term loans?|senior notes|bonds payable|finance lease|capital lease)\b')
def run(filings, vals, flloc):
    V = {r['a']: r for r in vals}
    out = []
    latest = {}
    for f in filings: latest[f['cik']] = max(latest.get(f['cik'], ''), f['p'] + '|' + f['a'])
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
            elif l['custom'] and (LABEL_DEBT.search(l['lb']) or LABEL_DEBT.search(header)) and not re.search(r'(?i)interest|operating', l['lb'] + ' ' + l['tag']):
                cand.append((l, 'custom line, debt label' + ('' if LABEL_DEBT.search(l['lb']) else f" (under header '{header}')")))
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
        own = next((d for d in cols if abs((date.fromisoformat(d) - per).days) <= 20), f['p'])
        prior = next((d for d in cols if 330 <= (per - date.fromisoformat(d)).days <= 400), None)
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
                    elif any(re.search(r'FinanceLease', t) for t in vv[col] if t not in ('FinanceLeaseLiability', 'FinanceLeaseLiabilityCurrent', 'FinanceLeaseLiabilityNoncurrent') and DEBT.match(t)):
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
                cl = vv[col].get('CapitalLeaseObligations') or cap_und.get('CapitalLeaseObligations')
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
            out.append(dict(cik=f['cik'], accession=f['a'], filing_period=f['p'], column=kind, period_end=col,
                            status=('component_sum' if len(nodes) > 1 else 'mapped') if nodes else 'not_presented',
                            tags='+'.join(t for t, *_ in nodes), parts='; '.join(f'{t}={v} [{loc_} {why}]' for t, v, loc_, why in nodes),
                            r_pages='+'.join(loc_ for _, _, loc_, _ in nodes), value=str(total) if nodes else '', flags='; '.join(flags), fl_loc=loc or ''))
    return out
if __name__ == '__main__':
    filings = json.load(open('filings.json')); vals = json.load(open('debtvals.json')); flloc = json.load(open('flloc.json'))
    import os
    if os.path.exists('../leasefetch/leases.jsonl'):
        for l in open('../leasefetch/leases.jsonl'):
            o = json.loads(l)
            for t, dt, dims, v, dec in o['facts']:
                if not dt or not re.match(r'^CapitalLeaseObligations(Current|Noncurrent)?$', t): continue
                loc = [m for ax, m in dims if ax.endswith('BalanceSheetLocationAxis')]
                if dims and not loc: continue          # other axes (segments, classes): not consolidated
                if len(dims) > 1: continue
                try: val = D(v)
                except Exception: continue
                LEASES.setdefault(o['acc'], {}).setdefault(dt, []).append((t, loc[0] if loc else '', val))
    for l in open('../exam/notes.jsonl'):
        o = json.loads(l)
        if o.get('fl_loc'): flloc['FY0:' + o['cik']] = o['fl_loc']
    tk = {r[1]: r[0] for r in csv.reader(open('tk.csv'))}
    rows = run(filings, vals, flloc)
    for r in rows: r['ticker'] = tk.get(r['cik'].zfill(10), '')
    w = csv.DictWriter(open('total_debt_all.csv', 'w', newline=''), fieldnames=['ticker'] + [k for k in rows[0] if k != 'ticker']); w.writeheader(); w.writerows(rows)
    print(len(rows), collections.Counter(r['status'] for r in rows))
