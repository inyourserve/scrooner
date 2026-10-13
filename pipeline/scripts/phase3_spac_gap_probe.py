"""Doc 50 Phase 3, step 1: do cash-flow gaps in companies that were once SPACs fall
in the pre-merger years?  (read-only)

Phase 3's premise (doc 50, 2026-10-11): `cash_flow_investing` / `cash_flow_financing`
gaps are not company-wide ("this SIC never reports it") but PERIOD-conditional: a
post-SPAC-merger operating company reports the lines normally, and genuinely lacks
them only for the pre-merger shell years. That was traced on three companies
(MultiSensor AI Holdings, VSee Health, Alpha Star Acquisition). This script tests it
on the whole gap population with an INDEPENDENT marker from SEC data: a SPAC holds a
trust account, tagged `AssetsHeldInTrust*`. A gap period that falls while the company
was still reporting trust-account assets is explained by "still a shell".

Per gap (company, period_end) it reports:
  leading    the gap is earlier than the company's first PRESENT period for the concept
  in_spac    the gap falls on or before (last trust-account fact + SPAC_SLACK_DAYS)
and aggregates by gap cause. Nothing is stored. A classifier should be built only if
a large share of the `no_mapped_tag` / `no_line_item_filed` gaps are in_spac AND
leading -- and then keyed on the trust-account evidence, not on SIC.

  uv run python pipeline/scripts/phase3_spac_gap_probe.py --concept cash_flow_investing_resolved
"""

import argparse
import collections
from datetime import timedelta

import psycopg

from scrooner_pipeline.common.config import settings

TRUST_TAGS = (
    "AssetsHeldInTrustNoncurrent",
    "AssetsHeldInTrustCurrent",
    "AssetsHeldInTrust",
    "AssetsHeldInTrustNoncurrentAndCurrent",
)
SPAC_SLACK_DAYS = 100  # one fiscal quarter of slack around the last trust-account fact
BATCH = 40
GENUINE_ABSENCE_CAUSES = ("no_mapped_tag", "no_line_item_filed")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--concept", default="cash_flow_investing_resolved")
    ap.add_argument("--causes", nargs="*", default=list(GENUINE_ABSENCE_CAUSES))
    args = ap.parse_args()

    with psycopg.connect(settings.database_url) as conn:
        conn.execute("set statement_timeout='100s'")
        concept_id = conn.execute(
            "select id from analytics.canonical_concept where name = %s",
            (args.concept,),
        ).fetchone()[0]
        trust_ids = [
            r[0]
            for r in conn.execute(
                "select id from core.concept where tag = any(%s)", (list(TRUST_TAGS),)
            ).fetchall()
        ]
        gaps = conn.execute(
            """
            select company_id, period_end, gap_cause, period_kind from analytics.period_gap
            where canonical_concept_id = %s and gap_cause = any(%s)
            """,
            (concept_id, args.causes),
        ).fetchall()
        by_company = collections.defaultdict(list)
        for company_id, period_end, cause, kind in gaps:
            by_company[company_id].append((period_end, cause, kind))
        companies = sorted(by_company)
        print(
            f"{args.concept}: {len(gaps)} gaps ({', '.join(args.causes)}) across {len(companies)} companies"
        )

        last_trust: dict[int, object] = {}
        first_present: dict[int, object] = {}
        last_present: dict[int, object] = {}
        for i in range(0, len(companies), BATCH):
            batch = companies[i : i + BATCH]
            for company_id, last in conn.execute(
                """
                select f.company_id, max(p.end_date) from core.fact f join core.period p on p.id = f.period_id
                where f.company_id = any(%s) and f.concept_id = any(%s) group by 1
                """,
                (batch, trust_ids),
            ).fetchall():
                last_trust[company_id] = last
            for company_id, first, last_present_date in conn.execute(
                """
                select cf.company_id, min(p.end_date), max(p.end_date) from analytics.canonical_fact cf join core.period p on p.id = cf.period_id
                where cf.company_id = any(%s) and cf.canonical_concept_id = %s group by 1
                """,
                (batch, concept_id),
            ).fetchall():
                first_present[company_id] = first
                last_present[company_id] = last_present_date

    tally: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for company_id, items in by_company.items():
        last = last_trust.get(company_id)
        first = first_present.get(company_id)
        for period_end, cause, kind in items:
            t = tally[cause]
            last_p = last_present.get(company_id)
            if first is None:
                position = "never_present"
            elif period_end < first:
                position = "leading"
            elif last_p is not None and period_end > last_p:
                position = "trailing"
            else:
                position = (
                    "interior"  # a hole INSIDE the company's own reported history
                )
            t["pos_" + position] += 1
            t["kind_" + kind] += 1
            t["gaps"] += 1
            leading = first is not None and period_end < first
            in_spac = last is not None and period_end <= last + timedelta(
                days=SPAC_SLACK_DAYS
            )
            t["leading"] += leading
            t["in_spac"] += in_spac
            t["leading_and_in_spac"] += leading and in_spac
            t["never_present"] += first is None
            t["company_had_trust_account"] += last is not None
    for cause, t in sorted(tally.items(), key=lambda kv: -kv[1]["gaps"]):
        n = t["gaps"]
        print(f"\n{cause}: {n} gaps")
        print(
            f"  leading (before the company's first present period): {t['leading']:>6} ({100 * t['leading'] / n:4.1f}%)"
        )
        print(
            f"  in_spac (<= last trust-account fact + {SPAC_SLACK_DAYS}d):          {t['in_spac']:>6} ({100 * t['in_spac'] / n:4.1f}%)"
        )
        print(
            f"  leading AND in_spac (the Phase 3 pattern):           {t['leading_and_in_spac']:>6} ({100 * t['leading_and_in_spac'] / n:4.1f}%)"
        )
        print(
            f"  company never has the concept at all:                {t['never_present']:>6} ({100 * t['never_present'] / n:4.1f}%)"
        )
        print("  where the gap sits relative to the company's own present history:")
        for pos in ("leading", "interior", "trailing", "never_present"):
            print(
                f"      {pos:<14}{t['pos_' + pos]:>6} ({100 * t['pos_' + pos] / n:4.1f}%)"
            )
        kinds = sorted((k[5:], v) for k, v in t.items() if k.startswith("kind_"))
        print(
            "  by period kind:",
            ", ".join(f"{k}={v} ({100 * v / n:.0f}%)" for k, v in kinds),
        )


if __name__ == "__main__":
    main()
