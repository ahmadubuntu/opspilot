from __future__ import annotations

from abc import ABC, abstractmethod


class MemoryProvider(ABC):
    """
    Runtime memory interface.

    Memory is advisory only.

    Runtime must never trust memory instead of
    querying the real system.
    """

    @abstractmethod
    def search(
        self,
        query: str,
    ) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def remember(
        self,
        text: str,
    ) -> None:
        raise NotImplementedError
