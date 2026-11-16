"""The RULEBOOK's test column stays honest (Ritwik measurement 2026-11-17, item 3): every cited test exists, and the number of rules
without a test can only go down (lower UNTESTED_MAX when you add tests)."""
import glob, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
UNTESTED_MAX = 85   # 2026-11-17: 85 of 268 rules cite no test function by name (D07/D10/D12 got theirs in da34ff06)


def _rows():
    s = open(os.path.join(ROOT, 'data-team', 'tags', 'RULEBOOK.md')).read()
    return [l for l in s.split('\n') if re.match(r'^\| [A-Z]\d+ \|', l)]


def _test_names():
    names, files = set(), set()
    for p in glob.glob(os.path.join(ROOT, 'data-team', 'tags', '**', 'test_*.py'), recursive=True) + glob.glob(os.path.join(ROOT, 'pipeline', 'tests', '**', 'test_*.py'), recursive=True):
        files.add(os.path.basename(p)[:-3])
        names |= set(re.findall(r'^def (test_\w+)', open(p).read(), re.M))
    return names, files


def test_every_cited_test_exists():
    names, files = _test_names()
    bad = [(l.split('|')[1].strip(), m) for l in _rows() for m in re.findall(r'\btest_\w+', l)
           if not (m in names or m in files or (m.endswith('_') and any(n.startswith(m) for n in names)))]
    assert not bad, bad


def test_untested_rules_never_increase():
    untested = [l.split('|')[1].strip() for l in _rows() if not re.search(r'\btest_\w+', l)]
    assert len(untested) <= UNTESTED_MAX, f'{len(untested)} rules cite no test (max {UNTESTED_MAX}): {untested}'
