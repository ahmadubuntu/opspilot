# Plugin Manifest Contract

## Purpose

A Plugin Manifest declares plugin identity, compatibility, requested permissions, and required transports. It is untrusted input and must be validated before any Tool is registered.

## Required Fields

- `id`: stable lowercase identifier
- `name`: human-readable name
- `version`: semantic version
- `api_version`: supported OpsPilot plugin API version
- `description`: plugin purpose
- `permissions`: requested capabilities
- `required_transports`: transport capabilities required by the plugin
- `enabled`: startup eligibility

## Example

```yaml
id: filesystem
name: Filesystem
version: 0.1.0
api_version: v1
description: Safe read-only workspace filesystem tools.
permissions:
  - workspace.read
required_transports:
  - local
enabled: true
```

## Validation

Runtime rejects manifests with:

- invalid or duplicate plugin IDs
- invalid semantic versions
- unsupported API versions
- unknown permissions
- unsupported transports
- undeclared capabilities
- unknown fields

Missing declarations are denied. A manifest describes what a plugin requests; it never grants authority.

## Lifecycle

```text
Discover
→ Load manifest
→ Validate manifest
→ Check compatibility and policy
→ Instantiate plugin
→ Register unique Tools
→ Ready
→ Unload
```

## Security Rules

Plugins are treated as untrusted, including first-party plugins. They must not bypass Runtime, access raw secrets, modify audit storage, communicate directly with users, or directly control transports.

Internal plugins use the typed Python Plugin contract. MCP and remote integrations are adapters and do not replace the internal plugin ABI.
