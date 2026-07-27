import asyncio
from pathlib import Path

from opspilot.core.local_transport import LocalTransport
from opspilot.core.workspace import Workspace
from opspilot.plugins.filesystem.plugin import FilesystemPlugin
from opspilot.runtime.approval import DenyApprovalProvider
from opspilot.runtime.audit import AuditEventType, InMemoryAuditSink
from opspilot.runtime.context import ExecutionContext
from opspilot.runtime.dispatcher import Dispatcher
from opspilot.runtime.policy import DefaultPolicyEngine
from opspilot.runtime.registry import ToolRegistry
from opspilot.runtime.requests import ToolRequest
from opspilot.runtime.runtime import Runtime
from opspilot.runtime.session import Session


def test_read_file_vertical_slice(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    session = Session()
    workspace = Workspace(tmp_path, LocalTransport())
    registry = ToolRegistry()
    registry.register_many(FilesystemPlugin().tools())
    audit = InMemoryAuditSink()
    runtime = Runtime(
        dispatcher=Dispatcher(registry),
        policy=DefaultPolicyEngine(),
        approval=DenyApprovalProvider(),
        audit=audit,
    )
    request = ToolRequest(
        session_id=session.id,
        tool_name="filesystem.read_file",
        arguments={"path": "README.md"},
    )
    context = ExecutionContext(session=session, request_id=request.request_id, workspace=workspace)

    result = asyncio.run(runtime.execute(context, request))

    assert result.success is True
    assert result.output == {"content": "hello"}
    assert [event.event_type for event in audit.events()] == [
        AuditEventType.REQUEST_RECEIVED,
        AuditEventType.POLICY_DECIDED,
        AuditEventType.TOOL_STARTED,
        AuditEventType.TOOL_COMPLETED,
    ]
