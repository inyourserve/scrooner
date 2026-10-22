"""I12 and I13 are reserved ids only (lane 2, 2026-10-22): storable by the amended
0097 constraint, produced by no rule, counted nowhere, never reported as clean."""

import re
from pathlib import Path

import pytest

from scrooner_pipeline.certification import model, runner
from scrooner_pipeline.certification.runner import (
    RunResult,
    render_summary,
    render_text,
)
from scrooner_pipeline.certification.model import RESERVED_INVARIANTS, INVARIANTS
from certification_fixtures import clean_company

CERT_DIR = Path(model.__file__).parent
MIGRATION_0097 = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "0097_certification_tables.sql"
)


def test_reserved_ids_are_exactly_i12_and_i13_and_disjoint_from_implemented():
    assert set(RESERVED_INVARIANTS) == {"I12", "I13"}
    assert not set(RESERVED_INVARIANTS) & set(INVARIANTS)
    assert INVARIANTS == tuple(
        f"I{n}" for n in range(1, 12)
    )  # nothing slipped into the implemented list


def test_a_finding_cannot_be_built_with_a_reserved_id():
    data = clean_company()
    for inv in RESERVED_INVARIANTS:
        with pytest.raises(ValueError, match="reserved"):
            model.finding(data, inv, model.REVIEW, "any_rule", "revenue")
    model.finding(
        data, "I4", model.REVIEW, "any_rule", "revenue"
    )  # implemented ids still work


def test_no_module_emits_a_reserved_id_literal():
    offenders = []
    for path in CERT_DIR.glob("*.py"):
        if path.name == "model.py":
            continue
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if (
                re.search(r"""["']I1[23]["']""", line)
                and "RESERVED_INVARIANTS" not in line
            ):
                offenders.append(f"{path.name}:{n}")
    assert offenders == []


def test_reports_say_reserved_not_clean_and_count_nothing_for_them():
    res = RunResult()
    text = render_summary(res)
    assert "reserved, NOT implemented" in text and "I12" in text and "I13" in text
    full = render_text(res)
    assert (
        "  I12 " not in full and "  I13 " not in full
    )  # no per-invariant zero row that reads as clean


def test_migration_0097_regex_accepts_reserved_ids_and_rejects_non_ids():
    sql = MIGRATION_0097.read_text()
    m = re.search(r"check \(invariant ~ '([^']+)'\)", sql)
    assert m, "0097 must carry the amended regex check"
    pattern = re.compile(m.group(1))
    assert all(pattern.match(i) for i in ("I1", "I11", "I12", "I13"))
    assert not any(pattern.match(i) for i in ("X1", "i12", "I", "I12a", "I-1"))
