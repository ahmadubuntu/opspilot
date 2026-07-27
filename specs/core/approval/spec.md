# Approval Contract Specification

## Status

Accepted for Contracts v1.

## Purpose

The Approval Service is responsible for obtaining explicit human authorization before executing operations that Policy classifies as requiring approval.

Approval is a mandatory Core Platform Service.

Approval never decides *whether* an operation is allowed.

That decision belongs exclusively to Policy.

Approval only records explicit human consent for one specific request.

---

# Responsibilities

Approval is responsible for:

* creating approval requests
* presenting execution summaries
* binding approval to one request
* enforcing expiration
* validating approver identity
* returning approval decisions
* preventing replay
* integrating with Audit

---

# Non-Responsibilities

Approval never:

* evaluates Policy
* executes Tools
* modifies Tool arguments
* changes Runtime state
* stores Secrets
* performs Transport operations

---

# Approval Request

Every approval request contains:

* request_id
* session_id
* tool
* plugin
* target
* validated arguments
* risk class
* dry-run summary (when available)
* expiration
* checksum of approved payload

Changing any field invalidates the approval.

---

# Approval Decisions

Possible results:

```text
APPROVED
REJECTED
EXPIRED
CANCELLED
```

Exactly one decision is returned.

---

# Request Binding

Approval is bound to:

* Tool
* arguments
* target
* risk class
* session
* request id

Changing any value requires a new Approval.

---

# Expiration

Approvals must expire.

Expired approvals cannot be reused.

Runtime must request a new approval.

---

# Replay Protection

Approvals are single-use.

An approval cannot authorize:

* another request
* another session
* another Tool
* another target

---

# Audit

Approval produces:

* APPROVAL_REQUESTED
* APPROVAL_GRANTED
* APPROVAL_REJECTED
* APPROVAL_EXPIRED

Approval never writes directly to storage.

Runtime coordinates Audit emission.

---

# Security Invariants

Approval cannot:

* approve unknown requests
* modify request payloads
* bypass Policy
* bypass Audit
* authorize another request
* survive expiration
* expose Secrets

---

# Acceptance Criteria

The Approval contract is implemented when:

* approvals are bound to one request
* replay is impossible
* expiration is enforced
* Audit events are emitted
* approval never bypasses Policy
* changed requests require new approval

