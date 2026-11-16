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
