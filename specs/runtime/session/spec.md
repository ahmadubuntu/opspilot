# Session Contract Specification

## Status

Accepted for Contracts v1.

## Purpose

A Session represents one authenticated execution context inside OpsPilot.

Every Runtime request belongs to exactly one Session.

---

# Responsibilities

Session owns:

* session identity
* user identity
* Workspace binding
* Host binding
* lifecycle
* limits
* cancellation
* metadata

---

# Non-Responsibilities

Session never:

* executes Tools
* evaluates Policy
* grants Approval
* performs Transport operations
* stores Secrets

---

# Session Identity

Every session has:

* session_id
* user_id
* created_at
* expires_at
* state

Session identifiers are globally unique.

---

# Session States

```text
CREATED

ACTIVE

EXPIRED

CANCELLED

CLOSED
```

Terminal states:

* EXPIRED
* CANCELLED
* CLOSED

---

# Lifecycle

```text
CREATED
    |
ACTIVE
    |
+-----------+
|           |
v           v
EXPIRED  CANCELLED
     \     /
      v   v
      CLOSED
```

Closed sessions never become active again.

---

# Workspace Binding

Every active session owns exactly one Workspace.

The Workspace cannot change during the lifetime of the session.

Future versions may support multiple Workspaces through a new contract.

---

# Host Binding

Each session is associated with one target HostIdentity.

Changing the host requires a new session.

---

# User Binding

Each session belongs to one authenticated user.

User identity cannot change.

---

# Session Limits

A session may define:

* maximum duration
* maximum requests
* maximum concurrent operations
* maximum artifact size

Exceeding a limit causes graceful termination.

---

# Cancellation

Cancelling a session cancels:

* active Runtime requests
* Tool execution
* Transport operations

Cancellation propagates through Runtime.

---

# Expiration

Expired sessions reject all new requests.

Running operations follow Runtime timeout and cancellation rules.

---

# Audit

Session events:

```text
SESSION_STARTED

SESSION_FINISHED

SESSION_CANCELLED

SESSION_EXPIRED
```

Audit ordering must remain chronological.

---

# Runtime Relationship

Runtime validates:

* session exists
* session active
* Workspace available
* Host available

before Tool execution.

---

# Security Invariants

A Session:

* cannot change owner
* cannot change Workspace
* cannot change Host
* cannot survive expiration
* cannot bypass Policy
* cannot bypass Approval
* cannot bypass Audit

---

# Acceptance Criteria

The Session contract is implemented when:

* every request belongs to one session
* expired sessions reject new requests
* cancellation propagates correctly
* Workspace and Host remain immutable
* Audit records lifecycle events

