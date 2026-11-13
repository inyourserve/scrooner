"""formula_lock.json: the committed (version, fingerprint) of every metric formula.

Formulas are frozen until the top-100 inputs certify. Editing any formula-relevant field of a
registry row (expression, inputs, period rule, null rules, perimeter, perimeter_spec, applies_to,
calculator) changes its fingerprint; tests/unit/test_metric_registry_agreement.py fails until the
metric's `version` is bumped AND this lock is regenerated, so a formula change is always a
reviewed, versioned event (and `provenance.proof_is_stale` marks the old cell proofs stale).

    python -m scrooner_pipeline.metrics.lock          # rewrite the lock after a deliberate bump
"""

from __future__ import annotations

import json
from pathlib import Path

from scrooner_pipeline.metrics.provenance import formula_fingerprint
from scrooner_pipeline.metrics.registry import get_registry

LOCK_PATH = Path(__file__).parent / "formula_lock.json"


def build_lock() -> dict[str, dict]:
    return {
        m.metric_id: {"version": m.version, "fingerprint": formula_fingerprint(m)}
        for m in get_registry().values()
    }


def load_lock() -> dict[str, dict]:
    return json.loads(LOCK_PATH.read_text())


def lock_problems() -> list[str]:
    lock, cur = load_lock(), build_lock()
    out = []
    for mid, now in cur.items():
        old = lock.get(mid)
        if old is None:
            out.append(
                f"{mid}: not in formula_lock.json (new metric: add it deliberately with `python -m scrooner_pipeline.metrics.lock`)"
            )
        elif (
            old["fingerprint"] != now["fingerprint"]
            and old["version"] == now["version"]
        ):
            out.append(
                f"{mid}: formula changed without a version bump (frozen until top-100 certification)"
            )
        elif old != now:
            out.append(
                f"{mid}: version/fingerprint changed; regenerate formula_lock.json in the same commit"
            )
    out += [
        f"{mid}: in formula_lock.json but not in the registry"
        for mid in lock
        if mid not in cur
    ]
    return out


if __name__ == "__main__":
    LOCK_PATH.write_text(json.dumps(build_lock(), indent=1, sort_keys=True) + "\n")
    print(f"wrote {LOCK_PATH} ({len(build_lock())} metrics)")
