from pathlib import Path

import pytest

from opspilot.core.errors import WorkspaceViolationError
from opspilot.core.local_transport import LocalTransport
from opspilot.core.workspace import Workspace


def test_workspace_rejects_parent_traversal(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path, LocalTransport())
    with pytest.raises(WorkspaceViolationError):
        workspace.resolve("../outside")


def test_workspace_rejects_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-opspilot-test"
    outside.mkdir(exist_ok=True)
    link = tmp_path / "escape"
    link.symlink_to(outside, target_is_directory=True)
    workspace = Workspace(tmp_path, LocalTransport())
    with pytest.raises(WorkspaceViolationError):
        workspace.resolve("escape/secret.txt")
