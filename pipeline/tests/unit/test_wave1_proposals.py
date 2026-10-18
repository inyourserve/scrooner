"""Wave 1 proposals in mapper/expanded_concepts.py must stay well-formed,
unapproved, and must not double-map a tag already mapped elsewhere."""

from scrooner_pipeline.mapper import concepts, expanded_concepts as ec

CONCEPTS = ec.WAVE1_CANONICAL_CONCEPTS
MAPPINGS = ec.WAVE1_CONCEPT_MAPPINGS
NAMES = {c[0] for c in CONCEPTS}
ALLOWED_CONF = {"provisional"}  # 'candidate' is not storable (migration 0004 CHECK)
STATEMENTS = {"income_statement", "balance_sheet", "cash_flow"}
EXPECTED_NAMES = {
    "retained_earnings",
    "weighted_avg_shares_basic",
    "weighted_avg_shares_diluted",
    "operating_lease_rou_asset",
    "operating_lease_liability_total",
    "operating_lease_liability_total_resolved",
    "operating_lease_liability_current",
    "operating_lease_liability_noncurrent",
    "interest_paid_cash",
    "income_taxes_paid_cash",
}


def _check_wellformed(concepts_, mappings):
    names = [c[0] for c in concepts_]
    assert len(names) == len(set(names))
    for name, statement, mode, desc in concepts_:
        assert statement in STATEMENTS and mode in {"first_match", "sum"} and desc
    for cname, tax, tag, prio, conf, notes in mappings:
        assert cname in names and tax in {"us-gaap", "dei"} and tag and prio >= 1
        assert conf in ALLOWED_CONF, f"{tag} must not be approved: {conf}"
        assert notes
    keys = [(m[0], m[2]) for m in mappings]
    assert len(keys) == len(set(keys))


def test_expected_concepts_present_and_wellformed():
    assert NAMES == EXPECTED_NAMES
    _check_wellformed(CONCEPTS, MAPPINGS)


def test_none_approved_and_notes_say_unapproved():
    assert all(m[4] != "approved" for m in MAPPINGS)
    assert all("unapproved" in m[5] for m in MAPPINGS)


def test_no_sum_mode_and_resolved_has_no_mapping_rows():
    # the sum fallback is a _resolved build, never a sum concept_mapping row
    assert all(c[2] == "first_match" for c in CONCEPTS)
    resolved = {n for n in NAMES if n.endswith("_resolved")}
    assert resolved == {"operating_lease_liability_total_resolved"}
    assert not [m for m in MAPPINGS if m[0] in resolved]


def test_first_match_priorities_unique_per_concept():
    by: dict[str, list[int]] = {}
    for m in MAPPINGS:
        by.setdefault(m[0], []).append(m[3])
    for n, ps in by.items():
        assert len(ps) == len(set(ps)), n


def test_cash_paid_never_mapped_as_expense_fallback():
    for m in MAPPINGS:
        assert m[0] not in {"interest_expense", "income_tax_expense", "stockholders_equity"}
    tags = {m[2] for m in MAPPINGS}
    assert not tags & {"InterestExpense", "IncomeTaxExpenseBenefit", "StockholdersEquity"}


def test_seeding_gate_default_off_keeps_live_lists_untouched():
    assert ec.WAVE1_SEED_ENABLED is False
    live_names = {c[0] for c in ec.NEW_CANONICAL_CONCEPTS}
    assert not live_names & NAMES
    assert not {m[2] for m in ec.NEW_CONCEPT_MAPPINGS} & {m[2] for m in MAPPINGS}


def test_no_tag_double_mapped_in_code_catalogs():
    wave = {(m[1], m[2]) for m in MAPPINGS}
    existing = {(m[1], m[2]) for m in concepts.CONCEPT_MAPPINGS}
    existing |= {(m[1], m[2]) for m in ec.NEW_CONCEPT_MAPPINGS}
    assert not wave & existing, wave & existing
    assert not NAMES & {c[0] for c in concepts.CANONICAL_CONCEPTS}


def _raises(fn):
    try:
        fn()
    except AssertionError:
        return True
    return False


def test_validator_rejects_approved_unknown_and_duplicate():
    assert _raises(
        lambda: _check_wellformed(
            CONCEPTS, MAPPINGS + [("retained_earnings", "us-gaap", "X", 9, "approved", "n")]
        )
    )
    assert _raises(
        lambda: _check_wellformed(
            CONCEPTS, MAPPINGS + [("nope", "us-gaap", "Y", 1, "provisional", "n")]
        )
    )
    assert _raises(lambda: _check_wellformed(CONCEPTS, MAPPINGS + [MAPPINGS[0]]))
