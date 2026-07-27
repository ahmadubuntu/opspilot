# ADR-0002: Plugin Discovery Strategy

Status: Accepted

Date: 2026-07-19

---

## Context

OpsPilot is designed around a plugin-based architecture.

The project must support:

- first-party plugins shipped with OpsPilot
- third-party plugins installed later
- future packaging through PyPI
- unit testing without dynamic discovery
- stable production deployments

The discovery mechanism must be predictable and extensible.

---

## Decision

Plugin discovery will happen in two phases.

### Stage 1 (Bootstrap)

Core plugins are imported explicitly by the plugin loader.

Example:

```python
from opspilot.plugins.filesystem import FilesystemPlugin
from opspilot.plugins.terminal import TerminalPlugin
```

This provides:

- deterministic startup
- simple debugging
- zero packaging complexity

---

### Stage 2 (Production)

Plugins are discovered through Python entry points.

Example:

```
[project.entry-points."opspilot.plugins"]
filesystem = "opspilot.plugins.filesystem:FilesystemPlugin"
terminal = "opspilot.plugins.terminal:TerminalPlugin"
```

Advantages:

- external plugins
- pip install support
- version isolation
- no modification of the core loader

---

## Consequences

PluginLoader will expose the same API regardless of the discovery strategy.

Only the discovery implementation changes.

The Runtime and Dispatcher must never know how plugins are discovered.

---

## Rejected Alternatives

### Scan directories recursively

Rejected because:

- slow
- non-deterministic
- difficult to package
- difficult to secure

### Import every module under plugins/

Rejected because imports may execute arbitrary initialization code.

---

## Migration

Bootstrap implementation:

```
PluginLoader.load_builtin_plugins()
```

Future implementation:

```
PluginLoader.load_entrypoint_plugins()
```

No Runtime changes are expected during migration.

---

## Decision Drivers

- deterministic startup
- production stability
- packaging compatibility
- extensibility
- testability
