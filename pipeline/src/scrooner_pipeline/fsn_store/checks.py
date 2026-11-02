"""Automatic proof of a stored filing (design §5): per statement column, do the filer's own
calculation arcs and the accounting identities hold? Results go to fsn.filing_check; a
served value may only come from a column whose checks all pass (fsn_select).

Column = (stmt, ddate, qtrs) of a filing. Tolerance = Σ 0.5·10^(-dcml) over the terms
(a child with dcml -6 contributes 500,000), with `common.rounding_unit`-style fallback of
one unit of the coarsest decimals when dcml is missing.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Iterable

import psycopg

STATEMENTS = ("BS", "IS", "CF")
# identities by standard tag (us-gaap), checked when every term is printed in the column
BS_IDENTITIES = (
    (
        "bs_assets_eq_liabilities_equity",
        ("Assets",),
        ("LiabilitiesAndStockholdersEquity",),
    ),
)
CF_CHANGE_TAGS = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
    "CashAndCashEquivalentsPeriodIncreaseDecrease",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
)
CF_PARTS = (
    "NetCashProvidedByUsedInOperatingActivities",
    "NetCashProvidedByUsedInInvestingActivities",
    "NetCashProvidedByUsedInFinancingActivities",
)
CF_FX = (
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "EffectOfExchangeRateOnCashAndCashEquivalents",
    # the TOTAL effect on cash under its other standard names (cohort dry run 41515845455: 231 + 80 + 9
    # companies print these, so every cash-flow column of theirs failed cf_parts_eq_change and every
    # CFO / buyback / dividend value in it was held; Nucor FY2024: parts -2,813 + FX -16 = change -2,829).
    # Never the discontinued-operations COMPONENT tags (…DisposalGroupIncludingDiscontinuedOperations,
    # …DiscontinuedOperations): a component is not the total, so they stay out.
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
    "EffectOfExchangeRateOnCashAndCashEquivalentsContinuingOperations",
    "EffectOfExchangeRateOnCash",
)
IS_GP = ("is_gross_profit", "GrossProfit", "Revenues", "CostOfRevenue")


@dataclass(frozen=True)
class Print:
    tag: str
    version: str
    value: Decimal
    dcml: int | None
    line: int | None


# FSN writes decimals="INF" (exact) as a sentinel; |dcml| beyond this is exact (no rounding) and
# would otherwise make a tolerance numeric cannot store (cohort run 41490624081: 17 shards failed)
DCML_EXACT = 20


def tol_of(dcmls: Iterable[int | None]) -> Decimal:
    t = Decimal(0)
    for d in dcmls:
        d = 0 if d is None else d
        if abs(d) > DCML_EXACT:
            continue  # an exact print adds no rounding slack
        t += Decimal(5) * (Decimal(10) ** (-d - 1))
    return t


def load_filing(conn: psycopg.Connection, filing_id: int) -> dict[str, Any]:
    """Statement lines, non-dimensional values per (stmt, ddate, qtrs) column, and calc arcs of one filing."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select l.stmt, l.line, t.tag, t.version, l.inpth
            from fsn.line l join fsn.tag t on t.id = l.tag_id
            where l.filing_id = %s and l.stmt in ('BS', 'IS', 'CF')
            order by l.stmt, l.report, l.line
            """,
            (filing_id,),
        )
        lines = cur.fetchall()
        cur.execute(
            """
            select t.tag, t.version, v.ddate, v.qtrs, v.value, v.dcml
            from fsn.value v join fsn.tag t on t.id = v.tag_id
            where v.filing_id = %s and v.dim_id = 0 and v.value is not null and v.uom = 'USD'
            """,
            (filing_id,),
        )
        values = cur.fetchall()
        cur.execute(
            """
            select a.grp, a.arc, p.tag, p.version, c.tag, c.version, a.weight
            from fsn.calc_arc a join fsn.tag p on p.id = a.parent_tag_id join fsn.tag c on c.id = a.child_tag_id
            where a.filing_id = %s
            """,
            (filing_id,),
        )
        arcs = cur.fetchall()
    stmt_of: dict[tuple[str, str], str] = {}
    line_of: dict[tuple[str, str], int] = {}
    on: dict[str, set[str]] = defaultdict(
        set
    )  # statement -> tags on it (a tag may sit on two)
    for stmt, line, tag, version, inpth in lines:
        if inpth:
            continue
        stmt_of.setdefault((tag, version), stmt)
        line_of.setdefault((tag, version), line)
        on[stmt].add(tag)
    flat: dict[tuple[str, date, int], Print] = {}
    for tag, version, ddate, qtrs, value, dcml in values:
        flat.setdefault(
            (tag, ddate, qtrs), Print(tag, version, Decimal(value), dcml, None)
        )
    by_col: dict[tuple[str, date, int], dict[tuple[str, str], Print]] = defaultdict(
        dict
    )
    for tag, version, ddate, qtrs, value, dcml in values:
        stmt = stmt_of.get((tag, version))
        if stmt is None:
            continue
        by_col[(stmt, ddate, qtrs)][(tag, version)] = Print(
            tag, version, Decimal(value), dcml, line_of.get((tag, version))
        )
    groups: dict[tuple[str, str, int], list[tuple[str, str, int]]] = defaultdict(list)
    for grp, _arc, ptag, pver, ctag, cver, w in arcs:
        groups[(ptag, pver, grp)].append((ctag, cver, w))
    return {
        "stmt_of": stmt_of,
        "columns": by_col,
        "groups": groups,
        "on": on,
        "values": flat,
    }


def check_column(
    stmt: str, col: dict[tuple[str, str], Print], groups: dict, stmt_of: dict
) -> list[dict[str, Any]]:
    """Checks of one column: every calc parent with all children printed in this column, plus the identities."""
    out: list[dict[str, Any]] = []
    # calc arcs: parent = Σ weight·child, when parent and every child are printed on this statement column
    for (ptag, pver, grp), children in groups.items():
        parent = col.get((ptag, pver))
        if parent is None or len(children) < 2:
            continue
        terms = [(t, w) for c, v, w in children if (t := col.get((c, v))) is not None]
        if len(terms) < len(children):
            continue
        if any(stmt_of.get((c, v)) != stmt for c, v, _ in children):
            continue
        rhs = sum((t.value * w for t, w in terms), Decimal(0))
        tol = tol_of([parent.dcml, *(t.dcml for t, _ in terms)])
        out.append(
            {
                "check_id": f"calc:{ptag}:{grp}",
                "ok": abs(parent.value - rhs) <= tol,
                "lhs": parent.value,
                "rhs": rhs,
                "tol": tol,
                "detail": {
                    "parent": ptag,
                    "children": [[c, w] for c, _v, w in children],
                },
            }
        )
    if stmt == "BS":
        for check_id, lhs_tags, rhs_tags in BS_IDENTITIES:
            lhs = [p for (t, _v), p in col.items() if t in lhs_tags]
            rhs = [p for (t, _v), p in col.items() if t in rhs_tags]
            if lhs and rhs:
                l, r = lhs[0], rhs[0]
                tol = tol_of([l.dcml, r.dcml])
                out.append(
                    {
                        "check_id": check_id,
                        "ok": abs(l.value - r.value) <= tol,
                        "lhs": l.value,
                        "rhs": r.value,
                        "tol": tol,
                        "detail": {},
                    }
                )
    if stmt == "CF":
        parts = [p for (t, _v), p in col.items() if t in CF_PARTS]
        change = [p for (t, _v), p in col.items() if t in CF_CHANGE_TAGS]
        if len(parts) == 3 and change:
            fx = [p for (t, _v), p in col.items() if t in CF_FX]
            # Whether the change line includes the FX line is the filer's layout, not the tag's name:
            # the pre-2018 CashAndCashEquivalentsPeriodIncreaseDecrease is used both ways (MSFT
            # includes FX, HD prints the change before FX). The column ties if it ties either way;
            # the "Excluding" tag never includes FX. The detail records which form tied.
            base = sum((p.value for p in parts), Decimal(0))
            tol_no = tol_of([change[0].dcml, *(p.dcml for p in parts)])
            forms = [("without_fx", base, tol_no)]
            if fx and "Excluding" not in change[0].tag:
                forms.insert(
                    0, ("with_fx", base + fx[0].value, tol_no + tol_of([fx[0].dcml]))
                )
            form, rhs, tol = next(
                (f for f in forms if abs(change[0].value - f[1]) <= f[2]), forms[0]
            )
            with_fx = form == "with_fx"
            out.append(
                {
                    "check_id": "cf_parts_eq_change",
                    "ok": abs(change[0].value - rhs) <= tol,
                    "lhs": change[0].value,
                    "rhs": rhs,
                    "tol": tol,
                    "detail": {
                        "change_tag": change[0].tag,
                        "fx_included": with_fx,
                    },
                }
            )
    if stmt == "IS":
        gp = {t: p for (t, _v), p in col.items() if t in IS_GP[1:]}
        if len(gp) == 3:
            rhs = gp["Revenues"].value - gp["CostOfRevenue"].value
            tol = tol_of([p.dcml for p in gp.values()])
            out.append(
                {
                    "check_id": IS_GP[0],
                    "ok": abs(gp["GrossProfit"].value - rhs) <= tol,
                    "lhs": gp["GrossProfit"].value,
                    "rhs": rhs,
                    "tol": tol,
                    "detail": {},
                }
            )
    return out


# NI incl. NCI - NCI = NI attributable to the parent (IS column)
NI_TOTAL, NI_NCI, NI_PARENT = (
    "ProfitLoss",
    "NetIncomeLossAttributableToNoncontrollingInterest",
    "NetIncomeLoss",
)
NI_TAGS = (NI_TOTAL, NI_PARENT)
CF_CASH_TOTAL = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
BS_CASH = (
    "CashAndCashEquivalentsAtCarryingValue",
    "CashCashEquivalentsAndShortTermInvestments",
    "Cash",
)
BS_RESTRICTED = (
    "RestrictedCash",
    "RestrictedCashCurrent",
    "RestrictedCashNoncurrent",
    "RestrictedCashAndCashEquivalentsAtCarryingValue",
    "RestrictedCashAndCashEquivalentsNoncurrent",
    "RestrictedCashAndInvestmentsCurrent",
)


def _row(
    check_id: str, lhs: Print, rhs_terms: list[Print], detail: dict
) -> dict[str, Any]:
    rhs = sum((p.value for p in rhs_terms), Decimal(0))
    tol = tol_of([lhs.dcml, *(p.dcml for p in rhs_terms)])
    return {
        "check_id": check_id,
        "ok": abs(lhs.value - rhs) <= tol,
        "lhs": lhs.value,
        "rhs": rhs,
        "tol": tol,
        "detail": detail,
    }


def check_ties(
    on: dict[str, set[str]], values: dict[tuple[str, date, int], Print]
) -> list[tuple[str, date, int, dict[str, Any]]]:
    """Ties across lines and statements of ONE filing (design §5), as (stmt, ddate, qtrs, check):
    IS: ProfitLoss - NCI = NetIncomeLoss when all three sit on the IS;
    CF: the net income line the CF starts from equals the same-named IS line;
    CF: closing cash incl. restricted = BS cash + the restricted-cash lines the BS prints
    (decided only when the BS prints restricted cash or the CF total is cash alone)."""
    out: list[tuple[str, date, int, dict[str, Any]]] = []
    cols = {(d, q) for (_t, d, q) in values}
    for ddate, qtrs in sorted(cols):

        def v(tag: str, stmt: str) -> Print | None:
            return values.get((tag, ddate, qtrs)) if tag in on.get(stmt, ()) else None

        if qtrs > 0:
            total, nci, parent = v(NI_TOTAL, "IS"), v(NI_NCI, "IS"), v(NI_PARENT, "IS")
            if total and nci and parent:
                nci_neg = Print(nci.tag, nci.version, -nci.value, nci.dcml, None)
                out.append(
                    (
                        "IS",
                        ddate,
                        qtrs,
                        _row(
                            "is_ni_total_minus_nci_eq_parent",
                            parent,
                            [total, nci_neg],
                            {},
                        ),
                    )
                )
            for tag in NI_TAGS:
                cf = v(tag, "CF")
                if cf is None:
                    continue
                is_ = [p for t in NI_TAGS if (p := v(t, "IS")) is not None]
                if is_:
                    best = min(is_, key=lambda p: abs(p.value - cf.value))
                    out.append(
                        (
                            "CF",
                            ddate,
                            qtrs,
                            _row(
                                "cross_cf_ni_eq_is_ni",
                                cf,
                                [best],
                                {"cf_tag": tag, "is_tag": best.tag},
                            ),
                        )
                    )
                break
        else:
            cf_total = v(CF_CASH_TOTAL, "CF")
            cash = next((p for t in BS_CASH if (p := v(t, "BS")) is not None), None)
            if cf_total is None or cash is None:
                continue
            restricted = [p for t in BS_RESTRICTED if (p := v(t, "BS")) is not None]
            if not restricted and cf_total.value != cash.value:
                continue  # restricted cash held in another BS line: not decidable here
            out.append(
                (
                    "CF",
                    ddate,
                    qtrs,
                    _row(
                        "cross_cf_closing_cash_eq_bs_cash",
                        cf_total,
                        [cash, *restricted],
                        {"bs_tags": [cash.tag, *(p.tag for p in restricted)]},
                    ),
                )
            )
    return out


def check_filing(
    conn: psycopg.Connection, filing_id: int, *, write: bool = True
) -> dict[str, int]:
    """Run every column check of one filing; replace its fsn.filing_check rows. Returns counts."""
    data = load_filing(conn, filing_id)
    rows = []
    for (stmt, ddate, qtrs), col in data["columns"].items():
        for c in check_column(stmt, col, data["groups"], data["stmt_of"]):
            rows.append(
                (
                    filing_id,
                    stmt,
                    ddate,
                    qtrs,
                    c["check_id"],
                    c["ok"],
                    c["lhs"],
                    c["rhs"],
                    c["tol"],
                    c["detail"],
                )
            )
    for stmt, ddate, qtrs, c in check_ties(data["on"], data["values"]):
        rows.append(
            (
                filing_id,
                stmt,
                ddate,
                qtrs,
                c["check_id"],
                c["ok"],
                c["lhs"],
                c["rhs"],
                c["tol"],
                c["detail"],
            )
        )
    counts = {
        "checks": len(rows),
        "failed": sum(1 for r in rows if not r[5]),
        "columns": len(data["columns"]),
    }
    if write:
        import json

        with conn.cursor() as cur:
            cur.execute(
                "delete from fsn.filing_check where filing_id = %s", (filing_id,)
            )
            cur.executemany(
                "insert into fsn.filing_check (filing_id, stmt, ddate, qtrs, check_id, ok, lhs, rhs, tol, detail) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)",
                [(*r[:9], json.dumps(r[9], default=str)) for r in rows],
            )
    return counts


def check_company(conn: psycopg.Connection, company_id: int) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            "select id from fsn.filing where company_id = %s order by accepted",
            (company_id,),
        )
        ids = [r[0] for r in cur.fetchall()]
    tot: dict[str, int] = defaultdict(int)
    for fid in ids:
        for k, v in check_filing(conn, fid).items():
            tot[k] += v
    tot["filings"] = len(ids)
    return dict(tot)
