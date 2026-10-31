"""scripts/check_migrations.py: gaps are legal only for numbers listed in SKIPPED.txt."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "check_migrations.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_migrations_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(directory: Path, number: int, body: str = "select 1;") -> None:
    (directory / f"{number:04d}_x.sql").write_text(body, encoding="utf-8")


@pytest.mark.unit
def test_unlisted_gap_fails(tmp_path):
    cm = _load()
    for n in (1, 2, 4):
        _write(tmp_path, n)
    failures, _ = cm.check(tmp_path)
    assert any("not contiguous" in f for f in failures)


@pytest.mark.unit
def test_listed_gap_passes_and_other_gap_still_fails(tmp_path):
    cm = _load()
    for n in (1, 2, 4, 6):
        _write(tmp_path, n)
    (tmp_path / "SKIPPED.txt").write_text("# c\n0003 never written\n", encoding="utf-8")
    failures, _ = cm.check(tmp_path)
    assert any("not contiguous" in f for f in failures)  # 0005 is not listed
    (tmp_path / "SKIPPED.txt").write_text("0003 never written\n0005 never written\n", encoding="utf-8")
    failures, versions = cm.check(tmp_path)
    assert failures == [] and versions == [1, 2, 4, 6]


@pytest.mark.unit
def test_skipped_number_must_not_have_a_file(tmp_path):
    cm = _load()
    for n in (1, 2, 3):
        _write(tmp_path, n)
    (tmp_path / "SKIPPED.txt").write_text("0002 oops\n", encoding="utf-8")
    failures, _ = cm.check(tmp_path)
    assert any("listed in SKIPPED.txt but a migration file uses it" in f for f in failures)


@pytest.mark.unit
def test_malformed_and_duplicate_skipped_lines_fail(tmp_path):
    cm = _load()
    for n in (1, 3):
        _write(tmp_path, n)
    (tmp_path / "SKIPPED.txt").write_text("0002\n0002 a\n0002 b\n", encoding="utf-8")
    failures, _ = cm.check(tmp_path)
    assert any("must be 'NNNN reason'" in f for f in failures)
    assert any("duplicate number 0002" in f for f in failures)


@pytest.mark.unit
def test_repo_migrations_pass():
    cm = _load()
    failures, _ = cm.check(cm.MIGRATION_DIR)
    assert failures == []
