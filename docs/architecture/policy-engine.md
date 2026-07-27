# Policy Engine

## Purpose

The Policy Engine decides whether an operation is allowed.

---

## Possible Decisions

- Allow
- Deny
- RequireApproval
- RequireDryRun

---

## Inputs

Policy evaluation considers:

- user
- host
- workspace
- plugin
- tool
- risk class
- arguments
- environment

---

## Responsibilities

The Policy Engine:

- evaluates permissions
- evaluates risk
- requests approval when required

---

## Non Responsibilities

The Policy Engine never:

- executes tools
- communicates with plugins
- accesses transports
- stores secrets

---

## Fail Closed

If policy evaluation fails,

the operation is denied.

---

## Future

Future versions may support:

- OPA
- Cedar
- organization policies
- RBAC
- ABAC
