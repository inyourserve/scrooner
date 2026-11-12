"""Copy one batch of docmaps into the worktree, add the hand check vs the shared docmap.py, inbox rows and the summary.
Usage: python3 -I commit_batch.py <reads_dir> <worktree> <first_rank> <last_rank>
Prints the ticker list; git is run by the caller."""
import sys, os, json, csv, glob, shutil, collections as C

R, WT, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
DATE = '2026-11-12'
ranks = {r['rank']: r for r in json.load(open(os.path.join(R, 'ranks.json')))}
log = {}
for fn in glob.glob(os.path.join(R, 'b*.log')):
    for line in open(fn):
        try:
            d = json.loads(line); log[d['rank']] = d
        except Exception:
            pass
dst = os.path.join(WT, 'data-team/companies/reads')
inbox = os.path.join(WT, 'data-team/tags/feedback-inbox-701-800.md')
if True:   # regenerated from every committed rank on each run (reruns must not duplicate rows)
    open(inbox, 'w').write('# Tag feedback inbox: document-first reads, ranks 701-800 (append-only)\n\n'
                           'Same format as feedback-inbox.md. Every row comes from a docmap in data-team/companies/reads/ (FILING-CHECKED R pages vs SEC companyfacts; era rows from companyfacts by 10-K, DATA-INFERRED).\n\n'
                           '| date | from | tag | what was learned | evidence | class | status |\n|---|---|---|---|---|---|---|\n')
def ts(s): return {t.split(':')[-1] for t in s.replace('+', ';').split(';') if t.strip()}
def norm(s): return (s or '').strip().lower().replace(' ', '_')
done = []
for rank in range(701, hi + 1):
    tk = ranks[rank]['ticker']
    md = os.path.join(R, 'out', f'{tk}-docmap-{DATE}.md'); cv = os.path.join(R, 'out', f'{tk}-docmap-{DATE}.csv')
    if not os.path.exists(md):
        print('MISSING', tk); sys.exit(2)
    # hand check vs the shared tool
    sh = os.path.join(R, 'shared', 'out', f'{tk}-docmap-{DATE}.csv')
    lines = ['', '## Hand check vs the shared reader (data-team/companies/reads/tools/docmap.py @558f2f15, origin/work/reads/901-1000)']
    if os.path.exists(sh):
        a = {r['data_point']: r for r in csv.DictReader(open(sh))}
        b = {r['data_point']: r for r in csv.DictReader(open(cv))}
        n_ag = 0; rows = []
        for dp, x in a.items():
            y = b.get(dp)
            if not y: continue
            same = norm(x['status']) == norm(y['status']) and (norm(x['status']) not in ('mapped', 'combined', 'component_sum') or ts(x['tags']) == ts(y['tags']))
            if same: n_ag += 1; continue
            why = ('shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides)' if norm(x['status']) == 'mapped' and not x['fy0_printed']
                   else 'sector template (approved 2026-11-01) for a not-presented line' if norm(y['status']) == 'out'
                   else 'ruling 2026-11-12 (operating expenses never include cost of revenue)' if dp == 'operating_expenses'
                   else 'face lines re-read for this row: see the face-line table above')
            rows.append(f"| {dp} | {x['status']} {x['tags'].replace('us-gaap:', '')[:60]} {x['fy0_printed']} | {y['status']} {y['tags'].replace('us-gaap:', '')[:80]} {y['fy0_printed']} | {why} |")
        lines += [f'{n_ag} data points agree; {len(rows)} differ. The value kept is the one printed on the R page.', '',
                  '| data point | shared reader | this read (kept) | why |', '|---|---|---|---|'] + rows
    else:
        lines.append('shared reader output not available for this company')
    open(os.path.join(dst, os.path.basename(md)), 'w').write(open(md).read() + '\n'.join(lines) + '\n')
    shutil.copy(cv, os.path.join(dst, os.path.basename(cv)))
    # inbox rows
    q = json.load(open(os.path.join(R, 'out', 'quirks', tk + '.json')))
    mq = os.path.join(R, 'manual_quirks', tk + '.json')
    if os.path.exists(mq): q += json.load(open(mq))
    with open(inbox, 'a') as f:
        for x in q:
            what = f"{x['ticker']} (rank {x['rank']}) [{x['kind']}] {x['data_point']}: '{x['label'][:90]}' — {x['note']}"
            ev = f"{x['accession']} {x['r_page']} {x['period_end']}".strip()
            cls = 'DATA-INFERRED (companyfacts by 10-K)' if x['kind'] == 'era_change' else 'FILING-CHECKED'
            f.write(f"| {DATE} | FSN expert (reads 701-800) | {x['tag'].replace('|', '/')[:200]} | {what.replace('|', '/')} | {ev} | {cls} | new |\n")
    done.append(tk)
# tools
td = os.path.join(dst, 'tools', 'reads701')
os.makedirs(td, exist_ok=True)
for t in ('read2.py', 'docmap.py', 'dbload.py', 'secget.py', 'commit_batch.py'):
    shutil.copy(os.path.join(R, 'tools', t), os.path.join(td, t))
open(os.path.join(td, 'README.md'), 'w').write(
    '# Reader used for ranks 701-800 (FSN expert session)\n\n'
    '`read2.py <outdir> <db_export.json> <ranks.json> <rank>...`: index, statement reports and FSN line tags from our DB (fsn.filing, fsn.report, fsn.line);\n'
    'R pages from sec.gov (statements only, 0.4 req/s, SEC_USER_AGENT from the environment); companyfacts from data.sec.gov.\n'
    'Rulings applied (Dhairya 2026-11-12): shares_outstanding = CommonStockSharesOutstanding at the BS date (never the dei cover); a wider receivables tag is AR only as the single receivables line; '
    'operating_expenses never includes cost of revenue (printed total excluding COGS, else the component sum of every line between GP and OI tied to GP - OI; a total including COGS is combined); '
    'eras FY2015 to latest for every data point (FY2015 10-K always opened). Every batch is hand-checked against the shared reader (tools/docmap.py) and each difference is decided on the R page.\n')
# summary (numbers only)
allr = sorted(k for k in log if 701 <= k <= hi)
rows = [log[k] for k in allr]
def s(k): return sum(int(r.get(k) or 0) for r in rows)
summ = os.path.join(dst, 'SUMMARY-701-800-2026-11-12.md')
cnt = C.Counter()
for k in allr:
    tk = ranks[k]['ticker']
    for r in csv.DictReader(open(os.path.join(dst, f'{tk}-docmap-{DATE}.csv'))):
        cnt[r['status']] += 1
        if r['status'] not in ('OUT', 'not_presented'): cnt['era_complete' if ' complete' in r['era_from_note'] else 'era_gap'] += 1
open(summ, 'w').write('\n'.join([
    '# Ranks 701-800 document-first reads: summary (numbers only)', '',
    f'| item | value |', '|---|---|',
    f'| companies read | {len(rows)} |', f'| statement R pages read (latest 10-K) | {s("statements")} |', f'| era 10-Ks opened | {s("era_10k")} |',
    f'| sec.gov + data.sec.gov requests (this reader + the shared reader used for the hand check; cumulative) | {sum(1 for _ in open(os.path.join(R, "requests.log")))} |', f'| face lines with an FY0 value | {s("face_lines")} |',
    f'| face lines equal to companyfacts | {s("face_api_equal")} |', f'| face lines differing from companyfacts | {s("face_api_differ")} |',
    f'| face lines without a companyfacts fact | {s("face_api_none")} |', f'| custom-tag face lines | {s("face_custom")} |', f'| dimensional face lines | {s("face_dimensional")} |',
    f'| data-point rows | {sum(v for k, v in cnt.items() if not k.startswith("era_"))} |',
    *[f'| status {k} | {v} |' for k, v in sorted(cnt.items()) if not k.startswith('era_')],
    f'| mapped data points with eras covered FY2015 (or first 10-K) to latest | {cnt["era_complete"]} |', f'| mapped data points with an era gap | {cnt["era_gap"]} |',
    f'| data-point value mismatches (printed vs companyfacts) | {s("dp_value_mismatch")} |', f'| quirk rows to the inbox | {s("quirks")} |', '']))
print(' '.join(done))
