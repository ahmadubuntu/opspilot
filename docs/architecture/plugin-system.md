# Plugin System

## Philosophy

Plugins extend OpsPilot.

Plugins never extend security.

Only the runtime controls execution.

---

## Plugin Lifecycle

```
Discover

↓

Validate Manifest

↓

Load

↓

Initialize

↓

Register Tools

↓

Ready

↓

unload
```

---

## Plugin Requirements

Every plugin must provide:

- manifest
- metadata
- version
- permissions
- tools

---

## Manifest

Example

```yaml
id: kubernetes

version: 1.0.0

permissions:
  - cluster_read
  - cluster_mutate

transport:
  - local
  - ssh
```

---

## Tool Registration

Every tool registers:

- name
- description
- input model
- output model
- risk level
- supports dry-run
- supports cancellation

---

## Dependency Injection

Plugins receive:

- logger
- transport
- audit
- policy
- workspace
- SecretProvider

Plugins never import these globally.

---

## Forbidden

Plugins must never:

- open SSH sessions directly
- invoke Docker directly
- read arbitrary filesystem paths
- bypass policy
- bypass audit
- bypass approvals

Plugins never receive raw secrets.

Plugins receive a SecretProvider capable of returning opaque handles or temporary credentials according to policy.

---

## Versioning

Plugin API follows semantic versioning.

Breaking changes require major version increments.

---

## Isolation

Plugin failures must never crash the runtime.

Runtime isolates plugin exceptions.

---

## Future

Future plugin types:

- Python
- External MCP
- Remote Agent


## Plugins Never

Plugins never:

- communicate directly with users
- approve operations
- evaluate permissions
- write audit records
- access transports directly
- execute arbitrary subprocesses
