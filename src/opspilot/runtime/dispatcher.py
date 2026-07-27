from __future__ import annotations

from pydantic import ValidationError

from opspilot.core.tool import Tool
from opspilot.runtime.context import ExecutionContext
from opspilot.runtime.registry import ToolRegistry
from opspilot.runtime.requests import ToolRequest


class Dispatcher:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def resolve(self, tool_name: str) -> Tool:
        return self._registry.get(tool_name)

    async def dispatch(self, context: ExecutionContext, request: ToolRequest) -> object:
        tool = self.resolve(request.tool_name)
        try:
            arguments = tool.definition.input_model.model_validate(request.arguments)
        except ValidationError:
            raise
        return await tool.execute(context, arguments)
