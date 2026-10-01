"""Structural guards for the two connection failure modes that cost real
runs: a dead connection cascading through a batch loop, and a dead socket
hanging a job for hours (2026-10-02)."""

import re
from pathlib import Path

from scrooner_pipeline.common.config import with_keepalives

SRC = Path(__file__).resolve().parents[2] / "src" / "scrooner_pipeline"

# A per-company loop that logs an error and moves on must replace a
# possibly-dead connection first. Missing it let one pooler drop fail 169
# of 172 companies in quality_flags / reconciliation / tax_reconciliation.
_LOG_THEN_CONTINUE = re.compile(
    r"^( +)log_error\(conn,[^\n]*\)\n\1continue\n", re.M
)


def test_no_batch_loop_continues_on_a_possibly_dead_connection():
    offenders = [
        str(path.relative_to(SRC))
        for path in SRC.rglob("*.py")
        if _LOG_THEN_CONTINUE.search(path.read_text())
    ]
    assert offenders == [], (
        "log_error(conn, ...) followed directly by `continue` keeps using a "
        f"possibly-dead connection; add `conn = safe_rollback(...)`: {offenders}"
    )


def test_keepalives_added_to_postgres_url():
    url = with_keepalives("postgresql://u:p@host:5432/db")
    assert "keepalives=1" in url and "tcp_user_timeout=120000" in url
    assert url.startswith("postgresql://u:p@host:5432/db?")


def test_explicit_url_params_win_and_existing_params_kept():
    url = with_keepalives("postgresql://h/db?sslmode=require&keepalives_idle=5")
    assert "sslmode=require" in url and "keepalives_idle=5" in url
    assert url.count("keepalives_idle") == 1


def test_non_postgres_url_untouched():
    assert with_keepalives("sqlite:///x.db") == "sqlite:///x.db"
