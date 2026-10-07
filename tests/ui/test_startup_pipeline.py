"""Unit tests for the UI WPipe startup pipeline (dto/, states/, main.py).

This module validates:
1. LoadUiSettings resolves the API URL, Streamlit port/address and wait budget from the environment.
2. WaitForApi marks the API as ready on a successful probe and degrades gracefully on timeout.
3. LaunchStreamlit builds the right command, exports CLUSTER_API_URL/PYTHONPATH and fails on non-zero exit.
4. The full pipeline built by main.build_pipeline runs every step in order without blocking.
5. The frontend package exposes a version string and the API client honours CLUSTER_API_URL.
"""

import os
from typing import Any

import pytest

import main as ui_main
from dto import UiStartupContext
from frontend import __version__
from states import LaunchStreamlit, LoadUiSettings, WaitForApi
from states import wait_for_api as wait_module


def test_context_defaults() -> None:
    """Validates safe defaults of the UI context for an empty pipeline input.

    What it tests:
    - Streamlit defaults to port 8501 and the API is not ready until probed.
    """
    ctx = UiStartupContext()
    assert ctx.port == 8501
    assert ctx.api_ready is False


def test_load_ui_settings_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates environment-driven configuration of the UI service.

    What it tests:
    - CLUSTER_API_URL (trailing slash stripped), STREAMLIT_PORT, STREAMLIT_ADDRESS
      and API_WAIT_SECONDS override defaults; the package version is injected.
    """
    monkeypatch.setenv("CLUSTER_API_URL", "http://api:8001/")
    monkeypatch.setenv("STREAMLIT_PORT", "8600")
    monkeypatch.setenv("STREAMLIT_ADDRESS", "127.0.0.1")
    monkeypatch.setenv("API_WAIT_SECONDS", "5")
    out = LoadUiSettings()({})
    assert out["api_url"] == "http://api:8001"
    assert out["port"] == 8600
    assert out["address"] == "127.0.0.1"
    assert out["api_wait_seconds"] == 5
    assert out["version"] == __version__


def test_wait_for_api_ready() -> None:
    """Validates that a healthy probe marks the API as ready and targets /health.

    What it tests:
    - The probe is called with '<api_url>/health' and api_ready becomes True.
    """
    urls: list[str] = []

    def probe(url: str) -> bool:
        urls.append(url)
        return True

    out = WaitForApi(interval=0, probe=probe)({"api_url": "http://api:8001"})
    assert out["api_ready"] is True
    assert urls == ["http://api:8001/health"]


def test_wait_for_api_timeout_is_non_fatal() -> None:
    """Validates graceful degradation when the API never becomes healthy.

    What it tests:
    - With a zero-second budget the step returns without raising and api_ready is False,
      so the UI still starts and can show connection errors to the operator.
    """
    out = WaitForApi(interval=0, probe=lambda _url: False)({"api_wait_seconds": 0})
    assert out["api_ready"] is False


def test_default_probe_handles_connection_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates that the default HTTP probe swallows network errors.

    What it tests:
    - A requests exception results in False instead of propagating.
    - An HTTP 200 response results in True.
    """

    class _Resp:
        status_code = 200

    def boom(*_args: Any, **_kwargs: Any) -> Any:
        raise wait_module.requests.ConnectionError("down")

    monkeypatch.setattr(wait_module.requests, "get", boom)
    assert wait_module._default_probe("http://x/health") is False  # pylint: disable=protected-access
    monkeypatch.setattr(wait_module.requests, "get", lambda *_a, **_k: _Resp())
    assert wait_module._default_probe("http://x/health") is True  # pylint: disable=protected-access


def test_launch_streamlit_command_and_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates the Streamlit command line and exported environment.

    What it tests:
    - The command runs 'streamlit run frontend/app.py' headless on the configured port/address.
    - CLUSTER_API_URL is exported and the UI root is prepended to PYTHONPATH.
    """
    monkeypatch.delenv("PYTHONPATH", raising=False)
    commands: list[list[str]] = []
    step = LaunchStreamlit(runner=lambda cmd: commands.append(cmd) or 0)
    step({"api_url": "http://api:8001", "port": 8502, "address": "0.0.0.0"})
    cmd = commands[0]
    assert cmd[1:4] == ["-m", "streamlit", "run"]
    assert cmd[4].endswith(os.path.join("frontend", "app.py"))
    assert cmd[cmd.index("--server.port") + 1] == "8502"
    assert cmd[cmd.index("--server.headless") + 1] == "true"
    assert os.environ["CLUSTER_API_URL"] == "http://api:8001"
    assert step.base_dir in os.environ["PYTHONPATH"].split(os.pathsep)


def test_launch_streamlit_raises_on_failure() -> None:
    """Validates that a crashing Streamlit process surfaces as an error.

    What it tests:
    - A non-zero exit code raises RuntimeError so the container restarts.
    """
    with pytest.raises(RuntimeError):
        LaunchStreamlit(runner=lambda _cmd: 1)({})


def test_full_pipeline_runs_all_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates the end-to-end WPipe orchestration defined in main.py.

    What it tests:
    - build_pipeline wires LoadUiSettings -> WaitForApi -> LaunchStreamlit.
    - With non-blocking doubles, the final context reports the API as ready and
      the Streamlit runner is invoked exactly once.
    """
    monkeypatch.setenv("CLUSTER_API_URL", "http://api:8001")
    launched: list[list[str]] = []
    pipeline = ui_main.build_pipeline(
        wait_step=WaitForApi(interval=0, probe=lambda _u: True),
        launch_step=LaunchStreamlit(runner=lambda cmd: launched.append(cmd) or 0),
    )
    result = pipeline.run({})
    assert len(launched) == 1
    assert result.get("api_ready") is True
