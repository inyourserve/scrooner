"""Cell proof end to end on a migrated scratch database (CI: Postgres 16): shown cells loaded from
analytics.canonical_fact, their claims from analytics.company_tag_map, proven against a synthetic filing
structure. One case each for a share count, a per-share value, a component sum and a note-only line,
with PROVEN and DISAGREE."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import psycopg
import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine
from scrooner_pipeline.proof.shown import load_shown

FY_END = date(2024, 12, 31)
ADSH = "0000000031-25-000001"

# name, statement of the concept, map rows [(decision, stmt, tag, sign)], facts [(tag, value)], shown value,
# filing [(tag, uom, value, dcml)], pre lines [(stmt, tag)], period kind
CASES = {
    "share_count": dict(
        name="weighted_diluted_shares",
        stmt="IS",
        rows=[("concept", "IS", "WeightedAverageNumberOfDilutedSharesOutstanding", 1)],
        facts=[("WeightedAverageNumberOfDilutedSharesOutstanding", "15000000000")],
        shown="15000000000",
        bad="15000005000",  # 5,000 shares off at decimals -3: the company's $ scale must not hide it
        filing=[
            (
                "WeightedAverageNumberOfDilutedSharesOutstanding",
                "shares",
                "15000000000",
                -3,
            )
        ],
        pre=[("IS", "WeightedAverageNumberOfDilutedSharesOutstanding")],
        kind="duration",
    ),
    "per_share": dict(
        name="basic_eps_resolved",
        stmt="IS",
        rows=[("concept", "IS", "EarningsPerShareBasic", 1)],
        facts=[("EarningsPerShareBasic", "7.49")],
        shown="7.49",
        bad="7.52",
        filing=[("EarningsPerShareBasic", "USD/shares", "7.49", 2)],
        pre=[("IS", "EarningsPerShareBasic")],
        kind="duration",
    ),
    "component_sum": dict(
        name="total_debt_resolved",
        stmt="BS",
        rows=[
            ("component", "BS", "LongTermDebtCurrent", 1),
            ("component", "BS", "LongTermDebtNoncurrent", 1),
        ],
        facts=[
            ("LongTermDebtCurrent", "10000000000"),
            ("LongTermDebtNoncurrent", "85000000000"),
        ],
        shown="95000000000",
        bad="85000000000",
        filing=[
            ("LongTermDebtCurrent", "USD", "10000000000", -6),
            ("LongTermDebtNoncurrent", "USD", "85000000000", -6),
        ],
        pre=[("BS", "LongTermDebtCurrent"), ("BS", "LongTermDebtNoncurrent")],
        kind="instant",
    ),
    "note_only": dict(
        name="cash_paid_for_interest",
        stmt="UN",
        rows=[("concept", "UN", "InterestPaidNet", 1)],
        facts=[("InterestPaidNet", "3500000000")],
        shown="3500000000",
        bad="3900000000",
        filing=[("InterestPaidNet", "USD", "3500000000", -6)],
        pre=[],  # printed in a note: no face line
        kind="duration",
    ),
}


def _world(conn, cik, case, shown_value):
    cid = conn.execute(
        "insert into core.company (cik, company_name) values (%s, 'T') returning id",
        (cik,),
    ).fetchone()[0]
    conn.execute(
        "insert into core.unit (unit_name) values ('usd') on conflict do nothing"
    )
    uid = conn.execute("select id from core.unit where unit_name='usd'").fetchone()[0]
    if case["kind"] == "instant":
        start, ptype, fp = FY_END, "instant", "FY"
    else:
        start, ptype, fp = date(2024, 1, 1), "duration", "FY"
    pid = conn.execute(
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
        "values (%s,%s,%s,%s,2024,%s) returning id",
        (cid, start, FY_END, ptype, fp),
    ).fetchone()[0]
    rid = conn.execute(
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
        "values (%s,'u','h',%s,200) returning id",
        (cik, f"raw/{cik}"),
    ).fetchone()[0]
    fid = conn.execute(
        "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) "
        "values (%s,%s,'10-K','2025-02-20',%s,false) returning id",
        (cid, ADSH, FY_END),
    ).fetchone()[0]

    def concept(tag):
        conn.execute(
            "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) on conflict do nothing",
            (tag,),
        )
        return conn.execute(
            "select id from core.concept where taxonomy='us-gaap' and tag=%s", (tag,)
        ).fetchone()[0]

    fact_ids = []
    for tag, value in case["facts"]:
        fact_ids.append(
            conn.execute(
                "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, "
                "is_authoritative, raw_object_id) values (%s,%s,%s,%s,%s,%s,true,%s) returning id",
                (cid, concept(tag), uid, pid, fid, value, rid),
            ).fetchone()[0]
        )
    # a round-million FY revenue so the company's money presentation scale is 6 (slack 1.5M)
    ppid = conn.execute(
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
        "values (%s,'2023-01-01','2023-12-31','duration',2023,'FY') returning id",
        (cid,),
    ).fetchone()[0]
    conn.execute(
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, "
        "raw_object_id) values (%s,%s,%s,%s,%s,5000000000,true,%s)",
        (cid, concept("Revenues"), uid, ppid, fid, rid),
    )
    row = conn.execute(
        "select id from analytics.canonical_concept where name = %s", (case["name"],)
    ).fetchone()
    if row is None:
        row = conn.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode) "
            "values (%s, 'income_statement', 'first_match') returning id",
            (case["name"],),
        ).fetchone()
    ccid = row[0]
    conn.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
        "values (%s,%s,%s,%s,%s)",
        (cid, ccid, pid, shown_value, fact_ids),
    )
    for decision, stmt, tag, sign in case["rows"]:
        is_comp = decision == "component"
        conn.execute(
            "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, "
            "parent_concept_id, sign, era_from, decided_by, rule_id) "
            "values (%s,'us-gaap',%s,%s,%s,%s,%s,%s,'2015-01-01','t','tm.r@1')",
            (
                cid,
                tag,
                stmt,
                decision,
                None if is_comp else ccid,
                ccid if is_comp else None,
                sign,
            ),
        )
    conn.commit()
    return cid


def _structure(case):
    s = FilingStructure(ADSH, "0000000031", "10-K", date(2025, 2, 20), FY_END)
    for i, (stmt, tag) in enumerate(case["pre"]):
        s.pre.append(PreLine(2, i, stmt, tag, "us-gaap/2024", tag, False))
    qtrs = 0 if case["kind"] == "instant" else 4
    for tag, uom, value, dcml in case["filing"]:
        s.num[(tag, FY_END, qtrs)].append(
            NumValue(tag, "us-gaap/2024", FY_END, qtrs, uom, Decimal(value), dcml)
        )
    return s


@pytest.mark.integration
@pytest.mark.parametrize("variant", ["proven", "disagree"])
@pytest.mark.parametrize("which", sorted(CASES))
def test_claim_driven_cell_is_proven_or_disagrees(
    isolated_database_url, which, variant
):
    case = CASES[which]
    shown_value = case["shown"] if variant == "proven" else case["bad"]
    cik = f"00000000{sorted(CASES).index(which)}{0 if variant == 'proven' else 1}"
    with psycopg.connect(isolated_database_url) as conn:
        cid = _world(conn, cik, case, shown_value)
        cells = [
            c
            for c in load_shown(conn, cid, floor=date(2015, 1, 1))
            if c.data_point_name == case["name"]
        ]
    assert len(cells) == 1
    cell = cells[0]
    assert cell.claim is not None and cell.claim.stmt == case["stmt"]
    assert cell.accession == ADSH
    p = pv.prove_cell(cell, _structure(case), "2025q1")
    if variant == "proven":
        assert p.verdict == pv.PROVEN, (p.reason_code, p.reason_text, p.checks)
        assert p.checks["claim"]["source"] == "company_tag_map"
    else:
        assert p.verdict == pv.DISAGREE, (p.verdict, p.reason_text)
