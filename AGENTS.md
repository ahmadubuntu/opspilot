# OpsPilot Agent Instructions

This file defines the mandatory development workflow for every AI agent.

## Core Principle

Specifications are the source of truth.

Code is an implementation of a specification.

Never implement a feature before its specification exists.

---

# Required Workflow

Every feature MUST follow this order.

1. Understand the problem.
2. Update or create ADR if architecture changes.
3. Create or update the Specification.
4. Define request/response models.
5. Define interfaces.
6. Implement.
7. Write tests.
8. Update documentation.

Never skip a step.

---

# Production Rules

Always assume:

- production environment
- multiple users
- future remote execution
- security first
- least privilege
- backward compatibility

Do not optimize for demos.

---

# Architecture Rules

Core owns:

- runtime
- dispatcher
- policy
- approval
- audit
- transport
- configuration

Plugins never implement those concerns.

Plugins only provide tools.

---

# Plugin Rules

Plugins:

- never execute arbitrary code outside Runtime
- never access secrets directly
- never bypass Policy Engine
- never bypass Audit
- never perform permission checks themselves

Runtime is responsible for all enforcement.

---

# Documentation Rules

Every feature requires:

- Specification
- Tests
- Documentation

Architecture changes additionally require an ADR.

---

# If unsure

Do not write code.

Improve the specification first.
