"""Backend test safety configuration.

The backend loads settings while modules are imported. These explicit dummy
values ensure test collection never reads developer or production credentials.
"""

import os
import sys
from pathlib import Path


os.environ["DATABASE_URL"] = "postgresql://scrooner_test:unused@127.0.0.1:9/scrooner_test"
os.environ["SUPABASE_URL"] = "https://scrooner-test.invalid"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-only-not-a-secret"
os.environ["SEC_USER_AGENT"] = "Scrooner test suite test@example.invalid"
# Same "fake, deliberately unreachable" pattern as DATABASE_URL above --
# cache.py reads REDIS_URL at import time (os.environ["REDIS_URL"], no
# default), so tests must never depend on a real Redis happening to be
# reachable (or not) from whatever machine runs them. Every test that
# actually exercises a cache read/write monkeypatches
# get_cached_result/set_cached_result, same discipline as get_connection.
os.environ["REDIS_URL"] = "redis://127.0.0.1:9/0"

# apps/backend is intentionally a thin application directory rather than an
# installed import package. Make that application root explicit for tests so
# `main`, `routers`, and `auth` resolve exactly as they do under uvicorn.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
