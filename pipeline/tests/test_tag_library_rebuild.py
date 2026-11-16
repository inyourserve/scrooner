from datetime import date
from decimal import Decimal as D
from pathlib import Path

import pytest

from scrooner_pipeline.mapper import tag_library_rebuild as t

RESOLVER_HEADER = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_node_tags_reads_tags_before_why():
    nodes = "Assets=74252000000.0000 [R4.htm:13]; us-gaap:Liabilities [NOTE] | why: BS R4 line 13 Foo=1"
    assert t.node_tags(nodes) == ["Assets", "Liabilities"]


def test_parse_resolver_keeps_decimal_and_rejects_bad_rows(tmp_path):
    p = write(
        tmp_path / "resolver-all110-2026-11-14.csv",
        RESOLVER_HEADER
        + "64803,CVS,total_assets,2014-12-31,I,mapped,Assets=1 [R4.htm:13] | why: x,74252000000.1234,0000064803-15-000008,own,ok,core,v1\n"
        + "0000064803,CVS,goodwill,2014-12-31,I,combined,,,,own,,core,v1\n"
        + "0000064803,CVS,bad,2014-12-31,I,not_a_decision,,,,own,,core,v1\n"
        + "0000064803,CVS,bad2,2014-99-31,I,mapped,,1,,own,,core,v1\n",
    )
    rows, rejects = t.parse_resolver(p)
    assert len(rows) == 2 and len(rejects) == 2
    first = next(r for r in rows if r["data_point"] == "total_assets")
    assert first["cik"] == "0000064803"
    assert first["value"] == D("74252000000.1234") and isinstance(first["value"], D)
    assert first["node_tags"] == ["Assets"]
    assert next(r for r in rows if r["data_point"] == "goodwill")["value"] is None


def test_newest_resolver_file_picks_latest_date(tmp_path):
    for n in (
        "resolver-all110-2026-11-14.csv",
        "resolver-all110-2026-11-16.csv",
        "resolver-bs-2026-11-20.csv",
    ):
        write(tmp_path / n, "")
    assert t.newest_resolver_file(tmp_path).name == "resolver-all110-2026-11-16.csv"


RULE_HEADER = "rule_id,version,namespace,data_point,scope,era,kind,when,then,precedence,evidence,author,date,note\n"


def test_parse_rules_prefers_lowest_order_and_skips_other_kinds(tmp_path):
    write(
        tmp_path / "is.csv",
        RULE_HEADER
        + 'lib.is.A,1,is,revenue,all,,tag,"{""stmt"":""IS"",""tag"":""Revenues"",""order"":2}","{""decision"":""map"",""concept"":""revenue""}",p,e,a,d,n1\n'
        + 'lib.is.B,1,is,revenue,all,,tag,"{""stmt"":""IS"",""tag"":""Revenues"",""order"":1}","{""decision"":""map"",""concept"":""revenue""}",p,e,a,d,n2\n'
        + 'c.X,1,company,revenue,X,,override,"{""cik"":""1"",""tag"":""Revenues"",""stmt"":""IS""}","{}",p,e,a,d,\n',
    )
    rules = t.parse_rules(tmp_path)
    assert list(rules) == [("IS", "Revenues")]
    assert rules[("IS", "Revenues")]["rule_id"] == "lib.is.B"


def test_polarity_classes(tmp_path):
    p = write(
        tmp_path / "p.csv",
        "data_point,sign,normalise,why\ncapex,+,Y,x\ncfo,±,N,x\ncf_ar_change,raw,N,x\n",
    )
    assert t.parse_polarity(p) == {
        "capex": "positive",
        "cfo": "signed",
        "cf_ar_change": "raw",
    }


def test_certified_company_ids(tmp_path):
    write(
        tmp_path / "MSFT-certificate-2026-11-14.md",
        "**Certified:** MSFT (company_id 4), x",
    )
    write(
        tmp_path / "BA-request-2026-11-15.md", "Certification request: BA (company 207)"
    )
    assert t.certified_company_ids(tmp_path) == {4}


def tm(
    tag,
    stmt="IS",
    role="concept",
    concept="revenue_resolved",
    companies=3,
    rows=10,
    rules=("company_tag_map.structural@1",),
    tax="us-gaap",
):
    return {
        "taxonomy": tax,
        "tag": tag,
        "stmt": stmt,
        "role": role,
        "concept": concept,
        "companies": companies,
        "rows": rows,
        "rule_ids": list(rules),
        "reason_class": None,
    }


def pf(tag, stmt, dp, proven=0, certified=0, disagree=0, unchecked=0, last=None):
    return {
        "tag": tag,
        "stmt": stmt,
        "data_point": dp,
        "proven": proven,
        "certified": certified,
        "disagree": disagree,
        "unchecked": unchecked,
        "last_proved": last,
    }


def src():
    return t.Sources(
        rules={
            ("IS", "Revenues"): {
                "rule_id": "lib.is.Revenues",
                "version": 1,
                "namespace": "is",
                "data_point": "revenue",
                "decision": "map",
                "concept": "revenue",
                "parent_concept": "",
                "reason_class": "",
                "note": "sign flips",
                "order": 1,
            },
            ("IS", "LibOnly"): {
                "rule_id": "lib.is.LibOnly",
                "version": 1,
                "namespace": "is",
                "data_point": "interest_expense",
                "decision": "map",
                "concept": "interest_expense_resolved",
                "parent_concept": "",
                "reason_class": "",
                "note": "",
                "order": 1,
            },
        },
        caveats={("IS", "Revenues"): "subset for banks"},
        polarity={"revenue": "signed", "interest_expense": "positive"},
        deprecations={"Revenues": ("RevenueFromContract", None)},
    )


def test_build_entries_counts_each_cell_once_and_carries_library_fields():
    entries = t.build_entries(
        [
            tm("Revenues"),
            tm("Revenues", companies=1, rows=2, tax="nee"),
            tm("Dup", stmt="CF", role="excluded", concept=""),
        ],
        [
            pf(
                "Revenues",
                "IS",
                "revenue_resolved",
                proven=100,
                certified=40,
                disagree=2,
                last=date(2026, 11, 14),
            ),
            pf(
                "Revenues",
                "IS",
                "revenue",
                proven=1,
                certified=0,
                last=date(2026, 11, 15),
            ),
        ],
        src(),
    )
    by = {(e["taxonomy"], e["tag"]): e for e in entries}
    rev = by[("us-gaap", "Revenues")]
    assert (rev["proven_cells"], rev["certified_cells"], rev["disagree_cells"]) == (
        101,
        40,
        2,
    )
    assert rev["last_verified"] == date(2026, 11, 15)
    assert by[("nee", "Revenues")]["proven_cells"] == 0  # never double counted
    assert rev["polarity"] == "signed" and rev["family"] == "is"
    assert (
        rev["library_rule_id"] == "lib.is.Revenues"
        and rev["deprecated_by"] == "RevenueFromContract"
    )
    assert any("subset for banks" in p for p in rev["known_problems"])
    assert any("2 cell_proof DISAGREE" in p for p in rev["known_problems"])
    assert by[("us-gaap", "Dup")]["data_point"] == ""
    assert by[("us-gaap", "Dup")]["family"] == "cf"


def test_library_only_rule_becomes_zero_count_entry_and_conflict_is_a_problem():
    entries = t.build_entries([tm("Revenues", role="excluded", concept="")], [], src())
    lib = next(e for e in entries if e["tag"] == "LibOnly")
    assert (lib["companies_mapped"], lib["proven_cells"]) == (0, 0) and lib[
        "polarity"
    ] == "positive"
    rev = next(e for e in entries if e["tag"] == "Revenues")
    assert any(
        "says map; company_tag_map holds it as excluded for 3 companies" in p
        for p in rev["known_problems"]
    )


def test_content_hash_is_stable_and_sensitive():
    a = t.build_entries([tm("Revenues")], [], src())
    b = t.build_entries([tm("Revenues")], [], src())
    c = t.build_entries([tm("Revenues", companies=4)], [], src())
    assert [e["content_hash"] for e in a] == [e["content_hash"] for e in b]

    def h(es):
        return next(e["content_hash"] for e in es if e["tag"] == "Revenues")

    assert h(a) != h(c)


def test_with_company_ids_drops_unknown_and_ambiguous():
    cells = [
        {"cik": "0000000001", "data_point": "x"},
        {"cik": "0000000002", "data_point": "x"},
        {"cik": "0000000003", "data_point": "x"},
    ]
    rows, stats = t.with_company_ids(cells, {"0000000001": 7, "0000000002": None})
    assert [r["company_id"] for r in rows] == [7]
    assert stats == {"unknown_cik": 1, "ambiguous_cik": 1}


def test_plan_counts():
    assert t.plan(
        {("a",): "1", ("b",): "1", ("c",): "1"}, {("a",): "1", ("b",): "2", ("d",): "1"}
    ) == {"insert": 1, "update": 1, "unchanged": 1, "delete": 1}


class FakeCur:
    def __init__(self, have):
        self.have, self.last = have, None

    def execute(self, sql, params=None):
        self.last = params

    def fetchall(self):
        return [(c,) for c in self.have.get(self.last[0], [])]


def test_check_migration_refuses_with_clear_message():
    with pytest.raises(
        t.MigrationMissing,
        match="migration 0128.*analytics.tag_library_entry \\(table\\)",
    ):
        t.check_migration(FakeCur({}))
    partial = {
        "tag_library_entry": [
            c for c in t.REQUIRED_COLUMNS["tag_library_entry"] if c != "known_problems"
        ],
        "resolver_decision": list(t.REQUIRED_COLUMNS["resolver_decision"]),
    }
    with pytest.raises(t.MigrationMissing, match="tag_library_entry.known_problems"):
        t.check_migration(FakeCur(partial))
    t.check_migration(FakeCur({k: list(v) for k, v in t.REQUIRED_COLUMNS.items()}))


def test_apply_refused_off_main():
    with pytest.raises(PermissionError):
        t.rebuild(object(), apply=True, github_ref="refs/heads/work/x")


def test_repo_files_parse_and_cover_every_resolver_decision():
    """The committed sources load: newest resolver file, rules, polarity (catches a format change)."""
    rows, rejects = t.parse_resolver(t.newest_resolver_file())
    assert rows and not rejects
    assert t.parse_rules() and t.parse_polarity()


def test_not_in_template_is_stored_and_an_unknown_decision_is_rejected(tmp_path):
    head = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"
    f = tmp_path / "resolver-all110-2026-01-01.csv"
    f.write_text(
        head
        + "0000000001,AAA,net_interest_income,2020-12-31,FY,not_in_template,,,,,,,v\n"
        + "0000000001,AAA,total_assets,2020-12-31,I,brand_new_value,,5,,,,,v\n"
    )
    rows, rejects = t.parse_resolver(f)
    assert [(r["data_point"], r["decision"], r["value"]) for r in rows] == [("net_interest_income", "not_in_template", None)]
    assert len(rejects) == 1 and "brand_new_value" in rejects[0]
    mig = (Path(__file__).resolve().parents[1] / "db/pending/0128_company_tag_metric_library.sql").read_text()
    assert "'not_in_template'" in mig.split("analytics.resolver_decision (")[1].split("node_tags")[0]
