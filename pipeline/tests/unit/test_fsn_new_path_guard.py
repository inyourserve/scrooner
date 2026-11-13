"""The new-path skip lives in the old-path writer commands themselves (Ritwik's PR #12 review, 2026-11-12):
no entry point can write a company on the new nightly path while HYBRID_NEW_PATH=on.

Entry points covered: reprocess_recent_filers.sh, reprocess_fiscal_year_relabel.sh, run_conflict_latest_filed.sh,
pipeline-recompute.yml (its per-company phases through the CLI, and its population phase, which calls writer
functions directly). Every writer command those entry points can reach is invoked through the real CLI with a
new-path CIK in --ciks: the command body must never see it."""

from __future__ import annotations

import re
from pathlib import Path

import psycopg
import pytest
import typer
from scrooner_pipeline.fsn_store import new_path

REPO = Path(__file__).resolve().parents[3]
NEW_PATH_CIK = "0000000002"
OLD_PATH_CIK = "0000000001"


def _apps() -> dict[str, typer.Typer]:
    from scrooner_pipeline.jobs import map as map_job
    from scrooner_pipeline.jobs import normalize as normalize_job

    return {"scrooner-normalize": normalize_job.app, "scrooner-map": map_job.app}


def _command_names(app: typer.Typer) -> set[str]:
    group = typer.main.get_command(app)
    return set(group.list_commands(typer.Context(group)))  # type: ignore[attr-defined]


def entry_point_commands() -> dict[str, set[str]]:
    """program -> every subcommand some entry point invokes (scripts and workflows, as written today)."""
    found: dict[str, set[str]] = {"scrooner-normalize": set(), "scrooner-map": set()}
    reprocess = (REPO / "pipeline/scripts/reprocess_recent_filers.sh").read_text()
    stages = re.search(r"STAGES=\(\n(.*?)\n\)", reprocess, re.S)
    assert stages, "reprocess_recent_filers.sh STAGES array not found"
    for entry in stages.group(1).split():
        kind, _, stage = entry.partition(":")
        found[f"scrooner-{kind}"].add(stage)
    relabel = (REPO / "pipeline/scripts/reprocess_fiscal_year_relabel.sh").read_text()
    for line in re.findall(r'^STAGES="([^"]+)"', relabel, re.M):
        found["scrooner-normalize"].update(line.split())
    m = re.search(r"for stage in ([a-z0-9 -]+); do\n\s+echo \"--- map", relabel)
    assert m, "relabel map stage loop not found"
    found["scrooner-map"].update(m.group(1).split())
    conflict = (REPO / "pipeline/scripts/run_conflict_latest_filed.sh").read_text()
    found["scrooner-normalize"].update(re.findall(r"scrooner-normalize ([a-z-]+)", conflict))
    wf = (REPO / ".github/workflows/pipeline-recompute.yml").read_text()

    def default(name: str) -> list[str]:
        m = re.search(rf"^      {name}:\n(?:        .*\n)*?        default: \"([^\"]*)\"", wf, re.M)
        assert m, f"pipeline-recompute.yml input {name} not found"
        return m.group(1).split()

    found["scrooner-normalize"].update(default("normalize_stages"))
    for name in ("resolve_stages", "population_stages", "metric_stages"):
        found["scrooner-map"].update(default(name))
    return found


def test_every_cli_command_is_classified_exactly_once():
    for program, app in _apps().items():
        names = _command_names(app)
        w, n = new_path.WRITER_COMMANDS[program], new_path.NOT_WRITER_COMMANDS[program]
        assert not (w & n), (program, w & n)
        assert names == w | n, (program, "unclassified", names - (w | n), "stale", (w | n) - names)


def test_the_reviewed_writers_are_writers():
    """The stages Ritwik's review names, and every canonical_fact writer behind the CLI."""
    assert {"conflict-latest-filed", "derive-interim-quarters", "derive-q4"} <= new_path.WRITER_COMMANDS["scrooner-normalize"]
    assert {
        "resolve-facts",
        "resolve-concept-fallbacks",
        "split-rebase",
        "resolve-statement-fallbacks",
        "resolve-conflict-fills",
        "resolve-dedup-holes",
        "resolve-parser-results",
    } <= new_path.WRITER_COMMANDS["scrooner-map"]
    # the SEC ingestion the tag-map mapper reads keeps running for every company
    assert {"identity", "periods", "units", "facts", "dedupe", "restatements"} <= new_path.NOT_WRITER_COMMANDS["scrooner-normalize"]


def test_every_entry_point_command_is_classified_and_passes_ciks():
    found = entry_point_commands()
    for program, cmds in found.items():
        allc = new_path.WRITER_COMMANDS[program] | new_path.NOT_WRITER_COMMANDS[program]
        assert cmds <= allc, (program, cmds - allc)
    for script in ("reprocess_fiscal_year_relabel.sh", "run_conflict_latest_filed.sh"):
        for line in (REPO / "pipeline/scripts" / script).read_text().splitlines():
            if re.search(r"uv run scrooner-(normalize|map) ", line):
                assert "--ciks" in line, (script, line)
    wf = (REPO / ".github/workflows/pipeline-recompute.yml").read_text()
    for line in wf.splitlines():
        if re.search(r"scrooner-(normalize|map) \"\$stage\"", line):
            assert "--ciks" in line, line


def _writer_entry_points() -> list[tuple[str, str]]:
    found = entry_point_commands()
    return sorted((p, c) for p, cmds in found.items() for c in cmds if c in new_path.WRITER_COMMANDS[p])


@pytest.mark.parametrize("program,command", _writer_entry_points())
def test_no_entry_point_writer_sees_a_new_path_company(monkeypatch, program, command):
    """Every writer some entry point runs, through the real CLI group: with HYBRID_NEW_PATH=on the command
    body never receives a new-path CIK; with only new-path CIKs it does not run at all; off, it sees all."""
    app = _apps()[program]
    group = typer.main.get_command(app)
    cmd = group.get_command(typer.Context(group), command)  # type: ignore[attr-defined]
    seen: list[str | None] = []
    monkeypatch.setattr(cmd, "callback", lambda **kw: seen.append(kw.get("ciks")))
    monkeypatch.setattr(new_path, "_db_new_path_ciks", lambda: [NEW_PATH_CIK])

    monkeypatch.setenv(new_path.FLAG, "on")
    if "ciks" not in {p.name for p in cmd.params}:
        # population-wide (no company list): refused outright while the flag is on (fail closed); the
        # functions behind it refuse too when called directly (test_population_writers_refuse_...)
        with pytest.raises(Exception, match="needs --ciks"):
            group.main([command], standalone_mode=False)
        assert seen == []
        return
    group.main([command, "--ciks", f"{OLD_PATH_CIK},{NEW_PATH_CIK}"], standalone_mode=False)
    assert seen == [OLD_PATH_CIK]
    seen.clear()
    group.main([command, "--ciks", NEW_PATH_CIK], standalone_mode=False)
    assert seen == []
    monkeypatch.setenv(new_path.FLAG, "off")
    group.main([command, "--ciks", f"{OLD_PATH_CIK},{NEW_PATH_CIK}"], standalone_mode=False)
    assert seen == [f"{OLD_PATH_CIK},{NEW_PATH_CIK}"]


def test_a_writer_without_ciks_is_refused_when_on(monkeypatch):
    with pytest.raises(new_path.NewPathRefused):
        new_path.guard_args(["--batch-size", "5"], lambda: [NEW_PATH_CIK])
    assert new_path.guard_args(["--ciks=1,2"], lambda: ["2"]) == ["--ciks=1"]
    assert new_path.guard_args(["--ciks", "2"], lambda: ["2"]) is None


def test_derived_and_ingestion_commands_are_not_filtered(monkeypatch):
    group = typer.main.get_command(_apps()["scrooner-map"])
    cmd = group.get_command(typer.Context(group), "calculate")  # type: ignore[attr-defined]
    seen: list[str | None] = []
    monkeypatch.setattr(cmd, "callback", lambda **kw: seen.append(kw.get("ciks")))
    monkeypatch.setattr(new_path, "_db_new_path_ciks", lambda: [NEW_PATH_CIK])
    monkeypatch.setenv(new_path.FLAG, "on")
    group.main(["calculate", "--ciks", f"{OLD_PATH_CIK},{NEW_PATH_CIK}"], standalone_mode=False)
    assert seen == [f"{OLD_PATH_CIK},{NEW_PATH_CIK}"]


# ---------------------------------------------------------------- population-wide writers (DB)


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if _one(c, "select to_regclass('analytics.slot_protected_cell') is not null and to_regclass('analytics.rule_run') is not null") is not True:
        c.close()
        pytest.skip("needs migrations 0100/0113")
    yield c
    c.close()


@pytest.mark.integration
@pytest.mark.parametrize(
    "module,function",
    [
        ("scrooner_pipeline.mapper.concept_fallback", "resolve_all_arithmetic_fallbacks"),
        ("scrooner_pipeline.mapper.conflict_resolution", "resolve_all_conflict_fills"),
        ("scrooner_pipeline.mapper.dedup_majority_resolver", "resolve_all_safe_concepts"),
    ],
)
def test_population_writers_refuse_once_a_company_is_on_the_new_path(conn, monkeypatch, module, function):
    """pipeline-recompute.yml's population phase calls these directly (no CLI, no company list)."""
    import importlib

    fn = getattr(importlib.import_module(module), function)
    cid = _one(conn, "insert into core.company (cik, company_name) values (%s, 'NEW PATH') returning id", (NEW_PATH_CIK,))
    concept = _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode) values ('np_test', 'income_statement', 'first_match') returning id")
    period = _one(conn, "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) values (%s, '2026-07-01', '2026-09-30', 'duration', 2026, 'Q3') returning id", (cid,))
    run = _one(conn, "insert into analytics.rule_run (rule_id, rule_version, mode, flag_name, flag_state) values ('company_tag_map.select@1', 1, 'apply', 't', 'on') returning run_id")
    conn.execute(
        "insert into analytics.slot_protected_cell (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256) values (%s, %s, %s, 'company_tag_map.select@1', 1, %s, 'x')",
        (cid, concept, period, str(run)),
    )
    conn.commit()
    monkeypatch.setenv(new_path.FLAG, "on")
    with pytest.raises(new_path.NewPathRefused):
        fn(conn)
    conn.rollback()
