# Architecture Decision Records

## Purpose

Architecture Decision Records (ADRs) document long-lived architectural decisions that affect multiple parts of OpsPilot.

Specifications describe *what* the system must do.

ADRs describe *why* the architecture is the way it is.

## When to create an ADR

Create an ADR when a decision:

* has meaningful alternatives
* affects multiple subsystems
* has significant reversal cost
* changes trust boundaries
* changes architectural ownership
* changes security assumptions
* changes extension mechanisms

Do **not** create ADRs for routine implementation details or local refactoring decisions.

## Lifecycle

```text
Proposed
    ↓
Accepted
    ↓
Implemented
    ↓
Superseded (optional)
```

## Relationship to Specifications

Priority order:

1. Accepted ADR
2. Accepted Specification
3. Source Code
4. Tests

Specifications must not contradict accepted ADRs.

If an accepted ADR changes, affected specifications and implementations must be reviewed.

