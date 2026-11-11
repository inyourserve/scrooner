"""core.period rows for companies whose history is filed under a predecessor CIK (core.company_history_source,
migration 0121; Dhairya ruling 2026-11-01, option a). For each predecessor window, every 10-K/10-Q the
predecessor filed with a report date inside the window becomes, for the successor company:
  a 10-Q -> a quarter duration (previous quarter end + 1 day .. report date) and an instant;
  a 10-K -> a fiscal-year duration (previous year end + 1 .. report date), the Q4 duration and an instant.
Exact dates come from the predecessor's own EDGAR submissions (reportDate); fiscal labels follow the
company's fiscal year end (fiscalYearEnd) with the select.fiscal_label rule (fiscal year = year of the
year-end that closes the period). Read-only on sec.gov (declared User-Agent, <= 4 requests/second);
writes a CSV for review; the 0121 apply script inserts it.

Usage: history_periods.py <company_history_sources.csv> <out.csv> <cache dir>
"""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import httpx

PERIODIC = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT"}
_last = [0.0]


def _get(url: str, ua: str) -> dict:
    wait = 0.26 - (time.time() - _last[0])  # <= 4 requests per second
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    r = httpx.get(url, headers={"User-Agent": ua}, timeout=60)
    r.raise_for_status()
    return r.json()


def submissions(cik: str, cache: Path, ua: str) -> tuple[list[tuple[str, date]], str | None]:
    """[(form, report date)] of every filing of the CIK, and its fiscalYearEnd (MMDD)."""
    main = cache / f"CIK{cik}.json"
    if not main.exists():
        main.write_text(json.dumps(_get(f"https://data.sec.gov/submissions/CIK{cik}.json", ua)))
    d = json.loads(main.read_text())
    pages = [d["filings"]["recent"]]
    for f in d["filings"].get("files", []):
        p = cache / f["name"]
        if not p.exists():
            p.write_text(json.dumps(_get(f"https://data.sec.gov/submissions/{f['name']}", ua)))
        pages.append(json.loads(p.read_text()))
    out = set()
    for pg in pages:
        for form, rd in zip(pg.get("form", []), pg.get("reportDate", [])):
            if form in PERIODIC and rd:
                out.add((form.split("/")[0], date.fromisoformat(rd)))
    return sorted(out, key=lambda x: x[1]), d.get("fiscalYearEnd")


def _month_end(d: date) -> date:
    nxt = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return nxt - timedelta(days=1)


def _rounded(d: date) -> date:
    """FSN-style nearest month end (day <= 15 -> previous month end)."""
    return date(d.year, d.month, 1) - timedelta(days=1) if d.day <= 15 else _month_end(d)


def label(end: date, fye: str | None, annual: bool) -> tuple[int | None, str | None]:
    if not fye or len(fye) != 4:
        return None, None
    m, day = int(fye[:2]), int(fye[2:])
    m = (m - 2) % 12 + 1 if day <= 15 else m
    r = _rounded(end)
    ahead = (m - r.month) % 12
    if ahead % 3:
        return None, None
    fy = r.year + (r.month + ahead - 1) // 12  # the year of the year-end month that closes the period
    if annual:
        return fy, "FY"
    return fy, f"Q{4 - ahead // 3}"


def rows_for(company_id: str, filings: list[tuple[str, date]], fye: str | None, lo: date, hi: date) -> list[dict]:
    ends = sorted({d for _f, d in filings})
    fy_ends = sorted({d for f, d in filings if f in ("10-K", "10-KT")})
    out = []
    for form, end in filings:
        if not lo <= end <= hi:
            continue
        prev = [d for d in ends if d < end and (end - d).days >= 60]
        q_start = (prev[-1] + timedelta(days=1)) if prev else end - timedelta(days=90)
        fy, fp = label(end, fye, False)
        out.append(dict(company_id=company_id, start_date=q_start, end_date=end, period_type="duration", fiscal_year=fy, fiscal_period=fp))
        afy, afp = label(end, fye, form in ("10-K", "10-KT"))
        out.append(dict(company_id=company_id, start_date=end, end_date=end, period_type="instant", fiscal_year=afy, fiscal_period=afp))
        if form in ("10-K", "10-KT"):
            prev_fy = [d for d in fy_ends if d < end and (end - d).days >= 300]
            y_start = (prev_fy[-1] + timedelta(days=1)) if prev_fy else end - timedelta(days=364)
            out.append(dict(company_id=company_id, start_date=y_start, end_date=end, period_type="duration", fiscal_year=afy, fiscal_period="FY"))
    return out


def main() -> None:
    sources, out_csv, cache = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    cache.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from scrooner_pipeline.common.config import settings
    from scrooner_pipeline.common.history_floor import HISTORY_FLOOR

    import psycopg

    srcs = [s for s in csv.DictReader(open(sources)) if s["relation"] == "predecessor"]
    with psycopg.connect(settings.database_url, connect_timeout=20) as conn:
        company_fye = dict(
            conn.execute(
                "select id::text, fiscal_year_end from core.company where id = any(%s)",
                ([int(s["company_id"]) for s in srcs],),
            ).fetchall()
        )
    rows: list[dict] = []
    for s in srcs:
        filings, fye = submissions(s["source_cik"], cache, settings.sec_user_agent)
        # a predecessor without fiscalYearEnd on EDGAR (Exelon Generation) follows its successor's
        fye = fye or company_fye.get(s["company_id"])
        # core keeps periods ending on or after the storage floor (common/history_floor.py): a window may start earlier
        lo, hi = max(date.fromisoformat(s["valid_from"]), HISTORY_FLOOR), date.fromisoformat(s["valid_to"])
        rows.extend({**r, "source_cik": s["source_cik"]} for r in rows_for(s["company_id"], filings, fye, lo, hi))
    seen, uniq = set(), []
    for r in rows:
        k = (r["company_id"], r["start_date"], r["end_date"], r["period_type"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["company_id", "source_cik", "start_date", "end_date", "period_type", "fiscal_year", "fiscal_period"])
        w.writeheader()
        w.writerows(uniq)
    print(f"{len(uniq)} periods for {len({r['company_id'] for r in uniq})} companies; unlabeled {sum(1 for r in uniq if not r['fiscal_period'])}")


if __name__ == "__main__":
    main()
