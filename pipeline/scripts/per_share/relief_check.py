"""Evidence for 'not filed separately (Item 302(a) relief)': for each candidate 10-K (filed on/after 2021-02-10, fiscal
year before 2021-08-09), fetch the main document and any EX-13 from sec.gov (<= 4 req/s, SEC_USER_AGENT) and decide:
  no_quarterly_table   no document has a quarterly per-share table (q4_table candidates == 0) AND none names a
                       quarterly-data section (QUARTERLY_PHRASE) -> the 10-K prints no separate Q4: reason
                       'not filed separately (Item 302(a) relief)', with the accession and each document's sha256
  table_or_phrase      a table or a section heading exists -> stays 'not captured' (the HTML parser's job)
  unread               a fetch failed or no 10-K document was found -> stays 'not captured'
usage: relief_check.py <scratch>  (input rpage/relief_candidates.json, output rpage/relief_evidence.json)"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, sys.argv[1] + "/rpage")
from q4_table import q4_eps  # noqa: E402

S = Path(sys.argv[1])
UA = os.environ["SEC_USER_AGENT"]
QUARTERLY_PHRASE = re.compile(
    r"quarterly\s+(financial\s+)?(data|information|results|operating\s+results)|selected\s+quarterly|"
    r"results\s+of\s+operations\s+by\s+quarter|unaudited\s+quarterly|quarterly\s+summary",
    re.I,
)
REQ = 0


def get(url: str) -> str:
    global REQ
    assert url.startswith("https://www.sec.gov/"), url
    time.sleep(0.26)
    REQ += 1
    with urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120
    ) as r:
        return r.read().decode("utf8", "ignore")


def docs_of(cik: int, acc: str) -> list[tuple[str, str]]:
    idx = get(
        f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{acc}-index.htm"
    )
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", idx, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        if len(cells) < 4:
            continue
        typ = re.sub(r"<[^>]+>", "", cells[3]).strip().upper()
        link = re.search(
            r'href="(?:/ix\?doc=)?(/Archives/edgar/data/[^"]+\.html?)"', cells[2]
        )
        if link and (typ == "10-K" or typ.startswith("EX-13")):
            out.append((typ, "https://www.sec.gov" + link.group(1)))
    return out


cands = json.load(open(S / "rpage/relief_candidates.json"))
by_acc: dict[str, list[dict]] = {}
for x in cands:
    by_acc.setdefault(x["accession"], []).append(x)
done_path = S / "rpage/relief_evidence.json"
evidence = json.loads(done_path.read_text()) if done_path.exists() else {}
for n, (acc, xs) in enumerate(sorted(by_acc.items())):
    if acc in evidence:
        continue
    end = date.fromisoformat(xs[0]["end"])
    try:
        docs = docs_of(int(xs[0]["cik"]), acc)
        rec = {"documents": [], "outcome": None}
        for typ, url in docs:
            body = get(url)
            res = q4_eps(body, end)
            phrase = QUARTERLY_PHRASE.search(re.sub(r"<[^>]+>", " ", body))
            rec["documents"].append({"type": typ, "url": url, "sha256": hashlib.sha256(body.encode()).hexdigest(),
                                     "candidate_tables": res["tables"], "phrase": phrase.group(0) if phrase else None})  # fmt: skip
        if not docs:
            rec["outcome"] = "unread"
        elif all(
            d["candidate_tables"] == 0 and d["phrase"] is None for d in rec["documents"]
        ):
            rec["outcome"] = "no_quarterly_table"
        else:
            rec["outcome"] = "table_or_phrase"
    except Exception as e:  # a fetch failure never becomes evidence
        rec = {"documents": [], "outcome": "unread", "error": str(e)[:200]}
    evidence[acc] = rec
    if n % 20 == 0:
        done_path.write_text(json.dumps(evidence, indent=0))
        print(
            n,
            len(by_acc),
            REQ,
            dict(Counter(v["outcome"] for v in evidence.values())),
            flush=True,
        )
done_path.write_text(json.dumps(evidence, indent=0))
print("done", REQ, dict(Counter(v["outcome"] for v in evidence.values())))
