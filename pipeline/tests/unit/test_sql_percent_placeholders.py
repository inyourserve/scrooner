"""psycopg reads every `%` in a query that has parameters as a placeholder, comments included.

The nightly refresh failed four nights running (2026-11-12..15, runs 43297498847..43749760986) with
`ProgrammingError: incomplete placeholder: '%'` because a SQL comment in reprocess_recent_filers.sh said
"about 73% already had". This scans the triple-quoted SQL of the Python heredocs in pipeline/scripts/*.sh."""

import re
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
HEREDOC = re.compile(r"<<'?PY'?\n(.*?)\nPY\n", re.S)
TRIPLE = re.compile(r'"""(.*?)"""', re.S)
# allowed: %s, %b, %t, %(name)s, %% ; anything else is a stray percent
STRAY = re.compile(r"%(?![sbt]|\([A-Za-z_][A-Za-z0-9_]*\)[sbt]|%)")


def stray_percents(text: str) -> list[str]:
    out = []
    for py in HEREDOC.findall(text):
        for sql in TRIPLE.findall(py):
            if "%s" not in sql and "%(" not in sql:
                continue  # no parameters: psycopg leaves % alone
            for line in sql.splitlines():
                if STRAY.search(line):
                    out.append(line.strip())
    return out


def test_detector_catches_a_percent_in_a_sql_comment():
    bad = "x=$(python3 - <<'PY'\ncur.execute(\n    \"\"\"\n    select 1 where a = %s\n    -- about 73% done\n    \"\"\", (1,))\nPY\n)\n"
    assert stray_percents(bad) == ["-- about 73% done"]


def test_no_stray_percent_in_parameterised_sql_of_pipeline_scripts():
    found = {
        p.name: hits for p in sorted(SCRIPTS.glob("*.sh")) if (hits := stray_percents(p.read_text()))
    }
    assert found == {}
