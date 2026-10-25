"""Instance reader: values of CUSTOM (and any other) tags straight from the
filing's own XBRL instance, for slot members the SEC companyfacts API never
carries (stdlib, run with -I).

Per filing: read the folder index (1 request), download the inline-XBRL
instance `*_htm.xml` (1 request), keep only facts whose context has NO
dimensions and whose entity is the filer, and write one evidence row per
(tag, period, unit). The download is deleted after extraction. Nothing is
written to the database; the evidence JSONL feeds the replay, which fills
`needs_instance_reader` cells from it under the same-accession rule.

sec.gov only, SEC_USER_AGENT from the environment (pipeline/.env), <= 4
requests/second, one process, stops when free disk < 4 GB.
usage: instance_reader.py <targets.txt: "cik adsh [tag,tag,...]" per line> <out.jsonl> [limit]
  with no tag list every undimensioned fact of the filing is kept.
"""
import json
import os
import re
import shutil
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = os.environ.get("SEC_USER_AGENT")
if not UA:
    sys.exit("SEC_USER_AGENT missing (source pipeline/.env)")
TMP = Path(sys.argv[2]).parent / "_instance_tmp"
TMP.mkdir(parents=True, exist_ok=True)
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9

XBRLI = "{http://www.xbrl.org/2003/instance}"
XBRLDI = "{http://xbrl.org/2006/xbrldi}"
requests = 0
last = 0.0


def get(url):
    global requests, last
    if shutil.disk_usage("/private/tmp").free < 4 * 1024**3:
        sys.exit(f"free disk < 4 GB after {requests} requests; stopping")
    wait = 0.26 - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
    last = time.monotonic()
    requests += 1
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            import gzip
            data = gzip.decompress(data)
        return data


def parse_instance(path, cik, wanted):
    """-> list of fact dicts from undimensioned, filer-entity contexts."""
    root = ET.parse(path).getroot()
    contexts = {}
    for c in root.iter(XBRLI + "context"):
        ent = c.find(XBRLI + "entity")
        ident = ent.find(XBRLI + "identifier") if ent is not None else None
        if ident is None or int(re.sub(r"\D", "", ident.text or "0") or 0) != int(cik):
            continue
        seg = ent.find(XBRLI + "segment")
        if seg is not None and list(seg):
            continue  # dimensioned context: not the consolidated face value
        per = c.find(XBRLI + "period")
        inst = per.find(XBRLI + "instant")
        if inst is not None:
            contexts[c.get("id")] = ("instant", inst.text.strip(), inst.text.strip())
        else:
            s, e = per.find(XBRLI + "startDate"), per.find(XBRLI + "endDate")
            contexts[c.get("id")] = ("duration", s.text.strip(), e.text.strip())
    units = {}
    for u in root.iter(XBRLI + "unit"):
        m = u.find(XBRLI + "measure")
        units[u.get("id")] = (m.text.split(":")[-1] if m is not None and m.text else None)
    out = []
    for el in root:
        if el.tag.startswith(XBRLI) or "}" not in el.tag:
            continue
        ns, local = el.tag[1:].split("}")
        ctx = el.get("contextRef")
        if ctx not in contexts:
            continue
        prefix = ns.rsplit("/", 1)[-1]
        if wanted and local not in wanted:
            continue
        if el.get("{http://www.w3.org/2001/XMLSchema-instance}nil") == "true":
            value = None
        else:
            value = (el.text or "").strip()
        ptype, start, end = contexts[ctx]
        out.append({
            "tag": local, "namespace": ns, "custom": "fasb.org/us-gaap" not in ns and "fasb.org/srt" not in ns
            and "xbrl.sec.gov/dei" not in ns,
            "period_type": ptype, "start": start, "end": end,
            "value": value, "decimals": el.get("decimals"), "unit": units.get(el.get("unitRef")),
            "context": ctx,
        })
    return out


done = fetched = failed = 0
with open(sys.argv[2], "a") as out:
    for line in open(sys.argv[1]):
        if done >= limit:
            break
        parts = line.split()
        if len(parts) < 2:
            continue
        cik, adsh = parts[0], parts[1]
        wanted = set(parts[2].split(",")) if len(parts) > 2 else set()
        done += 1
        folder = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/"
        try:
            names = [i["name"] for i in json.loads(get(folder + "index.json"))["directory"]["item"]]
            inst = next((n for n in names if n.endswith("_htm.xml")), None)
            if inst is None:  # pre-inline filings: the instance is <prefix>-<date>.xml
                xsd = next((n for n in names if n.endswith(".xsd")), None)
                inst = xsd[:-4] + ".xml" if xsd and xsd[:-4] + ".xml" in names else None
            if inst is None:
                failed += 1
                print("NO_INSTANCE", adsh, flush=True)
                continue
            local = TMP / inst
            local.write_bytes(get(folder + inst))
            facts = parse_instance(local, cik, wanted)
            local.unlink()  # downloads are deleted after use
            for f in facts:
                f.update({"cik": cik, "adsh": adsh, "source": "instance_reader", "instance": inst})
                out.write(json.dumps(f) + "\n")
            fetched += 1
            print(f"{adsh} facts {len(facts)}", flush=True)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL", adsh, type(e).__name__, str(e)[:100], flush=True)
print(f"attempted {done} read {fetched} failed {failed} requests {requests}")
