"""Error-injection harness: how much of each known error class do the certification checks catch?

Plants known errors, one class at a time, into a copy of the top-100 display export (data-team/strategy/
top100-coverage.csv is read, never written) and runs every existing check on the mutated copy and on the untouched
copy: the flow self-check / certify_display mechanical census (gate, badges, hide classes, hidden rows and years,
derived and total_debt census), the drawn-cell fact match (display_cert.check_cell / check_derived), the automated draw
checker (draw_check) and the tag expert's pattern detectors (data-team/tags/library/pattern_detectors.py: P02, P03,
P05/P06, P08). Recall per class is the share of planted cells a check flags in the mutated copy that it did not flag
the same way in the untouched copy. False positives are measured on untouched control cells: a new flag after the
injection (spillover) and the flag rate of the untouched export itself (an upper bound: it also holds real errors).

Error classes (each seen in a real failure):

- scale_x1000 / scale_x1e6: the value (and its parts) at the wrong scale (COP/RTX/SYK shares, STX FY2022 DPS 2,770,000).
- sign_flip: the value with the wrong sign (parts' signs flipped with it, so the parts still add up).
- period_shift: the prior year's value under this year's citation (a comparative column read as the current one).
- dropped_component: one non-zero part removed from a summed cell, the value re-summed (parts still add up).
- subline_as_total: a dimensioned sub-line of the cited filing served as the total (PFE product revenue vs total).
- combined_as_narrow: a wider printed receivable/payable line (balance or cash-flow change) served as the narrow item
  (BMY accounts receivable).
- rounded_duplicate: the value rounded as a coarser duplicate fact would be (WMT FY2023 372M served as 400M).
- restricted_cash_total: cash including restricted cash served as cash and equivalents.
- available_to_common_ni: net income available to common stockholders served as net income.
- wrong_hide: a shown year hidden with an evidenced hide class although its 10-K prints the line (WMT FY2015).
- missing_badge: a shown cell whose registry badge is blank (MA and WMT certifications 2026-11-22).
- derived_two_filings: a derived (derived: badge) summed cell whose parts cite two filings (doc 02: one filing).

The fact-swap classes (subline, combined, restricted cash, available to common) take the planted value from the
cited filing's own facts (fsn.*), so they are real figures a wrong mapping could serve, cited consistently.

Pure functions plus a recording fact source: a live run (read-only SELECTs) records every query result into one
evidence bundle per company, and BundleSource replays it offline (the CI test). Money is Decimal end to end.
"""

from __future__ import annotations

import csv
import gzip
import importlib.util
import json
import random
import re
import tempfile
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import draw_check as dck

HARNESS_VERSION = "inject@1"
CLASSES = (
    "scale_x1000",
    "scale_x1e6",
    "sign_flip",
    "period_shift",
    "dropped_component",
    "subline_as_total",
    "combined_as_narrow",
    "rounded_duplicate",
    "restricted_cash_total",
    "available_to_common_ni",
    "wrong_hide",
    "missing_badge",
    "derived_two_filings",
)
# checks that see every cell of an export (census) vs checks that see a cell only when certify draws it
CENSUS_CHECKS = ("self_check", "patterns")
DRAW_CHECKS = ("cell_match", "draw_check")
CHECKS = CENSUS_CHECKS + DRAW_CHECKS
SHOWN, HIDDEN_YEAR, HIDDEN_ROW = dc.SHOWN, dc.HIDDEN_YEAR, dc.HIDDEN_ROW
ROOT = Path(__file__).resolve().parents[4]
PATTERN_DETECTORS = ROOT / "data-team" / "tags" / "library" / "pattern_detectors.py"

Key = tuple[str, str, str]  # (ticker, data_point, fiscal_year)


# ---------------------------------------------------------------- export rows
def read_rows(path: Path) -> tuple[list[str], list[dict]]:
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r.fieldnames or []), list(r)


def write_rows(path: Path, fields: list[str], rows: list[dict]) -> None:
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "wt", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def key(r: dict) -> Key:
    return (r["ticker"], r["data_point"], str(r["fiscal_year"]))


def by_company(rows: Iterable[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        out[r["ticker"]].append(r)
    return dict(out)


def add_badges(fields: list[str], rows: list[dict]) -> list[str]:
    """An export written before the badge column (CSV_COLUMNS 'badge', 'sector'): give every shown cell the registry
    badge its own evidence names (top100_coverage.proof_step -> registry.badge_for), '' when it names none, so the
    badge checks have a column to judge. An export that has the column is left as it is. Returns the field list."""
    if "badge" in fields:
        return fields
    from scrooner_pipeline.mapper.top100_coverage import proof_step
    from scrooner_pipeline.metrics import registry as reg

    for r in rows:
        r["badge"], r["sector"] = "", r.get("sector") or "general"
        if r.get("display") != SHOWN:
            continue
        step = proof_step(r)
        if step:
            try:
                r["badge"] = reg.badge_for(
                    r["data_point"], r["sector"], {"decision": step, "flags": "proof"}
                )
            except reg.BadgeUndecided:
                pass
    return fields + [c for c in ("badge", "sector") if c not in fields]


# ---------------------------------------------------------------- parts text
_PART = re.compile(
    r"^(?P<neg>-?)(?P<tag>[A-Za-z0-9_]+)(?P<dims>\[[^\]]*\])?=(?P<val>-?[0-9.]+)@(?P<acc>[0-9-]+)#(?P<r>R?\d*)$"
)


def split_parts(text: str) -> list[dict]:
    out = []
    for raw in (text or "").split(";"):
        raw = raw.strip()
        if raw:
            m = _PART.match(raw)
            if not m:
                raise ValueError(f"unparseable part {raw!r}")
            out.append(m.groupdict())
    return out


def join_parts(parts: list[dict]) -> str:
    return ";".join(
        f"{p['neg']}{p['tag']}{p['dims'] or ''}={p['val']}@{p['acc']}#{p['r']}"
        for p in parts
    )


def fmt(d: Decimal) -> str:
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def dec(s) -> Decimal | None:
    s = str(s or "").strip()
    return Decimal(s) if s else None


def signed_sum(parts: list[dict]) -> Decimal:
    return sum(((-1 if p["neg"] else 1) * Decimal(p["val"]) for p in parts), Decimal(0))


# ---------------------------------------------------------------- injections
@dataclass
class Injection:
    cls: str
    ticker: str
    data_point: str
    fiscal_year: str
    before: str  # the cell's changed fields before, as JSON
    after: str  # ... and after
    note: str = ""

    @property
    def key(self) -> Key:
        return (self.ticker, self.data_point, self.fiscal_year)


FIELDS_CHANGED = (
    "display",
    "shown_value",
    "tag",
    "parts",
    "accession",
    "hide_class",
    "reason_code",
    "reason",
    "evidence",
    "class",
    "badge",
)

# Facts a mapping could wrongly serve, by class: (data points, predicate over (fact, shown) -> bool)
COMBINED_AR = re.compile(
    r"^(ReceivablesNetCurrent|AccountsNotesAndLoansReceivableNetCurrent|AccountsAndOtherReceivablesNetCurrent|"
    r"AccountsReceivableNetCurrent|AccountsAndNotesReceivableNet|AccountsReceivableNet|ReceivablesNet)$"
)
COMBINED_AP = re.compile(
    r"^(AccountsPayableAndAccruedLiabilitiesCurrent|AccountsPayableAndOtherAccruedLiabilitiesCurrent|"
    r"AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent|AccountsPayableCurrentAndNoncurrent|"
    r"AccountsPayableAndAccruedLiabilities)$"
)
COMBINED_CF_AR = re.compile(
    r"^(IncreaseDecreaseInAccountsAndOtherReceivables|IncreaseDecreaseInReceivables|IncreaseDecreaseInAccountsAndNotesReceivable)$"
)
COMBINED_CF_AP = re.compile(
    r"^(IncreaseDecreaseInAccountsPayableAndAccruedLiabilities|IncreaseDecreaseInAccountsPayableAndOtherOperatingLiabilities|"
    r"IncreaseDecreaseInAccountsPayableAndAccruedLiabilitiesAndOtherOperatingLiabilities)$"
)
COMBINED = {
    "accounts_receivable": COMBINED_AR,
    "accounts_payable": COMBINED_AP,
    "cf_ar_change": COMBINED_CF_AR,
    "cf_ap_change": COMBINED_CF_AP,
}
RESTRICTED_CASH_TOTAL = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "CashAndCashEquivalentsAndRestrictedCash",
)
AVAILABLE_TO_COMMON = (
    "NetIncomeLossAvailableToCommonStockholdersBasic",
    "NetIncomeLossAvailableToCommonStockholdersDiluted",
)
SUBLINE_DPS = (
    "revenue",
    "cost_of_revenue",
    "operating_expenses",
    "sga_expense",
    "research_and_development",
)
HIDE_EVIDENCE = {
    "verified_absent": "no face-statement line for this role in the year's own 10-K (resolver not_presented, column own)",
}

FactsFor = Callable[[str, set[str], set[str]], list[dck.FilingFact]]


def _shown(r: dict) -> bool:
    return r.get("display") == SHOWN and dec(r.get("shown_value")) is not None


def _single_tag(r: dict) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_]+", (r.get("tag") or "").strip())) and (
        not r.get("parts") or len(split_parts(r["parts"])) == 1
    )


def _days(a: str, b: str) -> int:
    return dc._days(a, b)


def _grain(dp: str) -> int:
    return 0 if dp in dc.INSTANT_DPS else 4


class Planter:
    """Plants errors into copies of the export rows. `facts_for(ticker, accessions, period_ends)` reads the cited
    filings' own facts (draw_check's FilingFact) for the fact-swap classes."""

    def __init__(
        self,
        rows_by_co: dict[str, list[dict]],
        seed: str,
        facts_for: FactsFor | None = None,
    ):
        self.base = rows_by_co
        self.mut = {t: [dict(r) for r in rs] for t, rs in rows_by_co.items()}
        self.rng = random.Random(seed)
        self.facts_for = facts_for
        self.used: set[tuple[str, str]] = (
            set()
        )  # (ticker, data_point): one injection per row
        self.injections: list[Injection] = []
        self.max_tries = 400  # fact-swap classes read a filing per candidate: stop scanning after this many tries

    # -- helpers
    def _cands(self, pred: Callable[[dict, list[dict]], bool]) -> list[dict]:
        out = [
            r
            for t, rs in self.mut.items()
            for r in rs
            if (t, r["data_point"]) not in self.used and pred(r, rs)
        ]
        self.rng.shuffle(out)
        return out

    def _record(self, cls: str, r: dict, before: dict, note: str = "") -> None:
        ch = {
            k: before.get(k, "")
            for k in FIELDS_CHANGED
            if before.get(k, "") != r.get(k, "")
        }
        self.injections.append(
            Injection(
                cls,
                r["ticker"],
                r["data_point"],
                str(r["fiscal_year"]),
                json.dumps(ch, sort_keys=True),
                json.dumps({k: r.get(k, "") for k in ch}, sort_keys=True),
                note,
            )
        )
        self.used.add((r["ticker"], r["data_point"]))

    def _facts(self, r: dict) -> list[dck.FilingFact]:
        if not self.facts_for:
            return []
        return self.facts_for(r["ticker"], {r["accession"]}, {r["period_end"]})

    def _at(self, r: dict, f: dck.FilingFact) -> bool:
        return (
            f.accession == r["accession"]
            and f.qtrs == _grain(r["data_point"])
            and _days(f.ddate, r["period_end"]) <= 7
            and dck.usd_unit(f.uom)
        )

    def _serve_fact(self, r: dict, f: dck.FilingFact) -> None:
        r["shown_value"] = fmt(f.value)
        r["tag"] = f.tag
        r["parts"] = (
            f"{f.tag}[{f.dims.replace(';', ',')}]={fmt(f.value)}@{f.accession}#{r['r_page'].removesuffix('.htm')}"
            if f.dims
            else ""
        )

    # -- classes
    def plant(self, cls: str, n: int) -> int:
        fn = getattr(self, "_p_" + cls)
        got = 0
        for tries, r in enumerate(self._cands(getattr(self, "_e_" + cls))):
            if got >= n or tries >= self.max_tries:
                break
            if (r["ticker"], r["data_point"]) in self.used:
                continue
            before = dict(r)
            note = fn(r)
            if note is None:
                r.clear()
                r.update(before)
                continue
            self._record(cls, r, before, note)
            got += 1
        return got

    def _e_scale(self, r, rs):
        return _shown(r) and dec(r["shown_value"]) != 0

    def _scale(self, r, k: Decimal):
        r["shown_value"] = fmt(Decimal(r["shown_value"]) * k)
        ps = split_parts(r.get("parts", ""))
        for p in ps:
            p["val"] = fmt(Decimal(p["val"]) * k)
        r["parts"] = join_parts(ps) if ps else r.get("parts", "")
        return f"x{k}"

    _e_scale_x1000 = _e_scale_x1e6 = _e_scale

    def _p_scale_x1000(self, r):
        return self._scale(r, Decimal(1000))

    def _p_scale_x1e6(self, r):
        return self._scale(r, Decimal(1000000))

    _e_sign_flip = _e_scale

    def _p_sign_flip(self, r):
        r["shown_value"] = fmt(-dec(r["shown_value"]))
        ps = split_parts(r.get("parts", ""))
        for p in ps:
            p["neg"] = "" if p["neg"] else "-"
        r["parts"] = join_parts(ps) if ps else r.get("parts", "")
        return "negated"

    def _prior(self, r, rs):
        fy = str(int(r["fiscal_year"]) - 1)
        return next(
            (
                x
                for x in rs
                if x["data_point"] == r["data_point"]
                and str(x["fiscal_year"]) == fy
                and _shown(x)
                and (x.get("tag") or "").strip() == (r.get("tag") or "").strip()
                and dec(x["shown_value"]) not in (dec(r["shown_value"]), Decimal(0))
            ),
            None,
        )

    def _e_period_shift(self, r, rs):
        return _shown(r) and _single_tag(r) and self._prior(r, rs) is not None

    def _p_period_shift(self, r):
        p = self._prior(r, self.mut[r["ticker"]])
        r["shown_value"] = p["shown_value"]
        ps = split_parts(r.get("parts", ""))
        for x in ps:
            x["val"] = fmt(abs(dec(p["shown_value"])))
        r["parts"] = join_parts(ps) if ps else r.get("parts", "")
        return f"FY{p['fiscal_year']} value {p['shown_value']} under FY{r['fiscal_year']} citation"

    def _e_dropped_component(self, r, rs):
        if not _shown(r):
            return False
        ps = split_parts(r.get("parts", ""))
        return len(ps) >= 2 and sum(1 for p in ps if Decimal(p["val"]) != 0) >= 2

    def _p_dropped_component(self, r):
        ps = split_parts(r["parts"])
        nz = [i for i, p in enumerate(ps) if Decimal(p["val"]) != 0]
        i = self.rng.choice(nz)
        gone = ps.pop(i)
        r["parts"] = join_parts(ps)
        r["shown_value"] = fmt(signed_sum(ps))
        tags = [t for t in (r.get("tag") or "").split(",") if t and t != gone["tag"]]
        r["tag"] = ",".join(tags)
        return f"dropped {gone['neg']}{gone['tag']}={gone['val']}"

    def _e_subline_as_total(self, r, rs):
        return (
            self.facts_for is not None
            and r["data_point"] in SUBLINE_DPS
            and _shown(r)
            and dec(r["shown_value"]) > 0
        )

    def _p_subline_as_total(self, r):
        total = dec(r["shown_value"])
        fam = {t for tier in dck.FAMILIES.get(r["data_point"], ()) for t in tier}
        fam |= {t for t in (r.get("tag") or "").split(",") if t}
        cand = [
            f
            for f in self._facts(r)
            if self._at(r, f)
            and f.dims
            and f.dims.count("=") == 1
            and f.tag in fam
            and total * Decimal("0.05") < f.value < total * Decimal("0.95")
        ]
        if not cand:
            return None
        f = max(cand, key=lambda f: (f.value, f.dims))
        self._serve_fact(r, f)
        return f"{f.tag}[{f.dims}]={fmt(f.value)} of total {fmt(total)}"

    def _e_combined_as_narrow(self, r, rs):
        return (
            self.facts_for is not None
            and r["data_point"] in COMBINED
            and _shown(r)
            and dec(r["shown_value"]) != 0
        )

    def _p_combined_as_narrow(self, r):
        shown = abs(dec(r["shown_value"]))
        rx = COMBINED[r["data_point"]]
        own = {t for t in (r.get("tag") or "").split(",") if t}
        flow = _grain(r["data_point"]) == 4
        cand = [
            f
            for f in self._facts(r)
            if self._at(r, f)
            and not f.dims
            and rx.match(f.tag)
            and f.tag not in own
            and f.value != 0
            # a balance: the wider line is larger; a cash-flow change: any other amount (the combined line nets more)
            and ((abs(f.value) != shown) if flow else (shown < f.value < shown * 3))
        ]
        if not cand:
            return None
        f = min(cand, key=lambda f: (abs(f.value), f.tag))
        self._serve_fact(r, f)
        return f"{f.tag}={fmt(f.value)} served for narrow {fmt(shown)}"

    def _e_rounded_duplicate(self, r, rs):
        v = dec(r.get("shown_value"))
        return (
            _shown(r)
            and _single_tag(r)
            and v is not None
            and abs(v) >= Decimal(10) ** 7
        )

    def _p_rounded_duplicate(self, r):
        v = dec(r["shown_value"])
        q = (
            Decimal(10) ** 8
            if abs(v) >= Decimal(5) * Decimal(10) ** 8
            else Decimal(10) ** 6
        )
        rv = (v / q).quantize(Decimal(1), rounding=ROUND_HALF_UP) * q
        if rv == v or rv == 0:
            return None
        r["shown_value"] = fmt(rv)
        ps = split_parts(r.get("parts", ""))
        for x in ps:
            x["val"] = fmt(abs(rv))
        r["parts"] = join_parts(ps) if ps else r.get("parts", "")
        return f"{fmt(v)} rounded to {fmt(rv)}"

    def _swap(self, r, tags: tuple[str, ...]):
        shown = Decimal(r["shown_value"])
        cand = [
            f
            for f in self._facts(r)
            if self._at(r, f)
            and not f.dims
            and f.tag in tags
            and f.tag not in (r.get("tag") or "")
            and abs(f.value) != abs(shown)
            and f.value != 0
        ]
        if not cand:
            return None
        f = sorted(cand, key=lambda f: (tags.index(f.tag), -f.dcml))[0]
        self._serve_fact(r, f)
        return f"{f.tag}={fmt(f.value)} served for {fmt(shown)}"

    def _e_restricted_cash_total(self, r, rs):
        return (
            self.facts_for is not None
            and r["data_point"] == "cash_and_equivalents"
            and _shown(r)
        )

    def _p_restricted_cash_total(self, r):
        return self._swap(r, RESTRICTED_CASH_TOTAL)

    def _e_available_to_common_ni(self, r, rs):
        return (
            self.facts_for is not None and r["data_point"] == "net_income" and _shown(r)
        )

    def _p_available_to_common_ni(self, r):
        return self._swap(r, AVAILABLE_TO_COMMON)

    def _e_wrong_hide(self, r, rs):
        return (
            _shown(r)
            and _single_tag(r)
            and dec(r["shown_value"]) != 0
            and sum(
                1
                for x in rs
                if x["data_point"] == r["data_point"] and x.get("display") == SHOWN
            )
            >= 3
        )

    def _p_wrong_hide(self, r):
        allow = r["data_point"] in dc.HIDE_YEAR_ALLOWLIST
        hc = dc.HC_VERIFIED_ABSENT if allow else dc.ONLY_COMBINED
        tag = (r.get("tag") or "").strip()
        r.update(
            display=HIDDEN_YEAR,
            shown_value="",
            tag="",
            parts="",
            hide_class=hc,
            reason_code=hc,
            **{"class": "REASON"},
            reason=f"planted hide ({hc}) of a year the 10-K prints",
            evidence=HIDE_EVIDENCE.get(hc, f"reported only combined: {tag}Abstract"),
            badge="",
        )
        return f"{tag} hidden as {hc}"

    def _e_missing_badge(self, r, rs):
        return _shown(r) and bool(r.get("badge"))

    def _p_missing_badge(self, r):
        was = r["badge"]
        r["badge"] = ""
        return f"badge {was!r} blanked"

    def _other_acc(self, r):
        rs = self.mut[r["ticker"]]
        accs = [
            x["accession"]
            for x in sorted(rs, key=lambda x: int(x["fiscal_year"]))
            if x["data_point"] == r["data_point"]
            and x.get("display") == SHOWN
            and x.get("accession")
            and x["accession"] != r["accession"]
            and int(x["fiscal_year"]) > int(r["fiscal_year"])
        ]
        return accs[0] if accs else None

    def _e_derived_two_filings(self, r, rs):
        return (
            _shown(r)
            and (r.get("badge") or "").startswith("derived:")
            and len(split_parts(r.get("parts", ""))) >= 2
            and len({p["acc"] for p in split_parts(r["parts"])}) == 1
            and self._other_acc(r) is not None
        )

    def _p_derived_two_filings(self, r):
        ps = split_parts(r["parts"])
        i = self.rng.randrange(len(ps))
        other = self._other_acc(r)
        ps[i]["acc"] = other
        r["parts"] = join_parts(ps)
        return f"part {ps[i]['tag']} cited from later filing {other}"


def plant_all(
    rows_by_co: dict[str, list[dict]],
    per_class: int,
    seed: str,
    facts_for: FactsFor | None = None,
    classes: Iterable[str] = CLASSES,
) -> tuple[dict[str, list[dict]], list[Injection], dict[str, int]]:
    p = Planter(rows_by_co, seed, facts_for)
    planted = {cls: p.plant(cls, per_class) for cls in classes}
    return p.mut, p.injections, planted


def apply_injections(
    rows_by_co: dict[str, list[dict]], injections: Iterable[Injection]
) -> dict[str, list[dict]]:
    """Replay a recorded injection set onto untouched rows (the CI fixture)."""
    mut = {t: [dict(r) for r in rs] for t, rs in rows_by_co.items()}
    for inj in injections:
        before, after = json.loads(inj.before), json.loads(inj.after)
        hit = [r for r in mut[inj.ticker] if key(r) == inj.key]
        if len(hit) != 1:
            raise ValueError(f"injection {inj.cls} {inj.key}: {len(hit)} rows")
        for k, v in before.items():
            if (hit[0].get(k) or "") != v:
                raise ValueError(
                    f"injection {inj.cls} {inj.key}: {k} is {hit[0].get(k)!r}, expected {v!r}"
                )
        hit[0].update(after)
    return mut


def read_injections(path: Path) -> list[Injection]:
    with open(path, newline="") as fh:
        return [
            Injection(
                r["class"],
                r["ticker"],
                r["data_point"],
                r["fiscal_year"],
                r["before"],
                r["after"],
                r.get("note", ""),
            )
            for r in csv.DictReader(fh)
        ]


def write_injections(path: Path, injections: Iterable[Injection]) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["class", "ticker", "data_point", "fiscal_year", "before", "after", "note"]
        )
        for i in injections:
            w.writerow(
                [
                    i.cls,
                    i.ticker,
                    i.data_point,
                    i.fiscal_year,
                    i.before,
                    i.after,
                    i.note,
                ]
            )


# ---------------------------------------------------------------- fact sources (record live, replay offline)
def _fact_row(f: dc.Fact) -> list:
    return [
        f.accession,
        f.tag,
        f.ddate,
        f.qtrs,
        f.dims,
        str(f.value),
        list(f.reports),
        f.dcml,
    ]


class BundleSource(dc.BundleFactSource):
    """Replay of a recorded bundle: display_cert.BundleFactSource plus the pattern detectors' presented-fact rows."""

    def presented_facts(self, cik, tags, dates):
        tg, ds = set(tags), set(dates)
        return [
            tuple(r) for r in self.b.get("presented", []) if r[3] in tg and r[4] in ds
        ]


class RecordingSource(dc.SqlFactSource):
    """Live, read-only: every query result is memoized by its arguments and recorded into `bundle`, which
    BundleSource replays (same rows, so the same verdicts)."""

    def __init__(self, conn, timeout_ms: int = 60000, record: bool = True):
        super().__init__(conn, timeout_ms)
        self.record = record
        self.bundle: dict = {}
        self._memo: dict = {}
        self._sets: dict[str, dict] = defaultdict(dict)

    def _add(self, name: str, rows: Iterable[list]) -> None:
        if not self.record:
            return
        s = self._sets[name]
        for r in rows:
            s.setdefault(json.dumps(r, default=str), r)
        self.bundle[name] = list(s.values())

    def _m(self, name, args, fn):
        k = (name, json.dumps(args, sort_keys=True, default=sorted))
        if k not in self._memo:
            self._memo[k] = fn()
        return self._memo[k]

    def facts(self, accessions, tags):
        acc, tg = sorted(set(accessions)), sorted(set(tags))
        got = self._m(
            "facts", [acc, tg], lambda: super(RecordingSource, self).facts(acc, tg)
        )
        self._add("facts", (_fact_row(f) for f in got))
        return got

    def company_facts(self, cik, tags):
        tg = sorted(set(tags))
        got = self._m(
            "company_facts",
            [cik, tg],
            lambda: super(RecordingSource, self).company_facts(cik, tg),
        )
        self._add("company_facts", (_fact_row(f) for f in got))
        return got

    def periodic_year_ends(self, cik):
        got = self._m(
            "year_ends",
            [cik],
            lambda: super(RecordingSource, self).periodic_year_ends(cik),
        )
        if self.record:
            self.bundle.setdefault("year_ends", {}).update(got)
        return got

    def presented_lines(self, cik, tags):
        tg = sorted(set(tags))
        got = self._m(
            "lines",
            [cik, tg],
            lambda: super(RecordingSource, self).presented_lines(cik, tg),
        )
        if self.record:
            ln = self.bundle.setdefault("lines", {})
            for a, ts in got.items():
                ln[a] = sorted(set(ln.get(a, [])) | set(ts))
        return got

    def filing_facts(self, accessions, period_ends):
        acc, pe = sorted(set(accessions)), sorted({p for p in period_ends if p})
        facts, lines = self._m(
            "filing_facts",
            [acc, pe],
            lambda: super(RecordingSource, self).filing_facts(acc, pe),
        )
        self._add(
            "filing_facts",
            (
                [
                    f.accession,
                    f.tag,
                    f.ddate,
                    f.qtrs,
                    f.dims,
                    str(f.value),
                    f.dcml,
                    f.uom,
                ]
                for f in facts
            ),
        )
        self._add(
            "filing_lines",
            (
                [x.accession, x.tag, x.report, x.stmt, x.plabel, x.line, x.negating]
                for x in lines
            ),
        )
        return facts, lines

    def presented_facts(self, cik, tags, dates):
        pd = pattern_detectors()
        tg, ds = sorted(set(tags)), sorted(set(dates))
        if not tg or not ds:
            return []

        def run():
            rows = self._q(
                pd.PRESENTED_SQL,
                {"cik": cik.lstrip("0").zfill(10), "tags": tg, "dates": ds},
            )
            return [(a, f, p, t, str(dd)[:10], int(q)) for a, f, p, t, dd, q in rows]

        got = self._m("presented", [cik, tg, ds], run)
        self._add("presented", (list(r) for r in got))
        return got


# ---------------------------------------------------------------- pattern detectors (tag expert, data-team/tags/library)
_PD = None


def pattern_detectors():
    global _PD
    if _PD is None:
        spec = importlib.util.spec_from_file_location(
            "pattern_detectors", PATTERN_DETECTORS
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        _PD = mod
    return _PD


def dup_facts_from(facts: Iterable[dck.FilingFact]) -> dict:
    """pattern_detectors.DUP_SQL over facts already read: undimensioned facts of one filing, tag, date and grain that
    carry more than one value -> [(value, dcml)]."""
    g: dict[tuple, set] = defaultdict(set)
    for f in facts:
        if not f.dims and f.qtrs in (0, 4):
            g[(f.accession, f.tag, f.ddate, f.qtrs)].add((f.value, f.dcml))
    return {k: sorted(v) for k, v in g.items() if len({x[0] for x in v}) > 1}


def run_patterns(
    rows: list[dict], cik: str, source, dp_tags: dict, filing_facts
) -> dict[tuple[str, str], str]:
    """P02 (coarser duplicate), P03 (share scale), P05/P06 (hidden year presented), P08 (derived parts) on one
    company's export rows -> {(data_point, period_end): first hit detail}."""
    pd = pattern_detectors()
    hits = pd.p03_share_scale(rows, "export") + pd.p08_derived_parts(rows)
    hits += pd.p02_coarser_duplicate([], dup_facts_from(filing_facts), rows)
    hidden = [
        r
        for r in rows
        if r.get("display") in (HIDDEN_YEAR, HIDDEN_ROW) and r.get("period_end")
    ]
    tags = (
        sorted(set().union(*(dp_tags.get(r["data_point"], set()) for r in hidden)))
        if hidden
        else []
    )
    if tags:
        import datetime

        dates = sorted(
            {
                (
                    datetime.date.fromisoformat(r["period_end"])
                    + datetime.timedelta(days=k)
                ).isoformat()
                for r in hidden
                for k in range(-7, 8)
            }
        )
        pres = {rows[0]["ticker"]: source.presented_facts(cik, tags, dates)}
        hits += pd.p05_p06_hidden_presented(hidden, pres, dp_tags)
    out: dict[tuple[str, str], str] = {}
    for h in hits:
        out.setdefault(
            (h["data_point"], h["period_end"]), f"{h['pattern_id']}: {h['detail']}"
        )
    return out


# ---------------------------------------------------------------- evaluation
@dataclass
class Flags:
    """{check: {(data_point, fiscal_year): detail}} for one copy of one company."""

    by_check: dict[str, dict[tuple[str, str], str]] = field(default_factory=dict)


def _cells(
    fields: list[str], rows: list[dict], tmp: Path
) -> tuple[Path, list[dc.Cell]]:
    path = tmp / f"{rows[0]['ticker']}.csv"
    write_rows(path, fields, rows)
    return path, dc.read_coverage(path)


def evaluate_copy(
    fields: list[str],
    rows: list[dict],
    cik: str,
    sample_keys: set[tuple[str, str]],
    source,
    dp_tags: dict,
) -> Flags:
    """Every check on one copy (untouched or mutated) of one company's export. self_check and patterns see every cell;
    cell_match and draw_check are run on `sample_keys` as if certify had drawn them."""
    out = Flags()
    with tempfile.TemporaryDirectory() as td:
        path, cells = _cells(fields, rows, Path(td))
        run = dc.certify(rows[0]["ticker"], cik, path, source, mechanical=True)
    sc: dict[tuple[str, str], str] = {}
    for f in dc.self_check_findings(run):
        if f.data_point == "*":
            continue
        ks = (
            [
                c.key
                for c in cells
                if c.data_point == f.data_point
                and c.display in (HIDDEN_ROW, HIDDEN_YEAR)
            ]
            if f.fiscal_year == "*"
            else [(f.data_point, f.fiscal_year)]
        )
        for k in ks:
            sc.setdefault(k, f"{f.check}: {f.detail}")
    out.by_check["self_check"] = sc
    sample = [c for c in cells if c.key in sample_keys and c.display == SHOWN]
    need_tags = (
        {t.tag for c in sample for t in dc.terms(c)}
        | dc.DEBT_FACE_TAGS
        | dc.LEASE_TAGS
        | dc.DERIVED_TAGS
    )
    need_acc = {t.accession for c in sample for t in dc.terms(c)} | {
        c.accession for c in sample
    }
    facts = source.facts(need_acc, need_tags) if sample else []
    cm = {}
    for c in sample:
        chk = (
            dc.check_derived(c, cells, facts)
            if dc.is_derived(c)
            else dc.check_cell(c, facts)
        )
        if chk.result == "MISMATCH":
            cm[c.key] = chk.evidence
    out.by_check["cell_match"] = cm
    ff, fl = source.filing_facts(*dck.needs(sample)) if sample else ([], [])
    dw = {}
    for a in dck.check_draw(sample, ff, fl) if sample else []:
        if a.outcome == dck.AUTO_MISMATCH:
            dw[a.key] = f"{a.method}: {a.detail}"
    out.by_check["draw_check"] = dw
    pe_fy = {(r["data_point"], r["period_end"]): str(r["fiscal_year"]) for r in rows}
    pats = run_patterns(rows, cik, source, dp_tags, ff)
    out.by_check["patterns"] = {
        (dp, pe_fy[(dp, pe)]): d for (dp, pe), d in pats.items() if (dp, pe) in pe_fy
    }
    return out


@dataclass
class CellResult:
    ticker: str
    data_point: str
    fiscal_year: str
    role: str  # injected | control
    cls: str  # error class, '' for a control cell
    p_drawn: float  # chance the 199-cell draw takes this cell
    base: dict[str, str]  # check -> detail ('' = not flagged)
    mut: dict[str, str]

    def caught(self, check: str) -> bool:
        m, b = self.mut.get(check, ""), self.base.get(check, "")
        return bool(m) and m != b

    def caught_any(self, checks: Iterable[str] = CHECKS) -> bool:
        return any(self.caught(c) for c in checks)


def evaluate_company(
    fields: list[str],
    base_rows: list[dict],
    mut_rows: list[dict],
    cik: str,
    injections: list[Injection],
    controls: set[tuple[str, str]],
    source,
    dp_tags: dict,
) -> list[CellResult]:
    inj_keys = {(i.data_point, i.fiscal_year): i for i in injections}
    sample = set(inj_keys) | controls
    fb = evaluate_copy(fields, base_rows, cik, sample, source, dp_tags)
    fm = evaluate_copy(fields, mut_rows, cik, sample, source, dp_tags)
    shown = sum(1 for r in mut_rows if r.get("display") == SHOWN)
    p = min(1.0, dc.DRAW_SIZE / shown) if shown else 1.0
    out = []
    for k in sorted(sample):
        inj = inj_keys.get(k)
        out.append(
            CellResult(
                base_rows[0]["ticker"],
                k[0],
                k[1],
                "injected" if inj else "control",
                inj.cls if inj else "",
                p,
                {c: fb.by_check.get(c, {}).get(k, "") for c in CHECKS},
                {c: fm.by_check.get(c, {}).get(k, "") for c in CHECKS},
            )
        )
    return out


def pick_controls(
    rows: list[dict],
    exclude: set[tuple[str, str]],
    n_shown: int,
    n_hidden: int,
    rng: random.Random,
):
    shown = sorted(
        (r["data_point"], str(r["fiscal_year"]))
        for r in rows
        if r.get("display") == SHOWN
        and (r["data_point"], str(r["fiscal_year"])) not in exclude
    )
    hidden = sorted(
        (r["data_point"], str(r["fiscal_year"]))
        for r in rows
        if r.get("display") in (HIDDEN_YEAR, HIDDEN_ROW)
        and (r["data_point"], str(r["fiscal_year"])) not in exclude
    )
    return set(rng.sample(shown, min(n_shown, len(shown)))) | set(
        rng.sample(hidden, min(n_hidden, len(hidden)))
    )


# ---------------------------------------------------------------- scoring
def score(results: list[CellResult]) -> dict:
    """Per class: planted, caught by each check, caught by any check, census-only, and the expected recall of one
    certify run (census catch, else a draw-check catch times the chance the 199-cell draw takes the cell).
    Controls: spillover (new flag after injection) and the untouched export's own flag rate."""
    per: dict[str, dict] = {}
    for cls in CLASSES:
        rs = [r for r in results if r.role == "injected" and r.cls == cls]
        n = len(rs)
        row: dict[str, float | int | None] = {"planted": n}
        for c in CHECKS:
            row[c] = sum(1 for r in rs if r.caught(c))
        row["any"] = sum(1 for r in rs if r.caught_any())
        row["census"] = sum(1 for r in rs if r.caught_any(CENSUS_CHECKS))
        row["one_run"] = (
            sum(
                1.0
                if r.caught_any(CENSUS_CHECKS)
                else (r.p_drawn if r.caught_any(DRAW_CHECKS) else 0.0)
                for r in rs
            )
            / n
            if n
            else None
        )
        row["recall"] = sum(1 for r in rs if r.caught_any()) / n if n else None
        per[cls] = row
    inj = [r for r in results if r.role == "injected"]
    ctl = [r for r in results if r.role == "control"]
    overall = {
        "planted": len(inj),
        "caught": sum(1 for r in inj if r.caught_any()),
        "recall": (sum(1 for r in inj if r.caught_any()) / len(inj)) if inj else None,
        "census": sum(1 for r in inj if r.caught_any(CENSUS_CHECKS)),
        "one_run": (
            sum(
                per[c]["one_run"] * per[c]["planted"]
                for c in CLASSES
                if per[c]["planted"]
            )
            / len(inj)
        )
        if inj
        else None,
    }
    controls = {
        "cells": len(ctl),
        "spillover": sum(1 for r in ctl if r.caught_any()),
        "spillover_by_check": {c: sum(1 for r in ctl if r.caught(c)) for c in CHECKS},
        "base_flagged": sum(1 for r in ctl if any(r.base.get(c) for c in CHECKS)),
        "base_flagged_by_check": {
            c: sum(1 for r in ctl if r.base.get(c)) for c in CHECKS
        },
    }
    return {
        "version": HARNESS_VERSION,
        "classes": per,
        "overall": overall,
        "controls": controls,
    }


RESULT_COLUMNS = [
    "ticker",
    "data_point",
    "fiscal_year",
    "role",
    "class",
    "p_drawn",
    *[f"caught_{c}" for c in CHECKS],
    "caught_any",
    *[f"base_{c}" for c in CHECKS],
    *[f"mut_{c}" for c in CHECKS],
]


def result_rows(results: list[CellResult]) -> list[dict]:
    out = []
    for r in results:
        d = {
            "ticker": r.ticker,
            "data_point": r.data_point,
            "fiscal_year": r.fiscal_year,
            "role": r.role,
            "class": r.cls,
            "p_drawn": f"{r.p_drawn:.3f}",
            "caught_any": int(r.caught_any()),
        }
        for c in CHECKS:
            d[f"caught_{c}"] = int(r.caught(c))
            d[f"base_{c}"] = r.base.get(c, "")[:200]
            d[f"mut_{c}"] = r.mut.get(c, "")[:200]
        out.append(d)
    return out
