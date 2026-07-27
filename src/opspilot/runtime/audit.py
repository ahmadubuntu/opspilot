from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AuditEventType(StrEnum):
    REQUEST_RECEIVED = "request_received"
    POLICY_DECIDED = "policy_decided"
    APPROVAL_RESOLVED = "approval_resolved"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"


class AuditEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    event_type: AuditEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: UUID
    request_id: UUID
    tool_name: str
    payload: dict[str, Any] = Field(default_factory=dict)


class AuditSink(ABC):
    @abstractmethod
    async def append(self, event: AuditEvent) -> None:
        raise NotImplementedError


class InMemoryAuditSink(AuditSink):
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    async def append(self, event: AuditEvent) -> None:
        self._events.append(event)

    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)
