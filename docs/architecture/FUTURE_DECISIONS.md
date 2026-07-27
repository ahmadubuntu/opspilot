# Future Architecture Decisions

This file contains architectural decisions that are accepted but intentionally postponed.
Nothing in this file may be implemented without an ADR.

---

# AD-001 — Host Transport Layer

Status:
Accepted (Deferred)

Reason:

Stage-1 only supports local execution.
However every core API MUST be transport-agnostic.

Future transports:

- Local
- SSH
- Remote Agent
- Kubernetes Exec
- WinRM (optional)

No plugin may directly execute commands on the host.

Everything goes through HostTransport.

---

# AD-002 — Policy Engine

Status:
Accepted (Deferred)

Every tool execution must pass through Policy Engine.

Policy decisions include:

- allow
- deny
- confirmation required
- dry-run required

Policies may depend on:

- tool
- arguments
- environment
- hostname
- workspace
- user

Plugins never implement authorization.

---

# AD-003 — Approval Service

Status:
Accepted (Deferred)

Mutating operations require approval.

Examples:

kubectl delete

terraform apply

docker rm

git push

rm -rf

Approval is a Core Runtime feature.

Never a plugin feature.

---

# AD-004 — Audit Log

Status:
Accepted (Deferred)

Every executed tool generates an immutable audit event.

Audit event contains:

- timestamp
- session id
- tool
- arguments
- result
- duration
- approval id
- execution status

Audit cannot be disabled.

---

# AD-005 — Risk Classes

Status:
Accepted (Deferred)

Every tool declares exactly one risk class.

Risk classes:

READ

WRITE_WORKSPACE

LOCAL_EXEC

REMOTE_EXEC

CLUSTER_MUTATE

SECRET_ACCESS

Policy Engine uses the risk class.

---

# AD-006 — Dry Run

Status:
Accepted (Deferred)

Mutating tools SHOULD support Dry Run.

Whenever possible the Runtime asks the tool to generate:

- diff
- preview
- plan

before execution.

---

# AD-007 — Plugin Permissions

Status:
Accepted (Deferred)

Every plugin declares permissions.

Example:

filesystem.read

filesystem.write

terminal.exec

docker.socket

kubernetes.mutate

postgres.write

Permissions are enforced by Runtime.

Never by plugins.

---

# AD-008 — Secrets Provider

Status:
Accepted (Deferred)

Plugins never read:

environment variables

password files

SSH keys

directly.

Secrets are injected through Runtime.

---

# AD-009 — Session Object

Status:
Accepted (Deferred)

Every execution belongs to one Session.

Session contains:

- user
- workspace
- host
- model
- memory
- approvals
- audit context

---

# AD-010 — Tool Registry

Status:
Accepted (Deferred)

Runtime owns the global tool registry.

Plugins only register tools.

Tool names must be globally unique.

Tool schemas are versioned.

---

# AD-011 — Open WebUI Independence

Status:
Accepted (Deferred)

Open WebUI is only one client.

Future clients:

CLI

REST API

Desktop UI

VSCode

Other MCP Clients

Core Runtime never imports Open WebUI.

---

# AD-012 — Local First

Status:
Permanent

OpsPilot never depends on cloud services.

Internet access is optional.

All core features must work offline.

---

# AD-013 — Production First

Status:
Permanent

Every feature is designed as if it will run in production.

No shortcuts that require future redesign.

Prefer architecture over convenience.

Prefer safety over speed.

Prefer explicit behavior over magic.

---

# AD-014 — Backward Compatibility

Status:
Permanent

Public APIs are versioned.

Plugin ABI changes require:

- ADR
- migration plan
- changelog entry

Breaking changes are never silent.
