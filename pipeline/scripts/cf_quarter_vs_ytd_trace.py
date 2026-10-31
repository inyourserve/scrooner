"""Trace a company's quarterly cash-flow cells against the printed year-to-date lines.

For each quarterly canonical cell of a cash-flow concept: the value production
shows, its source facts (tag, accession, filed or derived), and the quarter the
filer's own printed year-to-date lines imply (YTD_n - YTD_(n-1), from the FSN
sets of the filings that print them). A shown value that differs from the
year-to-date quarter is a 3-month fact taken from a note (dividends DECLARED
in the equity note, for example), never from the cash-flow face.

usage: PYTHONPATH=src python scripts/cf_quarter_vs_ytd_trace.py <ticker> <canonical_name> <fsn_root> [from_date] [to_date]
example: ... AAPL dividends_paid_resolved /path/to/fsn 2014-10-01 2019-12-31
Read-only: one Postgres connection (DATABASE_URL), FSN read from fsn_root.
"""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg

from scrooner_pipeline.proof.fsn import fsn_ddate, load_quarter, quarter_of

TAGS = {
    "dividends_paid_resolved": (
        "PaymentsOfDividends",
        "PaymentsOfDividendsCommonStock",
    ),
    "share_buybacks_resolved": ("PaymentsForRepurchaseOfCommonStock",),
    "capex_resolved": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ),
    "cfo_resolved": ("NetCashProvidedByUsedInOperatingActivities",),
    "cash_flow_investing_resolved": ("NetCashProvidedByUsedInInvestingActivities",),
    "cash_flow_financing_resolved": ("NetCashProvidedByUsedInFinancingActivities",),
}


def main(ticker: str, concept: str, fsn_root: Path, d_from: date, d_to: date) -> int:
    tags = TAGS[concept]
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as c:
        c.execute("set statement_timeout = '120s'")
        cid, cik = c.execute(
            "select id, cik from core.company where primary_ticker = %s", (ticker,)
        ).fetchone()
        cells = c.execute(
            """
            select p.fiscal_year, p.fiscal_period, p.start_date, p.end_date, cf.value, cf.source_fact_ids
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            where cf.company_id = %s and cc.name = %s and p.period_type = 'duration'
              and p.fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4') and p.end_date between %s and %s
            order by p.end_date
            """,
            (cid, concept, d_from, d_to),
        ).fetchall()
        fids = [f for r in cells for f in (r[5] or [])]
        facts = {
            r[0]: r[1:]
            for r in c.execute(
                "select f.id, co.tag, fl.accession_number, f.is_derived, f.value from core.fact f "
                "join core.concept co on co.id = f.concept_id join core.filing fl on fl.id = f.filing_id where f.id = any(%s)",
                (fids,),
            ).fetchall()
        }
        filings = c.execute(
            "select accession_number, form, period_of_report, filing_date from core.filing where company_id = %s "
            "and form in ('10-K', '10-Q') and period_of_report between %s and %s order by period_of_report",
            (cid, d_from - timedelta(days=120), d_to),
        ).fetchall()
    by_q: dict[str, set[str]] = {}
    for acc, _form, _por, fd in filings:
        by_q.setdefault(quarter_of(fd), set()).add(acc)
    structs = {}
    for q, accs in by_q.items():
        try:
            structs.update(load_quarter(fsn_root, q, accs))
        except FileNotFoundError:
            print(f"  (FSN period {q} not available)")
    ytd: dict[tuple[date, int], tuple[Decimal, str]] = {}
    for acc, st in structs.items():
        for (tag, dd, qtrs), vals in st.num.items():
            if tag in tags:
                ytd[(dd, qtrs)] = (vals[0].value, acc)
    print(f"{ticker} {concept}: shown quarter vs printed year-to-date lines")
    differ = 0
    for fy, fp, s, e, v, src in cells:
        n = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}[fp]
        cur = ytd.get((fsn_ddate(e), n))
        prev = (
            ytd.get((fsn_ddate(s - timedelta(days=1)), n - 1))
            if n > 1
            else (Decimal(0), "-")
        )
        implied = (cur[0] - prev[0]) if cur and prev else None
        srcs = [facts[f] for f in (src or []) if f in facts]
        flag = ""
        if implied is not None and abs(Decimal(v) - implied) > Decimal(1500000):
            flag = "  <-- DIFFERS"
            differ += 1
        srcs_txt = ", ".join(
            f"{t}@{acc[-10:]} {'derived' if d else 'filed'} {Decimal(val) / 1000000:.0f}M"
            for t, acc, d, val in srcs
        )
        print(
            f"  FY{fy} {fp} {s}..{e} shown={Decimal(v) / 1000000:.0f}M [{srcs_txt}] "
            f"ytd_quarter={'n/a' if implied is None else f'{implied / 1000000:.0f}M'}"
            f"{'' if not cur else f' ({cur[0] / 1000000:.0f} in {cur[1][-10:]} - {prev[0] / 1000000:.0f})'}{flag}"
        )
    print(
        f"cells: {len(cells)}, differing from the printed year-to-date quarter: {differ}"
    )
    return 0


if __name__ == "__main__":
    a = sys.argv
    sys.exit(
        main(
            a[1],
            a[2],
            Path(a[3]),
            date.fromisoformat(a[4]) if len(a) > 4 else date(2015, 1, 1),
            date.fromisoformat(a[5]) if len(a) > 5 else date.today(),
        )
    )
