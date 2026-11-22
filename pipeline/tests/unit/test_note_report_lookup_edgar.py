"""scan_edgar reads FilingSummary once, skips Cover, Statements then Details first, stops at the first full hit."""

from types import SimpleNamespace

from scrooner_pipeline.mapper import note_report_lookup as nl

SUMMARY = b"""<FilingSummary><MyReports>
<Report><HtmlFileName>R1.htm</HtmlFileName><MenuCategory>Cover</MenuCategory></Report>
<Report><HtmlFileName>R2.htm</HtmlFileName><MenuCategory>Statements</MenuCategory></Report>
<Report><HtmlFileName>R7.htm</HtmlFileName><MenuCategory>Notes</MenuCategory></Report>
<Report><HtmlFileName>R9.htm</HtmlFileName><MenuCategory>Details</MenuCategory></Report>
<Report><HtmlFileName>R10.htm</HtmlFileName><MenuCategory>Details</MenuCategory></Report>
<Report><HtmlFileName>R11.htm</HtmlFileName><MenuCategory>Details</MenuCategory></Report>
</MyReports></FilingSummary>"""

HITS = {"R10.htm": "defref_us-gaap_DebtCurrent'", "R11.htm": "defref_us-gaap_DebtCurrent'"}


class Client:
    def __init__(self):
        self.urls = []

    def get(self, url):
        name = url.rsplit("/", 1)[1]
        self.urls.append(name)
        if name == "FilingSummary.xml":
            return SimpleNamespace(content=SUMMARY)
        return SimpleNamespace(text=HITS.get(name, ""))


def test_stops_at_first_page_and_skips_statements():
    c = Client()
    got = nl.scan_edgar(c, 1, "0000000001-22-000001", {"DebtCurrent"})
    assert got == {"DebtCurrent": (10, 1)}
    assert c.urls == ["FilingSummary.xml", "R2.htm", "R9.htm", "R10.htm"]


def test_a_part_on_the_statement_face_is_found_there():
    c = Client()
    HITS["R2.htm"] = "defref_us-gaap_DebtCurrent'"
    try:
        got = nl.scan_edgar(c, 1, "0000000001-22-000001", {"DebtCurrent"})
    finally:
        del HITS["R2.htm"]
    assert got == {"DebtCurrent": (2, 1)}
    assert c.urls == ["FilingSummary.xml", "R2.htm"]


SUMMARY_PRE = b"""<FilingSummary><InputFiles><File>x-20161231.xml</File><File>x-20161231_pre.xml</File></InputFiles>
<MyReports>
<Report><HtmlFileName>R1.htm</HtmlFileName><MenuCategory>Cover</MenuCategory><Role>http://x.com/role/Cover</Role></Report>
<Report><HtmlFileName>R2.htm</HtmlFileName><MenuCategory>Statements</MenuCategory><Role>http://x.com/role/BS</Role></Report>
<Report><HtmlFileName>R9.htm</HtmlFileName><MenuCategory>Details</MenuCategory><Role>http://x.com/role/D9</Role></Report>
<Report><HtmlFileName>R10.htm</HtmlFileName><MenuCategory>Details</MenuCategory><Role>http://x.com/role/D10</Role></Report>
<Report><HtmlFileName>R11.htm</HtmlFileName><MenuCategory>Details</MenuCategory><Role>http://x.com/role/D11</Role></Report>
</MyReports></FilingSummary>"""

PRE = """<linkbase>
<link:presentationLink xlink:role="http://x.com/role/BS" xlink:type="extended">
<link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2016/elts/us-gaap-2016-01-31.xsd#us-gaap_Assets" xlink:type="locator"/>
</link:presentationLink>
<link:presentationLink xlink:role="http://x.com/role/D10" xlink:type="extended"/>
<link:presentationLink xlink:role="http://x.com/role/D11" xlink:type="extended">
<link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2016/elts/us-gaap-2016-01-31.xsd#us-gaap_AllocatedShareBasedCompensationExpense" xlink:type="locator"/>
</link:presentationLink>
</linkbase>"""


class PreClient(Client):
    def get(self, url):
        name = url.rsplit("/", 1)[1]
        self.urls.append(name)
        if name == "FilingSummary.xml":
            return SimpleNamespace(content=SUMMARY_PRE)
        if name.endswith("_pre.xml"):
            return SimpleNamespace(text=PRE)
        page = {"R11.htm": "defref_us-gaap_AllocatedShareBasedCompensationExpense'"}
        return SimpleNamespace(text=page.get(name, ""))


def test_the_presentation_linkbase_names_the_only_pages_to_open():
    """PM sbc: the filing's _pre.xml presents the tag on one report: open that page alone, confirm its defref."""
    c = PreClient()
    tag = "AllocatedShareBasedCompensationExpense"
    assert nl.scan_edgar(c, 1, "0000000001-17-000001", {tag}) == {tag: (11, 1)}
    assert c.urls == ["FilingSummary.xml", "x-20161231_pre.xml", "R11.htm"]
    # a tag the linkbase presents nowhere: no page is opened one by one
    c = PreClient()
    assert nl.scan_edgar(c, 1, "0000000001-17-000001", {"InterestPaid"}) == {}
    assert c.urls == ["FilingSummary.xml", "x-20161231_pre.xml"]
