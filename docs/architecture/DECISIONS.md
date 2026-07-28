# OpsPilot Architecture Summary

## Purpose

This document is the concise entry point for understanding the current OpsPilot architecture.

Detailed reasoning belongs in ADRs.

Detailed behavioral contracts belong in specifications.

## Canonical Decisions

- Runtime Execution Kernel is the only execution authority.
- Every request passes through Session, Policy, Approval when required, Dispatcher, Tool, Workspace, Transport, and Audit.
- Plugins provide Tools; Plugins do not own execution.
- Plugins do not expose a generic `execute()` switch.
- Core platform services are not optional Plugins.
- Policy, Approval, Audit, Session, Workspace, Transport, and Tool Registry are mandatory Core services.
- Internal Plugin and Tool contracts use typed Python interfaces.
- MCP is an external adapter and is not the internal Plugin ABI.
- Open WebUI is a replaceable client and does not own business logic.
- Policy evaluates every Tool request.
- Unknown or ambiguous execution intent fails closed.
- Approval is bound to one exact request and cannot be replayed.
- Audit is mandatory and append-only through its public API.
- Required pre-execution Audit failure prevents Tool execution.
- Workspace owns filesystem scope and path isolation.
- Policy may restrict Workspace access but cannot expand the Workspace root.
- HostTransport performs host operations but never authorizes them.
- Plugins and Tools never call subprocess, SSH, or host filesystems directly.
- Tools declare typed input and output models.
- Tools declare risk, permissions, mutation, dry-run, idempotency, and retry-safety metadata.
- Mutating operations are never automatically retried.
- Memory is advisory and never replaces current observation.
- Contracts v1 binds one User, Workspace, and Host to each Session.
- CLI and MCP must use the same Runtime API.
- The first vertical slice is read-only filesystem access.
- Architecture-sensitive changes require Spec and ADR review when applicable.
- Numbered duplicate source and architecture files are prohibited.
- Production code requires tests, Ruff, Mypy, and Pytest validation.

## Canonical Request Path

```text
Client
  |
  v
Runtime Execution Kernel
  |
  v
Session Validation
  |
  v
Tool Resolution and Input Validation
  |
  v
Policy Evaluation
  |
  +--> Deny
  +--> Dry Run
  +--> Approval
  |
  v
Dispatcher
  |
  v
Tool
  |
  v
Workspace
  |
  v
HostTransport
  |
  v
Target System
  |
  v
Output Validation and Audit

Initial Vertical Slice

Included:

filesystem.read_file
filesystem.list_directory
filesystem.stat

Excluded:

filesystem mutation
terminal execution
SSH
Docker mutation
Kubernetes
Kafka
PostgreSQL
MCP implementation
planning
RAG
multi-agent execution
Source-of-Truth Priority
Accepted ADR
Accepted specification
This architecture summary
Architecture documentation
Implementation
Tests
AI memory
Informal notes

A conflict between code and an accepted contract must be resolved explicitly.

Current Baseline

Architecture baseline: Contracts v1

Implementation status: Partial

Next implementation milestone: Runtime Execution Kernel and read-only filesystem vertical slice
