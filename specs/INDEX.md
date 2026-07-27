# OpsPilot Specification Index

## Purpose

This document is the canonical index of OpsPilot architecture and implementation specifications.

It defines:

* which specifications exist
* their current status
* their ownership
* their dependencies
* their implementation targets
* their validation requirements

This index is part of the architecture governance process.

A specification not listed here is not considered part of the canonical Contracts baseline.

---

# Status Definitions

## Draft

The specification is under active design.

It must not be treated as an implementation contract.

## Accepted

The specification has passed architecture review and may guide implementation.

## Implementing

The specification is accepted and currently being implemented.

## Implemented

The specification is represented by production code and tests.

## Superseded

The specification has been replaced by another accepted specification or ADR.

Superseded specifications must identify their replacement.

---

# Contracts v1 Baseline

## Core Specifications

| Specification                  | Status   | Primary Responsibility                          |
| ------------------------------ | -------- | ----------------------------------------------- |
| `specs/core/tool/spec.md`      | Accepted | Typed executable capability contract            |
| `specs/core/plugin/spec.md`    | Accepted | Plugin identity, lifecycle, and Tool ownership  |
| `specs/core/policy/spec.md`    | Accepted | Authorization decision model                    |
| `specs/core/approval/spec.md`  | Accepted | Explicit human approval contract                |
| `specs/core/audit/spec.md`     | Accepted | Immutable and ordered execution records         |
| `specs/core/workspace/spec.md` | Accepted | Filesystem scope and path isolation             |
| `specs/core/transport/spec.md` | Accepted | Local and future remote host execution boundary |

## Runtime Specifications

| Specification                     | Status   | Primary Responsibility                    |
| --------------------------------- | -------- | ----------------------------------------- |
| `specs/runtime/session/spec.md`   | Accepted | Session identity, lifecycle, and bindings |
| `specs/runtime/execution/spec.md` | Accepted | Canonical Runtime Execution Kernel flow   |

---

# Dependency Map

The canonical dependency direction is:

```text
Runtime Execution
    |
    +--> Session
    +--> Policy
    +--> Approval
    +--> Audit
    +--> Tool Registry
    |
    v
Tool
    |
    v
Plugin
    |
    v
Workspace
    |
    v
HostTransport
```

Detailed dependencies:

| Specification     | Depends On                                            |
| ----------------- | ----------------------------------------------------- |
| Tool              | Policy metadata, Workspace and Transport capabilities |
| Plugin            | Tool, manifest validation, permission admission       |
| Policy            | Tool metadata, Session, Workspace, target identity    |
| Approval          | Policy decision, Session, Tool request identity       |
| Audit             | Runtime events, Policy, Approval, Tool execution      |
| Workspace         | Session root binding, HostTransport                   |
| HostTransport     | Host identity, Workspace-approved targets             |
| Session           | Workspace, Host identity, user identity               |
| Runtime Execution | All Contracts v1 specifications                       |

---

# Canonical Execution Path

Every Tool request follows:

```text
Client
    |
    v
Runtime Execution Kernel
    |
    v
Session Validation
    |
    v
Tool Resolution
    |
    v
Input Validation
    |
    v
Policy Evaluation
    |
    +--> Deny
    +--> Approval
    +--> Dry Run
    |
    v
Dispatcher
    |
    v
Tool
    |
    v
Workspace
    |
    v
HostTransport
    |
    v
Target System
```

No client, Plugin, Tool, adapter, or Transport may bypass this path.

---

# Core Platform Services

The following components are mandatory Core Platform Services:

* Runtime Execution Kernel
* Session Service
* Tool Registry
* Policy Engine
* Approval Service
* Audit Service
* Workspace
* HostTransport
* SecretProvider

These components must not be implemented as optional Plugins.

---

# Plugin Boundary

Plugins provide:

* Plugin manifest
* Tool definitions
* Tool implementations
* domain-specific input and output models
* domain-specific error interpretation
* Plugin lifecycle behavior

Plugins do not provide:

* Policy
* Approval
* Audit persistence
* Session management
* Runtime orchestration
* unrestricted Transport
* unrestricted Workspace
* raw Secret access

---

# Adapter Boundary

Adapters include:

* CLI
* MCP
* Open WebUI integration
* future Web API
* future IDE integrations

Adapters submit requests to the Runtime API.

Adapters do not:

* call Tools directly
* call Plugins directly
* call Transport directly
* bypass Policy
* forge Approval
* suppress Audit

MCP is an external interoperability protocol.

MCP is not the internal Plugin or Tool ABI.

---

# Implementation Targets

## Tool Contract

Expected implementation targets:

```text
src/opspilot/core/tool.py
src/opspilot/core/risk.py
src/opspilot/core/permissions.py
src/opspilot/core/errors.py
src/opspilot/runtime/registry.py
```

Expected tests:

```text
tests/core/test_tool.py
tests/runtime/test_registry.py
```

## Plugin Contract

Expected implementation targets:

```text
src/opspilot/core/plugin.py
src/opspilot/core/manifest.py
src/opspilot/plugin_loader/discovery.py
src/opspilot/plugin_loader/registry.py
```

Expected tests:

```text
tests/core/test_plugin.py
tests/core/test_manifest.py
tests/plugin_loader/test_discovery.py
tests/plugin_loader/test_registry.py
```

## Policy Contract

Expected implementation targets:

```text
src/opspilot/runtime/policy.py
```

Expected tests:

```text
tests/runtime/test_policy.py
```

## Approval Contract

Expected implementation targets:

```text
src/opspilot/runtime/approval.py
```

Expected tests:

```text
tests/runtime/test_approval.py
```

## Audit Contract

Expected implementation targets:

```text
src/opspilot/runtime/audit.py
```

Expected tests:

```text
tests/runtime/test_audit.py
```

## Workspace Contract

Expected implementation targets:

```text
src/opspilot/core/workspace.py
```

Expected tests:

```text
tests/core/test_workspace.py
```

## Host Transport Contract

Expected implementation targets:

```text
src/opspilot/core/transport.py
src/opspilot/core/local_transport.py
```

Expected tests:

```text
tests/core/test_transport.py
tests/core/test_local_transport.py
```

## Session Contract

Expected implementation targets:

```text
src/opspilot/runtime/session.py
```

Expected tests:

```text
tests/runtime/test_session.py
```

## Runtime Execution Contract

Expected implementation targets:

```text
src/opspilot/runtime/context.py
src/opspilot/runtime/dispatcher.py
src/opspilot/runtime/kernel.py
src/opspilot/runtime/requests.py
src/opspilot/runtime/results.py
```

Expected tests:

```text
tests/runtime/test_context.py
tests/runtime/test_dispatcher.py
tests/runtime/test_kernel.py
```

---

# Initial Vertical Slice

The first complete implementation slice is read-only filesystem access.

Included Tools:

```text
filesystem.read_file
filesystem.list_directory
filesystem.stat
```

Execution path:

```text
CLI
    |
    v
Runtime Execution Kernel
    |
    v
Policy
    |
    v
Dispatcher
    |
    v
Filesystem Tool
    |
    v
Workspace
    |
    v
LocalTransport
```

Excluded from the initial slice:

* file writes
* file deletion
* terminal execution
* Docker mutation
* Kubernetes
* Kafka
* PostgreSQL
* SSH
* remote agents
* MCP implementation
* planner
* RAG
* multi-agent orchestration

---

# Validation Requirements

A specification may move from `Accepted` to `Implemented` only when:

* corresponding code exists
* unit tests exist
* integration tests exist where required
* security acceptance criteria are tested
* Ruff passes
* Mypy passes
* Pytest passes
* implementation matches canonical terminology
* no architecture guardrail is violated
* traceability records are updated

Required validation commands:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
git diff --check
```

---

# Change Control

Changes to an accepted specification require:

1. a documented reason
2. review of affected specifications
3. review of implementation impact
4. updated traceability
5. an ADR when the change is architecturally significant
6. passing validation checks

Breaking changes require explicit migration notes.

---

# Source of Truth

When documents conflict, the priority order is:

1. Accepted ADR
2. Accepted specification
3. Architecture decisions summary
4. Architecture documentation
5. Source code
6. Tests
7. AI memory files
8. informal notes

When source code conflicts with an accepted specification, the conflict must be resolved explicitly.

Code does not silently redefine architecture.

---

# Current Phase

Current phase:

```text
Phase 1.5 — Architecture Governance
```

Current objective:

* finalize Contracts v1 governance
* establish traceability
* review ADR coverage
* update architecture indexes
* pass the final Merge Gate

Next implementation phase:

```text
Phase 2 — Core Contracts and Runtime Kernel
```

---

# Ownership

Project owner:

```text
Ahmad Abdolmaleki
```

Architecture governance is currently maintained through:

* accepted specifications
* ADRs
* architecture reviews
* Git history
* AI onboarding documentation

---

# Last Reviewed

2026-07-27

