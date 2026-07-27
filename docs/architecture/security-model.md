# Security Model

Security is the highest priority of OpsPilot.

Convenience never overrides safety.

---

## Trust Boundaries

```
User

↓

Runtime

↓

Policy Engine

↓

Approval Engine

↓

Tool Dispatcher

↓

Plugin

↓

Transport

↓

Infrastructure
```

Each boundary validates requests.

---

## Security Principles

- Least Privilege
- Explicit Approval
- Fail Closed
- Zero Implicit Trust
- Audit Everything
- Default Deny
- Defense in Depth
- Secure by Default

---

## Risk Classes

READ

Examples

- ls
- kubectl get
- docker ps

Default

Allowed

---

WRITE_WORKSPACE

Examples

- edit files

Default

Approval

---

EXEC

Examples

- shell

Default

Approval

---

CLUSTER_MUTATE

Requires:

- Explicit Approval
- Dry Run (if supported)
- Diff Preview (if supported)

---

REMOTE_EXEC

Examples

SSH command execution

Default

Approval Required

Always requires explicit approval.

---

## Approval

Approval decisions include

- command
- arguments
- target
- risk
- estimated impact

---

## Secrets

Secrets never appear in:

- prompts
- logs
- audit output

Secrets are injected at runtime.

---

## Audit

Every execution records

- timestamp
- session
- user
- plugin
- tool
- arguments
- result
- duration

Audit logs are append-only.

---

## Workspace

Filesystem plugins are restricted to workspace roots.

Path traversal is rejected.

Symlink escapes are rejected.

---

## Future Security Features

- Plugin signing
- Policy bundles
- RBAC
- Secret providers
- Multi-user support

---

## Threats

The architecture explicitly defends against:

- Prompt Injection
- Path Traversal
- Symlink Escape
- Privilege Escalation
- Workspace Escape
- Secret Disclosure
- Arbitrary Code Execution
