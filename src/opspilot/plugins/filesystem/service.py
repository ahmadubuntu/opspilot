from __future__ import annotations

from pathlib import Path


class FilesystemService:

    def read(self, path: str) -> str:
        return Path(path).read_text()

    def write(
        self,
        path: str,
        content: str,
    ) -> None:
        Path(path).write_text(content)
