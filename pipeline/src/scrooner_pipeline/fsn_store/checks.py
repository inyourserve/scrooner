"""Automatic proof of a stored filing (design §5): per statement column, do the filer's own
calculation arcs and the accounting identities hold? Results go to fsn.filing_check; a
served value may only come from a column whose checks all pass (fsn_select).

Column = (stmt, ddate, qtrs) of a filing. Tolerance = Σ 0.5·10^(-dcml) over the terms
(a child with dcml -6 contributes 500,000), with `common.rounding_unit`-style fallback of
one unit of the coarsest decimals when dcml is missing.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Iterable

import psycopg
from scrooner_pipeline.fsn_store.stmt_effective import effective_stmt_sql

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
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
)
IS_GP = ("is_gross_profit", "GrossProfit", "Revenues", "CostOfRevenue")
# fallback operand families when the filer's calc tree has no arcs under the change-in-cash line: the FX
# effect and the change line come in several element names (ASU 2016-18 restricted-cash totals, the
# disposal-group variants MSFT uses since FY2023), so they are matched by family, not by a fixed list
CF_CHANGE_RE = re.compile(r"(?i)^(Cash\w*PeriodIncreaseDecrease\w*)$")
CF_FX_RE = re.compile(r"(?i)^EffectOfExchangeRateOn\w+$")
CF_CONT = (
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
    "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
)
CF_DISC_RE = re.compile(r"^(Net)?CashProvidedByUsedIn\w*DiscontinuedOperations\w*$")


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


# a filer who prints in whole millions rounds each operand to 10^6 whatever its decimals attribute says
# (MCD: decimals -5 on figures that are whole millions), so the rounding unit of a Print is the coarser
# of its declared decimals and 10^6 when the value is a whole number of millions (nothing narrower or
# wider is inferred from zeros: a round 1,000 at decimals 0 is still exact)
TRAILING_UNIT_CAP = 6


def _unit_exp(item: Print | int | None) -> int | None:
    """Exponent of the rounding unit (10^e), or None when the print is exact."""
    if isinstance(item, Print):
        d, v = item.dcml, item.value
    else:
        d, v = item, None
    d = 0 if d is None else d
    if abs(d) > DCML_EXACT:
        return None  # an exact print adds no rounding slack
    e = -d
    if v is not None and v != 0:
        n = int(v)
        if n == v:
            z = 0
            while n % 10 == 0 and z < TRAILING_UNIT_CAP:
                n //= 10
                z += 1
            if z >= TRAILING_UNIT_CAP:  # whole millions: the filer rounded to 10^6
                e = max(e, z)
    return e


def tol_of(items: Iterable[Print | int | None]) -> Decimal:
    """0.5 x unit per operand; items are Prints (declared decimals and trailing zeros) or bare dcml."""
    t = Decimal(0)
    for it in items:
        e = _unit_exp(it)
        if e is not None:
            t += Decimal(5) * (Decimal(10) ** (e - 1))
    return t


def index_values(
    values: list[tuple], stmt_of: dict, line_of: dict
) -> tuple[dict, dict]:
    """Prints per column. A tag may carry several copies of one column (iprx 0, 1, 2 ...: the face copy, then
    copies that include an adjustment member, ADI RetainedEarnings FY2018: 5,982,697,000 on the face, 6,313,723,000
    at iprx 3): the check reads the FACE copy, the lowest iprx, never the last. Rows come ordered by iprx; the first
    copy of a key wins."""
    flat: dict[tuple[str, date, int], Print] = {}
    by_col: dict[tuple[str, date, int], dict[tuple[str, str], Print]] = defaultdict(
        dict
    )
    for tag, version, ddate, qtrs, value, dcml, iprx in sorted(
        values, key=lambda r: r[6] or 0
    ):
        flat.setdefault(
            (tag, ddate, qtrs), Print(tag, version, Decimal(value), dcml, None)
        )
        stmt = stmt_of.get((tag, version))
        if stmt is None:
            continue
        by_col[(stmt, ddate, qtrs)].setdefault(
            (tag, version),
            Print(tag, version, Decimal(value), dcml, line_of.get((tag, version))),
        )
    return flat, by_col


def index_alts(values: list[tuple], stmt_of: dict) -> dict:
    """Every distinct printed value of a key per column, face copy (lowest iprx) first. A filing can carry a second,
    unrelated copy of one undimensioned fact (DIS 10-Q 0001744489-19-000100, Sep. 29 2018: accounts payable 10,518 at
    iprx 0 from another table, 9,479 at iprx 1 and 2 on the face); the calc check tries the other copies before failing."""
    alts: dict[tuple[str, date, int], dict[tuple[str, str], list[Decimal]]] = (
        defaultdict(dict)
    )
    for tag, version, ddate, qtrs, value, _dcml, _iprx in sorted(
        values, key=lambda r: r[6] or 0
    ):
        stmt = stmt_of.get((tag, version))
        if stmt is None:
            continue
        lst = alts[(stmt, ddate, qtrs)].setdefault((tag, version), [])
        if Decimal(value) not in lst:
            lst.append(Decimal(value))
    return alts


def index_members(rows: list[tuple], stmt_of: dict) -> dict:
    """{(stmt, ddate, qtrs): {dim_id: {(tag, version): value}}} from (tag, version, ddate, qtrs, dim_id, value) rows ordered
    by iprx; the first copy of a key wins."""
    out: dict = defaultdict(lambda: defaultdict(dict))
    for tag, version, ddate, qtrs, dim_id, value in rows:
        stmt = stmt_of.get((tag, version))
        if stmt is not None:
            out[(stmt, ddate, qtrs)][dim_id].setdefault((tag, version), Decimal(value))
    return out


def load_filing(conn: psycopg.Connection, filing_id: int) -> dict[str, Any]:
    """Statement lines, non-dimensional values per (stmt, ddate, qtrs) column, and calc arcs of one filing."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select es, line, tag, version, inpth from (
                select %s as es, l.report, l.line, t.tag, t.version, l.inpth
                from fsn.line l join fsn.tag t on t.id = l.tag_id
                where l.filing_id = %%s
            ) x where es in ('BS', 'IS', 'CF')
            order by es, report, line
            """
            % effective_stmt_sql("l"),
            (filing_id,),
        )
        lines = cur.fetchall()
        cur.execute(
            """
            select t.tag, t.version, v.ddate, v.qtrs, v.value, v.dcml, v.iprx
            from fsn.value v join fsn.tag t on t.id = v.tag_id
            where v.filing_id = %s and v.dim_id = 0 and v.value is not null and v.uom = 'USD'
            order by v.iprx
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
        # member rows of calc children (BLK prints a consolidated-VIE block whose rows carry a VIE member; the face totals
        # include them): one value per (tag, column, member), face copy first, the filer's own context only
        cur.execute(
            """
            select t.tag, t.version, v.ddate, v.qtrs, v.dim_id, v.value
            from fsn.value v join fsn.tag t on t.id = v.tag_id
            where v.filing_id = %s and v.dim_id <> 0 and v.value is not null and v.uom = 'USD' and v.coreg = ''
              and v.tag_id in (select child_tag_id from fsn.calc_arc where filing_id = %s)
            order by v.iprx
            """,
            (filing_id, filing_id),
        )
        member_values = cur.fetchall()
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
    flat, by_col = index_values(values, stmt_of, line_of)
    groups: dict[tuple[str, str, int], list[tuple[str, str, int]]] = defaultdict(list)
    for grp, _arc, ptag, pver, ctag, cver, w in arcs:
        groups[(ptag, pver, grp)].append((ctag, cver, w))
    return {
        "stmt_of": stmt_of,
        "columns": by_col,
        "alts": index_alts(values, stmt_of),
        "members": index_members(member_values, stmt_of),
        "groups": groups,
        "on": on,
        "values": flat,
    }


ALT_COMBOS = (
    64  # bound on the alternative-copy combinations tried for one failing calc group
)


def _resolve_calc_failure(
    parent: Print,
    terms: list[tuple[Print, int]],
    keys: list[tuple[str, str]],
    pkey: tuple[str, str],
    alts: dict,
    tol: Decimal,
    members: dict | None = None,
) -> str | None:
    """Why a failing calc group is not a value failure, or None. Two filing-structure causes (successor-check review 2026-11-14):
    alt_copy: another printed copy of the parent or a child (index_alts) makes the group foot;
    filer_double_count: the group foots without one child that another child of the group repeats (DIS CF FY2019 Q2: the
    discontinued-operations line and its subtotal, -35 each; LIN FY2019: PropertyPlantAndEquipmentNet beside the PP&E-plus-ROU tag)."""
    import itertools

    choices = [alts.get(pkey) or [parent.value]] + [
        alts.get(k) or [t.value] for k, (t, _w) in zip(keys, terms)
    ]
    if any(len(c) > 1 for c in choices):
        n = 0
        for combo in itertools.product(*choices):
            n += 1
            if n > ALT_COMBOS:
                break
            if (
                abs(
                    combo[0]
                    - sum((v * w for v, (_t, w) in zip(combo[1:], terms)), Decimal(0))
                )
                <= tol
            ):
                return "alt_copy"
    rhs = sum((t.value * w for t, w in terms), Decimal(0))
    # face_member_rows: the printed total also holds the group's own children under one member (BLK consolidated VIEs:
    # Dec. 31 2013 Liabilities 193,203 = undimensioned children 190,760 + VIE debt 2,369 + VIE other liabilities 74)
    for rows in (members or {}).values():
        extra = sum(
            (rows[k] * w for k, (_t, w) in zip(keys, terms) if k in rows), Decimal(0)
        )
        if extra != 0 and abs(parent.value - rhs - extra) <= tol:
            return "face_member_rows"
    for i, (t, w) in enumerate(terms):
        if abs(parent.value - (rhs - t.value * w)) > tol or t.value == 0:
            continue
        stem = re.sub(r"Net$", "", t.tag)
        for j, (u, wu) in enumerate(terms):
            if j != i and (
                u.value * wu == t.value * w
                or (
                    u.tag != t.tag
                    and u.tag.startswith(stem)
                    and abs(u.value) >= abs(t.value)
                )
            ):
                return "filer_double_count"
    return None


def check_column(
    stmt: str,
    col: dict[tuple[str, str], Print],
    groups: dict,
    stmt_of: dict,
    alts: dict | None = None,
    members: dict | None = None,
) -> list[dict[str, Any]]:
    """Checks of one column: every calc parent with all children printed in this column, plus the identities.
    alts: index_alts() of this column (optional). A calc group that fails is not a failure when another group of the same
    parent foots in this column (the filing's other calc trees: DIS/BLK, 81 of 99 'partial_group' failures, review 2026-11-14),
    when another printed copy makes it foot, when the face total also holds member rows of the group's children, or when the
    filer's calc counts one line twice (_resolve_calc_failure). members: index_members() of this column (optional)."""
    out: list[dict[str, Any]] = []
    alts = alts or {}
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
        tol = tol_of([parent, *(t for t, _ in terms)])
        ok = abs(parent.value - rhs) <= tol
        detail: dict[str, Any] = {
            "parent": ptag,
            "children": [[c, w] for c, _v, w in children],
        }
        if not ok:
            why = _resolve_calc_failure(
                parent,
                terms,
                [(c, v) for c, v, _w in children],
                (ptag, pver),
                alts,
                tol,
                members,
            )
            if why:
                ok, detail["resolved_by"] = True, why
        out.append(
            {
                "check_id": f"calc:{ptag}:{grp}",
                "ok": ok,
                "lhs": parent.value,
                "rhs": rhs,
                "tol": tol,
                "detail": detail,
            }
        )
    footed = {
        r["detail"]["parent"]: r["check_id"]
        for r in out
        if r["ok"] and "resolved_by" not in r["detail"]
    }
    for r in out:
        if not r["ok"] and r["detail"]["parent"] in footed:
            r["ok"], r["detail"]["resolved_by"] = (
                True,
                f"parent_foots_in_{footed[r['detail']['parent']]}",
            )
    if stmt == "BS":
        for check_id, lhs_tags, rhs_tags in BS_IDENTITIES:
            lhs = [p for (t, _v), p in col.items() if t in lhs_tags]
            rhs = [p for (t, _v), p in col.items() if t in rhs_tags]
            if lhs and rhs:
                l, r = lhs[0], rhs[0]
                tol = tol_of([l, r])
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
        rec = cf_change_check(col, groups)
        if rec is not None:
            out.append(rec)
    if stmt == "IS":
        gp = {t: p for (t, _v), p in col.items() if t in IS_GP[1:]}
        if len(gp) == 3:
            rhs = gp["Revenues"].value - gp["CostOfRevenue"].value
            tol = tol_of(list(gp.values()))
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


def cf_change_check(
    col: dict[tuple[str, str], Print], groups: dict
) -> dict[str, Any] | None:
    """cf_parts_eq_change: the change in cash equals its parts.

    1. The filer's own calc tree: when the change line is a calc parent whose children are all printed
       in this column, the identity is that arithmetic (FX, discontinued flows, restricted cash all come
       in because the filer put them in the tree). When the tree does not tie but the printed numbers do
       by step 2 (a defect in the linkbase, e.g. CFO weighted -1), the column passes and the detail
       records calc_tree_failed.
    2. No arcs: CFO + CFI + CFF (totals, else continuing + discontinued) + the FX effect against the
       printed change line (the ASU 2016-18 cash-plus-restricted-cash total when printed). Whether the
       change line includes FX is the filer's layout (HD prints the change before FX): the column ties if
       it ties either way; an "Excluding" change line never includes FX.
    """
    changes = [p for (t, _v), p in col.items() if CF_CHANGE_RE.match(t)]
    if not changes:
        return None
    # prefer the cash-plus-restricted-cash total including FX, then any other printed change line
    changes.sort(
        key=lambda p: ("RestrictedCash" not in p.tag, "Excluding" in p.tag, len(p.tag))
    )
    tree = _cf_tree(col, groups, changes)
    if tree is not None and tree["ok"]:
        return tree
    fb = _cf_fallback(col, changes)
    if tree is None:
        return fb
    if fb is not None and fb["ok"]:
        # the printed numbers tie; the filer's calc linkbase does not (a weight or rounding defect in the
        # tree, e.g. CFO weighted -1): the column passes, the tree defect is recorded
        fb["detail"]["calc_tree_failed"] = {
            "diff": str(tree["lhs"] - tree["rhs"]),
            "children": tree["detail"]["children"],
        }
        return fb
    return tree


def _cf_tree(
    col: dict[tuple[str, str], Print], groups: dict, changes: list[Print]
) -> dict[str, Any] | None:
    for change in changes:
        for (ptag, _pver, _grp), children in groups.items():
            if ptag != change.tag or len(children) < 2:
                continue
            maybe = [(col.get((c, v)), w) for c, v, w in children]
            terms = [(t, w) for t, w in maybe if t is not None]
            if len(terms) != len(maybe):
                continue
            rhs = sum((t.value * w for t, w in terms), Decimal(0))
            tol = tol_of([change, *(t for t, _ in terms)])
            return {
                "check_id": "cf_parts_eq_change",
                "ok": abs(change.value - rhs) <= tol,
                "lhs": change.value,
                "rhs": rhs,
                "tol": tol,
                "detail": {
                    "change_tag": change.tag,
                    "form": "calc_tree",
                    "children": [[c, str(w)] for c, _v, w in children],
                },
            }
    return None


def _cf_fallback(
    col: dict[tuple[str, str], Print], changes: list[Print]
) -> dict[str, Any] | None:
    tags = {t: p for (t, _v), p in col.items()}
    parts = [tags[t] for t in CF_PARTS if t in tags]
    form_parts = "totals"
    if len(parts) < 3:
        cont = [tags[t] for t in CF_CONT if t in tags]
        if len(cont) + len(parts) < 3:
            return None
        parts = parts + cont
        form_parts = "continuing"
    disc = (
        [p for t, p in tags.items() if CF_DISC_RE.match(t)]
        if form_parts == "continuing"
        else []
    )
    fx = [p for t, p in tags.items() if CF_FX_RE.match(t)]
    base = sum((p.value for p in parts + disc), Decimal(0))
    # several change or FX elements can sit in one column: try every (change, FX) pairing in priority
    # order; the column passes if any ties and the detail records which did (6b0b4355)
    cands: list[tuple[Print, Print | None, Decimal, Decimal]] = []
    for c in changes:
        tol_no = tol_of([c, *parts, *disc])
        if "Excluding" not in c.tag:
            for fxp in fx:
                cands.append((c, fxp, base + fxp.value, tol_no + tol_of([fxp])))
        cands.append((c, None, base, tol_no))
    c, fx_used, rhs, tol = next(
        (x for x in cands if abs(x[0].value - x[2]) <= x[3]), cands[0]
    )
    return {
        "check_id": "cf_parts_eq_change",
        "ok": abs(c.value - rhs) <= tol,
        "lhs": c.value,
        "rhs": rhs,
        "tol": tol,
        "detail": {
            "change_tag": c.tag,
            "form": f"fallback_{form_parts}",
            "fx_included": fx_used is not None,
            "fx_tag": fx_used.tag if fx_used is not None else None,
            "discontinued": [p.tag for p in disc],
        },
    }


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
    tol = tol_of([lhs, *rhs_terms])
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
        key = (stmt, ddate, qtrs)
        for c in check_column(
            stmt,
            col,
            data["groups"],
            data["stmt_of"],
            data.get("alts", {}).get(key),
            data.get("members", {}).get(key),
        ):
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
