"""WPipe state that launches the FastAPI application with Uvicorn."""

from typing import Any, Callable, Optional

from wpipe import step

from dto.api_startup_context import ApiStartupContext


def _default_runner(app_path: str, host: str, port: int, log_level: str) -> None:
    """Start Uvicorn in the foreground.

    Args:
        app_path: Import path of the ASGI application.
        host: Bind address.
        port: Bind port.
        log_level: Uvicorn log level.
    """
    import uvicorn  # pylint: disable=import-outside-toplevel

    uvicorn.run(app_path, host=host, port=port, log_level=log_level)


@step(
    name="ServeApi",
    version="v1.0",
    description="Serve the NeuralForge Cluster Admin FastAPI app (blocking).",
    tags=["serve"],
)
class ServeApi:
    """Final blocking step that serves the REST API.

    Attributes:
        app_path: Import path of the ASGI application.
        runner: Callable used to start the server (injectable for tests).
    """

    def __init__(
        self,
        app_path: str = "backend.app:app",
        runner: Optional[Callable[[str, str, int, str], None]] = None,
    ) -> None:
        """Configure the server step.

        Args:
            app_path: Import path of the ASGI application.
            runner: Optional server runner; defaults to Uvicorn.
        """
        self.app_path = app_path
        self.runner = runner or _default_runner

    def __call__(self, data: dict[str, Any]) -> dict[str, Any]:
        """Start serving the API until the process is stopped.

        Args:
            data: Current pipeline context as a dictionary.

        Returns:
            dict[str, Any]: The context (returned after the server stops).
        """
        ctx = ApiStartupContext(**data)
        print(f"[ServeApi] Serving {self.app_path} on {ctx.host}:{ctx.port}")
        self.runner(self.app_path, ctx.host, ctx.port, ctx.log_level)
        return ctx.model_dump()
