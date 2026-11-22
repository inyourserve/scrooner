"""Every tool's sec.gov request goes through the one machine-wide SEC budget (sec_pace -> common/sec_rate.py), never a
private sleep: the limiter is called once per request and the ceiling is the repo's 2 req/s."""
import importlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sec_pace  # noqa: E402


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _spy(monkeypatch):
    calls = []
    monkeypatch.setattr(sec_pace, "wait", lambda: calls.append(1))
    import urllib.request

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=0: _Resp(b"<xml/>"))
    return calls


def test_ceiling_is_the_repo_rule():
    assert sec_pace.CEILING == 2.0
    assert sec_pace.sec_rate.limiter(50)._min_interval == 0.5


def test_instance_evidence_paces_through_the_shared_budget(monkeypatch):
    monkeypatch.setenv("SEC_USER_AGENT", "Scrooner test test@example.com")
    ie = importlib.import_module("instance_evidence")
    calls = _spy(monkeypatch)
    assert ie._get("https://www.sec.gov/Archives/x") == "<xml/>"
    assert calls == [1]


def test_text_disclosure_paces_through_the_shared_budget(monkeypatch):
    monkeypatch.setenv("SEC_USER_AGENT", "Scrooner test test@example.com")
    td = importlib.import_module("text_disclosure")
    monkeypatch.setattr(td, "UA", "Scrooner test test@example.com")
    calls = _spy(monkeypatch)
    assert td.get("https://www.sec.gov/Archives/y") == "<xml/>"
    assert calls == [1]


def test_sec_pace_cli_is_the_shared_fetch(monkeypatch, tmp_path):
    """`python3 -I sec_pace.py fetch URL OUT` = sec_rate.main: one budget wait per request, cache on rerun."""
    calls = []
    monkeypatch.setattr(sec_pace.sec_rate, "wait", lambda: calls.append(1))
    monkeypatch.setenv("SEC_USER_AGENT", "Scrooner test test@example.com")
    import urllib.request

    def fake(req, timeout=0):
        r = _Resp(b"<xml/>")
        r.headers = {}
        return r

    monkeypatch.setattr(urllib.request, "urlopen", fake)
    out = tmp_path / "f.xml"
    assert sec_pace.sec_rate.main(["fetch", "https://www.sec.gov/Archives/z", str(out)]) == 0
    assert sec_pace.sec_rate.main(["fetch", "https://www.sec.gov/Archives/z", str(out)]) == 0
    assert out.read_bytes() == b"<xml/>" and calls == [1]
    assert sec_pace.fetch("https://www.sec.gov/Archives/z2") == b"<xml/>" and calls == [1, 1]
