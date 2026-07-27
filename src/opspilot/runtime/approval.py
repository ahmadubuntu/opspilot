from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from opspilot.core.tool import ToolDefinition
from opspilot.runtime.context import ExecutionContext
from opspilot.runtime.requests import ToolRequest


class ApprovalStatus(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: ApprovalStatus
    reason: str = ""


class ApprovalProvider(ABC):
    @abstractmethod
    async def request(
        self,
        context: ExecutionContext,
        request: ToolRequest,
        tool: ToolDefinition,
    ) -> ApprovalResult:
        raise NotImplementedError


class DenyApprovalProvider(ApprovalProvider):
    async def request(
        self,
        context: ExecutionContext,
        request: ToolRequest,
        tool: ToolDefinition,
    ) -> ApprovalResult:
        del context, request, tool
        return ApprovalResult(status=ApprovalStatus.REJECTED, reason="no approval UI configured")
