"""WPipe state that probes the Redis broker before the API starts serving."""

import time
from typing import Any

from wpipe import step

from backend.redis_client import get_redis_client
from dto.api_startup_context import ApiStartupContext


@step(
    name="CheckRedisConnection",
    version="v1.0",
    description="PING the Redis broker and record its latency (non-blocking on failure).",
    tags=["healthcheck"],
)
class CheckRedisConnection:
    """Verifies Redis connectivity without aborting startup when it is unavailable.

    The API must stay reachable even if Redis is temporarily down so that the
    UI can display a degraded health status instead of a connection error.
    """

    def __call__(self, data: dict[str, Any]) -> dict[str, Any]:
        """Ping Redis and store the result in the context.

        Args:
            data: Current pipeline context as a dictionary.

        Returns:
            dict[str, Any]: The updated context.
        """
        ctx = ApiStartupContext(**data)
        start = time.perf_counter()
        try:
            ctx.redis_ok = bool(get_redis_client().ping())
            ctx.redis_latency_ms = round((time.perf_counter() - start) * 1000, 2)
            print(f"[CheckRedisConnection] Redis OK ({ctx.redis_latency_ms} ms)")
        except Exception as exc:  # pylint: disable=broad-except
            ctx.redis_ok = False
            print(f"[CheckRedisConnection] Warning: Redis unreachable: {exc}")
        return ctx.model_dump()
