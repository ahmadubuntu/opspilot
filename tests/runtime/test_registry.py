import pytest

from opspilot.plugins.filesystem.tools import ReadFileTool
from opspilot.runtime.registry import ToolRegistry


def test_registry_rejects_duplicate_tool_names() -> None:
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    with pytest.raises(ValueError, match="already registered"):
        registry.register(ReadFileTool())
