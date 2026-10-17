import logging
from time import monotonic
from uuid import uuid4

logger = logging.getLogger("cockpit.request")


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get("X-Request-ID") or str(uuid4())
        started = monotonic()
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        logger.info(
            "request.completed request_id=%s method=%s path=%s status=%s duration_ms=%.1f actor=%s",
            request.request_id,
            request.method,
            request.path,
            response.status_code,
            (monotonic() - started) * 1000,
            request.user.pk if getattr(request, "user", None) and request.user.is_authenticated else "anonymous",
        )
        return response
