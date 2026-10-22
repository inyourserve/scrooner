"""The identity fix list of 2026-10-22 and its audited apply/reverse
(rule identity.cik_name_ticker@1, RF-20). Source of every item:
data-team/strategy/team/GATE-A-IDENTITY-REGISTRANT-CHECKS.md (Data Verifier,
sections 1, 2, 3e). NOT a general editor: a closed list, each item with its
accession and locator, each edit written together with a core.company_identity_
audit row (old value, new value, accession) in one transaction so
`reverse_run` can restore the old values exactly.

DO NOT rename id 1840. CIK 0000906107 IS the former Equity Residential, renamed
Vivmark Residential on 2026-08-17 (8-K 0001140361-26-033377 Item 5.03) and
trading as VMRK from 2026-08-18; company_name and primary_ticker are right.
Wrong on it: display_name (yfinance says AvalonBay), the missing EQR ticker
history, and a market cap on the pre-merger share count.

Durability: status / display_name / primary_ticker / holds are enforced
through the audit rows (company_master/identity_overrides.py), because the
nightly recomputes those columns from recency, yfinance and listings. company_name
is SEC truth (the same value the next submissions refresh writes), so it is a
plain audited edit.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

import psycopg

from scrooner_pipeline.common.cell_store import (
    finish_rule_run,
    mark_identity_audit_reversed,
    record_identity_audit,
    start_rule_run,
)

RULE_ID = "identity.cik_name_ticker@1"

F_DISPLAY = "display_name"
F_TICKER = "primary_ticker"
F_STATUS = "status"
F_NAME = "company_name"
F_LISTING_END = "listing_end"
F_MCAP_HOLD = "market_cap_hold"
F_PSEUDO = "pseudo_ticker"
FIELDS = (F_DISPLAY, F_TICKER, F_STATUS, F_NAME, F_LISTING_END, F_MCAP_HOLD, F_PSEUDO)

FC = "FILING-CHECKED"
DI = "DATA-INFERRED"


@dataclass(frozen=True)
class Fix:
    cik: str
    field: str
    new_value: str
    evidence_level: str
    accession: str | None
    locator: str | None
    note: str
    ticker: str | None = None  # listing_end only

    def __post_init__(self) -> None:
        if self.field not in FIELDS:
            raise ValueError(f"unknown field {self.field!r}")
        if self.evidence_level == FC and not (self.accession and self.locator):
            raise ValueError("a FILING-CHECKED fix cites accession and locator")
        if self.field == F_LISTING_END and not self.ticker:
            raise ValueError("listing_end needs a ticker")

    @property
    def audit_field(self) -> str:
        return (
            f"listing_end:{self.ticker}" if self.field == F_LISTING_END else self.field
        )


def _j(**kw: str | None) -> str:
    return json.dumps(kw, sort_keys=True)


VIVMARK_8K = "0001140361-26-033377"
SKYDANCE_8K = "0001104659-26-113913"

FIX_LIST: tuple[Fix, ...] = (
    # --- id 1840, CIK 0000906107: correct name and ticker; four real defects
    Fix(
        "0000906107",
        F_DISPLAY,
        "VIVMARK RESIDENTIAL",
        FC,
        VIVMARK_8K,
        "Item 5.03: name changed from Equity Residential to Vivmark Residential effective 2026-08-17",
        "display name came from yfinance (AvalonBay Communities, Inc.); SEC name wins when the vendor name matches neither the SEC name nor a former name",
    ),
    Fix(
        "0000906107",
        F_LISTING_END,
        "2026-08-17",
        FC,
        VIVMARK_8K,
        "Item 5.03: from 2026-08-18 the shares trade on NYSE as VMRK (8-K cover still shows EQR)",
        "EQR ticker history, so a search or historical join on EQR still finds the company",
        ticker="EQR",
    ),
    Fix(
        "0000906107",
        F_MCAP_HOLD,
        _j(
            event_date="2026-08-17",
            reason="share_count_predates_merger_issuance_8-K_0001140361-26-033377",
        ),
        FC,
        VIVMARK_8K,
        "Item 2.01 merger closing: each AvalonBay share became 2.793 Company shares (pre-merger cover count 374.9M, post-close about 773.7M)",
        "market cap used the pre-merger EQR cover share count (about half); hold until a share count dated on/after the closing exists (Q3 2026 10-Q). Decision 16 (history basis) still open",
    ),
    # --- AvalonBay id 1895: delisted and deregistered
    Fix(
        "0000915912",
        F_STATUS,
        _j(
            status="delisted",
            reason="acquired:merged_into_0000906107;25-NSE_0000876661-26-000689;15-12G_0001104659-26-102433",
        ),
        FC,
        VIVMARK_8K,
        "Item 2.01: AvalonBay merged into Canopy Merger Sub, a subsidiary of Vivmark Residential; 25-NSE 2026-08-17, 15-12G 2026-08-27, 15-15D 2026-09-16 (submissions list)",
        "status was active (status_as_of 2026-08-23, before the Form 15)",
    ),
    # --- Warner Bros. Discovery id 5851: acquired by Skydance 2026-10-06
    Fix(
        "0001437107",
        F_STATUS,
        _j(
            status="delisted",
            reason="acquired:skydance_8-K_0001104659-26-113913;15-12G_0001193125-26-423513",
        ),
        FC,
        SKYDANCE_8K,
        "Item 2.01: each WBD share converted into $31.00 cash (plus ticking consideration); WBD filed 15-12G 0001193125-26-423513 on 2026-10-16 (class line not opened by this work)",
        "status was active as of 2026-10-22",
    ),
    # --- Skydance id 4474 (was Paramount Skydance, PSKY)
    Fix(
        "0002041610",
        F_NAME,
        "Skydance Corp",
        FC,
        SKYDANCE_8K,
        "Item 5.03: name changed from Paramount Skydance Corporation to Skydance Corporation effective 2026-10-06",
        "stored name is 16 days stale; the same value the next submissions refresh writes",
    ),
    Fix(
        "0002041610",
        F_TICKER,
        "SKYD",
        FC,
        SKYDANCE_8K,
        "cover: Class B trading symbol SKYD (submissions tickers SKYD, PSKY, SKYD-WT)",
        "PSKY still appears in submissions beside SKYD; the nightly would pick the alphabetically first, so the corrected ticker is pinned",
    ),
    # --- subsidiary registrants whose only 'ticker' is a bond or preferred of the subsidiary
    Fix(
        "0000007323",
        F_PSEUDO,
        _j(reason="EAI_is_an_Entergy_Arkansas_4.875%_2066_bond_subsidiary_registrant"),
        DI,
        "0000065984-26-000174",
        "header FILER block: 0000007323 is a co-registrant of Entergy Corp's combined 10-K; vendor display name 'Entergy Arkansas, Inc. 1M BD 4.875%66'",
        "market cap was 466.6M Entergy Corp shares x the bond's price",
    ),
    Fix(
        "0000041091",
        F_PSEUDO,
        _j(
            reason="GPJA_is_a_Georgia_Power_5%_junior_subordinated_note_subsidiary_registrant"
        ),
        DI,
        "0000092122-26-000054",
        "Southern combined 10-Q header lists Georgia Power as a co-registrant; vendor name 'Georgia Power Company 5% JR SUB NT 77'",
        "vendor name is the only evidence the ticker is a note",
    ),
    Fix(
        "0000201533",
        F_PSEUDO,
        _j(reason="CMS-PB_is_a_Consumers_Energy_preferred_subsidiary_registrant"),
        DI,
        None,
        None,
        "ticker pattern -PB (preferred); Consumers Energy files with CMS Energy",
        "pattern and group membership only",
    ),
    Fix(
        "0000081023",
        F_PSEUDO,
        _j(reason="PNMXO_is_a_PNM_4.58%_preferred_subsidiary_registrant"),
        DI,
        None,
        None,
        "vendor name 'Public Service Company of New Mexico PFD 4.58%', OTC venue",
        "vendor name is the only evidence",
    ),
)


@dataclass
class PlannedEdit:
    fix: Fix
    company_id: int | None
    old_value: str | None
    new_value: str
    action: str  # apply | already_applied | no_company

    def row(self) -> tuple:
        return (
            self.fix.cik,
            self.fix.audit_field,
            self.old_value,
            self.new_value,
            self.action,
        )


def _current(cur, company_id: int, fix: Fix) -> str | None:
    f = fix.field
    if f in (F_DISPLAY, F_TICKER, F_NAME):
        col = {
            "display_name": "display_name",
            "primary_ticker": "primary_ticker",
            "company_name": "company_name",
        }[f]
        cur.execute(f"select {col} from core.company where id = %s", (company_id,))
        return cur.fetchone()[0]
    if f == F_STATUS:
        cur.execute(
            "select status, status_reason from core.company where id = %s",
            (company_id,),
        )
        status, reason = cur.fetchone()
        return _j(status=status, reason=reason)
    if f == F_LISTING_END:
        cur.execute(
            "select effective_to from core.listing where company_id = %s and ticker = %s",
            (company_id, fix.ticker),
        )
        row = cur.fetchone()
        return (
            "absent"
            if row is None
            else ("open" if row[0] is None else row[0].isoformat())
        )
    cur.execute("select to_regclass('core.company_identity_audit') is not null")
    if not cur.fetchone()[
        0
    ]:  # migration 0100 not applied yet: plan still works, apply would fail loudly
        return None
    cur.execute(
        "select new_value from core.company_identity_audit where company_id = %s and field = %s and reversed_at is null "
        "order by applied_at desc, id desc limit 1",
        (company_id, fix.audit_field),
    )
    row = cur.fetchone()
    return row[0] if row else None


def plan_fixes(
    conn: psycopg.Connection, fixes: Sequence[Fix] = FIX_LIST
) -> list[PlannedEdit]:
    out: list[PlannedEdit] = []
    with conn.cursor() as cur:
        for fix in fixes:
            cur.execute("select id from core.company where cik = %s", (fix.cik,))
            row = cur.fetchone()
            if row is None:
                out.append(PlannedEdit(fix, None, None, fix.new_value, "no_company"))
                continue
            old = _current(cur, row[0], fix)
            action = "already_applied" if old == fix.new_value else "apply"
            out.append(PlannedEdit(fix, row[0], old, fix.new_value, action))
    return out


def _write(
    cur, company_id: int, fix: Fix, value: str | None, *, restoring: bool = False
) -> None:
    f = fix.field
    if f == F_DISPLAY:
        cur.execute(
            "update core.company set display_name = %s, display_name_source = %s, display_name_updated_at = now() where id = %s",
            (
                value,
                ("yfinance" if value is not None else None)
                if restoring
                else "sec_submissions",
                company_id,
            ),
        )
    elif f == F_NAME:
        cur.execute(
            "update core.company set company_name = %s where id = %s",
            (value, company_id),
        )
    elif f == F_TICKER:
        cur.execute(
            "update core.company set primary_ticker = %s, primary_ticker_status = 'resolved', primary_ticker_updated_at = now() where id = %s",
            (value, company_id),
        )
    elif f == F_STATUS:
        data = json.loads(value or "{}")
        cur.execute(
            "update core.company set status = %s, status_as_of = %s, status_reason = %s where id = %s",
            (data.get("status"), date.today(), data.get("reason"), company_id),
        )
    elif f == F_LISTING_END:
        if value == "absent":
            cur.execute(
                "delete from core.listing where company_id = %s and ticker = %s",
                (company_id, fix.ticker),
            )
        else:
            end = None if value in (None, "open") else date.fromisoformat(value)
            cur.execute(
                "update core.listing set effective_to = %s where company_id = %s and ticker = %s",
                (end, company_id, fix.ticker),
            )
            if cur.rowcount == 0:
                cur.execute(
                    "insert into core.listing (company_id, ticker, exchange, effective_to, source) "
                    "select %s, %s, exchange, %s, 'unknown' from core.listing where company_id = %s limit 1",
                    (company_id, fix.ticker, end, company_id),
                )
    # holds (market_cap_hold, pseudo_ticker) live only as audit rows


def apply_fixes(
    conn: psycopg.Connection,
    plans: Sequence[PlannedEdit],
    *,
    git_commit: str | None = None,
) -> dict:
    """One run_id for the whole list; each edit and its audit row together.
    Does not commit. Items already applied or without a company are skipped."""
    todo = [p for p in plans if p.action == "apply"]
    run_id = start_rule_run(
        conn, RULE_ID, "apply", "on", [p.fix.cik for p in todo], git_commit=git_commit
    )
    with conn.cursor() as cur:
        for p in todo:
            assert p.company_id is not None  # action 'apply' implies the company exists
            _write(cur, p.company_id, p.fix, p.new_value)
            record_identity_audit(
                conn,
                company_id=p.company_id,
                field_name=p.fix.audit_field,
                old_value=p.old_value,
                new_value=p.new_value,
                rule_id=RULE_ID,
                evidence_level=p.fix.evidence_level,
                accession=p.fix.accession,
                locator=p.fix.locator,
                run_id=run_id,
            )
    stats = {"applied": len(todo), "skipped": len(plans) - len(todo)}
    finish_rule_run(conn, run_id, stats)
    return {"run_id": run_id, **stats}


def reverse_run(conn: psycopg.Connection, run_id: str) -> int:
    """Restore the old values of every unreversed audit row of a run (newest
    first) and mark them reversed. Does not commit."""
    with conn.cursor() as cur:
        cur.execute(
            "select id, company_id, field, old_value from core.company_identity_audit "
            "where run_id = %s::uuid and reversed_at is null order by id desc",
            (run_id,),
        )
        rows = cur.fetchall()
        for audit_id, company_id, field, old in rows:
            base, _, ticker = field.partition(":")
            fix = (
                Fix("", base, "", DI, None, None, "", ticker=ticker or None)
                if base in FIELDS
                else None
            )
            if fix is not None and base not in (F_MCAP_HOLD, F_PSEUDO):
                _write(cur, company_id, fix, old, restoring=True)
        for audit_id, *_ in rows:
            mark_identity_audit_reversed(conn, audit_id)
    return len(rows)
