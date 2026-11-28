"""Identity web over the shown export (2026-11-22, `identity_web@1`): a certification check, not a proof verdict.

Moved out of proof/identities.py on 2026-11-28 so the proof's verdict sources (tests/unit/test_detector_version_pin.py
VERDICT_SOURCES) stay exactly the code that decides a cell proof verdict. Nothing in proof/prove.py, proof/shown.py
or proof/runner.py calls this module; its callers are certification/display_cert.py, certification/draw_check.py
and scripts/certify_display.py. It reuses the operand tag sets of proof/identities.py.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from scrooner_pipeline.mapper.dqc_checks import tolerance
from scrooner_pipeline.proof.identities import (
    EQUITY_INCL_NCI_TAG,
    LSE_TAGS,
    NCI_INCOME_TAGS,
    NI_START_TAGS,
    TEMP_EQUITY_OTHER_TAGS,
    TEMP_EQUITY_PART_TAGS,
    TEMP_EQUITY_TAGS,
    TEMP_EQUITY_TOTAL_TAG,
)

# ================================================================ identity web over the shown export (2026-11-22)
# The same identities, judged over the SHOWN cells of a coverage export (top100-coverage.csv, or the resolver files
# read as cells) for every company x fiscal year, with the operands no export row carries (NCI, temporary equity,
# change in cash, FX, the CF start line, NCI income, income available to common, discrete quarters) read from the
# company's own filings in fsn.* (WEB_FACT_SQL, read-only). Each member cell carries its support: the automated
# draw checker's census outcome against the cited filing (AUTO_MATCH / AUTO_MISMATCH / NEEDS_READ) and the cell
# proof verdict. A BREAK names the members most likely wrong: AUTO_MISMATCH first, then members with neither a
# filing match nor a proof, then proof-only members; a member the filing's own fact matches is never the suspect.
# A break whose every member matches its filing fact is FILING_BREAK (the filing or the identity's operand set, not
# a shown value): reported, never opened. An EXACT identity that passes corroborates its one member the checker
# could not settle when every other member is AUTO_MATCH (draw_check.corroborate).

WEB_VERSION = "identity_web@1"
WEB_PASS, WEB_BREAK, WEB_FILING_BREAK = "PASS", "BREAK", "FILING_BREAK"
# identity names (the self-check reason and the report column)
ID_BS = "balance_sheet"
ID_CURRENT = "current_le_total"
ID_CF = "cash_flow"
ID_NI_CF = "net_income_cf"
ID_GP = "gross_profit"
ID_BAND = "operating_to_pretax_band"
ID_QUARTERS = "quarters_sum_to_year"
ID_EPS = "shares_x_eps"
WEB_IDENTITIES = (
    ID_BS,
    ID_CURRENT,
    ID_CF,
    ID_NI_CF,
    ID_GP,
    ID_BAND,
    ID_QUARTERS,
    ID_EPS,
)
# exact arithmetic of the filing (no slack beyond rounding): only these corroborate a cell
WEB_EXACT = frozenset({ID_BS, ID_CF, ID_NI_CF, ID_GP})

# support ranks: lower = more suspect
SUPPORT_RANK = {"AUTO_MISMATCH": 0, "none": 1, "proof": 2, "AUTO_MATCH": 9}

NCI_BS_TAGS = ("MinorityInterest", "NonredeemableNoncontrollingInterest")
CASH_CHANGE_INCL_FX = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
    "CashAndCashEquivalentsPeriodIncreaseDecrease",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperationsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
    "CashPeriodIncreaseDecrease",
)
CASH_CHANGE_EXCL_FX = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
    "CashAndCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
    "CashPeriodIncreaseDecreaseExcludingExchangeRateEffect",
)
FX_TAGS = (
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "EffectOfExchangeRateOnCashAndCashEquivalents",
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
    "EffectOfExchangeRateOnCash",
)
DISC_CF_TAGS = (
    "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
    "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
    "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
)
DISC_CF_TOTAL = "NetCashProvidedByUsedInDiscontinuedOperations"
# cash balances in the order the filing's own CF reconciles them (restricted cash per the filing: ASU 2016-18 total
# first, then cash and equivalents)
CASH_BALANCE_TAGS = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "CashAndCashEquivalentsAtCarryingValue",
    "Cash",
)
AVAIL_COMMON = {
    "basic": ("NetIncomeLossAvailableToCommonStockholdersBasic",),
    "diluted": (
        "NetIncomeLossAvailableToCommonStockholdersDiluted",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
    ),
}
QUARTER_DPS = (
    "revenue",
    "cost_of_revenue",
    "gross_profit",
    "operating_income",
    "income_before_tax",
    "net_income",
    "income_tax_expense",
)
QUARTER_SLACK = Decimal(
    "0.005"
)  # 10-Q quarters + a 10-K Q4: different vintages (recasts), 0.5% of the year
EPS_FALLBACK_SLACK = Decimal(
    "0.03"
)  # net income for income available to common: preferred / participating slack
WEB_TAGS: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *NCI_BS_TAGS,
            EQUITY_INCL_NCI_TAG,
            "StockholdersEquity",
            *TEMP_EQUITY_TAGS,
            *LSE_TAGS,
            *CASH_CHANGE_INCL_FX,
            *CASH_CHANGE_EXCL_FX,
            *FX_TAGS,
            *DISC_CF_TAGS,
            DISC_CF_TOTAL,
            *CASH_BALANCE_TAGS,
            *sorted(NI_START_TAGS),
            *NCI_INCOME_TAGS,
            *AVAIL_COMMON["diluted"],
        )
    )
)
WEB_FLOOR = "2013-01-01"
WEB_FORMS = ("10-K", "10-K/A", "10-KT", "10-Q", "10-Q/A", "20-F", "40-F")
# one read of the company's own filings: every undimensioned operand fact (and the shown flows' own tags, for the
# quarters), any duration; the CF statement's first lines
WEB_FACT_SQL = """
select f.accession, f.form, t.tag, v.ddate::text, v.qtrs, v.value, v.dcml, coalesce(v.uom, '')
from fsn.filing f
join fsn.value v on v.filing_id = f.id and coalesce(v.coreg, '') = '' and v.value is not null and v.qtrs in (0, 1, 3, 4)
join fsn.dim d on d.id = v.dim_id and d.segments = ''
join fsn.tag t on t.id = v.tag_id
where f.cik = lpad(ltrim(%(cik)s, '0'), 10, '0') and f.form = any(%(forms)s) and t.tag = any(%(tags)s)
  and v.ddate >= %(floor)s::date
"""
WEB_CF_LINE_SQL = """
select f.accession, t.tag, l.report, l.line
from fsn.filing f join fsn.line l on l.filing_id = f.id join fsn.tag t on t.id = l.tag_id
where f.cik = lpad(ltrim(%(cik)s, '0'), 10, '0') and f.form = any(%(forms)s) and l.stmt = 'CF' and l.line <= 8
"""


class WebFacts:
    """The operand facts of one company (WEB_FACT_SQL rows), indexed by (accession, tag, qtrs); the form of each
    accession; the first line of each filing's cash-flow statement."""

    def __init__(
        self,
        rows: Sequence[tuple[Any, ...]],
        cf_lines: Sequence[tuple[Any, ...]] = (),
    ):
        self.by: dict[tuple[str, str, int], list[tuple[date, Decimal, int]]] = (
            defaultdict(list)
        )
        self.form: dict[str, str] = {}
        self.own_end: dict[str, date] = {}
        for acc, form, tag, dd, q, val, dcml, uom in rows:
            toks = [
                t
                for t in str(uom or "").replace("/", " ").split()
                if len(t) == 3 and t.isupper()
            ]
            if any(t != "USD" for t in toks):
                continue  # a fact in another currency is never a USD operand
            d = date.fromisoformat(str(dd)[:10])
            self.by[(acc, tag, int(q))].append(
                (d, Decimal(str(val)), 32767 if dcml is None else int(dcml))
            )
            self.form[acc] = form
            if int(q) in (0, 1, 4) and d > self.own_end.get(acc, date.min):
                self.own_end[acc] = d
        # the net-income line the cash-flow statement starts from: the first NI_START_TAGS line of the filing's
        # main (lowest-numbered) CF report; a beginning cash balance printed above it (AAPL) is skipped
        main: dict[str, int] = {}
        for acc, _tag, rep, _line in cf_lines:
            main[acc] = min(main.get(acc, int(rep)), int(rep))
        first: dict[str, tuple[int, str]] = {}
        for acc, tag, rep, line in cf_lines:
            if int(rep) != main[acc] or str(tag) not in NI_START_TAGS:
                continue
            if acc not in first or int(line) < first[acc][0]:
                first[acc] = (int(line), str(tag))
        self.cf_first = {a: k[1] for a, k in first.items()}

    def get(self, acc: str, tag: str, end: date, qtrs: int) -> Decimal | None:
        cand = [
            (abs((d - end).days), -dc, v)
            for d, v, dc in self.by.get((acc, tag, qtrs), ())
            if abs((d - end).days) <= 7
        ]
        return min(cand)[2] if cand else None

    def first(
        self, acc: str, tags: Sequence[str], end: date, qtrs: int
    ) -> tuple[str, Decimal] | None:
        for t in tags:
            v = self.get(acc, t, end, qtrs)
            if v is not None:
                return t, v
        return None

    def quarters(
        self, tag: str, start: date, end: date
    ) -> dict[str, list[tuple[date, Decimal]]]:
        """Discrete-quarter facts (qtrs 1) of a tag ending inside (start, end], per accession."""
        out: dict[str, list[tuple[date, Decimal]]] = defaultdict(list)
        for (acc, t, q), vals in self.by.items():
            if t != tag or q != 1:
                continue
            for d, v, _dc in vals:
                if start < d <= end + timedelta(days=7):
                    out[acc].append((d, v))
        return out


@dataclass(frozen=True)
class WebMember:
    data_point: str
    value: Decimal
    support: str  # AUTO_MATCH | AUTO_MISMATCH | proof | none


@dataclass(frozen=True)
class WebResult:
    identity: str
    fiscal_year: str
    status: str  # PASS | BREAK | FILING_BREAK
    members: tuple[WebMember, ...]
    lhs: Decimal
    rhs: Decimal
    tolerance: Decimal
    suspects: tuple[str, ...]
    detail: str

    @property
    def exact(self) -> bool:
        return self.identity in WEB_EXACT and "slack" not in self.detail

    def opens(self, dp: str) -> bool:
        """Does the break open this suspect? Always for an exact identity; for a banded one (pretax band, shares x
        EPS, quarters) only when the suspect has no proof or its filing fact differs: a proven cell that breaks only a
        band (CAT interest partly above operating income, DELL two-class EPS) goes to a read, not open."""
        sup = next((m.support for m in self.members if m.data_point == dp), "none")
        return self.status == WEB_BREAK and (self.exact or sup != "proof")

    def reason(self, dp: str) -> str:
        mem = ", ".join(f"{m.data_point}={m.value} [{m.support}]" for m in self.members)
        return (
            f"identity {self.identity} breaks FY{self.fiscal_year}: {self.lhs} vs {self.rhs} "
            f"(diff {self.lhs - self.rhs}, tolerance {self.tolerance}); {dp} is the member no filing fact or proof "
            f"supports; members {mem}; {self.detail}"
        )


def support_of(auto: str | None, proof: str | None) -> str:
    """A member's support: the draw checker's census outcome decides when it settled the cell; else the proof."""
    if auto in ("AUTO_MATCH", "AUTO_MISMATCH"):
        return auto
    return "proof" if (proof or "").upper() == "PROVEN" else "none"


def _suspects(
    members: Sequence[WebMember], among: Sequence[str] | None = None
) -> tuple[str, ...]:
    pool = [m for m in members if among is None or m.data_point in among]
    pool = [m for m in pool if m.support != "AUTO_MATCH"] or (
        [m for m in members if m.support != "AUTO_MATCH"] if among is not None else []
    )
    if not pool:
        return ()
    best = min(SUPPORT_RANK[m.support] for m in pool)
    return tuple(m.data_point for m in pool if SUPPORT_RANK[m.support] == best)


def _result(
    identity: str,
    fy: str,
    members: Sequence[WebMember],
    lhs: Decimal,
    rhs: Decimal,
    tol: Decimal,
    ok: bool,
    detail: str,
    among: Sequence[str] | None = None,
) -> WebResult:
    if ok:
        return WebResult(
            identity, fy, WEB_PASS, tuple(members), lhs, rhs, tol, (), detail
        )
    sus = _suspects(members, among)
    return WebResult(
        identity,
        fy,
        WEB_BREAK if sus else WEB_FILING_BREAK,
        tuple(members),
        lhs,
        rhs,
        tol,
        sus,
        detail,
    )


def _close(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    return abs(a - b) <= tol


def web_period(
    fy: str,
    cells: dict[str, Any],
    support: dict[str, str],
    wf: WebFacts,
) -> list[WebResult]:
    """Every identity of one company fiscal year. cells: data point -> shown cell (attributes value, accession,
    period_end, tag, parts); support: data point -> support_of(...)."""
    out: list[WebResult] = []

    def mem(*dps: str) -> list[WebMember] | None:
        if not all(
            cells.get(d) is not None and cells[d].value is not None for d in dps
        ):
            return None
        return [WebMember(d, cells[d].value, support.get(d, "none")) for d in dps]

    def end_of(dp: str) -> date | None:
        c = cells.get(dp)
        pe = (c.period_end if c is not None else "") or ""
        return date.fromisoformat(pe[:10]) if pe else None

    def acc_of(*dps: str) -> str:
        return next(
            (
                cells[d].accession
                for d in dps
                if cells.get(d) is not None and cells[d].accession
            ),
            "",
        )

    # 1. assets = liabilities + equity + NCI + temporary equity (the operands from the liabilities' filing)
    m = mem("total_assets", "total_liabilities", "stockholders_equity")
    if m and (end := end_of("total_assets")):
        a, li, e = (x.value for x in m)
        acc = acc_of("total_liabilities", "total_assets")
        nci = wf.first(acc, NCI_BS_TAGS, end, 0)
        incl = wf.get(acc, EQUITY_INCL_NCI_TAG, end, 0)
        se = wf.get(acc, "StockholdersEquity", end, 0)
        nci_v = (
            nci[1]
            if nci
            else (incl - se if incl is not None and se is not None else None)
        )
        temp = wf.get(acc, TEMP_EQUITY_TOTAL_TAG, end, 0)
        if temp is None:
            parts = [
                v
                for t in TEMP_EQUITY_PART_TAGS
                if (v := wf.get(acc, t, end, 0)) is not None
            ]
            temp = sum(parts, Decimal(0)) if parts else None
        others = [
            v
            for t in TEMP_EQUITY_OTHER_TAGS
            if (v := wf.get(acc, t, end, 0)) is not None
        ]
        adds = [x for x in (nci_v, temp) if x is not None]
        opts = {Decimal(0)}
        for x in [*adds, *others]:
            opts |= {o + x for o in opts}
        if incl is not None:
            opts.add(
                incl - e
            )  # the shown equity is the parent's, the filing's total equity holds NCI
        r = a - li - e
        tol = tolerance([a, li, e, *adds, *others])
        ok = any(_close(r, o, tol) for o in opts)
        lse = wf.first(acc, LSE_TAGS, end, 0)
        among: list[str] | None = None
        if not ok and lse is not None:
            # the filing's own L&SE localises the break: assets off the face total, or the other side
            among = (
                ["total_assets"]
                if not _close(a, lse[1], tolerance([a, lse[1]]))
                else ["total_liabilities", "stockholders_equity"]
            )
        bs_best = min(opts, key=lambda o: abs(r - o))
        out.append(
            _result(
                ID_BS,
                fy,
                m,
                a,
                li + e + bs_best,
                tol,
                ok,
                f"filing {acc}: NCI {nci_v}, temporary equity {temp}, other mezzanine {others or '-'}"
                + (f", {lse[0]} {lse[1]}" if lse else ""),
                among,
            )
        )
    # 2. current assets <= total assets; current liabilities <= total liabilities
    for cur, tot in (
        ("current_assets", "total_assets"),
        ("current_liabilities", "total_liabilities"),
    ):
        m = mem(cur, tot)
        if m:
            c, t = m[0].value, m[1].value
            tol = tolerance([c, t])
            out.append(
                _result(ID_CURRENT, fy, m, c, t, tol, c <= t + tol, f"{cur} <= {tot}")
            )
    # 3. CFO + CFI + CFF (+ FX, + discontinued) = change in cash, the filing's own change line or balances
    m = mem("cfo", "cash_flow_investing", "cash_flow_financing")
    if m and (end := end_of("cfo")):
        s = sum((x.value for x in m), Decimal(0))
        acc = acc_of("cfo")
        fx = wf.first(acc, FX_TAGS, end, 4)
        disc = [v for t in DISC_CF_TAGS if (v := wf.get(acc, t, end, 4)) is not None]
        dtot = wf.get(acc, DISC_CF_TOTAL, end, 4)
        disc_opts = (
            {Decimal(0)}
            | ({sum(disc, Decimal(0))} if disc else set())
            | ({dtot} if dtot is not None else set())
        )
        chg_incl = wf.first(acc, CASH_CHANGE_INCL_FX, end, 4)
        chg_excl = wf.first(acc, CASH_CHANGE_EXCL_FX, end, 4)
        targets: list[tuple[str, Decimal, bool]] = []  # (source, change, includes FX)
        if chg_incl:
            targets.append((chg_incl[0], chg_incl[1], True))
        if chg_excl:
            targets.append((chg_excl[0], chg_excl[1], False))
        if not targets:
            prior = end - timedelta(days=365)
            for bt in CASH_BALANCE_TAGS:
                e1, e0 = wf.get(acc, bt, end, 0), wf.get(acc, bt, prior, 0)
                if e1 is not None and e0 is not None:
                    targets.append((f"{bt} {e1} - {e0}", e1 - e0, True))
                    break
        if targets:
            fx_v = fx[1] if fx else Decimal(0)
            extra = [fx_v, *disc] + ([dtot] if dtot is not None else [])
            tol = tolerance([*(x.value for x in m), *(t[1] for t in targets), *extra])
            cf_best: tuple[Decimal, Decimal, str] | None = None
            for src, chg, with_fx in targets:
                for dv in disc_opts:
                    for f in {fx_v, Decimal(0)} if with_fx else {Decimal(0)}:
                        lhs = s + f + dv
                        if cf_best is None or abs(lhs - chg) < abs(
                            cf_best[0] - cf_best[1]
                        ):
                            cf_best = (lhs, chg, f"{src}; FX {f}; discontinued {dv}")
            assert cf_best is not None
            lhs, chg, why = cf_best
            out.append(
                _result(
                    ID_CF,
                    fy,
                    m,
                    lhs,
                    chg,
                    tol,
                    _close(lhs, chg, tol),
                    f"filing {acc}: {why}",
                )
            )
    # 4. net income on the IS = the CF starting line (ProfitLoss less the printed NCI income)
    m = mem("net_income")
    if m and (ni_end := end_of("net_income")):
        acc = acc_of("net_income", "cfo")
        cf_tag = wf.cf_first.get(acc) or ""
        start_v = wf.get(acc, cf_tag, ni_end, 4) if cf_tag in NI_START_TAGS else None
        if cf_tag and start_v is not None:
            ni = m[0].value
            rhs: Decimal | None = start_v
            note = f"CF start {cf_tag} {start_v}"
            if cf_tag == "ProfitLoss":
                nci_inc = wf.first(acc, NCI_INCOME_TAGS, ni_end, 4)
                if nci_inc is not None:
                    rhs, note = (
                        start_v - nci_inc[1],
                        note + f" - {nci_inc[0]} {nci_inc[1]}",
                    )
                elif ni != start_v:
                    rhs = None  # NCI income not printed: parent vs total cannot be told apart
            if rhs is not None:
                tol = tolerance([ni, start_v])
                out.append(
                    _result(
                        ID_NI_CF,
                        fy,
                        m,
                        ni,
                        rhs,
                        tol,
                        _close(ni, rhs, tol),
                        f"filing {acc}: {note}",
                    )
                )
    # 5. gross profit = revenue - cost of revenue, all three shown
    m = mem("revenue", "cost_of_revenue", "gross_profit")
    if m:
        rv, cr, gp = (x.value for x in m)
        tol = tolerance([rv, cr, gp])
        out.append(
            _result(
                ID_GP,
                fy,
                m,
                rv - abs(cr),
                gp,
                tol,
                _close(rv - abs(cr), gp, tol),
                "revenue - cost of revenue",
            )
        )
    # 6. pretax - operating income = the band: other income (expense), net less the interest lines in the band
    m = mem("operating_income", "income_before_tax", "other_income_expense_net")
    if m:
        oi, pt, oie = (x.value for x in m)
        ie_m, ii_m = mem("interest_expense"), mem("interest_income")
        ie = abs(ie_m[0].value) if ie_m else None
        ii = ii_m[0].value if ii_m else None
        opts = {Decimal(0)}
        if ie is not None:
            opts.add(-ie)
        if ii is not None:
            opts |= {o + ii for o in list(opts)}
        r = pt - oi - oie
        tol = tolerance([oi, pt, oie] + [x for x in (ie, ii) if x is not None])
        band_best = min(opts, key=lambda o: abs(r - o))
        mm = m + (ie_m or []) + (ii_m or [])
        out.append(
            _result(
                ID_BAND,
                fy,
                mm,
                pt - oi,
                oie + band_best,
                tol,
                any(_close(r, o, tol) for o in opts),
                f"pretax - operating income = other income (expense), net {oie} + interest effect {band_best}",
            )
        )
    # 7. quarters sum to the year: the 10-K's own quarterly table (one vintage), else the 10-Qs' quarters + the
    # 10-K's Q4, at 0.5% slack
    for dp in QUARTER_DPS:
        m = mem(dp)
        qc = cells.get(dp)
        if not m or qc is None or qc.parts or not (qend := end_of(dp)):
            continue
        qtag = (qc.tag or "").split(":")[-1].strip()
        if not qtag:
            continue
        qacc = qc.accession
        qstart = qend - timedelta(days=371)
        qs = wf.quarters(qtag, qstart, qend)
        own = sorted({d: v for d, v in qs.get(qacc, [])}.items())
        q4 = next((v for d, v in own if abs((d - qend).days) <= 7), None)
        if q4 is None:
            continue
        fyv = m[0].value
        signs = (Decimal(1), Decimal(-1)) if is_fixed_positive_dp(dp) else (Decimal(1),)
        if len(own) == 4:
            vals = [v for _, v in own]
            total, slack, src = (
                sum(vals, Decimal(0)),
                Decimal(0),
                f"10-K {qacc} quarterly table",
            )
        else:
            picked: dict[date, Decimal] = {}
            for qa, lst in qs.items():
                if qa == qacc or wf.form.get(qa, "").split("/")[0] != "10-Q":
                    continue
                for d, v in lst:
                    if (
                        wf.own_end.get(qa) is not None
                        and abs((wf.own_end[qa] - d).days) <= 7
                    ):
                        picked.setdefault(
                            d, v
                        )  # the 10-Q whose own period is the quarter (original vintage)
            q13 = [v for d, v in sorted(picked.items()) if (qend - d).days > 45]
            if len(q13) != 3:
                continue
            vals = [*q13, q4]
            total, slack, src = (
                sum(vals, Decimal(0)),
                QUARTER_SLACK * abs(fyv),
                "10-Q quarters + 10-K Q4",
            )
        tol = tolerance([fyv, *vals]) + slack
        ok = any(_close(fyv, sg * total, tol) for sg in signs)
        out.append(
            _result(
                ID_QUARTERS,
                fy,
                m,
                fyv,
                total,
                tol,
                ok,
                f"{dp} {qtag}: {src} {' + '.join(str(v) for v in vals)}"
                + (" (slack 0.5%)" if slack else ""),
            )
        )
    # 8. weighted shares x EPS = income available to common (net income at 3% slack where the filing has none)
    for kind, eps_dp, sh_dp in (
        ("basic", "basic_eps", "weighted_basic_shares"),
        ("diluted", "diluted_eps", "weighted_diluted_shares"),
    ):
        m = mem(eps_dp, sh_dp)
        if not m or not (end := end_of(eps_dp)):
            continue
        eps, sh = m[0].value, m[1].value
        if sh <= 0:
            continue
        acc = acc_of(eps_dp)
        avail = wf.first(acc, AVAIL_COMMON[kind], end, 4)
        if avail is not None:
            num, slack, src = avail[1], Decimal(0), f"{avail[0]} {avail[1]} ({acc})"
        else:
            ni_m = mem("net_income")
            if not ni_m:
                continue
            m = m + ni_m
            num, slack, src = (
                ni_m[0].value,
                EPS_FALLBACK_SLACK * abs(ni_m[0].value),
                "net income (slack 3%)",
            )
        tol = Decimal("0.005") * sh + tolerance([num]) + slack
        out.append(
            _result(
                ID_EPS,
                fy,
                m,
                eps * sh,
                num,
                tol,
                _close(eps * sh, num, tol),
                f"{kind}: {eps_dp} x {sh_dp} vs {src}",
            )
        )
    return out


def is_fixed_positive_dp(dp: str) -> bool:
    from scrooner_pipeline.common.polarity import is_fixed_positive

    return is_fixed_positive(dp)


WEB_MEMBER_DPS = frozenset(
    {
        "total_assets", "total_liabilities", "stockholders_equity", "current_assets", "current_liabilities",
        "cfo", "cash_flow_investing", "cash_flow_financing", "net_income", "revenue", "cost_of_revenue",
        "gross_profit", "operating_income", "income_before_tax", "other_income_expense_net", "interest_expense",
        "interest_income", "income_tax_expense", "basic_eps", "diluted_eps", "weighted_basic_shares",
        "weighted_diluted_shares",
    }
)  # fmt: skip


def web_tags(cells: Iterable[Any]) -> list[str]:
    """WEB_TAGS plus the shown quarter-checked flows' own tags (one read per company)."""
    own = {
        (c.tag or "").split(":")[-1].strip()
        for c in cells
        if c.data_point in QUARTER_DPS and c.tag
    }
    return sorted(set(WEB_TAGS) | {t for t in own if t})


def identity_web(
    cells: Iterable[Any],
    wf: WebFacts,
    auto: dict[tuple[str, str], str] | None = None,
    proof: dict[tuple[str, str], str] | None = None,
) -> list[WebResult]:
    """Every identity over every fiscal year of one company's SHOWN cells. auto: (dp, fy) -> draw checker census
    outcome; proof: (dp, fy) -> proof verdict (the export's proof_verdict)."""
    auto, proof = auto or {}, proof or {}
    by_fy: dict[str, dict[str, Any]] = defaultdict(dict)
    for c in cells:
        if c.data_point in WEB_MEMBER_DPS and c.value is not None:
            by_fy[str(c.fiscal_year)][c.data_point] = c
    out: list[WebResult] = []
    for fy in sorted(by_fy):
        sup = {
            dp: support_of(auto.get((dp, fy)), proof.get((dp, fy))) for dp in by_fy[fy]
        }
        out += web_period(fy, by_fy[fy], sup, wf)
    return out


def web_corroborated(results: Iterable[WebResult]) -> dict[tuple[str, str], str]:
    """(dp, fy) -> evidence for cells an EXACT identity corroborates: the identity holds, the cell is its one member
    the draw checker did not settle, and every other member is AUTO_MATCH against the filing (the rest of the
    identity's operands are the filing's own facts)."""
    out: dict[tuple[str, str], str] = {}
    for r in results:
        if r.status != WEB_PASS or not r.exact:
            continue
        open_ = [m for m in r.members if m.support != "AUTO_MATCH"]
        if len(open_) != 1 or open_[0].support == "AUTO_MISMATCH":
            continue
        out.setdefault(
            (open_[0].data_point, r.fiscal_year),
            f"{WEB_VERSION} {r.identity} holds ({r.lhs} vs {r.rhs}, tolerance {r.tolerance}) with every other "
            f"member AUTO_MATCH; {r.detail}",
        )
    return out
