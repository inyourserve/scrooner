"""Guard rail: a change to the proof's verdict logic must bump proof/prove.py DETECTOR_VERSION.

The mapper's proof guard (company_tag_map._load_proof_disagree) reads only proof rows of the CURRENT detector
version. If prove.py / shown.py change what a verdict means but the version stays, old DISAGREE rows keep
holding cells the fixed proof never re-judges (MSFT sga_expense FY2016-17, 2026-11-13).

How: a sha256 of the AST (comments and formatting do not count) of every verdict-relevant source is pinned next
to the version it belongs with. Editing any of them fails this test until the pin is updated TOGETHER with a
DETECTOR_VERSION bump (a pure refactor that keeps verdicts the same may re-pin the hash with the same version,
said so in the commit message).
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from scrooner_pipeline.proof.prove import DETECTOR_VERSION

SRC = Path(__file__).resolve().parents[2] / "src" / "scrooner_pipeline"
VERDICT_SOURCES = (
    "proof/prove.py",
    "proof/shown.py",
    "proof/dims.py",
    "common/authority.py",
    "common/presentation_scale.py",
)

PINNED_VERSION = "cell_proof_v3_2026-11-13"
PINNED_HASH = "d0f3b864fe8fadea8451d0d97bf665aa1a5d1d1c58bd7c09b7ad36d6d47fe843"


def source_hash() -> str:
    h = hashlib.sha256()
    for rel in VERDICT_SOURCES:
        tree = ast.parse((SRC / rel).read_text())
        for node in ast.walk(tree):  # DETECTOR_VERSION's own value is pinned separately
            if isinstance(node, ast.Assign) and any(
                getattr(t, "id", "") == "DETECTOR_VERSION" for t in node.targets
            ):
                node.value = ast.Constant("")
        h.update(rel.encode() + ast.dump(tree).encode())
    return h.hexdigest()


def test_verdict_logic_change_needs_detector_version_bump():
    assert PINNED_VERSION == DETECTOR_VERSION, (
        "DETECTOR_VERSION changed: set PINNED_VERSION and PINNED_HASH here to match"
    )
    assert source_hash() == PINNED_HASH, (
        "a verdict-relevant proof source changed. If verdicts can differ, bump DETECTOR_VERSION in "
        "proof/prove.py; then set PINNED_VERSION and PINNED_HASH here to "
        f"{source_hash()}"
    )
