"""The proof_blank stage of pipeline-fsn-write.yml (ruling addendum N2): plan unless apply is true, and a
before-image upload precedes every --apply load. Text-level parse (pyyaml is not a pipeline dependency)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

WORKFLOW = (
    Path(__file__).resolve().parents[3] / ".github/workflows/pipeline-fsn-write.yml"
)


def _steps(job: str) -> list[str]:
    text = WORKFLOW.read_text()
    m = re.search(rf"^  {job}:\n(.*?)(?=^  \S|\Z)", text, re.S | re.M)
    assert m, f"job {job} not found"
    body = m.group(1)
    steps = body.split("\n    steps:\n", 1)[1]
    return re.split(r"^      - ", steps, flags=re.M)[1:]


def _loads(steps: list[str], flag: str) -> list[int]:
    return [i for i, s in enumerate(steps) if "scrooner-cells load" in s and flag in s]


@pytest.mark.unit
def test_the_stage_is_an_input_choice_with_an_apply_boolean_default_false():
    text = WORKFLOW.read_text()
    assert re.search(r"options: \[[^\]]*proof_blank[^\]]*\]", text)
    m = re.search(r"^      apply:\n(.*?)(?=^      \w+:\n)", text, re.S | re.M)
    assert m and "type: boolean" in m.group(1) and "default: false" in m.group(1)
    assert "proof_run:" in text


@pytest.mark.unit
def test_proof_blank_plans_unless_apply_is_true():
    steps = _steps("proof_blank")
    plans = _loads(steps, "--plan")
    applies = _loads(steps, "--apply")
    assert plans and applies
    for i in plans:
        assert "!inputs.apply" in steps[i]
    for i in applies:
        assert "inputs.apply" in steps[i] and "!inputs.apply" not in steps[i]
        assert "--plan" not in steps[i]
    # no load is unconditional
    for i in plans + applies:
        assert re.search(r"^\s*if: ", steps[i], re.M)


@pytest.mark.unit
def test_a_before_image_upload_precedes_every_apply_load():
    steps = _steps("proof_blank")
    uploads = [
        i
        for i, s in enumerate(steps)
        if "upload-artifact" in s and "fsn-proofblank-before-image-" in s
    ]
    applies = _loads(steps, "--apply")
    assert uploads and applies
    assert min(uploads) < min(applies)
    # the export itself precedes its upload
    exports = [i for i, s in enumerate(steps) if "proof_blank_before_image.py" in s]
    assert exports and min(exports) < min(uploads)


@pytest.mark.unit
def test_other_jobs_skip_proof_blank_and_it_needs_the_seed_preflight():
    text = WORKFLOW.read_text()
    assert re.search(r"^  proof_blank:\n(?:.*\n)*?    needs: seed\n", text, re.M)
    assert "inputs.stage != 'restore' && inputs.stage != 'proof_blank'" in text
