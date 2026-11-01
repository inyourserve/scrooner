"""Per-share selection rules of the EPS lane, importable (stdlib). Moved VERBATIM from eps_fsn_scan.py
(Verifier: VERIFY-EPS-FAMILY-C-V3-2026-11-02, 15/15) so the cohort scan and the FSN-store company reader
(pipeline/scripts/slot_records/fsn_company_pershare.py) run the same code. The only change: swapped_copies
takes `copies` as an argument instead of reading the scan's global. The regression gate checks that every
function body here equals the original's (ast) apart from that parameter.

EPS is never derived: these rules only choose among FILED copies.
"""

import re
from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

TAGS = {
    "EarningsPerShareBasic",
    "EarningsPerShareDiluted",
    "EarningsPerShareBasicAndDiluted",
}
# A one-axis context is accepted only for the 10-K "quarterly financial data (unaudited)" presentation axis
# (UNH: Quarterlyfinancialdata=QuarterlyFinancialDataUnaudited); entity, segment, class and restatement axes never.
QUARTERLY_AXIS = re.compile(r"^[^;=]*quarter[^;=]*=[^;]*;?$", re.I)
REJECT_AXIS = re.compile(
    r"consolidat|entit|segment|class|series|restat|scenario|adjust|previously|parent|subsidiar",
    re.I,
)
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-KT/A"}


def month_end(d: date) -> date:
    this = date(d.year, d.month, monthrange(d.year, d.month)[1])
    prev = d.replace(day=1) - timedelta(days=1)
    return this if (this - d) <= (d - prev) else prev


def allowed(segment: str) -> bool:
    return segment == "" or (
        bool(QUARTERLY_AXIS.match(segment)) and not REJECT_AXIS.search(segment)
    )


def same(a: str, b: str) -> bool:
    return abs(Decimal(a) - Decimal(b)) <= Decimal("0.005")


def swapped_copies(copies) -> set[tuple[str, str, str, str, str]]:
    """(cik, tag, ddate, qtrs, accession) of copies proven to be a context swap: filing F reports at date d the value
    another filing G reports at d', and at d' something other than G's value (News Corp FY2016 10-K
    0001193125-16-679975 tags FY2016 Q4 and FY2015 Q4 with each other's dates; FY2015 10-K and FY2017 10-K agree
    with the stored values). A genuine restatement (only one date changes) is never a swap: it stays hidden."""
    by: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for (cik, tag, dd, q), v in copies.items():
        for x in v:
            if allowed(x[4]):
                by[(cik, tag, q)][x[1]][dd] = x[0]
    out = set()
    for (cik, tag, q), filings in by.items():
        for f, fv in filings.items():
            for g, gv in filings.items():
                if f == g:
                    continue
                for d, fval in fv.items():
                    for d2, gval in gv.items():
                        if (
                            d2 != d
                            and d2 in fv
                            and same(fval, gval)
                            and not same(fv[d2], gval)
                        ):
                            out.add((cik, tag, d, q, f))
                            out.add((cik, tag, d2, q, f))
    return out


def select(copies, SWAPPED, cik, tags, dd, q):
    """The scan's per-cell selection (eps_fsn_scan.py main loop body, unchanged): the concept's own tag first,
    the combined tag only when the own tag has no copy; swapped copies dropped; copies within 0.005 agree
    (witness = the earliest filed) else hidden."""
    found = []
    for tag in tags:
        found = [x for x in copies.get((cik, tag, dd, q), []) if allowed(x[4])]
        if found:
            break
    dropped = [x for x in found if (cik, tag, dd, q, x[1]) in SWAPPED]
    drop_ids = [x[1] for x in dropped] if dropped and len(dropped) < len(found) else []
    found = [x for x in found if x[1] not in drop_ids]
    if not found:
        res = {"outcome": "not_in_fsn"}
    else:
        vals = sorted({Decimal(x[0]) for x in found})
        if vals[-1] - vals[0] > Decimal("0.005"):
            res = {"outcome": "fsn_copies_disagree", "values": [str(v) for v in vals]}
        else:
            v, adsh, form, filed, segment = min(found, key=lambda x: (x[3], x[1]))
            res = {
                "outcome": "replace_with_fsn_value",
                "value": str(Decimal(v)),
                "accession": adsh,
                "form": form,
                "filed": filed,
                "tag": tag,
                "copies": len(found),
                "axis": segment,
                "qtrs": q,
                "swapped_copies_dropped": drop_ids,
            }
    return res
