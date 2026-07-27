# Approval System

## Purpose

The Approval System prevents dangerous operations from executing without explicit user consent.

---

## Principles

Approval is determined by Policy.

Approval is never decided by plugins.

---

## Approval Request

An approval request contains:

- operation
- plugin
- tool
- target
- arguments
- risk class
- estimated impact
- dry-run result (if available)
- diff preview (if available)

---

## Approval Result

Possible outcomes:

- Approved
- Rejected
- Expired

---

## Rules

READ operations should not require approval.

WRITE operations may require approval.

EXEC operations usually require approval.

REMOTE_EXEC always requires approval.

CLUSTER_MUTATE always requires approval.

---

## Timeout

Approval requests expire after a configurable timeout.

Expired requests never execute automatically.

---

## Audit

Every approval decision is recorded.

Approved or rejected actions are both auditable.
