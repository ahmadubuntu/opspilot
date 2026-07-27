import pytest
from pydantic import ValidationError

from opspilot.core.manifest import PluginManifest
from opspilot.core.permissions import Permission


def test_manifest_is_immutable_and_rejects_unknown_fields() -> None:
    manifest = PluginManifest(
        id="filesystem",
        name="Filesystem",
        version="1.0.0",
        permissions=frozenset({Permission.WORKSPACE_READ}),
    )
    assert manifest.id == "filesystem"
    with pytest.raises(ValidationError):
        PluginManifest(id="Filesystem", name="Filesystem", version="1.0.0")


def test_manifest_rejects_invalid_semver() -> None:
    with pytest.raises(ValidationError):
        PluginManifest(id="filesystem", name="Filesystem", version="one")
