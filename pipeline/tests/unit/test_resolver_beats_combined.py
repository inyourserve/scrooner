"""ONE-PATH: a structural (resolver) row of the cell beats an older company_tag_map 'combined' row (AMGN interest
expense: the resolver reads it from a note under InterestExpenseDebt; the library combined row spans interest expense and
interest income). Rule-scoped: only cells a combined row spans are re-proved."""

from __future__ import annotations

from datetime import date

import pytest
from scrooner_pipeline.proof import rules
from scrooner_pipeline.proof.prove import Shown
from scrooner_pipeline.proof.shown import (
    claim_for,
    combined_for,
    resolver_decision_beats_combined,
)

END = date(2015, 12, 31)
STRUCT = "company_tag_map.structural@1"
# (id, decision, stmt, tag, concept, parent, sign, era_from, era_to, rule_id)
RESOLVER_ROW = (
    595832, "concept", "UN", "InterestExpenseDebt", "interest_expense", None, 1,
    date(2015, 1, 1), date(2015, 12, 31), STRUCT,
)  # fmt: skip
DOCMAP_ROW = (
    1, "concept", "IS", "InterestExpenseDebt", "interest_expense", None, 1,
    date(2015, 1, 1), None, "company_tag_map.docmap@1",
)  # fmt: skip
COMBINED = [
    (
        "InterestExpenseDebt",
        ("interest_expense", "interest_income"),
        date(2015, 3, 31),
        date(2026, 6, 30),
    )
]


@pytest.mark.unit
def test_structural_row_of_the_cell_beats_the_combined_row():
    assert combined_for(COMBINED, "interest_expense", END) == ("InterestExpenseDebt",)
    assert resolver_decision_beats_combined([RESOLVER_ROW], "interest_expense", END)
    c = claim_for([RESOLVER_ROW], "interest_expense", END)
    assert c is not None and c.tags == ("InterestExpenseDebt",)


@pytest.mark.unit
def test_an_old_docmap_row_or_another_era_or_another_concept_does_not_beat_it():
    assert not resolver_decision_beats_combined([DOCMAP_ROW], "interest_expense", END)
    assert not resolver_decision_beats_combined(
        [RESOLVER_ROW], "interest_expense", date(2016, 12, 31)
    )
    assert not resolver_decision_beats_combined([RESOLVER_ROW], "interest_income", END)
    assert not resolver_decision_beats_combined([], "interest_expense", END)


@pytest.mark.unit
def test_structural_component_row_beats_it_too():
    comp = (7, "component", "IS", "InterestExpenseDebt", None, "interest_expense", 1,
            date(2015, 1, 1), None, STRUCT)  # fmt: skip
    assert resolver_decision_beats_combined([comp], "interest_expense", END)


@pytest.mark.unit
def test_rule_is_registered_and_selects_cells_a_combined_row_spans():
    r = rules.RULES["resolver_beats_combined"]
    assert r.legacy_version == 0  # a stored row without the rule is re-proved
    spans = Shown(
        1, "interest_expense", "FY", date(2015, 1, 1), END, 1, ("InterestExpenseDebt",),
        "A", (1,), False, 6, combined_splits=(("InterestExpenseDebt", ("a", "b")),),
    )  # fmt: skip
    plain = Shown(
        1, "revenue", "FY", date(2015, 1, 1), END, 1, ("Revenues",), "A", (1,), False, 6
    )  # fmt: skip
    assert rules.rules_used(spans, {})["resolver_beats_combined"] == r.version
    assert "resolver_beats_combined" not in rules.rules_used(plain, {})
