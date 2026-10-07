"""Entrypoint of the NeuralForge Cluster Admin API service (WPipe orchestrated).

Pipeline: LoadApiSettings -> CheckRedisConnection -> SeedAdminUser -> ServeApi
"""

import os
from typing import Any, Optional

from wpipe import Pipeline

from backend import __version__
from states import CheckRedisConnection, LoadApiSettings, SeedAdminUser, ServeApi


def build_pipeline(serve_step: Optional[ServeApi] = None) -> Pipeline:
    """Build the API startup pipeline.

    Args:
        serve_step: Optional custom serving step (used by tests to avoid blocking).

    Returns:
        Pipeline: Configured WPipe pipeline.
    """
    pipeline = Pipeline(
        pipeline_name="cluster_admin_api",
        pipeline_version=__version__,
        tracking_db=os.getenv("WPIPE_TRACKING_DB") or None,
        show_progress=False,
        verbose=False,
        max_retries=0,
    )
    pipeline.set_steps(
        [
            LoadApiSettings(),
            CheckRedisConnection(),
            SeedAdminUser(),
            serve_step or ServeApi(),
        ]
    )
    return pipeline


def main() -> dict[str, Any]:
    """Run the API startup pipeline.

    Returns:
        dict[str, Any]: Final pipeline context (after the server stops).
    """
    print(f"=== NeuralForge Cluster Admin API v{__version__} (WPipe) ===")
    return build_pipeline().run({})


if __name__ == "__main__":
    main()
