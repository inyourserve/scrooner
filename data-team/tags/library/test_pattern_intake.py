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
