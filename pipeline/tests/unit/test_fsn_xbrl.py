"""EDGAR XBRL -> FSN rows (fsn_store.xbrl_fsn): the rules, and equivalence with the SEC FSN set on two
real filings (META 10-Q and NextEra's combined NEE/FPL 10-Q, both in the 2026m10 set). No database.

The fixtures hold each filing's EDGAR files byte for byte (instance, schema, linkbases,
FilingSummary.xml, MetaLinks.json, the cover and statement R pages, the index header) and the same
accession's rows of the SEC set 2026m10 (sub, num, pre, cal, ren). The 20-filing run is
pipeline/scripts/results/fsn_xbrl_equivalence/summary.md."""

from __future__ import annotations

import csv
import io
import json
import tarfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from scrooner_pipeline.fsn_store import edgar_fetch, xbrl_fsn
from scrooner_pipeline.fsn_store.xbrl_equivalence import compare

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "fsn_xbrl"
META = "0001628280-26-066773"
NEE = "0000753308-26-000081"


def load_fixture(
    adsh: str,
) -> tuple[xbrl_fsn.FilingFiles, dict[str, list[dict[str, str]]]]:
    files: dict[str, bytes] = {}
    expected: dict[str, list[dict[str, str]]] = {}
    with tarfile.open(FIXTURES / f"{adsh}.tar.xz") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            raw = tf.extractfile(m).read()  # type: ignore[union-attr]
            kind, name = m.name.split("/")[-2:]
            if kind == "edgar":
                files[name] = raw
            else:
                fh = io.StringIO(raw.decode("utf-8"), newline="")
                expected[name[: -len(".tsv")]] = list(
                    csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
                )
    header = json.loads(files.pop("header.json"))
    return xbrl_fsn.FilingFiles(adsh, files, header), expected


# ---------------------------------------------------------------- rules


@pytest.mark.parametrize(
    "day,want",
    [
        (date(2026, 9, 30), date(2026, 9, 30)),
        (date(2026, 10, 22), date(2026, 10, 31)),  # MSFT's cover date
        (date(2024, 9, 16), date(2024, 9, 30)),
        (
            date(2026, 2, 15),
            date(2026, 1, 31),
        ),  # COST public float: Feb 28 is nearer, FSN says Jan 31
        (date(2026, 1, 3), date(2025, 12, 31)),
        (date(2026, 8, 30), date(2026, 8, 31)),
    ],
)
def test_ddate_rounds_like_the_fsn_set(day, want):
    assert xbrl_fsn.round_month_end(day) == want


def test_versions_and_names():
    assert (
        xbrl_fsn.version_of("http://fasb.org/us-gaap/2026", "A", set())
        == "us-gaap/2026"
    )
    assert (
        xbrl_fsn.version_of("http://xbrl.sec.gov/dei/2014-01-31", "A", set())
        == "dei/2014"
    )
    assert (
        xbrl_fsn.version_of(
            "http://www.microsoft.com/20260930",
            "ACC",
            {"http://www.microsoft.com/20260930"},
        )
        == "ACC"
    )
    assert xbrl_fsn.strip_axis("StatementScenarioAxis") == "Scenario"
    assert xbrl_fsn.strip_member("ScenarioUnspecifiedDomain") == "ScenarioUnspecified"


def test_text_drops_non_ascii_and_quotes_like_the_sec_files():
    assert xbrl_fsn.fsn_text("Stockholders’ equity:") == "Stockholders equity:"
    assert xbrl_fsn.fsn_text('net"') == '"net"""'
    assert xbrl_fsn.fsn_value("1380000000") == "1380000000.0000"
    assert xbrl_fsn.fsn_value("0.00005") == "0.0001"
    assert xbrl_fsn.fsn_value(None) == ""


def test_statement_types_follow_the_fsn_set():
    r = xbrl_fsn.classify_reports(
        [
            (1, "C", "Cover", ""),
            (2, "C", "Audit Information", ""),  # MU: a second cover report has no stmt
            (3, "S", "Consolidated Balance Sheets", ""),
            (4, "S", "Consolidated Balance Sheets (Parenthetical)", ""),
            (
                5,
                "S",
                "Consolidated Statements of Comprehensive Income",
                "",
            ),  # lone CI is the IS
            (6, "S", "Consolidated Statements Of Cash Flows", ""),
            (7, "S", "Statement of Cash Flows (Parenthetical)", ""),
            (
                8,
                "S",
                "Statements of Operations (Parentheticals)",
                "",
            ),  # CB: second CF parenthetical
            (9, "S", "Consolidated Balance Sheets", ""),  # a co-registrant's copy: UN
            (
                10,
                "S",
                "Consolidated Balance Sheets (Parenthetical)",
                "",
            ),  # its parenthetical stays UN
        ]
    )
    assert r == {
        1: ("CP", 0),
        3: ("BS", 0),
        4: ("BS", 1),
        5: ("IS", 0),
        6: ("CF", 0),
        7: ("CF", 1),
        9: ("UN", 0),
        10: ("UN", 1),
    }


def test_a_cover_only_amendment_has_no_cp():
    """TECH 10-K/A (Part III, 2026m10): no statements, so the cover report carries no stmt."""
    assert (
        xbrl_fsn.classify_reports(
            [(1, "C", "Cover", ""), (2, "N", "Insider Trading", "")]
        )
        == {}
    )
    assert xbrl_fsn.classify_reports(
        [(1, "C", "Cover", ""), (2, "S", "Balance Sheets", "")]
    )[1] == ("CP", 0)


def test_index_header_parse():
    text = """<ACCEPTANCE-DATETIME>20261021171819
CONFORMED SUBMISSION TYPE:\t10-Q
CONFORMED PERIOD OF REPORT:\t20260930
FILED AS OF DATE:\t\t20261021
FILER:
\t\tCOMPANY CONFORMED NAME:\t\t\tNEXTERA ENERGY INC
\t\tCENTRAL INDEX KEY:\t\t\t0000753308
FILER:
\t\tCOMPANY CONFORMED NAME:\t\t\tFLORIDA POWER &amp; LIGHT CO
\t\tCENTRAL INDEX KEY:\t\t\t0000037634
"""
    h = edgar_fetch.parse_header(text.replace("<", "&lt;").replace(">", "&gt;"))
    assert h["accepted"] == "2026-10-21 17:18:00.0"  # SEC rounds to the minute
    late = edgar_fetch.parse_header("&lt;ACCEPTANCE-DATETIME&gt;20261021201241")
    assert late["accepted"] == "2026-10-21 20:13:00.0"
    assert (h["form"], h["period"], h["filed"], h["cik"]) == (
        "10-Q",
        "2026-09-30",
        "20261021",
        "0000753308",
    )
    assert h["aciks"] == ["0000037634"]


def test_fetcher_refuses_other_hosts_and_an_undeclared_agent():
    with pytest.raises(ValueError):
        edgar_fetch.EdgarClient("no contact")
    client = edgar_fetch.EdgarClient("Scrooner test test@example.com")
    with pytest.raises(ValueError):
        client.get("https://data.example.com/x")
    client.close()


# ---------------------------------------------------------------- equivalence on real filings


@pytest.mark.parametrize("adsh", [META, NEE])
def test_edgar_build_equals_the_fsn_set(adsh):
    files, expected = load_fixture(adsh)
    got = xbrl_fsn.convert(files)
    res = compare(expected, got)
    assert res["num"]["missing"] == 0 and res["num"]["extra"] == 0, res["num"][
        "examples"
    ]
    assert not {
        k: v for k, v in res["num"]["column_diffs"].items() if k != "footnote"
    }, res["num"]
    assert res["pre"]["pass_exact"], res["pre"]
    assert res["cal"]["pass"], res["cal"]
    assert res["sub"]["pass"], res["sub"]
    assert res["pass"]


def test_nee_coregistrant_values_keep_their_entity():
    """FPL's own balance sheet: LegalEntityAxis alone -> coreg and still a dimension (dimh != 0)."""
    files, _ = load_fixture(NEE)
    got = xbrl_fsn.convert(files)
    fpl = [
        r
        for r in got["num"]
        if r["coreg"] == "FloridaPowerLightCompany" and r["tag"] == "Assets"
    ]
    assert fpl and all(r["dimh"] != xbrl_fsn.NO_DIM and r["dimn"] == "1" for r in fpl)
    consolidated = [
        r
        for r in got["num"]
        if r["tag"] == "Assets" and r["dimh"] == xbrl_fsn.NO_DIM and r["iprx"] == "0"
    ]
    assert {r["ddate"] for r in consolidated} == {"20251231", "20260930"}
    assert all(Decimal(r["value"]) > 0 for r in consolidated)
    assert got["sub"][0]["aciks"] == "37634"


def test_meta_statement_lines_and_values():
    files, _ = load_fixture(META)
    got = xbrl_fsn.convert(files)
    bs = [r for r in got["pre"] if r["stmt"] == "BS" and r["inpth"] == "0"]
    assert bs[0]["tag"] == "AssetsAbstract" and any(
        r["tag"] == "LiabilitiesAndStockholdersEquity" for r in bs
    )
    rev = [
        r
        for r in got["num"]
        if r["tag"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
        and r["dimh"] == xbrl_fsn.NO_DIM
        and r["qtrs"] == "1"
        and r["iprx"] == "0"
    ]
    # the 10-Q's own quarter and its prior-year comparative, as printed (SEC set 2026m10)
    assert {(r["ddate"], r["value"], r["uom"], r["dcml"]) for r in rev} == {
        ("20250930", "51242000000.0000", "USD", "-6"),
        ("20260930", "64601000000.0000", "USD", "-6"),
    }


# ---------------------------------------------------------------- a synthetic filing (the rules the real fixtures do not exercise)

ACC = "0000000001-26-000001"
INSTANCE = b"""<?xml version="1.0"?>
<xbrl xmlns="http://www.xbrl.org/2003/instance" xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
      xmlns:us-gaap="http://fasb.org/us-gaap/2026" xmlns:x="http://example.com/20260930"
      xmlns:iso4217="http://www.xbrl.org/2003/iso4217">
 <context id="i"><entity><identifier scheme="http://www.sec.gov/CIK">1</identifier></entity><period><instant>2026-09-30</instant></period></context>
 <context id="d"><entity><identifier scheme="http://www.sec.gov/CIK">1</identifier>
  <segment><xbrldi:typedMember dimension="us-gaap:StatementOfIncomeLocationBalanceAxis"><us-gaap:QName.domain>us-gaap:Revenues</us-gaap:QName.domain></xbrldi:typedMember>
   <xbrldi:explicitMember dimension="x:ZetaAxis">x:OneMember</xbrldi:explicitMember>
   <xbrldi:explicitMember dimension="us-gaap:ConsolidationItemsAxis">us-gaap:OperatingSegmentsMember</xbrldi:explicitMember></segment></entity>
  <period><instant>2026-09-30</instant></period></context>
 <unit id="usd"><measure>iso4217:USD</measure></unit>
 <us-gaap:Assets contextRef="i" unitRef="usd" decimals="-6">100</us-gaap:Assets>
 <us-gaap:AssetsCurrent contextRef="i" unitRef="usd" decimals="-6">60</us-gaap:AssetsCurrent>
 <us-gaap:AssetsCurrent contextRef="i" unitRef="usd" decimals="-3">60000</us-gaap:AssetsCurrent>
 <us-gaap:AssetsNoncurrent contextRef="d" unitRef="usd" decimals="-6">40</us-gaap:AssetsNoncurrent>
</xbrl>"""
SCHEMA = b"""<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:link="http://www.xbrl.org/2003/linkbase"
  xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xbrli="http://www.xbrl.org/2003/instance" targetNamespace="http://example.com/20260930">
 <xs:element id="x_ZetaAxis" name="ZetaAxis" abstract="true"/>
 <xs:element id="x_OneMember" name="OneMember" abstract="true"/>
 <xs:element id="x_UnusedAxis" name="UnusedAxis" abstract="true"/>
 <xs:element id="x_UnusedDomain" name="UnusedDomain" abstract="true"/>
 <xs:annotation><xs:appinfo><link:linkbase>
  <link:presentationLink xlink:type="extended" xlink:role="http://example.com/role/BS">
   <link:loc xlink:type="locator" xlink:label="root" xlink:href="us-gaap.xsd#us-gaap_StatementOfFinancialPositionAbstract"/>
   <link:loc xlink:type="locator" xlink:label="ax" xlink:href="x.xsd#x_UnusedAxis"/>
   <link:loc xlink:type="locator" xlink:label="dom" xlink:href="x.xsd#x_UnusedDomain"/>
   <link:loc xlink:type="locator" xlink:label="ab" xlink:href="us-gaap.xsd#us-gaap_AssetsAbstract"/>
   <link:loc xlink:type="locator" xlink:label="ac" xlink:href="us-gaap.xsd#us-gaap_AssetsCurrent"/>
   <link:loc xlink:type="locator" xlink:label="cc" xlink:href="us-gaap.xsd#us-gaap_CommitmentsAndContingencies"/>
   <link:loc xlink:type="locator" xlink:label="a" xlink:href="us-gaap.xsd#us-gaap_Assets"/>
   <link:presentationArc xlink:type="arc" xlink:from="root" xlink:to="ax" order="1"/>
   <link:presentationArc xlink:type="arc" xlink:from="ax" xlink:to="dom" order="1"/>
   <link:presentationArc xlink:type="arc" xlink:from="root" xlink:to="ab" order="2"/>
   <link:presentationArc xlink:type="arc" xlink:from="ab" xlink:to="ac" order="1" preferredLabel="http://www.xbrl.org/2003/role/terseLabel"/>
   <link:presentationArc xlink:type="arc" xlink:from="ab" xlink:to="a" order="3" preferredLabel="http://www.xbrl.org/2003/role/totalLabel"/>
   <link:presentationArc xlink:type="arc" xlink:from="root" xlink:to="cc" order="3"/>
  </link:presentationLink>
  <link:calculationLink xlink:type="extended" xlink:role="http://example.com/role/BS">
   <link:loc xlink:type="locator" xlink:label="a" xlink:href="us-gaap.xsd#us-gaap_Assets"/>
   <link:loc xlink:type="locator" xlink:label="ac" xlink:href="us-gaap.xsd#us-gaap_AssetsCurrent"/>
   <link:loc xlink:type="locator" xlink:label="other" xlink:href="us-gaap.xsd#us-gaap_OtherAssetsNoncurrent"/>
   <link:calculationArc xlink:type="arc" xlink:from="a" xlink:to="ac" weight="1"/>
   <link:calculationArc xlink:type="arc" xlink:from="a" xlink:to="other" weight="-1"/>
  </link:calculationLink>
  <link:labelLink xlink:type="extended">
   <link:loc xlink:type="locator" xlink:label="ac" xlink:href="us-gaap.xsd#us-gaap_AssetsCurrent"/>
   <link:label xlink:type="resource" xlink:label="l_ac" xlink:role="http://www.xbrl.org/2003/role/terseLabel">Total current assets</link:label>
   <link:labelArc xlink:type="arc" xlink:from="ac" xlink:to="l_ac"/>
  </link:labelLink>
 </link:linkbase></xs:appinfo></xs:annotation>
</xs:schema>"""
SUMMARY = b"""<FilingSummary><MyReports>
 <Report><HtmlFileName>R2.htm</HtmlFileName><LongName>100 - Statement - Balance Sheets</LongName>
  <Role>http://example.com/role/BS</Role><ShortName>Balance Sheets</ShortName><MenuCategory>Statements</MenuCategory></Report>
</MyReports></FilingSummary>"""
# the renderer shows the abstract, the current assets and the total, not the empty commitments row
R2 = b"""<a onclick="Show.showAR( this, 'defref_us-gaap_AssetsAbstract', window );"></a>
<a onclick="Show.showAR( this, 'defref_us-gaap_AssetsCurrent', window );"></a>
<a onclick="Show.showAR( this, 'defref_us-gaap_Assets', window );"></a>"""


def synthetic() -> dict[str, list[dict[str, str]]]:
    files = {
        "x-20260930_htm.xml": INSTANCE,
        "x-20260930.xsd": SCHEMA,
        "FilingSummary.xml": SUMMARY,
        "R2.htm": R2,
    }
    return xbrl_fsn.convert(
        xbrl_fsn.FilingFiles(ACC, files, {"cik": "1", "form": "10-Q"})
    )


def test_pre_mirrors_the_rendered_page():
    pre = synthetic()["pre"]
    # the unused axis and domain and the empty commitments row are gone; the root is not numbered
    assert [(r["line"], r["tag"], r["prole"], r["plabel"]) for r in pre] == [
        ("1", "AssetsAbstract", "label", ""),
        ("2", "AssetsCurrent", "terseLabel", "Total current assets"),
        ("3", "Assets", "totalLabel", ""),
    ]
    assert {r["stmt"] for r in pre} == {"BS"}


def test_typed_axes_follow_the_explicit_ones_and_iprx_prefers_precision():
    num = synthetic()["num"]
    dim = [r for r in num if r["tag"] == "AssetsNoncurrent"][0]
    seg = "ConsolidationItems=OperatingSegments;Zeta=One;StatementOfIncomeLocationBalance=us-gaap:Revenues;"
    assert xbrl_fsn.segments_of(
        [
            ("StatementOfIncomeLocationBalanceAxis", "us-gaap:Revenues", True),
            ("ZetaAxis", "One", False),
            ("ConsolidationItemsAxis", "OperatingSegmentsMember", False),
        ]
    ) == (seg, "", 3)
    assert xbrl_fsn.segments_of(
        [("LegalEntityAxis", "FloridaPowerLightCompanyMember", False)]
    ) == (
        "LegalEntity=FloridaPowerLightCompany;",
        "FloridaPowerLightCompany",
        1,
    )
    assert dim["dimn"] == "3" and dim["dimh"] != xbrl_fsn.NO_DIM
    cur = sorted(
        (r["iprx"], r["dcml"], r["value"]) for r in num if r["tag"] == "AssetsCurrent"
    )
    assert cur == [("0", "-3", "60000.0000"), ("1", "-6", "60.0000")]


def test_no_arc_to_a_child_without_a_fact():
    cal = synthetic()["cal"]
    assert [(r["grp"], r["arc"], r["ptag"], r["ctag"], r["negative"]) for r in cal] == [
        ("1", "1", "Assets", "AssetsCurrent", "1")
    ]


# ---------------------------------------------------------------- fetch fails closed; the stage flag is off


class _FakeResp:
    def __init__(self, body: bytes):
        self.content = body
        self.text = body.decode("utf-8", "replace")

    def json(self):
        return json.loads(self.content)


class _FakeClient:
    """Serves a filing directory from a dict; a name mapped to an exception raises it."""

    def __init__(self, files: dict[str, object]):
        self.files = files

    def get(self, url: str):
        name = url.rsplit("/", 1)[-1]
        if name == "index.json":
            return _FakeResp(
                json.dumps(
                    {"directory": {"item": [{"name": n} for n in self.files]}}
                ).encode()
            )
        body = self.files[name]
        if isinstance(body, Exception):
            raise body
        return _FakeResp(body)  # type: ignore[arg-type]


def _directory() -> dict[str, object]:
    files, _ = load_fixture(META)
    out: dict[str, object] = dict(files.files)
    out[f"{META}-index-headers.html"] = (
        b"&lt;ACCEPTANCE-DATETIME&gt;20261029161000\nCONFORMED SUBMISSION TYPE:\t10-Q\n"
    )
    return out


def test_fetch_builds_the_filing_from_all_of_its_inputs():
    ff = edgar_fetch.fetch_filing(
        _FakeClient(_directory()), META.split("-")[0], META, "edgar:2026-11-11"
    )
    assert xbrl_fsn.convert(ff)["num"]


@pytest.mark.parametrize(
    "break_it", ["http_error", "missing_r_page", "no_summary", "no_instance"]
)
def test_fetch_fails_closed(break_it):
    """Any missing input fails the whole filing (never a partial build); build() reports it, loads nothing."""
    import httpx

    from scrooner_pipeline.fsn_store import increment

    d = _directory()
    instance = next(n for n in d if n.endswith("_htm.xml"))
    if break_it == "http_error":
        req = httpx.Request("GET", "https://www.sec.gov/x")
        d[instance] = httpx.HTTPStatusError(
            "404", request=req, response=httpx.Response(404, request=req)
        )
    elif break_it == "missing_r_page":
        d.pop("R2.htm")
    elif break_it == "no_summary":
        d.pop("FilingSummary.xml")
    else:
        d.pop(instance)
    client = _FakeClient(d)
    cand = increment.Candidate(
        1, "0001326801", META, "10-Q", "2026-10-29", "2026-09-30"
    )
    res = increment.build(
        [cand],
        lambda c: edgar_fetch.fetch_filing(
            client, c.cik, c.accession, "edgar:2026-11-11"
        ),
    )
    assert not res.built and [f["accession"] for f in res.failed] == [META]


def test_nightly_stage_is_off_by_default():
    import os
    import subprocess

    script = (
        Path(__file__).resolve().parents[2] / "scripts" / "fsn_nightly_incremental.sh"
    )
    env = {k: v for k, v in os.environ.items() if k != "FSN_NIGHTLY_STAGE"}
    out = subprocess.run(
        ["bash", str(script)], capture_output=True, text=True, env=env, timeout=60
    )
    assert out.returncode == 0 and "FSN_NIGHTLY_STAGE=off, skipped" in out.stdout
    wf = (
        Path(__file__).resolve().parents[3]
        / ".github"
        / "workflows"
        / "pipeline-refresh.yml"
    ).read_text()
    assert (
        "vars.FSN_NIGHTLY_STAGE || 'off'" in wf
        and "vars.HYBRID_NEW_PATH || 'off'" in wf
    )
    sanity = (
        Path(__file__).resolve().parents[3]
        / ".github"
        / "workflows"
        / "pipeline-sanity.yml"
    ).read_text()
    assert "vars.HYBRID_NEW_PATH || 'off'" in sanity
