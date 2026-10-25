"""Shared pieces of the slot-record engine (stdlib + psycopg). One copy of each
rule that every family uses, so a fix lands once and is re-verified once:

  load_cal(cal_dir, adsh)          calc linkbase with the fallback chain
                                   (_cal.xml -> .xsd embedded -> MetaLinks.json)
  statement_children(arcs, role_rx) parent -> children in the STATEMENT role only
  fetch_instants(cur, cik, tags)   same-accession instant facts (the original
                                   filing of each instant, periodic forms only)
  rounding_unit(values)            the filer's rounding unit (identity tolerance)
  SecClient                        sec.gov fetch: SEC_USER_AGENT, <= 4 req/s,
                                   disk floor, request counter
  face_rows_for(path, accessions)  ordered BS face rows per filing from the FSDS
                                   pre extract (plain or .gz)
Regression numbers the refactor must keep: 19-company BS set 851 ties / 0
withheld / 16 of 16 anchors; batch 2 378 ties; debt fixtures 15 of 15.
"""
import gzip
import json
import os
import re
import shutil
import time
import urllib.request
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import build_debt_slots as b

PERIODIC_FORMS = ("10-K", "10-Q", "10-K/A", "10-Q/A")
NOTE_ROLE_RX = b.NOTE_ROLE_RX
BS_ROLE_RX = b.BS_ROLE_RX
CF_ROLE_RX = re.compile(r"cash ?-?flows?", re.I)


def load_cal(cal_dir, adsh):
    """-> (taxonomy_era, arcs) or (None, {}) when no cal file is present.
    arcs: {(role, parent): [(child, weight, child_is_custom)]}."""
    d = Path(cal_dir) / adsh
    files = sorted(d.glob("*_cal.xml")) or sorted(d.glob("*.xsd"))
    meta = d / "MetaLinks.json"
    if files:
        cal = b.parse_cal(files[0])
    elif meta.exists():
        cal = b.parse_metalinks(meta)
    else:
        return None, {}
    return cal["era"], cal["arcs"]


def statement_children(arcs, role_rx):
    """parent -> set(children) restricted to the statement role (never a note role)."""
    children = defaultdict(set)
    for (role, parent), kids in arcs.items():
        if not role_rx.search(role) or NOTE_ROLE_RX.search(role):
            continue
        children[parent].update(c for c, _w, _cu in kids)
    return children


def rounding_unit(values, cap=Decimal(1000000)):
    """Largest power of ten dividing every non-zero value (capped)."""
    unit = cap
    for v in values:
        if v is None or v == 0:
            continue
        while unit > 1 and v % unit != 0:
            unit /= 10
    return unit


def fetch_instants(cur, cik, tags, since="2015-01-01"):
    """{end_date: {tag: Decimal, '__accession__': acc}} with every term of a cell
    from ONE filing: the original (period_of_report == end) else the accession
    carrying the most of the needed tags. Periodic forms only."""
    cur.execute(
        """
        select co.tag, p.end_date::text, f.value::numeric, f.is_authoritative,
               fi.accession_number, fi.period_of_report::text
        from core.fact f
        join core.concept co on co.id = f.concept_id
        join core.period p on p.id = f.period_id
        join core.unit u on u.id = f.unit_id
        join core.company c on c.id = f.company_id
        join core.filing fi on fi.id = f.filing_id
        where c.cik = %s and p.period_type = 'instant' and co.taxonomy = 'us-gaap'
          and u.unit_name = 'usd' and co.tag = any(%s) and fi.form = any(%s)
          and p.end_date >= %s
        order by co.tag, p.end_date, f.is_authoritative desc, f.id desc
        """,
        (cik, sorted(tags), list(PERIODIC_FORMS), since),
    )
    by_acc = defaultdict(lambda: defaultdict(dict))
    original = {}
    for tag, e, v, _auth, acc, por in cur.fetchall():
        by_acc[e][acc].setdefault(tag, v)
        if por == e:
            original.setdefault(e, acc)
    facts = {}
    for e, accs in by_acc.items():
        acc = original.get(e) or max(accs, key=lambda a: len(accs[a]))
        facts[e] = dict(accs[acc])
        facts[e]["__accession__"] = acc
    return facts


def face_rows_for(path, accessions, stmt="BS"):
    """Ordered face rows per filing: {adsh: [{tag, custom, label}, ...]}."""
    tmp = defaultdict(list)
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("stmt", stmt) == stmt and r["adsh"] in accessions:
                tmp[r["adsh"]].append((r["report"], r["line"], {"tag": r["tag"], "custom": r["custom"], "label": r.get("label") or ""}))
    return {a: [d for _, _, d in sorted(v, key=lambda x: (x[0], x[1]))] for a, v in tmp.items()}


class SecClient:
    """sec.gov only; SEC_USER_AGENT from the environment; <= 4 requests/second;
    stops when free disk < 4 GB; counts requests for the push message."""

    def __init__(self, min_free_gb=4):
        self.ua = os.environ.get("SEC_USER_AGENT")
        if not self.ua:
            raise SystemExit("SEC_USER_AGENT missing (source pipeline/.env)")
        self.requests = 0
        self._last = 0.0
        self.min_free = min_free_gb * 1024**3

    def get(self, url):
        if not url.startswith("https://www.sec.gov/"):
            raise ValueError("sec.gov only: " + url)
        if shutil.disk_usage("/private/tmp").free < self.min_free:
            raise SystemExit(f"free disk below floor after {self.requests} requests; stopping")
        wait = 0.26 - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": self.ua, "Accept-Encoding": "gzip, deflate"})
        self._last = time.monotonic()
        self.requests += 1
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
            return gzip.decompress(data) if r.headers.get("Content-Encoding") == "gzip" else data

    def folder(self, cik, adsh):
        return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/"

    def index_names(self, cik, adsh):
        return [i["name"] for i in json.loads(self.get(self.folder(cik, adsh) + "index.json"))["directory"]["item"]]
