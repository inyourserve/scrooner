"""Research tool for doc/scoping/37_Scrooner_Segment_Revenue_Scoping.md --
NOT part of the production pipeline (not imported by any job, no
CLI wiring) -- a one-off/rerunnable script that generates the reference
data file `pipeline/reference/segment_report_index.json`, so a future
build of the actual segment-revenue fetcher doesn't need to rediscover
which report each of the top 100 companies uses.

What it does, per company: finds the single most recent 10-Q or 10-K
(whichever was filed later -- doc 37's own "one filing, no backfill"
correction), fetches that filing's real FilingSummary.xml, and records
every report whose title suggests it holds segment or disaggregated-
revenue data.

Why report TITLE, not R-number, is what gets stored: R-number (R38.htm,
R68.htm, etc.) is NOT stable across a company's own filings -- it's a
per-filing sequential rendering order that shifts if any disclosure is
added/removed/reordered in a later filing. A company's own title text
for a given disclosure ("Segment Information", "Revenue - Disaggregated
Net Sales...") is far more stable quarter to quarter, since it comes
from the company's own XBRL element/label choices, which rarely change.
Storing titles (not R-numbers) means a future fetch just re-reads that
filing's own FilingSummary.xml at fetch time to resolve the CURRENT
R-number for that title -- cheap, and correct even if the company's
own numbering has shifted since this index was built.

This is a genuinely new fetch pattern for this project (see doc 37):
individual filing documents, not the bulk Company Facts JSON API. Uses
the shared, now-cross-process-safe SECClient rate limiter (fixed
2026-08-29/30) so running this alongside any other SEC-fetching job is
safe.
"""

import json
import re
import sys
from pathlib import Path

from scrooner_pipeline.common.sec_client import SECClient

# Widened 2026-08-30 after a real miss: American Airlines has no
# "Segment"/"Disaggregat"-titled note at all (correctly single-segment
# under ASC 280) but DOES have real geographic revenue data, filed under
# "Revenue Recognition - Passenger Revenue by Geographic Region
# (Details)" -- a company-specific title choice for the same underlying
# ASC 606 disclosure. Checked live before widening rather than guessing:
# confirmed by fetching AAL's actual FilingSummary.xml directly.
SEGMENT_TITLE_PATTERN = re.compile(
    r"segment|disaggregat|revenue.*(geographic|by region|by product|by category)",
    re.IGNORECASE,
)
# "(Tables)"/"(Policies)" reports are XBRL presentation scaffolding with
# no actual values -- only "(Details)" or a bare disclosure title
# (no "(Tables)"/"(Policies)" suffix) carries real numbers.
SCAFFOLDING_SUFFIX_PATTERN = re.compile(r"\((Tables|Policies)\)\s*$", re.IGNORECASE)

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "reference" / "segment_report_index.json"


def _latest_10q_or_10k(client: SECClient, cik: str) -> dict | None:
    padded = cik.zfill(10)
    data = client.get_json(f"https://data.sec.gov/submissions/CIK{padded}.json")
    recent = data["filings"]["recent"]
    best = None
    for i, form in enumerate(recent["form"]):
        if form not in ("10-Q", "10-K"):
            continue
        filing_date = recent["filingDate"][i]
        if best is None or filing_date > best["filing_date"]:
            best = {
                "form": form,
                "filing_date": filing_date,
                "accession_number": recent["accessionNumber"][i],
            }
    return best


def _filing_summary_reports(client: SECClient, cik_int: int, accession_number: str) -> list[dict]:
    accession_nodash = accession_number.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_nodash}/"
    response = client.get(base + "FilingSummary.xml")
    text = response.text
    reports = []
    for match in re.finditer(r"<Report[^>]*>.*?</Report>", text, re.S):
        block = match.group(0)
        html_name = re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", block)
        short_name = re.search(r"<ShortName>(.*?)</ShortName>", block)
        if html_name and short_name:
            reports.append({"html_file": html_name.group(1), "title": short_name.group(1).strip()})
    return reports


def build_index(companies: list[dict]) -> dict:
    index: dict[str, dict] = {}
    with SECClient() as client:
        for company in companies:
            cik = company["cik"]
            ticker = company["ticker"]
            try:
                filing = _latest_10q_or_10k(client, cik)
                if filing is None:
                    index[cik] = {"ticker": ticker, "company_name": company["company_name"], "status": "no_10q_or_10k_found"}
                    continue
                reports = _filing_summary_reports(client, int(cik), filing["accession_number"])
                candidates = [
                    {**r, "likely_tabular": "(Details)" in r["title"]}
                    for r in reports
                    if SEGMENT_TITLE_PATTERN.search(r["title"]) and not SCAFFOLDING_SUFFIX_PATTERN.search(r["title"])
                ]
                # A bare title with no "(Details)"/"(Tables)"/"(Policies)" suffix
                # is usually the disclosure's narrative text, not a data table
                # (confirmed live: Apple's own "Segment Information" -- no
                # suffix -- vs. "...Information by Reportable Segment
                # (Details)", which is the real numbers) -- likely_tabular
                # flags this so a future fetch can skip the narrative ones
                # without re-deriving this distinction from scratch.
                index[cik] = {
                    "ticker": ticker,
                    "company_name": company["company_name"],
                    "status": "found" if candidates else "no_segment_disclosure_matched",
                    "source_filing": {"form": filing["form"], "filing_date": filing["filing_date"], "accession_number": filing["accession_number"]},
                    "candidate_reports": candidates,
                }
                print(f"{ticker}: {filing['form']} {filing['filing_date']} -> {len(candidates)} candidate report(s)", file=sys.stderr)
            except Exception as exc:  # noqa: BLE001 -- research script, log and continue past any one company's failure
                index[cik] = {"ticker": ticker, "company_name": company["company_name"], "status": "error", "error": repr(exc)}
                print(f"{ticker}: ERROR {exc!r}", file=sys.stderr)
    return index


def main() -> None:
    import csv

    companies = []
    with open(sys.argv[1]) as f:
        # pipe-delimited, not comma -- several real company names contain a
        # literal comma ("Cencora, Inc."), which broke a naive comma-CSV
        # split on first run.
        for row in csv.reader(f, delimiter="|"):
            cik, ticker, company_name, _revenue = row
            companies.append({"cik": cik, "ticker": ticker, "company_name": company_name})

    index = build_index(companies)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(index, indent=2, sort_keys=True))
    found = sum(1 for v in index.values() if v.get("status") == "found")
    print(f"\n{found}/{len(index)} companies matched a candidate segment/disaggregation report.", file=sys.stderr)
    print(f"Written to {OUTPUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
