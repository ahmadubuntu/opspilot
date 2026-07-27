from __future__ import annotations

import asyncio
from pathlib import Path

from opspilot.core.transport import DirectoryEntry, HostTransport


class LocalTransport(HostTransport):
    async def read_text(self, path: str) -> str:
        return await asyncio.to_thread(Path(path).read_text, encoding="utf-8")

    async def list_directory(self, path: str) -> list[DirectoryEntry]:
        def collect() -> list[DirectoryEntry]:
            return [
                DirectoryEntry(name=item.name, is_directory=item.is_dir())
                for item in sorted(Path(path).iterdir(), key=lambda item: item.name)
            ]

        return await asyncio.to_thread(collect)
