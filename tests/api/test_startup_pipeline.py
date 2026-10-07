"""Unit tests for the API WPipe startup pipeline (dto/, states/, main.py).

This module validates:
1. LoadApiSettings resolves host, port, log level, Redis URL and version from the environment.
2. CheckRedisConnection records success/latency and degrades gracefully when Redis fails.
3. SeedAdminUser only seeds the admin account when Redis is reachable.
4. ServeApi delegates to the injected runner with the resolved bind settings.
5. The full pipeline built by main.build_pipeline runs every step in order without blocking.
"""

from typing import Any

import pytest

import main as api_main
from backend import __version__
from dto import ApiStartupContext
from states import CheckRedisConnection, LoadApiSettings, SeedAdminUser, ServeApi
from states import check_redis_connection as redis_state_module
from states import seed_admin_user as seed_state_module


class _FakeRedis:
    """Minimal Redis double whose PING result is configurable."""

    def __init__(self, ok: bool = True, fail: bool = False) -> None:
        self.ok = ok
        self.fail = fail

    def ping(self) -> bool:
        """Return the configured PING result or raise a connection error."""
        if self.fail:
            raise ConnectionError("redis down")
        return self.ok


def test_context_defaults() -> None:
    """Validates that the DTO exposes safe defaults for an empty pipeline input.

    What it tests:
    - Building the context from an empty dict works (pipeline starts with {}).
    - Port defaults to 8001 and Redis is considered unhealthy until probed.
    """
    ctx = ApiStartupContext()
    assert ctx.port == 8001
    assert ctx.redis_ok is False
    assert ctx.admin_seeded is False


def test_load_api_settings_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates environment-driven configuration of the API service.

    What it tests:
    - API_HOST, API_PORT and API_LOG_LEVEL override the defaults.
    - The Redis URL and package version are injected into the context.
    """
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("API_PORT", "9100")
    monkeypatch.setenv("API_LOG_LEVEL", "warning")
    out = LoadApiSettings()({})
    assert out["host"] == "127.0.0.1"
    assert out["port"] == 9100
    assert out["log_level"] == "warning"
    assert out["redis_url"].startswith("redis://")
    assert out["version"] == __version__


def test_check_redis_connection_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates that a healthy Redis is flagged as reachable with a latency value.

    What it tests:
    - redis_ok becomes True and redis_latency_ms is a non-negative float.
    """
    monkeypatch.setattr(redis_state_module, "get_redis_client", lambda: _FakeRedis(ok=True))
    out = CheckRedisConnection()({})
    assert out["redis_ok"] is True
    assert out["redis_latency_ms"] >= 0


def test_check_redis_connection_failure_is_non_fatal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates graceful degradation when Redis is unreachable.

    What it tests:
    - A connection error does not raise; redis_ok is simply False so the API
      can still start and report a degraded health status to the UI.
    """
    monkeypatch.setattr(redis_state_module, "get_redis_client", lambda: _FakeRedis(fail=True))
    out = CheckRedisConnection()({})
    assert out["redis_ok"] is False
    assert out["redis_latency_ms"] is None


@pytest.mark.parametrize("redis_ok, expected_calls", [(True, 1), (False, 0)])
def test_seed_admin_user_depends_on_redis(
    monkeypatch: pytest.MonkeyPatch, redis_ok: bool, expected_calls: int
) -> None:
    """Validates that admin seeding only runs when Redis answered the probe.

    What it tests:
    - With redis_ok=True the seeding routine is invoked exactly once.
    - With redis_ok=False the routine is skipped and admin_seeded stays False.
    """
    calls: list[int] = []
    monkeypatch.setattr(seed_state_module, "seed_default_admin", lambda: calls.append(1))
    out = SeedAdminUser()({"redis_ok": redis_ok})
    assert len(calls) == expected_calls
    assert out["admin_seeded"] is redis_ok


def test_serve_api_uses_injected_runner() -> None:
    """Validates that ServeApi forwards the resolved bind settings to the runner.

    What it tests:
    - The runner receives the ASGI path, host, port and log level from the context.
    """
    received: list[tuple[Any, ...]] = []
    step = ServeApi(runner=lambda *args: received.append(args))
    step({"host": "0.0.0.0", "port": 8123, "log_level": "debug"})
    assert received == [("backend.app:app", "0.0.0.0", 8123, "debug")]


def test_full_pipeline_runs_all_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates the end-to-end WPipe orchestration defined in main.py.

    What it tests:
    - build_pipeline wires LoadApiSettings -> CheckRedisConnection -> SeedAdminUser -> ServeApi.
    - Running it with a non-blocking runner produces a final context where Redis
      is healthy, the admin was seeded and the server runner was invoked once.
    """
    monkeypatch.setattr(redis_state_module, "get_redis_client", lambda: _FakeRedis(ok=True))
    monkeypatch.setattr(seed_state_module, "seed_default_admin", lambda: None)
    served: list[tuple[Any, ...]] = []
    pipeline = api_main.build_pipeline(serve_step=ServeApi(runner=lambda *a: served.append(a)))
    result = pipeline.run({})
    assert len(served) == 1
    assert result.get("redis_ok") is True
    assert result.get("admin_seeded") is True
