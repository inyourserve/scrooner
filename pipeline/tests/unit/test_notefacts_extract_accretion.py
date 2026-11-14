"""The standard note-fact input (data-team/tags/line_map/tools/extract_notefacts.sql) carries accretion facts, so the
D&A accretion-evidence rule (resolve_is.accretion_reported) runs from it at 1,000 companies."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SQL = Path(__file__).resolve().parents[3] / "data-team" / "tags" / "line_map" / "tools" / "extract_notefacts.sql"


@pytest.mark.unit
def test_notefact_extract_pulls_every_standard_accretion_tag():
    sql = SQL.read_text()
    tg = re.search(r"tg as \(select id, tag from fsn\.tag where (.*?)\)\nselect", sql, re.S)
    assert tg, "tg CTE not found"
    clause = tg.group(1)
    assert "not custom" in clause and "tag like '%Accretion%'" in clause
    assert not re.search(r"(?m)^\s*--.*tag like", clause)  # not commented out
