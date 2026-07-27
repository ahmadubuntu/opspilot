# OpsPilot Implementation Contracts

> This document defines implementation-level contracts derived from architecture decisions.
>
> Any code that violates these contracts requires an ADR or explicit architecture review.

---

# 1. Dependency Rules

## Allowed Dependency Direction

Client Layer
|
v
Adapters
|
v
Runtime
|
v
Core Services
|
v
Infrastructure

Allowed:


runtime -> core
runtime -> policy
runtime -> audit
runtime -> transport
runtime -> plugins_api


Not allowed:


runtime -> kubernetes plugin
runtime -> docker plugin
runtime -> git plugin

plugin -> runtime internals

plugin -> another plugin


---

# 2. Core Invariants

The following components are mandatory core services:

- Policy Engine
- Approval Manager
- Audit Manager
- Session Manager
- Tool Registry
- Transport Manager
- Error Manager

They cannot be implemented as optional plugins.

Reason:

Core safety guarantees must not depend on extensions.

---

# 3. Runtime Contract

Runtime MUST:

- create execution context
- validate requests
- resolve tools
- check policy
- request approval when required
- execute through dispatcher
- collect results
- write audit events

Runtime MUST NOT:

- execute shell commands directly
- access Kubernetes APIs directly
- access Docker API directly
- manage credentials directly

---

# 4. Plugin Contract

Every plugin MUST provide:

PluginManifest
Plugin class
Tool definitions
Input models
Output models


Minimum metadata:

```yaml
id:
version:
description:
permissions:
required_transports:
tools:
5. Tool Contract

Every tool MUST declare:

name
description
input schema
output schema
risk class
mutation behavior
required permissions

Example:

name: kubernetes.list_pods

risk:
  level: READ

mutates: false

permissions:
  - kubernetes.read
6. Tool Execution Flow

Every tool execution follows:

Request
   |
   v
Session Validation
   |
   v
Tool Resolution
   |
   v
Permission Check
   |
   v
Risk Evaluation
   |
   v
Approval Decision
   |
   v
Transport Execution
   |
   v
Result Validation
   |
   v
Audit Record

No step may be skipped.

7. Approval Contract

Approval is required for:

destructive operations
remote execution
infrastructure mutation
credential usage
unknown risk operations

Approval request MUST contain:

action
tool
plugin
target
arguments
risk
expected impact

Approval cannot be:

implicit
hidden inside plugin code
bypassed by configuration
8. Audit Contract

Every execution creates audit events.

Required fields:

event_id:
timestamp:
session_id:
user:
plugin:
tool:
arguments:
target:
risk:
decision:
result:
error:

Audit writes must be centralized.

Plugins cannot directly modify audit storage.

9. Transport Contract

Transport provides execution capability.

Interface:

execute()
read()
write()
stream()

Initial implementations:

LocalTransport
SSHTransport (future)
RemoteAgentTransport (future)

Transport does not decide:

authorization
permissions
approvals
10. Workspace Contract

Workspace MUST provide:

isolated root
safe path resolution
traversal prevention
symlink validation

Unsafe:

../../etc/passwd
/proc/*
/sys/*

must be rejected.

11. Secret Handling Contract

Forbidden:

secret in prompt
secret in logs
secret in markdown
secret in environment dumps
secret in tool arguments

Allowed:

SecretReference
SecretHandle
SecretProvider API
12. Error Handling Contract

Errors MUST be classified.

Categories:

VALIDATION_ERROR
POLICY_DENIED
APPROVAL_REQUIRED
TRANSPORT_ERROR
PLUGIN_ERROR
TIMEOUT
CANCELLED
UNKNOWN

Retry rules:

Allowed:

network failures
temporary transport failures

Forbidden automatic retry:

mutations
destructive actions
13. Memory Contract

Memory provides context.

Memory does not provide truth.

Rules:

Tool output > Memory
Current state > Cached state
Observed data > Previous execution

Runtime decides:

what memory is retrieved
when memory is invalid

Plugins cannot query memory directly.

14. MCP Contract

MCP is an adapter.

Allowed:

MCP Client
    |
    v
MCP Server
    |
    v
Runtime API

Forbidden:

MCP Server
    |
    v
Plugin directly

MCP does not implement:

policy
approval
audit
execution
15. Testing Contract

Each core component requires:

Unit tests:

policy decisions
tool validation
permission checks
state transitions

Integration tests:

runtime + plugin
runtime + transport
runtime + MCP

Security tests:

path traversal
privilege escalation attempts
unauthorized execution
secret leakage
16. Definition of Done For New Plugins

A plugin is complete only when:

manifest exists
permissions declared
tools have schemas
risk levels assigned
audit works
policy works
tests exist
documentation exists
17. AI Agent Development Rules

When modifying OpsPilot:

AI agents MUST:

Read:
PROJECT_PRINCIPLES.md
ARCHITECTURE_DECISIONS.md
this file
Check:
dependency rules
security boundaries
existing ADRs
Before changing architecture:
create ADR
explain alternatives
explain migration impact
Status

Canonical.

Changes require architecture review.
