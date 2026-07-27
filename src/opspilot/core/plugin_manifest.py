from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Transport(str, Enum):
    LOCAL = "local"
    SSH = "ssh"
    REMOTE_AGENT = "remote_agent"


class PluginPermission(str, Enum):
    FILESYSTEM = "filesystem"
    TERMINAL = "terminal"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    KAFKA = "kafka"
    POSTGRES = "postgres"
    SENTRY = "sentry"


class PluginManifest(BaseModel):
    """
    Metadata describing a plugin.

    The manifest is consumed by the plugin loader before the plugin
    is instantiated.
    """

    id: str
    name: str
    version: str

    description: str

    api_version: int = 1

    permissions: list[PluginPermission] = Field(default_factory=list)

    supported_transports: list[Transport] = Field(
        default_factory=lambda: [Transport.LOCAL]
    )

    enabled: bool = True
