# Versioning

OpsPilot follows Semantic Versioning.

MAJOR

Breaking API changes.

MINOR

Backward-compatible features.

PATCH

Bug fixes.

Plugin API versioning is independent.

Every plugin declares:

- plugin_version
- api_version

Runtime refuses incompatible plugins.

Deprecated APIs remain supported for at least one MINOR release.
