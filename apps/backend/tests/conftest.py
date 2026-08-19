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

# apps/backend is intentionally a thin application directory rather than an
# installed import package. Make that application root explicit for tests so
# `main`, `routers`, and `auth` resolve exactly as they do under uvicorn.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
