# Spec Baseline Consistency Review

## Status

Changes required before merge.

## Scope

The following specifications were reviewed together:

* `specs/core/tool/spec.md`
* `specs/core/plugin/spec.md`
* `specs/core/policy/spec.md`
* `specs/core/audit/spec.md`
* `specs/core/workspace/spec.md`
* `specs/core/transport/spec.md`
* `specs/runtime/execution/spec.md`

## Executive Summary

The specifications share a consistent overall architecture:

```text
Client
  |
  v
Runtime Execution Kernel
  |
  +--> Session
  +--> Policy
  +--> Approval
  +--> Audit
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

The primary boundaries are coherent:

* Runtime owns orchestration.
* Plugins provide Tools.
* Policy decides.
* Approval records explicit human consent.
* Audit records execution facts.
* Workspace constrains filesystem scope.
* Transport performs host operations.
* MCP remains an external adapter.

However, the baseline is not ready to merge because two mandatory contracts are referenced but not specified:

* Approval
* Session

Several terminology and behavioral inconsistencies also require correction.

---

# 1. Missing Approval Specification

## Severity

Blocker.

## Finding

The Policy and Runtime specifications depend heavily on Approval behavior, but no canonical Approval specification exists.

Undefined areas include:

* Approval identity
* Approval request schema
* Approval expiration
* payload integrity
* request binding
* approver authorization
* rejection behavior
* cancellation behavior
* replay prevention
* approval audit events
* durable pending approvals

## Required Action

Create:

```text
specs/core/approval/spec.md
```

The specification must define:

* Approval request
* Approval decision
* exact request binding
* expiration
* approver identity
* rejection
* cancellation
* replay prevention
* Audit integration
* fail-closed behavior

The Spec Baseline must not be merged before this file exists.

---

# 2. Missing Session Specification

## Severity

Blocker.

## Finding

The Runtime Execution specification requires:

* active session validation
* user identity
* Workspace ownership
* target host association
* limits
* cancellation
* session shutdown

These behaviors are not defined by a canonical Session contract.

## Required Action

Create:

```text
specs/runtime/session/spec.md
```

The specification must define:

* Session identity
* lifecycle
* user binding
* Workspace binding
* target binding
* expiration
* limits
* cancellation
* shutdown
* session Audit events
* concurrency rules

The Spec Baseline must not be merged before this file exists.

---

# 3. Audit Event Naming Inconsistency

## Severity

Required correction.

## Finding

The Runtime Execution specification references:

```text
REQUEST_DENIED
```

The Audit specification does not define that event.

The Audit specification currently defines:

```text
SESSION_STARTED
SESSION_FINISHED
REQUEST_RECEIVED
REQUEST_VALIDATED
POLICY_EVALUATED
APPROVAL_REQUESTED
APPROVAL_GRANTED
APPROVAL_REJECTED
TOOL_STARTED
TOOL_FINISHED
TOOL_FAILED
TIMEOUT
CANCELLED
RUNTIME_ERROR
PLUGIN_ERROR
```

## Decision

Add these events to the Audit specification:

```text
REQUEST_DENIED
APPROVAL_EXPIRED
DRY_RUN_STARTED
DRY_RUN_FINISHED
DRY_RUN_FAILED
OUTPUT_VALIDATION_FAILED
```

Use `TOOL_FINISHED` consistently.

Do not introduce `TOOL_COMPLETED` as a second name.

---

# 4. Audit Tamper-Evidence Contradiction

## Severity

Required correction.

## Finding

The Audit specification says Audit must be:

```text
tamper-evident
```

Later, cryptographic hashes and signed chains are described as future functionality.

Append-only storage is achievable in Contracts v1.

Strong cryptographic tamper evidence is not yet required by the current implementation plan.

## Decision

For Contracts v1, Audit must be:

* append-only
* immutable through the Audit API
* ordered
* structured
* correlated
* durable according to backend guarantees

Cryptographic tamper evidence remains a future enhancement.

Replace the mandatory `tamper-evident` statement with:

```text
designed for future tamper-evident storage
```

---

# 5. Audit Failure Behavior

## Severity

Required correction.

## Finding

The Runtime Execution specification states:

* required pre-execution Audit failure causes fail-closed behavior
* Tool execution must not begin without required Audit events

The Audit specification does not currently define this invariant.

## Decision

Add the following rule to the Audit specification:

```text
If a mandatory pre-execution Audit event cannot be persisted,
Runtime must fail closed and must not execute the Tool.
```

Post-execution Audit failure must be returned as a critical Runtime failure and must not be silently ignored.

---

# 6. Workspace Root Exception Contradiction

## Severity

Required correction.

## Finding

The Workspace purpose says operations remain inside the configured root:

```text
unless a higher-level policy explicitly grants a narrower approved exception
```

Later, the same specification says:

* Tool-supplied absolute paths are rejected
* access outside the root is not supported in Contracts v1
* one root is a mandatory security boundary

These statements conflict.

## Decision

Contracts v1 does not support out-of-root exceptions.

Replace the purpose statement with:

```text
The Workspace ensures that Tool filesystem operations remain inside
one explicitly configured root.
```

Policy may restrict access further inside the Workspace.

Policy cannot expand the Workspace beyond its configured root in Contracts v1.

Future external-path capabilities require a separate contract and ADR.

---

# 7. Tool Retry Metadata Is Missing

## Severity

Required correction.

## Finding

The Runtime Execution specification says Tools declare whether they are:

* idempotent
* safe to retry

The Tool specification does not define this metadata in `ToolDefinition`.

## Decision

Add these fields to the Tool definition:

```text
idempotent
retry_safe
```

Rules:

* `idempotent` describes operation semantics.
* `retry_safe` describes whether Runtime may retry after a clearly retryable failure.
* `mutates=true` defaults to `retry_safe=false`.
* Runtime must never infer either value from the Tool name.
* ambiguous execution state always prevents automatic retry.

---

# 8. Tool Owner Metadata

## Severity

Recommended correction.

## Finding

Tool names are namespaced by Plugin identifier, but Tool ownership is inferred only from the name.

This creates avoidable ambiguity during:

* manifest validation
* registration
* Audit
* compatibility checking

## Decision

Add explicit Tool owner metadata:

```text
plugin_id
```

`ToolDefinition.name` remains fully qualified:

```text
filesystem.read_file
```

Runtime validates that:

```text
definition.plugin_id == manifest.id
```

and that the Tool name begins with:

```text
<plugin_id>.
```

---

# 9. Plugin Permission Admission Terminology

## Severity

Required clarification.

## Finding

The Plugin lifecycle includes:

```text
Permissions Evaluated
```

This could be confused with per-request Policy evaluation.

Plugin loading performs admission validation, not execution authorization.

## Decision

Rename this lifecycle stage:

```text
Permission Admission Checked
```

Meaning:

* requested permissions are known
* requested permissions are supported
* project configuration permits loading the Plugin
* undeclared capabilities are rejected

Per-request authorization still occurs through Policy for every Tool request.

---

# 10. Policy Dry-Run and Approval Sequence

## Severity

No structural blocker; clarification required.

## Finding

Policy returns one primary decision:

```text
ALLOW
DENY
REQUIRE_APPROVAL
REQUIRE_DRY_RUN
```

Cluster mutations may require both dry-run and Approval.

## Decision

The sequence remains:

```text
REQUIRE_DRY_RUN
    |
    v
Dry-run execution
    |
    v
Policy re-evaluation
    |
    v
REQUIRE_APPROVAL
```

Contracts v1 does not return two simultaneous primary decisions.

Policy evaluation may include constraints and reasons, but Runtime follows one primary transition at a time.

Document this explicitly in Policy and Runtime specifications.

---

# 11. Input Validation Order

## Severity

Accepted.

## Finding

Runtime validates Tool input before Policy evaluation.

This is correct because Policy needs typed, normalized arguments.

## Invariant

The order is:

```text
Tool resolution
    |
    v
Input schema validation
    |
    v
Policy evaluation
```

Input validation must not perform Tool execution or external side effects.

---

# 12. Workspace and Transport Boundary

## Severity

Accepted with implementation caution.

## Decision

Workspace owns:

* root isolation
* safe relative paths
* traversal rejection
* symlink escape prevention
* path limits

Transport owns:

* actual local or remote I/O
* process execution
* timeout
* cancellation
* output capture
* host communication

Tools must not pass raw host paths directly to Transport.

Workspace must produce a transport-safe path capability or validated target representation.

The exact Python type will be defined during Contracts v1 implementation.

---

# 13. Initial Vertical Slice Scope

## Severity

Accepted.

The first implementation remains read-only.

Included:

```text
filesystem.read_file
filesystem.list_directory
filesystem.stat
```

Excluded:

```text
filesystem.write_file
filesystem.delete
terminal execution
SSH
Docker mutation
Kubernetes
Kafka
PostgreSQL
Planner
RAG
MCP implementation
```

Transport may define future process-execution contracts, but the initial vertical slice does not expose an executable Tool.

---

# 14. Canonical Naming

Use these terms consistently:

```text
Runtime Execution Kernel
Tool
ToolDefinition
ToolRegistry
Plugin
PluginManifest
PluginContext
ExecutionContext
PolicyEngine
PolicyEvaluation
ApprovalService
ApprovalRequest
ApprovalDecision
AuditService
AuditEvent
Workspace
WorkspacePath
HostTransport
HostIdentity
```

Avoid introducing parallel names such as:

```text
CoreRuntime
RuntimeManager
ConfirmationProvider
AuditLogger
TransportManager
ExecutionWorkspace
```

unless a later ADR intentionally changes the canonical terminology.

---

# 15. Merge Gate

The `docs/spec-baseline-v1` Branch may be merged only when:

* Approval specification exists.
* Session specification exists.
* Audit event names are aligned.
* Audit failure behavior is aligned.
* Workspace root exception is removed.
* Tool retry metadata is added.
* Tool Plugin ownership metadata is added.
* Plugin admission terminology is clarified.
* Dry-run and Approval sequencing is explicit.
* all expected Spec files exist.
* repository checks pass.
* working tree is clean.

## Required Specification Set

```text
specs/core/tool/spec.md
specs/core/plugin/spec.md
specs/core/policy/spec.md
specs/core/approval/spec.md
specs/core/audit/spec.md
specs/core/workspace/spec.md
specs/core/transport/spec.md
specs/runtime/session/spec.md
specs/runtime/execution/spec.md
```

## Validation Commands

```bash
uv run pytest
uv run ruff check .
uv run mypy src
git diff --check
git status
```

## Merge Decision

Not approved yet.

Next required specification:

```text
specs/core/approval/spec.md
```

