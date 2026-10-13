"""Does a `no_line_item_filed` period gap really mean the filing has no such line?

sanity/period_completeness.py labels a missing (company, concept, period) cell
`no_line_item_filed` (finding type legitimate_absence) when the expected filing
carries no fact whose tag matches the concept's pattern. That decides from XBRL
facts, so it cannot see a line that is on the rendered statement but tagged in a way
the pattern misses. This script samples such gaps and reads the filing's own rendered
cash-flow statement (FilingSummary.xml -> R*.htm, as parsers/filing_line_evidence.py
does) to check whether the line is really absent.

  verdict "line_on_statement":  the statement HAS the line -> the gap is NOT legitimate
                                (an unmapped / custom tag, or a fact we failed to read)
  verdict "no_line":            the statement was read and has no such line -> confirmed
  verdict "statement_not_found" / "no_filing": no evidence either way (not counted)

Read-only. Defaults reproduce the 2026-10-13 check of cash_flow_investing_resolved.

  uv run python pipeline/scripts/verify_no_line_item_filed.py --sample 40 --kind Q
"""

import argparse
import collections
import random
import re

import httpx
import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.parsers.filing_line_evidence import _pick_report, extract_labels
from scrooner_pipeline.segments.segment_revenue import _filing_summary_reports

CASH_FLOW_TITLE = re.compile(r"cash\s+flows?", re.IGNORECASE)
# concept -> label pattern for the line on the cash-flow statement
LINE_PATTERNS = {
    "cash_flow_investing_resolved": re.compile(r"investing\s+activities", re.I),
    "cash_flow_financing_resolved": re.compile(r"financing\s+activities", re.I),
    "cfo_resolved": re.compile(r"operating\s+activities", re.I),
}
# a "Net cash ... investing activities" TOTAL, not the section heading alone
TOTAL_LINE = re.compile(
    r"^\s*(total\s+)?net\s+cash\b.*activities|^\s*net\s+cash\s+(flows?\s+)?(provided|used|from)",
    re.I,
)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--concept",
        default="cash_flow_investing_resolved",
        choices=sorted(LINE_PATTERNS),
    )
    ap.add_argument("--cause", default="no_line_item_filed")
    ap.add_argument("--kind", default="Q", help="period kind: Q, Q4 or FY")
    ap.add_argument("--sample", type=int, default=40)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()
    pattern = LINE_PATTERNS[args.concept]

    with psycopg.connect(settings.database_url) as conn:
        conn.execute("set statement_timeout='100s'")
        rows = conn.execute(
            """
            select g.company_id, c.cik, c.company_name, g.period_end, f.accession_number, f.form
            from analytics.period_gap g
            join analytics.canonical_concept cc on cc.id = g.canonical_concept_id
            join core.company c on c.id = g.company_id and c.status = 'active'
            join core.filing f on f.id = g.filing_id
            where cc.name = %s and g.gap_cause = %s and g.period_kind = %s
            """,
            (args.concept, args.cause, args.kind),
        ).fetchall()
    random.Random(args.seed).shuffle(rows)
    sample = rows[: args.sample]
    print(
        f"{len(rows)} {args.cause} {args.kind} gaps for {args.concept}; checking {len(sample)} filings"
    )

    tally: collections.Counter = collections.Counter()
    shown = collections.defaultdict(list)
    with SECClient() as client:
        for company_id, cik, name, period_end, accession, form in sample:
            try:
                reports = _filing_summary_reports(client, int(cik), accession)
                report = _pick_report(reports, CASH_FLOW_TITLE) if reports else None
                if report is None:
                    verdict, label = "statement_not_found", None
                else:
                    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"
                    labels = extract_labels(client.get(base + report["html_file"]).text)
                    hit = next(
                        (
                            l
                            for l in labels
                            if pattern.search(l) and TOTAL_LINE.search(l)
                        ),
                        None,
                    )
                    verdict, label = (
                        ("line_on_statement", hit) if hit else ("no_line", None)
                    )
            except httpx.HTTPStatusError:
                verdict, label = "no_filing", None
            tally[verdict] += 1
            if len(shown[verdict]) < 5:
                shown[verdict].append(
                    f"{name[:34]:<34} {form:<5} period {period_end}  {accession}"
                    + (f"  -> '{label[:50]}'" if label else "")
                )

    decided = tally["line_on_statement"] + tally["no_line"]
    print(f"\nverdicts: {dict(tally)}")
    if decided:
        wrong = tally["line_on_statement"]
        print(
            f"of {decided} filings where the statement was read: the line IS on the statement for {wrong} ({100 * wrong / decided:.0f}%)"
            f" -> {args.cause} would be wrong for that share"
        )
    for verdict, examples in shown.items():
        print(f"\n{verdict} (examples):")
        for e in examples:
            print("  " + e)


if __name__ == "__main__":
    main()
