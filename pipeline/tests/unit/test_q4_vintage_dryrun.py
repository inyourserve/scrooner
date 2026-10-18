"""Unit tests for normalizer/q4_vintage_dryrun.py (synthetic rows only; no DB)."""

import json
from datetime import date
from decimal import Decimal

from scrooner_pipeline.normalizer import q4_vintage_dryrun as q
from scrooner_pipeline.normalizer.q4_vintage_dryrun import Fact, Tolerance, evaluate_cell

D = Decimal
EXACT = Tolerance(rel=D(0), abs_tol=D(0))
LOOSE = Tolerance(rel=D(0), abs_tol=D(2))  # supplied by the caller in tests

FY_START, FY_END = date(2024, 1, 1), date(2024, 12, 31)
YTD_END = date(2024, 9, 30)

_next_id = [0]


def fact(value, acc, filed, start, end, fp, auth=True, unit="USD", derived=False):
    _next_id[0] += 1
    return Fact(
        _next_id[0],
        D(str(value)),
        acc,
        filed,
        start,
        end,
        auth,
        fp,
        unit,
        derived,
    )


def fy(value, acc="10K-A", filed=date(2025, 2, 20), auth=True, start=FY_START, end=FY_END):
    return fact(value, acc, filed, start, end, "FY", auth)


def ytd9(value, acc="10Q3-A", filed=date(2024, 11, 5), auth=True, start=FY_START, end=YTD_END):
    return fact(value, acc, filed, start, end, None, auth)


def run(facts, tol=EXACT, **kw):
    kw.setdefault("additive", True)
    return evaluate_cell(facts, company_id=1, concept_id=2, tol=tol, **kw)


# ---------------------------------------------------------------- clean


def test_clean_nine_month():
    c = run([fy(1000), ytd9(700)])
    assert c.category == q.CLEAN
    assert c.q4_value == D(300)
    assert c.formula_id == q.FORMULA_YTD9
    assert c.q4_start == date(2024, 10, 1) and c.q4_end == FY_END
    assert c.arithmetic == "1000 - 700 = 300"
    assert c.vintage_basis == "unrestated_single_value"
    assert c.fy_accessions == ["10K-A"] and c.ytd_accessions == ["10Q3-A"]
    assert c.block_reason is None


def test_clean_chain_when_no_nine_month():
    q1 = fact(200, "Q1", date(2024, 5, 1), date(2024, 1, 1), date(2024, 3, 31), "Q1")
    q2 = fact(250, "Q2", date(2024, 8, 1), date(2024, 4, 1), date(2024, 6, 30), "Q2")
    q3 = fact(250, "Q3", date(2024, 11, 1), date(2024, 7, 1), date(2024, 9, 30), "Q3")
    c = run([fy(1000), q1, q2, q3])
    assert c.category == q.CLEAN
    assert c.formula_id == q.FORMULA_CHAIN
    assert c.q4_value == D(300)
    assert c.arithmetic == "1000 - (200 + 250 + 250) = 300"
    assert c.ytd_fact_ids == [q1.fact_id, q2.fact_id, q3.fact_id]


def test_negative_q4_is_allowed_for_additive_flows():
    c = run([fy(100), ytd9(160)])
    assert c.category == q.CLEAN and c.q4_value == D(-60)


def test_costco_16_week_fiscal_q4():
    start, end = date(2024, 9, 2), date(2025, 8, 31)  # 52 weeks
    ytd_end = date(2025, 5, 11)  # 36 weeks = 252 days, Q4 = 112 days
    c = run(
        [
            fact(275235, "COST-10K", date(2025, 10, 8), start, end, "FY"),
            fact(190000, "COST-Q3", date(2025, 6, 4), start, ytd_end, None),
        ]
    )
    assert c.category == q.CLEAN
    assert c.q4_start == date(2025, 5, 12)
    assert (c.q4_end - c.q4_start).days == 111  # 112 inclusive days
    assert c.q4_value == D(85235)


def test_costco_pattern_blocked_if_remainder_band_too_narrow():
    start, end = date(2024, 9, 2), date(2025, 8, 31)
    c = run(
        [
            fact(100, "K", date(2025, 10, 8), start, end, "FY"),
            fact(60, "Q", date(2025, 6, 4), start, date(2025, 5, 11), None),
        ],
        q4_max_days=100,
    )
    assert c.category == q.BLOCKED_NO_YTD


# ---------------------------------------------------- rounding / tolerance


def test_rounding_only_copies_are_same_vintage_under_supplied_tolerance():
    c = run(
        [
            fy(1000, "10K-A", date(2025, 2, 20), auth=False),
            fy(1001, "10K-B", date(2025, 3, 5), auth=False),
            ytd9(700),
        ],
        tol=LOOSE,
    )
    assert c.category == q.SAME_VINTAGE
    assert c.fy_value == D(1001)  # latest-filed copy, as the resolver does
    assert c.q4_value == D(301)


def test_same_rounding_difference_blocks_when_tolerance_is_zero():
    c = run(
        [
            fy(1000, "10K-A", date(2025, 2, 20), auth=False),
            fy(1001, "10K-B", date(2025, 3, 5), auth=False),
            ytd9(700),
        ],
        tol=EXACT,
    )
    # two FY clusters, the 9M never re-filed after the later one: not evidenced
    assert c.category == q.BLOCKED_MIXED


def test_tolerance_is_required_no_default():
    import inspect

    sig = inspect.signature(evaluate_cell)
    assert sig.parameters["tol"].default is inspect.Parameter.empty


# ------------------------------------------------------- restatement/vintage


def test_restated_fy_with_original_ytd_blocks():
    c = run(
        [
            fy(1000, "10K-ORIG", date(2025, 2, 20)),
            fy(900, "10K-RESTATED", date(2026, 2, 20)),
            ytd9(700),  # filed 2024-11, never restated, not re-filed
        ]
    )
    assert c.category == q.BLOCKED_MIXED
    assert c.block_reason.startswith("ytd9:valid_pairing_exists_only_for_superseded_fy_value")
    assert c.q4_value is None
    # the legitimate as-filed pair is reported but not selected
    assert any(
        a["vintage_basis"] == "as_filed_original" and a["q4_value"] == D(300)
        for a in c.alternatives
    )


def test_allow_flag_accepts_as_filed_pair_but_marks_it_superseded():
    c = run(
        [fy(1000, "10K-ORIG", date(2025, 2, 20)), fy(900, "10K-R", date(2026, 2, 20)), ytd9(700)],
        allow_non_latest_fy_vintage=True,
    )
    assert c.category == q.SAME_VINTAGE
    assert c.vintage_basis == "as_filed_original"
    assert c.q4_value == D(300)
    assert c.fy_is_latest_vintage is False
    assert "fy_value_is_superseded_by_a_later_filing" in c.notes


def test_ytd_reconfirmed_after_restated_fy_is_same_vintage():
    c = run(
        [
            fy(1000, "10K-ORIG", date(2025, 2, 20)),
            fy(900, "10K-R", date(2025, 8, 1)),
            ytd9(700, "10Q3", date(2024, 11, 5)),
            ytd9(700, "10Q3-comp", date(2025, 11, 5)),  # same value re-filed later
        ]
    )
    assert c.category == q.SAME_VINTAGE
    assert c.vintage_basis == "reconfirmed_after"
    assert c.q4_value == D(200)
    assert c.fy_is_latest_vintage is True


def _both_restated():
    return [
        fy(1000, "10K-ORIG", date(2025, 2, 20)),
        fy(900, "10K-R", date(2026, 2, 20)),
        ytd9(700, "Q3-ORIG", date(2024, 11, 5)),
        ytd9(650, "Q3-R", date(2025, 11, 5)),
    ]


def test_both_restated_without_evidence_blocks_even_though_ranks_align():
    c = run(_both_restated())
    assert c.category == q.BLOCKED_MIXED


def test_both_restated_with_overlap_agreement_derives_latest_vintage():
    prior_start, prior_end = date(2023, 1, 1), date(2023, 12, 31)
    ctx = [
        fact(500, "10K-R", date(2026, 2, 20), prior_start, prior_end, "FY"),
        fact(500, "Q3-R", date(2025, 11, 5), prior_start, prior_end, "FY"),
    ]
    c = run(_both_restated(), context_facts=ctx)
    assert c.category == q.SAME_VINTAGE
    assert c.vintage_basis == "overlap_agreement"
    assert c.fy_value == D(900) and c.ytd_value == D(650) and c.q4_value == D(250)


def test_overlap_disagreement_vetoes_the_pairing():
    prior_start, prior_end = date(2023, 1, 1), date(2023, 12, 31)
    ctx = [
        fact(500, "10K-R", date(2026, 2, 20), prior_start, prior_end, "FY"),
        fact(480, "Q3-R", date(2025, 11, 5), prior_start, prior_end, "FY"),
    ]
    assert run(_both_restated(), context_facts=ctx).category == q.BLOCKED_MIXED


def test_same_accession_is_same_vintage():
    c = run(
        [
            fy(1000, "COMBINED", date(2025, 2, 20)),
            fy(900, "10K-R", date(2026, 2, 20)),
            ytd9(700, "COMBINED", date(2025, 2, 20)),
            ytd9(650, "Q3-R", date(2025, 11, 5)),
        ]
    )
    # the same-accession pair is the original one, but its FY is superseded
    assert c.category == q.BLOCKED_MIXED
    assert any(a["vintage_basis"] == "same_accession" for a in c.alternatives)


def test_same_accession_on_latest_fy_derives():
    c = run([fy(900, "COMBINED", date(2025, 2, 20)), ytd9(650, "COMBINED", date(2025, 2, 20)),
             ytd9(700, "Q3-ORIG", date(2024, 11, 5))])
    assert c.category == q.SAME_VINTAGE and c.vintage_basis == "same_accession"
    assert c.q4_value == D(250)


# ------------------------------------------------------------ sign conflict


def test_pure_sign_conflict_is_quarantined():
    c = run([fy(-500, "10K-A"), fy(500, "10K-B", date(2025, 4, 1)), ytd9(300)])
    assert c.category == q.BLOCKED_SIGN
    assert c.q4_value is None


def test_sign_conflict_on_ytd_side():
    c = run([fy(500), ytd9(300, "Q-A"), ytd9(-300, "Q-B", date(2025, 1, 5))])
    assert c.category == q.BLOCKED_SIGN


def test_zero_is_not_a_sign_conflict():
    c = run([fy(0, "A"), fy(0, "B", date(2025, 3, 1)), ytd9(0)])
    assert c.category == q.CLEAN


def test_genuinely_different_values_are_not_sign_conflict():
    c = run([fy(500, "A"), fy(-400, "B", date(2025, 4, 1)), ytd9(300)])
    assert c.category != q.BLOCKED_SIGN


# ---------------------------------------------------------- other blocks


def test_no_ytd_source():
    c = run([fy(1000)])
    assert c.category == q.BLOCKED_NO_YTD


def test_incomplete_chain_is_no_source():
    q1 = fact(200, "Q1", date(2024, 5, 1), date(2024, 1, 1), date(2024, 3, 31), "Q1")
    assert run([fy(1000), q1]).category == q.BLOCKED_NO_YTD


def test_no_fy_fact():
    c = run([ytd9(700)])
    assert c.category == q.BLOCKED_NO_FY


def test_fy_span_ambiguous():
    c = run([fy(1000), fy(1000, "X", end=date(2025, 1, 5)), ytd9(700)])
    assert c.category == q.BLOCKED_NO_FY and c.block_reason == "fy_span_ambiguous"


def test_non_additive_concept_blocked_even_with_perfect_inputs():
    c = run([fy(1000), ytd9(700)], additive=False)
    assert c.category == q.BLOCKED_NON_ADDITIVE


def test_instant_facts_are_not_additive_flows():
    inst = fact(100, "A", date(2025, 2, 20), None, FY_END, "FY")
    assert run([inst]).category == q.BLOCKED_NON_ADDITIVE


def test_mixed_units_blocked():
    c = run([fy(1000), fact(700, "Q", date(2024, 11, 5), FY_START, YTD_END, None, unit="CAD")])
    assert c.category == q.BLOCKED_MIXED and c.block_reason == "mixed_units_in_cell"


def test_ytd_and_chain_disagreement_blocks():
    q1 = fact(200, "Q1", date(2024, 5, 1), date(2024, 1, 1), date(2024, 3, 31), "Q1")
    q2 = fact(250, "Q2", date(2024, 8, 1), date(2024, 4, 1), date(2024, 6, 30), "Q2")
    q3 = fact(250, "Q3", date(2024, 11, 1), date(2024, 7, 1), date(2024, 9, 30), "Q3")
    c = run([fy(1000), ytd9(650), q1, q2, q3])  # 9M says 650, chain says 700
    assert c.category == q.BLOCKED_MIXED and c.block_reason == "ytd9_and_chain_disagree"


def test_ytd_and_chain_agreeing_is_noted():
    q1 = fact(200, "Q1", date(2024, 5, 1), date(2024, 1, 1), date(2024, 3, 31), "Q1")
    q2 = fact(250, "Q2", date(2024, 8, 1), date(2024, 4, 1), date(2024, 6, 30), "Q2")
    q3 = fact(250, "Q3", date(2024, 11, 1), date(2024, 7, 1), date(2024, 9, 30), "Q3")
    c = run([fy(1000), ytd9(700), q1, q2, q3])
    assert c.category == q.CLEAN and "ytd9_and_chain_agree" in c.notes


def test_chain_member_with_conflicting_copies_is_not_paired():
    q1 = fact(200, "Q1", date(2024, 5, 1), date(2024, 1, 1), date(2024, 3, 31), "Q1")
    q1b = fact(210, "Q1b", date(2024, 9, 1), date(2024, 1, 1), date(2024, 3, 31), "Q1")
    q2 = fact(250, "Q2", date(2024, 8, 1), date(2024, 4, 1), date(2024, 6, 30), "Q2")
    q3 = fact(250, "Q3", date(2024, 11, 1), date(2024, 7, 1), date(2024, 9, 30), "Q3")
    c = run([fy(1000), q1, q1b, q2, q3])
    assert c.category == q.BLOCKED_MIXED
    assert "chain_member_has_multiple_values" in c.block_reason


def test_chain_gap_is_not_contiguous():
    q1 = fact(200, "Q1", date(2024, 5, 1), date(2024, 1, 1), date(2024, 3, 31), "Q1")
    q2 = fact(250, "Q2", date(2024, 8, 1), date(2024, 4, 5), date(2024, 6, 30), "Q2")
    q3 = fact(250, "Q3", date(2024, 11, 1), date(2024, 7, 1), date(2024, 9, 30), "Q3")
    c = run([fy(1000), q1, q2, q3])
    assert c.category == q.BLOCKED_MIXED
    assert "chain_not_contiguous" in c.block_reason


def test_different_fiscal_start_ytd_is_ignored():
    wrong = ytd9(700, start=date(2023, 12, 1))
    assert run([fy(1000), wrong]).category == q.BLOCKED_NO_YTD


def test_derived_facts_are_never_inputs():
    d = fact(700, "DER", date(2025, 1, 1), FY_START, YTD_END, None, derived=True)
    assert run([fy(1000), d]).category == q.BLOCKED_NO_YTD


def test_direct_reported_q4_is_surfaced_for_precedence():
    q4 = fact(300, "Q4", date(2025, 2, 20), date(2024, 10, 1), FY_END, "Q4")
    c = run([fy(1000), ytd9(700), q4])
    assert c.direct_q4_fact_ids == [q4.fact_id]
    assert "direct_reported_q4_exists_prefer_it" in c.notes


# --------------------------------------------------------------- records


def test_every_category_reachable_and_exclusive():
    seen = {
        run([fy(1000), ytd9(700)]).category,
        run(
            [fy(1000, auth=False), fy(1001, "B", date(2025, 3, 1), auth=False), ytd9(700)],
            tol=LOOSE,
        ).category,
        run([fy(1000, "A"), fy(900, "B", date(2026, 2, 1)), ytd9(700)]).category,
        run([fy(-5, "A"), fy(5, "B", date(2025, 4, 1)), ytd9(3)]).category,
        run([fy(1000)]).category,
        run([ytd9(1)]).category,
        run([fy(1), ytd9(1)], additive=False).category,
    }
    assert seen == set(q.CATEGORIES)


def test_record_is_json_serialisable_with_decimal_arithmetic():
    c = run([fy("1000.50"), ytd9("700.25")])
    rec = json.loads(json.dumps(c.to_record()))
    assert rec["q4_value"] == "300.25"
    assert rec["arithmetic"] == "1000.50 - 700.25 = 300.25"
    assert rec["formula_id"] == q.FORMULA_YTD9
    assert rec["policy_version"] == q.POLICY_VERSION
    assert rec["tolerance"] == {"rel": "0", "abs_tol": "0"}
    assert isinstance(c.q4_value, Decimal)


def test_summarize_counts_categories_and_reasons():
    cs = [run([fy(1)]), run([fy(1)]), run([fy(1000), ytd9(700)])]
    s = q.summarize(cs)
    assert s[q.BLOCKED_NO_YTD] == 2 and s[q.CLEAN] == 1
    assert s["reason:no_ytd9_and_no_complete_q1_q3_chain"] == 2


# ---------------------------------------------------------------- loader


class _Cur:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.conn.calls.append((sql, params))

    def fetchall(self):
        return self.conn.rows_for(self.conn.calls[-1][1]["company_ids"])


class _Conn:
    def __init__(self, rows_by_company):
        self.calls = []
        self.rows_by_company = rows_by_company
        self.committed = False

    def cursor(self):
        return _Cur(self)

    def commit(self):
        self.committed = True

    def rows_for(self, ids):
        return [r for i in ids for r in self.rows_by_company.get(i, [])]


def _row(fid, cid, concept, value, acc, filed, start, end, auth, fp, unit="USD"):
    return (fid, cid, concept, unit, D(str(value)), acc, filed, start, end, auth, fp)


def test_loader_is_read_only_parameterized_and_chunked():
    rows = {
        1: [
            _row(1, 1, 10, 1000, "K", date(2025, 2, 20), FY_START, FY_END, True, "FY"),
            _row(2, 1, 10, 700, "Q", date(2024, 11, 5), FY_START, YTD_END, True, None),
            _row(3, 1, 11, 5, "K", date(2025, 2, 20), FY_START, FY_END, True, "FY"),
        ],
        2: [],
        3: [_row(9, 3, 10, 50, "K", date(2025, 2, 20), FY_START, FY_END, True, "FY")],
    }
    conn = _Conn(rows)
    out = list(
        q.load_candidates(
            conn,
            [3, 1, 2],
            concept_ids=[10, 11],
            additive_concept_ids=[10],
            tol=EXACT,
            chunk_size=2,
        )
    )
    assert len(conn.calls) == 2  # chunked by company id
    assert conn.calls[0][1]["company_ids"] == [1, 2]
    assert conn.calls[1][1]["company_ids"] == [3]
    sql = conn.calls[0][0].lower()
    for word in ("insert ", "update ", "delete ", "truncate", "alter ", "drop "):
        assert word not in sql
    assert "%(company_ids)s" in sql and "not f.is_derived" in sql
    assert not conn.committed
    cats = {(c.company_id, c.concept_id): c.category for c in out}
    assert cats[(1, 10)] == q.CLEAN
    assert cats[(1, 11)] == q.BLOCKED_NON_ADDITIVE
    assert cats[(3, 10)] == q.BLOCKED_NO_YTD


def test_overlap_disagreement_vetoes_even_single_value_sides():
    # Both sides single-valued (the single-value rule would accept), but the
    # two filings disagree on another period they both report: a basis change.
    ps, pe = date(2023, 1, 1), date(2023, 12, 31)
    ctx = [
        fact(500, "10K-A", date(2025, 2, 20), ps, pe, "FY"),
        fact(470, "10Q3-A", date(2024, 11, 5), ps, pe, "FY"),
    ]
    c = run([fy(1000), ytd9(700)], context_facts=ctx)
    assert c.category == q.BLOCKED_MIXED
    agree = [
        fact(500, "10K-A", date(2025, 2, 20), ps, pe, "FY"),
        fact(500, "10Q3-A", date(2024, 11, 5), ps, pe, "FY"),
    ]
    assert run([fy(1000), ytd9(700)], context_facts=agree).vintage_basis == "overlap_agreement"
