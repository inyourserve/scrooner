"""The one loader of family cell files into analytics.canonical_fact
(data-team/46-canonical-fact-v2/CELL-FORMAT-v1.md).

A family file (JSONL, gzip) carries one row per displayed cell: a value with its
provenance, or a blank with its reason from the frozen eight-state contract.
Per company, in one transaction: bind every row to a core.period (exact dates
win; else fiscal_year + fiscal_period + period_type with the end within
BIND_DAYS of the FSN month-end), resolve source facts in one bulk join
(accession + tag + period), write the facts an FSN-only value needs through
facts.normalize_payload with an fsn:// lineage row, delete the family's data
points for the company, insert the valued cells, and replace the blank
reasons under one analytics.rule_run (scope run + company + rule). Plan mode
does all of it and rolls back. Idempotent: the same file twice gives the same
rows. The loader takes no before-image itself; a caller that needs a rollback
copies the companies' canonical_fact and cell_blank_reason rows first
(`scrooner-fsn pilot-prod`) and puts them back with `restore` (`scrooner-cells restore`).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from collections.abc import Callable
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.cell_contract import (
    BLANK_STATES,
    EVIDENCE_LEVELS,
    STATES,
    CellKey,
    parse_rule_id,
    validate_defect,
)
from scrooner_pipeline.common.cell_store import (
    BlankReason,
    finish_rule_run,
    replace_rule_reasons,
    start_rule_run,
)
from scrooner_pipeline.common.history_floor import HISTORY_FLOOR
from scrooner_pipeline.normalizer.facts import normalize_payload

logger = structlog.get_logger()

GRAINS = ("FY", "Q", "I")
UNITS = {"USD": "usd", "USD/shares": "usd/shares", "shares": "shares", "pure": "pure"}
VALUED = frozenset({"value", "derived", "evidenced_zero"})
BIND_DAYS = 10
BUCKET = "fsn-notes"
CHUNK = 5000

# Spec section 4: one data point, one family. A data point absent here is
# unowned: loaded with a warning in the report, never silently.
OWNERSHIP: dict[str, str] = {}
for _fam, _points in {
    "is_core": (
        "revenue_sanity",
        "net_income",
        "operating_income",
        "gross_profit",
        "cost_of_revenue",
        "operating_expenses",
        "income_before_tax",
        "income_tax_expense",
    ),
    "pershare_filed": (
        "basic_eps",
        "diluted_eps",
        "dividends_per_share",
        "shares_outstanding",
    ),
    "pershare_derived": ("effective_tax_rate_reported",),
    "cashflow": (
        "cfo",
        "cash_flow_investing",
        "cash_flow_financing",
        "share_buybacks",
        "dividends_paid",
    ),
    "capex_da_cash_debt": (
        "capex",
        "depreciation_amortization",
        "cash_and_equivalents",
        "total_debt",
    ),
    "interest": ("interest_expense", "interest_income"),
    "bs_core": (
        "total_assets",
        "total_liabilities",
        "current_assets",
        "current_liabilities",
        "stockholders_equity",
        "ppe_net",
        "inventory",
    ),
}.items():
    for _p in _points:
        OWNERSHIP[_p] = _fam
        OWNERSHIP[f"{_p}_resolved"] = _fam


@dataclass
class CellRow:
    line: int
    key: CellKey
    state: str
    value: Decimal | None
    unit: str | None
    decimals: int | None
    source_fact_ids: list[int]
    accession: str | None
    tag: str | None
    members: list[dict[str, Any]] | None
    fsn_set: str | None
    derivation: dict[str, Any] | None
    rule_id: str
    evidence_level: str
    reason_code: str | None
    reason_text: str | None
    defect_class: str | None
    owner: str | None
    root_cause_class: str | None
    input_refs: dict[str, Any]
    fiscal_year: int | None
    fiscal_period: str | None
    period_type: str | None
    fsn_end: date | None
    exact_dates: bool
    period_id: int | None = None
    # fsn.value ids behind the value (FSN store, migration 0118); lineage on their own
    source_value_ids: list[int] = field(default_factory=list)


@dataclass
class LoadReport:
    family: str
    mode: str
    files: list[str]
    sha256: dict[str, str]
    rows: int = 0
    rejected: Counter = field(default_factory=Counter)
    reject_samples: list[dict[str, Any]] = field(default_factory=list)
    unowned_points: set[str] = field(default_factory=set)
    companies: int = 0
    valued_written: int = 0
    reasons_written: int = 0
    deleted: int = 0
    periods_created: int = 0
    facts_materialized: int = 0
    run_id: str | None = None
    overridden: int = 0
    lineage_defects: int = 0
    skipped_loaded: int = 0
    headroom_waits: int = 0
    protected: int = 0
    per_company: list[dict[str, Any]] = field(default_factory=list)

    def reject(self, line: int, why: str, **ctx: Any) -> None:
        self.rejected[why] += 1
        if len(self.reject_samples) < 200:
            self.reject_samples.append({"line": line, "why": why, **ctx})

    def as_dict(self) -> dict[str, Any]:
        d = {
            k: v
            for k, v in self.__dict__.items()
            if k not in ("rejected", "unowned_points")
        }
        d["rejected"] = dict(self.rejected)
        d["unowned_points"] = sorted(self.unowned_points)
        return d


# --------------------------------------------------------------------------
# reading and validating
# --------------------------------------------------------------------------
def _d(v: Any) -> date | None:
    return date.fromisoformat(v) if v else None


def read_file(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    text = gzip.decompress(raw) if path.suffix == ".gz" else raw
    rows = [json.loads(line) for line in text.decode().splitlines() if line.strip()]
    return rows, sha


def parse_row(line: int, r: dict[str, Any], known_points: set[str]) -> CellRow | str:
    """A CellRow, or the rejection reason (spec section 5)."""
    name = r.get("data_point_name")
    if name not in known_points:
        return "unknown_data_point_name"
    grain = r.get("period_grain")
    if grain not in GRAINS:
        return "grain_not_FY_Q_I"
    state = r.get("state")
    if not isinstance(state, str) or state not in STATES:
        return "state_outside_contract"
    try:
        start, end = _d(r.get("period_start")), _d(r.get("period_end"))
        fsn_end = _d(r.get("fsn_end"))
    except ValueError:
        return "bad_date"
    exact = start is not None and end is not None
    if not exact and not (
        r.get("fiscal_year")
        and r.get("fiscal_period")
        and r.get("period_type")
        and fsn_end
    ):
        return "no_period_key"
    ptype = r.get("period_type") or ("instant" if grain == "I" else "duration")
    if (grain == "I") != (ptype == "instant"):
        return "grain_period_type_mismatch"
    if exact and grain == "I" and start != end:
        return "instant_with_span"
    key_end = end or fsn_end
    if key_end < HISTORY_FLOOR:
        return "period_before_history_floor"
    value = r.get("value")
    if state in VALUED:
        if value is None:
            return "valued_state_without_value"
        try:
            value = Decimal(str(value))
        except InvalidOperation:
            return "value_not_decimal"
        if r.get("unit") not in UNITS:
            return "unit_missing_or_unknown"
        if state == "derived" and not r.get("derivation"):
            return "derived_without_derivation"
    else:
        if value is not None:
            return "blank_state_with_value"
        if not r.get("reason_code"):
            return "blank_without_reason_code"
    try:
        parse_rule_id(r.get("rule_id") or "")
    except ValueError:
        return "bad_rule_id"
    if r.get("evidence_level") not in EVIDENCE_LEVELS:
        return "bad_evidence_level"
    try:
        validate_defect(
            state, r.get("defect_class"), r.get("owner"), r.get("root_cause_class")
        )
    except ValueError:
        return "defect_fields_inconsistent"
    try:
        key = CellKey(
            int(r["company_id"]),
            name,
            grain,
            start or fsn_end,
            end or fsn_end,
            r.get("basis") or "latest",
        )
    except (KeyError, ValueError, TypeError):
        return "bad_key"
    return CellRow(
        line=line,
        key=key,
        state=state,
        value=value if state in VALUED else None,
        unit=r.get("unit"),
        decimals=r.get("decimals"),
        source_fact_ids=[int(x) for x in (r.get("source_fact_ids") or [])],
        source_value_ids=[int(x) for x in (r.get("source_value_ids") or [])],
        accession=r.get("accession"),
        tag=r.get("tag"),
        members=r.get("members"),
        fsn_set=r.get("fsn_set"),
        derivation=r.get("derivation"),
        rule_id=r["rule_id"],
        evidence_level=r["evidence_level"],
        reason_code=r.get("reason_code"),
        reason_text=r.get("reason_text"),
        defect_class=r.get("defect_class"),
        owner=r.get("owner"),
        root_cause_class=r.get("root_cause_class"),
        input_refs=r.get("input_refs") or {},
        fiscal_year=r.get("fiscal_year"),
        fiscal_period=r.get("fiscal_period"),
        period_type=ptype,
        fsn_end=fsn_end,
        exact_dates=exact,
    )


# --------------------------------------------------------------------------
# binding and resolving, per company
# --------------------------------------------------------------------------
def bind_periods(
    conn: psycopg.Connection, company_id: int, rows: list[CellRow], *, create: bool
) -> tuple[list[CellRow], list[tuple[CellRow, str]], int]:
    """Set period_id on every row it can; return (bound, [(row, why)], periods_created)."""
    with conn.cursor() as cur:
        cur.execute(
            "select id, start_date, end_date, period_type, fiscal_year, fiscal_period from core.period where company_id = %s",
            (company_id,),
        )
        periods = cur.fetchall()
    exact = {(s, e, t): pid for pid, s, e, t, _fy, _fp in periods}
    by_label: dict[tuple, list[tuple[int, date]]] = defaultdict(list)
    for pid, _s, e, t, fy, fp in periods:
        by_label[(fy, fp, t)].append((pid, e))
    bound, bad, created = [], [], 0
    for r in rows:
        pid = None
        if r.exact_dates:
            pid = exact.get((r.key.period_start, r.key.period_end, r.period_type))
        if pid is None and r.fiscal_year and r.fiscal_period and r.fsn_end:
            cands = [
                (abs((e - r.fsn_end).days), p)
                for p, e in by_label.get(
                    (r.fiscal_year, r.fiscal_period, r.period_type), []
                )
                if abs((e - r.fsn_end).days) <= BIND_DAYS
            ]
            if cands:
                pid = min(cands)[1]
        if pid is None and r.exact_dates and create:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
                    values (%s, %s, %s, %s, %s, %s)
                    on conflict (company_id, start_date, end_date, period_type) do update set fiscal_year = core.period.fiscal_year
                    returning id
                    """,
                    (
                        company_id,
                        r.key.period_start,
                        r.key.period_end,
                        r.period_type,
                        r.fiscal_year,
                        r.fiscal_period,
                    ),
                )
                pid = cur.fetchone()[0]
            exact[(r.key.period_start, r.key.period_end, r.period_type)] = pid
            created += 1
        if pid is None:
            bad.append((r, "period_unresolvable"))
            continue
        r.period_id = pid
        bound.append(r)
    return bound, bad, created


def resolve_facts(
    conn: psycopg.Connection, company_id: int, rows: list[CellRow]
) -> dict[tuple[str, str, int], list[int]]:
    """(accession, tag, period_id) -> core.fact ids, authoritative first, one query per company."""
    accs = {r.accession for r in rows if r.accession}
    tags = {r.tag for r in rows if r.tag}
    for r in rows:
        for m in r.members or []:
            if m.get("accession"):
                accs.add(m["accession"])
            if m.get("tag"):
                tags.add(m["tag"])
    if not accs or not tags:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select fl.accession_number, co.tag, f.period_id, f.id, f.is_authoritative
            from core.fact f
            join core.filing fl on fl.id = f.filing_id
            join core.concept co on co.id = f.concept_id
            where f.company_id = %s and fl.company_id = %s and fl.accession_number = any(%s) and co.tag = any(%s)
            order by f.is_authoritative desc, f.id
            """,
            (company_id, company_id, sorted(accs), sorted(tags)),
        )
        out: dict[tuple[str, str, int], list[int]] = defaultdict(list)
        for acc, tag, pid, fid, _auth in cur.fetchall():
            out[(acc, tag, pid)].append(fid)
    return out


def materialize_fsn_fact(
    conn: psycopg.Connection, company_id: int, cik: str, r: CellRow, period_row: tuple
) -> list[int]:
    """A filed value that exists only in the FSN set (no core.fact): write the
    fact through facts.normalize_payload with an fsn:// lineage row, exactly
    like the B9 instance fallback, and return its fact id(s)."""
    with conn.cursor() as cur:
        cur.execute(
            "select form, filing_date from core.filing where company_id = %s and accession_number = %s",
            (company_id, r.accession),
        )
        fl = cur.fetchone()
    if fl is None:
        return []
    start, end, _ptype, fy, fp = period_row
    taxonomy, _, tag = (r.tag or "").rpartition(":")
    taxonomy = taxonomy or "us-gaap"
    entry = {
        "start": None if r.key.period_grain == "I" else start.isoformat(),
        "end": end.isoformat(),
        "val": r.value,
        "accn": r.accession,
        "fy": fy or end.year,
        "fp": fp or ("FY" if r.key.period_grain == "FY" else "Q"),
        "form": fl[0],
        "filed": fl[1].isoformat(),
    }
    payload = {"cik": cik, "facts": {taxonomy: {tag: {"units": {r.unit: [entry]}}}}}
    pj = json.dumps(payload, default=str, sort_keys=True)
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status, fetched_at)
            values (%s, %s, %s, %s, 200, now()) returning id
            """,
            (
                cik,
                f"fsn://{BUCKET}/{r.fsn_set}/{r.fsn_set}_num.tsv.zst#{r.accession}",
                hashlib.sha256(pj.encode()).hexdigest(),
                f"{BUCKET}/{r.fsn_set}/{r.fsn_set}_num.tsv.zst",
            ),
        )
        raw_id = cur.fetchone()[0]
    normalize_payload(conn, company_id, cik, payload, raw_id)
    with conn.cursor() as cur:
        cur.execute(
            "select id from core.fact where company_id = %s and period_id = %s and raw_object_id = %s",
            (company_id, r.period_id, raw_id),
        )
        return [x[0] for x in cur.fetchall()]


HEADROOM_SLEEP_S = 30.0
HEADROOM_MAX_WAITS = 60  # 30 min, then the shard fails rather than wait forever


def wait_for_headroom(
    conn: psycopg.Connection,
    max_backends: int,
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    """Pause while more than max_backends client backends are open (the founder's connection budget,
    re-checked during a run, not only at its start). Returns the number of waits; raises after
    HEADROOM_MAX_WAITS."""
    for waits in range(HEADROOM_MAX_WAITS + 1):
        used = conn.execute(
            "select count(*) from pg_stat_activity where backend_type = 'client backend'"
        ).fetchone()[0]  # type: ignore[index]
        conn.commit()
        if used <= max_backends:
            return waits
        logger.warning(
            "cell_loader.headroom_wait", used=used, max_backends=max_backends
        )
        sleep(HEADROOM_SLEEP_S)
    raise RuntimeError(
        f"client backends stayed above {max_backends} for {HEADROOM_MAX_WAITS} checks"
    )


def protect_cells(
    conn: psycopg.Connection,
    cid: int,
    scope_ids: list[int],
    valued: list[CellRow],
    blanks: list[CellRow],
    concept_ids: dict[str, int],
    run_id: str,
    package_sha: str,
) -> int:
    """Inside the company's transaction: the family's keys of this company are protected (0113) exactly
    where this load wrote them. Valued keys carry their value; a blank key is protected only where the
    0113 value column accepts null (a migration), else it is left to the reason store."""
    nullable = (
        conn.execute(
            "select is_nullable from information_schema.columns where table_schema = 'analytics' "
            "and table_name = 'slot_protected_cell' and column_name = 'value'"
        ).fetchone()
        or ("NO",)
    )[0] == "YES"
    keys: dict[tuple[int, int], tuple[str, Decimal | None]] = {}
    if nullable:
        for b in blanks:
            if b.period_id is not None:
                keys[(concept_ids[b.key.data_point_name], b.period_id)] = (
                    b.rule_id,
                    None,
                )
    for r in valued:
        keys[(concept_ids[r.key.data_point_name], r.period_id)] = (r.rule_id, r.value)  # type: ignore[index]
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.slot_protected_cell where company_id = %s and canonical_concept_id = any(%s)",
            (cid, scope_ids),
        )
        if keys:
            cur.execute(
                """
                insert into analytics.slot_protected_cell
                    (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256)
                select %s, u.c, u.p, u.r, u.v, %s, %s
                from unnest(%s::bigint[], %s::bigint[], %s::text[], %s::numeric[]) as u(c, p, r, v)
                """,
                (
                    cid,
                    run_id,
                    package_sha,
                    [k[0] for k in keys],
                    [k[1] for k in keys],
                    [v[0] for v in keys.values()],
                    [v[1] for v in keys.values()],
                ),
            )
    return len(keys)


def _has_source_value_ids(conn: psycopg.Connection) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from information_schema.columns where table_schema = 'analytics' "
            "and table_name = 'canonical_fact' and column_name = 'source_value_ids'"
        )
        return cur.fetchone()[0] == 1


def _has_provenance_columns(conn: psycopg.Connection) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from information_schema.columns where table_schema = 'analytics' "
            "and table_name = 'canonical_fact' and column_name in ('rule_run_id', 'family')"
        )
        return cur.fetchone()[0] == 2


LINEAGE_REASON = "value_lineage_unresolved"


def demote_to_lineage_defect(r: CellRow, why: str) -> None:
    """A filed value whose source cannot be tied to a core.fact (no accession/tag,
    or nothing resolves) is never published: the key stays, as a defect
    (ingestion, data_engineer_l2) carrying the unpublished value in input_refs,
    so the cell is an explained blank, not a reasonless one."""
    r.input_refs = {
        **r.input_refs,
        "unpublished_value": str(r.value),
        "why": why,
        "accession": r.accession,
        "tag": r.tag,
    }
    r.state, r.value, r.unit, r.derivation = "defect", None, None, None
    r.reason_code = LINEAGE_REASON
    r.reason_text = (
        f"Value not shown: its source could not be tied to a stored fact ({why})."
    )
    r.defect_class, r.owner, r.root_cause_class = (
        "ingestion",
        "data_engineer_l2",
        "ingestion",
    )


def to_reason(r: CellRow) -> BlankReason:
    return BlankReason(
        key=r.key,
        state=r.state,
        rule_id=r.rule_id,
        reason_code=r.reason_code or "",
        defect_class=r.defect_class,
        owner=r.owner,
        root_cause_class=r.root_cause_class,
        reason_text=r.reason_text,
        input_refs={
            **r.input_refs,
            "accession": r.accession,
            "tag": r.tag,
            "fsn_set": r.fsn_set,
        },
        source_fact_ids=tuple(r.source_fact_ids),
    )


# --------------------------------------------------------------------------
# the load
# --------------------------------------------------------------------------
def apply_defect_overrides(
    cells: list[CellRow],
    overrides: list[dict[str, Any]],
    reason_code: str,
    rule_id: str,
) -> int:
    """Turn the cells named in `overrides` (company_id, data_point_name,
    period_grain, period_start, period_end, optional why/input_accessions) into
    defect(period, period_engineer) blanks with `reason_code`: the way a lane's
    late-found suspect cells (e.g. mixed-vintage derived quarters) are kept out
    of production without losing the key. Returns the number of cells changed."""
    want = {
        (
            int(o["company_id"]),
            o["data_point_name"],
            o["period_grain"],
            date.fromisoformat(o["period_start"]),
            date.fromisoformat(o["period_end"]),
        ): o
        for o in overrides
    }
    n = 0
    for c in cells:
        k = (
            c.key.company_id,
            c.key.data_point_name,
            c.key.period_grain,
            c.key.period_start,
            c.key.period_end,
        )
        o = want.get(k)
        if o is None:
            continue
        c.state, c.value, c.unit, c.derivation = "defect", None, None, None
        c.reason_code = reason_code
        c.reason_text = (
            "Held: "
            + "; ".join(o.get("why") or [reason_code])
            + (
                f" (inputs {', '.join(o['input_accessions'])})"
                if o.get("input_accessions")
                else ""
            )
        )
        c.defect_class, c.owner, c.root_cause_class = (
            "period",
            "period_engineer",
            "period",
        )
        c.rule_id = rule_id
        c.input_refs = {**c.input_refs, "override": o}
        n += 1
    return n


def load(
    conn: psycopg.Connection,
    family: str,
    paths: list[Path],
    *,
    apply: bool,
    manifest_rule_id: str | None = None,
    git_commit: str | None = None,
    data_points: list[str] | None = None,
    defect_overrides: list[dict[str, Any]] | None = None,
    defect_reason: str = "mixed_vintage_inputs",
    connect: Callable[[], psycopg.Connection] | None = None,
    shard: tuple[int, int] | None = None,
    skip_loaded: bool = False,
    max_backends: int | None = None,
    sleep: Callable[[float], None] = time.sleep,
    protect: bool = False,
) -> LoadReport:
    """paths: one or more cell files of ONE family (merged; a key in two files is
    a rejection). data_points: the delete scope (default: the manifest's or the
    file's data points). apply=False plans inside a transaction and rolls back.
    max_backends: before each company, wait while more client backends than this are open.
    protect: record every written key in analytics.slot_protected_cell (0113) so the nightly refresh
    cannot overwrite it; the family's other keys of the company lose their protection."""
    mode = "apply" if apply else "dry_run"
    rep = LoadReport(family, mode, [str(p) for p in paths], {})
    raw_rows: list[tuple[int, dict[str, Any]]] = []
    manifest: dict[str, Any] = {}
    for p in paths:
        m = p.with_name("manifest.json")
        if m.exists() and not manifest:
            manifest = json.loads(m.read_text())
        rows, sha = read_file(p)
        rep.sha256[str(p)] = sha
        raw_rows.extend((i + 1, r) for i, r in enumerate(rows))
    rep.rows = len(raw_rows)
    # the load's own rule id: the manifest's when it is ONE rule id; a family whose
    # manifest lists several rule ids (one per data point) is run under cells.<family>@1
    m_rule = manifest.get("rule_id")
    rule_id = (
        manifest_rule_id
        or (m_rule if isinstance(m_rule, str) else None)
        or f"cells.{family}@1"
    )
    parse_rule_id(rule_id)
    with conn.cursor() as cur:
        cur.execute("select id, name from analytics.canonical_concept")
        concept_ids = {name: cid for cid, name in cur.fetchall()}
    cells: list[CellRow] = []
    seen: set[tuple] = set()
    for line, r in raw_rows:
        parsed = parse_row(line, r, set(concept_ids))
        if isinstance(parsed, str):
            rep.reject(line, parsed, data_point_name=r.get("data_point_name"))
            continue
        owner = OWNERSHIP.get(parsed.key.data_point_name)
        if owner is None:
            rep.unowned_points.add(parsed.key.data_point_name)
        elif owner != family:
            rep.reject(
                line,
                "key_owned_by_another_family",
                data_point_name=parsed.key.data_point_name,
                owner=owner,
            )
            continue
        k = (
            parsed.key.company_id,
            parsed.key.data_point_name,
            parsed.key.period_grain,
            parsed.key.period_start,
            parsed.key.period_end,
            parsed.key.basis,
        )
        if k in seen:
            rep.reject(
                line, "duplicate_key", data_point_name=parsed.key.data_point_name
            )
            continue
        seen.add(k)
        cells.append(parsed)
    scope_names = (
        data_points
        or manifest.get("data_points")
        or sorted({c.key.data_point_name for c in cells})
    )
    # Guard (scrooner-0f 2026-11-01): a data point whose file carries ZERO valued
    # cells would be blanked for every company by delete-then-insert (the
    # interest_income case). Such points leave the delete scope and their rows
    # are rejected, listed under data_point_has_no_valued_cells.
    if defect_overrides:
        rep.overridden = apply_defect_overrides(
            cells, defect_overrides, defect_reason, f"cells.{family}_override@1"
        )
    valued_points = {c.key.data_point_name for c in cells if c.state in VALUED}
    empty_points = [n for n in scope_names if n not in valued_points]
    for n in empty_points:
        rep.reject(0, "data_point_has_no_valued_cells", data_point_name=n)
    scope_names = [n for n in scope_names if n in valued_points]
    cells = [c for c in cells if c.key.data_point_name in valued_points]
    scope_ids = [concept_ids[n] for n in scope_names if n in concept_ids]
    by_company: dict[int, list[CellRow]] = defaultdict(list)
    for c in cells:
        by_company[c.key.company_id].append(c)
    if shard is not None:
        # shard i of n by company_id: n loaders on one file in parallel, disjoint companies,
        # each under its own rule_run (stats carry the shard)
        i, n = shard
        by_company = defaultdict(
            list, {cid: r for cid, r in by_company.items() if cid % n == i}
        )
        rep.files = [f"{f} [shard {i}/{n}]" for f in rep.files]
    if connect is not None:
        # parsing a 280k-row file takes minutes; the connection opened before it has
        # gone stale through the pooler twice (SSL "Operation timed out"), so the
        # database work starts on a fresh one
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass
        conn = connect()
        prov = _has_provenance_columns(conn)
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik from core.company where id = any(%s)", (sorted(by_company),)
        )
        ciks = dict(cur.fetchall())
    for cid in sorted(by_company):
        if cid not in ciks:
            for c in by_company[cid]:
                rep.reject(c.line, "unknown_company", company_id=cid)
            del by_company[cid]
    prov = _has_provenance_columns(conn)
    if any(c.source_value_ids for c in cells) and not _has_source_value_ids(conn):
        raise RuntimeError(
            "cells carry source_value_ids but analytics.canonical_fact has no such column (migration 0118)"
        )
    done_companies: set[int] = set()
    if skip_loaded and apply and _has_provenance_columns(conn):
        # companies already loaded from this very file (sha) by an earlier apply run: skip them
        with conn.cursor() as cur:
            cur.execute(
                "select distinct cf.company_id from analytics.canonical_fact cf join analytics.rule_run r on r.run_id = cf.rule_run_id "
                "where cf.family = %s and r.mode = 'apply' and r.before_image_ref = %s and cf.company_id = any(%s)",
                (family, ",".join(rep.sha256.values())[:200], sorted(by_company)),
            )
            done_companies = {r[0] for r in cur.fetchall()}
        for cid in done_companies:
            by_company.pop(cid, None)
        rep.skipped_loaded = len(done_companies)
    run_id = start_rule_run(
        conn,
        rule_id,
        mode,
        "on" if apply else "off",
        sorted(ciks.values()),
        git_commit=git_commit,
        before_image_ref=",".join(rep.sha256.values())[:200],
    )
    rep.run_id = run_id
    conn.commit()  # the manifest row stands alone; every company below is its own transaction
    done = 0
    for cid in sorted(by_company):
        company_rows = by_company[cid]
        if max_backends is not None:
            rep.headroom_waits += wait_for_headroom(conn, max_backends, sleep)
        for attempt in range(1, 4):
            try:
                _load_company(
                    conn,
                    cid,
                    company_rows,
                    ciks[cid],
                    family,
                    run_id,
                    scope_ids,
                    concept_ids,
                    prov,
                    apply,
                    rep,
                    protect=protect,
                    package_sha=",".join(rep.sha256.values())[:200],
                )
            except _PlanRollback:
                break
            except psycopg.OperationalError as exc:
                # a dropped pooler/SSL connection mid-run: the company's transaction is
                # gone, so reconnect and redo THIS company (idempotent), up to 3 times
                logger.warning(
                    "cell_loader.reconnect",
                    company_id=cid,
                    attempt=attempt,
                    error=repr(exc)[:160],
                )
                if connect is None or attempt == 3:
                    raise
                try:
                    conn.close()
                except Exception:  # noqa: BLE001
                    pass
                conn = connect()
                prov = _has_provenance_columns(conn)
            else:
                if apply:
                    conn.commit()
                break
        done += 1
        if done % 25 == 0 or done == len(by_company):
            logger.info(
                "cell_loader.progress",
                family=family,
                mode=mode,
                companies=done,
                of=len(by_company),
                valued=rep.valued_written,
                reasons=rep.reasons_written,
                rejected=sum(rep.rejected.values()),
            )
    return _finish(conn, run_id, rep, apply)


def _load_company(
    conn: psycopg.Connection,
    cid: int,
    rows: list[CellRow],
    cik: str,
    family: str,
    run_id: str,
    scope_ids: list[int],
    concept_ids: dict[str, int],
    prov: bool,
    apply: bool,
    rep: LoadReport,
    *,
    protect: bool = False,
    package_sha: str = "",
) -> None:
    """One company in one transaction; plan mode raises _PlanRollback at the end so it rolls back."""
    if True:
        with conn.transaction():
            # the 0113 guard (trg_slot_protected_cell_guard, live) silently skips any
            # canonical_fact write on a protected cell unless the session is the slot
            # writer; the cell loader IS the authorised writer of its family's cells
            conn.execute("set local scrooner.slot_writer = 'on'")
            bound, bad, created = bind_periods(conn, cid, rows, create=True)
            for r, why in bad:
                rep.reject(
                    r.line, why, company_id=cid, data_point_name=r.key.data_point_name
                )
            rep.periods_created += created
            facts = resolve_facts(conn, cid, bound)
            with conn.cursor() as cur:
                cur.execute(
                    "select id, start_date, end_date, period_type, fiscal_year, fiscal_period from core.period where id = any(%s)",
                    ([r.period_id for r in bound],),
                )
                prow = {x[0]: x[1:] for x in cur.fetchall()}
            valued: list[CellRow] = []
            reasons_by_rule: dict[str, list[BlankReason]] = defaultdict(list)
            for r in bound:
                if (
                    r.state == "value"
                    and not r.source_fact_ids
                    and not r.source_value_ids
                    and not r.tag
                    and not r.members
                ):
                    demote_to_lineage_defect(
                        r, "no accession/tag and no fact ids in the cell file"
                    )
                    rep.lineage_defects += 1
                if r.state in BLANK_STATES:
                    reasons_by_rule[r.rule_id].append(to_reason(r))
                    continue
                if not r.source_fact_ids and r.state == "value":
                    ids: list[int] = []
                    if r.accession and r.tag and r.period_id is not None:
                        ids += facts.get((r.accession, r.tag, r.period_id), [])
                    for m in r.members or []:
                        m_acc, m_tag = m.get("accession") or r.accession, m.get("tag")
                        if m_acc and m_tag and r.period_id is not None:
                            ids += facts.get((m_acc, m_tag, r.period_id), [])
                    if not ids and r.source_value_ids:
                        # an FSN-store cell: fsn.value ids are its lineage; core.fact ids only where they resolve
                        valued.append(r)
                        continue
                    if not ids and r.fsn_set and r.accession and r.tag:
                        ids = materialize_fsn_fact(conn, cid, cik, r, prow[r.period_id])
                        rep.facts_materialized += len(ids)
                    if not ids:
                        demote_to_lineage_defect(
                            r,
                            f"no core.fact for {r.tag} in {r.accession} at this period",
                        )
                        rep.lineage_defects += 1
                        reasons_by_rule[r.rule_id].append(to_reason(r))
                        continue
                    r.source_fact_ids = sorted(set(ids))
                valued.append(r)
            with conn.cursor() as cur:
                cur.execute(
                    "delete from analytics.canonical_fact where company_id = %s and canonical_concept_id = any(%s)",
                    (cid, scope_ids),
                )
                rep.deleted += cur.rowcount
                payload: list[dict[str, Any]] = [
                    {
                        "company_id": cid,
                        "canonical_concept_id": concept_ids[r.key.data_point_name],
                        "period_id": r.period_id,
                        "value": r.value,
                        "source_fact_ids": r.source_fact_ids,
                        "source_value_ids": r.source_value_ids,
                        "run_id": run_id,
                        "family": family,
                    }
                    for r in valued
                ]
                if payload:
                    # one statement per company (unnest of parallel arrays): executemany
                    # cost one round trip per row over the remote pooler
                    cols = {
                        "company_id": [r["company_id"] for r in payload],
                        "canonical_concept_id": [
                            r["canonical_concept_id"] for r in payload
                        ],
                        "period_id": [r["period_id"] for r in payload],
                        "value": [r["value"] for r in payload],
                        "run_id": [r["run_id"] for r in payload],
                        "family": [r["family"] for r in payload],
                    }
                    extra_cols = ", rule_run_id, family" if prov else ""
                    extra_sel = ", v.run_id::uuid, v.family" if prov else ""
                    cur.execute(
                        f"""
                        insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids{extra_cols})
                        select v.company_id, v.canonical_concept_id, v.period_id, v.value, '{{}}'::bigint[]{extra_sel}
                        from unnest(%(company_id)s::bigint[], %(canonical_concept_id)s::bigint[], %(period_id)s::bigint[],
                                    %(value)s::numeric[], %(run_id)s::text[], %(family)s::text[])
                             as v(company_id, canonical_concept_id, period_id, value, run_id, family)
                        """,
                        cols,
                    )
                    # source_fact_ids are ragged arrays: one update statement with unnest of (period, concept, ids-as-text)
                    cur.execute(
                        """
                        update analytics.canonical_fact cf set source_fact_ids = u.ids::bigint[]
                        from unnest(%(concept)s::bigint[], %(period)s::bigint[], %(ids)s::text[]) as u(concept, period, ids)
                        where cf.company_id = %(cid)s and cf.canonical_concept_id = u.concept and cf.period_id = u.period
                        """,
                        {
                            "cid": cid,
                            "concept": [
                                r["canonical_concept_id"]
                                for r in payload
                                if r["source_fact_ids"]
                            ],
                            "period": [
                                r["period_id"] for r in payload if r["source_fact_ids"]
                            ],
                            "ids": [
                                "{"
                                + ",".join(str(i) for i in r["source_fact_ids"])
                                + "}"
                                for r in payload
                                if r["source_fact_ids"]
                            ],
                        },
                    )
                    with_values = [r for r in payload if r["source_value_ids"]]
                    if with_values:
                        cur.execute(
                            """
                            update analytics.canonical_fact cf set source_value_ids = u.ids::bigint[]
                            from unnest(%(concept)s::bigint[], %(period)s::bigint[], %(ids)s::text[]) as u(concept, period, ids)
                            where cf.company_id = %(cid)s and cf.canonical_concept_id = u.concept and cf.period_id = u.period
                            """,
                            {
                                "cid": cid,
                                "concept": [
                                    r["canonical_concept_id"] for r in with_values
                                ],
                                "period": [r["period_id"] for r in with_values],
                                "ids": [
                                    "{"
                                    + ",".join(str(i) for i in r["source_value_ids"])
                                    + "}"
                                    for r in with_values
                                ],
                            },
                        )
            rep.valued_written += len(valued)
            n_reasons = 0
            for rid, reasons in reasons_by_rule.items():
                n_reasons += replace_rule_reasons(conn, run_id, cid, rid, reasons)
            rep.reasons_written += n_reasons
            if protect:
                blanks = [r for r in bound if r.state in BLANK_STATES]
                rep.protected += protect_cells(
                    conn,
                    cid,
                    scope_ids,
                    valued,
                    blanks,
                    concept_ids,
                    run_id,
                    package_sha,
                )
            rep.companies += 1
            rep.per_company.append(
                {
                    "company_id": cid,
                    "cik": cik,
                    "valued": len(valued),
                    "reasons": n_reasons,
                    "unbound": len(bad),
                    "periods_created": created,
                }
            )
            if not apply:
                raise _PlanRollback


class _PlanRollback(Exception):
    """Raised inside the per-company transaction in plan mode so it rolls back."""


def _finish(
    conn: psycopg.Connection, run_id: str, rep: LoadReport, apply: bool
) -> LoadReport:
    stats = {
        k: v
        for k, v in rep.as_dict().items()
        if k not in ("per_company", "reject_samples")
    }
    finish_rule_run(conn, run_id, stats)
    conn.commit()
    logger.info(
        "cell_loader.done",
        **{k: v for k, v in stats.items() if k not in ("sha256", "files")},
    )
    return rep


BEFORE_IMAGE_TABLES = (
    ("analytics.canonical_fact", "canonical_fact.csv.gz", "canonical_concept_id"),
    ("analytics.cell_blank_reason", "cell_blank_reason.csv.gz", "data_point_name"),
    # protection rows (0113): a restored key is protected exactly as before the write
    (
        "analytics.slot_protected_cell",
        "slot_protected_cell.csv.gz",
        "canonical_concept_id",
    ),
)


def restore(
    conn: psycopg.Connection,
    before_dir: Path,
    company_ids: list[int],
    data_points: list[str],
    *,
    apply: bool,
) -> dict[str, Any]:
    """Put a before-image (CSV with header, as `copy ... to stdout with csv header` wrote it) back for the
    named companies and data points: per company, in one transaction, delete the current canonical_fact,
    cell_blank_reason and slot_protected_cell rows in scope and insert the before-image rows (original ids). Rows outside the
    data points are not touched; core.period rows a load created stay (harmless, unreferenced). Plan mode rolls
    back each company."""
    import gzip

    with conn.cursor() as cur:
        cur.execute(
            "select id, name from analytics.canonical_concept where name = any(%s)",
            (data_points,),
        )
        concept_ids = [r[0] for r in cur.fetchall()]
    staged: dict[str, tuple[str, list[str]]] = {}
    for table, fname, _ in BEFORE_IMAGE_TABLES:
        path = before_dir / fname
        with gzip.open(path, "rt") as fh:
            header = fh.readline().strip()
        cols = header.split(",")
        tmp = "_before_" + table.split(".")[1]
        conn.execute(f"create temp table if not exists {tmp} (like {table})")
        conn.execute(f"truncate {tmp}")
        with (
            gzip.open(path, "rb") as fh,
            conn.cursor().copy(
                f"copy {tmp} ({header}) from stdin with csv header"
            ) as cp,
        ):
            while chunk := fh.read(1 << 20):
                cp.write(chunk)
        staged[table] = (tmp, cols)
    conn.commit()
    out: dict[str, Any] = {"mode": "apply" if apply else "dry_run", "companies": {}}
    for cid in company_ids:
        counts: dict[str, int] = {}
        try:
            with conn.transaction():
                conn.execute("set local scrooner.slot_writer = 'on'")
                for table, _, key in BEFORE_IMAGE_TABLES:
                    tmp, cols = staged[table]
                    scope = (
                        concept_ids if key == "canonical_concept_id" else data_points
                    )
                    collist = ", ".join(cols)
                    with conn.cursor() as cur:
                        cur.execute(
                            f"delete from {table} where company_id = %s and {key} = any(%s)",
                            (cid, scope),
                        )
                        counts[f"{table}.deleted"] = cur.rowcount
                        overriding = (
                            ""
                            if table == "analytics.slot_protected_cell"
                            else " overriding system value"
                        )
                        cur.execute(
                            f"insert into {table} ({collist}){overriding} "
                            f"select {collist} from {tmp} where company_id = %s and {key} = any(%s)",
                            (cid, scope),
                        )
                        counts[f"{table}.restored"] = cur.rowcount
                if not apply:
                    raise _PlanRollback
        except _PlanRollback:
            pass
        out["companies"][cid] = counts
    return out
