"""Sharded standard extract: shard_ciks / merge_shards (scripts/ci/run_extract_sql.py) and assemble equivalence
(data-team/tags/line_map/tools/standard_run.py): 2 shards merged == 1 run. No database."""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("run_extract_sql", ROOT / "scripts/ci/run_extract_sql.py")
rx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rx)
TOOLS = ROOT / "data-team/tags/line_map/tools"
sys.path.insert(0, str(TOOLS))
import standard_run  # noqa: E402


def test_shard_ciks_contiguous_balanced_clamped():
    ciks = [str(c) for c in (500, 7, 90, 12, 3, 44, 1)]
    parts = rx.shard_ciks(ciks, 3)
    assert [len(p) for p in parts] == [3, 2, 2]
    assert [c for p in parts for c in p] == ['1', '3', '7', '12', '44', '90', '500']
    assert len(rx.shard_ciks(ciks, 99)) == 7          # never more shards than CIKs
    assert len(rx.shard_ciks([str(i) for i in range(1, 40)], 50)) == 12   # capped at MAX_SHARDS
    assert rx.shard_ciks(['5'], 8) == [['5']]


def _rows(cik):
    c = f'{int(cik):010d}'
    a, b = f'{c}-24-000001', f'{c}-23-000001'
    return dict(
        lines=[dict(cik=c, a=a, p='2024-12-31', fd='2025-02-01', lines='L1|x', calc='c1'),
               dict(cik=c, a=b, p='2023-12-31', fd='2024-02-01', lines='L2|y', calc='')],
        bs=[dict(a=a, cpv='par|1')],
        notes=[dict(a=a, vals='n|1', mvals='m|2', cvals='c|3', zlines='z|0'), dict(a=b, vals='n|9', mvals=None, cvals=None, zlines=None)],
        face=[dict(a=a, vals='f|5', cvals='fc|6', clines='cl|7'), dict(a=f'{c}-22-000009', vals='f|8', cvals=None, clines=None)],
    )


def _write(d, ciks):
    d.mkdir(parents=True, exist_ok=True)
    for kind in rx.KINDS:
        with open(d / f'{kind}.jsonl', 'w') as f:
            for c in ciks:
                for r in _rows(c)[kind]:
                    f.write(json.dumps(r) + '\n')


def _assembled(d):
    standard_run.assemble(str(d))
    return {k: (d / f'{k}.json').read_text() for k in
            ('filings', 'notefacts', 'memberfacts', 'compfacts', 'zlines', 'clines', 'lentity')}


def test_two_shards_assemble_equals_single_run(tmp_path):
    parts = rx.shard_ciks(['320193', '789019', '1018724', '1652044', '51143'], 2)
    assert len(parts) == 2
    _write(tmp_path / 'single', [c for p in parts for c in p])
    for i, p in enumerate(parts):
        _write(tmp_path / 'sh' / f'standard-extract-shard-{i}-99', p)
    per = rx.merge_shards(str(tmp_path / 'sh'), str(tmp_path / 'merged'))
    assert per['0']['lines'] == 2 * len(parts[0]) and per['1']['face'] == 2 * len(parts[1])
    one, two = _assembled(tmp_path / 'single'), _assembled(tmp_path / 'merged')
    assert one == two
    assert json.loads(one['filings']) and json.loads(one['notefacts'])          # not comparing two empties
    for kind in rx.KINDS:
        assert (tmp_path / 'single' / f'{kind}.jsonl').read_text() == (tmp_path / 'merged' / f'{kind}.jsonl').read_text()


def test_merge_orders_numerically_not_lexically_and_refuses_gaps(tmp_path):
    for i in range(12):
        _write(tmp_path / f'standard-extract-shard-{i}-5', [str(100 + i)])
    rx.merge_shards(str(tmp_path), str(tmp_path / 'o'))
    got = [json.loads(l)['cik'] for l in open(tmp_path / 'o' / 'lines.jsonl')]
    assert got[::2] == [f'{100 + i:010d}' for i in range(12)]
    shutil.rmtree(tmp_path / 'standard-extract-shard-1-5')
    with pytest.raises(SystemExit):
        rx.merge_shards(str(tmp_path), str(tmp_path / 'o2'))


def test_merge_refuses_a_shard_missing_a_kind_and_keeps_retries(tmp_path):
    _write(tmp_path / 'shard-0-1', ['1'])
    _write(tmp_path / 'shard-1-1', ['2'])
    (tmp_path / 'shard-1-1' / 'retries.json').write_text(json.dumps([dict(file='lines-00.sql', outcome='ok_alone')]))
    rx.merge_shards(str(tmp_path), str(tmp_path / 'o'))
    assert json.load(open(tmp_path / 'o' / 'retries.json'))[0]['shard'] == 1
    (tmp_path / 'shard-1-1' / 'face.jsonl').unlink()
    with pytest.raises(SystemExit):
        rx.merge_shards(str(tmp_path), str(tmp_path / 'o3'))


def test_manifest_carries_per_shard_counts_and_cli_shard(tmp_path):
    _write(tmp_path / 'shard-0-1', ['1'])
    per = rx.merge_shards(str(tmp_path), str(tmp_path / 'o'))
    m = rx.manifest(str(tmp_path / 'o'), '1', 'sha', '1', per)
    assert m['shards'] == per and 'shards.json' not in m['files']
    out = subprocess.run([sys.executable, str(ROOT / 'scripts/ci/run_extract_sql.py'), 'shard', '--ciks', '3,1,2', '--n', '2'],
                         capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == [dict(i=0, n=2, ciks='1,2'), dict(i=1, n=1, ciks='3')]
