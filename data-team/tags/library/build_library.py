"""Build the Scrooner tag library: one row per element, generated from code and data so it never drifts.

    python3 data-team/tags/library/build_library.py            (from the repo root; read-only, no network, no DB)

Inputs (all in the repo):
  data-team/tags/taxonomy/elements.csv, deprecations.csv, calc.csv   FASB US-GAAP 2014-2026 (optional until the ingest lands)
  data-team/tags/line_map/rules/roles.csv, polarity.csv, filer_xbrl_errors.csv, fsn_dropped_facts.csv, extract_families.txt
  data-team/tags/line_map/tools/resolve_cf.py, resolve_all.py, total_debt.py   element lists in code (imported, never copied)
  data-team/tags/line_map/resolver-all110-*.csv            the newest resolver output: usage, served cells, R pages
  data-team/tags/library/proof_by_tag.csv                  analytics.cell_proof aggregated by shown_tag (refresh: proof_by_tag.sql)
  data-team/strategy/certification/*-coverage-*.csv        certified cells (class PROVEN in a certification coverage file)
  data-team/tags/library/standard-tag-library.csv, company-overrides.csv, fsn-*.csv, needs-detail-answers-r1r2.csv  (folded in)
  data-team/tags/RULEBOOK.md, data-team/tags/cards/*.md, mind/entries/*.md, data-team/22-FILING-LESSONS-LEDGER.md
  data-team/47-fsn-store/company_tag_map/concepts_catalog.csv, pipeline/src/scrooner_pipeline/metrics/registry/*.csv
Outputs (data-team/tags/library/):
  library.csv, library.json, library.schema.json, INDEX.md, browser.html, CHANGELOG.md (appended per build), coverage.json
"""
import csv, glob, html, json, os, re, sys, collections, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
LIB = os.path.join(ROOT, 'data-team', 'tags', 'library')
LM = os.path.join(ROOT, 'data-team', 'tags', 'line_map')
TAX = os.path.join(ROOT, 'data-team', 'tags', 'taxonomy')
sys.path.insert(0, os.path.join(LM, 'tools'))
csv.field_size_limit(10 ** 8)

COLUMNS = [
    'element', 'taxonomy', 'standard_label', 'definition', 'balance', 'period_type', 'data_type', 'abstract', 'taxonomy_years',
    'deprecated_year', 'replaces', 'deprecated_by', 'deprecation_chain',
    'data_point', 'roles_rows', 'role_kind', 'rule_id', 'resolver_functions', 'tests', 'polarity', 'family', 'statements',
    'positions', 'calc_parents', 'filer_calc_parents', 'labels_seen', 'learned_filings', 'learned_companies', 'learned_statements', 'member_axes', 'custom',
    'metrics', 'concept_catalog', 'links',
    'companies', 'filings_seen', 'years_seen', 'served_cells', 'example_cells',
    'proof_cells', 'proven_cells', 'proof_companies', 'certified_cells', 'last_verified', 'composite_uses',
    'fsn_lines_top100', 'fsn_companies_top100', 'legacy_decision', 'legacy_concept', 'legacy_caveat', 'company_overrides',
    'known_problems', 'problem_commits', 'dqc_rules', 'cards', 'mind_ids', 'ledger_lines',
    'quality', 'full_row',
]


def rows_of(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', errors='ignore') as fh:
        return list(csv.DictReader(fh))


def j(xs, n=None):
    xs = [x for x in dict.fromkeys(x for x in xs if x)]
    return ';'.join(xs[:n] if n else xs)


def main():
    import resolve_all, resolve_cf, total_debt   # the resolver's own lists: imported, never copied
    lib = collections.defaultdict(lambda: collections.defaultdict(list))

    def add(el, k, v):
        if el and re.fullmatch(r'\w+', el) and v not in (None, ''):
            lib[el][k].append(str(v))

    # 1. taxonomy (FASB): meaning, balance, period type, deprecations, calc parents
    tax = {r['name']: r for r in rows_of(os.path.join(TAX, 'elements.csv'))}
    dep = rows_of(os.path.join(TAX, 'deprecations.csv'))
    succ, pred = collections.defaultdict(list), collections.defaultdict(list)
    for d in dep:
        for s in re.split(r'[;|, ]+', d.get('replacement_element') or d.get('replacement_element(s)') or ''):
            if s:
                succ[d['element']].append(f"{s}@{d.get('deprecated_in_year', '')}")
                pred[s].append(f"{d['element']}@{d.get('deprecated_in_year', '')}")
        if d.get('chain'):
            add(d['element'], 'deprecation_chain', d['chain'])
    for d in rows_of(os.path.join(TAX, 'dqc_rule_elements.csv')):   # XBRL US data-quality rules that name the element
        el = (d.get('element') or '').split(':')[-1]
        if d.get('element_prefix') == 'us-gaap' or (d.get('element') or '').startswith('us-gaap:'):
            add(el, 'dqc_rules', d['rule_id'] + (f" ({d['role_in_rule']})" if d.get('role_in_rule') else ''))
    calc_par = collections.defaultdict(set)
    for c in rows_of(os.path.join(TAX, 'calc.csv')):
        calc_par[c.get('child')].add(c.get('parent'))

    # 2. roles.csv and code lists: data points, role kind, families
    roles = rows_of(os.path.join(LM, 'rules', 'roles.csv'))
    dp_of = collections.defaultdict(set)
    for R in roles:
        for kind, field in (('primary', 'alternatives'), ('combined', 'combined_if')):
            for i, alt in enumerate((R.get(field) or '').split('|')):
                for t in alt.split('+'):
                    if t:
                        dp_of[t].add(R['data_point'])
                        add(t, 'roles_rows', f"roles.csv:{R['data_point']}")
                        add(t, 'role_kind', f"{R['data_point']}:{kind}{'' if len(alt.split('+')) == 1 else '-part'}#{i + 1}")
                        add(t, 'statements', R.get('stmt'))
    code_lists = {'capex': ('resolve_cf.CAPEX', resolve_cf.CAPEX)}
    for dp, spec in resolve_cf.WC.items():
        code_lists[dp] = (f'resolve_cf.WC[{dp}]', spec['fam'] + spec['comb'])
    for dp, ts in resolve_all.NARROW.items():
        code_lists.setdefault(dp + ':narrow', (f'resolve_all.NARROW[{dp}]', ts))
    for key, (where, ts) in code_lists.items():
        for t in ts:
            dp = key.split(':')[0]
            dp_of[t].add(dp)
            add(t, 'family', where)
    for dp in [R['data_point'] for R in roles]:
        for t in resolve_all.dp_elements(dp):
            dp_of[t].add(dp)
    pol = {r.get('data_point'): r for r in rows_of(os.path.join(LM, 'rules', 'polarity.csv'))}
    for t, dps in dp_of.items():
        for dp in sorted(dps):
            add(t, 'data_point', dp)
            if dp in pol:
                add(t, 'polarity', f"{dp}:{pol[dp].get('sign') or pol[dp].get('polarity') or list(pol[dp].values())[1]}")

    # 3. resolver output: usage and served cells
    outs = sorted(glob.glob(os.path.join(LM, 'resolver-all110-*.csv')))
    served_total = served_with_el = 0
    served_els = []
    node_rx = re.compile(r'(?:^|; )-?(\w+)(?:\[[^\]]*\])?=-?[\d.]+ \[(R\d+\.htm:\d+|NOTE|SE|BSP)[^\]]*\]')
    use = collections.defaultdict(lambda: dict(c=set(), f=set(), y=set(), n=0, ex=[], pos=collections.Counter()))
    version = ''
    for r in (rows_of(outs[-1]) if outs else []):
        version = r.get('resolver_version') or version
        nodes = (r.get('nodes') or '').split(' | why')[0]
        els = node_rx.findall(nodes)
        served = r.get('decision') in ('mapped', 'component_sum', 'derived', 'derived_not_printed')
        if served:
            served_total += 1
            served_els.append([e for e, _ in els])
        for e, loc in els:
            u = use[e]
            u['c'].add(r['ticker']); u['f'].add(r['accession']); u['y'].add(r['period_end'][:4])
            u['pos']['note' if loc == 'NOTE' else 'bs_parenthetical' if loc == 'BSP' else 'equity_statement' if loc == 'SE' else 'face'] += 1
            if served:
                u['n'] += 1
                if len(u['ex']) < 3:
                    u['ex'].append(f"{r['ticker']} {r['period_end'][:4]} {r['data_point']} {r['accession']} {loc}")
            add(e, 'data_point', r['data_point'])
    for e, u in use.items():
        lib[e]['companies'] = [str(len(u['c']))]; lib[e]['filings_seen'] = [str(len(u['f']))]
        lib[e]['years_seen'] = [f"{min(u['y'])}-{max(u['y'])}" if u['y'] else '']
        lib[e]['served_cells'] = [str(u['n'])]; lib[e]['example_cells'] = u['ex']
        lib[e]['positions'] = [f'{k}:{v}' for k, v in u['pos'].most_common()]

    # 4. proof (analytics.cell_proof by shown_tag) and certification files
    for p in rows_of(os.path.join(LIB, 'proof_by_tag.csv')):
        parts = [x.split(':')[-1] for x in p['element'].split(',')]
        for e in parts:
            if len(parts) == 1:
                lib[e]['proof_cells'] = [p['proof_cells']]; lib[e]['proven_cells'] = [p['proven_cells']]
                lib[e]['proof_companies'] = [p['proof_companies']]; lib[e]['last_verified'] = [p['last_proved']]
            else:
                add(e, 'composite_uses', f"{p['element']} ({p['proven_cells']} proven)")
    cert = collections.Counter()
    latest = {}
    for path in glob.glob(os.path.join(ROOT, 'data-team', 'strategy', 'certification', '*-coverage-*.csv')):
        tk = os.path.basename(path).split('-coverage-')[0]
        latest[tk] = max(latest.get(tk, ''), path)
    for path in latest.values():
        for r in rows_of(path):
            if r.get('class') == 'PROVEN' and r.get('tag'):
                for e in r['tag'].split('+'):
                    cert[e.strip('-')] += 1
    for e, n in cert.items():
        lib[e]['certified_cells'] = [str(n)]

    # 5. folded-in legacy library (FSN-read statement library, overrides, needs-detail answers)
    for r in rows_of(os.path.join(LIB, 'standard-tag-library.csv')):
        e = r.get('tag')
        add(e, 'statements', r.get('stmt')); add(e, 'legacy_decision', r.get('decision')); add(e, 'legacy_concept', r.get('concept'))
        add(e, 'legacy_caveat', (r.get('caveat') or '')[:300])
        lib[e]['fsn_lines_top100'] = [r.get('lines_top100') or '']; lib[e]['fsn_companies_top100'] = [r.get('companies_top100') or '']
    for r in rows_of(os.path.join(LIB, 'needs-detail-answers-r1r2.csv')):
        add(r.get('tag'), 'legacy_decision', r.get('decision')); add(r.get('tag'), 'legacy_concept', r.get('canonical_concept_key'))
        add(r.get('tag'), 'legacy_caveat', (r.get('exceptions') or '')[:300])
    for path in glob.glob(os.path.join(LIB, 'fsn-*.csv')):
        for r in rows_of(path):
            e = r.get('tag') or r.get('element')
            add(e, 'statements', os.path.basename(path)[4:-4])
    for r in rows_of(os.path.join(LIB, 'company-overrides.csv')):
        add(r.get('tag'), 'company_overrides', f"{r.get('company')}:{r.get('concept')}:{r.get('status')}")

    # 6. known problems with their fixes
    for r in rows_of(os.path.join(LM, 'rules', 'filer_xbrl_errors.csv')):
        e = r.get('tag') or r.get('element')
        add(e, 'known_problems', f"filer XBRL error {r.get('accession', '')}: {(r.get('evidence') or r.get('note') or '')[:160]}")
    for r in rows_of(os.path.join(LM, 'rules', 'fsn_dropped_facts.csv')):
        e = r.get('tag') or (list(r.values())[1] if len(r) > 1 else '')
        add(e, 'known_problems', f"FSN dropped fact {list(r.values())[0]} (fsn_dropped_facts.csv)")

    # 7. rulebook, tests, functions, cards, mind, ledger: element named in the text
    known = set(lib) | set(tax) | set(dp_of)
    word = re.compile(r'\b([A-Z][A-Za-z0-9]{6,})\b')
    rb = open(os.path.join(ROOT, 'data-team', 'tags', 'RULEBOOK.md')).read() if os.path.exists(os.path.join(ROOT, 'data-team', 'tags', 'RULEBOOK.md')) else ''
    rule_dp = collections.defaultdict(set)
    for line in rb.splitlines():
        m = re.match(r'^\| ([XCFIBKD]\d+) \|', line)
        if not m:
            continue
        rid = m.group(1)
        cells = [c.strip() for c in line.strip('|').split('|')]
        for t in set(word.findall(line)) & known:
            add(t, 'rule_id', rid)
            for fn in re.findall(r'\b(?:ra|rc|rcf|ris|rbs|td|si)\.(\w+)', line):
                add(t, 'resolver_functions', fn)
            for tst in re.findall(r'::(test_\w+)', line):
                add(t, 'tests', tst)
            for c in re.findall(r'commit (\.\d+|[0-9a-f]{8})', line):
                add(t, 'problem_commits', f"{rid}:{c}")
        if len(cells) > 2 and re.fullmatch(r'[a-z_/]+', cells[1] or ''):
            for dp in cells[1].split('/'):
                rule_dp[dp].add(rid)
    for t, dps in dp_of.items():   # a ruling indexed by data point applies to every element of that data point
        for dp in dps:
            for rid in sorted(rule_dp.get(dp, ())):
                add(t, 'rule_id', rid)
    for path in sorted(glob.glob(os.path.join(ROOT, 'data-team', 'tags', 'cards', '**', '*.md'), recursive=True)):
        rel = os.path.relpath(path, ROOT)
        for t in set(word.findall(open(path, errors='ignore').read())) & known:
            add(t, 'cards', rel)
    for path in sorted(glob.glob(os.path.join(ROOT, 'mind', 'entries', '*.md'))):
        txt = open(path, errors='ignore').read()
        mid = re.search(r'^id: (.+)$', txt, re.M)
        for t in set(word.findall(txt)) & known:
            add(t, 'mind_ids', mid.group(1).strip() if mid else os.path.basename(path)[:-3])
    ledger = os.path.join(ROOT, 'data-team', '22-FILING-LESSONS-LEDGER.md')
    if os.path.exists(ledger):
        for i, line in enumerate(open(ledger, errors='ignore'), 1):
            for t in set(word.findall(line)) & known:
                add(t, 'ledger_lines', f"L{i}")

    # 8. metrics and concepts catalog: data point -> metric ids
    cat = {r['name'] for r in rows_of(os.path.join(ROOT, 'data-team', '47-fsn-store', 'company_tag_map', 'concepts_catalog.csv'))}
    met = collections.defaultdict(set)
    for path in glob.glob(os.path.join(ROOT, 'pipeline', 'src', 'scrooner_pipeline', 'metrics', 'registry', '*.csv')):
        for r in rows_of(path):
            for dp in re.findall(r'[a-z][a-z_]+', (r.get('seed_inputs') or '') + ' ' + (r.get('expression') or '')):
                met[dp].add(r['metric_id'])
    for t in list(lib):
        dps = set(lib[t].get('data_point', []))
        for dp in dps:
            for m in sorted(met.get(dp, ())):
                add(t, 'metrics', m)
            if dp in cat:
                add(t, 'concept_catalog', dp)

    # 8b. learned from the filings themselves (learn_from_filings.py over the standard extract): every element filers use
    learned = {r['element']: r for r in rows_of(os.path.join(LIB, 'learned_elements.csv'))}
    for e, r in learned.items():
        lib[e]['labels_seen'] = [r['labels']]; lib[e]['filer_calc_parents'] = [r['calc_parents']]; lib[e]['learned_filings'] = [r['filings']]
        lib[e]['learned_companies'] = [r['companies']]; lib[e]['learned_statements'] = [r['statements']]; lib[e]['member_axes'] = [r['member_axes']]
        lib[e]['custom'] = [r['custom']]
    # 9. assemble rows: every element with any knowledge, plus the full taxonomy
    out = []
    for e in sorted(set(lib) | set(tax)):
        L = lib.get(e, {})
        T = tax.get(e, {})
        row = {k: '' for k in COLUMNS}
        row.update(element=e, taxonomy='us-gaap' if T else ('custom' if (L.get('custom') or [''])[0] == '1' else 'us-gaap?' if L.get('custom') else 'unknown'),
                   standard_label=T.get('standard_label', ''), definition=(T.get('documentation') or '')[:400], balance=T.get('balance', ''),
                   period_type=T.get('period_type', ''), data_type=T.get('type', ''), abstract=T.get('abstract', ''),
                   taxonomy_years=f"{T.get('first_year', '')}-{T.get('last_year', '')}" if T else '', deprecated_year=T.get('deprecated_year', ''),
                   replaces=j(pred.get(e, [])), deprecated_by=j(succ.get(e, []) or ([T['replacement']] if T.get('replacement') else [])),
                   calc_parents=j(sorted(calc_par.get(e, ())), 12))
        for k, v in L.items():
            if k in row and v:
                row[k] = j(v, 3 if k == 'example_cells' else 8 if k == 'composite_uses' else 20)
        row['links'] = j([f'card:{c}' for c in row['cards'].split(';') if c] + [f'mind:{m}' for m in row['mind_ids'].split(';') if m] + [f'ledger:{l}' for l in row['ledger_lines'].split(';') if l][:10] + [f'test:{t}' for t in row['tests'].split(';') if t] + [f'fn:{x}' for x in row['resolver_functions'].split(';') if x])
        prob_n = len([x for x in (row['known_problems'] or '').split(';') if x])
        row['quality'] = f"companies={row['companies'] or 0};proven={row['proven_cells'] or 0};certified={row['certified_cells'] or 0};open_problems={prob_n};verified={row['last_verified'] or '-'}"
        need = ['data_point', 'rule_id', 'served_cells']
        row['full_row'] = 'yes' if all(row[k] for k in need) and (row['definition'] or not tax) and (row['proven_cells'] or row['certified_cells']) else 'no'
        out.append(row)
    known_rows = {r['element']: r for r in out}

    # coverage: share of served cells whose every element has a full row
    full = sum(1 for els in served_els if els and all(known_rows.get(e, {}).get('full_row') == 'yes' for e in els))
    cov = dict(built=datetime.date.today().isoformat(), resolver_version=version, rows=len(out),
               rows_with_usage=sum(1 for r in out if r['served_cells']), rows_full=sum(1 for r in out if r['full_row'] == 'yes'),
               taxonomy_elements=len(tax), served_cells=served_total, served_cells_all_elements_full=full,
               coverage_pct=round(100 * full / served_total, 1) if served_total else 0)

    # changelog: per-element diff against the previous library.csv
    prev = {r['element']: r for r in rows_of(os.path.join(LIB, 'library.csv'))}
    changes = []
    for e, r in known_rows.items():
        p = prev.get(e)
        if not p:
            if r['served_cells'] or r['rule_id']:
                changes.append(f"+ {e}")
            continue
        diff = [k for k in ('data_point', 'rule_id', 'served_cells', 'proven_cells', 'certified_cells', 'known_problems', 'deprecated_by') if (p.get(k) or '') != (r.get(k) or '')]
        if diff:
            changes.append(f"~ {e}: {', '.join(diff)}")

    with open(os.path.join(LIB, 'library.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS); w.writeheader(); w.writerows(out)
    used = [r for r in out if r['served_cells'] or r['rule_id'] or r['data_point'] or r['proven_cells']]
    json.dump(used, open(os.path.join(LIB, 'library.json'), 'w'), separators=(',', ':'))
    json.dump(cov, open(os.path.join(LIB, 'coverage.json'), 'w'), indent=1)
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'Scrooner tag library row', 'type': 'object',
              'required': ['element'], 'properties': {k: {'type': 'string'} for k in COLUMNS},
              'description': 'One row per element. Lists are ;-separated. Generated by build_library.py; never edit by hand.'}
    json.dump(schema, open(os.path.join(LIB, 'library.schema.json'), 'w'), indent=1)
    with open(os.path.join(LIB, 'CHANGELOG.md'), 'a') as fh:
        fh.write(f"\n## {cov['built']} ({version}): {len(changes)} element changes, {cov['rows']} rows, coverage {cov['coverage_pct']}%\n")
        for c in changes[:400]:
            fh.write(f"- {c}\n")
        if len(changes) > 400:
            fh.write(f"- ... {len(changes) - 400} more\n")
    write_index(used, cov)
    write_browser(used, cov)
    print(json.dumps(cov))


def write_index(rows, cov):
    by = lambda key: collections.defaultdict(list)
    dp, st, fam, prob = by(0), by(0), by(0), by(0)
    for r in rows:
        for d in filter(None, r['data_point'].split(';')):
            dp[d].append(r['element'])
        for s in filter(None, r['statements'].split(';')):
            st[s].append(r['element'])
        for f in filter(None, r['family'].split(';')):
            fam[f].append(r['element'])
        for p in filter(None, r['known_problems'].split(';')):
            prob[p.split(' ')[0] + ' ' + p.split(' ')[1] if ' ' in p else p].append(r['element'])
    L = [f"# Tag library index (generated {cov['built']}, {cov['resolver_version']})", '',
         f"{cov['rows']} rows ({cov['rows_with_usage']} with resolver usage, {cov['taxonomy_elements']} taxonomy elements); "
         f"coverage {cov['coverage_pct']}% of {cov['served_cells']} resolver-served cells have a full row for every element they use.", '',
         'Search and follow links in [browser.html](browser.html). Columns: [library.schema.json](library.schema.json).', '']
    for title, d in (('By data point', dp), ('By statement', st), ('By family (code lists)', fam), ('By problem type', prob)):
        L += [f'## {title}', '']
        for k in sorted(d):
            els = sorted(set(d[k]))
            L.append(f"- **{k}** ({len(els)}): " + ', '.join(f'`{e}`' for e in els[:40]) + (' ...' if len(els) > 40 else ''))
        L.append('')
    open(os.path.join(LIB, 'INDEX.md'), 'w').write('\n'.join(L))


def write_browser(rows, cov):
    data = json.dumps(rows, separators=(',', ':')).replace('</', '<\\/')
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scrooner Tag Library</title><style>
:root{--bg:#fff;--fg:#1d1d1f;--mut:#6b6b70;--line:#e3e3e6;--acc:#0b57d0}
@media (prefers-color-scheme: dark){:root{--bg:#141416;--fg:#ececee;--mut:#9b9ba1;--line:#2c2c30;--acc:#8ab4f8}}
body{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0;padding:16px;max-width:1100px;margin:auto}
input{width:100%;box-sizing:border-box;padding:10px;font-size:15px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
.el{border-bottom:1px solid var(--line);padding:10px 0}.el h3{margin:0 0 4px;font-size:15px;word-break:break-all}
.k{color:var(--mut);display:inline-block;min-width:150px;vertical-align:top}.v{display:inline-block;max-width:calc(100% - 160px);word-break:break-word}
a{color:var(--acc);cursor:pointer;text-decoration:none}.q{font-size:12px;color:var(--mut);overflow-wrap:anywhere}
.v,.el h3{overflow-wrap:anywhere}@media (max-width:600px){.k{display:block;min-width:0}.v{display:block;max-width:100%}}
</style></head><body><h1>Scrooner tag library</h1><p class="q">__META__</p>
<input id="q" placeholder="Search an element, data point, ruling ID, ticker or problem" autofocus><div id="n" class="q"></div><div id="out"></div>
<script>
const D=__DATA__;const LINK=new Set(['data_point','rule_id','replaces','deprecated_by','calc_parents','metrics','family']);
const out=document.getElementById('out'),q=document.getElementById('q'),n=document.getElementById('n');
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function val(k,v){if(!v)return'';return v.split(';').map(x=>LINK.has(k)?'<a data-q="'+esc(x.split('@')[0].split(':')[0])+'">'+esc(x)+'</a>':esc(x)).join('; ')}
function show(){const t=q.value.trim().toLowerCase();let r=t?D.filter(o=>Object.values(o).some(v=>String(v).toLowerCase().includes(t))):D.slice(0,50);
r.sort((a,b)=>(b.element.toLowerCase()===t)-(a.element.toLowerCase()===t)||(+b.served_cells||0)-(+a.served_cells||0));n.textContent=r.length+' rows';
out.innerHTML=r.slice(0,100).map(o=>'<div class="el"><h3>'+esc(o.element)+'</h3><div class="q">'+esc(o.quality)+'</div>'+Object.entries(o).filter(([k,v])=>v&&k!=='element'&&k!=='quality').map(([k,v])=>'<div><span class="k">'+k+'</span><span class="v">'+val(k,v)+'</span></div>').join('')+'</div>').join('')}
out.addEventListener('click',e=>{const a=e.target.closest('a[data-q]');if(a){q.value=a.dataset.q;show();window.scrollTo(0,0)}});q.addEventListener('input',show);show();
</script></body></html>"""
    meta = html.escape(f"Generated {cov['built']} from {cov['resolver_version']}: {len(rows)} elements with knowledge; coverage {cov['coverage_pct']}% of served cells.")
    open(os.path.join(LIB, 'browser.html'), 'w').write(page.replace('__META__', meta).replace('__DATA__', data))


if __name__ == '__main__':
    main()
