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


_FSN_CAL_CACHE = {}


def fsn_cal_arcs(cal_tsv_path, adsh, pre_tsv_path=None):
    """Arcs for one filing from the FSN data set's cal.tsv, in the same shape
    as load_cal: {(role, parent): [(child, weight, child_is_custom)]}. cal.tsv
    has no role URIs, only a group number, so the STATEMENT of a group is
    decided by the elements it totals (an element rule, not a label rule):
      BS = the largest group whose parents include LiabilitiesAndStockholders
           Equity / LiabilitiesAndPartnersCapital (or Assets together with
           Liabilities / LiabilitiesCurrent / StockholdersEquity);
      CF = the group with NetCashProvidedByUsedInOperatingActivities as parent;
      other groups keep 'grp<n>' (treated as note roles by the statement
      filters). 'negative' is the weight (1 / -1); custom = version column not
      us-gaap/srt/dei/ifrs. pre_tsv_path is accepted for a future refinement."""
    import csv
    import io
    import subprocess
    key = str(cal_tsv_path)
    if key not in _FSN_CAL_CACHE:
        if key.endswith(".zst"):
            fh = io.TextIOWrapper(subprocess.Popen(["zstd", "-dc", key], stdout=subprocess.PIPE).stdout, encoding="utf-8", errors="replace")
        else:
            fh = open(key, encoding="utf-8", errors="replace")
        by = defaultdict(lambda: defaultdict(list))  # adsh -> grp -> [(parent, child, weight, custom)]
        for r in csv.DictReader(fh, delimiter="\t"):
            custom = not r.get("cversion", "").startswith(("us-gaap", "srt", "dei", "ifrs"))
            by[r["adsh"]][r["grp"]].append((r["ptag"], r["ctag"], str(float(r.get("negative") or "1")), custom))
        _FSN_CAL_CACHE[key] = by
    groups = _FSN_CAL_CACHE[key].get(adsh, {})
    bs_candidates = []
    cf_group = None
    for g, arcs in groups.items():
        parents = {p for p, _c, _w, _cu in arcs}
        if parents & {"LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital"} or (
                "Assets" in parents and parents & {"Liabilities", "LiabilitiesCurrent", "StockholdersEquity"}):
            bs_candidates.append((len(arcs), g))
        if "NetCashProvidedByUsedInOperatingActivities" in parents or "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations" in parents:
            if cf_group is None or len(arcs) > len(groups[cf_group]):
                cf_group = g
    bs_group = max(bs_candidates)[1] if bs_candidates else None
    out = defaultdict(list)
    for g, arcs in groups.items():
        role = "BS#grp" + g if g == bs_group else ("CashFlow#grp" + g if g == cf_group else "grp" + g)
        for p, c, w, cu in arcs:
            out[(role, p)].append((c, w, cu))
    return dict(out)


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


def fetch_durations(cur, cik, tags, since="2015-01-01"):
    """{(start, end): (accession, {tag: Decimal})} with every term of a cell from
    ONE filing (the original whose period_of_report is the end date, else the
    accession carrying the most of the needed tags). Periodic forms only, and
    NEVER a derived fact (Verifier D&A V2: ABBV Q4 2020 replay 2,088M came from
    a derived quarter built on a nine-month figure not on the Q3 10-Q face;
    the slot engine reads what the filer tagged, never a subtraction)."""
    cur.execute(
        """
        select co.tag, p.start_date::text, p.end_date::text, f.value::numeric, f.is_authoritative,
               fi.accession_number, fi.period_of_report::text
        from core.fact f
        join core.concept co on co.id = f.concept_id
        join core.period p on p.id = f.period_id
        join core.unit u on u.id = f.unit_id
        join core.company c on c.id = f.company_id
        join core.filing fi on fi.id = f.filing_id
        where c.cik = %s and p.period_type = 'duration' and co.taxonomy = 'us-gaap'
          and u.unit_name = 'usd' and co.tag = any(%s) and p.end_date >= %s and fi.form = any(%s)
          and f.is_derived = false
        order by co.tag, p.start_date, p.end_date, f.is_authoritative desc, f.id desc
        """,
        (cik, sorted(tags), since, list(PERIODIC_FORMS)),
    )
    by_acc = defaultdict(lambda: defaultdict(dict))
    original = {}
    for tag, s, e, v, _auth, acc, por in cur.fetchall():
        by_acc[(s, e)][acc].setdefault(tag, v)
        if por == e:
            original.setdefault((s, e), acc)
    return {key: (original.get(key) or max(accs, key=lambda a: len(accs[a])), accs[original.get(key) or max(accs, key=lambda a: len(accs[a]))])
            for key, accs in by_acc.items()}


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
