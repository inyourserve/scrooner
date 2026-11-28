"""Current versions a company's served cells are compared against (the catch-up sweep, PIPELINE.md section 3).

Per company: the proof DETECTOR_VERSION, a hash of the company's resolver rows (resolver_version ignored, exactly the
diff rule of scripts/ci/top100_changed.py, so a pure version bump re-runs nothing) and a hash of the filings loaded for
it in fsn.filing. Each is read-only and cheap: files plus ONE batched query for the whole cohort.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROVE = "pipeline/src/scrooner_pipeline/proof/prove.py"
LINE_MAP = "data-team/tags/line_map"


def detector_version(root: Path = ROOT) -> str:
    m = re.search(
        r'^DETECTOR_VERSION\s*=\s*"([^"]+)"', (root / PROVE).read_text(), re.M
    )
    if not m:
        raise RuntimeError("DETECTOR_VERSION not found in proof/prove.py")
    return m.group(1)


def resolver_rows_sha(ticker: str, root: Path = ROOT) -> str:
    """sha256 of the company's resolver + rules rows without the resolver_version column ('none' when it has no file)."""
    h, seen = hashlib.sha256(), False
    for rel in (f"{LINE_MAP}/resolver/{ticker}.csv", f"{LINE_MAP}/{ticker}.csv"):
        p = root / rel
        if not p.is_file():
            continue
        seen = True
        rows = []
        for r in csv.DictReader(io.StringIO(p.read_text(encoding="utf-8"))):
            rows.append(
                tuple((k, v) for k, v in sorted(r.items()) if k != "resolver_version")
            )
        h.update(rel.encode())
        h.update(repr(sorted(rows)).encode())
    return h.hexdigest()[:16] if seen else "none"


def filings_sha(conn, ciks: list[str]) -> dict[str, str]:
    conn.execute("set statement_timeout = '120s'")
    rows = conn.execute(
        "select cik, array_agg(accession order by accession) from fsn.filing where cik = any(%s) group by cik",
        (ciks,),
    ).fetchall()
    out = {c: "none" for c in ciks}
    for cik, accs in rows:
        out[cik] = hashlib.sha256("|".join(accs).encode()).hexdigest()[:16]
    return out


def current(conn, members, root: Path = ROOT) -> dict[str, dict[str, str]]:
    """cik -> versions dict for every cohort member."""
    det = detector_version(root)
    fs = filings_sha(conn, [m.cik for m in members])
    return {
        m.cik: {
            "detector": det,
            "resolver_rows": resolver_rows_sha(m.ticker, root),
            "filings": fs[m.cik],
        }
        for m in members
    }
