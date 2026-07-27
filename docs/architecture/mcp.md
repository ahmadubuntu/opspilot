# MCP Integration

OpsPilot exposes an MCP Server.

MCP is an integration protocol.

It is not the Runtime.

---

# Architecture

Client

↓

MCP Server

↓

Runtime

↓

Plugins

---

# Responsibilities

MCP:

- Receive requests
- Validate protocol
- Forward to Runtime
- Return structured responses

Runtime:

- Execute logic
- Enforce policy
- Audit
- Dispatch tools

---

# Design Rules

Runtime must never depend on MCP.

CLI and MCP use the same Runtime API.

Future clients:

- Open WebUI
- VSCode
- Claude Desktop
- Cursor
- Custom applications

---

# Future

Streaming

Progress events

Cancellation

Remote Runtime


---

## MCP Is Not

MCP is not:

- the Runtime
- the internal plugin API
- the Policy Engine
- the Approval System
- the Audit System
- the Planner

The Runtime must remain completely usable without MCP.

CLI, tests, and future clients all use the same Runtime API.
