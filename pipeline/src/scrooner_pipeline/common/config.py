from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# libpq TCP keepalive + user timeout, added to every pipeline connection
# (2026-10-02). Without them a connection the Supabase pooler drops
# silently leaves the client blocked in recv() forever: a
# calculate-fcf-growth run sat 29 hours with no query in pg_stat_activity,
# and earlier runs hung 4+ hours the same way. With these, a dead socket
# raises OperationalError within ~2 minutes, which the batch loops'
# safe_rollback() then turns into a reconnect. Explicit values already in
# DATABASE_URL win.
CONNECTION_KEEPALIVE_PARAMS = {
    "keepalives": "1",
    "keepalives_idle": "60",
    "keepalives_interval": "15",
    "keepalives_count": "4",
    "tcp_user_timeout": "120000",
}


def with_keepalives(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in ("postgres", "postgresql"):
        return url
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    for key, value in CONNECTION_KEEPALIVE_PARAMS.items():
        query.setdefault(key, value)
    return urlunsplit(parts._replace(query=urlencode(query)))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str

    @field_validator("database_url")
    @classmethod
    def _add_keepalives(cls, value: str) -> str:
        return with_keepalives(value)
    supabase_url: str
    supabase_service_role_key: str
    sec_user_agent: str

    # Market-price vendor (doc 02, resolved 2026-08-17 -- see that doc's
    # decision register). Optional so the pipeline still runs without it
    # (e.g. any job that doesn't touch market prices) -- required only by
    # whatever module actually calls Alpaca.
    alpaca_api_key: str | None = None
    alpaca_api_secret: str | None = None

    # Doc 07 §3: SEC's own ceiling is 10 req/s; doc 02 locks a deliberate
    # buffer under it. Don't raise this just because 10 is technically allowed.
    sec_max_requests_per_second: float = 8.0

    # Day 4: local cache dir for bulk zips (companyfacts.zip/submissions.zip),
    # keyed by date since SEC recompiles them nightly (doc 07 §5). Without
    # this, every invocation -- including a resume after a kill, and any
    # small-scope test run -- re-downloads the full ~1.4GB archive from
    # scratch even though most of it gets thrown away or skipped. See
    # doc/learnings/day-04-retry-and-resume.md.
    bulk_zip_cache_dir: Path = Path(".cache/bulk-zips")


settings = Settings()
