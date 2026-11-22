"""Static guard (SYSTEMS.md #1): no module under pipeline/src, pipeline/scripts, scripts or data-team fetches sec.gov
without the ONE machine-wide budget (common/sec_rate.py, 2 req/s in total; founder 2026-11-17). A file that names a
sec.gov host and opens an HTTP connection (urllib, requests, httpx, http.client, curl/wget subprocess) must route its
requests through sec_rate / sec_pace (or the clients built on it: SECClient, EdgarClient). A private sleep loop is not
a limiter. Tests (test_*.py, conftest.py) are exempt: they mock the network."""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOTS = ("pipeline/src", "pipeline/scripts", "scripts", "data-team")
SKIP_DIRS = {".venv", "node_modules", "__pycache__", ".cache", ".runs"}
LIMITER = (
    REPO / "pipeline/src/scrooner_pipeline/common/sec_rate.py"
)  # the budget itself

SEC_HOST = re.compile(r"(?:www|data|efts)\.sec\.gov|\bsec\.gov/")
FETCH = re.compile(
    r"urlopen\s*\(|\brequests\.(?:get|post|head|request|Session)\s*\("
    r"|\bhttpx\.(?:get|post|head|stream|request|Client|AsyncClient)\s*\("
    r"|\bhttp\.client\b|\burllib3\b|[\"'](?:curl|wget)[\"']|\bcurl\s+-"
)
ROUTED = re.compile(
    r"\bsec_rate\.(?:wait|limiter|fetch|fetch_to)\s*\(|\bsec_pace\.(?:wait|fetch)\s*\("
    r"|\bSECClient\s*\(|\bEdgarClient\s*\("
)


def _sources():
    for root in ROOTS:
        base = REPO / root
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if SKIP_DIRS.intersection(path.relative_to(REPO).parts):
                continue
            if path.name.startswith("test_") or path.name == "conftest.py":
                continue
            if path == LIMITER:
                continue
            yield path


PRIVATE_LIMITER = re.compile(r"scrooner_sec_rate_limiter\.lock")


def unrouted(paths):
    """Files that fetch a sec.gov URL without calling the shared limiter, or that build their own limiter on the
    SEC lock file (own rate, bypassing the 2 req/s clamp of sec_rate.limiter)."""
    bad = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        if SEC_HOST.search(text) and FETCH.search(text) and not ROUTED.search(text):
            bad.append(path)
        elif PRIVATE_LIMITER.search(text):
            bad.append(path)
    return bad


def test_every_sec_gov_fetcher_goes_through_the_shared_limiter():
    bad = [str(p.relative_to(REPO)) for p in unrouted(_sources())]
    assert not bad, (
        "sec.gov fetched without common/sec_rate.py (use sec_rate.wait()/sec_rate.fetch(), "
        "sec_pace.wait() for data-team tools, or SECClient/EdgarClient): "
        + ", ".join(sorted(bad))
    )


def test_the_guard_catches_a_private_sleep_loop(tmp_path):
    raw = tmp_path / "raw.py"
    raw.write_text(
        "import time, urllib.request\n"
        "def get(u):\n"
        "    time.sleep(0.25)\n"
        "    return urllib.request.urlopen('https://www.sec.gov/' + u).read()\n"
    )
    curl = tmp_path / "curl.py"
    curl.write_text(
        "import subprocess\n"
        "subprocess.run(['curl', '-s', 'https://data.sec.gov/submissions/x.json'])\n"
    )
    ok = tmp_path / "ok.py"
    ok.write_text(
        "import urllib.request\n"
        "from scrooner_pipeline.common import sec_rate\n"
        "def get(u):\n"
        "    sec_rate.wait()\n"
        "    return urllib.request.urlopen('https://www.sec.gov/' + u).read()\n"
    )
    own = tmp_path / "own.py"
    own.write_text(
        "from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter\n"
        "LIM = CrossProcessRateLimiter(4.0, '/tmp/scrooner_sec_rate_limiter.lock')\n"
    )
    other = tmp_path / "other.py"
    other.write_text(
        "import httpx\nhttpx.post('https://example.supabase.co/storage')\n"
    )
    assert unrouted([raw, curl, own, ok, other]) == [raw, curl, own]


def test_the_guard_scans_the_known_fetchers():
    names = {str(p.relative_to(REPO)) for p in _sources()}
    for must in (
        "pipeline/scripts/per_share/eps_face_read.py",
        "pipeline/scripts/slot_records/common.py",
        "pipeline/src/scrooner_pipeline/common/sec_client.py",
        "data-team/tags/line_map/tools/instance_evidence.py",
    ):
        assert must in names
