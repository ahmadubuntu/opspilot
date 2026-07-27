# Error Model

## Purpose

OpsPilot uses a structured error model so that every component reports failures in a predictable way.

Errors are intended for:

- Runtime
- Plugins
- CLI
- MCP
- Future Web APIs

No component should invent its own error format.

---

# Error Categories

## ValidationError

The request is invalid.

Examples:

- Missing required field
- Invalid argument type
- Unsupported option

Retry:

No

---

## PolicyError

Blocked by Policy Engine.

Examples:

- Forbidden command
- Access outside workspace
- Disabled plugin

Retry:

No

---

## ApprovalRequired

Execution requires human approval.

Examples:

- kubectl delete
- docker rm
- git push
- ssh execution

Retry:

Yes

(after approval)

---

## TransportError

Host communication failed.

Examples:

- SSH disconnected
- Local process failed
- Timeout

Retry:

Maybe

Runtime decides.

---

## ToolExecutionError

The tool failed after execution started.

Examples:

- kubectl returned non-zero
- git merge conflict
- docker build failed

Retry:

Depends on tool.

---

## PluginError

Plugin implementation failure.

Examples:

- uncaught exception
- invalid manifest
- incompatible version

Retry:

No

Plugin should be isolated.

---

## RuntimeError

Internal Runtime failure.

Examples:

- Dispatcher failure
- Session corruption
- Memory retrieval failure

Retry:

No

Requires investigation.

---

## Cancelled

Operation cancelled.

Examples:

- User cancelled
- Timeout budget exceeded

Retry:

User decides.

---

# Error Response

Every error contains:

- category
- code
- message
- retryable
- details (optional)

Example

```json
{
  "category": "TransportError",
  "code": "SSH_TIMEOUT",
  "message": "SSH connection timed out.",
  "retryable": true
}
```

---

# Error Propagation

```
Plugin
    ↓
Dispatcher
    ↓
Runtime
    ↓
CLI / MCP
```

Plugins never print directly to users.

Runtime converts internal failures into structured errors.

---

# Logging

Every error must be logged with:

- session_id
- request_id
- plugin_id
- tool_name
- host_id
- duration

Sensitive information must never appear in logs.

---

# Recovery

Runtime decides whether an operation can be retried.

Mutating operations are never automatically retried.

Read-only operations may be retried when safe.

---

# Principles

- Fail closed
- Structured errors only
- No raw Python tracebacks to users
- Retry only when safe
- Preserve original cause for debugging
