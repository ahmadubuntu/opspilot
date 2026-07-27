from __future__ import annotations

from collections.abc import Iterable

from opspilot.core.errors import ErrorCategory, ErrorDetail, ToolNotFoundError
from opspilot.core.tool import Tool, ToolDefinition


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        name = tool.definition.name
        if name in self._tools:
            raise ValueError(f"tool already registered: {name}")
        self._tools[name] = tool

    def register_many(self, tools: Iterable[Tool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(
                ErrorDetail(
                    category=ErrorCategory.TOOL_NOT_FOUND,
                    code="TOOL_NOT_FOUND",
                    message=f"Unknown tool: {name}",
                )
            ) from exc

    def definitions(self) -> tuple[ToolDefinition, ...]:
        return tuple(tool.definition for tool in self._tools.values())
