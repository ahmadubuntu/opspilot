from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DirectoryEntry:
    name: str
    is_directory: bool


class HostTransport(ABC):
    @abstractmethod
    async def read_text(self, path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def list_directory(self, path: str) -> list[DirectoryEntry]:
        raise NotImplementedError
