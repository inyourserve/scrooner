from contextlib import contextmanager
from typing import Iterator

import psycopg

from scrooner_pipeline.common.config import settings


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    with psycopg.connect(settings.database_url) as conn:
        yield conn
