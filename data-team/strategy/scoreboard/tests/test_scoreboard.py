"""Unit tests for the scoreboard scripts (stdlib unittest). Run:
  python3 -m unittest discover -s data-team/strategy/scoreboard/tests -v
Each safety check has a mutation test: the check must FAIL on a deliberately broken input.
"""
import csv
import gzip
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import build_scoreboard as B  # noqa: E402
import rt1_reconcile as RT  # noqa: E402
import sampling_frame as SF  # noqa: E402
import sb_lib as L  # noqa: E402


def quiet(fn, *a, **k):
    """call fn with stdout/stderr silenced (the scripts print their reports)"""
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **k)


def write_cells(path: Path, rows):
    """rows: (company_id, data_point, has_value 't'/'f', reason)"""
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["company_id", "data_point_name", "has_value", "gap_reason"])
        w.writerows(rows)


class TestLib(unittest.TestCase):
    def test_pct_half_up_and_empty_denominator(self):
        self.assertEqual(L.pct(123326, 160718), "76.73")
        self.assertEqual(L.pct(1, 8), "12.50")
        self.assertEqual(L.pct(1, 3), "33.33")
        self.assertEqual(L.pct(5, 0), "")          # never a fake 0

    def test_id_hash_is_numeric_sort(self):
        # sorted as strings, 10 < 2; the freeze register uses numeric order
        self.assertNotEqual(L.id_list_hash([10, 2]), L.sha256_bytes(b"10,2")[:16])
        self.assertEqual(L.id_list_hash([10, 2]), L.sha256_bytes(b"2,10")[:16])

    def test_reason_pattern_and_tokens(self):
        self.assertEqual(L.reason_pattern("missing:prior_period(2011_Q1)"), "missing:prior_period(...)")
        self.assertEqual(L.reason_tokens("missing:gross_profit(2025),gross_profit(2024),shares_outstanding(2025)..."),
                         ("missing", ["gross_profit", "gross_profit", "shares_outstanding"], True))
        self.assertEqual(L.reason_tokens("incomplete:numerator")[1], ["numerator"])

    def test_resolve_token(self):
        g = L.load_graph()
        self.assertEqual(L.resolve_token("ebitda_ttm", "ev_ebitda", g), ["ebitda"])
        self.assertEqual(L.resolve_token("ttm_operating_income", "roic", g), ["operating_income"])
        self.assertEqual(L.resolve_token("numerator", "net_margin", g), ["net_income"])
        self.assertEqual(L.resolve_token("denominator", "net_margin", g), ["revenue"])
        self.assertEqual(L.resolve_token("nonsense_name", "net_margin", g), [])

    def test_deterministic_gzip(self):
        d = Path(tempfile.mkdtemp())
        try:
            L.write_gz_deterministic("a,b\n1,2\n", d / "x.gz")
            L.write_gz_deterministic("a,b\n1,2\n", d / "y.gz")
            self.assertEqual((d / "x.gz").read_bytes(), (d / "y.gz").read_bytes())
            self.assertEqual(gzip.open(d / "x.gz").read(), b"a,b\n1,2\n")
        finally:
            shutil.rmtree(d)

    def test_staleness_thresholds_come_from_the_module(self):
        self.assertEqual(L.staleness_thresholds(), (400, 230))
        # mutation: a module without the constants must fail loudly
        d = Path(tempfile.mkdtemp())
        try:
            (d / "s.py").write_text("X = 1\n")
            with self.assertRaises(RuntimeError):
                L.staleness_thresholds(d / "s.py")
        finally:
            shutil.rmtree(d)

    def test_is_stale_boundaries_and_never_hides_unprovable(self):
        a, q = 400, 230
        self.assertFalse(L.is_stale("FY", "2025-01-01", "2026-02-05", a, q))   # 400 days: kept
        self.assertTrue(L.is_stale("FY", "2025-01-01", "2026-02-06", a, q))    # 401: stale
        self.assertFalse(L.is_stale("Q2", "2026-01-01", "2026-08-19", a, q))   # 230: kept
        self.assertTrue(L.is_stale("TTM", "2026-01-01", "2026-08-20", a, q))   # 231
        self.assertFalse(L.is_stale("", "2020-01-01", "2026-01-01", a, q))     # no label
        self.assertFalse(L.is_stale("FY", "", "2026-01-01", a, q))             # no period
        self.assertFalse(L.is_stale("FY", "2020-01-01", "", a, q))             # no reference
        self.assertFalse(L.is_stale("ZZ", "2020-01-01", "2026-01-01", a, q))   # unknown label


class TestExtractAndDiff(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_diff_classes(self):
        write_cells(self.d / "p.csv", [(1, "a", "t", ""), (1, "b", "f", "r1"), (1, "c", "t", ""),
                                       (2, "a", "f", "x"), (2, "b", "t", "")])
        write_cells(self.d / "c.csv", [(1, "a", "t", ""), (1, "b", "t", ""), (1, "c", "f", ""),
                                       (2, "a", "f", "y"), (3, "a", "t", "")])
        got = {k: c for k, c, _, _ in L.diff_extracts(L.Extract(self.d / "p.csv"), L.Extract(self.d / "c.csv"))}
        self.assertEqual(got[(1, "b")], "value_appeared")
        self.assertEqual(got[(1, "c")], "value_disappeared")
        self.assertEqual(got[(2, "a")], "reason_changed")
        self.assertEqual(got[(2, "b")], "company_absent_from_table")
        self.assertEqual(got[(3, "a")], "cell_new")
        self.assertNotIn((1, "a"), got)

    def test_absent_row_never_counts_as_valued(self):
        with open(self.d / "e.csv", "w") as fh:
            fh.write("company_id,data_point_name,has_value,gap_reason,absent_from_table\n1,a,t,,t\n")
        self.assertFalse(L.Extract(self.d / "e.csv").cells[(1, "a")]["has_value"])


class TestClassifier(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.g = L.load_graph()
        self.m = L.load_reason_map()

    def tearDown(self):
        shutil.rmtree(self.d)

    def clf(self, rows):
        write_cells(self.d / "c.csv", rows)
        return L.Classifier(L.Extract(self.d / "c.csv"), self.g, self.m)

    def test_terminal_and_null(self):
        c = self.clf([(1, "goodwill", "f", ""), (1, "inventory", "f", "line_not_presented_in_filing"),
                      (1, "capex", "f", "line_in_filing_not_extracted")])
        self.assertEqual(c.classify(1, "goodwill")[:2], ("unclassified", "triage"))
        self.assertEqual(c.classify(1, "inventory")[:2], ("evidence_pending", "sector_analyst"))
        self.assertEqual(c.classify(1, "capex")[:2], ("vocabulary", "tag_mapper"))

    def test_cascade_inherits_blocker_class(self):
        c = self.clf([(1, "net_margin", "f", "incomplete:denominator"), (1, "revenue", "f", "line_in_filing_not_extracted"),
                      (1, "net_income", "t", "")])
        r = c.classify(1, "net_margin")
        self.assertEqual(r[:2], ("vocabulary", "tag_mapper"))
        self.assertIn("via:revenue", r[3])

    def test_cascade_prefers_defect_over_candidate_legitimate(self):
        # a reason that is in the frozen map and names two inputs
        c = self.clf([(1, "roic", "f", "incomplete:ttm_income_tax_expense,stockholders_equity"),
                      (1, "income_tax_expense", "f", "line_not_presented_in_filing"),
                      (1, "stockholders_equity", "f", "line_in_filing_not_extracted")])
        self.assertEqual(c.classify(1, "roic")[0], "vocabulary")

    def test_cascade_no_blank_input_uses_fallback_not_a_guess(self):
        c = self.clf([(1, "net_margin", "f", "incomplete:numerator"), (1, "net_income", "t", ""), (1, "revenue", "t", "")])
        r = c.classify(1, "net_margin")
        self.assertEqual(r[0], "unclassified")
        self.assertIn("walk_no_blank_input", r[3])

    def test_unmapped_reason_is_reported_not_defaulted(self):
        c = self.clf([(1, "goodwill", "f", "a_reason_nobody_mapped")])
        r = c.classify(1, "goodwill")
        self.assertIn("UNMAPPED_REASON", r[3])
        self.assertEqual(sum(c.unmapped.values()), 1)

    def test_valued_with_reason_is_not_a_blank(self):
        c = self.clf([(1, "ev_sales", "t", "partial:missing_debt_or_cash")])
        self.assertEqual(c.classify(1, "ev_sales")[0], "finding_open")

    def test_every_reason_of_the_export_is_mapped_and_in_the_enums(self):
        ext = L.Extract(L.EXPORT_GZ)
        clf = L.Classifier(ext, self.g, self.m)
        for (cid, dp), cell in ext.cells.items():
            if not cell["has_value"] or cell["reason"]:
                cls, owner, _rf, _n = clf.classify(cid, dp)
                self.assertIn(cls, L.CLASSES)
                self.assertIn(owner, L.OWNERS)
        self.assertEqual(sum(clf.unmapped.values()), 0)


class TestRT1(unittest.TestCase):
    def test_passes_on_the_committed_export(self):
        res = RT.run()
        self.assertEqual([r for r in res if not r["passed"]], [])
        self.assertGreaterEqual(len(res), 50)

    def test_mutation_one_flipped_cell_fails_loudly(self):
        d = Path(tempfile.mkdtemp())
        try:
            text = gzip.open(L.EXPORT_GZ, "rt").read().split("\n")
            # flip the first valued cell to blank (breaks hash, valued, blank, pct ...)
            for i, ln in enumerate(text[1:], 1):
                if ",t," in ln:
                    text[i] = ln.replace(",t,", ",f,", 1)
                    break
            p = d / "m.csv"
            p.write_text("\n".join(text))
            res = RT.run(p)
            failed = {r["check"] for r in res if not r["passed"]}
            self.assertIn("export sha256 (decompressed)", failed)
            self.assertIn("valued", failed)
            self.assertEqual(quiet(RT.main, ["--cells", str(p)]), 1)
        finally:
            shutil.rmtree(d)

    def test_mutation_dropped_row_fails(self):
        d = Path(tempfile.mkdtemp())
        try:
            text = gzip.open(L.EXPORT_GZ, "rt").read().split("\n")
            p = d / "m.csv"
            p.write_text("\n".join(text[:-2]) + "\n")
            failed = {r["check"] for r in RT.run(p) if not r["passed"]}
            self.assertIn("D0 cells", failed)
        finally:
            shutil.rmtree(d)


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.out = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.out)

    def rows(self):
        return list(csv.DictReader(open(self.out / "2026-10-20.csv", newline="")))

    def test_build_from_export_has_the_baseline_and_passes_validation(self):
        self.assertEqual(quiet(B.main, ["--out-dir", str(self.out)]), 0)
        rows = self.rows()
        self.assertEqual(B.validate_rows(rows), [])
        k = {(r["k_id"], r["segment"], r["denominator_id"], r["status"]): r for r in rows}
        r = k[("K1", "all", "D0", "MEASURED")]
        self.assertEqual((r["numerator"], r["denominator"], r["value"]), ("123326", "160718", "76.73"))
        r = k[("K1", "all", "D0e", "MEASURED")]
        self.assertEqual((r["numerator"], r["denominator"], r["value"]), ("98332", "131138", "74.98"))
        self.assertEqual(k[("K2", "all", "D0", "MEASURED")]["value"], "13349")
        self.assertEqual(k[("K2c", "all", "D0", "MEASURED")]["value"], "116")
        self.assertEqual(k[("K7", "all", "D0", "NOT_COMPUTABLE")]["value"], "")
        self.assertEqual(k[("K1c", "all", "D0", "NOT_COMPUTABLE")]["value"], "")
        self.assertEqual(k[("K1c.product_head_proxy", "all", "D0", "REPORTED")]["value"], "73.35")
        self.assertTrue(any(r["k_id"] == "RT-1" and r["value"] == "PASS" for r in rows))
        self.assertEqual(B.verify_manifest(self.out), [])
        # proxy register: row count = blanks + valued-with-reason; no unowned, enums respected
        reg = list(csv.DictReader(gzip.open(self.out / "defects/2026-10-20.defects.csv.gz", "rt")))
        self.assertEqual(len(reg), 37392 + 116)
        self.assertTrue(all(r["defect_class"] in L.CLASSES and r["owner"] in L.OWNERS for r in reg))
        self.assertTrue(all(r["source"] == "proxy" for r in reg))
        # the class counts in the scoreboard equal the register's blank rows by class
        from collections import Counter
        cnt = Counter(r["defect_class"] for r in reg if r["proxy_state"] == "blank")
        for r in rows:
            if r["k_id"] == "K4" and r["segment"].startswith("class:"):
                self.assertEqual(int(r["value"]), cnt.get(r["segment"][6:], 0))
        # unclassified in the proxy == blanks the map could not attribute (>= the reasonless 13,349)
        self.assertGreaterEqual(cnt["unclassified"], 13349)

    def test_refuses_to_overwrite_a_published_scoreboard(self):
        self.assertEqual(quiet(B.main, ["--out-dir", str(self.out)]), 0)
        self.assertEqual(quiet(B.main, ["--out-dir", str(self.out)]), 1)

    def test_erratum_keeps_the_original(self):
        self.assertEqual(quiet(B.main, ["--out-dir", str(self.out)]), 0)
        before = (self.out / "2026-10-20.csv").read_bytes()
        self.assertEqual(quiet(B.main, ["--out-dir", str(self.out), "--erratum", "1", "--reason", "test"]), 0)
        self.assertEqual((self.out / "2026-10-20.csv").read_bytes(), before)
        self.assertTrue((self.out / "2026-10-20.r1.csv").exists())
        self.assertEqual(quiet(B.main, ["--out-dir", str(self.out), "--erratum", "2"]), 1)   # reason mandatory

    def test_mutation_manifest_detects_a_changed_published_file(self):
        quiet(B.main, ["--out-dir", str(self.out)])
        with open(self.out / "2026-10-20.csv", "a") as fh:
            fh.write("tamper\n")
        self.assertEqual(B.verify_manifest(self.out), ["2026-10-20.csv"])
        with self.assertRaises(SystemExit):
            B.manifest_append(self.out, [self.out / "2026-10-20.csv"])

    def test_mutation_rt1_failure_blocks_publication(self):
        d = Path(tempfile.mkdtemp())
        orig = L.D0E_REMOVED_FILE
        try:
            bad = d / "r.txt"
            bad.write_text("revenue\n")          # a wrong removal list breaks D0e equalities
            L.D0E_REMOVED_FILE = bad
            self.assertEqual(quiet(B.main, ["--out-dir", str(self.out)]), 1)
            self.assertFalse((self.out / "2026-10-20.csv").exists())
        finally:
            L.D0E_REMOVED_FILE = orig
            shutil.rmtree(d)

    def test_validate_rows_catches_each_violation(self):
        ok = {"k_id": "K", "k_version": "1", "denominator_id": "D0", "status": "MEASURED", "value": "1",
              "note": "", "query_file": "q", "query_sha256": "h"}
        self.assertEqual(B.validate_rows([ok]), [])
        for mut in ({"value": ""}, {"k_version": ""}, {"denominator_id": ""}, {"status": "BOGUS"},
                    {"status": "NOT_COMPUTABLE", "value": "", "note": ""},
                    {"status": "NOT_COMPUTABLE", "value": "0", "note": "x"}, {"query_file": ""}):
            self.assertTrue(B.validate_rows([{**ok, **mut}]), mut)

    def test_gaming_check(self):
        self.assertTrue(B.gaming_check(100, 200, 110, 200, True)[0])
        self.assertFalse(B.gaming_check(100, 200, 100, 190, True)[0])    # percent up by shrinking denominator only
        self.assertFalse(B.gaming_check(100, 200, 120, 220, False)[0])   # denominator changed, no chain row
        self.assertTrue(B.gaming_check(100, 200, 120, 220, True)[0])

    def test_previous_extract_produces_movement_rows_and_tripwire(self):
        prev = self.out / "prev.csv"
        text = gzip.open(L.EXPORT_GZ, "rt").read().split("\n")
        n = 0
        for i, ln in enumerate(text[1:], 1):          # blank 1000 valued cells in the "previous" extract
            if ",t," in ln and n < 1000:
                text[i] = ln.replace(",t,", ",f,", 1)
                n += 1
        prev.write_text("\n".join(text))
        self.assertEqual(quiet(B.main, ["--out-dir", str(self.out), "--prev-cells", str(prev)]), 0)
        m = {r["k_id"]: r for r in self.rows() if r["section"] == "M"}
        self.assertEqual(m["M.value_appeared"]["value"], "1000")
        self.assertEqual(m["M.tripwire_k1_0.5pt"]["value"], "YES")      # +0.6 points


class TestLivePeriodsPath(unittest.TestCase):
    """The K7/K1c/K1h branch is exercised on a synthetic live-format extract."""

    def test_k7_and_k1c_computed_when_periods_and_reference_exist(self):
        out = Path(tempfile.mkdtemp())
        try:
            ids, _ = L.load_cohort()
            names = L.read_lines(L.D0_NAMES_FILE)
            p = out / "live.csv"
            with open(p, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["company_id", "data_point_name", "data_point_type", "has_value",
                            "has_value_any_period", "gap_reason", "latest_period_end", "latest_label",
                            "absent_from_table"])
                for i, cid in enumerate(ids):
                    for dp in names:
                        if i == 0 and dp == "revenue":
                            w.writerow([cid, dp, "concept", "t", "", "", "2020-12-31", "FY", "f"])   # stale
                        elif i == 0 and dp == "goodwill":
                            w.writerow([cid, dp, "concept", "t", "", "", "2025-12-31", "FY", "f"])   # current
                        elif i == 1 and dp == "gross_margin":
                            w.writerow([cid, dp, "metric", "f", "t", "line_not_presented_in_filing", "", "", "f"])               # hidden blank
                        elif i == 2 and dp == "capex":
                            w.writerow([cid, dp, "concept", "f", "", "", "", "", "t"])               # absent
                        else:
                            w.writerow([cid, dp, "concept", "f", "", "", "", "", "f"])
            ref = out / "ref.csv"
            ref.write_text("company_id,ref_end\n" + f"{ids[0]},2026-06-30\n")
            (out / "o").mkdir()
            self.assertEqual(quiet(B.main, ["--cells", str(p), "--as-of", "2026-11-02", "--ref-end", str(ref),
                                            "--out-dir", str(out / "o")]), 0)
            rows = list(csv.DictReader(open(out / "o/2026-11-02.csv", newline="")))
            k = {(r["k_id"], r["segment"], r["denominator_id"]): r for r in rows}
            self.assertEqual(k[("K7", "all", "D0")]["value"], "1")                 # only the 2020 FY revenue
            self.assertEqual(k[("K1c", "all", "D0")]["numerator"], "1")            # valued 2, minus 1 stale
            self.assertEqual(k[("K1h", "all", "D0")]["value"], "1")
            self.assertEqual(k[("D0.absent_from_table", "all", "D0")]["value"], "1")
        finally:
            shutil.rmtree(out)


class TestSampling(unittest.TestCase):
    def test_deterministic_and_reproducible_by_the_documented_rule(self):
        ext = L.Extract(L.EXPORT_GZ)
        names = set(L.read_lines(L.D0_NAMES_FILE))
        frame = SF.cell_frame(ext, "reasonless", names)
        self.assertEqual(len(frame), 13349)
        a, pool = SF.draw(frame, "123", 40)
        b, _ = SF.draw(frame, "123", 40)
        self.assertEqual(a, b)
        self.assertEqual(pool, 13349)
        import hashlib
        want = sorted(frame, key=lambda k: (hashlib.md5(f"{k[0]}|{k[1]}123".encode()).hexdigest(), k))[:40]
        self.assertEqual(a, want)
        c, _ = SF.draw(frame, "124", 40)
        self.assertNotEqual(a, c)                       # the seed matters

    def test_exclusions_are_honoured(self):
        ext = L.Extract(L.EXPORT_GZ)
        frame = SF.cell_frame(ext, "reasonless", set(L.read_lines(L.D0_NAMES_FILE)))
        first, _ = SF.draw(frame, "9", 40)
        second, pool = SF.draw(frame, "9", 40, exclude=set(first))
        self.assertFalse(set(first) & set(second))
        self.assertEqual(pool, 13349 - 40)

    def test_s4_exclusions_all_sit_in_the_reasonless_frame(self):
        ext = L.Extract(L.EXPORT_GZ)
        _, cohort = L.load_cohort()
        t2id = {r["ticker"]: c for c, r in cohort.items()}
        ex = SF.load_exclusions(L.SB_DIR / "lists/s4_first_draw_exclusions.csv", t2id)
        self.assertEqual(len(ex), 40)
        frame = set(SF.cell_frame(ext, "reasonless", set(L.read_lines(L.D0_NAMES_FILE))))
        self.assertEqual(ex - frame, set())

    def test_group_policy(self):
        groups = {i: "tiny" for i in range(1, 11)}
        groups.update({i: "bank" for i in range(100, 160)})
        groups.update({i: "corporate" for i in range(1000, 1100)})
        groups.update({i: "other_financial" for i in range(2000, 2050)})
        rows = SF.group_frames(groups, "7")
        by = {}
        for r in rows:
            by.setdefault(r["group"], []).append(r)
        self.assertTrue(all(r["reread"] == 1 for r in by["tiny"]))
        self.assertEqual(sum(r["reread"] for r in by["bank"]), 30)
        self.assertEqual(sum(r["reread"] for r in by["corporate"]), 60)
        self.assertEqual(sum(r["reread"] for r in by["other_financial"]), 30)
        self.assertTrue(by["other_financial"][0]["policy"].startswith("DEFAULT"))
        self.assertEqual([r["seed_rank"] for r in by["bank"]], list(range(1, 61)))


class TestLiveRunnerGates(unittest.TestCase):
    def test_plan_only_opens_no_connection_and_authorisation_is_mandatory(self):
        import extract_live as E
        self.assertEqual(quiet(E.main, ["--authorised-by", "t", "--out-dir", "/nonexistent", "--plan-only"]), 0)
        with self.assertRaises(SystemExit):
            quiet(E.main, ["--out-dir", "/nonexistent"])       # --authorised-by missing

    def test_connection_gate_stops_above_the_limit(self):
        import extract_live as E

        class Cur:
            def __init__(s, n): s.n = n
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def execute(s, *a, **k): pass
            def fetchone(s): return (s.n,)

        class Conn:
            def __init__(s, n): s.n = n
            def cursor(s): return Cur(s.n)

        E.Runner(Conn(14), 14, print).gate()                   # 14 is allowed
        with self.assertRaises(E.GateError):
            E.Runner(Conn(15), 14, print).gate()               # 15 stops, no retry

    def test_sql_files_are_read_only_and_the_runner_has_no_write_statement(self):
        import re
        for p in (L.SB_DIR / "sql").glob("*.sql"):
            body = "\n".join(ln for ln in p.read_text().splitlines() if not ln.strip().startswith("--"))
            self.assertFalse(re.search(r"\b(insert|update|delete|alter|drop|create|truncate|grant)\b", body, re.I), p.name)
        src = (L.SCRIPTS / "extract_live.py").read_text()
        code = "\n".join(ln for ln in src.splitlines() if not ln.strip().startswith("#"))
        self.assertNotIn("executemany", code)
        self.assertNotRegex(code, r"cur\.execute\(\s*[\"'](insert|update|delete|alter|drop|create)", )


if __name__ == "__main__":
    unittest.main()
