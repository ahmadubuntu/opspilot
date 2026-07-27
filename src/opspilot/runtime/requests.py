from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ToolRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    request_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    target: str = "local"
