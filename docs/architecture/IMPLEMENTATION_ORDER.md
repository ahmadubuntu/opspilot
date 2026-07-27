# Implementation Order

This document defines the mandatory implementation order of OpsPilot.

The order MUST NOT be changed without an Architecture Decision Record (ADR).

---

## Phase 1 — Foundation

- Configuration system
- Logging
- Plugin Manifest
- Plugin ABI
- Tool Registry
- Session Model

No business plugins may be implemented before this phase.

---

## Phase 2 — Execution Kernel

Implement:

- Runtime
- Policy Engine
- Approval Engine
- Audit Engine
- Host Transport

The execution kernel is responsible for all privileged operations.

Plugins MUST NOT bypass it.

---

## Phase 3 — First Plugin

Filesystem

Only READ operations.

No WRITE.

No DELETE.

No EXEC.

Filesystem plugin is used to validate:

- Plugin API
- Tool Registry
- Permission system
- Audit events

---

## Phase 4 — Terminal

Terminal plugin.

Initially:

- Allowlisted commands
- Dry Run
- Approval required

No shell pipelines.

No sudo.

---

## Phase 5 — Git

Read operations.

Diff.

Status.

Branch.

Commit (approval).

Push disabled by default.

---

## Phase 6 — Docker

Read-only.

Containers.

Images.

Volumes.

Network.

Mutation operations require approval.

---

## Phase 7 — Kubernetes

Read-only first.

Cluster inspection.

Namespace inspection.

Pod inspection.

Logs.

Later:

kubectl apply

kubectl delete

kubectl rollout

---

## Phase 8

Kafka

Postgres

Sentry

etc.

Only after the execution kernel has proven stable.

---

# Never Skip

The following components MUST always exist before adding new plugins.

- Policy
- Approval
- Audit
- Tool Registry
- Plugin ABI
- Host Transport

---

# Golden Rule

Every new plugin must validate the architecture.

No plugin may introduce new architectural concepts.

The architecture drives plugins.

Plugins never drive the architecture.
