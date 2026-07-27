# Dispatcher

## Purpose

The Dispatcher is responsible for routing ToolRequests to the correct plugin.

It does not execute business logic.

It does not perform authorization.

It does not implement tools.

---

## Responsibilities

The Dispatcher:

- resolves the target plugin
- validates tool existence
- creates execution context
- invokes the selected plugin
- returns ToolResult

---

## Non Responsibilities

The Dispatcher never:

- evaluates permissions
- asks for approval
- writes audit logs
- manages sessions
- stores memory
- retries operations
- performs transport operations

Those concerns belong to other Runtime components.

---

## Request Flow

```
ToolRequest
    ↓
Dispatcher
    ↓
Plugin Registry
    ↓
Selected Plugin
    ↓
ToolResult
```

---

## Validation

Before dispatching:

- plugin exists
- tool exists
- tool version supported
- request model valid

Otherwise:

Return ToolNotFound or ValidationError.

---

## Failure Handling

Dispatcher failures never crash the Runtime.

Unexpected plugin exceptions become:

PluginExecutionError

---

## Concurrency

Dispatcher is stateless.

Multiple Dispatcher instances may exist simultaneously.

---

## Extension Points

Future versions may support:

- remote dispatch
- distributed dispatch
- load balancing
- execution queues

without changing the Tool interface.
