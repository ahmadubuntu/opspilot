# Runtime Architecture

## Overview

The runtime is the execution kernel of OpsPilot.

Its responsibility is to safely execute user requests through registered tools while enforcing policies, approvals, auditing and transport abstraction.

The runtime owns all execution.

Plugins never execute commands directly.

---

## Runtime Responsibilities

- Session lifecycle
- Memory loading
- Planning
- Policy evaluation
- Approval requests
- Tool dispatch
- Audit logging
- Error handling
- Cancellation
- Budget enforcement

---

## Execution Pipeline

```
Client
    │
    ▼
Gateway
    │
    ▼
Runtime
    │
    ├── Memory
    ├── Planner
    ├── Policy Engine
    ├── Approval Engine
    ├── Tool Dispatcher
    └── Audit Logger
             │
             ▼
        Registered Plugin
             │
             ▼
      Host Transport Layer
             │
             ▼
      Target Infrastructure
```

---

## Runtime Rules

The runtime:

- owns every execution
- assigns request IDs
- assigns session IDs
- injects plugin context
- records every action
- handles retries
- enforces timeouts

Plugins are intentionally stateless.

---

## Execution States

```
Created

↓

Planning

↓

WaitingForApproval

↓

Executing

↓

Completed
```

or

```
Created

↓

Planning

↓

Rejected
```

or

```
Created

↓

Planning

↓

Executing

↓

Failed
```

---

## Cancellation

Cancellation may happen at any state before execution finishes.

Every tool must support cancellation whenever technically possible.

---

## Timeouts

Every tool execution has:

- soft timeout
- hard timeout

Plugins cannot disable runtime timeouts.

---

## Retry

Only explicitly retryable failures may be retried.

Runtime never retries mutating operations automatically.

---

## Thread Safety

Plugins must be reentrant.

Runtime may execute multiple tools concurrently.

Plugins must never depend on global mutable state.
