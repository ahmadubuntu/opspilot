from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from opspilot.core.manifest import PluginManifest
from opspilot.core.tool import Tool


class Plugin(ABC):
    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        raise NotImplementedError

    @abstractmethod
    def tools(self) -> Iterable[Tool]:
        raise NotImplementedError
