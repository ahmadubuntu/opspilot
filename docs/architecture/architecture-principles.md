# Architecture Principles

## Local First

The system must work entirely offline.

Cloud services are optional.

---

## Security First

Every action is denied unless explicitly allowed.

---

## Human Approval

Mutating operations require explicit approval unless policy allows otherwise.

---

## Separation of Concerns

Runtime controls execution.

Plugins provide capabilities.

Policies enforce permissions.

Audit records actions.

---

## Transport Independence

Business logic must not depend on local filesystems.

Every operation must work with future transports:

- Local
- SSH
- Remote Agent

without redesign.

---

## Strong Typing

All public interfaces use typed request/response models.

No dictionary-based APIs.

---

## Explicit Contracts

Every component has a documented contract.

No implicit behavior.
