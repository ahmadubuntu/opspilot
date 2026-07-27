from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from opspilot.core.permissions import Permission

_PLUGIN_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")


class PluginManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str = Field(min_length=1)
    version: str
    api_version: str = "v1"
    description: str = ""
    permissions: frozenset[Permission] = Field(default_factory=frozenset)
    required_transports: frozenset[str] = Field(default_factory=lambda: frozenset({"local"}))
    enabled: bool = True

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not _PLUGIN_ID.fullmatch(value):
            raise ValueError("plugin id must be lowercase and namespace-safe")
        return value

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        if not _SEMVER.fullmatch(value):
            raise ValueError("plugin version must be semantic versioning compatible")
        return value
