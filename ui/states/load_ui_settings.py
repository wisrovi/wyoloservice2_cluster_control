"""WPipe state that resolves the runtime configuration of the UI service."""

import os
from typing import Any

from wpipe import step

from dto.ui_startup_context import UiStartupContext
from frontend import __version__


@step(
    name="LoadUiSettings",
    version="v1.0",
    description="Resolve API URL, Streamlit port and wait timeout from the environment.",
    tags=["config"],
)
class LoadUiSettings:
    """Loads the UI runtime configuration into the shared context."""

    def __call__(self, data: dict[str, Any]) -> dict[str, Any]:
        """Populate API URL, Streamlit bind settings and version.

        Args:
            data: Current pipeline context as a dictionary.

        Returns:
            dict[str, Any]: The updated context.
        """
        ctx = UiStartupContext(**data)
        ctx.api_url = os.getenv("CLUSTER_API_URL", ctx.api_url).rstrip("/")
        ctx.port = int(os.getenv("STREAMLIT_PORT", str(ctx.port)))
        ctx.address = os.getenv("STREAMLIT_ADDRESS", ctx.address)
        ctx.api_wait_seconds = int(os.getenv("API_WAIT_SECONDS", str(ctx.api_wait_seconds)))
        ctx.version = __version__
        print(f"[LoadUiSettings] UI v{ctx.version} -> {ctx.address}:{ctx.port} | API: {ctx.api_url}")
        return ctx.model_dump()
