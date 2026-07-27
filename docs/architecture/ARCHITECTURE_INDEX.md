# Architecture Index

Read the architecture documents in the following order.

```
Vision
    ↓
Architecture Principles
    ↓
Runtime
    ↓
Dispatcher
    ↓
Policy Engine
    ↓
Approval
    ↓
Audit
    ↓
Host Transport
    ↓
Plugin System
    ↓
Workspace
    ↓
Memory
    ↓
MCP
    ↓
Error Model
```

---

## Documents

| Component | Document |
|-----------|----------|
| Principles | architecture-principles.md |
| Runtime | runtime.md |
| Dispatcher | dispatcher.md |
| Policy | policy-engine.md |
| Approval | approval.md |
| Audit | audit.md |
| Transport | host-transport.md |
| Plugin System | plugin-system.md |
| Workspace | workspace.md |
| Memory | memory.md |
| MCP | mcp.md |
| Errors | error-model.md |

---

The Runtime is the execution kernel.

Everything else is either a platform service or an integration layer.

When documents disagree:

ADR → Architecture → Specification → Code
