"""pattern_intake.py: each verifier FAIL in registry.csv opens exactly one tag-expert intake row; reruns add nothing."""
import csv, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REG_HDR = 'ticker,date,verdict,coverage_sha256,seed,n,errors,upper_bound_95,approver\n'
H1, H2, H3 = 'a' * 64, 'b' * 64, 'c' * 64


def run(tmp, reg_text):
    reg = tmp / 'registry.csv'
    reg.write_text(reg_text)
    appr = tmp / 'approvals'
    appr.mkdir(exist_ok=True)
    (appr / 'WMT-final-draw-2026-11-22.md').write_text('draw')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'pattern_intake.py'), '--registry', str(reg), '--intake',
                        str(tmp / 'intake.csv'), '--approvals', str(appr), '--today', '2026-11-22'],
                       capture_output=True, text=True, check=True)
    return r.stdout, list(csv.DictReader(open(tmp / 'intake.csv')))


def test_fail_rows_open_intake_rows_once(tmp_path):
    reg = REG_HDR + f'GILD,2026-11-16,PASS,{H1},s,32,0,0.08,R\nWMT,2026-11-22,FAIL,{H2},s2,32,1,0.13,R\n'
    out, rows = run(tmp_path, reg)
    assert [r['intake_id'] for r in rows] == [f'PI-WMT-2026-11-22-{H2[:8]}']
    r = rows[0]
    assert r['status'] == 'OPEN' and r['owner'] == 'tag-expert' and r['errors'] == '1'
    assert r['evidence'].endswith('WMT-final-draw-2026-11-22.md')
    # the tag expert's edits survive a rerun, and a rerun adds nothing
    text = (tmp_path / 'intake.csv').read_text().replace(',OPEN,', ',CLOSED,')
    (tmp_path / 'intake.csv').write_text(text)
    out, rows = run(tmp_path, reg)
    assert len(rows) == 1 and rows[0]['status'] == 'CLOSED' and '0 new' in out
    # a new FAIL verdict (same ticker, new coverage hash) appends one more row
    out, rows = run(tmp_path, reg + f'WMT,2026-11-23,FAIL,{H3},s3,32,0,0.08,R\n')
    assert [r['verdict_date'] for r in rows] == ['2026-11-22', '2026-11-23'] and rows[0]['status'] == 'CLOSED'


def test_malformed_fail_row_is_skipped(tmp_path):
    out, rows = run(tmp_path, REG_HDR + 'bad ticker,2026-11-22,FAIL,xyz,s,32,0,0.08,R\n')
    assert rows == []


# ---------------------------------------------------------------- drill source (pattern_intake.py --drills)
DRILL_HDR = ('date,class,kind,ticker,cik,data_point,period_end,accession,tag,resolver_status,resolver_value,key_source,key_value,'
             'evidence_label,evidence,detail\n')
ATT_HDR = 'date,ticker,data_point,gate,evidence_label,compared,agree,rule_gap,data_gap,filer_error\n'


def miss(day, cls, kind, tk, dp, pe, tag='', ev=''):
    return f'{day},{cls},{kind},{tk},1,{dp},{pe},A1,{tag},mapped,5,cell_proof PROVEN,6,DATA-INFERRED,{ev},\n'


def run_drills(tmp, intake_text=None):
    intake = tmp / 'intake.csv'
    if intake_text is not None:
        intake.write_text(intake_text)
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'pattern_intake.py'), '--drills', str(tmp / 'drills'),
                        '--intake', str(intake), '--accuracy', str(tmp / 'acc.csv'), '--inbox', str(tmp / 'inbox'),
                        '--eligible', str(tmp / 'eligible.csv'), '--today', '2026-11-23'],
                       capture_output=True, text=True, check=True)
    return r.stdout, list(csv.DictReader(open(intake))), list(csv.DictReader(open(tmp / 'acc.csv')))


def test_drill_misses_group_dedupe_flag_and_keep_expert_edits(tmp_path):
    d = tmp_path / 'drills'
    d.mkdir()
    (d / '2026-11-21.csv').write_text(
        DRILL_HDR + miss('2026-11-21', 'rule_gap', 'proof_disagree', 'AA', 'sga_expense', '2024-12-31', 'SellingGeneralAndAdministrativeExpense')
        + miss('2026-11-21', 'rule_gap', 'proof_disagree', 'BB', 'sga_expense', '2024-12-31', 'SellingGeneralAndAdministrativeExpense')
        + miss('2026-11-21', 'data_gap', 'proof_disagree', 'AA', 'goodwill', '2019-03-31', '', 'proof 0001-19-1 Goodwill=5; no resolver row')
        + miss('2026-11-21', 'data_gap', 'proof_disagree', 'BB', 'goodwill', '2019-03-31', '', 'proof 0002-19-1 Goodwill=7; no resolver row')
        + miss('2026-11-21', 'rule_gap', 'no_role', 'AA', 'net_income', '2024-12-31'))
    # the same AA sga cell again on a later day (deduped), plus one new CC sga cell
    (d / '2026-11-22.csv').write_text(
        DRILL_HDR + miss('2026-11-22', 'rule_gap', 'proof_disagree', 'AA', 'sga_expense', '2024-12-31', 'SellingGeneralAndAdministrativeExpense')
        + miss('2026-11-22', 'rule_gap', 'proof_disagree', 'CC', 'sga_expense', '2023-12-31', 'SellingGeneralAndAdministrativeExpense'))
    verifier = (','.join(['PI-WMT-2026-11-22-bbbbbbbb', '2026-11-22', 'tag-expert', 'OPEN', 'WMT', '2026-11-22', f'WMT|2026-11-22|{H2}',
                          's2', '1', '0.13', 'R', 'e', '', '']) + '\n')
    old_hdr = 'intake_id,opened,owner,status,ticker,verdict_date,registry_key,seed,errors,upper_bound_95,approver,evidence,pattern_id,resolution\n'
    out, rows, _ = run_drills(tmp_path, old_hdr + verifier)
    v = [r for r in rows if r['source'] == 'verifier']
    assert len(v) == 1 and v[0]['intake_id'] == 'PI-WMT-2026-11-22-bbbbbbbb' and v[0]['errors'] == '1'   # upgraded, values kept
    dr = {(r['miss_class'], r['data_point']): r for r in rows if r['source'] == 'drill'}
    assert set(dr) == {('rule_gap|proof_disagree', 'sga_expense'), ('data_gap|proof_disagree', 'goodwill'), ('rule_gap|no_role', 'net_income')}
    sga = dr[('rule_gap|proof_disagree', 'sga_expense')]
    assert (sga['companies'], sga['cells'], sga['days'], sga['first_seen'], sga['last_seen']) == ('3', '3', '2', '2026-11-21', '2026-11-22')
    assert sga['element'] == 'SellingGeneralAndAdministrativeExpense' and sga['flag'] == 'rule_proposal' and sga['ticker'] == 'AA,BB,CC'
    gw = dr[('data_gap|proof_disagree', 'goodwill')]
    assert gw['element'] == 'Goodwill' and gw['flag'] == 'recurring'          # element from the proof; a data gap is not a rule
    assert dr[('rule_gap|no_role', 'net_income')]['flag'] == ''               # one company: not recurring
    # the tag expert closes the sga row; a rerun keeps that and adds nothing
    intake = tmp_path / 'intake.csv'
    rows2 = [dict(r, status='CLOSED', pattern_id='P-SGA') if r['intake_id'] == sga['intake_id'] else r for r in rows]
    with open(intake, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows2)
    out, rows3, _ = run_drills(tmp_path)
    assert '0 new, 0 updated' in out and len(rows3) == len(rows)
    s3 = next(r for r in rows3 if r['intake_id'] == sga['intake_id'])
    assert s3['status'] == 'CLOSED' and s3['pattern_id'] == 'P-SGA'
    # the verifier source still appends to the upgraded file
    reg = tmp_path / 'registry.csv'
    reg.write_text(REG_HDR + f'WMT,2026-11-23,FAIL,{H3},s3,32,0,0.08,R\n')
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'pattern_intake.py'), '--registry', str(reg), '--intake', str(intake),
                    '--approvals', str(tmp_path), '--today', '2026-11-23'], check=True, capture_output=True)
    rows4 = list(csv.DictReader(open(intake)))
    assert len(rows4) == len(rows3) + 1 and rows4[-1]['source'] == 'verifier' and rows4[-1]['verdict_date'] == '2026-11-23'


def test_class_accuracy_latest_day_wins_and_graduation_bar(tmp_path):
    d = tmp_path / 'drills'
    d.mkdir()
    (d / '2026-11-21.csv').write_text(DRILL_HDR)
    (d / '2026-11-22.csv').write_text(DRILL_HDR)
    # revenue: 200 companies, filing-checked, all agree -> graduates; day 1's miss for T0 is superseded by day 2's agree
    a1 = ATT_HDR + '2026-11-21,T0,revenue,docmap,FILING-CHECKED,1,0,1,0,0\n'
    a2 = ATT_HDR + ''.join(f'2026-11-22,T{i},revenue,docmap,FILING-CHECKED,1,1,0,0,0\n' for i in range(200))
    # sga: 300 companies with proof keys only (DATA-INFERRED) -> never graduates; data_gap counted apart
    a2 += ''.join(f'2026-11-22,T{i},sga_expense,proof,DATA-INFERRED,2,2,0,0,0\n' for i in range(300))
    a2 += '2026-11-22,T0,sga_expense,proof,DATA-INFERRED,5,0,0,5,0\n'.replace('proof,', 'proof_np,')
    # cogs: 200 filing-checked companies with 2 errors -> 99.0% but upper bound > 1.5% -> no
    a2 += ''.join(f'2026-11-22,T{i},cost_of_revenue,docmap,FILING-CHECKED,1,{0 if i < 2 else 1},{1 if i < 2 else 0},0,0\n' for i in range(200))
    (d / '2026-11-21-attempts.csv').write_text(a1)
    (d / '2026-11-22-attempts.csv').write_text(a2)
    out, _, acc = run_drills(tmp_path)
    by = {r['class']: r for r in acc}
    rev, sga, cogs = by['revenue'], by['sga_expense'], by['cost_of_revenue']
    assert (rev['fc_attempts'], rev['fc_correct'], rev['fc_companies'], rev['graduated']) == ('200', '200', '200', 'yes')
    assert float(rev['fc_cp_upper_error_95']) <= 0.015 and rev['days'] == '1'
    assert (sga['attempts'], sga['correct'], sga['accuracy'], sga['fc_attempts'], sga['graduated']) == ('600', '600', '1.0000', '0', 'no')
    assert sga['data_gap_excluded'] == '5'
    assert cogs['fc_accuracy'] == '0.9900' and float(cogs['fc_cp_upper_error_95']) > 0.015 and cogs['graduated'] == 'no'
    assert '1 graduated' in out


def test_every_rule_gap_miss_class_opens_one_deduped_inbox_proposal_linked_to_evidence(tmp_path):
    d = tmp_path / 'drills'
    d.mkdir()
    sga = 'SellingGeneralAndAdministrativeExpense'
    (d / '2026-11-21.csv').write_text(
        DRILL_HDR + miss('2026-11-21', 'rule_gap', 'proof_disagree', 'AA', 'sga_expense', '2024-12-31', sga)
        + miss('2026-11-21', 'rule_gap', 'proof_disagree', 'BB', 'sga_expense', '2024-12-31', sga)
        + miss('2026-11-21', 'rule_gap', 'no_role', 'AA', 'net_income', '2024-12-31')       # one company: still proposed
        + miss('2026-11-21', 'data_gap', 'proof_disagree', 'AA', 'goodwill', '2019-03-31', '', 'proof 0001-19-1 Goodwill=5'))
    inbox = tmp_path / 'inbox'
    inbox.mkdir()
    (inbox / 'STATUS.csv').write_text('proposal_file,rule_id,status,backtest_delta,date,note\nold.csv,r1,accepted v1,,2026-11-13,n\n')
    out, intake, _ = run_drills(tmp_path)
    props = list(csv.DictReader(open(inbox / 'drill-auto.csv')))
    assert len(props) == 2 and '2 rules/inbox proposal(s) (2 new)' in out         # data_gap is not a rule: no proposal
    by = {r['data_point']: r for r in props}
    p = by['sga_expense']
    assert p['kind'] == 'proposal_open' and p['proposed_by'] == 'daily-drill-auto' and p['when'] == '' and p['scope'] == 'all'
    assert 'drills:data-team/tags/drills/2026-11-21.csv' in p['evidence']              # linked to the drill file
    iid = next(r['intake_id'] for r in intake if r['data_point'] == 'sga_expense')
    assert p['finding'].startswith(iid) and 'AA sga_expense 2024-12-31' in p['finding'] and 'companies=2' in p['note']
    st = list(csv.DictReader(open(inbox / 'STATUS.csv')))
    assert st[0]['rule_id'] == 'r1' and st[0]['status'] == 'accepted v1'              # existing status rows untouched
    assert {r['rule_id'] for r in st[1:]} == {r['rule_id'] for r in props} and {r['status'] for r in st[1:]} == {'open'}
    # a later day adds a company to the same pattern and a new pattern: same rule_id, one new proposal, tag expert edits kept
    rows = list(csv.DictReader(open(inbox / 'drill-auto.csv')))
    for r in rows:
        if r['data_point'] == 'sga_expense':
            r.update(kind='override', when='{"x":1}', then='{"y":2}')
    with open(inbox / 'drill-auto.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    (d / '2026-11-22.csv').write_text(
        DRILL_HDR + miss('2026-11-22', 'rule_gap', 'proof_disagree', 'CC', 'sga_expense', '2023-12-31', sga)
        + miss('2026-11-22', 'rule_gap', 'proof_disagree', 'CC', 'goodwill', '2023-12-31', 'Goodwill'))
    out, _, _ = run_drills(tmp_path)
    props2 = {r['rule_id']: r for r in csv.DictReader(open(inbox / 'drill-auto.csv'))}
    assert len(props2) == 3 and '(1 new)' in out and p['rule_id'] in props2
    assert props2[p['rule_id']]['kind'] == 'override' and props2[p['rule_id']]['when'] == '{"x":1}'
    assert len(list(csv.DictReader(open(inbox / 'STATUS.csv')))) == 4
    out, _, _ = run_drills(tmp_path)                                                    # idempotent rerun
    assert '(0 new)' in out and len(list(csv.DictReader(open(inbox / 'STATUS.csv')))) == 4


def test_graduated_class_is_marked_auto_map_eligible_and_revoked_when_it_drops(tmp_path):
    d = tmp_path / 'drills'
    d.mkdir()
    (d / '2026-11-22.csv').write_text(DRILL_HDR)
    good = ATT_HDR + ''.join(f'2026-11-22,T{i},revenue,docmap,FILING-CHECKED,1,1,0,0,0\n' for i in range(200))
    good += ''.join(f'2026-11-22,T{i},sga_expense,proof,DATA-INFERRED,1,1,0,0,0\n' for i in range(300))   # proof keys never graduate
    (d / '2026-11-22-attempts.csv').write_text(good)
    out, _, _ = run_drills(tmp_path)
    el = list(csv.DictReader(open(tmp_path / 'eligible.csv')))
    assert [(r['class'], r['status'], r['graduated_on'], r['fc_companies']) for r in el] == [('revenue', 'auto-map-eligible', '2026-11-23', '200')]
    assert '1 auto-map-eligible' in out
    # five wrong filing-checked rows on a later day: the bar fails, the class is revoked (kept, not deleted)
    bad = ATT_HDR + ''.join(f'2026-11-24,T{i},revenue,docmap,FILING-CHECKED,1,{0 if i < 5 else 1},{1 if i < 5 else 0},0,0\n' for i in range(200))
    (d / '2026-11-24.csv').write_text(DRILL_HDR)
    (d / '2026-11-24-attempts.csv').write_text(bad)
    out, _, _ = run_drills(tmp_path)
    el = list(csv.DictReader(open(tmp_path / 'eligible.csv')))
    assert [(r['class'], r['status'], r['graduated_on']) for r in el] == [('revenue', 'revoked', '2026-11-23')]
