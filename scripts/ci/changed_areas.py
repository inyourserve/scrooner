"""Print GitHub step outputs `python=` and `app=` for ci.yml: which suites a push or pull request needs.

Conservative: when the diff cannot be computed (new branch, force push, shallow history) both are true.
Python is skipped only when every changed path is app-only (apps/app, packages, mind). The app suite runs only when
the app, the design system, or this CI plumbing changed.
"""

import os
import subprocess
import sys

APP_PREFIXES = ("apps/app/", "packages/")
NON_PYTHON_PREFIXES = APP_PREFIXES + ("mind/",)
ALWAYS_ALL = (".github/workflows/ci.yml", "scripts/ci/changed_areas.py")
ZERO = "0" * 40


def classify(paths: list[str] | None) -> dict[str, bool]:
    if paths is None:
        return {"python": True, "app": True}
    if any(p in ALWAYS_ALL for p in paths):
        return {"python": True, "app": True}
    python = any(not p.startswith(NON_PYTHON_PREFIXES) for p in paths)
    app = any(p.startswith(APP_PREFIXES) for p in paths)
    return {"python": python, "app": app}


def changed_paths(env: dict[str, str]) -> list[str] | None:
    base = env.get("PR_BASE") if env.get("EVENT") == "pull_request" else env.get("BEFORE")
    if not base or base == ZERO:
        return None
    rng = f"{base}...HEAD" if env.get("EVENT") == "pull_request" else f"{base}..HEAD"
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", rng], check=True, capture_output=True, text=True
        ).stdout
    except subprocess.CalledProcessError:
        return None
    return [p for p in out.splitlines() if p]


def main() -> int:
    areas = classify(changed_paths(dict(os.environ)))
    for k, v in areas.items():
        print(f"{k}={'true' if v else 'false'}")
    print(areas, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
