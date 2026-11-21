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


@pytest.mark.unit
def test_notefact_extract_pulls_the_filer_own_ppe_net_element():
    # GS FY2014-22 ppe_net is the filer's own note element gs:PropertyPlantsAndEquipmentNet (the face has no PP&E line): the
    # own-period CTE must carry that custom element, as the member CTE (tgm) already does
    sql = SQL.read_text()
    tg = re.search(r"(?m)^tg as \(select id, tag from fsn\.tag where (.*)$", sql)
    assert tg, "tg CTE not found"
    assert "custom and tag ~* '^PropertyPlants?AndEquipment\\w*Net$'" in tg.group(1)
