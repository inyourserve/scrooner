"""Tests for standard_inputs.one_filing_per_period (rule X110). Run: python3 -m pytest this file."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import standard_inputs as SI


def _f(a, p, fd, cik='0001108524'):
    return dict(cik=cik, a=a, p=p, fd=fd, lines='')


def test_second_10k_for_the_same_period_keeps_only_the_latest_filed():
    fs = [_f('0001108524-20-000014', '2020-01-31', '2020-03-05'),
          _f('0001108524-21-000014', '2021-01-31', '2021-03-17'),
          _f('0001108524-22-000008', '2021-01-31', '2022-02-24'),
          _f('0001108524-22-000013', '2022-01-31', '2022-03-11'),
          _f('0000320193-21-000105', '2021-01-31', '2021-10-29', cik='0000320193')]   # another filer, same period: kept
    kept, dropped = SI.one_filing_per_period(fs)
    assert [f['a'] for f in dropped] == ['0001108524-21-000014']
    assert [f['a'] for f in kept] == ['0001108524-20-000014', '0001108524-22-000008', '0001108524-22-000013', '0000320193-21-000105']


def test_no_duplicates_is_a_no_op():
    fs = [_f('A', '2020-12-31', '2021-02-01'), _f('B', '2021-12-31', '2022-02-01')]
    kept, dropped = SI.one_filing_per_period(fs)
    assert kept == fs and dropped == []
