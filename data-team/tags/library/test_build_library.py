"""The library generator runs from the repo and every row carries the DB schema's columns (Dhairya 2026-11-16)."""
import csv, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DB_COLUMNS = ['element', 'taxonomy', 'data_point', 'rule_id', 'polarity', 'family', 'deprecated_by', 'replaces', 'statements', 'positions',
              'companies', 'proven_cells', 'certified_cells', 'known_problems', 'links', 'last_verified']


def test_build_writes_the_library_with_the_db_columns(tmp_path):
    env = dict(os.environ, LIBRARY_OUT=str(tmp_path))   # never rewrite the committed library from a test
    out = subprocess.run([sys.executable, os.path.join(HERE, 'build_library.py')], capture_output=True, text=True, check=True, env=env).stdout
    cov = json.loads(out.strip().splitlines()[-1])
    assert cov['rows'] > 0 and 0 <= cov['coverage_pct'] <= 100
    rows = list(csv.DictReader(open(tmp_path / 'library.csv')))
    assert all(c in rows[0] for c in DB_COLUMNS)
    by = {r['element']: r for r in rows}
    # an element the resolver serves carries its data point, ruling and usage
    r = by['PaymentsForRepurchaseOfCommonStock']
    assert 'share_buybacks' in r['data_point'] and r['rule_id'] and int(r['served_cells']) > 0
    # its data point links to the one definition table (metrics/registry/data_points.csv)
    assert r['standard_definition'].startswith('share_buybacks: ') and 'def:registry/data_points.csv#share_buybacks' in r['links']
    assert r['fallback_badges'].startswith('share_buybacks: as_printed')
    # open pattern hits (pattern_detectors.py, founder 2026-11-22) reach each element's known_problems and the coverage summary
    hits = [h for h in csv.DictReader(open(os.path.join(HERE, 'pattern_hits.csv'))) if h['element']]
    assert set(cov['pattern_hits']) == {p['pattern_id'] for p in csv.DictReader(open(os.path.join(HERE, 'patterns.csv')))}
    for h in hits[:20]:
        assert f"pattern {h['pattern_id']} " in by[h['element']]['known_problems'], h
