"""Validate "latest filing wins" for a tag against SEC's own XBRL Frames values.

normalizer/conflict_latest_filed.py promotes the latest-filed fact when a period's
filings disagree and Stage 2e left none authoritative. It is only safe for tags
where that rule reproduces what SEC currently publishes. This script measures it,
so a tag is added to VALIDATED_TAGS / VALIDATED_QUARTER_TAGS only on evidence.

For each tag it finds periods in the sample where NO fact is authoritative and the
filed values genuinely differ, then asks, against the Frames value for that
company and period end, how often each rule picks the right number:
  latest    the most recently filed value (what the stage promotes)
  earliest  the first filed value
  majority  the value most filings agree on (only when a strict majority exists)

Results the stage was built on (2026-10-04): latest matched 99.7-100% for six annual
tags and 100% for four quarterly tags; majority only 72-80%; earliest 21-48%.

  uv run python pipeline/scripts/validate_latest_filed_vs_frames.py \\
      --tag ProfitLoss --tag SalesRevenueNet --kind fy
  uv run python pipeline/scripts/validate_latest_filed_vs_frames.py \\
      --tag NetIncomeLoss --kind quarter --max-companies 400

Use --include-promoted to re-test periods the stage has already resolved (the
usual case for a tag it covers: nothing is left unresolved, so without the flag
there is nothing to compare).

A tag is reported SAFE only if latest-filed matches Frames on >= --min-rate of at
least --min-holes periods. Periods Frames has no value for (non-calendar fiscal
years, companies that do not file that tag) are excluded and counted separately.
Read-only: it never writes to the database.
"""

import argparse
import collections
import pickle
import random
from decimal import Decimal
from pathlib import Path

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.sec_client import SECClient

FRAMES_URL = "https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/USD/{period}.json"
YEARS = range(2012, 2026)
TOLERANCE = Decimal("0.005")  # 0.5% relative: rounding variants count as equal
BATCH = 20  # companies per query; larger batches hit the pooler's 2-minute cap
FY_DAYS = (340, 380)
QUARTER_DAYS = (80, 100)


def close(a, b) -> bool:
    a, b = Decimal(a), Decimal(b)
    return abs(a - b) <= TOLERANCE * max(abs(b), Decimal(1))


def frame_periods(kind: str) -> list[str]:
    if kind == "fy":
        return [f"CY{y}" for y in YEARS]
    return [f"CY{y}Q{q}" for y in YEARS for q in (1, 2, 3, 4)]


def load_frames(taxonomy: str, tag: str, kind: str, cache_dir: Path) -> dict:
    """{(cik int, period end iso): value} for every Frames period, cached on disk
    because a full fetch is ~14 (annual) or ~56 (quarterly) SEC requests."""
    cache = cache_dir / f"frames_{taxonomy}_{tag}_{kind}.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    frames: dict = {}
    with SECClient() as client:
        for period in frame_periods(kind):
            url = FRAMES_URL.format(taxonomy=taxonomy, tag=tag, period=period)
            try:
                data = client.get_json(url)
            except Exception:
                continue  # no frame for that period / tag
            for row in data.get("data", []):
                frames[(row["cik"], row["end"])] = Decimal(str(row["val"]))
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(pickle.dumps(frames))
    return frames


def sample_company_ids(conn, n: int, seed: int) -> list[int]:
    """Companies that actually have disagreeing-filing gaps today, so the sample
    is the population the rule would act on."""
    ids = [
        r[0]
        for r in conn.execute(
            """
            select distinct company_id from analytics.company_data_finding
            where status = 'open'
              and evidence->>'cause' in ('q4_not_derived', 'quarter_not_derived',
                                          'conflict_material', 'conflict_split')
            """
        ).fetchall()
    ]
    random.Random(seed).shuffle(ids)
    return ids[:n]


def evaluate_tag(
    conn,
    taxonomy: str,
    tag: str,
    kind: str,
    company_ids: list[int],
    frames: dict,
    ciks: dict,
    include_promoted: bool = False,
) -> dict:
    concept = conn.execute(
        "select id from core.concept where taxonomy = %s and tag = %s", (taxonomy, tag)
    ).fetchone()
    if concept is None:
        return {"error": "tag not found in core.concept"}
    low, high = FY_DAYS if kind == "fy" else QUARTER_DAYS
    periods_sql = (
        "p.fiscal_period = 'FY'"
        if kind == "fy"
        else "p.fiscal_period in ('Q1','Q2','Q3')"
    )
    tally: collections.Counter = collections.Counter()
    for i in range(0, len(company_ids), BATCH):
        rows = conn.execute(
            f"""
            select f.company_id, p.end_date, f.value, fl.filing_date, f.id,
                   -- with --include-promoted, a fact the stage promoted does not count as
                   -- "already authoritative", so those periods are re-tested as holes
                   (f.is_authoritative and not (%s and r.fact_id is not null)) as is_authoritative
            from core.fact f
            join core.period p on p.id = f.period_id
            join core.filing fl on fl.id = f.filing_id
            left join core.fact_conflict_resolution r on r.fact_id = f.id
            where f.company_id = any(%s) and f.concept_id = %s and not f.is_derived
              and p.period_type = 'duration' and {periods_sql}
              and (p.end_date - p.start_date) between %s and %s
              and p.end_date >= '2012-01-01'
            """,
            (include_promoted, company_ids[i : i + BATCH], concept[0], low, high),
        ).fetchall()
        groups = collections.defaultdict(list)
        for company_id, end, value, filed, fact_id, auth in rows:
            groups[(company_id, end)].append((value, filed, fact_id, auth))
        for (company_id, end), items in groups.items():
            values = {v for v, *_ in items}
            if any(a for *_, a in items) or len(values) < 2:
                continue  # already resolved, or not a real disagreement
            ref = frames.get((ciks[company_id], end.isoformat()))
            if ref is None:
                tally["no_frame_value"] += 1
                continue
            latest = max(items, key=lambda x: (x[1], x[2]))[0]
            earliest = min(items, key=lambda x: (x[1], x[2]))[0]
            votes: collections.Counter = collections.Counter()
            for v, *_ in items:
                for known in list(votes):
                    if close(v, known):
                        votes[known] += 1
                        break
                else:
                    votes[v] += 1
            top, n_top = votes.most_common(1)[0]
            tally["holes_with_frame"] += 1
            tally["latest_ok"] += close(latest, ref)
            tally["earliest_ok"] += close(earliest, ref)
            if n_top * 2 > len(items):
                tally["majority_applies"] += 1
                tally["majority_ok"] += close(top, ref)
    return dict(tally)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--tag",
        action="append",
        required=True,
        help="us-gaap tag (repeatable); 'taxonomy:Tag' for another taxonomy",
    )
    ap.add_argument("--kind", choices=("fy", "quarter"), default="fy")
    ap.add_argument("--max-companies", type=int, default=400)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--min-rate", type=float, default=0.99)
    ap.add_argument("--min-holes", type=int, default=200)
    ap.add_argument(
        "--include-promoted",
        action="store_true",
        help="also test periods conflict-latest-filed already promoted (re-validates a tag the stage covers)",
    )
    ap.add_argument("--cache-dir", default="/tmp/latest_filed_validation")
    args = ap.parse_args()

    with psycopg.connect(settings.database_url) as conn:
        conn.execute("set statement_timeout='100s'")
        company_ids = sample_company_ids(conn, args.max_companies, args.seed)
        ciks = dict(
            conn.execute(
                "select id, cik::bigint from core.company where id = any(%s)",
                (company_ids,),
            ).fetchall()
        )
        print(
            f"sample: {len(company_ids)} companies with disagreeing-filing gaps; kind={args.kind}"
        )
        for spec in args.tag:
            taxonomy, _, tag = spec.rpartition(":")
            taxonomy = taxonomy or "us-gaap"
            frames = load_frames(taxonomy, tag, args.kind, Path(args.cache_dir))
            t = evaluate_tag(
                conn,
                taxonomy,
                tag,
                args.kind,
                company_ids,
                frames,
                ciks,
                args.include_promoted,
            )
            if "error" in t:
                print(f"\n{taxonomy}:{tag}: {t['error']}")
                continue
            n = t.get("holes_with_frame", 0)
            rate = (t.get("latest_ok", 0) / n) if n else 0.0
            maj = t.get("majority_applies", 0)
            verdict = (
                "SAFE to add"
                if n >= args.min_holes and rate >= args.min_rate
                else "NOT validated"
            )
            if n < args.min_holes:
                verdict += f" (only {n} comparable periods; need {args.min_holes}: raise --max-companies)"
            print(f"\n{taxonomy}:{tag}  [{verdict}]")
            print(
                f"  comparable periods: {n} (+{t.get('no_frame_value', 0)} with no Frames value)"
            )
            print(f"  latest   : {t.get('latest_ok', 0)}/{n} = {100 * rate:.1f}%")
            print(
                f"  earliest : {t.get('earliest_ok', 0)}/{n} = {100 * t.get('earliest_ok', 0) / n if n else 0:.1f}%"
            )
            print(
                f"  majority : {t.get('majority_ok', 0)}/{maj} = {100 * t.get('majority_ok', 0) / maj if maj else 0:.1f}% (where a strict majority exists)"
            )


if __name__ == "__main__":
    main()
