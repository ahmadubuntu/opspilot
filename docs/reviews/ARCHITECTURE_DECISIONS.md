# OpsPilot Architecture Decisions

> This document is the canonical summary of accepted, rejected, and pending architecture decisions.
>
> Detailed reasoning belongs in ADR documents.
> This file only describes the current architectural truth.

---

# 1. Core Philosophy

## Accepted

OpsPilot is:

- Local-first
- Safety-first
- Model-independent
- Plugin-extensible
- Runtime-centric
- Human-controlled for risky operations

The system must optimize for:

- predictable behavior
- controlled execution
- auditability
- extensibility
- operational safety

Convenience must never override safety.

---

# 2. Runtime Ownership

## Accepted

The Runtime is the execution kernel.

Runtime owns:

- agent execution loop
- session lifecycle
- tool dispatch
- policy enforcement
- approval workflow
- audit coordination
- error handling
- execution state machine
- timeout management
- cancellation handling

Runtime does NOT own:

- UI
- Open WebUI behavior
- MCP protocol details
- infrastructure implementation
- Kubernetes logic
- Docker logic
- Git implementation

---

# 3. Plugin Model

## Accepted

Plugins provide capabilities.

Plugins do NOT define platform behavior.

Plugins are:

- stateless
- permission-bound
- policy-controlled
- runtime-managed

Plugins must never:

- bypass policy
- bypass approval
- write audit records directly
- access secrets directly
- execute arbitrary commands outside transport layer

---

# 4. Plugin ABI

## Accepted

Internal plugins use typed Python contracts.

Primary interfaces:

- PluginManifest
- PluginContext
- ToolDefinition
- ToolRequest
- ToolResult

External integrations use adapters.

MCP is not the internal plugin ABI.

---

# 5. MCP Boundary

## Accepted

MCP is an interoperability layer.

MCP may expose OpsPilot capabilities to:

- Open WebUI
- external agents
- future clients

MCP does NOT own:

- security
- authorization
- approval
- audit
- planning
- execution

All MCP requests enter through Runtime.

Flow:

Client
|
v
MCP Adapter
|
v
Runtime
|
v
Policy
|
v
Tool Dispatcher
|
v
Plugins


---

# 6. Security Model

## Accepted

Security is enforced by Core.

Mandatory components:

- Policy Engine
- Approval System
- Audit System
- Transport Isolation
- Workspace Isolation

Default behavior:

- unknown action => deny
- ambiguous action => require confirmation
- risky mutation => dry-run first when possible

---

# 7. Transport Model

## Accepted

Transport abstracts execution environment.

Supported future transports:

- LocalTransport
- SSHTransport
- RemoteAgentTransport

Transport responsibilities:

- execute
- read
- write
- stream output

Transport does NOT:

- authorize actions
- decide permissions
- bypass policy

---

# 8. Workspace Model

## Accepted

Workspace is a security boundary.

Requirements:

- path isolation
- traversal protection
- symlink protection
- host-aware workspace mapping

Workspace must not assume:

- local filesystem
- single machine
- fixed paths

---

# 9. Secrets

## Accepted

Secrets never enter:

- prompts
- LLM context
- logs
- plugin configuration files

Plugins receive:

- secret references
- opaque handles
- controlled access

Never raw secret material.

---

# 10. Audit

## Accepted

Every meaningful action must be auditable.

Audit records include:

- session id
- user
- tool
- plugin
- arguments
- target
- decision
- result
- timestamps

Audit is append-only.

---

# 11. Tool Risk Classification

## Accepted

Tools are classified.

Initial categories:
READ
WRITE_WORKSPACE
EXEC
CLUSTER_MUTATE
REMOTE_EXEC


Risk level affects:

- policy decision
- approval requirement
- logging detail

---

# 12. Memory

## Accepted

Memory assists reasoning.

Memory never replaces reality.

Rules:

- tools are the source of truth
- cached information is never authoritative
- uncertain state requires fresh observation

Memory layers:

- session memory
- project memory
- operational knowledge

---

# 13. Documentation Rules

## Accepted

Documentation is part of the product.

Required:

- ADRs for important decisions
- architecture specs
- machine-readable contracts where possible

Markdown alone is not enough for critical contracts.

---

# 14. Development Rules

## Accepted

Before implementing large features:

Required:

- architecture contract
- security consideration
- ADR if decision is irreversible

Avoid:

- premature plugins
- premature distribution
- microservices-per-plugin
- undocumented behavior

---

# 15. Rejected Approaches

## Rejected

### MCP as internal plugin system

Reason:

- too coupled to external protocol
- poor typed contract experience
- harder testing

---

### Everything as plugin

Reason:

Core invariants cannot depend on optional components.

---

### Plugin direct subprocess execution

Reason:

Bypasses:

- policy
- audit
- transport abstraction

---

### Runtime importing concrete plugins

Reason:

Creates coupling and destroys extensibility.

---

### Open WebUI as the agent runtime

Reason:

UI must remain replaceable.

---

### Docker-first for the agent itself

Reason:

Host integration complexity:

- Docker socket
- kubeconfig
- SSH agent
- local GPU

Agent may run on host; supporting services may run in containers.

---

# 16. Open Decisions

Pending:

- plugin signing strategy
- distributed runtime
- remote agent protocol
- streaming execution model
- multi-agent orchestration
- advanced memory backend
- OPA integration

---

# Last Updated

YYYY-MM-DD

