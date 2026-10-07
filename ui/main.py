"""Entrypoint of the NeuralForge Cluster Admin UI service (WPipe orchestrated).

Pipeline: LoadUiSettings -> WaitForApi -> LaunchStreamlit
"""

import os
from typing import Any, Optional

from wpipe import Pipeline

from frontend import __version__
from states import LaunchStreamlit, LoadUiSettings, WaitForApi


def build_pipeline(
    wait_step: Optional[WaitForApi] = None,
    launch_step: Optional[LaunchStreamlit] = None,
) -> Pipeline:
    """Build the UI startup pipeline.

    Args:
        wait_step: Optional custom API wait step (used by tests).
        launch_step: Optional custom launcher step (used by tests).

    Returns:
        Pipeline: Configured WPipe pipeline.
    """
    pipeline = Pipeline(
        pipeline_name="cluster_admin_ui",
        pipeline_version=__version__,
        tracking_db=os.getenv("WPIPE_TRACKING_DB") or None,
        show_progress=False,
        verbose=False,
        max_retries=0,
    )
    pipeline.set_steps(
        [
            LoadUiSettings(),
            wait_step or WaitForApi(),
            launch_step or LaunchStreamlit(),
        ]
    )
    return pipeline


def main() -> dict[str, Any]:
    """Run the UI startup pipeline.

    Returns:
        dict[str, Any]: Final pipeline context (after Streamlit exits).
    """
    print(f"=== NeuralForge Cluster Admin UI v{__version__} (WPipe) ===")
    return build_pipeline().run({})


if __name__ == "__main__":
    main()
