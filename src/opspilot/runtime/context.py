from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from opspilot.core.workspace import Workspace
from opspilot.runtime.session import Session


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    session: Session
    request_id: UUID
    workspace: Workspace
    target: str = "local"
    metadata: dict[str, Any] = field(default_factory=dict)
