"""WPipe state that resolves the runtime configuration of the API service."""

import os
from typing import Any

from wpipe import step

from backend import __version__
from backend.config import settings
from dto.api_startup_context import ApiStartupContext


@step(
    name="LoadApiSettings",
    version="v1.0",
    description="Resolve bind address, port and Redis URL from the environment.",
    tags=["config"],
)
class LoadApiSettings:
    """Loads the API runtime configuration into the shared context."""

    def __call__(self, data: dict[str, Any]) -> dict[str, Any]:
        """Populate host, port, log level, Redis URL and version.

        Args:
            data: Current pipeline context as a dictionary.

        Returns:
            dict[str, Any]: The updated context.
        """
        ctx = ApiStartupContext(**data)
        ctx.host = os.getenv("API_HOST", ctx.host)
        ctx.port = int(os.getenv("API_PORT", str(ctx.port)))
        ctx.log_level = os.getenv("API_LOG_LEVEL", ctx.log_level)
        ctx.redis_url = settings.REDIS_URL
        ctx.version = __version__
        safe_url = ctx.redis_url.split("@")[-1]
        print(f"[LoadApiSettings] API v{ctx.version} -> {ctx.host}:{ctx.port} | Redis: {safe_url}")
        return ctx.model_dump()
