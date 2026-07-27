from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from opspilot.core.errors import ErrorDetail


class ToolResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    request_id: UUID
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: ErrorDetail | None = None
    duration_ms: int = Field(ge=0)
