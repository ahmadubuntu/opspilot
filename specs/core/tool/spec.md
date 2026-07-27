# Tool Contract Specification

## Status

Accepted for Contracts v1.

## Purpose

A Tool is the smallest independently executable capability exposed through OpsPilot.

Tools are implemented by plugins but discovered, validated, authorized, executed, and audited through the Execution Kernel.

## Responsibilities

A Tool is responsible for:

- declaring its identity and behavior
- declaring typed input and output models
- declaring required permissions
- declaring its risk classification
- implementing one bounded capability
- returning structured results
- respecting cancellation and runtime deadlines where technically possible

## Non-Responsibilities

A Tool never:

- evaluates policy
- approves its own execution
- communicates directly with users
- writes directly to audit storage
- accesses raw secrets
- opens raw SSH connections
- invokes subprocesses outside HostTransport
- calls another plugin directly
- bypasses Workspace boundaries

## Definition

Every Tool exposes a `ToolDefinition` containing:

- unique qualified name
- human-readable description
- typed input model
- typed output model
- risk class
- required permissions
- mutation indicator
- dry-run support indicator
- execution timeout

Tool names use a qualified namespace:

```text
<plugin-id>.<capability>
Examples:

filesystem.read_file
git.status
kubernetes.list_pods
Input Contract

Internal Python tools use concrete Pydantic model classes.

Raw dictionaries must not reach Tool implementations.

Input validation occurs before execution.

Invalid input produces a structured validation failure and the Tool is not invoked.

Output Contract

Tools return a validated Pydantic output model.

Tools do not return client-formatted Markdown, terminal UI output, or MCP-specific payloads.

Presentation belongs to adapters and clients.

Execution Contract

Tool execution receives:

validated typed input
immutable execution context
bounded Workspace access
approved capability handles
cancellation state
deadline information

Execution context is created by the Runtime.

Tools never create or replace their execution context.

Risk Classes

Initial risk classes are:

READ
WRITE_WORKSPACE
EXEC
CLUSTER_MUTATE
REMOTE_EXEC

Risk metadata informs Policy but does not replace Policy evaluation.

Mutation Rules

Mutating Tools must:

declare mutates=true
support dry-run when technically possible
provide a preview or expected-impact description when possible
identify the affected target and scope
never be automatically retried
emit sufficient information for audit events
Error Rules

Expected failures are represented as structured OpsPilot errors.

Unexpected exceptions are isolated and normalized by the Dispatcher or Runtime.

Raw tracebacks must not be returned to clients.

Cancellation and Timeout

Tools must honor cancellation where technically possible.

Tools must not:

disable Runtime deadlines
silently continue after cancellation
create unmanaged background processes
detach work without registering it with Runtime
Security Invariants

A Tool cannot authorize itself.

A Tool cannot weaken Policy, Approval, Audit, Workspace, Transport, or SecretProvider controls.

Unknown behavior is denied by default.

Compatibility

Internal Python tools use the typed Python ABI.

External protocols such as MCP receive generated JSON Schema through adapters.

MCP is not the internal Tool ABI.

Acceptance Criteria

The contract is considered implemented when:

duplicate Tool names are rejected
input models are validated before execution
output models are validated
risk and permission metadata are available to Policy
Tools cannot be dispatched without registration
Tool failures are normalized into structured errors
tests cover registration, validation, execution, and failure behavior

---
