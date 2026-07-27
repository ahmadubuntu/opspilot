from __future__ import annotations

from opspilot.core.tool import Tool, ToolDefinition


class ToolRegistry:
    """
    Stores registered tools by their unique qualified names.

    The registry owns tool lookup and duplicate-name detection.
    It does not execute tools or evaluate policy.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool.

        Raises:
            ValueError: If another tool already uses the same name.
        """

        name = tool.definition.name

        if name in self._tools:
            raise ValueError(
                f"Tool '{name}' is already registered.",
            )

        self._tools[name] = tool

    def get(self, name: str) -> Tool:
        """
        Return a registered tool by name.

        Raises:
            KeyError: If the requested tool does not exist.
        """

        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown tool: '{name}'.",
            ) from exc

    def contains(self, name: str) -> bool:
        """
        Return whether a tool name is registered.
        """

        return name in self._tools

    def list(self) -> tuple[ToolDefinition, ...]:
        """
        Return immutable definitions for all registered tools.
        """

        return tuple(
            tool.definition
            for tool in self._tools.values()
        )

    def __len__(self) -> int:
        return len(self._tools)
