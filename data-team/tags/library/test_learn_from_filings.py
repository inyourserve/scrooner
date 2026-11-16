"""learn_from_filings reads a standard extract and records what filers do: labels, statements, calc parents, served labels."""
import csv, json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))


def test_learner_records_labels_parents_and_served_labels(tmp_path):
    f = dict(cik='0000000001', a='A1', p='2022-12-31', lines='BS|2|1|PrepaidExpenseCurrent|0|0|terseLabel|Inventories|3123~BS|2|2|Assets|0|0|totalLabel|Total assets|9000',
             calc='1|Assets|PrepaidExpenseCurrent|1')
    json.dump([f], open(tmp_path / 'filings.json', 'w'))
    res = tmp_path / 'r.csv'
    with open(res, 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['ticker', 'data_point', 'decision', 'nodes', 'accession'])
        w.writerow(['T', 'inventory', 'mapped', 'PrepaidExpenseCurrent=3123 [R2.htm:1]', 'A1'])
    lib_dir = tempfile.mkdtemp()
    env = dict(os.environ)
    code = open(os.path.join(HERE, 'learn_from_filings.py')).read().replace("HERE = os.path.dirname(os.path.abspath(__file__))", f"HERE = {lib_dir!r}")
    script = os.path.join(lib_dir, 'l.py'); open(script, 'w').write(code)
    subprocess.run([sys.executable, script, str(tmp_path), str(res)], check=True, env=env, capture_output=True)
    el = {r['element']: r for r in csv.DictReader(open(os.path.join(lib_dir, 'learned_elements.csv')))}
    assert 'Inventories (1)' in el['PrepaidExpenseCurrent']['labels'] and 'Assets(+) 1' in el['PrepaidExpenseCurrent']['calc_parents']
    lab = list(csv.DictReader(open(os.path.join(lib_dir, 'learned_labels.csv'))))
    assert lab[0]['data_point'] == 'inventory' and lab[0]['label'] == 'inventories'
