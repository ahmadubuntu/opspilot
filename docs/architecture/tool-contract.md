# Tool Contract

## Purpose

A Tool is the smallest executable capability exposed by OpsPilot. Plugins provide Tools; the Runtime Kernel controls their validation, policy evaluation, approval, execution, timeout handling, and auditing.

## Definition

Every Tool declares:

- globally unique, namespaced name
- human-readable description
- Pydantic input model
- Pydantic output model
- risk class
- required permissions
- mutation flag
- dry-run support
- timeout

Internal Python tools use typed Pydantic model classes. External adapters such as MCP expose their JSON Schema representation and do not redefine the internal ABI.

## Execution Contract

```text
ToolRequest
→ Registry resolution
→ Input validation
→ Policy evaluation
→ Approval when required
→ Tool execution
→ Output validation/serialization
→ Audit
```

A Tool receives an immutable `ExecutionContext` and validated input model. It returns a structured output model.

## Risk Classes

- `READ`: observation only; normally allowed and always audited.
- `WRITE_WORKSPACE`: modifies the active workspace; approval policy applies.
- `EXEC`: executes a process or command; approval normally required.
- `CLUSTER_MUTATE`: changes infrastructure; explicit approval and dry-run when available.
- `REMOTE_EXEC`: executes on a remote target; explicit approval always required.
- `SYSTEM`: privileged or host-level changes; deny or explicit approval by policy.

## Rules

Tools must not:

- call another plugin directly
- bypass Policy, Approval, or Audit
- communicate directly with users
- access raw secrets
- use global mutable state
- open raw SSH sessions
- invoke subprocesses outside HostTransport
- access paths outside Workspace

Read-only operations should be idempotent. Mutating operations must document idempotency and support dry-run or preview whenever technically possible.

## Errors

Expected failures use structured OpsPilot errors. Unexpected exceptions are normalized by Runtime and must not expose raw tracebacks or secrets to clients.
