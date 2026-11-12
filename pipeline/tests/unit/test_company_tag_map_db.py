"""resolve-facts through analytics.company_tag_map on a migrated scratch database (CI: Postgres 16)."""

from __future__ import annotations

from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.mapper.resolve import resolve


def _one(conn, sql, *args):
    return conn.execute(sql, args).fetchone()[0]


def _seed(conn):
    cc = lambda n, st: _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s,%s,'first_match') returning id", n, st)
    rev, opex = cc("tm_rev", "income_statement"), cc("tm_opex", "income_statement")
    raw = _one(conn, "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) values ('0000000000','u','s','p',200) returning id")
    unit = _one(conn, "insert into core.unit (unit_name) values ('USD') returning id")
    tags = {}
    for t in ("Revenues", "SalesRevenueNet", "OpA", "OpB", "OtherOpex"):
        tags[t] = _one(conn, "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) returning id", t)
    # global rules that would pick the excluded / unmapped tags
    for cid, tag, pr in ((rev, "SalesRevenueNet", 1), (rev, "Revenues", 2), (opex, "OtherOpex", 1)):
        conn.execute("insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority) values (%s,%s,%s)", (cid, tags[tag], pr))
    ctx = {"rev": rev, "opex": opex, "raw": raw, "unit": unit, "tags": tags}

    def company(cik, mapped):
        co = _one(conn, "insert into core.company (cik, company_name) values (%s,%s) returning id", cik, cik)
        per = {}
        for name, end in (("in", "2018-12-31"), ("out", "2020-12-31")):
            per[name] = _one(conn, "insert into core.period (company_id, start_date, end_date, period_type) values (%s,%s,%s,'duration') returning id", co, f"{end[:4]}-01-01", end)
        fil = {}
        for name, d in (("old", "2019-02-01"), ("new", "2019-03-01")):
            fil[name] = _one(conn, "insert into core.filing (company_id, accession_number, form, filing_date) values (%s,%s,'10-K',%s) returning id", co, f"{cik}-{name}", d)

        def fact(tag, period, filing, value, auth=True):
            return _one(conn, "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) values (%s,%s,%s,%s,%s,%s,%s,%s) returning id",
                        co, tags[tag], unit, per[period], fil[filing], Decimal(value), auth, raw)

        return co, per, fil, fact

    ctx["company"] = company
    return ctx


@pytest.mark.integration
def test_tag_map_company_uses_only_the_map_and_control_keeps_the_old_path(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        co, per, fil, fact = x["company"]("0000000101", True)
        fact("Revenues", "in", "old", "100")
        f_new = fact("Revenues", "in", "new", "110")          # latest accepted filing wins
        fact("SalesRevenueNet", "in", "new", "777")             # excluded in the map, first in the global rules
        fact("Revenues", "out", "new", "55")                    # outside the era
        a = fact("OpA", "in", "new", "10")
        b = fact("OpB", "in", "new", "5")
        fact("OtherOpex", "in", "new", "444")                   # global rule for opex, not in the map
        # a non-authoritative copy (other unit) must never be used
        u2 = _one(conn, "insert into core.unit (unit_name) values ('USDx') returning id")
        conn.execute("insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) values (%s,%s,%s,%s,%s,%s,false,%s)", (co, x["tags"]["Revenues"], u2, per["in"], fil["new"], Decimal("999"), x["raw"]))
        calc = _one(conn, "insert into fsn.filing (accession, cik, form, fsn_set) values (%s,'0000000101','10-K','tm.r@1') returning id", "0000000101-new")
        pt, ca, cb = (_one(conn, "insert into fsn.tag (tag, version) values (%s,'2018') returning id", t) for t in ("OperatingExpenses", "OpA", "OpB"))
        for c in (ca, cb):
            conn.execute("insert into fsn.calc_arc (filing_id, grp, arc, parent_tag_id, child_tag_id, weight) values (%s,1,%s,%s,%s,1)", (calc, c, pt, c))
        ins = "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, parent_concept_id, sign, reason_class, era_from, era_to, evidence_cal_parent, decided_by, rule_id) values (%s,'us-gaap',%s,'IS',%s,%s,%s,%s,%s,%s,%s,%s,'t','tm.r@1')"
        conn.execute(ins, (co, "Revenues", "concept", x["rev"], None, 1, None, "2015-01-01", "2019-12-31", None))
        conn.execute(ins, (co, "SalesRevenueNet", "excluded", x["rev"], None, 1, "wrong_concept", "2015-01-01", None, None))
        for t in ("OpA", "OpB"):
            conn.execute(ins, (co, t, "component", None, x["opex"], 1, None, "2015-01-01", None, "OperatingExpenses"))
        # control: no map rows, same global rules
        co2, per2, fil2, fact2 = x["company"]("0000000102", False)
        fact2("SalesRevenueNet", "in", "new", "5")
        fact2("Revenues", "in", "new", "6")
        conn.commit()

        stats = resolve(conn, {"0000000101", "0000000102"})
        assert stats["tag_map_companies"] == 1 and stats["errored"] == 0
        rows = conn.execute("select company_id, canonical_concept_id, period_id, value, source_fact_ids from analytics.canonical_fact where company_id in (%s,%s)", (co, co2)).fetchall()
        by = {(r[0], r[1], r[2]): (r[3], r[4]) for r in rows}
        assert by[(co, x["rev"], per["in"])] == (Decimal("110"), [f_new])
        assert (co, x["rev"], per["out"]) not in by
        assert by[(co, x["opex"], per["in"])][0] == Decimal("15")
        assert sorted(by[(co, x["opex"], per["in"])][1]) == sorted([a, b])
        assert 444 not in {v for v, _ in by.values()} and 777 not in {v for v, _ in by.values()} and 999 not in {v for v, _ in by.values()}
        assert len([k for k in by if k[0] == co]) == 2
        assert by[(co2, x["rev"], per2["in"])][0] == Decimal("5")   # old path: global priority 1


@pytest.mark.integration
def test_table_checks_overlap_trigger_and_seeder(isolated_database_url, tmp_path):
    from scrooner_pipeline.mapper.company_tag_map_seed import seed

    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        co, *_ = x["company"]("0000000201", True)
        conn.commit()
        base = "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, reason, era_from, era_to, decided_by, rule_id) values (%s,'us-gaap','T','IS',%s,%s,%s,%s,%s,'t','tm.r@1')"

        def bad(*args):
            with pytest.raises(psycopg.errors.Error):
                conn.execute(base, (co, *args))
            conn.rollback()

        bad("concept", None, None, "2015-01-01", None)            # concept needs a concept
        bad("combined", x["rev"], None, "2015-01-01", None)       # combined needs the spanned concept names
        names = {r[0] for r in conn.execute("select name from analytics.canonical_concept")}
        assert {"weighted_basic_shares", "weighted_diluted_shares", "cash_paid_for_interest", "cash_paid_for_income_taxes", "net_interest_income"} <= names
        bad("excluded", None, None, "2015-01-01", None)           # excluded needs a reason
        bad("concept", x["rev"], None, "2016-01-01", "2015-01-01")  # era_from > era_to
        conn.execute(base, (co, "concept", x["rev"], None, "2015-01-01", "2017-12-31"))
        conn.commit()
        bad("concept", x["rev"], None, "2017-12-31", None)        # overlapping era, same tag and stmt
        conn.execute(base, (co, "concept", x["rev"], None, "2018-01-01", None))  # adjacent era is fine
        # one tag feeds a second concept in the same era; excluded rows overlap freely
        conn.execute(base, (co, "concept", x["opex"], None, "2018-01-01", None))
        conn.commit()
        # an excluded detail row (no concept) may coexist with a component row of the same tag; two excluded rows may overlap
        comp = "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, parent_concept_id, era_from, decided_by, rule_id) values (%s,'us-gaap','T','IS','component',%s,'2018-01-01','t','tm.r@1')"
        comp = comp.replace("'T'", "'T2'")
        conn.execute(comp, (co, x["rev"]))
        conn.execute(comp, (co, x["opex"]))  # one tag a component of two parents
        base2 = base.replace("'T'", "'T2'")
        conn.execute(base2, (co, "excluded", None, "detail", "2018-01-01", None))
        conn.commit()
        conn.execute(base2, (co, "excluded", None, "again", "2019-01-01", None))  # excluded rows may overlap each other
        conn.commit()
        with pytest.raises(psycopg.errors.Error):  # another tag, same concept, overlapping era: refused
            conn.execute(base.replace("'T'", "'T3'"), (co, "concept", x["rev"], None, "2019-01-01", None))
        conn.rollback()
        conn.execute(base.replace("'T'", "'T3'").replace("'IS'", "'IS'"), (co, "concept", x["rev"], None, "2012-01-01", "2014-12-31"))  # an era before: fine
        conn.commit()
        conn.commit()
        csv_path = tmp_path / "m.csv"
        csv_path.write_text(
            "cik,taxonomy,tag,stmt,decision,canonical_concept,era_from,decided_by,rule_id,reason\n"
            "0000000201,us-gaap,Revenues,IS,concept,tm_rev,2015-01-01,t,tm.r@1,\n"
            "0000000201,us-gaap,Other,IS,excluded,,2015-01-01,t,tm.r@1,not a revenue line\n"
        )
        dry = seed(conn, csv_path)
        assert dry["rows"] == 2 and dry["errors"] == [] and not dry["applied"]
        assert _one(conn, "select count(*) from analytics.company_tag_map") == 8  # dry run wrote nothing
        done = seed(conn, csv_path, apply=True)
        assert done["applied"] and _one(conn, "select count(*) from analytics.company_tag_map") == 2
        assert _one(conn, "select count(*) from analytics.company_tag_map where tag = 'T'") == 0  # replaced
        csv_path.write_text(csv_path.read_text() + "0000000201,us-gaap,Bad,IS,excluded,,2015-01-01,t,tm.r@1,\n")
        assert seed(conn, csv_path, apply=True)["errors"]  # a bad row blocks the whole file


@pytest.mark.integration
def test_tagless_not_presented_writes_blank_reason_and_printed_value_wins(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        gp = _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode) values ('tm_gp','income_statement','first_match') returning id")
        co, per, fil, fact = x["company"]("0000000301", True)
        fact("Revenues", "in", "new", "110")
        ins = "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, reason, era_from, decided_by, rule_id) values (%s,%s,%s,'IS',%s,%s,%s,'2015-01-01','t','tm.r@1')"
        conn.execute(ins, (co, "us-gaap", "Revenues", "concept", x["rev"], None))
        conn.execute(ins, (co, None, None, "not_presented", gp, "no gross profit line on the face"))
        conn.execute(ins, (co, None, None, "not_in_template", x["rev"], "wrongly claimed"))
        conn.commit()
        stats = resolve(conn, {"0000000301"})
        assert stats["errored"] == 0
        blanks = conn.execute("select data_point_name, state, reason_text, rule_id, period_end from analytics.cell_blank_reason where company_id = %s", (co,)).fetchall()
        gp_ends = {b[4].isoformat() for b in blanks if b[0] == "tm_gp"}
        assert gp_ends == {"2018-12-31", "2020-12-31"}
        assert {(b[1], b[2], b[3]) for b in blanks if b[0] == "tm_gp"} == {("not_presented", "no gross profit line on the face", "tm.r@1")}
        # tm_rev is printed for 2018: no blank there (value wins); the unprinted 2020 period is a blank
        assert {b[4].isoformat() for b in blanks if b[0] == "tm_rev"} == {"2020-12-31"}
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", co, x["rev"]) == Decimal("110")


@pytest.mark.integration
def test_combined_line_is_served_in_company_combined_line_and_feeds_no_concept(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        conn.execute("insert into core.concept (taxonomy, tag) values ('us-gaap', 'ApAndAccrued')")
        ap = _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode) values ('tm_ap','income_statement','first_match') returning id")
        co, per, fil, fact = x["company"]("0000000401", True)
        x["tags"]["ApAndAccrued"] = _one(conn, "select id from core.concept where tag = 'ApAndAccrued'")
        fid = fact("ApAndAccrued", "in", "new", "500")
        conn.execute("insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, components, reason, era_from, evidence_plabel, decided_by, rule_id) values (%s,'us-gaap','ApAndAccrued','IS','combined',%s,'spans two',%s,'AP and accrued','t','tm.r@1')", (co, ["tm_ap", "tm_other"], "2015-01-01"))
        conn.commit()
        assert resolve(conn, {"0000000401"})["errored"] == 0
        assert conn.execute("select plabel, value, components, source_fact_ids from analytics.company_combined_line where company_id = %s", (co,)).fetchall() == [("AP and accrued", Decimal("500"), ["tm_ap", "tm_other"], [fid])]
        assert _one(conn, "select count(*) from analytics.canonical_fact where company_id = %s", co) == 0
        got = conn.execute("select data_point_name, state, reason_text from analytics.cell_blank_reason where company_id = %s order by 1", (co,)).fetchall()
        assert got == [("tm_ap", "not_in_template", "shown as the company's combined line 'AP and accrued'"), ("tm_other", "not_in_template", "shown as the company's combined line 'AP and accrued'")]


@pytest.mark.integration
def test_coregistrant_filing_facts_are_never_served_only_the_registrants_own(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        co, per, fil, fact = x["company"]("0000000501", True)  # PLD-shaped: the parent
        fact("Revenues", "in", "old", "100")                   # the parent's own filing
        fact("Revenues", "in", "new", "40")                    # the later, combined filing's subsidiary figure
        for name, role in (("old", "primary"), ("new", "co_registrant")):
            conn.execute("insert into core.filing_registrant (accession_number, registrant_cik, company_id, role, filer_count) values (%s,'0000000501',%s,%s,2)", (f"0000000501-{name}", co, role))
        conn.execute("insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) values (%s,'us-gaap','Revenues','IS','concept',%s,'2015-01-01','t','tm.r@1')", (co, x["rev"]))
        conn.commit()
        assert resolve(conn, {"0000000501"})["errored"] == 0
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", co, x["rev"]) == Decimal("100")


@pytest.mark.integration
def test_history_source_predecessor_window_is_read_and_exclude_window_is_not(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        succ, sper, sfil, sfact = x["company"]("0000000601", True)
        pred, pper, pfil, pfact = x["company"]("0000000602", False)  # the predecessor's own core.company row
        pfact("Revenues", "in", "old", "100")   # predecessor history for the 2018 period (the successor has none)
        sfact("Revenues", "out", "new", "55")   # the successor's own 2020 filing, inside an exclude window
        conn.execute("update core.filing set period_of_report = '2018-12-31' where company_id = %s", (pred,))
        conn.execute("update core.filing set period_of_report = '2020-12-31' where company_id = %s", (succ,))
        ins = "insert into core.company_history_source (company_id, source_cik, relation, source_name, valid_from, valid_to, reason) values (%s,%s,%s,'n',%s,%s,'t')"
        conn.execute(ins, (succ, "0000000602", "predecessor", "2014-01-01", "2019-12-31"))
        conn.execute(ins, (succ, "0000000601", "exclude", "2020-01-01", "2020-12-31"))
        conn.execute("insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) values (%s,'us-gaap','Revenues','IS','concept',%s,'2015-01-01','t','tm.r@1')", (succ, x["rev"]))
        conn.commit()
        assert resolve(conn, {"0000000601"})["errored"] == 0
        got = dict(conn.execute("select period_id, value from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", (succ, x["rev"])).fetchall())
        assert got == {sper["in"]: Decimal("100")}  # predecessor window read onto the successor's period; exclude window never sourced


@pytest.mark.integration
def test_two_units_two_values_same_tag_period_filing_is_a_blank_and_the_key_allows_it(isolated_database_url, monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")
    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        co, per, fil, fact = x["company"]("0000000701", True)
        fact("Revenues", "in", "new", "100")
        u2 = _one(conn, "insert into core.unit (unit_name) values ('USDseg') returning id")
        # unique (company, concept, unit, period, filing): a second unit may carry a second value
        conn.execute("insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id) values (%s,%s,%s,%s,%s,%s,%s)", (co, x["tags"]["Revenues"], u2, per["in"], fil["new"], Decimal("40"), x["raw"]))
        conn.execute("insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) values (%s,'us-gaap','Revenues','IS','concept',%s,'2015-01-01','t','tm.r@1')", (co, x["rev"]))
        conn.commit()
        assert resolve(conn, {"0000000701"})["errored"] == 0
        assert _one(conn, "select count(*) from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", co, x["rev"]) == 0
        assert _one(conn, "select reason_code from analytics.cell_blank_reason where company_id = %s and data_point_name = 'tm_rev' and period_end = '2018-12-31'", co) == "conflicting_values_in_filing"


@pytest.mark.integration
def test_seeder_applies_open_periods_with_the_main_file_in_one_replace(isolated_database_url, tmp_path):
    from scrooner_pipeline.mapper.company_tag_map_seed import seed

    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        co, *_ = x["company"]("0000000801", True)
        conn.commit()
        main = tmp_path / "m.csv"
        main.write_text("company_id,taxonomy,tag,stmt,decision,canonical_concept,era_from,decided_by,rule_id\n" f"{co},us-gaap,Revenues,IS,concept,tm_rev,2015-01-01,t,tm.r@1\n")
        op = tmp_path / "o.csv"
        op.write_text(f'company_id,stmt,concept,period,why\n{co},IS,tm_rev,2020-12-31,"x"\n')
        st = seed(conn, main, apply=True, open_periods=op)
        assert st["errors"] == [] and st["applied"] and st["rows"] == 2
        assert conn.execute("select decision, tag, rule_id, reason from analytics.company_tag_map where company_id = %s order by decision", (co,)).fetchall() == [
            ("concept", "Revenues", "tm.r@1", None), ("not_presented", None, "tagmap.open_period@1", "not printed in this filing")]


@pytest.mark.integration
def test_seeder_refuses_instant_component_rows_except_total_debt(isolated_database_url, tmp_path):
    from scrooner_pipeline.mapper.company_tag_map_seed import seed

    with psycopg.connect(isolated_database_url) as conn:
        x = _seed(conn)
        inv = _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode) values ('tm_inventory','balance_sheet','first_match') returning id")
        conn.execute("insert into analytics.canonical_concept (name, statement, combination_mode) values ('total_debt_resolved','balance_sheet','first_match') on conflict (name) do nothing")
        co, *_ = x["company"]("0000000901", True)
        conn.commit()
        f = tmp_path / "m.csv"
        head = "company_id,taxonomy,tag,stmt,decision,parent_concept,sign,era_from,decided_by,rule_id\n"
        f.write_text(head + f"{co},us-gaap,Raw,BS,component,tm_inventory,1,2015-01-01,t,tm.r@1\n" + f"{co},us-gaap,Notes,BS,component,total_debt_resolved,1,2015-01-01,t,tm.r@1\n" + f"{co},us-gaap,Opex1,IS,component,tm_rev,1,2015-01-01,t,tm.r@1\n")
        st = seed(conn, f)
        assert [r["parent_concept"] for r in st["refused_instant_components"]] == ["tm_inventory"]
        assert len(st["errors"]) == 1 and "instant component sum refused" in st["errors"][0]
        assert inv
