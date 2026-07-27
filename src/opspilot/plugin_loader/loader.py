from __future__ import annotations

from collections.abc import Iterable

from opspilot.core.plugin import Plugin
from opspilot.runtime.registry import ToolRegistry


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        plugin_id = plugin.manifest.id
        if plugin_id in self._plugins:
            raise ValueError(f"plugin already registered: {plugin_id}")
        self._plugins[plugin_id] = plugin

    def get(self, plugin_id: str) -> Plugin:
        return self._plugins[plugin_id]

    def all(self) -> tuple[Plugin, ...]:
        return tuple(self._plugins.values())


class PluginLoader:
    def __init__(self, plugins: Iterable[Plugin] = ()) -> None:
        self._plugins = tuple(plugins)

    def load(self, plugin_registry: PluginRegistry, tool_registry: ToolRegistry) -> None:
        for plugin in self._plugins:
            if not plugin.manifest.enabled:
                continue
            plugin_registry.register(plugin)
            tool_registry.register_many(plugin.tools())
