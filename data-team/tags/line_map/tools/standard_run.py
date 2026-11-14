"""One path from FSN to the resolver's inputs for any CIK list (read-only; no side files).

  python3 standard_run.py sql CIKS OUTDIR [--batch 4]
      writes OUTDIR/{lines,bs,notes,face}-NN.sql: the four standard queries per CIK batch
      (extract.sql: face lines + calc; extract_bs.sql: balance-sheet parenthetical cpv; extract_notefacts.sql; extract_facelines.sql).
  python3 standard_run.py assemble OUTDIR
      reads OUTDIR/{lines,bs,notes,face}.jsonl (one JSON object per result row, the query's column names) and writes
      filings.json, notefacts.json, memberfacts.json, compfacts.json, zlines.json, clines.json into OUTDIR.
Then: cd OUTDIR && python3 resolve_all.py VERSION OUT.csv (with tk.csv: ticker,cik10 per line)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import standard_inputs as si

TIMEOUT = "set statement_timeout='55s';"


def _ciks_sql(path, ciks):
    sql = open(path).read()
    sql = re.sub(r"set statement_timeout='\d+s';", TIMEOUT, sql)
    return sql.replace('__CIKS__', ','.join(str(int(c)) for c in ciks))


def write_sql(ciks, outdir, batch=4):
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for k in range(0, len(ciks), batch):
        b = ciks[k:k + batch]
        q = {'lines': _ciks_sql(os.path.join(HERE, 'extract.sql'), b), 'bs': _ciks_sql(os.path.join(HERE, 'extract_bs.sql'), b),
             'notes': si.build_sql(b), 'face': si.build_sql(b, sql_path=si.FACE_SQL_PATH)}
        for kind, sql in q.items():
            sql = sql[sql.index('set statement_timeout'):] if 'set statement_timeout' in sql else sql
            open(os.path.join(outdir, f'{kind}-{n:02d}.sql'), 'w').write(re.sub(r"set statement_timeout='\d+s';", TIMEOUT, sql))
        n += 1
    return n


def _rows(path):
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []


def assemble(outdir):
    J = lambda k: _rows(os.path.join(outdir, k + '.jsonl'))
    cpv = {r['a']: r.get('cpv') for r in J('bs')}
    filings = []
    for r in J('lines'):
        f = dict(cik=r['cik'].zfill(10), a=r['a'], p=r['p'], fd=r.get('fd'), lines=r.get('lines') or '', calc=r.get('calc') or '')
        if cpv.get(r['a']): f['cpv'] = cpv[r['a']]
        filings.append(f)
    main = [(r['a'], r.get('vals'), r.get('mvals'), r.get('cvals'), r.get('zlines')) for r in J('notes')]
    face = [(r['a'], r.get('vals'), r.get('cvals'), r.get('clines')) for r in J('face')]
    rows = si.merge_rows(main, face)
    nf, mf, cf = si.split_rows(rows)
    out = dict(filings=filings, notefacts=nf, memberfacts=mf, compfacts=cf, zlines=si.zero_lines(rows), clines=si.face_clines(face))
    for k, v in out.items(): json.dump(v, open(os.path.join(outdir, k + '.json'), 'w'))
    return {k: len(v) for k, v in out.items()}


if __name__ == '__main__':
    if sys.argv[1] == 'sql':
        ciks = [c for c in re.split(r'[,\s]+', sys.argv[2]) if c]
        b = int(sys.argv[sys.argv.index('--batch') + 1]) if '--batch' in sys.argv else 4
        print(write_sql(ciks, sys.argv[3], b), 'batches')
    elif sys.argv[1] == 'assemble':
        print(assemble(sys.argv[2]))
