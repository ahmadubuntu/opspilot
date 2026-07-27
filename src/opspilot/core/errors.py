from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorCategory(StrEnum):
    VALIDATION = "validation"
    POLICY_DENIED = "policy_denied"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_REJECTED = "approval_rejected"
    TOOL_NOT_FOUND = "tool_not_found"
    TOOL_EXECUTION = "tool_execution"
    TRANSPORT = "transport"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    INTERNAL = "internal"


class ErrorDetail(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    category: ErrorCategory
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class OpsPilotError(Exception):
    def __init__(self, detail: ErrorDetail) -> None:
        super().__init__(detail.message)
        self.detail = detail


class ToolNotFoundError(OpsPilotError):
    pass


class PolicyDeniedError(OpsPilotError):
    pass


class ApprovalRejectedError(OpsPilotError):
    pass


class WorkspaceViolationError(OpsPilotError):
    pass
