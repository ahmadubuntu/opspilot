from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from opspilot.core.risk import RiskClass
from opspilot.core.tool import ToolDefinition
from opspilot.runtime.context import ExecutionContext
from opspilot.runtime.requests import ToolRequest


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    REQUIRE_DRY_RUN = "require_dry_run"


class PolicyEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    decision: PolicyDecision
    reason: str
    matched_policy: str | None = None


class PolicyEngine(ABC):
    @abstractmethod
    async def evaluate(
        self,
        context: ExecutionContext,
        request: ToolRequest,
        tool: ToolDefinition,
    ) -> PolicyEvaluation:
        raise NotImplementedError


class DefaultPolicyEngine(PolicyEngine):
    async def evaluate(
        self,
        context: ExecutionContext,
        request: ToolRequest,
        tool: ToolDefinition,
    ) -> PolicyEvaluation:
        del context, request
        if tool.risk is RiskClass.READ:
            return PolicyEvaluation(decision=PolicyDecision.ALLOW, reason="read-only tool")
        if tool.risk in {RiskClass.CLUSTER_MUTATE, RiskClass.REMOTE_EXEC}:
            return PolicyEvaluation(
                decision=PolicyDecision.REQUIRE_APPROVAL,
                reason="high-risk operation requires explicit approval",
            )
        if tool.mutates or tool.risk in {RiskClass.WRITE_WORKSPACE, RiskClass.EXEC, RiskClass.SYSTEM}:
            return PolicyEvaluation(
                decision=PolicyDecision.REQUIRE_APPROVAL,
                reason="mutating or executable operation requires approval",
            )
        return PolicyEvaluation(decision=PolicyDecision.DENY, reason="unknown risk classification")
