"""Era back-extension of docmap rows (mapper/era_extend.py): pure walk logic, and the loader against fsn rows."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import era_extend as ee

TAG = "Revenues"
REF = "0000000077-25-000001"


def L(stmt="IS", prole="terseLabel", label="net sales", parents=("GrossProfit",)):
    return ee.Line(stmt, prole, label, frozenset(parents))


def data(years: dict, lines: dict, mapped=None):
    """years: fiscal year -> accession (period = Dec 31); lines: accession -> {tag: [Line]}."""
    return ee.FsnData(
        {date(y, 12, 31): [a] for y, a in years.items()}, lines, mapped or {}
    )


def acc(y):
    return f"0000000077-{y % 100:02d}-000001"


YEARS = {y: acc(y) for y in range(2015, 2026)}
BASE = date(2024, 1, 1)  # the read (FY2025 10-K) printed FY2025 and FY2024


def lines_for(years, **kw):
    return {acc(y): {TAG: [L(**kw)]} for y in years}


def run(d):
    return ee.extend([TAG], set(), BASE, acc(2025), d)[:3]


def test_extends_back_across_continuous_years():
    era, adsh, log = run(data(YEARS, lines_for(YEARS)))
    # the FY2023 10-K prints FY2023 and FY2022 ... the FY2015 10-K prints FY2015 and FY2014; floor 2015-01-01
    assert era == date(2015, 1, 1)
    assert adsh == acc(2016) or adsh == acc(2015)
    assert all(r["check"] == "pass" for r in log)
    assert [r["adsh"] for r in log][0] == acc(2024)


def test_stops_at_a_tag_switch():
    ls = lines_for(YEARS)
    for y in (2020, 2019, 2018, 2017, 2016, 2015):
        ls[acc(y)] = {"SalesRevenueNet": [L()]}  # the company printed another tag before 2021
    era, adsh, log = run(data(YEARS, ls))
    assert era == date(2020, 1, 1)  # the FY2021 10-K prints FY2021 and FY2020
    assert adsh == acc(2021)
    assert log[-1]["check"] == "fail" and "not printed" in log[-1]["detail"]


def test_stops_at_a_changed_line():
    ls = lines_for(YEARS)
    ls[acc(2020)] = {TAG: [L(stmt="CF", label="other", prole="x")]}
    era, adsh, _ = run(data(YEARS, ls))
    assert (era, adsh) == (date(2020, 1, 1), acc(2021))
    ls[acc(2020)] = {TAG: [L(parents=("Other",))]}
    assert run(data(YEARS, ls))[0] == date(2020, 1, 1)  # calc parent changed


def test_stops_at_a_gap_and_never_bridges():
    years = {y: a for y, a in YEARS.items() if y != 2019}  # no FY2019 filing in the store
    era, adsh, log = run(data(years, lines_for(years)))
    assert era == date(2019, 1, 1) and adsh == acc(2020)
    assert log[-1]["check"] == "fail" and log[-1]["detail"].startswith("gap")


def test_other_tag_mapped_to_the_concept_stops():
    ls = lines_for(YEARS)
    mp = {acc(2019): {7: {"SalesRevenueNet"}}}
    era, _, _, _ = ee.extend([TAG], {7}, BASE, acc(2025), data(YEARS, ls, mp))
    assert era == date(2019, 1, 1)


def test_unknown_reference_extends_nothing():
    d = data(YEARS, {})
    era, adsh, log = run(d)
    assert (era, adsh) == (BASE, None) and log[0]["check"] == "fail"



def test_calc_parent_relaxed_only_when_the_earlier_filing_has_no_arc():
    ls = lines_for(YEARS)
    ls[acc(2020)] = {TAG: [L(parents=())]}  # no calc arc in FY2020: passes on stmt + role/label
    assert run(data(YEARS, ls))[0] == date(2015, 1, 1)
    ls[acc(2020)] = {TAG: [L(parents=("Other",))]}  # a different parent still cuts
    assert run(data(YEARS, ls))[0] == date(2020, 1, 1)


def V(kind="annual", unit="usd"):
    return {(kind, unit)}


def value_data(with_value, other_unit_year=None):
    """The read 10-K has no face line, only a non-dimensional value (a note / CF supplemental tag)."""
    vals = {acc(y): {TAG: V()} for y in with_value}
    if other_unit_year:
        vals[acc(other_unit_year)] = {TAG: V(unit="shares")}
    d = data(YEARS, {})
    d.values = vals
    return d


def test_value_fallback_extends_marks_value_and_stops():
    era, adsh, log, by_value = ee.extend(
        [TAG], set(), BASE, acc(2025), value_data(range(2019, 2026))
    )
    assert (era, adsh, by_value) == (date(2018, 1, 1), acc(2019), True)
    assert log[-1]["check"] == "fail" and "value" in log[-1]["detail"]


def test_value_fallback_needs_the_same_unit_class():
    d = value_data(range(2019, 2026), other_unit_year=2021)
    era, _, _, _ = ee.extend([TAG], set(), BASE, acc(2025), d)
    assert era == date(2021, 1, 1)  # FY2021 carries the tag in another unit class: cut


def test_value_fallback_stops_when_another_tag_is_mapped():
    d = value_data(range(2015, 2026))
    d.mapped = {acc(2019): {7: {"Other"}}}
    assert ee.extend([TAG], {7}, BASE, acc(2025), d)[0] == date(2019, 1, 1)


def test_not_printed_logs_the_other_tag_used():
    ls = lines_for(YEARS)
    ls[acc(2020)] = {"SalesRevenueNet": [L()]}
    d = data(YEARS, ls, {acc(2020): {7: {"SalesRevenueNet"}}})
    d.by_label = {acc(2020): {("IS", "net sales"): {"SalesRevenueNet"}}}
    log = ee.extend([TAG], {7}, BASE, acc(2025), d)[2]
    assert log[-1]["check"] == "fail"
    assert log[-1]["other_tag"] == "label:SalesRevenueNet;line_map:SalesRevenueNet"

# ---- loader, DB-backed -------------------------------------------------------------------------------------------

CSV = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZE,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Net sales,,FILING-CHECKED,
"""
MD = f"Latest 10-K opened: {REF} (period 2025-12-31)"


def _seed(conn, years_with_tag):
    cid = conn.execute(
        "insert into core.company (cik, company_name, primary_ticker) values ('0000000077', 'Z', 'ZZE') returning id"
    ).fetchone()[0]
    tid = conn.execute(
        "insert into fsn.tag (tag, version) values ('Revenues', 'us-gaap/2024') returning id"
    ).fetchone()[0]
    other = conn.execute(
        "insert into fsn.tag (tag, version) values ('SalesRevenueNet', 'us-gaap/2024') returning id"
    ).fetchone()[0]
    for y in range(2015, 2026):
        fid = conn.execute(
            "insert into fsn.filing (accession, company_id, cik, form, period, fsn_set) "
            "values (%s, %s, '0000000077', '10-K', %s, 'x') returning id",
            (acc(y), cid, date(y, 12, 31)),
        ).fetchone()[0]
        if y in years_with_tag:
            conn.execute(
                "insert into fsn.line (filing_id, report, line, stmt, tag_id, prole, plabel) "
                "values (%s, 2, 1, 'IS', %s, 'terseLabel', 'Net sales')",
                (fid, tid),
            )
        else:
            conn.execute(
                "insert into fsn.line (filing_id, report, line, stmt, tag_id, prole, plabel) "
                "values (%s, 2, 1, 'IS', %s, 'terseLabel', 'Net sales')",
                (fid, other),
            )
    return cid


@pytest.mark.integration
def test_loader_extends_and_records_evidence(isolated_database_url, tmp_path: Path):
    (tmp_path / "ZZE-docmap-2026-11-12.csv").write_text(CSV)
    (tmp_path / "ZZE-docmap-2026-11-12.md").write_text(MD)
    paths = sorted(tmp_path.glob("*-docmap-*.csv"))
    log = tmp_path / "era.csv"
    with psycopg.connect(isolated_database_url) as conn:
        cid = _seed(conn, set(range(2019, 2026)))  # same tag FY2019-2025, another tag before
        conn.commit()
        plain = dl.load(conn, paths)
        assert plain["extended"] == []
        stats = dl.load(conn, paths, apply=True, extend_eras=True, era_log=log)
        assert len(stats["extended"]) == 1
        rows = conn.execute(
            """select rule_id, era_from::text, era_to::text, evidence_adsh, serve_note, decided_by
               from analytics.company_tag_map where company_id = %s order by era_from""",
            (cid,),
        ).fetchall()
        assert [(r[0], r[1], r[2]) for r in rows] == [
            (ee.EXT_RULE_ID, "2018-01-01", "2023-12-31"),  # FY2019 10-K prints FY2019 and FY2018
            (dl.RULE_ID, "2024-01-01", None),
        ]
        assert rows[0][3] == REF and rows[0][4].startswith(ee.EXT_MARK) and acc(2019) in rows[0][4]
        # idempotent: a second apply replaces both rules' rows
        dl.load(conn, paths, apply=True, extend_eras=True)
        assert conn.execute(
            "select count(*) from analytics.company_tag_map where company_id = %s", (cid,)
        ).fetchone()[0] == 2
    assert "pass" in log.read_text() and "fail" in log.read_text()


def absent_data(years, lines_by_year=None, facts_years=None, cand_fact_years=()):
    lbl = {
        acc(y): {("IS", "other"): set((lines_by_year or {}).get(y, {"Other"}))}
        for y in years
    }
    d = data(years, {})
    d.by_label = lbl
    with_facts = {acc(y) for y in (facts_years if facts_years is not None else years)}
    present = {acc(y): {"Cand"} for y in cand_fact_years}
    return d, with_facts, present


def absent(years=YEARS, **kw):
    combined = kw.pop("combined", [])
    d, wf, pr = absent_data(years, **kw)
    # the candidate set may include the combined tag itself (it serves other concepts): it must not count against
    return ee.extend_absent({"Cand"} | set(combined), combined, BASE, d, wf, pr)


def test_absence_extends_until_a_candidate_fact_or_line():
    era, adsh, log = absent()
    assert era == date(2015, 1, 1)
    assert all(r["check"] == "pass" for r in log)
    era, adsh, log = absent(cand_fact_years=(2019,))  # a candidate among the FY2019 10-K's facts (a note)
    assert (era, adsh) == (date(2019, 1, 1), acc(2020))
    assert log[-1]["check"] == "fail" and log[-1]["other_tag"] == "Cand"
    era, _, _ = absent(lines_by_year={2018: {"Cand"}})  # a candidate on a statement line
    assert era == date(2018, 1, 1)


def test_absence_needs_xbrl_facts_and_never_bridges_a_gap():
    era, _, log = absent(facts_years=[y for y in YEARS if y != 2020])
    assert era == date(2020, 1, 1) and "no XBRL facts" in log[-1]["detail"]
    era, _, log = absent(years={y: a for y, a in YEARS.items() if y != 2019})
    assert era == date(2019, 1, 1) and log[-1]["detail"].startswith("gap")


def test_combined_row_needs_the_combined_line_printed():
    lines = {y: {"Comb"} for y in range(2018, 2026)}
    lines[2017] = {"Other"}
    era, _, log = absent(lines_by_year=lines, combined=["Comb"])
    assert era == date(2017, 1, 1)  # FY2018 10-K prints FY2018 and FY2017; FY2017's own 10-K has no combined line
    assert "combined line is not printed" in log[-1]["detail"]
    lines[2020] = {"Comb", "Cand"}  # the concept is tagged separately beside the combined line
    assert absent(lines_by_year=lines, combined=["Comb"])[0] == date(2020, 1, 1)


CSV_REASON = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZE,revenue,not_presented,,IS,R3.htm,,,FILING-CHECKED,no revenue line
"""


@pytest.mark.integration
def test_loader_reason_row_extension(isolated_database_url, tmp_path: Path):
    (tmp_path / "ZZE-docmap-2026-11-12.csv").write_text(CSV_REASON)
    (tmp_path / "ZZE-docmap-2026-11-12.md").write_text(MD)
    paths = sorted(tmp_path.glob("*-docmap-*.csv"))
    with psycopg.connect(isolated_database_url) as conn:
        cid = _seed(conn, set())
        rev = conn.execute(
            "select id from analytics.canonical_concept where name = 'revenue_sanity_resolved'"
        ).fetchone()[0]
        other = conn.execute(
            "insert into core.company (cik, company_name, primary_ticker) values ('0000000088', 'O', 'OOO') returning id"
        ).fetchone()[0]
        conn.execute(
            "insert into analytics.company_tag_map (company_id, cik, taxonomy, tag, stmt, decision, canonical_concept_id, "
            "era_from, decided_by, rule_id) values (%s, '0000000088', 'us-gaap', 'Revenues', 'IS', 'concept', %s, "
            "'2015-01-01', 'structure', 'company_tag_map.library@1')",
            (other, rev),
        )
        conn.execute("insert into core.unit (unit_name) values ('usd') on conflict do nothing")
        uid = conn.execute("select id from core.unit where unit_name = 'usd'").fetchone()[0]
        rid = conn.execute(
            "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
            "values ('0000000077', 'u', 'h', 'raw/77', 200) returning id"
        ).fetchone()[0]
        for tag in ("Dummy", "Revenues"):
            conn.execute(
                "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) on conflict do nothing", (tag,)
            )
        cdummy, crev = (
            conn.execute("select id from core.concept where tag = %s", (t,)).fetchone()[0]
            for t in ("Dummy", "Revenues")
        )
        for y in range(2015, 2026):
            pid = conn.execute(
                "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
                "values (%s, %s, %s, 'duration', %s, 'FY') returning id",
                (cid, date(y, 1, 1), date(y, 12, 31), y),
            ).fetchone()[0]
            fid = conn.execute(
                "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) "
                "values (%s, %s, '10-K', %s, %s, false) returning id",
                (cid, acc(y), date(y + 1, 2, 20), date(y, 12, 31)),
            ).fetchone()[0]
            for c in (cdummy, crev) if y == 2019 else (cdummy,):
                conn.execute(
                    "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, "
                    "raw_object_id) values (%s, %s, %s, %s, %s, 5, true, %s)",
                    (cid, c, uid, pid, fid, rid),
                )
        conn.commit()
        dl.load(conn, paths, apply=True, extend_eras=True)
        rows = conn.execute(
            "select rule_id, decision, era_from::text, era_to::text, serve_note from analytics.company_tag_map "
            "where company_id = %s order by era_from",
            (cid,),
        ).fetchall()
    assert [r[:4] for r in rows] == [
        (ee.EXT_RULE_ID, "not_presented", "2019-01-01", "2023-12-31"),
        (dl.RULE_ID, "not_presented", "2024-01-01", None),
    ]
    assert rows[0][4].startswith(ee.EXT_MARK_ABSENT)


CSV_NOTE = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZE,cash_paid_for_income_taxes,component_in_note,us-gaap:IncomeTaxesPaidNet,Taxes - Details,R60,Taxes paid,,FILING-CHECKED,
"""


@pytest.mark.integration
def test_loader_value_fallback_for_a_note_tag(isolated_database_url, tmp_path: Path):
    (tmp_path / "ZZE-docmap-2026-11-12.csv").write_text(CSV_NOTE)
    (tmp_path / "ZZE-docmap-2026-11-12.md").write_text(MD)
    paths = sorted(tmp_path.glob("*-docmap-*.csv"))
    with psycopg.connect(isolated_database_url) as conn:
        cid = _seed(conn, set())
        tid = conn.execute(
            "insert into fsn.tag (tag, version) values ('IncomeTaxesPaidNet', 'us-gaap/2024') returning id"
        ).fetchone()[0]
        for y in range(2019, 2026):
            fid = conn.execute(
                "select id from fsn.filing where accession = %s", (acc(y),)
            ).fetchone()[0]
            conn.execute(
                "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, value) "
                "values (%s, %s, %s, %s, 4, 'USD', 0, 5)",
                (fid, cid, tid, date(y, 12, 31)),
            )
        conn.commit()
        dl.load(conn, paths, apply=True, extend_eras=True)
        rows = conn.execute(
            "select rule_id, era_from::text, era_to::text, serve_note from analytics.company_tag_map "
            "where company_id = %s order by era_from",
            (cid,),
        ).fetchall()
    assert [(r[0], r[1], r[2]) for r in rows] == [
        (ee.EXT_RULE_ID, "2018-01-01", "2023-12-31"),
        (dl.RULE_ID, "2024-01-01", None),
    ]
    assert rows[0][3].startswith(ee.EXT_MARK_VALUE)


# --- comparative-column extension -------------------------------------------------------------------------------------


def _dec(y):
    return date(y if y > 100 else 2000 + y, 12, 31)


def _cmp(
    start_year,
    prints,
    own_years=None,
    kinds=None,
    filings=None,
    tags=("Rev",),
    other=None,
):
    """A concept covered from `start_year` (open); prints: {filing year: [ddate years it prints for every tag]}."""
    g = {
        1: [ee.Covered(date(start_year, 1, 1), None, frozenset(tags), payload=["row"])]
    }
    fl = {acc(y): _dec(y) for y in (filings if filings is not None else prints)}
    printed = {}
    own = {}
    for y, cols in prints.items():
        for t in tags:
            printed[(acc(y), t)] = {
                _dec(c): {(kinds or {}).get(c, "annual")} for c in cols
            }
            own[(acc(y), t)] = {(kinds or {}).get(y, "annual")} if y in cols else set()
    return ee.comparative_slices(g, fl, printed, own, other)[0]


def _span(slices):
    return sorted(
        (s.era_from.isoformat(), s.era_to.isoformat(), s.adsh) for s in slices
    )


def test_comparative_extends_year_by_year_on_each_next_10k():
    s = _cmp(2024, {2024: [2024, 2023], 2023: [2023, 2022], 2022: [2022, 2021]})
    assert _span(s) == [
        ("2021-01-01", "2021-12-31", acc(22)),
        ("2022-01-01", "2022-12-31", acc(23)),
        ("2023-01-01", "2023-12-31", acc(24)),
    ]


def test_comparative_needs_the_next_10k_to_print_the_same_tag_for_that_year():
    # FY2023 10-K does not print FY2022: FY2022 stays open, and FY2021 (printed by the FY2022 10-K) is NOT bridged
    s = _cmp(2024, {2024: [2024, 2023], 2023: [2023], 2022: [2022, 2021]})
    assert _span(s) == [("2023-01-01", "2023-12-31", acc(24))]
    # the tag is printed under another tag only: nothing
    assert _cmp(2024, {2024: [2024, 2023]}, tags=("Rev",), other=None) != []
    g = {1: [ee.Covered(date(2024, 1, 1), None, frozenset({"Rev"}))]}
    printed = {(acc(24), "Other"): {_dec(24): {"annual"}, _dec(23): {"annual"}}}
    assert (
        ee.comparative_slices(
            g, {acc(24): _dec(24)}, printed, {(acc(24), "Other"): {"annual"}}
        )[0]
        == []
    )


def test_comparative_needs_the_next_10k_to_exist_and_the_same_kind():
    assert (
        _cmp(2024, {2024: [2024, 2023]}, filings=[]) == []
    )  # the 10-K is not in the store
    assert (
        _cmp(2024, {2024: [2024, 2023]}, kinds={2023: "instant"}) == []
    )  # prior column of another kind
    assert (
        _cmp(2024, {2024: [2024, 2023]}, other=lambda a, k: {"Rev2"}) == []
    )  # another tag mapped to the concept


def test_comparative_never_extends_past_the_latest_year_or_a_reason_group():
    # nothing covers 2025 and no 10-K follows it; a reason-only neighbor carries no tag
    g = {1: [ee.Covered(date(2022, 1, 1), date(2024, 12, 31), frozenset({"Rev"}))]}
    printed = {(acc(26), "Rev"): {_dec(25): {"annual"}, _dec(26): {"annual"}}}
    s = ee.comparative_slices(
        g, {acc(26): _dec(26)}, printed, {(acc(26), "Rev"): {"annual"}}
    )[0]
    assert _span(s) == [
        ("2025-01-01", "2025-12-31", acc(26))
    ]  # forward by one year; FY2026 itself has no next 10-K
    reason = {1: [ee.Covered(date(2024, 1, 1), None, None)]}
    printed = {(acc(24), "Rev"): {_dec(24): {"annual"}, _dec(23): {"annual"}}}
    assert (
        ee.comparative_slices(
            reason, {acc(24): _dec(24)}, printed, {(acc(24), "Rev"): {"annual"}}
        )[0]
        == []
    )


def test_comparative_stays_after_a_row_ending_inside_the_year_and_at_the_floor():
    g = {
        1: [
            ee.Covered(date(2024, 1, 1), None, frozenset({"Rev"})),
            ee.Covered(date(2015, 1, 1), date(2022, 6, 30), None),
        ]
    }
    printed = {
        (acc(24), "Rev"): {_dec(24): {"annual"}, _dec(23): {"annual"}},
        (acc(23), "Rev"): {_dec(23): {"annual"}, _dec(22): {"annual"}},
    }
    own = {(acc(24), "Rev"): {"annual"}, (acc(23), "Rev"): {"annual"}}
    s = ee.comparative_slices(g, {acc(24): _dec(24), acc(23): _dec(23)}, printed, own)[
        0
    ]
    # FY2022 starts after the reason row ended (2022-06-30): the slice does not overlap it
    assert _span(s) == [
        ("2022-07-01", "2022-12-31", acc(23)),
        ("2023-01-01", "2023-12-31", acc(24)),
    ]
    s2 = _cmp(2016, {2016: [2016, 2015], 2015: [2015, 2014]})
    assert _span(s2) == [
        ("2015-01-01", "2015-12-31", acc(16))
    ]  # FY2014 is before the data window


CSV_CMP = """ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note
ZZE,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Net sales,,FILING-CHECKED,
"""


@pytest.mark.integration
def test_loader_comparative_extension_from_the_next_10k(
    isolated_database_url, tmp_path: Path
):
    (tmp_path / "ZZE-docmap-2026-11-12.csv").write_text(CSV_CMP)
    (tmp_path / "ZZE-docmap-2026-11-12.md").write_text(MD)
    paths = sorted(tmp_path.glob("*-docmap-*.csv"))
    with psycopg.connect(isolated_database_url) as conn:
        cid = _seed(conn, {2024, 2025})  # the FSN line walk reaches FY2023 and stops
        tid = conn.execute("select id from fsn.tag where tag = 'Revenues'").fetchone()[
            0
        ]
        for y, cols in {
            2025: [2025, 2024],
            2024: [2024, 2023],
            2023: [2023, 2022],
            2022: [2022],
        }.items():
            fid = conn.execute(
                "select id from fsn.filing where accession = %s", (acc(y),)
            ).fetchone()[0]
            for c in cols:
                conn.execute(
                    "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, value) "
                    "values (%s, %s, %s, %s, 4, 'USD', 0, 5)",
                    (fid, cid, tid, _dec(c)),
                )
        conn.commit()
        dl.load(conn, paths, apply=True, extend_eras=True)
        q = (
            "select rule_id, decided_by, era_from::text, era_to::text, evidence_adsh, serve_note "
            "from analytics.company_tag_map where company_id = %s order by era_from"
        )
        rows = conn.execute(q, (cid,)).fetchall()
        assert [(r[0], r[1], r[2], r[3], r[4]) for r in rows] == [
            (ee.EXT_RULE_ID, ee.COMP_BY, "2022-01-01", "2022-12-31", acc(23)),
            (ee.EXT_RULE_ID, "era_extend", "2023-01-01", "2023-12-31", REF),
            (dl.RULE_ID, "docmap", "2024-01-01", None, REF),
        ]
        assert rows[0][5].startswith(ee.COMP_MARK)
        dl.load(conn, paths, apply=True, extend_eras=True)  # idempotent
        assert conn.execute(q, (cid,)).fetchall() == rows
