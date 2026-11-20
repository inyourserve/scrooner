"""Learn element behaviour from the filings themselves (the standard extract the resolver reads), so the library is built from what filers
actually do, not from hand lists.

    python3 data-team/tags/library/learn_from_filings.py EXTRACT_DIR [RESOLVER_CSV]

EXTRACT_DIR holds filings.json, notefacts.json, memberfacts.json (standard_run.py assemble). RESOLVER_CSV defaults to the newest
data-team/tags/line_map/resolver-all110-*.csv. Writes, in data-team/tags/library/:

  learned_elements.csv  element, filings, companies, years, statements (stmt:count), face_valued (lines with an own-period value),
                        labels (top 5 own labels with counts), calc_parents (top 5 parents in the filers' own calc trees, with weight),
                        note_filings (filings holding an undimensioned note fact), member_axes (top axes seen on its member facts),
                        custom (1 when every filing that uses it marks it as an extension element)
  learned_labels.csv    data_point, label (normalised), cells, companies, elements: the face labels of the lines the resolver SERVED
                        for each data point. These are candidates for label rules (FACE_LABEL), reviewed before use, never applied blindly.

Read-only; no DB, no network. Run it after every extract; build_library.py folds both files into library.csv.
"""
import collections, csv, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
csv.field_size_limit(10 ** 8)


def norm(lb):
    lb = re.sub(r'\(.*?\)', '', lb or '').lower()
    lb = re.sub(r'[^a-z ,&]', ' ', lb)
    return re.sub(r'\s+', ' ', lb).strip(' ,')


def main(extract_dir, resolver_csv=None):
    filings = json.load(open(os.path.join(extract_dir, 'filings.json')))
    notes = json.load(open(os.path.join(extract_dir, 'notefacts.json'))) if os.path.exists(os.path.join(extract_dir, 'notefacts.json')) else {}
    members = json.load(open(os.path.join(extract_dir, 'memberfacts.json'))) if os.path.exists(os.path.join(extract_dir, 'memberfacts.json')) else {}
    E = collections.defaultdict(lambda: dict(f=set(), c=set(), y=set(), st=collections.Counter(), val=0, lb=collections.Counter(),
                                             par=collections.Counter(), nf=set(), ax=collections.Counter(), cust=set()))
    label_at = {}
    for f in filings:
        a, cik, yr = f['a'], f['cik'], f['p'][:4]
        for x in (f.get('lines') or '').split('~'):
            p = x.split('|')
            if len(p) < 9 or p[0] not in ('BS', 'IS', 'CF'):
                continue
            e = E[p[3]]
            e['f'].add(a); e['c'].add(cik); e['y'].add(yr); e['st'][p[0]] += 1; e['cust'].add(p[4])
            if p[8]:
                e['val'] += 1
            if p[7]:
                e['lb'][p[7].strip()] += 1
            label_at[(a, p[1], p[2])] = p[7]
        for arc in (f.get('calc') or '').split('~'):
            q = arc.split('|')
            if len(q) == 4:
                E[q[2]]['par'][f"{q[1]}({'+' if q[3].startswith('1') else '-'})"] += 1
        for x in (notes.get(a) or '').split('~'):
            t = x.split('|')[0]
            if t:
                E[t]['nf'].add(a); E[t]['c'].add(cik); E[t]['y'].add(yr)
        for x in (members.get(a) or '').split('~'):
            q = x.split('|')
            if len(q) == 4:
                for ax in re.findall(r'(\w+)=', q[3]):
                    E[q[0]]['ax'][ax] += 1
    out = []
    for t, e in sorted(E.items()):
        out.append(dict(element=t, filings=len(e['f']), companies=len(e['c']), years=f"{min(e['y'])}-{max(e['y'])}" if e['y'] else '',
                        statements=';'.join(f'{k}:{v}' for k, v in e['st'].most_common()), face_valued=e['val'],
                        labels=';'.join(f'{k} ({v})' for k, v in e['lb'].most_common(5)),
                        calc_parents=';'.join(f'{k} {v}' for k, v in e['par'].most_common(5)), note_filings=len(e['nf']),
                        member_axes=';'.join(f'{k} {v}' for k, v in e['ax'].most_common(3)), custom=1 if e['cust'] == {'1'} else 0))
    with open(os.path.join(HERE, 'learned_elements.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)

    # labels of the lines the resolver served, per data point
    if not resolver_csv:
        split = sorted(glob.glob(os.path.join(ROOT, 'data-team', 'tags', 'line_map', 'resolver', '*.csv')))
        resolver_csv = split or sorted(glob.glob(os.path.join(ROOT, 'data-team', 'tags', 'line_map', 'resolver-all110-*.csv')))[-1]
    rx = re.compile(r'(?:^|; )-?(\w+)(?:\[[^\]]*\])?=-?[\d.]+ \[R(\d+)\.htm:(\d+)(?:@([\d-]+))?\]')
    L = collections.defaultdict(lambda: dict(n=0, c=set(), e=collections.Counter()))
    _paths = [resolver_csv] if isinstance(resolver_csv, str) else list(resolver_csv)
    for r in (row for _p in _paths for row in csv.DictReader(open(_p))):
        if r['decision'] not in ('mapped', 'component_sum'):
            continue
        for t, rep, ln, acc in rx.findall((r.get('nodes') or '').split(' | why')[0]):
            lb = label_at.get((acc or r['accession'], rep, ln))
            if lb:
                k = (r['data_point'], norm(lb))
                L[k]['n'] += 1; L[k]['c'].add(r['ticker']); L[k]['e'][t] += 1
    rows = [dict(data_point=dp, label=lb, cells=v['n'], companies=len(v['c']), elements=';'.join(f'{k} {n}' for k, n in v['e'].most_common(4)))
            for (dp, lb), v in sorted(L.items(), key=lambda kv: (kv[0][0], -kv[1]['n']))]
    with open(os.path.join(HERE, 'learned_labels.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['data_point', 'label', 'cells', 'companies', 'elements']); w.writeheader(); w.writerows(rows)
    print(json.dumps(dict(filings=len(filings), elements=len(out), standard=sum(1 for o in out if not o['custom']),
                          custom=sum(1 for o in out if o['custom']), labels=len(rows), data_points=len({r['data_point'] for r in rows}))))


if __name__ == '__main__':
    main(*sys.argv[1:3])
