"""WPipe state that launches the Streamlit dashboard."""

import os
import subprocess
import sys
from typing import Any, Callable, Optional

from wpipe import step

from dto.ui_startup_context import UiStartupContext


def _default_runner(command: list[str]) -> int:
    """Run Streamlit in the foreground and return its exit code.

    Args:
        command: Full command line to execute.

    Returns:
        int: Process exit code.
    """
    return subprocess.call(command)  # noqa: S603


@step(
    name="LaunchStreamlit",
    version="v1.0",
    description="Serve the NeuralForge Cluster Admin Streamlit dashboard (blocking).",
    tags=["serve"],
)
class LaunchStreamlit:
    """Final blocking step that serves the Streamlit UI.

    Attributes:
        base_dir: Root directory of the UI service (added to PYTHONPATH).
        script_path: Path to the Streamlit entry script.
        runner: Callable used to execute the command (injectable for tests).
    """

    def __init__(
        self,
        script_path: Optional[str] = None,
        runner: Optional[Callable[[list[str]], int]] = None,
    ) -> None:
        """Configure the launcher.

        Args:
            script_path: Path to the Streamlit app; defaults to frontend/app.py.
            runner: Optional command runner; defaults to subprocess.call.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        self.script_path = script_path or os.path.join(base_dir, "frontend", "app.py")
        self.runner = runner or _default_runner

    def build_command(self, ctx: UiStartupContext) -> list[str]:
        """Build the Streamlit command line.

        Args:
            ctx: Current UI startup context.

        Returns:
            list[str]: Command line arguments.
        """
        return [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            self.script_path,
            "--server.port",
            str(ctx.port),
            "--server.address",
            ctx.address,
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ]

    def __call__(self, data: dict[str, Any]) -> dict[str, Any]:
        """Start Streamlit until the process is stopped.

        Args:
            data: Current pipeline context as a dictionary.

        Returns:
            dict[str, Any]: The context (returned after Streamlit exits).

        Raises:
            RuntimeError: If Streamlit exits with a non-zero code.
        """
        ctx = UiStartupContext(**data)
        os.environ["CLUSTER_API_URL"] = ctx.api_url
        python_path = os.environ.get("PYTHONPATH", "")
        if self.base_dir not in python_path.split(os.pathsep):
            os.environ["PYTHONPATH"] = os.pathsep.join(p for p in (self.base_dir, python_path) if p)
        print(f"[LaunchStreamlit] Serving {self.script_path} on {ctx.address}:{ctx.port}")
        exit_code = self.runner(self.build_command(ctx))
        if exit_code != 0:
            raise RuntimeError(f"Streamlit exited with code {exit_code}")
        return ctx.model_dump()
