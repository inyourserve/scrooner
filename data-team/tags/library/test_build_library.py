"""The library generator runs from the repo and every row carries the DB schema's columns (Dhairya 2026-11-16).
One tag library (2026-11-22): the build also writes each card's generated block, and CI fails when the committed
library is older than the newest resolver output."""
import csv, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(HERE, '..', 'cards')
sys.path.insert(0, HERE)
import build_library as B   # noqa: E402

DB_COLUMNS = ['element', 'taxonomy', 'data_point', 'rule_id', 'polarity', 'family', 'deprecated_by', 'replaces', 'statements', 'positions',
              'companies', 'proven_cells', 'certified_cells', 'known_problems', 'links', 'last_verified']


def _build(tmp_path):
    cards = tmp_path / 'cards'
    shutil.copytree(CARDS, cards)
    for name in os.listdir(cards):   # start from the hand-written cards only, so the build must write every block itself
        if name.endswith('.md'):
            text = B.hand_written((cards / name).read_text(encoding='utf-8'))
            (cards / name).write_text(text.replace(B.HAND + '\n', ''), encoding='utf-8')
    env = dict(os.environ, LIBRARY_OUT=str(tmp_path), CARDS_DIR=str(cards))   # never rewrite the committed library or cards from a test
    out = subprocess.run([sys.executable, os.path.join(HERE, 'build_library.py')], capture_output=True, text=True, check=True, env=env).stdout
    return json.loads(out.strip().splitlines()[-1]), cards


def test_build_writes_the_library_with_the_db_columns(tmp_path):
    cov, cards = _build(tmp_path)
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
    # polarity is the class the DB loaders store (rules/polarity.csv: capex is +, normalised)
    assert 'capex:positive' in by['PaymentsToAcquirePropertyPlantAndEquipment']['polarity'].split(';')


def test_every_hand_written_card_gets_a_generated_block_and_keeps_its_prose(tmp_path):
    cov, cards = _build(tmp_path)
    for name in sorted(os.listdir(CARDS)):
        if not name.endswith('.md'):
            continue
        before = B.hand_written(open(os.path.join(CARDS, name), encoding='utf-8').read())
        after = open(cards / name, encoding='utf-8').read()
        assert after.count(B.GEN_BEGIN) == 1 and after.count(B.GEN_END) == 1, name
        # the hand-written part is kept line for line (the HAND-WRITTEN marker is the only added line)
        hand = [ln for ln in B.hand_written(after).splitlines() if ln != B.HAND]
        assert hand == [ln for ln in before.splitlines() if ln != B.HAND], name
    interest = open(cards / 'interest.md', encoding='utf-8').read()
    block = interest[interest.index(B.GEN_BEGIN):]
    assert '### `InterestExpense`' in block and '**Data point:** interest_expense' in block and '**Rules:**' in block
    assert '**Known problems:**' in block and cov['resolver_version'] in block


def test_card_block_is_rebuilt_in_place_and_never_feeds_the_card_index(tmp_path):
    cards = tmp_path / 'cards'
    cards.mkdir()
    card = cards / 'x.md'
    card.write_text('# Card x\n\nHand prose about `PaymentsForRepurchaseOfCommonStock`.\n', encoding='utf-8')
    row = {k: '' for k in B.COLUMNS}
    rows = {'PaymentsForRepurchaseOfCommonStock': dict(row, element='PaymentsForRepurchaseOfCommonStock', data_point='share_buybacks', served_cells='9'),
            'NotNamedInTheCard': dict(row, element='NotNamedInTheCard', data_point='capex', served_cells='99')}
    old = B.CARDS
    B.CARDS = str(cards)
    try:
        B.write_cards(rows, {'resolver_version': 'resolver-all110-.1'})
        first = card.read_text(encoding='utf-8')
        B.write_cards(rows, {'resolver_version': 'resolver-all110-.2'})
        second = card.read_text(encoding='utf-8')
    finally:
        B.CARDS = old
    assert first.startswith('# Card x\n' + B.HAND + '\n') and 'Hand prose about' in first
    assert '### `PaymentsForRepurchaseOfCommonStock`' in first and 'NotNamedInTheCard' not in first
    assert second.count(B.GEN_BEGIN) == 1 and '.2' in second and 'resolver-all110-.1' not in second
    assert B.hand_written(second) == B.hand_written(first)
    hits = tmp_path / 'pattern_hits.csv'
    hits.write_text('element,pattern_id,ticker\nPaymentsForRepurchaseOfCommonStock,P07,AAPL\nPaymentsForRepurchaseOfCommonStock,P07,MSFT\n', encoding='utf-8')
    block = B.card_section('x.md', B.hand_written(second), rows, {'resolver_version': '.2'}, B.pattern_hits(str(hits)))
    assert '**Pattern hits:** P07 (2)' in block
    # element names inside the generated block are not hand-written mentions
    card.write_text(B.hand_written(first) + '\n' + B.GEN_BEGIN + ' -->\n`NotNamedInTheCard`\n' + B.GEN_END + '\n', encoding='utf-8')
    assert 'NotNamedInTheCard' not in B.hand_written(card.read_text(encoding='utf-8'))


def _resolver(tmp_path, *versions):
    d = tmp_path / 'resolver'
    d.mkdir()
    for i, v in enumerate(versions):
        (d / f'T{i}.csv').write_text(f'ticker,resolver_version\nT{i},{v}\n', encoding='utf-8')
    return str(d)


def test_version_check_fails_when_the_library_is_older_than_the_resolver(tmp_path):
    cov = tmp_path / 'coverage.json'
    cov.write_text(json.dumps({'resolver_version': 'resolver-all110-.89'}))
    assert B.check_version(str(cov), _resolver(tmp_path, 'resolver-all110-.89', 'resolver-all110-.90'))
    shutil.rmtree(tmp_path / 'resolver')
    assert B.check_version(str(cov), _resolver(tmp_path, 'resolver-all110-.89', 'resolver-all110-.88')) == ''
    cov.write_text(json.dumps({'resolver_version': 'dev'}))
    assert B.check_version(str(cov), str(tmp_path / 'resolver'))   # a dev build never satisfies a numbered release
    assert B.version_number('resolver-all110-.100') == 100 and B.version_number('dev') is None


def test_committed_library_is_built_for_the_newest_resolver_version():
    """The CI gate (also `build_library.py --check-version`): every resolver release rebuilds the library."""
    assert B.check_version() == ''
