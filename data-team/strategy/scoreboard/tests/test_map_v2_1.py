"""Tests for reason_class_map v2.1 (Chief's second review a-f). Mutation checks: the v2 map or the old
behaviour must give the other answer."""

import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import make_reason_class_map_v2_1 as G21  # noqa: E402
import reclass_v2_1 as R21  # noqa: E402
import sb_lib as L  # noqa: E402


def mk(tmp: Path, rows):
    p = tmp / "c.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["company_id", "data_point_name", "has_value", "gap_reason"])
        w.writerows(rows)
    return L.Extract(p)


class T(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.g = L.load_graph()
        self.v2 = L.load_reason_map(L.REASON_MAP_V2)
        self.v21 = L.load_reason_map(L.REASON_MAP_V2_1)

    def tearDown(self):
        shutil.rmtree(self.d)

    def c(self, rows, m=None, legacy=False):
        return L.Classifier(
            mk(self.d, rows), self.g, m or self.v21, legacy_bucket=legacy
        )

    def test_published_files_and_generator(self):
        self.assertEqual(
            L.sha256_file(L.REASON_MAP_V2)[:24], "39c905dd5d87f8594c2f96a9"
        )  # v2 untouched
        G21.G.OVERRIDES = G21.OV
        got = G21.G.build(L.EXPORT_GZ)
        have = list(csv.DictReader(open(L.REASON_MAP_V2_1, newline="")))
        self.assertEqual(len(got), len(have))
        for r in have:
            self.assertIn(r["class"], L.CLASSES)
            self.assertIn(r["owner"], L.OWNERS)

    def test_a_gross_margin_fallback_is_unclassified_metric_only_without_candidate(
        self,
    ):
        rows = [
            (1, "margin_expanding_3yr", "f", "missing:fewer_than_3_years_gross_margin"),
            (1, "gross_margin", "t", ""),
        ]
        r = self.c(rows).classify(1, "margin_expanding_3yr")
        self.assertEqual(
            (r.cls, r.owner, r.candidate, r.bucket),
            ("unclassified", "triage", "", "metric_only_fallback"),
        )
        self.assertFalse(r.currency_unknown)
        o = self.c(rows, self.v2).classify(
            1, "margin_expanding_3yr"
        )  # mutation: v2 said period / history_horizon
        self.assertEqual((o.cls, o.candidate), ("period", "history_horizon"))
        # still cascades when gross_margin is blank
        b = self.c(
            [rows[0], (1, "gross_margin", "f", "line_in_filing_not_extracted")]
        ).classify(1, "margin_expanding_3yr")
        self.assertEqual(b.cls, "vocabulary")

    def test_b_prior_period_keeps_class_but_no_history_horizon(self):
        rows = [(1, "revenue_growth_10y_cagr", "f", "missing:prior_period(2016_Q2)")]
        r = self.c(rows).classify(1, "revenue_growth_10y_cagr")
        self.assertEqual((r.cls, r.candidate), ("period", ""))
        o = self.c(rows, self.v2).classify(1, "revenue_growth_10y_cagr")
        self.assertEqual(o.candidate, "history_horizon")

    def test_c_ttm_dividend_and_buyback_fallbacks_carry_second_signal_and_candidate(
        self,
    ):
        for pat, dp, inp in (
            (
                "missing:share_buybacks_ttm",
                "share_repurchases_pct_fcf",
                "share_buybacks",
            ),
            ("missing:dividends_paid_ttm", "dividends_pct_fcf", "dividends_paid"),
            ("missing:dividends_per_share_ttm", "payout_ratio", "dividends_per_share"),
        ):
            rows = [(1, dp, "f", pat), (1, inp, "t", "")]
            r = self.c(rows).classify(1, dp)
            self.assertEqual(
                (r.cls, r.second_signal, r.candidate),
                ("period", "tag_mapper", "evidenced_zero"),
                pat,
            )
            o = self.c(rows, self.v2).classify(1, dp)
            self.assertEqual((o.second_signal, o.candidate), ("", ""), pat)  # mutation
        # when the dividend leaf itself is blank the cell inherits that blocker, not the fallback
        r = self.c(
            [
                (1, "payout_ratio", "f", "missing:dividends_per_share_ttm"),
                (1, "dividends_per_share", "f", "line_in_filing_not_extracted"),
            ]
        ).classify(1, "payout_ratio")
        self.assertEqual(r.cls, "vocabulary")

    def test_d_fcf_ttm_rationale_is_corrected(self):
        row = self.v21[("missing:fcf_ttm", "*")]
        self.assertIn("ANNUAL fcf", row["rationale"])
        self.assertNotIn("ANNUAL fcf", self.v2[("missing:fcf_ttm", "*")]["rationale"])
        self.assertEqual(
            L.resolve_token("fcf_ttm", "dividends_pct_fcf", self.g), ["fcf"]
        )  # the claim in the text is true

    def test_e_immaterial_revenue_base_candidate(self):
        r = self.c([(1, "debtor_days", "f", "immaterial_revenue_base")]).classify(
            1, "debtor_days"
        )
        self.assertEqual(r.candidate, "undefined_by_math")
        self.assertEqual(
            self.c([(1, "debtor_days", "f", "immaterial_revenue_base")], self.v2)
            .classify(1, "debtor_days")
            .candidate,
            "",
        )

    def test_f_currency_is_orthogonal_to_the_class(self):
        # period-class walk fallback with a concept input valued at any period: flag set, class untouched
        rows = [(1, "ebitda_margin", "f", "missing:ebitda_ttm"), (1, "ebitda", "t", "")]
        r = self.c(rows).classify(1, "ebitda_margin")
        self.assertEqual(r.cls, "period")
        self.assertFalse(r.currency_unknown)  # ebitda is a metric input
        rows = [
            (1, "share_repurchases_pct_fcf", "f", "missing:share_buybacks_ttm"),
            (1, "share_buybacks", "t", ""),
        ]
        r = self.c(rows).classify(1, "share_repurchases_pct_fcf")
        self.assertEqual((r.cls, r.currency_unknown, r.bucket), ("period", True, ""))
        # mutation: the legacy classifier only bucketed unclassified cells, so it never flagged this period cell
        rows2 = [
            (1, "net_margin", "f", "incomplete:numerator"),
            (1, "net_income", "t", ""),
            (1, "revenue", "t", ""),
        ]
        leg = self.c(rows2, self.v2, legacy=True).classify(1, "net_margin")
        self.assertEqual((leg.cls, leg.bucket), ("unclassified", "currency_unknown"))
        new = self.c(rows2).classify(1, "net_margin")
        self.assertEqual(
            (new.cls, new.bucket, new.currency_unknown), ("unclassified", "", True)
        )

    def test_published_counts_on_the_export(self):
        ext = L.Extract(L.EXPORT_GZ)
        g = L.load_graph()
        names = set(L.read_lines(L.D0_NAMES_FILE))
        res, clf = R21.classify_blank(ext, g, self.v21, names, False)
        cls, buck, flag = R21.counts(ext, res)
        self.assertEqual(sum(clf.unmapped.values()), 0)
        self.assertEqual(
            (cls["period"], cls["unclassified"], buck["metric_only_fallback"]),
            (6444, 21722, 168),
        )
        self.assertEqual(flag, 6515)
        r2, _ = R21.classify_blank(ext, g, self.v2, names, True)
        c2, b2, _ = R21.counts(ext, r2)
        self.assertEqual(
            (c2["period"], c2["unclassified"], b2["currency_unknown"]),
            (6612, 21554, 4671),
        )  # v2 reproducible

    def test_prior_period_reconciliation_arithmetic(self):
        pp = R21.prior_period_reconciliation(L.Extract(L.EXPORT_GZ))
        self.assertEqual(
            (pp["all"], pp["fy_base"], pp["quarter_label_base"]), (1879, 81, 1798)
        )
        self.assertEqual(pp["all"], pp["fy_base"] + pp["quarter_label_base"])
        self.assertEqual(pp["label_year_le_2014"], 62)

    def test_verifier_queue_order_and_contents(self):
        rows = list(
            csv.DictReader(
                open(L.SB_DIR / "frames/verifier_queue_v2_1_2026-10-20.csv", newline="")
            )
        )
        prios = [int(r["priority"]) for r in rows]
        self.assertEqual(prios, sorted(prios))  # priority 1 first
        p1 = [r for r in rows if r["priority"] == "1"]
        self.assertEqual(len(p1), 116)
        self.assertTrue(
            all(r["gap_reason"] == "partial:missing_debt_or_cash" for r in p1)
        )
        gm = [r for r in rows if r["priority"] == "2"]
        self.assertTrue(all(r["data_point_name"] == "margin_expanding_3yr" for r in gm))
        self.assertGreaterEqual(len(gm), 10)
        self.assertTrue(all(r["evidence_label"] == "DATA-INFERRED" for r in rows))

    def test_manifest_still_verifies(self):
        import build_scoreboard as B

        self.assertEqual(B.verify_manifest(L.SB_DIR), [])


if __name__ == "__main__":
    unittest.main()
