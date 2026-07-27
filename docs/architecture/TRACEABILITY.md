# OpsPilot Architecture Traceability

## Purpose

This document maps OpsPilot architectural decisions and specifications to their expected implementation and validation artifacts.

It exists to ensure that:

* accepted specifications are implemented intentionally
* implementation files have a documented architectural basis
* tests cover required contract behavior
* architectural changes can be evaluated for impact
* AI agents and developers can identify the source of each requirement
* documentation, code, and tests do not evolve independently

This file is part of the Architecture Governance baseline.

---

# Traceability Model

OpsPilot uses the following traceability chain:

```text
Architecture Decision
        |
        v
Accepted Specification
        |
        v
Implementation Contract
        |
        v
Source Code
        |
        v
Tests
        |
        v
Validation Evidence
```

Every production-critical capability must be traceable through this chain.

---

# Status Definitions

## Planned

The implementation target is defined but does not yet exist.

## Partial

Some implementation or tests exist, but the accepted specification is not fully satisfied.

## Implementing

Active implementation is in progress on a dedicated branch.

## Implemented

The accepted specification is represented by code and tests and has passed required validation.

## Diverged

The code or tests conflict with the accepted specification.

Divergence must be resolved explicitly and must never be silently accepted.

---

# Contracts v1 Traceability Matrix

| Contract          | Specification                     | Primary ADR                         | Implementation Targets                                                                                                                                                           | Test Targets                                                                                                                                | Status  |
| ----------------- | --------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Tool              | `specs/core/tool/spec.md`         | Pending ADR review                  | `src/opspilot/core/tool.py`, `src/opspilot/core/risk.py`, `src/opspilot/core/permissions.py`, `src/opspilot/runtime/registry.py`                                                 | `tests/core/test_tool.py`, `tests/runtime/test_registry.py`                                                                                 | Partial |
| Plugin            | `specs/core/plugin/spec.md`       | `docs/adr/0002-plugin-discovery.md` | `src/opspilot/core/plugin.py`, `src/opspilot/core/manifest.py`, `src/opspilot/plugin_loader/discovery.py`, `src/opspilot/plugin_loader/registry.py`                              | `tests/core/test_plugin.py`, `tests/core/test_manifest.py`, `tests/plugin_loader/test_discovery.py`, `tests/plugin_loader/test_registry.py` | Partial |
| Policy            | `specs/core/policy/spec.md`       | Pending ADR review                  | `src/opspilot/runtime/policy.py`                                                                                                                                                 | `tests/runtime/test_policy.py`                                                                                                              | Partial |
| Approval          | `specs/core/approval/spec.md`     | Pending ADR review                  | `src/opspilot/runtime/approval.py`                                                                                                                                               | `tests/runtime/test_approval.py`                                                                                                            | Planned |
| Audit             | `specs/core/audit/spec.md`        | Pending ADR review                  | `src/opspilot/runtime/audit.py`                                                                                                                                                  | `tests/runtime/test_audit.py`                                                                                                               | Partial |
| Workspace         | `specs/core/workspace/spec.md`    | Pending ADR review                  | `src/opspilot/core/workspace.py`                                                                                                                                                 | `tests/core/test_workspace.py`                                                                                                              | Partial |
| Host Transport    | `specs/core/transport/spec.md`    | Pending ADR review                  | `src/opspilot/core/transport.py`, `src/opspilot/core/local_transport.py`                                                                                                         | `tests/core/test_transport.py`, `tests/core/test_local_transport.py`                                                                        | Partial |
| Session           | `specs/runtime/session/spec.md`   | Pending ADR review                  | `src/opspilot/runtime/session.py`                                                                                                                                                | `tests/runtime/test_session.py`                                                                                                             | Planned |
| Runtime Execution | `specs/runtime/execution/spec.md` | Pending ADR review                  | `src/opspilot/runtime/context.py`, `src/opspilot/runtime/dispatcher.py`, `src/opspilot/runtime/kernel.py`, `src/opspilot/runtime/requests.py`, `src/opspilot/runtime/results.py` | `tests/runtime/test_context.py`, `tests/runtime/test_dispatcher.py`, `tests/runtime/test_kernel.py`                                         | Partial |

---

# Tool Contract Traceability

## Architectural Requirements

The Tool contract requires:

* typed input and output models
* explicit Tool ownership
* unique qualified names
* declared risk
* declared permissions
* mutation metadata
* dry-run metadata
* idempotency metadata
* retry-safety metadata
* bounded timeout
* structured execution failures

## Expected Implementation

```text
src/opspilot/core/tool.py
src/opspilot/core/risk.py
src/opspilot/core/permissions.py
src/opspilot/core/errors.py
src/opspilot/runtime/registry.py
```

## Expected Tests

```text
tests/core/test_tool.py
tests/runtime/test_registry.py
```

## Required Test Coverage

* Tool definition validation
* invalid qualified name rejection
* Plugin ownership mismatch rejection
* duplicate Tool rejection
* input-model validation
* output-model validation
* risk serialization
* permission serialization
* retry metadata behavior
* ambiguous execution preventing retry

## Current Status

Partial.

Existing Tool and Registry implementation must be reviewed against the accepted Tool specification during Phase 2.

---

# Plugin Contract Traceability

## Architectural Requirements

The Plugin contract requires:

* validated manifest
* stable Plugin identity
* Semantic Versioning
* explicit Plugin API version
* Tool ownership
* permission admission
* deterministic discovery
* bounded initialization
* bounded shutdown
* lifecycle failure isolation
* no generic Plugin execution switch
* no direct Runtime-internal dependency
* no direct Secret access
* no direct subprocess or SSH access

## Expected Implementation

```text
src/opspilot/core/plugin.py
src/opspilot/core/manifest.py
src/opspilot/plugin_loader/discovery.py
src/opspilot/plugin_loader/registry.py
```

## Expected Tests

```text
tests/core/test_plugin.py
tests/core/test_manifest.py
tests/plugin_loader/test_discovery.py
tests/plugin_loader/test_registry.py
```

## Required Test Coverage

* manifest validation
* duplicate Plugin rejection
* duplicate Tool rejection
* undeclared Tool rejection
* permission-admission failure
* API-version incompatibility
* initialization timeout
* initialization rollback
* failure isolation
* shutdown behavior

## Current Status

Partial.

Manifest tests exist, but complete Plugin lifecycle and discovery behavior are not implemented.

---

# Policy Contract Traceability

## Architectural Requirements

The Policy contract requires:

* evaluation for every request
* deterministic structured decisions
* fail-closed behavior
* least privilege
* argument inspection
* protected-resource rules
* strict decision precedence
* dry-run sequencing
* approval sequencing
* timeout handling
* decision Audit events

## Expected Implementation

```text
src/opspilot/runtime/policy.py
```

## Expected Tests

```text
tests/runtime/test_policy.py
```

## Required Test Coverage

* `ALLOW`
* `DENY`
* `REQUIRE_APPROVAL`
* `REQUIRE_DRY_RUN`
* unknown decision
* missing permission
* protected resource
* conflicting rules
* strictest-rule precedence
* policy timeout
* policy exception
* dry-run re-evaluation sequence
* fail-closed behavior

## Current Status

Partial.

Existing Policy code must be replaced or extended to return the canonical `PolicyEvaluation` model.

---

# Approval Contract Traceability

## Architectural Requirements

The Approval contract requires:

* exact request binding
* payload-integrity verification
* single-use decisions
* expiration
* approver identity
* rejection
* cancellation
* replay prevention
* Audit integration
* fail-closed behavior

## Expected Implementation

```text
src/opspilot/runtime/approval.py
```

## Expected Tests

```text
tests/runtime/test_approval.py
```

## Required Test Coverage

* valid approval
* rejection
* expiration
* cancellation
* payload mutation invalidation
* target mutation invalidation
* Tool mutation invalidation
* request replay rejection
* session mismatch rejection
* unauthorized approver
* missing approval
* Audit event creation

## Current Status

Planned.

No Contracts v1 implementation exists yet.

---

# Audit Contract Traceability

## Architectural Requirements

The Audit contract requires:

* append-only API
* immutable events
* chronological ordering
* structured event models
* request correlation
* session correlation
* failure recording
* Approval recording
* dry-run recording
* sensitive-data redaction
* fail-closed pre-execution persistence
* explicit post-execution persistence failure

## Expected Implementation

```text
src/opspilot/runtime/audit.py
```

## Expected Tests

```text
tests/runtime/test_audit.py
```

## Required Test Coverage

* event serialization
* event ordering
* request correlation
* session correlation
* immutable records
* redaction
* Policy denial event
* Approval events
* dry-run events
* Tool success
* Tool failure
* timeout
* cancellation
* pre-execution Audit failure
* post-execution Audit failure

## Current Status

Partial.

The existing Audit abstraction does not yet implement the complete canonical event model.

---

# Workspace Contract Traceability

## Architectural Requirements

The Workspace contract requires:

* exactly one root per session
* relative Tool paths
* absolute-path rejection
* traversal rejection
* symlink-escape rejection
* protected-path support
* non-existing target validation
* deterministic directory listing
* resource limits
* Transport independence
* no Policy-based root expansion

## Expected Implementation

```text
src/opspilot/core/workspace.py
```

## Expected Tests

```text
tests/core/test_workspace.py
```

## Required Test Coverage

* valid relative path
* absolute-path rejection
* parent traversal rejection
* nested traversal rejection
* symlink escape
* symlink within root
* non-existing child target
* protected path
* deterministic listing
* file-size limit
* directory-entry limit
* invalid encoding
* remote-compatible path semantics

## Current Status

Partial.

Basic traversal and symlink tests exist. Resource limits, protected paths, and remote-compatible target representation remain to be implemented.

---

# Host Transport Contract Traceability

## Architectural Requirements

The HostTransport contract requires:

* explicit HostIdentity
* structured process arguments
* no implicit shell
* bounded timeout
* cancellation
* bounded output
* separate stdout and stderr
* restricted environment inheritance
* explicit working directory
* Workspace-approved paths
* structured failure classification
* retryability metadata
* ambiguity metadata
* resource cleanup

## Expected Implementation

```text
src/opspilot/core/transport.py
src/opspilot/core/local_transport.py
```

## Expected Tests

```text
tests/core/test_transport.py
tests/core/test_local_transport.py
```

## Required Test Coverage

* structured execution success
* non-zero exit
* executable not found
* timeout
* cancellation
* stdout capture
* stderr capture
* output truncation
* environment restriction
* invalid working directory
* Workspace boundary
* resource cleanup
* retryability classification
* ambiguous execution state

## Current Status

Partial.

The current transport abstraction and LocalTransport require review against the accepted specification.

---

# Session Contract Traceability

## Architectural Requirements

The Session contract requires:

* globally unique identity
* immutable user binding
* immutable Workspace binding
* immutable Host binding
* explicit lifecycle
* expiration
* cancellation
* request limits
* concurrency limits
* lifecycle Audit events
* terminal-state enforcement

## Expected Implementation

```text
src/opspilot/runtime/session.py
```

## Expected Tests

```text
tests/runtime/test_session.py
```

## Required Test Coverage

* Session creation
* activation
* expiration
* cancellation
* closure
* invalid state transition
* immutable user
* immutable Workspace
* immutable Host
* request after expiration
* request after cancellation
* request-limit enforcement
* cancellation propagation
* lifecycle Audit events

## Current Status

Planned.

No Contracts v1 implementation exists yet.

---

# Runtime Execution Traceability

## Architectural Requirements

The Runtime Execution contract requires:

* one canonical execution path
* Session validation
* Tool resolution
* typed input validation
* mandatory Policy evaluation
* Approval enforcement
* dry-run enforcement
* thin Dispatcher
* immutable ExecutionContext
* timeout
* cancellation
* output validation
* retry control
* state-machine enforcement
* structured results
* mandatory ordered Audit

## Expected Implementation

```text
src/opspilot/runtime/context.py
src/opspilot/runtime/dispatcher.py
src/opspilot/runtime/kernel.py
src/opspilot/runtime/requests.py
src/opspilot/runtime/results.py
```

## Expected Tests

```text
tests/runtime/test_context.py
tests/runtime/test_dispatcher.py
tests/runtime/test_kernel.py
```

## Required Test Coverage

* successful read request
* invalid Session
* unknown Tool
* invalid Tool input
* Policy denial
* Approval required
* Approval rejection
* Approval expiration
* dry-run unsupported
* dry-run re-evaluation
* Tool failure
* invalid output
* timeout
* cancellation
* Audit precondition failure
* Audit postcondition failure
* invalid state transition
* retry-safe read
* mutation retry prevention
* ambiguous execution state

## Current Status

Partial.

A simplified Runtime path exists. The canonical Execution Kernel is planned for Phase 2.

---

# Initial Vertical Slice Traceability

## Scope

The first complete product slice includes:

```text
filesystem.read_file
filesystem.list_directory
filesystem.stat
```

## Expected Plugin Implementation

```text
plugins/filesystem/manifest.yaml
plugins/filesystem/plugin.py
plugins/filesystem/models.py
plugins/filesystem/tools.py
```

## Expected Tests

```text
tests/plugins/filesystem/test_read_file.py
tests/plugins/filesystem/test_list_directory.py
tests/plugins/filesystem/test_stat.py
tests/integration/test_filesystem_read_slice.py
```

## Required Execution Path

```text
CLI
    |
    v
Runtime Execution Kernel
    |
    v
Session
    |
    v
Policy
    |
    v
Audit
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

## Status

Planned after Phase 2 Core Contracts implementation.

---

# ADR Coverage

The current accepted ADR set must be reviewed against Contracts v1.

Known ADR:

```text
docs/adr/0002-plugin-discovery.md
```

Potential missing ADR subjects:

* Execution Kernel ownership
* MCP as external adapter
* Core services versus Plugins
* Workspace and Transport separation
* mandatory Policy, Approval, and Audit
* typed Python Plugin ABI
* one Workspace and Host per Session in Contracts v1
* fail-closed execution semantics

These subjects must be assessed during the Phase 1.5 ADR Review.

Not every specification requires a separate ADR.

An ADR is required when the decision:

* selects between meaningful alternatives
* has significant reversal cost
* affects multiple architectural boundaries
* constrains future implementation
* changes security or trust assumptions

---

# Source-File Traceability Rule

During Phase 2, every primary implementation module must reference its governing specification in its module docstring.

Example:

```python
"""
Implements:
- specs/core/tool/spec.md
- docs/adr/NNNN-example.md
"""
```

Do not add an ADR reference when no applicable ADR exists.

Tests should name the acceptance criterion they validate through descriptive test names and docstrings where useful.

---

# Pull Request Traceability Rule

Every architecture-sensitive Pull Request must identify:

* affected specifications
* affected ADRs
* implementation files
* tests added or changed
* security impact
* migration impact
* validation commands executed

A Pull Request must not claim a specification is implemented unless all required acceptance criteria and validation checks pass.

---

# Change Impact Procedure

When an accepted specification changes:

1. update the specification
2. update this traceability document
3. identify affected ADRs
4. identify affected source files
5. identify affected tests
6. document migration impact
7. run all validation checks
8. update `specs/INDEX.md`
9. update `.ai/STATUS.yaml`
10. commit the change with an architecture-aware message

---

# Validation Evidence

Required repository validation:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
git diff --check
```

Future CI should preserve validation results for every Pull Request.

---

# Current Governance Phase

```text
Phase 1.5 — Architecture Governance
```

Remaining tasks:

* complete ADR coverage review
* update `ARCHITECTURE_INDEX.md`
* update `implementation-contracts.md`
* update AI status files
* perform final consistency review
* pass Merge Gate
* merge `docs/spec-baseline-v1` into `main`

---

# Last Reviewed

2026-07-27

