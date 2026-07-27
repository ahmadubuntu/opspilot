# Architecture Guardrails

This document defines the non-negotiable architectural rules of OpsPilot.

Any change violating these rules requires a new ADR.

---

# 1. Core Owns Trust

The Core is the only trusted component.

The Core owns:

- Session lifecycle
- Configuration
- Policy Engine
- Approval Engine
- Audit Engine
- Tool Registry
- Plugin Loader
- Host Transport
- Secrets Management

Plugins are never trusted.

---

# 2. Plugins Are Pure Tool Providers

Plugins provide capabilities.

Plugins never own:

- Security
- Authentication
- Authorization
- Policy
- Approval
- Auditing
- Session State

Plugins must remain stateless whenever possible.

---

# 3. Every Action Goes Through Policy

No tool executes directly.

Execution flow:

Client
→ Runtime
→ Policy Engine
→ Approval (if required)
→ Tool Dispatcher
→ Plugin
→ Host Transport
→ Audit

Bypassing this flow is forbidden.

---

# 4. Host Transport Is Mandatory

Plugins never access:

- local filesystem
- ssh
- docker socket
- kubernetes
- cloud APIs

directly.

All access must use HostTransport.

---

# 5. Security Before Features

Adding features must never weaken:

- isolation
- permissions
- auditing
- confirmation
- sandboxing

If a conflict exists:

Security wins.

---

# 6. Local First

OpsPilot runs locally.

Cloud services are optional.

The architecture must not depend on:

- OpenAI
- Anthropic
- Azure
- AWS

---

# 7. Model Independent

Business logic never depends on a specific LLM.

Supported backends include:

- LM Studio
- Ollama
- OpenAI-compatible APIs
- vLLM
- future providers

Changing model providers must require configuration only.

---

# 8. UI Independent

The runtime never depends on Open WebUI.

Supported clients may include:

- Open WebUI
- CLI
- VSCode Extension
- Web UI
- REST API

All clients use the same runtime.

---

# 9. MCP Is an Adapter

MCP is an integration protocol.

It is not the internal architecture.

Internal APIs remain strongly typed Python interfaces.

---

# 10. Explicit Permissions

Every tool declares:

- permissions
- risk class
- required approval
- supported transports

Nothing is inferred.

---

# 11. Dry Run First

Every mutating tool should support:

- preview
- dry-run
- diff

before execution whenever technically possible.

---

# 12. Audit Everything

Every tool invocation must produce:

- timestamp
- session
- tool
- arguments
- user
- result
- duration
- approval status

Audit logs are append-only.

---

# 13. Secrets Never Reach the LLM

Secrets must never appear:

- in prompts
- in chat history
- in logs
- in memory
- in exceptions

Secrets are resolved only during execution.

---

# 14. Strong Typing

Every tool uses:

- Pydantic Input
- Pydantic Output

No untyped dictionaries.

No stringly-typed APIs.

---

# 15. Backward Compatibility

Public plugin interfaces must be versioned.

Breaking changes require:

- new version
- migration notes
- ADR

---

# 16. Fail Safe

On uncertainty:

The system refuses to execute.

Never guess.

Never assume.

Never auto-retry dangerous operations.

---

# 17. Production First

Every architectural decision assumes:

- production environments
- critical infrastructure
- financial systems
- regulated environments

Developer convenience is secondary.

---

# 18. Human Remains in Control

The agent assists.

The human decides.

Autonomous execution is never the default.

---

# 19. Simplicity Wins

Prefer:

- fewer abstractions
- fewer services
- fewer dependencies
- explicit code

Avoid architecture that exists only for hypothetical future needs.

---

# 20. Architecture Is Stable

Features evolve.

Architecture changes rarely.

Every architectural change requires:

- ADR
- design review
- impact analysis
