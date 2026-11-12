"""Tag Expert predictor ENGINE (v7+). All domain knowledge lives in data-team/tags/rules/*.csv (LEARNING-SYSTEM.md §1-2);
this file only evaluates rules. Deterministic; VERSION = hash of the rule files. Every output row carries the rule_ids that fired.
Inputs: FSN face lines of the latest 10-K (tools/LINES.sql) + optional note facts (tools/NOTES.sql).
Usage: predict.py LINES.jsonl TICKER RANK RULES_DIR [NOTES.jsonl] > TICKER-prediction.csv
"""
import csv, json, re, sys, os, glob, hashlib
def dp_of(concept):
    c = (concept or '').strip()
    c = {'revenue_sanity_resolved':'revenue'}.get(c, c)
    return c[:-9] if c.endswith('_resolved') else c
def load_kb(d):
    rows = []
    h = hashlib.sha256()
    for f in sorted(glob.glob(os.path.join(d, '*.csv'))):
        data = open(f, 'rb').read(); h.update(os.path.basename(f).encode()); h.update(data)
        rows += list(csv.DictReader(open(f, newline='')))
    for r in rows:
        r['W'] = json.loads(r['when'] or '{}'); r['T'] = json.loads(r['then'] or '{}')
    K = {'version': 'v7-' + h.hexdigest()[:10]}
    by = lambda kind: sorted([r for r in rows if r['kind'] == kind], key=lambda r: (r['W'].get('order', 0), r['W'].get('rank', 0)))
    K['DPS'] = [r['data_point'] for r in by('data_point')]
    K['HOME'] = {r['data_point']: r['T']['home_stmt'] for r in by('data_point')}
    K['lib'] = {}
    for r in by('tag'):
        K['lib'][(r['W']['stmt'], r['W']['tag'])] = dict(r['T'], rid=r['rule_id'])
    K['ov'] = {}
    for r in by('override'):
        K['ov'][(r['W']['cik'], r['W']['tag'])] = dict(concept=r['T']['concept'], rid=r['rule_id'])
    K['nd'] = {}
    for r in by('combined_concept'):
        K['nd'].setdefault(r['W']['tag'], (r['T']['data_point'], r['rule_id']))
    K['NOTE'] = {r['data_point']: (r['T']['tag'], r['rule_id']) for r in by('note_default')}
    K['NODEF'] = {r['data_point'] for r in by('note_default') if r['T'].get('disabled_when_no_face')}
    K['NOTE_RULES'] = {}
    for r in by('note_fact'):
        K['NOTE_RULES'].setdefault(r['data_point'], []).append((r['W']['tag'], r['T']['status'], r['rule_id']))
    K['DURATION_SUM'] = {r['data_point'] for r in by('sum_allowed')}
    K['DEMOTE'] = {r['data_point']: (r['W']['label_regex'], r['rule_id']) for r in by('label_demote')}
    K['PREF'] = {r['data_point']: (r['T']['tag'], r['rule_id']) for r in by('prefer_tag')}
    K['BANK'] = {r['data_point']: (r['W']['tags'], r['rule_id']) for r in by('bank_tag')}
    K['DETECT'] = {r['T']['group']: (r['W'], r['rule_id']) for r in by('sector_detect')}
    so = by('sector_out')[0]; K['OUT'] = (set(so['T']['data_points']), so['rule_id'])
    un = by('unclassified_np')[0]; K['UNCL'] = (set(un['T']['data_points']), un['rule_id'])
    sr = [r for r in by('stmt_restrict') if r['data_point'] == 'shares_outstanding'][0]; K['SHR_STMTS'] = (tuple(sr['W']['stmts']), sr['rule_id'])
    K['PTH_OK'] = set(by('parenthetical_allowed')[0]['T']['data_points'])
    K['P'] = {r['rule_id']: r['W'] for r in by('procedure')}
    K['PT'] = {r['rule_id']: json.loads(r.get('then') or '{}') for r in by('procedure')}
    return K
def home(dp): return KB['HOME'].get(dp, 'IS')
KB = None
def sign(v):
    try: x = float(v)
    except (TypeError, ValueError): return ''
    return '+' if x > 0 else '-' if x < 0 else '0'
def main(lines_path, ticker, rank, rulesdir, notes_path=None):
    global KB
    KB = load_kb(os.environ.get('TAG_RULES_DIR') or rulesdir)  # backtest.py passes the rules dir by env, library dir as argv
    lib, ov, nd = KB['lib'], KB['ov'], KB['nd']
    DPS, BANK, NOTE, NOTE_RULES, DURATION_SUM, DEMOTE = KB['DPS'], KB['BANK'], KB['NOTE'], KB['NOTE_RULES'], KB['DURATION_SUM'], KB['DEMOTE']
    P = KB['P']; RID = {}; memcos = []
    L = [json.loads(l) for l in open(lines_path) if l.strip()]
    L = [l for l in L if not l.get('missing')]
    for l in L:
        for k in ('pth', 'cu', 'neg', 'r', 'ln'):
            try: l[k] = int(l.get(k) or 0)
            except (TypeError, ValueError): l[k] = 0
        if l.get('val') == '': l['val'] = None
    cik = L[0]['cik'] if L else ''
    NF = None  # note facts of this filing: tag -> {qtrs: value}
    FLLOC = ['']  # finance-lease balance-sheet location from FinanceLeaseLiability*StatementOfFinancialPositionExtensibleList: in/out/none
    LOC = {}  # IncomeStatementLocationAxis member facts (exam/tools/LOCATION.sql): tag -> {undim, msum, mtot, nm, dc}
    if notes_path:
        NF = {}
        for ln_ in open(notes_path):
            o_ = json.loads(ln_)
            if o_['cik'] != cik: continue
            for kv in (o_.get('facts') or '').split('|'):
                if '=' not in kv: continue
                t_, rest = kv.split('=', 1); q_, v_ = rest.split(':', 1)
                NF.setdefault(t_, {})[int(q_)] = v_
            LOC.update(o_.get('loc') or {})
            FLLOC[0] = o_.get('fl_loc') or FLLOC[0]
    tags = {l['tag'] for l in L}
    def det(g):
        w = KB['DETECT'][g][0]
        return all(t in tags for t in w.get('all_of', [])) and bool(tags & set(w.get('any_of', [])))
    bank, insurer, classified = det('bank'), det('insurer'), det('classified_bs')
    cand = {d: [] for d in DPS}
    single_class = {}
    _PC = KB['P'].get('per_share.class_member_face_line')
    if _PC:
        for _r in {l['r'] for l in L if l['st'] == 'IS'}:
            _rl = [l for l in L if l['st'] == 'IS' and l['r'] == _r]
            if any(l['tag'] == 'StatementClassOfStockAxis' for l in _rl):
                _m = [l for l in _rl if l['tag'].endswith('Member') and re.search(_PC['member_regex'], l['tag'])]
                _other_axes = [l for l in _rl if l['tag'].endswith('Axis') and l['tag'] != 'StatementClassOfStockAxis']
                single_class[_r] = len(_m) == 1 and not _other_axes
    for l in L:
        dp_allowed_inpth = False
        o = ov.get((cik, l['tag']))
        r = lib.get((l['st'], l['tag']))
        if r is None:
            r = next((v for (s, t), v in lib.items() if t == l['tag']), None)
        rids = []
        if o is not None:
            c = o['concept']
            if c.startswith('('): continue
            dec, dp = 'map', dp_of(c); rids.append(o['rid'])
        elif r is not None:
            dec = r['decision']; dp = dp_of(r['concept']) or dp_of(r['parent_concept']); rids.append(r['rid'])
            if not dp and (dec == 'combined' or 'combined' in (r.get('reason_class') or '')) and l['tag'] in nd:
                dec, dp = 'combined', nd[l['tag']][0]; rids.append(nd[l['tag']][1])
        elif l['tag'] in nd:
            dec, dp = 'combined', nd[l['tag']][0]; rids.append(nd[l['tag']][1])
        else:
            continue
        if not dp or dp not in cand: continue
        if l['pth'] and dp not in KB['PTH_OK']: continue
        if l['val'] in (None, ''):
            # Dhairya 2026-11-13 (STZ): a face line printed only under the single class-of-stock member is still the face line
            PC = KB['P'].get('per_share.class_member_face_line')
            if not (PC and dp in PC['data_points'] and l['st'] == 'IS' and not l['pth'] and single_class.get(l['r'])): continue
            l['cm'] = 1; rids.append('per_share.class_member_face_line')
        if dec == 'map' and dp in DEMOTE and re.search(DEMOTE[dp][0], l['lab'] or ''):
            dec = 'combined'; rids.append(DEMOTE[dp][1])
        if dec == 'map' and r is not None and r.get('decision') == 'map' and dp == 'shares_outstanding' and l['st'] not in KB['SHR_STMTS'][0]: continue
        RID[(dp, id(l))] = rids
        cand[dp].append((dec, l))
    out = []
    cur = {'fired': []}
    def emit(d, lines=()):
        ids = list(cur['fired'])
        for l in lines: ids += RID.get((d['data_point'], id(l)), [])
        d['rule_ids'] = ';'.join(dict.fromkeys(i for i in ids if i)); out.append(d)
    for dp in DPS:
        c = cand[dp]; h = home(dp)
        maps = [l for d, l in c if d == 'map']
        comps = [l for d, l in c if d == 'component']
        combs = [l for d, l in c if d == 'combined']
        PREF = KB['PREF']; fired = []; cur['fired'] = fired
        def pick(ls):
            same = [l for l in ls if l['st'] == h] or ls
            if dp in PREF and any(l['tag'] == PREF[dp][0] for l in same): same = [l for l in same if l['tag'] == PREF[dp][0]]; fired.append(PREF[dp][1])
            return max(same, key=lambda l: abs(float(l['val'] or 0)))
        status, chosen, rule = 'not_presented', [], 'no face line'
        if (dp in KB['OUT'][0]) and (bank or (insurer and not classified)):
            status, rule = 'OUT', 'sector template (bank/insurer)'; fired.append(KB['OUT'][1])
        elif dp in BANK:
            fired.append(BANK[dp][1]); hit = [l for l in L if l['tag'] in BANK[dp][0] and not l['pth'] and l['val'] not in (None, '')]
            if bank and hit: status, chosen, rule = 'mapped', [pick(hit)], 'bank template tag'
            elif not bank: status, rule = 'OUT', 'not a bank'
        elif dp == 'operating_expenses':
            PO = P['is.operating_expenses.procedure']; fired.append('is.operating_expenses.procedure')
            IS_ = [l for l in L if l['st'] == 'IS' and not l['pth']]
            def first(tag):
                x = [l for l in IS_ if l['tag'] == tag and l['val'] is not None]
                return x[0] if x else None
            fv = lambda l: float(l['val']) if l is not None and l['val'] is not None else None
            oil, gpl = first(PO['oi_tag']), first(PO['gp_tag'])
            corl = next((l for d, l in cand['cost_of_revenue'] if l['st'] == 'IS'), None)
            revs = [l for d, l in cand['revenue'] if d == 'map' and l['st'] == 'IS']
            rev = max((fv(l) for l in revs), key=abs) if revs else None
            oi, gp, cor = fv(oil), fv(gpl), fv(corl)
            if gp is None and rev is not None and cor is not None: gp = rev - cor
            near = lambda a, b: a is not None and b is not None and abs(a - b) <= max(abs(b) * PO['tolerance'], 1)
            tmpl = [t for t in PO['template_totals'] if first(t)]
            tot = [l for l in IS_ if l['tag'] in PO['total_tags'] and l['val'] is not None]
            excl = [l for l in tot if gp is not None and oi is not None and near(fv(l), gp - oi)]
            incl = [l for l in tot if l not in excl]
            if tmpl and (bank or insurer or corl is None):
                status, chosen, rule = 'mapped', [first(tmpl[0])], 'sector template total'
            elif excl:
                status, chosen, rule = 'mapped', [excl[0]], 'printed opex total excluding cost of revenue (ties to GP - OI)'
            elif gp is not None and oi is not None and oil is not None:
                start = gpl or corl
                band = [l for l in IS_ if l['r'] == oil['r'] and start is not None and l['r'] == start['r'] and start['ln'] < l['ln'] < oil['ln']
                        and l['val'] is not None and l['tag'] not in PO['band_exclude'] and not l['tag'].endswith('Abstract')]
                def dtol(ls):
                    # Dhairya 2026-11-13 (TMO): tie within half the printed unit x number of printed components (from each line's dcml)
                    t = 0.0
                    for l in ls:
                        try: d = int(l.get('dc') or 0)
                        except (TypeError, ValueError): d = 0
                        if -20 < d <= 0: t += 0.5 * 10 ** (-d)
                    return t * PO.get('dcml_tolerance_factor', 1)
                anchors = [x for x in (gpl or corl, oil) if x is not None]
                bsum = sum((-fv(l) if l.get('cr') == 'C' else fv(l)) for l in band) if band else None
                tie_ok = band and (abs(bsum - (gp - oi)) <= dtol(band + anchors) if PO.get('dcml_tolerance') else near(bsum, gp - oi))
                if tie_ok:
                    status, chosen, rule = 'component_sum', band, 'every face line between GP/COR and OI; ties to GP - OI'
                elif incl:
                    status, chosen, rule = 'combined', [incl[0]], 'total includes cost of revenue: combined, never opex'
                else:
                    status, rule = 'not_presented', 'opex lines do not tie to GP - OI'
            elif incl and cor is not None:
                status, chosen, rule = 'combined', [incl[0]], 'total includes cost of revenue'
            elif incl and PO.get('dim_cos_component_sum') and (lambda t0: [l for l in IS_ if l['r'] == t0['r'] and l['ln'] < t0['ln'] and l['val'] is None and l['tag'] in PO['dim_cos_tags']])(incl[0]):
                # Dhairya 2026-11-13 (WYNN): cost of revenue printed only by product/service member inside a one-step total ->
                # opex = component_sum of the valued face lines after the cost line, up to the total
                t0 = incl[0]
                cl = max(l['ln'] for l in IS_ if l['r'] == t0['r'] and l['ln'] < t0['ln'] and l['val'] is None and l['tag'] in PO['dim_cos_tags'])
                band = [l for l in IS_ if l['r'] == t0['r'] and cl < l['ln'] < t0['ln'] and l['val'] is not None and l['tag'] not in PO['band_exclude'] and not l['tag'].endswith('Abstract')]
                cosb = [l for l in band if re.search(PO['cos_label_regex'], l['lab'] or '') or l['tag'].startswith(tuple(PO['cos_tag_prefixes'])) or re.search(r'(?i)interest', l['tag'])]
                if band and not cosb:
                    memcos.append(next(l for l in IS_ if l['r'] == t0['r'] and l['ln'] == cl))
                    status, chosen, rule = 'component_sum', band, 'cost of revenue printed by member only inside the total: opex = face lines after it (WYNN ruling 2026-11-13)'
                else:
                    status, chosen, rule = 'combined', [t0], 'total contains a member-only cost-of-revenue line and other cost lines'
            elif incl:
                # ruling 5 (refined 2026-11-12): no cost-of-revenue line anywhere; total maps unless a cost-of-sales-type line sits inside it
                t0 = incl[0]
                inside = [l for l in IS_ if l['r'] == t0['r'] and l['ln'] < t0['ln'] and l['val'] is not None and not l['tag'].endswith('Abstract')]
                rev_ln = max([l['ln'] for l in revs if l['r'] == t0['r']] or [0])
                inside = [l for l in inside if l['ln'] > rev_ln]
                COS = PO['cos_label_regex']
                cos_tags = tuple(PO['cos_tag_prefixes'])
                hit = [l for l in inside if re.search(COS, l['lab'] or '') or l['tag'].startswith(cos_tags)]
                if hit:
                    status, chosen, rule = 'combined', [t0], 'one-step total contains a cost-of-sales-type line (ruling 5 refined)'
                else:
                    status, chosen, rule = 'mapped', [t0], 'one-step total with no cost-of-sales-type line (ruling 5 refined: GP = revenue)'
            else:
                status, rule = 'not_presented', 'no opex total and no GP/COR anchor'
        elif dp == 'accounts_receivable' and not maps and combs:
            PA = P['bs.accounts_receivable.single_line']; fired.append('bs.accounts_receivable.single_line')
            bsr = [l for l in L if l['st'] == 'BS' and not l['pth'] and l['val'] is not None and re.search(PA['receivable_label'], l['lab'] or '') and not re.search(PA['exclude_label'], l['lab'] or '')]
            head = lambda x: re.split(PA['label_head_split'], x or '')[0] if PA.get('label_head_split') else (x or '')
            if len(bsr) == 1 and not re.search(PA['wider_label'], head(bsr[0]['lab'])):
                status, chosen, rule = 'mapped', bsr, 'single plain receivables line on the BS face (override rule, Dhairya 2026-11-12)'
            else:
                status, chosen, rule = 'combined', [pick(combs)], 'wider receivables tag beside other receivables lines or a wider label'
        elif dp == 'interest_expense' and not maps:
            PI = P['is.interest_expense.plain_caption_net_tag']
            nt = [l for l in L if l['st'] == 'IS' and not l['pth'] and l['val'] is not None and l['tag'] in PI['tags'] and re.fullmatch(PI['label_fullmatch'], l['lab'] or '')]
            if nt:
                fired.append('is.interest_expense.plain_caption_net_tag')
                status, chosen, rule = 'mapped', nt[:1], 'plain "Interest expense" caption on a net tag (interest card VRTX/AAON rule)'
            elif comps or combs:
                cs = [l for d, l in cand['interest_expense'] if d in ('component', 'combined')]
                status, chosen, rule = 'combined', [pick(cs)], 'net or partial interest line'
        elif dp == 'net_income' and not maps:
            PN = P['is.net_income.no_parent_line']; fired.append('is.net_income.no_parent_line')
            ISn = [l for l in L if l['st'] == 'IS' and not l['pth'] and l['val'] is not None]
            pref_line = any(re.search(PN['preferred_label'], l['lab'] or '') for l in ISn)
            nci_line = any(any(p_ in l['tag'] for p_ in PN['nci_tag_parts']) for l in ISn)
            na = [l for l in ISn if l['tag'] == PN['available_tag']]
            pl = [l for l in ISn if l['tag'] == PN['profitloss_tag']]
            if na and not pref_line:
                status, chosen, rule = 'mapped', na[:1], 'available-to-common = NI with no NetIncomeLoss and no preferred line (net-income card)'
            elif pl and not nci_line:
                status, chosen, rule = 'mapped', pl[:1], 'ProfitLoss = NI with no NetIncomeLoss and no NCI line'
            elif comps or combs:
                status, chosen, rule = 'combined', [pick([l for d, l in cand[dp]])], 'incl. NCI or after preferred'
        elif dp == 'depreciation_and_amortization' and not maps and comps:
            fired.append('cf.depreciation_and_amortization.lone_line')
            dep = [l for l in comps if l['tag'] in P['cf.depreciation_and_amortization.lone_line']['lone_tags'] and l['st'] == 'CF']
            others = [l for l in comps if l not in dep and l['st'] == 'CF']
            if dep and not others:
                status, chosen, rule = 'mapped', dep[:1], 'lone CF depreciation line = the D&A line'
            elif len([l for l in comps if l['st'] == 'CF']) >= 2:
                status, chosen, rule = 'component_sum', [l for l in comps if l['st'] == 'CF'], 'CF D&A components (duration sum)'
        elif maps and dp == 'capex' and comps and any(l['st'] == 'CF' for l in comps):
            fired.append('cf.capex.sum_lines'); status, chosen, rule = 'component_sum', [pick(maps)] + [l for l in comps if l['st'] == 'CF'], 'capex = sum of printed CF capex lines (founder 2026-11-04 item 3)'
        elif maps:
            status, chosen, rule = 'mapped', [pick(maps)], 'library map'
        elif comps and (dp in DURATION_SUM) and len({l['st'] for l in comps}) >= 1:
            st = h if any(l['st'] == h for l in comps) else comps[0]['st']
            cs = [l for l in comps if l['st'] == st]
            if len(cs) >= 2 or dp == 'total_debt':
                status, chosen, rule = 'component_sum', cs, 'printed face components (duration sum; total_debt founder sum)'
            elif dp == 'sga_expense' and cs[0]['tag'] in P['is.sga_expense.lone_ga']['tags']:
                PG = P['is.sga_expense.lone_ga']; fired.append('is.sga_expense.lone_ga')
                sell = [l for l in L if l['st'] == 'IS' and not l['pth'] and l is not cs[0] and not l['tag'].endswith('Abstract')
                        and (re.search(PG['selling_label_regex'], l['lab'] or '') or re.search(PG['selling_tag_regex'], l['tag']))
                        and not re.search(PG['not_selling_regex'], (l['lab'] or '') + ' ' + l['tag'])]
                if not sell:
                    status, chosen, rule = 'mapped', cs, 'lone G&A line; no selling/marketing line on the face (TLN ruling 2026-11-13)'
                elif all(l['val'] is not None for l in sell) and all(l['r'] == cs[0]['r'] for l in sell):
                    status, chosen, rule = 'component_sum', cs + sell, 'G&A + printed selling/marketing lines (Dhairya 2026-11-13; never G&A alone when S&M exists)'
                else:
                    status, rule = 'not_presented', 'G&A alone is not SG&A when a selling/marketing line exists (Dhairya 2026-11-13)'
            elif dp == 'interest_expense' and cs[0]['tag'] == P['is.interest_expense.sole_debt']['tag'] and not any('Interest' in l['tag'] and l['tag'] != P['is.interest_expense.sole_debt']['tag'] and l['st'] == 'IS' for l in L):
                status, chosen, rule = 'mapped', cs, 'sole-debt interest rule'; fired.append('is.interest_expense.sole_debt')
            else:
                status, rule = 'not_presented', 'single component only'
        elif combs:
            status, chosen, rule = 'combined', [pick(combs)], 'combined line (library or label demote)'
        elif dp in KB['UNCL'][0] and not classified:
            status, rule = 'not_presented', 'unclassified balance sheet'; fired.append(KB['UNCL'][1])
        elif NF is not None and dp in NOTE_RULES:
            hit = None
            for tg, st_, rid_ in NOTE_RULES[dp]:
                if tg in NF and (4 in NF[tg] or 0 in NF[tg]):
                    hit = (tg, st_); fired.append(rid_); break
            if hit:
                emit(dict(ticker=ticker, rank=rank, data_point=dp, status=hit[1], tags=('us-gaap:' + hit[0]), stmt='NOTE', sign=sign(NF[hit[0]].get(4, NF[hit[0]].get(0))), scale='',
                                era_break='', prior_tag='', value_source='sec_api', acc=L[0]['acc'] if L else '', r_page='', label='', fy0_value=NF[hit[0]].get(4, NF[hit[0]].get(0)), rule='note fact present in the filing (FSN value)'))
                continue
            status, rule = 'not_presented', 'no face line and no note fact'
            if dp == 'interest_income':
                ISl = [l for l in L if l['st'] == 'IS' and not l['pth'] and l['val'] is not None]
                PII = P['notes.interest_income.inside_net_line']
                oil_ = next((l for l in ISl if l['tag'] == PII['oi_tag']), None)
                ptl_ = next((l for l in ISl if l['tag'].startswith(PII['pretax_prefix'])), None)
                if ptl_ is not None:
                    lo_ = oil_['ln'] if oil_ is not None and oil_['r'] == ptl_['r'] else 0
                    nl = [l for l in ISl if l['r'] == ptl_['r'] and lo_ < l['ln'] < ptl_['ln'] and re.search(PII['label_any'], l['lab'] or '') and re.search(PII['label_net'], l['lab'] or '')]
                    if nl:
                        fired.append('notes.interest_income.inside_net_line')
                        status, chosen, rule = 'combined', [nl[0]], 'interest income only inside a net/other face line between OI and pretax'
        elif dp in NOTE and dp not in KB['NODEF']:
            status, rule = 'mapped', 'note-sourced default tag (no face line)'; fired.append(NOTE[dp][1])
            emit(dict(ticker=ticker, rank=rank, data_point=dp, status=status, tags='us-gaap:' + NOTE[dp][0], stmt='NOTE', sign='', scale='',
                            era_break='', prior_tag='', value_source='sec_api', acc=L[0]['acc'] if L else '', r_page='', label='', fy0_value='', rule=rule))
            continue
        PFL = P.get('bs.total_debt.finance_leases')
        if PFL and dp == 'total_debt' and chosen and status in ('component_sum', 'mapped'):
            # founder 2026-11-04 item 5 (total debt includes finance leases); Dhairya 2026-11-13 guards: (1) a debt line whose tag or
            # label already includes leases -> no separate lease line; (2) never both the note total and a face split; (3) the note total
            # only when no face line carries finance leases and the XBRL location list puts the leases outside debt; (4) operating never
            BSf = [l for l in L if l['st'] == 'BS' and not l['pth'] and l.get('val') not in (None, '')]
            incl = lambda l: l['tag'] in PFL['lease_inclusive_tags'] or re.search(PFL['lease_inclusive_label'], l['lab'] or '')
            debt = [l for l in chosen if l['tag'] not in PFL['face_lease_tags']]
            face_fl = [l for l in BSf if l['tag'] in PFL['face_lease_tags'] and not re.search(PFL['operating_label'], l['lab'] or '')]
            if any(incl(l) for l in debt) or any(incl(l) for l in BSf if l['tag'] in PFL['lease_inclusive_tags']):
                if len(debt) != len(chosen): chosen = debt; rule += '; debt line already includes leases (no separate lease line)'
            elif face_fl:
                add = [l for l in face_fl if l not in chosen]
                if add: chosen = chosen + add; status = 'component_sum'; rule += '; + printed finance lease liabilities (founder item 5)'
            elif NF and FLLOC[0] == 'out':
                fl = NF.get('FinanceLeaseLiability', {}).get(0)
                if fl not in (None, '') and float(fl) > 0:
                    chosen = chosen + [dict(st='NOTE', tag='FinanceLeaseLiability', cu=0, val=fl, r='', lab='finance lease liability (note)', acc=chosen[0]['acc'], pth=0, ln=0, dc='')]
                    status = 'component_sum'; rule += '; + note finance lease liability, XBRL location outside debt (founder item 5)'
            fired.append('bs.total_debt.finance_leases')
        if chosen:
            l0 = chosen[0]
            era = [l for l in chosen if l.get('prior') and l['prior'] != l['tag']]
            emit(dict(ticker=ticker, rank=rank, data_point=dp, status=status,
                            tags=';'.join(('us-gaap:' if not l['cu'] else 'custom:') + l['tag'] for l in chosen), stmt=l0['st'],
                            sign=sign(l0['val']), scale=l0.get('dc', ''), era_break='Y' if era else 'N', prior_tag=';'.join(l['prior'] for l in era),
                            value_source='fsn_xbrl' if any(l['cu'] or l.get('cm') for l in chosen) else 'sec_api', acc=l0['acc'], r_page='R%s' % l0['r'],
                            label=l0['lab'], fy0_value=l0['val'], rule=rule), chosen)
        else:
            emit(dict(ticker=ticker, rank=rank, data_point=dp, status=status, tags='', stmt='', sign='', scale='', era_break='', prior_tag='',
                            value_source='', acc=L[0]['acc'] if L else '', r_page='', label='', fy0_value='', rule=rule))
    PLm = KB['P'].get('notes.location_member_total')
    if PLm and LOC:
        # Dhairya 2026-11-13 (CSCO): an undimensioned fact that is only an income-statement-location slice (the location members
        # sum to more) -> component_sum of the location members, value_source fsn_xbrl; a printed location total must tie (dcml tolerance)
        for o in out:
            for tg in PLm['tags'].get(o['data_point'], []):
                x = LOC.get(tg)
                if not x or x.get('msum') is None or (x.get('nm') or 0) < 2: continue
                tol = 0.5 * 10 ** (-(x.get('dc') or 0)) * ((x.get('nm') or 0) + 1)
                if x.get('mtot') is not None and abs(x['msum'] - x['mtot']) > tol: continue
                if x.get('undim') is not None and x['msum'] <= x['undim'] + tol: continue
                if x.get('undim') is None and o['status'] != 'not_presented': continue
                o.update(status='component_sum', tags='us-gaap:' + tg + '{IncomeStatementLocation members}', stmt='NOTE', sign='+', value_source='fsn_xbrl',
                         r_page='', label='', fy0_value='%.4f' % x['msum'], rule='sum of income-statement-location members (CSCO ruling 2026-11-13)',
                         rule_ids='notes.location_member_total')
                break
    if memcos and 'is.cost_of_revenue.member_only' in KB['PT']:
        # Dhairya 2026-11-13 (WYNN): cost of revenue printed only by ProductOrServiceAxis member -> component_sum of the
        # printed member facts (duration sum of printed face lines); companyfacts has no dimensioned facts -> fsn_xbrl
        T = KB['PT']['is.cost_of_revenue.member_only']; l0 = memcos[0]
        for o in out:
            if o['data_point'] == 'cost_of_revenue' and o['status'] == 'not_presented':
                o.update(status=T['status'], tags=('custom:' if l0['cu'] else 'us-gaap:') + l0['tag'], stmt='IS', sign='+', value_source=T['value_source'],
                         r_page='R%s' % l0['r'], label=l0['lab'], fy0_value='', rule='printed member facts of a member-only cost line (WYNN ruling 2026-11-13)',
                         rule_ids='is.cost_of_revenue.member_only')
    for o in out:
        o['fy0_api'] = o.get('fy0_value', '')
        o['evidence_class'] = 'PREDICTED (predict.py %s)' % KB['version']
    w = csv.DictWriter(sys.stdout, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
if __name__ == '__main__':
    main(*sys.argv[1:6])
