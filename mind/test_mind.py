"""Run from inside mind/: python3 -m unittest test_mind"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mind  # noqa: E402


def entry(eid, title, body, **kw):
    return {"id": eid, "title": title, "kind": "lesson", "evidence": "CODE-CHECKED", "tags": kw.get("tags", []),
            "paths": kw.get("paths", []), "created": "2026-01-01", "verified": "2026-01-01", "body": body, "status": "active"}


class MindTests(unittest.TestCase):
    def test_rank_prefers_title_and_tag_matches(self):
        a = entry("a", "Bank revenue must be NII plus noninterest", "Citigroup Revenues is net of interest expense", tags=["bank"])
        b = entry("b", "Pooler connection ceiling", "bank is mentioned once in passing here")
        top = mind.rank("bank revenue", [a, b])[0][1]
        self.assertEqual(top["id"], "a")

    def test_no_match_returns_empty(self):
        self.assertEqual(mind.rank("zzzz", [entry("a", "x y", "foo bar")]), [])

    def test_dump_parse_roundtrip(self):
        e = entry("a", "T", "Body text", tags=["x", "y"], paths=["mind/mind.py"])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.md"
            p.write_text(mind.dump(e))
            back = mind.parse(p)
        self.assertEqual((back["id"], back["tags"], back["paths"], back["body"]), ("a", ["x", "y"], ["mind/mind.py"], "Body text"))

    def test_duplicate_detected(self):
        a = entry("a", "Never sum institutional and mutual fund ownership", "A fund can appear in both 13F and N-PORT")
        b = entry("b", "Never sum institutional and mutual fund ownership %", "A fund can appear in both 13F and N-PORT filings")
        c = entry("c", "Unrelated", "Totally different subject about pooler connections")
        self.assertGreaterEqual(mind.jaccard(a, b), mind.DUP_JACCARD)
        self.assertLess(mind.jaccard(a, c), mind.DUP_JACCARD)

    def test_score_needs_signals_and_reweights(self):
        s = [{"n": 1}] * 4 + [{"n": 0}] * 4
        self.assertEqual(mind.compute_score(s[:3], [], [], [])[0], None)
        score, comp, _ = mind.compute_score(s, [], [], [])
        self.assertEqual((score, list(comp)), (50, ["hit_rate"]))
        r = [{"rating": 5}] * 5 + [{"rating": 0}] * 3
        _, comp, adoption = mind.compute_score(s, [], [], r)
        self.assertEqual(adoption, (5, 8))
        self.assertAlmostEqual(comp["session_rating"][0], 1.0)

    def test_unused_sessions_never_penalise(self):
        r = [{"rating": 0}] * 10
        self.assertIsNone(mind.compute_score([], [], [], r)[0])


if __name__ == "__main__":
    unittest.main()
