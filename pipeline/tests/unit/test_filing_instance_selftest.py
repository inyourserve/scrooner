"""The 50-filing equivalence gate for a future fallback reader (harness only).
Fixtures are SYNTHETIC filings shaped like real ones; the reader is fake."""

from datetime import date
from decimal import Decimal

from scrooner_pipeline.sanity import filing_instance_selftest as st
from scrooner_pipeline.sanity.filing_instance_selftest import InstanceFact, SampleFiling

D = Decimal
END = date(2026, 6, 27)


def fact(tag, value, start=date(2026, 3, 29), end=END, unit="USD", taxonomy="us-gaap"):
    return InstanceFact(taxonomy, tag, unit, start, end, D(str(value)))


STORED = [
    fact("Revenues", 100),
    fact("Assets", 500, start=None),
    fact("NetIncomeLoss", 7),
]


def filing(i):
    return SampleFiling(
        f"0000000000-26-{i:06d}",
        "0000000001",
        "10-Q",
        i,
        END,
        "quarterly|fye_month_09|52_53_week",
    )


class Replay:
    def __init__(self, transform=lambda facts: facts):
        self.transform = transform

    def read(self, f):
        return self.transform(list(STORED))


def run(reader, n=50):
    return st.run_selftest(
        reader, [filing(i) for i in range(n)], lambda f: list(STORED)
    )


def test_perfect_reader_passes_with_fifty_filings():
    rep = run(Replay())
    assert (
        rep.passed
        and rep.summary()["matched_facts"] == 150
        and rep.summary()["gate_passed"]
    )


def test_fewer_than_fifty_filings_never_passes_the_gate():
    rep = run(Replay(), n=49)
    assert not rep.passed and rep.summary()["passed_filings"] == 49


def test_duplicate_accessions_do_not_count_as_distinct_filings():
    rep = st.run_selftest(Replay(), [filing(1)] * 60, lambda f: list(STORED))
    assert rep.distinct_filings == 1 and not rep.passed


def test_one_missing_fact_fails_the_whole_gate():
    rep = st.run_selftest(
        Replay(lambda facts: facts[:-1] if True else facts),
        [filing(i) for i in range(50)],
        lambda f: list(STORED),
    )
    assert not rep.passed and rep.results[0].missing and rep.summary()["failed_filings"]


def test_one_wrong_value_fails_even_with_ninety_nine_percent_recall_elsewhere():
    calls = {"n": 0}

    def tweak(facts):
        calls["n"] += 1
        if calls["n"] == 25:  # one filing out of fifty has one value off by 1
            facts[0] = fact("Revenues", 101)
        return facts

    rep = run(Replay(tweak))
    assert not rep.passed
    bad = [r for r in rep.results if not r.passed]
    assert len(bad) == 1 and bad[0].mismatched[0][1:] == (D("100"), D("101"))


def test_unit_period_and_taxonomy_are_part_of_the_key():
    wrong_unit = Replay(lambda fs: [fact("Revenues", 100, unit="EUR")] + fs[1:])
    wrong_period = Replay(
        lambda fs: [fact("Revenues", 100, end=date(2026, 6, 28))] + fs[1:]
    )
    wrong_tax = Replay(lambda fs: [fact("Revenues", 100, taxonomy="custom")] + fs[1:])
    for reader in (wrong_unit, wrong_period, wrong_tax):
        assert not run(reader).passed


def test_extra_reader_facts_are_counted_but_never_block_or_get_written():
    rep = run(Replay(lambda fs: fs + [fact("CustomExtensionThing", 1, taxonomy="abc")]))
    assert rep.passed and rep.summary()["extra_facts_not_written"] == 50


def test_conflicting_duplicates_in_the_reader_fail():
    rep = run(Replay(lambda fs: fs + [fact("Revenues", 999)]))
    assert not rep.passed and rep.results[0].duplicate_conflicts == 1


def test_a_filing_with_no_stored_facts_cannot_pass():
    r = st.compare_filing(filing(1), [], list(STORED))
    assert not r.passed


def test_stratified_sampler_is_deterministic_and_spreads_strata():
    cands = []
    i = 0
    for stratum, count in (("annual|a", 30), ("quarterly|b", 30), ("quarterly|c", 5)):
        for _ in range(count):
            i += 1
            cands.append(SampleFiling(f"A-{i:04d}", "c", "10-Q", i, END, stratum))
    a = st.stratify(cands, 12, seed=7)
    b = st.stratify(list(reversed(cands)), 12, seed=7)
    assert [x.accession for x in a] == [x.accession for x in b]
    assert {
        s: sum(1 for x in a if x.stratum == s)
        for s in ("annual|a", "quarterly|b", "quarterly|c")
    } == {
        "annual|a": 4,
        "quarterly|b": 4,
        "quarterly|c": 4,
    }
    assert (
        st.stratum_label("10-K", date(2026, 9, 26), True)
        == "annual|fye_month_09|52_53_week"
    )
