from __future__ import annotations

from pathlib import Path, PurePosixPath

from opspilot.core.errors import ErrorCategory, ErrorDetail, WorkspaceViolationError
from opspilot.core.transport import DirectoryEntry, HostTransport


class Workspace:
    def __init__(self, root: Path, transport: HostTransport) -> None:
        self._root = root.resolve(strict=True)
        if not self._root.is_dir():
            raise ValueError("workspace root must be a directory")
        self._transport = transport

    @property
    def root(self) -> Path:
        return self._root

    def resolve(self, relative_path: str) -> Path:
        path = PurePosixPath(relative_path or ".")
        if path.is_absolute() or ".." in path.parts:
            self._raise_violation(relative_path)

        candidate = (self._root / Path(*path.parts)).resolve(strict=False)
        try:
            candidate.relative_to(self._root)
        except ValueError:
            self._raise_violation(relative_path)
        return candidate

    async def read_text(self, relative_path: str) -> str:
        return await self._transport.read_text(str(self.resolve(relative_path)))

    async def list_directory(self, relative_path: str = ".") -> list[DirectoryEntry]:
        return await self._transport.list_directory(str(self.resolve(relative_path)))

    @staticmethod
    def _raise_violation(path: str) -> None:
        raise WorkspaceViolationError(
            ErrorDetail(
                category=ErrorCategory.VALIDATION,
                code="WORKSPACE_PATH_ESCAPE",
                message=f"Path escapes workspace boundary: {path!r}",
            )
        )
