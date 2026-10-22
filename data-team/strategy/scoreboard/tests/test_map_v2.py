"""Tests for reason_class_map_v2 and the classifier fixes (Chief's review of v1, items 1-11).
Each rule has a mutation check: the v1 map or the old behaviour must give the OTHER answer."""

import csv
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import build_scoreboard as B  # noqa: E402
import make_reason_class_map_v2 as G  # noqa: E402
import sb_lib as L  # noqa: E402

V1_SHA = "126ab4dcda4fca7c3939cf18eedcd6cea4be9fe278343a965fd41aca974445b6"


def mk(tmp: Path, rows):
    p = tmp / "c.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["company_id", "data_point_name", "has_value", "gap_reason"])
        w.writerows(rows)
    return L.Extract(p)


class Base(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.g = L.load_graph()
        self.v1 = L.load_reason_map(L.REASON_MAP)
        self.v2 = L.load_reason_map(L.REASON_MAP_V2)

    def tearDown(self):
        shutil.rmtree(self.d)

    def c(self, rows, m=None):
        return L.Classifier(mk(self.d, rows), self.g, m or self.v2)


class TestFamilies(Base):
    def test_family_tokens(self):
        f = lambda dp: L.data_point_family(dp, self.g)  # noqa: E731
        self.assertEqual(f("revenue"), "revenue_row")
        self.assertEqual(f("revenue_sanity_resolved"), "revenue_row")
        self.assertEqual(f("gross_profit_resolved"), "gp_cost_row")
        self.assertEqual(f("operating_income"), "opex_oi_row")
        self.assertEqual(f("revenue_growth_5y_cagr"), "revenue_growth")
        self.assertEqual(f("dps_growth_yoy"), "dps_growth")
        self.assertEqual(f("eps_growth_3y_cagr"), "eps_growth")
        self.assertEqual(f("fcf_per_share"), "den_share_count")
        self.assertEqual(f("institutional_ownership_pct"), "den_share_count")
        self.assertEqual(f("ev_sales"), "den_revenue")
        self.assertEqual(f("payables_days"), "den_cost_of_revenue")
        self.assertEqual(f("goodwill"), "*")

    def test_v2_file_is_what_the_generator_produces_and_in_enums(self):
        rows = G.build(L.EXPORT_GZ)
        with open(L.REASON_MAP_V2, newline="") as fh:
            have = list(csv.DictReader(fh))
        self.assertEqual(len(rows), len(have))
        self.assertEqual(
            {(r["pattern_key"], r["family"]) for r in rows},
            {(r["pattern_key"], r["family"]) for r in have},
        )
        for r in have:
            self.assertIn(r["class"], L.CLASSES)
            self.assertIn(r["owner"], L.OWNERS)

    def test_v1_is_untouched(self):
        self.assertEqual(L.sha256_file(L.REASON_MAP), V1_SHA)

    def test_every_export_reason_maps_under_v2(self):
        ext = L.Extract(L.EXPORT_GZ)
        clf = L.Classifier(ext, self.g, self.v2)
        for (cid, dp), cell in ext.cells.items():
            if cell["reason"] or not cell["has_value"]:
                r = clf.classify(cid, dp)
                self.assertIn(r.cls, L.CLASSES)
                self.assertIn(r.owner, L.OWNERS)
        self.assertEqual(sum(clf.unmapped.values()), 0)


class TestRules(Base):
    def test_item3_sector_income_split_by_line(self):
        for dp, cls, owner in (
            ("gross_profit", "evidence_pending", "sector_analyst"),
            ("cost_of_revenue_resolved", "evidence_pending", "sector_analyst"),
            ("operating_expenses", "definition_pending", "accountant"),
            ("operating_income_resolved", "definition_pending", "accountant"),
            ("revenue", "definition_pending", "accountant"),
        ):
            r = self.c([(1, dp, "f", "bank_interest_income_not_revenue")]).classify(
                1, dp
            )
            self.assertEqual((r.cls, r.owner), (cls, owner), dp)
        # mutation: v1 gave every line evidence_pending / sector_analyst
        r = self.c(
            [(1, "operating_income", "f", "bank_interest_income_not_revenue")], self.v1
        ).classify(1, "operating_income")
        self.assertEqual(r.cls, "evidence_pending")

    def test_item4_implausible_is_guard_hidden_with_resolver_root(self):
        r = self.c(
            [
                (
                    1,
                    "institutional_ownership_pct",
                    "f",
                    "implausible:institutional_shares_exceed_shares_outstanding",
                )
            ]
        ).classify(1, "institutional_ownership_pct")
        self.assertEqual((r.cls, r.root_cause), ("guard_hidden", "resolver"))
        r1 = self.c(
            [
                (
                    1,
                    "institutional_ownership_pct",
                    "f",
                    "implausible:institutional_shares_exceed_shares_outstanding",
                )
            ],
            self.v1,
        ).classify(1, "institutional_ownership_pct")
        self.assertEqual(r1.cls, "resolver")

    def test_item5_zero_denominator_by_data_point(self):
        for dp, cls, owner in (
            ("fcf_per_share", "resolver", "data_engineer_l1"),
            ("ev_sales", "evidence_pending", "sector_analyst"),
            ("inventory_days", "evidence_pending", "sector_analyst"),
            ("eps_dilution_spread", "evidence_pending", "data_engineer_l1"),
        ):
            r = self.c([(1, dp, "f", "zero_denominator")]).classify(1, dp)
            self.assertEqual((r.cls, r.owner), (cls, owner), dp)
        r = self.c([(1, "inventory_days", "f", "zero_denominator")]).classify(
            1, "inventory_days"
        )
        self.assertEqual(r.candidate, "not_in_template")
        r = self.c([(1, "fcf_per_share", "f", "zero_denominator")], self.v1).classify(
            1, "fcf_per_share"
        )
        self.assertEqual(r.cls, "evidence_pending")  # mutation: v1 did not split

    def test_item6_zero_base_by_data_point(self):
        a = self.c([(1, "revenue_growth_yoy", "f", "zero_base_value")]).classify(
            1, "revenue_growth_yoy"
        )
        self.assertEqual((a.owner, a.rf), ("sector_analyst", "RF-38"))
        b = self.c([(1, "dps_growth_yoy", "f", "zero_base_value")]).classify(
            1, "dps_growth_yoy"
        )
        self.assertEqual((b.owner, b.second_signal), ("data_engineer_l1", "tag_mapper"))
        e = self.c([(1, "eps_growth_yoy", "f", "zero_base_value")]).classify(
            1, "eps_growth_yoy"
        )
        self.assertEqual(
            (e.owner, e.candidate), ("data_engineer_l1", "undefined_by_math")
        )
        o = self.c([(1, "eps_growth_yoy", "f", "zero_base_value")], self.v1).classify(
            1, "eps_growth_yoy"
        )
        self.assertEqual(o.owner, "sector_analyst")  # mutation

    def test_item2_prior_period_is_period(self):
        r = self.c(
            [(1, "revenue_growth_10y_cagr", "f", "missing:prior_period(2016_Q2)")]
        ).classify(1, "revenue_growth_10y_cagr")
        self.assertEqual(
            (r.cls, r.owner, r.candidate),
            ("period", "period_engineer", "history_horizon"),
        )
        r1 = self.c(
            [(1, "revenue_growth_10y_cagr", "f", "missing:prior_period(2016_Q2)")],
            self.v1,
        ).classify(1, "revenue_growth_10y_cagr")
        self.assertEqual(r1.cls, "evidence_pending")

    def test_item7_fewer_than_3_years_cascades_through_gross_margin(self):
        r = self.c(
            [
                (
                    1,
                    "margin_expanding_3yr",
                    "f",
                    "missing:fewer_than_3_years_gross_margin",
                ),
                (1, "gross_margin", "f", "line_in_filing_not_extracted"),
            ]
        ).classify(1, "margin_expanding_3yr")
        self.assertEqual(r.cls, "vocabulary")
        self.assertIn("via:gross_margin", r.note)
        r2 = self.c(
            [
                (
                    1,
                    "margin_expanding_3yr",
                    "f",
                    "missing:fewer_than_3_years_gross_margin",
                ),
                (1, "gross_margin", "t", ""),
            ]
        ).classify(1, "margin_expanding_3yr")
        self.assertEqual(r2.cls, "period")  # fallback only when gross_margin is valued
        self.assertEqual(
            L.resolve_token(
                "fewer_than_3_years_gross_margin", "margin_expanding_3yr", self.g
            ),
            ["gross_margin"],
        )

    def test_item8_share_count_1y_ago_does_not_look_at_current_shares(self):
        self.assertEqual(
            L.resolve_token("share_count_1y_ago", "share_dilution_trend", self.g), []
        )
        rows = [
            (1, "share_dilution_trend", "f", "missing:share_count_1y_ago"),
            (1, "shares_outstanding", "f", "line_in_filing_not_extracted"),
        ]  # current shares blank+vocabulary
        r = self.c(rows).classify(1, "share_dilution_trend")
        self.assertEqual(
            (r.cls, r.owner), ("period", "period_engineer")
        )  # mutation: the alias would give vocabulary

    def test_item9_owner_fixes(self):
        for pat, dp in (
            ("negative_ratio_undefined_cagr", "eps_growth_5y_cagr"),
            ("non_positive_growth_not_meaningful", "peg_ratio"),
            ("immaterial_prior_base", "net_income_growth_3y_cagr"),
            ("zero_denominator", "eps_dilution_spread"),
        ):
            r = self.c([(1, dp, "f", pat)]).classify(1, dp)
            self.assertEqual(r.owner, "data_engineer_l1", pat)
            r1 = self.c([(1, dp, "f", pat)], self.v1).classify(1, dp)
            self.assertEqual(r1.owner, "sector_analyst", pat)

    def test_item10_no_dividend_history_second_signal_and_partial_debt(self):
        r = self.c(
            [(1, "dividend_growth_streak_years", "f", "no_dividend_history")]
        ).classify(1, "dividend_growth_streak_years")
        self.assertEqual(r.second_signal, "tag_mapper")
        rows = [
            (1, "ev_sales", "t", "partial:missing_debt_or_cash"),
            (1, "total_debt_resolved", "f", ""),
            (1, "cash_and_equivalents", "t", ""),
        ]
        p = self.c(rows).classify(1, "ev_sales")
        self.assertTrue(p.excl_k1c)
        self.assertIn("missing_input:total_debt_resolved", p.note)
        self.assertNotIn("cash_and_equivalents", p.note.split("missing_input:")[1])

    def test_item11_input_with_no_row_is_not_valued(self):
        rows = [
            (1, "net_margin", "f", "incomplete:denominator"),
            (1, "net_income", "t", ""),
        ]  # revenue has NO row
        r = self.c(rows).classify(1, "net_margin")
        self.assertIn("revenue:no_row", r.note)
        self.assertNotIn(
            "walk_no_blank_input", r.note
        )  # old behaviour: counted as valued, fell back
        self.assertTrue(r.note.startswith("via:revenue"))

    def test_item1_notes_and_currency_unknown_bucket(self):
        rows = [
            (1, "net_margin", "f", "incomplete:numerator"),
            (1, "net_income", "t", ""),
            (1, "revenue", "t", ""),
        ]
        r = self.c(rows).classify(1, "net_margin")
        self.assertIn("net_income:valued_any_period", r.note)
        self.assertNotIn("valued_latest", r.note)
        self.assertEqual(r.cls, "unclassified")
        self.assertTrue(r.currency_unknown)  # v2.1: an orthogonal flag, not a bucket
        leg = L.Classifier(mk(self.d, rows), self.g, self.v2, legacy_bucket=True)
        self.assertEqual(leg.classify(1, "net_margin").bucket, "currency_unknown")
        # a metric input is valued_latest and leaves no currency doubt
        rows = [
            (1, "cash_conversion_cycle", "f", "incomplete:add"),
            (1, "debtor_days", "t", ""),
            (1, "inventory_days", "t", ""),
        ]
        r2 = self.c(rows).classify(1, "cash_conversion_cycle")
        self.assertIn("debtor_days:valued_latest", r2.note)
        self.assertNotEqual(r2.bucket, "currency_unknown")


class TestK1cAndManifest(Base):
    def test_k1c_excludes_valued_with_reason(self):
        out = Path(tempfile.mkdtemp())
        try:
            ids, _ = L.load_cohort()
            names = L.read_lines(L.D0_NAMES_FILE)
            p = out / "live.csv"
            with open(p, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(
                    [
                        "company_id",
                        "data_point_name",
                        "data_point_type",
                        "has_value",
                        "has_value_any_period",
                        "gap_reason",
                        "latest_period_end",
                        "latest_label",
                        "absent_from_table",
                    ]
                )
                for cid in ids:
                    for dp in names:
                        if cid == ids[0] and dp == "goodwill":
                            w.writerow(
                                [
                                    cid,
                                    dp,
                                    "concept",
                                    "t",
                                    "",
                                    "",
                                    "2025-12-31",
                                    "FY",
                                    "f",
                                ]
                            )
                        elif cid == ids[0] and dp == "ev_sales":
                            w.writerow(
                                [
                                    cid,
                                    dp,
                                    "metric",
                                    "t",
                                    "t",
                                    "partial:missing_debt_or_cash",
                                    "2026-03-31",
                                    "TTM",
                                    "f",
                                ]
                            )
                        else:
                            w.writerow([cid, dp, "concept", "f", "", "", "", "", "f"])
            ref = out / "ref.csv"
            ref.write_text(f"company_id,ref_end\n{ids[0]},2026-06-30\n")
            (out / "o").mkdir()
            rc = (
                B.main(
                    [
                        "--cells",
                        str(p),
                        "--as-of",
                        "2026-11-02",
                        "--ref-end",
                        str(ref),
                        "--out-dir",
                        str(out / "o"),
                    ]
                )
                if False
                else None
            )
            import contextlib

            with contextlib.redirect_stdout(io.StringIO()):
                rc = B.main(
                    [
                        "--cells",
                        str(p),
                        "--as-of",
                        "2026-11-02",
                        "--ref-end",
                        str(ref),
                        "--out-dir",
                        str(out / "o"),
                    ]
                )
            self.assertEqual(rc, 0)
            rows = list(csv.DictReader(open(out / "o/2026-11-02.csv", newline="")))
            k = {(r["k_id"], r["segment"], r["denominator_id"]): r for r in rows}
            self.assertEqual(
                k[("K1c", "all", "D0")]["numerator"], "1"
            )  # 2 valued - 1 with a reason
            self.assertEqual(k[("K7", "all", "D0")]["value"], "0")
            self.assertEqual(
                k[("K4", "bucket:metric_only_fallback", "D0")]["k_version"],
                "proxy@2.1",
            )
        finally:
            shutil.rmtree(out)

    def test_chain_may_grow_but_published_text_may_not_change(self):
        out = Path(tempfile.mkdtemp())
        try:
            (out / "CHAIN.md").write_text("# h\n\n## 2026-10-20\n\nrow\n\n")
            self.assertEqual(B.manifest_append(out, [out / "CHAIN.md"]), 1)
            with open(out / "CHAIN.md", "a") as fh:
                fh.write("## second\n\nmore\n")
            self.assertEqual(
                B.manifest_append(out, [out / "CHAIN.md"]), 1
            )  # appending is fine
            self.assertEqual(B.verify_manifest(out), [])
            (out / "CHAIN.md").write_text(
                (out / "CHAIN.md").read_text().replace("row", "ROW")
            )
            self.assertEqual(
                B.verify_manifest(out), ["CHAIN.md"]
            )  # mutation: edit detected
            with self.assertRaises(SystemExit):
                B.manifest_append(out, [out / "CHAIN.md"])
        finally:
            shutil.rmtree(out)

    def test_committed_manifest_verifies(self):
        self.assertEqual(B.verify_manifest(L.SB_DIR), [])


if __name__ == "__main__":
    unittest.main()
