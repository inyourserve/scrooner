"""I1 balance identity and I2 statement ties.

Reuses sanity/accounting_identity.IDENTITIES and evaluate() (the declarative
identities, the NCI / temporary-equity adjustment powerset and the 2026-10-02
fix are not re-implemented). Differences from that observer:

  * it runs on the display layer of ONE chunk of companies and emits findings
    with a severity instead of a per-company pass-rate;
  * a failure beyond WRONG_GAP is `wrong_value` (blocks certification), a
    smaller failure is `review`;
  * I2 adds the cash roll-forward (cash change = CFO + CFI + CFF + FX).

Not implemented (no canonical concept exists for the inputs): net income on the
cash-flow statement vs the income statement, retained-earnings roll-forward.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from scrooner_pipeline.sanity.accounting_identity import IDENTITIES, Identity, evaluate

from .thresholds import (
    ROUNDING_TOLERANCE,
    LIABILITIES_NCI_TOLERANCE,
    WRONG_GAP,
    SCALE_RATIO,
    CASH_ROLL_TOLERANCE,
    FY_MIN_DAYS,
    FY_MAX_DAYS,
    CASH_DATE_SLACK_DAYS,
)
from .model import (
    NCI_CLAIM_TAGS,
    INFO,
    REVIEW,
    WRONG_VALUE,
    CompanyData,
    Finding,
    finding,
    power_of_ten_signature,
)


def _close(a: Decimal, b: Decimal) -> bool:
    return a == b or (
        max(abs(a), abs(b)) != 0
        and abs(a - b) / max(abs(a), abs(b)) <= ROUNDING_TOLERANCE
    )


# Relative gap (to the identity's basis) beyond which a failed tie is no longer
# plausible rounding / perimeter noise: a 25% gap on assets = L + E is a wrong
# component, not a missing NCI line.

# The net income identity cannot see every reconciling item (discontinued
# operations, equity-method income, NCI: JNJ's 2023 Kenvue exchange gain puts
# net income 3x above pretax - tax and the tie is legitimately open). Its failure
# is `wrong_value` only when stored and expected differ by a SCALE (>= 50x either
# way, or a power-of-ten signature); a smaller gap is `review`.
SCALE_ONLY_IDENTITIES = frozenset({"net_income", "gross_profit"})

I1_IDENTITIES = ("balance_sheet", "current_assets_within_total", "cash_within_total")
I2_IDENTITIES = ("gross_profit", "net_income")

# Cash roll-forward: restricted cash, FX and ASU 2016-18 make small gaps normal.


def _scale_apart(actual: Decimal, expected: Decimal | None) -> bool:
    if expected is None or expected == 0 or actual == 0:
        return False
    ratio = abs(actual / expected)
    big = ratio if ratio >= 1 else 1 / ratio
    return big >= SCALE_RATIO or power_of_ten_signature(big)


def _by_period(data: CompanyData) -> dict[str, dict[int, object]]:
    out: dict[str, dict[int, object]] = {}
    for base, cells in data.display_by_concept().items():
        out[base] = {c.period_id: c for c in cells}
    return out


def _identity(name: str) -> Identity:
    return next(i for i in IDENTITIES if i.name == name)


def _check_identity(
    data: CompanyData, by_period, identity: Identity, invariant: str
) -> list[Finding]:
    findings: list[Finding] = []
    names = identity.concepts
    if any(n not in by_period for n in names):
        return findings
    adj_by_period: dict[tuple[int, str], Decimal] = {}
    for a in data.adjustment_facts:
        adj_by_period[(a.period_id, a.tag)] = a.value
    common = set.intersection(*(set(by_period[n]) for n in names))
    for period_id in sorted(common):
        cells = {n: by_period[n][period_id] for n in names}
        target = cells[identity.target]
        term_sources = {
            s for c in (cells[n] for n, _ in identity.terms) for s in c.source_ids
        }
        if set(target.source_ids) & term_sources:
            continue  # tautology guard: target was derived from its own terms
        values = {n: c.value for n, c in cells.items()}
        adjustments = {
            tag: adj_by_period[(period_id, tag)]
            for tag, _sign in identity.adjustments
            if (period_id, tag) in adj_by_period
        }
        result = evaluate(identity, values, adjustments)
        if result.passed:
            continue
        if identity.name in SCALE_ONLY_IDENTITIES:
            # data-team/strategy/team/CERTIFY-HELDOUT-VALIDATION: the net income and
            # gross profit identities were 0/4 right on held-out cells (NCI at MPC and
            # SPGI, excise taxes in MO's revenue, a REIT layout at DOC): they cannot see
            # the reconciling items, so a gap that is not a unit-scale error is `info`
            # (counted, never stored, never blocking).
            severity = (
                WRONG_VALUE if _scale_apart(result.actual, result.expected) else INFO
            )
        else:
            severity = WRONG_VALUE if (result.rel_gap or 0) > WRONG_GAP else REVIEW
        findings.append(
            finding(
                data,
                invariant,
                severity,
                f"identity:{identity.name}",
                target,
                other=result.expected,
                identity=identity.name,
                description=identity.description,
                rel_gap=str(result.rel_gap),
                used_adjustments=result.used_adjustments,
                terms={n: str(values[n]) for n, _ in identity.terms},
                source_ids=sorted(set(target.source_ids) | term_sources),
            )
        )
    return findings


NCI_TAGS = NCI_CLAIM_TAGS


def _liabilities_nci(data: CompanyData) -> list[Finding]:
    """A calculated total liabilities must equal assets - equity - every claim that is
    neither liability nor parent equity (noncontrolling interest, REDEEMABLE
    noncontrolling interest, temporary equity). VLO 2020-12-31 stored 33,814M against
    32,132M on the balance sheet. The claims are read from the cell's own sources AND
    from the authoritative facts of the same period (ILMN: the redeemable NCI is not
    among the cell's sources, so the first version expected 1,845M where the face says
    1,811M). Two findings, both `wrong_value`:
      liabilities_nci_added      stored = assets - equity + NCI (the NCI added instead of
                                 subtracted, SWK 2021: 3.0M on 12,471M), at ANY size
      liabilities_nci_treatment  stored differs from the right value by more than 0.5%
    A filed total liabilities is checked by the balance identity instead."""
    out: list[Finding] = []
    adj: dict[int, dict[str, Decimal]] = {}
    for f in data.adjustment_facts:
        if f.tag in NCI_TAGS:
            adj.setdefault(f.period_id, {})[f.tag] = f.value
    for cell in data.display_cells():
        if cell.base != "total_liabilities":
            continue
        srcs = data.source_facts(cell)
        a = next((s for s in srcs if s.tag == "Assets"), None)
        e = next((s for s in srcs if s.tag == "StockholdersEquity"), None)
        if a is None or e is None:
            continue
        claims: dict[str, Decimal] = {
            s.tag: s.value for s in srcs if s.tag in NCI_TAGS and s.value
        }
        for tag, value in adj.get(cell.period_id, {}).items():
            if value:
                claims.setdefault(tag, value)
        if not claims:
            continue
        n = sum(claims.values(), Decimal(0))
        expected = a.value - e.value - n
        if expected <= 0:
            continue
        evidence: dict[str, Any] = dict(
            assets=str(a.value),
            parent_equity=str(e.value),
            noncontrolling_interest=str(n),
            claims={t: str(v) for t, v in claims.items()},
            note="total liabilities = assets - equity - noncontrolling interests; they are equity",
        )
        if _close(cell.value, a.value - e.value + n) and not _close(
            cell.value, expected
        ):
            out.append(
                finding(
                    data,
                    "I1",
                    WRONG_VALUE,
                    "liabilities_nci_added",
                    cell,
                    other=expected,
                    source_ids=sorted(s.id for s in srcs),
                    **evidence,
                )
            )
        elif abs(cell.value - expected) / expected > LIABILITIES_NCI_TOLERANCE:
            out.append(
                finding(
                    data,
                    "I1",
                    WRONG_VALUE,
                    "liabilities_nci_treatment",
                    cell,
                    other=expected,
                    source_ids=sorted(s.id for s in srcs),
                    **evidence,
                )
            )
    return out


def _cash_roll(data: CompanyData, by_period) -> list[Finding]:
    findings: list[Finding] = []
    cash = sorted(
        by_period.get("cash_and_equivalents", {}).values(), key=lambda c: c.end
    )
    if not cash:
        return findings
    for cfo in by_period.get("cfo", {}).values():
        d = cfo.days
        if d is None or not (FY_MIN_DAYS <= d <= FY_MAX_DAYS) or cfo.start is None:
            continue
        inv = by_period.get("cash_flow_investing", {}).get(cfo.period_id)
        fin = by_period.get("cash_flow_financing", {}).get(cfo.period_id)
        if inv is None or fin is None:
            continue
        end_cash = next(
            (c for c in cash if abs((c.end - cfo.end).days) <= CASH_DATE_SLACK_DAYS),
            None,
        )
        prior_cash = next(
            (
                c
                for c in cash
                if abs((c.end - cfo.start).days - 1) <= CASH_DATE_SLACK_DAYS
            ),
            None,
        )
        if end_cash is None or prior_cash is None:
            continue
        delta = end_cash.value - prior_cash.value
        total = cfo.value + inv.value + fin.value
        basis = max(abs(end_cash.value), abs(total), abs(delta), Decimal(1))
        gap = abs(delta - total) / basis
        if gap <= CASH_ROLL_TOLERANCE:
            continue
        # FX effect, restricted cash and ASU 2016-18 are not in the inputs, so
        # this is never wrong_value on its own: a person or the Verifier decides.
        findings.append(
            finding(
                data,
                "I2",
                REVIEW,
                "cash_roll_forward",
                end_cash,
                other=prior_cash.value + total,
                rel_gap=str(gap),
                cash_change=str(delta),
                cfo=str(cfo.value),
                cfi=str(inv.value),
                cff=str(fin.value),
                note="FX effect and restricted cash are not in the inputs",
                source_ids=sorted(set(end_cash.source_ids) | set(cfo.source_ids)),
            )
        )
    return findings


def check(data: CompanyData) -> list[Finding]:
    by_period = _by_period(data)
    findings: list[Finding] = []
    findings += _liabilities_nci(data)
    for name in I1_IDENTITIES:
        findings += _check_identity(data, by_period, _identity(name), "I1")
    for name in I2_IDENTITIES:
        findings += _check_identity(data, by_period, _identity(name), "I2")
    findings += _cash_roll(data, by_period)
    return findings
