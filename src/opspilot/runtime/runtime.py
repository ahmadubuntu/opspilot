from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, ValidationError

from opspilot.core.errors import (
    ApprovalRejectedError,
    ErrorCategory,
    ErrorDetail,
    OpsPilotError,
    PolicyDeniedError,
)
from opspilot.runtime.approval import ApprovalProvider, ApprovalStatus
from opspilot.runtime.audit import AuditEvent, AuditEventType, AuditSink
from opspilot.runtime.context import ExecutionContext
from opspilot.runtime.dispatcher import Dispatcher
from opspilot.runtime.policy import PolicyDecision, PolicyEngine
from opspilot.runtime.requests import ToolRequest
from opspilot.runtime.results import ToolResult


class Runtime:
    def __init__(
        self,
        *,
        dispatcher: Dispatcher,
        policy: PolicyEngine,
        approval: ApprovalProvider,
        audit: AuditSink,
    ) -> None:
        self._dispatcher = dispatcher
        self._policy = policy
        self._approval = approval
        self._audit = audit

    async def execute(self, context: ExecutionContext, request: ToolRequest) -> ToolResult:
        started = time.perf_counter()
        await self._record(AuditEventType.REQUEST_RECEIVED, context, request)
        tool = self._dispatcher.resolve(request.tool_name)

        evaluation = await self._policy.evaluate(context, request, tool.definition)
        await self._record(
            AuditEventType.POLICY_DECIDED,
            context,
            request,
            {"decision": evaluation.decision.value, "reason": evaluation.reason},
        )

        if evaluation.decision is PolicyDecision.DENY:
            error = ErrorDetail(
                category=ErrorCategory.POLICY_DENIED,
                code="POLICY_DENIED",
                message=evaluation.reason,
            )
            await self._record(AuditEventType.TOOL_FAILED, context, request, error.model_dump(mode="json"))
            raise PolicyDeniedError(error)

        if evaluation.decision in {PolicyDecision.REQUIRE_APPROVAL, PolicyDecision.REQUIRE_DRY_RUN}:
            approval = await self._approval.request(context, request, tool.definition)
            await self._record(
                AuditEventType.APPROVAL_RESOLVED,
                context,
                request,
                {"status": approval.status.value, "reason": approval.reason},
            )
            if approval.status is not ApprovalStatus.APPROVED:
                error = ErrorDetail(
                    category=ErrorCategory.APPROVAL_REJECTED,
                    code="APPROVAL_REJECTED",
                    message=approval.reason or "Execution was not approved",
                )
                raise ApprovalRejectedError(error)

        await self._record(AuditEventType.TOOL_STARTED, context, request)
        try:
            raw_output = await self._dispatcher.dispatch(context, request)
            output = self._serialize_output(raw_output)
            result = ToolResult(
                request_id=request.request_id,
                success=True,
                output=output,
                duration_ms=self._duration_ms(started),
            )
            await self._record(AuditEventType.TOOL_COMPLETED, context, request, {"duration_ms": result.duration_ms})
            return result
        except ValidationError as exc:
            error = ErrorDetail(
                category=ErrorCategory.VALIDATION,
                code="INVALID_TOOL_ARGUMENTS",
                message="Tool arguments failed validation",
                details={"errors": exc.errors(include_url=False)},
            )
            await self._record(AuditEventType.TOOL_FAILED, context, request, error.model_dump(mode="json"))
            return ToolResult(
                request_id=request.request_id,
                success=False,
                error=error,
                duration_ms=self._duration_ms(started),
            )
        except OpsPilotError as exc:
            await self._record(AuditEventType.TOOL_FAILED, context, request, exc.detail.model_dump(mode="json"))
            raise
        except Exception as exc:
            error = ErrorDetail(
                category=ErrorCategory.TOOL_EXECUTION,
                code="TOOL_EXECUTION_FAILED",
                message=str(exc) or exc.__class__.__name__,
            )
            await self._record(AuditEventType.TOOL_FAILED, context, request, error.model_dump(mode="json"))
            return ToolResult(
                request_id=request.request_id,
                success=False,
                error=error,
                duration_ms=self._duration_ms(started),
            )

    async def _record(
        self,
        event_type: AuditEventType,
        context: ExecutionContext,
        request: ToolRequest,
        payload: dict[str, Any] | None = None,
    ) -> None:
        await self._audit.append(
            AuditEvent(
                event_type=event_type,
                session_id=context.session.id,
                request_id=request.request_id,
                tool_name=request.tool_name,
                payload=payload or {},
            )
        )

    @staticmethod
    def _serialize_output(output: object) -> dict[str, Any]:
        if isinstance(output, BaseModel):
            return output.model_dump(mode="json")
        if isinstance(output, dict):
            return {str(key): value for key, value in output.items()}
        return {"value": output}

    @staticmethod
    def _duration_ms(started: float) -> int:
        return max(0, int((time.perf_counter() - started) * 1000))
