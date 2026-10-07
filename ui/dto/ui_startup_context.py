"""Shared WPipe context for the UI service startup pipeline."""

from pydantic import BaseModel


class UiStartupContext(BaseModel):
    """Typed state shared across every step of the UI startup pipeline.

    Attributes:
        api_url: Base URL of the Cluster Admin API consumed by the UI.
        port: TCP port exposed by Streamlit.
        address: Network interface where Streamlit binds.
        api_wait_seconds: Maximum time to wait for the API health endpoint.
        api_ready: Whether the API answered its health endpoint in time.
        version: Version of the UI package being served.
    """

    api_url: str = "http://localhost:8001"
    port: int = 8501
    address: str = "0.0.0.0"
    api_wait_seconds: int = 60
    api_ready: bool = False
    version: str = "unknown"
