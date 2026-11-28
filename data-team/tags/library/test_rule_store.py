"""M2 step 1: the one rule loader. Parity (predictor and resolver read the same rules through it) and a contradiction
check against a reviewed baseline. No rule content or resolver output changes. Run in CI with the library tests."""

import csv
import os
import shutil
import sys
from pathlib import Path

import pytest

TAGS = Path(__file__).resolve().parent.parent
for sub in ("rules", "exam/tools", "line_map/tools"):
    sys.path.insert(0, str(TAGS / sub))
import predict  # noqa: E402
import resolve_all  # noqa: E402
import rule_store as rs  # noqa: E402

BASELINE = Path(__file__).resolve().parent / "rule-store-known-conflicts.csv"


@pytest.fixture(scope="module")
def rules():
    return rs.load_all()


def test_predictor_tag_rules_parity(rules):
    kb = predict.load_kb(str(TAGS / "rules"))
    assert rs.tag_decisions(rules) == kb["lib"]
    assert len(kb["lib"]) > 400


def test_predictor_override_parity(rules):
    kb = predict.load_kb(str(TAGS / "rules"))
    assert rs.overrides(rules) == kb["ov"]
    assert kb["ov"]


def test_resolver_roles_parity(rules):
    """Every (data_point, role, element) the resolver's ROLES reads is in the loader, and nothing else."""
    want: dict[str, dict[str, set[str]]] = {}
    for r in resolve_all.ROLES:
        d = want.setdefault(r["data_point"], {})
        for role, els in (
            ("alt", r["alternatives"].split("|")),
            ("parent", [r["parent"]]),
            (
                "fallback",
                [r["fallback"]] if r["fallback"] and " " not in r["fallback"] else [],
            ),
        ):
            if els := {e for e in els if e}:
                d[role] = els
    assert rs.role_rows(rules) == want


def test_resolver_polarity_parity(rules):
    got = rs.polarity(rules)
    assert set(got) == set(resolve_all.POLARITY)
    assert all(got[k]["sign"] == v["sign"] for k, v in resolve_all.POLARITY.items())


def test_no_duplicate_rule_ids(rules):
    # An accepted proposal may stay in rules/inbox/ beside its active row (is.operating_expenses.procedure); the
    # inbox is bookkeeping, so only live stores must be unique.
    ids = [r.rule_id for r in rules if r.store != rs.INBOX]
    assert len(ids) == len(set(ids))


def test_no_silent_overwrite_in_predictor_keys(rules):
    """predict.load_kb keeps the last row per key; two rows on one key would be a silent contradiction."""
    for cls, key in (
        ("tag", lambda r: (r.data["when"]["stmt"], r.data["when"]["tag"])),
        ("override", lambda r: (r.data["when"]["cik"], r.data["when"]["tag"])),
    ):
        keys = [key(r) for r in rules if r.store == rs.PREDICTOR and r.cls == cls]
        assert len(keys) == len(set(keys)), cls


def _baseline() -> set[tuple]:
    with open(BASELINE, newline="") as fh:
        return {
            (
                r["kind"],
                r["stmt"],
                r["element"],
                r["resolver_data_points"],
                r["predictor_rule_id"],
            )
            for r in csv.DictReader(fh)
        }


def test_contradictions_match_reviewed_baseline(rules):
    """A new predictor-vs-resolver contradiction fails CI; a closed one must leave the baseline."""
    now = set(rs.conflicts(rules))
    base = _baseline()
    assert not (now - base), (
        f"new rule-store contradictions (decide, then fix or review into {BASELINE.name}): {sorted(now - base)}"
    )
    assert not (base - now), (
        f"baseline rows no longer in conflict (delete them from {BASELINE.name}): {sorted(base - now)}"
    )
    assert not any(k == "HARD" for k, *_ in now), (
        "a HARD contradiction cannot be baselined"
    )


def _copy_stores(tmp: Path):
    r, d = tmp / "rules", tmp / "line_map_rules"
    shutil.copytree(
        TAGS / "rules", r, ignore=shutil.ignore_patterns("inbox", "retired", "*.py")
    )
    shutil.copytree(TAGS / "line_map" / "rules", d)
    return r, d


def test_contradiction_check_catches_a_hard_conflict(tmp_path):
    """Mutation: point the resolver's AR alternative at a tag the predictor maps to another concept."""
    r, d = _copy_stores(tmp_path)
    p = d / "roles.csv"
    text = p.read_text()
    old = "accounts_receivable,BS,AssetsCurrent,AccountsReceivableNetCurrent|"
    assert old in text
    p.write_text(
        text.replace(old, old + "Assets|", 1)
    )  # predictor: BS Assets -> total_assets
    got = rs.conflicts(rs.load_all(str(r), str(d)))
    assert any(k == "HARD" and el == "Assets" for k, _, el, *_ in got)


def test_parity_catches_a_one_sided_edit(tmp_path):
    """Mutation: change a predictor tag rule in a copy; the loader view and predict.load_kb must still agree on the
    copy (both read it), and must differ from the committed rules (proves the comparison can fail)."""
    r, d = _copy_stores(tmp_path)
    p = r / "bs.csv"
    text = p.read_text()
    assert "total_assets_resolved" in text
    p.write_text(text.replace("total_assets_resolved", "total_assets_XX_resolved", 1))
    mutated = rs.tag_decisions(rs.load_all(str(r), str(d)))
    assert mutated == predict.load_kb(str(r))["lib"]
    assert mutated != predict.load_kb(str(TAGS / "rules"))["lib"]


def test_predictor_reads_through_the_loader(monkeypatch):
    """M2 step 2: predict.load_kb takes its rows from rule_store.load_predictor (not its own csv read)."""
    full = predict.load_kb(str(TAGS / "rules"))
    assert full["ov"] and full["lib"]
    seen = []
    real = rs.load_predictor

    def fewer(d=None):
        seen.append(d)
        return [r for r in real(d) if r.cls != "override"]

    monkeypatch.setattr(rs, "load_predictor", fewer)
    kb = predict.load_kb(str(TAGS / "rules"))
    assert seen and kb["ov"] == {} and kb["lib"] == full["lib"]
    assert (
        kb["version"] == full["version"]
    )  # the VERSION hash still covers the files, not the loaded rows
