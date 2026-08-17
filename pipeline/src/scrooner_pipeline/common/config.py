from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    supabase_url: str
    supabase_service_role_key: str
    sec_user_agent: str

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
