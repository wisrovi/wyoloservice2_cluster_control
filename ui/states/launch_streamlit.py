"""WPipe state that launches the NeuralForge VSCode Workbench server.

Preserves backwards compatibility with LaunchStreamlit references.
"""

from states.launch_workbench import LaunchWorkbench

# Backward-compatible alias
LaunchStreamlit = LaunchWorkbench

__all__ = ["LaunchWorkbench", "LaunchStreamlit"]
