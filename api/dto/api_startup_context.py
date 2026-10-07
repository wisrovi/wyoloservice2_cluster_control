"""Shared WPipe context for the API service startup pipeline."""

from typing import Optional

from pydantic import BaseModel, Field


class ApiStartupContext(BaseModel):
    """Typed state shared across every step of the API startup pipeline.

    Attributes:
        host: Network interface where Uvicorn binds.
        port: TCP port exposed by the FastAPI service.
        log_level: Uvicorn log level.
        redis_url: Redis connection URL resolved from the environment.
        redis_ok: Whether the Redis broker answered a PING.
        redis_latency_ms: Round-trip latency of the Redis PING in milliseconds.
        admin_seeded: Whether the default admin seeding routine was executed.
        version: Version of the API package being served.
    """

    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "info"
    redis_url: Optional[str] = None
    redis_ok: bool = False
    redis_latency_ms: Optional[float] = None
    admin_seeded: bool = False
    version: str = Field(default="unknown")
