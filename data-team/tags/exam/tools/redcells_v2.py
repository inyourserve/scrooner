"""Red-cell causes, fixes and evidence for top100-coverage v2 (6e9a31be).
Inputs (run from the scratchpad): v2/cov.csv, v2/sum.csv, exam/lines_eng + predict.py (FY0), wt/.../eras/*-prediction.csv, fixes/*-fixes-*.csv.
Output: v2/redcells_v2.csv."""
import csv,collections,os,glob,subprocess,io,json,re
from datetime import date
D=date.fromisoformat
cov=[r for r in csv.DictReader(open('v2/cov.csv')) if r['class'] in ('DISAGREE','UNCHECKED','BLANK')]
pct={r['ticker']:float(r['pct_proven_plus_reason'] or 0) for r in csv.DictReader(open('v2/sum.csv'))}
ranks={r[1]:(r[0],r[2]) for r in csv.reader(open('exam/ranks.csv'))}
preds=collections.defaultdict(list)
for tk in sorted({x['ticker'] for x in cov}):
    if os.path.exists(f'exam/lines_eng/{tk}.jsonl') and tk in ranks:
        r=subprocess.run(['python3','wt/data-team/tags/exam/tools/predict.py',f'exam/lines_eng/{tk}.jsonl',tk,ranks[tk][0],'wt/data-team/tags/rules','exam/notes.jsonl'],capture_output=True,text=True)
        rows=list(csv.DictReader(io.StringIO(r.stdout)))
        if rows:
            per=json.loads(open(f'exam/lines_eng/{tk}.jsonl').readline())['per']
            preds[tk].append((D(per),rows[0]['acc'],{x['data_point']:x for x in rows}))
    for f in glob.glob(f'wt/data-team/tags/exam/eras/{tk}-*-prediction.csv'):
        rows=list(csv.DictReader(open(f)))
        if rows: preds[tk].append((D(rows[0]['period']),rows[0]['acc'],{x['data_point']:x for x in rows}))
FIX={}
for f in glob.glob('fixes/*-fixes-*.csv'):
    tk=os.path.basename(f).split('-fixes')[0]
    for i,x in enumerate(csv.DictReader(open(f)),start=2):
        FIX[(tk,x['data_point'],x['period_end'])]=(os.path.basename(f),i,x)
REVIEW_BAD={('C','deposits','2024-12-31'),('C','loans_net','2024-12-31'),('AXP','deposits','2024-12-31')}
def pred_for(tk,pe):
    best=None
    for per,acc,m in preds.get(tk,[]):
        d=abs((per-pe).days)
        if d<=10 and (best is None or d<best[0]): best=(d,per,acc,m)
    return best
NOTE_DPS={'weighted_basic_shares','weighted_diluted_shares','cash_paid_for_income_taxes','cash_paid_for_interest','amortization_of_intangibles','sbc','shares_outstanding','dividends_per_share'}
def pev(tk,dp,pe):
    p=pred_for(tk,pe)
    if p and dp in p[3]:
        r=p[3][dp]; return r,p[2],f"predict v7 on {p[2]} ({p[1]}): {r['status']} {r['tags']} stmt {r['stmt'] or '-'} {r['r_page'] or ''} = {r['fy0_value'] or r['fy0_api'] or '-'}"
    return None,None,'no filing-matched prediction'
out=[]
for x in cov:
    tk,dp,pe,cl,rc,rs=x['ticker'],x['data_point'],D(x['period_end']),x['class'],x['reason_code'],x['reason']
    key=(tk,dp,x['period_end']); fx=FIX.get(key)
    r,acc,pe_txt=pev(tk,dp,pe)
    scope='systemic'; owner='Engineering'; cause=fix=''; ev=pe_txt
    shown=f"shown {x['shown_value']} {x['tag']} {x['accession']} {x['r_page']}".strip()
    # ---------------- DISAGREE
    if cl=='DISAGREE':
        if rc=='check_failed:components_sum':
            cause='proof: value equals the printed face total but the components_sum check failed (components on another statement or in a note are dropped; audit R06, shown.py:69-74)'
            fix='S1 prove.py: a printed total that the face prints is PROVEN on the line; components_sum is advisory, or gather components across statements'
            ev=f'{shown}; proof: {rs}'
        elif rc=='shown_is_not_the_authoritative_copy':
            if dp=='sga_expense' and 'GeneralAndAdministrativeExpense' in x['tag'] and 'Selling' in x['tag']:
                cause='proof: authoritative copy is G&A alone, but the filing prints S&M and G&A, so SG&A = component_sum (Dhairya ruling 2026-11-13, MSFT incident); the shown value is right'
                fix='S2 prove.py expectation for sga_expense: component_sum G&A + S&M when both are printed; never G&A alone'
            else:
                cause='proof: authoritative-copy pick (latest-filed vs original) differs from the shown vintage (audit R13)'
                fix='S3 one authority rule for shown and proof: the latest-filed authoritative copy (272117e0/af68721e follow-up); re-serve or re-prove so both read the same copy'
            ev=f'{shown}; proof: {rs}'
        elif rc=='only_a_component_line_presented':
            cause='proof: revenue sanity resolver treats every IS revenue candidate as a component of another and refuses the total'
            fix='S4 prove.py revenue: the top-most revenue line on the IS (the calc parent, or the line whose components tie to it) is the total; component-of-another applies only to children'
            ev=f'{shown}; proof: {rs}'
        elif rc=='shown_differs_from_printed_line':
            if dp=='amortization_of_intangibles' and 'CapitalizedComputerSoftwareAmortization' in rs:
                cause='proof compares intangible amortization with the capitalized-software amortization line; those are different perimeters (amortization card)'
                fix='S5 prove.py: CapitalizedComputerSoftwareAmortization1 is not an expectation for amortization_of_intangibles'
            elif dp=='total_debt':
                scope='reader'; owner='reader'
                cause='served total_debt omits parts the filing prints (current debt / finance or capital leases); ruling total_debt includes finance and capital leases'
                fix='fix file: total_debt component_sum of the printed parts (the proof sum shown in evidence), era covering this year'
            elif dp=='sga_expense' and 'GeneralAndAdministrativeExpense' in x['tag'] and 'Selling' not in x['tag']:
                scope='reader'; owner='reader'
                cause='served SG&A is G&A alone while S&M is printed (ruling 2026-11-13, MSFT incident)'
                fix='fix file: sga_expense component_sum SellingAndMarketingExpense + GeneralAndAdministrativeExpense'
            else:
                scope='reader'; owner='reader'
                cause='served value is not the printed line the proof found'
                fix='fix file: map the printed line (proof evidence) for this era, or record why the served line is the right perimeter'
            ev=f'{shown}; proof: {rs}; '+pe_txt
    # ---------------- UNCHECKED
    elif cl=='UNCHECKED':
        if 'not yet public' in rs and tk=='SHOP':
            cause='SHOP filed its annual reports on Form 40-F before it switched to 10-K, so the proof (10-K only) finds no filing for these years'
            fix='S6 prove.py: accept the 40-F annual report (US-GAAP XBRL) as the year filing for a 40-F-then-10-K filer, else the first 10-K comparative column; otherwise reason history_horizon'
            ev=f'{shown}; proof: {rs}'
        elif 'not yet public' in rs and tk=='GEV':
            cause='GEV pre-spin year (spun from GE 2024-04): no own 10-K; the Form 10 and first 10-K carry carve-out comparatives'
            fix='S6 prove.py: prove pre-spin years against the first 10-K comparative column; earlier years reason history_horizon'
            ev=f'{shown}; proof: {rs}'
        elif 'not yet public' in rs:
            cause='served value for a pre-IPO year; the proof has no 10-K of that year, but the next 10-K prints it as a comparative column'
            fix='S6 prove.py: prove a year with no own 10-K against the next 10-K comparative column (same rule as era_comparative, db5d8c87)'
            ev=f'{shown}; proof: {rs}'
        elif 'not in the fsn-notes bucket' in rs or 'no FSN structure for the shown accession' in rs:
            cause='proof input missing: the shown 10-K has no FSN statement structure in the proof set (quarter not in the fsn-notes bucket, or the accession absent from the loaded set)'
            fix='S7 load the missing FSN quarters/accessions into the proof set (2026 quarters when SEC publishes them), or prove from the filing instance on sec.gov'
            ev=f'{shown}; proof: {rs}'
        elif 'no company_tag_map claim' in rs:
            scope='reader'; owner='reader'
            cause='served value has no tag-map claim and no hand expectation, so nothing to prove against'
            fix='fix file: write the claim for this era (decision, tag, accession, R page, value)'
            ev=f'{shown}; proof: {rs}; '+pe_txt
        elif rc=='proof_is_for_another_value':
            cause='proof is PROVEN for a different value than served (served is the predictor candidate, the proven value is not loaded)'
            fix='S8 loader: serve the proven value (cell_proof.shown_value) or re-prove the served one; one writer per cell'
            ev=f'{shown}; proof: {rs}; '+pe_txt
        elif 'components_without_single_calc_parent' in rs:
            cause='mapper hold: component sum needs one calc parent; the rulings tie face lines instead (opex/SG&A tie, tolerance 0.5 x unit x n)'
            fix='S9 tag-map mapper: accept a component_sum whose face lines tie to the printed total or GP/COR-to-OI span within tolerance, without a single calc parent'
            ev=f'{shown}; {rs}; '+pe_txt
        elif rs.startswith('PREDICTOR-CANDIDATE') or rs.startswith('combined line') or 'presents no' in rs or 'prints no' in rs or rs.startswith('no non-operating'):
            scope='reader'; owner='reader'
            st=(r or {}).get('status','')
            if 'combined line' in rs or st=='combined':
                cause='the filing prints this item only inside a combined line; the served value is the combined line'
                fix='fix file: decision combined (no concept value), unserve the value'
            elif ('presents no' in rs) and r and st in ('mapped','component_sum') and x['tag'] and x['tag'].split(',')[0] in (r['tags'] or ''):
                scope='systemic'; owner='Engineering'
                cause=f"proof reads one statement/tag list; the filing prints the served tag on {r['stmt'] or 'another statement'} {r['r_page']}"
                fix='S16 prove.py: look for the line on every statement the docmap/claim names (DPS on EQ or note, SBC on CF under AllocatedShareBasedCompensationExpense, CI on its own statement)'
            elif 'presents no' in rs or 'prints no' in rs or st in ('not_presented','OUT'):
                cause='the filing has no such line on the statement the proof read; the served value comes from elsewhere'
                fix='fix file: decision not_presented, or map the line where the filing prints it (EQ, CI or note) with stmt and R page'
            else:
                cause='served value is a predictor candidate with no face line behind it'
                fix='fix file: hand-read the filing; mapped with R page, or not_presented/combined'
            ev=f'{shown}; proof: {rs[:200]}; '+pe_txt
        elif 'not mapped for this era' in rs:
            scope='reader'; owner='reader'
            cause='served value is the predictor candidate; the tag-map has no claim covering this era'
            fix='fix file: era-extend the claim to this year (same tag as the nearest year, evidence = this 10-K R page)'
            ev=f'{shown}; proof: {rs[:120]}; '+pe_txt
        else:
            scope='reader'; owner='reader'
            cause='served value with no proof row and no stated reason'
            fix='fix file: hand-read; mapped with R page or a reason'
            ev=f'{shown}; '+pe_txt
    # ---------------- BLANK
    else:
        if rc.startswith('docmap_') and rc.endswith('_not_loaded'):
            st=rc[7:-11]
            cause=f'loader: the filing-checked docmap decided {st}, nothing loaded'
            fix=f'S10 loader: write docmap decisions (not_presented/combined/not_located/review/component_in_note as cell reasons; component_sum as values) for every era year'
            ev=f'docmap {x["docmap_status"]} {x["r_page"]}; '+pe_txt
        elif rc=='proof_disagree':
            cause='mapper hold: the cell proof DISAGREEs, so the mapper refuses to write'
            fix='S11 resolve the underlying proof DISAGREE (most are R13 authority / R06 components / revenue resolver, S1-S4); then the mapper writes'
        elif rc in ('components_without_single_calc_parent',):
            cause='mapper hold: component sum needs one calc parent; the rulings tie face lines instead'
            fix='S9 tag-map mapper: accept a tying face-line component_sum without a single calc parent'
        elif rc=='opex_tie_needs_gross_profit_and_operating_income_of_the_filing':
            cause='mapper hold: opex tie needs GP and OI; the ruling allows COR in place of GP (span COR..OI)'
            fix='S12 mapper: opex tie from COR when no GP line; no OI line -> not_presented'
        elif rc=='opex_components_do_not_tie_gross_profit_to_operating_income':
            scope='reader'; owner='reader'
            cause='face lines between GP/COR and OI do not tie (an unprinted or note-only item sits in the span)'
            fix='fix file: decision combined or not_presented with the face lines listed (ruling §AE: only tying spans are component_sum)'
        elif rc in ('restated_copies_disagree','no_authoritative_fact','components_from_different_filings','mixed_value_sources'):
            cause=f'authority: {rc} (several vintages, none chosen; audit R13)'
            fix='S3 one authority rule: the latest-filed authoritative copy wins; components may come from that one filing'
        elif rc in ('G1_printed_line',):
            cause='slot rule G1 holds cost_of_revenue though a printed COR line exists'
            fix='S13 slot rule G1: release the hold when the face prints a single COR line (or the member-only COGS ruling applies)'
        elif rc in ('filer_scale_error','no_filed_column_for_period','line_presented_combined_with_others','not_captured','component_missing_for_period','no_calc_evidence'):
            if rc in ('component_missing_for_period','no_calc_evidence'):
                scope='reader'; owner='reader'
                cause=f'mapper hold {rc}: a part is missing in this year'
                fix='fix file: era-specific claim (the parts this 10-K prints) or not_presented'
            else:
                cause=f'evidenced reason {rc} stored, but the classifier counts it BLANK'
                fix='S14 top100_coverage classify: count filer_scale_error, no_filed_column_for_period, line_presented_combined_with_others and not_captured as REASON (they carry filing evidence)'
            ev=f'{rs}; '+pe_txt
        elif rc=='proof_proven_but_no_served_value':
            cause='proof PROVEN but no served value (loader did not write the proven value)'
            fix='S8 loader: serve the proven value'
            ev=f'{shown}; '+pe_txt
        else:  # no_value_no_reason
            st=(r or {}).get('status','')
            if r and st in ('mapped','component_sum') and r['tags']:
                if dp in NOTE_DPS or r['stmt'] in ('NOTE','') or r['value_source']=='sec_api':
                    cause=f'value printed in the filing (note/face) but not served: note-only facts are refused (audit R01 prove.py:185,614-624; fsn.py:255-260 drops dimensioned)'
                    fix='S15 accept undimensioned consolidated note facts (ruling §AG) in fsn.py/prove.py; then load the claim'
                else:
                    scope='reader'; owner='reader'
                    cause=f'value printed on the face but not served: no claim for this era'
                    fix=f'fix file: {st} {r["tags"]} stmt {r["stmt"]} {r["r_page"]}, era covering {x["period_end"]}'
            elif r and st in ('not_presented','OUT','combined','component_in_note'):
                scope='reader'; owner='reader'
                cause=f'the filing has no separate line ({st})'
                fix=f'fix file: decision {st} with the predictor rule as evidence, then hand-check'
            elif r:
                scope='reader'; owner='reader'; cause=f'predictor {st}'; fix='fix file: hand-read'
            else:
                PRED={'XOM':('0000034088 Exxon Mobil Corp',2025),'BLK':('0001364742 BlackRock Inc (pre-2024 holdco)',2024),'MRVL':('0001058057 Marvell Technology Group',2021),'AVGO':('0001649338 Broadcom Ltd / 0001441634 Avago',2017),'DIS':('0001001039 Walt Disney Co (pre-2019 holdco)',2018),'LIN':('0000884905 Praxair',2017)}
                if tk in PRED and int(x['fiscal_year'])<=PRED[tk][1]:
                    cause=f'successor registrant: the 10-Ks for this year were filed by the predecessor CIK {PRED[tk][0]}; the build reads only the current CIK'
                    fix='S17 company master: link predecessor CIK filings to the company for the era build, proof and docmap (one company, several filer CIKs)'
                    ev=f'company CIK {ranks.get(tk,("",""))[1]}; every cell of {tk} FY<={PRED[tk][1]} without a filing-matched read'
                elif pe.year>=2026 or x['fiscal_year']=='2026':
                    cause='latest 10-K not in FSN yet (FY2026)'; fix='S7 load the FSN quarter, or prove from the sec.gov instance'
                else:
                    scope='reader'; owner='reader'
                    IPO={'PLTR':2020,'CRWD':2020,'UBER':2019,'DELL':2017}
                    if tk in IPO and int(x['fiscal_year'])<IPO[tk]:
                        cause=f'pre-IPO year: no own 10-K; the first 10-K (FY{IPO[tk]}) prints at most 2 prior years (IS/CF) and 1 prior BS'
                        fix='fix file: comparative column of the first 10-K where printed; otherwise reason history_horizon (no 10-K prints this period)'
                    else:
                        cause='no filing-matched prediction (this year\'s 10-K was not in my era set)'
                        fix='fix file: value from the first 10-K printing the period (own, else next comparative), same tag as the nearest year'
                    near=sorted(preds.get(tk,[]),key=lambda q: abs((q[0]-pe).days))
                    if near and dp in near[0][2]:
                        q=near[0][2][dp]; ev=f"nearest {near[0][1]} ({near[0][0]}): {q['status']} {q['tags']}"
    if fx:
        f,i,row=fx
        if key in REVIEW_BAD:
            ev+=f' | reader fix {f}:{i} says {row["decision"]}, wrong per REVIEW-tag-expert (printed in two 10-Ks)'
        else:
            ev+=f' | reader fix {f}:{i} already decides {row["decision"]} {row.get('tags') or row.get('tag(s)') or row.get('tag','')} {row.get('printed_value','')}'
            if scope=='reader': cause+=' (fix file ready; needs the hybrid build to load it)'
    rk=int(x['rank']); band=f'{(rk-1)//20*20+1}-{(rk-1)//20*20+20}'
    out.append(dict(priority=0,rank=rk,ticker=tk,pct_proven_plus_reason=pct.get(tk,0),band=band,data_point=dp,fiscal_year=x['fiscal_year'],period_end=x['period_end'],cls=cl,coverage_reason=rc,scope=scope,owner=owner,systemic_id=fix.split(' ')[0] if scope=='systemic' else '',cause=cause,fix=fix,evidence=ev))
def pk(o):
    t=o['ticker']; p=pct.get(t,0)
    return (0 if t=='JNJ' else 1 if p>=95 else 2, -p, o['rank'], o['data_point'], o['fiscal_year'])
out.sort(key=pk)
for i,o in enumerate(out,1): o['priority']=i
w=csv.DictWriter(open('v2/redcells_v2.csv','w',newline=''),fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
C=collections.Counter((o['scope'],o['systemic_id']) for o in out)
for k,v in sorted(C.items(),key=lambda kv:-kv[1]): print(v,k)
print(collections.Counter((o['band'],o['scope']) for o in out))
