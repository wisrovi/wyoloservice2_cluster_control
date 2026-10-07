"""WPipe state that waits until the Cluster Admin API is healthy."""

import time
from typing import Any, Callable, Optional

import requests
from wpipe import step

from dto.ui_startup_context import UiStartupContext


def _default_probe(url: str) -> bool:
    """Return True when the API health endpoint answers HTTP 200.

    Args:
        url: Full URL of the health endpoint.

    Returns:
        bool: Whether the API is healthy.
    """
    try:
        return requests.get(url, timeout=3).status_code == 200
    except requests.RequestException:
        return False


@step(
    name="WaitForApi",
    version="v1.0",
    description="Poll the API /health endpoint until it is ready or the timeout expires.",
    tags=["healthcheck"],
)
class WaitForApi:
    """Waits for the backend before serving the UI (non-fatal on timeout).

    Attributes:
        interval: Seconds between probes.
        probe: Callable that checks the health URL (injectable for tests).
    """

    def __init__(
        self,
        interval: float = 2.0,
        probe: Optional[Callable[[str], bool]] = None,
    ) -> None:
        """Configure the wait step.

        Args:
            interval: Seconds between probes.
            probe: Optional custom health probe.
        """
        self.interval = interval
        self.probe = probe or _default_probe

    def __call__(self, data: dict[str, Any]) -> dict[str, Any]:
        """Poll the API until healthy or until the wait budget is exhausted.

        Args:
            data: Current pipeline context as a dictionary.

        Returns:
            dict[str, Any]: The updated context.
        """
        ctx = UiStartupContext(**data)
        health_url = f"{ctx.api_url}/health"
        deadline = time.monotonic() + ctx.api_wait_seconds
        while True:
            if self.probe(health_url):
                ctx.api_ready = True
                print(f"[WaitForApi] API is healthy at {health_url}")
                break
            if time.monotonic() >= deadline:
                print(f"[WaitForApi] Warning: API not ready after {ctx.api_wait_seconds}s; starting UI anyway.")
                break
            time.sleep(self.interval)
        return ctx.model_dump()
