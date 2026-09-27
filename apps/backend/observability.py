"""Low-cardinality, content-free API request observability.

Every request receives a server-generated correlation ID. Structured events
and the in-process snapshot deliberately contain only method, route template,
status, and duration; query strings, request bodies, authorization headers,
and user identifiers are never recorded here.

The snapshot is useful for a single-process private beta and deterministic
health checks. Structured request events remain the durable integration point
for a deployment log/metrics backend and avoid pretending that process-local
counters are a multi-worker time-series store.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from time import perf_counter
from typing import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import Request, Response

logger = structlog.get_logger("scrooner.api")


@dataclass
class _RequestBucket:
    count: int = 0
    client_errors: int = 0
    server_errors: int = 0
    total_duration_ms: float = 0.0
    max_duration_ms: float = 0.0

    def observe(self, status_code: int, duration_ms: float) -> None:
        self.count += 1
        self.client_errors += 400 <= status_code < 500
        self.server_errors += status_code >= 500
        self.total_duration_ms += duration_ms
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)

    def snapshot(self) -> dict:
        return {
            "count": self.count,
            "client_errors": self.client_errors,
            "server_errors": self.server_errors,
            "server_error_rate": round(self.server_errors / self.count, 6)
            if self.count
            else 0.0,
            "latency_ms": {
                "average": round(self.total_duration_ms / self.count, 3)
                if self.count
                else 0.0,
                "maximum": round(self.max_duration_ms, 3),
            },
        }


class ApiRequestMetrics:
    """Thread-safe, process-local request counters grouped by route template."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._started_at = datetime.now(timezone.utc)
            self._total = _RequestBucket()
            self._endpoints: dict[tuple[str, str], _RequestBucket] = {}

    def observe(
        self, method: str, endpoint: str, status_code: int, duration_ms: float
    ) -> None:
        key = (method.upper(), endpoint)
        with self._lock:
            self._total.observe(status_code, duration_ms)
            self._endpoints.setdefault(key, _RequestBucket()).observe(
                status_code, duration_ms
            )

    def snapshot(self) -> dict:
        with self._lock:
            endpoints = [
                {"method": method, "endpoint": endpoint, **bucket.snapshot()}
                for (method, endpoint), bucket in sorted(self._endpoints.items())
            ]
            return {
                "scope": "single_process_since_start",
                "started_at": self._started_at.isoformat(),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "requests": self._total.snapshot(),
                "endpoints": endpoints,
            }


api_request_metrics = ApiRequestMetrics()


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    template = getattr(route, "path", None)
    return template if isinstance(template, str) else "<unmatched>"


async def observe_http_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """FastAPI middleware implementation kept separate for direct testing."""
    request_id = str(uuid4())
    request.state.request_id = request_id
    started = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        duration_ms = (perf_counter() - started) * 1000
        endpoint = _route_template(request)
        api_request_metrics.observe(request.method, endpoint, status_code, duration_ms)
        logger.info(
            "api.request.completed",
            request_id=request_id,
            method=request.method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=round(duration_ms, 3),
        )
