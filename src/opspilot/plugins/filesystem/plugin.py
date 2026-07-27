from __future__ import annotations

from collections.abc import Iterable

from opspilot.core.manifest import PluginManifest
from opspilot.core.permissions import Permission
from opspilot.core.plugin import Plugin
from opspilot.core.tool import Tool
from opspilot.plugins.filesystem.tools import ListDirectoryTool, ReadFileTool


class FilesystemPlugin(Plugin):
    _manifest = PluginManifest(
        id="filesystem",
        name="Filesystem",
        version="0.1.0",
        description="Safe read-only workspace filesystem tools.",
        permissions=frozenset({Permission.WORKSPACE_READ}),
        required_transports=frozenset({"local"}),
    )

    @property
    def manifest(self) -> PluginManifest:
        return self._manifest

    def tools(self) -> Iterable[Tool]:
        return (ReadFileTool(), ListDirectoryTool())
