#!/usr/bin/env python3
"""Runner for the resolver's standard extract (pipeline-standard-extract.yml). Read-only, no SEC access.

  run_extract_sql.py run SQLDIR [--only le]   execute SQLDIR/<kind>-NN.sql in name order on ONE connection, append one
                                              JSON object per result row (column names as keys) to SQLDIR/<kind>.jsonl
  run_extract_sql.py ciks --ciks A,B | --csv PATH
                                              print the comma list of CIKs; a csv needs a cik or company_id column
                                              (company_id is resolved to the CIK of the company's latest annual report)
  run_extract_sql.py manifest OUTDIR --out FILE --run-id ID --code-sha SHA --ciks LIST
                                              row counts and SHA-256 of every file in OUTDIR

Decimal-safe: Decimal and date values are written as strings; a float value is refused (money is never a float).
The session must report transaction_read_only = on before any query runs (PGOPTIONS from the workflow)."""
import argparse
import csv
import datetime as dt
import glob
import hashlib
import json
import os
import re
from decimal import Decimal

LEAD_SET = re.compile(r"\A\s*(?:--[^\n]*\n\s*)*(set\s+statement_timeout\s*=\s*'\d+s'\s*;)", re.I)
MAX_TIMEOUT_S = 900


def _default(o):
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, (dt.date, dt.datetime, dt.time)):
        return o.isoformat()
    raise TypeError(f'cannot serialise {type(o).__name__}')


def _reject_float(o):
    if isinstance(o, float):
        raise TypeError('float value in an extract row (money must be text or Decimal)')
    if isinstance(o, dict):
        for v in o.values():
            _reject_float(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            _reject_float(v)


def split_sql(sql):
    """-> (leading `set statement_timeout` statement or '', the query without the trailing semicolon)."""
    m = LEAD_SET.match(sql)
    pre, rest = (m.group(1), sql[m.end():]) if m else ('', sql)
    if m:
        secs = int(re.search(r"'(\d+)s'", pre).group(1))
        if secs > MAX_TIMEOUT_S:
            raise SystemExit(f'statement_timeout {secs}s exceeds {MAX_TIMEOUT_S}s')
    return pre, rest.strip().rstrip(';').strip()


def assert_read_only(conn):
    with conn.cursor() as cur:
        cur.execute('show transaction_read_only')
        if cur.fetchone()[0] != 'on':
            raise SystemExit('refusing: session is not read-only')


def run_file(conn, path, out_path, append):
    pre, query = split_sql(open(path).read())
    n = 0
    with conn.cursor() as cur, open(out_path, 'a' if append else 'w') as out:
        if pre:
            cur.execute(pre)
        cur.execute(query)
        cols = [d[0] if isinstance(d, tuple) else d.name for d in cur.description]
        for row in cur:
            rec = dict(zip(cols, row))
            _reject_float(rec)
            out.write(json.dumps(rec, default=_default, separators=(',', ':')) + '\n')
            n += 1
    conn.rollback()
    return n


def run_dir(conn, sqldir, only=None):
    assert_read_only(conn)
    seen, counts = set(), {}
    for path in sorted(glob.glob(os.path.join(sqldir, '*-[0-9][0-9].sql'))):
        kind = os.path.basename(path).rsplit('-', 1)[0]
        if only and kind != only:
            continue
        n = run_file(conn, path, os.path.join(sqldir, kind + '.jsonl'), kind in seen)
        seen.add(kind)
        counts[kind] = counts.get(kind, 0) + n
        print(f'{os.path.basename(path)}: {n} rows', flush=True)
    if not counts:
        raise SystemExit('no SQL files found')
    return counts


def connect():
    import psycopg
    # The Supabase pooler drops PGOPTIONS startup parameters, so the session is made read-only explicitly here
    # (and every transaction after it); assert_read_only still checks it before any query.
    conn = psycopg.connect(os.environ['DATABASE_URL'], autocommit=True)
    conn.execute('set session characteristics as transaction read only')
    conn.execute('set default_transaction_read_only = on')
    conn.autocommit = False
    return conn


def _clean(ciks):
    bad = [c for c in ciks if not re.fullmatch(r'\d{1,10}', c)]
    if bad:
        raise SystemExit(f'not a CIK: {bad[:3]}')
    return sorted({str(int(c)) for c in ciks}, key=int)


def ciks_from_csv(path, conn_factory=connect):
    rows = list(csv.DictReader(open(path)))
    if not rows:
        raise SystemExit('empty csv')
    cols = {c.strip().lower(): c for c in rows[0]}
    if 'cik' in cols:
        return _clean([r[cols['cik']].strip() for r in rows if r[cols['cik']].strip()])
    if 'company_id' in cols:
        ids = sorted({int(r[cols['company_id']]) for r in rows if r[cols['company_id']].strip()})
        conn = conn_factory()
        assert_read_only(conn)
        with conn.cursor() as cur:
            cur.execute("select distinct on (company_id) cik::text from fsn.filing where company_id = any(%s) "
                        "and form in ('10-K','20-F','40-F') order by company_id, period desc, filed desc", (ids,))
            got = [r[0] for r in cur.fetchall()]
        if len(got) != len(ids):
            raise SystemExit(f'{len(ids)} company_ids but {len(got)} have an annual report in fsn.filing')
        return _clean(got)
    raise SystemExit('csv needs a cik or company_id column')


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def manifest(outdir, run_id, code_sha, ciks):
    files = {}
    for p in sorted(glob.glob(os.path.join(outdir, '*.json')) + glob.glob(os.path.join(outdir, '*.jsonl'))):
        name = os.path.basename(p)
        if name == 'manifest.json':
            continue
        rows = sum(1 for _ in open(p)) if name.endswith('.jsonl') else len(json.load(open(p)))
        files[name] = dict(rows=rows, sha256=sha256(p), bytes=os.path.getsize(p))
    return dict(run_id=run_id, code_sha=code_sha, ciks=ciks, n_ciks=len([c for c in ciks.split(',') if c]), files=files)


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('sqldir')
    r.add_argument('--only')
    c = sub.add_parser('ciks')
    c.add_argument('--ciks')
    c.add_argument('--csv')
    m = sub.add_parser('manifest')
    m.add_argument('outdir')
    m.add_argument('--out', required=True)
    m.add_argument('--run-id', default='')
    m.add_argument('--code-sha', default='')
    m.add_argument('--ciks', default='')
    a = ap.parse_args(argv)
    if a.cmd == 'run':
        run_dir(connect(), a.sqldir, a.only)
    elif a.cmd == 'ciks':
        if bool(a.ciks) == bool(a.csv):
            raise SystemExit('give exactly one of --ciks or --csv')
        got = _clean([x for x in re.split(r'[,\s]+', a.ciks.strip()) if x]) if a.ciks else ciks_from_csv(a.csv)
        print(','.join(got))
    else:
        json.dump(manifest(a.outdir, a.run_id, a.code_sha, a.ciks), open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
