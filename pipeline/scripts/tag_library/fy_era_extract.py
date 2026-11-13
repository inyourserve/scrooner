"""Read-only FSN extract for fy_era_status.py: every 10-K (since 2015) of the map's companies with its count of face
statements, the lines a per-year decision can use (a candidate or combined tag of any data point, or a label candidate),
and the candidate tags among each 10-K's XBRL facts (core.fact, any authority: presence is the question; the FSN store has
the statement pages only, the facts cover the notes). One connection, four queries per company, statement_timeout 60s,
read-only transactions. Usage: fy_era_extract.py <tag_map.csv> <filings_out.csv> <lines_out.csv> <facts_out.csv>"""
import csv
import os
import sys

import psycopg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fy_era_status import LABEL, candidates  # noqa: E402

tm, fil_out, lin_out, fct_out = sys.argv[1:5]
rows = list(csv.DictReader(open(tm)))
serve, comb = candidates(rows)
tags = sorted(set().union(*serve.values(), *comb.values()))
companies = sorted({int(r["company_id"]) for r in rows})
FIL = ["company_id", "accession", "form", "period", "accepted", "faces"]
LIN = ["accession", "report", "rfile", "line", "stmt", "tag", "custom", "plabel"]
nf = nl = nx = 0
with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn, \
        open(fil_out, "w", newline="") as ff, open(lin_out, "w", newline="") as fl, open(fct_out, "w", newline="") as fx:
    conn.execute("set statement_timeout = '60s'")
    conn.execute("set default_transaction_read_only = on")
    wf, wl, wx = csv.writer(ff), csv.writer(fl), csv.writer(fx)
    wf.writerow(FIL)
    wl.writerow(LIN)
    wx.writerow(["accession", "tag"])
    for c in companies:
        fs = conn.execute("""select f.id, f.accession, f.form, f.period, f.accepted,
                                    (select count(distinct l.stmt) from fsn.line l where l.filing_id = f.id and l.stmt in ('BS', 'IS', 'CF'))
                             from fsn.filing f where f.company_id = %s and f.form in ('10-K', '10-K/A', '10-KT', '10-KT/A')
                             and f.period >= '2014-12-20'""", (c,)).fetchall()
        for fid, acc, form, period, accepted, faces in fs:
            wf.writerow([c, acc, form, period, accepted.isoformat() if accepted else "", faces])
            nf += 1
        for a, n in conn.execute("""select fl.accession_number, count(*) from core.fact f join core.filing fl on fl.id = f.filing_id
                                    where f.company_id = %s and fl.form in ('10-K', '10-K/A', '10-KT', '10-KT/A')
                                    and fl.filing_date >= '2015-01-01' group by 1""", (c,)):
            wx.writerow([a, "*"])  # the filing has XBRL facts at all (n of them)
        for a, tag in conn.execute("""select distinct fl.accession_number, c.tag from core.fact f
                                      join core.filing fl on fl.id = f.filing_id join core.concept c on c.id = f.concept_id
                                      where f.company_id = %s and fl.form in ('10-K', '10-K/A', '10-KT', '10-KT/A')
                                      and fl.filing_date >= '2015-01-01' and c.tag = any(%s)""", (c, tags)):
            wx.writerow([a, tag])
            nx += 1
        ids = [x[0] for x in fs]
        if not ids:
            continue
        acc_of = {x[0]: x[1] for x in fs}
        for fid, report, rfile, line, stmt, tag, custom, plabel in conn.execute(
                """select l.filing_id, l.report, r.rfile, l.line, l.stmt, t.tag, t.custom, l.plabel
                   from fsn.line l join fsn.tag t on t.id = l.tag_id
                   left join fsn.report r on r.filing_id = l.filing_id and r.report = l.report
                   where l.filing_id = any(%s)""", (ids,)):
            if tag in tags or any(rx.search(plabel or "") for rx in LABEL.values()):
                wl.writerow([acc_of[fid], report, rfile or "", line, stmt, tag, "t" if custom else "f", plabel or ""])
                nl += 1
print("filings", nf, "| lines", nl, "| fact tags", nx, "| companies", len(companies), "| candidate tags", len(tags))
