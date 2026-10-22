"""Entrypoint of the NeuralForge Cluster Admin UI service (WPipe orchestrated).

Pipeline: LoadUiSettings -> WaitForApi -> LaunchWorkbench
"""

import os
from typing import Any, Optional

from wpipe import Pipeline

from frontend import __version__
from states import LaunchWorkbench, LoadUiSettings, WaitForApi


def build_pipeline(
    wait_step: Optional[WaitForApi] = None,
    launch_step: Optional[LaunchWorkbench] = None,
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
            launch_step or LaunchWorkbench(),
        ]
    )
    return pipeline


def main() -> dict[str, Any]:
    """Run the UI startup pipeline.

    Returns:
        dict[str, Any]: Final pipeline context (after workbench exits).
    """
    print(f"=== NeuralForge Cluster Admin VSCode Workbench UI v{__version__} (WPipe) ===")
    return build_pipeline().run({})


if __name__ == "__main__":
    main()
