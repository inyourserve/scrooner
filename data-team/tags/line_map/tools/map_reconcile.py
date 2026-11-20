"""The company tag map must derive from the resolver, never the other way round (Dhairya 2026-11-16: 46 library 'combined' rows,
e.g. AMGN InterestExpenseDebt, vetoed cells the resolver maps).

    python3 map_reconcile.py check [MAP_CSV] [RESOLVER_CSV]     exit 1 and list the conflicts
    python3 map_reconcile.py apply [MAP_CSV] [RESOLVER_CSV]     rewrite the convertible rows in place, print the review list

A CONFLICT: a map row with decision 'combined' for (company, element) whose era holds a resolver own-column cell of one of the row's
components (or its canonical concept) that the resolver serves (mapped / component_sum / derived_not_printed) with that element
among its nodes.

APPLY converts a conflicting row to decision 'concept' only when the resolver is unanimous over the row's era: every resolver own-column
cell of the company in [era_from, era_to] whose nodes name the element is 'mapped' with that element as its ONLY node, all for ONE data
point. The row keeps its era and evidence; canonical_concept = that data point; decided_by = 'resolver'; rule_id = 'resolver_beats_library';
reason cites the resolver version. Anything else (the element is a component of a sum, the resolver splits the era between 'combined'
and 'mapped', or maps the element to two data points) is NOT changed and is listed for review.
"""
import collections, csv, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
MAP = os.path.join(ROOT, 'data-team', '47-fsn-store', 'company_tag_map', 'ranks_1_50.csv')
SERVED = ('mapped', 'component_sum', 'derived_not_printed')
NODE = re.compile(r'(?:^|; )-?(\w+)(?:\[[^\]]*\])?=')
csv.field_size_limit(10 ** 8)


def newest_resolver():
    split = sorted(glob.glob(os.path.join(ROOT, 'data-team', 'tags', 'line_map', 'resolver', '*.csv')))
    return split or sorted(glob.glob(os.path.join(ROOT, 'data-team', 'tags', 'line_map', 'resolver-all110-*.csv')))[-1:]


def resolver_cells(path):
    """{cik10: [(data_point, period_end, decision, [node elements], version)]}, own-column cells only."""
    out = collections.defaultdict(list)
    paths = [path] if isinstance(path, str) else list(path)  # one file, or the per-company files
    for r in (row for p in paths for row in csv.DictReader(open(p))):
        if (r.get('column') or 'own') != 'own':
            continue
        nodes = NODE.findall((r.get('nodes') or '').split(' | why')[0])
        out[r['cik'].zfill(10)].append((r['data_point'], r['period_end'], r['decision'], nodes, r.get('resolver_version', '')))
    return out


def _dps(row):
    return {x for x in (row.get('components') or '').split(';') if x} | ({row['canonical_concept']} if row.get('canonical_concept') else set())


def conflicts(map_rows, cells):
    """[(row index, [(dp, period_end, decision)])] for combined rows the resolver contradicts."""
    out = []
    for i, x in enumerate(map_rows):
        if x['decision'] != 'combined':
            continue
        lo, hi, dps = x['era_from'] or '0000', x['era_to'] or '9999', _dps(x)
        hit = [(dp, pe, dec) for dp, pe, dec, nodes, _ in cells.get(x['cik'].zfill(10), [])
               if dec in SERVED and x['tag'] in nodes and dp in dps and lo <= pe <= hi]
        if hit:
            out.append((i, hit))
    return out


def convertible(row, cells):
    """(data_point, version) when the resolver serves the element alone for one data point in every era cell naming it, else None."""
    lo, hi = row['era_from'] or '0000', row['era_to'] or '9999'
    seen = [(dp, dec, nodes, v) for dp, pe, dec, nodes, v in cells.get(row['cik'].zfill(10), []) if lo <= pe <= hi and row['tag'] in nodes]
    if not seen or any(dec != 'mapped' or nodes != [row['tag']] for dp, dec, nodes, v in seen):
        return None
    dps = {dp for dp, _, _, _ in seen}
    return (dps.pop(), seen[0][3]) if len(dps) == 1 else None


def main(mode, map_csv=MAP, resolver_csv=None):
    resolver_csv = resolver_csv or newest_resolver()
    rows = list(csv.DictReader(open(map_csv)))
    fields = list(rows[0].keys())
    cells = resolver_cells(resolver_csv)
    found = conflicts(rows, cells)
    if mode == 'check':
        for i, hit in found:
            x = rows[i]
            print(f"CONFLICT {x['ticker']} {x['tag']} {x['era_from']}..{x['era_to']}: combined, the resolver serves "
                  f"{sorted({dp for dp, _, _ in hit})} in {len(hit)} cell(s)")
        print(f'{len(found)} conflicting combined row(s)')
        return 1 if found else 0
    review, retire = [], set()
    for i, hit in found:
        x = rows[i]
        c = convertible(x, cells)
        if not c:
            review.append(x); continue
        dp, version = c
        # an existing concept row of the same company, statement and concept over an overlapping era: the SAME element covering this
        # era makes the combined row redundant (retire it); a different element would give two concept rows (review)
        lo, hi = x['era_from'] or '0000', x['era_to'] or '9999'
        other = [y for j, y in enumerate(rows) if j != i and y['decision'] == 'concept' and y['cik'] == x['cik'] and y['stmt'] == x['stmt']
                 and y['canonical_concept'] == dp and (y['era_from'] or '0000') <= hi and lo <= (y['era_to'] or '9999')]
        if other:
            if all(y['tag'] == x['tag'] and (y['era_from'] or '0000') <= lo and hi <= (y['era_to'] or '9999') for y in other):
                retire.add(i)
            else:
                review.append(x)
            continue
        x.update(decision='concept', canonical_concept=dp, components='', parent_concept='', combine_sign='', decided_by='resolver',
                 rule_id='resolver_beats_library', reason_class='resolver_mapped',
                 reason=f"{version}: the resolver serves {dp} from {x['tag']} alone in every cell of the era (was combined: {x['reason']})")
    with open(map_csv, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(r for j, r in enumerate(rows) if j not in retire)
    print(f'converted {len(found) - len(review) - len(retire)} row(s); retired {len(retire)} redundant row(s); {len(review)} left for review:')
    for x in review:
        print(f"  REVIEW {x['ticker']} {x['tag']} {x['era_from']}..{x['era_to']} ({x['reason'][:90]})")
    return 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
