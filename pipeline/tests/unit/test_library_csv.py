"""The DB loaders read the one tag library (data-team/tags/library/library.csv) instead of re-deriving element
knowledge (SYSTEMS.md #6, 2026-11-22). These pin the reader and the committed library's contract with them."""

import csv

from scrooner_pipeline.common.polarity import POLARITY_CSV
from scrooner_pipeline.mapper import library_csv as L

HEAD = "element,taxonomy,data_point,polarity,deprecated_by,replaces,legacy_caveat,legacy_decision,known_problems,company_overrides,metrics,served_cells,proven_cells,certified_cells,full_row\n"


def _lib(tmp_path, body):
    p = tmp_path / "library.csv"
    p.write_text(HEAD + body, encoding="utf-8")
    return L.load(p)


def test_knowledge_parses_polarity_deprecations_caveats_problems(tmp_path):
    rows = _lib(
        tmp_path,
        "A,us-gaap,capex,capex:positive,,,,,,,,,,,\n"
        "B,us-gaap,cfo;fcf,cfo:signed;fcf:raw,C@2018;D@2018,,misuse,,p1;p2,,,,,,\n"
        "C,us-gaap,,,,B@2018;Z@2017,,,,,,,,,\n",
    )
    k = L.knowledge(rows)
    assert k.polarity == {"capex": "positive", "cfo": "signed", "fcf": "raw"}
    assert k.deprecations == {"B": ("C;D", None), "C": (None, "B;Z")}
    assert k.caveats == {"B": "misuse"}
    assert k.problems == {"B": ["p1", "p2"]}


def test_mapping_status_and_sec_tag_library_rows(tmp_path):
    rows = _lib(
        tmp_path,
        "Full,us-gaap,revenue,,,,,,,,m_rev,10,5,0,yes\n"
        "Served,us-gaap,capex,,,,,,,,,3,0,0,no\n"
        "Alt,us-gaap,capex,,,,,,,,,,,,no\n"
        "Over,us-gaap,,,,,,,,ACME:x:FILING-CHECKED,,,,,no\n"
        "Excl,us-gaap,,,,,,excluded,,,,,,,no\n"
        "Nothing,us-gaap,,,,,,,,,,,,,no\n"
        "AcmeCustom,custom,revenue,,,,,,,,,2,0,0,no\n",
    )
    got = {r[1]: r for r in L.sec_tag_library_rows(rows)}
    assert got["Full"] == ("us-gaap", "Full", "approved", ["revenue"], [], ["m_rev"])
    assert got["Served"][2:5] == ("provisional", ["capex"], [])
    assert got["Alt"][2:5] == ("candidate", [], ["capex"])
    assert got["Over"][2] == "company_preference"
    assert got["Excl"][2] == "rejected"
    assert "Nothing" not in got
    assert (
        got["AcmeCustom"][0] == "*"
    )  # an extension joins by tag name to non-us-gaap concepts


def test_committed_library_carries_the_polarity_class_of_every_polarity_rule(archived_repo_file):
    """library.csv's polarity is the class the DB columns expect (positive/signed/raw), for every data point in
    rules/polarity.csv: the rebuild no longer reads polarity.csv itself."""
    with POLARITY_CSV.open(newline="", encoding="utf-8") as fh:
        want = {}
        for r in csv.DictReader(fh):
            sign, norm = r["sign"].strip(), r["normalise"].strip().upper()
            want[r["data_point"].strip()] = (
                "positive"
                if sign == "+" and norm == "Y"
                else "raw"
                if sign == "raw"
                else "signed"
            )
    archived_repo_file("data-team/tags/library/library.csv")  # skips only when Storage is not configured
    k = L.knowledge(L.load())
    assert {dp: k.polarity.get(dp) for dp in want} == want
    assert len(k.deprecations) > 1000 and any(v[1] for v in k.deprecations.values())
    assert L.built_for().startswith("resolver-")
