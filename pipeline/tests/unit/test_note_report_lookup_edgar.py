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
