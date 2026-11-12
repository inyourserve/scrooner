"""Tests for backtest.py with tiny fixtures: stub predictors, real grade.py, no DB, no git.
Run: python3 -m pytest data-team/tags/exam/tools/test_backtest.py"""
import csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest  # noqa: E402

STUB = 'import sys\nsys.stdout.write(open(sys.argv[4] + "/" + sys.argv[2] + ".csv").read())\n'
KEYF = ['ticker', 'data_point', 'status', 'tags', 'stmt', 'r_page', 'label', 'fy0_api', 'evidence_class', 'note']
PREDF = ['ticker', 'rank', 'data_point', 'status', 'tags', 'rule_ids']
HAND_TK = [f'T{i:02d}' for i in range(1, 21)]
TAG = {'revenue': 'us-gaap:Revenues', 'goodwill': 'us-gaap:Goodwill'}


def write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)


def key(tk, dp, note=''):
    return dict(ticker=tk, data_point=dp, status='mapped', tags=TAG[dp], stmt='IS', r_page='R4', label=dp, fy0_api='',
                evidence_class='FILING-CHECKED', note=note)


# Not hand-verified key rows (must be excluded): T21 AUTO, T22 machine-full-filing, T24 AUTO even with a check: hand;
# T23 machine + check: hand is kept.
EXTRA = {'T21': 'AUTO: first candidate tag on face', 'T22': 'check: machine-full-filing | accn x R4.htm',
         'T23': 'check: machine-full-filing | check: hand R4.htm agree', 'T24': 'AUTO: R4.htm read | check: hand R4.htm agree'}


def setup(tmp, wrong_base, wrong_cand):
    """wrong_* = set of (ticker, data_point) the predictor gets wrong (wrong tag); everything else right."""
    keys = tmp / 'keys'
    for tk in HAND_TK:
        write(keys / f'{tk}-docmap-2026-11-13.csv', KEYF, [key(tk, 'revenue'), key(tk, 'goodwill')])
    for tk, note in EXTRA.items():
        write(keys / f'{tk}-docmap-2026-11-13.csv', KEYF, [key(tk, 'revenue', note)])
    lines = tmp / 'lines'; lines.mkdir()
    for tk in HAND_TK + list(EXTRA):
        (lines / f'{tk}.jsonl').write_text('{}\n')
    write(tmp / 'groups.csv', ['ticker', 'sector', 'template_group'], [dict(ticker=t, sector='Technology', template_group='corporate')
                                                                         for t in HAND_TK + list(EXTRA)])
    for name, wrong in (('base', wrong_base), ('cand', wrong_cand)):
        d = tmp / name
        d.mkdir()
        (d / 'predict.py').write_text(STUB)
        for tk in HAND_TK + list(EXTRA):
            dps = ['revenue', 'goodwill'] if tk in HAND_TK else ['revenue']
            write(d / 'lib' / f'{tk}.csv', PREDF, [dict(ticker=tk, rank=0, data_point=dp, status='mapped',
                                                        tags='us-gaap:Wrong' if (tk, dp) in wrong else TAG[dp], rule_ids=f'r.{dp}') for dp in dps])
    return ['--baseline', str(tmp / 'base/predict.py'), '--baseline-lib', str(tmp / 'base/lib'),
            '--candidate', str(tmp / 'cand/predict.py'), '--candidate-lib', str(tmp / 'cand/lib'),
            '--keys-dir', str(keys), '--lines-dir', str(lines), '--groups-csv', str(tmp / 'groups.csv'),
            '--ranks-csv', '', '--work-dir', str(tmp / 'work'), '--out', str(tmp / 'report'), '--workers', '2']


def report(tmp):
    return {(r['data_point'], r['group']): r for r in csv.DictReader(open(tmp / 'report.csv'))}


GW_BASE_WRONG = {('T01', 'goodwill'), ('T02', 'goodwill')}  # goodwill x corporate baseline 18/20 = 90%, not graduated


def test_regression_in_graduated_class_fails(tmp_path):
    # revenue x corporate is 21/21 = 100% (graduated); the candidate breaks one row there although net is +1
    args = setup(tmp_path, GW_BASE_WRONG, {('T05', 'revenue')})
    assert backtest.main(args) == 1
    r = report(tmp_path)[('revenue', 'corporate')]
    assert (r['n'], r['right_to_wrong'], r['graduated']) == ('21', '1', 'Y')
    assert 'revenue x corporate' in (tmp_path / 'report.md').read_text()


def test_net_gain_passes(tmp_path):
    # fixes 2 goodwill rows, breaks 1 goodwill row (class at 90%, not graduated): net +1 -> pass
    args = setup(tmp_path, GW_BASE_WRONG, {('T03', 'goodwill')})
    assert backtest.main(args) == 0
    r = report(tmp_path)[('goodwill', 'corporate')]
    assert (r['n'], r['baseline_acc'], r['candidate_acc'], r['right_to_wrong'], r['wrong_to_right']) == ('20', '90.0', '95.0', '1', '2')


def test_net_zero_with_changes_fails(tmp_path):
    args = setup(tmp_path, GW_BASE_WRONG, {('T01', 'goodwill'), ('T03', 'goodwill')})
    assert backtest.main(args) == 1


def test_identical_predictors_pass(tmp_path):
    args = setup(tmp_path, GW_BASE_WRONG, GW_BASE_WRONG)
    assert backtest.main(args) == 0
    assert '+0' in (tmp_path / 'report.md').read_text()


def test_auto_and_machine_rows_excluded(tmp_path):
    # the candidate breaks the AUTO (T21, T24) and machine-only (T22) revenue rows in the graduated revenue class; they are
    # not hand-verified, so they are not compared; the machine + check: hand row (T23) is compared
    args = setup(tmp_path, GW_BASE_WRONG, {('T21', 'revenue'), ('T22', 'revenue'), ('T24', 'revenue'), ('T01', 'goodwill')})
    assert backtest.main(args) == 0
    assert report(tmp_path)[('revenue', 'corporate')]['n'] == '21'


def test_ledger_rows(tmp_path):
    args = setup(tmp_path, GW_BASE_WRONG, {('T01', 'goodwill')})
    led = tmp_path / 'ledger.csv'
    assert backtest.main(args + ['--ledger', str(led)]) == 0
    rows = list(csv.DictReader(open(led)))
    assert len(rows) == 41 and {r['ticker'] for r in rows}.isdisjoint({'T21', 'T22', 'T24'})
    r = next(r for r in rows if (r['ticker'], r['data_point']) == ('T01', 'goodwill'))
    assert (r['result'], r['rule_ids'], r['group'], r['evidence']) == ('wrong', 'r.goodwill', 'corporate', 'hand')
