#!/usr/bin/env python3
"""Runner for the resolver's standard extract (pipeline-standard-extract.yml). Read-only, no SEC access.

  run_extract_sql.py run SQLDIR [--only le]   execute SQLDIR/<kind>-NN.sql in name order on ONE connection, append one
                                              JSON object per result row (column names as keys) to SQLDIR/<kind>.jsonl
  run_extract_sql.py ciks --ciks A,B | --csv PATH
                                              print the comma list of CIKs; a csv needs a cik or company_id column
                                              (company_id is resolved to the CIK of the company's latest annual report)
  run_extract_sql.py manifest OUTDIR --out FILE --run-id ID --code-sha SHA --ciks LIST [--shards FILE]
                                              row counts and SHA-256 of every file in OUTDIR (+ per-shard row counts)
  run_extract_sql.py shard --ciks LIST --n N  print the matrix JSON: N contiguous, balanced shards of the sorted CIK list
  run_extract_sql.py merge SHARDSDIR OUTDIR   concatenate each kind's .jsonl (and retries.json) over SHARDSDIR/*shard-<i>-*
                                              in shard order into OUTDIR; writes OUTDIR/shards.json (rows per shard and kind)

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
RETRY_FLOOR_S = 600  # the single-CIK retry runs at least this long (still capped at MAX_TIMEOUT_S)
# Last resort for one company that still times out alone (run 43833278049: Citigroup, CIK 831001, face at 600s): the query is
# re-run per filing-period slice. Every output row of the four standard queries (lines, bs, notes, face) is one filing of `company_filings`, and whether
# a filing belongs is decided per filing, so restricting `f.period` inside that CTE partitions the rows exactly.
PERIOD_ANCHOR = re.compile(r"(where\s+co\.cik::bigint\s+in\s+\(\s*\d+\s*\))", re.I)
SLICE_BOUNDS = ("2014-01-01", "2016-01-01", "2018-01-01", "2020-01-01", "2022-01-01", "2024-01-01")


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


def _is_timeout(e):
    return getattr(e, 'sqlstate', None) == '57014' or type(e).__name__ == 'QueryCanceled'


def timeout_of(sql):
    m = LEAD_SET.match(sql)
    return int(re.search(r"'(\d+)s'", m.group(1)).group(1)) if m else None


def with_timeout(sql, secs):
    secs = min(secs, MAX_TIMEOUT_S)
    stmt = f"set statement_timeout='{secs}s';"
    m = LEAD_SET.match(sql)
    return sql[:m.start(1)] + stmt + sql[m.end(1):] if m else stmt + '\n' + sql


def period_slices(sql, bounds=SLICE_BOUNDS):
    """The single-company query split into filing-period slices [None, b0), [b0, b1), ..., [bn, None); [] when the query
    has no `where co.cik::bigint in (<one cik>)` anchor (it cannot be sliced safely)."""
    if len(PERIOD_ANCHOR.findall(sql)) != 1:
        return []
    edges = [None, *bounds, None]
    out = []
    for lo, hi in zip(edges, edges[1:]):
        cond = "".join(
            [f" and f.period >= date '{lo}'" if lo else "", f" and f.period < date '{hi}'" if hi else ""]
        )
        out.append(((lo, hi), PERIOD_ANCHOR.sub(lambda m: m.group(1) + cond, sql, count=1)))
    return out


def batch_ciks(sql):
    """The CIKs a generated batch query selects (every kind but le carries `cik::bigint in (a,b,..)`)."""
    m = re.search(r"cik::bigint in \(([\d,\s]+)\)", sql)
    return [c.strip() for c in m.group(1).split(',') if c.strip()] if m else []


def query_lines(conn, sql):
    """Run one SQL text (an optional leading set statement, then one query); -> the JSON lines, nothing written."""
    pre, query = split_sql(sql)
    lines = []
    with conn.cursor() as cur:
        if pre:
            cur.execute(pre)
        cur.execute(query)
        cols = [d[0] if isinstance(d, tuple) else d.name for d in cur.description]
        for row in cur:
            rec = dict(zip(cols, row))
            _reject_float(rec)
            lines.append(json.dumps(rec, default=_default, separators=(',', ':')))
    return lines


def default_regen(kind, cik):
    """The kind's query for ONE cik, generated by the resolver tool (same SQL, one-company batch)."""
    import sys
    import tempfile
    tools = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data-team', 'tags', 'line_map', 'tools')
    sys.path.insert(0, tools)
    import standard_run
    with tempfile.TemporaryDirectory() as d:
        standard_run.write_sql([cik], d, 1)
        return open(os.path.join(d, f'{kind}-00.sql')).read()


def _attempt(conn, sql):
    """-> (lines, None) or (None, error) when the statement timed out; any other error propagates."""
    try:
        lines = query_lines(conn, sql)
        conn.rollback()
        return lines, None
    except Exception as e:  # noqa: BLE001
        if not _is_timeout(e):
            raise
        conn.rollback()
        return None, e


def run_file(conn, path, out_path, append, regen=default_regen, retries=None):
    """Run one batch file. A statement timeout re-splits the batch: each CIK alone, at the batch's own timeout, then once at
    double (capped at MAX_TIMEOUT_S). Rows are written only when the whole batch succeeded; every retry goes into `retries`."""
    sql = open(path).read()
    name = os.path.basename(path)
    lines, err = _attempt(conn, sql)
    if err is not None:
        kind = name.rsplit('-', 1)[0]
        base = timeout_of(sql) or 55
        ciks = batch_ciks(sql)
        retries = retries if retries is not None else []
        print(f'{name}: statement timeout; re-splitting {len(ciks) or 1} unit(s)', flush=True)
        units = [(c, regen(kind, c)) for c in ciks] if ciks and len(ciks) > 1 else [(ciks[0] if ciks else None, sql)]
        lines = []
        for cik, usql in units:
            single = usql is sql
            got, e2 = (None, err) if single else _attempt(conn, usql)
            rec = dict(file=name, kind=kind, cik=cik, batch_timeout_s=base)
            if got is None:
                # one CIK alone gets the long ceiling (a single company with many filings, e.g. AXP face, needs >110s)
                dbl = min(max(base * 2, RETRY_FLOOR_S), MAX_TIMEOUT_S)
                got, e3 = _attempt(conn, with_timeout(usql, dbl))
                rec.update(retry_timeout_s=dbl, outcome='ok_doubled' if got is not None else 'failed')
                if got is None and (slices := period_slices(usql)):
                    # still too slow alone: run it per filing-period slice, each at the ceiling
                    print(f'{name}: CIK {cik} times out alone at {dbl}s; running {len(slices)} period slices', flush=True)
                    got, done = [], []
                    for (lo, hi), ssql in slices:
                        part, e4 = _attempt(conn, with_timeout(ssql, MAX_TIMEOUT_S))
                        if part is None:
                            got, e3 = None, e4
                            rec.update(failed_slice=[lo, hi])
                            break
                        got += part
                        done.append([lo, hi])
                    rec.update(slices=done, slice_timeout_s=MAX_TIMEOUT_S)
                    if got is not None:
                        rec.update(outcome='ok_sliced')
                retries.append(rec)
                if got is None:
                    raise SystemExit(f'CIK {cik} ({name}) still times out at {dbl}s: {e3}')
            else:
                rec.update(retry_timeout_s=None, outcome='ok_alone')
                retries.append(rec)
            lines += got
    with open(out_path, 'a' if append else 'w') as out:
        for ln in lines:
            out.write(ln + '\n')
    return len(lines)


def run_dir(conn, sqldir, only=None, regen=default_regen):
    assert_read_only(conn)
    seen, counts, retries = set(), {}, []
    for path in sorted(glob.glob(os.path.join(sqldir, '*-[0-9][0-9].sql'))):
        kind = os.path.basename(path).rsplit('-', 1)[0]
        if only and kind != only:
            continue
        n = run_file(conn, path, os.path.join(sqldir, kind + '.jsonl'), kind in seen, regen, retries)
        seen.add(kind)
        counts[kind] = counts.get(kind, 0) + n
        print(f'{os.path.basename(path)}: {n} rows', flush=True)
    if not counts:
        raise SystemExit('no SQL files found')
    if retries:
        rp = os.path.join(sqldir, 'retries.json')
        prior = json.load(open(rp)) if os.path.exists(rp) else []
        json.dump(prior + retries, open(rp, 'w'), indent=1)
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


MAX_SHARDS = 12
KINDS = ('lines', 'bs', 'notes', 'face')


def shard_ciks(ciks, n):
    """Sorted CIKs -> up to n contiguous shards whose sizes differ by at most 1 (contiguous, so the concatenated rows keep a
    single run's CIK order). Never an empty shard; n is clamped to 1..MAX_SHARDS."""
    ciks = _clean(list(ciks))
    n = max(1, min(int(n), MAX_SHARDS, len(ciks) or 1))
    q, r = divmod(len(ciks), n)
    out, k = [], 0
    for i in range(n):
        size = q + (1 if i < r else 0)
        out.append(ciks[k:k + size])
        k += size
    return [c for c in out if c]


def merge_shards(shards_dir, outdir):
    """Concatenate SHARDS_DIR/<...shard-<i>-...>/<kind>.jsonl in shard order; -> {shard index: {kind: rows}}."""
    found = {}
    for d in os.listdir(shards_dir):
        m = re.search(r'shard-(\d+)(?:-|$)', d)
        if m and os.path.isdir(os.path.join(shards_dir, d)):
            found[int(m.group(1))] = os.path.join(shards_dir, d)
    if not found:
        raise SystemExit(f'no shard directories in {shards_dir}')
    idx = sorted(found)
    if idx != list(range(len(idx))):
        raise SystemExit(f'shard indexes not contiguous from 0: {idx}')
    os.makedirs(outdir, exist_ok=True)
    per, retries = {}, []
    for kind in KINDS:
        with open(os.path.join(outdir, kind + '.jsonl'), 'w') as out:
            for i in idx:
                p = os.path.join(found[i], kind + '.jsonl')
                if not os.path.exists(p):
                    raise SystemExit(f'shard {i} has no {kind}.jsonl')
                n = 0
                for ln in open(p):
                    if ln.strip():
                        out.write(ln if ln.endswith('\n') else ln + '\n')
                        n += 1
                per.setdefault(str(i), {})[kind] = n
    for i in idx:
        rp = os.path.join(found[i], 'retries.json')
        if os.path.exists(rp):
            retries += [dict(r, shard=i) for r in json.load(open(rp))]
    if retries:
        json.dump(retries, open(os.path.join(outdir, 'retries.json'), 'w'), indent=1)
    json.dump(per, open(os.path.join(outdir, 'shards.json'), 'w'), indent=1)
    return per


def manifest(outdir, run_id, code_sha, ciks, shards=None):
    files = {}
    for p in sorted(glob.glob(os.path.join(outdir, '*.json')) + glob.glob(os.path.join(outdir, '*.jsonl'))):
        name = os.path.basename(p)
        if name == 'manifest.json':
            continue
        rows = sum(1 for _ in open(p)) if name.endswith('.jsonl') else len(json.load(open(p)))
        if name == 'shards.json':
            continue
        files[name] = dict(rows=rows, sha256=sha256(p), bytes=os.path.getsize(p))
    rp = os.path.join(outdir, 'retries.json')
    retries = json.load(open(rp)) if os.path.exists(rp) else []
    m = dict(run_id=run_id, code_sha=code_sha, ciks=ciks, n_ciks=len([c for c in ciks.split(',') if c]), files=files,
             retries=retries)
    if shards:
        m['shards'] = shards
    return m


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
    m.add_argument('--shards')
    h = sub.add_parser('shard')
    h.add_argument('--ciks', required=True)
    h.add_argument('--n', default='8')
    g = sub.add_parser('merge')
    g.add_argument('shards_dir')
    g.add_argument('outdir')
    a = ap.parse_args(argv)
    if a.cmd == 'run':
        run_dir(connect(), a.sqldir, a.only)
    elif a.cmd == 'ciks':
        if bool(a.ciks) == bool(a.csv):
            raise SystemExit('give exactly one of --ciks or --csv')
        got = _clean([x for x in re.split(r'[,\s]+', a.ciks.strip()) if x]) if a.ciks else ciks_from_csv(a.csv)
        print(','.join(got))
    elif a.cmd == 'shard':
        parts = shard_ciks([x for x in re.split(r'[,\s]+', a.ciks.strip()) if x], a.n)
        print(json.dumps([dict(i=i, n=len(c), ciks=','.join(c)) for i, c in enumerate(parts)], separators=(',', ':')))
    elif a.cmd == 'merge':
        print(json.dumps(merge_shards(a.shards_dir, a.outdir)))
    else:
        sh = json.load(open(a.shards)) if a.shards else None
        json.dump(manifest(a.outdir, a.run_id, a.code_sha, a.ciks, sh), open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
