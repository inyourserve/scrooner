"""A small, safe expression language for metric formulas. No eval, no exec.

Grammar (precedence low to high):
    sum    := term (('+' | '-') term)*
    term   := unary (('*' | '/') unary)*
    unary  := '-' unary | atom
    atom   := NUMBER | NAME | NAME '(' args ')' | '(' sum ')'

Names are canonical concept ids, other metric ids, or `price`. Allowed functions
(everything else is a parse error): abs, avg, ttm, annual, quarterly, lag, growth.
Numbers are Decimal; floats are never created.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

ALLOWED_FUNCS = {
    "abs": 1,  # abs(x)
    "avg": 1,  # average of the opening and closing balance of an instant concept
    "ttm": 1,  # trailing-twelve-month value of a flow
    "annual": 1,  # fiscal-year value
    "quarterly": 1,  # single-quarter value
    "lag": 2,  # lag(x, n): the same fiscal period n years earlier
    "growth": 2,  # growth(x, n): n=1 (x - lag)/lag ; n>1 compound annual rate over n years
}
RESERVED_NAMES = {"price"}

_TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z0-9_]*)|(.))")


class ExprError(ValueError):
    pass


@dataclass(frozen=True)
class Num:
    value: Decimal


@dataclass(frozen=True)
class Name:
    name: str


@dataclass(frozen=True)
class Neg:
    arg: object


@dataclass(frozen=True)
class Bin:
    op: str
    left: object
    right: object


@dataclass(frozen=True)
class Call:
    func: str
    args: tuple


def _tokens(text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    pos = 0
    text = text.rstrip()
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m:
            raise ExprError(f"cannot tokenize at {pos}: {text!r}")
        pos = m.end()
        num, name, sym = m.groups()
        if num is not None:
            out.append(("num", num))
        elif name is not None:
            out.append(("name", name))
        elif sym in "+-*/(),":
            out.append(("sym", sym))
        else:
            raise ExprError(f"character {sym!r} is not allowed in a formula: {text!r}")
    return out


class _Parser:
    def __init__(self, text: str):
        self.toks = _tokens(text)
        self.i = 0
        self.text = text

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else ("end", "")

    def take(self, kind=None, val=None):
        t = self.peek()
        if (kind and t[0] != kind) or (val and t[1] != val):
            raise ExprError(f"expected {val or kind}, got {t[1]!r} in {self.text!r}")
        self.i += 1
        return t

    def parse(self):
        node = self.sum()
        if self.peek()[0] != "end":
            raise ExprError(f"trailing input {self.peek()[1]!r} in {self.text!r}")
        return node

    def sum(self):
        node = self.term()
        while self.peek() in (("sym", "+"), ("sym", "-")):
            op = self.take()[1]
            node = Bin(op, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while self.peek() in (("sym", "*"), ("sym", "/")):
            op = self.take()[1]
            node = Bin(op, node, self.unary())
        return node

    def unary(self):
        if self.peek() == ("sym", "-"):
            self.take()
            return Neg(self.unary())
        return self.atom()

    def atom(self):
        kind, val = self.peek()
        if kind == "num":
            self.take()
            return Num(Decimal(val))
        if kind == "name":
            self.take()
            if self.peek() == ("sym", "("):
                if val not in ALLOWED_FUNCS:
                    raise ExprError(
                        f"function {val!r} is not allowed (allowed: {sorted(ALLOWED_FUNCS)})"
                    )
                self.take()
                args = [self.sum()]
                while self.peek() == ("sym", ","):
                    self.take()
                    args.append(self.sum())
                self.take("sym", ")")
                if len(args) != ALLOWED_FUNCS[val]:
                    raise ExprError(
                        f"{val}() takes {ALLOWED_FUNCS[val]} argument(s), got {len(args)}"
                    )
                if val in ("lag", "growth") and not (
                    isinstance(args[0], Name) and isinstance(args[1], Num)
                ):
                    raise ExprError(f"{val}() needs (name, whole number of years)")
                if val in ("avg", "ttm", "annual", "quarterly") and not isinstance(
                    args[0], Name
                ):
                    raise ExprError(f"{val}() takes a single name")
                return Call(val, tuple(args))
            return Name(val)
        if (kind, val) == ("sym", "("):
            self.take()
            node = self.sum()
            self.take("sym", ")")
            return node
        raise ExprError(f"unexpected {val or 'end of formula'!r} in {self.text!r}")


def parse(text: str):
    if not text or not text.strip():
        raise ExprError("empty formula")
    return _Parser(text).parse()


def names(node) -> list[str]:
    """Identifiers used, in first-appearance order."""
    seen: list[str] = []

    def walk(n):
        if isinstance(n, Name):
            if n.name not in seen:
                seen.append(n.name)
        elif isinstance(n, Neg):
            walk(n.arg)
        elif isinstance(n, Bin):
            walk(n.left)
            walk(n.right)
        elif isinstance(n, Call):
            for a in n.args:
                walk(a)

    walk(node)
    return seen


def chain(node):
    """Top-level +/- chain as [(sign, name)] when every term is a bare name; else None."""
    terms: list[tuple[int, str]] = []

    def walk(n, sign):
        if isinstance(n, Name):
            terms.append((sign, n.name))
            return True
        if isinstance(n, Bin) and n.op in "+-":
            return walk(n.left, sign) and walk(n.right, sign if n.op == "+" else -sign)
        return False

    return terms if walk(node, 1) else None


def classify(node):
    """Map the AST onto the legacy generic-engine shape: (shape, [(concept, role)]), or None
    when the formula is not one of the six generic shapes (it is then computed elsewhere)."""
    c = chain(node)
    if c is not None:
        if c[0][0] < 0 or len(c) < 2:
            return None
        if all(s > 0 for s, _ in c):
            return "additive", [(n, "add") for _, n in c]
        return "sum_diff", [(n, "add") for s, n in c if s > 0] + [
            (n, "subtract") for s, n in c if s < 0
        ]
    if (
        isinstance(node, Bin)
        and node.op == "*"
        and isinstance(node.right, Num)
        and node.right.value == 365
    ):
        inner = classify(node.left)
        if inner and inner[0] == "ratio":
            return "days", inner[1]
        return None
    if isinstance(node, Bin) and node.op == "/":
        top, bot = chain(node.left), chain(node.right)
        if (
            top is not None
            and bot is not None
            and top[0][0] > 0
            and all(s > 0 for s, _ in bot)
        ):
            den = [(n, "denominator") for _, n in bot]
            if all(s > 0 for s, _ in top):
                return "ratio", [(n, "numerator") for _, n in top] + den
            return "sum_diff_ratio", (
                [(n, "add") for s, n in top if s > 0]
                + [(n, "subtract") for s, n in top if s < 0]
                + den
            )
        return _classify_roic(node)
    return None


def _classify_roic(node):
    # (nopat_base * (1 - tax / pretax)) / (debt + equity - cash)
    if not (
        isinstance(node.left, Bin)
        and node.left.op == "*"
        and isinstance(node.left.left, Name)
    ):
        return None
    rate = node.left.right
    if not (
        isinstance(rate, Bin)
        and rate.op == "-"
        and rate.left == Num(Decimal(1))
        and isinstance(rate.right, Bin)
        and rate.right.op == "/"
        and isinstance(rate.right.left, Name)
        and isinstance(rate.right.right, Name)
    ):
        return None
    ic = chain(node.right)
    if ic is None or ic[0][0] < 0 or not any(s < 0 for s, _ in ic):
        return None
    return "roic", (
        [
            (node.left.left.name, "nopat_base"),
            (rate.right.left.name, "tax_rate_numerator"),
            (rate.right.right.name, "tax_rate_denominator"),
        ]
        + [(n, "invested_capital_add") for s, n in ic if s > 0]
        + [(n, "invested_capital_subtract") for s, n in ic if s < 0]
    )
