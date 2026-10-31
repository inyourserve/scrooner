"""One read-only database connection for the per-share lane's dry-run scripts (statement_timeout set)."""

import os
from pathlib import Path

import psycopg


def conn(
    env_file: Path = Path(__file__).resolve().parents[1] / ".env",
) -> psycopg.Connection:
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))
    c = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)
    c.execute("set statement_timeout = '120s'")
    c.execute("set default_transaction_read_only = on")
    return c
