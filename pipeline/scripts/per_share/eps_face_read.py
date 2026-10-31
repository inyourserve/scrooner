"""Face read for the Family C 'copies disagree' EPS cells: the cell's own original periodic filing's R pages
(quarterly-data note for a 10-K Q4, the income statement for a 10-Q). sec.gov only, SEC_USER_AGENT, <= 4 req/s.
usage: eps_face_read.py <scratch>  (DB read-only for the filing list; kit from pipeline/src on PYTHONPATH)"""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from ro import conn  # noqa: E402
from scrooner_pipeline.verification import filing_kit as fk  # noqa: E402

S = Path(sys.argv[1])
UA = os.environ["SEC_USER_AGENT"]
REQUESTS = 0


class Client:
    def get(self, url: str) -> bytes:
        global REQUESTS
        assert url.startswith("https://www.sec.gov/"), url
        time.sleep(0.3)
        REQUESTS += 1
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60
        ) as r:
            return r.read()


cells = [
    x
    for x in json.load(open(S / "epsfsn3/nc_fsn_outcomes.json"))
    if x["outcome"] == "fsn_copies_disagree"
]
c = conn()
filing = {}
for x in cells:
    end = date.fromisoformat(x["end"])
    form = "10-K" if x["fp"] == "Q4" else "10-Q"
    row = c.execute(
        """select accession_number from core.filing where company_id = %s and form = %s
           and period_of_report between %s and %s order by filing_date, id limit 1""",
        (x["company_id"], form, end - timedelta(days=7), end + timedelta(days=7)),
    ).fetchone()
    filing[x["canonical_fact_id"]] = (row[0] if row else None, form)
client, pages, out = Client(), {}, []
for x in cells:
    acc, form = filing[x["canonical_fact_id"]]
    if acc is None:
        out.append({**x, "face": None, "face_note": "no original periodic filing"})
        continue
    if acc not in pages:
        folder = f"https://www.sec.gov/Archives/edgar/data/{int(x['cik'])}/{acc.replace('-', '')}/"
        fs = client.get(folder + "FilingSummary.xml").decode("utf8", "ignore")
        reps = fk._reports(fs)
        if form == "10-K":
            pick = [
                r
                for r in reps
                if re.search(r"quarter", r[0], re.I)
                and re.search(r"detail", r[0], re.I)
            ] or [r for r in reps if re.search(r"quarter", r[0], re.I)]
        else:
            sel = fk.select_income_statement(fs)
            pick = [r for r in reps if sel and r[1] == sel[1]]
        pages[acc] = [
            (r[0], fk.parse_rpage(client.get(folder + r[1]).decode("utf8", "ignore")))
            for r in pick[:2]
        ]
    end = date.fromisoformat(x["end"])
    want = "diluted" if x["concept"].startswith("diluted") else "basic"
    hits = []
    for name, page in pages[acc]:
        cols = [
            i
            for i, d in enumerate(page.columns)
            if d is not None
            and abs((d - end).days) <= 7
            and (page.months[i : i + 1] or [None])[0] in (3, None)
        ]
        for row in page.rows:
            lab = row.label.lower()
            if want in lab and ("share" in lab or "eps" in lab or "per" in lab):
                for i in cols:
                    if i < len(row.values) and row.values[i] is not None:
                        hits.append(
                            {
                                "report": name,
                                "label": row.label,
                                "value": str(row.values[i]),
                            }
                        )
    out.append({**x, "accession": acc, "face": hits})
(S / "epsfsn3/face_read.json").write_text(json.dumps(out, indent=1, default=str))
for o in out:
    print(
        o["canonical_fact_id"],
        o["cik"],
        o["concept"],
        o["end"],
        "copies",
        o["values"],
        "stored",
        o["stored"],
        "| face:",
        [(h["label"][:40], h["value"]) for h in (o["face"] or [])][:4],
    )
print("SEC requests", REQUESTS)
