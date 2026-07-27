from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from opspilot.core.permissions import Permission
from opspilot.core.risk import RiskClass


if TYPE_CHECKING:
    from opspilot.runtime.context import ExecutionContext


class EmptyInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class EmptyOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ToolDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    name: str = Field(pattern=r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")
    description: str = Field(min_length=1)
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    risk: RiskClass
    permissions: frozenset[Permission] = Field(default_factory=frozenset)
    mutates: bool = False
    supports_dry_run: bool = False
    timeout_seconds: int = Field(default=60, ge=1, le=3600)


class Tool(ABC):
    definition: ClassVar[ToolDefinition]

    @abstractmethod
    async def execute(self, context: "ExecutionContext", arguments: BaseModel) -> BaseModel:
        raise NotImplementedError

