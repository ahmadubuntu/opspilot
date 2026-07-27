# Memory Architecture

## Purpose

Memory helps the Runtime make better decisions.

Memory never replaces reality.

Whenever the current state matters, Runtime must execute tools instead of trusting memory.

---

# Types of Memory

## Session Memory

Short-lived.

Contains:

- conversation
- tool results
- approvals
- execution history

Destroyed when the session ends.

---

## Project Memory

Persistent.

Contains:

- architecture
- ADRs
- project documentation
- design decisions

Usually stored under:

```

docs/
.ai/

```

---

## Knowledge Memory

Optional.

Examples:

- Runbooks
- Kubernetes documentation
- Internal documentation
- External indexed knowledge

May use vector databases in future.

---

## Runtime Cache

Temporary cache only.

Examples:

- kubectl outputs
- git status
- docker ps

Cache improves performance.

Cache is NEVER the source of truth.

---

# Retrieval

Only Runtime retrieves memory.

Plugins never query memory directly.

Flow:

```

User
↓
Runtime
↓
Memory Retrieval
↓
Planning
↓
Tool Execution

```

---

# Freshness

Memory becomes stale.

Runtime must execute tools again when:

- current cluster state matters
- filesystem may have changed
- remote host may have changed
- uncertainty exists

Reality always wins over memory.

---

# Memory Rules

Memory:

may suggest

Memory:

never authorizes

Memory:

never approves

Memory:

never executes tools

Memory:

never bypasses Policy Engine

---

# Future Storage

Possible backends:

- SQLite
- ChromaDB
- PostgreSQL
- OpenSearch

Backend choice must not affect Runtime APIs.

---

# Privacy

Secrets are never stored inside Memory.

Credentials are never embedded into semantic memories.

Sensitive tool outputs may be excluded or redacted.

---

# Principles

- Memory is advisory
- Runtime owns retrieval
- Plugins are stateless
- Cache is not truth
- Reality overrides memory
