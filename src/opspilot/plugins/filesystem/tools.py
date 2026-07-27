from __future__ import annotations

from pydantic import BaseModel

from opspilot.core.permissions import Permission
from opspilot.core.risk import RiskClass
from opspilot.core.tool import Tool, ToolDefinition
from opspilot.plugins.filesystem.models import (
    DirectoryEntryOutput,
    ListDirectoryInput,
    ListDirectoryOutput,
    ReadFileInput,
    ReadFileOutput,
)
from opspilot.runtime.context import ExecutionContext


class ReadFileTool(Tool):
    definition = ToolDefinition(
        name="filesystem.read_file",
        description="Read a UTF-8 text file inside the active workspace.",
        input_model=ReadFileInput,
        output_model=ReadFileOutput,
        risk=RiskClass.READ,
        permissions=frozenset({Permission.WORKSPACE_READ}),
    )

    async def execute(self, context: ExecutionContext, arguments: BaseModel) -> BaseModel:
        assert isinstance(arguments, ReadFileInput)
        return ReadFileOutput(content=await context.workspace.read_text(arguments.path))


class ListDirectoryTool(Tool):
    definition = ToolDefinition(
        name="filesystem.list_directory",
        description="List entries inside a directory in the active workspace.",
        input_model=ListDirectoryInput,
        output_model=ListDirectoryOutput,
        risk=RiskClass.READ,
        permissions=frozenset({Permission.WORKSPACE_READ}),
    )

    async def execute(self, context: ExecutionContext, arguments: BaseModel) -> BaseModel:
        assert isinstance(arguments, ListDirectoryInput)
        entries = await context.workspace.list_directory(arguments.path)
        return ListDirectoryOutput(
            entries=[
                DirectoryEntryOutput(name=item.name, is_directory=item.is_directory)
                for item in entries
            ]
        )
